DOCUMENTACION TECNICA DEL SISTEMA: TIENDA INTELIGENTE

    INFORMACION GENERAL Y TECNOLOGIAS

    Repositorio de GitHub: https://github.com/tu-usuario/HackaSofttek

    Entorno de Desarrollo: Visual Studio Code (VS Code)

    Gestor de Base de Datos: Microsoft SQL Server, base Hakaton_JR (esquema v3, con perfil de solo lectura para la IA)

    APIs e Integraciones:

        Google Gemini API: https://aistudio.google.com/apikey (Utilizada para chat conversacional con function calling, traduccion de lenguaje natural a SQL, generacion automatizada de reportes y creacion de PDFs)

        FastAPI (API REST principal): Se ejecuta localmente en http://localhost:8000 (con documentacion interactiva en /docs)

        ReportLab: Generacion de los reportes en PDF con graficas

    PROBLEMATICA OPERATIVA EN EL COMERCIO MINORISTA

En la gestion tradicional de tiendas y cadenas comerciales, los administradores y operadores suelen lidiar con los siguientes puntos criticos:

    Perdida por Caducidad y Mermas: La falta de visibilidad en tiempo real sobre las fechas de expiracion de los productos genera acumulacion de inventario vencido que no puede comercializarse, impactando directamente en el margen de ganancia

    Sobreinventario y Capital Inmovilizado: Compras excesivas de productos de bajo desplazamiento atan capital de trabajo que podria utilizarse de manera mas eficiente en mercancia con alta rotacion

    Calculos de Reabastecimiento Ineficientes: Determinar que pedir, a que proveedor y en que cantidades exactas suele basarse en estimaciones empiricas o calculos manuales propensos a errores humanos, lo que provoca quiebres de stock

    Aislamiento Logistico entre Sucursales: La dificultad para identificar desequilibrios de inventario (mientras una sucursal tiene exceso de stock de un articulo y otra padece desabastecimiento) retrasa las transferencias internas optimas

    Burocracia y Lentitud en la Generacion de Reportes: Los gerentes pierden horas valiosas consolidando metricas operativas y redactando reportes diarios en lugar de tomar decisiones estrategicas basadas en datos consolidados

    LA SOLUCION: ARQUITECTURA Y COMPONENTES DEL SISTEMA

El proyecto Tienda Inteligente resuelve estas problematicas integrando logica de negocio especializada en la cadena de suministro con capacidades cognitivas de inteligencia artificial.

Flujo general: SQL Server -> Backend en Python (FastAPI, toda la logica de negocio) -> Gemini (redaccion de reportes, preguntas libres y PDFs) -> Paginas web (login, dashboard y asistente).

3.1. Estructura de Archivos del Backend

    db.py: Conexion a SQL Server (backend y solo lectura para la IA)

    seguridad.py: Hash y verificacion de contrasenas

    logica.py: Calculos: caducidad, descuentos, sobreinventario, stock actual, pedido sugerido, transferencias, retraso de proveedores, mermas y quiebres

    ia.py: Gemini: chat con function calling, respaldo de texto a SQL, reportes, consultas predefinidas del asistente y creacion de PDFs

    main.py: Endpoints de la API

    pdf_reporte.py: Arma los PDF (encabezado, indicadores, texto de la IA) con el aspecto visual elegido

    graficas_pdf.py: Dibuja las graficas que van dentro de los PDF

    cargar_historial.py: Genera 60 dias de datos de prueba para todas las sucursales a partir de los datos reales

    asignar_contrasenas.py: Asigna contrasenas a los trabajadores para poder entrar al sistema

    probar_ia.py: Chat con la IA desde la terminal, para pruebas

    requirements.txt: Dependencias (fastapi, uvicorn, pyodbc, python-dotenv, google-genai, reportlab)

    .env.example: Plantilla de configuracion (se copia como .env, que NUNCA se sube a Git)

3.2. Archivos del Frontend (en la raiz del proyecto)

    login.html: Inicio de sesion conectado a /api/login

    dashboard.html: Tablero del operador con 3 secciones: Inventario y mermas, Pedidos y entregas, Reportes

    asistente.html: Asistente con 4 botones predefinidos y chat libre con la IA

    tema.css y tema.js: Modo oscuro, aspectos visuales y panel de "Configuracion visual"

