"""
ia.py - Todo lo relacionado con Gemini.

Tres usos, una sola API:
  1. generar_reporte()  -> Python junta los datos, Gemini redacta el reporte.
  2. chatear()          -> function calling: Gemini decide qué función de logica.py llamar.
  3. consulta_sql()     -> respaldo: Gemini escribe un SELECT que se corre con el usuario de solo lectura.
"""
import json
import os
import re
import time
import uuid
from datetime import date

from dotenv import load_dotenv
from google import genai
from google.genai import errors, types

import db
import logica

load_dotenv()

MODELO = os.getenv("GEMINI_MODEL", "gemini-flash-latest")
_client: genai.Client | None = None


def cliente() -> genai.Client:
    """Crea el cliente la primera vez que se usa (así el backend arranca aunque falte la API key)."""
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("Falta GEMINI_API_KEY en el archivo .env")
        _client = genai.Client(api_key=api_key)
    return _client


class ErrorIA(Exception):
    """Error amigable para mostrar en el frontend."""


def _manejar_error(e: Exception) -> ErrorIA:
    if isinstance(e, errors.APIError):
        if e.code == 429:
            return ErrorIA("La IA recibió demasiadas peticiones. Intenta de nuevo en unos segundos.")
        if e.code in (401, 403):
            return ErrorIA("La API key de Gemini no es válida o no tiene permisos.")
        return ErrorIA(f"Error de Gemini ({e.code}). Intenta de nuevo.")
    return ErrorIA(f"No se pudo conectar con Gemini: {e}")


# =====================================================================
# Esquema que se le explica a Gemini para el respaldo de texto a SQL
# =====================================================================
ESQUEMA_BD = """
Base de datos SQL Server "Hakaton_JR" (usa sintaxis T-SQL: TOP en lugar de LIMIT, GETDATE(), DATEADD, DATEDIFF).

sucursal(idsucursal, nombre, direccion, telefono, activa)
puesto(idpuesto, nombre, rol_sistema)                       -- rol_sistema: operador | gerente | ninguno
turno(idturno, nombre, hora_inicio, hora_fin)
trabajador(idtrabajador, nombre, apellido, idsucursal, idpuesto, idturno, activo)
categoria(idcategoria, nombre)
proveedor(idproveedor, nombre, telefono, correo, dias_entrega_prometidos)
producto(idproducto, nombre, idcategoria, idproveedor, precio_venta, costo, vida_util_dias, es_perecedero, unidad, activo)
lote(idlote, idproducto, idsucursal, iddetalle_pedido, cantidad_inicial, cantidad_actual, fecha_entrada, fecha_caducidad)
venta(idventa, idsucursal, fecha, total)
detalle_venta(iddetalle_venta, idventa, idproducto, idlote, cantidad, precio_unitario, descuento_pct)
pedido(idpedido, idproveedor, idsucursal, idtrabajador, fecha_pedido, fecha_prometida, fecha_llegada, estado, observaciones)
    -- estado: pendiente | en_camino | recibido | cancelado
detalle_pedido(iddetalle_pedido, idpedido, idproducto, cantidad_pedida, cantidad_recibida, cantidad_danada, costo_unitario)
transferencia(idtransferencia, idlote, idsucursal_origen, idsucursal_destino, cantidad, fecha, idtrabajador, estado)
causa_merma(idcausa, nombre, descripcion)                   -- Caducidad, Daño, Proveedor, Robo, Otro
merma(idmerma, idlote, idcausa, idtrabajador, cantidad, costo_total, fecha, observaciones)
promocion(idpromocion, idlote, porcentaje, fecha_inicio, fecha_fin, motivo, origen, estado, idtrabajador)
reporte(idreporte, idtrabajador, idsucursal, fecha, titulo, contenido, estado, idgerente, fecha_revision, comentario_gerente)

Vistas:
vw_inventario_actual(idsucursal, sucursal, idproducto, producto, categoria, existencia, proxima_caducidad)
vw_venta_promedio_diaria(idsucursal, idproducto, venta_promedio_diaria)      -- últimos 30 días
vw_retraso_proveedor(idproveedor, proveedor, entregas, retraso_promedio_horas, pct_entregas_tarde)
vw_productos_por_caducar(idlote, idsucursal, sucursal, idproducto, producto, cantidad_actual, fecha_caducidad, dias_para_caducar, valor_en_riesgo)
"""

PALABRAS_PROHIBIDAS = re.compile(
    r"\b(insert|update|delete|drop|alter|create|truncate|merge|exec|execute|grant|revoke|deny|"
    r"backup|restore|shutdown|openrowset|opendatasource|xp_\w+|sp_\w+|into)\b",
    re.IGNORECASE,
)


