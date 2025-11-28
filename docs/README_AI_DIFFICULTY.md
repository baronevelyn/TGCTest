# 🤖 Sistema de Dificultad de IA - Mini TCG

## 📋 Descripción

Sistema completo de 10 niveles de dificultad para la IA del juego, basado en **280,000 simulaciones de batalla** reales. Cada nivel ajusta:

- **Campeones disponibles** (desde los más débiles hasta los dominantes)
- **Calidad de construcción de mazo** (0% aleatorio → 100% optimizado)
- **Calidad de decisiones** (0% aleatorio → 100% óptimo)
- **Tasa de errores** (90% → 0%)

---

## 🎯 Niveles Disponibles

| Nivel | Nombre | Campeones | Calidad Mazo | Errores | Dificultad |
|-------|--------|-----------|--------------|---------|------------|
| 1 | 🟢 Tutorial | Sylvana, Lumina, Arcanus | 10% | 90% | Muy Fácil |
| 2 | 🟢 Novato | Sylvana, Lumina, Arcanus | 20% | 80% | Fácil |
| 3 | 🟡 Aficionado | Arcanus, Tacticus, Shadowblade, Lumina | 30% | 70% | Fácil-Media |
| 4 | 🟡 Competente | Arcanus, Tacticus, Shadowblade, Lumina | 40% | 60% | Media |
| 5 | 🟠 Avanzado | Shadowblade, Tacticus, Brutus, Ragnar | 50% | 50% | Media-Difícil |
| 6 | 🟠 Experto | Shadowblade, Tacticus, Brutus, Ragnar | 60% | 40% | Difícil |
| 7 | 🔴 Maestro | **Brutus, Ragnar, Mystara** | 70% | 30% | Muy Difícil |
| 8 | 🔴 Gran Maestro | **Brutus, Ragnar, Mystara** | 80% | 20% | Extremo |
| 9 | ⚫ Leyenda | **Mystara, Brutus, Ragnar** | 90% | 10% | Brutal |
| 10 | 💀 Imposible | **Mystara (73% WR), Brutus, Ragnar** | 100% | 0% | Imposible |

---

## 🚀 Uso Rápido

### Iniciar el Juego
```bash
python main_menu.py
```

### Desde el Menú Principal:
1. Selecciona **"🎯 JUGAR VS IA"**
2. Elige tu nivel de dificultad (1-10)
3. ¡Juega!

---

## 💻 Uso Programático

### Crear una IA de Nivel Específico
```python
from ai_difficulty import SmartAI

# Crear IA de nivel 7 (Maestro)
ai = SmartAI(difficulty=7)

# Crear jugador IA completo (con campeón y mazo optimizado)
ai_player = ai.create_player(deck_size=40)

# Obtener información del nivel
info = ai.get_difficulty_info()
print(f"Nivel: {info['name']}")
print(f"Campeones: {info['champions']}")
print(f"Calidad: {info['deck_quality']}")
```

### Integrar en un Juego
```python
from ai_difficulty import SmartAI
from game_logic import Game
from models import Player
from cards import build_random_deck
from champions import get_random_champion

# Crear jugador humano
player_champion = get_random_champion()
player_deck = build_random_deck(40)
player = Player('Jugador', player_deck, player_champion)

# Crear IA con dificultad 8
ai = SmartAI(difficulty=8)
ai_player = ai.create_player(deck_size=40)

# Iniciar juego
game = Game(player, ai_player, on_game_over_callback)
game.start()
```

---

## 📊 Tier List de Campeones (Basado en 280k Simulaciones)

### S-Tier (73%+ WR)
1. **Mystara** - 73.76% WR ⭐
   - Pasiva: Genera 2 tokens 1/1 cada turno
   - Estrategia: Control con valor exponencial

2. **Brutus** - 73.27% WR
   - Pasiva: Tropas aliadas +1 ATK
   - Estrategia: Aggro con tropas baratas

3. **Ragnar** - 72.19% WR
   - Pasiva: +1 carta cada turno
   - Estrategia: Midrange con ventaja de cartas

### C-Tier
4. **Shadowblade** - 47.41% WR
5. **Tacticus** - 42.50% WR

### D-Tier
6. **Arcanus** - 38.15% WR
7. **Lumina** - 31.86% WR

### F-Tier
8. **Sylvana** - 20.87% WR ⚠️

---

## 🎮 Recomendaciones por Nivel de Jugador

### 🟢 Principiantes (Primera vez)
- **Niveles 1-2**
- Aprende mecánicas sin presión
- Win rate esperado: 85-95%

### 🟡 Jugadores Casuales
- **Niveles 3-5**
- Nivel 5 es el más equilibrado (50/50)
- Win rate esperado: 45-75%

### 🟠 Jugadores Competitivos
- **Niveles 6-8**
- Requiere construcción optimizada de mazos
- Win rate esperado: 15-45%

### 🔴 Maestros
- **Niveles 9-10**
- IA casi perfecta
- Win rate esperado: 5-20%
- Solo ganable con juego excepcional + suerte

---

## 🗂️ Archivos del Sistema

