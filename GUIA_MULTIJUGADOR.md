# 🎮 Mini TCG - Guía Rápida Multijugador Online

## 🚀 Inicio Rápido (Recomendado)

### MÉTODO 1: Hamachi (Más Fácil) 🟢

#### Para AMBOS jugadores:

1. **Descarga e instala Hamachi:**
   - https://www.vpn.net/
   - Instalación gratuita

2. **Crea/Únete a una red:**
   - **Host:** Crea red → Ingresa nombre y contraseña → Anota tu IP Hamachi (ej: `25.123.45.67`)
   - **Invitado:** Únete a red → Usa nombre y contraseña del host

3. **Host - Inicia el servidor:**
   ```powershell
   python server/app.py
   ```

4. **Invitado - Configura cliente:**
   ```powershell
   .\configurar_servidor.ps1
   ```
   Elige opción 3 y usa la IP Hamachi del host (ej: `25.123.45.67`)

5. **AMBOS - Inician el juego:**
   ```powershell
   python main_menu.py
   ```
   Ve a Multijugador → Quick Match o Custom Match

---

### MÉTODO 2: ngrok (Sin instalar nada en el invitado) 🟡

#### Para el HOST:

1. **Configura el servidor:**
   ```powershell
   .\configurar_servidor.ps1
   ```
   Elige opción 2 (ngrok)

2. **Inicia servidor + ngrok automáticamente:**
   ```powershell
   .\iniciar_servidor_online.ps1
   ```
   
3. **Copia la URL pública** que muestra ngrok (ej: `https://abc123.ngrok-free.app`)

4. **Comparte la URL con tu amigo**

5. **Inicia el juego:**
   ```powershell
   python main_menu.py
   ```

#### Para el INVITADO:

1. **Recibe la URL del servidor** de tu amigo (ej: `https://abc123.ngrok-free.app`)

2. **Configura tu cliente:**
   ```powershell
   .\configurar_servidor.ps1
   ```
   Elige opción 2 y pega la URL que te compartió tu amigo

3. **Inicia el juego:**
   ```powershell
   python main_menu.py
   ```

4. **¡Disfruta!** El juego automáticamente te emparejará con tu amigo

---

## 📋 Método Manual (Sin Scripts)

### Opción A: Hamachi (Recomendado para principiantes) 🟢

#### AMBOS jugadores:
1. Descarga Hamachi: https://www.vpn.net/
2. Instala y crea cuenta gratuita

#### Host:
1. En Hamachi: Crea red → Nombre: `TCG-Game`, Contraseña: `tu_password`
2. Anota tu IP Hamachi (ej: `25.123.45.67`)
3. Inicia el servidor:
   ```powershell
   python server/app.py
   ```
4. Comparte tu IP Hamachi con tu amigo
5. Inicia el juego: `python main_menu.py`

#### Invitado:
1. En Hamachi: Únete a red → Nombre: `TCG-Game`, Contraseña: `tu_password`
2. Edita `server_config.txt`:
   ```
   SERVER_URL=http://25.123.45.67:5000
   ```
   (Usa la IP Hamachi de tu amigo)
3. Inicia el juego: `python main_menu.py`

**✅ Ventajas de Hamachi:**
- No requiere configurar router
- Muy fácil de usar
- Conexión estable y de baja latencia
- Funciona incluso con NAT estricto

---

### Opción B: Usando ngrok

#### Host:
1. Descarga ngrok: https://ngrok.com/download
2. Inicia el servidor:
   ```powershell
   python server/app.py
   ```
3. En otra terminal, inicia ngrok:
   ```powershell
   ngrok http 5000
   ```
4. Copia la URL pública que muestra
5. Comparte la URL con tu amigo
6. Inicia el juego: `python main_menu.py`

#### Invitado:
1. Edita `server_config.txt`
2. Cambia la línea `SERVER_URL=` con la URL de tu amigo
3. Inicia el juego: `python main_menu.py`

