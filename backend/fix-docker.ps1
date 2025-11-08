# Script avanzado de diagnóstico y reparación de Docker Desktop
# Resuelve el error: "Docker Desktop is unable to start"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Reparador de Docker Desktop" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar si se ejecuta como administrador
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "[ADVERTENCIA] Algunas verificaciones requieren permisos de administrador." -ForegroundColor Yellow
    Write-Host "Para una reparación completa, ejecuta este script como administrador." -ForegroundColor Yellow
    Write-Host ""
}

# Función para verificar si un servicio está corriendo
function Test-ServiceRunning {
    param([string]$ServiceName)
    $service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
    if ($service -and $service.Status -eq 'Running') {
        return $true
    }
    return $false
}

# Función para verificar si WSL está instalado
function Test-WSLInstalled {
    try {
        $wslVersion = wsl --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            return $true
        }
    } catch {
        # Intentar verificar de otra manera
        $wslPath = Get-Command wsl -ErrorAction SilentlyContinue
        return ($null -ne $wslPath)
    }
    return $false
}

# Función para verificar si Hyper-V está habilitado
function Test-HyperVEnabled {
    try {
        $hyperv = Get-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V-All -ErrorAction SilentlyContinue
        if ($hyperv -and $hyperv.State -eq 'Enabled') {
            return $true
        }
    } catch {
        # Si no se puede verificar, asumir que no está habilitado
    }
    return $false
}

# Función para verificar virtualización en BIOS
function Test-VirtualizationEnabled {
    try {
        $vm = Get-ComputerInfo -Property "HyperV*" -ErrorAction SilentlyContinue
        # Verificar si la virtualización está disponible
        $cpu = Get-WmiObject Win32_Processor
        return ($cpu.VirtualizationFirmwareEnabled -or $cpu.SecondLevelAddressTranslationExtensions)
    } catch {
        return $null
    }
}

Write-Host "[1/8] Verificando instalación de Docker..." -ForegroundColor Yellow
$dockerPath = Get-Command docker -ErrorAction SilentlyContinue
if (-not $dockerPath) {
    Write-Host "[ERROR] Docker no está instalado o no está en el PATH." -ForegroundColor Red
    Write-Host ""
    Write-Host "Solución:" -ForegroundColor Yellow
    Write-Host "  1. Descarga Docker Desktop: https://www.docker.com/products/docker-desktop" -ForegroundColor White
    Write-Host "  2. Instálalo y reinicia tu computadora" -ForegroundColor White
    exit 1
}
Write-Host "[OK] Docker está instalado" -ForegroundColor Green
Write-Host ""

Write-Host "[2/8] Verificando estado de Docker Desktop..." -ForegroundColor Yellow
$dockerDesktopProcess = Get-Process "Docker Desktop" -ErrorAction SilentlyContinue
if ($dockerDesktopProcess) {
    Write-Host "[INFO] Docker Desktop está ejecutándose" -ForegroundColor Cyan
} else {
    Write-Host "[INFO] Docker Desktop no está ejecutándose" -ForegroundColor Yellow
}
Write-Host ""

Write-Host "[3/8] Verificando WSL 2..." -ForegroundColor Yellow
if (Test-WSLInstalled) {
    Write-Host "[OK] WSL está instalado" -ForegroundColor Green
    try {
        $wslStatus = wsl --status 2>$null
        Write-Host $wslStatus
    } catch {
        Write-Host "[INFO] No se pudo obtener el estado detallado de WSL" -ForegroundColor Yellow
    }
} else {
    Write-Host "[ERROR] WSL 2 no está instalado" -ForegroundColor Red
    Write-Host ""
    Write-Host "Solución:" -ForegroundColor Yellow
    Write-Host "  1. Abre PowerShell como Administrador" -ForegroundColor White
    Write-Host "  2. Ejecuta: wsl --install" -ForegroundColor White
    Write-Host "  3. Reinicia tu computadora" -ForegroundColor White
    Write-Host "  4. Vuelve a ejecutar este script" -ForegroundColor White
    Write-Host ""
    if ($isAdmin) {
        $install = Read-Host "¿Deseas instalar WSL 2 ahora? (S/N)"
        if ($install -eq "S" -or $install -eq "s") {
            Write-Host "Instalando WSL 2..." -ForegroundColor Yellow
            wsl --install
            Write-Host "[INFO] Reinicia tu computadora después de la instalación" -ForegroundColor Yellow
        }
    }
}
Write-Host ""

