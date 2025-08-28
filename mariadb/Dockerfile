FROM ubuntu

# Actualiza la imagen base de Ubuntu
RUN apt update && apt -y upgrade

# Configura para instalación no interactiva
ENV DEBIAN_FRONTEND=noninteractive

# Instala MariaDB
RUN apt-get update && apt-get install -y mariadb-server

COPY factura_db.sql /tmp/factura_db.sql
# Configura MariaDB para permitir conexiones remotas
RUN sed -i 's/bind-address.*=.*/bind-address = 0.0.0.0/' /etc/mysql/mariadb.conf.d/50-server.cnf || \
    echo 'bind-address = 0.0.0.0' >> /etc/mysql/mariadb.conf.d/50-server.cnf

# Script de inicialización
RUN service mariadb start && \
    mariadb -e "CREATE USER 'admin'@'%' IDENTIFIED BY 'admin123';" && \
    mariadb -e "GRANT ALL PRIVILEGES ON *.* TO 'admin'@'%' WITH GRANT OPTION;" && \
    mariadb -e "FLUSH PRIVILEGES;" && \
    mariadb -e "SOURCE /tmp/factura_db.sql;" && \
    service mariadb stop

# Expone el puerto por defecto de MariaDB
EXPOSE 3306

# Comando para mantener MariaDB en ejecución
CMD ["mysqld_safe"]