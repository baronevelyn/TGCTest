# 🎮 Plan de Implementación Multiplayer P2P para Mini TCG

## 📋 Análisis del Estado Actual

### Arquitectura Actual
- **Juego Local**: Todo el estado del juego está en una única instancia de `Game`
- **Turnos**: Sistema secuencial `'player'` → `'ai'` 
- **IA**: `ImprovedAIPlayer` toma decisiones automáticamente
- **GUI**: Tkinter con `game_gui.py` y callbacks síncronos
- **Estado del Juego**: Completamente en memoria local

### Componentes Clave Identificados
```
game_logic.py (803 líneas)
├── class Game
│   ├── __init__(player, ai, on_update)
│   ├── start() - Inicialización
│   ├── start_turn(who) - Inicio de turno
│   ├── play_card(card_index, target) - Jugar carta
│   ├── end_turn() - Fin de turno
│   ├── ai_turn() - Turno de IA
│   └── combat system (attack, block, etc.)
│
models.py
├── Player(name, deck, champion, ai_config)
├── Card(properties)
└── Deck(cards)
│
game_gui.py
└── UI callbacks y rendering
```

---

## 🎯 Objetivos del Multiplayer P2P

### Requisitos Funcionales
1. **Conexión P2P** entre 2 jugadores
2. **Sincronización de estado** del juego en tiempo real
3. **Turnos alternados** entre jugadores reales
4. **Validación** de acciones en ambos lados
5. **Reconexión** en caso de desconexión temporal
6. **Chat opcional** entre jugadores

### Requisitos No Funcionales
- **Latencia aceptable**: < 200ms para acciones
- **Seguridad**: Validación anti-cheating
- **Confiabilidad**: Manejo de desconexiones
- **UX**: Interfaz clara de conexión/espera

---

## 🏗️ Arquitectura Propuesta

### Opción 1: Socket.IO + Servidor Relay (Recomendada para empezar)
```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│  Player 1   │◄────────┤    Servidor  ├────────►│  Player 2   │
│   (Client)  │  Socket │     Relay    │ Socket  │   (Client)  │
└─────────────┘   .IO   └──────────────┘   .IO   └─────────────┘
```

**Ventajas:**
- ✅ Fácil atravesar NAT/firewalls
- ✅ Bibliotecas maduras (python-socketio)
- ✅ Servidor simple solo retransmite mensajes
- ✅ Puede expandirse a matchmaking

**Desventajas:**
- ⚠️ Requiere servidor (puede ser gratuito: Heroku, Railway, Render)
- ⚠️ No es P2P puro (pero latencia similar)

### Opción 2: WebRTC P2P Puro
```
┌─────────────┐                            ┌─────────────┐
│  Player 1   │◄─────── WebRTC ──────────►│  Player 2   │
│   (Client)  │     Direct Connection      │   (Client)  │
└─────────────┘                            └─────────────┘
       │                                          │
       └──────► STUN Server (solo inicial) ◄─────┘
```

**Ventajas:**
- ✅ Verdadero P2P sin servidor central
- ✅ Menor latencia potencial
- ✅ Mayor privacidad

**Desventajas:**
- ❌ Más complejo de implementar
- ❌ Problemas con NAT simétrico
- ❌ Requiere STUN/TURN servers igualmente

### Opción 3: ZeroMQ + Rendezvous Server
```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│  Player 1   │         │  Rendezvous  │         │  Player 2   │
│             │────────►│    Server    │◄────────│             │
│   (ZMQ)     │ Obtain  │  (Get peer   │ Obtain  │   (ZMQ)     │
│             │ peer IP │   address)   │ peer IP │             │
└──────┬──────┘         └──────────────┘         └──────┬──────┘
       │                                                  │
       └─────────────► Direct ZMQ Connection ◄───────────┘
```

**Ventajas:**
- ✅ Alta performance
- ✅ Patrones de mensajería robustos
- ✅ Conexión directa después de rendezvous

**Desventajas:**
- ⚠️ Curva de aprendizaje
- ⚠️ Puede fallar con NAT estricto

---

## 📦 Implementación Recomendada: Socket.IO

### Stack Tecnológico
```python
# Backend (Servidor Relay)
- Flask: Framework web ligero
- Flask-SocketIO: WebSocket handling
- eventlet/gevent: Async I/O

# Frontend (Cliente)
- python-socketio[client]: Cliente Python
- Tkinter: GUI existente (mantener)
- Threading: Para no bloquear UI
```

