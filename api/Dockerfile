FROM ubuntu

# Actualizar sistema
RUN apt update && apt upgrade -y

# Instalar dependencias de Python y PostgreSQL
RUN apt install -y python3 python3-pip python3-flask python3-requests python3-psycopg2

# Crear directorio de trabajo
WORKDIR /app

# Copiar el código de la API
COPY api.py /app/

# Exponer el puerto
EXPOSE 4000

# Comando para ejecutar la aplicación
CMD ["python3", "api.py"]