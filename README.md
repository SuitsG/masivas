# Aplicación de Base de Datos Masivas

Una aplicación completa que demuestra el manejo de múltiples bases de datos usando Docker, con un frontend desarrollado en Flask y un backend API que conecta a PostgreSQL, MySQL y MariaDB.

## 📋 Descripción

Esta aplicación es un proyecto académico que implementa un sistema de gestión de datos masivos utilizando múltiples sistemas de gestión de bases de datos (SGBD). El proyecto está dividido en tres módulos principales:

- **Módulo Mundo**: Gestión de información geográfica (países, estados, ciudades) usando PostgreSQL
- **Módulo Hoja de Vida**: Sistema de gestión de perfiles profesionales usando MySQL
- **Módulo Historial de Facturas**: Sistema de facturación usando MariaDB

## 🏗️ Arquitectura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │   Databases     │
│   Flask App     │◄──►│   Flask API     │◄──►│   PostgreSQL    │
│   (Puerto 5000) │    │   (Puerto 8080) │    │   MySQL         │
│                 │    │                 │    │   MariaDB       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Componentes Principales

- **Frontend**: Aplicación Flask que sirve como interfaz de usuario y proxy API
- **Backend**: API REST desarrollada en Flask que gestiona las conexiones a las bases de datos
- **Bases de Datos**: Tres contenedores Docker con PostgreSQL, MySQL y MariaDB

## 🚀 Instalación y Configuración

### Prerrequisitos

- Docker y Docker Compose
- Python 3.8+
- PowerShell (Windows) o Bash (Linux/Mac)

### Instalación Rápida

#### Opción 1: Ejecutar Todo (Recomendado)
```powershell
# En Windows
.\start-all.ps1

# En Linux/Mac
./start-all.sh
```

#### Opción 2: Ejecutar Componentes por Separado

**Backend (Bases de datos + API):**
```powershell
# Windows
.\start-backend.ps1

# Linux/Mac
./start-backend.sh
```

**Frontend:**
```powershell
# Windows  
.\start-frontend.ps1

# Linux/Mac
./start-frontend.sh
```

## 🗄️ Bases de Datos

### PostgreSQL - Módulo Mundo
- **Puerto**: 5432 (interno), acceso a través de la API
- **Base de datos**: `mundo`
- **Tablas**: `country`, `city`, `countrylanguage`
- **Funcionalidades**: Consulta de países, ciudades y lenguajes

### MySQL - Módulo Hoja de Vida  
- **Puerto**: 4001 (externo)
- **Base de datos**: `hojaVida`
- **Usuario**: admin / admin123
- **Funcionalidades**: Gestión de perfiles profesionales

### MariaDB - Módulo Historial de Facturas
- **Puerto**: 4003 (externo) 
- **Base de datos**: `tienda`
- **Usuario**: admin / admin123
- **Funcionalidades**: Sistema de facturación y historial

## 🌐 Uso de la Aplicación

### Acceso a la Aplicación
Una vez iniciados todos los servicios, accede a:
- **Frontend**: http://localhost:5000
- **API Backend**: http://localhost:8080

### Módulos Disponibles

#### 1. Módulo Mundo 🌍
- **Ruta**: `/mundo`
- **Funcionalidades**:
  - Cargar todos los países
  - Buscar país por nombre
  - Encontrar ciudades repetidas
  - Consultar información detallada de países

#### 2. Módulo Hoja de Vida 👤
- **Ruta**: `/hojaVida`
- **Funcionalidades**:
  - Gestión de perfiles profesionales
  - Búsqueda y filtrado de candidatos
  - Administración de datos personales

#### 3. Módulo Historial de Facturas 🧾
- **Ruta**: `/historialFactura`
- **Funcionalidades**:
  - Consulta de facturas
  - Historial de transacciones
  - Reportes de ventas

## 📁 Estructura del Proyecto

