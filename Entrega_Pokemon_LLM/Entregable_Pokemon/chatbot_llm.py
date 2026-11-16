# Chatbot Pokemon con LLM. Uso por consola: python chatbot_llm.py
# El modelo responde solo con los hechos de base_conocimiento.pl

import os
import re
import sys
import time
from pathlib import Path

import requests

try:
    from dotenv import dotenv_values, load_dotenv

    _CARPETA = Path(__file__).parent
    load_dotenv(_CARPETA / ".env")
    # Respaldo: el token tambien se acepta en .env.example
    if not os.getenv("LLM_API_KEY"):
        _token = dotenv_values(_CARPETA / ".env.example").get("LLM_API_KEY")
        if _token:
            os.environ["LLM_API_KEY"] = _token
except ImportError:
    pass

RUTA_BASE = Path(__file__).parent / "Codigo_Prolog" / "base_conocimiento.pl"

# Configuracion (se puede cambiar desde el archivo .env)
URL_API = os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1")
URL_API = URL_API.rstrip("/")
MODELO = os.getenv("LLM_MODEL", "openai/gpt-oss-120b")
# Se prueban en orden si el modelo configurado deja de existir
MODELOS_ALTERNATIVOS = [
    "openai/gpt-oss-20b",
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
]
# low, medium o high
ESFUERZO_RAZONAMIENTO = os.getenv("LLM_REASONING", "low")
# Mensajes previos que se reenvian al modelo
MAX_HISTORIAL = 6
# Reintentos al alcanzar el limite gratuito (error 429)
MAX_REINTENTOS = 3
# Segundos maximos de espera por reintento
ESPERA_MAXIMA = 30

_modelo_en_uso = MODELO


class ErrorLLM(Exception):
    # Error con mensaje apto para mostrar al usuario
    pass


def token_configurado():
    return os.getenv("LLM_API_KEY") or os.getenv("GROQ_API_KEY") or ""


def modelo_en_uso():
    return _modelo_en_uso


# Lectura de la base de conocimiento

_HECHO = re.compile(
    r"^(pokemon_de_tipo|ventaja|resistente|inmune|evolucion)"
    r"\(\s*(?:(\w+)\s*,\s*)?\[([^\]]*)\]\s*\)\s*\."
)


def cargar_base(ruta=RUTA_BASE):
    # Lee los hechos del archivo Prolog y los devuelve como diccionarios
    base = {
        "pokemon_de_tipo": {},
        "ventaja": {},
        "resistente": {},
        "inmune": {},
        "evolucion": [],
    }
    texto = Path(ruta).read_text(encoding="utf-8", errors="replace")
    for linea in texto.splitlines():
        hecho = _HECHO.match(linea.strip())
        if not hecho:
            continue
        predicado, clave, lista = hecho.groups()
        elementos = [e.strip() for e in lista.split(",") if e.strip()]
        # Se descartan las reglas con variables, p. ej. evolucion([P|_])
        if not all(re.fullmatch(r"[a-z]\w*", e) for e in elementos):
            continue
        if predicado == "evolucion":
            base["evolucion"].append(elementos)
        else:
            base[predicado][clave] = elementos

    tipos_por_pokemon = {}
    for tipo, pokemones in base["pokemon_de_tipo"].items():
        for pokemon in pokemones:
            tipos_por_pokemon.setdefault(pokemon, []).append(tipo)
    base["tipos_por_pokemon"] = tipos_por_pokemon
    base["pokemones"] = list(tipos_por_pokemon)
    base["tipos"] = list(base["ventaja"])
    return base


def _lineas(diccionario):
    filas = []
    for clave, valores in diccionario.items():
        texto = ", ".join(valores) if valores else "ninguno"
        filas.append(f"- {clave}: {texto}")
    return "\n".join(filas)


