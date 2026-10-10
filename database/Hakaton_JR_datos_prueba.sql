/* =====================================================================
   Hakaton_JR - Datos de prueba (15 INSERT por tabla)
   Se ejecuta sobre la base recien creada con Hakaton_JR_esquema_v3.sql
   (los ids se asignan en orden, 1 a 15; no ejecutar dos veces sin recrear).
   puesto, turno y causa_merma ya traen sus datos en el esquema.
   Los datos salen del dataset de Glazed Co. salvo donde se indica INVENTADO.
   ===================================================================== */
USE Hakaton_JR;
GO


-- ---------------------------------------------------------------
-- sucursal
-- Tiendas reales del dataset (las 15 con mas eventos de merma). Telefono: no existe en el dataset.
-- ---------------------------------------------------------------
INSERT INTO sucursal (nombre, direccion, telefono, activa, codigo, region, tipo_sitio, fecha_cierre) VALUES ('S001 - Food Court - Full Counter 1', 'Harborview International Airport', NULL, 1, 'S001', 'Northeast', 'Airport', NULL);
INSERT INTO sucursal (nombre, direccion, telefono, activa, codigo, region, tipo_sitio, fecha_cierre) VALUES ('S002 - Arrivals Hall - Shop-In-Shop 2', 'Harborview International Airport', NULL, 1, 'S002', 'Northeast', 'Airport', NULL);
INSERT INTO sucursal (nombre, direccion, telefono, activa, codigo, region, tipo_sitio, fecha_cierre) VALUES ('S004 - Departures Lobby - Shop-In-Shop 4', 'Harborview International Airport', NULL, 1, 'S004', 'Northeast', 'Airport', NULL);
INSERT INTO sucursal (nombre, direccion, telefono, activa, codigo, region, tipo_sitio, fecha_cierre) VALUES ('S011 - Departures Lobby - Express Kiosk 3', 'Desert Gate Airport', NULL, 1, 'S011', 'Southwest', 'Airport', NULL);
INSERT INTO sucursal (nombre, direccion, telefono, activa, codigo, region, tipo_sitio, fecha_cierre) VALUES ('S012 - Food Court - Full Counter 1', 'Union Central Rail Station', NULL, 1, 'S012', 'Northeast', 'Rail Station', NULL);
INSERT INTO sucursal (nombre, direccion, telefono, activa, codigo, region, tipo_sitio, fecha_cierre) VALUES ('S019 - Ticketing Level - Shop-In-Shop 2', 'Millbrook Regional Airport', NULL, 1, 'S019', 'Midwest', 'Airport', NULL);
INSERT INTO sucursal (nombre, direccion, telefono, activa, codigo, region, tipo_sitio, fecha_cierre) VALUES ('S021 - Departures Lobby - Shop-In-Shop 2', 'Cascade Bay Airport', NULL, 1, 'S021', 'Northwest', 'Airport', NULL);
INSERT INTO sucursal (nombre, direccion, telefono, activa, codigo, region, tipo_sitio, fecha_cierre) VALUES ('S022 - Terminal A - Shop-In-Shop 1', 'Metro Bus Terminal', NULL, 1, 'S022', 'Northeast', 'Bus Terminal', NULL);
INSERT INTO sucursal (nombre, direccion, telefono, activa, codigo, region, tipo_sitio, fecha_cierre) VALUES ('S023 - Gate Area East - Full Counter 2', 'Metro Bus Terminal', NULL, 1, 'S023', 'Northeast', 'Bus Terminal', NULL);
INSERT INTO sucursal (nombre, direccion, telefono, activa, codigo, region, tipo_sitio, fecha_cierre) VALUES ('S027 - Post-Security - Shop-In-Shop 2', 'Southport Airport', NULL, 1, 'S027', 'Southeast', 'Airport', NULL);
INSERT INTO sucursal (nombre, direccion, telefono, activa, codigo, region, tipo_sitio, fecha_cierre) VALUES ('S028 - Food Court - Full Counter 1  ', 'Eastgate International Airport', NULL, 1, 'S028', 'Northeast', 'Airport', NULL);
INSERT INTO sucursal (nombre, direccion, telefono, activa, codigo, region, tipo_sitio, fecha_cierre) VALUES ('S030 - Gate Area West - Shop-In-Shop 1', 'Bayfront Municipal Airport', NULL, 1, 'S030', 'Southeast', 'Airport', NULL);
INSERT INTO sucursal (nombre, direccion, telefono, activa, codigo, region, tipo_sitio, fecha_cierre) VALUES ('S033 - Gate Area West - Express Kiosk 1', 'Midtown Transit Hub', NULL, 1, 'S033', 'Northeast', 'Rail Station', NULL);
INSERT INTO sucursal (nombre, direccion, telefono, activa, codigo, region, tipo_sitio, fecha_cierre) VALUES ('S034 - Gate Area East - Full Counter 1', 'Casino Resort Plaza', NULL, 1, 'S034', 'Southwest', 'Resort', NULL);
INSERT INTO sucursal (nombre, direccion, telefono, activa, codigo, region, tipo_sitio, fecha_cierre) VALUES ('S035 - Main Concourse - Express Kiosk 1  ', 'Steel City Airport', NULL, 1, 'S035', 'Northeast', 'Airport', NULL);

-- ---------------------------------------------------------------
-- trabajador
-- INVENTADO (el dataset no trae personal). Hashes de ejemplo, no son contrasenas reales.
-- ---------------------------------------------------------------
INSERT INTO trabajador (nombre, apellido, idsucursal, idpuesto, idturno, usuario, contrasena_hash, activo) VALUES ('Carlos', 'Ramírez', 1, 1, 1, 'cramirez', 'hash_demo_cramirez', 1);
INSERT INTO trabajador (nombre, apellido, idsucursal, idpuesto, idturno, usuario, contrasena_hash, activo) VALUES ('Lucía', 'Fernández', 2, 2, 2, 'lfernandez', 'hash_demo_lfernandez', 1);
INSERT INTO trabajador (nombre, apellido, idsucursal, idpuesto, idturno, usuario, contrasena_hash, activo) VALUES ('Miguel', 'Torres', 3, 3, 1, NULL, NULL, 1);
INSERT INTO trabajador (nombre, apellido, idsucursal, idpuesto, idturno, usuario, contrasena_hash, activo) VALUES ('Ana', 'Morales', 4, 1, 2, 'amorales', 'hash_demo_amorales', 1);
INSERT INTO trabajador (nombre, apellido, idsucursal, idpuesto, idturno, usuario, contrasena_hash, activo) VALUES ('Jorge', 'Castillo', 5, 2, 1, 'jcastillo', 'hash_demo_jcastillo', 1);
INSERT INTO trabajador (nombre, apellido, idsucursal, idpuesto, idturno, usuario, contrasena_hash, activo) VALUES ('Sofía', 'Herrera', 6, 4, 2, NULL, NULL, 1);
INSERT INTO trabajador (nombre, apellido, idsucursal, idpuesto, idturno, usuario, contrasena_hash, activo) VALUES ('Luis', 'Navarro', 7, 1, 1, 'lnavarro', 'hash_demo_lnavarro', 1);
INSERT INTO trabajador (nombre, apellido, idsucursal, idpuesto, idturno, usuario, contrasena_hash, activo) VALUES ('Valeria', 'Ortega', 8, 2, 2, 'vortega', 'hash_demo_vortega', 1);
INSERT INTO trabajador (nombre, apellido, idsucursal, idpuesto, idturno, usuario, contrasena_hash, activo) VALUES ('Diego', 'Salazar', 9, 3, 1, NULL, NULL, 1);
INSERT INTO trabajador (nombre, apellido, idsucursal, idpuesto, idturno, usuario, contrasena_hash, activo) VALUES ('Paola', 'Mendoza', 10, 1, 2, 'pmendoza', 'hash_demo_pmendoza', 1);
INSERT INTO trabajador (nombre, apellido, idsucursal, idpuesto, idturno, usuario, contrasena_hash, activo) VALUES ('Ricardo', 'Vargas', 11, 2, 1, 'rvargas', 'hash_demo_rvargas', 1);
INSERT INTO trabajador (nombre, apellido, idsucursal, idpuesto, idturno, usuario, contrasena_hash, activo) VALUES ('Daniela', 'Ríos', 12, 4, 2, NULL, NULL, 1);
INSERT INTO trabajador (nombre, apellido, idsucursal, idpuesto, idturno, usuario, contrasena_hash, activo) VALUES ('Andrés', 'Cabrera', 13, 1, 1, 'acabrera', 'hash_demo_acabrera', 1);
INSERT INTO trabajador (nombre, apellido, idsucursal, idpuesto, idturno, usuario, contrasena_hash, activo) VALUES ('Fernanda', 'Luna', 14, 2, 2, 'fluna', 'hash_demo_fluna', 1);
INSERT INTO trabajador (nombre, apellido, idsucursal, idpuesto, idturno, usuario, contrasena_hash, activo) VALUES ('Héctor', 'Domínguez', 15, 3, 1, NULL, NULL, 1);

