FROM ubuntu

ENV DEBIAN_FRONTEND=noninteractive


RUN apt update && apt upgrade -y
RUN apt install -y build-essential libmariadb-dev-compat libmariadb-dev
RUN apt install -y mariadb-client
RUN apt install -y python3 python3-pip python3-flask python3-requests python3-psycopg2
RUN apt install -y python3-mysql.connector

# Crear directorio de trabajo
WORKDIR /app

# Copiar el código de la API
COPY api.py /app/

# Exponer el puerto
EXPOSE 4000

# Comando para ejecutar la aplicación
CMD ["python3", "api.py"]