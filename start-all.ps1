# Script para levantar AMBOS servicios en paralelo
Write-Host "=== INICIANDO APLICACION COMPLETA ===" -ForegroundColor Cyan

# Función para ejecutar backend en proceso separado
$backendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    & ".\start-backend.ps1"
}

# Esperar un poco antes de iniciar frontend
Write-Host "Esperando 5 segundos antes de iniciar frontend..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Función para ejecutar frontend en proceso separado
$frontendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    & ".\start-frontend.ps1"
}

Write-Host "=== SERVICIOS INICIADOS ===" -ForegroundColor Cyan
Write-Host "Backend Job ID: $($backendJob.Id)" -ForegroundColor Yellow
Write-Host "Frontend Job ID: $($frontendJob.Id)" -ForegroundColor Yellow
Write-Host ""
Write-Host "Para ver logs del backend: Receive-Job $($backendJob.Id) -Keep" -ForegroundColor Yellow
Write-Host "Para ver logs del frontend: Receive-Job $($frontendJob.Id) -Keep" -ForegroundColor Yellow
Write-Host ""
Write-Host "Para detener servicios: Stop-Job $($backendJob.Id),$($frontendJob.Id); Remove-Job $($backendJob.Id),$($frontendJob.Id)" -ForegroundColor Yellow

# Mantener el script ejecutándose
Write-Host "Presiona Ctrl+C para detener todos los servicios..." -ForegroundColor Green
try {
    while ($true) {
        Start-Sleep -Seconds 1
    }
} finally {
    Write-Host "Deteniendo servicios..." -ForegroundColor Red
    Stop-Job $backendJob.Id, $frontendJob.Id -ErrorAction SilentlyContinue
    Remove-Job $backendJob.Id, $frontendJob.Id -ErrorAction SilentlyContinue
}
