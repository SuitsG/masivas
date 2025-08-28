import csv
import mysql.connector


conexion = mysql.connector.connect(
    host='localhost',
    user='root',
    password='root',
    database='hojaVida'
)

cursor = conexion.cursor()