3.3. Base de Datos (carpeta database)

    01_esquema.sql: Esquema v3 (tablas, vistas como vw_fecha_referencia, inventario_diario, codigos de sucursal, proveedor y producto)

    02_usuarios.sql: Usuario ia_lectura de solo lectura para la IA (sin acceso a contrasenas)

    Hakaton_JR_datos_prueba.sql: Datos de prueba basicos

    EXPLICACION DETALLADA DEL CODIGO POR MODULO

db.py - Capa de Conexion a Base de Datos
Establece la comunicacion con la instancia de Microsoft SQL Server utilizando el driver ODBC 18. Gestiona perfiles de conexion diferenciados: por un lado maneja conexiones con privilegios transaccionales para las operaciones del backend (escritura, actualizaciones de inventario y registro de pedidos) y por otro lado provee conexiones aisladas de solo lectura destinadas exclusivamente a las consultas generadas por la Inteligencia Artificial, resguardando la integridad y seguridad de la base de datos corporativa.

seguridad.py - Control de Acceso y Credenciales
Provee funciones criptograficas para el manejo seguro de credenciales de operadores y gerentes. Implementa hash PBKDF2-SHA256 con sal y verificacion de contrasenas. Permite generar los hashes correspondientes desde la terminal (ejecutando python seguridad.py MiContrasena) para almacenarlos de manera segura en el campo trabajador.contrasena_hash de la base de datos.

logica.py - Motor de Negocio y Algoritmos Operativos
Concentra la logica matematica y las reglas operativas del comercio minorista. Todos los calculos usan como "hoy" la fecha de referencia de la base de datos (vista vw_fecha_referencia = fecha de la ultima venta registrada, 2026-09-30 en los datos actuales), para que la demo siempre muestre datos coherentes. Contiene:

    Productos por caducar con descuento escalonado (50/30/15/10 % segun dias restantes, +10 % si no se alcanza a vender, maximo 60 %)

    Sobreinventario y stock actual por producto (agotado, bajo, exceso u ok, con dias de cobertura)

    Pedido sugerido por punto de reorden, respetando multiplos de caja y lo que ya viene en camino

    Transferencias sugeridas entre sucursales

    Retraso de proveedores comparando puntualidad y surtido reales contra lo que dice su contrato

    Mermas por causa, por producto, por semana y comparativo entre sucursales, y relacion entre merma y quiebres de stock

    Acciones: registrar llegada de pedidos, registrar mermas y aplicar promociones

ia.py - Integracion con Google Gemini
Actua como el puente cognitivo entre el sistema de la tienda y el modelo de lenguaje de Google Gemini. Configura la GEMINI_API_KEY e implementa function calling. Permite que la IA interprete preguntas formuladas por los usuarios en lenguaje natural, las traduzca de forma segura a consultas o llamadas del sistema, y redacte o sintetice reportes gerenciales listos para su revision. Detalles:

    Modelo principal gemini-flash-latest y de respaldo gemini-flash-lite-latest; si Gemini esta saturado (error 503 o 429) reintenta y cambia al modelo de respaldo automaticamente

    Las herramientas de la IA son de solo lectura. La consulta SQL libre solo acepta SELECT/WITH, bloquea palabras peligrosas, no permite ";" ni leer contrasenas y regresa maximo 200 filas

    Consultas predefinidas del asistente (reporte diario, que descuentos aplicar, que y cuanto pedir, stock actual) con cache de 10 minutos

    La IA puede crear PDFs desde el chat (herramientas generar_reporte_pdf y crear_pdf); el archivo queda disponible 2 horas para descargarlo

    La respuesta del chat indica que herramientas consulto la IA y los archivos que genero

