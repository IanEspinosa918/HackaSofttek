"""
cargar_historial.py - Llena la base de datos con 60 días de operación para TODAS las sucursales,
para que el dashboard, los reportes y las gráficas tengan datos.

Parte de los datos reales que ya están en la BD (sucursales, productos con su precio, costo, vida útil
y tamaño de caja, proveedores con sus días de entrega y su cumplimiento de contrato) y simula la
operación día por día:
  - Ventas diarias por producto (más en fin de semana, más en aeropuertos).
  - Pedidos a proveedor con su fecha prometida y su llegada real (retrasos y surtido incompleto
    según el desempeño de cada proveedor).
  - Lotes con su caducidad; lo que no se vende a tiempo se registra como merma por caducidad.
  - Merma por daño, robo y producto que llegó dañado del proveedor.
  - Historial diario de inventario (inventario_diario) con horas sin producto.

Historias incluidas para la demo:
  - S030 y S001 piden de más donas -> mucha merma por caducidad.
  - S022 pide de menos bagels -> quiebres de inventario.
  - Northfield Bakery Partners llega tarde más seguido de lo que dice su contrato.

IMPORTANTE: borra y vuelve a generar ventas, lotes, pedidos, mermas, promociones, transferencias
e inventario diario. NO toca sucursales, trabajadores, productos, proveedores ni reportes.

Uso (dentro de backend, con el venv activo):
    python cargar_historial.py              -> pide confirmación y carga
    python cargar_historial.py --si         -> sin confirmación
    python cargar_historial.py --sin-reasignar   -> no cambia el proveedor de ningún producto
"""
import math
import random
import sys
from collections import defaultdict
from datetime import date, datetime, time, timedelta

DIAS = 60
FECHA_FIN = date(2026, 9, 30)          # último día del dataset (fecha de referencia)
SEMILLA = 2026                         # misma semilla = mismos datos cada vez
HORAS_OPERACION = 16

# Reasignación opcional de proveedor (todos los productos del dataset vienen de Northfield)
REASIGNAR = [
    ("bagel", "SUP08"),            # Metro Wholesale Foods
    ("muffin", "SUP03"),           # Summit Frozen Foods
    ("mffin", "SUP03"),
    ("oatmeal", "SUP07"),          # Harbor Catering Supplies
]

# Desempeño REAL simulado de cada proveedor (vs. su contrato): (prob. de llegar a tiempo, prob. de surtir completo)
DESEMPENO = {"SUP01": (0.72, 0.90), "SUP03": (0.90, 0.93), "SUP07": (0.93, 0.96), "SUP08": (0.86, 0.84)}
DESEMPENO_DEFECTO = (0.92, 0.95)

# Historias: (código de sucursal, texto que debe contener el producto) -> factor de pedido
SESGOS = [
    ("S030", "donut", 1.75),
    ("S001", "6 donuts", 1.8),
    ("S001", "6 bacon", 1.5),
    ("S022", "bagel", 0.55),
    ("S012", "croiss", 1.45),
]


# =====================================================================
# Simulación (no toca la base de datos)
# =====================================================================
def demanda_base(precio: float) -> float:
    if precio < 0.05:
        return 1.5
    if precio < 1:
        return 26
    if precio < 3:
        return 20
    if precio < 6:
        return 16
    if precio < 13:
        return 12
    return 10


def poisson(rng: random.Random, lam: float) -> int:
    if lam <= 0:
        return 0
    if lam > 30:
        return max(0, int(round(rng.gauss(lam, math.sqrt(lam)))))
    L, k, p = math.exp(-lam), 0, 1.0
    while True:
        p *= rng.random()
        if p <= L:
            return k
        k += 1


