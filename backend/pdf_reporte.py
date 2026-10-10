"""
pdf_reporte.py - Convierte un reporte (texto en Markdown generado por la IA) en un PDF con formato.

Soporta lo que usa Gemini en los reportes: títulos (#, ##, ###), párrafos, **negritas**, *cursivas*,
listas con viñetas o numeradas y tablas en Markdown.
"""
import io
import re
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (ListFlowable, ListItem, Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)

VERDE = colors.HexColor("#1f5c4a")
VERDE_SUAVE = colors.HexColor("#e6efeb")
AMBAR = colors.HexColor("#e8a33d")
TINTA = colors.HexColor("#1d1b19")
GRIS = colors.HexColor("#6f6a64")
LINEA = colors.HexColor("#e3ddd4")
FONDO = colors.HexColor("#f4f1ec")

# Las fuentes estándar del PDF no traen emojis ni algunos símbolos: se reemplazan por texto
_REEMPLAZOS = {
    "⚠️": "(!)", "⚠": "(!)", "✅": "(ok)", "❌": "(x)", "👍": "", "📉": "", "📈": "", "🔴": "", "🟡": "",
    "🟢": "", "→": "->", "–": "-", "—": "-", "“": '"', "”": '"', "‘": "'", "’": "'", "…": "...", "•": "-",
    "≈": "~", "≥": ">=", "≤": "<=",
}


def _limpiar(texto: str) -> str:
    for a, b in _REEMPLAZOS.items():
        texto = texto.replace(a, b)
    # Quita cualquier otro carácter que no exista en Latin-1 (la codificación de las fuentes estándar)
    return texto.encode("latin-1", "ignore").decode("latin-1")


def _en_linea(texto: str) -> str:
    """Escapa el texto y convierte **negrita**, *cursiva* y `código` a las etiquetas de ReportLab."""
    t = _limpiar(texto)
    t = t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    t = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"(^|[^*])\*([^*\s][^*]*)\*", r"\1<i>\2</i>", t)
    t = re.sub(r"`([^`]+)`", r"<font face='Courier'>\1</font>", t)
    return t


def _estilos():
    base = getSampleStyleSheet()
    return {
        "titulo": ParagraphStyle("titulo", parent=base["Title"], fontName="Helvetica-Bold", fontSize=18,
                                 leading=22, textColor=TINTA, alignment=TA_LEFT, spaceAfter=4),
        "sub": ParagraphStyle("sub", parent=base["Normal"], fontSize=9.5, leading=13, textColor=GRIS),
        "h1": ParagraphStyle("h1", parent=base["Heading1"], fontName="Helvetica-Bold", fontSize=14,
                             leading=18, textColor=VERDE, spaceBefore=12, spaceAfter=5),
        "h2": ParagraphStyle("h2", parent=base["Heading2"], fontName="Helvetica-Bold", fontSize=12.5,
                             leading=16, textColor=VERDE, spaceBefore=12, spaceAfter=4),
        "h3": ParagraphStyle("h3", parent=base["Heading3"], fontName="Helvetica-Bold", fontSize=11,
                             leading=14, textColor=TINTA, spaceBefore=8, spaceAfter=3),
        "p": ParagraphStyle("p", parent=base["Normal"], fontSize=10, leading=14.5, textColor=TINTA, spaceAfter=5),
        "li": ParagraphStyle("li", parent=base["Normal"], fontSize=10, leading=14, textColor=TINTA),
        "celda": ParagraphStyle("celda", parent=base["Normal"], fontSize=8.5, leading=11, textColor=TINTA),
        "celda_h": ParagraphStyle("celda_h", parent=base["Normal"], fontName="Helvetica-Bold", fontSize=8.5,
                                  leading=11, textColor=TINTA),
        "kpi_label": ParagraphStyle("kpi_label", parent=base["Normal"], fontSize=8, leading=10, textColor=GRIS),
        "kpi_valor": ParagraphStyle("kpi_valor", parent=base["Normal"], fontName="Helvetica-Bold",
                                    fontSize=13, leading=16, textColor=TINTA),
    }