main.py - Exposicion de Endpoints (FastAPI)
Inicializa la aplicacion web mediante FastAPI, exponiendo la interfaz REST del sistema. La lista completa se puede probar en http://localhost:8000/docs. Rutas principales:

    General:
        GET /api/salud: Estado del sistema, conexion a la base y fecha de referencia
        POST /api/login: Autenticacion de trabajadores (responde USUARIO_NO_ENCONTRADO, CONTRASENA_INCORRECTA o SIN_ACCESO)
        GET /api/sucursales: Lista de sucursales

    Inventario y mermas:
        GET /api/dashboard/{idsucursal}: Indicadores del tablero
        GET /api/caducidad/{idsucursal}, /api/sobreinventario/{idsucursal}, /api/stock/{idsucursal}
        GET /api/transferencias: Movimientos de stock sugeridos entre sucursales
        POST /api/promociones: Aplicar descuento a un lote
        GET /api/mermas/{idsucursal}, /api/mermas/{idsucursal}/quiebres, /api/comparativo/mermas, /api/causas-merma
        POST /api/mermas: Registrar una merma

    Pedidos y entregas:
        GET /api/pedidos/{idsucursal}: Entregas pendientes
        GET /api/pedidos/{idsucursal}/sugeridos: Calculo automatizado de reabastecimiento
        GET /api/pedidos/{idsucursal}/historial y GET /api/pedido/{idpedido}: Historial y detalle
        POST /api/pedidos: Crear pedido
        POST /api/pedidos/{id}/llegada: Registro de recepcion de mercancia
        GET /api/proveedores/retraso: Desempeno de proveedores contra contrato

    Inteligencia Artificial:
        GET /api/asistente/opciones y POST /api/asistente/{tipo}: Botones predefinidos del asistente
        POST /api/chat y DELETE /api/chat/{id_sesion}: Chat libre con la IA
        POST /api/reportes/generar: Generacion de reportes diarios en modo borrador asistidos por IA
        POST /api/reportes/{id}/enviar: Envio formal de reportes al gerente
        POST /api/reportes/{id}/revisar: El gerente marca el reporte como revisado y deja un comentario
        GET /api/reportes: Visualizacion de reportes recibidos

    PDF (todos aceptan ?tema=oscuro|claro|esmeralda|oceano):
        GET /api/reportes/{id}/pdf: Descarga un reporte guardado como PDF con graficas
        POST /api/pdf: Convierte cualquier texto (por ejemplo, una respuesta del asistente) en PDF
        GET /api/archivos/{token}: Descarga un PDF que la IA creo desde el chat

pdf_reporte.py y graficas_pdf.py - Reportes en PDF
Generan PDFs con encabezado, tarjetas de indicadores, una seccion "Panorama en graficas" y el analisis de la IA. Las graficas cambian segun el tipo de reporte: el reporte diario lleva merma por semana, merma por causa, valor en riesgo por producto y comparativo entre sucursales; descuentos, pedidos y stock llevan sus propias graficas. El PDF usa el mismo aspecto visual que el usuario tenga elegido en la pagina.

cargar_historial.py - Datos de Prueba para Todas las Sucursales
Genera 60 dias de operacion (2026-08-02 a 2026-09-30) para todas las sucursales a partir de los productos, proveedores y sucursales reales, para que todas las graficas tengan datos. Borra y vuelve a llenar las tablas operativas (venta, detalle_venta, pedido, detalle_pedido, lote, merma, inventario_diario, promocion, transferencia); no toca sucursales, productos, proveedores ni trabajadores. Incluye casos para la demo (sucursales que piden de mas, una que pide de menos y un proveedor que llega tarde).

    python cargar_historial.py               (pide confirmacion)
    python cargar_historial.py --si          (sin confirmacion)
    python cargar_historial.py --sin-reasignar   (no cambia el proveedor de los productos)

asignar_contrasenas.py - Contrasenas de Prueba
    python asignar_contrasenas.py                     (todos los trabajadores con la contrasena Demo2026)
    python asignar_contrasenas.py MiClave cramirez    (solo a un usuario)

probar_ia.py - Herramienta de Pruebas en Terminal
Es un script de utilidad para desarrolladores y operadores que permite interactuar directamente con las capacidades de la IA desde la linea de comandos de la terminal en VS Code. Permite iniciar sesiones de chat de prueba especificando opcionalmente el identificador de la sucursal (python probar_ia.py 2) o generar un reporte sin guardarlo (python probar_ia.py reporte 2).

    FRONTEND (PAGINAS WEB)

