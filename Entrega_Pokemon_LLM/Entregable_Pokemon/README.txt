CHATBOT POKÉMON KANTO - Proyecto 2, Fundamentos de IA (UNAB)
============================================================

Dos chatbots sobre la misma base de conocimiento: uno en Prolog y otro
con un LLM, más una interfaz web y una evaluación con 20 preguntas.

REQUISITOS
----------
- Conexión a internet (el LLM se usa por internet; no se descarga nada).
- Un token gratuito de Groq (ver paso 1).
- Python 3.9 o superior y SWI-Prolog: si no están instalados, el
  instalador (paso 2) los instala solo.

INSTRUCCIONES PARA EJECUTAR
---------------------------
1. Obtener el token gratuito
   - Entrar a https://console.groq.com y crear una cuenta (sin tarjeta).
   - Ir a "API Keys" -> "Create API Key" y copiar la clave (gsk_...).

2. Ejecutar el instalador (descomprimir el .zip antes, en una carpeta de
   ruta corta, por ejemplo C:\Pokemon)
   - Windows: doble clic en iniciar.bat
              (aceptar el permiso de administrador al instalar Prolog).
   - Linux / macOS: abrir una terminal en la carpeta y ejecutar
              ./iniciar.sh
              (si no tiene permiso: bash iniciar.sh).
   El instalador revisa Python y SWI-Prolog, instala lo que falte, crea
   el entorno virtual (en Windows: %LOCALAPPDATA%\PokemonKanto\venv; en
   Linux/macOS: .venv), instala las dependencias, levanta la
   aplicación y abre el navegador en http://127.0.0.1:5000
   Las siguientes veces parte directo.

3. Usar la aplicación en el navegador
   - Pestaña "Chatbot Prolog": elegir una consulta del menú y escribir
     el pokémon o tipo.
   - Pestaña "Chatbot LLM": pegar el token en el campo de arriba y
     escribir una pregunta libre.
   - Para detener la aplicación: Ctrl + C en la ventana del instalador.

4. (Opcional) Dejar el token fijo para todos los usuarios
   - Escribirlo en LLM_API_KEY= dentro del archivo .env (el instalador
     lo crea la primera vez):
     LLM_API_KEY=gsk_su_token
   - También se acepta en .env.example si .env no tiene token.
   - Quien reciba la carpeta con el token adentro podrá usarlo: quitarlo
     de .env y .env.example antes de compartirla.

OTRAS FORMAS DE EJECUTAR
------------------------
Usar siempre el Python del entorno virtual creado por el instalador:

Chatbot Prolog por consola (desde la carpeta Codigo_Prolog):
    swipl chatbot.pl
    ?- main.

Chatbot LLM por consola (necesita el token en .env):
    %LOCALAPPDATA%\PokemonKanto\venv\Scripts\python chatbot_llm.py   (Windows)
    .venv/bin/python chatbot_llm.py              (Linux / macOS)

Evaluación de las 20 preguntas (necesita el token en .env):
    %LOCALAPPDATA%\PokemonKanto\venv\Scripts\python evaluacion.py    (Windows)
    .venv/bin/python evaluacion.py               (Linux / macOS)
  Genera resultados_evaluacion.md y resultados_evaluacion.csv.
  Tarda un par de minutos por el límite por minuto del plan gratuito.
  Si aparece el aviso de límite de uso, repetir con: evaluacion.py --pausa 10
  Para evaluar solo Prolog (sin token): evaluacion.py --solo-prolog

SIN USAR EL INSTALADOR (revisión sin ejecutar iniciar.bat ni iniciar.sh)
-----------------------------------------------------------------------
Los instaladores son archivos de texto: se pueden abrir con el Bloc de
notas y leer antes de ejecutarlos. Solo instalan Python y SWI-Prolog con
winget (el instalador oficial de Windows) y las dependencias de
requirements.txt. Quien prefiera no ejecutarlos puede hacerlo a mano:

A) Aplicación web completa
   1. Instalar Python 3.9+ (https://www.python.org/downloads/, marcando
      "Add python.exe to PATH") y SWI-Prolog
      (https://www.swi-prolog.org/download/stable).
   2. Abrir una terminal (cmd) en esta carpeta y ejecutar, línea por línea:
      Windows:
        python -m venv %LOCALAPPDATA%\PokemonKanto\venv
        %LOCALAPPDATA%\PokemonKanto\venv\Scripts\pip install -r requirements.txt
        %LOCALAPPDATA%\PokemonKanto\venv\Scripts\python app.py
      Linux / macOS:
        python3 -m venv .venv
        .venv/bin/pip install -r requirements.txt
        .venv/bin/python app.py
   3. Abrir http://127.0.0.1:5000 (el token se toma de .env.example).

B) Solo el chatbot Prolog (no necesita Python ni internet)
   1. Instalar SWI-Prolog.
   2. Abrir una terminal en la carpeta Codigo_Prolog y ejecutar:
        swipl chatbot.pl
        ?- main.

C) Solo revisar el código
   Todo el código fuente está en texto plano: Codigo_Prolog/ (Prolog),
   chatbot_llm.py, app.py, puente_prolog.py, evaluacion.py y
   static/index.html. No hay ejecutables ni archivos compilados.

SOLUCIÓN DE PROBLEMAS
---------------------
- "Falta el token del LLM": pegar el token en la página o en .env.
- "El token del LLM no es válido": revisar que esté completo (gsk_...).
- "Se alcanzó el límite de uso gratuito": esperar un minuto y reintentar.
- La página avisa que Prolog no está disponible: instalar SWI-Prolog
  (https://www.swi-prolog.org/download/stable) y volver a ejecutar el
  instalador. Si está en una ruta poco común, escribirla en .env:
  SWIPL_PATH=C:\ruta\a\swipl.exe
- Windows sin winget: el instalador abre la página de descarga de Python;
  instalarlo marcando "Add python.exe to PATH" y ejecutar de nuevo.
- Cambiar el puerto (por defecto 5000): definir la variable PORT.

ARCHIVOS
--------
iniciar.bat / iniciar.sh   Instalador y lanzador (Windows / Linux, macOS)
app.py                     Servidor web (Flask)
static/index.html          Página web
chatbot_llm.py             Chatbot con LLM (punto 4)
puente_prolog.py           Conexión Python -> Prolog
evaluacion.py              Evaluación comparativa (punto 6)
preguntas.json             Las 20 preguntas con su respuesta esperada
requirements.txt           Dependencias de Python
.env.example               Plantilla de configuración (token)
Codigo_Prolog/
    base_conocimiento.pl   Hechos y reglas (entrega 1)
    chatbot.pl             Chatbot en Prolog con menú (entrega 1)
    puente_web.pl          Puente que usa la interfaz web

LÍMITES DEL PLAN GRATUITO
-------------------------
Groq limita las solicitudes y los tokens por minuto y por día. Si se
alcanza el límite, la aplicación espera y reintenta; si persiste, muestra
un aviso. El modelo por defecto es openai/gpt-oss-120b; se puede cambiar
con LLM_MODEL en .env.

INFORME DE DESEMPENO (punto 6.b)
--------------------------------
  pip install python-docx
  python evaluacion.py          (consulta ambos chatbots, ~2 min)
  python generar_informe.py     (crea Informe_Desempeno.docx)
Revise a mano las respuestas del LLM antes de entregar.
