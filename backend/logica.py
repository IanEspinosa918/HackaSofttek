"""
logica.py - Toda la lógica de negocio. Aquí se calculan los números; la IA solo los interpreta.

Las funciones de la sección "CONSULTAS" son de solo lectura y también se le entregan
a Gemini como herramientas (function calling). Por eso tienen nombres claros,
tipos en los parámetros y un docstring que explica qué regresan: Gemini lee eso
para decidir cuál usar.

Las funciones de la sección "ACCIONES" escriben en la BD y solo las usan los endpoints,
nunca la IA.
"""
import math
import time as _time
from datetime import date, datetime, time, timedelta

import db

# ---------------------------------------------------------------------
# Parámetros de negocio (ajústenlos a su escenario)
# ---------------------------------------------------------------------
DIAS_STOCK_SEGURIDAD = 1        # días extra de inventario para no quedarse sin producto
DIAS_COBERTURA_OBJETIVO = 5     # para cuántos días se pide mercancía
DIAS_FALTANTE = 2               # si la existencia alcanza para menos de esto, se considera faltante

# Descuento escalonado por días para caducar: (máximo de días, % de descuento)
ESCALA_DESCUENTO = [(1, 50), (3, 30), (5, 15), (7, 10)]
EXTRA_SI_NO_SE_VENDERA = 10     # puntos extra si el ritmo de venta no alcanza
DESCUENTO_MAXIMO = 60


# =====================================================================
# Utilidades internas
# =====================================================================

_CACHE_FECHA = {"valor": None, "hasta": 0.0}


def fecha_referencia() -> date:
    """
    El "hoy" del sistema: el último día con ventas (vista vw_fecha_referencia).
    Con el dataset es 2026-09-30; con datos en vivo avanza sola.
    Se guarda 60 s en memoria para no consultarla en cada cálculo.
    """
    if _CACHE_FECHA["valor"] and _time.time() < _CACHE_FECHA["hasta"]:
        return _CACHE_FECHA["valor"]
    try:
        fila = db.consultar("SELECT fecha_ref FROM vw_fecha_referencia")
        valor = _a_fecha(fila[0]["fecha_ref"]) if fila and fila[0]["fecha_ref"] else date.today()
    except Exception:
        valor = date.today()
    _CACHE_FECHA.update(valor=valor, hasta=_time.time() + 60)
    return valor


def _hoy() -> date:
    return fecha_referencia()


def _ahora() -> datetime:
    """Momento actual según la fecha de referencia (si es hoy, la hora real; si no, el cierre de ese día)."""
    ref = fecha_referencia()
    return datetime.now() if ref == date.today() else datetime.combine(ref, time(23, 59))


def _a_fecha(valor) -> date:
    if isinstance(valor, date):
        return valor
    return datetime.fromisoformat(str(valor)).date()


def descuento_por_dias(dias_para_caducar: int, no_se_vendera: bool = False) -> int:
    """Regla escalonada de descuento."""
    base = 0
    for max_dias, pct in ESCALA_DESCUENTO:
        if dias_para_caducar <= max_dias:
            base = pct
            break
    if base and no_se_vendera:
        base = min(DESCUENTO_MAXIMO, base + EXTRA_SI_NO_SE_VENDERA)
    return base


def _lotes_con_existencia(idsucursal: int | None = None) -> list[dict]:
    sql = """
        SELECT l.idlote, l.idsucursal, RTRIM(s.nombre) AS sucursal, l.idproducto, p.nombre AS producto,
               c.nombre AS categoria, p.costo, p.precio_venta, l.cantidad_actual, l.fecha_caducidad
        FROM lote l
        JOIN producto  p ON p.idproducto  = l.idproducto
        JOIN categoria c ON c.idcategoria = p.idcategoria
        JOIN sucursal  s ON s.idsucursal  = l.idsucursal
        WHERE l.cantidad_actual > 0
    """
    params: tuple = ()
    if idsucursal is not None:
        sql += " AND l.idsucursal = ?"
        params = (idsucursal,)
    return db.consultar(sql + " ORDER BY l.fecha_caducidad", params)


