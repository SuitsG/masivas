import mysql.connector
import csv

conexion = mysql.connector.connect(
    host="127.0.0.1",
    user="admin",
    password="admin123",
    database="hoja_vida",
    port=3306
)

sentencia = conexion.cursor()

# Leer el archivo CSV una sola vez y almacenar los datos
with open('nueva_db.csv', encoding='utf-8') as archivo:
    contenido = list(csv.reader(archivo))

# Extraer países únicos
pais = set()
for fila in contenido:
    pais.add((fila[0], fila[1]))

print(pais)

# Insertar países
for paises in pais:
    print(paises)
    sentencia.execute("INSERT INTO pais (nombre, nacionalidad) VALUES (%s, %s)", (paises[0], paises[1]))

# Insertar estados
for fila in contenido:
    sentencia.execute("""
        INSERT INTO estado (nombre, pais_id)
        VALUES (%s, (SELECT pais_id FROM pais WHERE nombre = %s))
    """, (fila[2], fila[0]))

# Insertar ciudades
for fila in contenido:
    sentencia.execute("""
        INSERT INTO ciudad (nombre, estado_id)
        VALUES (%s, (SELECT estado_id FROM estado WHERE nombre = %s))
    """, (fila[3], fila[2]))

# ==============================
# INSERTS PARA persona
# ==============================
personas_data = [
    ('Carlos Andrés','Pérez','Gómez','CC','1001001','M','COL','Colombia','Cundinamarca','Bogotá','1990-05-12','Calle 123 #45-67','Colombia','Cundinamarca','Bogotá','3101234567','carlos.perez@email.com'),
    ('María Fernanda','López','Rodríguez','CC','1001002','F','COL','Colombia','Antioquia','Medellín','1992-08-21','Carrera 12 #34-56','Colombia','Antioquia','Medellín','3152345678','maria.lopez@email.com'),
    ('Juan Sebastián','Martínez','Suárez','CC','1001003','M','COL','Colombia','Valle','Cali','1985-03-10','Av. 5 #67-89','Colombia','Valle','Cali','3009876543','juan.martinez@email.com'),
    ('Ana Sofía','Ramírez','Castro','CE','1001004','F','ECU','Ecuador','Pichincha','Quito','1995-12-01','Calle Real #12-90','Colombia','Atlántico','Barranquilla','3224567890','ana.ramirez@email.com'),
    ('David','García','Hernández','PAS','P123456','M','ESP','España','Madrid','Madrid','1988-07-15','Calle Mayor 10','Colombia','Santander','Bucaramanga','3011231234','david.garcia@email.com'),
    ('Laura','Moreno','Jiménez','CC','1001005','F','COL','Colombia','Santander','Bucaramanga','1993-01-22','Cl 45 #12-34','Colombia','Santander','Bucaramanga','3202223344','laura.moreno@email.com'),
    ('Felipe','Torres','Salazar','CC','1001006','M','COL','Colombia','Caldas','Manizales','1991-09-11','Carrera 67 #11-90','Colombia','Caldas','Manizales','3104445566','felipe.torres@email.com'),
    ('Camila','Ortega','Ruiz','CE','1001007','F','PER','Perú','Lima','Lima','1997-02-17','Av. Central 50','Colombia','Cundinamarca','Chía','3227778899','camila.ortega@email.com'),
    ('Andrés','Vargas','Londoño','CC','1001008','M','COL','Colombia','Tolima','Ibagué','1989-04-03','Cl 90 #20-30','Colombia','Tolima','Ibagué','3115556677','andres.vargas@email.com'),
    ('Natalia','Mejía','Córdoba','CC','1001009','F','COL','Colombia','Risaralda','Pereira','1994-10-19','Carrera 8 #40-22','Colombia','Risaralda','Pereira','3006667788','natalia.mejia@email.com')
]