def _tabla(filas: list[list[str]], estilos, ancho: float) -> Table:
    n = max(len(f) for f in filas)
    filas = [f + [""] * (n - len(f)) for f in filas]
    datos = [[Paragraph(_en_linea(c), estilos["celda_h"] if i == 0 else estilos["celda"]) for c in fila]
             for i, fila in enumerate(filas)]
    # Ancho de cada columna según lo largo de su contenido (con mínimo y máximo para que no se aplaste)
    largos = [max(min(len(_limpiar(f[c])), 45) for f in filas) + 4 for c in range(n)]
    total = sum(largos)
    anchos = [max(ancho * 0.08, ancho * l / total) for l in largos]
    escala = ancho / sum(anchos)
    t = Table(datos, colWidths=[a * escala for a in anchos], repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), FONDO),
        ("LINEBELOW", (0, 0), (-1, -1), 0.5, LINEA),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def _markdown_a_flowables(texto: str, estilos, ancho: float) -> list:
    lineas = (texto or "").replace("\r", "").split("\n")
    historia, lista, tipo_lista = [], [], None

    def cerrar_lista():
        nonlocal lista, tipo_lista
        if lista:
            historia.append(ListFlowable(
                [ListItem(Paragraph(_en_linea(x), estilos["li"]), leftIndent=14) for x in lista],
                bulletType="1" if tipo_lista == "ol" else "bullet",
                start="1" if tipo_lista == "ol" else None,
                bulletFontSize=9, leftIndent=14, bulletColor=VERDE,
            ))
            historia.append(Spacer(1, 4))
        lista, tipo_lista = [], None

    i = 0
    while i < len(lineas):
        t = lineas[i].strip()
        # Tabla Markdown: | a | b |  seguido de |---|---|
        if re.match(r"^\|.*\|$", t) and i + 1 < len(lineas) and re.match(r"^\|?\s*:?-{2,}", lineas[i + 1].strip()):
            cerrar_lista()
            celdas = lambda s: [c.strip() for c in s.strip().strip("|").split("|")]
            filas = [celdas(t)]
            i += 2
            while i < len(lineas) and re.match(r"^\|.*\|$", lineas[i].strip()):
                filas.append(celdas(lineas[i]))
                i += 1
            historia.append(_tabla(filas, estilos, ancho))
            historia.append(Spacer(1, 8))
            continue
        if m := re.match(r"^(#{1,3})\s+(.*)$", t):
            cerrar_lista()
            historia.append(Paragraph(_en_linea(m.group(2)), estilos[f"h{len(m.group(1))}"]))
        elif m := re.match(r"^[-*•]\s+(.*)$", t):
            if tipo_lista != "ul":
                cerrar_lista()
                tipo_lista = "ul"
            lista.append(m.group(1))
        elif m := re.match(r"^\d+[.)]\s+(.*)$", t):
            if tipo_lista != "ol":
                cerrar_lista()
                tipo_lista = "ol"
            lista.append(m.group(1))
        elif t == "":
            cerrar_lista()
        else:
            cerrar_lista()
            historia.append(Paragraph(_en_linea(t), estilos["p"]))
        i += 1
    cerrar_lista()
    return historia


ETIQUETAS_INDICADORES = {
    "valor_en_riesgo_7_dias": ("Valor en riesgo (7 días)", "dinero"),
    "lotes_por_caducar_7_dias": ("Lotes por caducar (7 días)", None),
    "lotes_por_caducar_48_horas": ("Caducan en 48 h", None),
    "productos_con_sobreinventario": ("Con sobreinventario", None),
    "valor_sobreinventario_en_riesgo": ("Valor en exceso", "dinero"),
    "entregas_pendientes": ("Entregas pendientes", None),
    "entregas_retrasadas": ("Entregas retrasadas", None),
    "merma_ultimos_30_dias": ("Merma (30 días)", "dinero"),
}


def _tarjetas_indicadores(indicadores: dict, estilos, ancho: float) -> Table:
    celdas = []
    for clave, (etiqueta, tipo) in ETIQUETAS_INDICADORES.items():
        if clave not in indicadores:
            continue
        v = indicadores[clave]
        valor = f"${float(v):,.2f}" if tipo == "dinero" else f"{v}"
        celdas.append([Paragraph(etiqueta, estilos["kpi_label"]), Paragraph(valor, estilos["kpi_valor"])])
    columnas = 4
    filas = [celdas[i:i + columnas] for i in range(0, len(celdas), columnas)]
    filas = [f + [""] * (columnas - len(f)) for f in filas]
    t = Table(filas, colWidths=[ancho / columnas] * columnas)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), FONDO),
        ("BOX", (0, 0), (-1, -1), 0, colors.white),
        ("INNERGRID", (0, 0), (-1, -1), 3, colors.white),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    return t


