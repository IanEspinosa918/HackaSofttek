"""
asignar_contrasenas.py - Pone una contraseña real a los usuarios de prueba.

Los datos de prueba traen hashes de ejemplo ("hash_demo_...") con los que no se puede iniciar sesión.
Este script:
  1. Crea un usuario (inicial del nombre + apellido, ej. cramirez) a los operadores y gerentes que no tienen.
  2. Reemplaza el hash de todos los trabajadores con usuario por el de una contraseña.
  3. Imprime la lista de usuarios para entrar.

Uso:
    python asignar_contrasenas.py              -> todos con la contraseña "Demo2026"
    python asignar_contrasenas.py MiClave123   -> todos con "MiClave123"
    python asignar_contrasenas.py MiClave123 cramirez   -> solo a ese usuario
"""
import sys
import unicodedata

import db
from seguridad import hash_contrasena

contrasena = sys.argv[1] if len(sys.argv) > 1 else "Demo2026"
solo_usuario = sys.argv[2] if len(sys.argv) > 2 else None

def _limpio(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto or "").encode("ascii", "ignore").decode()
    return "".join(c for c in texto.lower() if c.isalnum())


# 1) Operadores y gerentes activos sin usuario -> se les crea uno
sin_usuario = db.consultar("""
    SELECT t.idtrabajador, t.nombre, t.apellido
    FROM trabajador t
    JOIN puesto p ON p.idpuesto = t.idpuesto
    WHERE t.usuario IS NULL AND t.activo = 1 AND p.rol_sistema IN ('operador', 'gerente')
    ORDER BY t.idtrabajador
""")
if sin_usuario and not solo_usuario:
    usados = {r["usuario"] for r in db.consultar("SELECT usuario FROM trabajador WHERE usuario IS NOT NULL")}
    for t in sin_usuario:
        apellido = _limpio((t["apellido"] or "").split(" ")[0])
        base = (_limpio(t["nombre"])[:1] + apellido)[:36] or f"usuario{t['idtrabajador']}"
        nuevo, n = base, 2
        while nuevo in usados:
            nuevo, n = f"{base}{n}", n + 1
        usados.add(nuevo)
        db.ejecutar("UPDATE trabajador SET usuario = ? WHERE idtrabajador = ?", (nuevo, t["idtrabajador"]))
    print(f"Se crearon {len(sin_usuario)} usuario(s) nuevos.\n")

# 2) Asignar la contraseña
sql = """
    SELECT t.idtrabajador, t.usuario, t.nombre, t.apellido, RTRIM(s.nombre) AS sucursal, p.rol_sistema
    FROM trabajador t
    JOIN puesto p   ON p.idpuesto   = t.idpuesto
    JOIN sucursal s ON s.idsucursal = t.idsucursal
    WHERE t.usuario IS NOT NULL AND t.activo = 1 AND p.rol_sistema IN ('operador', 'gerente')
"""
params: tuple = ()
if solo_usuario:
    sql += " AND t.usuario = ?"
    params = (solo_usuario,)

usuarios = db.consultar(sql + " ORDER BY t.idtrabajador", params)
if not usuarios:
    print("No se encontraron trabajadores activos con puesto de operador o gerente.")
    print("Revisa que la tabla trabajador tenga datos y que su puesto tenga rol_sistema 'operador' o 'gerente'.")
    sys.exit(1)

for u in usuarios:
    db.ejecutar("UPDATE trabajador SET contrasena_hash = ? WHERE idtrabajador = ?",
                (hash_contrasena(contrasena), u["idtrabajador"]))

print(f"Contraseña '{contrasena}' asignada a {len(usuarios)} usuario(s):\n")
print(f"{'USUARIO':<12} {'ROL':<9} {'NOMBRE':<22} SUCURSAL")
for u in usuarios:
    print(f"{u['usuario']:<12} {u['rol_sistema']:<9} {u['nombre'] + ' ' + u['apellido']:<22} {u['sucursal']}")
