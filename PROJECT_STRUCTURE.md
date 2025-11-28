# Project Structure

## Root Directory
```
TGCTest/
├── main_menu.py          # Main entry point - Game launcher
├── massive_simulator.py  # Mass game simulation tool
├── README.md            # Project documentation
├── requirements.txt     # Python dependencies
```

## Source Code (`src/`)
Core game logic and systems:
- **Game Logic**: `game_logic.py` - Core game mechanics (single-player)
- **GUI**: `game_gui.py` - Tkinter-based game interface with animations
- **Cards**: `cards.py`, `models.py` - Card definitions and data models
- **Champions**: `champions.py` - Champion abilities and stats
- **AI System**: 
  - `ai_player.py` - Basic AI
  - `ai_difficulty.py` - Advanced AI with 10 difficulty levels
- **Deck Building**: `deck_builder.py` - Interactive deck constructor
- **Analysis**: `game_analysis.py`, `log_analyzer.py` - Game statistics
- **Difficulty Selector**: `difficulty_selector.py` - UI for AI difficulty

### Multiplayer (`src/multiplayer/`)
⚠️ **Currently under reconstruction**
- `client_game_sync.py` - Client state synchronization (working)
- `game_state_sync.py` - Legacy P2P system (deprecated)
- `network_manager.py` - Network communication layer
- `message_protocol.py` - Network message definitions

## Server (`server/`)
Server-authoritative multiplayer architecture:
- `app.py` - Flask-SocketIO server with game state management
- `setup_server.py` - Server configuration and firewall setup

## Tests (`tests/`)
- `test_ai_difficulty.py` - AI system tests
- `test_game_analysis.py` - Game analysis tests
- `test_deck_builder.py` - Deck builder tests
- `ejemplos_uso_ia.py` - AI usage examples

## Tools (`tools/`)
Development and analysis utilities:
- `demo_improved_ai.py` - AI system showcase
- `massive_log_analyzer_v2.py` - Log analysis tool

## Documentation (`docs/`)
- `README.md` - Main documentation
- `SPELL_SYSTEM.md` - Spell mechanics
- `README_AI_DIFFICULTY.md` - AI difficulty guide
- `SISTEMA_DIFICULTAD.txt` - Difficulty system (Spanish)
- `CAMPEONES.txt` - Champion information
- `RESUMEN_COMPLETO.txt` - Complete summary
- Multiplayer documentation (archived - being rewritten):
  - `FASE1_MULTIPLAYER_COMPLETA.md`
  - `INICIO_RAPIDO_3MIN.md`
  - `INTEGRATION_SUMMARY.md`
  - `PROTOTIPO_MULTIPLAYER_INSTRUCCIONES.md`
  - `RESUMEN_EJECUTIVO_MULTIPLAYER.md`

## Data (`data/`)
Game logs and analysis results:
- `ANALISIS_AVANZADO_*.txt` - Advanced analysis
- `GAME_LOGS_*.txt` - Individual game logs
- `MASSIVE_LOGS_*.txt` - Mass simulation logs
- `STATS_*.txt` - Statistics summaries

## Assets (`assets/`)
- `cards/` - Card images (auto-generated)

## Utilities (`utils/`)
- `generate_assets.py` - Card image generator
- `generate_spell_assets.py` - Spell card generator

## Archived (`archived/`)
Old/deprecated code kept for reference:
- `test_multiplayer_setup.py` - Old multiplayer setup
- `test_multiplayer_prototype.py` - Old multiplayer prototype

## Current Status

### ✅ Fully Functional
- Single-player game with AI
- 10-level AI difficulty system
- Deck builder
- Game analysis and logging
- Mass simulation tools

### ⚠️ Under Reconstruction
- Multiplayer system (being rebuilt with clean architecture)
- Server-authoritative model implemented but not integrated
- Base game cleaned of multiplayer code for clean separation

### 📋 Next Steps
1. Design new multiplayer architecture (separate from base game)
2. Implement Phase 1: Basic card play
3. Implement Phase 2: Combat system
4. Implement Phase 3: Complete features (spells, abilities)
