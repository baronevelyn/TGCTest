# 🎮 Mini TCG - Trading Card Game

Un juego de cartas coleccionables con sistema de campeones, IA inteligente con 10 niveles de dificultad, simulaciones basadas en datos, y **multiplayer online en tiempo real**.

---

## 📁 Estructura del Proyecto

```
TGCTest/
│
├── 📂 src/                    # Código fuente principal
│   ├── __init__.py
│   ├── models.py              # Modelos de datos (Card, Player, Deck)
│   ├── cards.py               # Sistema de cartas (tropas y hechizos)
│   ├── champions.py           # 8 campeones únicos con habilidades
│   ├── game_logic.py          # Lógica principal del juego (soporta multiplayer)
│   ├── ai_player.py           # IA básica del juego
│   ├── ai_difficulty.py       # Sistema de 10 niveles de dificultad
│   ├── game_gui.py            # Interfaz gráfica del juego
│   ├── deck_builder.py        # Constructor de mazos manual
│   ├── difficulty_selector.py # Selector gráfico de dificultad
│   ├── multiplayer_lobby.py   # Lobby de multijugador
│   ├── game_analysis.py       # Simulador de 280k batallas
│   └── 📂 multiplayer/        # Sistema multiplayer (Fase 1 completa)
│       ├── network_manager.py    # Cliente Socket.IO
│       ├── game_state_sync.py    # Sincronización de estado
│       └── message_protocol.py   # Protocolo de mensajes
│
├── 📂 tests/                  # Tests y ejemplos
│   ├── test_ai_difficulty.py  # Suite de tests del sistema de IA
│   └── ejemplos_uso_ia.py     # 9 ejemplos de uso del sistema
│
├── 📂 docs/                   # Documentación
│   ├── README.md              # README principal del juego
│   ├── README_AI_DIFFICULTY.md # Documentación del sistema de IA
│   ├── SISTEMA_DIFICULTAD.txt  # Guía completa de dificultad
│   ├── RESUMEN_COMPLETO.txt    # Resumen de todo el sistema
│   ├── CAMPEONES.txt          # Descripción de todos los campeones
│   ├── SPELL_SYSTEM.md        # Sistema de hechizos
│   ├── MULTIPLAYER_README.md  # 🌐 Documentación multiplayer
│   ├── MULTIPLAYER_TESTING_GUIDE.md # Guía de pruebas multiplayer
│   └── MULTIPLAYER_P2P_PLAN.md # Plan completo Fases 1-5
│
├── 📂 data/                   # Datos y resultados
│   └── SIMULACION_10000_RESULTADOS.txt  # Resultados de 280k simulaciones
│
├── 📂 utils/                  # Utilidades
│   ├── generate_assets.py    # Generador de assets de tropas
│   └── generate_spell_assets.py  # Generador de assets de hechizos
│
├── 📂 assets/                 # Recursos gráficos
│   ├── troops/                # Imágenes de tropas
│   └── spells/                # Imágenes de hechizos
│
├── 📂 server/                 # 🌐 Servidor multiplayer
│   ├── app.py                 # Servidor Flask-SocketIO
│   └── requirements.txt       # Dependencias del servidor
│
├── main_menu.py              # 🚀 PUNTO DE ENTRADA PRINCIPAL
├── setup_server.py           # Configuración automática del servidor
├── test_multiplayer_setup.py # Verificación del sistema multiplayer
├── requirements.txt          # Dependencias del proyecto
└── FASE1_MULTIPLAYER_COMPLETA.md # 🎉 Estado de implementación
```

---

## 🚀 Inicio Rápido

### 1. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 2. Ejecutar el Juego
```bash
python main_menu.py
```

### 3. Opciones del Menú
- **🎯 Jugar vs IA** - Selecciona dificultad (1-10) y juega
- **🃏 Crear Mazo** - Constructor manual de mazos
- **📊 Simulaciones** - Ejecuta 280,000 simulaciones
- **📈 Ver Estadísticas** - Consulta resultados de simulaciones
- **🌐 MULTIJUGADOR** - Juega online contra otros jugadores (¡NUEVO!)
- **🎲 Juego Rápido** - Mazos y campeones aleatorios

---

## 🌐 Sistema Multiplayer (Fase 1 Completa)

### Inicio Rápido - Multiplayer

#### Paso 1: Iniciar Servidor
```bash
cd server
python app.py
```

#### Paso 2: Configurar Clientes
En cada PC:
```bash
python main_menu.py
```
- Seleccionar **🌐 MULTIJUGADOR**
- Conectar al servidor (`localhost` o IP remota)
- **Find Match** (matchmaking) o **Create/Join Room** (código privado)

### Características Multiplayer
- ✅ **Matchmaking Automático** - Emparejamiento instantáneo
- ✅ **Salas Privadas** - Códigos de 6 caracteres
- ✅ **Sincronización en Tiempo Real** - Todas las acciones sincronizadas
- ✅ **Validación de Acciones** - Servidor valida jugadas
- ✅ **Detección de Desconexión** - Manejo de oponentes desconectados
- ✅ **LAN y Internet** - Juega localmente o en línea

