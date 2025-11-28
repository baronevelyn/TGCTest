# Multiplayer UI - Documentation

## Overview
Nueva interfaz gráfica diseñada específicamente para partidas online de TCG. Construida desde cero con separación clara entre visualización y lógica de juego.

## Demo
Para probar la UI sin conexión:
```bash
python tools\demo_multiplayer_ui.py
```

## Características Implementadas ✅

### 1. Zonas de Juego

#### Sección del Oponente (Superior)
- **Barra de información**: Vida, Maná, Cantidad de cartas
- **Mano del oponente**: Cartas ocultas (reversos)
- **Zona activa del oponente**: Criaturas visibles con stats completos

#### Separador Visual
- Línea dorada que divide claramente ambos lados del tablero

#### Sección del Jugador (Inferior)
- **Zona activa**: Tus criaturas con indicadores de ataque
- **Mano**: Cartas completas y clickeables
- **Barra de información**: Vida, Maná, Estado del turno
- **Botones de acción**: End Turn, Declare Attacks, Cancel

### 2. Panel Lateral Derecho

#### Log de Acciones (Superior)
- Registro cronológico de todas las acciones del juego
- Fondo oscuro con texto verde (estilo terminal)
- Auto-scroll hacia el último mensaje
- Incluye:
  - Cartas jugadas
  - Ataques realizados
  - Cambios de turno
  - Cambios de maná

#### Chat (Inferior)
- Chat en tiempo real entre jugadores
- Mensajes diferenciados por color:
  - **Azul**: Mensajes propios
  - **Rojo**: Mensajes del oponente
  - **Naranja**: Mensajes del sistema
- Campo de entrada con botón Send
- Enter para enviar rápido
- Auto-scroll hacia último mensaje

### 3. Visualización de Cartas

#### Cartas en Mano
- **Dimensiones**: 90x110 px
- **Información mostrada**:
  - 💎 Costo de maná (esquina superior derecha)
  - Nombre de la carta
  - ⚔️ Ataque / 🛡️ Defensa (para Tropas)
  - Habilidades (primeras 2)
- **Estados**:
  - Normal: Fondo azul (Tropa) o morado (Hechizo)
  - Hover: Borde hundido para feedback visual
  - Clickeable solo en tu turno

#### Cartas en Zona Activa
- **Información adicional**:
  - ⚡ Indicador de puede atacar
  - Fondo gris si está girada (tapped)
- **Modo ataque**:
  - Clickeable cuando está en modo selección de atacantes
  - Borde rojo grueso cuando está seleccionada

#### Cartas del Oponente (Mano)
- **Reverso**: 50x70 px con icono 🃏
- **Fondo morado**
- Solo muestra cantidad, no contenido

### 4. Sistema de Acciones

#### Jugar Cartas
1. Tu turno activado
2. Click en carta de tu mano
3. Callback `on_play_card(index)` ejecutado
4. UI actualizada automáticamente

#### Declarar Ataques
1. Click en "DECLARE ATTACKS"
2. UI entra en modo selección
3. Click en criaturas que pueden atacar
4. Criaturas seleccionadas destacadas en rojo
5. Click en "CONFIRM ATTACKS" o "CANCEL"
6. Callback `on_declare_attacks([indices])` ejecutado

#### Terminar Turno
1. Click en "END TURN"
2. Callback `on_end_turn()` ejecutado
3. UI desactiva controles

#### Enviar Chat
1. Escribir en campo de entrada
2. Enter o click en "Send"
3. Callback `on_send_chat(message)` ejecutado
4. Mensaje aparece en chat con color propio

### 5. Gestión de Turnos

#### Tu Turno
- ✅ Indicador verde "YOUR TURN"
- Botones END TURN y DECLARE ATTACKS activos
- Cartas en mano clickeables
- Criaturas pueden ser seleccionadas para ataque

#### Turno del Oponente
- ⏳ Indicador "Opponent's turn..."
- Todos los botones desactivados
- Cartas en mano no clickeables
- Solo observación

## Arquitectura de la UI

### Clase Principal: `MultiplayerGameUI`

```python
MultiplayerGameUI(
    root: tk.Tk,
    player_name: str,
    opponent_name: str,
    on_play_card: Callable[[int], None],
    on_end_turn: Callable[[], None],
    on_declare_attacks: Callable[[List[int]], None],
    on_send_chat: Callable[[str], None]
)
```

### Data Class: `CardDisplay`

```python
@dataclass
class CardDisplay:
    name: str
    cost: int
    attack: int
    defense: int
    card_type: str  # 'Troop' or 'Spell'
    abilities: List[str]
    can_attack: bool = False
    is_tapped: bool = False
```

### Métodos Públicos

