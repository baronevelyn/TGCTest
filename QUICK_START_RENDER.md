# 🚀 Quick Start - Deploy a Render.com

## ¿Qué incluye esta configuración?

✅ Servidor Flask-SocketIO listo para producción
✅ Configuración automática de puertos para Render
✅ Requirements.txt con todas las dependencias
✅ Archivo render.yaml para deploy automático
✅ Cliente configurable (local o servidor remoto)

## 📋 Checklist antes de deploy

1. ✅ Archivos creados:
   - `render.yaml` - Configuración de Render
   - `server.py` - Punto de entrada WSGI
   - `requirements.txt` - Dependencias actualizado
   - `runtime.txt` - Versión de Python
   - `DEPLOY_RENDER.md` - Guía completa

2. ✅ Código actualizado:
   - `server/app.py` - Usa variable PORT del entorno
   - `server_config.txt` - Instrucciones para cambiar URL

## 🎯 Pasos rápidos (5 minutos)

### 1. Sube tu código a GitHub
```bash
# En la carpeta TGCTest
git init
git add .
git commit -m "Ready for Render deployment"

# Crea un repo en GitHub y ejecuta:
git remote add origin https://github.com/TU_USUARIO/TGCTest.git
git branch -M main
git push -u origin main
```

### 2. Deploy en Render
1. Ve a [render.com](https://render.com) y regístrate con GitHub
2. Haz clic en **"New +"** → **"Web Service"**
3. Selecciona tu repositorio `TGCTest`
4. Render detectará automáticamente `render.yaml`
5. Haz clic en **"Apply"** y luego **"Create Web Service"**

### 3. Espera el deploy (2-5 minutos)
Render instalará las dependencias y arrancará el servidor.

### 4. Obtén tu URL
En el dashboard verás algo como:
```
https://mini-tcg-server-xxxx.onrender.com
```

### 5. Actualiza el cliente
Edita `server_config.txt`:
```
# Comenta esta línea:
# SERVER_URL=http://localhost:5000

# Descomenta y actualiza esta:
SERVER_URL=https://mini-tcg-server-xxxx.onrender.com
```

### 6. ¡Juega!
Ejecuta `python main_menu.py` desde cualquier lugar del mundo.

## 🧪 Verificar que funciona

### Test desde navegador:
```
https://tu-servidor.onrender.com
```

Deberías ver:
```json
{
  "status": "online",
  "message": "Mini TCG Multiplayer Server",
  "active_rooms": 0,
  "waiting_players": 0
}
```

### Test desde el juego:
1. Inicia el juego: `python main_menu.py`
2. Selecciona "Multijugador"
3. El estado de conexión debe decir "Conectado ✅"

## ⚡ Próximos pasos

### Mantener servidor despierto (opcional)
El plan gratuito "duerme" después de 15 min sin actividad.

**Solución fácil con UptimeRobot:**
1. Regístrate en [uptimerobot.com](https://uptimerobot.com) (gratis)
2. Crea un monitor HTTP(s)
3. URL: `https://tu-servidor.onrender.com`
4. Intervalo: 5 minutos

Esto hará un ping cada 5 minutos y mantendrá el servidor activo.

## 🐛 Problemas comunes

### "Application failed to respond"
- Revisa logs en Render Dashboard
- Verifica que todas las dependencias estén en `requirements.txt`

### Conexión lenta la primera vez
- Normal si el servidor estaba dormido
- Tarda ~30 segundos en despertar
- Usa UptimeRobot para evitarlo

### "Module not found"
- Falta alguna dependencia en `requirements.txt`
- Revisa logs en Render para ver cuál falta
- Agrega la dependencia y haz push

## 📊 Monitoreo

En el Dashboard de Render puedes ver:
- ✅ Estado del servidor (Running/Sleeping)
- 📊 CPU y memoria usada
- 📝 Logs en tiempo real
- 🔄 Historial de deploys
- ⚙️ Variables de entorno

## 💰 Límites del plan gratuito

- **750 horas/mes** (~24/7 con sleep inteligente)
- **Hasta 512 MB RAM**
- **Auto-sleep** después de 15 min sin actividad
- **1 worker** (suficiente para 2-10 jugadores simultáneos)

Para más jugadores → Plan Starter ($7/mes) con más RAM y sin sleep.

## 🎉 ¡Listo!

Tu juego ahora es totalmente online sin necesidad de:
- ❌ Hamachi
- ❌ Port forwarding
- ❌ Configurar router
- ❌ IP pública
- ❌ VPN

Solo compartes la URL del servidor y cualquiera puede jugar contigo desde cualquier lugar del mundo! 🌍