def simular(sucursales, productos, proveedores, trabajadores, causas, ids_inicio):
    """
    Regresa un diccionario con las filas a insertar en cada tabla (con ids ya asignados).
    sucursales: [{idsucursal, codigo, tipo_sitio}], productos: [{idproducto, nombre, precio_venta, costo,
    vida_util_dias, tamano_caja, idproveedor}], proveedores: {idproveedor: {codigo, dias}},
    trabajadores: {idsucursal: idtrabajador}, causas: {nombre: idcausa}
    """
    rng = random.Random(SEMILLA)
    inicio = FECHA_FIN - timedelta(days=DIAS - 1)
    nid = dict(ids_inicio)              # siguiente id por tabla

    def siguiente(tabla):
        v = nid[tabla]
        nid[tabla] += 1
        return v

    filas = defaultdict(list)
    factor_sitio = {"Airport": 1.2, "Rail Station": 1.0, "Bus Terminal": 0.8, "Resort": 1.1}

    for suc in sucursales:
        ids = suc["idsucursal"]
        f_suc = factor_sitio.get(suc.get("tipo_sitio"), 1.0) * rng.uniform(0.75, 1.25)
        trab = trabajadores.get(ids)
        prods = []
        for p in productos:
            if float(p["precio_venta"]) < 0.05:
                continue   # producto de prueba del dataset (precio 0.01): no se simula
            sesgo = 1.0
            for codigo, texto, factor in SESGOS:
                if suc.get("codigo") == codigo and texto in p["nombre"].lower():
                    sesgo = factor
            prods.append({**p, "lam": demanda_base(float(p["precio_venta"])) * f_suc * rng.uniform(0.7, 1.3),
                          "sesgo": sesgo, "lotes": [], "pendiente": []})

        for n in range(DIAS):
            dia = inicio + timedelta(days=n)
            ultimo = dia == FECHA_FIN
            f_dia = {4: 1.2, 5: 1.3, 6: 1.25, 0: 0.9}.get(dia.weekday(), 1.0)
            # Fin de día del dataset: lo que sigue "en camino" se queda pendiente
            pedidos_hoy = defaultdict(list)       # idproveedor -> [(producto, cantidad)]
            detalle_venta = []

            for p in prods:
                apertura = sum(l["qty"] for l in p["lotes"])
                recibida = 0
                # 1) Llegadas de hoy
                for ped in [x for x in p["pendiente"] if x["llegada"].date() == dia]:
                    p["pendiente"].remove(ped)
                    buenas = ped["recibida"] - ped["danada"]
                    idlote = siguiente("lote")
                    cad = dia + timedelta(days=int(p["vida_util_dias"]))
                    fila_lote = [idlote, p["idproducto"], ids, ped["iddetalle"], ped["recibida"], buenas, dia, cad]
                    filas["lote"].append(fila_lote)
                    p["lotes"].append({"idlote": idlote, "qty": buenas, "cad": cad, "fila": fila_lote})
                    recibida += ped["recibida"]
                    if ped["danada"]:
                        filas["merma"].append([siguiente("merma"), idlote, causas["Proveedor"], trab, ped["danada"],
                                               round(ped["danada"] * float(p["costo"]), 2),
                                               ped["llegada"], "Llegó dañado en la recepción"])
                # 2) Ventas (lo que caduca primero se vende primero)
                demanda = poisson(rng, p["lam"] * f_dia)
                vendida = 0
                for l in sorted(p["lotes"], key=lambda x: x["cad"]):
                    tomar = min(l["qty"], demanda - vendida)
                    l["qty"] -= tomar
                    vendida += tomar
                    if vendida >= demanda:
                        break
                faltante = demanda - vendida
                horas_quiebre = round(HORAS_OPERACION * faltante / demanda * 2) / 2 if demanda else 0
                if vendida:
                    detalle_venta.append((p, vendida))
                # 3) Daño y robo en tienda (ocasional)
                danada = 0
                for causa, prob, maximo in (("Daño", 0.07, 2), ("Robo", 0.012, 1)):
                    con_stock = [l for l in p["lotes"] if l["qty"] > 0]
                    if con_stock and rng.random() < prob:
                        l = con_stock[0]
                        cant = min(l["qty"], rng.randint(1, maximo))
                        l["qty"] -= cant
                        danada += cant
                        filas["merma"].append([siguiente("merma"), l["idlote"], causas[causa], trab, cant,
                                               round(cant * float(p["costo"]), 2), datetime.combine(dia, time(15, 30)),
                                               "Producto dañado en tienda" if causa == "Daño" else "Faltante en conteo"])
                # 4) Caducidad al cierre (el último día no: esos lotes quedan como alerta de "por caducar")
                expirada = 0
                if not ultimo:
                    for l in p["lotes"]:
                        if l["qty"] > 0 and l["cad"] <= dia + timedelta(days=1):
                            filas["merma"].append([siguiente("merma"), l["idlote"], causas["Caducidad"], trab, l["qty"],
                                                   round(l["qty"] * float(p["costo"]), 2),
                                                   datetime.combine(dia, time(21, 0)), "Producto vencido al cierre"])
                            expirada += l["qty"]
                            l["qty"] = 0
                cierre = sum(l["qty"] for l in p["lotes"])
                for l in p["lotes"]:
                    l["fila"][5] = l["qty"]          # cantidad_actual del lote = lo que le queda
                p["lotes"] = [l for l in p["lotes"] if l["qty"] > 0]
                en_pedido = sum(x["pedida"] for x in p["pendiente"])
                filas["inventario_diario"].append([ids, p["idproducto"], dia, apertura, recibida, vendida, expirada,
                                                   danada, cierre, en_pedido, horas_quiebre])
                # 5) Pedido para el día de llegada (política de reorden con el sesgo de la sucursal)
                prov = proveedores[p["idproveedor"]]
                L = max(1, int(prov["dias"]))
                llegada_dia = dia + timedelta(days=L)
                f_llegada = {4: 1.2, 5: 1.3, 6: 1.25, 0: 0.9}.get(llegada_dia.weekday(), 1.0)
                # Lo que todavía servirá ese día: lotes y pedidos en camino que no caducan antes,
                # menos lo que se venderá de ellos mientras llega el nuevo pedido
                vida = max(1, int(p["vida_util_dias"]))
                util = sum(l["qty"] for l in p["lotes"] if l["cad"] > llegada_dia)
                util += sum(x["recibida"] - x["danada"] for x in p["pendiente"]
                            if x["llegada"].date() <= llegada_dia
                            and x["llegada"].date() + timedelta(days=vida) > llegada_dia)
                util = max(0.0, util - p["lam"] * min(L - 1, vida - 1))
                objetivo = (p["lam"] * f_llegada + 0.5 * math.sqrt(p["lam"])) * p["sesgo"]
                falta = objetivo - util
                caja = max(1, int(p["tamano_caja"] or 1))
                if falta > caja * 0.35:
                    cantidad = max(caja, int(math.ceil(falta / caja - 0.3)) * caja)   # se pide en cajas completas
                    pedidos_hoy[p["idproveedor"]].append((p, cantidad))

            # Venta del día (un ticket resumen por sucursal)
            if detalle_venta:
                idventa = siguiente("venta")
                total = 0.0
                for p, cant in detalle_venta:
                    precio = float(p["precio_venta"])
                    total += cant * precio
                    filas["detalle_venta"].append([siguiente("detalle_venta"), idventa, p["idproducto"], None, cant,
                                                   precio, 0])
                filas["venta"].append([idventa, ids, datetime.combine(dia, time(20, 0)), round(total, 2)])

            # Pedidos del día, uno por proveedor
            for idprov, lineas in pedidos_hoy.items():
                prov = proveedores[idprov]
                a_tiempo, surtido = DESEMPENO.get(prov["codigo"], DESEMPENO_DEFECTO)
                fecha_pedido = datetime.combine(dia, time(8, 0))
                prometida = datetime.combine(dia + timedelta(days=max(1, int(prov["dias"]))), time(10, 0))
                if rng.random() < a_tiempo:
                    llegada = prometida - timedelta(minutes=rng.randint(0, 50))
                else:
                    llegada = prometida + timedelta(hours=rng.choice([1, 2, 2, 3, 3, 4, 5, 6, 8, 26]))
                pendiente = llegada.date() > FECHA_FIN
                idpedido = siguiente("pedido")
                estado = "en_camino" if pendiente else "recibido"
                filas["pedido"].append([idpedido, idprov, ids, trab, fecha_pedido, prometida,
                                        None if pendiente else llegada, estado, None])
                completo = rng.random() < surtido
                for p, cant in lineas:
                    recibida = cant if completo else int(cant * rng.uniform(0.7, 0.95))
                    danada = rng.randint(1, 2) if (not pendiente and rng.random() < 0.03 and recibida > 2) else 0
                    iddet = siguiente("detalle_pedido")
                    filas["detalle_pedido"].append([iddet, idpedido, p["idproducto"], cant,
                                                    None if pendiente else recibida, danada if not pendiente else 0,
                                                    float(p["costo"])])
                    p["pendiente"].append({"iddetalle": iddet, "pedida": cant, "recibida": recibida,
                                           "danada": danada, "llegada": llegada})
    return filas


