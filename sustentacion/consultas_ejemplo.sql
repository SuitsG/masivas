-- ====================================================================
-- CONSULTAS DE EJEMPLO - Base de Datos Recursos Humanos (BDRH)
-- ====================================================================
-- Este archivo contiene consultas de ejemplo para explorar la base de datos

-- ====================================================================
-- 1. CONSULTAS BÁSICAS DE EXPLORACIÓN
-- ====================================================================

-- Ver todas las tablas disponibles
SHOW TABLES;

-- Ver la estructura de la tabla principal de empleados
DESCRIBE empleados;

-- Ver la estructura de la vista personalizada
DESCRIBE vw_empleados_detalle;

-- Contar el total de registros en cada tabla
SELECT 'empleados' as tabla, COUNT(*) as total FROM empleados
UNION ALL
SELECT 'departamentos', COUNT(*) FROM departamentos
UNION ALL
SELECT 'trabajos', COUNT(*) FROM trabajos
UNION ALL
SELECT 'ubicaciones', COUNT(*) FROM ubicaciones;

-- ====================================================================
-- 2. CONSULTAS DE EMPLEADOS
-- ====================================================================

-- Top 10 empleados con mayor salario
SELECT nombres, apellidos, salario, fecha_ingreso
FROM empleados
ORDER BY salario DESC
LIMIT 10;

-- Empleados contratados en los últimos 5 años
SELECT nombres, apellidos, fecha_ingreso, 
       DATEDIFF(CURDATE(), fecha_ingreso) / 365 as años_antiguedad
FROM empleados
WHERE fecha_ingreso >= DATE_SUB(CURDATE(), INTERVAL 5 YEAR)
ORDER BY fecha_ingreso DESC;

-- Salario promedio por departamento
SELECT d.departamento_nombre, 
       COUNT(e.empleado_id) as total_empleados,
       AVG(e.salario) as salario_promedio,
       MIN(e.salario) as salario_minimo,
       MAX(e.salario) as salario_maximo
FROM empleados e
JOIN departamentos d ON e.departamento_id = d.departamento_id
GROUP BY d.departamento_nombre
ORDER BY salario_promedio DESC;

-- ====================================================================
-- 3. USANDO LA VISTA PERSONALIZADA
-- ====================================================================

-- Empleados del departamento IT con información completa
SELECT nombre_completo, trabajo_nombre, salario, ciudad, pais_nombre
FROM vw_empleados_detalle 
WHERE departamento_nombre = 'IT'
ORDER BY salario DESC;

-- Empleados por región geográfica
SELECT region_nombre, 
       COUNT(*) as total_empleados,
       AVG(salario) as salario_promedio
FROM vw_empleados_detalle 
GROUP BY region_nombre
ORDER BY total_empleados DESC;

-- Empleados con más de 10 años de antigüedad
SELECT nombre_completo, departamento_nombre, antiguedad_anios, salario
FROM vw_empleados_detalle 
WHERE antiguedad_anios > 10
ORDER BY antiguedad_anios DESC;

-- ====================================================================
-- 4. CONSULTAS AVANZADAS CON JOINS
-- ====================================================================

-- Jerarquía organizacional: empleados y sus jefes
SELECT 
    CONCAT(emp.nombres, ' ', emp.apellidos) as empleado,
    CONCAT(jefe.nombres, ' ', jefe.apellidos) as jefe,
    d.departamento_nombre
FROM empleados emp
LEFT JOIN empleados jefe ON emp.gerencia_id = jefe.empleado_id
LEFT JOIN departamentos d ON emp.departamento_id = d.departamento_id
ORDER BY d.departamento_nombre, jefe.nombres;

-- Empleados con sus dependientes
SELECT 
    CONCAT(e.nombres, ' ', e.apellidos) as empleado,
    COUNT(dep.dependiente_id) as num_dependientes
