# Sistema de Mazos Guardados

## Descripción
El juego ahora incluye un sistema completo para crear, guardar y utilizar mazos personalizados.

## Características

### 1. Constructor de Mazos (Deck Builder)
- Accesible desde el menú principal
- Permite crear mazos personalizados carta por carta
- Seleccionar un campeón para el mazo
- **NUEVO**: Al finalizar, guarda el mazo con un nombre personalizado
- **NUEVO**: Regresa al menú principal después de guardar

### 2. Jugar vs IA
- **NUEVO**: Antes de elegir la dificultad, puedes elegir:
  - 🎲 **Mazo Aleatorio**: Genera un mazo aleatorio de 40 cartas
  - 📚 **Mazo Guardado**: Selecciona uno de tus mazos creados
- Luego seleccionas la dificultad de la IA (1-10)
- Juegas con el mazo elegido

### 3. Multijugador - Custom Match
- **NUEVO**: Al elegir Custom Match, puedes:
  - 🎲 **Mazo Aleatorio**: Usar un mazo generado automáticamente
  - 📚 **Mazo Guardado**: Seleccionar uno de tus mazos creados
- **Ya NO** te envía al Constructor de Mazos
- Búsqueda de partida con el mazo seleccionado

## Archivos del Sistema

### Nuevos Archivos
- `src/deck_manager.py`: Gestiona guardar/cargar/listar mazos
- `src/deck_selector.py`: UI para seleccionar entre mazo aleatorio o guardado
- `data/saved_decks/`: Directorio donde se guardan los mazos (formato JSON)

### Archivos Modificados
- `src/deck_builder.py`:
  - Botón cambiado de "▶️ JUGAR" a "💾 GUARDAR MAZO"
  - Solicita nombre del mazo al guardar
  - Regresa al menú principal después de guardar
  
- `main_menu.py`:
  - `start_vs_ai()`: Usa `deck_selector` antes de elegir dificultad
  - `_start_custom_match()`: Usa `deck_selector` en vez de deck builder

## Formato de Mazos Guardados

Los mazos se guardan en `data/saved_decks/` como archivos JSON:

```json
{
  "name": "Mi Mazo",
  "champion": "Mystara",
  "cards": [
    {
      "name": "Goblin",
      "cost": 1,
      "damage": 2,
      "health": 3,
      "type": "troop",
      "ability": null,
      ...
    },
    ...
  ]
}
```

## Flujo de Usuario

### Crear un Mazo
1. Menú Principal → 🃏 **CREAR MAZO**
2. Seleccionar cartas y campeón
3. Clic en **💾 GUARDAR MAZO**
4. Ingresar nombre del mazo
5. Confirmación y regreso al menú

### Jugar vs IA con Mazo Guardado
1. Menú Principal → 🎯 **JUGAR VS IA**
2. Seleccionar **📚 MAZOS GUARDADOS**
3. Elegir un mazo de la lista
4. Seleccionar dificultad de IA (1-10)
5. ¡Jugar!

### Multijugador con Mazo Guardado
1. Menú Principal → 🌐 **MULTIJUGADOR**
2. Seleccionar **🎨 CUSTOM MATCH**
3. Seleccionar **📚 MAZOS GUARDADOS**
4. Elegir un mazo de la lista
5. Esperar emparejamiento
6. ¡Jugar!

## Validaciones

Los mazos deben cumplir:
- Mínimo 30 cartas, máximo 60
- Mínimo 15 tropas
- Mínimo 5 hechizos
- 1 campeón seleccionado

## Notas Técnicas

- Los mazos se guardan con nombres sanitizados (solo alfanuméricos, espacios, guiones)
- Al cargar, las cartas se reconstruyen usando `create_card()` para mantener consistencia
- El selector de deck es reutilizable en diferentes modos de juego