def generar_pdf(titulo: str, contenido: str, sucursal: str | None = None, fecha: str | None = None,
                autor: str | None = None, estado: str | None = None, indicadores: dict | None = None,
                comentario_gerente: str | None = None) -> bytes:
    """Regresa los bytes del PDF listo para descargar."""
    buffer = io.BytesIO()
    margen = 1.8 * cm
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=margen, rightMargin=margen,
                            topMargin=2.3 * cm, bottomMargin=1.8 * cm,
                            title=_limpiar(titulo), author="Tienda Inteligente")
    ancho = letter[0] - 2 * margen
    estilos = _estilos()

    detalles = [x for x in [
        f"Sucursal: {sucursal}" if sucursal else None,
        f"Fecha: {fecha}" if fecha else None,
        f"Elaboró: {autor}" if autor else None,
        f"Estado: {estado}" if estado else None,
    ] if x]

    historia = [Paragraph(_en_linea(titulo), estilos["titulo"])]
    if detalles:
        historia.append(Paragraph(_en_linea("  ·  ".join(detalles)), estilos["sub"]))
    historia.append(Spacer(1, 12))
    if indicadores:
        historia.append(_tarjetas_indicadores(indicadores, estilos, ancho))
        historia.append(Spacer(1, 10))
    historia += _markdown_a_flowables(contenido, estilos, ancho)
    if comentario_gerente:
        historia.append(Spacer(1, 10))
        caja = Table([[Paragraph(_en_linea(f"**Comentario del gerente:** {comentario_gerente}"), estilos["p"])]],
                     colWidths=[ancho])
        caja.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), VERDE_SUAVE),
                                  ("LEFTPADDING", (0, 0), (-1, -1), 10), ("TOPPADDING", (0, 0), (-1, -1), 8),
                                  ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
        historia.append(caja)

    generado = datetime.now().strftime("%d/%m/%Y %H:%M")

    def encabezado_y_pie(canvas, documento):
        canvas.saveState()
        ancho_pag, alto_pag = letter
        # Franja superior
        canvas.setFillColor(VERDE)
        canvas.rect(0, alto_pag - 1.1 * cm, ancho_pag, 1.1 * cm, stroke=0, fill=1)
        canvas.setFillColor(AMBAR)
        canvas.rect(0, alto_pag - 1.1 * cm - 3, ancho_pag, 3, stroke=0, fill=1)
        canvas.setFillColor(colors.white)
        canvas.setFont("Helvetica-Bold", 11)
        canvas.drawString(margen, alto_pag - 0.72 * cm, "Tienda Inteligente")
        canvas.setFont("Helvetica", 8.5)
        canvas.drawRightString(ancho_pag - margen, alto_pag - 0.72 * cm, "Reporte de inventario y mermas")
        # Pie
        canvas.setFillColor(GRIS)
        canvas.setFont("Helvetica", 7.5)
        canvas.drawString(margen, 1.0 * cm, f"Generado con IA a partir de los datos del sistema · {generado}")
        canvas.drawRightString(ancho_pag - margen, 1.0 * cm, f"Página {documento.page}")
        canvas.restoreState()

    doc.build(historia, onFirstPage=encabezado_y_pie, onLaterPages=encabezado_y_pie)
    return buffer.getvalue()


def nombre_archivo(titulo: str) -> str:
    """Nombre de archivo seguro: 'Reporte diario - S001 - 2026-09-30' -> 'reporte-diario-s001-2026-09-30.pdf'."""
    base = _limpiar(titulo).lower()
    for a, b in {"á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u", "ñ": "n", "¿": "", "?": ""}.items():
        base = base.replace(a, b)
    base = re.sub(r"[^a-z0-9]+", "-", base).strip("-")
    return (base[:80] or "reporte") + ".pdf"