-- ---------------------------------------------------------------
-- categoria
-- Categorias reales de products.csv
-- ---------------------------------------------------------------
INSERT INTO categoria (nombre) VALUES ('Bakery');
INSERT INTO categoria (nombre) VALUES ('Specialty Beverage');
INSERT INTO categoria (nombre) VALUES ('Coffee & Tea');
INSERT INTO categoria (nombre) VALUES ('Sandwiches');
INSERT INTO categoria (nombre) VALUES ('Souvenir & Merch');
INSERT INTO categoria (nombre) VALUES ('Catering');
INSERT INTO categoria (nombre) VALUES ('Grab & Go');
INSERT INTO categoria (nombre) VALUES ('Recipe');
INSERT INTO categoria (nombre) VALUES ('Packaged Beverage');
INSERT INTO categoria (nombre) VALUES ('SPECIALTY BEVERAGE ');
INSERT INTO categoria (nombre) VALUES ('sandwiches');
INSERT INTO categoria (nombre) VALUES ('bakery');
INSERT INTO categoria (nombre) VALUES ('Produce');
INSERT INTO categoria (nombre) VALUES ('Sweet Snacks');
INSERT INTO categoria (nombre) VALUES ('Bakery Goods');

-- ---------------------------------------------------------------
-- proveedor
-- Los primeros 8 son reales (suppliers.csv); los 7 ultimos (SUP09-SUP15) son INVENTADOS para completar 15.
-- ---------------------------------------------------------------
INSERT INTO proveedor (nombre, telefono, correo, dias_entrega_prometidos, codigo, fill_rate_contrato, puntualidad_contrato) VALUES ('Northfield Bakery Partners', '555-0101', 'ventas1@ejemplo.com', 1, 'SUP01', 0.95, 0.93);
INSERT INTO proveedor (nombre, telefono, correo, dias_entrega_prometidos, codigo, fill_rate_contrato, puntualidad_contrato) VALUES ('Coastal Beverage Distribution', '555-0102', 'ventas2@ejemplo.com', 3, 'SUP02', 0.97, 0.95);
INSERT INTO proveedor (nombre, telefono, correo, dias_entrega_prometidos, codigo, fill_rate_contrato, puntualidad_contrato) VALUES ('Summit Frozen Foods', '555-0103', 'ventas3@ejemplo.com', 2, 'SUP03', 0.92, 0.9);
INSERT INTO proveedor (nombre, telefono, correo, dias_entrega_prometidos, codigo, fill_rate_contrato, puntualidad_contrato) VALUES ('Riverbend Fresh & Dairy', '555-0104', 'ventas4@ejemplo.com', 1, 'SUP04', 0.94, 0.92);
INSERT INTO proveedor (nombre, telefono, correo, dias_entrega_prometidos, codigo, fill_rate_contrato, puntualidad_contrato) VALUES ('Pioneer Merch & Packaging', '555-0105', 'ventas5@ejemplo.com', 7, 'SUP05', 0.88, 0.85);
INSERT INTO proveedor (nombre, telefono, correo, dias_entrega_prometidos, codigo, fill_rate_contrato, puntualidad_contrato) VALUES ('Evergreen Coffee Roasters', '555-0106', 'ventas6@ejemplo.com', 4, 'SUP06', 0.96, 0.94);
INSERT INTO proveedor (nombre, telefono, correo, dias_entrega_prometidos, codigo, fill_rate_contrato, puntualidad_contrato) VALUES ('Harbor Catering Supplies', '555-0107', 'ventas7@ejemplo.com', 2, 'SUP07', 0.93, 0.9);
INSERT INTO proveedor (nombre, telefono, correo, dias_entrega_prometidos, codigo, fill_rate_contrato, puntualidad_contrato) VALUES ('Metro Wholesale Foods', '555-0108', 'ventas8@ejemplo.com', 3, 'SUP08', 0.9, 0.88);
INSERT INTO proveedor (nombre, telefono, correo, dias_entrega_prometidos, codigo, fill_rate_contrato, puntualidad_contrato) VALUES ('Lakeside Dairy Cooperative', '555-0109', 'ventas9@ejemplo.com', 2, 'SUP09', 0.969, 0.949);
INSERT INTO proveedor (nombre, telefono, correo, dias_entrega_prometidos, codigo, fill_rate_contrato, puntualidad_contrato) VALUES ('Redwood Packaging Supply', '555-0110', 'ventas10@ejemplo.com', 2, 'SUP10', 0.936, 0.948);
INSERT INTO proveedor (nombre, telefono, correo, dias_entrega_prometidos, codigo, fill_rate_contrato, puntualidad_contrato) VALUES ('Sunrise Produce Wholesale', '555-0111', 'ventas11@ejemplo.com', 1, 'SUP11', 0.915, 0.921);
INSERT INTO proveedor (nombre, telefono, correo, dias_entrega_prometidos, codigo, fill_rate_contrato, puntualidad_contrato) VALUES ('Golden Grain Mills', '555-0112', 'ventas12@ejemplo.com', 3, 'SUP12', 0.949, 0.895);
INSERT INTO proveedor (nombre, telefono, correo, dias_entrega_prometidos, codigo, fill_rate_contrato, puntualidad_contrato) VALUES ('Metro Disposables Group', '555-0113', 'ventas13@ejemplo.com', 2, 'SUP13', 0.924, 0.887);
INSERT INTO proveedor (nombre, telefono, correo, dias_entrega_prometidos, codigo, fill_rate_contrato, puntualidad_contrato) VALUES ('Harbor Fresh Foods', '555-0114', 'ventas14@ejemplo.com', 3, 'SUP14', 0.951, 0.928);
INSERT INTO proveedor (nombre, telefono, correo, dias_entrega_prometidos, codigo, fill_rate_contrato, puntualidad_contrato) VALUES ('Prairie Eggs & Poultry', '555-0115', 'ventas15@ejemplo.com', 2, 'SUP15', 0.977, 0.932);

