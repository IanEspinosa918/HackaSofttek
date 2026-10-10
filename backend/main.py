"""
main.py - API del proyecto (FastAPI).

Arrancar:   uvicorn main:app --reload
Documentación interactiva para probar cada endpoint:  http://localhost:8000/docs
"""
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

import db
import ia
import logica
from seguridad import verificar_contrasena

app = FastAPI(title="Tienda Inteligente - API", version="0.1.0")

# Permite que el HTML abierto desde otra dirección (o con doble clic) llame a la API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _error(e: Exception, codigo: int = 400):
    raise HTTPException(status_code=codigo, detail=str(e))


# =====================================================================
# Modelos de entrada
# =====================================================================
class LoginEntrada(BaseModel):
    usuario: str
    contrasena: str


class ChatEntrada(BaseModel):
    mensaje: str = Field(min_length=1, max_length=2000)
    id_sesion: str | None = None
    idsucursal: int | None = None
    nombre_usuario: str | None = None


class ReporteEntrada(BaseModel):
    idsucursal: int
    idtrabajador: int


class RevisionEntrada(BaseModel):
    idgerente: int
    comentario: str | None = None


class DetalleRecibido(BaseModel):
    iddetalle_pedido: int
    cantidad_recibida: int = Field(ge=0)
    cantidad_danada: int = Field(default=0, ge=0)


class LlegadaEntrada(BaseModel):
    detalles: list[DetalleRecibido] = []   # vacío = llegó todo completo


class MermaEntrada(BaseModel):
    idlote: int
    idcausa: int
    cantidad: int = Field(gt=0)
    idtrabajador: int
    observaciones: str | None = None


class PromocionEntrada(BaseModel):
    idlote: int
    porcentaje: float = Field(gt=0, le=100)
    idtrabajador: int
    dias_vigencia: int | None = None
    motivo: str = "caducidad"
    origen: str = "sistema"


class DetallePedidoEntrada(BaseModel):
    idproducto: int
    cantidad: int = Field(gt=0)


class PedidoEntrada(BaseModel):
    idproveedor: int
    idsucursal: int
    idtrabajador: int
    productos: list[DetallePedidoEntrada]


# =====================================================================
# General
# =====================================================================
@app.get("/api/salud", tags=["General"])
def salud():
    """Verifica que la API y la base de datos respondan."""
    try:
        db.consultar("SELECT 1 AS ok")
        bd = "conectada"
    except Exception as e:
        bd = f"error: {e}"
    return {"api": "ok", "base_de_datos": bd, "modelo_ia": ia.MODELO}


@app.post("/api/login", tags=["General"])
def login(datos: LoginEntrada):
    """
    Regresa {ok: true, usuario: {...}} o {ok: false, codigo: ...}
    con los mismos códigos que espera login.html.
    """
    filas = db.consultar("""
        SELECT t.idtrabajador, t.nombre, t.apellido, t.idsucursal, s.nombre AS sucursal,
               p.rol_sistema, t.contrasena_hash
        FROM trabajador t
        JOIN puesto   p ON p.idpuesto   = t.idpuesto
        JOIN sucursal s ON s.idsucursal = t.idsucursal
        WHERE t.usuario = ? AND t.activo = 1
    """, (datos.usuario.strip(),))
    if not filas:
        return {"ok": False, "codigo": "USUARIO_NO_ENCONTRADO"}
    t = filas[0]
    if not verificar_contrasena(datos.contrasena, t["contrasena_hash"]):
        return {"ok": False, "codigo": "CONTRASENA_INCORRECTA"}
    if t["rol_sistema"] not in ("operador", "gerente"):
        return {"ok": False, "codigo": "SIN_ACCESO"}
    t.pop("contrasena_hash")
    return {"ok": True, "usuario": t}


@app.get("/api/sucursales", tags=["General"])
def sucursales():
    return logica.listar_sucursales()


# =====================================================================
# Dashboard e inventario
# =====================================================================
@app.get("/api/dashboard/{idsucursal}", tags=["Inventario"])
def dashboard(idsucursal: int):
    """Todo lo que necesita dashboard.html en una sola llamada."""
    return {
        "indicadores": logica.resumen_sucursal(idsucursal),
        "caducidad": logica.productos_por_caducar(idsucursal, 7),
        "sobreinventario": logica.sobreinventario(idsucursal),
        "entregas": logica.entregas_pendientes(idsucursal),
        "merma_semanal": logica.merma_por_semana(idsucursal, 8),
        "merma_causa": logica.merma_por_causa(idsucursal, 30),
    }


@app.get("/api/caducidad/{idsucursal}", tags=["Inventario"])
def caducidad(idsucursal: int, dias: int = 7):
    return logica.productos_por_caducar(idsucursal, dias)


@app.get("/api/sobreinventario/{idsucursal}", tags=["Inventario"])
def sobre(idsucursal: int):
    return logica.sobreinventario(idsucursal)


@app.get("/api/transferencias", tags=["Inventario"])
def transferencias():
    return logica.transferencias_sugeridas()


@app.post("/api/promociones", tags=["Inventario"])
def crear_promocion(p: PromocionEntrada):
    try:
        return {"idpromocion": logica.aplicar_promocion(**p.model_dump())}
    except ValueError as e:
        _error(e)


# =====================================================================
# Pedidos y proveedores
# =====================================================================
@app.get("/api/pedidos/{idsucursal}", tags=["Pedidos"])
def pedidos(idsucursal: int):
    return logica.entregas_pendientes(idsucursal)


@app.get("/api/pedidos/{idsucursal}/sugeridos", tags=["Pedidos"])
def pedidos_sugeridos(idsucursal: int):
    return logica.sugerir_pedidos(idsucursal)