login.html
Inicio de sesion con mensajes de "usuario no encontrado" y "contrasena incorrecta". Guarda la sesion en el navegador.

dashboard.html
Tablero del operador con selector de sucursal y 3 secciones, todas con datos de la base:

    Inventario y mermas: indicadores, productos por caducar con boton "Aplicar descuento", sobreinventario, stock actual y, al fondo, mermas (por semana, por causa y comparativo entre sucursales)

    Pedidos y entregas: entregas pendientes con registro de llegada, pedido sugerido con boton "Crear pedido", historial y retraso de proveedores

    Reportes: generar el reporte diario con IA, enviarlo al gerente, revisarlo y descargarlo en PDF

asistente.html
Cuatro botones predefinidos (Generar reporte diario, Que descuentos aplicar, Que y cuanto pedir, Stock actual) con opcion de regenerar y descargar en PDF, mas un chat libre con la IA. En el chat se le puede pedir un PDF (por ejemplo "Hazme el reporte diario en PDF") y aparece un boton para descargarlo.

    ESTETICA Y CONFIGURACION VISUAL

    Modo oscuro por defecto. Las tarjetas que contienen graficas o texto tienen un borde con gradiente

    Panel "Configuracion visual" abajo a la izquierda (en el login aparece flotando en la misma esquina) con 4 aspectos: Oscuro, Claro, Esmeralda y Oceano. La eleccion se guarda en el navegador (localStorage, clave ti_tema) y aplica en todas las paginas

    Las barras de las graficas son gradientes con un color que contrasta con el aspecto, y cambian de color segun la cantidad: baja, media o alta respecto al valor mas grande de la grafica. Cada grafica lleva su leyenda Bajo / Medio / Alto, y la semana actual y la sucursal propia van remarcadas

    Los PDF se generan con el mismo aspecto elegido (la pagina manda el parametro ?tema= al backend)

    Para agregar un aspecto nuevo: definir sus colores en tema.css (html[data-tema="..."]), agregarlo a la lista TEMAS de tema.js y a PALETAS en pdf_reporte.py

    INSTALACION Y EJECUCION

1. Base de datos: ejecutar database/01_esquema.sql, cargar los datos y (opcional) database/02_usuarios.sql. Para llenar todas las sucursales: python cargar_historial.py

2. Backend (dentro de la carpeta backend):

    python -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt
    copy .env.example .env      (llenar GEMINI_API_KEY y DB_SERVER, por ejemplo PCIAN\MSSQLSERVER01)
    python asignar_contrasenas.py
    uvicorn main:app --reload

   Si PowerShell bloquea el venv: Set-ExecutionPolicy -Scope CurrentUser RemoteSigned

3. Comprobar: abrir http://localhost:8000/api/salud (debe decir base de datos "conectada")

4. Abrir login.html en el navegador y entrar con un usuario (por ejemplo cramirez / Demo2026). Despues de actualizar archivos recargar con Ctrl+F5

    SEGURIDAD

    La API key de Gemini va solo en backend/.env, que esta en .gitignore. Nunca usar git add -f .env ni compartir la llave; si se expone, se debe rotar en AI Studio

    Contrasenas guardadas con hash PBKDF2, nunca en texto plano

    La IA solo tiene herramientas de lectura; el filtro de SQL y el usuario ia_lectura (con DENY sobre las columnas de contrasena) evitan que modifique datos o lea credenciales

    REGISTRO DE ACTUALIZACIONES

    Backend adaptado a la base de datos v3 (dataset Glazed Co., fecha de referencia 2026-09-30, inventario_diario, contratos de proveedor)

    Reintentos y modelo de respaldo para los errores 503 de Gemini; ejecucion manual de llamadas a funciones que el SDK dejaba sin responder

    Asistente con 4 botones predefinidos y chat libre

    Dashboard rehecho en 3 secciones (Inventario y mermas, Pedidos y entregas, Reportes) con datos reales de la base

    Reportes en PDF descargables, tambien creados por la IA desde el chat

    Graficas dentro de los PDF

    Script cargar_historial.py con datos de 60 dias para todas las sucursales

    Modo oscuro, panel de Configuracion visual con 4 aspectos, graficas con gradiente y color por cantidad, y PDFs con el mismo aspecto
