# Sistema de Hechizos - Guía Completa

## Resumen
Se ha implementado un sistema completo de hechizos instantáneos que permite a los jugadores y a la IA lanzar hechizos con diversos efectos.

## Cartas de Hechizos Disponibles

### Hechizos de Daño
1. **Rayo** (Coste: 2)
   - Daño: 3
   - Objetivo: Tropa enemiga
   - Descripción: "Daño directo a tropa"

2. **Bola de Fuego** (Coste: 3)
   - Daño: 4
   - Objetivo: Tropa enemiga
   - Descripción: "Gran daño a tropa"

3. **Descarga Eléctrica** (Coste: 1)
   - Daño: 2
   - Objetivo: Tropa enemiga
   - Descripción: "Daño rápido"

4. **Ráfaga de Flechas** (Coste: 3)
   - Daño: 1 a todas las tropas enemigas
   - Objetivo: Todas las tropas enemigas
   - Descripción: "1 daño a todas tropas enemigas"

5. **Tormenta de Fuego** (Coste: 5)
   - Daño: 2 a todas las tropas enemigas
   - Objetivo: Todas las tropas enemigas
   - Descripción: "2 daño a todas tropas enemigas"

### Hechizos de Curación
6. **Curación** (Coste: 1)
   - Curación: 3 HP
   - Objetivo: Jugador
   - Descripción: "Restaura 3 vida"

7. **Curación Mayor** (Coste: 3)
   - Curación: 7 HP
   - Objetivo: Jugador
   - Descripción: "Restaura 7 vida"

### Hechizos de Destrucción
8. **Destierro** (Coste: 4)
   - Efecto: Destruye cualquier tropa enemiga
   - Objetivo: Tropa enemiga
   - Descripción: "Destruye tropa enemiga"

9. **Aniquilar** (Coste: 2)
   - Efecto: Destruye tropa enemiga dañada
   - Objetivo: Tropa enemiga con HP < HP máximo
   - Descripción: "Destruye tropa dañada"

### Hechizos de Utilidad
10. **Dibujar Cartas** (Coste: 2)
    - Efecto: Roba 2 cartas
    - Objetivo: Automático
    - Descripción: "Roba 2 cartas"

## Características del Sistema

### Para el Jugador
1. **Identificación Visual**
   - Los hechizos se muestran en la mano con fondo morado y símbolo ⚡
   - Tienen imágenes distintivas con efectos visuales mágicos
   - Muestran su descripción completa

2. **Selección de Objetivo**
   - Al jugar un hechizo, aparece un diálogo para elegir el objetivo
   - Los botones cambian de color según el tipo:
     - Rojo: Objetivos enemigos
     - Verde: Objetivos aliados
   - Los hechizos sin objetivo (AoE, auto) se lanzan automáticamente

3. **Efectos Inmediatos**
   - Los hechizos se ejecutan instantáneamente
   - Van directamente al cementerio (no se quedan en el campo)
   - Los efectos se muestran en el log de acciones

### Para la IA
La IA tiene una estrategia inteligente para usar hechizos:

1. **Prioridad Letal**
   - Usa hechizos de daño directo si puede matar al jugador

2. **Eliminación de Amenazas**
   - Usa Destierro/Aniquilar en tropas enemigas caras
   - Prioriza destruir cartas de alto coste

3. **Daño Táctico**
   - Usa hechizos de daño para matar tropas enemigas
   - Prioriza objetivos que pueda eliminar
   - Usa AoE cuando hay 3+ enemigos o puede matar múltiples

4. **Supervivencia**
   - Usa curación cuando su vida está baja (<15 HP)

5. **Recursos**
   - Usa "Dibujar Cartas" cuando tiene pocas cartas en mano (≤3)

## Construcción de Mazos
- Los mazos ahora contienen 30% de hechizos por defecto (configurable)
- La mano inicial es de 5 cartas (aumentada de 3)
- Esto asegura que los jugadores tengan al menos 1-2 hechizos al empezar

## Archivos Modificados

### models.py
- Agregado campo `description` para texto descriptivo
- Los campos `spell_target` y `spell_effect` ya existían

### cards.py
- Definidos 10 hechizos en `SPELL_TEMPLATES`
- Función `create_card()` acepta parámetros de hechizo
- `build_random_deck()` acepta `spell_ratio` (default 0.3)

### game_logic.py
- Método `execute_spell()`: Ejecuta efectos de hechizos
- Método `destroy_card()`: Elimina cartas del campo
- `play_card()`: Maneja tanto tropas como hechizos
- Turnos de IA actualizados para lanzar hechizos

### game_gui.py
- Visualización de hechizos en mano con estilo morado
- Función `ask_spell_target()`: Diálogo de selección de objetivo
- `on_play()` actualizado para manejar hechizos

### ai_player.py
- Método `choose_spell_to_cast()`: IA decide qué hechizo usar
- Estrategia de 5 niveles para uso inteligente de hechizos

### generate_spell_assets.py
- Script para generar imágenes de hechizos
- Crea 200x300px PNG con efectos visuales mágicos
- Colores codificados según tipo de efecto

## Cómo Jugar con Hechizos

1. **Jugar un Hechizo**
   - Haz clic en un hechizo en tu mano
   - Si requiere objetivo, selecciona uno en el diálogo
   - El efecto se aplica inmediatamente
   - El hechizo va al cementerio

2. **Estrategias**
   - Usa hechizos de daño para eliminar amenazas
   - Guarda curación para momentos críticos
   - Los hechizos de destrucción ignoran HP
   - "Dibujar Cartas" ayuda a recuperar recursos

3. **Timing**
   - Los hechizos se pueden jugar en tu turno
   - Usa antes de atacar para limpiar defensores
   - Usa después de jugar tropas si sobra maná

## Próximas Mejoras Posibles
- Hechizos de contrahechizo
- Hechizos permanentes (encantamientos)
- Efectos que duran varios turnos
- Hechizos con múltiples objetivos
- Sistema de "stack" para hechizos en respuesta
