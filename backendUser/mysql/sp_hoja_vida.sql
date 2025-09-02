-- ===================================================
-- Procedimiento: Reporte tiempo de experiencia
-- ===================================================

DROP PROCEDURE IF EXISTS reporte_tiempo_experiencia;

DELIMITER $$

CREATE PROCEDURE reporte_tiempo_experiencia(IN p_numero_documento VARCHAR(255))
BEGIN
  DECLARE v_persona_id INT DEFAULT NULL;
  
  -- Handler para errores SQL
  DECLARE EXIT HANDLER FOR SQLEXCEPTION
  BEGIN
    GET DIAGNOSTICS CONDITION 1
      @sqlstate = RETURNED_SQLSTATE,
      @errno = MYSQL_ERRNO,
      @text = MESSAGE_TEXT;
    RESIGNAL;
  END;

  -- Buscar la persona
  SELECT persona_id INTO v_persona_id
  FROM persona
  WHERE numero_documento = p_numero_documento
  LIMIT 1;

  -- Validar que existe la persona
  IF v_persona_id IS NULL THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = CONCAT('No existe persona con documento: ', p_numero_documento);
  END IF;

  -- Consulta principal
  WITH base AS (
    SELECT
      CASE
        WHEN sector = 'PUBLICA' THEN 'SERVIDOR PÚBLICO'
        WHEN (empresa LIKE '%independient%' OR empresa LIKE '%freelan%'
              OR cargo_contrato LIKE '%independient%' OR cargo_contrato LIKE '%servicio%')
          THEN 'TRABAJADOR INDEPENDIENTE'
        ELSE 'EMPLEADO DEL SECTOR PRIVADO'
      END AS categoria,
      GREATEST(fecha_ingreso, DATE('1900-01-01')) AS ini,
      LEAST(COALESCE(fecha_retiro, CURDATE()), CURDATE()) AS fin
    FROM experiencia_laboral
    WHERE persona_id = v_persona_id
      AND fecha_ingreso IS NOT NULL
  ),
  rangos AS (
    SELECT categoria, ini, fin
    FROM base
    WHERE fin >= ini
  ),
  orden AS (
    SELECT
      categoria, ini, fin,
      CASE
        WHEN LAG(fin) OVER (PARTITION BY categoria ORDER BY ini) >= ini THEN 0
        ELSE 1
      END AS nueva_isla
    FROM rangos
  ),
  islas AS (
    SELECT
      categoria, ini, fin,
      SUM(nueva_isla) OVER (
        PARTITION BY categoria
        ORDER BY ini
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
      ) AS grp
    FROM orden
  ),
  colapsado AS (
    SELECT categoria, MIN(ini) AS ini, MAX(fin) AS fin
    FROM islas
    GROUP BY categoria, grp
  ),
  meses_categoria AS (
    SELECT
      categoria,
      COALESCE(SUM(TIMESTAMPDIFF(MONTH, ini, fin)), 0) AS total_meses
    FROM colapsado
    GROUP BY categoria
  ),
  detalle AS (
    SELECT 'SERVIDOR PÚBLICO' AS categoria,
           COALESCE((SELECT total_meses FROM meses_categoria WHERE categoria='SERVIDOR PÚBLICO'), 0) AS total_meses
    UNION ALL
    SELECT 'EMPLEADO DEL SECTOR PRIVADO',
           COALESCE((SELECT total_meses FROM meses_categoria WHERE categoria='EMPLEADO DEL SECTOR PRIVADO'), 0)
    UNION ALL
    SELECT 'TRABAJADOR INDEPENDIENTE',
           COALESCE((SELECT total_meses FROM meses_categoria WHERE categoria='TRABAJADOR INDEPENDIENTE'), 0)
  ),
  totales AS (
    SELECT 'TOTAL TIEMPO EXPERIENCIA' AS categoria,
           COALESCE(SUM(total_meses), 0) AS total_meses
    FROM detalle
  )
  SELECT
    s.categoria AS ocupacion,
    FLOOR(s.total_meses / 12) AS anios,
    (s.total_meses % 12) AS meses
  FROM (
    SELECT * FROM detalle
    UNION ALL
    SELECT * FROM totales
  ) AS s
  ORDER BY FIELD(
    s.categoria,
    'SERVIDOR PÚBLICO',
    'EMPLEADO DEL SECTOR PRIVADO',
    'TRABAJADOR INDEPENDIENTE',
    'TOTAL TIEMPO EXPERIENCIA'
  );
END$$

DELIMITER ;

-- =========================================
-- FIN DEL SCRIPT
-- =========================================