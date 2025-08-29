#!/bin/bash
# Script para levantar el backend (Docker containers) en Mac/Linux

echo "=== INICIANDO BACKEND (CONTENEDORES DOCKER) ==="

# Cambiar al directorio del backend
cd backendUser

# Verificar si Docker está ejecutándose
echo "Verificando Docker..."
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker no está ejecutándose. Por favor, inicia Docker Desktop primero."
    exit 1
fi

# Ejecutar docker-compose
echo "Construyendo y levantando contenedores..."
docker-compose up --build

echo "=== BACKEND INICIADO ==="
