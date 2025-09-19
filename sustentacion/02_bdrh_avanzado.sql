-- ===============================================================
-- Taller SQL Avanzado - BDR-RH (Recursos Humanos)
-- Entrega: archivo .sql debidamente documentado con:
--  1) Vista
--  2) Índice(s)
--  3) Procedimiento almacenado
--  4) Disparador (Trigger)
--  5) Evento (Event Scheduler)
--
-- NOTAS IMPORTANTES
-- - Ejecute primero el script base de la BDR-RH (tablas y datos).
-- - Este script asume MySQL 8.x.
-- - Para eventos, habilite el planificador si su servidor lo permite:
--     SET GLOBAL event_scheduler = ON;   -- (Requiere privilegios)
-- - Use 'USE bdrh;' para trabajar sobre el esquema de la BDR-RH.
-- ===============================================================

/* ================================
   PREPARACIÓN
   ================================ */
-- Usar el esquema principal del taller (asegúrese de haberlo creado con el script base)
USE bdrh;

-- (Opcional) Modo seguro
SET SESSION sql_safe_updates = 0;

/* ================================
   1) VISTA: vw_empleados_detalle
   Descripción:
     Vista que muestra información consolidada de empleados junto con
     su trabajo, departamento, ubicación, país y región.
   Propósito:
     - Simplificar reportes para RRHH.
     - Evitar reescritura de JOINs complejos.
   ================================ */

-- Eliminar la vista si existe para permitir recrearla sin errores
DROP VIEW IF EXISTS vw_empleados_detalle;

CREATE VIEW vw_empleados_detalle AS
SELECT
    e.empleado_id,
    CONCAT(e.nombres, ' ', e.apellidos) AS nombre_completo,
    e.email,
    e.numero_telefono,
    e.fecha_ingreso,
    TIMESTAMPDIFF(YEAR, e.fecha_ingreso, CURDATE()) AS antiguedad_anios,
    t.trabajo_nombre,
    d.departamento_nombre,
    u.ciudad,
    p.pais_nombre,
    r.region_nombre,
    e.salario
FROM empleados e
JOIN trabajos       t ON t.trabajo_id      = e.trabajo_id
LEFT JOIN departamentos d ON d.departamento_id = e.departamento_id
LEFT JOIN ubicaciones   u ON u.ubicacion_id   = d.ubicacion_id
LEFT JOIN paises        p ON p.pais_id        = u.pais_id
LEFT JOIN regiones      r ON r.region_id      = p.region_id
ORDER BY e.nombres, e.apellidos;

-- Ejemplo de uso:
-- SELECT * FROM vw_empleados_detalle WHERE departamento_nombre = 'IT';

/* ================================
   2) ÍNDICES
   Justificación:
     - Aceleran búsquedas y JOINs frecuentes.
     - Unique en email evita duplicados y mejora calidad de datos.
   Advertencia:
     - Los índices aceleran SELECT pero añaden costo a INSERT/UPDATE/DELETE.
   ================================ */

-- 2.1. Índice único sobre el correo electrónico
-- (Primero lo eliminamos si existiera con otro tipo)
DROP INDEX IF EXISTS ux_empleados_email ON empleados;
CREATE UNIQUE INDEX ux_empleados_email ON empleados(email);

-- 2.2. Índice compuesto por departamento y trabajo para consultas analíticas
DROP INDEX IF EXISTS ix_empleados_depto_trabajo ON empleados;
CREATE INDEX ix_empleados_depto_trabajo ON empleados(departamento_id, trabajo_id);

-- 2.3. Índice de apoyo al FK (si no existiera) en departamentos(ubicacion_id)
DROP INDEX IF EXISTS ix_departamentos_ubicacion ON departamentos;
CREATE INDEX ix_departamentos_ubicacion ON departamentos(ubicacion_id);

-- Verificación rápida de índices:
-- SHOW INDEX FROM empleados;
-- SHOW INDEX FROM departamentos;

/* ================================
   3) PROCEDIMIENTO ALMACENADO: sp_aumentar_salario_departamento
   Funcionalidad:
     Aumenta el salario de TODOS los empleados de un departamento en un porcentaje dado.
     El nuevo salario se encaja dentro de [salario_min, salario_max] de su trabajo.
   Parámetros:
     IN  p_departamento_id INT       -> departamento objetivo
     IN  p_porcentaje      DECIMAL   -> porcentaje de aumento (ej: 5 para +5%)
     OUT p_filas           INT       -> filas realmente afectadas
   Manejo de errores:
     Usa transacción y handler para revertir ante excepciones.
   ================================ */

DROP PROCEDURE IF EXISTS sp_aumentar_salario_departamento;
DELIMITER //