def consulta_sql(sql: str) -> list[dict]:
    """
    Ejecuta una consulta SELECT de solo lectura (T-SQL) sobre la base de datos de la tienda.
    Úsala SOLO si ninguna otra herramienta responde la pregunta.
    Regresa como máximo 200 filas.
    """
    limpio = sql.strip().rstrip(";").strip()
    if not re.match(r"^(select|with)\b", limpio, re.IGNORECASE):
        return [{"error": "Solo se permiten consultas SELECT."}]
    if ";" in limpio or PALABRAS_PROHIBIDAS.search(limpio) or "contrasena" in limpio.lower():
        return [{"error": "La consulta contiene instrucciones no permitidas."}]
    try:
        return db.consultar(limpio, lectura=True, limite=200)
    except Exception as e:  # el error regresa a Gemini para que corrija su consulta
        return [{"error": f"Error al ejecutar la consulta: {e}"}]


# =====================================================================
# Herramientas que Gemini puede usar (todas de solo lectura)
# =====================================================================
HERRAMIENTAS = [
    logica.listar_sucursales,
    logica.resumen_sucursal,
    logica.productos_por_caducar,
    logica.sobreinventario,
    logica.retraso_proveedores,
    logica.entregas_pendientes,
    logica.sugerir_pedidos,
    logica.transferencias_sugeridas,
    logica.merma_por_causa,
    logica.merma_por_producto,
    logica.merma_por_semana,
    consulta_sql,
]


def _instrucciones_chat(idsucursal: int | None, nombre_usuario: str | None) -> str:
    contexto = ""
    if idsucursal is not None:
        contexto += f"\nEl usuario trabaja en la sucursal con idsucursal = {idsucursal}. Si no menciona otra, usa esa."
    if nombre_usuario:
        contexto += f"\nEl usuario se llama {nombre_usuario}."
    return f"""Eres el asistente de inventario de "Tienda Inteligente", una cadena de tiendas con varias sucursales.
Ayudas al operador de inventario a reducir mermas: productos por caducar, descuentos, sobreinventario,
pedidos a proveedores, retrasos de entrega y transferencias entre sucursales.

Reglas:
- Responde siempre en español, breve y directo. Usa viñetas cuando haya varios elementos.
- Usa SIEMPRE las herramientas para obtener datos. Nunca inventes números, productos ni proveedores.
- Si mencionan una sucursal por nombre, usa listar_sucursales para obtener su id.
- Prefiere las herramientas específicas; usa consulta_sql solo si ninguna otra sirve.
- Expresa dinero en pesos mexicanos con formato $1,234.
- Cuando tenga sentido, termina con una acción concreta recomendada.
- Si no hay datos para responder, dilo claramente.
- La fecha de hoy es {date.today().isoformat()}.{contexto}

Esquema de la base de datos (para consulta_sql):
{ESQUEMA_BD}"""


# =====================================================================
# USO 2 y 3: Chat con function calling (+ respaldo SQL)
# =====================================================================
_SESIONES: dict[str, dict] = {}
_MAX_SESIONES = 100
_EXPIRA_SEGUNDOS = 60 * 60


def _limpiar_sesiones() -> None:
    ahora = time.time()
    for sid in [s for s, v in _SESIONES.items() if ahora - v["ultimo_uso"] > _EXPIRA_SEGUNDOS]:
        del _SESIONES[sid]
    while len(_SESIONES) > _MAX_SESIONES:
        mas_viejo = min(_SESIONES, key=lambda s: _SESIONES[s]["ultimo_uso"])
        del _SESIONES[mas_viejo]


def _nuevo_chat(idsucursal: int | None, nombre_usuario: str | None):
    return cliente().chats.create(
        model=MODELO,
        config=types.GenerateContentConfig(
            system_instruction=_instrucciones_chat(idsucursal, nombre_usuario),
            tools=HERRAMIENTAS,
            temperature=0.2,  # respuestas consistentes, poco "creativas"
            automatic_function_calling=types.AutomaticFunctionCallingConfig(maximum_remote_calls=8),
        ),
    )


