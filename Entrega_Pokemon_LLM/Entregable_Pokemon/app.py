# Interfaz web (Flask). Ejecutar: python app.py

import os
import threading
import webbrowser

from flask import Flask, jsonify, request, send_from_directory

import chatbot_llm
import puente_prolog

app = Flask(__name__, static_folder="static")
_opciones = []


@app.get("/")
def inicio():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/api/estado")
def estado():
    global _opciones
    error_prolog = None
    # El menu de Prolog se lee una sola vez
    if not _opciones:
        try:
            _opciones = puente_prolog.listar_opciones()
        except puente_prolog.ErrorProlog as error:
            error_prolog = str(error)
    opciones = _opciones
    return jsonify({
        "prolog": {
            "disponible": bool(opciones),
            "error": error_prolog,
            "opciones": opciones,
        },
        "llm": {
            "token_configurado": bool(chatbot_llm.token_configurado()),
            "modelo": chatbot_llm.modelo_en_uso(),
        },
    })


@app.post("/api/prolog")
def api_prolog():
    datos = request.get_json(silent=True) or {}
    try:
        resultado = puente_prolog.consultar(
            datos.get("opcion"), datos.get("valores") or []
        )
    except (TypeError, ValueError):
        return jsonify({"error": "Opcion no valida."}), 400
    except puente_prolog.ErrorProlog as error:
        return jsonify({"error": str(error)}), 503
    return jsonify(resultado)


@app.post("/api/llm")
def api_llm():
    datos = request.get_json(silent=True) or {}
    historial = datos.get("historial")
    if not isinstance(historial, list):
        historial = []
    historial = [t for t in historial if isinstance(t, dict)]
    # Token ingresado en la pagina (opcional)
    token = request.headers.get("X-LLM-Token", "")
    try:
        resultado = chatbot_llm.preguntar(
            datos.get("mensaje", ""), historial, token
        )
    except chatbot_llm.ErrorLLM as error:
        return jsonify({"error": str(error)}), 400
    return jsonify(resultado)


if __name__ == "__main__":
    puerto = int(os.getenv("PORT", "5000"))
    url = f"http://127.0.0.1:{puerto}"
    print(f"\n  Chatbot Pokemon Kanto disponible en {url}\n")
    # Abre el navegador cuando el servidor ya esta arriba
    if os.getenv("ABRIR_NAVEGADOR", "1") == "1":
        threading.Timer(1.5, webbrowser.open, args=(url,)).start()
    app.run(host="127.0.0.1", port=puerto, debug=False)
