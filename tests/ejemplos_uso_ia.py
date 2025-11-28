"""
Ejemplos de uso del Sistema de Dificultad de IA.
Muestra cómo integrar el sistema en diferentes contextos.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# ============================================================================
# EJEMPLO 1: Uso Básico - Crear y usar una IA
# ============================================================================

from src.ai_engine import get_difficulty_info, create_ai_opponent
from src.models import Player

# Obtener información de nivel 5 (Avanzado)
info = get_difficulty_info(5)
print(f"Nombre: {info['name']}")
print(f"Campeones: {', '.join(info['champions'])}")
print(f"Calidad de mazo: {info['deck_quality']}")
print(f"Calidad de juego: {info['play_quality']}")

# Crear oponente IA completo
champion, deck, config = create_ai_opponent(difficulty_level=5)
ai_player = Player('IA', deck, champion=champion, ai_config=config)
print(f"\nIA creada: {ai_player.name}")
if ai_player.champion:
    print(f"Campeón: {ai_player.champion.name}")
print(f"Cartas en el mazo: {len(ai_player.deck.cards)}")


# ============================================================================
# EJEMPLO 2: Integración con el Juego
# ============================================================================

from src.ai_engine import create_ai_opponent
from src.game_logic import Game
from src.models import Player
from src.cards import build_random_deck
from src.champions import get_random_champion

def crear_partida_vs_ia(nivel_dificultad):
    """Crea una partida contra la IA del nivel especificado."""
    
    # Crear jugador humano
    player_champion = get_random_champion()
    player_deck = build_random_deck(40)
    player = Player('Jugador', player_deck, player_champion)
    
    # Crear IA
    ai_champion, ai_deck, ai_config = create_ai_opponent(difficulty_level=nivel_dificultad)
    ai_player = Player('IA', ai_deck, champion=ai_champion, ai_config=ai_config)
    
    print(f"Partida iniciada:")
    if player.champion:
        print(f"  Jugador: {player.champion.name}")
    if ai_player.champion:
        print(f"  IA: {ai_player.name} ({ai_player.champion.name})")
    
    # Crear y empezar el juego
    def on_game_over():
        print("¡Partida terminada!")
    
    game = Game(player, ai_player, on_game_over)
    return game

# Uso
game = crear_partida_vs_ia(nivel_dificultad=7)
# game.start()  # Iniciar el juego


# ============================================================================
# EJEMPLO 3: Comparar Diferentes Niveles
# ============================================================================

def comparar_niveles():
    """Compara la configuración de diferentes niveles."""
    
    niveles = [1, 5, 10]
    
    print("=" * 80)
    print("COMPARACIÓN DE NIVELES")
    print("=" * 80)
    
    for nivel in niveles:
        info = get_difficulty_info(nivel)
        
        print(f"\nNivel {nivel}: {info['name']}")
        print(f"  Campeones: {', '.join(info['champions'])}")
        print(f"  Calidad de mazo: {info['deck_quality']}")
        print(f"  Calidad de juego: {info['play_quality']}")
        print(f"  Tasa de errores: {info['mistake_rate']}")

# Ejecutar comparación
# comparar_niveles()


# ============================================================================
# EJEMPLO 4: Torneo Progresivo
# ============================================================================

def torneo_progresivo(jugador):
    """
    Enfrenta al jugador contra IAs de dificultad creciente.
    Debe ganar 2 de 3 partidas para avanzar.
    """
    
    nivel_actual = 1
    
    while nivel_actual <= 10:
        print(f"\n{'=' * 60}")
        print(f"NIVEL {nivel_actual} - DESAFÍO")
        print(f"{'=' * 60}")
        
        victorias = 0
        derrotas = 0
        
        while victorias < 2 and derrotas < 2:
            # Crear IA del nivel actual
            ai_champion, ai_deck, ai_config = create_ai_opponent(difficulty_level=nivel_actual)
            ai_player = Player('IA', ai_deck, champion=ai_champion, ai_config=ai_config)
            
            # Crear juego
            game = Game(jugador, ai_player, lambda: None)
            
            # Simular partida (en realidad se jugaría)
            # resultado = game.start()
            # if resultado == "player_wins":
            #     victorias += 1
            # else:
            #     derrotas += 1
            
            print(f"Partida {victorias + derrotas + 1}: ", end="")
            # Simulamos resultado para el ejemplo
            import random
            if random.random() > 0.3 + (nivel_actual * 0.05):
                victorias += 1
                print("VICTORIA ✅")
            else:
                derrotas += 1
                print("DERROTA ❌")
        
        if victorias >= 2:
            print(f"\n🎉 ¡Nivel {nivel_actual} SUPERADO!")
            nivel_actual += 1
        else:
            print(f"\n💀 Derrotado en nivel {nivel_actual}")
            break
    
    if nivel_actual > 10:
        print("\n" + "=" * 60)
        print("🏆 ¡CAMPEÓN! Has superado todos los niveles")
        print("=" * 60)


# ============================================================================
# EJEMPLO 5: Análisis de Construcción de Mazos
# ============================================================================

def analizar_construccion_mazo(nivel):
    """Analiza cómo construye mazos la IA para un nivel específico."""
    
    info = get_difficulty_info(nivel)
    
    print(f"\n{'=' * 70}")
    print(f"ANÁLISIS DE CONSTRUCCIÓN DE MAZO")
    print(f"Nivel: {nivel} ({info['name']})")
    print(f"{'=' * 70}")
    
    # Construir 3 mazos de ejemplo
    for i in range(3):
        champion, deck, config = create_ai_opponent(difficulty_level=nivel)
        
        # Analizar composición
        tropas = [c for c in deck.cards if c.card_type == 'troop']
        hechizos = [c for c in deck.cards if c.card_type == 'spell']
        
        coste_promedio = sum(c.cost for c in deck.cards) / len(deck.cards)
        
        print(f"\nMazo {i+1} - Campeón: {champion.name}")
        print(f"  Tropas: {len(tropas)} | Hechizos: {len(hechizos)}")
        print(f"  Coste promedio: {coste_promedio:.2f}")
        
        # Top 3 cartas más usadas
        from collections import Counter
        carta_counts = Counter(c.name for c in deck.cards)
        top3 = carta_counts.most_common(3)
        
        print(f"  Top 3 cartas:")
        for carta, count in top3:
            print(f"    - {carta}: x{count}")

# Uso
# analizar_construccion_mazo("Mystara", 10)
# analizar_construccion_mazo("Brutus", 10)


# ============================================================================
# EJEMPLO 6: Sistema de Ranking
# ============================================================================

class SistemaRanking:
    """Sistema de ranking basado en victorias contra diferentes niveles."""
    
    def __init__(self):
        self.puntos = 0
        self.victorias_por_nivel = {i: 0 for i in range(1, 11)}
        self.derrotas_por_nivel = {i: 0 for i in range(1, 11)}
    
    def registrar_victoria(self, nivel):
        """Registra una victoria y suma puntos según el nivel."""
        self.victorias_por_nivel[nivel] += 1
        
        # Puntos según nivel (nivel 1 = 10 pts, nivel 10 = 100 pts)
        puntos_ganados = nivel * 10
        self.puntos += puntos_ganados
        
        print(f"✅ Victoria vs Nivel {nivel}! +{puntos_ganados} puntos")
        print(f"   Puntos totales: {self.puntos}")
    
    def registrar_derrota(self, nivel):
        """Registra una derrota."""
        self.derrotas_por_nivel[nivel] += 1
        print(f"❌ Derrota vs Nivel {nivel}")
    
    def obtener_rango(self):
        """Obtiene el rango del jugador según sus puntos."""
        if self.puntos < 100:
            return "🟤 Bronce"
        elif self.puntos < 300:
            return "⚪ Plata"
        elif self.puntos < 600:
            return "🟡 Oro"
        elif self.puntos < 1000:
            return "💎 Platino"
        elif self.puntos < 1500:
            return "💠 Diamante"
        else:
            return "👑 Maestro"
    
    def mostrar_estadisticas(self):
        """Muestra las estadísticas del jugador."""
        print("\n" + "=" * 60)
        print("📊 ESTADÍSTICAS DEL JUGADOR")
        print("=" * 60)
        print(f"Rango: {self.obtener_rango()}")
        print(f"Puntos totales: {self.puntos}")
        print(f"\nRecord por nivel:")
        
        for nivel in range(1, 11):
            v = self.victorias_por_nivel[nivel]
            d = self.derrotas_por_nivel[nivel]
            total = v + d
            
            if total > 0:
                wr = (v / total) * 100
                print(f"  Nivel {nivel:2d}: {v}V - {d}D ({wr:.1f}% WR)")

# Uso
# ranking = SistemaRanking()
# ranking.registrar_victoria(5)
# ranking.registrar_victoria(7)
# ranking.registrar_derrota(8)
# ranking.mostrar_estadisticas()


# ============================================================================
# EJEMPLO 7: Entrenamiento Adaptativo
# ============================================================================

def entrenamiento_adaptativo(jugador):
    """
    Sistema que ajusta automáticamente la dificultad según el rendimiento.
    """
    
    nivel_actual = 5  # Empezar en nivel medio
    victorias_consecutivas = 0
    derrotas_consecutivas = 0
    
    print("🎮 MODO ENTRENAMIENTO ADAPTATIVO")
    print("La dificultad se ajustará según tu rendimiento\n")
    
    for partida in range(20):  # 20 partidas de entrenamiento
        # Crear IA del nivel actual
        ai = SmartAI(difficulty=nivel_actual)
        ai_player = ai.create_player(deck_size=40)
        
        print(f"\nPartida {partida + 1} - Nivel {nivel_actual}")
        
        # Crear juego
        game = Game(jugador, ai_player, lambda: None)
        
        # Simular resultado (en realidad se jugaría)
        import random
        victoria = random.random() > (0.3 + nivel_actual * 0.05)
        
        if victoria:
            victorias_consecutivas += 1
            derrotas_consecutivas = 0
            print("  ✅ VICTORIA")
            
            # Subir nivel después de 2 victorias consecutivas
            if victorias_consecutivas >= 2 and nivel_actual < 10:
                nivel_actual += 1
                victorias_consecutivas = 0
                print(f"  📈 ¡Subiste a nivel {nivel_actual}!")
        else:
            derrotas_consecutivas += 1
            victorias_consecutivas = 0
            print("  ❌ DERROTA")
            
            # Bajar nivel después de 3 derrotas consecutivas
            if derrotas_consecutivas >= 3 and nivel_actual > 1:
                nivel_actual -= 1
                derrotas_consecutivas = 0
                print(f"  📉 Bajaste a nivel {nivel_actual}")
    
    print(f"\n🎯 Entrenamiento completo! Nivel final: {nivel_actual}")


# ============================================================================
# EJEMPLO 8: Uso con GUI
# ============================================================================

def ejemplo_con_gui():
    """Ejemplo de cómo usar el selector de dificultad con GUI."""
    
    import tkinter as tk
    from src.difficulty_selector import show_difficulty_selector
    from src.ai_engine import SmartAI
    
    root = tk.Tk()
    root.withdraw()  # Ocultar ventana principal
    
    def on_difficulty_selected(level):
        print(f"\n✅ Dificultad seleccionada: Nivel {level}")
        
        # Crear IA
        ai = SmartAI(difficulty=level)
        info = ai.get_difficulty_info()
        
        print(f"Nombre: {info['name']}")
        print(f"Campeones: {', '.join(info['champions'])}")
        
        # Crear jugador IA
        ai_player = ai.create_player()
        print(f"\nIA lista para jugar:")
        print(f"  Nombre: {ai_player.name}")
        if ai_player.champion:
            print(f"  Campeón: {ai_player.champion.name}")
        print(f"  Cartas: {len(ai_player.deck.cards)}")
    
    # Mostrar selector
    level = show_difficulty_selector(on_difficulty_selected)
    
    if level:
        print("\n🎮 ¡Listo para jugar!")
    else:
        print("\n❌ Selección cancelada")

# Uso
# ejemplo_con_gui()


# ============================================================================
# EJEMPLO 9: Testing y Validación
# ============================================================================

def validar_sistema():
    """Valida que el sistema funciona correctamente."""
    
    print("\n🧪 VALIDANDO SISTEMA DE DIFICULTAD\n")
    
    errores = []
    
    # Test 1: Todos los niveles se pueden crear
    print("Test 1: Creación de niveles...", end=" ")
    try:
        for i in range(1, 11):
            ai = SmartAI(difficulty=i)
            assert ai.difficulty.level == i
        print("✅")
    except Exception as e:
        print(f"❌ {e}")
        errores.append("Creación de niveles falló")
    
    # Test 2: Pools de campeones son distintos
    print("Test 2: Pools de campeones...", end=" ")
    try:
        ai1 = SmartAI(difficulty=1)
        ai10 = SmartAI(difficulty=10)
        
        pool1 = set(ai1.difficulty.champion_pool)
        pool10 = set(ai10.difficulty.champion_pool)
        
        assert pool1 != pool10, "Los pools deberían ser diferentes"
        assert "Mystara" in pool10, "Mystara debería estar en nivel 10"
        assert "Sylvana" not in pool10, "Sylvana no debería estar en nivel 10"
        print("✅")
    except Exception as e:
        print(f"❌ {e}")
        errores.append("Pools de campeones incorrectos")
    
    # Test 3: Calidad de mazo aumenta con nivel
    print("Test 3: Calidad de mazo progresiva...", end=" ")
    try:
        calidades = [SmartAI(difficulty=i).difficulty.deck_quality for i in range(1, 11)]
        assert calidades == sorted(calidades), "Calidad debería aumentar"
        assert calidades[0] == 0.1, "Nivel 1 debería ser 10%"
        assert calidades[9] == 1.0, "Nivel 10 debería ser 100%"
        print("✅")
    except Exception as e:
        print(f"❌ {e}")
        errores.append("Calidad de mazo no progresa correctamente")
    
    # Test 4: Se pueden crear jugadores
    print("Test 4: Creación de jugadores...", end=" ")
    try:
        ai = SmartAI(difficulty=5)
        player = ai.create_player(deck_size=40)
        
        assert player is not None
        assert player.champion is not None
        assert len(player.deck.cards) == 40
        print("✅")
    except Exception as e:
        print(f"❌ {e}")
        errores.append("Creación de jugadores falló")
    
    # Resultado final
    print("\n" + "=" * 60)
    if errores:
        print("❌ VALIDACIÓN FALLIDA")
        for error in errores:
            print(f"  - {error}")
    else:
        print("✅ TODOS LOS TESTS PASARON")
        print("   Sistema de dificultad funcionando correctamente")
    print("=" * 60)

# Uso
# validar_sistema()


# ============================================================================
# EJECUTAR EJEMPLOS
# ============================================================================

if __name__ == '__main__':
    print("\n" + "=" * 80)
    print(" " * 20 + "EJEMPLOS DE USO DEL SISTEMA DE DIFICULTAD")
    print("=" * 80)
    
    # Descomentar para ejecutar cada ejemplo:
    
    # print("\n--- EJEMPLO 1: Uso Básico ---")
    # # (El código ya está arriba)
    
    # print("\n--- EJEMPLO 3: Comparar Niveles ---")
    # comparar_niveles()
    
    # print("\n--- EJEMPLO 5: Análisis de Construcción de Mazos ---")
    # analizar_construccion_mazo("Mystara", 10)
    
    # print("\n--- EJEMPLO 6: Sistema de Ranking ---")
    # ranking = SistemaRanking()
    # ranking.registrar_victoria(7)
    # ranking.mostrar_estadisticas()
    
    print("\n--- EJEMPLO 9: Validación del Sistema ---")
    validar_sistema()
    
    print("\n\n💡 Tip: Descomenta los ejemplos que quieras ejecutar")
