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

## Documento Ejecutivo

1 Problemática Operativa en el Comercio Minorista

En la gestión tradicional de tiendas y cadenas comerciales, los administradores y operadores suelen lidiar con los siguientes puntos críticos

    Pérdida por Caducidad y Mermas: La falta de visibilidad en tiempo real sobre las fechas de expiración de los productos genera acumulación de inventario vencido que no puede comercializarse, impactando directamente en el margen de ganancia

    Sobreinventario y Capital Inmovilizado: Compras excesivas de productos de bajo desplazamiento atan capital de trabajo que podría utilizarse de manera más eficiente en mercancía con alta rotación

    Cálculos de Reabastecimiento Ineficientes: Determinar qué pedir, a qué proveedor y en qué cantidades exactas suele basarse en estimaciones empíricas o cálculos manuales propensos a errores humanos, lo que provoca quiebres de stock

    Aislamiento Logístico entre Sucursales: La dificultad para identificar desequilibrios de inventario (mientras una sucursal tiene exceso de stock de un artículo y otra padece desabastecimiento) retrasa las transferencias internas óptimas

    Burocracia y Lentitud en la Generación de Reportes: Los gerentes pierden horas valiosas consolidando métricas operativas y redactando reportes diarios en lugar de tomar decisiones estratégicas basadas en datos consolidados

2 La Solución: Arquitectura y Capacidades de Tienda Inteligente

El proyecto Tienda Inteligente resuelve estas problemáticas integrando lógica de negocio especializada en la cadena de suministro con capacidades cognitivas de inteligencia artificial

2.1 Componentes del Sistema Backend

    db py (Capa de Datos): Gestiona la conexión segura con SQL Server, implementando políticas de acceso diferenciadas (cuentas transaccionales para operaciones del backend y perfiles de solo lectura dedicados para las consultas de la IA, precautelando la integridad de los datos)

    seguridad py (Control de Acceso): Provee mecanismos de hash y verificación de credenciales para garantizar un acceso seguro al sistema y la gestión de operadores y gerentes

    logica py (Motor de Negocio y Algoritmos): Automatiza los cálculos críticos de la operación minorista: control y alertas de caducidad de productos, determinación de políticas de descuentos dinámicos, detección de sobreinventario, generación automatizada de pedidos sugeridos basados en histórico y rotación, sugerencia y coordinación de transferencias de inventario entre sucursales, y gestión y registro de mermas

    ia py (Inteligencia Artificial con Gemini): Conecta el ecosistema de la tienda con Google Gemini mediante function calling, permitiendo respaldar consultas de texto a SQL de forma controlada y automatizar la redacción y síntesis de reportes gerenciales

    main py (API REST - FastAPI): Expone endpoints de alto rendimiento para la integración con interfaces frontend (como el panel de control o aplicaciones web) y terminales de prueba