def _ventas_promedio(idsucursal: int | None = None, dias: int = 30) -> dict[tuple, float]:
    """
    Venta promedio diaria por (sucursal, producto) en los últimos `dias` días hasta la fecha de referencia.
    Junta dos fuentes (detalle_venta e inventario_diario.vendida) y promedia sobre los días
    que tienen registro, así funciona igual con la muestra del dataset que con datos completos.
    """
    ref = fecha_referencia()
    desde = ref - timedelta(days=dias - 1)
    filtro_v = " AND v.idsucursal = ?" if idsucursal is not None else ""
    filtro_i = " AND idsucursal = ?" if idsucursal is not None else ""
    sql = f"""
        SELECT idsucursal, idproducto, AVG(CAST(vendido AS DECIMAL(12,2))) AS venta_promedio_diaria
        FROM (
            SELECT idsucursal, idproducto, dia, MAX(vendido) AS vendido
            FROM (
                SELECT v.idsucursal, dv.idproducto, CAST(v.fecha AS DATE) AS dia, SUM(dv.cantidad) AS vendido
                FROM detalle_venta dv JOIN venta v ON v.idventa = dv.idventa
                WHERE CAST(v.fecha AS DATE) BETWEEN ? AND ?{filtro_v}
                GROUP BY v.idsucursal, dv.idproducto, CAST(v.fecha AS DATE)
                UNION ALL
                SELECT idsucursal, idproducto, fecha, vendida
                FROM inventario_diario
                WHERE vendida IS NOT NULL AND fecha BETWEEN ? AND ?{filtro_i}
            ) fuentes
            GROUP BY idsucursal, idproducto, dia
        ) por_dia
        GROUP BY idsucursal, idproducto
    """
    params: list = [desde, ref] + ([idsucursal] if idsucursal is not None else [])
    params += [desde, ref] + ([idsucursal] if idsucursal is not None else [])
    return {(r["idsucursal"], r["idproducto"]): float(r["venta_promedio_diaria"] or 0)
            for r in db.consultar(sql, tuple(params))}


def _analisis_inventario(idsucursal: int | None = None) -> dict[tuple, dict]:
    """
    Para cada (sucursal, producto) con existencia simula la venta FEFO
    (lo que caduca primero se vende primero) al ritmo de venta promedio
    y calcula cuántas unidades de cada lote NO se alcanzarán a vender antes de caducar.
    """
    hoy = _hoy()
    ventas = _ventas_promedio(idsucursal)
    grupos: dict[tuple, dict] = {}

    for lote in _lotes_con_existencia(idsucursal):
        clave = (lote["idsucursal"], lote["idproducto"])
        g = grupos.setdefault(clave, {
            "idsucursal": lote["idsucursal"], "sucursal": lote["sucursal"],
            "idproducto": lote["idproducto"], "producto": lote["producto"],
            "categoria": lote["categoria"], "costo": float(lote["costo"]),
            "venta_promedio_diaria": round(ventas.get(clave, 0.0), 2),
            "existencia": 0, "unidades_en_riesgo": 0, "lotes": [],
        })
        g["existencia"] += lote["cantidad_actual"]
        g["lotes"].append(lote)

    for g in grupos.values():
        venta = g["venta_promedio_diaria"]
        vendido_acumulado = 0.0
        for lote in g["lotes"]:  # ya vienen ordenados por caducidad
            dias = max(0, (_a_fecha(lote["fecha_caducidad"]) - hoy).days)
            capacidad_hasta_caducar = venta * dias          # lo que se puede vender hasta esa fecha
            disponible_para_este_lote = max(0.0, capacidad_hasta_caducar - vendido_acumulado)
            se_vende = min(lote["cantidad_actual"], disponible_para_este_lote)
            vendido_acumulado += se_vende
            riesgo = lote["cantidad_actual"] - math.floor(se_vende)
            lote["dias_para_caducar"] = dias
            lote["unidades_en_riesgo"] = max(0, riesgo)
            g["unidades_en_riesgo"] += lote["unidades_en_riesgo"]

        g["dias_cobertura"] = round(g["existencia"] / venta, 1) if venta > 0 else None
        g["valor_en_riesgo"] = round(g["unidades_en_riesgo"] * g["costo"], 2)

    return grupos


# =====================================================================
# CONSULTAS (solo lectura) - también son herramientas de la IA
# =====================================================================

def listar_sucursales() -> list[dict]:
    """
    Lista las sucursales activas con id, código (S001...), nombre, ubicación, región y tipo de sitio
    (aeropuerto, estación, etc.). Úsala para traducir el nombre o código de una sucursal a su id.
    """
    return db.consultar("""
        SELECT idsucursal, codigo, RTRIM(nombre) AS nombre, direccion AS ubicacion, region, tipo_sitio
        FROM sucursal
        WHERE activa = 1 AND (fecha_cierre IS NULL OR fecha_cierre > ?)
        ORDER BY idsucursal
    """, (fecha_referencia(),))


def productos_por_caducar(idsucursal: int, dias: int = 7) -> list[dict]:
    """
    Lotes de una sucursal que caducan en los próximos `dias` días.
    Regresa por lote: producto, existencia, días para caducar, unidades que no se alcanzarán a vender
    al ritmo actual, valor en riesgo (a costo) y el descuento sugerido en porcentaje.
    """
    analisis = _analisis_inventario(idsucursal)
    resultado = []
    for g in analisis.values():
        for lote in g["lotes"]:
            if lote["dias_para_caducar"] <= dias:
                no_se_vendera = lote["unidades_en_riesgo"] > 0
                resultado.append({
                    "idlote": lote["idlote"],
                    "producto": g["producto"],
                    "categoria": g["categoria"],
                    "existencia": lote["cantidad_actual"],
                    "fecha_caducidad": lote["fecha_caducidad"],
                    "dias_para_caducar": lote["dias_para_caducar"],
                    "venta_promedio_diaria": g["venta_promedio_diaria"],
                    "unidades_que_no_se_venderian": lote["unidades_en_riesgo"],
                    "valor_en_riesgo": round(lote["cantidad_actual"] * g["costo"], 2),
                    "descuento_sugerido_pct": descuento_por_dias(lote["dias_para_caducar"], no_se_vendera),
                })
    return sorted(resultado, key=lambda r: (r["dias_para_caducar"], -r["valor_en_riesgo"]))


