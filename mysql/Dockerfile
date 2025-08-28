FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Actualiza paquetes
RUN apt-get update && apt-get -y upgrade

# Instala MariaDB + Python + dependencias
RUN apt-get install -y \
    mariadb-server mariadb-client \
    python3 python3-pip python3-dev libssl-dev \
    python3-mysql.connector

# Copia tus archivos
COPY hoja_vida.sql /tmp/hoja_vida.sql
COPY scripts.py /tmp/scripts.py
COPY nueva_db.csv /tmp/nueva_db.csv

# Configuración MariaDB: permitir conexiones remotas
RUN sed -i "s/^bind-address\s*=.*/bind-address = 0.0.0.0/" /etc/mysql/mariadb.conf.d/50-server.cnf

# Inicializa la base de datos y crea el usuario
RUN service mariadb start && \
    mariadb -e "CREATE USER 'admin'@'%' IDENTIFIED BY 'admin123';" && \
    mariadb -e "GRANT ALL PRIVILEGES ON *.* TO 'admin'@'%' WITH GRANT OPTION;" && \
    mariadb -e "FLUSH PRIVILEGES;" && \
    mariadb < /tmp/hoja_vida.sql && \
    service mariadb stop

# Expone el puerto por defecto
EXPOSE 3306

# Mantiene MariaDB corriendo
CMD ["mysqld_safe"]