### Estructura de Carpetas Propuesta
```
TGCTest/
├── src/
│   ├── multiplayer/
│   │   ├── __init__.py
│   │   ├── network_manager.py      # Maneja conexión Socket.IO
│   │   ├── game_state_sync.py      # Sincroniza estado del juego
│   │   ├── message_protocol.py     # Define mensajes P2P
│   │   └── lobby_manager.py        # Sistema de lobbies/matchmaking
│   │
│   ├── game_logic_mp.py           # Game class adaptada para MP
│   └── game_gui_mp.py             # GUI adaptada para MP
│
├── server/
│   ├── app.py                     # Servidor Flask-SocketIO
│   ├── room_manager.py            # Gestión de salas
│   ├── requirements.txt
│   └── Procfile                   # Para despliegue
│
└── main_menu.py                   # Agregar opción "Multiplayer"
```

---

## 🔄 Protocolo de Mensajes

### Mensajes de Conexión
```python
# Cliente → Servidor
{
    "type": "join_lobby",
    "player_name": "Victor",
    "deck_code": "ABC123XYZ"  # Hash del mazo para validación
}

# Servidor → Clientes (ambos)
{
    "type": "match_found",
    "room_id": "game_12345",
    "opponent": "Juan",
    "you_start": true  # Indica quién empieza
}
```

### Mensajes de Juego
```python
# Inicio de partida
{
    "type": "game_start",
    "your_champion": {...},
    "your_deck": [...],
    "opponent_champion": {...},
    "opponent_deck_size": 40
}

# Acción: Jugar carta
{
    "type": "play_card",
    "player_id": "player1",
    "card_index": 2,
    "card_data": {...},      # Datos completos para validación
    "target_index": null,
    "mana_after": 3
}

# Acción: Atacar
{
    "type": "attack",
    "player_id": "player1",
    "attacker_index": 1,
    "target": "player",      # o index de criatura
    "blocker_index": null
}

# Acción: Fin de turno
{
    "type": "end_turn",
    "player_id": "player1",
    "game_state_hash": "abc123"  # Para verificar sincronización
}

# Estado de sincronización (cada turno)
{
    "type": "state_sync",
    "turn": 5,
    "active_player": "player1",
    "player1_life": 15,
    "player2_life": 18,
    "checksum": "xyz789"
}
```

---

## 🛠️ Fases de Implementación

### FASE 1: Infraestructura Base (1-2 días)
**Objetivo:** Servidor funcional + cliente básico conectándose

**Tareas:**
1. ✅ Crear servidor Flask-SocketIO básico
2. ✅ Implementar `NetworkManager` en cliente
3. ✅ Sistema de salas/rooms
4. ✅ Prueba de conexión bidireccional
5. ✅ Lobby de espera (UI simple)

**Entregable:** Dos clientes pueden conectarse a una sala y verse

---

### FASE 2: Sincronización de Estado (2-3 días)
**Objetivo:** Estado del juego sincronizado entre clientes

**Tareas:**
1. ✅ Definir protocolo de mensajes completo
2. ✅ Implementar serialización de `Player`, `Card`, `Game`
3. ✅ Crear `GameStateSync` para broadcast de acciones
4. ✅ Sistema de validación de acciones
5. ✅ Manejo de desincronización (checksums)

**Entregable:** Acciones de un jugador se replican en el otro cliente

---

### FASE 3: Lógica de Juego Adaptada (2-3 días)
**Objetivo:** Game loop funcionando en modo multiplayer

**Tareas:**
1. ✅ Refactorizar `Game` para separar lógica local/remota
2. ✅ Eliminar lógica de IA cuando es multiplayer
3. ✅ Implementar turnos remotos
4. ✅ Combate con bloqueo remoto (esperar decisión)
5. ✅ Sistema de timeout para acciones

**Entregable:** Partida completa jugable 1v1

---

### FASE 4: UI/UX Multiplayer (1-2 días)
**Objetivo:** Interfaz pulida para multiplayer

**Tareas:**
1. ✅ Lobby de búsqueda de partida
2. ✅ Indicador "Esperando al oponente..."
3. ✅ Chat básico (opcional)
4. ✅ Botón "Rendirse"
5. ✅ Pantalla de desconexión/reconexión

**Entregable:** UX completa para multiplayer

---

### FASE 5: Pulido y Testing (1-2 días)
**Objetivo:** Sistema estable y probado

**Tareas:**
1. ✅ Testing extensivo de casos edge
2. ✅ Optimización de latencia
3. ✅ Manejo robusto de errores
4. ✅ Logging y debugging
5. ✅ Documentación de uso

