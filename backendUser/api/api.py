from flask import Flask, jsonify, request
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import mysql.connector

app = Flask(__name__)


# Configuraciones de base de datos usando variables de entorno y nombres de servicios Docker
MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "mysql"),  # nombre del servicio en docker-compose
    "user": os.getenv("MYSQL_USER", "admin"),
    "password": os.getenv("MYSQL_PASSWORD", "admin123"),
    "database": os.getenv("MYSQL_DATABASE", "hojaVida"),
    "port": int(os.getenv("MYSQL_PORT", "3306")),
}

MARIADB_CONFIG = {
    "host": os.getenv("MARIADB_HOST", "mariadb"),  # nombre del servicio en docker-compose
    "user": os.getenv("MARIADB_USER", "admin"),
    "password": os.getenv("MARIADB_PASSWORD", "admin123"),
    "database": os.getenv("MARIADB_DATABASE", "tienda"),
    "port": int(os.getenv("MARIADB_PORT", "3306")),
}

# Config DB (usa variables de entorno si existen)
POSTGRES_CONFIG = {
    "host": os.getenv("DB_HOST", "postgres"),
    "database": os.getenv("DB_NAME", "mundo"),
    "user": os.getenv("DB_USER", "admin"),
    "password": os.getenv("DB_PASSWORD", "admin123"),
    "port": int(os.getenv("DB_PORT", "5432")),
}


def get_mysql_connection():
    """Conexión a MySQL para hoja de vida"""
    try:
        return mysql.connector.connect(**MYSQL_CONFIG)
    except mysql.connector.Error as err:
        print(f"Error conectando a MySQL: {err}")
        return None

def get_mariadb_connection():
    """Conexión a MariaDB para factura_db"""
    try:
        return mysql.connector.connect(**MARIADB_CONFIG)
    except mysql.connector.Error as err:
        print(f"Error conectando a MariaDB: {err}")
        return None

def get_db_connection():
    return psycopg2.connect(**POSTGRES_CONFIG)

def postgres_all(sql, params=None):
    params = params or ()
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql, params)
                return cur.fetchall(), None
    except psycopg2.Error as e:
        return None, str(e)
    
def query_mysql(sql, params=None, database="mysql"):
    """Ejecutar consulta en MySQL/MariaDB"""
    params = params or ()
    connection = get_mysql_connection() if database == "mysql" else get_mariadb_connection()
    
    if not connection:
        return None, "No se pudo conectar a la base de datos"
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(sql, params)
        
        # Para procedimientos almacenados, necesitamos obtener todos los result sets
        results = []
        for result in cursor.stored_results():
            results.extend(result.fetchall())
        
        # Si no hay stored_results, usar fetchall normal
        if not results:
            results = cursor.fetchall()
            
        cursor.close()
        connection.close()
        return results, None
    except mysql.connector.Error as err:
        return None, str(err)

# BASE DE DATOS HOJA DE VIDA

@app.route("/mundo/obtenerPaisesEstadosCiudades", methods=["GET"])
def obtener_paises_estados_ciudades():
    sql = """
    SELECT
        c.name AS country,
        s.name AS state,
        ci.name AS city
    FROM countries c
    JOIN states   s  ON s.country_id = c.id
    JOIN cities   ci ON ci.state_id  = s.id
    ORDER BY c.name, s.name, ci.name;
    """
    rows, err = postgres_all(sql)
    if err:
        return jsonify({"error": "DB error", "detail": err}), 500
    return jsonify(rows), 200

@app.route("/mundo/obtenerPaisesEstadosCiudades/<string:country_name>", methods=["GET"])
def obtener_por_pais(country_name):
    sql = """
    SELECT
        c.name AS country,
        s.name AS state,
        ci.name AS city
    FROM countries c
    JOIN states   s  ON s.country_id = c.id
    JOIN cities   ci ON ci.state_id  = s.id
    WHERE c.name ILIKE %s
    ORDER BY s.name, ci.name;
    """
    rows, err = postgres_all(sql, (country_name,))
    if err:
        return jsonify({"error": "DB error", "detail": err}), 500
    return jsonify(rows), 200

