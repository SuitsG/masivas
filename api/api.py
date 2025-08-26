from flask import Flask, jsonify
import os
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

# Config DB (usa variables de entorno si existen)
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "postgres"),
    "database": os.getenv("DB_NAME", "mundo"),
    "user": os.getenv("DB_USER", "admin"),
    "password": os.getenv("DB_PASSWORD", "admin123"),
    "port": int(os.getenv("DB_PORT", "5432")),
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

def query_all(sql, params=None):
    params = params or ()
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql, params)
                return cur.fetchall(), None
    except psycopg2.Error as e:
        return None, str(e)

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
    rows, err = query_all(sql)
    if err:
        return jsonify({"error": "DB error", "detail": err}), 500
    return jsonify(rows), 200

@app.route("/obtenerPaisesEstadosCiudades/<string:country_name>", methods=["GET"])
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
    rows, err = query_all(sql, (country_name,))
    if err:
        return jsonify({"error": "DB error", "detail": err}), 500
    return jsonify(rows), 200

@app.route("/listarCiudadesRepetidasPais/<string:country_name>", methods=["GET"])
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
    rows, err = query_all(sql, (country_name, country_name,))
    if err:
        return jsonify({"error": "DB error", "detail": err}), 500
    return jsonify(rows), 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    # debug=True solo en desarrollo
    app.run(host="0.0.0.0", port=4000, debug=True)
