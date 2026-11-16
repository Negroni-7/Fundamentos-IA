# Genera Informe_Desempeno.docx a partir de resultados_evaluacion.json
#
# python evaluacion.py        (genera el json con ambos chatbots)
# python generar_informe.py   (requiere: pip install python-docx)
#
# Opcional: analisis_manual.txt y conclusiones_manual.txt (parrafos
# separados por linea en blanco) se agregan al informe.
#
# Si el json solo tiene Prolog, la seccion del LLM queda marcada
# como pendiente.

import json
import sys
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt

CARPETA = Path(__file__).parent
SALIDA = CARPETA / "Informe_Desempeno.docx"

INTEGRANTES = [
    "Martín Araneda Aceituno",
    "Stefano Negroni Postiglione",
    "Isabella Quintero González",
]
FECHA = "15 de noviembre de 2026"

PROPUESTAS = [
    (
        "Chatbot híbrido (Prolog + LLM)",
        "El LLM solo interpreta la pregunta y extrae pokémon, tipos y "
        "opción del menú; la respuesta la calcula Prolog. Se combina la "
        "comprensión del lenguaje natural del LLM con la exactitud de la "
        "base de conocimiento. Se implementa en app.py (nuevo endpoint) "
        "reutilizando puente_prolog.consultar().",
    ),
    (
        "Cálculo de efectividad combinada",
        "Reglas Prolog que combinen ventajas, resistencias e inmunidades "
        "de los dos tipos de un pokémon (x4, x2, x1, x0.5, x0.25, x0). "
        "Se agregan en base_conocimiento.pl y se expone una opción nueva "
        "en el menú de chatbot.pl y puente_web.pl.",
    ),
    (
        "RAG para una base de conocimiento mayor",
        "Hoy toda la base (~5000 caracteres) cabe en el prompt. Con las "
        "151 especies o más se deben recuperar solo los hechos relevantes "
        "a cada pregunta (búsqueda por coincidencia de nombres o "
        "embeddings) antes de llamar al LLM. Se cambia construir_contexto() "
        "en chatbot_llm.py.",
    ),
    (
        "Comprensión de preguntas compuestas con DCG",
        "Una gramática DCG en Prolog permitiría interpretar frases como "
        "«agua y psíquico» (pregunta 19), que el menú actual no soporta. "
        "Se agrega un módulo nuevo en Codigo_Prolog y se conecta en "
        "puente_web.pl.",
    ),
    (
        "Rendimiento del puente Prolog",
        "Cada consulta lanza un proceso swipl nuevo. Mantener un proceso "
        "persistente (o usar janus/pyswip) elimina el tiempo de arranque "
        "en puente_prolog.py.",
    ),
    (
        "Evaluación más robusta",
        "Ampliar de 20 a 50 o más preguntas, repetir cada pregunta varias "
        "veces con el LLM y añadir revisión humana además de la corrección "
        "automática de evaluacion.py.",
    ),
    (
        "Despliegue y limpieza",
        "Publicar la aplicación en un servicio con la clave en variables "
        "de entorno (no en el repositorio) y eliminar la definición "
        "duplicada de leer_linea/1 entre base_conocimiento.pl y "
        "chatbot.pl.",
    ),
]


def cargar():
    ruta = CARPETA / "resultados_evaluacion.json"
    if not ruta.exists():
        raise SystemExit("Falta resultados_evaluacion.json: ejecute "
                         "primero python evaluacion.py")
    return json.loads(ruta.read_text(encoding="utf-8"))


def resumen(filas, c):
    v = [f[f"{c}_veredicto"] for f in filas]
    t = [f[f"{c}_segundos"] for f in filas if f[f"{c}_segundos"] is not None]
    return {
        "Correcta": v.count("Correcta"),
        "Parcial": v.count("Parcial"),
        "Incorrecta": v.count("Incorrecta"),
        "Sin respuesta": v.count("Sin respuesta"),
        "tiempo": sum(t) / len(t) if t else None,
        "total": len(v),
    }