# =====================================================================
# Base de datos
# =====================================================================
COLUMNAS = {
    "pedido": "idpedido, idproveedor, idsucursal, idtrabajador, fecha_pedido, fecha_prometida, fecha_llegada, estado, observaciones",
    "detalle_pedido": "iddetalle_pedido, idpedido, idproducto, cantidad_pedida, cantidad_recibida, cantidad_danada, costo_unitario",
    "lote": "idlote, idproducto, idsucursal, iddetalle_pedido, cantidad_inicial, cantidad_actual, fecha_entrada, fecha_caducidad",
    "venta": "idventa, idsucursal, fecha, total",
    "detalle_venta": "iddetalle_venta, idventa, idproducto, idlote, cantidad, precio_unitario, descuento_pct",
    "merma": "idmerma, idlote, idcausa, idtrabajador, cantidad, costo_total, fecha, observaciones",
    "inventario_diario": "idsucursal, idproducto, fecha, cantidad_apertura, recibida, vendida, expirada, danada, cantidad_cierre, en_pedido, horas_quiebre",
}
CON_IDENTITY = {"pedido", "detalle_pedido", "lote", "venta", "detalle_venta", "merma"}
ORDEN_INSERT = ["pedido", "detalle_pedido", "lote", "venta", "detalle_venta", "merma", "inventario_diario"]
ORDEN_BORRADO = ["promocion", "transferencia", "merma", "detalle_venta", "venta", "lote",
                 "detalle_pedido", "pedido", "inventario_diario"]


