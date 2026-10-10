"""
asignar_contrasenas.py - Pone una contraseña real a los usuarios de prueba.

Los datos de prueba traen hashes de ejemplo ("hash_demo_...") con los que no se puede iniciar sesión.
Este script reemplaza el hash de todos los trabajadores que tienen usuario por el de una contraseña.

Uso:
    python asignar_contrasenas.py              -> todos con la contraseña "Demo2026"
    python asignar_contrasenas.py MiClave123   -> todos con "MiClave123"
    python asignar_contrasenas.py MiClave123 cramirez   -> solo a ese usuario
"""
import sys

import db
from seguridad import hash_contrasena

contrasena = sys.argv[1] if len(sys.argv) > 1 else "Demo2026"
solo_usuario = sys.argv[2] if len(sys.argv) > 2 else None

sql = """
    SELECT t.idtrabajador, t.usuario, t.nombre, t.apellido, RTRIM(s.nombre) AS sucursal, p.rol_sistema
    FROM trabajador t
    JOIN puesto p   ON p.idpuesto   = t.idpuesto
    JOIN sucursal s ON s.idsucursal = t.idsucursal
    WHERE t.usuario IS NOT NULL
"""
params: tuple = ()
if solo_usuario:
    sql += " AND t.usuario = ?"
    params = (solo_usuario,)

usuarios = db.consultar(sql + " ORDER BY t.idtrabajador", params)
if not usuarios:
    print("No se encontraron usuarios.")
    sys.exit(1)

for u in usuarios:
    db.ejecutar("UPDATE trabajador SET contrasena_hash = ? WHERE idtrabajador = ?",
                (hash_contrasena(contrasena), u["idtrabajador"]))

print(f"Contraseña '{contrasena}' asignada a {len(usuarios)} usuario(s):\n")
print(f"{'USUARIO':<12} {'ROL':<9} {'NOMBRE':<22} SUCURSAL")
for u in usuarios:
    print(f"{u['usuario']:<12} {u['rol_sistema']:<9} {u['nombre'] + ' ' + u['apellido']:<22} {u['sucursal']}")