-- ---------------------------------------------------------------
-- producto
-- Los 15 SKUs con control de inventario y mas mermas. Costo = mediana de purchase_orders.
-- ---------------------------------------------------------------
INSERT INTO producto (nombre, idcategoria, idproveedor, precio_venta, costo, vida_util_dias, es_perecedero, unidad, activo, sku, tamano_caja) VALUES ('2 Donut Holes', 1, 1, 0.5, 0.16, 1, 1, 'pieza', 1, 'SKU-100003', 12);
INSERT INTO producto (nombre, idcategoria, idproveedor, precio_venta, costo, vida_util_dias, es_perecedero, unidad, activo, sku, tamano_caja) VALUES ('6 Donuts', 1, 1, 12.15, 2.78, 1, 1, 'pieza', 1, 'SKU-100304', 12);
INSERT INTO producto (nombre, idcategoria, idproveedor, precio_venta, costo, vida_util_dias, es_perecedero, unidad, activo, sku, tamano_caja) VALUES ('8 Donut Holes', 1, 1, 4.2, 1.1, 1, 1, 'pieza', 1, 'SKU-100599', 12);
INSERT INTO producto (nombre, idcategoria, idproveedor, precio_venta, costo, vida_util_dias, es_perecedero, unidad, activo, sku, tamano_caja) VALUES ('12 Croiss-Ant Donuts', 1, 1, 19.99, 4.93, 1, 1, 'pieza', 1, 'SKU-100502', 12);
INSERT INTO producto (nombre, idcategoria, idproveedor, precio_venta, costo, vida_util_dias, es_perecedero, unidad, activo, sku, tamano_caja) VALUES ('3 Donut Holes', 1, 1, 0.75, 0.18, 1, 1, 'pieza', 1, 'SKU-100524', 12);
INSERT INTO producto (nombre, idcategoria, idproveedor, precio_venta, costo, vida_util_dias, es_perecedero, unidad, activo, sku, tamano_caja) VALUES ('Bagel Twist', 1, 1, 3.4, 1.16, 2, 1, 'pieza', 1, 'SKU-100900', 12);
INSERT INTO producto (nombre, idcategoria, idproveedor, precio_venta, costo, vida_util_dias, es_perecedero, unidad, activo, sku, tamano_caja) VALUES ('4 Donut Holes', 1, 1, 1.5, 0.35, 1, 1, 'pieza', 1, 'SKU-100257', 12);
INSERT INTO producto (nombre, idcategoria, idproveedor, precio_venta, costo, vida_util_dias, es_perecedero, unidad, activo, sku, tamano_caja) VALUES ('Donut Holes Donut Holes 5 Count', 1, 1, 2.65, 0.77, 1, 1, 'pieza', 1, 'SKU-100514', 12);
INSERT INTO producto (nombre, idcategoria, idproveedor, precio_venta, costo, vida_util_dias, es_perecedero, unidad, activo, sku, tamano_caja) VALUES ('2 Mffin 6Pc Hb', 1, 1, 3.39, 0.96, 2, 1, 'pieza', 1, 'SKU-100403', 12);
INSERT INTO producto (nombre, idcategoria, idproveedor, precio_venta, costo, vida_util_dias, es_perecedero, unidad, activo, sku, tamano_caja) VALUES ('Oatmeal W Brown Sugar And Fruit', 1, 1, 2.19, 0.8, 2, 1, 'pieza', 1, 'SKU-100292', 12);
INSERT INTO producto (nombre, idcategoria, idproveedor, precio_venta, costo, vida_util_dias, es_perecedero, unidad, activo, sku, tamano_caja) VALUES ('12 Bagels', 1, 1, 11.45, 3.09, 2, 1, 'pieza', 1, 'SKU-100506', 12);
INSERT INTO producto (nombre, idcategoria, idproveedor, precio_venta, costo, vida_util_dias, es_perecedero, unidad, activo, sku, tamano_caja) VALUES ('10 DONUT HOLES TOPPED DOZEN DONUTS', 2, 1, 0.01, 0.0, 1, 1, 'pieza', 1, 'SKU-100616', 12);
INSERT INTO producto (nombre, idcategoria, idproveedor, precio_venta, costo, vida_util_dias, es_perecedero, unidad, activo, sku, tamano_caja) VALUES ('Bagel W Butter', 1, 1, 3.55, 0.96, 2, 1, 'pieza', 1, 'SKU-100131', 12);
INSERT INTO producto (nombre, idcategoria, idproveedor, precio_venta, costo, vida_util_dias, es_perecedero, unidad, activo, sku, tamano_caja) VALUES ('Original Coffee Cake Muffin', 1, 1, 5.99, 2.17, 2, 1, 'pieza', 1, 'SKU-100664', 12);
INSERT INTO producto (nombre, idcategoria, idproveedor, precio_venta, costo, vida_util_dias, es_perecedero, unidad, activo, sku, tamano_caja) VALUES ('6 Bacon Donuts', 1, 1, 12.6, 2.97, 1, 1, 'pieza', 1, 'SKU-100473', 12);

-- ---------------------------------------------------------------
-- pedido
-- Lineas reales de purchase_orders (incluye entregas incompletas y en transito).
-- ---------------------------------------------------------------
INSERT INTO pedido (idproveedor, idsucursal, idtrabajador, fecha_pedido, fecha_prometida, fecha_llegada, estado, observaciones) VALUES (1, 5, 1, '2026-09-29 08:00:00', '2026-09-30 10:00:00', '2026-09-30 10:00:00', 'recibido', NULL);
INSERT INTO pedido (idproveedor, idsucursal, idtrabajador, fecha_pedido, fecha_prometida, fecha_llegada, estado, observaciones) VALUES (1, 14, 13, '2026-09-29 08:00:00', '2026-09-30 10:00:00', '2026-09-30 10:00:00', 'recibido', NULL);
INSERT INTO pedido (idproveedor, idsucursal, idtrabajador, fecha_pedido, fecha_prometida, fecha_llegada, estado, observaciones) VALUES (1, 8, 10, '2026-09-29 08:00:00', '2026-09-30 10:00:00', '2026-09-30 10:00:00', 'recibido', NULL);
INSERT INTO pedido (idproveedor, idsucursal, idtrabajador, fecha_pedido, fecha_prometida, fecha_llegada, estado, observaciones) VALUES (1, 12, 7, '2026-09-29 08:00:00', '2026-09-30 10:00:00', '2026-09-30 10:00:00', 'recibido', NULL);
INSERT INTO pedido (idproveedor, idsucursal, idtrabajador, fecha_pedido, fecha_prometida, fecha_llegada, estado, observaciones) VALUES (1, 14, 13, '2026-09-29 08:00:00', '2026-09-30 10:00:00', '2026-09-30 10:00:00', 'recibido', NULL);
INSERT INTO pedido (idproveedor, idsucursal, idtrabajador, fecha_pedido, fecha_prometida, fecha_llegada, estado, observaciones) VALUES (1, 9, 13, '2026-09-28 08:00:00', '2026-09-29 10:00:00', '2026-09-29 10:00:00', 'recibido', 'Entrega incompleta');
INSERT INTO pedido (idproveedor, idsucursal, idtrabajador, fecha_pedido, fecha_prometida, fecha_llegada, estado, observaciones) VALUES (1, 13, 13, '2026-09-25 08:00:00', '2026-09-26 10:00:00', '2026-09-26 10:00:00', 'recibido', 'Entrega incompleta');
INSERT INTO pedido (idproveedor, idsucursal, idtrabajador, fecha_pedido, fecha_prometida, fecha_llegada, estado, observaciones) VALUES (1, 2, 7, '2026-09-23 08:00:00', '2026-09-24 10:00:00', '2026-09-24 10:00:00', 'recibido', 'Entrega incompleta');
INSERT INTO pedido (idproveedor, idsucursal, idtrabajador, fecha_pedido, fecha_prometida, fecha_llegada, estado, observaciones) VALUES (1, 5, 1, '2026-09-22 08:00:00', '2026-09-23 10:00:00', '2026-09-23 10:00:00', 'recibido', 'Entrega incompleta');
INSERT INTO pedido (idproveedor, idsucursal, idtrabajador, fecha_pedido, fecha_prometida, fecha_llegada, estado, observaciones) VALUES (1, 14, 13, '2026-09-30 08:00:00', '2026-10-01 10:00:00', NULL, 'en_camino', NULL);
INSERT INTO pedido (idproveedor, idsucursal, idtrabajador, fecha_pedido, fecha_prometida, fecha_llegada, estado, observaciones) VALUES (1, 5, 1, '2026-09-30 08:00:00', '2026-10-01 10:00:00', NULL, 'en_camino', NULL);
INSERT INTO pedido (idproveedor, idsucursal, idtrabajador, fecha_pedido, fecha_prometida, fecha_llegada, estado, observaciones) VALUES (1, 8, 10, '2026-09-30 08:00:00', '2026-10-01 10:00:00', NULL, 'en_camino', NULL);
INSERT INTO pedido (idproveedor, idsucursal, idtrabajador, fecha_pedido, fecha_prometida, fecha_llegada, estado, observaciones) VALUES (1, 3, 10, '2026-09-29 08:00:00', '2026-09-30 10:00:00', '2026-09-30 10:00:00', 'recibido', NULL);
INSERT INTO pedido (idproveedor, idsucursal, idtrabajador, fecha_pedido, fecha_prometida, fecha_llegada, estado, observaciones) VALUES (1, 15, 1, '2026-09-29 08:00:00', '2026-09-30 10:00:00', '2026-09-30 10:00:00', 'recibido', NULL);
INSERT INTO pedido (idproveedor, idsucursal, idtrabajador, fecha_pedido, fecha_prometida, fecha_llegada, estado, observaciones) VALUES (1, 1, 1, '2026-09-29 08:00:00', '2026-09-30 10:00:00', '2026-09-30 10:00:00', 'recibido', NULL);