def texto_manual(nombre):
    # Parrafos redactados a mano (separados por linea en blanco)
    ruta = CARPETA / nombre
    if not ruta.exists():
        return []
    texto = ruta.read_text(encoding="utf-8").strip()
    return [p.strip() for p in texto.split("\n\n") if p.strip()]


def parrafo(doc, texto, negrita=False, tam=11):
    p = doc.add_paragraph()
    run = p.add_run(texto)
    run.bold = negrita
    run.font.size = Pt(tam)
    p.paragraph_format.space_after = Pt(6)
    return p


def viñetas(doc, items):
    for item in items:
        doc.add_paragraph(item, style="List Bullet")


def tabla(doc, encabezado, filas, tam=9):
    t = doc.add_table(rows=1, cols=len(encabezado))
    t.style = "Table Grid"
    for i, texto in enumerate(encabezado):
        celda = t.rows[0].cells[i]
        celda.text = ""
        run = celda.paragraphs[0].add_run(texto)
        run.bold = True
        run.font.size = Pt(tam)
    for fila in filas:
        celdas = t.add_row().cells
        for i, texto in enumerate(fila):
            celdas[i].text = ""
            celdas[i].paragraphs[0].add_run(str(texto)).font.size = Pt(tam)
    doc.add_paragraph()


def portada(doc):
    for texto, tam, negrita in [
        ("Universidad Andrés Bello", 16, True),
        ("Facultad de Ingeniería", 13, False),
        ("Fundamentos de Inteligencia Artificial (8329)", 13, False),
        ("", 11, False),
        ("Proyecto 2 – Entrega 2", 20, True),
        ("Chatbot Pokémon Kanto: versión Prolog y versión LLM", 14, False),
        ("Informe de análisis de desempeño", 14, True),
        ("", 11, False),
        ("Docente: Jacqueline Kohler Casasempere", 12, False),
        ("Estudiantes: " + "; ".join(INTEGRANTES), 12, False),
        ("Santiago de Chile, " + FECHA, 12, False),
    ]:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(texto)
        r.bold = negrita
        r.font.size = Pt(tam)
    doc.add_page_break()


def analisis(doc, filas, tiene_llm, modelo):
    rp = resumen(filas, "prolog")
    n = rp["total"]
    parrafo(
        doc,
        f"Prolog respondió correctamente {rp['Correcta']} de {n} preguntas "
        f"({100 * rp['Correcta'] / n:.0f} %), con un tiempo promedio de "
        f"{rp['tiempo']:.2f} s por consulta (incluye el arranque del "
        "intérprete SWI-Prolog). Las respuestas sin acierto corresponden "
        "a preguntas que el menú no contempla.",
    )
    fallas = [f for f in filas if f["prolog_veredicto"] != "Correcta"]
    if fallas:
        viñetas(doc, [
            f"Pregunta {f['id']} ({f['pregunta']}): {f['prolog_veredicto']}"
            for f in fallas
        ])
    if not tiene_llm:
        parrafo(
            doc,
            "[PENDIENTE] Los resultados de la versión LLM no están en "
            "este archivo. Ejecute python evaluacion.py con el token "
            "configurado y vuelva a generar el informe.",
            negrita=True,
        )
        return
    rl = resumen(filas, "llm")
    parrafo(
        doc,
        f"El LLM ({modelo}) respondió correctamente {rl['Correcta']} de "
        f"{n} preguntas ({100 * rl['Correcta'] / n:.0f} %), con "
        f"{rl['Parcial']} parciales, {rl['Incorrecta']} incorrecta(s) y "
        f"{rl['Sin respuesta']} sin respuesta. Su tiempo promedio fue "
        f"{rl['tiempo']:.2f} s." if rl["tiempo"] is not None else
        f"El LLM no entregó respuestas válidas ({rl['Sin respuesta']} "
        "sin respuesta).",
    )
    fallas = [f for f in filas if f["llm_veredicto"] != "Correcta"]
    if fallas:
        parrafo(doc, "Preguntas donde el LLM no acertó por completo:")
        viñetas(doc, [
            f"Pregunta {f['id']} ({f['pregunta']}): {f['llm_veredicto']}. "
            f"Esperado: {f['esperado']}."
            for f in fallas
        ])
    ventaja = [f for f in filas
               if f["prolog_veredicto"] != "Correcta"
               and f["llm_veredicto"] == "Correcta"]
    if ventaja:
        parrafo(doc, "Preguntas que solo el LLM resolvió: "
                + ", ".join(str(f["id"]) for f in ventaja) + ".")