Write-Host "[4/8] Verificando servicios de Docker..." -ForegroundColor Yellow
$dockerServices = @("com.docker.service", "docker")
$servicesRunning = $true
foreach ($service in $dockerServices) {
    if (Test-ServiceRunning $service) {
        Write-Host "[OK] Servicio $service está corriendo" -ForegroundColor Green
    } else {
        Write-Host "[ADVERTENCIA] Servicio $service no está corriendo" -ForegroundColor Yellow
        $servicesRunning = $false
    }
}
Write-Host ""

Write-Host "[5/8] Verificando procesos de Docker..." -ForegroundColor Yellow
$dockerProcesses = Get-Process | Where-Object { $_.ProcessName -like "*docker*" -or $_.ProcessName -like "*com.docker*" }
if ($dockerProcesses) {
    Write-Host "[INFO] Procesos de Docker encontrados:" -ForegroundColor Cyan
    $dockerProcesses | ForEach-Object { Write-Host "  - $($_.ProcessName) (PID: $($_.Id))" -ForegroundColor Gray }
} else {
    Write-Host "[INFO] No hay procesos de Docker ejecutándose" -ForegroundColor Yellow
}
Write-Host ""

Write-Host "[6/8] Verificando configuración de Docker..." -ForegroundColor Yellow
$dockerConfigPath = "$env:USERPROFILE\.docker"
if (Test-Path $dockerConfigPath) {
    Write-Host "[OK] Configuración de Docker encontrada" -ForegroundColor Green
} else {
    Write-Host "[INFO] Configuración de Docker no encontrada (se creará al iniciar)" -ForegroundColor Yellow
}
Write-Host ""

Write-Host "[7/8] Intentando reparar Docker Desktop..." -ForegroundColor Yellow
Write-Host ""

# Paso 1: Cerrar procesos de Docker
Write-Host "  [1/4] Cerrando procesos de Docker..." -ForegroundColor Cyan
$dockerProcesses = Get-Process | Where-Object { 
    $_.ProcessName -like "*docker*" -or 
    $_.ProcessName -like "*com.docker*" -or
    $_.ProcessName -eq "Docker Desktop"
}
if ($dockerProcesses) {
    foreach ($proc in $dockerProcesses) {
        try {
            Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
            Write-Host "    [OK] Proceso $($proc.ProcessName) cerrado" -ForegroundColor Gray
        } catch {
            Write-Host "    [ADVERTENCIA] No se pudo cerrar $($proc.ProcessName)" -ForegroundColor Yellow
        }
    }
    Start-Sleep -Seconds 2
} else {
    Write-Host "    [INFO] No hay procesos de Docker para cerrar" -ForegroundColor Gray
}

# Paso 2: Reiniciar servicios de Docker (requiere admin)
if ($isAdmin) {
    Write-Host "  [2/4] Reiniciando servicios de Docker..." -ForegroundColor Cyan
    $dockerServices = @("com.docker.service")
    foreach ($service in $dockerServices) {
        $svc = Get-Service -Name $service -ErrorAction SilentlyContinue
        if ($svc) {
            try {
                Restart-Service -Name $service -Force -ErrorAction SilentlyContinue
                Write-Host "    [OK] Servicio $service reiniciado" -ForegroundColor Gray
            } catch {
                Write-Host "    [ADVERTENCIA] No se pudo reiniciar $service" -ForegroundColor Yellow
            }
        }
    }
    Start-Sleep -Seconds 3
} else {
    Write-Host "  [2/4] Omitiendo reinicio de servicios (requiere admin)" -ForegroundColor Yellow
}