def chatear(mensaje: str, id_sesion: str | None = None, idsucursal: int | None = None,
            nombre_usuario: str | None = None) -> dict:
    """
    Envía un mensaje al asistente. Si no hay id_sesion se crea una conversación nueva.
    Regresa la respuesta, el id de sesión (para seguir la conversación) y las herramientas usadas.
    """
    _limpiar_sesiones()
    if not id_sesion or id_sesion not in _SESIONES:
        id_sesion = id_sesion or uuid.uuid4().hex
        try:
            _SESIONES[id_sesion] = {"chat": _nuevo_chat(idsucursal, nombre_usuario), "ultimo_uso": time.time()}
        except Exception as e:
            raise _manejar_error(e)

    sesion = _SESIONES[id_sesion]
    sesion["ultimo_uso"] = time.time()
    try:
        respuesta = sesion["chat"].send_message(mensaje)
    except Exception as e:
        raise _manejar_error(e)

    herramientas_usadas = []
    for contenido in respuesta.automatic_function_calling_history or []:
        for parte in contenido.parts or []:
            if parte.function_call and parte.function_call.name not in herramientas_usadas:
                herramientas_usadas.append(parte.function_call.name)

    return {
        "respuesta": respuesta.text or "No pude generar una respuesta, intenta reformular la pregunta.",
        "id_sesion": id_sesion,
        "herramientas_usadas": herramientas_usadas,
    }


def reiniciar_chat(id_sesion: str) -> None:
    _SESIONES.pop(id_sesion, None)


# =====================================================================
# USO 1: Reporte diario
# =====================================================================
INSTRUCCIONES_REPORTE = """Eres analista de inventario de "Tienda Inteligente".
Redacta el reporte diario que el operador de inventario envía al gerente de su sucursal.

Formato (Markdown):
## Resumen
2 o 3 frases con lo más importante del día.
## Riesgos de merma
Viñetas con los productos más urgentes (por caducar y sobreinventario), con cantidades y valor en riesgo.
## Proveedores y entregas
Retrasos relevantes y su impacto.
## Acciones recomendadas
Lista numerada y priorizada: descuentos a aplicar, pedidos a hacer, transferencias entre sucursales.
Indica qué acciones requieren aprobación del gerente (descuentos mayores a 30% y transferencias).

Reglas:
- Usa SOLO los datos proporcionados. No inventes cifras ni productos.
- Si una sección no tiene datos, dilo en una línea.
- Dinero en pesos mexicanos con formato $1,234.
- Sé concreto: máximo ~300 palabras."""


def _datos_para_reporte(idsucursal: int) -> dict:
    sucursal = db.consultar("SELECT nombre FROM sucursal WHERE idsucursal = ?", (idsucursal,))
    transferencias = [t for t in logica.transferencias_sugeridas()
                      if idsucursal in (t["idsucursal_origen"], t["idsucursal_destino"])]
    return {
        "fecha": date.today().isoformat(),
        "sucursal": sucursal[0]["nombre"] if sucursal else str(idsucursal),
        "indicadores": logica.resumen_sucursal(idsucursal),
        "productos_por_caducar": logica.productos_por_caducar(idsucursal, 7)[:15],
        "sobreinventario": logica.sobreinventario(idsucursal)[:10],
        "entregas_pendientes": logica.entregas_pendientes(idsucursal),
        "retraso_proveedores": logica.retraso_proveedores(),
        "pedidos_sugeridos": logica.sugerir_pedidos(idsucursal)[:10],
        "transferencias_sugeridas": transferencias[:10],
        "merma_por_causa_30_dias": logica.merma_por_causa(idsucursal, 30),
    }


def generar_reporte(idsucursal: int, idtrabajador: int, guardar: bool = True) -> dict:
    """Junta los datos de la sucursal, le pide a Gemini el reporte y lo guarda como borrador."""
    datos = _datos_para_reporte(idsucursal)
    try:
        r = cliente().models.generate_content(
            model=MODELO,
            contents=f"Datos de la sucursal (JSON):\n{json.dumps(datos, ensure_ascii=False, default=str)}",
            config=types.GenerateContentConfig(system_instruction=INSTRUCCIONES_REPORTE, temperature=0.3),
        )
    except Exception as e:
        raise _manejar_error(e)

    contenido = r.text or "No se pudo generar el reporte."
    titulo = f"Reporte diario - {datos['sucursal']} - {datos['fecha']}"
    idreporte = None
    if guardar:
        idreporte = db.ejecutar("""
            INSERT INTO reporte (idtrabajador, idsucursal, titulo, contenido, estado)
            OUTPUT INSERTED.idreporte VALUES (?, ?, ?, ?, 'borrador')
        """, (idtrabajador, idsucursal, titulo, contenido))
    return {"idreporte": idreporte, "titulo": titulo, "contenido": contenido, "indicadores": datos["indicadores"]}
