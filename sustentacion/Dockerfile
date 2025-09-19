FROM mariadb:latest

# Credenciales (mejor pasarlas en runtime; aquí van como ejemplo)
ENV MARIADB_ROOT_PASSWORD=admin1234
ENV MARIADB_USER=admin
ENV MARIADB_PASSWORD=admin1234
ENV MARIADB_DATABASE=bdrh

# Puerto 3310 por configuración
RUN printf "[mysqld]\nport=3310\nbind-address=0.0.0.0\n" > /etc/mysql/conf.d/port.cnf
# Scripts de inicialización (se ejecutan SOLO cuando /var/lib/mysql está vacío)
COPY 01_bdrh_base.sql /docker-entrypoint-initdb.d/01_bdrh_base.sql
COPY 02_bdrh_avanzado.sql /docker-entrypoint-initdb.d/02_bdrh_avanzado.sql

# Forzar ejecución de scripts incluso si el volumen ya existe
RUN chmod +x /docker-entrypoint-initdb.d/*.sql
ENV MARIADB_INITDB_SKIP_TZINFO=1

EXPOSE 3310
# No definas CMD: la imagen ya trae:
# ENTRYPOINT ["docker-entrypoint.sh"]
# CMD ["mysqld"]