**Entregable:** Sistema multiplayer estable y documentado

---

## 🔒 Seguridad y Anti-Cheating

### Validaciones Necesarias
```python
# Servidor debe validar:
1. ✅ El jugador tiene la carta que dice jugar
2. ✅ Tiene suficiente maná
3. ✅ Es su turno
4. ✅ La acción es legal (ej: atacar con criatura untapped)
5. ✅ Los targets son válidos

# Cliente debe validar:
1. ✅ Los mensajes vienen de su oponente actual
2. ✅ Las acciones del oponente son válidas
3. ✅ El estado sincronizado es consistente
```

### Hash de Estado
```python
def compute_game_hash(game_state):
    """Genera hash del estado para detectar desincronización"""
    data = {
        'turn': game_state.turn_number,
        'p1_life': game_state.player1.life,
        'p2_life': game_state.player2.life,
        'p1_board': [card.id for card in game_state.player1.active_zone],
        'p2_board': [card.id for card in game_state.player2.active_zone],
    }
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
```

---

## 💾 Datos a Sincronizar

### Al Inicio del Juego
- Mazos completos de ambos jugadores
- Campeones elegidos
- Orden de turnos (random seed compartido)
- IDs únicos para cada carta

### Durante el Juego
- Cada acción (play_card, attack, block, end_turn)
- Cambios de vida
- Cartas robadas (solo cantidad para oponente)
- Efectos activados
- Log de acciones

### Estado Completo (checkpoint cada X turnos)
- Vida de ambos jugadores
- Todas las cartas en todas las zonas
- Maná actual/máximo
- Turno y fase actual

---

## 🧪 Plan de Testing

### Tests Unitarios
```python
# test_network_manager.py
- test_connection()
- test_send_receive_message()
- test_reconnection()
- test_timeout_handling()

# test_game_state_sync.py
- test_serialize_game_state()
- test_deserialize_game_state()
- test_apply_remote_action()
- test_state_validation()
```

### Tests de Integración
```python
# test_multiplayer_flow.py
- test_full_game_flow()
- test_concurrent_actions()
- test_disconnect_reconnect()
- test_invalid_actions_rejected()
```

### Tests Manuales
1. Jugar partida completa 1v1 local
2. Jugar partida en diferentes redes
3. Probar desconexión intencional
4. Probar acciones simultáneas
5. Probar con lag artificial

---

## 📊 Estimación de Recursos

### Tiempo Total: 8-12 días de desarrollo
- Fase 1: 1-2 días
- Fase 2: 2-3 días  
- Fase 3: 2-3 días
- Fase 4: 1-2 días
- Fase 5: 1-2 días

### Recursos del Servidor
- **Gratis (desarrollo):** Railway.app, Render.com (500hrs/mes)
- **Producción:** $5-10/mes (DigitalOcean droplet)
- **Ancho de banda:** ~10KB/turno × 20 turnos × 100 partidas/día = ~20MB/día

### Dependencias Nuevas
```python
# requirements.txt (añadir)
flask==3.0.0
flask-socketio==5.3.5
python-socketio[client]==5.10.0
eventlet==0.33.3
```

---

## 🚀 Despliegue

### Servidor (Railway.app - Gratis)
```bash
# Crear cuenta en railway.app
# Conectar repo de GitHub
# Railway detecta Flask automáticamente
# Despliegue en 1 clic
```

### Cliente (Tu máquina)
```bash
# Sin cambios - solo ejecutar main_menu.py
# Configurar SERVER_URL en config
python main_menu.py
```

---

## 🎮 Flujo de Usuario Final

### 1. Menú Principal
```
┌──────────────────────────────┐
│   🎮 MINI TCG - MENÚ         │
├──────────────────────────────┤
│                              │
│   [⚔️ Jugar vs IA]           │
│                              │
│   [🌐 Multijugador]          │  ← NUEVO
│                              │
│   [🎨 Constructor de Mazos]  │
│                              │
│   [⚙️ Configuración]         │
│                              │
└──────────────────────────────┘
```

### 2. Lobby Multiplayer
```
┌────────────────────────────────┐
│   🌐 MULTIJUGADOR              │
├────────────────────────────────┤
│                                │
│   Tu nombre: [Victor____]      │
│   Tu mazo: [Mazo 1 ▼]         │
│                                │
│   [🔍 Buscar Partida]          │
│                                │
│   [🏠 Crear Sala Privada]      │
│   Código: [______]             │
│   [🚪 Unirse a Sala]           │
│                                │
│   Jugadores en línea: 5        │
│                                │
└────────────────────────────────┘
```

