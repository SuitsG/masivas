#!/bin/bash
# Script para levantar el frontend (Python Flask) en Mac/Linux

echo "=== INICIANDO FRONTEND (APLICACION PYTHON) ==="

# Cambiar al directorio del frontend
cd frontendUser

# Verificar si Python está instalado
echo "Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 no está instalado."
    exit 1
fi

# Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo "Creando entorno virtual..."
    python3 -m venv venv
else
    echo "Entorno virtual ya existe."
fi

# Activar entorno virtual
echo "Activando entorno virtual..."
source venv/bin/activate

# Instalar/actualizar requirements
echo "Instalando dependencias..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "Warning: No se encontró requirements.txt"
fi

# Ejecutar la aplicación Flask
echo "Iniciando aplicación Flask..."
if [ -f "app.py" ]; then
    python app.py
else
    echo "Error: No se encontró app.py"
    exit 1
fi

echo "=== FRONTEND INICIADO ==="
