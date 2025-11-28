# Deployment en Render.com - Mini TCG Multiplayer Server

## 🚀 Pasos para Deploy

### 1. Crear cuenta en Render
1. Ve a [render.com](https://render.com)
2. Regístrate con GitHub (recomendado)

### 2. Preparar repositorio Git
```bash
# Si no tienes git inicializado
git init

# Agregar archivos
git add .
git commit -m "Setup for Render deployment"

# Crear repositorio en GitHub y subir
git remote add origin https://github.com/TU_USUARIO/TGCTest.git
git branch -M main
git push -u origin main
```

### 3. Crear Web Service en Render
1. En Render Dashboard, haz clic en **"New +"** → **"Web Service"**
2. Conecta tu repositorio de GitHub
3. Configuración:
   - **Name**: `mini-tcg-server` (o el nombre que prefieras)
   - **Region**: Frankfurt (Europa) o cualquier cercana
   - **Branch**: `main`
   - **Root Directory**: (dejar vacío)
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --worker-class geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 server.app:app --bind 0.0.0.0:$PORT`
4. Haz clic en **"Create Web Service"**

### 4. Obtener URL del servidor
Después del deploy (toma 2-5 minutos), obtendrás una URL como:
```
https://mini-tcg-server.onrender.com
```

### 5. Actualizar cliente para usar servidor en producción

En `src/multiplayer/network_manager.py`, cambia la URL del servidor:

```python
# Desarrollo local
SERVER_URL = 'http://localhost:5000'

# Producción
SERVER_URL = 'https://mini-tcg-server.onrender.com'
```

O mejor aún, usa una variable de entorno:

```python
import os
SERVER_URL = os.environ.get('TCG_SERVER_URL', 'http://localhost:5000')
```

## 📊 Verificar que funciona

### Test rápido:
Abre en navegador: `https://tu-servidor.onrender.com`

Deberías ver:
```json
{
  "status": "online",
  "message": "Mini TCG Multiplayer Server",
  "active_rooms": 0,
  "waiting_players": 0
}
```

## ⚠️ Limitaciones del plan gratuito

1. **Sleep después de 15 min de inactividad**
   - El servidor "se duerme" si no hay actividad
   - Primera conexión tarda ~30 segundos en despertar
   - Solución: Hacer un ping cada 10 minutos desde un cron job externo

2. **750 horas/mes**
   - Suficiente para ~24/7 si se usa sleep inteligente
   - Se reinicia el 1º de cada mes

3. **Rendimiento limitado**
   - Suficiente para 2-10 jugadores simultáneos
   - Para más jugadores, necesitas plan pago

## 🔧 Mantener el servidor despierto (opcional)

### Opción 1: Cron-job.org (gratis)
1. Crea cuenta en [cron-job.org](https://cron-job.org)
2. Crea un cron job:
   - URL: `https://tu-servidor.onrender.com`
   - Intervalo: Cada 10 minutos
3. Esto mantiene el servidor activo

### Opción 2: UptimeRobot (gratis)
1. Crea cuenta en [uptimerobot.com](https://uptimerobot.com)
2. Añade monitor HTTP(s)
3. URL: Tu servidor en Render
4. Interval: 5 minutos

## 🐛 Troubleshooting

### Error: "Application failed to respond"
- Revisa logs en Render Dashboard
- Verifica que el puerto use `$PORT` en lugar de `5000` hardcoded

### Error: "Build failed"
- Revisa que `requirements.txt` esté correcto
- Verifica que Python 3.13 sea compatible (usa 3.11 si hay problemas)

### Conexión lenta la primera vez
- Normal - servidor estaba "dormido"
- Siguiente conexión será inmediata

## 💡 Alternativas si Render no funciona

1. **Railway.app** - Similar pero con $5 crédito gratis/mes
2. **Fly.io** - Hasta 3 VMs gratis, buena latencia
3. **Heroku** - Ya no tiene plan gratuito (requiere $5/mes mínimo)

## 📝 Notas adicionales

- Los logs se pueden ver en tiempo real en Render Dashboard
- Auto-deploy cada vez que haces push a GitHub
- SSL/HTTPS incluido automáticamente
- Sin necesidad de Hamachi, ngrok o configurar routers
