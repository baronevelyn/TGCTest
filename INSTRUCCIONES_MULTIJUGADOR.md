# 🌐 Instrucciones para Jugar Online con un Amigo

## Método 1: Usando ngrok (Recomendado) ⚡

ngrok crea un túnel público para que tu amigo pueda conectarse sin configurar puertos.

### Paso 1: Descargar ngrok
1. Ve a https://ngrok.com/download
2. Descarga ngrok para Windows
3. Descomprime el archivo y coloca `ngrok.exe` en una carpeta accesible

### Paso 2: Crear cuenta (gratis)
1. Regístrate en https://dashboard.ngrok.com/signup
2. Copia tu authtoken desde https://dashboard.ngrok.com/get-started/your-authtoken
3. Ejecuta en PowerShell:
   ```powershell
   .\ngrok.exe config add-authtoken TU_TOKEN_AQUI
   ```

### Paso 3: Iniciar el servidor del juego
1. Abre PowerShell en la carpeta del proyecto
2. Ejecuta:
   ```powershell
   python server/app.py
   ```
3. Verás: `🚀 Servidor Socket.IO iniciado en http://localhost:5000`

### Paso 4: Crear el túnel ngrok
1. Abre OTRA terminal PowerShell
2. Navega a donde está ngrok.exe
3. Ejecuta:
   ```powershell
   .\ngrok.exe http 5000
   ```
4. Verás una URL pública como: `https://abc123.ngrok-free.app`

### Paso 5: Compartir la URL con tu amigo
1. Copia la URL que muestra ngrok (ej: `https://abc123.ngrok-free.app`)
2. Envíala a tu amigo
3. Tu amigo debe modificar `network_manager.py` (ver abajo)

### Paso 6: Tu amigo configura su cliente
Tu amigo debe editar `src/multiplayer/network_manager.py` y cambiar la línea 20:

```python
# Cambiar de:
def __init__(self, server_url: str = 'http://localhost:5000'):

# A:
def __init__(self, server_url: str = 'https://abc123.ngrok-free.app'):
```

(Reemplaza `abc123.ngrok-free.app` con tu URL real de ngrok)

### Paso 7: ¡Jugar!
- **Tú**: Ejecuta `python main_menu.py` → Multijugador → Quick Match o Custom Match
- **Tu amigo**: Ejecuta `python main_menu.py` → Multijugador → Quick Match o Custom Match
- ¡El servidor los emparejará automáticamente!

---

## Método 2: Port Forwarding (Avanzado) 🔧

Si no quieres usar ngrok, puedes abrir el puerto 5000 en tu router.

### Paso 1: Obtener tu IP local
```powershell
ipconfig
```
Busca tu `IPv4 Address` (ej: `192.168.1.100`)

### Paso 2: Configurar Port Forwarding en tu router
1. Accede a tu router (usualmente `192.168.1.1` o `192.168.0.1`)
2. Busca la sección "Port Forwarding" o "Virtual Server"
3. Crea una regla:
   - **Puerto Externo**: 5000
   - **Puerto Interno**: 5000
   - **IP Local**: Tu IP local (ej: `192.168.1.100`)
   - **Protocolo**: TCP

### Paso 3: Obtener tu IP pública
Ve a https://www.whatismyip.com/ y anota tu IP pública (ej: `203.0.113.45`)

### Paso 4: Tu amigo configura su cliente
Tu amigo debe editar `src/multiplayer/network_manager.py`:

```python
def __init__(self, server_url: str = 'http://203.0.113.45:5000'):
```

(Reemplaza `203.0.113.45` con tu IP pública real)

### Paso 5: Iniciar servidor y jugar
```powershell
python server/app.py
python main_menu.py
```

---

## Método 3: Ambos editan network_manager.py manualmente

Para una solución rápida sin ngrok ni port forwarding:

### Servidor (Tú):
1. Ejecuta `python server/app.py`
2. Usa ngrok como se describió arriba
3. Envía la URL a tu amigo

### Cliente (Tu amigo):
Edita `src/multiplayer/network_manager.py` línea 20:
```python
def __init__(self, server_url: str = 'https://TU_URL_NGROK_AQUI'):
```

---

## 🎮 Modos de Juego

### Quick Match
- Mazos aleatorios generados automáticamente
- Emparejamiento inmediato

### Custom Match
- Elige tu propio mazo guardado
- Elige tu campeón favorito

---

## 🐛 Solución de Problemas

### "Connection Error: Could not connect to server"
- Verifica que el servidor esté corriendo (`python server/app.py`)
- Verifica que ngrok esté corriendo (`.\ngrok.exe http 5000`)
- Revisa que la URL en `network_manager.py` sea correcta

### "Waiting for opponent..." no encuentra match
- Asegúrate de que ambos jugadores estén conectados al mismo servidor
- Ambos deben elegir el mismo modo (Quick Match o Custom Match)
- Revisa la consola del servidor para ver si ambos están conectados

### ngrok muestra "ERR_NGROK_3200"
- Actualiza tu authtoken: `.\ngrok.exe config add-authtoken TU_TOKEN`
- Asegúrate de tener una cuenta en ngrok.com

---

## 📝 Notas Importantes

- **ngrok gratuito**: La URL cambia cada vez que reinicias ngrok
- **Límites gratuitos**: ngrok tiene un límite de conexiones por minuto
- **Latencia**: ngrok puede añadir algo de latencia (50-200ms)
- **Firewall**: Asegúrate de que tu firewall permita conexiones en el puerto 5000

---

## 🔄 Flujo Completo (ngrok)

```
[Tu PC]
  ├─ Terminal 1: python server/app.py          (puerto 5000)
  ├─ Terminal 2: ngrok http 5000               (túnel público)
  └─ Terminal 3: python main_menu.py           (jugar tú)

[PC de tu amigo]
  └─ Terminal: python main_menu.py             (jugar amigo)
                (con network_manager.py editado)
```

---

¡Listo! Con estos pasos deberías poder jugar con tu amigo desde cualquier parte del mundo 🌍