@app.route("/mundo/listarCiudadesRepetidasPais/<string:country_name>", methods=["GET"])
def listar_ciudades_repetidas_pais(country_name):
    # Lista ciudades repetidas mostrando todos los estados donde aparecen
    sql = """
    SELECT
        c.name AS country,
        s.name AS state,
        ci.name AS city
    FROM countries c
    JOIN states  s  ON s.country_id = c.id
    JOIN cities  ci ON ci.state_id  = s.id
    WHERE c.name ILIKE %s
    AND ci.name IN (
        SELECT ci2.name
        FROM cities ci2
        JOIN states s2 ON ci2.state_id = s2.id
        JOIN countries c2 ON s2.country_id = c2.id
        WHERE c2.name ILIKE %s
        GROUP BY ci2.name
        HAVING COUNT(*) > 1
    )
    ORDER BY ci.name, s.name;
    """
    rows, err = postgres_all(sql, (country_name, country_name,))
    if err:
        return jsonify({"error": "DB error", "detail": err}), 500
    return jsonify(rows), 200



# Api para formato Unico de hoja de Vida
@app.route("/hoja_vida/reporte_tiempo_experiencia/<string:numero_documento>", methods=["GET"])
def reporte_tiempo_experiencia(numero_documento):
    check_persona_sql = "SELECT persona_id FROM persona WHERE numero_documento = %s LIMIT 1"
    persona_result, err = query_mysql(check_persona_sql, (numero_documento,))
    if err:
        return jsonify({"error": "DB error", "detail": err}), 500
    if not persona_result:
        return jsonify({"error": f"No existe persona con documento {numero_documento}"}), 404

    sql = """
    WITH
    persona_lookup AS (
      SELECT persona_id
      FROM persona
      WHERE numero_documento = %s
      LIMIT 1
    ),
    base AS (
  SELECT
    CASE
      WHEN sector = 'PUBLICA' THEN 'SERVIDOR PÚBLICO'
      WHEN (
        INSTR(LOWER(empresa), 'independient') > 0 OR
        INSTR(LOWER(empresa), 'freelan') > 0 OR
        INSTR(LOWER(cargo_contrato), 'independient') > 0 OR
        INSTR(LOWER(cargo_contrato), 'servicio') > 0
      ) THEN 'TRABAJADOR INDEPENDIENTE'
      ELSE 'EMPLEADO DEL SECTOR PRIVADO'
    END AS categoria,

    -- inicio siempre válido y no futuro
    GREATEST(DATE(fecha_ingreso), DATE('1900-01-01')) AS ini,

    -- fin: si es_actual=1 o no hay retiro => hoy; si retiro > hoy => hoy; si no, retiro
    LEAST(
      COALESCE(
        CASE WHEN es_actual = 1 THEN CURDATE() ELSE fecha_retiro END,
        CURDATE()
      ),
      CURDATE()
    ) AS fin
  FROM experiencia_laboral
  WHERE persona_id = (SELECT persona_id FROM persona_lookup)
    AND fecha_ingreso IS NOT NULL
    ),
    rangos AS (
      SELECT categoria, ini, fin
      FROM base
      WHERE fin >= ini
    ),

    -- Colapso POR CATEGORÍA
    orden_cat AS (
      SELECT
        categoria, ini, fin,
        CASE WHEN LAG(fin) OVER (PARTITION BY categoria ORDER BY ini) >= ini THEN 0 ELSE 1 END AS nueva_isla
      FROM rangos
    ),
    islas_cat AS (
      SELECT
        categoria, ini, fin,
        SUM(nueva_isla) OVER (PARTITION BY categoria ORDER BY ini ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS grp
      FROM orden_cat
    ),
    colapsado_cat AS (
      SELECT categoria, MIN(ini) AS ini, MAX(fin) AS fin
      FROM islas_cat
      GROUP BY categoria, grp
    ),
    meses_categoria AS (
      SELECT categoria, COALESCE(SUM(TIMESTAMPDIFF(MONTH, ini, fin)), 0) AS total_meses
      FROM colapsado_cat
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

    -- Colapso GLOBAL (todas las categorías) para TOTAL sin doble conteo
    orden_global AS (
      SELECT
        ini, fin,
        CASE WHEN LAG(fin) OVER (ORDER BY ini) >= ini THEN 0 ELSE 1 END AS nueva_isla
      FROM (SELECT ini, fin FROM rangos) t
    ),
    islas_global AS (
      SELECT
        ini, fin,
        SUM(nueva_isla) OVER (ORDER BY ini ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS grp
      FROM orden_global
    ),
    colapsado_global AS (
      SELECT MIN(ini) AS ini, MAX(fin) AS fin
      FROM islas_global
      GROUP BY grp
    ),
    total_global AS (
      SELECT COALESCE(SUM(TIMESTAMPDIFF(MONTH, ini, fin)), 0) AS total_meses
      FROM colapsado_global
    ),
    totales AS (
      SELECT 'TOTAL TIEMPO EXPERIENCIA' AS categoria,
             (SELECT total_meses FROM total_global) AS total_meses
    )
    SELECT
      s.categoria AS ocupacion,
      FLOOR(s.total_meses / 12) AS anios,
      MOD(s.total_meses, 12) AS meses,
      s.total_meses AS total_meses_calculados
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
    )
    """

    rows, err = query_mysql(sql, (numero_documento,))
    if err:
        return jsonify({"error": "DB error", "detail": err}), 500

    resultado = [{
        "ocupacion": r["ocupacion"],
        "años": int(r["anios"]),
        "meses": int(r["meses"]),
        "total_meses": int(r["total_meses_calculados"]),
        "descripcion": f"{int(r['anios'])} años y {int(r['meses'])} meses"
    } for r in rows]

    return jsonify({"numero_documento": numero_documento, "reporte_experiencia": resultado}), 200


