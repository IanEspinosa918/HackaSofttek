"""
graficas_pdf.py - Gráficas para los PDF, dibujadas con los datos reales de la base de datos
(no con lo que escribe la IA). Usa reportlab.graphics, sin dependencias extra.

Diseño: barras en gradiente con los colores del tema elegido. El color de cada barra depende de
su magnitud respecto a la mayor (baja, media o alta) y cada gráfica lleva su leyenda; las alertas
también van escritas en texto ("(incumple)", "(bajo)", "(esta)") para no depender solo del color.
"""
from contextvars import ContextVar

from reportlab.graphics.shapes import Drawing, Line, Rect, String
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle

import logica
from pdf_reporte import _limpiar, mezclar, paleta

# Paleta del PDF que se está generando (ContextVar: cada petición usa la suya aunque haya varias a la vez)
_PALETA: ContextVar[dict] = ContextVar("paleta_pdf", default=paleta("claro"))
H = colors.HexColor
ESTADOS = {"agotado": (H("#fb7185"), H("#e11d48")), "bajo": (H("#fcd34d"), H("#f97316")),
           "exceso": (H("#60a5fa"), H("#3b82f6")), "ok": (H("#6ee7b7"), H("#10b981"))}


def _c(clave: str):
    return _PALETA.get()[clave]


def _mag(valor: float, maximo: float) -> tuple:
    """Colores (claro, oscuro) del gradiente según la magnitud: baja, media o alta."""
    r = valor / maximo if maximo > 0 else 0
    return _c("mag")[0 if r < 0.34 else 1 if r < 0.67 else 2]


def _dinero(v: float) -> str:
    return f"${v:,.2f}"


def _corto(texto: str, n: int) -> str:
    t = _limpiar(str(texto)).strip()
    return t if len(t) <= n else t[: n - 2].rstrip() + ".."


def _ajustar(texto: str, ancho_max: float, fuente: str = "Helvetica", tam: float = 8) -> str:
    """Recorta el texto para que quepa en `ancho_max` puntos (mide el ancho real de la fuente)."""
    t = _limpiar(str(texto)).strip()
    if stringWidth(t, fuente, tam) <= ancho_max:
        return t
    while t and stringWidth(t + "..", fuente, tam) > ancho_max:
        t = t[:-1]
    return t.rstrip() + ".."


def _gradiente_h(d: Drawing, x, y, largo, grosor, c_claro, c_oscuro, pasos: int = 28):
    """Barra horizontal en gradiente (oscuro en la base -> claro en la punta)."""
    pasos = max(2, min(pasos, int(largo)))
    w = largo / pasos
    for k in range(pasos):
        d.add(Rect(x + k * w, y, w + 0.3, grosor, strokeColor=None,
                   fillColor=mezclar(c_oscuro, c_claro, k / (pasos - 1))))


def _gradiente_v(d: Drawing, x, y, grosor, alto, c_claro, c_oscuro, pasos: int = 28):
    """Columna en gradiente (oscuro abajo -> claro arriba)."""
    pasos = max(2, min(pasos, int(alto)))
    h = alto / pasos
    for k in range(pasos):
        d.add(Rect(x, y + k * h, grosor, h + 0.3, strokeColor=None,
                   fillColor=mezclar(c_oscuro, c_claro, k / (pasos - 1))))


def _leyenda(ancho: float, textos=("Bajo", "Medio", "Alto")) -> Drawing:
    d = Drawing(ancho, 14)
    x = 0
    for (claro, oscuro), texto in zip(_c("mag"), textos):
        _gradiente_h(d, x, 3, 16, 6, claro, oscuro, pasos=8)
        d.add(String(x + 20, 3, texto, fontName="Helvetica", fontSize=7, fillColor=_c("gris")))
        x += 24 + stringWidth(texto, "Helvetica", 7) + 10
    return d


