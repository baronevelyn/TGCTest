# 🎮 GUÍA DE PRUEBAS: MINI TCG MULTIPLAYER

## 📋 Requisitos Previos

### Dependencias Python
Asegúrate de tener instaladas las siguientes dependencias:

```bash
pip install flask flask-socketio gevent gevent-websocket python-socketio[client] python-engineio
```

### Estructura Completada
- ✅ Protocolo de mensajes (`src/multiplayer/message_protocol.py`)
- ✅ Sistema de sincronización (`src/multiplayer/game_state_sync.py`)
- ✅ Game logic adaptado para multiplayer (`src/game_logic.py`)
- ✅ Lobby UI (`src/multiplayer_lobby.py`)
- ✅ Servidor con validación (`server/app.py`)
- ✅ Integración con menú principal (`main_menu.py`)

---

## 🚀 PRUEBA 1: Dos PCs en la misma red

### Paso 1: Preparar el Servidor (PC Host)

1. **Obtén la IP local del PC que actuará como servidor:**
   ```powershell
   ipconfig
   ```
   Busca tu dirección IPv4 (ej: `192.168.1.100`)

2. **Abre el puerto 5000 en el firewall de Windows:**
   ```powershell
   New-NetFirewallRule -DisplayName "TCG Server" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow
   ```

3. **Inicia el servidor:**
   ```powershell
   cd server
   python app.py
   ```
   
   Deberías ver:
   ```
   🚀 Servidor Socket.IO iniciado en http://0.0.0.0:5000
   📡 Esperando conexiones...
   ```

### Paso 2: Configurar Cliente 1 (PC Host)

1. **Inicia el juego:**
   ```powershell
   python main_menu.py
   ```

2. **Selecciona "🌐 MULTIJUGADOR"**

3. **En el lobby:**
   - El campo de servidor debería tener: `http://localhost:5000`
   - Click en **"Connect"**
   - Espera el mensaje: ✓ Connected to server

4. **Opciones para conectar:**
   - **Opción A:** Click en **"Find Match"** (matchmaking automático)
   - **Opción B:** Click en **"Create Room"** → Se genera un código de 6 caracteres (ej: `ABC123`)

### Paso 3: Configurar Cliente 2 (PC Remoto)

1. **Inicia el juego en el segundo PC:**
   ```powershell
   python main_menu.py
   ```

2. **Selecciona "🌐 MULTIJUGADOR"**

3. **En el lobby:**
   - **IMPORTANTE:** Cambia el campo de servidor a: `http://IP_DEL_SERVIDOR:5000`
     - Ejemplo: `http://192.168.1.100:5000`
   - Click en **"Connect"**
   - Espera el mensaje: ✓ Connected to server

4. **Opciones para conectar:**
   - **Opción A (Matchmaking):** Click en **"Find Match"**
     - Si el Cliente 1 también está en matchmaking, se emparejarán automáticamente
   
   - **Opción B (Sala privada):** 
     - Ingresa el código de 6 caracteres que generó el Cliente 1
     - Click en **"Join Room"**

### Paso 4: Jugar

Una vez emparejados:

1. **El cliente Host (quien creó la sala o fue primero en matchmaking):**
   - Verá: "Your turn - You go first!"
   - Puede jugar cartas, activar habilidades y atacar

2. **El cliente Invitado:**
   - Verá: "Opponent's turn - Waiting..."
   - Esperará a que el oponente termine su turno

3. **Acciones sincronizadas:**
   - ✅ Jugar cartas (tropas y hechizos)
   - ✅ Activar habilidades
   - ✅ Declarar ataques
   - ✅ Finalizar turno
   - ✅ Rendirse

4. **Observar en ambos PCs:**
   - Las cartas jugadas por el oponente aparecen en su tablero
   - Los ataques se reflejan en tiempo real
   - El log de acciones muestra las jugadas de ambos jugadores

---

## 🔧 PRUEBA 2: Mismo PC (Para Testing Rápido)

### Terminal 1: Servidor
```powershell
cd server
python app.py
```

### Terminal 2: Cliente 1
```powershell
python main_menu.py
```
- Seleccionar Multijugador
- Servidor: `http://localhost:5000`
- Create Room o Find Match

