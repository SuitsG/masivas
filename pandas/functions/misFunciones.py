import os
import pandas as pd
import sys
import matplotlib.pyplot as plt
from conexiones.conexionMariaDB import base_datos
from conexiones.conexionMariaDB import motor_mariadb
import json


def leer_csv(archivo):
    """ 
    Funcion para leer archivos CSV con diferentes codificaciones.
    Intenta varias codificaciones comunes hasta encontrar una que funcione.
    Devuelve las primeras filas del DataFrame como string.
    """

    esquemaCodificacion = ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']

    for codificacion in esquemaCodificacion:
        try:
            df_csv = pd.read_csv(archivo, encoding=codificacion)
            return df_csv.head().to_string()
        except (UnicodeDecodeError, ValueError):
            continue
    return "No se pudo leer el archivo CSV con ninguna de las codificaciones."



def leer_html(url):
    """ 
    Funcion para leer archivos HTML.
    Devuelve las primeras filas del DataFrame como string.
    """
    df_html = pd.read_html(url)
    return df_html[0].head().to_string()


def leer_xlsx(archivo):
    """
    Funcion para leer archivos XLSX.
    Devuelve las primeras filas del DataFrame como string.
    """
    df_xlsx = pd.read_excel(archivo)
    return df_xlsx.head().to_string()


def leer_json(archivo):
    """
    Funcion para leer archivos JSON.
    Devuelve las primeras filas del DataFrame como string.
    """
    with open(archivo, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Si el JSON tiene múltiples claves, mostrar la primera tabla encontrada
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, list) and len(value) > 0:
                df_json = pd.DataFrame(value)
                return f"Tabla: {key}\n" + df_json.head().to_string()
    
    # Si es una lista directa
    if isinstance(data, list):
        df_json = pd.DataFrame(data)
        return df_json.head().to_string()
    
    return str(data)



def crear_dataframe(data):
    """ 
    Funcion para crear un DataFrame a partir de una lista de diccionarios.
    Devuelve el DataFrame.
    """
    df = pd.DataFrame(data)
    return df



def leer_txt(data):
    """
    Funcion para leer archivos TXT con separador tabulador.
    Devuelve las primeras filas del DataFrame como string.
    """
    df_txt = pd.read_csv(data, sep="\t")
    return df_txt.head().to_string()



def leer_hdf5(data):
    """
    Funcion para leer archivos HDF5.
    Devuelve las primeras filas del DataFrame como string.
    """
    df_hdf5 = pd.read_hdf(data,key='ventas')
    return df_hdf5.head().to_string()


def unir_excels(array_archivos):
    """
    Funcion para unir multiples archivos Excel en uno solo.
    """
    dataframes = []
    
    # Leer cada archivo Excel y convertirlo a DataFrame
    for archivo in array_archivos:
        try:
            df = pd.read_excel(archivo)
            dataframes.append(df)
        except Exception as e:
            print(f"Error leyendo {archivo}: {e}")
            continue
    
    # Concatenar todos los DataFrames
    if dataframes:
        df_unido = pd.concat(dataframes, axis=0, ignore_index=True)
        df_unido.to_excel("../data/RELAX_UNIDO.xlsx", index=False)
        return df_unido.head().to_string()
    else:
        return "No se pudieron leer archivos para unir."


def limpiar_archivo_temporal(archivo):
    """
    Funcion para limpiar un archivo Excel temporal.
    Elimina columnas innecesarias y guarda el resultado en un nuevo archivo CSV.
    Devuelve las primeras filas del DataFrame limpio como string.
    """
    df = pd.read_excel(archivo, engine='openpyxl')

    # elimina columnas indicadas (si alguna no existe, se ignora)
    df = df.drop(columns=["SM", "Jquía.productos", "Grupo artíc. ext."], errors="ignore")

    # guardar como CSV (UTF-8 con BOM para que Excel muestre bien tildes)
    df.to_csv("../data/RELAX_LIMPIO.csv", index=False, encoding="utf-8-sig")
    
    return df.head().to_string()