def _sin_datos(ancho: float, alto: float = 60) -> Drawing:
    d = Drawing(ancho, alto)
    d.add(Rect(0, 0, ancho, alto, fillColor=_c("pista"), strokeColor=None))
    d.add(String(ancho / 2, alto / 2 - 3, "Sin datos para esta gráfica", fontName="Helvetica",
                 fontSize=8.5, fillColor=_c("gris"), textAnchor="middle"))
    return d


def barras_horizontales(filas: list[tuple], ancho: float, formato=_dinero, max_filas: int = 8,
                        colores_fijos: dict | None = None) -> Drawing:
    """
    filas = [(etiqueta, valor, clave_color_opcional, nota_opcional)]. Una barra por fila, valor al final.
    Por defecto el color sale de la magnitud; con `colores_fijos` se usa el color de la clave (p. ej. estados).
    """
    filas = [f for f in filas if f[1] is not None][:max_filas]
    if not filas or max(float(f[1]) for f in filas) <= 0:
        return _sin_datos(ancho)
    alto_fila, grosor = 20, 9
    alto = alto_fila * len(filas) + 4
    d = Drawing(ancho, alto)
    col_etiqueta = ancho * 0.36
    col_valor = 74 if any(len(f) > 3 and f[3] for f in filas) else 52
    area = ancho - col_etiqueta - col_valor - 6
    maximo = max(float(f[1]) for f in filas)
    for i, fila in enumerate(filas):
        etiqueta, valor = fila[0], float(fila[1])
        clave = fila[2] if len(fila) > 2 else None
        nota = fila[3] if len(fila) > 3 else None
        y = alto - (i + 1) * alto_fila + (alto_fila - grosor) / 2
        d.add(String(0, y + 1.5, _ajustar(etiqueta, col_etiqueta - 6), fontName="Helvetica-Bold" if nota else "Helvetica",
                     fontSize=8, fillColor=_c("tinta")))
        d.add(Rect(col_etiqueta, y, area, grosor, fillColor=_c("pista"), strokeColor=None))
        largo = max(1.5, area * valor / maximo)
        claro, oscuro = colores_fijos[clave] if colores_fijos and clave in colores_fijos else _mag(valor, maximo)
        _gradiente_h(d, col_etiqueta, y, largo, grosor, claro, oscuro)
        texto = formato(valor) + (f"  {nota}" if nota else "")
        d.add(String(col_etiqueta + area + 6, y + 1.5, _limpiar(texto), fontName="Helvetica-Bold",
                     fontSize=8, fillColor=_c("tinta")))
    return d


def columnas(filas: list[tuple], ancho: float, alto: float = 130, formato=_dinero) -> Drawing:
    """filas = [(etiqueta, valor)] en orden cronológico. Remarca la última y etiqueta la última y la máxima."""
    filas = [(e, float(v or 0)) for e, v in filas]
    if not filas or max(v for _, v in filas) <= 0:
        return _sin_datos(ancho, 80)
    d = Drawing(ancho, alto)
    base_y, margen_izq, arriba = 16, 34, 14
    area_alto = alto - base_y - arriba
    area_ancho = ancho - margen_izq
    maximo = max(v for _, v in filas)
    for k in (0.5, 1.0):
        y = base_y + area_alto * k
        d.add(Line(margen_izq, y, ancho, y, strokeColor=_c("linea"), strokeWidth=0.5))
        d.add(String(margen_izq - 4, y - 3, f"${maximo * k:,.0f}", fontName="Helvetica", fontSize=7,
                     fillColor=_c("gris"), textAnchor="end"))
    d.add(Line(margen_izq, base_y, ancho, base_y, strokeColor=_c("gris"), strokeWidth=0.6))
    hueco = area_ancho / len(filas)
    grosor = min(24, hueco * 0.55)
    i_max = max(range(len(filas)), key=lambda i: filas[i][1])
    for i, (etiqueta, valor) in enumerate(filas):
        x = margen_izq + hueco * i + (hueco - grosor) / 2
        h = max(1.5, area_alto * valor / maximo)
        ultima = i == len(filas) - 1
        claro, oscuro = _mag(valor, maximo)
        _gradiente_v(d, x, base_y, grosor, h, claro, oscuro)
        if ultima:   # la semana actual va remarcada
            d.add(Rect(x - 1.5, base_y, grosor + 3, h + 1.5, fillColor=None, strokeColor=_c("tinta"), strokeWidth=1))
        d.add(String(x + grosor / 2, 4, _corto(etiqueta, 8), fontName="Helvetica", fontSize=7,
                     fillColor=_c("gris"), textAnchor="middle"))
        if ultima or i == i_max:
            d.add(String(x + grosor / 2, base_y + h + 3, formato(valor), fontName="Helvetica-Bold",
                         fontSize=7.5, fillColor=_c("tinta"), textAnchor="middle"))
    return d


