# Script para iniciar servidor + ngrok automáticamente
# Requiere tener ngrok instalado y configurado

Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║         INICIAR SERVIDOR MULTIJUGADOR + NGROK              ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Verificar si ngrok está instalado
$ngrokPath = Get-Command ngrok -ErrorAction SilentlyContinue
if (-not $ngrokPath) {
    Write-Host "⚠️  ngrok no encontrado en el PATH" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Opciones:" -ForegroundColor White
    Write-Host "1. Descarga ngrok desde: https://ngrok.com/download"
    Write-Host "2. O ingresa la ruta completa a ngrok.exe:"
    $customPath = Read-Host "Ruta a ngrok.exe (o Enter para salir)"
    
    if ($customPath -and (Test-Path $customPath)) {
        $ngrokCmd = $customPath
    } else {
        Write-Host "❌ Cancelado. Instala ngrok o especifica la ruta correcta." -ForegroundColor Red
        Read-Host "Presiona Enter para salir..."
        exit
    }
} else {
    $ngrokCmd = "ngrok"
}

Write-Host "✅ ngrok encontrado" -ForegroundColor Green
Write-Host ""

# Iniciar servidor del juego en background
Write-Host "🚀 Iniciando servidor del juego en puerto 5000..." -ForegroundColor Cyan
$serverJob = Start-Job -ScriptBlock {
    param($path)
    Set-Location $path
    python server/app.py
} -ArgumentList (Get-Location).Path

Start-Sleep -Seconds 2

# Verificar que el servidor inició
$serverStarted = $false
for ($i = 0; $i -lt 10; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:5000" -TimeoutSec 1 -ErrorAction SilentlyContinue
        $serverStarted = $true
        break
    } catch {
        Start-Sleep -Milliseconds 500
    }
}

if (-not $serverStarted) {
    Write-Host "⚠️  El servidor tardó en iniciar, pero continuando..." -ForegroundColor Yellow
}

Write-Host "✅ Servidor del juego iniciado (Job ID: $($serverJob.Id))" -ForegroundColor Green
Write-Host ""

# Iniciar ngrok
Write-Host "🌐 Iniciando ngrok..." -ForegroundColor Cyan
Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║  IMPORTANTE: Copia la URL 'Forwarding' que aparece abajo  ║" -ForegroundColor Green
Write-Host "║  Ejemplo: https://abc123.ngrok-free.app                   ║" -ForegroundColor Green
Write-Host "║                                                            ║" -ForegroundColor Green
Write-Host "║  Comparte esta URL con tu amigo para que pueda jugar      ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "Presiona Ctrl+C para detener el servidor y ngrok" -ForegroundColor Yellow
Write-Host ""

# Ejecutar ngrok (bloqueante - mostrará la interfaz de ngrok)
try {
    & $ngrokCmd http 5000
} finally {
    # Cleanup: detener el servidor cuando se cierre ngrok
    Write-Host ""
    Write-Host "🛑 Deteniendo servidor del juego..." -ForegroundColor Yellow
    Stop-Job -Id $serverJob.Id
    Remove-Job -Id $serverJob.Id
    Write-Host "✅ Servidor detenido" -ForegroundColor Green
}