def crear_parcialDB():
    """
    Crear la base de datos parcialDB y la tabla productos
    Devuelve un mensaje indicando el resultado de la operación.
    """
    try:    
        conexion = motor_mariadb()
        if conexion is None:
            return "Error: No se pudo conectar al motor MariaDB."
        cursor = conexion.cursor()
        
        # Crear base de datos
        cursor.execute("CREATE DATABASE IF NOT EXISTS parcialDB;")
        cursor.execute("USE parcialDB;")
        
        # Crear tabla
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                material VARCHAR(100),
                descripcion VARCHAR(255),
                fabricante VARCHAR(100),
                modificado DATETIME
            );
        """)
        
        conexion.commit()
        cursor.close()
        conexion.close()
        
        return "Base de datos parcialDB y tabla productos creadas exitosamente"
    
    except Exception as err:
        return f"Error creando base de datos: {err}"

def cargar_datos_parcialDB(archivo):
    """
    Cargar datos desde a la base de datos parcialDB desde un archivo CSV.
    El archivo debe tener las columnas: Material, Texto breve de material, Fabricante, Últ.mod.
    Las columnas se mapean a la tabla productos como:
    - Material -> material
    - Texto breve de material -> descripcion
    - Fabricante -> fabricante
    - Últ.mod. -> modificado
    Se ignoran filas con datos inválidos o faltantes en campos críticos.
    Devuelve un mensaje indicando el resultado de la operación.
    """
    try:
        # Verificar si el archivo existe
        if not os.path.exists(archivo):
            return f"Error: El archivo {archivo} no existe"
        
        conexion = base_datos("parcialDB")
        if conexion is None:
            return "Error: No se pudo conectar a la base de datos parcialDB."

        cursor = conexion.cursor()

        # Usar pandas para leer el CSV
        df = pd.read_csv(archivo, encoding='utf-8')
        
        print(f"Archivo CSV leído: {len(df)} filas")
        print(f"Columnas disponibles: {list(df.columns)}")
        
        # Preparar la consulta de inserción
        insert_query = """
        INSERT INTO productos (material, descripcion, fabricante, modificado) 
        VALUES (%s, %s, %s, %s)
        """
        
        filas_insertadas = 0
        
        for index, row in df.iterrows():
            try:
                # Usar los nombres de columnas reales del archivo
                material = str(row.get('Material', ''))[:100] if pd.notna(row.get('Material')) else ''
                descripcion = str(row.get('Texto breve de material', ''))[:255] if pd.notna(row.get('Texto breve de material')) else ''
                fabricante = str(row.get('Fabricante', ''))[:100] if pd.notna(row.get('Fabricante')) else ''
                
                # Manejar la fecha modificado usando el nombre real de la columna
                modificado_str = str(row.get('Últ.mod.', '')) if pd.notna(row.get('Últ.mod.')) else None
                if modificado_str and modificado_str != 'nan':
                    # Intentar convertir la fecha (tomar solo los primeros 10 caracteres YYYY-MM-DD)
                    try:
                        from datetime import datetime
                        fecha_parte = modificado_str[:10]  # Tomar solo YYYY-MM-DD
                        modificado = datetime.strptime(fecha_parte, '%Y-%m-%d').date()
                    except:
                        continue  # Saltar filas con fechas inválidas
                else:
                    continue  # Saltar filas sin fecha
                
                # Insertar los datos
                cursor.execute(insert_query, (material, descripcion, fabricante, modificado))
                filas_insertadas += 1
                
            except Exception as row_err:
                print(f"Error en fila {index}: {row_err}")
                continue

        conexion.commit()
        cursor.close()
        conexion.close()

        return f"Datos cargados exitosamente. Filas insertadas: {filas_insertadas} de {len(df)} filas totales"
    
    except Exception as err:
        return f"Error cargando datos: {err}"
    


def grafico_top_fabricantes():
    """
    Hace una consulta a la base de datos parcialDB para obtener los 10 fabricantes
    con más productos y genera un gráfico de barras.
    Devuelve un mensaje indicando el resultado de la operación.
    """
    try:
        conexion = base_datos("parcialDB")
        if conexion is None:
            return "Error: No se pudo conectar a la base de datos parcialDB."
        
        # Consulta para obtener top 10 fabricantes
        sql = """
        SELECT fabricante, COUNT(*) as cantidad
        FROM productos 
        WHERE fabricante IS NOT NULL AND fabricante != ''
        GROUP BY fabricante 
        ORDER BY cantidad DESC 
        LIMIT 10;
        """
        
        df = pd.read_sql_query(sql, conexion)
        conexion.close()
        
        # Crear gráfico de barras
        plt.figure(figsize=(12, 6))
        plt.bar(df['fabricante'], df['cantidad'])
        plt.title('Top 10 Fabricantes por Cantidad de Productos')
        plt.xlabel('Fabricante')
        plt.ylabel('Cantidad de Productos')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.show()
        
        return f"Gráfico generado exitosamente. Top fabricante: {df.iloc[0]['fabricante']} con {df.iloc[0]['cantidad']} productos"
        
    except Exception as err:
        return f"Error generando gráfico: {err}"


def grafico_altas_por_mes():
    """
    Gráfico de líneas mostrando altas por mes.
    """
    conexion = None
    try:
        conexion = base_datos("parcialDB")
        if conexion is None:
            return "Error: No se pudo conectar a la base de datos parcialDB."
        
        sql = """
        SELECT 
            YEAR(modificado)  AS año,
            MONTH(modificado) AS mes,
            COUNT(*)          AS cantidad
        FROM productos 
        WHERE modificado IS NOT NULL
        GROUP BY YEAR(modificado), MONTH(modificado)
        ORDER BY año, mes;
        """
        df = pd.read_sql_query(sql, conexion)

        if df.empty:
            return "No hay datos para graficar."

        # Etiqueta año-mes
        df["mes_año"] = df["año"].astype(str) + "-" + df["mes"].astype(int).astype(str).str.zfill(2)

        # Eje X: posiciones y etiquetas
        n = len(df)
        x = list(range(n))
        step = max(1, n // 10)   # como mucho ~10 etiquetas
        tick_pos = list(range(0, n, step))
        tick_labels = df["mes_año"].iloc[::step].astype(str).tolist()

        # Gráfico
        plt.figure(figsize=(12, 6))
        plt.plot(x, df["cantidad"].astype(float).tolist(), marker="o")
        plt.title("Evolución de Productos Modificados por Mes")
        plt.xlabel("Período")
        plt.ylabel("Cantidad de Productos")
        plt.xticks(tick_pos, tick_labels, rotation=45)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()

        return f"Gráfico generado exitosamente. {n} períodos analizados."
    except Exception as err:
        return f"Error generando gráfico: {err}"
    finally:
        if conexion is not None:
            try:
                conexion.close()
            except Exception:
                pass



def grafico_top_materiales():
    """
    Gráfico de pastel con los top materiales (por descripción).
    """
    try:
        conexion = base_datos("parcialDB")
        if conexion is None:
            return "Error: No se pudo conectar a la base de datos parcialDB."
        
        # Consulta SQL
        sql = """
        SELECT 
            SUBSTRING(descripcion, 1, 20) AS tipo_material,
            COUNT(*) AS cantidad
        FROM productos 
        WHERE descripcion IS NOT NULL AND descripcion <> ''
        GROUP BY SUBSTRING(descripcion, 1, 20)
        ORDER BY cantidad DESC 
        LIMIT 8;
        """

        df = pd.read_sql_query(sql, conexion)

        if df.empty:
            return "No hay datos para graficar."

        # Convertir Series a listas para Pylance/matplotlib
        labels = df["tipo_material"].astype(str).tolist()
        sizes  = df["cantidad"].astype(float).tolist()

        # Gráfico de pastel
        plt.figure(figsize=(10, 8))
        plt.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90)
        plt.title("Distribución de Tipos de Materiales (Top 8)")
        plt.axis("equal")   # círculo perfecto
        plt.tight_layout()
        plt.show()

        return f"Gráfico generado exitosamente. {len(df)} categorías mostradas."
    
    except Exception as err:
        return f"Error generando gráfico: {err}"
    
    finally:
        if conexion is not None:
            try:
                conexion.close()
            except Exception:
                pass


def histograma_obsolescencia():
    """
    Histograma de obsolescencia de productos (días desde última modificación)
    """
    try:
        conexion = base_datos("parcialDB")
        if conexion is None:
            return "Error: No se pudo conectar a la base de datos parcialDB."
        
        # Consulta para calcular días desde última modificación
        sql = """
        SELECT DATEDIFF(CURDATE(), modificado) AS dias_obsolescencia
        FROM productos
        WHERE modificado IS NOT NULL;
        """

        df = pd.read_sql_query(sql, conexion)
        conexion.close()

        # Crear histograma
        plt.figure(figsize=(10, 6))
        plt.hist(df['dias_obsolescencia'], bins=30, edgecolor='black', alpha=0.7)
        plt.title('Histograma de Obsolescencia de Productos')
        plt.xlabel('Días desde última modificación')
        plt.ylabel('Cantidad de Productos')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()
        
        promedio_dias = df['dias_obsolescencia'].mean()
        return f"Histograma generado exitosamente. Promedio de obsolescencia: {promedio_dias:.1f} días"
        
    except Exception as err:
        return f"Error generando gráfico: {err}"
    
# ========================================

def ejecutar_script_sql(archivo):
    """
    Ejecuta un archivo .sql contra MySQL sin usar 'multi'.
    Lee y ejecuta cada sentencia separada por ';' respetando comillas y backticks.
    Credenciales embebidas en la función.
    """
    conn = motor_mariadb()
    if conn is None:
        return "Error: No se pudo conectar al motor MariaDB."
    cur = conn.cursor()

    # 3) Leer archivo (utf-8-sig por si trae BOM)
    try:
        with open(archivo, "r", encoding="utf-8-sig") as f:
            sql_script = f.read()
    except Exception as e:
        cur.close(); conn.close()
        return f"Error leyendo el archivo: {e}"

    # 5) Split seguro por ';' (respeta ' " ` y escapes)
    def _split_sql(sql: str):
        stmts, buf = [], []
        in_str = None      # "'", '"', "`" o None
        esc = False        # escape con \
        for ch in sql:
            buf.append(ch)
            if in_str:
                if esc:
                    esc = False
                elif ch == "\\":
                    esc = True
                elif ch == in_str:
                    in_str = None
            else:
                if ch in ("'", '"', "`"):
                    in_str = ch
                elif ch == ";":
                    stmt = "".join(buf).strip().rstrip(";").strip()
                    if stmt:
                        stmts.append(stmt)
                    buf = []
        tail = "".join(buf).strip()
        if tail:
            stmts.append(tail)
        return stmts

    statements = _split_sql(sql_script)

    # 6) Ejecutar sentencias en orden
    try:
        for stmt in statements:
            cur.execute(stmt)
            # Commit para DDL/DML y por seguridad en cambios de contexto
            if stmt[:6].upper() in ("INSERT", "UPDATE", "DELETE", "CREATE", "DROP  ", "ALTER ", "REPLAC", "TRUNCA", "RENAME", "GRANT ", "REVOKE", "USE   "):
                conn.commit()
        # Commit final por si quedó algo pendiente
        conn.commit()
    except Exception as e:
        try:
            conn.rollback()
        except Exception:
            pass
        cur.close(); conn.close()
        return f"Error ejecutando script SQL: {e}"

    # 7) Cerrar y devolver
    cur.close()
    conn.close()
    return "Script SQL ejecutado exitosamente"



def consulta_salario_superior_promedio():
    """ 
    Usa la funcion base_datos para conectarse a la base de datos 'recursos_humanos'
    y ejecuta una consulta para obtener los nombres, apellidos y salarios de los empleados
    cuyo salario es superior al salario promedio de todos los empleados.
    Devuelve los resultados en un DataFrame formateado como string.
    """
    try:
        conn = base_datos("recursos_humanos")
        if conn is None:
            return "Error: No se pudo conectar a la base de datos 'recursos_humanos'."
        with conn.cursor() as cur:
            sql = """
                SELECT nombres, apellidos, salario
                FROM empleados
                WHERE salario > (SELECT AVG(salario) FROM empleados);
                """
            cur.execute(sql)
            resultados = cur.fetchall()
                
            if not resultados:
                return "No se encontraron empleados con salario superior al promedio."
                
                # Crear DataFrame para mejor visualización
            df = pd.DataFrame(resultados, columns=['Nombres', 'Apellidos', 'Salario'])
            return df.to_string(index=False)
    except Exception as err:
        return f"Error en la consulta: {err}"
    