def construir_contexto(base):
    # Convierte los hechos en texto para el modelo
    cadenas = "\n".join(
        "- " + " -> ".join(cadena) for cadena in base["evolucion"]
    )
    return (
        "POKEMON REGISTRADOS Y SUS TIPOS (pokemon: tipos)\n"
        f"{_lineas(base['tipos_por_pokemon'])}\n\n"
        "POKEMON POR TIPO (tipo: pokemon de ese tipo)\n"
        f"{_lineas(base['pokemon_de_tipo'])}\n\n"
        "CADENAS EVOLUTIVAS (de forma base a forma final)\n"
        f"{cadenas}\n"
        "Los pokemon que no aparecen en ninguna cadena no tienen "
        "cadena evolutiva.\n\n"
        "VENTAJAS (tipo atacante: tipos defensores contra los que es "
        "super efectivo)\n"
        f"{_lineas(base['ventaja'])}\n\n"
        "RESISTENCIAS (tipo defensor: tipos de ataque que resiste)\n"
        f"{_lineas(base['resistente'])}\n\n"
        "INMUNIDADES (tipo defensor: tipos de ataque a los que es "
        "inmune)\n"
        f"{_lineas(base['inmune'])}\n"
        "Los tipos que no aparecen en esta lista no tienen inmunidades."
    )


INSTRUCCIONES = (
    "Eres un chatbot experto en la Pokedex de la region de Kanto. "
    "Respondes preguntas usando UNICAMENTE la base de conocimiento que "
    "aparece mas abajo.\n\n"
    "Reglas:\n"
    "1. Usa solo los datos de la base de conocimiento. No uses tu "
    "conocimiento propio sobre Pokemon, aunque sepas que en los juegos "
    "algo es distinto.\n"
    "2. Mundo cerrado: si un pokemon o un tipo no aparece en la base, "
    "responde que no esta registrado en la base de conocimiento. No "
    "inventes datos.\n"
    "3. Un pokemon puede tener uno o dos tipos. Un tipo de ataque es "
    "super efectivo contra un pokemon si es super efectivo contra al "
    "menos uno de sus tipos.\n"
    "4. En una cadena evolutiva el primero es la forma base, el ultimo "
    "es la forma final y los que estan entre medio son formas "
    "intermedias.\n"
    "5. Antes de responder revisa todas las filas relevantes de las "
    "tablas; cuando te pidan una lista, entregala completa y sin "
    "elementos de mas.\n"
    "6. Si la pregunta no trata sobre este dominio, indica amablemente "
    "que solo respondes sobre la Pokedex de Kanto.\n"
    "7. Responde en espanol, de forma breve y directa, escribiendo los "
    "nombres tal como aparecen en la base.\n\n"
    "BASE DE CONOCIMIENTO\n"
)

_BASE = cargar_base()
PROMPT_SISTEMA = INSTRUCCIONES + construir_contexto(_BASE)


# Llamada al LLM


def _enviar(mensajes, token, modelo):
    cuerpo = {"model": modelo, "messages": mensajes, "temperature": 0}
    # Los modelos gpt-oss razonan: se limita para gastar menos tokens
    if "gpt-oss" in modelo:
        cuerpo["reasoning_effort"] = ESFUERZO_RAZONAMIENTO
    return requests.post(
        f"{URL_API}/chat/completions",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json=cuerpo,
        timeout=90,
    )


def _detalle_error(respuesta):
    try:
        error = respuesta.json().get("error", {})
        if isinstance(error, dict):
            return error.get("message", "")
        return str(error)
    except ValueError:
        return respuesta.text[:200]


def _segundos_de_espera(respuesta, intento):
    try:
        espera = float(respuesta.headers.get("retry-after", ""))
    except ValueError:
        espera = 5 * (intento + 1)
    return min(max(espera, 1), ESPERA_MAXIMA)