CREATE PROCEDURE sp_aumentar_salario_departamento(
    IN  p_departamento_id INT,
    IN  p_porcentaje      DECIMAL(6,2),
    OUT p_filas           INT
)
BEGIN
    DECLARE exit handler FOR SQLEXCEPTION
    BEGIN
        -- Ante error, revertimos y propagamos filas afectadas como NULL
        ROLLBACK;
        SET p_filas = NULL;
    END;

    START TRANSACTION;

    -- Actualizamos salarios con tope mínimo/máximo según el trabajo
    UPDATE empleados e
    JOIN trabajos  t ON t.trabajo_id = e.trabajo_id
    SET e.salario = LEAST(
                      GREATEST(e.salario * (1 + (p_porcentaje/100)), t.salario_min),
                      t.salario_max
                    )
    WHERE e.departamento_id = p_departamento_id;

    -- Filas realmente afectadas (es decir, con cambio)
    SET p_filas = ROW_COUNT();

    COMMIT;
END //

DELIMITER ;

-- Ejemplo de ejecución:
-- SET @filas = 0;
-- CALL sp_aumentar_salario_departamento(6, 5.00, @filas);
-- SELECT @filas AS filas_actualizadas;

/* ================================
   4) DISPARADOR (TRIGGER): trg_empleados_audit_salario
   Propósito:
     Registrar todo cambio de salario en una tabla de auditoría.
   Tabla de auditoría:
     cambios_salario(empleado_id, cambiado_en, antiguo_salario, nuevo_salario)
   Momento/EVENTO:
     BEFORE UPDATE en empleados
   ================================ */

-- Tabla de auditoría (si no existe)
CREATE TABLE IF NOT EXISTS cambios_salario(
    empleado_id     INT NOT NULL,
    cambiado_en     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    antiguo_salario DECIMAL(8,2),
    nuevo_salario   DECIMAL(8,2),
    PRIMARY KEY (empleado_id, cambiado_en)
);

-- Eliminar el trigger si existe
DROP TRIGGER IF EXISTS trg_empleados_audit_salario;
DELIMITER //

CREATE TRIGGER trg_empleados_audit_salario
BEFORE UPDATE ON empleados
FOR EACH ROW
BEGIN
    IF NEW.salario <> OLD.salario THEN
        INSERT INTO cambios_salario(empleado_id, antiguo_salario, nuevo_salario)
        VALUES (OLD.empleado_id, OLD.salario, NEW.salario);
    END IF;
END //

DELIMITER ;

-- Prueba breve:
-- UPDATE empleados SET salario = salario * 1.03 WHERE empleado_id = 110;
-- SELECT * FROM cambios_salario WHERE empleado_id = 110 ORDER BY cambiado_en DESC;

/* ================================
   5) EVENTO (EVENT SCHEDULER): ev_resumen_salarios_mensual
   Propósito:
     Generar mensualmente un resumen de salarios por departamento.
   Tabla destino:
     resumen_salarios_mensual(periodo, departamento_id, departamento_nombre, promedio_salario, total_empleados)
   Frecuencia:
     Cada 1 mes, iniciando en el próximo minuto desde su creación (ajuste si desea).
   Requisitos:
     SET GLOBAL event_scheduler = ON;
   ================================ */

-- Tabla de resumen (si no existe)
CREATE TABLE IF NOT EXISTS resumen_salarios_mensual(
    periodo DATE NOT NULL,
    departamento_id INT NOT NULL,
    departamento_nombre VARCHAR(30) NOT NULL,
    promedio_salario DECIMAL(10,2) NOT NULL,
    total_empleados INT NOT NULL,
    PRIMARY KEY (periodo, departamento_id)
);

-- Borramos el evento si existiera
DROP EVENT IF EXISTS ev_resumen_salarios_mensual;
DELIMITER //

CREATE EVENT ev_resumen_salarios_mensual
    ON SCHEDULE EVERY 1 MONTH
    STARTS CURRENT_TIMESTAMP + INTERVAL 1 MINUTE  -- Ajuste si prefiere el 1 de cada mes a determinada hora
    DO
BEGIN
    -- El periodo se registrará como el primer día del mes en curso
    INSERT INTO resumen_salarios_mensual (periodo, departamento_id, departamento_nombre, promedio_salario, total_empleados)
    SELECT
        DATE_FORMAT(CURRENT_DATE, '%Y-%m-01') AS periodo,
        d.departamento_id,
        d.departamento_nombre,
        ROUND(AVG(e.salario), 2) AS promedio_salario,
        COUNT(*) AS total_empleados
    FROM empleados e
    JOIN departamentos d ON d.departamento_id = e.departamento_id
    GROUP BY d.departamento_id, d.departamento_nombre
    ON DUPLICATE KEY UPDATE
        promedio_salario = VALUES(promedio_salario),
        total_empleados  = VALUES(total_empleados);
END //

DELIMITER ;

-- Comprobaciones útiles:
-- SHOW EVENTS WHERE Db = 'bdrh';
-- SELECT * FROM resumen_salarios_mensual ORDER BY periodo DESC, departamento_id;

/* ================================
   FIN DEL SCRIPT
   ================================ */
