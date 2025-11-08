@echo off
REM Script de inicio rápido para TextLab Backend (Windows)

echo ========================================
echo   TextLab Backend - Inicio Rapido
echo ========================================
echo.

REM Verificar si Docker está instalado
where docker >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker no esta instalado o no esta en el PATH.
    echo.
    echo Por favor:
    echo   1. Instala Docker Desktop desde: https://www.docker.com/products/docker-desktop
    echo   2. Reinicia tu computadora despues de instalar
    echo   3. Asegurate de que Docker Desktop este corriendo
    pause
    exit /b 1
)

REM Verificar si Docker está corriendo
echo [INFO] Verificando Docker...
docker ps >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker no esta corriendo.
    echo.
    echo Por favor:
    echo   1. Abre Docker Desktop desde el menu de inicio
    echo   2. Espera a que aparezca "Docker Desktop is running" en la barra de tareas
    echo   3. Vuelve a ejecutar este script
    echo.
    echo Intentando iniciar Docker Desktop automaticamente...
    start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe" 2>nul
    if %errorlevel% equ 0 (
        echo [INFO] Docker Desktop se esta iniciando. Espera 30 segundos y vuelve a ejecutar este script.
    ) else (
        echo [INFO] No se pudo iniciar Docker Desktop automaticamente.
        echo Por favor inicia Docker Desktop manualmente.
    )
    pause
    exit /b 1
)

echo [OK] Docker esta corriendo.

echo [1/4] Verificando servicios Docker...
docker-compose ps

echo.
echo [2/4] Iniciando servicios (PostgreSQL, Redis, Backend, Celery)...
docker-compose up -d --build

if %errorlevel% neq 0 (
    echo [ERROR] Error al iniciar servicios.
    pause
    exit /b 1
)

echo.
echo [3/4] Esperando que los servicios esten listos...
timeout /t 10 /nobreak >nul

echo.
echo [4/4] Ejecutando migraciones de base de datos...
docker-compose exec -T backend alembic upgrade head

if %errorlevel% neq 0 (
    echo [ADVERTENCIA] Error al ejecutar migraciones. Verifica los logs.
) else (
    echo [OK] Migraciones aplicadas correctamente.
)

echo.
echo ========================================
echo   Servicios iniciados correctamente!
echo ========================================
echo.
echo URLs disponibles:
echo   - API: http://localhost:8000
echo   - Documentacion: http://localhost:8000/docs
echo   - Health Check: http://localhost:8000/health
echo.
echo Para ver los logs:
echo   docker-compose logs -f
echo.
echo Para detener los servicios:
echo   docker-compose down
echo.
pause