### Acciones Soportadas
- Jugar cartas (tropas y hechizos)
- Activar habilidades
- Declarar ataques
- Finalizar turno
- Rendirse

### Documentación Completa
- 📖 **`docs/MULTIPLAYER_README.md`** - Guía principal
- 📖 **`docs/MULTIPLAYER_TESTING_GUIDE.md`** - Instrucciones de prueba
- 📖 **`FASE1_MULTIPLAYER_COMPLETA.md`** - Estado de implementación

---

## 🎯 Sistema de Dificultad de IA

### 10 Niveles Progresivos

| Nivel | Nombre | Campeones | Calidad | Errores |
|-------|--------|-----------|---------|---------|
| 1 | 🟢 Tutorial | Débiles | 10% | 90% |
| 2 | 🟢 Novato | Débiles | 20% | 80% |
| 3 | 🟡 Aficionado | Mediocres | 30% | 70% |
| 4 | 🟡 Competente | Mediocres | 40% | 60% |
| 5 | 🟠 Avanzado | Buenos | 50% | 50% |
| 6 | 🟠 Experto | Buenos | 60% | 40% |
| 7 | 🔴 Maestro | Top Tier | 70% | 30% |
| 8 | 🔴 Gran Maestro | Top Tier | 80% | 20% |
| 9 | ⚫ Leyenda | Top Tier | 90% | 10% |
| 10 | 💀 Imposible | Mystara/Brutus/Ragnar | 100% | 0% |

### Características
- ✅ Basado en 280,000 simulaciones reales
- ✅ Construcción de mazos optimizada por campeón
- ✅ Estrategias específicas para cada nivel
- ✅ Progresión equilibrada (fácil → imposible)

---

## 🏆 Campeones Disponibles

### S-Tier (73%+ WR)
1. **Mystara** - 73.76% WR
   - Genera 2 tokens 1/1 cada turno
   
2. **Brutus** - 73.27% WR
   - Tropas aliadas +1 ATK
   
3. **Ragnar** - 72.19% WR
   - +1 carta cada turno, no puede bloquear

### Otros Campeones
- **Shadowblade** - 47.41% WR (Tropas ≤3 coste +1 HP)
- **Tacticus** - 42.50% WR (Descarta 1, roba 2)
- **Arcanus** - 38.15% WR (Hechizos -1 maná)
- **Lumina** - 31.86% WR (Cura 2 HP/turno)
- **Sylvana** - 20.87% WR (Tropas 4+ HP ganan +1/+1)

---

## 🃏 Sistema de Juego

### Mecánicas Principales
- **Vida**: 20-40 HP según campeón
- **Maná**: Aumenta cada turno (máx 10)
- **Mazos**: 30-60 cartas (mínimo 15 tropas, 5 hechizos)
- **Zona Activa**: Máximo 7 cartas
- **Mano**: Máximo 10 cartas

### Tipos de Cartas

**Tropas:**
- Goblin, Archer, Knight, Mage, Berserker
- Dragon, Golem, Guardian, Wall, etc.

**Habilidades:**
- **Furia**: Puede atacar dos veces
- **Taunt**: Debe ser bloqueada
- **Volar**: Solo puede ser bloqueada por Volar

**Hechizos:**
- Daño directo (Rayo, Bola de Fuego)
- Curación (Curación, Curación Mayor)
- Remoción (Destierro, Aniquilar)
- Utilidad (Dibujar Cartas)

---

## 📊 Simulaciones y Análisis

### Datos Disponibles
- **280,000 batallas** simuladas
- **28 matchups** (todas las combinaciones de campeones)
- **10,000 partidas** por matchup
- Win rates precisos por campeón

### Ejecutar Simulaciones
```bash
python src/game_analysis.py
```

Los resultados se guardan en `data/SIMULACION_10000_RESULTADOS.txt`

---

## 🧪 Testing

### Ejecutar Tests
```bash
python tests/test_ai_difficulty.py
```

### Tests Incluidos
- ✅ Creación de 10 niveles de dificultad
- ✅ Generación de jugadores IA
- ✅ Composición de mazos
- ✅ Pools de campeones
- ✅ Calidad progresiva

---

## 📚 Documentación

### Documentos Disponibles

- **`docs/README.md`** - Guía principal del juego
- **`docs/README_AI_DIFFICULTY.md`** - Sistema de IA en detalle
- **`docs/SISTEMA_DIFICULTAD.txt`** - Guía completa de dificultad
- **`docs/RESUMEN_COMPLETO.txt`** - Resumen de todo el sistema
- **`docs/CAMPEONES.txt`** - Descripción de campeones
- **`docs/SPELL_SYSTEM.md`** - Sistema de hechizos

---

## 💻 Uso Programático

### Crear una IA
```python
from src.ai_difficulty import SmartAI

# Crear IA de nivel 7
ai = SmartAI(difficulty=7)
ai_player = ai.create_player(deck_size=40)

print(f"IA: {ai_player.name}")
print(f"Campeón: {ai_player.champion.name}")
```