### Terminal 3: Cliente 2
```powershell
python main_menu.py
```
- Seleccionar Multijugador
- Servidor: `http://localhost:5000`
- Join Room (con código) o Find Match

---

## 🐛 Resolución de Problemas

### Problema: "Connection failed"
**Causa:** El servidor no está corriendo o la IP/puerto es incorrecta.

**Solución:**
- Verificar que el servidor esté corriendo (Terminal 1 debe mostrar "Esperando conexiones...")
- Verificar que la IP sea correcta con `ipconfig`
- Verificar que el firewall permita el puerto 5000

### Problema: "Room not found"
**Causa:** El código de sala es incorrecto o la sala ya expiró.

**Solución:**
- Verificar que el código sea exactamente de 6 caracteres
- Que el host haya creado la sala recientemente
- Intentar crear una nueva sala

### Problema: "Room full"
**Causa:** La sala ya tiene 2 jugadores.

**Solución:**
- Crear una nueva sala privada
- Usar matchmaking automático

### Problema: El oponente no ve mis acciones
**Causa:** Sincronización de red fallando.

**Solución:**
1. Verificar en el servidor (Terminal 1) que aparezca:
   ```
   📤 Acción retransmitida: play_card (Room: XXXXXX)
   ```
2. Verificar conexión de red estable
3. Reiniciar ambos clientes

### Problema: "Opponent disconnected"
**Causa:** El otro jugador cerró el juego o perdió conexión.

**Solución:**
- Normal, volver al lobby y buscar otra partida

---

## 🎯 Checklist de Validación

### Funcionalidad Básica
- [ ] Servidor se inicia sin errores
- [ ] Cliente 1 se conecta al servidor
- [ ] Cliente 2 se conecta al servidor
- [ ] Matchmaking empareja a ambos clientes
- [ ] Salas privadas funcionan (crear + unirse)

### Gameplay
- [ ] El jugador anfitrión puede jugar en su primer turno
- [ ] El jugador invitado debe esperar su turno
- [ ] Las cartas jugadas se ven en ambos clientes
- [ ] Los ataques se sincronizan correctamente
- [ ] El cambio de turno funciona
- [ ] El juego detecta victoria/derrota
- [ ] Rendirse funciona correctamente

### Networking
- [ ] Latencia aceptable (< 200ms en LAN)
- [ ] No hay lag visible en las acciones
- [ ] Desconexión maneja correctamente
- [ ] Reconexión permite volver al menú

---

## 📊 Logs del Servidor

Mientras juegas, en la terminal del servidor deberías ver:

```
✅ Cliente conectado: abc123def456
✅ Cliente conectado: ghi789jkl012
🎮 Partida creada: game_abc123de
📤 Acción retransmitida: play_card (Room: game_abc123de)
📤 Acción retransmitida: end_turn (Room: game_abc123de)
📤 Acción retransmitida: declare_attacks (Room: game_abc123de)
```

---

## 🎉 Próximos Pasos (Fase 2+)

Una vez que las pruebas básicas funcionen:

1. **Validación de estado en servidor** - Prevenir trampas
2. **Sistema de cuentas** - Login/registro
3. **Matchmaking por ranking** - ELO/MMR
4. **Replay system** - Guardar y ver partidas
5. **Chat en partida** - Comunicación entre jugadores
6. **Espectadores** - Ver partidas en curso
7. **Torneos** - Sistema de brackets

---

## 📝 Notas Importantes

- **Puerto 5000:** Asegúrate de que no esté en uso por otra aplicación
- **Red LAN:** Para probar entre PCs, ambos deben estar en la misma red local
- **Internet:** Para jugar por Internet, necesitarás port forwarding en tu router o un servidor cloud
- **Latencia:** En LAN deberías tener < 50ms, por Internet depende de la distancia

---

## 🆘 Soporte

Si encuentras problemas:
1. Revisar logs del servidor (Terminal 1)
2. Verificar connectivity con `ping IP_DEL_SERVIDOR`
3. Reiniciar servidor y clientes
4. Verificar versiones de las librerías

**¡Listo para jugar! 🎮✨**
