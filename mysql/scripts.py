import csv
import mysql.connector

conexion = mysql.connector.connect(
    host='localhost',
    user='admin',
    password='admin123',
    database='hojaVida',
    port=3306
)

cursor = conexion.cursor()

# CSV con columnas: pais, nacionalidad, estado, ciudad
with open('nueva_db.csv', 'r', encoding='utf-8', newline='') as archivo_csv:
    lector = csv.reader(archivo_csv)
    encabezados = next(lector)  # salta encabezados

    for fila in lector:
        pais, nacionalidad, estado, ciudad = fila[0], fila[1], fila[2], fila[3]

        # 1) PAÍS: único por nombre (tu lógica)
        cursor.execute("""
            INSERT INTO pais (nombre, nacionalidad)
            SELECT %s, %s
            WHERE NOT EXISTS (SELECT 1 FROM pais WHERE nombre = %s)
        """, (pais, nacionalidad, pais))

        # 2) ESTADO: puede repetir nombre, pero no para el mismo país
        cursor.execute("""
            INSERT INTO estado (nombre, pais_id)
            SELECT %s, p.pais_id
            FROM pais p
            WHERE p.nombre = %s
              AND NOT EXISTS (
                SELECT 1
                FROM estado e
                WHERE e.nombre = %s AND e.pais_id = p.pais_id
              )
        """, (estado, pais, estado))

        # 3) CIUDAD: puede repetir nombre, pero no para el mismo estado (del país correspondiente)
        cursor.execute("""
            INSERT INTO ciudad (nombre, estado_id)
            SELECT %s, e.estado_id
            FROM estado e
            JOIN pais p ON p.pais_id = e.pais_id
            WHERE e.nombre = %s
              AND p.nombre = %s
              AND NOT EXISTS (
                SELECT 1
                FROM ciudad c
                WHERE c.nombre = %s AND c.estado_id = e.estado_id
              )
        """, (ciudad, estado, pais, ciudad))

conexion.commit()
cursor.close()
conexion.close()
