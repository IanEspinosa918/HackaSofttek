/* =====================================================================
   Usuarios de base de datos para el proyecto
   - app_backend : lo usa el backend en Python (lee y escribe)
   - ia_lectura  : lo usa la IA para consultas libres (SOLO lectura, sin ver contraseñas)

   REQUISITO: SQL Server debe aceptar autenticación de SQL Server.
   En SSMS: clic derecho al servidor > Propiedades > Seguridad >
   "Modo de autenticación de SQL Server y Windows" > Aceptar, y reiniciar el servicio.

   Cambien las contraseñas antes de ejecutar.
   ===================================================================== */

USE master;
GO

IF NOT EXISTS (SELECT 1 FROM sys.server_principals WHERE name = 'app_backend')
    CREATE LOGIN app_backend WITH PASSWORD = 'Backend#2026!', CHECK_POLICY = ON;
GO
IF NOT EXISTS (SELECT 1 FROM sys.server_principals WHERE name = 'ia_lectura')
    CREATE LOGIN ia_lectura WITH PASSWORD = 'IaLectura#2026!', CHECK_POLICY = ON;
GO

USE Hakaton_JR;
GO

IF NOT EXISTS (SELECT 1 FROM sys.database_principals WHERE name = 'app_backend')
    CREATE USER app_backend FOR LOGIN app_backend;
GO
IF NOT EXISTS (SELECT 1 FROM sys.database_principals WHERE name = 'ia_lectura')
    CREATE USER ia_lectura FOR LOGIN ia_lectura;
GO

-- Backend: leer y escribir datos (no puede cambiar la estructura de las tablas)
ALTER ROLE db_datareader ADD MEMBER app_backend;
ALTER ROLE db_datawriter ADD MEMBER app_backend;
GO

-- IA: solo SELECT
ALTER ROLE db_datareader ADD MEMBER ia_lectura;
GO

-- La IA nunca puede ver los hashes de contraseña ni los usuarios de login
DENY SELECT ON trabajador (contrasena_hash, usuario) TO ia_lectura;
-- Y explícitamente no puede modificar nada
DENY INSERT, UPDATE, DELETE ON SCHEMA::dbo TO ia_lectura;
GO

PRINT 'Usuarios app_backend e ia_lectura listos.';
GO