### 3. En Partida
```
┌────────────────────────────────────┐
│  Victor (TÚ)      vs    Juan       │
│  ❤️ 20            vs    ❤️ 20      │
│  💎 5/7           vs    💎 4/6     │
├────────────────────────────────────┤
│                                    │
│   [Tu tablero]                     │
│   [3 cartas en juego]              │
│                                    │
│   ════════════════════             │
│                                    │
│   [Tablero del oponente]           │
│   [2 cartas en juego]              │
│                                    │
├────────────────────────────────────┤
│  💬 Juan: ¡Buena jugada!           │
│  [Escribe mensaje...]              │
│                                    │
│  [⏭️ Fin de Turno]  [🏳️ Rendirse]  │
└────────────────────────────────────┘
```

---

## ❓ Decisiones Pendientes

### 1. ¿Servidor Relay o P2P Puro?
**Recomendación:** Socket.IO con servidor relay
- Más fácil de implementar
- Mejor para atravesar NAT
- Puede evolucionar a matchmaking

### 2. ¿Validación Cliente o Servidor?
**Recomendación:** Híbrida
- Servidor valida reglas básicas (anti-cheating)
- Cliente valida inmediatamente (UX rápida)
- Servidor es fuente de verdad

### 3. ¿Chat de voz?
**Recomendación:** No para v1
- Añade complejidad significativa
- Text chat es suficiente
- Puede añadirse después

### 4. ¿Matchmaking o solo salas?
**Recomendación:** Ambos
- Fase 1: Solo salas privadas
- Fase 2: Añadir matchmaking simple

### 5. ¿Ranking/Ladder?
**Recomendación:** No para v1
- Requiere persistencia (base de datos)
- Puede añadirse después
- Enfocarse en jugabilidad primero

---

## 📝 Próximos Pasos

### Opción A: Empezar Inmediatamente
```bash
# 1. Instalar dependencias
pip install flask flask-socketio python-socketio[client] eventlet

# 2. Crear servidor básico
mkdir server
touch server/app.py

# 3. Crear módulo multiplayer
mkdir src/multiplayer
touch src/multiplayer/__init__.py
touch src/multiplayer/network_manager.py

# 4. Implementar Fase 1
```

### Opción B: Prototipo Rápido (1-2 horas)
Crear un proof-of-concept minimalista que:
1. Conecta 2 clientes a un servidor
2. Sincroniza un contador simple
3. Demuestra comunicación bidireccional
4. Valida que la arquitectura funciona

### Opción C: Profundizar en el Plan
- Revisar arquitectura propuesta
- Discutir alternativas
- Ajustar alcance
- Definir prioridades

---

## 🎯 Recomendación Final

**Comenzar con Opción B (Prototipo):**
1. Crear servidor Socket.IO minimal (50 líneas)
2. Crear cliente de prueba (30 líneas)
3. Probar conexión y envío de mensajes
4. **Si funciona:** Proceder con Fase 1
5. **Si hay problemas:** Reevaluar arquitectura

**Ventajas:**
- ✅ Validación rápida del concepto
- ✅ Detectar problemas temprano
- ✅ Aprender las tecnologías
- ✅ Decisión informada para continuar

---

## 📚 Recursos Útiles

### Documentación
- [Flask-SocketIO Docs](https://flask-socketio.readthedocs.io/)
- [Python-SocketIO Client](https://python-socketio.readthedocs.io/)
- [Socket.IO Protocol](https://socket.io/docs/v4/)

### Tutoriales
- [Real-time Apps with Flask-SocketIO](https://blog.miguelgrinberg.com/post/easy-websockets-with-flask-and-gevent)
- [Building a Multiplayer Game](https://www.youtube.com/watch?v=H8t4DJ3Tdrg)

### Deployment
- [Railway.app Docs](https://docs.railway.app/)
- [Render.com Flask Deploy](https://render.com/docs/deploy-flask)

---

## ✅ Conclusión

El proyecto es **100% viable** con la arquitectura propuesta. Socket.IO es la mejor opción por:
- ✅ Balance perfecto entre complejidad y funcionalidad
- ✅ Ecosistema maduro y bien documentado
- ✅ Facilita futuras expansiones (matchmaking, chat, etc.)
- ✅ Despliegue gratuito disponible

**Tiempo estimado total:** 8-12 días de desarrollo activo
**Complejidad:** Media (con experiencia en Python/Tkinter ya ayuda mucho)

¿Procedemos con el prototipo o quieres ajustar algo del plan?
