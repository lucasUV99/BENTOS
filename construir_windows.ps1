<#
.SYNOPSIS
    Construye el instalador de BENTOS para Windows.

.DESCRIPTION
    Ejecuta PyInstaller con la configuración definida en bentos_windows.spec
    y genera el ejecutable BENTOS.exe en la carpeta dist/.
    
    Opcionalmente copia el resultado a un pendrive.

.EXAMPLE
    .\construir_windows.ps1
    .\construir_windows.ps1 -CopiarA "E:\BENTOS"
#>

param(
    [string]$CopiarA = ""
)

$ErrorActionPreference = "Continue"
$BaseDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  BENTOS — Construir Instalador Windows" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Activar entorno virtual
$VenvPython = Join-Path $BaseDir ".venv\Scripts\python.exe"
$VenvPyInstaller = Join-Path $BaseDir ".venv\Scripts\pyinstaller.exe"

if (-not (Test-Path $VenvPython)) {
    Write-Host "ERROR: No se encontro el entorno virtual en .venv\" -ForegroundColor Red
    Write-Host "Ejecuta: python -m venv .venv" -ForegroundColor Yellow
    exit 1
}

if (-not (Test-Path $VenvPyInstaller)) {
    Write-Host "Instalando PyInstaller..." -ForegroundColor Yellow
    & $VenvPython -m pip install pyinstaller --quiet 2>&1 | Out-Null
}

# Instalar dependencias
Write-Host "Verificando dependencias..." -ForegroundColor Yellow
& $VenvPython -m pip install -r (Join-Path $BaseDir "requirements.txt") --quiet 2>&1 | Out-Null
Write-Host "Dependencias OK" -ForegroundColor Green

# Limpiar builds anteriores
$DistDir = Join-Path $BaseDir "dist"
$BuildDir = Join-Path $BaseDir "build"

if (Test-Path $DistDir) {
    Write-Host "Limpiando dist/ anterior..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force $DistDir
}
if (Test-Path $BuildDir) {
    Remove-Item -Recurse -Force $BuildDir
}

# Construir
Write-Host ""
Write-Host "Construyendo BENTOS.exe..." -ForegroundColor Green
Write-Host "Esto puede tardar varios minutos..." -ForegroundColor Gray
Write-Host ""

Push-Location $BaseDir
try {
    & $VenvPyInstaller bentos_windows.spec --noconfirm 2>&1 | ForEach-Object {
        if ($_ -match "ERROR|error|Error") {
            Write-Host $_ -ForegroundColor Red
        } elseif ($_ -match "WARNING|warning") {
            # Silenciar warnings comunes
        } elseif ($_ -match "Building|Completed|successfully") {
            Write-Host $_ -ForegroundColor Green
        }
    }
} finally {
    Pop-Location
}

# Verificar resultado
$ExePath = Join-Path $DistDir "BENTOS.exe"

if (Test-Path $ExePath) {
    $FileSize = (Get-Item $ExePath).Length / 1MB
    Write-Host ""
    Write-Host "================================================" -ForegroundColor Green
    Write-Host "  CONSTRUCCION EXITOSA" -ForegroundColor Green
    Write-Host "================================================" -ForegroundColor Green
    Write-Host "  Archivo: $ExePath" -ForegroundColor White
    Write-Host "  Tamano:  $([math]::Round($FileSize, 1)) MB" -ForegroundColor White
    Write-Host ""
    
    # Copiar a pendrive si se especificó
    if ($CopiarA -ne "") {
        Write-Host "Copiando a $CopiarA..." -ForegroundColor Yellow
        
        if (-not (Test-Path $CopiarA)) {
            New-Item -ItemType Directory -Path $CopiarA -Force | Out-Null
        }
        
        $DestinoWindows = Join-Path $CopiarA "Windows"
        if (-not (Test-Path $DestinoWindows)) {
            New-Item -ItemType Directory -Path $DestinoWindows -Force | Out-Null
        }
        
        Copy-Item $ExePath (Join-Path $DestinoWindows "BENTOS.exe") -Force
        
        # Crear archivo de instrucciones
        @"
BENTOS — Instalación Windows
==============================

1. Copia el archivo BENTOS.exe a tu escritorio o carpeta deseada
2. Doble clic en BENTOS.exe para ejecutar
3. Windows SmartScreen puede mostrar una advertencia
   → Haz clic en "Más información" → "Ejecutar de todos modos"

Requisitos:
- Windows 10 o superior
- Conexión a internet (para sincronización con la nube)

Soporte: Contacta al administrador del sistema
"@ | Set-Content (Join-Path $DestinoWindows "INSTRUCCIONES.txt") -Encoding UTF8

        Write-Host "Copiado a: $DestinoWindows\BENTOS.exe" -ForegroundColor Green
    }
    
    # Calcular SHA256
    $Hash = (Get-FileHash $ExePath -Algorithm SHA256).Hash
    Write-Host "  SHA256:  $Hash" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Guarda este hash para publicar la actualizacion." -ForegroundColor Yellow
    
} else {
    Write-Host ""
    Write-Host "ERROR: No se genero BENTOS.exe" -ForegroundColor Red
    Write-Host "Revisa los errores arriba." -ForegroundColor Red
    exit 1
}
