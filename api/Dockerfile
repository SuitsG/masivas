FROM ubuntu

ENV DEBIAN_FRONTEND=noninteractive


# Actualizar sistema
RUN apt update && apt upgrade -y

# Instalar dependencias de compilación para mariadb
RUN apt install -y build-essential libmariadb-dev-compat libmariadb-dev

# Instalar MariaDB client y dependencias del sistema
RUN apt install -y mariadb-client

# Instalar dependencias de Python y PostgreSQL
RUN apt install -y python3 python3-pip python3-flask python3-requests python3-psycopg2

# Instalar paquetes Python para conectividad (solo mysql-connector-python)
RUN apt install mysql-connector-python

# Crear directorio de trabajo
WORKDIR /app

# Copiar el código de la API
COPY api.py /app/

# Exponer el puerto
EXPOSE 4000

# Comando para ejecutar la aplicación
CMD ["python3", "api.py"]