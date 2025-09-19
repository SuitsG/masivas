# 🎯 Masivas Project

## 👥 Autores
- **Daniel Yesid Casallas Páez** 👨‍💻
- **Laura Tatiana Bernal Yanquen** 👩‍💻

## 🚀 Comandos de Inicio

> 📋 **Prerrequisito:** Asegúrate de tener Docker instalado e iniciado antes de continuar.

### 🏠 Raíz del proyecto
Para iniciar el proyecto completo:
```bash
docker-compose up --build
```

### 🗄️ Acceso a MySQL/MariaDB
Conecta a la base de datos con el siguiente comando:
```bash
mysql -h 127.16.0.1 -P 4001 -u admin -p
```
> ⚠️ **Nota:** Si el comando no funciona, verificar las variables de entorno.

### 🐳 Acceso a Contenedores
Para ingresar al contenedor de pandas:
```bash
docker exec -it pandas bash
```

### 📊 Configuración de Notebooks
Para trabajar con Jupyter notebooks:
1. 📦 Instala la extensión **Dev Containers** en VS Code
2. 🔄 Haz clic en **"Reopen in Container"** para abrir en el entorno de pandas
3. ✅ Ahora podrás usar el kernel del contenedor de pandas


## 🧹 Limpieza de Archivos

> ⚠️ **Importante:** Antes de ejecutar el notebook, elimina los archivos de limpieza existentes para evitar errores durante la ejecución.

### 📝 Pasos para la limpieza:
1. 🗑️ Localiza y elimina todos los archivos generados previamente
2. ✨ Ejecuta el notebook desde cero para una experiencia sin errores
3. 🔄 Esto permitirá regenerar todos los archivos de manera correcta

> 💡 **Tip:** Los archivos ya existentes pueden causar conflictos. Una limpieza previa garantiza un funcionamiento óptimo.

---
*¡Happy coding! 💻*