@echo off
REM Script de diagnostico de Docker

echo ========================================
echo   Diagnostico de Docker
echo ========================================
echo.

echo [1] Verificando si Docker esta instalado...
where docker >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Docker encontrado en el PATH
    where docker
) else (
    echo [ERROR] Docker no encontrado en el PATH
    echo.
    echo Posibles causas:
    echo   - Docker Desktop no esta instalado
    echo   - Docker no esta en el PATH del sistema
    echo   - Necesitas reiniciar la terminal despues de instalar Docker
    echo.
    pause
    exit /b 1
)

echo.
echo [2] Verificando si Docker esta corriendo...
docker ps >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Docker esta corriendo correctamente
    echo.
    echo Contenedores activos:
    docker ps
) else (
    echo [ERROR] Docker no esta corriendo
    echo.
    REM Verificar el error especifico
    docker ps 2>&1 | findstr /C:"unable to start" >nul
    if %errorlevel% equ 0 (
        echo [ERROR ESPECIFICO] Docker Desktop is unable to start
        echo.
        echo Este es un error comun. Soluciones:
        echo.
        echo OPCION 1 - Script de reparacion automatica:
        echo   Ejecuta: powershell -ExecutionPolicy Bypass -File fix-docker.ps1
        echo.
        echo OPCION 2 - Solucion manual rapida:
        echo   1. Cierra Docker Desktop completamente
        echo   2. Abre PowerShell como Administrador
        echo   3. Ejecuta: wsl --shutdown
        echo   4. Reinicia Docker Desktop
        echo.
        echo OPCION 3 - Verificar WSL 2:
        echo   1. Abre PowerShell como Administrador
        echo   2. Ejecuta: wsl --install
        echo   3. Reinicia tu computadora
        echo.
    ) else (
        echo Soluciones:
        echo   1. Abre Docker Desktop desde el menu de inicio
        echo   2. Espera a que aparezca "Docker Desktop is running"
        echo   3. Verifica que no haya errores en Docker Desktop
        echo.
    )
    
    REM Intentar iniciar Docker Desktop
    echo Intentando iniciar Docker Desktop...
    start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe" 2>nul
    if %errorlevel% equ 0 (
        echo [INFO] Docker Desktop se esta iniciando...
        echo Espera 30-60 segundos y vuelve a ejecutar este script.
        echo.
        echo Si el problema persiste, ejecuta: fix-docker.ps1
    ) else (
        echo [ERROR] No se pudo iniciar Docker Desktop automaticamente.
        echo Por favor inicia Docker Desktop manualmente.
        echo.
        echo Para reparacion automatica, ejecuta: fix-docker.ps1
    )
    pause
    exit /b 1
)

echo.
echo [3] Verificando Docker Compose...
docker-compose --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Docker Compose esta disponible
    docker-compose --version
) else (
    echo [ADVERTENCIA] Docker Compose no encontrado
    echo Intentando con 'docker compose' (version integrada)...
    docker compose version >nul 2>&1
    if %errorlevel% equ 0 (
        echo [OK] Docker Compose (integrado) esta disponible
        docker compose version
    ) else (
        echo [ERROR] Docker Compose no esta disponible
    )
)

echo.
echo ========================================
echo   Diagnostico completado
echo ========================================
echo.
pause

