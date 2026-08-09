CREATE DATABASE IF NOT EXISTS pos_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE pos_db;

CREATE TABLE IF NOT EXISTS categorias (
    id_categoria INT AUTO_INCREMENT PRIMARY KEY,
    nombre_categoria VARCHAR(100) NOT NULL UNIQUE,
    descripcion VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS producto (
    id_producto INT AUTO_INCREMENT PRIMARY KEY,
    id_categoria INT NOT NULL,
    codigo_barra VARCHAR(50) NOT NULL UNIQUE,
    nombre_producto VARCHAR(150) NOT NULL,
    precio_compra DECIMAL(10,2) NOT NULL,
    precio_venta DECIMAL(10,2) NOT NULL,
    stock_actual INT NOT NULL DEFAULT 0,
    stock_minimo INT NOT NULL DEFAULT 5,
    CONSTRAINT fk_producto_categoria FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria),
    CONSTRAINT chk_producto_precios CHECK (precio_compra >= 0 AND precio_venta >= 0),
    CONSTRAINT chk_producto_stock CHECK (stock_actual >= 0)
);

CREATE TABLE IF NOT EXISTS clientes (
    id_cliente INT AUTO_INCREMENT PRIMARY KEY,
    nombre_cliente VARCHAR(150) NOT NULL,
    dni VARCHAR(20) UNIQUE,
    telefono VARCHAR(20),
    direccion VARCHAR(200)
);

CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre_usuario VARCHAR(50) NOT NULL UNIQUE,
    contrasena VARCHAR(255) NOT NULL,
    rol VARCHAR(20) NOT NULL
);

CREATE TABLE IF NOT EXISTS proveedores (
    id_proveedor INT AUTO_INCREMENT PRIMARY KEY,
    nombre_empresa VARCHAR(150) NOT NULL,
    telefono VARCHAR(20),
    rtn VARCHAR(30) UNIQUE,
    contacto VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS facturas (
    id_factura INT AUTO_INCREMENT PRIMARY KEY,
    id_cliente INT NOT NULL,
    id_usuario INT NOT NULL,
    numero_factura VARCHAR(50) NOT NULL UNIQUE,
    fecha DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    subtotal DECIMAL(10,2) NOT NULL,
    impuesto DECIMAL(10,2) NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    CONSTRAINT fk_factura_cliente FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
    CONSTRAINT fk_factura_usuario FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);

CREATE TABLE IF NOT EXISTS detalle_factura (
    id_detalle_factura INT AUTO_INCREMENT PRIMARY KEY,
    id_factura INT NOT NULL,
    id_producto INT NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    CONSTRAINT fk_detalle_factura FOREIGN KEY (id_factura) REFERENCES facturas(id_factura) ON DELETE CASCADE,
    CONSTRAINT fk_detalle_factura_producto FOREIGN KEY (id_producto) REFERENCES producto(id_producto),
    CONSTRAINT chk_detalle_factura_cantidad CHECK (cantidad > 0)
);

CREATE TABLE IF NOT EXISTS compras (
    id_compra INT AUTO_INCREMENT PRIMARY KEY,
    id_proveedor INT NOT NULL,
    id_usuario INT NOT NULL,
    numero_referencia VARCHAR(50) NOT NULL,
    fecha DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    total DECIMAL(10,2) NOT NULL,
    CONSTRAINT uq_compra_referencia UNIQUE (id_proveedor, numero_referencia),
    CONSTRAINT fk_compra_proveedor FOREIGN KEY (id_proveedor) REFERENCES proveedores(id_proveedor),
    CONSTRAINT fk_compra_usuario FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);

CREATE TABLE IF NOT EXISTS detalle_compras (
    id_detalle_compra INT AUTO_INCREMENT PRIMARY KEY,
    id_compra INT NOT NULL,
    id_producto INT NOT NULL,
    cantidad INT NOT NULL,
    costo_unitario DECIMAL(10,2) NOT NULL,
    CONSTRAINT fk_detalle_compra FOREIGN KEY (id_compra) REFERENCES compras(id_compra) ON DELETE CASCADE,
    CONSTRAINT fk_detalle_compra_producto FOREIGN KEY (id_producto) REFERENCES producto(id_producto),
    CONSTRAINT chk_detalle_compra_cantidad CHECK (cantidad > 0)
);

INSERT IGNORE INTO categorias (id_categoria, nombre_categoria, descripcion) VALUES (1, 'General', 'Categoría general');
INSERT IGNORE INTO clientes (id_cliente, nombre_cliente, dni, telefono, direccion) VALUES (1, 'Cliente General', '0000000000000', '00000000', 'Ciudad');
INSERT IGNORE INTO usuarios (id_usuario, nombre_usuario, contrasena, rol) VALUES (1, 'admin', 'admin123', 'Administrador');
INSERT IGNORE INTO proveedores (id_proveedor, nombre_empresa, telefono, rtn, contacto) VALUES (1, 'Proveedor General', '00000000', '00000000000000', 'Contacto General');
INSERT IGNORE INTO producto (id_categoria, codigo_barra, nombre_producto, precio_compra, precio_venta, stock_actual, stock_minimo) VALUES
    (1, '75010001', 'Camiseta Deportiva', 150.00, 250.00, 50, 5),
    (1, '75010002', 'Tachones / Tacos', 500.00, 850.00, 20, 2);
