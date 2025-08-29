#!/usr/bin/env python3
import csv
import mysql.connector

CSV_PATH = "/tmp/nueva_db.csv"   # En tu Dockerfile copias a /tmp

conexion = mysql.connector.connect(
    host='localhost',
    user='admin',
    password='admin123',
    database='hojaVida',
    port=3306
)
conexion.autocommit = False
cursor = conexion.cursor()

# =============================
# INSERTAR PAÍS / ESTADO / CIUDAD
# =============================
sql_pais = """
INSERT INTO pais (nombre, nacionalidad)
SELECT %s, %s
WHERE NOT EXISTS (SELECT 1 FROM pais WHERE nombre = %s)
"""

sql_estado = """
INSERT INTO estado (nombre, pais_id)
SELECT %s, p.pais_id
FROM pais p
WHERE p.nombre = %s
  AND NOT EXISTS (
    SELECT 1 FROM estado e
    WHERE e.nombre = %s AND e.pais_id = p.pais_id
  )
"""

sql_ciudad = """
INSERT INTO ciudad (nombre, estado_id)
SELECT %s,
       (SELECT e.estado_id
          FROM estado e
          JOIN pais p ON p.pais_id = e.pais_id
         WHERE e.nombre = %s AND p.nombre = %s
         LIMIT 1)
WHERE NOT EXISTS (
  SELECT 1
  FROM ciudad c
  JOIN estado e2 ON e2.estado_id = c.estado_id
  JOIN pais p2 ON p2.pais_id = e2.pais_id
  WHERE c.nombre = %s AND e2.nombre = %s AND p2.nombre = %s
)
"""

BATCH = 5000
pend = 0

with open(CSV_PATH, 'r', encoding='utf-8', newline='') as f:
    lector = csv.reader(f)
    next(lector)  # encabezados: pais,nacionalidad,estado,ciudad
    for pais, nacionalidad, estado, ciudad in lector:
        cursor.execute(sql_pais,   (pais, nacionalidad, pais))
        cursor.execute(sql_estado, (estado, pais, estado))
        cursor.execute(sql_ciudad, (ciudad, estado, pais, ciudad, estado, pais))
        pend += 1
        if pend >= BATCH:
            conexion.commit(); pend = 0

if pend:
    conexion.commit()

# =============================
# AYUDAS: OBTENER TRIPLAS VÁLIDAS (pais, estado, ciudad)
# =============================
def get_geo_triple(offset: int = 0):
    """
    Devuelve (pais_id, estado_id, ciudad_id, nacionalidad_txt, pais_nombre, estado_nombre, ciudad_nombre)
    usando un offset sobre el orden natural por IDs.
    Si no hay suficientes filas para el offset, reintenta con offset 0.
    """
    q = """
    SELECT p.pais_id, e.estado_id, c.ciudad_id, p.nacionalidad,
           p.nombre AS pais_nombre, e.nombre AS estado_nombre, c.nombre AS ciudad_nombre
    FROM pais p
    JOIN estado e ON e.pais_id = p.pais_id
    JOIN ciudad c ON c.estado_id = e.estado_id
    ORDER BY p.pais_id, e.estado_id, c.ciudad_id
    LIMIT %s, 1
    """
    cursor.execute(q, (offset,))
    row = cursor.fetchone()
    if not row:
        cursor.execute(q, (0,))
        row = cursor.fetchone()
    return row  # puede ser None si no hubiera datos

# =============================
# DATOS DE PRUEBA: DISTRITOS
# =============================
cursor.executemany(
    """
    INSERT INTO distrito_militar (nombre)
    VALUES (%s)
    ON DUPLICATE KEY UPDATE nombre = VALUES(nombre)
    """,
    [("DM-01",), ("DM-02",), ("DM-03",)]
)

