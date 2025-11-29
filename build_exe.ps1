# Builds a standalone Windows .exe for Mini TCG using PyInstaller
# Requirements: Windows, PowerShell, internet access
# Output: dist/MiniTCG/MiniTCG.exe

param(
    [switch]$Windowed = $true,
    [switch]$Clean = $false,
    [switch]$OneFile = $false
)

$ErrorActionPreference = 'Stop'

Write-Host "Preparing environment..." -ForegroundColor Cyan

# Ensure venv (optional). If you already have an env, comment this out.
if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment (.venv)" -ForegroundColor Cyan
    python -m venv .venv
}

$venvPython = Join-Path ".venv" "Scripts/python.exe"
$venvPip = Join-Path ".venv" "Scripts/pip.exe"
if (-not (Test-Path $venvPython)) {
    Write-Host "WARNING: venv python not found; falling back to system python" -ForegroundColor Yellow
    $venvPython = "python"
    $venvPip = "pip"
}

Write-Host "Installing build dependencies (pyinstaller)..." -ForegroundColor Cyan
& $venvPip install --upgrade pip | Out-Null
& $venvPip install pyinstaller | Out-Null

Write-Host "Installing app dependencies from requirements.txt..." -ForegroundColor Cyan
if (Test-Path "requirements.txt") {
    & $venvPip install -r requirements.txt
}

# Optional clean
if ($Clean) {
    Write-Host "Cleaning previous build" -ForegroundColor Cyan
    Remove-Item -Recurse -Force dist -ErrorAction SilentlyContinue
    Remove-Item -Recurse -Force build -ErrorAction SilentlyContinue
}

# Assets to include
$assets = @(
    "assets",
    "data",
    "docs"
)

# Build options
$consoleFlag = "--noconsole"
if (-not $Windowed) {
    $consoleFlag = "--console"
}

# Icon (optional)
$icon = ""
if (Test-Path "assets/app.ico") {
    $icon = "--icon assets/app.ico"
}

# Build command
$entry = "main_menu.py"
$distName = "MiniTCG"

# Collect binaries automatically
$addDataArgs = @()
foreach ($item in $assets) {
    if (Test-Path $item) {
        $addDataArgs += "--add-data"
        # PyInstaller uses ';' as separator on Windows
        $addDataArgs += "$item;$item"
    }
}

if ($OneFile) {
    Write-Host "Building ONEFILE $distName.exe from $entry" -ForegroundColor Green
} else {
    Write-Host "Building $distName.exe from $entry (folder mode)" -ForegroundColor Green
}

$pyiArgs = @(
    "--name", $distName,
    $consoleFlag,
    "--clean",
    "--noconfirm"
)
if ($OneFile) { $pyiArgs += "--onefile" }
if ($icon -ne "") { $pyiArgs += $icon }
$pyiArgs += $addDataArgs
$pyiArgs += $entry

& $venvPython -m PyInstaller $pyiArgs

if ($OneFile) {
    # Onefile output exe path differs
    $distExe = Join-Path "dist" "$distName.exe"
    if (Test-Path $distExe) {
        Write-Host "Onefile exe built at $distExe" -ForegroundColor Green
    } else {
        Write-Host "WARNING: Expected onefile exe not found at $distExe" -ForegroundColor Yellow
    }
    # Copy server_config.txt next to release exe (not inside dist)
} else {
    # Folder mode copy config inside dist/MiniTCG
    if (Test-Path "server_config.txt") {
        New-Item -ItemType Directory -Force -Path (Join-Path "dist" $distName) | Out-Null
        $targetCfg = Join-Path (Join-Path "dist" $distName) "server_config.txt"
        Copy-Item "server_config.txt" $targetCfg -Force
    }
}

if ($OneFile) {
    Write-Host "Build complete (onefile): dist/$distName.exe" -ForegroundColor Green
    Write-Host "Distribute just dist/$distName.exe (keep server_config.txt alongside if overriding URL)." -ForegroundColor Green
} else {
    Write-Host "Build complete: dist/$distName/$distName.exe" -ForegroundColor Green
    Write-Host "Distribute the dist/$distName folder. No Python required." -ForegroundColor Green
}

# Make a top-level easy-access copy
try {
    $releaseDir = "release"
    New-Item -ItemType Directory -Force -Path $releaseDir | Out-Null
    if ($OneFile) {
        $builtExe = Join-Path "dist" ("$distName.exe")
    } else {
        $builtExe = Join-Path (Join-Path "dist" $distName) ("$distName.exe")
    }
    if (Test-Path $builtExe) {
        $releaseExe = Join-Path $releaseDir ("$distName.exe")
        Copy-Item $builtExe $releaseExe -Force
        # If onefile, also copy server_config.txt for convenience
        if ($OneFile -and (Test-Path "server_config.txt")) {
            Copy-Item "server_config.txt" (Join-Path $releaseDir "server_config.txt") -Force
        }
        Write-Host "Copied easy-access exe to $releaseExe" -ForegroundColor Cyan
    } else {
        Write-Host "WARNING: Built exe not found at $builtExe" -ForegroundColor Yellow
    }
} catch {
    Write-Host "WARNING: Could not create easy-access copy: $($_.Exception.Message)" -ForegroundColor Yellow
}