-- ---------------------------------------------------------------
-- detalle_pedido
-- Un detalle por pedido. cantidad_danada = 0 (el dataset no la trae).
-- ---------------------------------------------------------------
INSERT INTO detalle_pedido (idpedido, idproducto, cantidad_pedida, cantidad_recibida, cantidad_danada, costo_unitario) VALUES (1, 10, 12, 12, 0, 0.82);
INSERT INTO detalle_pedido (idpedido, idproducto, cantidad_pedida, cantidad_recibida, cantidad_danada, costo_unitario) VALUES (2, 3, 12, 12, 0, 1.06);
INSERT INTO detalle_pedido (idpedido, idproducto, cantidad_pedida, cantidad_recibida, cantidad_danada, costo_unitario) VALUES (3, 1, 12, 12, 0, 0.16);
INSERT INTO detalle_pedido (idpedido, idproducto, cantidad_pedida, cantidad_recibida, cantidad_danada, costo_unitario) VALUES (4, 13, 12, 12, 0, 0.99);
INSERT INTO detalle_pedido (idpedido, idproducto, cantidad_pedida, cantidad_recibida, cantidad_danada, costo_unitario) VALUES (5, 1, 12, 12, 0, 0.16);
INSERT INTO detalle_pedido (idpedido, idproducto, cantidad_pedida, cantidad_recibida, cantidad_danada, costo_unitario) VALUES (6, 14, 24, 12, 0, 2.18);
INSERT INTO detalle_pedido (idpedido, idproducto, cantidad_pedida, cantidad_recibida, cantidad_danada, costo_unitario) VALUES (7, 14, 24, 12, 0, 2.11);
INSERT INTO detalle_pedido (idpedido, idproducto, cantidad_pedida, cantidad_recibida, cantidad_danada, costo_unitario) VALUES (8, 9, 24, 12, 0, 0.96);
INSERT INTO detalle_pedido (idpedido, idproducto, cantidad_pedida, cantidad_recibida, cantidad_danada, costo_unitario) VALUES (9, 5, 24, 12, 0, 0.18);
INSERT INTO detalle_pedido (idpedido, idproducto, cantidad_pedida, cantidad_recibida, cantidad_danada, costo_unitario) VALUES (10, 1, 12, NULL, 0, 0.16);
INSERT INTO detalle_pedido (idpedido, idproducto, cantidad_pedida, cantidad_recibida, cantidad_danada, costo_unitario) VALUES (11, 14, 24, NULL, 0, 2.17);
INSERT INTO detalle_pedido (idpedido, idproducto, cantidad_pedida, cantidad_recibida, cantidad_danada, costo_unitario) VALUES (12, 13, 12, NULL, 0, 0.94);
INSERT INTO detalle_pedido (idpedido, idproducto, cantidad_pedida, cantidad_recibida, cantidad_danada, costo_unitario) VALUES (13, 5, 12, 12, 0, 0.19);
INSERT INTO detalle_pedido (idpedido, idproducto, cantidad_pedida, cantidad_recibida, cantidad_danada, costo_unitario) VALUES (14, 13, 12, 12, 0, 0.96);
INSERT INTO detalle_pedido (idpedido, idproducto, cantidad_pedida, cantidad_recibida, cantidad_danada, costo_unitario) VALUES (15, 4, 12, 12, 0, 5.05);

-- ---------------------------------------------------------------
-- lote
-- Los primeros lotes se reconstruyen de dias con merma (ya sin existencia); los ultimos son recepciones vigentes al 30-sep-2026.
-- ---------------------------------------------------------------
INSERT INTO lote (idproducto, idsucursal, iddetalle_pedido, cantidad_inicial, cantidad_actual, fecha_entrada, fecha_caducidad) VALUES (13, 11, NULL, 26, 0, '2026-09-28', '2026-09-30');
INSERT INTO lote (idproducto, idsucursal, iddetalle_pedido, cantidad_inicial, cantidad_actual, fecha_entrada, fecha_caducidad) VALUES (13, 3, NULL, 27, 0, '2026-09-25', '2026-09-27');
INSERT INTO lote (idproducto, idsucursal, iddetalle_pedido, cantidad_inicial, cantidad_actual, fecha_entrada, fecha_caducidad) VALUES (10, 8, NULL, 5, 0, '2026-09-24', '2026-09-26');
INSERT INTO lote (idproducto, idsucursal, iddetalle_pedido, cantidad_inicial, cantidad_actual, fecha_entrada, fecha_caducidad) VALUES (13, 8, NULL, 13, 0, '2026-09-21', '2026-09-23');
INSERT INTO lote (idproducto, idsucursal, iddetalle_pedido, cantidad_inicial, cantidad_actual, fecha_entrada, fecha_caducidad) VALUES (9, 11, NULL, 13, 0, '2026-09-18', '2026-09-20');
INSERT INTO lote (idproducto, idsucursal, iddetalle_pedido, cantidad_inicial, cantidad_actual, fecha_entrada, fecha_caducidad) VALUES (2, 12, NULL, 12, 0, '2026-09-29', '2026-09-30');
INSERT INTO lote (idproducto, idsucursal, iddetalle_pedido, cantidad_inicial, cantidad_actual, fecha_entrada, fecha_caducidad) VALUES (5, 13, NULL, 12, 0, '2026-09-29', '2026-09-30');
INSERT INTO lote (idproducto, idsucursal, iddetalle_pedido, cantidad_inicial, cantidad_actual, fecha_entrada, fecha_caducidad) VALUES (11, 15, NULL, 8, 0, '2026-09-28', '2026-09-30');
INSERT INTO lote (idproducto, idsucursal, iddetalle_pedido, cantidad_inicial, cantidad_actual, fecha_entrada, fecha_caducidad) VALUES (2, 9, NULL, 12, 0, '2026-09-29', '2026-09-30');
INSERT INTO lote (idproducto, idsucursal, iddetalle_pedido, cantidad_inicial, cantidad_actual, fecha_entrada, fecha_caducidad) VALUES (10, 6, NULL, 12, 0, '2026-09-28', '2026-09-30');
INSERT INTO lote (idproducto, idsucursal, iddetalle_pedido, cantidad_inicial, cantidad_actual, fecha_entrada, fecha_caducidad) VALUES (10, 5, 1, 12, 12, '2026-09-30', '2026-10-02');
INSERT INTO lote (idproducto, idsucursal, iddetalle_pedido, cantidad_inicial, cantidad_actual, fecha_entrada, fecha_caducidad) VALUES (3, 14, 2, 12, 10, '2026-09-30', '2026-10-01');
INSERT INTO lote (idproducto, idsucursal, iddetalle_pedido, cantidad_inicial, cantidad_actual, fecha_entrada, fecha_caducidad) VALUES (1, 8, 3, 12, 7, '2026-09-30', '2026-10-01');
INSERT INTO lote (idproducto, idsucursal, iddetalle_pedido, cantidad_inicial, cantidad_actual, fecha_entrada, fecha_caducidad) VALUES (13, 12, 4, 12, 12, '2026-09-30', '2026-10-02');
INSERT INTO lote (idproducto, idsucursal, iddetalle_pedido, cantidad_inicial, cantidad_actual, fecha_entrada, fecha_caducidad) VALUES (1, 14, 5, 12, 8, '2026-09-30', '2026-10-01');