# =============================
# DATOS DE PRUEBA: PERSONAS (3 ejemplos)
# Usamos geos distintos con offsets para variar nacimiento/residencia
# =============================
personas = [
    {
        "doc": "CC1001", "tipo": "CC", "sexo": "F",
        "nombres": "Ana Maria", "ap1": "Lopez", "ap2": "Gonzalez",
        "nac_offset": 0, "res_offset": 10,
        "fecha_nac": "1996-03-12", "dir": "Calle 10 #12-34",
        "tel": "3001234567", "email": "ana.lopez@example.com"
    },
    {
        "doc": "CE2001", "tipo": "CE", "sexo": "M",
        "nombres": "Carlos Andres", "ap1": "Perez", "ap2": "Gomez",
        "nac_offset": 1, "res_offset": 11,
        "fecha_nac": "1992-07-25", "dir": "Carrera 45 #67-89",
        "tel": "3017654321", "email": "carlos.perez@example.com"
    },
    {
        "doc": "PAS3001", "tipo": "PAS", "sexo": "F",
        "nombres": "Laura", "ap1": "Torres", "ap2": "Ramirez",
        "nac_offset": 2, "res_offset": 12,
        "fecha_nac": "1998-11-05", "dir": "Av. Principal 123",
        "tel": "3025557788", "email": "laura.torres@example.com"
    },
]

sql_persona = """
INSERT INTO persona (
    nombres, primer_apellido, segundo_apellido, tipo_documento, numero_documento, sexo,
    nacionalidad, pais_nacimiento_id, estado_nacimiento_id, ciudad_nacimiento_id,
    fecha_nacimiento, direccion, pais_residencia_id, estado_residencia_id, ciudad_residencia_id,
    telefono, email
)
SELECT
    %s, %s, %s, %s, %s, %s,
    %s, %s, %s, %s,
    %s, %s, %s, %s, %s,
    %s, %s
WHERE NOT EXISTS (
    SELECT 1 FROM persona WHERE numero_documento = %s
)
"""

for p in personas:
    nac = get_geo_triple(p["nac_offset"])
    res = get_geo_triple(p["res_offset"])
    if not nac or not res:
        continue  # si no hay datos geográficos cargados, saltar

    (pais_nac_id, estado_nac_id, ciudad_nac_id, nac_txt, *_rest1) = nac
    (pais_res_id, estado_res_id, ciudad_res_id, *_rest2) = res

    params = (
        p["nombres"], p["ap1"], p["ap2"], p["tipo"], p["doc"], p["sexo"],
        nac_txt, pais_nac_id, estado_nac_id, ciudad_nac_id,
        p["fecha_nac"], p["dir"], pais_res_id, estado_res_id, ciudad_res_id,
        p["tel"], p["email"],
        p["doc"]
    )
    cursor.execute(sql_persona, params)

# =============================
# DATOS DE PRUEBA: LIBRETA MILITAR (2 personas)
# =============================
sql_libreta = """
INSERT INTO libreta_militar (persona_id, clase, numero, distrito_id)
SELECT pe.persona_id, %s, %s, dm.distrito_id
FROM persona pe
JOIN distrito_militar dm ON dm.nombre = %s
WHERE pe.numero_documento = %s
  AND NOT EXISTS (SELECT 1 FROM libreta_militar lm WHERE lm.persona_id = pe.persona_id)
"""
cursor.execute(sql_libreta, ("Primera", "LM-0001", "DM-01", "CC1001"))
cursor.execute(sql_libreta, ("Segunda", "LM-0002", "DM-02", "CE2001"))

# =============================
# DATOS DE PRUEBA: IDIOMAS
# =============================
sql_idioma = """
INSERT INTO idioma (persona_id, nombre, habla, lee, escribe)
SELECT pe.persona_id, %s, %s, %s, %s
FROM persona pe
WHERE pe.numero_documento = %s
  AND NOT EXISTS (
    SELECT 1 FROM idioma i
    WHERE i.persona_id = pe.persona_id AND i.nombre = %s
  )
"""
# Ana
cursor.execute(sql_idioma, ("Español", "Muy Bien", "Muy Bien", "Muy Bien", "CC1001", "Español"))
cursor.execute(sql_idioma, ("Inglés",  "Bien",     "Bien",     "Regular", "CC1001", "Inglés"))
# Carlos
cursor.execute(sql_idioma, ("Español", "Muy Bien", "Muy Bien", "Muy Bien", "CE2001", "Español"))
cursor.execute(sql_idioma, ("Portugués","Regular", "Regular", "Regular",  "CE2001", "Portugués"))
# Laura
cursor.execute(sql_idioma, ("Español", "Muy Bien", "Muy Bien", "Muy Bien", "PAS3001", "Español"))
cursor.execute(sql_idioma, ("Inglés",  "Bien",     "Bien",     "Bien",     "PAS3001", "Inglés"))