def preguntar(mensaje, historial=None, token=None):
    # Devuelve {"respuesta", "modelo", "segundos"}
    # historial: lista de {"role": "user"|"assistant", "content": str}
    # token: si no se entrega, se usa el del archivo .env
    global _modelo_en_uso

    token = (token or token_configurado()).strip()
    if not token:
        raise ErrorLLM(
            "Falta el token del LLM. Ingreselo en la pagina o definalo "
            "en el archivo .env (LLM_API_KEY)."
        )
    mensaje = (mensaje or "").strip()
    if not mensaje:
        raise ErrorLLM("Escriba una pregunta.")

    mensajes = [{"role": "system", "content": PROMPT_SISTEMA}]
    for turno in (historial or [])[-MAX_HISTORIAL:]:
        rol = turno.get("role")
        if rol in ("user", "assistant") and turno.get("content"):
            mensajes.append(
                {"role": rol, "content": str(turno["content"])[:2000]}
            )
    mensajes.append({"role": "user", "content": mensaje[:1000]})

    candidatos = [_modelo_en_uso]
    candidatos += [m for m in MODELOS_ALTERNATIVOS if m != _modelo_en_uso]
    inicio = time.time()
    ultimo_error = ""

    for modelo in candidatos:
        for intento in range(MAX_REINTENTOS + 1):
            try:
                respuesta = _enviar(mensajes, token, modelo)
            except requests.RequestException:
                raise ErrorLLM(
                    "No se pudo conectar con el servicio del LLM. "
                    "Revise su conexion a internet."
                )

            if respuesta.status_code == 200:
                mensaje_llm = respuesta.json()["choices"][0]["message"]
                contenido = mensaje_llm.get("content") or ""
                contenido = re.sub(
                    r"<think>.*?</think>", "", contenido, flags=re.S
                ).strip()
                if not contenido:
                    raise ErrorLLM(
                        "El modelo no entrego una respuesta. "
                        "Intente nuevamente."
                    )
                _modelo_en_uso = modelo
                return {
                    "respuesta": contenido,
                    "modelo": modelo,
                    "segundos": round(time.time() - inicio, 2),
                }

            codigo = respuesta.status_code
            ultimo_error = _detalle_error(respuesta)
            if codigo in (401, 403):
                raise ErrorLLM(
                    "El token del LLM no es valido o no tiene permisos."
                )
            if codigo == 429:
                if intento < MAX_REINTENTOS:
                    time.sleep(_segundos_de_espera(respuesta, intento))
                    continue
                raise ErrorLLM(
                    "Se alcanzo el limite de uso gratuito del LLM. "
                    "Espere un minuto e intente de nuevo."
                )
            # El modelo ya no existe: se prueba el siguiente
            if codigo in (400, 404) and "model" in ultimo_error.lower():
                break
            if codigo >= 500 and intento < MAX_REINTENTOS:
                time.sleep(2)
                continue
            raise ErrorLLM(
                f"El servicio del LLM devolvio un error ({codigo}): "
                f"{ultimo_error}"
            )

    raise ErrorLLM(
        "Ningun modelo configurado esta disponible. Defina LLM_MODEL en "
        f"el archivo .env. Detalle: {ultimo_error}"
    )


# Chat por consola


def main():
    # Evita errores de codificacion en la consola de Windows
    sys.stdout.reconfigure(errors="replace")
    print("=" * 46)
    print("     CHATBOT POKEMON KANTO  -  version LLM")
    print("=" * 46)
    print("Escriba su pregunta ('salir' para terminar).\n")
    historial = []
    while True:
        try:
            pregunta = input("Usted: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if pregunta.lower() in ("salir", "0", "exit"):
            break
        if not pregunta:
            continue
        try:
            resultado = preguntar(pregunta, historial)
        except ErrorLLM as error:
            print(f"[Error] {error}\n")
            continue
        print(f"Chatbot: {resultado['respuesta']}\n")
        historial += [
            {"role": "user", "content": pregunta},
            {"role": "assistant", "content": resultado["respuesta"]},
        ]
    print("Gracias por ocupar nuestro chat!")


if __name__ == "__main__":
    main()