-- ---------------------------------------------------------------
-- venta
-- Ventas reales (sales_daily): una linea por venta, total = net_sales.
-- ---------------------------------------------------------------
INSERT INTO venta (idsucursal, fecha, total) VALUES (5, '2026-09-30 12:00:00', 246.08);
INSERT INTO venta (idsucursal, fecha, total) VALUES (13, '2026-09-30 12:00:00', 55.92);
INSERT INTO venta (idsucursal, fecha, total) VALUES (15, '2026-09-30 12:00:00', 26.57);
INSERT INTO venta (idsucursal, fecha, total) VALUES (6, '2026-09-30 12:00:00', 12.57);
INSERT INTO venta (idsucursal, fecha, total) VALUES (2, '2026-09-30 12:00:00', 2.69);
INSERT INTO venta (idsucursal, fecha, total) VALUES (9, '2026-09-30 12:00:00', 10.56);
INSERT INTO venta (idsucursal, fecha, total) VALUES (11, '2026-09-30 12:00:00', 2.36);
INSERT INTO venta (idsucursal, fecha, total) VALUES (1, '2026-09-30 12:00:00', 10.14);
INSERT INTO venta (idsucursal, fecha, total) VALUES (7, '2026-09-30 12:00:00', 2.43);
INSERT INTO venta (idsucursal, fecha, total) VALUES (14, '2026-09-30 12:00:00', 54.47);
INSERT INTO venta (idsucursal, fecha, total) VALUES (3, '2026-09-30 12:00:00', 1.74);
INSERT INTO venta (idsucursal, fecha, total) VALUES (8, '2026-09-30 12:00:00', 3.19);
INSERT INTO venta (idsucursal, fecha, total) VALUES (4, '2026-09-30 12:00:00', 22.0);
INSERT INTO venta (idsucursal, fecha, total) VALUES (12, '2026-09-30 12:00:00', 9.16);
INSERT INTO venta (idsucursal, fecha, total) VALUES (10, '2026-09-30 12:00:00', 21.54);

-- ---------------------------------------------------------------
-- detalle_venta
-- ---------------------------------------------------------------
INSERT INTO detalle_venta (idventa, idproducto, idlote, cantidad, precio_unitario, descuento_pct) VALUES (1, 14, NULL, 32, 7.69, 0.0);
INSERT INTO detalle_venta (idventa, idproducto, idlote, cantidad, precio_unitario, descuento_pct) VALUES (2, 14, NULL, 8, 6.99, 0.0);
INSERT INTO detalle_venta (idventa, idproducto, idlote, cantidad, precio_unitario, descuento_pct) VALUES (3, 13, NULL, 8, 3.69, 9.99);
INSERT INTO detalle_venta (idventa, idproducto, idlote, cantidad, precio_unitario, descuento_pct) VALUES (4, 3, NULL, 3, 4.19, 0.0);
INSERT INTO detalle_venta (idventa, idproducto, idlote, cantidad, precio_unitario, descuento_pct) VALUES (5, 8, NULL, 1, 2.99, 10.03);
INSERT INTO detalle_venta (idventa, idproducto, idlote, cantidad, precio_unitario, descuento_pct) VALUES (6, 5, NULL, 12, 0.88, 0.0);
INSERT INTO detalle_venta (idventa, idproducto, idlote, cantidad, precio_unitario, descuento_pct) VALUES (7, 1, NULL, 4, 0.59, 0.0);
INSERT INTO detalle_venta (idventa, idproducto, idlote, cantidad, precio_unitario, descuento_pct) VALUES (8, 7, NULL, 6, 1.69, 0.0);
INSERT INTO detalle_venta (idventa, idproducto, idlote, cantidad, precio_unitario, descuento_pct) VALUES (9, 5, NULL, 3, 0.81, 0.0);
INSERT INTO detalle_venta (idventa, idproducto, idlote, cantidad, precio_unitario, descuento_pct) VALUES (10, 13, NULL, 13, 4.19, 0.0);
INSERT INTO detalle_venta (idventa, idproducto, idlote, cantidad, precio_unitario, descuento_pct) VALUES (11, 1, NULL, 3, 0.58, 0.0);
INSERT INTO detalle_venta (idventa, idproducto, idlote, cantidad, precio_unitario, descuento_pct) VALUES (12, 8, NULL, 1, 3.19, 0.0);
INSERT INTO detalle_venta (idventa, idproducto, idlote, cantidad, precio_unitario, descuento_pct) VALUES (13, 4, NULL, 1, 22.0, 0.0);
INSERT INTO detalle_venta (idventa, idproducto, idlote, cantidad, precio_unitario, descuento_pct) VALUES (14, 10, NULL, 4, 2.29, 0.0);
INSERT INTO detalle_venta (idventa, idproducto, idlote, cantidad, precio_unitario, descuento_pct) VALUES (15, 13, NULL, 6, 3.59, 0.0);

-- ---------------------------------------------------------------
-- transferencia
-- INVENTADO sobre lotes reales con existencia (el dataset no trae transferencias).
-- ---------------------------------------------------------------
INSERT INTO transferencia (idlote, idsucursal_origen, idsucursal_destino, cantidad, fecha, idtrabajador, estado) VALUES (11, 5, 9, 6, '2026-09-28 10:00:00', 1, 'sugerida');
INSERT INTO transferencia (idlote, idsucursal_origen, idsucursal_destino, cantidad, fecha, idtrabajador, estado) VALUES (12, 14, 4, 5, '2026-09-29 11:00:00', 13, 'aprobada');
INSERT INTO transferencia (idlote, idsucursal_origen, idsucursal_destino, cantidad, fecha, idtrabajador, estado) VALUES (13, 8, 14, 1, '2026-09-30 12:00:00', 10, 'realizada');
INSERT INTO transferencia (idlote, idsucursal_origen, idsucursal_destino, cantidad, fecha, idtrabajador, estado) VALUES (14, 12, 4, 6, '2026-09-28 13:00:00', 7, 'rechazada');
INSERT INTO transferencia (idlote, idsucursal_origen, idsucursal_destino, cantidad, fecha, idtrabajador, estado) VALUES (15, 14, 7, 2, '2026-09-29 14:00:00', 13, 'sugerida');
INSERT INTO transferencia (idlote, idsucursal_origen, idsucursal_destino, cantidad, fecha, idtrabajador, estado) VALUES (11, 5, 14, 6, '2026-09-30 15:00:00', 1, 'aprobada');
INSERT INTO transferencia (idlote, idsucursal_origen, idsucursal_destino, cantidad, fecha, idtrabajador, estado) VALUES (12, 14, 9, 2, '2026-09-28 16:00:00', 13, 'realizada');
INSERT INTO transferencia (idlote, idsucursal_origen, idsucursal_destino, cantidad, fecha, idtrabajador, estado) VALUES (13, 8, 4, 1, '2026-09-29 17:00:00', 10, 'rechazada');
INSERT INTO transferencia (idlote, idsucursal_origen, idsucursal_destino, cantidad, fecha, idtrabajador, estado) VALUES (14, 12, 9, 3, '2026-09-30 10:00:00', 7, 'sugerida');
INSERT INTO transferencia (idlote, idsucursal_origen, idsucursal_destino, cantidad, fecha, idtrabajador, estado) VALUES (15, 14, 12, 2, '2026-09-28 11:00:00', 13, 'aprobada');
INSERT INTO transferencia (idlote, idsucursal_origen, idsucursal_destino, cantidad, fecha, idtrabajador, estado) VALUES (11, 5, 4, 3, '2026-09-29 12:00:00', 1, 'realizada');
INSERT INTO transferencia (idlote, idsucursal_origen, idsucursal_destino, cantidad, fecha, idtrabajador, estado) VALUES (12, 14, 15, 5, '2026-09-30 13:00:00', 13, 'rechazada');
INSERT INTO transferencia (idlote, idsucursal_origen, idsucursal_destino, cantidad, fecha, idtrabajador, estado) VALUES (13, 8, 9, 1, '2026-09-28 14:00:00', 10, 'sugerida');
INSERT INTO transferencia (idlote, idsucursal_origen, idsucursal_destino, cantidad, fecha, idtrabajador, estado) VALUES (14, 12, 14, 4, '2026-09-29 15:00:00', 7, 'aprobada');
INSERT INTO transferencia (idlote, idsucursal_origen, idsucursal_destino, cantidad, fecha, idtrabajador, estado) VALUES (15, 14, 2, 3, '2026-09-30 16:00:00', 13, 'realizada');