# Paso 3: Limpiar recursos de Docker
Write-Host "  [3/4] Limpiando recursos de Docker..." -ForegroundColor Cyan
try {
    docker system prune -f 2>$null | Out-Null
    Write-Host "    [OK] Recursos limpiados" -ForegroundColor Gray
} catch {
    Write-Host "    [INFO] No se pudo limpiar (Docker no está corriendo)" -ForegroundColor Gray
}

# Paso 4: Intentar iniciar Docker Desktop
Write-Host "  [4/4] Iniciando Docker Desktop..." -ForegroundColor Cyan
$dockerDesktopPaths = @(
    "C:\Program Files\Docker\Docker\Docker Desktop.exe",
    "${env:ProgramFiles(x86)}\Docker\Docker\Docker Desktop.exe",
    "$env:LOCALAPPDATA\Docker\Docker Desktop.exe"
)

$dockerDesktopStarted = $false
foreach ($path in $dockerDesktopPaths) {
    if (Test-Path $path) {
        try {
            Start-Process $path
            Write-Host "    [OK] Docker Desktop iniciado desde: $path" -ForegroundColor Green
            $dockerDesktopStarted = $true
            break
        } catch {
            Write-Host "    [ERROR] No se pudo iniciar desde: $path" -ForegroundColor Red
        }
    }
}

if (-not $dockerDesktopStarted) {
    Write-Host "    [ERROR] No se encontró Docker Desktop.exe" -ForegroundColor Red
    Write-Host "    Por favor inicia Docker Desktop manualmente desde el menú de inicio" -ForegroundColor Yellow
}
Write-Host ""

Write-Host "[8/8] Esperando que Docker Desktop inicie..." -ForegroundColor Yellow
Write-Host "Esto puede tomar 30-60 segundos..." -ForegroundColor Gray
Write-Host ""

$maxAttempts = 12
$attempt = 0
$dockerReady = $false

while ($attempt -lt $maxAttempts -and -not $dockerReady) {
    $attempt++
    Write-Host "  Intento $attempt/$maxAttempts..." -ForegroundColor Gray -NoNewline
    try {
        docker ps 2>$null | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host " [OK]" -ForegroundColor Green
            $dockerReady = $true
        } else {
            Write-Host " [Esperando...]" -ForegroundColor Yellow
            Start-Sleep -Seconds 5
        }
    } catch {
        Write-Host " [Esperando...]" -ForegroundColor Yellow
        Start-Sleep -Seconds 5
    }
}

Write-Host ""

if ($dockerReady) {
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  ¡Docker Desktop está funcionando!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Contenedores activos:" -ForegroundColor Cyan
    docker ps
    Write-Host ""
    Write-Host "Ahora puedes ejecutar: .\start.ps1" -ForegroundColor Yellow
} else {
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "  Docker Desktop aún no está listo" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Soluciones adicionales:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. Reinicia Docker Desktop manualmente:" -ForegroundColor White
    Write-Host "   - Cierra Docker Desktop completamente" -ForegroundColor Gray
    Write-Host "   - Espera 10 segundos" -ForegroundColor Gray
    Write-Host "   - Ábrelo nuevamente desde el menú de inicio" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. Verifica los logs de Docker Desktop:" -ForegroundColor White
    Write-Host "   - Abre Docker Desktop" -ForegroundColor Gray
    Write-Host "   - Ve a Settings > Troubleshoot > View logs" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3. Reinstala Docker Desktop si el problema persiste:" -ForegroundColor White
    Write-Host "   - Desinstala Docker Desktop" -ForegroundColor Gray
    Write-Host "   - Reinicia tu computadora" -ForegroundColor Gray
    Write-Host "   - Descarga e instala la última versión" -ForegroundColor Gray
    Write-Host ""
    Write-Host "4. Verifica que WSL 2 esté correctamente configurado:" -ForegroundColor White
    Write-Host "   - Ejecuta: wsl --set-default-version 2" -ForegroundColor Gray
    Write-Host "   - Verifica: wsl --status" -ForegroundColor Gray
    Write-Host ""
}

Write-Host ""
Read-Host "Presiona Enter para salir"