def sobreinventario(idsucursal: int) -> list[dict]:
    """
    Productos de una sucursal con más existencia de la que se alcanzará a vender antes de caducar.
    Regresa existencia, venta promedio diaria, días de cobertura, unidades en riesgo y valor en riesgo.
    """
    filas = [
        {k: v for k, v in g.items() if k != "lotes"}
        for g in _analisis_inventario(idsucursal).values()
        if g["unidades_en_riesgo"] > 0
    ]
    return sorted(filas, key=lambda r: -r["valor_en_riesgo"])


def retraso_proveedores() -> list[dict]:
    """
    Desempeño de cada proveedor contra su contrato, según lo registrado por los operadores:
    entregas recibidas, retraso promedio en horas, puntualidad real vs. contratada y
    surtido real (cantidad recibida / pedida) vs. contratado. Un surtido bajo provoca quiebres;
    entregas tarde de perecederos provocan merma.
    """
    filas = db.consultar("""
        SELECT pr.idproveedor, pr.codigo, pr.nombre AS proveedor, pr.dias_entrega_prometidos,
               pr.puntualidad_contrato, pr.fill_rate_contrato,
               COUNT(DISTINCT CASE WHEN pe.estado = 'recibido' THEN pe.idpedido END) AS entregas,
               COUNT(DISTINCT CASE WHEN pe.estado IN ('pendiente', 'en_camino') THEN pe.idpedido END) AS pedidos_abiertos,
               ISNULL(r.retraso_promedio_horas, 0) AS retraso_promedio_horas,
               r.pct_entregas_tarde,
               SUM(CASE WHEN pe.estado = 'recibido' THEN d.cantidad_pedida END)   AS unidades_pedidas,
               SUM(CASE WHEN pe.estado = 'recibido' THEN d.cantidad_recibida END) AS unidades_recibidas
        FROM proveedor pr
        LEFT JOIN pedido pe           ON pe.idproveedor = pr.idproveedor
        LEFT JOIN detalle_pedido d    ON d.idpedido     = pe.idpedido
        LEFT JOIN vw_retraso_proveedor r ON r.idproveedor = pr.idproveedor
        GROUP BY pr.idproveedor, pr.codigo, pr.nombre, pr.dias_entrega_prometidos,
                 pr.puntualidad_contrato, pr.fill_rate_contrato, r.retraso_promedio_horas, r.pct_entregas_tarde
        HAVING COUNT(pe.idpedido) > 0
    """)
    resultado = []
    for f in filas:
        pedidas, recibidas = f.pop("unidades_pedidas"), f.pop("unidades_recibidas")
        f["retraso_promedio_horas"] = round(float(f["retraso_promedio_horas"] or 0), 1)
        tarde = f.pop("pct_entregas_tarde")
        f["puntualidad_real"] = round(1 - float(tarde) / 100, 3) if tarde is not None else None
        f["surtido_real"] = round(recibidas / pedidas, 3) if pedidas else None
        incumple = []
        if f["puntualidad_real"] is not None and f["puntualidad_contrato"] is not None \
                and f["puntualidad_real"] < f["puntualidad_contrato"]:
            incumple.append("puntualidad")
        if f["surtido_real"] is not None and f["fill_rate_contrato"] is not None \
                and f["surtido_real"] < f["fill_rate_contrato"]:
            incumple.append("surtido")
        f["incumple_contrato_en"] = incumple
        resultado.append(f)
    return sorted(resultado, key=lambda r: (-len(r["incumple_contrato_en"]), -r["retraso_promedio_horas"]))


def entregas_pendientes(idsucursal: int) -> list[dict]:
    """
    Pedidos de una sucursal que aún no llegan, con fecha prometida, llegada estimada
    (fecha prometida + retraso promedio histórico del proveedor) y si ya van tarde.
    """
    filas = db.consultar("""
        SELECT pe.idpedido, pr.nombre AS proveedor, pe.fecha_pedido, pe.fecha_prometida, pe.estado,
               ISNULL(r.retraso_promedio_horas, 0) AS retraso_promedio_horas
        FROM pedido pe
        JOIN proveedor pr ON pr.idproveedor = pe.idproveedor
        LEFT JOIN vw_retraso_proveedor r ON r.idproveedor = pe.idproveedor
        WHERE pe.idsucursal = ? AND pe.estado IN ('pendiente', 'en_camino')
        ORDER BY pe.fecha_prometida
    """, (idsucursal,))
    ahora = _ahora()
    for f in filas:
        prometida = datetime.fromisoformat(f["fecha_prometida"])
        retraso = max(0.0, float(f["retraso_promedio_horas"]))
        f["llegada_estimada"] = (prometida + timedelta(hours=retraso)).isoformat(timespec="minutes")
        f["va_tarde"] = ahora > prometida
        f["retraso_promedio_horas"] = round(retraso, 1)
    return filas


