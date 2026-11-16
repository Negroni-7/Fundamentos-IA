# Evaluacion comparativa Prolog vs LLM con las 20 preguntas de
# preguntas.json. Genera resultados_evaluacion.md, .csv y .json
# (el .json alimenta generar_informe.py)
#
# python evaluacion.py               evalua ambos chatbots
# python evaluacion.py --solo-prolog no consulta al LLM
# python evaluacion.py --pausa 8     segundos de espera entre preguntas
#
# La correccion es automatica: revisar a mano las respuestas del LLM

import argparse
import csv
import json
import re
import sys
import time
from pathlib import Path

import chatbot_llm
import puente_prolog

CARPETA = Path(__file__).parent
BASE = chatbot_llm.cargar_base()
VOCABULARIO = set(BASE["pokemones"]) | set(BASE["tipos"])

CORRECTA = "Correcta"
PARCIAL = "Parcial"
INCORRECTA = "Incorrecta"
SIN_RESPUESTA = "Sin respuesta"


# Correccion automatica


def palabras(texto):
    return re.findall(r"[a-z0-9]+", puente_prolog.normalizar(texto))


def corregir(respuesta, evaluacion):
    # Compara la respuesta en texto libre con lo esperado
    tokens = palabras(respuesta)
    mencionados = set(tokens) & VOCABULARIO
    forma = evaluacion["forma"]

    # Debe nombrar exactamente estos pokemon o tipos
    if forma == "conjunto":
        esperado = set(evaluacion["esperado"])
        ignorados = set(evaluacion.get("ignorar", []))
        sobrantes = mencionados - esperado - ignorados
        encontrados = mencionados & esperado
        if encontrados == esperado and not sobrantes:
            return CORRECTA
        return PARCIAL if encontrados else INCORRECTA

    if forma == "si_no":
        if tokens and tokens[0] in ("si", "no"):
            polaridad = tokens[0]
        else:
            polaridad = "no" if "no" in tokens else "si"
        return CORRECTA if polaridad == evaluacion["esperado"] else INCORRECTA

    if forma == "numero":
        numero = evaluacion["esperado"]
        en_letras = {8: "ocho"}.get(numero, "")
        if str(numero) in tokens or en_letras in tokens:
            return CORRECTA
        return INCORRECTA

    if forma == "palabra":
        return CORRECTA if evaluacion["esperado"] in tokens else INCORRECTA

    # Debe decir que no esta en la base, sin inventar datos
    if forma == "no_registrado":
        inventa = mencionados & set(evaluacion.get("prohibido", []))
        return CORRECTA if "no" in tokens and not inventa else INCORRECTA

    raise ValueError(f"Forma de evaluacion desconocida: {forma}")


def texto_esperado(evaluacion):
    forma = evaluacion["forma"]
    if forma == "conjunto":
        return ", ".join(evaluacion["esperado"])
    if forma == "no_registrado":
        return "Indicar que no está registrado en la base"
    return str(evaluacion["esperado"])


# Ejecucion de cada chatbot


def responder_prolog(pregunta):
    if pregunta["prolog"] is None:
        return "(El menú no tiene una consulta para esta pregunta)", \
            SIN_RESPUESTA, None
    try:
        r = puente_prolog.consultar(
            pregunta["prolog"]["opcion"], pregunta["prolog"]["valores"]
        )
    except puente_prolog.ErrorProlog as error:
        return f"(Error: {error})", SIN_RESPUESTA, None
    veredicto = corregir(r["respuesta"], pregunta["evaluacion"])
    return r["respuesta"], veredicto, r["segundos"]


def responder_llm(pregunta):
    # Sin historial: cada pregunta es independiente
    try:
        r = chatbot_llm.preguntar(pregunta["pregunta"])
    except chatbot_llm.ErrorLLM as error:
        return f"(Error: {error})", SIN_RESPUESTA, None
    veredicto = corregir(r["respuesta"], pregunta["evaluacion"])
    return r["respuesta"], veredicto, r["segundos"]


# Reporte


def resumen(filas, chatbot):
    veredictos = [f[f"{chatbot}_veredicto"] for f in filas]
    tiempos = [
        f[f"{chatbot}_segundos"]
        for f in filas
        if f[f"{chatbot}_segundos"] is not None
    ]
    return {
        CORRECTA: veredictos.count(CORRECTA),
        PARCIAL: veredictos.count(PARCIAL),
        INCORRECTA: veredictos.count(INCORRECTA),
        SIN_RESPUESTA: veredictos.count(SIN_RESPUESTA),
        "exactitud": 100 * veredictos.count(CORRECTA) / len(veredictos),
        "tiempo": sum(tiempos) / len(tiempos) if tiempos else None,
    }


def celda(texto):
    return str(texto).replace("|", "\\|").replace("\n", " ").strip()