for persona in personas_data:
    sentencia.execute("""
        INSERT INTO persona (nombres, primer_apellido, segundo_apellido, tipo_documento, numero_documento, sexo, nacionalidad, 
                           pais_nacimiento_id, estado_nacimiento_id, ciudad_nacimiento_id, fecha_nacimiento, direccion, 
                           pais_residencia_id, estado_residencia_id, ciudad_residencia_id, telefono, email)
        VALUES (%s, %s, %s, %s, %s, %s, %s, 
                (SELECT pais_id FROM pais WHERE nombre = %s),
                (SELECT estado_id FROM estado WHERE nombre = %s),
                (SELECT ciudad_id FROM ciudad WHERE nombre = %s),
                %s, %s,
                (SELECT pais_id FROM pais WHERE nombre = %s),
                (SELECT estado_id FROM estado WHERE nombre = %s),
                (SELECT ciudad_id FROM ciudad WHERE nombre = %s),
                %s, %s)
    """, persona)

# ==============================
# INSERTS PARA distrito_militar
# ==============================
distritos_data = [('01',), ('02',), ('03',), ('04',), ('05',), ('06',), ('07',), ('08',), ('09',), ('10',)]

for distrito in distritos_data:
    sentencia.execute("INSERT INTO distrito_militar (nombre) VALUES (%s)", distrito)

# ==============================
# INSERTS PARA libreta_militar
# ==============================
libretas_data = [
    ('1001001','Primera','LM1001','01'),
    ('1001003','Segunda','LM1002','02'),
    ('P123456','Primera','LM1003','03'),
    ('1001006','Segunda','LM1004','04'),
    ('1001008','Primera','LM1005','05')
]

for libreta in libretas_data:
    sentencia.execute("""
        INSERT INTO libreta_militar (persona_id, clase, numero, distrito_id)
        VALUES ((SELECT persona_id FROM persona WHERE numero_documento = %s), %s, %s,
                (SELECT distrito_id FROM distrito_militar WHERE nombre = %s))
    """, libreta)

# ==============================
# INSERTS PARA idioma
# ==============================
idiomas_data = [
    ('1001001','Inglés','Bien','Muy Bien','Regular'),
    ('1001002','Francés','Regular','Regular','Regular'),
    ('1001003','Inglés','Muy Bien','Muy Bien','Bien'),
    ('1001004','Alemán','Regular','Bien','Regular'),
    ('P123456','Inglés','Bien','Bien','Bien'),
    ('1001005','Portugués','Muy Bien','Bien','Regular'),
    ('1001006','Inglés','Muy Bien','Muy Bien','Muy Bien'),
    ('1001007','Francés','Bien','Bien','Regular'),
    ('1001008','Inglés','Regular','Bien','Regular'),
    ('1001009','Italiano','Bien','Regular','Regular')
]

for idioma in idiomas_data:
    sentencia.execute("""
        INSERT INTO idioma (persona_id, nombre, habla, lee, escribe)
        VALUES ((SELECT persona_id FROM persona WHERE numero_documento = %s), %s, %s, %s, %s)
    """, idioma)

# ==============================
# INSERTS PARA educacion_basica
# ==============================
educacion_basica_data = [
    ('1001001',11,'Bachiller Académico','2007-11-30'),
    ('1001002',11,'Bachiller Comercial','2009-11-30'),
    ('1001003',11,'Bachiller Técnico','2003-11-30'),
    ('1001004',10,'Bachiller en Ciencias','2011-11-30'),
    ('P123456',11,'Bachiller Académico','2005-11-30'),
    ('1001005',11,'Bachiller Técnico','2010-11-30'),
    ('1001006',11,'Bachiller Académico','2008-11-30'),
    ('1001007',11,'Bachiller Comercial','2013-11-30'),
    ('1001008',11,'Bachiller Técnico','2006-11-30'),
    ('1001009',11,'Bachiller Académico','2012-11-30')
]

for educacion in educacion_basica_data:
    sentencia.execute("""
        INSERT INTO educacion_basica (persona_id, ultimo_grado_aprobado, titulo_obtenido, fecha_grado)
        VALUES ((SELECT persona_id FROM persona WHERE numero_documento = %s), %s, %s, %s)
    """, educacion)

