"""
db.py - Conexión a SQL Server.

Dos conexiones:
  - app:     la usa el backend (lectura y escritura).
  - lectura: la usa la IA para consultas SQL libres (solo SELECT).
"""
import os
from datetime import date, datetime, time
from decimal import Decimal

import pyodbc
from dotenv import load_dotenv

load_dotenv()

DRIVER = os.getenv("DB_DRIVER", "ODBC Driver 18 for SQL Server")
SERVER = os.getenv("DB_SERVER", r"localhost\SQLEXPRESS")
DATABASE = os.getenv("DB_NAME", "Hakaton_JR")


def _cadena(usuario: str | None, contrasena: str | None) -> str:
    base = f"DRIVER={{{DRIVER}}};SERVER={SERVER};DATABASE={DATABASE};TrustServerCertificate=yes;"
    if usuario:
        return base + f"UID={usuario};PWD={contrasena};"
    # Sin usuario: autenticación de Windows
    return base + "Trusted_Connection=yes;"


def conexion_app() -> pyodbc.Connection:
    return pyodbc.connect(_cadena(os.getenv("DB_APP_USER"), os.getenv("DB_APP_PASSWORD")))


def conexion_lectura() -> pyodbc.Connection:
    usuario = os.getenv("DB_IA_USER")
    if not usuario:
        # Si aún no crean el usuario de solo lectura, se usa la del backend.
        # Las consultas igual se validan en ia.py, pero lo ideal es crear ia_lectura.
        return conexion_app()
    return pyodbc.connect(_cadena(usuario, os.getenv("DB_IA_PASSWORD")))


def _limpiar(valor):
    """Convierte tipos de SQL Server a tipos que se pueden mandar como JSON."""
    if isinstance(valor, Decimal):
        return float(valor)
    if isinstance(valor, (datetime, date, time)):
        return valor.isoformat()
    return valor


def consultar(sql: str, params: tuple = (), lectura: bool = False, limite: int | None = None) -> list[dict]:
    """Ejecuta un SELECT y regresa una lista de diccionarios."""
    con = conexion_lectura() if lectura else conexion_app()
    try:
        cur = con.cursor()
        cur.execute(sql, params)
        columnas = [c[0] for c in cur.description]
        filas = cur.fetchmany(limite) if limite else cur.fetchall()
        return [{col: _limpiar(v) for col, v in zip(columnas, fila)} for fila in filas]
    finally:
        con.close()


def ejecutar(sql: str, params: tuple = ()) -> int | None:
    """Ejecuta INSERT/UPDATE. Si el SQL tiene OUTPUT INSERTED.id, regresa ese id."""
    con = conexion_app()
    try:
        cur = con.cursor()
        cur.execute(sql, params)
        nuevo_id = None
        if cur.description:  # hubo OUTPUT
            fila = cur.fetchone()
            nuevo_id = fila[0] if fila else None
        con.commit()
        return nuevo_id
    finally:
        con.close()
