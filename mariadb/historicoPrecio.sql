SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

CREATE DATABASE IF NOT EXISTS factura_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE factura_db;


CREATE TABLE cliente (
    cliente_id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    documento VARCHAR(20) UNIQUE NOT NULL,
    telefono VARCHAR(20),
    correo VARCHAR(100) UNIQUE,
    direccion VARCHAR(255)
);

CREATE TABLE articulo (
    articulo_id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    categoria VARCHAR(50),
    marca VARCHAR(50)
);

CREATE TABLE historial_precio (
    historial_id INT AUTO_INCREMENT PRIMARY KEY,
    articulo_id INT NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE,
    FOREIGN KEY (articulo_id) REFERENCES articulo(articulo_id)
);

CREATE TABLE factura (
    factura_id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL,
    fecha_factura DATETIME NOT NULL DEFAULT NOW(),
    total DECIMAL(12,2),
    FOREIGN KEY (cliente_id) REFERENCES cliente(cliente_id)
);

CREATE TABLE detalle_factura (
    detalle_id INT AUTO_INCREMENT PRIMARY KEY,
    factura_id INT NOT NULL,
    articulo_id INT NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(12,2) NOT NULL,
    FOREIGN KEY (factura_id) REFERENCES factura(factura_id),
    FOREIGN KEY (articulo_id) REFERENCES articulo(articulo_id)
);


-- Clientes
    INSERT INTO cliente (nombre, apellido, documento, telefono, correo, direccion) VALUES
    ('Laura', 'Gómez', '123456789', '3001234567', 'laura.gomez@example.com', 'Calle 10 #20-30'),
    ('Carlos', 'Pérez', '987654321', '3109876543', 'carlos.perez@example.com', 'Carrera 15 #40-22');

    -- Artículos
    INSERT INTO articulo (nombre, descripcion, categoria, marca) VALUES
    ('Televisor 50"', 'Televisor LED 50 pulgadas 4K UHD', 'Electrodoméstico', 'Samsung'),
    ('Lavadora 20kg', 'Lavadora automática 20kg carga superior', 'Electrodoméstico', 'LG'),
    ('Nevera 400L', 'Nevera no frost 400 litros', 'Electrodoméstico', 'Whirlpool');

    -- Historial de precios
    INSERT INTO historial_precio (articulo_id, precio, fecha_inicio, fecha_fin) VALUES
    (1, 2500000, '2024-01-01', '2024-06-30'),
    (1, 2300000, '2024-07-01', NULL),
    (2, 1800000, '2024-01-01', NULL),
    (3, 3200000, '2024-03-01', NULL);

    -- Facturas
    INSERT INTO factura (cliente_id, total) VALUES
    (1, 4600000),
    (2, 2300000);

    -- Detalle facturas
    INSERT INTO detalle_factura (factura_id, articulo_id, cantidad, precio_unitario, subtotal) VALUES
    (1, 1, 1, 2300000, 2300000),
    (1, 2, 1, 2300000, 2300000),
    (2, 1, 1, 2300000, 2300000);



    /* Consulta permita observar los cambios de precio de venta de un mismo artículo a través del tiempo*/

SELECT 
    a.nombre AS articulo,
    h.precio,
    h.fecha_inicio,
    h.fecha_fin
FROM historial_precio h
JOIN articulo a ON h.articulo_id = a.articulo_id
WHERE a.articulo_id = 1
ORDER BY h.fecha_inicio;



-- procedimiento almacenado para obtener el historial de precios de un artículo
DELIMITER $$;

CREATE PROCEDURE historial_precio(IN p_nombre_articulo VARCHAR(100))
BEGIN
    SELECT 
        a.nombre AS articulo,
        h.precio,
        h.fecha_inicio,
        h.fecha_fin
    FROM historial_precio h
    JOIN articulo a ON h.articulo_id = a.articulo_id
    WHERE a.nombre = p_nombre_articulo 
    ORDER BY h.fecha_inicio;
END$$

DELIMITER ;

CALL historial_precio('Televisor 50"');