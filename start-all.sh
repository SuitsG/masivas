#!/bin/bash
# Script para levantar AMBOS servicios en paralelo en Mac/Linux

echo "=== INICIANDO APLICACION COMPLETA ==="

# Función para limpiar procesos al salir
cleanup() {
    echo ""
    echo "Deteniendo servicios..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    wait $BACKEND_PID $FRONTEND_PID 2>/dev/null
    echo "Servicios detenidos."
    exit 0
}

# Configurar trap para limpiar al recibir SIGINT (Ctrl+C)
trap cleanup SIGINT

# Ejecutar backend en segundo plano
echo "Iniciando backend..."
./start-backend.sh &
BACKEND_PID=$!

# Esperar un poco antes de iniciar frontend
echo "Esperando 5 segundos antes de iniciar frontend..."
sleep 5

# Ejecutar frontend en segundo plano
echo "Iniciando frontend..."
./start-frontend.sh &
FRONTEND_PID=$!

echo "=== SERVICIOS INICIADOS ==="
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "Para detener todos los servicios, presiona Ctrl+C"
echo ""

# Esperar indefinidamente hasta que se presione Ctrl+C
wait $BACKEND_PID $FRONTEND_PID
