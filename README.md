Documentación Técnica del Sistema: Tienda Inteligente
1. Información General y Tecnologías

    Repositorio de GitHub: https://github.com/tu-usuario/HackaSofttek (Reemplazar con el enlace exacto del repositorio)

    Entorno de Desarrollo: Visual Studio Code (VS Code)

    Gestor de Base de Datos: Microsoft SQL Server (con esquemas para backend y perfiles de solo lectura para la IA)

    APIs e Integraciones:

        Google Gemini API: https://aistudio.google.com/apikey (Utilizada para chat conversacional con function calling, traducción de lenguaje natural a SQL y generación automatizada de reportes)

        FastAPI (API REST principal): Se ejecuta localmente en http://localhost:8000 (con documentación interactiva en /docs) y despliegue del frontend opcional en /app/.

2. Problemática Operativa en el Comercio Minorista

En la gestión tradicional de tiendas y cadenas comerciales, los administradores y operadores suelen lidiar con los siguientes puntos críticos:

    Pérdida por Caducidad y Mermas: La falta de visibilidad en tiempo real sobre las fechas de expiración de los productos genera acumulación de inventario vencido que no puede comercializarse, impactando directamente en el margen de ganancia.

    Sobreinventario y Capital Inmovilizado: Compras excesivas de productos de bajo desplazamiento atan capital de trabajo que podría utilizarse de manera más eficiente en mercancía con alta rotación.

    Cálculos de Reabastecimiento Ineficientes: Determinar qué pedir, a qué proveedor y en qué cantidades exactas suele basarse en estimaciones empíricas o cálculos manuales propensos a errores humanos, lo que provoca quiebres de stock.

    Aislamiento Logístico entre Sucursales: La dificultad para identificar desequilibrios de inventario (mientras una sucursal tiene exceso de stock de un artículo y otra padece desabastecimiento) retrasa las transferencias internas óptimas.

    Burocracia y Lentitud en la Generación de Reportes: Los gerentes pierden horas valiosas consolidando métricas operativas y redactando reportes diarios en lugar de tomar decisiones estratégicas basadas en datos consolidados.

3. La Solución: Arquitectura y Componentes del Sistema

El proyecto Tienda Inteligente resuelve estas problemáticas integrando lógica de negocio especializada en la cadena de suministro con capacidades cognitivas de inteligencia artificial.
3.1. Estructura de Archivos del Backend

    db.py: Conexión a SQL Server (backend y solo lectura para la IA)

    seguridad.py: Hash y verificación de contraseñas

    logica.py: Cálculos: caducidad, descuentos, sobreinventario, pedido sugerido, transferencias, mermas

    ia.py: Gemini: chat con function calling, respaldo de texto a SQL y reportes

    main.py: Endpoints de la API

    probar_ia.py: Chat con la IA desde la terminal, para pruebas

4. Explicación Detallada del Código por Módulo
db.py - Capa de Conexión a Base de Datos

    Qué hace: Establece la comunicación con la instancia de Microsoft SQL Server utilizando el driver ODBC 18.

    Detalle técnico: Gestiona perfiles de conexión diferenciados. Por un lado, maneja conexiones con privilegios transaccionales para las operaciones del backend (escritura, actualizaciones de inventario y registro de pedidos). Por otro lado, provee conexiones aisladas de solo lectura destinadas exclusivamente a las consultas generadas por la Inteligencia Artificial, resguardando la integridad y seguridad de la base de datos corporativa.

seguridad.py - Control de Acceso y Credenciales

    Qué hace: Provee funciones criptográficas para el manejo seguro de credenciales de operadores y gerentes.

    Detalle técnico: Implementa algoritmos de hash y verificación de contraseñas mediante la librería de cifrado. Permite generar los hashes correspondientes desde la terminal (ej. ejecutando python seguridad.py MiContraseña) para almacenarlos de manera segura en el campo trabajador.contrasena_hash de la base de datos.
