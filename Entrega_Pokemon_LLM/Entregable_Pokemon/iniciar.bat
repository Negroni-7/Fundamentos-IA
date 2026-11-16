@echo off
rem Instala Python y SWI-Prolog si faltan y levanta la aplicacion
setlocal EnableExtensions
title Chatbot Pokemon Kanto
cd /d "%~dp0"

echo ==================================================
echo   Chatbot Pokemon Kanto - instalacion y arranque
echo ==================================================
echo.

if not exist "app.py" goto falta_descomprimir

rem ---------- 1. Python ---------------------------------------------------
call :buscar_python
if defined PYEXE goto python_listo

echo [1/4] Python no esta instalado. Instalando Python 3.13...
where winget >nul 2>&1
if errorlevel 1 goto python_manual
winget install -e --id Python.Python.3.13 --accept-package-agreements --accept-source-agreements
call :buscar_python
if not defined PYEXE goto python_manual

:python_listo
echo [1/4] Python listo: %PYEXE% %PYARG%

rem ---------- 2. SWI-Prolog -----------------------------------------------
call :buscar_swipl
if defined SWIPL_PATH goto prolog_listo

echo [2/4] SWI-Prolog no esta instalado. Instalando...
echo       Windows puede pedir permiso de administrador: acepte para continuar.
where winget >nul 2>&1
if errorlevel 1 goto prolog_manual
winget install -e --id SWI-Prolog.SWI-Prolog --accept-package-agreements --accept-source-agreements
call :buscar_swipl
if not defined SWIPL_PATH goto prolog_manual

:prolog_listo
echo [2/4] SWI-Prolog listo: %SWIPL_PATH%
goto dependencias

:prolog_manual
echo.
echo AVISO: no se pudo instalar SWI-Prolog automaticamente.
echo        Puede instalarlo desde https://www.swi-prolog.org/download/stable
echo        La aplicacion se abrira igual, pero solo funcionara el chatbot LLM.
echo.

rem ---------- 3. Entorno virtual y dependencias ---------------------------
rem El entorno va en una ruta corta: las rutas largas de Windows danan pip
:dependencias
set "VENV=%LOCALAPPDATA%\PokemonKanto\venv"
"%VENV%\Scripts\python.exe" -m pip --version >nul 2>&1
if not errorlevel 1 goto instalar_dependencias
echo [3/4] Creando entorno virtual...
if exist "%VENV%" rmdir /s /q "%VENV%"
"%PYEXE%" %PYARG% -m venv "%VENV%"
"%VENV%\Scripts\python.exe" -m pip --version >nul 2>&1
if errorlevel 1 goto error_venv

:instalar_dependencias
echo [3/4] Instalando dependencias (requiere internet la primera vez)...
"%VENV%\Scripts\python.exe" -m pip install -q --disable-pip-version-check -r requirements.txt >"%TEMP%\pip_pokemon.log" 2>&1
if not errorlevel 1 goto dependencias_listas
if defined REINTENTO goto error_dependencias
set "REINTENTO=1"
echo       Fallo la instalacion. Recreando el entorno virtual...
if exist "%VENV%" rmdir /s /q "%VENV%"
goto dependencias

:dependencias_listas
if not exist ".env" copy ".env.example" ".env" >nul

rem ---------- 4. Aplicacion -----------------------------------------------
echo [4/4] Iniciando la aplicacion...
echo.
echo   La pagina se abrira sola en el navegador (http://127.0.0.1:5000).
echo   Para detener la aplicacion cierre esta ventana o presione Ctrl + C.
echo.
"%VENV%\Scripts\python.exe" app.py
echo.
echo La aplicacion se detuvo.
pause
exit /b 0

rem ======================= Mensajes de error ==============================
:falta_descomprimir
echo No se encontro app.py junto a este archivo.
echo Descomprima primero el .zip completo y ejecute iniciar.bat desde la carpeta descomprimida.
pause
exit /b 1

:python_manual
echo.
echo No se pudo instalar Python automaticamente (este equipo no tiene winget o la instalacion fallo).
echo Se abrira la pagina de descarga: instale Python marcando "Add python.exe to PATH"
echo y luego vuelva a ejecutar iniciar.bat.
start "" "https://www.python.org/downloads/"
pause
exit /b 1

:error_venv
echo.
echo No se pudo crear el entorno virtual en %VENV%
echo Detalle: ejecute manualmente  "%PYEXE%" %PYARG% -m venv "%VENV%"
pause
exit /b 1

:error_dependencias
echo.
echo No se pudieron instalar las dependencias. Detalle del error:
echo.
type "%TEMP%\pip_pokemon.log"
echo.
echo Revise la conexion a internet y vuelva a ejecutar iniciar.bat.
pause
exit /b 1

rem ======================= Subrutinas =====================================
rem Busca un Python 3.9+ que funcione ("where python" no basta: Windows trae un acceso falso)
:buscar_python
set "PYEXE="
set "PYARG="
call :probar_python py -3
if defined PYEXE goto :eof
call :probar_python python
if defined PYEXE goto :eof
for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python3*") do call :probar_python "%%D\python.exe"
if defined PYEXE goto :eof
for /d %%D in ("%ProgramFiles%\Python3*") do call :probar_python "%%D\python.exe"
goto :eof

:probar_python
"%~1" %2 -c "import sys; raise SystemExit(sys.version_info < (3, 9))" >nul 2>&1
if errorlevel 1 goto :eof
set "PYEXE=%~1"
set "PYARG=%2"
goto :eof

rem Guarda la ruta de swipl.exe en SWIPL_PATH
:buscar_swipl
set "SWIPL_PATH="
for /f "delims=" %%P in ('where swipl 2^>nul') do if not defined SWIPL_PATH set "SWIPL_PATH=%%P"
if defined SWIPL_PATH goto :eof
for %%R in ("%ProgramFiles%\swipl\bin\swipl.exe" "%ProgramFiles(x86)%\swipl\bin\swipl.exe" "%LOCALAPPDATA%\Programs\swipl\bin\swipl.exe") do if not defined SWIPL_PATH if exist %%R set "SWIPL_PATH=%%~R"
goto :eof
