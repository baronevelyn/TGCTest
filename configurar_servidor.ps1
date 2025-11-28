# Script para configurar el servidor multijugador
# Ejecuta este script para cambiar la URL del servidor fácilmente

Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║        CONFIGURADOR DE SERVIDOR MULTIJUGADOR               ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

Write-Host "Selecciona el tipo de conexión:" -ForegroundColor Yellow
Write-Host "1. Local (localhost:5000) - Para jugar en la misma PC o red local"
Write-Host "2. Hamachi (Requiere Hamachi instalado) - RECOMENDADO para jugar online"
Write-Host "3. ngrok (Requiere URL de ngrok) - Para jugar online sin instalar en invitado"
Write-Host "4. IP Pública (Requiere port forwarding) - Para jugar online (avanzado)"
Write-Host "5. URL personalizada"
Write-Host ""

$choice = Read-Host "Elige una opción (1-5)"

switch ($choice) {
    "1" {
        $url = "http://localhost:5000"
        Write-Host "`n✅ Configurado para juego LOCAL" -ForegroundColor Green
        Write-Host "Perfecto para jugar en la misma computadora o red local" -ForegroundColor Gray
    }
    "2" {
        Write-Host "`n🌐 Configuración con Hamachi (RECOMENDADO)" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Pasos para usar Hamachi:" -ForegroundColor Yellow
        Write-Host "1. Descarga Hamachi: https://www.vpn.net/"
        Write-Host "2. Instala y crea/únete a una red"
        Write-Host "3. Anota tu IP de Hamachi (ej: 25.123.45.67)"
        Write-Host ""
        Write-Host "¿Eres el HOST o el INVITADO?" -ForegroundColor White
        Write-Host "H - Host (quien inicia el servidor)"
        Write-Host "I - Invitado (quien se conecta)"
        $role = Read-Host "Elige (H/I)"
        
        if ($role -eq "H" -or $role -eq "h") {
            $url = "http://localhost:5000"
            Write-Host "`n✅ Configurado para HOST con Hamachi" -ForegroundColor Green
            Write-Host ""
            Write-Host "📋 SIGUIENTE PASO:" -ForegroundColor Yellow
            Write-Host "1. Abre Hamachi y crea una red (ej: nombre=TCG-Game)"
            Write-Host "2. Anota tu IP de Hamachi (botón derecho → Copiar dirección IPv4)"
            Write-Host "3. Comparte tu IP y la contraseña de la red con tu amigo"
            Write-Host "4. Ejecuta: python server/app.py"
            Write-Host "5. Luego ejecuta: python main_menu.py"
        } else {
            Write-Host ""
            $hamachiIP = Read-Host "Ingresa la IP de Hamachi de tu amigo (ej: 25.123.45.67)"
            $url = "http://${hamachiIP}:5000"
            Write-Host "`n✅ Configurado para INVITADO con Hamachi" -ForegroundColor Green
            Write-Host ""
            Write-Host "📋 SIGUIENTE PASO:" -ForegroundColor Yellow
            Write-Host "1. Abre Hamachi y únete a la red de tu amigo"
            Write-Host "2. Espera a que tu amigo inicie el servidor"
            Write-Host "3. Ejecuta: python main_menu.py"
        }
    }
    "3" {
        Write-Host "`nPara usar ngrok:" -ForegroundColor Yellow
        Write-Host "1. Descarga ngrok desde: https://ngrok.com/download"
        Write-Host "2. Ejecuta: ngrok http 5000"
        Write-Host "3. Copia la URL que muestra (ej: https://abc123.ngrok-free.app)"
        Write-Host ""
        $url = Read-Host "Ingresa la URL de ngrok"
        if (-not $url.StartsWith("http")) {
            $url = "https://" + $url
        }
        Write-Host "`n✅ Configurado para juego ONLINE (ngrok)" -ForegroundColor Green
    }
    "4" {
        Write-Host "`nPara usar IP pública:" -ForegroundColor Yellow
        Write-Host "1. Configura port forwarding en tu router (puerto 5000)"
        Write-Host "2. Obtén tu IP pública desde: https://www.whatismyip.com/"
        Write-Host ""
        $ip = Read-Host "Ingresa tu IP pública"
        $url = "http://${ip}:5000"
        Write-Host "`n✅ Configurado para juego ONLINE (IP pública)" -ForegroundColor Green
    }
    "5" {
        $url = Read-Host "Ingresa la URL completa del servidor"
        Write-Host "`n✅ Configurado con URL personalizada" -ForegroundColor Green
    }
    default {
        Write-Host "`n❌ Opción inválida. Usando localhost por defecto." -ForegroundColor Red
        $url = "http://localhost:5000"
    }
}

# Guardar configuración
$config = @"
# Configuración del Servidor Multijugador
# Edita esta línea con la URL de tu servidor

# Para jugar localmente (ambos en la misma red):
# SERVER_URL=http://localhost:5000

# Para jugar online con ngrok:
# SERVER_URL=https://tu-url-ngrok.ngrok-free.app

# Para jugar con IP pública (port forwarding):
# SERVER_URL=http://TU_IP_PUBLICA:5000

SERVER_URL=$url
"@

$config | Out-File -FilePath "server_config.txt" -Encoding UTF8

Write-Host "`n📝 Configuración guardada en server_config.txt" -ForegroundColor Cyan
Write-Host "   URL del servidor: $url" -ForegroundColor White
Write-Host ""

if ($choice -ne "2") {
    Write-Host "🎮 Para jugar:" -ForegroundColor Yellow
    Write-Host "   1. Inicia el servidor: python server/app.py"
    if ($choice -eq "3") {
        Write-Host "   2. Inicia ngrok: ngrok http 5000"
        Write-Host "   3. Comparte la URL de ngrok con tu amigo"
        Write-Host "   4. Ejecuta el juego: python main_menu.py"
    } else {
        Write-Host "   2. Ejecuta el juego: python main_menu.py"
    }
    Write-Host ""
}

Read-Host "Presiona Enter para continuar..."
