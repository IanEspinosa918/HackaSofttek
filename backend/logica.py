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
from datetime import date, datetime, timedelta

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

def _hoy() -> date:
    return date.today()


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
        SELECT l.idlote, l.idsucursal, s.nombre AS sucursal, l.idproducto, p.nombre AS producto,
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


def _ventas_promedio(idsucursal: int | None = None) -> dict[tuple, float]:
    sql = "SELECT idsucursal, idproducto, venta_promedio_diaria FROM vw_venta_promedio_diaria"
    params: tuple = ()
    if idsucursal is not None:
        sql += " WHERE idsucursal = ?"
        params = (idsucursal,)
    return {(r["idsucursal"], r["idproducto"]): float(r["venta_promedio_diaria"] or 0)
            for r in db.consultar(sql, params)}


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
    """Lista todas las sucursales activas con su id y nombre. Úsala para traducir el nombre de una sucursal a su id."""
    return db.consultar("SELECT idsucursal, nombre, direccion FROM sucursal WHERE activa = 1 ORDER BY idsucursal")


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
    Desempeño de entrega de cada proveedor según lo registrado por los operadores:
    número de entregas, retraso promedio en horas y porcentaje de entregas tarde.
    """
    return db.consultar("""
        SELECT r.idproveedor, r.proveedor, pr.dias_entrega_prometidos, r.entregas,
               CAST(r.retraso_promedio_horas AS DECIMAL(10,1)) AS retraso_promedio_horas,
               CAST(r.pct_entregas_tarde AS DECIMAL(5,1))      AS pct_entregas_tarde
        FROM vw_retraso_proveedor r
        JOIN proveedor pr ON pr.idproveedor = r.idproveedor
        ORDER BY r.retraso_promedio_horas DESC
    """)


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
    ahora = datetime.now()
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
        SELECT v.idproducto, p.nombre AS producto, p.vida_util_dias, p.costo,
               pr.idproveedor, pr.nombre AS proveedor, pr.dias_entrega_prometidos,
               v.venta_promedio_diaria,
               ISNULL(i.existencia, 0)              AS existencia,
               ISNULL(r.retraso_promedio_horas, 0)  AS retraso_promedio_horas
        FROM vw_venta_promedio_diaria v
        JOIN producto  p  ON p.idproducto   = v.idproducto
        JOIN proveedor pr ON pr.idproveedor = p.idproveedor
        LEFT JOIN vw_inventario_actual i ON i.idsucursal = v.idsucursal AND i.idproducto = v.idproducto
        LEFT JOIN vw_retraso_proveedor r ON r.idproveedor = pr.idproveedor
        WHERE v.idsucursal = ? AND p.activo = 1
    """, (idsucursal,))

    sugerencias = []
    for f in filas:
        venta = float(f["venta_promedio_diaria"] or 0)
        if venta <= 0:
            continue
        dias_entrega_real = f["dias_entrega_prometidos"] + max(0.0, float(f["retraso_promedio_horas"])) / 24
        punto_reorden = venta * (dias_entrega_real + DIAS_STOCK_SEGURIDAD)
        if f["existencia"] > punto_reorden:
            continue
        dias_objetivo = min(DIAS_COBERTURA_OBJETIVO, f["vida_util_dias"] * 0.6)
        cantidad = math.ceil(venta * (dias_entrega_real + dias_objetivo) - f["existencia"])
        if cantidad <= 0:
            continue
        sugerencias.append({
            "idproducto": f["idproducto"],
            "producto": f["producto"],
            "idproveedor": f["idproveedor"],
            "proveedor": f["proveedor"],
            "existencia": f["existencia"],
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
        WHERE m.fecha >= DATEADD(DAY, -?, CAST(GETDATE() AS DATE))
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
        WHERE m.fecha >= DATEADD(DAY, -?, CAST(GETDATE() AS DATE))
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
        WHERE m.fecha >= DATEADD(WEEK, -?, CAST(GETDATE() AS DATE))
    """
    params: list = [semanas]
    if idsucursal is not None:
        sql += " AND l.idsucursal = ?"
        params.append(idsucursal)
    return db.consultar(sql + " GROUP BY DATEPART(ISO_WEEK, m.fecha) ORDER BY desde", tuple(params))


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
                    INSERT INTO merma (idlote, idcausa, idtrabajador, cantidad, costo_total, observaciones)
                    VALUES (?, ?, ?, ?, ?, 'Llegó dañado en la recepción')
                """, (idlote, causa_proveedor[0]["idcausa"], pedido[0]["idtrabajador"], danada,
                      danada * float(d["costo"])))

    db.ejecutar("UPDATE pedido SET fecha_llegada = SYSDATETIME(), estado = 'recibido' WHERE idpedido = ?", (idpedido,))
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
        INSERT INTO merma (idlote, idcausa, idtrabajador, cantidad, costo_total, observaciones)
        OUTPUT INSERTED.idmerma VALUES (?, ?, ?, ?, ?, ?)
    """, (idlote, idcausa, idtrabajador, cantidad, cantidad * float(lote[0]["costo"]), observaciones))
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
