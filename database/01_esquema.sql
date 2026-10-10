/* =====================================================================
   Tienda Inteligente para Retail - Esquema de base de datos
   Motor: SQL Server (2016 o superior)
   Enfoque: control de mermas, inventario por lote, pedidos y reportes

   Se puede ejecutar varias veces: borra las tablas y las vuelve a crear.
   ===================================================================== */

IF DB_ID('Hakaton_JR') IS NULL
    CREATE DATABASE Hakaton_JR;
GO

USE Hakaton_JR;
GO

/* ---------------------------------------------------------------------
   0. Limpieza (orden inverso a las dependencias)
   --------------------------------------------------------------------- */
DROP VIEW  IF EXISTS vw_productos_por_caducar;
DROP VIEW  IF EXISTS vw_retraso_proveedor;
DROP VIEW  IF EXISTS vw_venta_promedio_diaria;
DROP VIEW  IF EXISTS vw_inventario_actual;

DROP TABLE IF EXISTS reporte;
DROP TABLE IF EXISTS promocion;
DROP TABLE IF EXISTS merma;
DROP TABLE IF EXISTS causa_merma;
DROP TABLE IF EXISTS transferencia;
DROP TABLE IF EXISTS detalle_venta;
DROP TABLE IF EXISTS venta;
DROP TABLE IF EXISTS lote;            -- antes que detalle_pedido (lote apunta a detalle_pedido)
DROP TABLE IF EXISTS detalle_pedido;
DROP TABLE IF EXISTS pedido;
DROP TABLE IF EXISTS producto;
DROP TABLE IF EXISTS proveedor;
DROP TABLE IF EXISTS categoria;
DROP TABLE IF EXISTS trabajador;
DROP TABLE IF EXISTS turno;
DROP TABLE IF EXISTS puesto;
DROP TABLE IF EXISTS sucursal;
GO

/* =====================================================================
   1. ORGANIZACIÓN: sucursales, puestos, turnos y trabajadores
   ===================================================================== */

CREATE TABLE sucursal (
    idsucursal   INT IDENTITY(1,1) PRIMARY KEY,
    nombre       VARCHAR(80)  NOT NULL UNIQUE,
    direccion    VARCHAR(150) NULL,
    telefono     VARCHAR(15)  NULL,
    activa       BIT          NOT NULL DEFAULT 1
);
GO

-- El puesto define también el rol en el sistema (operador o gerente)
CREATE TABLE puesto (
    idpuesto     INT IDENTITY(1,1) PRIMARY KEY,
    nombre       VARCHAR(50) NOT NULL UNIQUE,
    rol_sistema  VARCHAR(20) NOT NULL
        CONSTRAINT ck_puesto_rol CHECK (rol_sistema IN ('operador', 'gerente', 'ninguno'))
);
GO

CREATE TABLE turno (
    idturno      INT IDENTITY(1,1) PRIMARY KEY,
    nombre       VARCHAR(30) NOT NULL UNIQUE,
    hora_inicio  TIME        NOT NULL,
    hora_fin     TIME        NOT NULL
);
GO

CREATE TABLE trabajador (
    idtrabajador    INT IDENTITY(1,1) PRIMARY KEY,
    nombre          VARCHAR(60)  NOT NULL,
    apellido        VARCHAR(60)  NOT NULL,
    idsucursal      INT          NOT NULL,
    idpuesto        INT          NOT NULL,
    idturno         INT          NOT NULL,
    usuario         VARCHAR(40)  NULL,          -- solo quien entra al sistema
    contrasena_hash VARCHAR(255) NULL,          -- nunca la contraseña en texto
    activo          BIT          NOT NULL DEFAULT 1,
    CONSTRAINT fk_trabajador_sucursal FOREIGN KEY (idsucursal) REFERENCES sucursal(idsucursal),
    CONSTRAINT fk_trabajador_puesto   FOREIGN KEY (idpuesto)   REFERENCES puesto(idpuesto),
    CONSTRAINT fk_trabajador_turno    FOREIGN KEY (idturno)    REFERENCES turno(idturno)
);
GO

-- Usuario único, pero permitiendo varios trabajadores sin usuario (NULL)
CREATE UNIQUE INDEX ux_trabajador_usuario ON trabajador (usuario) WHERE usuario IS NOT NULL;
GO

/* =====================================================================
   2. CATÁLOGO: categorías, proveedores y productos
   ===================================================================== */

CREATE TABLE categoria (
    idcategoria  INT IDENTITY(1,1) PRIMARY KEY,
    nombre       VARCHAR(50) NOT NULL UNIQUE
);
GO