def sugerir_pedidos(idsucursal: int) -> list[dict]:
    """
    Productos de una sucursal que ya deben pedirse. Usa el punto de reorden:
    venta diaria x (días prometidos del proveedor + su retraso real promedio) + stock de seguridad.
    Regresa existencia, punto de reorden, cantidad sugerida a pedir y a qué proveedor.
    No sugiere más de lo que se puede vender dentro de la vida útil del producto.
    """
    filas = db.consultar("""
        SELECT p.idproducto, p.nombre AS producto, p.sku, p.vida_util_dias, p.costo, ISNULL(p.tamano_caja, 1) AS tamano_caja,
               pr.idproveedor, pr.nombre AS proveedor, pr.dias_entrega_prometidos,
               ISNULL(i.existencia, 0)              AS existencia,
               ISNULL(r.retraso_promedio_horas, 0)  AS retraso_promedio_horas,
               ISNULL(abiertos.en_camino, 0)        AS en_camino
        FROM producto p
        JOIN proveedor pr ON pr.idproveedor = p.idproveedor
        LEFT JOIN vw_inventario_actual i ON i.idsucursal = ? AND i.idproducto = p.idproducto
        LEFT JOIN vw_retraso_proveedor r ON r.idproveedor = pr.idproveedor
        LEFT JOIN (
            SELECT d.idproducto, SUM(d.cantidad_pedida) AS en_camino
            FROM pedido pe JOIN detalle_pedido d ON d.idpedido = pe.idpedido
            WHERE pe.idsucursal = ? AND pe.estado IN ('pendiente', 'en_camino')
            GROUP BY d.idproducto
        ) abiertos ON abiertos.idproducto = p.idproducto
        WHERE p.activo = 1
    """, (idsucursal, idsucursal))
    ventas = _ventas_promedio(idsucursal)

    sugerencias = []
    for f in filas:
        venta = ventas.get((idsucursal, f["idproducto"]), 0.0)
        if venta <= 0:
            continue
        dias_entrega_real = f["dias_entrega_prometidos"] + max(0.0, float(f["retraso_promedio_horas"])) / 24
        punto_reorden = venta * (dias_entrega_real + DIAS_STOCK_SEGURIDAD)
        disponible = f["existencia"] + f["en_camino"]      # lo que ya viene en camino también cuenta
        if disponible > punto_reorden:
            continue
        # No pedir más de lo que se vende dentro de la vida útil (vida útil de 1 día = cobertura de 1 día)
        dias_objetivo = max(1.0, min(DIAS_COBERTURA_OBJETIVO, f["vida_util_dias"] * 0.6))
        cantidad = math.ceil(venta * (dias_entrega_real + dias_objetivo) - disponible)
        if cantidad <= 0:
            continue
        caja = max(1, int(f["tamano_caja"]))
        cantidad = math.ceil(cantidad / caja) * caja       # el proveedor surte en múltiplos de caja
        sugerencias.append({
            "idproducto": f["idproducto"],
            "producto": f["producto"],
            "sku": f["sku"],
            "idproveedor": f["idproveedor"],
            "proveedor": f["proveedor"],
            "existencia": f["existencia"],
            "en_camino": f["en_camino"],
            "tamano_caja": caja,
            "venta_promedio_diaria": round(venta, 2),
            "dias_entrega_real": round(dias_entrega_real, 1),
            "punto_reorden": math.ceil(punto_reorden),
            "cantidad_sugerida": cantidad,
            "costo_estimado": round(cantidad * float(f["costo"]), 2),
            "urgente": f["existencia"] < venta * dias_entrega_real,  # se acabará antes de que llegue
        })
    return sorted(sugerencias, key=lambda s: (not s["urgente"], s["producto"]))


def transferencias_sugeridas() -> list[dict]:
    """
    Sugiere mover producto entre sucursales: de una sucursal donde se va a echar a perder
    (sobreinventario) a otra donde está por agotarse. Regresa producto, origen, destino y cantidad.
    """
    analisis = _analisis_inventario()
    ventas = _ventas_promedio()

    # existencia por (sucursal, producto), incluyendo los que tienen 0
    existencia = {clave: g["existencia"] for clave, g in analisis.items()}
    nombres_suc = {s["idsucursal"]: s["nombre"] for s in listar_sucursales()}

    sugerencias = []
    for (suc_origen, prod), g in analisis.items():
        sobrante = g["unidades_en_riesgo"]
        if sobrante <= 0:
            continue
        candidatos = []
        for (suc_dest, prod_dest), venta_dest in ventas.items():
            if prod_dest != prod or suc_dest == suc_origen or venta_dest <= 0:
                continue
            exist_dest = existencia.get((suc_dest, prod), 0)
            if exist_dest < venta_dest * DIAS_FALTANTE:
                necesita = math.ceil(venta_dest * DIAS_COBERTURA_OBJETIVO - exist_dest)
                candidatos.append((necesita, suc_dest, exist_dest, venta_dest))
        for necesita, suc_dest, exist_dest, venta_dest in sorted(candidatos, reverse=True):
            if sobrante <= 0:
                break
            cantidad = min(sobrante, necesita)
            if cantidad <= 0:
                continue
            sobrante -= cantidad
            sugerencias.append({
                "idproducto": prod,
                "producto": g["producto"],
                "idsucursal_origen": suc_origen,
                "sucursal_origen": g["sucursal"],
                "idsucursal_destino": suc_dest,
                "sucursal_destino": nombres_suc.get(suc_dest, str(suc_dest)),
                "cantidad": cantidad,
                "existencia_destino": exist_dest,
                "venta_diaria_destino": round(venta_dest, 2),
                "valor_rescatado": round(cantidad * g["costo"], 2),
            })
    return sorted(sugerencias, key=lambda s: -s["valor_rescatado"])


