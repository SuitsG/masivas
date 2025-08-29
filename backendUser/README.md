# Proyecto: Base de Datos Masivas con Docker y MySQL

## Requisitos previos

- Tener instalado [Docker](https://docs.docker.com/get-docker/) y [Docker Compose](https://docs.docker.com/compose/install/) en tu sistema.

## Inicialización del proyecto

1. **Clona el repositorio** (si aplica) y abre la carpeta del proyecto en tu terminal.

2. **Construye y ejecuta el contenedor**:

   ```sh
   docker-compose up --build
   ```

   Esto creará una imagen basada en Ubuntu, instalará MySQL y configurará un usuario y contraseña para acceder a la base de datos.

## Acceso a la base de datos MySQL

Una vez el contenedor esté en ejecución, puedes conectarte a MySQL desde tu terminal local usando el siguiente comando:

```sh
mysql -h 127.0.0.1 -P 3306 -u admin -p
```

Cuando se solicite la contraseña, ingresa:

```
admin123
```

## Credenciales de la base de datos

- **Usuario:** `admin`
- **Contraseña:** `admin123`
- **Host:** `127.0.0.1`
- **Puerto:** `3306`

## Ejemplo de conexión

```sh
mysql -h 127.0.0.1 -P 3306 -u admin -p
# Password: admin123
```

---

**Notas:**
- El contenedor expone el puerto 3306 para conexiones externas.
- El usuario `admin` tiene todos los privilegios sobre todas las bases de datos.
- Si tienes problemas de conexión, asegúrate de que Docker esté corriendo y que el puerto 3306 no esté bloqueado por tu firewall.