---

### Opción C: Port Forwarding (Avanzado)

#### Host:
1. Obtén tu IP local:
   ```powershell
   ipconfig
   ```
2. Accede a tu router (usualmente `192.168.1.1`)
3. Configura Port Forwarding:
   - Puerto externo: 5000
   - Puerto interno: 5000
   - IP: Tu IP local
4. Obtén tu IP pública: https://www.whatismyip.com/
5. Inicia el servidor: `python server/app.py`
6. Comparte tu IP pública con tu amigo
7. Inicia el juego: `python main_menu.py`

#### Invitado:
1. Edita `server_config.txt`
2. Cambia: `SERVER_URL=http://IP_PUBLICA_AMIGO:5000`
3. Inicia el juego: `python main_menu.py`

---

## 🎯 Modos de Juego

### Quick Match
- Mazos aleatorios
- Emparejamiento instantáneo
- Ideal para partidas rápidas

### Custom Match
- Elige tu mazo guardado
- Elige tu campeón
- Más estratégico

---

## 🐛 Solución de Problemas

### "Connection Error: Could not connect to server"
✅ **Solución:**
- Verifica que el servidor esté corriendo
- Si usas ngrok, verifica que esté activo
- Revisa que la URL en `server_config.txt` sea correcta

### "Waiting for opponent..." infinito
✅ **Solución:**
- Ambos deben estar en el mismo modo (Quick Match o Custom Match)
- Ambos deben conectarse al mismo servidor
- Revisa la consola del servidor para ver conexiones

### ngrok: "ERR_NGROK_3200"
✅ **Solución:**
1. Crea cuenta en https://ngrok.com/
2. Copia tu authtoken desde el dashboard
3. Ejecuta: `ngrok config add-authtoken TU_TOKEN`

### El juego se desconecta durante la partida
✅ **Solución:**
- Verifica tu conexión a internet
- Si usas ngrok gratuito, puede haber límites de tiempo
- Reinicia ngrok y actualiza la URL

---

## 📝 Requisitos

- **Python 3.8+**
- **Paquetes Python:**
  ```powershell
  pip install flask flask-socketio gevent python-socketio
  ```
- **ngrok (opcional pero recomendado):**
  - Descarga: https://ngrok.com/download
  - Cuenta gratuita: https://ngrok.com/signup

---

## 🔒 Seguridad

- ngrok proporciona HTTPS automáticamente
- No compartas tu authtoken de ngrok
- Usa conexiones de confianza (amigos/familia)
- El servidor no almacena datos personales

---

## 💡 Consejos

### Comparación de Métodos:

| Método | Dificultad | Latencia | Estabilidad | Requiere Config Router |
|--------|-----------|----------|-------------|------------------------|
| **Hamachi** | ⭐ Fácil | 🟢 Baja (20-50ms) | 🟢 Excelente | ❌ No |
| **ngrok** | ⭐⭐ Media | 🟡 Media (50-200ms) | 🟡 Buena | ❌ No |
| **Port Forward** | ⭐⭐⭐ Difícil | 🟢 Mínima | 🟢 Excelente | ✅ Sí |

### Recomendaciones:
- **Primera vez:** Usa Hamachi (más simple)
- **Sin instalar software:** Usa ngrok (solo el host necesita instalarlo)
- **Mejor rendimiento:** Port Forwarding (requiere acceso al router)
- **LAN local:** Usa `http://localhost:5000` (ambos en misma red)

### Tips:
- **Firewall:** Windows puede pedir permiso para Python y Hamachi, acepta
- **Reconexión:** Si se cae la conexión, reinicia el servidor
- **Latencia:** Hamachi ofrece la mejor latencia para juego online

---

## 📞 Soporte

Si tienes problemas:
1. Revisa la consola del servidor para errores
2. Verifica que ambos tengan la misma versión del juego
3. Prueba primero en modo local antes de online

---

¡Disfruta jugando con tus amigos! 🎉