```
masivas/
├── README.md
├── start-all.ps1/.sh          # Scripts de inicio completo
├── start-backend.ps1/.sh      # Scripts para backend
├── start-frontend.ps1/.sh     # Scripts para frontend
│
├── backendUser/               # Backend y bases de datos
│   ├── docker-compose.yml    # Configuración de contenedores
│   ├── api/
│   │   ├── api.py            # API principal Flask
│   │   └── Dockerfile
│   ├── postgres/             # Configuración PostgreSQL
│   │   ├── Dockerfile
│   │   └── world.sql
│   ├── mysql/                # Configuración MySQL
│   │   ├── Dockerfile
│   │   ├── hoja_vida.sql
│   │   └── nueva_db.csv
│   └── mariadb/              # Configuración MariaDB
│       ├── Dockerfile
│       └── tienda.sql
│
└── frontendUser/             # Frontend Flask
    ├── app.py               # Aplicación principal
    ├── requirements.txt
    ├── static/              # Archivos estáticos
    │   ├── css/
    │   └── js/
    └── templates/           # Plantillas HTML
        ├── base.html
        ├── index.html
        ├── mundo.html
        ├── hoja_vida.html
        └── historial_factura.html
```

## 🛠️ Desarrollo

### Dependencias del Backend
```txt
Flask==2.3.3
psycopg2-binary==2.9.7
mysql-connector-python==8.1.0
requests==2.31.0
```

### Dependencias del Frontend
```txt
Flask==3.0.3
requests==2.32.3
python-dotenv==1.0.1
```

### Variables de Entorno

El proyecto utiliza las siguientes variables de entorno (con valores por defecto):

```env
# API Backend
API_BASE=http://localhost:8080

# PostgreSQL
DB_HOST=postgres
DB_NAME=mundo
DB_USER=admin
DB_PASSWORD=admin123
DB_PORT=5432

# MySQL
MYSQL_HOST=mysql
MYSQL_USER=admin
MYSQL_PASSWORD=admin123
MYSQL_DATABASE=hojaVida
MYSQL_PORT=3306

# MariaDB
MARIADB_HOST=mariadb
MARIADB_USER=admin
MARIADB_PASSWORD=admin123
MARIADB_DATABASE=tienda
MARIADB_PORT=3306
```

## 🐋 Docker

### Servicios Docker
- **postgres**: PostgreSQL para el módulo mundo
- **mysql**: MySQL para hojas de vida
- **mariadb**: MariaDB para facturación
- **api**: Backend Flask API

### Red Docker
Los contenedores se ejecutan en una red personalizada `base_masivas` con IPs estáticas:
- PostgreSQL: 172.18.0.3
- MySQL: 172.18.0.2
- MariaDB: 172.18.0.4
- API: 172.18.0.5

## 🔧 Resolución de Problemas

### Problemas Comunes

1. **Puerto ocupado**: Verificar que los puertos 5000, 8080, 4001, 4003 estén disponibles
2. **Error de conexión a BD**: Esperar unos segundos para que los contenedores se inicialicen completamente
3. **Módulos no cargados**: Verificar que Docker esté ejecutándose y las imágenes se hayan construido correctamente

### Logs y Diagnóstico
```powershell
# Ver logs de Docker
docker-compose -f backendUser/docker-compose.yml logs

# Ver contenedores en ejecución
docker ps

# Reiniciar servicios
docker-compose -f backendUser/docker-compose.yml restart
```

## 📚 API Endpoints

### Módulo Mundo
- `GET /paises` - Obtener todos los países
- `GET /paises/{nombre}` - Buscar país por nombre
- `GET /ciudades-repetidas` - Ciudades con nombres duplicados

### Módulo Hoja de Vida
- `GET /hoja-vida` - Listar perfiles
- `POST /hoja-vida` - Crear perfil
- Endpoints adicionales para gestión de candidatos

### Módulo Facturas
- `GET /facturas` - Historial de facturas
- `GET /facturas/{id}` - Detalle de factura
- Endpoints adicionales para reportes

## 🤝 Contribución

Este es un proyecto académico. Para contribuir:

1. Fork el repositorio
2. Crear una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear un Pull Request

## 📄 Licencia

Este proyecto es para fines educativos y académicos.

## 👥 Autores

- Desarrollo inicial: Proyecto académico de Base de Datos Masivas
- Universidad: UNIMINUTO

---

> **Nota**: Este proyecto está diseñado para demostrar conceptos de bases de datos masivas y arquitecturas multi-SGBD en un entorno académico.