@app.route("/hoja_vida/tablas_persona/<string:name_tabla>", methods=["GET"])
def tablas_persona(name_tabla):
    # Validar nombres de tabla permitidos para evitar SQL injection
    tablas_permitidas = ['persona', 'pais', 'estado', 'ciudad', 'distrito_militar', 
                        'libreta_militar', 'idioma', 'educacion_basica', 
                        'educacion_superior', 'experiencia_laboral']
    
    if name_tabla not in tablas_permitidas:
        return jsonify({"error": "Tabla no permitida"}), 400
    
    sql = f"SELECT * FROM {name_tabla}"
    rows, err = query_mysql(sql, (), "mysql")
    if err:
        return jsonify({"error": "DB error", "detail": err}), 500
    return jsonify(rows), 200



    # BASE DE DATOS FACTURA

@app.route("/factura_db/historial_precio/<string:producto_name>", methods=["GET"])
def historial_precio(producto_name):
    sql = """
    SELECT 
        a.nombre AS articulo,
        h.precio,
        h.fecha_inicio,
        h.fecha_fin
    FROM historial_precio h
    JOIN articulo a ON h.articulo_id = a.articulo_id
    WHERE a.nombre = %s 
    ORDER BY h.fecha_inicio
    """
    rows, err = query_mysql(sql, (producto_name,), "mariadb")
    if err:
        return jsonify({"error": "DB error", "detail": err}), 500
    return jsonify(rows), 200


@app.route("/factura_db/tabla_productos/<string:name_tabla>", methods=["GET"])
def tabla_productos(name_tabla):
    # Validar nombres de tabla permitidos para evitar SQL injection
    tablas_permitidas = ['cliente', 'articulo', 'historial_precio', 'factura', 'detalle_factura']
    
    if name_tabla not in tablas_permitidas:
        return jsonify({"error": "Tabla no permitida"}), 400
    
    sql = f"SELECT * FROM {name_tabla}"
    rows, err = query_mysql(sql, (), "mariadb")
    if err:
        return jsonify({"error": "DB error", "detail": err}), 500
    return jsonify(rows), 200



@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    # debug=True solo en desarrollo
    app.run(host="0.0.0.0", port=4000, debug=True)