# Multiplayer Development Roadmap

## Estado Actual ✅
- ✅ Servidor Flask-SocketIO funcionando (`server/app.py`)
- ✅ Servidor puede crear juegos y manejar estado
- ✅ Cliente puede conectarse y recibir estados del servidor
- ✅ Serialización de cartas y estado funcionando
- ✅ Base game completamente limpia de código multiplayer
- ✅ Todas las dependencias instaladas

## Problemas Identificados ⚠️
1. **Arquitectura Mixta**: El código mezcla single-player con multiplayer
2. **Game Class Limpia**: Ya no tiene `multiplayer_mode`, `is_host`, `game_sync`
3. **Integración Rota**: `main_menu.py` tiene código multiplayer desactivado
4. **Cliente Necesita Refactor**: Debe visualizar estado sin ejecutar lógica

## Plan de Reconstrucción 🚀

### Fase 1: Estructura Base (Arquitectura Limpia)
**Objetivo**: Crear estructura separada para multiplayer sin tocar single-player

**Archivos a Crear**:
1. `src/multiplayer/server_game.py` - Game logic del lado del servidor
2. `src/multiplayer/client_view.py` - Vista cliente (solo visualización)
3. `src/multiplayer/multiplayer_gui.py` - GUI específica para multiplayer
4. `server/game_handler.py` - Handler separado para lógica del servidor

**Decisiones de Diseño**:
- Servidor mantiene **UN SOLO** `Game` instance por partida
- Servidor ejecuta toda la lógica: validación, ejecución, estado
- Clientes **NO** crean instancias de `Game`
- Clientes solo:
  - Envían acciones (play_card, end_turn, declare_attacks)
  - Reciben estados completos del servidor
  - Visualizan el estado recibido

### Fase 2: Implementación Básica (Card Play)
**Objetivo**: Dos jugadores pueden jugar cartas y verse mutuamente

**Features**:
- ✅ Conexión y matchmaking (ya funciona)
- 🔨 Jugar cartas de criatura
- 🔨 Visualización sincronizada
- 🔨 Turno del oponente

**No Incluye**:
- ❌ Combate
- ❌ Hechizos con objetivo
- ❌ Habilidades de campeón
- ❌ Habilidades de cartas (Furia, Volar, etc.)

### Fase 3: Sistema de Combate
**Objetivo**: Implementar combat completo

**Features**:
- Declarar atacantes
- Declarar bloqueadores
- Resolución de daño
- Muerte de criaturas

### Fase 4: Features Completas
**Objetivo**: Implementar todo el juego

**Features**:
- Hechizos con targeting
- Habilidades de campeón
- Habilidades de cartas
- Victoria/Derrota

## Arquitectura Propuesta 📐

### Servidor (Autoritativo)
```python
# server/game_handler.py
class MultiplayerGameHandler:
    def __init__(self):
        self.games = {}  # room_id -> Game instance
    
    def create_game(self, room_id, player1_sid, player2_sid):
        # Crear Game con mazos y todo
        game = Game(player1, player2, on_update=lambda: None)
        self.games[room_id] = {
            'game': game,
            'players': {player1_sid: 'player', player2_sid: 'ai'}
        }
        return game
    
    def handle_play_card(self, room_id, player_sid, card_index):
        # Validar turno
        # Ejecutar game.play_card()
        # Broadcast estado actualizado
        pass
    
    def get_state_for_player(self, room_id, player_sid):
        # Retornar estado desde perspectiva del jugador
        pass
```

### Cliente (Visualización)
```python
# src/multiplayer/client_view.py
class MultiplayerClientView:
    """Cliente que solo visualiza, no ejecuta lógica"""
    
    def __init__(self, root, network_manager, is_host):
        self.root = root
        self.network = network_manager
        self.is_host = is_host
        
        # Solo estado visual
        self.my_hand = []
        self.my_active = []
        self.opponent_hand_count = 0
        self.opponent_active = []
        
        # Setup callbacks
        self.network.on_game_state = self.apply_state
    
    def apply_state(self, state):
        """Actualizar vista con estado del servidor"""
        self.my_hand = state['my_hand']
        self.opponent_hand_count = state['opponent_hand_count']
        self.update_ui()
    
    def on_play_card(self, index):
        """Enviar acción al servidor, no ejecutar local"""
        self.network.send_action({
            'type': 'play_card',
            'card_index': index
        })
```

## Próximos Pasos Inmediatos 🎯

### Paso 1: Crear game_handler.py
Separar lógica de servidor de app.py para mantenerlo limpio

### Paso 2: Crear client_view.py  
Vista simple que solo recibe y muestra estado

### Paso 3: Actualizar main_menu.py
Usar nueva arquitectura para iniciar multiplayer

### Paso 4: Test End-to-End
Dos clientes conectados pueden jugar cartas básicas

## Criterios de Éxito ✓

**Fase 1 Completa Cuando**:
1. Dos clientes pueden conectarse
2. Ver mano inicial de 5 cartas cada uno
3. Jugador 1 juega una carta de criatura
4. Jugador 2 VE la carta aparecer en active zone de oponente
5. Jugador 2 termina turno
6. Jugador 1 puede jugar de nuevo

**NO** es necesario:
- Combate
- Hechizos
- Habilidades
- Ganar/Perder

Solo: **Jugar cartas y turnarse**
