@echo off
REM Script para detener servicios de TextLab Backend (Windows)

echo ========================================
echo   Deteniendo servicios TextLab Backend
echo ========================================
echo.

docker-compose down

echo.
echo Servicios detenidos correctamente.
pause