# ==============================
# INSERTS PARA educacion_superior
# ==============================
educacion_superior_data = [
    ('1001001','UN','Ingeniería de Sistemas',10,True,'2012-12-15',None),
    ('1001002','ES','Especialización en Finanzas',2,False,None,None),
    ('1001003','MG','Maestría en Educación',4,False,None,None),
    ('1001004','TC','Técnico en Diseño Gráfico',6,True,'2015-06-20',None),
    ('P123456','DOC','Doctorado en Ciencias Sociales',8,True,'2020-07-30',None),
    ('1001005','UN','Administración de Empresas',8,True,'2016-11-10',None),
    ('1001006','TL','Tecnología en Mecatrónica',5,False,None,None),
    ('1001007','TE','Tecnología Especializada en Marketing',6,True,'2018-09-12',None),
    ('1001008','UN','Medicina',12,True,'2014-12-01','MP12345'),
    ('1001009','ES','Especialización en Derecho Laboral',2,False,None,None)
]

for educacion in educacion_superior_data:
    sentencia.execute("""
        INSERT INTO educacion_superior (persona_id, modalidad, nombre_estudio, semestre_aprobado, graduado, fecha_terminacion, numero_tarjeta)
        VALUES ((SELECT persona_id FROM persona WHERE numero_documento = %s), %s, %s, %s, %s, %s, %s)
    """, educacion)

# ==============================
# INSERTS PARA experiencia_laboral
# ==============================
experiencia_data = [
    ('1001001','PUBLICA','Ministerio de Educación','Colombia','Cundinamarca','Bogotá','contacto@mineducacion.gov.co','6011234567','2013-01-15','2016-12-20','Analista de Sistemas','TI','Cl 26 #69-76',False),
    ('1001002','PRIVADA','Bancolombia','Colombia','Antioquia','Medellín','talento@bancolombia.com','6042345678','2017-03-01','2020-06-30','Asesora Financiera','Comercial','Cl 48 #20-30',False),
    ('1001003','PRIVADA','Grupo Éxito','Colombia','Antioquia','Medellín','rrhh@grupoexito.com','6048765432','2006-05-10','2012-09-15','Coordinador de Ventas','Ventas','Cl 65 #20-45',False),
    ('1001004','PUBLICA','Alcaldía de Quito','Ecuador','Pichincha','Quito','empleo@quito.gob.ec','5932223344','2016-01-10','2018-12-20','Diseñadora Gráfica','Comunicaciones','Av. Amazonas 123',False),
    ('P123456','PRIVADA','BBVA España','España','Madrid','Madrid','empleo@bbva.com','34912345678','2010-02-01','2015-11-01','Analista de Riesgos','Riesgos','Cl Mayor 100',False),
    ('1001005','PRIVADA','Avianca','Colombia','Santander','Bucaramanga','rrhh@avianca.com','6074567890','2016-07-15','2021-03-30','Administradora','Operaciones','Cl 45 #67-89',False),
    ('1001006','PUBLICA','Universidad de Caldas','Colombia','Caldas','Manizales','empleo@ucaldas.edu.co','6067654321','2012-09-01','2018-11-20','Profesor Auxiliar','Académico','Cl 58 #23-12',False),
    ('1001007','PRIVADA','Nestlé Perú','Perú','Lima','Lima','talento@nestle.com','5117654321','2019-01-01','2022-12-31','Analista de Marketing','Marketing','Av. Central 56',False),
    ('1001008','PUBLICA','Hospital San Rafael','Colombia','Tolima','Ibagué','rrhh@sanrafael.org','6082345678','2015-03-01',None,'Médico General','Urgencias','Cl 10 #15-25',True),
    ('1001009','PRIVADA','Nutresa','Colombia','Risaralda','Pereira','empleo@nutresa.com','6063456789','2020-05-01',None,'Abogada Junior','Jurídica','Cl 33 #14-55',True)
]

for experiencia in experiencia_data:
    sentencia.execute("""
        INSERT INTO experiencia_laboral (persona_id, sector, empresa, pais, departamento, municipio, correo_entidad, telefonos, fecha_ingreso, fecha_retiro, cargo_contrato, dependencia, direccion_entidad, es_actual)
        VALUES ((SELECT persona_id FROM persona WHERE numero_documento = %s), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, experiencia)

# Confirmar todas las transacciones
conexion.commit()
print("Todas las inserciones han sido completadas exitosamente.")

# Cerrar cursor y conexión
sentencia.close()
conexion.close()