@app.post("/api/pedidos", tags=["Pedidos"])
def crear_pedido(p: PedidoEntrada):
    """Crea un pedido. La fecha prometida se calcula con los días que promete el proveedor."""
    prov = db.consultar("SELECT dias_entrega_prometidos FROM proveedor WHERE idproveedor = ?", (p.idproveedor,))
    if not prov:
        _error(ValueError("Proveedor no encontrado"), 404)
    idpedido = db.ejecutar("""
        INSERT INTO pedido (idproveedor, idsucursal, idtrabajador, fecha_prometida, estado)
        OUTPUT INSERTED.idpedido
        VALUES (?, ?, ?, DATEADD(DAY, ?, SYSDATETIME()), 'pendiente')
    """, (p.idproveedor, p.idsucursal, p.idtrabajador, prov[0]["dias_entrega_prometidos"]))
    for d in p.productos:
        db.ejecutar("""
            INSERT INTO detalle_pedido (idpedido, idproducto, cantidad_pedida, costo_unitario)
            SELECT ?, idproducto, ?, costo FROM producto WHERE idproducto = ?
        """, (idpedido, d.cantidad, d.idproducto))
    return {"idpedido": idpedido}


@app.post("/api/pedidos/{idpedido}/llegada", tags=["Pedidos"])
def marcar_llegada(idpedido: int, datos: LlegadaEntrada | None = None):
    """El operador marca que llegó el pedido. Crea los lotes y registra lo que llegó dañado como merma."""
    recibidos = {d.iddetalle_pedido: d.model_dump() for d in (datos.detalles if datos else [])}
    try:
        return logica.registrar_llegada(idpedido, recibidos)
    except ValueError as e:
        _error(e)


@app.get("/api/proveedores/retraso", tags=["Pedidos"])
def proveedores_retraso():
    return logica.retraso_proveedores()


# =====================================================================
# Mermas
# =====================================================================
@app.get("/api/mermas/{idsucursal}", tags=["Mermas"])
def mermas(idsucursal: int, dias: int = 30):
    return {
        "por_causa": logica.merma_por_causa(idsucursal, dias),
        "por_producto": logica.merma_por_producto(idsucursal, dias),
        "por_semana": logica.merma_por_semana(idsucursal, 8),
    }


@app.post("/api/mermas", tags=["Mermas"])
def crear_merma(m: MermaEntrada):
    try:
        return {"idmerma": logica.registrar_merma(**m.model_dump())}
    except ValueError as e:
        _error(e)


# =====================================================================
# IA: chat y reportes
# =====================================================================
@app.post("/api/chat", tags=["IA"])
def chat(entrada: ChatEntrada):
    """Pregúntale lo que sea al asistente. Manda el id_sesion que te regresó para continuar la conversación."""
    try:
        return ia.chatear(entrada.mensaje, entrada.id_sesion, entrada.idsucursal, entrada.nombre_usuario)
    except ia.ErrorIA as e:
        _error(e, 503)


@app.delete("/api/chat/{id_sesion}", tags=["IA"])
def chat_reiniciar(id_sesion: str):
    ia.reiniciar_chat(id_sesion)
    return {"ok": True}


@app.post("/api/reportes/generar", tags=["IA"])
def reporte_generar(entrada: ReporteEntrada):
    """Genera el reporte diario con Gemini y lo guarda como borrador."""
    try:
        return ia.generar_reporte(entrada.idsucursal, entrada.idtrabajador)
    except ia.ErrorIA as e:
        _error(e, 503)


@app.post("/api/reportes/{idreporte}/enviar", tags=["IA"])
def reporte_enviar(idreporte: int):
    db.ejecutar("UPDATE reporte SET estado = 'enviado', fecha = SYSDATETIME() WHERE idreporte = ? AND estado = 'borrador'",
                (idreporte,))
    return {"idreporte": idreporte, "estado": "enviado"}


@app.post("/api/reportes/{idreporte}/revisar", tags=["IA"])
def reporte_revisar(idreporte: int, r: RevisionEntrada):
    """El gerente marca el reporte como revisado y deja un comentario."""
    db.ejecutar("""
        UPDATE reporte SET estado = 'revisado', idgerente = ?, fecha_revision = ?, comentario_gerente = ?
        WHERE idreporte = ?
    """, (r.idgerente, datetime.now(), r.comentario, idreporte))
    return {"idreporte": idreporte, "estado": "revisado"}


@app.get("/api/reportes", tags=["IA"])
def reportes(idsucursal: int | None = None, estado: str | None = None):
    """Lista de reportes (para la vista del gerente)."""
    sql = """
        SELECT r.idreporte, r.titulo, r.contenido, r.estado, r.fecha, s.nombre AS sucursal,
               t.nombre + ' ' + t.apellido AS autor, r.comentario_gerente
        FROM reporte r
        JOIN sucursal s   ON s.idsucursal   = r.idsucursal
        JOIN trabajador t ON t.idtrabajador = r.idtrabajador
        WHERE 1 = 1
    """
    params: list = []
    if idsucursal is not None:
        sql += " AND r.idsucursal = ?"
        params.append(idsucursal)
    if estado:
        sql += " AND r.estado = ?"
        params.append(estado)
    return db.consultar(sql + " ORDER BY r.fecha DESC", tuple(params))


# =====================================================================
# Frontend: si existe la carpeta ../frontend se sirve en http://localhost:8000/app/
# =====================================================================
FRONTEND = Path(__file__).resolve().parent.parent / "frontend"
if FRONTEND.is_dir():
    app.mount("/app", StaticFiles(directory=FRONTEND, html=True), name="frontend")

    @app.get("/", include_in_schema=False)
    def raiz():
        return RedirectResponse("/app/login.html")