def _bloque(titulo: str, subtitulo: str, dibujo: Drawing, leyenda: bool = True, ancho: float | None = None):
    # Lista de elementos: una celda de tabla acepta varios elementos apilados
    estilo_t = ParagraphStyle("g_titulo", fontName="Helvetica-Bold", fontSize=10.5, leading=13, textColor=_c("tinta"))
    estilo_s = ParagraphStyle("g_sub", fontName="Helvetica", fontSize=8, leading=10, textColor=_c("gris"), spaceAfter=4)
    elementos = [Paragraph(_limpiar(titulo), estilo_t), Paragraph(_limpiar(subtitulo), estilo_s), dibujo]
    if leyenda:
        elementos += [Spacer(1, 3), _leyenda(ancho or dibujo.width)]
    return elementos


def _cuadricula(bloques: list, ancho: float) -> list:
    """Acomoda las gráficas de dos en dos, cada una en una tarjeta con el color del tema."""
    if not bloques:
        return []
    medio = (ancho - 16) / 2
    filas = [bloques[i:i + 2] + ([""] if len(bloques[i:i + 2]) == 1 else []) for i in range(0, len(bloques), 2)]
    t = Table(filas, colWidths=[medio + 8, medio + 8], hAlign="LEFT", spaceBefore=2)
    estilo = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("INNERGRID", (0, 0), (-1, -1), 6, _c("fondo")),
    ]
    for r, fila in enumerate(filas):
        for col, celda in enumerate(fila):
            if celda != "":
                estilo += [("BACKGROUND", (col, r), (col, r), _c("panel")),
                           ("LINEABOVE", (col, r), (col, r), 2, _c("marca"))]
    t.setStyle(TableStyle(estilo))
    return [t]


# ---------------------------------------------------------------------
# Gráficas por tipo de documento
# ---------------------------------------------------------------------
def _merma_semanal(idsucursal, medio):
    sem = logica.merma_por_semana(idsucursal, 8)
    meses = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
    def etiqueta(f):
        s = str(f["desde"])[:10]
        return f"{int(s[8:10])} {meses[int(s[5:7]) - 1]}" if len(s) == 10 else s
    return _bloque("Merma por semana", "Costo de lo perdido · la semana más reciente va remarcada",
                   columnas([(etiqueta(f), f["costo_total"]) for f in sem], medio))


def _merma_causa(idsucursal, medio):
    causas = logica.merma_por_causa(idsucursal, 30)
    return _bloque("Merma por causa", "Costo · últimos 30 días",
                   barras_horizontales([(c["causa"], c["costo_total"]) for c in causas], medio))


def _comparativo(idsucursal, medio):
    comp = logica.merma_por_sucursal(30)
    filas = [(c.get("codigo") or c["sucursal"], c["costo_total"], None,
              "(esta)" if c["idsucursal"] == idsucursal else None) for c in comp]
    return _bloque("Merma entre sucursales", "Costo · 30 días · (esta) = la sucursal del reporte", barras_horizontales(filas, medio))


def _riesgo_por_producto(idsucursal, medio):
    acumulado: dict[str, float] = {}
    for c in logica.productos_por_caducar(idsucursal, 7):
        acumulado[c["producto"]] = acumulado.get(c["producto"], 0) + c["valor_en_riesgo"]
    filas = sorted(acumulado.items(), key=lambda x: -x[1])
    return _bloque("Valor en riesgo por producto", "Lotes que caducan en 7 días · a costo",
                   barras_horizontales(filas, medio))


