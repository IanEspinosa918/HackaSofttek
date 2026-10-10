DOCUMENTACION TECNICA DEL SISTEMA: TIENDA INTELIGENTE

    INFORMACION GENERAL Y TECNOLOGIAS

    Repositorio de GitHub: https://github.com/tu-usuario/HackaSofttek

    Entorno de Desarrollo: Visual Studio Code (VS Code)

    Gestor de Base de Datos: Microsoft SQL Server (con esquemas para backend y perfiles de solo lectura para la IA)

    APIs e Integraciones:

        Google Gemini API: https://aistudio.google.com/apikey (Utilizada para chat conversacional con function calling, traduccion de lenguaje natural a SQL y generacion automatizada de reportes)

        FastAPI (API REST principal): Se ejecuta localmente en http://localhost:8000 (con documentacion interactiva en /docs) y despliegue del frontend opcional en /app/

    PROBLEMATICA OPERATIVA EN EL COMERCIO MINORISTA

En la gestion tradicional de tiendas y cadenas comerciales, los administradores y operadores suelen lidiar con los siguientes puntos criticos:

    Perdida por Caducidad y Mermas: La falta de visibilidad en tiempo real sobre las fechas de expiracion de los productos genera acumulacion de inventario vencido que no puede comercializarse, impactando directamente en el margen de ganancia

    Sobreinventario y Capital Inmovilizado: Compras excesivas de productos de bajo desplazamiento atan capital de trabajo que podria utilizarse de manera mas eficiente en mercancia con alta rotacion

    Calculos de Reabastecimiento Ineficientes: Determinar que pedir, a que proveedor y en que cantidades exactas suele basarse en estimaciones empiricas o calculos manuales propensos a errores humanos, lo que provoca quiebres de stock

    Aislamiento Logistico entre Sucursales: La dificultad para identificar desequilibrios de inventario (mientras una sucursal tiene exceso de stock de un articulo y otra padece desabastecimiento) retrasa las transferencias internas optimas

    Burocracia y Lentitud en la Generacion de Reportes: Los gerentes pierden horas valiosas consolidando metricas operativas y redactando reportes diarios en lugar de tomar decisiones estrategicas basadas en datos consolidados

    LA SOLUCION: ARQUITECTURA Y COMPONENTES DEL SISTEMA

El proyecto Tienda Inteligente resuelve estas problematicas integrando logica de negocio especializada en la cadena de suministro con capacidades cognitivas de inteligencia artificial.

3.1. Estructura de Archivos del Backend

    db.py: Conexion a SQL Server (backend y solo lectura para la IA)

    seguridad.py: Hash y verificacion de contrasenas

    logica.py: Calculos: caducidad, descuentos, sobreinventario, pedido sugerido, transferencias, mermas

    ia.py: Gemini: chat con function calling, respaldo de texto a SQL y reportes

    main.py: Endpoints de la API

    probar_ia.py: Chat con la IA desde la terminal, para pruebas

    EXPLICACION DETALLADA DEL CODIGO POR MODULO

db.py - Capa de Conexion a Base de Datos
Establece la comunicacion con la instancia de Microsoft SQL Server utilizando el driver ODBC 18. Gestiona perfiles de conexion diferenciados: por un lado maneja conexiones con privilegios transaccionales para las operaciones del backend (escritura, actualizaciones de inventario y registro de pedidos) y por otro lado provee conexiones aisladas de solo lectura destinadas exclusivamente a las consultas generadas por la Inteligencia Artificial, resguardando la integridad y seguridad de la base de datos corporativa.

seguridad.py - Control de Acceso y Credenciales
Provee funciones criptograficas para el manejo seguro de credenciales de operadores y gerentes. Implementa algoritmos de hash y verificacion de contrasenas. Permite generar los hashes correspondientes desde la terminal (ejecutando python seguridad.py MiContrasena) para almacenarlos de manera segura en el campo trabajador.contrasena_hash de la base de datos.

logica.py - Motor de Negocio y Algoritmos Operativos
Concentra la logica matematica y las reglas operativas del comercio minorista. Contiene las rutinas automatizadas para calcular y alertar sobre la caducidad proxima de mercancias, aplicar politicas de descuentos dinamicos basados en la rotacion del producto, detectar sobreinventario para evitar la inmovilizacion de capital, calcular pedidos sugeridos precisos combinando historicos de ventas y stock actual, coordinar transferencias de inventario entre sucursales y registrar las mermas del negocio.

ia.py - Integracion con Google Gemini
Actua como el puente cognitivo entre el sistema de la tienda y el modelo de lenguaje de Google Gemini. Configura la GEMINI_API_KEY e implementa function calling. Permite que la IA interprete preguntas formuladas por los usuarios en lenguaje natural, las traduzca de forma segura a consultas o llamadas del sistema, y redacte o sintetice reportes gerenciales listos para su revision.

main.py - Exposicion de Endpoints (FastAPI)
Inicializa la aplicacion web asincrona mediante FastAPI, exponiendo la interfaz REST del sistema. Define las rutas principales del sistema:

    POST /api/login: Autenticacion de trabajadores

    GET /api/dashboard/{idsucursal}: Consolidacion de metricas para tableros gerenciales

    GET /api/pedidos/{idsucursal}/sugeridos: Calculo automatizado de reabastecimiento

    POST /api/pedidos/{id}/llegada: Registro de recepcion de mercancia

    GET /api/transferencias: Movimientos de stock entre sucursales

    POST /api/chat: Interfaz de consulta con la IA

    POST /api/reportes/generar: Generacion de reportes diarios en modo borrador asistidos por IA

    POST /api/reportes/{id}/enviar: Envio formal de reportes al gerente

    GET /api/reportes: Visualizacion de reportes recibidos

probar_ia.py - Herramienta de Pruebas en Terminal
Es un script de utilidad para desarrolladores y operadores que permite interactuar directamente con las capacidades de la IA desde la linea de comandos de la terminal en VS Code. Permite iniciar sesiones de chat de prueba especificando opcionalmente el identificador de la sucursal (ejecutando python probar_ia.py 2) o disparar la ejecucion de reportes automatizados en modo te