def merma_por_causa(idsucursal: int | None = None, dias: int = 30) -> list[dict]:
    """Merma total (unidades y costo en pesos) agrupada por causa en los últimos `dias` días. Sin idsucursal = todas las sucursales."""
    sql = """
        SELECT c.nombre AS causa, SUM(m.cantidad) AS unidades, SUM(m.costo_total) AS costo_total
        FROM merma m
        JOIN causa_merma c ON c.idcausa = m.idcausa
        JOIN lote l        ON l.idlote  = m.idlote
        WHERE m.fecha >= DATEADD(DAY, -?, (SELECT fecha_ref FROM vw_fecha_referencia))
    """
    params: list = [dias]
    if idsucursal is not None:
        sql += " AND l.idsucursal = ?"
        params.append(idsucursal)
    return db.consultar(sql + " GROUP BY c.nombre ORDER BY costo_total DESC", tuple(params))


def merma_por_producto(idsucursal: int | None = None, dias: int = 30, top: int = 10) -> list[dict]:
    """Productos con más merma (en pesos) en los últimos `dias` días, con su causa principal. Sin idsucursal = todas las sucursales."""
    sql = f"""
        SELECT TOP ({int(top)}) p.nombre AS producto, SUM(m.cantidad) AS unidades, SUM(m.costo_total) AS costo_total
        FROM merma m
        JOIN lote l     ON l.idlote     = m.idlote
        JOIN producto p ON p.idproducto = l.idproducto
        WHERE m.fecha >= DATEADD(DAY, -?, (SELECT fecha_ref FROM vw_fecha_referencia))
    """
    params: list = [dias]
    if idsucursal is not None:
        sql += " AND l.idsucursal = ?"
        params.append(idsucursal)
    return db.consultar(sql + " GROUP BY p.nombre ORDER BY costo_total DESC", tuple(params))


def merma_por_semana(idsucursal: int | None = None, semanas: int = 8) -> list[dict]:
    """Costo de merma por semana en las últimas `semanas` semanas. Sin idsucursal = todas las sucursales."""
    sql = """
        SELECT DATEPART(ISO_WEEK, m.fecha) AS semana, MIN(CAST(m.fecha AS DATE)) AS desde,
               SUM(m.costo_total) AS costo_total
        FROM merma m
        JOIN lote l ON l.idlote = m.idlote
        WHERE m.fecha >= DATEADD(WEEK, -?, (SELECT fecha_ref FROM vw_fecha_referencia))
    """
    params: list = [semanas]
    if idsucursal is not None:
        sql += " AND l.idsucursal = ?"
        params.append(idsucursal)
    return db.consultar(sql + " GROUP BY DATEPART(ISO_WEEK, m.fecha) ORDER BY desde", tuple(params))


def merma_por_sucursal(dias: int = 30) -> list[dict]:
    """
    Compara la merma (unidades y costo) entre sucursales en los últimos `dias` días,
    con su región y tipo de sitio. Sirve para ver qué sucursales o tipos de sitio pierden más.
    """
    return db.consultar("""
        SELECT s.idsucursal, s.codigo, RTRIM(s.nombre) AS sucursal, s.region, s.tipo_sitio,
               SUM(m.cantidad) AS unidades, SUM(m.costo_total) AS costo_total,
               SUM(CASE WHEN c.nombre = 'Caducidad' THEN m.costo_total ELSE 0 END) AS costo_caducidad,
               SUM(CASE WHEN c.nombre <> 'Caducidad' THEN m.costo_total ELSE 0 END) AS costo_otras_causas
        FROM merma m
        JOIN lote l        ON l.idlote     = m.idlote
        JOIN sucursal s    ON s.idsucursal = l.idsucursal
        JOIN causa_merma c ON c.idcausa    = m.idcausa
        WHERE m.fecha >= DATEADD(DAY, -?, (SELECT fecha_ref FROM vw_fecha_referencia))
        GROUP BY s.idsucursal, s.codigo, s.nombre, s.region, s.tipo_sitio
        ORDER BY costo_total DESC
    """, (dias,))