| Archivo | Descripción |
|---------|-------------|
| `ai_difficulty.py` | Sistema principal de dificultad y construcción de mazos |
| `difficulty_selector.py` | Interfaz gráfica para seleccionar dificultad |
| `main_menu.py` | Menú principal con integración completa |
| `test_ai_difficulty.py` | Suite de tests para verificar el sistema |
| `SISTEMA_DIFICULTAD.txt` | Documentación completa del sistema |
| `SIMULACION_10000_RESULTADOS.txt` | Datos de 280,000 simulaciones |

---

## 🧪 Testing

Ejecutar la suite de tests completa:
```bash
python test_ai_difficulty.py
```

Tests incluidos:
- ✅ Creación de los 10 niveles
- ✅ Diferencias de calidad entre niveles
- ✅ Restricciones de pool de campeones
- ✅ Composición de mazos por campeón
- ✅ Construcción optimizada

---

## 🔧 Características Técnicas

### Construcción de Mazos Optimizada
- **Tier lists** de tropas y hechizos basados en eficiencia (daño/coste)
- **Estrategias específicas** por campeón:
  - Mystara: 40% hechizos, late game, defensivo
  - Brutus: 20% hechizos, aggro, tropas baratas
  - Ragnar: 25% hechizos, midrange, tropas grandes
  - Y más...

### Sistema de Calidad
- **Baja calidad (10-30%)**: Cartas mayormente aleatorias
- **Media calidad (40-60%)**: Mix de cartas óptimas y subóptimas
- **Alta calidad (70-90%)**: Prioriza las mejores cartas
- **Perfecta (100%)**: Solo las cartas más eficientes

### Pool de Campeones Progresivo
- **Niveles 1-2**: Solo campeones débiles (20-30% WR)
- **Niveles 3-4**: Campeones mediocres (30-47% WR)
- **Niveles 5-6**: Buenos campeones (47-73% WR)
- **Niveles 7-10**: Solo top tier (73% WR)

---

## 📈 Datos de Simulación

El sistema está respaldado por:
- **280,000 batallas simuladas**
- **28 matchups** (todas las combinaciones de campeones)
- **10,000 partidas** por matchup
- **Consistencia validada** (<1% varianza entre ejecuciones)

Ver `SIMULACION_10000_RESULTADOS.txt` para datos completos.

---

## 🎨 Interfaz Gráfica

El selector de dificultad incluye:
- 📋 Lista completa de 10 niveles con colores
- 📊 Información detallada de cada nivel
- 🎯 Campeones disponibles por nivel
- 💡 Recomendaciones según experiencia
- 🖱️ Hover effects y UI pulida

---

## ⚙️ Opciones del Menú Principal

### 🎯 Jugar vs IA
Selecciona dificultad y juega contra la IA optimizada

### 🃏 Crear Mazo
Constructor de mazos manual con 40 cartas

### 📊 Simulaciones
Ejecuta 280,000 simulaciones (10,000 por matchup)

### 📈 Ver Estadísticas
Consulta resultados de simulaciones previas

### 🎲 Juego Rápido
Mazos y campeones completamente aleatorios

---

## 🏆 Ejemplos de Win Rates por Nivel

| Nivel | WR Jugador Promedio | WR Jugador Experto |
|-------|---------------------|---------------------|
| 1 | 95% | 99% |
| 3 | 70% | 85% |
| 5 | 50% | 65% |
| 7 | 30% | 45% |
| 9 | 15% | 25% |
| 10 | 10% | 20% |

*Nota: Win rates estimados basados en simulaciones*

---

## 📝 Notas Importantes

⚠️ **Nivel 10 es extremadamente difícil**
- La IA tiene 73% de win rate según simulaciones
- Mazos 100% optimizados
- No comete errores
- Requiere juego perfecto + suerte para ganar

💡 **Nivel 5 es el punto equilibrado**
- 50% calidad en todo
- Partidas justas y competitivas
- Ideal para medir habilidad real

🎮 **Progresión recomendada**
- Empieza en Nivel 1
- Sube cuando ganes 3 partidas seguidas
- Nivel 5 = jugador promedio
- Nivel 7+ = jugador competitivo

---

## 🔮 Futuras Mejoras

- [ ] Sistema de ranking persistente
- [ ] Estadísticas de victorias/derrotas por nivel
- [ ] Logros y desbloqueos
- [ ] Modo torneo vs múltiples IAs
- [ ] Replay de partidas
- [ ] Análisis post-partida

---

## 📜 Licencia

Este sistema es parte del proyecto Mini TCG.

---

## 👥 Créditos

Sistema de dificultad diseñado con datos de:
- 280,000 simulaciones de batalla
- Análisis estadístico de 8 campeones
- Optimización de construcción de mazos
- Testing extensivo de balance

---

## 📞 Soporte

Para reportar bugs o sugerir mejoras:
1. Ejecuta `test_ai_difficulty.py` para verificar
2. Consulta `SISTEMA_DIFICULTAD.txt` para documentación completa
3. Revisa `SIMULACION_10000_RESULTADOS.txt` para datos

---

**¡Disfruta el desafío!** 🎮
