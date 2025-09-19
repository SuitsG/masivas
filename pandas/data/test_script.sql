-- Script SQL de prueba con creación y uso de base de datos
-- Usar las mismas credenciales: admin/admin123 puerto 4001

-- Crear base de datos de prueba
CREATE DATABASE IF NOT EXISTS test_db;

-- Usar la base de datos
USE test_db;

-- Crear tabla de ejemplo
CREATE TABLE IF NOT EXISTS empleados (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100),
    departamento VARCHAR(50),
    salario DECIMAL(10,2),
    fecha_ingreso DATE
);

-- Insertar datos de ejemplo
INSERT INTO empleados (nombre, departamento, salario, fecha_ingreso) VALUES
('Juan Pérez', 'IT', 75000.00, '2023-01-15'),
('María García', 'RRHH', 65000.00, '2023-02-20'),
('Carlos López', 'Ventas', 55000.00, '2023-03-10'),
('Ana Martínez', 'IT', 80000.00, '2023-04-05'),
('Luis Rodríguez', 'Finanzas', 70000.00, '2023-05-12');

-- Consulta de verificación
SELECT 'Tabla empleados creada y datos insertados' as resultado;

-- Mostrar los datos insertados
SELECT * FROM empleados;