def merma_y_quiebres(idsucursal: int | None = None, dias: int = 30) -> list[dict]:
    """
    Historial diario de inventario por producto en los últimos `dias` días (sin idsucursal = todas las sucursales, por sucursal y producto):
    unidades vendidas, expiradas, dañadas y horas sin producto (quiebre).
    Mucha expiración = se pide de más; muchas horas de quiebre = se pide de menos.
    Regresa también el porcentaje de merma sobre lo recibido y un diagnóstico.
    """
    por_sucursal = idsucursal is None
    col_suc = "i.idsucursal, RTRIM(s.nombre) AS sucursal, " if por_sucursal else ""
    grp_suc = "i.idsucursal, s.nombre, " if por_sucursal else ""
    filtro = "" if por_sucursal else "AND i.idsucursal = ?"
    params = (dias,) if por_sucursal else (dias, idsucursal)
    filas = db.consultar(f"""
        SELECT {"TOP (25) " if por_sucursal else ""}{col_suc}p.idproducto, p.nombre AS producto, p.sku,
               COUNT(*)                          AS dias_registrados,
               SUM(ISNULL(i.recibida, 0))        AS recibida,
               SUM(ISNULL(i.vendida, 0))         AS vendida,
               SUM(ISNULL(i.expirada, 0))        AS expirada,
               SUM(ISNULL(i.danada, 0))          AS danada,
               SUM(ISNULL(i.horas_quiebre, 0))   AS horas_quiebre,
               SUM((ISNULL(i.expirada, 0) + ISNULL(i.danada, 0)) * p.costo) AS costo_merma
        FROM inventario_diario i
        JOIN producto p ON p.idproducto = i.idproducto
        JOIN sucursal s ON s.idsucursal = i.idsucursal
        WHERE i.fecha >= DATEADD(DAY, -?, (SELECT fecha_ref FROM vw_fecha_referencia)) {filtro}
        GROUP BY {grp_suc}p.idproducto, p.nombre, p.sku
        ORDER BY costo_merma DESC
    """, params)
    for f in filas:
        base = f["recibida"] or (f["vendida"] + f["expirada"] + f["danada"])
        f["pct_merma"] = round((f["expirada"] + f["danada"]) * 100 / base, 1) if base else None
        f["horas_quiebre"] = round(float(f["horas_quiebre"] or 0), 1)
        f["costo_merma"] = round(float(f["costo_merma"] or 0), 2)
        if f["expirada"] > 0 and f["horas_quiebre"] == 0:
            f["diagnostico"] = "se pide de más: reducir pedido o aplicar descuento antes de caducar"
        elif f["horas_quiebre"] > 0 and f["expirada"] == 0:
            f["diagnostico"] = "se pide de menos: hay horas sin producto"
        elif f["horas_quiebre"] > 0 and f["expirada"] > 0:
            f["diagnostico"] = "mal momento de pedido: hay quiebres y también caducidad"
        else:
            f["diagnostico"] = "sin problema relevante"
    return filas


def stock_actual(idsucursal: int) -> list[dict]:
    """
    Existencia actual de cada producto en una sucursal con su venta promedio diaria, días de cobertura,
    próxima caducidad, unidades que no se alcanzarán a vender y un estado: agotado, bajo, exceso u ok.
    """
    productos = db.consultar("""
        SELECT p.idproducto, p.nombre AS producto, p.sku, c.nombre AS categoria, p.costo,
               ISNULL(i.existencia, 0) AS existencia, i.proxima_caducidad
        FROM producto p
        JOIN categoria c ON c.idcategoria = p.idcategoria
        LEFT JOIN vw_inventario_actual i ON i.idsucursal = ? AND i.idproducto = p.idproducto
        WHERE p.activo = 1
    """, (idsucursal,))
    ventas = _ventas_promedio(idsucursal)
    analisis = _analisis_inventario(idsucursal)
    orden = {"agotado": 0, "bajo": 1, "exceso": 2, "ok": 3}
    resultado = []
    for p in productos:
        venta = round(ventas.get((idsucursal, p["idproducto"]), 0.0), 2)
        existencia = p["existencia"] or 0
        if existencia == 0 and venta == 0:
            continue  # producto que esta sucursal no maneja
        riesgo = analisis.get((idsucursal, p["idproducto"]), {}).get("unidades_en_riesgo", 0)
        cobertura = round(existencia / venta, 1) if venta > 0 else None
        if existencia == 0:
            estado = "agotado"
        elif cobertura is not None and cobertura < DIAS_FALTANTE:
            estado = "bajo"
        elif riesgo > 0:
            estado = "exceso"
        else:
            estado = "ok"
        resultado.append({
            "idproducto": p["idproducto"], "producto": p["producto"], "sku": p["sku"],
            "categoria": p["categoria"], "existencia": existencia,
            "venta_promedio_diaria": venta, "dias_cobertura": cobertura,
            "proxima_caducidad": p["proxima_caducidad"], "unidades_en_riesgo": riesgo,
            "valor_inventario": round(existencia * float(p["costo"]), 2), "estado": estado,
        })
    return sorted(resultado, key=lambda r: (orden[r["estado"]], r["producto"]))


