FROM ubuntu


# Actualiza la imagen base de Ubuntu
RUN apt update && apt -y upgrade

# Instala MySQL
RUN apt-get update && apt-get install -y mysql-server

COPY hojaVida.sql /tmp/hojaVida.sql

# Inicializa el servicio de MySQL
# Crea usuario y contraseña en MySQL
RUN service mysql start && \
    mysql -e "CREATE USER 'admin'@'%' IDENTIFIED WITH mysql_native_password BY 'admin123';" && \
    mysql -e "GRANT ALL PRIVILEGES ON *.* TO 'admin'@'%' WITH GRANT OPTION;" && \
    mysql -e "FLUSH PRIVILEGES;" && \
    mysql -e "SOURCE /tmp/hojaVida.sql;" && \
    service mysql stop

# Comando para permitir conexiones remotas (opcional)
RUN sed -i "s/^bind-address\s*=.*/bind-address = 0.0.0.0/" /etc/mysql/mysql.conf.d/mysqld.cnf
# Expone el puerto por defecto de MySQL
EXPOSE 3306

# Mantiene el servicio de MySQL en ejecución
CMD ["mysqld_safe"]