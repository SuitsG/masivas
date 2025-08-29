-- =========================================
-- Script BD hoja_vida
-- MySQL/MariaDB 10.x/8.x
-- =========================================

SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

DROP DATABASE IF EXISTS hojaVida;

CREATE DATABASE hojaVida
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE hojaVida;

-- ===================================================
-- Tablas
-- ===================================================

CREATE TABLE pais (
  pais_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  nacionalidad VARCHAR(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE estado (
  estado_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  pais_id INT NOT NULL,
  CONSTRAINT fk_estado_pais
    FOREIGN KEY (pais_id) REFERENCES pais(pais_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE ciudad (
  ciudad_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  estado_id INT NOT NULL,
  CONSTRAINT fk_ciudad_estado
    FOREIGN KEY (estado_id) REFERENCES estado(estado_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE persona (
    persona_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    nombres VARCHAR(100) NOT NULL,
    primer_apellido VARCHAR(50) NOT NULL,
    segundo_apellido VARCHAR(50),
    tipo_documento ENUM('CC','CE','PAS') NOT NULL,
    numero_documento VARCHAR(20) NOT NULL UNIQUE,
    sexo ENUM('M','F') NOT NULL,

    -- OJO: dejamos el campo nacionalidad, pero SIN FK a pais(nacionalidad)
    nacionalidad VARCHAR(100) NOT NULL,

    pais_nacimiento_id INT NOT NULL,
    estado_nacimiento_id INT NOT NULL,
    ciudad_nacimiento_id INT NOT NULL,
    fecha_nacimiento DATE,
    direccion VARCHAR(150),
    pais_residencia_id INT NOT NULL,
    estado_residencia_id INT NOT NULL,
    ciudad_residencia_id INT NOT NULL,
    telefono VARCHAR(20),
    email VARCHAR(100),

    CONSTRAINT fk_persona_pais_nac
      FOREIGN KEY (pais_nacimiento_id) REFERENCES pais(pais_id),
    CONSTRAINT fk_persona_estado_nac
      FOREIGN KEY (estado_nacimiento_id) REFERENCES estado(estado_id),
    CONSTRAINT fk_persona_ciudad_nac
      FOREIGN KEY (ciudad_nacimiento_id) REFERENCES ciudad(ciudad_id),
    CONSTRAINT fk_persona_pais_res
      FOREIGN KEY (pais_residencia_id) REFERENCES pais(pais_id),
    CONSTRAINT fk_persona_estado_res
      FOREIGN KEY (estado_residencia_id) REFERENCES estado(estado_id),
    CONSTRAINT fk_persona_ciudad_res
      FOREIGN KEY (ciudad_residencia_id) REFERENCES ciudad(ciudad_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE distrito_militar (
  distrito_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(10) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE libreta_militar (
  libreta_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  persona_id INT NOT NULL UNIQUE,
  clase ENUM('Primera','Segunda'),
  numero VARCHAR(20),
  distrito_id INT,
  CONSTRAINT fk_libreta_persona
    FOREIGN KEY (persona_id) REFERENCES persona(persona_id),
  CONSTRAINT fk_libreta_distrito
    FOREIGN KEY (distrito_id) REFERENCES distrito_militar(distrito_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE idioma (
    idioma_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    persona_id INT NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    habla ENUM('Regular','Bien','Muy Bien'),
    lee ENUM('Regular','Bien','Muy Bien'),
    escribe ENUM('Regular','Bien','Muy Bien'),
    CONSTRAINT fk_idioma_persona
      FOREIGN KEY (persona_id) REFERENCES persona(persona_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE educacion_basica (
    basica_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    persona_id INT NOT NULL,
    ultimo_grado_aprobado INT CHECK (ultimo_grado_aprobado BETWEEN 1 AND 11),
    titulo_obtenido VARCHAR(100),
    fecha_grado DATE,
    CONSTRAINT fk_basica_persona
      FOREIGN KEY (persona_id) REFERENCES persona(persona_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE educacion_superior (
    superior_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    persona_id INT NOT NULL,
    modalidad ENUM('TC','TL','TE','UN','ES','MG','DOC') NOT NULL,
    nombre_estudio VARCHAR(150),
    semestre_aprobado INT,
    graduado BOOLEAN,
    fecha_terminacion DATE,
    numero_tarjeta VARCHAR(50),
    CONSTRAINT fk_superior_persona
      FOREIGN KEY (persona_id) REFERENCES persona(persona_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE experiencia_laboral (
  id_exp INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  persona_id INT NOT NULL,
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
  es_actual BOOLEAN DEFAULT FALSE,
  CONSTRAINT fk_exp_persona
    FOREIGN KEY (persona_id) REFERENCES persona(persona_id)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =========================================
-- Índices (para rendimiento)
-- =========================================
CREATE INDEX idx_pais_nacionalidad       ON pais(nacionalidad);
CREATE INDEX idx_pais_nombre             ON pais(nombre);
CREATE INDEX idx_estado_pais_nombre      ON estado(pais_id, nombre);
CREATE INDEX idx_ciudad_estado_nombre    ON ciudad(estado_id, nombre);

-- =========================================
-- FIN
-- =========================================
