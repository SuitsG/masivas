import mysql.connector
import csv

conn = mysql.connector.connect(
    host="127.0.0.1",
    user="admin",
    password="admin123",
    database="colombia",
    port=3306
)
cursor = conn.cursor()

region_cache = {}
depto_cache = {}

def norm_codigo(text):
    # Conserva como string sin espacios
    return text.strip()

def norm_municipio_codigo(text):
    # Quita espacios; conserva el punto (o quitarlo si prefieres)
    return text.strip()

with open("municipios.csv", newline='', encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    field_map = {h.strip().lstrip('\ufeff'): h for h in reader.fieldnames}

    print("Campos detectados en CSV:", field_map)

    for line_no, row in enumerate(reader, start=2):
        # Detectar fila mal formada
        if row is None or any(k not in field_map.values() for k in row.keys()):
            print(f"[WARN] Fila {line_no} mal formada: {row}")
            continue
        # Si algún campo clave es None
        required_keys = [
            field_map["REGION"],
            field_map["CÓDIGO DANE DEL DEPARTAMENTO"],
            field_map["DEPARTAMENTO"],
            field_map["CÓDIGO DANE DEL MUNICIPIO"],
            field_map["MUNICIPIO"]
        ]
        if any(row[k] in (None, "") for k in required_keys):
            print(f"[SKIP] Fila {line_no} con valores vacíos: {row}")
            continue

        region_name = row[field_map["REGION"]].strip()
        depto_cod = norm_codigo(row[field_map["CÓDIGO DANE DEL DEPARTAMENTO"]])
        depto_name = row[field_map["DEPARTAMENTO"]].strip()
        muni_cod = norm_municipio_codigo(row[field_map["CÓDIGO DANE DEL MUNICIPIO"]])
        muni_name = row[field_map["MUNICIPIO"]].strip()

        # Insert región
        region_id = region_cache.get(region_name)
        if region_id is None:
            cursor.execute("SELECT region_id FROM region WHERE region_name=%s", (region_name,))
            res = cursor.fetchone()
            if res:
                region_id = res[0]
            else:
                cursor.execute("INSERT INTO region (region_name) VALUES (%s)", (region_name,))
                region_id = cursor.lastrowid
            region_cache[region_name] = region_id

        # Insert departamento
        depto_id = depto_cache.get(depto_cod)
        if depto_id is None:
            cursor.execute("SELECT departamento_id FROM departamento WHERE departamento_codigo_dane=%s", (depto_cod,))
            res = cursor.fetchone()
            if res:
                depto_id = res[0]
            else:
                cursor.execute(
                    "INSERT INTO departamento (departamento_name, departamento_codigo_dane, region_id) VALUES (%s,%s,%s)",
                    (depto_name, depto_cod, region_id)
                )
                depto_id = cursor.lastrowid
            depto_cache[depto_cod] = depto_id

        # Insert municipio (evita duplicado por código)
        cursor.execute("SELECT municipio_id FROM municipio WHERE municipio_codigo_dane=%s", (muni_cod,))
        if cursor.fetchone() is None:
            cursor.execute(
                "INSERT INTO municipio (municipio_name, municipio_codigo_dane, departamento_id) VALUES (%s,%s,%s)",
                (muni_name, muni_cod, depto_id)
            )

conn.commit()
cursor.close()
conn.close()
print("Carga completa.")