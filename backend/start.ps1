# Script de inicio rápido para TextLab Backend (PowerShell)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  TextLab Backend - Inicio Rapido" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar si Docker está instalado
$dockerPath = Get-Command docker -ErrorAction SilentlyContinue
if (-not $dockerPath) {
    Write-Host "[ERROR] Docker no está instalado o no está en el PATH." -ForegroundColor Red
    Write-Host ""
    Write-Host "Por favor:" -ForegroundColor Yellow
    Write-Host "  1. Instala Docker Desktop desde: https://www.docker.com/products/docker-desktop" -ForegroundColor White
    Write-Host "  2. Reinicia tu computadora después de instalar" -ForegroundColor White
    Write-Host "  3. Asegúrate de que Docker Desktop esté corriendo" -ForegroundColor White
    exit 1
}

# Verificar si Docker está corriendo
Write-Host "[INFO] Verificando Docker..." -ForegroundColor Yellow
try {
    docker ps | Out-Null
    Write-Host "[OK] Docker está corriendo." -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Docker no está corriendo." -ForegroundColor Red
    Write-Host ""
    Write-Host "Por favor:" -ForegroundColor Yellow
    Write-Host "  1. Abre Docker Desktop desde el menú de inicio" -ForegroundColor White
    Write-Host "  2. Espera a que aparezca 'Docker Desktop is running' en la barra de tareas" -ForegroundColor White
    Write-Host "  3. Vuelve a ejecutar este script" -ForegroundColor White
    Write-Host ""
    Write-Host "Intentando iniciar Docker Desktop automáticamente..." -ForegroundColor Yellow
    
    $dockerDesktopPath = "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    if (Test-Path $dockerDesktopPath) {
        Start-Process $dockerDesktopPath
        Write-Host "[INFO] Docker Desktop se está iniciando. Espera 30 segundos y vuelve a ejecutar este script." -ForegroundColor Yellow
    } else {
        Write-Host "[INFO] No se pudo encontrar Docker Desktop. Por favor inicia Docker Desktop manualmente." -ForegroundColor Yellow
    }
    exit 1
}

Write-Host "[1/4] Verificando servicios Docker..." -ForegroundColor Yellow
docker-compose ps

Write-Host ""
Write-Host "[2/4] Iniciando servicios (PostgreSQL, Redis, Backend, Celery)..." -ForegroundColor Yellow
docker-compose up -d --build

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Error al iniciar servicios." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[3/4] Esperando que los servicios estén listos..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host ""
Write-Host "[4/4] Ejecutando migraciones de base de datos..." -ForegroundColor Yellow
docker-compose exec -T backend alembic upgrade head

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Migraciones aplicadas correctamente." -ForegroundColor Green
} else {
    Write-Host "[ADVERTENCIA] Error al ejecutar migraciones. Verifica los logs." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Servicios iniciados correctamente!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "URLs disponibles:" -ForegroundColor White
Write-Host "  - API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "  - Documentación: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "  - Health Check: http://localhost:8000/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "Para ver los logs:" -ForegroundColor White
Write-Host "  docker-compose logs -f" -ForegroundColor Gray
Write-Host ""
Write-Host "Para detener los servicios:" -ForegroundColor White
Write-Host "  docker-compose down" -ForegroundColor Gray
Write-Host ""

