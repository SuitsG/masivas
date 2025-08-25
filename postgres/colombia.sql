CREATE DATABASE colombia;

\c colombia

CREATE TABLE region(
region_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
region_nombre VARCHAR(255)
);

CREATE TABLE departamento(
departamento_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
departamento_nombre VARCHAR(255),
departamento_codigo_dane VARCHAR(10) UNIQUE,
region_id INT NOT NULL REFERENCES region(region_id)
);

CREATE TABLE municipio(
municipio_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
municipio_nombre VARCHAR(255),
municipio_codigo_dane VARCHAR(10) UNIQUE,
departamento_id INT NOT NULL REFERENCES departamento(departamento_id)
);

CREATE OR REPLACE PROCEDURE cargar_csv(ruta TEXT)
LANGUAGE plpgsql
AS $$
DECLARE
    filas     TEXT[];
    columnas  TEXT[];
    i         INT;
BEGIN
    filas := string_to_array(pg_read_file(ruta), E'\r\n');

    -- Regiones
    FOR i IN 2..array_length(filas, 1) LOOP
        columnas := string_to_array(filas[i], ',');
        INSERT INTO region(region_nombre)
        SELECT columnas[1]
        WHERE NOT EXISTS (
            SELECT 1 FROM region r WHERE r.region_nombre = columnas[1]
        );
    END LOOP;

    -- Departamentos
    FOR i IN 2..array_length(filas, 1) LOOP
        columnas := string_to_array(filas[i], ',');
        INSERT INTO departamento (departamento_nombre, departamento_codigo_dane, region_id)
        SELECT columnas[3], columnas[2],
               (SELECT r.region_id FROM region r WHERE r.region_nombre = columnas[1])
        WHERE NOT EXISTS (
            SELECT 1 FROM departamento d WHERE d.departamento_codigo_dane = columnas[2]
        );
    END LOOP;

    -- Municipios
    FOR i IN 2..array_length(filas, 1) LOOP
        columnas := string_to_array(filas[i], ',');
        INSERT INTO municipio (municipio_nombre, municipio_codigo_dane, departamento_id)
        SELECT columnas[5], columnas[4],
               (SELECT d.departamento_id FROM departamento d
                WHERE d.departamento_codigo_dane = columnas[2])
        WHERE NOT EXISTS (
            SELECT 1 FROM municipio m WHERE m.municipio_codigo_dane = columnas[4]
        );
    END LOOP;
END;
$$;

CREATE OR REPLACE VIEW listar_colombia AS
SELECT 
  r.region_nombre AS "REGION",
  d.departamento_codigo_dane AS "CODIGO DANE DEPARTAMENTO",
  d.departamento_nombre AS "DEPARTAMENTO",
  m.municipio_codigo_dane AS "CODIGO DANE MUNICIPIO",
  m.municipio_nombre AS "MUNICIPIO"
FROM region r
JOIN departamento d ON r.region_id = d.region_id
JOIN municipio m ON d.departamento_id = m.departamento_id;

CREATE OR REPLACE VIEW municipios_repetidos AS
SELECT d.departamento_nombre, m.municipio_nombre 
FROM departamento d
JOIN municipio m ON d.departamento_id = m.departamento_id
WHERE m.municipio_nombre IN (
SELECT municipio_nombre 
FROM municipio
GROUP BY municipio_nombre
HAVING COUNT(*)>1
) ORDER BY m.municipio_nombre;