def trabajador_por_defecto(idsucursal: int) -> int:
    """Si no se indica quién hace la acción: el operador de la sucursal, o cualquier trabajador de ella."""
    fila = db.consultar("""
        SELECT TOP (1) t.idtrabajador
        FROM trabajador t JOIN puesto p ON p.idpuesto = t.idpuesto
        WHERE t.activo = 1
        ORDER BY CASE WHEN t.idsucursal = ? AND p.rol_sistema = 'operador' THEN 0
                      WHEN t.idsucursal = ? THEN 1 ELSE 2 END, t.idtrabajador
    """, (idsucursal, idsucursal))
    return fila[0]["idtrabajador"] if fila else 1


def historial_pedidos(idsucursal: int, dias: int = 30) -> list[dict]:
    """Pedidos de una sucursal en los últimos `dias` días con su estado, retraso y unidades pedidas/recibidas."""
    filas = db.consultar("""
        SELECT pe.idpedido, pr.nombre AS proveedor, pe.fecha_pedido, pe.fecha_prometida, pe.fecha_llegada, pe.estado,
               SUM(d.cantidad_pedida) AS unidades_pedidas,
               SUM(d.cantidad_recibida) AS unidades_recibidas,
               SUM(d.cantidad_danada) AS unidades_danadas,
               SUM(d.cantidad_pedida * d.costo_unitario) AS costo,
               STRING_AGG(p.nombre, ', ') AS productos
        FROM pedido pe
        JOIN proveedor pr     ON pr.idproveedor = pe.idproveedor
        JOIN detalle_pedido d ON d.idpedido     = pe.idpedido
        JOIN producto p       ON p.idproducto   = d.idproducto
        WHERE pe.idsucursal = ?
          AND pe.fecha_pedido >= DATEADD(DAY, -?, (SELECT fecha_ref FROM vw_fecha_referencia))
        GROUP BY pe.idpedido, pr.nombre, pe.fecha_pedido, pe.fecha_prometida, pe.fecha_llegada, pe.estado
        ORDER BY pe.fecha_pedido DESC
    """, (idsucursal, dias))
    for f in filas:
        if f["fecha_llegada"]:
            minutos = (datetime.fromisoformat(f["fecha_llegada"]) - datetime.fromisoformat(f["fecha_prometida"])).total_seconds() / 60
            f["retraso_horas"] = round(minutos / 60, 1)
        else:
            f["retraso_horas"] = None
        f["costo"] = round(float(f["costo"] or 0), 2)
    return filas


def detalle_pedido(idpedido: int) -> dict:
    """Encabezado y líneas de un pedido (para registrar su llegada producto por producto)."""
    pedido = db.consultar("""
        SELECT pe.idpedido, pe.idsucursal, pr.nombre AS proveedor, pe.fecha_pedido, pe.fecha_prometida,
               pe.fecha_llegada, pe.estado
        FROM pedido pe JOIN proveedor pr ON pr.idproveedor = pe.idproveedor
        WHERE pe.idpedido = ?
    """, (idpedido,))
    if not pedido:
        raise ValueError("Pedido no encontrado")
    lineas = db.consultar("""
        SELECT d.iddetalle_pedido, p.nombre AS producto, p.sku, d.cantidad_pedida, d.cantidad_recibida,
               d.cantidad_danada, d.costo_unitario
        FROM detalle_pedido d JOIN producto p ON p.idproducto = d.idproducto
        WHERE d.idpedido = ?
    """, (idpedido,))
    return {**pedido[0], "lineas": lineas}


def resumen_sucursal(idsucursal: int) -> dict:
    """Indicadores clave de una sucursal: valor en riesgo de merma, lotes por caducar, productos con sobreinventario, entregas pendientes y retrasadas, y merma del mes."""
    caducar = productos_por_caducar(idsucursal, 7)
    sobre = sobreinventario(idsucursal)
    entregas = entregas_pendientes(idsucursal)
    merma_mes = sum(float(m["costo_total"] or 0) for m in merma_por_causa(idsucursal, 30))
    return {
        "valor_en_riesgo_7_dias": round(sum(c["valor_en_riesgo"] for c in caducar), 2),
        "lotes_por_caducar_7_dias": len(caducar),
        "lotes_por_caducar_48_horas": sum(1 for c in caducar if c["dias_para_caducar"] <= 2),
        "productos_con_sobreinventario": len(sobre),
        "valor_sobreinventario_en_riesgo": round(sum(s["valor_en_riesgo"] for s in sobre), 2),
        "entregas_pendientes": len(entregas),
        "entregas_retrasadas": sum(1 for e in entregas if e["va_tarde"]),
        "merma_ultimos_30_dias": round(merma_mes, 2),
    }


# =====================================================================
# ACCIONES (escriben en la BD) - solo para endpoints, NUNCA para la IA
# =====================================================================

