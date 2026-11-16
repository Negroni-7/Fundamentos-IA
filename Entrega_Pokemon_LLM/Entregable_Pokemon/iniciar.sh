#!/usr/bin/env bash
# Instala Python y SWI-Prolog si faltan y levanta la aplicacion
# Uso: ./iniciar.sh
cd "$(dirname "$0")" || exit 1

echo "=================================================="
echo "  Chatbot Pokemon Kanto - instalacion y arranque"
echo "=================================================="
echo

# Gestor de paquetes
GESTOR=""
for g in pacman apt-get dnf zypper brew; do
    if command -v "$g" >/dev/null 2>&1; then GESTOR="$g"; break; fi
done
SUDO=""
if [ "$(id -u)" -ne 0 ] && [ "$GESTOR" != "brew" ]; then SUDO="sudo"; fi

instalar() {  # $1 = python | venv | prolog
    echo "      (puede pedir la clave de administrador)"
    case "$GESTOR:$1" in
        pacman:python|pacman:venv)  $SUDO pacman -S --needed python ;;
        pacman:prolog)              $SUDO pacman -S --needed swi-prolog ;;
        apt-get:python|apt-get:venv) $SUDO apt-get update && $SUDO apt-get install -y python3 python3-venv python3-pip ;;
        apt-get:prolog)             $SUDO apt-get update && $SUDO apt-get install -y swi-prolog-core ;;
        dnf:python|dnf:venv)        $SUDO dnf install -y python3 python3-pip ;;
        dnf:prolog)                 $SUDO dnf install -y pl ;;
        zypper:python|zypper:venv)  $SUDO zypper --non-interactive install python3 python3-pip ;;
        zypper:prolog)              $SUDO zypper --non-interactive install swi-prolog ;;
        brew:python|brew:venv)      brew install python ;;
        brew:prolog)                brew install swi-prolog ;;
        *) echo "      No se reconocio el gestor de paquetes de este sistema."; return 1 ;;
    esac
}

python_ok() { command -v python3 >/dev/null 2>&1 && python3 -c 'import sys; raise SystemExit(sys.version_info < (3, 9))' 2>/dev/null; }

# --- 1. Python -------------------------------------------------------------
if ! python_ok; then
    echo "[1/4] Python 3 no esta instalado. Instalando..."
    instalar python
    if ! python_ok; then
        echo "No se pudo instalar Python 3.9 o superior. Instalelo manualmente y vuelva a ejecutar ./iniciar.sh"
        exit 1
    fi
fi
echo "[1/4] Python listo: $(python3 --version 2>&1)"

# --- 2. SWI-Prolog ---------------------------------------------------------
if ! command -v swipl >/dev/null 2>&1; then
    echo "[2/4] SWI-Prolog no esta instalado. Instalando..."
    instalar prolog
fi
if command -v swipl >/dev/null 2>&1; then
    echo "[2/4] SWI-Prolog listo: $(command -v swipl)"
else
    echo "AVISO: no se pudo instalar SWI-Prolog. La aplicacion se abrira igual,"
    echo "       pero solo funcionara el chatbot LLM."
fi

# --- 3. Entorno virtual y dependencias -------------------------------------
# Entorno virtual: Arch, Debian y Ubuntu bloquean pip en el Python del sistema
if ! .venv/bin/python -c 'import pip' >/dev/null 2>&1; then
    echo "[3/4] Creando entorno virtual..."
    rm -rf .venv
    if ! python3 -m venv .venv >/dev/null 2>&1; then
        echo "      Falta el modulo venv de Python. Instalando..."
        rm -rf .venv
        instalar venv
        python3 -m venv .venv || { echo "No se pudo crear el entorno virtual."; exit 1; }
    fi
fi
echo "[3/4] Instalando dependencias (requiere internet la primera vez)..."
if ! SALIDA=$(.venv/bin/python -m pip install -q --disable-pip-version-check -r requirements.txt 2>&1); then
    echo "No se pudieron instalar las dependencias. Detalle del error:"
    echo "$SALIDA"
    echo "Revise la conexion a internet y vuelva a ejecutar el instalador."
    exit 1
fi

[ -f .env ] || cp .env.example .env

# --- 4. Aplicacion ---------------------------------------------------------
echo "[4/4] Iniciando la aplicacion..."
echo
echo "  La pagina se abrira sola en el navegador (http://127.0.0.1:5000)."
echo "  Para detener la aplicacion presione Ctrl + C."
echo
exec .venv/bin/python app.py