CREATE TABLE proveedor (
    idproveedor              INT IDENTITY(1,1) PRIMARY KEY,
    nombre                   VARCHAR(80) NOT NULL UNIQUE,
    telefono                 VARCHAR(15) NULL,
    correo                   VARCHAR(100) NULL,
    dias_entrega_prometidos  INT NOT NULL DEFAULT 1
        CONSTRAINT ck_proveedor_dias CHECK (dias_entrega_prometidos >= 0)
);
GO

CREATE TABLE producto (
    idproducto      INT IDENTITY(1,1) PRIMARY KEY,
    nombre          VARCHAR(80)   NOT NULL,
    idcategoria     INT           NOT NULL,
    idproveedor     INT           NOT NULL,
    precio_venta    DECIMAL(10,2) NOT NULL CONSTRAINT ck_producto_precio CHECK (precio_venta >= 0),
    costo           DECIMAL(10,2) NOT NULL CONSTRAINT ck_producto_costo  CHECK (costo >= 0),
    vida_util_dias  INT           NOT NULL CONSTRAINT ck_producto_vida   CHECK (vida_util_dias > 0),
    es_perecedero   BIT           NOT NULL DEFAULT 1,
    unidad          VARCHAR(15)   NOT NULL DEFAULT 'pieza',   -- pieza, kg, litro
    activo          BIT           NOT NULL DEFAULT 1,
    CONSTRAINT fk_producto_categoria FOREIGN KEY (idcategoria) REFERENCES categoria(idcategoria),
    CONSTRAINT fk_producto_proveedor FOREIGN KEY (idproveedor) REFERENCES proveedor(idproveedor)
);
GO

/* =====================================================================
   3. INVENTARIO POR LOTE
   Cada entrada de mercancía a una sucursal es un lote con su propia
   fecha de caducidad. El inventario se calcula sumando los lotes.
   ===================================================================== */

CREATE TABLE lote (
    idlote            INT IDENTITY(1,1) PRIMARY KEY,
    idproducto        INT  NOT NULL,
    idsucursal        INT  NOT NULL,
    iddetalle_pedido  INT  NULL,          -- de qué pedido vino (se liga más abajo)
    cantidad_inicial  INT  NOT NULL CONSTRAINT ck_lote_inicial CHECK (cantidad_inicial >= 0),
    cantidad_actual   INT  NOT NULL CONSTRAINT ck_lote_actual  CHECK (cantidad_actual  >= 0),
    fecha_entrada     DATE NOT NULL,
    fecha_caducidad   DATE NOT NULL,
    CONSTRAINT fk_lote_producto FOREIGN KEY (idproducto) REFERENCES producto(idproducto),
    CONSTRAINT fk_lote_sucursal FOREIGN KEY (idsucursal) REFERENCES sucursal(idsucursal),
    CONSTRAINT ck_lote_fechas   CHECK (fecha_caducidad >= fecha_entrada),
    CONSTRAINT ck_lote_cantidad CHECK (cantidad_actual <= cantidad_inicial)
);
GO

/* =====================================================================
   4. VENTAS (para calcular la venta promedio diaria)
   ===================================================================== */

CREATE TABLE venta (
    idventa       INT IDENTITY(1,1) PRIMARY KEY,
    idsucursal    INT       NOT NULL,
    fecha         DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    total         DECIMAL(12,2) NOT NULL DEFAULT 0,
    CONSTRAINT fk_venta_sucursal FOREIGN KEY (idsucursal) REFERENCES sucursal(idsucursal)
);
GO

CREATE TABLE detalle_venta (
    iddetalle_venta  INT IDENTITY(1,1) PRIMARY KEY,
    idventa          INT           NOT NULL,
    idproducto       INT           NOT NULL,
    idlote           INT           NULL,     -- de qué lote salió (opcional)
    cantidad         INT           NOT NULL CONSTRAINT ck_dv_cantidad CHECK (cantidad > 0),
    precio_unitario  DECIMAL(10,2) NOT NULL,
    descuento_pct    DECIMAL(5,2)  NOT NULL DEFAULT 0,
    CONSTRAINT fk_dv_venta    FOREIGN KEY (idventa)    REFERENCES venta(idventa),
    CONSTRAINT fk_dv_producto FOREIGN KEY (idproducto) REFERENCES producto(idproducto),
    CONSTRAINT fk_dv_lote     FOREIGN KEY (idlote)     REFERENCES lote(idlote)
);
GO

