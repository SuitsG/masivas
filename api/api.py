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
    "database": os.getenv("MYSQL_DATABASE", "hoja_vida"),
    "port": int(os.getenv("MYSQL_PORT", "3306")),
}

MARIADB_CONFIG = {
    "host": os.getenv("MARIADB_HOST", "mariadb"),  # nombre del servicio en docker-compose
    "user": os.getenv("MARIADB_USER", "admin"),
    "password": os.getenv("MARIADB_PASSWORD", "admin123"),
    "database": os.getenv("MARIADB_DATABASE", "factura_db"),
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
        result = cursor.fetchall()
        cursor.close()
        connection.close()
        return result, None
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


@app.route("/hoja_vida/reporte_tiempo_experiencia/<string:numero_documento>", methods=["GET"])
def reporte_tiempo_experiencia(numero_documento):
    sql = "CALL reporte_tiempo_experiencia(%s)"
    rows, err = query_mysql(sql, (numero_documento,))
    if err:
        return jsonify({"error": "DB error", "detail": err}), 500
    return jsonify(rows), 200


@app.route("/hoja_vida/tablas_persona/<string:name_tabla>", methods=["GET"])
def tablas_persona(name_tabla):
    sql = "SELECT * FROM %s"
    rows, err = query_mysql(sql, (name_tabla,))
    if err:
        return jsonify({"error": "DB error", "detail": err}), 500
    return jsonify(rows), 200





    # BASE DE DATOS FACTURA

@app.route("/factura_db/historial_precio/<string:producto_name>", methods=["GET"])
def historial_precio(producto_name):
    sql = "CALL historial_precio(%s)"
    rows, err = query_mysql(sql, (producto_name,))
    if err:
        return jsonify({"error": "DB error", "detail": err}), 500
    return jsonify(rows), 200


@app.route("/factura_db/tabla_productos/<string:name_tabla>", methods=["POST"])
def tabla_productos(name_tabla):
    sql = "SELECT * FROM %s"
    rows, err = query_mysql(sql, (name_tabla,))
    if err:
        return jsonify({"error": "DB error", "detail": err}), 500
    return jsonify(rows), 200



 




@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    # debug=True solo en desarrollo
    app.run(host="0.0.0.0", port=4000, debug=True)