### Iniciar un Juego
```python
from src.game_logic import Game
from src.models import Player
from src.cards import build_random_deck
from src.champions import get_random_champion

# Crear jugadores
player = Player('Jugador', build_random_deck(40), get_random_champion())
ai_player = ai.create_player()

# Iniciar juego
game = Game(player, ai_player, on_game_over_callback)
game.start()
```

---

## 🛠️ Tecnologías

- **Python 3.13**
- **tkinter** - Interfaz gráfica
- **PIL/Pillow** - Procesamiento de imágenes
- **Arquitectura modular** - 8 módulos principales

---

## ⚙️ Configuración

### Requisitos
- Python 3.10+
- tkinter (incluido con Python)
- Pillow (para imágenes)

### Instalación
```bash
# Clonar o descargar el proyecto
cd TGCTest

# Instalar dependencias
pip install -r requirements.txt

# Generar assets (opcional)
python utils/generate_assets.py
python utils/generate_spell_assets.py
```

---

## 🎮 Controles del Juego

### Durante tu Turno
- **Click en carta** - Seleccionar/Jugar carta de la mano
- **Click en tropa** - Declarar atacante
- **Click en objetivo** - Seleccionar objetivo de hechizo/ataque
- **Botón "End Turn"** - Terminar turno

### Bloqueadores
- Cuando la IA ataca, se te pregunta si quieres bloquear
- Selecciona una tropa para bloquear o cancela

---

## 🐛 Problemas Conocidos

### Ragnar - No puede bloquear
✅ **ARREGLADO** - Las tropas de Ragnar ya no pueden defender al jugador

### Errores de Tipo
✅ **ARREGLADO** - Todos los errores de tipo None resueltos

---

## 🔧 Desarrollo

### Estructura de Módulos

**Core:**
- `models.py` - Clases base (Card, Player, Deck)
- `game_logic.py` - Motor del juego

**Cards & Champions:**
- `cards.py` - Definición de cartas
- `champions.py` - Definición de campeones

**AI:**
- `ai_player.py` - IA básica
- `ai_difficulty.py` - Sistema de dificultad

**UI:**
- `game_gui.py` - Interfaz principal
- `deck_builder.py` - Constructor de mazos
- `difficulty_selector.py` - Selector de dificultad

**Analysis:**
- `game_analysis.py` - Simulador y estadísticas

---

## 📈 Estadísticas del Proyecto

- **Archivos de código**: 15+
- **Líneas de código**: ~5,000+
- **Tests**: 7 tests principales
- **Documentos**: 6 archivos de documentación
- **Campeones**: 8 únicos
- **Cartas**: 15 tropas + 10 hechizos
- **Niveles de IA**: 10
- **Simulaciones**: 280,000 batallas

---

## 🚀 Próximas Mejoras

- [ ] Sistema de ranking persistente
- [ ] Estadísticas de victorias/derrotas
- [ ] Logros y desbloqueos
- [ ] Modo torneo
- [ ] Replay de partidas
- [ ] Análisis post-partida
- [ ] Modo entrenamiento adaptativo
- [ ] Perfil de jugador

---

## 📜 Versión

**v2.0.0** - Sistema de Dificultad de IA Completo
- 10 niveles de dificultad basados en datos
- 280,000 simulaciones para balance
- Organización en carpetas
- Documentación completa

### Historial de Releases Recientes

**v0.1.8** - Corrección robo invitado
- Auto `start_turn` al detectar cambio de turno vía snapshot (`game_state_update`).
- Soluciona que el jugador que no empieza (invitado) no robara cartas.

**v0.1.7** - Tk incluido + fallback
- Reconstruido con Python 3.12 (Tk dentro del onefile).
- Fallback con MessageBox nativo si faltara Tk.
- Incluye fix de sincronización de robo (v0.1.6).

**v0.1.6** - Fix sincronización de robo en Multiplayer
- Se añadió handler de `game_state_update` en el cliente para aplicar el snapshot completo del estado.
- Las manos del oponente ahora reflejan correctamente el tamaño tras robos (se crean cartas "Hidden").
- Corrige bug donde un jugador quedaba bloqueado con solo las 5 cartas iniciales.

**v0.1.5** - Build OneFile funcional con GUI
- Se reconstruyó con Python 3.12 + tkinter incluido.
- Flags: `-OneFile -PythonExe -ForceVenv` en `build_exe.ps1`.
- Soluciona salida silenciosa por ausencia de tkinter.

---

## 👥 Créditos

Sistema desarrollado con:
- 280,000 simulaciones de batalla
- Análisis estadístico de 8 campeones
- Optimización basada en datos
- Testing exhaustivo

---

## 📞 Soporte

Para problemas o sugerencias:
1. Ejecuta los tests: `python tests/test_ai_difficulty.py`
2. Consulta la documentación en `docs/`
3. Revisa los ejemplos en `tests/ejemplos_uso_ia.py`

---

**¡Disfruta el juego!** 🎮

```
python main_menu.py
```