def escribir_markdown(filas, chatbots, ruta):
    nombres = {
        "prolog": "Prolog",
        "llm": f"LLM ({chatbot_llm.modelo_en_uso()})",
    }
    fecha = time.strftime("%d-%m-%Y %H:%M")
    lineas = [
        "# Evaluación comparativa de los chatbots (20 preguntas)",
        "",
        f"Fecha de ejecución: {fecha}",
        "",
        "## Resumen",
        "",
        "| Chatbot | Correctas | Parciales | Incorrectas | Sin respuesta "
        "| Exactitud | Tiempo promedio |",
        "|---|---|---|---|---|---|---|",
    ]
    for c in chatbots:
        r = resumen(filas, c)
        tiempo = f"{r['tiempo']:.2f} s" if r["tiempo"] is not None else "-"
        lineas.append(
            f"| {nombres[c]} | {r[CORRECTA]} | {r[PARCIAL]} "
            f"| {r[INCORRECTA]} | {r[SIN_RESPUESTA]} "
            f"| {r['exactitud']:.0f} % | {tiempo} |"
        )

    lineas += ["", "## Detalle por pregunta", ""]
    for f in filas:
        lineas += [
            f"### {f['id']}. {f['pregunta']}",
            "",
            f"- **Categoría:** {f['categoria']}",
            f"- **Respuesta esperada:** {f['esperado']}",
        ]
        for c in chatbots:
            segundos = f[c + "_segundos"]
            tiempo = f", {segundos} s" if segundos is not None else ""
            lineas.append(
                f"- **{nombres[c]}** ({f[c + '_veredicto']}{tiempo}): "
                f"{celda(f[c + '_respuesta'])}"
            )
        lineas.append("")
    lineas += [
        "> La corrección es automática (compara los pokémon y tipos "
        "nombrados en cada respuesta con los esperados).",
        "> Revisar manualmente las respuestas del LLM antes de usar "
        "estas cifras en el informe.",
        "",
    ]
    Path(ruta).write_text("\n".join(lineas), encoding="utf-8")


def escribir_csv(filas, chatbots, ruta):
    columnas = ["id", "categoria", "pregunta", "esperado"]
    for c in chatbots:
        columnas += [f"{c}_respuesta", f"{c}_veredicto", f"{c}_segundos"]
    with open(ruta, "w", newline="", encoding="utf-8-sig") as archivo:
        escritor = csv.DictWriter(
            archivo, fieldnames=columnas, delimiter=";", extrasaction="ignore"
        )
        escritor.writeheader()
        escritor.writerows(filas)


def main():
    # Evita errores de codificacion en la consola de Windows
    sys.stdout.reconfigure(errors="replace")
    parser = argparse.ArgumentParser(
        description="Evaluacion comparativa Prolog vs LLM"
    )
    parser.add_argument(
        "--solo-prolog", action="store_true", help="no consultar al LLM"
    )
    parser.add_argument(
        "--pausa",
        type=float,
        default=4,
        help="segundos de espera entre preguntas al LLM",
    )
    args = parser.parse_args()

    chatbots = ["prolog"] if args.solo_prolog else ["prolog", "llm"]
    if "llm" in chatbots and not chatbot_llm.token_configurado():
        raise SystemExit(
            "Falta el token del LLM en el archivo .env (LLM_API_KEY). "
            "Use --solo-prolog para omitirlo."
        )
    if not puente_prolog.disponible():
        print("Aviso: no se encontro SWI-Prolog; Prolog quedara sin "
              "evaluar.\n")

    ruta_preguntas = CARPETA / "preguntas.json"
    preguntas = json.loads(ruta_preguntas.read_text(encoding="utf-8"))
    filas = []
    for numero, pregunta in enumerate(preguntas, 1):
        print(f"[{numero}/{len(preguntas)}] {pregunta['pregunta']}")
        fila = {
            "id": pregunta["id"],
            "categoria": pregunta["categoria"],
            "pregunta": pregunta["pregunta"],
            "esperado": texto_esperado(pregunta["evaluacion"]),
        }
        respuesta, veredicto, segundos = responder_prolog(pregunta)
        fila["prolog_respuesta"] = respuesta
        fila["prolog_veredicto"] = veredicto
        fila["prolog_segundos"] = segundos
        print(f"    Prolog -> {veredicto}")
        if "llm" in chatbots:
            respuesta, veredicto, segundos = responder_llm(pregunta)
            fila["llm_respuesta"] = respuesta
            fila["llm_veredicto"] = veredicto
            fila["llm_segundos"] = segundos
            print(f"    LLM    -> {veredicto}")
            # Respeta el limite por minuto del plan gratuito
            if numero < len(preguntas):
                time.sleep(args.pausa)
        filas.append(fila)

    escribir_markdown(filas, chatbots, CARPETA / "resultados_evaluacion.md")
    escribir_csv(filas, chatbots, CARPETA / "resultados_evaluacion.csv")
    datos = {"chatbots": chatbots, "modelo": chatbot_llm.modelo_en_uso(),
             "filas": filas}
    (CARPETA / "resultados_evaluacion.json").write_text(
        json.dumps(datos, ensure_ascii=False, indent=1), encoding="utf-8"
    )

    print("\nRESUMEN")
    for c in chatbots:
        r = resumen(filas, c)
        print(
            f"  {c:<7} correctas: {r[CORRECTA]}/{len(filas)}  "
            f"parciales: {r[PARCIAL]}  incorrectas: {r[INCORRECTA]}  "
            f"sin respuesta: {r[SIN_RESPUESTA]}"
        )
    print("\nArchivos: resultados_evaluacion.md, .csv y .json")


if __name__ == "__main__":
    main()
