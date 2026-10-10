# Backend - Tienda Inteligente

API en Python (FastAPI) que conecta SQL Server con Gemini.

## Archivos

| Archivo | Qué hace |
|---|---|
| `db.py` | Conexión a SQL Server (backend y solo lectura para la IA) |
| `seguridad.py` | Hash y verificación de contraseñas |
| `logica.py` | Cálculos: caducidad, descuentos, sobreinventario, pedido sugerido, transferencias, mermas |
| `ia.py` | Gemini: chat con function calling, respaldo de texto a SQL y reportes |
| `main.py` | Endpoints de la API |
| `probar_ia.py` | Chat con la IA desde la terminal, para pruebas |

## Instalación (una sola vez)

1. Instalar **ODBC Driver 18 for SQL Server** (si no lo tienen).
2. En esta carpeta:
   ```
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Copiar `.env.example` como `.env` y poner la `GEMINI_API_KEY` (https://aistudio.google.com/apikey).
   Revisar `DB_SERVER` (por defecto `localhost\SQLEXPRESS`).
4. (Opcional, recomendado) Ejecutar `database/02_usuarios.sql` y poner esos usuarios en el `.env`.

## Uso

```
venv\Scripts\activate
uvicorn main:app --reload
```

- Probar todos los endpoints: http://localhost:8000/docs
- Verificar conexión: http://localhost:8000/api/salud
- Chat por terminal: `python probar_ia.py` o `python probar_ia.py 2` (sucursal 2)
- Reporte por terminal: `python probar_ia.py reporte 1`

## Crear un usuario para el login

```
python seguridad.py MiContraseña
```
Copia el hash que imprime y guárdalo en `trabajador.contrasena_hash`.

## Endpoints principales

| Método | Ruta | Para qué |
|---|---|---|
| POST | `/api/login` | Login (regresa los códigos que espera login.html) |
| GET | `/api/dashboard/{idsucursal}` | Todo lo del dashboard en una llamada |
| GET | `/api/pedidos/{idsucursal}/sugeridos` | Qué pedir y cuánto |
| POST | `/api/pedidos/{id}/llegada` | El operador marca que llegó un pedido |
| GET | `/api/transferencias` | Mover producto entre sucursales |
| POST | `/api/chat` | Preguntarle a la IA |
| POST | `/api/reportes/generar` | Reporte diario con IA (se guarda como borrador) |
| POST | `/api/reportes/{id}/enviar` | Enviar al gerente |
| GET | `/api/reportes` | Reportes recibidos (vista del gerente) |

Si existe la carpeta `../frontend`, el frontend se sirve en http://localhost:8000/app/