/* =====================================================================
   5. PEDIDOS A PROVEEDOR (aquí el operador marca los tiempos)
   ===================================================================== */

CREATE TABLE pedido (
    idpedido         INT IDENTITY(1,1) PRIMARY KEY,
    idproveedor      INT       NOT NULL,
    idsucursal       INT       NOT NULL,
    idtrabajador     INT       NOT NULL,          -- quién hizo el pedido
    fecha_pedido     DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    fecha_prometida  DATETIME2 NOT NULL,          -- cuándo dijo el proveedor que llegaría
    fecha_llegada    DATETIME2 NULL,              -- cuándo llegó de verdad (lo marca el operador)
    estado           VARCHAR(15) NOT NULL DEFAULT 'pendiente'
        CONSTRAINT ck_pedido_estado CHECK (estado IN ('pendiente', 'en_camino', 'recibido', 'cancelado')),
    observaciones    VARCHAR(250) NULL,
    CONSTRAINT fk_pedido_proveedor  FOREIGN KEY (idproveedor)  REFERENCES proveedor(idproveedor),
    CONSTRAINT fk_pedido_sucursal   FOREIGN KEY (idsucursal)   REFERENCES sucursal(idsucursal),
    CONSTRAINT fk_pedido_trabajador FOREIGN KEY (idtrabajador) REFERENCES trabajador(idtrabajador)
);
GO

CREATE TABLE detalle_pedido (
    iddetalle_pedido   INT IDENTITY(1,1) PRIMARY KEY,
    idpedido           INT NOT NULL,
    idproducto         INT NOT NULL,
    cantidad_pedida    INT NOT NULL CONSTRAINT ck_dp_pedida   CHECK (cantidad_pedida > 0),
    cantidad_recibida  INT NULL     CONSTRAINT ck_dp_recibida CHECK (cantidad_recibida >= 0),
    cantidad_danada    INT NOT NULL DEFAULT 0 CONSTRAINT ck_dp_danada CHECK (cantidad_danada >= 0),
    costo_unitario     DECIMAL(10,2) NOT NULL,
    CONSTRAINT fk_dp_pedido   FOREIGN KEY (idpedido)   REFERENCES pedido(idpedido),
    CONSTRAINT fk_dp_producto FOREIGN KEY (idproducto) REFERENCES producto(idproducto)
);
GO

-- Ahora que existe detalle_pedido, ligamos el lote con su pedido de origen
ALTER TABLE lote
    ADD CONSTRAINT fk_lote_detalle_pedido
    FOREIGN KEY (iddetalle_pedido) REFERENCES detalle_pedido(iddetalle_pedido);
GO

/* =====================================================================
   6. TRANSFERENCIAS ENTRE SUCURSALES
   ===================================================================== */

CREATE TABLE transferencia (
    idtransferencia     INT IDENTITY(1,1) PRIMARY KEY,
    idlote              INT       NOT NULL,       -- lote de origen
    idsucursal_origen   INT       NOT NULL,
    idsucursal_destino  INT       NOT NULL,
    cantidad            INT       NOT NULL CONSTRAINT ck_transf_cantidad CHECK (cantidad > 0),
    fecha               DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    idtrabajador        INT       NOT NULL,
    estado              VARCHAR(15) NOT NULL DEFAULT 'sugerida'
        CONSTRAINT ck_transf_estado CHECK (estado IN ('sugerida', 'aprobada', 'realizada', 'rechazada')),
    CONSTRAINT fk_transf_lote       FOREIGN KEY (idlote)             REFERENCES lote(idlote),
    CONSTRAINT fk_transf_origen     FOREIGN KEY (idsucursal_origen)  REFERENCES sucursal(idsucursal),
    CONSTRAINT fk_transf_destino    FOREIGN KEY (idsucursal_destino) REFERENCES sucursal(idsucursal),
    CONSTRAINT fk_transf_trabajador FOREIGN KEY (idtrabajador)       REFERENCES trabajador(idtrabajador),
    CONSTRAINT ck_transf_distintas  CHECK (idsucursal_origen <> idsucursal_destino)
);
GO

/* =====================================================================
   7. MERMAS (el centro del proyecto)
   ===================================================================== */

CREATE TABLE causa_merma (
    idcausa      INT IDENTITY(1,1) PRIMARY KEY,
    nombre       VARCHAR(40)  NOT NULL UNIQUE,   -- Caducidad, Daño, Proveedor, Robo, Otro
    descripcion  VARCHAR(150) NULL
);
GO

