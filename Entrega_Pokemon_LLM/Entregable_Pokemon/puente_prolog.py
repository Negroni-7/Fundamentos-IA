# Puente Python -> Prolog: ejecuta Codigo_Prolog/puente_web.pl con swipl

import os
import re
import shutil
import subprocess
import time
import unicodedata
from pathlib import Path

CARPETA_PROLOG = Path(__file__).parent / "Codigo_Prolog"
SCRIPT = CARPETA_PROLOG / "puente_web.pl"

_RUTAS_WINDOWS = [
    r"C:\Program Files\swipl\bin\swipl.exe",
    r"C:\Program Files (x86)\swipl\bin\swipl.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Programs\swipl\bin\swipl.exe"),
]


class ErrorProlog(Exception):
    # Error con mensaje apto para mostrar al usuario
    pass


def ruta_swipl():
    # Busca swipl en SWIPL_PATH, en el PATH y en rutas tipicas de Windows
    candidatos = [os.getenv("SWIPL_PATH"), shutil.which("swipl")]
    candidatos += _RUTAS_WINDOWS
    for candidato in candidatos:
        if candidato and Path(candidato).exists():
            return candidato
    return None


def disponible():
    return ruta_swipl() is not None and SCRIPT.exists()


def normalizar(texto):
    # Minusculas, sin tildes y solo ASCII
    sin_tildes = unicodedata.normalize("NFKD", str(texto))
    sin_tildes = sin_tildes.encode("ascii", "ignore").decode("ascii")
    return sin_tildes.lower().strip()


def _argumento(texto):
    # Deja solo letras, digitos y espacios para pasarlo a swipl
    limpio = re.sub(r"[^a-z0-9 ]", " ", normalizar(texto)).strip()
    return limpio[:60] or "vacio"


def _ejecutar(argumentos):
    swipl = ruta_swipl()
    if not swipl:
        raise ErrorProlog(
            "No se encontro SWI-Prolog (swipl). Instalelo o defina "
            "SWIPL_PATH en el archivo .env."
        )
    try:
        proceso = subprocess.run(
            [swipl, "-q", str(SCRIPT), *argumentos],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=15,
            cwd=CARPETA_PROLOG,
        )
    except subprocess.TimeoutExpired:
        raise ErrorProlog("Prolog tardo demasiado en responder.")
    return proceso.returncode, proceso.stdout.strip()


def listar_opciones():
    # Devuelve el menu leido desde opcion/5 de chatbot.pl
    codigo, salida = _ejecutar(["opciones"])
    if codigo != 0:
        raise ErrorProlog("No se pudo leer el menu desde Prolog.")
    opciones = []
    for linea in salida.splitlines():
        partes = linea.split("|")
        if len(partes) != 4:
            continue
        numero, categoria, texto, entradas = partes
        opciones.append({
            "numero": int(numero),
            "categoria": categoria,
            "texto": texto,
            "entradas": [
                dict(zip(("clase", "etiqueta"), e.split("=", 1)))
                for e in entradas.split(";") if e
            ],
        })
    return opciones


def consultar(numero, valores=()):
    # Ejecuta la opcion del menu. valida=False si Prolog rechazo la entrada
    argumentos = ["consultar", str(int(numero))]
    argumentos += [_argumento(v) for v in valores]
    inicio = time.time()
    codigo, salida = _ejecutar(argumentos)
    if codigo not in (0, 2) or not salida:
        raise ErrorProlog("Prolog no pudo responder la consulta.")
    return {
        "respuesta": salida,
        "valida": codigo == 0,
        "segundos": round(time.time() - inicio, 2),
    }