def main():
    import db  # se importa aquí para poder probar la simulación sin base de datos

    confirmar = "--si" not in sys.argv
    reasignar = "--sin-reasignar" not in sys.argv
    print(f"Se generarán {DIAS} días de operación (hasta {FECHA_FIN}) para todas las sucursales.")
    print("Se BORRARÁN ventas, lotes, pedidos, mermas, promociones, transferencias e inventario diario.")
    if confirmar and input("¿Continuar? (s/n): ").strip().lower() not in ("s", "si", "sí", "y"):
        print("Cancelado.")
        return

    con = db.conexion_app()
    cur = con.cursor()
    cur.fast_executemany = True
    try:
        def consultar(sql, params=()):
            cur.execute(sql, params)
            cols = [c[0] for c in cur.description]
            return [dict(zip(cols, r)) for r in cur.fetchall()]

        # Reasignación de proveedor (opcional)
        if reasignar:
            for texto, codigo in REASIGNAR:
                cur.execute("""
                    UPDATE producto SET idproveedor = (SELECT idproveedor FROM proveedor WHERE codigo = ?)
                    WHERE LOWER(nombre) LIKE ? AND EXISTS (SELECT 1 FROM proveedor WHERE codigo = ?)
                """, (codigo, f"%{texto}%", codigo))
            print("Proveedores reasignados: bagels -> Metro Wholesale, muffins -> Summit Frozen, avena -> Harbor Catering.")

        sucursales = consultar("SELECT idsucursal, codigo, tipo_sitio FROM sucursal WHERE activa = 1")
        productos = consultar("""SELECT idproducto, nombre, precio_venta, costo, vida_util_dias, tamano_caja, idproveedor
                                 FROM producto WHERE activo = 1""")
        proveedores = {r["idproveedor"]: {"codigo": r["codigo"], "dias": r["dias_entrega_prometidos"]}
                       for r in consultar("SELECT idproveedor, codigo, dias_entrega_prometidos FROM proveedor")}
        trabajadores = {}
        for r in consultar("""SELECT t.idsucursal, t.idtrabajador FROM trabajador t JOIN puesto p ON p.idpuesto = t.idpuesto
                              WHERE t.activo = 1 ORDER BY CASE WHEN p.rol_sistema = 'operador' THEN 0 ELSE 1 END, t.idtrabajador"""):
            trabajadores.setdefault(r["idsucursal"], r["idtrabajador"])
        cualquiera = next(iter(trabajadores.values()))
        for s in sucursales:
            trabajadores.setdefault(s["idsucursal"], cualquiera)
        causas = {r["nombre"]: r["idcausa"] for r in consultar("SELECT idcausa, nombre FROM causa_merma")}
        causas.setdefault("Daño", causas.get("Danio", causas.get("Dano", 2)))

        # Borrado de los datos de operación
        for tabla in ORDEN_BORRADO:
            cur.execute(f"DELETE FROM {tabla}")
        for tabla in CON_IDENTITY | {"promocion", "transferencia"}:
            cur.execute(f"DBCC CHECKIDENT ('{tabla}', RESEED, 0) WITH NO_INFOMSGS")

        filas = simular(sucursales, productos, proveedores, trabajadores, causas, {t: 1 for t in CON_IDENTITY})

        for tabla in ORDEN_INSERT:
            datos = filas.get(tabla, [])
            if not datos:
                continue
            cols = COLUMNAS[tabla]
            marcas = ", ".join("?" * len(cols.split(",")))
            if tabla in CON_IDENTITY:
                cur.execute(f"SET IDENTITY_INSERT {tabla} ON")
            for i in range(0, len(datos), 2000):
                cur.executemany(f"INSERT INTO {tabla} ({cols}) VALUES ({marcas})", datos[i:i + 2000])
            if tabla in CON_IDENTITY:
                cur.execute(f"SET IDENTITY_INSERT {tabla} OFF")
            print(f"  {tabla:<18} {len(datos):>7,} filas")
        con.commit()
    except Exception:
        con.rollback()
        print("\nOcurrió un error; no se guardó nada (la base de datos quedó como estaba).")
        raise
    finally:
        con.close()

    print("\nListo. Reinicia el backend (o espera 1 minuto) para que tome la fecha de referencia.")


if __name__ == "__main__":
    main()
