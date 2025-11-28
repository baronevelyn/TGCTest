# ⚔️ Mini TCG Prototype

Un juego de cartas coleccionables (TCG) con sistema de campeones y constructor de mazos personalizado.

## 🎮 Características

### Sistema de Campeones
8 campeones únicos con habilidades pasivas:

- **Arcanus** (Mago de Batalla): Los hechizos cuestan 1 maná menos
- **Brutus** (Señor de la Guerra): Todas tus tropas tienen +1 ATK
- **Mystara** (Invocadora): Invoca un Token 1/1 al inicio del turno
- **Shadowblade** (Asesino): Tropas baratas (≤3 maná) tienen +1 ATK y Prisa
- **Lumina** (Clérigo): Cura 1 HP a todas tus tropas al inicio del turno
- **Tacticus** (Estratega): Robas 2 cartas por turno en lugar de 1
- **Ragnar** (Berserker): No puedes bloquear, todas tus tropas tienen Furia
- **Sylvana** (Druida): Tropas grandes (≥4 HP) ganan +1/+1

### Constructor de Mazos
- **Restricciones del Mazo:**
  - Total: 30-60 cartas
  - Mínimo 15 tropas
  - Mínimo 5 hechizos
- Selección de campeón obligatoria
- Generación aleatoria de mazos
- Sistema de guardado/carga

### Sistema de Juego
- **Tropas:** 15 tipos con habilidades (Furia, Volar, Taunt, Invocar Aliado)
- **Hechizos:** 10 tipos con efectos variados (daño, curación, buffs, AoE)
- **Mecánicas:**
  - Sistema de maná creciente
  - Combate entre tropas
  - Bloqueo estratégico
  - IA con toma de decisiones

## 🚀 Cómo Jugar

### Inicio Rápido
```powershell
python main_menu.py
```

Elige una opción:
1. **🎨 Constructor de Mazos** - Crea tu mazo personalizado
2. **🎲 Juego Rápido** - Mazos y campeones aleatorios

### Controles del Juego
- **Jugar Carta:** Click en carta de la mano
- **Atacar:** Click en tropa atacante, luego objetivo
- **Hechizos:** Selecciona objetivo después de jugar
- **Bloquear:** Elige bloqueo cuando el enemigo ataque
- **Fin de Turno:** Click en "End Turn"

## 📁 Estructura del Proyecto

```
TGCTest/
│
├── main_menu.py          # Menú principal
├── deck_builder.py       # Constructor de mazos
├── game_gui.py           # Interfaz gráfica del juego
├── game_logic.py         # Motor del juego
├── champions.py          # Definiciones de campeones
├── cards.py              # Definiciones de cartas
├── models.py             # Modelos de datos
├── ai_player.py          # Inteligencia artificial
│
├── assets/               # Recursos gráficos
│   └── cards/           # Imágenes de hechizos
│
└── CAMPEONES.txt        # Documentación de campeones
```

## 🎯 Estrategias por Campeón

### Arcanus (Control)
- Aprovecha los hechizos baratos
- Domina el tablero con magia
- Combos de múltiples hechizos

### Brutus (Aggro)
- Inunda con tropas
- Presión constante
- +1 ATK hace todos los trades favorables

### Mystara (Token)
- Acumula tokens
- Hechizos de área enemigos
- Late game poderoso

### Shadowblade (Tempo)
- Tropas baratas con Prisa
- Golpes rápidos y letales
- Remata con hechizos

### Lumina (Midrange)
- Tropas difíciles de eliminar
- Curación constante
- Desgaste al oponente

### Tacticus (Combo)
- Busca piezas clave
- Combos complejos
- Control de recursos

### Ragnar (Hyper Aggro)
- Todo tiene Furia
- No bloquear es ventaja
- Matar antes de morir

### Sylvana (Big)
- Tropas grandes inmortales
- Buffs acumulativos
- Imbloqueables

## 📝 Reglas del Mazo

1. **Tamaño:** 30-60 cartas
2. **Composición:**
   - Mínimo 15 tropas
   - Mínimo 5 hechizos
3. **Campeón:** 1 obligatorio

## 🐛 Solución de Problemas

### El juego no arranca
```powershell
# Verifica la instalación de Python
python --version

# Instala dependencias
pip install pillow
```

### Errores de importación
```powershell
# Asegúrate de estar en el directorio correcto
cd C:\Users\Victor\Desktop\TGCTest
```

### No aparecen imágenes
- Las imágenes de hechizos están en `assets/cards/`
- Se generan automáticamente si faltan

## 📊 Información Técnica

- **Python:** 3.13+
- **GUI:** tkinter
- **Imágenes:** PIL/Pillow
- **Arquitectura:** MVC modular

## 🔄 Historial de Versiones

### v2.0 - Sistema de Campeones
- 8 campeones con pasivas únicas
- Constructor de mazos personalizado
- Menú principal
- Tooltips de campeones
- Documentación completa

### v1.0 - Sistema Base
- 15 tropas con habilidades
- 10 hechizos instantáneos
- IA básica
- Sistema de combate

## 📚 Documentación Adicional

Ver `CAMPEONES.txt` para estrategias detalladas de cada campeón.

---

**Desarrollado con ❤️ para aprender desarrollo de juegos en Python**