#### Actualización de Estado
```python
# Actualizar turno
ui.set_turn(is_my_turn: bool)

# Actualizar estadísticas
ui.update_player_stats(life: int, mana: int, max_mana: int)
ui.update_opponent_stats(life: int, mana: int, max_mana: int, hand_count: int)

# Actualizar zonas
ui.update_my_hand(cards: List[CardDisplay])
ui.update_my_active(cards: List[CardDisplay])
ui.update_opponent_hand(card_count: int)
ui.update_opponent_active(cards: List[CardDisplay])
```

#### Logging y Chat
```python
# Agregar al log de acciones
ui.log_action(message: str)

# Agregar mensaje de chat
ui.add_chat_message(sender: str, message: str)

# Agregar mensaje del sistema
ui.add_system_message(message: str)
```

### Función Helper
```python
# Convertir dict a CardDisplay
card = card_from_dict({
    'name': 'Goblin',
    'cost': 1,
    'attack': 2,
    'defense': 1,
    'card_type': 'Troop',
    'abilities': ['Furia'],
    'can_attack': True,
    'is_tapped': False
})
```

## Paleta de Colores

### Zonas del Tablero
- **Fondo general**: `#1a1a2e` (Gris muy oscuro)
- **Oponente info**: `#e74c3c` (Rojo)
- **Oponente mano**: `#2c3e50` (Gris oscuro)
- **Oponente activo**: `#34495e` (Gris medio)
- **Mi activo**: `#2c3e50` (Gris oscuro)
- **Mi mano**: `#16213e` (Azul oscuro)
- **Mi info**: `#27ae60` (Verde)
- **Separador**: `#f39c12` (Dorado)

### Cartas
- **Tropa**: `#3498db` (Azul)
- **Hechizo**: `#9b59b6` (Morado)
- **Girada**: `#7f8c8d` (Gris)
- **Reverso**: `#8e44ad` (Morado oscuro)
- **Seleccionada**: `#e74c3c` (Rojo)

### Botones
- **End Turn**: `#e67e22` (Naranja)
- **Declare Attacks**: `#c0392b` (Rojo oscuro)
- **Confirm Attacks**: `#27ae60` (Verde)
- **Cancel**: `#95a5a6` (Gris)
- **Send Chat**: `#3498db` (Azul)

### Texto
- **Stats dorados**: `#f1c40f`
- **Texto claro**: `#ecf0f1`
- **Log verde**: `#a0d468`

## Flujo de Interacción

### Inicio de Partida
```python
# 1. Crear UI
ui = MultiplayerGameUI(root, "Player1", "Player2", callbacks...)

# 2. Inicializar estado
ui.update_player_stats(25, 1, 1)
ui.update_opponent_stats(25, 1, 1, 5)
ui.update_my_hand(initial_cards)
ui.update_opponent_hand(5)

# 3. Empezar turno
ui.set_turn(is_my_turn=True)
ui.log_action("🎮 Game started!")
ui.add_system_message("Good luck!")
```

### Durante el Juego
```python
# Cuando el jugador hace algo
def on_play_card(index):
    # Enviar acción al servidor
    network.send_action({'type': 'play_card', 'index': index})

# Cuando llega estado del servidor
def on_server_state(state):
    ui.update_my_hand(state['my_hand'])
    ui.update_my_active(state['my_active'])
    ui.update_opponent_active(state['opponent_active'])
    ui.update_opponent_hand(state['opponent_hand_count'])
    ui.set_turn(state['is_my_turn'])
    ui.log_action(state.get('last_action', ''))
```

## Próximos Pasos

Esta UI está lista para integrarse con:
1. **NetworkManager**: Para enviar acciones al servidor
2. **ClientGameSync**: Para recibir y aplicar estados del servidor
3. **Main Menu**: Para lanzar desde el menú multiplayer

### Integración Pendiente
- Conectar callbacks con network manager
- Recibir estados del servidor y actualizar UI
- Manejar desconexiones
- Implementar animaciones (opcional)

## Notas de Diseño

### Principios
1. **Solo Visualización**: La UI NO ejecuta lógica de juego
2. **Callbacks Simples**: Solo envía acciones, no valida
3. **Estado Externo**: Todo el estado viene del servidor
4. **Responsive**: Se adapta a diferentes resoluciones
5. **Feedback Visual**: Hover, selección, estados claros

### Performance
- Todas las zonas se reconstruyen completamente en cada update
- No hay animaciones pesadas por ahora
- Scrolling automático en logs y chat
- Límite de 300px para panel lateral (no crece infinitamente)

### Accesibilidad
- Cursores apropiados (hand2 para clickeable)
- Estados visuales claros (disabled buttons)
- Colores con buen contraste
- Texto legible (Arial, Consolas)
