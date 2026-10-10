"""
probar_ia.py - Chatea con el asistente desde la terminal, sin frontend ni FastAPI.
Sirve para comprobar que Gemini y la base de datos funcionan juntos.

Uso:
    python probar_ia.py              -> chat (sucursal 1 por defecto)
    python probar_ia.py 2            -> chat como operador de la sucursal 2
    python probar_ia.py reporte 1    -> genera un reporte de la sucursal 1 (sin guardarlo)
"""
import sys

import ia


def modo_chat(idsucursal: int):
    print(f"Asistente de inventario (sucursal {idsucursal}). Escribe 'salir' para terminar.\n")
    id_sesion = None
    while True:
        try:
            mensaje = input("Tú: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if mensaje.lower() in ("salir", "exit", "q"):
            break
        if not mensaje:
            continue
        try:
            r = ia.chatear(mensaje, id_sesion, idsucursal)
        except ia.ErrorIA as e:
            print(f"[Error] {e}\n")
            continue
        id_sesion = r["id_sesion"]
        if r["herramientas_usadas"]:
            print(f"  (consultó: {', '.join(r['herramientas_usadas'])})")
        if r.get("modelo") and r["modelo"] != ia.MODELO:
            print(f"  (usando modelo de respaldo: {r['modelo']})")
        print(f"IA: {r['respuesta']}\n")


def modo_reporte(idsucursal: int):
    print("Generando reporte...\n")
    r = ia.generar_reporte(idsucursal, idtrabajador=1, guardar=False)
    print(r["titulo"])
    print("=" * len(r["titulo"]))
    print(r["contenido"])


if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "reporte":
        modo_reporte(int(args[1]) if len(args) > 1 else 1)
    else:
        modo_chat(int(args[0]) if args else 1)
