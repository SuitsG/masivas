import mysql.connector
import os

# Configuración para conectar al motor MariaDB (sin base de datos específica)
MARIADB_CONFIG = {
    "host": "mariadb",
    "user": "admin", 
    "password": "admin123",
    "port": 3306,
}

def motor_mariadb():
    """
    Función para conectar al motor MariaDB sin base de datos específica.
    """
    try:
        conexion = mysql.connector.connect(**MARIADB_CONFIG)
        print("Conexión exitosa al motor MariaDB")
        return conexion
    except mysql.connector.Error as err:
        print(f"Error al conectar a MariaDB: {err}")
        return None

def base_datos(nombre_bd):
    """
    Función para conectar a una base de datos específica en MariaDB.
    """
    config_bd = MARIADB_CONFIG.copy()
    config_bd["database"] = nombre_bd
    try:
        conexion = mysql.connector.connect(**config_bd)
        print(f"Conexión exitosa a la base de datos '{nombre_bd}'")
        return conexion
    except mysql.connector.Error as err:
        print(f"Error al conectar a la base de datos '{nombre_bd}': {err}")
        return None

