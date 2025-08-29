# Script para levantar el frontend (Python Flask)
Write-Host "=== INICIANDO FRONTEND (APLICACION PYTHON) ===" -ForegroundColor Green

# Cambiar al directorio del frontend
Set-Location "frontendUser"

# Verificar si Python está instalado
Write-Host "Verificando Python..." -ForegroundColor Yellow
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Error: Python no está instalado o no está en PATH." -ForegroundColor Red
    exit 1
}

# Crear entorno virtual si no existe
if (-not (Test-Path "venv")) {
    Write-Host "Creando entorno virtual..." -ForegroundColor Yellow
    python -m venv venv
} else {
    Write-Host "Entorno virtual ya existe." -ForegroundColor Yellow
}

# Activar entorno virtual
Write-Host "Activando entorno virtual..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Instalar/actualizar requirements
Write-Host "Instalando dependencias..." -ForegroundColor Yellow
if (Test-Path "requirements.txt") {
    pip install -r requirements.txt
} else {
    Write-Host "Warning: No se encontró requirements.txt" -ForegroundColor Yellow
}

# Ejecutar la aplicación Flask
Write-Host "Iniciando aplicación Flask..." -ForegroundColor Yellow
if (Test-Path "app.py") {
    python app.py
} else {
    Write-Host "Error: No se encontró app.py" -ForegroundColor Red
    exit 1
}

Write-Host "=== FRONTEND INICIADO ===" -ForegroundColor Green
