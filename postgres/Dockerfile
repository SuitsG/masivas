FROM ubuntu

# Configura para instalación no interactiva
ENV DEBIAN_FRONTEND=noninteractive

# Actualiza la imagen base de Ubuntu
RUN apt-get update && apt-get -y upgrade

# Instala dependencias necesarias
RUN apt-get update && apt-get install -y \
    wget \
    ca-certificates \
    gnupg \
    lsb-release \
    sudo

# Agrega el repositorio oficial de PostgreSQL
RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - && \
    echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list

# Instala PostgreSQL 17
RUN apt-get update && apt-get install -y \
    postgresql-17 \
    postgresql-contrib-17 \
    && rm -rf /var/lib/apt/lists/*

# Configura PostgreSQL para permitir conexiones remotas
RUN echo "host all all 0.0.0.0/0 md5" >> /etc/postgresql/17/main/pg_hba.conf
RUN echo "listen_addresses='*'" >> /etc/postgresql/17/main/postgresql.conf

COPY colombia.sql /tmp/colombia.sql

# Script de inicialización
RUN service postgresql start && \
    sudo -u postgres psql -c "CREATE USER admin WITH PASSWORD 'admin123' SUPERUSER;" && \
    sudo -u postgres psql -f /tmp/colombia.sql && \
    service postgresql stop

# Expone el puerto por defecto de PostgreSQL
EXPOSE 5432

# Cambia al usuario postgres para ejecutar PostgreSQL
USER postgres

# Comando para mantener PostgreSQL en ejecución
CMD ["/usr/lib/postgresql/17/bin/postgres", "-D", "/var/lib/postgresql/17/main", "-c", "config_file=/etc/postgresql/17/main/postgresql.conf"]