def main():
    datos = cargar()
    filas = datos["filas"]
    tiene_llm = "llm" in datos["chatbots"]
    modelo = datos.get("modelo", "")
    doc = Document()
    doc.styles["Normal"].font.name = "Calibri"
    doc.styles["Normal"].font.size = Pt(11)
    portada(doc)

    doc.add_heading("1. Introducción", 1)
    parrafo(
        doc,
        "Este informe compara dos versiones del chatbot de dominio "
        "Pokémon (región de Kanto): la versión Prolog de la entrega 1, "
        "basada en una base de conocimiento lógica y un menú de consultas, "
        "y la versión con LLM de la entrega 2, que usa un modelo de "
        "lenguaje de capa gratuita (Groq) al que se le entrega la misma "
        "base de conocimiento como contexto. Ambas se usan desde una "
        "interfaz web simple.",
    )

    doc.add_heading("2. Descripción de las versiones", 1)
    parrafo(doc, "Versión Prolog", negrita=True)
    viñetas(doc, [
        "40 pokémon, 18 tipos, 13 cadenas evolutivas y 22 opciones de menú.",
        "Respuestas deterministas calculadas por inferencia lógica.",
        "Entrada limitada: el usuario elige una opción y entrega los datos "
        "(pokémon, tipo) que el menú pide.",
    ])
    parrafo(doc, "Versión LLM", negrita=True)
    viñetas(doc, [
        f"Modelo {modelo or 'openai/gpt-oss-120b'} vía API de Groq, "
        "temperatura 0.",
        "La base de conocimiento se extrae de base_conocimiento.pl y se "
        "inyecta en el prompt del sistema junto con reglas de mundo "
        "cerrado (no inventar datos).",
        "Acepta preguntas en lenguaje natural libre.",
    ])
    parrafo(doc, "Interfaz web", negrita=True)
    parrafo(
        doc,
        "Servidor Flask con una página estática de dos pestañas (Prolog y "
        "LLM). El token del LLM se lee del archivo .env o se ingresa en "
        "la página.",
    )

    doc.add_heading("3. Metodología", 1)
    parrafo(
        doc,
        "Se definió un conjunto de 20 preguntas del dominio "
        "(preguntas.json): 18 cubiertas por el menú Prolog, una pregunta "
        "compuesta que el menú no soporta (agua y psíquico) y una sobre un "
        "pokémon fuera de la base (Eevee). Cada pregunta se hizo a ambos "
        "chatbots con evaluacion.py, sin historial de conversación. Las "
        "respuestas se clasifican automáticamente como Correcta, Parcial, "
        "Incorrecta o Sin respuesta comparando los pokémon y tipos "
        "nombrados con los esperados. Los tiempos incluyen toda la "
        "consulta (arranque de Prolog o llamada de red al LLM).",
    )

    doc.add_heading("4. Resultados", 1)
    doc.add_heading("4.1 Resumen", 2)
    encabezado = ["Chatbot", "Correctas", "Parciales", "Incorrectas",
                  "Sin respuesta", "Tiempo promedio"]
    cuerpo = []
    for c, nombre in [("prolog", "Prolog"), ("llm", f"LLM ({modelo})")]:
        if c not in datos["chatbots"]:
            cuerpo.append([nombre, "-", "-", "-", "-", "pendiente"])
            continue
        r = resumen(filas, c)
        t = f"{r['tiempo']:.2f} s" if r["tiempo"] is not None else "-"
        cuerpo.append([nombre, r["Correcta"], r["Parcial"],
                       r["Incorrecta"], r["Sin respuesta"], t])
    tabla(doc, encabezado, cuerpo)

    doc.add_heading("4.2 Las 20 preguntas y las respuestas de cada versión",
                    2)
    for f in filas:
        doc.add_heading(f"Pregunta {f['id']}: {f['pregunta']}", 3)
        cuerpo = [["Categoría", f["categoria"]],
                  ["Respuesta esperada", f["esperado"]],
                  ["Prolog (" + f["prolog_veredicto"] + ")",
                   f["prolog_respuesta"]]]
        if tiene_llm:
            cuerpo.append(["LLM (" + f["llm_veredicto"] + ")",
                           f["llm_respuesta"]])
        else:
            cuerpo.append(["LLM", "[PENDIENTE: ejecutar evaluacion.py]"])
        tabla(doc, ["Campo", "Contenido"], cuerpo, tam=9)

    doc.add_heading("5. Análisis de desempeño", 1)
    analisis(doc, filas, tiene_llm, modelo)
    for texto in texto_manual("analisis_manual.txt"):
        parrafo(doc, texto)

    doc.add_heading("6. Fortalezas y debilidades", 1)
    doc.add_heading("6.1 Versión Prolog", 2)
    parrafo(doc, "Fortalezas", negrita=True)
    viñetas(doc, [
        "Respuestas exactas y reproducibles: no inventa datos.",
        "Rápida, sin costo ni dependencia de internet o de un token.",
        "Fácil de auditar: cada respuesta sale de hechos y reglas "
        "explícitos.",
    ])
    parrafo(doc, "Debilidades", negrita=True)
    viñetas(doc, [
        "Entrada rígida: solo responde lo que el menú contempla.",
        "No entiende lenguaje natural ni preguntas compuestas.",
        "Ampliar el conocimiento exige editar hechos a mano.",
    ])
    doc.add_heading("6.2 Versión LLM", 2)
    parrafo(doc, "Fortalezas", negrita=True)
    viñetas(doc, [
        "Entiende preguntas en lenguaje natural, con distintas "
        "redacciones y combinaciones.",
        "Se adapta a preguntas nuevas sin programar cada consulta.",
        "Responde de forma conversacional.",
    ])
    parrafo(doc, "Debilidades", negrita=True)
    viñetas(doc, [
        "No es determinista: puede equivocarse o inventar datos aunque "
        "se le indique usar solo la base.",
        "Depende de internet, de un token y de los límites de la capa "
        "gratuita (tokens por minuto).",
        "Es más lenta y consume el contexto con toda la base de "
        "conocimiento en cada consulta.",
    ])

    doc.add_heading("7. Conclusiones", 1)
    manual = texto_manual("conclusiones_manual.txt")
    if manual:
        for texto in manual:
            parrafo(doc, texto)
    elif tiene_llm:
        parrafo(
            doc,
            "Los resultados muestran que cada versión resuelve un "
            "problema distinto: Prolog garantiza exactitud dentro de lo "
            "que el menú cubre, y el LLM entrega flexibilidad de entrada "
            "a cambio de menor confiabilidad. Una arquitectura híbrida "
            "(sección 8) combina ambas ventajas.",
        )
    else:
        parrafo(doc, "[PENDIENTE] Redactar tras incorporar los resultados "
                     "del LLM.", negrita=True)

    doc.add_heading("8. Propuestas de mejora", 1)
    for i, (titulo, texto) in enumerate(PROPUESTAS, 1):
        parrafo(doc, f"8.{i} {titulo}", negrita=True)
        parrafo(doc, texto)

    doc.add_heading("9. Código y versionado", 1)
    parrafo(
        doc,
        "El código del sistema se mantiene versionado en el repositorio "
        "git del proyecto. Archivos principales: app.py (servidor), "
        "chatbot_llm.py (LLM), puente_prolog.py y "
        "Codigo_Prolog/puente_web.pl (conexión con Prolog), "
        "evaluacion.py y preguntas.json (evaluación), "
        "static/index.html (interfaz).",
    )
    doc.save(SALIDA)
    print("Informe generado:", SALIDA.name)


if __name__ == "__main__":
    sys.stdout.reconfigure(errors="replace")
    main()
