# 🌐 Mini TCG - Sistema Multiplayer

## ✅ FASE 1 COMPLETA

El sistema multiplayer está implementado y listo para probar entre dos PCs.

### 📦 Componentes Implementados

#### Backend (Servidor)
- **`server/app.py`** - Servidor Flask-SocketIO relay
  - Matchmaking automático
  - Salas privadas con códigos de 6 caracteres
  - Validación básica de acciones
  - Retransmisión de mensajes entre clientes

#### Frontend (Cliente)
- **`src/multiplayer/network_manager.py`** - Cliente Socket.IO
- **`src/multiplayer/game_state_sync.py`** - Sincronización de estado del juego
- **`src/multiplayer/message_protocol.py`** - Protocolo de mensajes
- **`src/multiplayer_lobby.py`** - UI de lobby en Tkinter
- **`src/game_logic.py`** - Adaptado para soportar modo multiplayer

#### Integración
- **`main_menu.py`** - Botón de Multijugador añadido al menú principal

---

## 🚀 Inicio Rápido

### 1. Verificar Setup
```bash
python test_multiplayer_setup.py
```

### 2. Configurar Servidor (si juegas en red local)
```bash
python setup_server.py
```

### 3. Iniciar Servidor
```bash
cd server
python app.py
```

### 4. Iniciar Clientes
En dos terminales diferentes (o dos PCs):
```bash
python main_menu.py
```
- Seleccionar **🌐 MULTIJUGADOR**
- Configurar servidor (`http://localhost:5000` o `http://IP_DEL_SERVIDOR:5000`)
- Click **Connect**
- **Opción A:** Click **Find Match** (ambos clientes)
- **Opción B:** Cliente 1 → **Create Room**, Cliente 2 → **Join Room** (con código)

---

## 🎮 Características

### Funcionalidad Actual (Fase 1)
- ✅ Conexión cliente-servidor con Socket.IO
- ✅ Matchmaking automático
- ✅ Salas privadas con códigos
- ✅ Sincronización de juego en tiempo real:
  - Jugar cartas (tropas y hechizos)
  - Activar habilidades
  - Declarar ataques
  - Finalizar turno
  - Rendirse
- ✅ Detección de desconexión
- ✅ Validación básica de acciones en servidor

### Pendiente (Fases 2-5)
- ⏳ Validación completa de estado en servidor (anti-trampas)
- ⏳ Sistema de cuentas (login/registro)
- ⏳ Matchmaking por ranking (ELO/MMR)
- ⏳ Sistema de replay
- ⏳ Chat en partida
- ⏳ Espectadores
- ⏳ Torneos

---

## 📡 Arquitectura

### Patrón Relay
```
Cliente 1 <--> Servidor <--> Cliente 2
```

El servidor actúa como intermediario:
1. Cliente envía acción al servidor
2. Servidor valida y retransmite al oponente
3. Ambos clientes actualizan su estado local

### Protocolo de Mensajes
- **`game_action`** - Acción de juego (play_card, attack, etc.)
- **`match_found`** - Emparejamiento exitoso
- **`opponent_action`** - Acción del oponente recibida
- **`opponent_disconnected`** - Oponente desconectado

---

## 🔧 Configuración

### Puertos
- **5000** - Socket.IO/HTTP (servidor)

### Firewall (Windows)
```powershell
New-NetFirewallRule -DisplayName "TCG Server" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow
```

### Dependencias
```bash
pip install flask flask-socketio gevent gevent-websocket python-socketio[client] python-engineio
```

---

## 🐛 Troubleshooting

| Problema | Solución |
|----------|----------|
| "Connection failed" | Verificar que servidor esté corriendo y IP sea correcta |
| "Room not found" | Verificar código de sala (6 caracteres) |
| "Room full" | Sala tiene 2 jugadores, crear nueva |
| Acciones no se sincronizan | Verificar logs del servidor, revisar conexión |
| Alta latencia | Normal > 200ms en Internet, < 50ms en LAN |

Ver logs del servidor para debug detallado.

---

## 📚 Documentación

- **`docs/MULTIPLAYER_P2P_PLAN.md`** - Plan completo de implementación (Fases 1-5)
- **`docs/MULTIPLAYER_TESTING_GUIDE.md`** - Guía detallada de pruebas
- **`PROTOTIPO_MULTIPLAYER_INSTRUCCIONES.md`** - Instrucciones del prototipo inicial

---

## 🎯 Prueba de Aceptación

### Checklist Básico
- [ ] Servidor se inicia sin errores
- [ ] Dos clientes se conectan al servidor
- [ ] Matchmaking empareja clientes
- [ ] Salas privadas funcionan
- [ ] Host puede jugar su primer turno
- [ ] Guest espera su turno
- [ ] Cartas se sincronizan entre clientes
- [ ] Ataques se reflejan en ambos lados
- [ ] Cambio de turno funciona
- [ ] Juego detecta victoria/derrota
- [ ] Desconexión se maneja correctamente

---

## 🏆 Estado del Proyecto

**Versión:** 1.0 (Fase 1 Completa)  
**Última actualización:** 25 de Noviembre 2025  
**Próxima fase:** Validación de estado en servidor

**¡Listo para jugar entre dos PCs! 🎮✨**