-- ---------------------------------------------------------------
-- merma
-- Mermas reales: expired_qty -> Caducidad, damaged_qty -> Danio (inventory_daily). costo_total = cantidad x costo.
-- ---------------------------------------------------------------
INSERT INTO merma (idlote, idcausa, idtrabajador, cantidad, costo_total, fecha, observaciones) VALUES (1, 1, 4, 1, 0.96, '2026-09-30 19:00:00', 'Producto vencido al cierre');
INSERT INTO merma (idlote, idcausa, idtrabajador, cantidad, costo_total, fecha, observaciones) VALUES (1, 2, 4, 3, 2.88, '2026-09-30 19:00:00', 'Producto danado en tienda');
INSERT INTO merma (idlote, idcausa, idtrabajador, cantidad, costo_total, fecha, observaciones) VALUES (2, 1, 10, 8, 7.68, '2026-09-27 19:00:00', 'Producto vencido al cierre');
INSERT INTO merma (idlote, idcausa, idtrabajador, cantidad, costo_total, fecha, observaciones) VALUES (2, 2, 10, 3, 2.88, '2026-09-27 19:00:00', 'Producto danado en tienda');
INSERT INTO merma (idlote, idcausa, idtrabajador, cantidad, costo_total, fecha, observaciones) VALUES (3, 1, 10, 1, 0.8, '2026-09-26 19:00:00', 'Producto vencido al cierre');
INSERT INTO merma (idlote, idcausa, idtrabajador, cantidad, costo_total, fecha, observaciones) VALUES (3, 2, 10, 1, 0.8, '2026-09-26 19:00:00', 'Producto danado en tienda');
INSERT INTO merma (idlote, idcausa, idtrabajador, cantidad, costo_total, fecha, observaciones) VALUES (4, 1, 10, 3, 2.88, '2026-09-23 19:00:00', 'Producto vencido al cierre');
INSERT INTO merma (idlote, idcausa, idtrabajador, cantidad, costo_total, fecha, observaciones) VALUES (4, 2, 10, 1, 0.96, '2026-09-23 19:00:00', 'Producto danado en tienda');
INSERT INTO merma (idlote, idcausa, idtrabajador, cantidad, costo_total, fecha, observaciones) VALUES (5, 1, 4, 4, 3.84, '2026-09-20 19:00:00', 'Producto vencido al cierre');
INSERT INTO merma (idlote, idcausa, idtrabajador, cantidad, costo_total, fecha, observaciones) VALUES (5, 2, 4, 1, 0.96, '2026-09-20 19:00:00', 'Producto danado en tienda');
INSERT INTO merma (idlote, idcausa, idtrabajador, cantidad, costo_total, fecha, observaciones) VALUES (6, 1, 7, 9, 25.02, '2026-09-30 19:00:00', 'Producto vencido al cierre');
INSERT INTO merma (idlote, idcausa, idtrabajador, cantidad, costo_total, fecha, observaciones) VALUES (7, 1, 13, 7, 1.26, '2026-09-30 19:00:00', 'Producto vencido al cierre');
INSERT INTO merma (idlote, idcausa, idtrabajador, cantidad, costo_total, fecha, observaciones) VALUES (8, 1, 1, 1, 3.09, '2026-09-30 19:00:00', 'Producto vencido al cierre');
INSERT INTO merma (idlote, idcausa, idtrabajador, cantidad, costo_total, fecha, observaciones) VALUES (9, 1, 13, 7, 19.46, '2026-09-30 19:00:00', 'Producto vencido al cierre');
INSERT INTO merma (idlote, idcausa, idtrabajador, cantidad, costo_total, fecha, observaciones) VALUES (10, 1, 4, 10, 8.0, '2026-09-30 19:00:00', 'Producto vencido al cierre');

-- ---------------------------------------------------------------
-- promocion
-- INVENTADO sobre lotes reales con existencia (rebajas para evitar merma).
-- ---------------------------------------------------------------
INSERT INTO promocion (idlote, porcentaje, fecha_inicio, fecha_fin, motivo, origen, estado, idtrabajador) VALUES (11, 40, '2026-09-28', '2026-10-01', 'caducidad', 'ia', 'activa', 1);
INSERT INTO promocion (idlote, porcentaje, fecha_inicio, fecha_fin, motivo, origen, estado, idtrabajador) VALUES (12, 15, '2026-09-29', '2026-10-04', 'sobreinventario', 'sistema', 'pendiente', 13);
INSERT INTO promocion (idlote, porcentaje, fecha_inicio, fecha_fin, motivo, origen, estado, idtrabajador) VALUES (13, 12, '2026-09-30', '2026-10-05', 'estrategica', 'manual', 'finalizada', 10);
INSERT INTO promocion (idlote, porcentaje, fecha_inicio, fecha_fin, motivo, origen, estado, idtrabajador) VALUES (14, 30, '2026-10-01', '2026-10-04', 'caducidad', 'ia', 'activa', 7);
INSERT INTO promocion (idlote, porcentaje, fecha_inicio, fecha_fin, motivo, origen, estado, idtrabajador) VALUES (15, 15, '2026-09-28', '2026-10-03', 'sobreinventario', 'sistema', 'rechazada', 13);
INSERT INTO promocion (idlote, porcentaje, fecha_inicio, fecha_fin, motivo, origen, estado, idtrabajador) VALUES (11, 15, '2026-09-29', '2026-10-02', 'estrategica', 'manual', 'activa', 1);
INSERT INTO promocion (idlote, porcentaje, fecha_inicio, fecha_fin, motivo, origen, estado, idtrabajador) VALUES (12, 25, '2026-09-30', '2026-10-03', 'caducidad', 'ia', 'pendiente', 13);
INSERT INTO promocion (idlote, porcentaje, fecha_inicio, fecha_fin, motivo, origen, estado, idtrabajador) VALUES (13, 15, '2026-10-01', '2026-10-06', 'sobreinventario', 'sistema', 'finalizada', 10);
INSERT INTO promocion (idlote, porcentaje, fecha_inicio, fecha_fin, motivo, origen, estado, idtrabajador) VALUES (14, 12, '2026-09-28', '2026-10-03', 'estrategica', 'manual', 'activa', 7);
INSERT INTO promocion (idlote, porcentaje, fecha_inicio, fecha_fin, motivo, origen, estado, idtrabajador) VALUES (15, 40, '2026-09-29', '2026-10-02', 'caducidad', 'ia', 'rechazada', 13);
INSERT INTO promocion (idlote, porcentaje, fecha_inicio, fecha_fin, motivo, origen, estado, idtrabajador) VALUES (11, 20, '2026-09-30', '2026-10-05', 'sobreinventario', 'sistema', 'activa', 1);
INSERT INTO promocion (idlote, porcentaje, fecha_inicio, fecha_fin, motivo, origen, estado, idtrabajador) VALUES (12, 10, '2026-10-01', '2026-10-03', 'estrategica', 'manual', 'pendiente', 13);
INSERT INTO promocion (idlote, porcentaje, fecha_inicio, fecha_fin, motivo, origen, estado, idtrabajador) VALUES (13, 30, '2026-09-28', '2026-10-03', 'caducidad', 'ia', 'finalizada', 10);
INSERT INTO promocion (idlote, porcentaje, fecha_inicio, fecha_fin, motivo, origen, estado, idtrabajador) VALUES (14, 15, '2026-09-29', '2026-10-02', 'sobreinventario', 'sistema', 'activa', 7);
INSERT INTO promocion (idlote, porcentaje, fecha_inicio, fecha_fin, motivo, origen, estado, idtrabajador) VALUES (15, 12, '2026-09-30', '2026-10-03', 'estrategica', 'manual', 'rechazada', 13);