CREATE TABLE merma (
    idmerma        INT IDENTITY(1,1) PRIMARY KEY,
    idlote         INT           NOT NULL,
    idcausa        INT           NOT NULL,
    idtrabajador   INT           NOT NULL,       -- quién la registró
    cantidad       INT           NOT NULL CONSTRAINT ck_merma_cantidad CHECK (cantidad > 0),
    costo_total    DECIMAL(12,2) NOT NULL,       -- cantidad x costo del producto al registrarla
    fecha          DATETIME2     NOT NULL DEFAULT SYSDATETIME(),
    observaciones  VARCHAR(250)  NULL,
    CONSTRAINT fk_merma_lote       FOREIGN KEY (idlote)       REFERENCES lote(idlote),
    CONSTRAINT fk_merma_causa      FOREIGN KEY (idcausa)      REFERENCES causa_merma(idcausa),
    CONSTRAINT fk_merma_trabajador FOREIGN KEY (idtrabajador) REFERENCES trabajador(idtrabajador)
);
GO

/* =====================================================================
   8. PROMOCIONES / DESCUENTOS (aplicados a un lote)
   ===================================================================== */

CREATE TABLE promocion (
    idpromocion    INT IDENTITY(1,1) PRIMARY KEY,
    idlote         INT          NOT NULL,
    porcentaje     DECIMAL(5,2) NOT NULL CONSTRAINT ck_promo_pct CHECK (porcentaje > 0 AND porcentaje <= 100),
    fecha_inicio   DATE         NOT NULL,
    fecha_fin      DATE         NOT NULL,
    motivo         VARCHAR(30)  NOT NULL DEFAULT 'caducidad'
        CONSTRAINT ck_promo_motivo CHECK (motivo IN ('caducidad', 'sobreinventario', 'estrategica')),
    origen         VARCHAR(15)  NOT NULL DEFAULT 'sistema'     -- quién lo propuso
        CONSTRAINT ck_promo_origen CHECK (origen IN ('sistema', 'ia', 'manual')),
    estado         VARCHAR(15)  NOT NULL DEFAULT 'activa'
        CONSTRAINT ck_promo_estado CHECK (estado IN ('pendiente', 'activa', 'finalizada', 'rechazada')),
    idtrabajador   INT          NOT NULL,        -- quién la aplicó
    CONSTRAINT fk_promo_lote       FOREIGN KEY (idlote)       REFERENCES lote(idlote),
    CONSTRAINT fk_promo_trabajador FOREIGN KEY (idtrabajador) REFERENCES trabajador(idtrabajador),
    CONSTRAINT ck_promo_fechas     CHECK (fecha_fin >= fecha_inicio)
);
GO

/* =====================================================================
   9. REPORTES (generados con IA, enviados al gerente)
   ===================================================================== */

CREATE TABLE reporte (
    idreporte        INT IDENTITY(1,1) PRIMARY KEY,
    idtrabajador     INT           NOT NULL,     -- autor (operador)
    idsucursal       INT           NOT NULL,
    fecha            DATETIME2     NOT NULL DEFAULT SYSDATETIME(),
    titulo           VARCHAR(120)  NOT NULL,
    contenido        NVARCHAR(MAX) NOT NULL,     -- texto generado por Gemini
    estado           VARCHAR(15)   NOT NULL DEFAULT 'borrador'
        CONSTRAINT ck_reporte_estado CHECK (estado IN ('borrador', 'enviado', 'revisado')),
    idgerente        INT           NULL,         -- quién lo revisó
    fecha_revision   DATETIME2     NULL,
    comentario_gerente VARCHAR(500) NULL,
    CONSTRAINT fk_reporte_trabajador FOREIGN KEY (idtrabajador) REFERENCES trabajador(idtrabajador),
    CONSTRAINT fk_reporte_sucursal   FOREIGN KEY (idsucursal)   REFERENCES sucursal(idsucursal),
    CONSTRAINT fk_reporte_gerente    FOREIGN KEY (idgerente)    REFERENCES trabajador(idtrabajador)
);
GO

/* =====================================================================
   10. ÍNDICES para las consultas más frecuentes
   ===================================================================== */

CREATE INDEX ix_lote_sucursal_caducidad ON lote (idsucursal, fecha_caducidad) INCLUDE (idproducto, cantidad_actual);
CREATE INDEX ix_lote_producto           ON lote (idproducto);
CREATE INDEX ix_venta_sucursal_fecha    ON venta (idsucursal, fecha);
CREATE INDEX ix_dv_producto             ON detalle_venta (idproducto);
CREATE INDEX ix_pedido_proveedor        ON pedido (idproveedor, estado);
CREATE INDEX ix_merma_fecha             ON merma (fecha);
GO

