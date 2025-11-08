#!/bin/bash

# Script para detener servicios de TextLab Backend (Linux/Mac)

echo "========================================"
echo "  Deteniendo servicios TextLab Backend"
echo "========================================"
echo ""

docker-compose down

echo ""
echo "Servicios detenidos correctamente."