-- ---------------------------------------------------------------
-- reporte
-- INVENTADO: texto de ejemplo con las cifras de merma de esta muestra.
-- ---------------------------------------------------------------
INSERT INTO reporte (idtrabajador, idsucursal, fecha, titulo, contenido, estado, idgerente, fecha_revision, comentario_gerente) VALUES (1, 1, '2026-09-30 17:00:00', 'Reporte de mermas - S001 - Food Court - Full Counter 1', 'Resumen semanal de S001 - Food Court - Full Counter 1. Sin mermas registradas en la muestra. Se recomienda mantener el nivel actual de pedido y vigilar los lotes proximos a caducar.', 'enviado', NULL, NULL, NULL);
INSERT INTO reporte (idtrabajador, idsucursal, fecha, titulo, contenido, estado, idgerente, fecha_revision, comentario_gerente) VALUES (7, 2, '2026-09-30 17:00:00', 'Reporte de mermas - S002 - Arrivals Hall - Shop-In-Shop 2', 'Resumen semanal de S002 - Arrivals Hall - Shop-In-Shop 2. Sin mermas registradas en la muestra. Se recomienda mantener el nivel actual de pedido y vigilar los lotes proximos a caducar.', 'revisado', 8, '2026-10-01 09:30:00', 'Revisado, aplicar ajuste de pedido.');
INSERT INTO reporte (idtrabajador, idsucursal, fecha, titulo, contenido, estado, idgerente, fecha_revision, comentario_gerente) VALUES (10, 3, '2026-09-30 17:00:00', 'Reporte de mermas - S004 - Departures Lobby - Shop-In-Shop 4', 'Resumen semanal de mermas de S004 - Departures Lobby - Shop-In-Shop 4. Merma registrada en la muestra: $10.56 USD, principalmente por caducidad. Recomendacion: reducir el pedido de los productos con mayor vencimiento y revisar los lotes proximos a caducar.', 'borrador', NULL, NULL, NULL);
INSERT INTO reporte (idtrabajador, idsucursal, fecha, titulo, contenido, estado, idgerente, fecha_revision, comentario_gerente) VALUES (4, 4, '2026-09-30 17:00:00', 'Reporte de mermas - S011 - Departures Lobby - Express Kiosk ', 'Resumen semanal de S011 - Departures Lobby - Express Kiosk 3. Sin mermas registradas en la muestra. Se recomienda mantener el nivel actual de pedido y vigilar los lotes proximos a caducar.', 'enviado', NULL, NULL, NULL);
INSERT INTO reporte (idtrabajador, idsucursal, fecha, titulo, contenido, estado, idgerente, fecha_revision, comentario_gerente) VALUES (1, 5, '2026-09-30 17:00:00', 'Reporte de mermas - S012 - Food Court - Full Counter 1', 'Resumen semanal de S012 - Food Court - Full Counter 1. Sin mermas registradas en la muestra. Se recomienda mantener el nivel actual de pedido y vigilar los lotes proximos a caducar.', 'revisado', 2, '2026-10-01 09:30:00', 'Revisado, aplicar ajuste de pedido.');
INSERT INTO reporte (idtrabajador, idsucursal, fecha, titulo, contenido, estado, idgerente, fecha_revision, comentario_gerente) VALUES (4, 6, '2026-09-30 17:00:00', 'Reporte de mermas - S019 - Ticketing Level - Shop-In-Shop 2', 'Resumen semanal de mermas de S019 - Ticketing Level - Shop-In-Shop 2. Merma registrada en la muestra: $8.00 USD, principalmente por caducidad. Recomendacion: reducir el pedido de los productos con mayor vencimiento y revisar los lotes proximos a caducar.', 'borrador', NULL, NULL, NULL);
INSERT INTO reporte (idtrabajador, idsucursal, fecha, titulo, contenido, estado, idgerente, fecha_revision, comentario_gerente) VALUES (7, 7, '2026-09-30 17:00:00', 'Reporte de mermas - S021 - Departures Lobby - Shop-In-Shop 2', 'Resumen semanal de S021 - Departures Lobby - Shop-In-Shop 2. Sin mermas registradas en la muestra. Se recomienda mantener el nivel actual de pedido y vigilar los lotes proximos a caducar.', 'enviado', NULL, NULL, NULL);
INSERT INTO reporte (idtrabajador, idsucursal, fecha, titulo, contenido, estado, idgerente, fecha_revision, comentario_gerente) VALUES (10, 8, '2026-09-30 17:00:00', 'Reporte de mermas - S022 - Terminal A - Shop-In-Shop 1', 'Resumen semanal de mermas de S022 - Terminal A - Shop-In-Shop 1. Merma registrada en la muestra: $5.44 USD, principalmente por caducidad. Recomendacion: reducir el pedido de los productos con mayor vencimiento y revisar los lotes proximos a caducar.', 'revisado', 11, '2026-10-01 09:30:00', 'Revisado, aplicar ajuste de pedido.');
INSERT INTO reporte (idtrabajador, idsucursal, fecha, titulo, contenido, estado, idgerente, fecha_revision, comentario_gerente) VALUES (13, 9, '2026-09-30 17:00:00', 'Reporte de mermas - S023 - Gate Area East - Full Counter 2', 'Resumen semanal de mermas de S023 - Gate Area East - Full Counter 2. Merma registrada en la muestra: $19.46 USD, principalmente por caducidad. Recomendacion: reducir el pedido de los productos con mayor vencimiento y revisar los lotes proximos a caducar.', 'borrador', NULL, NULL, NULL);
INSERT INTO reporte (idtrabajador, idsucursal, fecha, titulo, contenido, estado, idgerente, fecha_revision, comentario_gerente) VALUES (10, 10, '2026-09-30 17:00:00', 'Reporte de mermas - S027 - Post-Security - Shop-In-Shop 2', 'Resumen semanal de S027 - Post-Security - Shop-In-Shop 2. Sin mermas registradas en la muestra. Se recomienda mantener el nivel actual de pedido y vigilar los lotes proximos a caducar.', 'enviado', NULL, NULL, NULL);
INSERT INTO reporte (idtrabajador, idsucursal, fecha, titulo, contenido, estado, idgerente, fecha_revision, comentario_gerente) VALUES (4, 11, '2026-09-30 17:00:00', 'Reporte de mermas - S028 - Food Court - Full Counter 1  ', 'Resumen semanal de mermas de S028 - Food Court - Full Counter 1  . Merma registrada en la muestra: $8.64 USD, principalmente por caducidad. Recomendacion: reducir el pedido de los productos con mayor vencimiento y revisar los lotes proximos a caducar.', 'revisado', 5, '2026-10-01 09:30:00', 'Revisado, aplicar ajuste de pedido.');
INSERT INTO reporte (idtrabajador, idsucursal, fecha, titulo, contenido, estado, idgerente, fecha_revision, comentario_gerente) VALUES (7, 12, '2026-09-30 17:00:00', 'Reporte de mermas - S030 - Gate Area West - Shop-In-Shop 1', 'Resumen semanal de mermas de S030 - Gate Area West - Shop-In-Shop 1. Merma registrada en la muestra: $25.02 USD, principalmente por caducidad. Recomendacion: reducir el pedido de los productos con mayor vencimiento y revisar los lotes proximos a caducar.', 'borrador', NULL, NULL, NULL);
INSERT INTO reporte (idtrabajador, idsucursal, fecha, titulo, contenido, estado, idgerente, fecha_revision, comentario_gerente) VALUES (13, 13, '2026-09-30 17:00:00', 'Reporte de mermas - S033 - Gate Area West - Express Kiosk 1', 'Resumen semanal de mermas de S033 - Gate Area West - Express Kiosk 1. Merma registrada en la muestra: $1.26 USD, principalmente por caducidad. Recomendacion: reducir el pedido de los productos con mayor vencimiento y revisar los lotes proximos a caducar.', 'enviado', NULL, NULL, NULL);
INSERT INTO reporte (idtrabajador, idsucursal, fecha, titulo, contenido, estado, idgerente, fecha_revision, comentario_gerente) VALUES (13, 14, '2026-09-30 17:00:00', 'Reporte de mermas - S034 - Gate Area East - Full Counter 1', 'Resumen semanal de S034 - Gate Area East - Full Counter 1. Sin mermas registradas en la muestra. Se recomienda mantener el nivel actual de pedido y vigilar los lotes proximos a caducar.', 'revisado', 14, '2026-10-01 09:30:00', 'Revisado, aplicar ajuste de pedido.');
INSERT INTO reporte (idtrabajador, idsucursal, fecha, titulo, contenido, estado, idgerente, fecha_revision, comentario_gerente) VALUES (1, 15, '2026-09-30 17:00:00', 'Reporte de mermas - S035 - Main Concourse - Express Kiosk 1 ', 'Resumen semanal de mermas de S035 - Main Concourse - Express Kiosk 1  . Merma registrada en la muestra: $3.09 USD, principalmente por caducidad. Recomendacion: reducir el pedido de los productos con mayor vencimiento y revisar los lotes proximos a caducar.', 'borrador', NULL, NULL, NULL);