FROM empleados e
LEFT JOIN dependientes dep ON e.empleado_id = dep.empleado_id
GROUP BY e.empleado_id, e.nombres, e.apellidos
HAVING num_dependientes > 0
ORDER BY num_dependientes DESC;

-- ====================================================================
-- 5. CONSULTAS DE ANÁLISIS DE UBICACIONES
-- ====================================================================

-- Distribución de empleados por ciudad
SELECT 
    u.ciudad,
    p.pais_nombre,
    COUNT(e.empleado_id) as total_empleados
FROM ubicaciones u
JOIN departamentos d ON u.ubicacion_id = d.ubicacion_id
JOIN empleados e ON d.departamento_id = e.departamento_id
JOIN paises p ON u.pais_id = p.pais_id
GROUP BY u.ciudad, p.pais_nombre
ORDER BY total_empleados DESC;

-- ====================================================================
-- 6. PROCEDIMIENTOS ALMACENADOS
-- ====================================================================

-- Llamar al procedimiento para obtener empleados por departamento
CALL sp_empleados_por_departamento('IT');
CALL sp_empleados_por_departamento('Sales');

-- Ver todos los procedimientos disponibles
SHOW PROCEDURE STATUS WHERE Db = 'bdrh';

-- ====================================================================
-- 7. TRIGGERS Y AUDITORÍA
-- ====================================================================

-- Ver todos los triggers
SHOW TRIGGERS;

-- Ver cambios recientes de salario (tabla de auditoría)
SELECT * FROM cambios_salario 
ORDER BY fecha_cambio DESC 
LIMIT 10;

-- Actualizar un salario para probar el trigger
-- UPDATE empleados SET salario = salario * 1.1 WHERE empleado_id = 100;

-- ====================================================================
-- 8. EVENTOS PROGRAMADOS
-- ====================================================================

-- Ver eventos activos
SHOW EVENTS;

-- Ver tabla de resumen generada por eventos
SELECT * FROM resumen_salarios_mensual 
ORDER BY año DESC, mes DESC 
LIMIT 5;

-- ====================================================================
-- 9. CONSULTAS DE RENDIMIENTO CON ÍNDICES
-- ====================================================================

-- Ver índices en la tabla empleados
SHOW INDEX FROM empleados;

-- Buscar empleados por email (usa índice único)
SELECT nombres, apellidos, email 
FROM empleados 
WHERE email = 'SKING@company.com';

-- Buscar empleados por departamento (usa índice foreign key)
SELECT COUNT(*) as total 
FROM empleados 
WHERE departamento_id = 6;

-- ====================================================================
-- 10. CONSULTAS DE ESTADÍSTICAS GENERALES
-- ====================================================================

-- Resumen general de la empresa
SELECT 
    (SELECT COUNT(*) FROM empleados) as total_empleados,
    (SELECT COUNT(*) FROM departamentos) as total_departamentos,
    (SELECT COUNT(DISTINCT pais_id) FROM ubicaciones) as paises_operacion,
    (SELECT ROUND(AVG(salario), 2) FROM empleados) as salario_promedio_general,
    (SELECT COUNT(*) FROM dependientes) as total_dependientes;

-- Rango salarial por trabajo
SELECT 
    t.trabajo_nombre,
    COUNT(e.empleado_id) as empleados,
    MIN(e.salario) as salario_min,
    MAX(e.salario) as salario_max,
    AVG(e.salario) as salario_promedio
FROM trabajos t
LEFT JOIN empleados e ON t.trabajo_id = e.trabajo_id
GROUP BY t.trabajo_id, t.trabajo_nombre
ORDER BY salario_promedio DESC;

-- ====================================================================
-- NOTA: Para ejecutar estas consultas, conéctate a la base de datos:
-- mysql -h 127.0.0.1 -P 3307 -u root -p
-- Contraseña: admin
-- 
-- Luego ejecuta: USE bdrh;
-- ====================================================================