def _descuento_por_lote(idsucursal, medio):
    filas = [(f'{c["producto"]} #{c["idlote"]}', c["descuento_sugerido_pct"],
              None, f'({c["dias_para_caducar"]} d)') for c in logica.productos_por_caducar(idsucursal, 7)
             if c["descuento_sugerido_pct"]]
    return _bloque("Descuento sugerido por lote", "Porcentaje sugerido · (días para caducar)",
                   barras_horizontales(filas, medio, formato=lambda v: f"{v:.0f}%"))


def _pedido_por_proveedor(idsucursal, medio):
    costo: dict[str, float] = {}
    for s in logica.sugerir_pedidos(idsucursal):
        costo[s["proveedor"]] = costo.get(s["proveedor"], 0) + s["costo_estimado"]
    return _bloque("Pedido sugerido por proveedor", "Costo estimado de compra",
                   barras_horizontales(sorted(costo.items(), key=lambda x: -x[1]), medio))


def _retraso_proveedores(medio):
    filas = [(p["proveedor"], p["retraso_promedio_horas"], None,
              "(incumple)" if p["incumple_contrato_en"] else None) for p in logica.retraso_proveedores()]
    return _bloque("Retraso promedio por proveedor", "Horas · (incumple) = no cumple su contrato",
                   barras_horizontales(filas, medio, formato=lambda v: f"{v:.1f} h"))


def _stock_por_estado(idsucursal, medio):
    stock = logica.stock_actual(idsucursal)
    filas = [(e.capitalize(), sum(1 for s in stock if s["estado"] == e), e) for e in ("agotado", "bajo", "exceso", "ok")]
    return _bloque("Productos por estado", "Cantidad de productos en cada estado (color = estado)",
                   barras_horizontales([f for f in filas if f[1]] or filas, medio, formato=lambda v: f"{v:.0f}",
                                       colores_fijos=ESTADOS), leyenda=False)


def _cobertura(idsucursal, medio):
    stock = [s for s in logica.stock_actual(idsucursal) if s["dias_cobertura"] is not None]
    filas = [(s["producto"], s["dias_cobertura"], None,
              "(bajo)" if s["dias_cobertura"] < logica.DIAS_FALTANTE else None)
             for s in sorted(stock, key=lambda s: s["dias_cobertura"])]
    return _bloque("Días de cobertura por producto", f"(bajo) = menos de {logica.DIAS_FALTANTE} días de inventario",
                   barras_horizontales(filas, medio, formato=lambda v: f"{v:.1f} d"))


def graficas_para(tipo: str | None, idsucursal: int | None, ancho: float, P: dict | None = None) -> list:
    """Lista de elementos (para el PDF) con las gráficas que corresponden al tipo de documento."""
    if idsucursal is None:
        return []
    _PALETA.set(P or paleta("claro"))
    medio = (ancho - 16) / 2 - 8
    try:
        if tipo == "descuentos":
            bloques = [_riesgo_por_producto(idsucursal, medio), _descuento_por_lote(idsucursal, medio)]
        elif tipo == "pedidos":
            bloques = [_pedido_por_proveedor(idsucursal, medio), _retraso_proveedores(medio)]
        elif tipo == "stock":
            bloques = [_stock_por_estado(idsucursal, medio), _cobertura(idsucursal, medio)]
        elif tipo == "reporte":
            bloques = [_merma_semanal(idsucursal, medio), _merma_causa(idsucursal, medio),
                       _riesgo_por_producto(idsucursal, medio), _comparativo(idsucursal, medio)]
        else:  # cualquier otro documento: panorama de mermas
            bloques = [_merma_semanal(idsucursal, medio), _merma_causa(idsucursal, medio)]
    except Exception:
        return []   # si falla una consulta, el PDF sale igual pero sin gráficas
    return [Spacer(1, 4)] + _cuadricula(bloques, ancho)