-- ---------------------------------------------------------------
-- inventario_diario
-- Filas reales de inventory_daily (dias con merma y recientes).
-- ---------------------------------------------------------------
INSERT INTO inventario_diario (idsucursal, idproducto, fecha, cantidad_apertura, recibida, vendida, expirada, danada, cantidad_cierre, en_pedido, horas_quiebre) VALUES (3, 13, '2026-09-27', 24, 24, 16, 8, 3, 21, 24, 0.0);
INSERT INTO inventario_diario (idsucursal, idproducto, fecha, cantidad_apertura, recibida, vendida, expirada, danada, cantidad_cierre, en_pedido, horas_quiebre) VALUES (15, 11, '2026-09-30', 8, 0, 7, 1, 0, 0, 0, 0.0);
INSERT INTO inventario_diario (idsucursal, idproducto, fecha, cantidad_apertura, recibida, vendida, expirada, danada, cantidad_cierre, en_pedido, horas_quiebre) VALUES (8, 13, '2026-09-23', 12, 12, 9, 3, 1, 11, 12, 0.0);
INSERT INTO inventario_diario (idsucursal, idproducto, fecha, cantidad_apertura, recibida, vendida, expirada, danada, cantidad_cierre, en_pedido, horas_quiebre) VALUES (11, 9, '2026-09-20', 12, 12, 8, 4, 1, 11, 12, 0.0);
INSERT INTO inventario_diario (idsucursal, idproducto, fecha, cantidad_apertura, recibida, vendida, expirada, danada, cantidad_cierre, en_pedido, horas_quiebre) VALUES (11, 13, '2026-09-30', 23, 36, 22, 1, 3, 33, 0, 0.0);
INSERT INTO inventario_diario (idsucursal, idproducto, fecha, cantidad_apertura, recibida, vendida, expirada, danada, cantidad_cierre, en_pedido, horas_quiebre) VALUES (12, 2, '2026-09-30', 0, 12, 3, 9, 0, 0, 0, 0.0);
INSERT INTO inventario_diario (idsucursal, idproducto, fecha, cantidad_apertura, recibida, vendida, expirada, danada, cantidad_cierre, en_pedido, horas_quiebre) VALUES (13, 5, '2026-09-30', 0, 12, 5, 7, 0, 0, 0, 0.0);
INSERT INTO inventario_diario (idsucursal, idproducto, fecha, cantidad_apertura, recibida, vendida, expirada, danada, cantidad_cierre, en_pedido, horas_quiebre) VALUES (6, 10, '2026-09-30', 12, 0, 2, 10, 0, 0, 0, 0.0);
INSERT INTO inventario_diario (idsucursal, idproducto, fecha, cantidad_apertura, recibida, vendida, expirada, danada, cantidad_cierre, en_pedido, horas_quiebre) VALUES (8, 10, '2026-09-26', 4, 12, 3, 1, 1, 11, 0, 0.0);
INSERT INTO inventario_diario (idsucursal, idproducto, fecha, cantidad_apertura, recibida, vendida, expirada, danada, cantidad_cierre, en_pedido, horas_quiebre) VALUES (9, 2, '2026-09-30', 0, 12, 5, 7, 0, 0, 0, 0.0);
INSERT INTO inventario_diario (idsucursal, idproducto, fecha, cantidad_apertura, recibida, vendida, expirada, danada, cantidad_cierre, en_pedido, horas_quiebre) VALUES (5, 10, '2026-09-30', 24, 12, 21, 3, 0, 12, 0, 0.0);
INSERT INTO inventario_diario (idsucursal, idproducto, fecha, cantidad_apertura, recibida, vendida, expirada, danada, cantidad_cierre, en_pedido, horas_quiebre) VALUES (11, 10, '2026-09-27', 21, 12, 15, 6, 0, 12, 24, 0.0);
INSERT INTO inventario_diario (idsucursal, idproducto, fecha, cantidad_apertura, recibida, vendida, expirada, danada, cantidad_cierre, en_pedido, horas_quiebre) VALUES (10, 2, '2026-09-29', 0, 12, 1, 11, 0, 0, 12, 0.0);
INSERT INTO inventario_diario (idsucursal, idproducto, fecha, cantidad_apertura, recibida, vendida, expirada, danada, cantidad_cierre, en_pedido, horas_quiebre) VALUES (2, 3, '2026-09-29', 0, 12, 3, 9, 0, 0, 12, 0.0);
INSERT INTO inventario_diario (idsucursal, idproducto, fecha, cantidad_apertura, recibida, vendida, expirada, danada, cantidad_cierre, en_pedido, horas_quiebre) VALUES (12, 11, '2026-09-25', 9, 0, 3, 6, 0, 0, 12, 0.0);

GO
PRINT 'Datos de prueba cargados (15 por tabla).';
GO
