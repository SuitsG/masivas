-- =========================================
-- MySQL 8.x
-- =========================================

SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

CREATE DATABASE IF NOT EXISTS hojaVida
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE hojaVida;

-- (En MySQL no se crean tipos ENUM globales con CREATE TYPE;
--  se declaran directamente en las columnas)

-- ===================================================
-- Tablas
-- ===================================================

CREATE TABLE persona (
    persona_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    nombres VARCHAR(100) NOT NULL,
    primer_apellido VARCHAR(50) NOT NULL,
    segundo_apellido VARCHAR(50),
    tipo_documento ENUM('CC','CE','PAS') NOT NULL,
    numero_documento VARCHAR(20) UNIQUE NOT NULL,
    sexo ENUM('M','F') NOT NULL,
    nacionalidad ENUM('COL','EXTRANJERO') NOT NULL,
    pais_nacimiento VARCHAR(50),
    depto_nacimiento VARCHAR(50),
    municipio_nacimiento VARCHAR(50),
    fecha_nacimiento DATE,
    direccion VARCHAR(150),
    pais_residencia VARCHAR(50),
    depto_residencia VARCHAR(50),
    municipio_residencia VARCHAR(50),
    telefono VARCHAR(20),
    email VARCHAR(100)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE distrito_militar (
  distrito_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(10) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE libreta_militar (
  libreta_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  persona_id INT NOT NULL UNIQUE REFERENCES datos_personales(persona_id),
  clase ENUM('Primera','Segunda'),
  numero VARCHAR(20),
  distrito_id INT REFERENCES distrito_militar(distrito_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE idioma (
    idioma_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    persona_id INT NOT NULL REFERENCES datos_personales(persona_id),
    nombre VARCHAR(100) NOT NULL,
    habla ENUM('Regular','Bien','Muy Bien'),
    lee ENUM('Regular','Bien','Muy Bien'),
    escribe ENUM('Regular','Bien','Muy Bien')
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE educacion_basica (
    basica_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    persona_id INT NOT NULL REFERENCES datos_personales(persona_id),
    ultimo_grado_aprobado INT CHECK (ultimo_grado_aprobado BETWEEN 1 AND 11),
    titulo_obtenido VARCHAR(100),
    fecha_grado DATE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE educacion_superior (
    superior_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    persona_id INT NOT NULL REFERENCES datos_personales(persona_id),
    modalidad ENUM('TC','TL','TE','UN','ES','MG','DOC') NOT NULL,
    nombre_estudio VARCHAR(150),
    semestre_aprobado INT,
    graduado BOOLEAN,
    fecha_terminacion DATE,
    numero_tarjeta VARCHAR(50)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE experiencia_laboral (
  id_exp INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  persona_id INT NOT NULL REFERENCES datos_personales(persona_id) ON DELETE CASCADE ON UPDATE CASCADE,
  sector ENUM('PUBLICA','PRIVADA') NOT NULL,
  empresa VARCHAR(200) NOT NULL,
  pais VARCHAR(80),
  departamento VARCHAR(80),
  municipio VARCHAR(80),
  correo_entidad VARCHAR(120),
  telefonos VARCHAR(120),
  fecha_ingreso DATE NOT NULL,
  fecha_retiro DATE,
  cargo_contrato VARCHAR(160),
  dependencia VARCHAR(160),
  direccion_entidad VARCHAR(200),
  es_actual BOOLEAN DEFAULT FALSE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

/* Store Procedures */

DELIMITER $$

CREATE PROCEDURE reporte_tiempo_experiencia(IN p_numero_documento VARCHAR(255))
BEGIN
  DECLARE v_persona_id INT;

  -- Buscar la persona por número de documento
  SELECT persona_id
    INTO v_persona_id
  FROM datos_personales
  WHERE numero_documento = p_numero_documento
  LIMIT 1;

  IF v_persona_id IS NULL THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = CONCAT('No existe persona con documento ', p_numero_documento);
  END IF;

  WITH
  base AS (
    SELECT
      CASE
        WHEN sector = 'PUBLICA' THEN 'SERVIDOR PÚBLICO'
        WHEN (empresa LIKE '%independient%' OR empresa LIKE '%freelan%'
              OR cargo_contrato LIKE '%independient%' OR cargo_contrato LIKE '%servicio%')
          THEN 'TRABAJADOR INDEPENDIENTE'
        ELSE 'EMPLEADO DEL SECTOR PRIVADO'
      END AS categoria,
      GREATEST(fecha_ingreso, '1900-01-01') AS ini,
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



/* insercion de datos */

-- ==============================
-- INSERTS PARA datos_personales
-- ==============================
INSERT INTO datos_personales (nombres, primer_apellido, segundo_apellido, tipo_documento, numero_documento, sexo, nacionalidad, pais_nacimiento, depto_nacimiento, municipio_nacimiento, fecha_nacimiento, direccion, pais_residencia, depto_residencia, municipio_residencia, telefono, email)
VALUES
('Carlos Andrés','Pérez','Gómez','CC','1001001','M','COL','Colombia','Cundinamarca','Bogotá','1990-05-12','Calle 123 #45-67','Colombia','Cundinamarca','Bogotá','3101234567','carlos.perez@email.com'),
('María Fernanda','López','Rodríguez','CC','1001002','F','COL','Colombia','Antioquia','Medellín','1992-08-21','Carrera 12 #34-56','Colombia','Antioquia','Medellín','3152345678','maria.lopez@email.com'),
('Juan Sebastián','Martínez','Suárez','CC','1001003','M','COL','Colombia','Valle','Cali','1985-03-10','Av. 5 #67-89','Colombia','Valle','Cali','3009876543','juan.martinez@email.com'),
('Ana Sofía','Ramírez','Castro','CE','1001004','F','EXTRANJERO','Ecuador','Pichincha','Quito','1995-12-01','Calle Real #12-90','Colombia','Atlántico','Barranquilla','3224567890','ana.ramirez@email.com'),
('David','García','Hernández','PAS','P123456','M','EXTRANJERO','España','Madrid','Madrid','1988-07-15','Calle Mayor 10','Colombia','Santander','Bucaramanga','3011231234','david.garcia@email.com'),
('Laura','Moreno','Jiménez','CC','1001005','F','COL','Colombia','Santander','Bucaramanga','1993-01-22','Cl 45 #12-34','Colombia','Santander','Bucaramanga','3202223344','laura.moreno@email.com'),
('Felipe','Torres','Salazar','CC','1001006','M','COL','Colombia','Caldas','Manizales','1991-09-11','Carrera 67 #11-90','Colombia','Caldas','Manizales','3104445566','felipe.torres@email.com'),
('Camila','Ortega','Ruiz','CE','1001007','F','EXTRANJERO','Perú','Lima','Lima','1997-02-17','Av. Central 50','Colombia','Cundinamarca','Chía','3227778899','camila.ortega@email.com'),
('Andrés','Vargas','Londoño','CC','1001008','M','COL','Colombia','Tolima','Ibagué','1989-04-03','Cl 90 #20-30','Colombia','Tolima','Ibagué','3115556677','andres.vargas@email.com'),
('Natalia','Mejía','Córdoba','CC','1001009','F','COL','Colombia','Risaralda','Pereira','1994-10-19','Carrera 8 #40-22','Colombia','Risaralda','Pereira','3006667788','natalia.mejia@email.com');

INSERT INTO experiencia_laboral (persona_id, sector, empresa, pais, departamento, municipio, correo_entidad, telefonos, fecha_ingreso, fecha_retiro, cargo_contrato, dependencia, direccion_entidad, es_actual) VALUES
(1,'PRIVADA','Nutresa','Colombia','Risaralda','Pereira','empleo@nutresa.com','6063456789','2020-05-01',NULL,'Ingeniera Alimentos','Ingenieria','Cl 33 #14-55',TRUE);

-- ==============================
-- INSERTS PARA libreta_militar
-- ==============================
INSERT INTO libreta_militar (persona_id, clase, numero, distrito_militar) VALUES
(1,'Primera','LM1001','01'),
(3,'Segunda','LM1002','02'),
(5,'Primera','LM1003','03'),
(7,'Segunda','LM1004','04'),
(9,'Primera','LM1005','05'),
(2,'Primera','LM1006','06'),
(4,'Segunda','LM1007','07'),
(6,'Primera','LM1008','08'),
(8,'Segunda','LM1009','09'),
(10,'Primera','LM1010','10');

-- ==============================
-- INSERTS PARA idioma
-- ==============================
INSERT INTO idioma (persona_id, nombre, habla, lee, escribe) VALUES
(1,'Inglés','Bien','Muy Bien','Regular'),
(2,'Francés','Regular','Regular','Regular'),
(3,'Inglés','Muy Bien','Muy Bien','Bien'),
(4,'Alemán','Regular','Bien','Regular'),
(5,'Inglés','Bien','Bien','Bien'),
(6,'Portugués','Muy Bien','Bien','Regular'),
(7,'Inglés','Muy Bien','Muy Bien','Muy Bien'),
(8,'Francés','Bien','Bien','Regular'),
(9,'Inglés','Regular','Bien','Regular'),
(10,'Italiano','Bien','Regular','Regular');

-- ==============================
-- INSERTS PARA educacion_basica
-- ==============================
INSERT INTO educacion_basica (persona_id, ultimo_grado_aprobado, titulo_obtenido, fecha_grado) VALUES
(1,11,'Bachiller Académico','2007-11-30'),
(2,11,'Bachiller Comercial','2009-11-30'),
(3,11,'Bachiller Técnico','2003-11-30'),
(4,10,'Bachiller en Ciencias','2011-11-30'),
(5,11,'Bachiller Académico','2005-11-30'),
(6,11,'Bachiller Técnico','2010-11-30'),
(7,11,'Bachiller Académico','2008-11-30'),
(8,11,'Bachiller Comercial','2013-11-30'),
(9,11,'Bachiller Técnico','2006-11-30'),
(10,11,'Bachiller Académico','2012-11-30');

-- ==============================
-- INSERTS PARA educacion_superior
-- ==============================
INSERT INTO educacion_superior (persona_id, modalidad, nombre_estudio, semestre_aprobado, graduado, fecha_terminacion, numero_tarjeta) VALUES
(1,'UN','Ingeniería de Sistemas',10,TRUE,'2012-12-15',NULL),
(2,'ES','Especialización en Finanzas',2,FALSE,NULL,NULL),
(3,'MG','Maestría en Educación',4,FALSE,NULL,NULL),
(4,'TC','Técnico en Diseño Gráfico',6,TRUE,'2015-06-20',NULL),
(5,'DOC','Doctorado en Ciencias Sociales',8,TRUE,'2020-07-30',NULL),
(6,'UN','Administración de Empresas',8,TRUE,'2016-11-10',NULL),
(7,'TL','Tecnología en Mecatrónica',5,FALSE,NULL,NULL),
(8,'TE','Tecnología Especializada en Marketing',6,TRUE,'2018-09-12',NULL),
(9,'UN','Medicina',12,TRUE,'2014-12-01','MP12345'),
(10,'ES','Especialización en Derecho Laboral',2,FALSE,NULL,NULL);

-- ==============================
-- INSERTS PARA experiencia_laboral
-- ==============================
INSERT INTO experiencia_laboral (persona_id, sector, empresa, pais, departamento, municipio, correo_entidad, telefonos, fecha_ingreso, fecha_retiro, cargo_contrato, dependencia, direccion_entidad, es_actual) VALUES
(1,'PUBLICA','Ministerio de Educación','Colombia','Cundinamarca','Bogotá','contacto@mineducacion.gov.co','6011234567','2013-01-15','2016-12-20','Analista de Sistemas','TI','Cl 26 #69-76',FALSE),
(2,'PRIVADA','Bancolombia','Colombia','Antioquia','Medellín','talento@bancolombia.com','6042345678','2017-03-01','2020-06-30','Asesora Financiera','Comercial','Cl 48 #20-30',FALSE),
(3,'PRIVADA','Grupo Éxito','Colombia','Antioquia','Medellín','rrhh@grupoexito.com','6048765432','2006-05-10','2012-09-15','Coordinador de Ventas','Ventas','Cl 65 #20-45',FALSE),
(4,'PUBLICA','Alcaldía de Quito','Ecuador','Pichincha','Quito','empleo@quito.gob.ec','5932223344','2016-01-10','2018-12-20','Diseñadora Gráfica','Comunicaciones','Av. Amazonas 123',FALSE),
(5,'PRIVADA','BBVA España','España','Madrid','Madrid','empleo@bbva.com','34912345678','2010-02-01','2015-11-01','Analista de Riesgos','Riesgos','Cl Mayor 100',FALSE),
(6,'PRIVADA','Avianca','Colombia','Santander','Bucaramanga','rrhh@avianca.com','6074567890','2016-07-15','2021-03-30','Administradora','Operaciones','Cl 45 #67-89',FALSE),
(7,'PUBLICA','Universidad de Caldas','Colombia','Caldas','Manizales','empleo@ucaldas.edu.co','6067654321','2012-09-01','2018-11-20','Profesor Auxiliar','Académico','Cl 58 #23-12',FALSE),
(8,'PRIVADA','Nestlé Perú','Perú','Lima','Lima','talento@nestle.com','5117654321','2019-01-01','2022-12-31','Analista de Marketing','Marketing','Av. Central 56',FALSE),
(9,'PUBLICA','Hospital San Rafael','Colombia','Tolima','Ibagué','rrhh@sanrafael.org','6082345678','2015-03-01',NULL,'Médico General','Urgencias','Cl 10 #15-25',TRUE),
(10,'PRIVADA','Nutresa','Colombia','Risaralda','Pereira','empleo@nutresa.com','6063456789','2020-05-01',NULL,'Abogada Junior','Jurídica','Cl 33 #14-55',TRUE);