def registrar_llegada(idpedido: int, recibidos: dict[int, dict] | None = None) -> dict:
    """
    Marca un pedido como recibido y crea los lotes correspondientes.
    `recibidos` = {iddetalle_pedido: {"cantidad_recibida": n, "cantidad_danada": n}}
    Si no se manda, se asume que llegó todo completo y en buen estado.
    """
    recibidos = recibidos or {}
    pedido = db.consultar("SELECT idsucursal, idtrabajador, estado FROM pedido WHERE idpedido = ?", (idpedido,))
    if not pedido:
        raise ValueError("Pedido no encontrado")
    if pedido[0]["estado"] == "recibido":
        raise ValueError("Ese pedido ya fue recibido")
    idsucursal = pedido[0]["idsucursal"]

    detalles = db.consultar("""
        SELECT d.iddetalle_pedido, d.idproducto, d.cantidad_pedida, p.vida_util_dias, p.costo
        FROM detalle_pedido d JOIN producto p ON p.idproducto = d.idproducto
        WHERE d.idpedido = ?
    """, (idpedido,))

    hoy = _hoy()
    causa_proveedor = db.consultar("SELECT idcausa FROM causa_merma WHERE nombre = 'Proveedor'")
    for d in detalles:
        info = recibidos.get(d["iddetalle_pedido"], {})
        recibida = int(info.get("cantidad_recibida", d["cantidad_pedida"]))
        danada = int(info.get("cantidad_danada", 0))
        buenas = max(0, recibida - danada)

        db.ejecutar("UPDATE detalle_pedido SET cantidad_recibida = ?, cantidad_danada = ? WHERE iddetalle_pedido = ?",
                    (recibida, danada, d["iddetalle_pedido"]))
        if recibida > 0:
            caducidad = hoy + timedelta(days=d["vida_util_dias"])
            idlote = db.ejecutar("""
                INSERT INTO lote (idproducto, idsucursal, iddetalle_pedido, cantidad_inicial, cantidad_actual,
                                  fecha_entrada, fecha_caducidad)
                OUTPUT INSERTED.idlote VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (d["idproducto"], idsucursal, d["iddetalle_pedido"], recibida, buenas, hoy, caducidad))
            # Lo que llegó dañado se registra como merma imputable al proveedor
            if danada > 0 and causa_proveedor:
                db.ejecutar("""
                    INSERT INTO merma (idlote, idcausa, idtrabajador, cantidad, costo_total, fecha, observaciones)
                    VALUES (?, ?, ?, ?, ?, ?, 'Llegó dañado en la recepción')
                """, (idlote, causa_proveedor[0]["idcausa"], pedido[0]["idtrabajador"], danada,
                      danada * float(d["costo"]), _ahora()))

    # Hora de llegada según la fecha de referencia, para no distorsionar el retraso histórico con datos del dataset
    db.ejecutar("UPDATE pedido SET fecha_llegada = ?, estado = 'recibido' WHERE idpedido = ?", (_ahora(), idpedido))
    return {"idpedido": idpedido, "estado": "recibido", "lotes_creados": len(detalles)}


def registrar_merma(idlote: int, idcausa: int, cantidad: int, idtrabajador: int, observaciones: str | None = None) -> int:
    """Registra una merma y descuenta la cantidad del lote."""
    lote = db.consultar("""
        SELECT l.cantidad_actual, p.costo FROM lote l JOIN producto p ON p.idproducto = l.idproducto
        WHERE l.idlote = ?
    """, (idlote,))
    if not lote:
        raise ValueError("Lote no encontrado")
    if cantidad > lote[0]["cantidad_actual"]:
        raise ValueError("La merma es mayor que la existencia del lote")
    idmerma = db.ejecutar("""
        INSERT INTO merma (idlote, idcausa, idtrabajador, cantidad, costo_total, fecha, observaciones)
        OUTPUT INSERTED.idmerma VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (idlote, idcausa, idtrabajador, cantidad, cantidad * float(lote[0]["costo"]), _ahora(), observaciones))
    db.ejecutar("UPDATE lote SET cantidad_actual = cantidad_actual - ? WHERE idlote = ?", (cantidad, idlote))
    return idmerma


def aplicar_promocion(idlote: int, porcentaje: float, idtrabajador: int, dias_vigencia: int | None = None,
                      motivo: str = "caducidad", origen: str = "sistema") -> int:
    """Aplica un descuento a un lote. Por defecto dura hasta la fecha de caducidad del lote."""
    lote = db.consultar("SELECT fecha_caducidad FROM lote WHERE idlote = ?", (idlote,))
    if not lote:
        raise ValueError("Lote no encontrado")
    hoy = _hoy()
    fin = hoy + timedelta(days=dias_vigencia) if dias_vigencia else _a_fecha(lote[0]["fecha_caducidad"])
    return db.ejecutar("""
        INSERT INTO promocion (idlote, porcentaje, fecha_inicio, fecha_fin, motivo, origen, estado, idtrabajador)
        OUTPUT INSERTED.idpromocion VALUES (?, ?, ?, ?, ?, ?, 'activa', ?)
    """, (idlote, porcentaje, hoy, max(fin, hoy), motivo, origen, idtrabajador))