/* =====================================================================
   11. VISTAS (le simplifican la vida al backend y a la IA)
   ===================================================================== */

-- Existencia actual por producto y sucursal
CREATE VIEW vw_inventario_actual AS
SELECT
    s.idsucursal,
    s.nombre                AS sucursal,
    p.idproducto,
    p.nombre                AS producto,
    c.nombre                AS categoria,
    SUM(l.cantidad_actual)  AS existencia,
    MIN(CASE WHEN l.cantidad_actual > 0 THEN l.fecha_caducidad END) AS proxima_caducidad
FROM lote l
JOIN producto  p ON p.idproducto  = l.idproducto
JOIN categoria c ON c.idcategoria = p.idcategoria
JOIN sucursal  s ON s.idsucursal  = l.idsucursal
GROUP BY s.idsucursal, s.nombre, p.idproducto, p.nombre, c.nombre;
GO

-- Venta promedio diaria de los últimos 30 días
CREATE VIEW vw_venta_promedio_diaria AS
SELECT
    v.idsucursal,
    dv.idproducto,
    CAST(SUM(dv.cantidad) AS DECIMAL(10,2)) / 30.0 AS venta_promedio_diaria
FROM detalle_venta dv
JOIN venta v ON v.idventa = dv.idventa
WHERE v.fecha >= DATEADD(DAY, -30, CAST(GETDATE() AS DATE))
GROUP BY v.idsucursal, dv.idproducto;
GO

-- Retraso real promedio por proveedor (en horas), con base en lo que marca el operador
CREATE VIEW vw_retraso_proveedor AS
SELECT
    pr.idproveedor,
    pr.nombre AS proveedor,
    COUNT(*)  AS entregas,
    AVG(CAST(DATEDIFF(MINUTE, pe.fecha_prometida, pe.fecha_llegada) AS DECIMAL(10,2))) / 60.0 AS retraso_promedio_horas,
    SUM(CASE WHEN pe.fecha_llegada > pe.fecha_prometida THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS pct_entregas_tarde
FROM pedido pe
JOIN proveedor pr ON pr.idproveedor = pe.idproveedor
WHERE pe.estado = 'recibido' AND pe.fecha_llegada IS NOT NULL
GROUP BY pr.idproveedor, pr.nombre;
GO

-- Lotes con existencia que caducan en los próximos 7 días
CREATE VIEW vw_productos_por_caducar AS
SELECT
    l.idlote,
    s.idsucursal,
    s.nombre AS sucursal,
    p.idproducto,
    p.nombre AS producto,
    l.cantidad_actual,
    l.fecha_caducidad,
    DATEDIFF(DAY, CAST(GETDATE() AS DATE), l.fecha_caducidad) AS dias_para_caducar,
    l.cantidad_actual * p.costo AS valor_en_riesgo
FROM lote l
JOIN producto p ON p.idproducto = l.idproducto
JOIN sucursal s ON s.idsucursal = l.idsucursal
WHERE l.cantidad_actual > 0
  AND l.fecha_caducidad BETWEEN CAST(GETDATE() AS DATE) AND DATEADD(DAY, 7, CAST(GETDATE() AS DATE));
GO

/* =====================================================================
   12. CATÁLOGOS BÁSICOS (datos fijos que no cambian)
   El resto de los datos de prueba los cargará generar_datos.py
   ===================================================================== */

INSERT INTO puesto (nombre, rol_sistema) VALUES
    ('Operador de inventario', 'operador'),
    ('Gerente de sucursal',    'gerente'),
    ('Cajero',                 'ninguno'),
    ('Auxiliar de piso',       'ninguno');

INSERT INTO turno (nombre, hora_inicio, hora_fin) VALUES
    ('Matutino',   '07:00', '15:00'),
    ('Vespertino', '15:00', '23:00');

INSERT INTO causa_merma (nombre, descripcion) VALUES
    ('Caducidad', 'El producto venció antes de venderse'),
    ('Daño',      'Golpeado, roto o mal manejado en tienda'),
    ('Proveedor', 'Llegó dañado o fuera de especificación'),
    ('Robo',      'Faltante no justificado'),
    ('Otro',      'Cualquier otra causa');
GO

PRINT 'Esquema de Hakaton_JR creado correctamente.';
GO
