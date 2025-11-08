#!/bin/bash

# Script de inicio rápido para TextLab Backend (Linux/Mac)

set -e

echo "========================================"
echo "  TextLab Backend - Inicio Rapido"
echo "========================================"
echo ""

# Verificar si Docker está corriendo
if ! docker ps > /dev/null 2>&1; then
    echo "[ERROR] Docker no está corriendo. Por favor inicia Docker."
    exit 1
fi

echo "[1/4] Verificando servicios Docker..."
docker-compose ps

echo ""
echo "[2/4] Iniciando servicios (PostgreSQL, Redis, Backend, Celery)..."
docker-compose up -d --build

echo ""
echo "[3/4] Esperando que los servicios estén listos..."
sleep 10

echo ""
echo "[4/4] Ejecutando migraciones de base de datos..."
if docker-compose exec -T backend alembic upgrade head; then
    echo "[OK] Migraciones aplicadas correctamente."
else
    echo "[ADVERTENCIA] Error al ejecutar migraciones. Verifica los logs."
fi

echo ""
echo "========================================"
echo "  Servicios iniciados correctamente!"
echo "========================================"
echo ""
echo "URLs disponibles:"
echo "  - API: http://localhost:8000"
echo "  - Documentación: http://localhost:8000/docs"
echo "  - Health Check: http://localhost:8000/health"
echo ""
echo "Para ver los logs:"
echo "  docker-compose logs -f"
echo ""
echo "Para detener los servicios:"
echo "  docker-compose down"
echo ""

