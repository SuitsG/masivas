# Script para levantar el backend (Docker containers)
Write-Host "=== INICIANDO BACKEND (CONTENEDORES DOCKER) ===" -ForegroundColor Green

# Cambiar al directorio del backend
Set-Location "backendUser"

# Verificar si Docker está ejecutándose
Write-Host "Verificando Docker..." -ForegroundColor Yellow
if (-not (Get-Process "Docker Desktop" -ErrorAction SilentlyContinue)) {
    Write-Host "Error: Docker Desktop no está ejecutándose. Por favor, inicia Docker Desktop primero." -ForegroundColor Red
    exit 1
}

# Ejecutar docker-compose
Write-Host "Construyendo y levantando contenedores..." -ForegroundColor Yellow
docker-compose up --build

Write-Host "=== BACKEND INICIADO ===" -ForegroundColor Green
