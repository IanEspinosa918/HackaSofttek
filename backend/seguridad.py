"""
seguridad.py - Hash de contraseñas con PBKDF2 (viene incluido en Python, no hay que instalar nada).

Formato guardado en trabajador.contrasena_hash:
    pbkdf2_sha256$<iteraciones>$<sal>$<hash>
"""
import hashlib
import hmac
import secrets

ITERACIONES = 200_000


def hash_contrasena(contrasena: str) -> str:
    sal = secrets.token_hex(16)
    h = hashlib.pbkdf2_hmac("sha256", contrasena.encode(), sal.encode(), ITERACIONES).hex()
    return f"pbkdf2_sha256${ITERACIONES}${sal}${h}"


def verificar_contrasena(contrasena: str, guardado: str | None) -> bool:
    if not guardado:
        return False
    try:
        _, iteraciones, sal, h = guardado.split("$")
    except ValueError:
        return False
    calculado = hashlib.pbkdf2_hmac("sha256", contrasena.encode(), sal.encode(), int(iteraciones)).hex()
    return hmac.compare_digest(calculado, h)


if __name__ == "__main__":
    # Uso: python seguridad.py MiContraseña   -> imprime el hash para meterlo a la BD
    import sys
    print(hash_contrasena(sys.argv[1] if len(sys.argv) > 1 else "1234"))