# =============================
# DATOS DE PRUEBA: EDUCACIÓN BÁSICA
# =============================
sql_basica = """
INSERT INTO educacion_basica (persona_id, ultimo_grado_aprobado, titulo_obtenido, fecha_grado)
SELECT pe.persona_id, %s, %s, %s
FROM persona pe
WHERE pe.numero_documento = %s
  AND NOT EXISTS (
    SELECT 1 FROM educacion_basica b WHERE b.persona_id = pe.persona_id
  )
"""
cursor.execute(sql_basica, (11, "Bachiller Académico", "2013-11-30", "CC1001"))
cursor.execute(sql_basica, (11, "Bachiller Técnico",   "2010-11-30", "CE2001"))
cursor.execute(sql_basica, (11, "Bachiller Académico", "2015-11-30", "PAS3001"))

# =============================
# DATOS DE PRUEBA: EDUCACIÓN SUPERIOR
# =============================
sql_superior = """
INSERT INTO educacion_superior (persona_id, modalidad, nombre_estudio, semestre_aprobado, graduado, fecha_terminacion, numero_tarjeta)
SELECT pe.persona_id, %s, %s, %s, %s, %s, %s
FROM persona pe
WHERE pe.numero_documento = %s
  AND NOT EXISTS (
    SELECT 1 FROM educacion_superior s WHERE s.persona_id = pe.persona_id
  )
"""
cursor.execute(sql_superior, ("UN", "Ingeniería de Sistemas", 10, True,  "2020-12-15", "TARJ-001", "CC1001"))
cursor.execute(sql_superior, ("TL", "Tecnología en Redes",     6, True,  "2014-06-30", "TARJ-002", "CE2001"))
cursor.execute(sql_superior, ("ES", "Especialización en Datos", 2, False, None,         None,       "PAS3001"))

# =============================
# DATOS DE PRUEBA: EXPERIENCIA LABORAL
# (usa valores de texto para pais/departamento/municipio)
# =============================
sql_exp = """
INSERT INTO experiencia_laboral (
  persona_id, sector, empresa, pais, departamento, municipio, correo_entidad, telefonos,
  fecha_ingreso, fecha_retiro, cargo_contrato, dependencia, direccion_entidad, es_actual
)
SELECT pe.persona_id, %s, %s,
       p.nombre, e.nombre, c.nombre,
       %s, %s, %s, %s, %s, %s, %s, %s
FROM persona pe
JOIN pais p    ON p.pais_id = pe.pais_residencia_id
JOIN estado e  ON e.estado_id = pe.estado_residencia_id
JOIN ciudad c  ON c.ciudad_id = pe.ciudad_residencia_id
WHERE pe.numero_documento = %s
  AND NOT EXISTS (
    SELECT 1 FROM experiencia_laboral ex WHERE ex.persona_id = pe.persona_id
  )
"""
cursor.execute(sql_exp, ("PRIVADA", "Tech Solutions S.A.S",
                         "contacto@techsolutions.com", "3200000000",
                         "2021-01-10", None, "Desarrolladora Backend", "TI",
                         "Cra 12 #34-56", True, "CC1001"))

cursor.execute(sql_exp, ("PUBLICA", "Alcaldía Municipal",
                         "recursoshumanos@alcaldia.gov", "6011234567",
                         "2015-03-01", "2018-07-31", "Analista de Sistemas", "Sistemas",
                         "Cl. 1 #2-03", False, "CE2001"))

cursor.execute(sql_exp, ("PRIVADA", "Market Data LTDA",
                         "rrhh@marketdata.com", "3101234567",
                         "2023-05-15", None, "Data Analyst Jr", "Analytics",
                         "Av 7 #80-20", True, "PAS3001"))

# =============================
# COMMIT FINAL
# =============================
conexion.commit()
cursor.close()
conexion.close()

print("Carga completada: ubicaciones + datos de prueba.")
