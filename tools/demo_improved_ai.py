"""
Demo del Sistema de IA Mejorado v2.0
Muestra los 10 niveles de dificultad y sus características
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.ai_engine import AIConfig, get_difficulty_info, DataDrivenDeckBuilder
from src.champions import get_champion_by_name


def print_difficulty_showcase():
    """Muestra todos los niveles de dificultad."""
    print("\n" + "="*120)
    print("🎮 SISTEMA DE IA MEJORADO v2.0 - BASADO EN 280,000 PARTIDAS REALES")
    print("="*120)
    
    print("\n📊 DATOS CLAVE DEL ANÁLISIS:")
    print("   • Mejores Campeones: Mystara (73.79%), Brutus (73.34%), Ragnar (71.86%)")
    print("   • Mejores Cartas: Berserker (51.64%), Wolf (51.01%), Knight (50.77%)")
    print("   • Mejor Habilidad: Furia (51.32% WR)")
    print("   • Ratio Óptimo Mazo: 28 Tropas / 12 Hechizos (2.33:1)")
    print("   • Duración Promedio: 6 turnos")
    
    print("\n" + "="*120)
    print("🎯 NIVELES DE DIFICULTAD")
    print("="*120 + "\n")
    
    for level in range(1, 11):
        config = AIConfig(level)
        
        print(f"\n{'─'*120}")
        print(f"NIVEL {level}: {config.name}")
        print(f"{'─'*120}")
        print(f"\n🏆 Campeones: {', '.join(config.champion_pool)}")
        print(f"📊 Optimización de Deck: {config.deck_optimization*100:.0f}%")
        print(f"🎯 Calidad de Juego: {config.play_quality*100:.0f}%")
        print(f"❌ Probabilidad de Error: {config.mistake_chance*100:.0f}%")
        if config.uses_ability_priority:
            print(f"⚡ Prioriza habilidad Furia (51.5% WR)")
        if config.uses_matchup_knowledge:
            print(f"🧠 Usa conocimiento de matchups")
        
        # Ejemplo de campeón
        if level in [1, 3, 5, 7, 9, 10]:
            import random
            from src.champions import get_champion_by_name
            champion_name = random.choice(config.champion_pool)
            champion = get_champion_by_name(champion_name)
            
            print(f"\n💡 Ejemplo - Campeón: {champion.name}")
            print(f"   Pasiva: {champion.passive_description}")


def print_matchup_analysis():
    """Muestra análisis de matchups basado en datos."""
    print("\n\n" + "="*120)
    print("⚔️  ANÁLISIS DE MATCHUPS (Basado en 280,000 partidas)")
    print("="*120 + "\n")
    
    print("🔥 TOP 5 MEJORES MATCHUPS:")
    best_matchups = [
        ("Ragnar", "Sylvana", 95.22),
        ("Mystara", "Lumina", 93.02),
        ("Mystara", "Sylvana", 92.03),
        ("Mystara", "Shadowblade", 87.30),
        ("Brutus", "Lumina", 87.07),
    ]
    
    for i, (champ1, champ2, wr) in enumerate(best_matchups, 1):
        print(f"   {i}. {champ1:<12} vs {champ2:<12} - {wr:>6.2f}%")
    
    print("\n❄️  TOP 5 PEORES MATCHUPS:")
    worst_matchups = [
        ("Lumina", "Arcanus", 44.65),
        ("Sylvana", "Arcanus", 44.52),
        ("Brutus", "Ragnar", 44.32),
        ("Arcanus", "Tacticus", 38.98),
        ("Tacticus", "Shadowblade", 34.92),
    ]
    
    for i, (champ1, champ2, wr) in enumerate(worst_matchups, 1):
        print(f"   {i}. {champ1:<12} vs {champ2:<12} - {wr:>6.2f}%")


def print_recommendations():
    """Imprime recomendaciones de uso."""
    print("\n\n" + "="*120)
    print("💡 RECOMENDACIONES DE USO")
    print("="*120 + "\n")
    
    recommendations = {
        "Principiantes": {
            "levels": "1-2",
            "description": "Aprende las mecánicas sin presión. La IA usa campeones débiles y mazos aleatorios.",
            "tips": ["Experimenta con diferentes cartas", "Aprende el sistema de combate", "Prueba todas las habilidades"]
        },
        "Jugadores Casuales": {
            "levels": "3-5",
            "description": "Desafío moderado que requiere estrategia básica.",
            "tips": ["Construye mazos coherentes", "Aprende timing de hechizos", "Practica bloqueos eficientes"]
        },
        "Jugadores Competitivos": {
            "levels": "6-8",
            "description": "La IA usa campeones top-tier y mazos optimizados. Requiere buen juego.",
            "tips": ["Domina las curvas de maná", "Conoce los matchups", "Optimiza tu mazo al máximo"]
        },
        "Maestros": {
            "levels": "9-10",
            "description": "IA casi perfecta con 73%+ win rate. Extremadamente difícil.",
            "tips": ["Juego perfecto requerido", "Aprovecha cada error", "Conoce el meta profundamente"]
        }
    }
    
    for category, info in recommendations.items():
        print(f"\n🎯 {category} (Niveles {info['levels']}):")
        print(f"   {info['description']}")
        print("   Tips:")
        for tip in info['tips']:
            print(f"      • {tip}")


def print_deck_building_tips():
    """Consejos para construcción de mazos."""
    print("\n\n" + "="*120)
    print("📦 GUÍA DE CONSTRUCCIÓN DE MAZOS (Basada en Datos)")
    print("="*120 + "\n")
    
    print("✅ COMPOSICIÓN ÓPTIMA:")
    print("   • 28 Tropas / 12 Hechizos (ratio 2.33:1)")
    print("   • Curva de maná: mayoría 2-4 de coste")
    print("   • Incluir sinergias con tu campeón\n")
    
    print("⭐ MEJORES TROPAS (>50% Win Rate):")
    best_troops = [
        ("Berserker", "3 maná", "Furia", "51.64%"),
        ("Wolf", "2 maná", "Furia", "51.01%"),
        ("Knight", "3 maná", "-", "50.77%"),
        ("Archer", "2 maná", "-", "50.55%"),
        ("Mage", "4 maná", "-", "50.42%"),
        ("Goblin", "1 maná", "-", "50.39%"),
    ]
    
    for name, cost, ability, wr in best_troops:
        abil_str = f"[{ability}]" if ability != "-" else ""
        print(f"   • {name:<12} {cost:<7} {abil_str:<12} WR: {wr}")
    
    print("\n⚡ MEJORES HECHIZOS:")
    best_spells = [
        ("Aniquilar", "2 maná", "Destruir dañado", "50.55%"),
        ("Descarga Eléctrica", "1 maná", "2 daño", "50.17%"),
        ("Destierro", "4 maná", "Destruir cualquiera", "50.12%"),
        ("Rayo", "2 maná", "3 daño", "50.12%"),
    ]
    
    for name, cost, effect, wr in best_spells:
        print(f"   • {name:<20} {cost:<7} {effect:<20} WR: {wr}")
    
    print("\n🎭 ESTRATEGIAS POR ESTILO:")
    styles = {
        "Aggro (Brutus)": ["Muchas tropas baratas (1-3 coste)", "Berserker, Wolf, Goblin", "Hechizos de daño directo"],
        "Control (Mystara)": ["Tropas defensivas (Taunt)", "Hechizos de remoción", "Curación para aguantar"],
        "Midrange (Ragnar)": ["Balance de tropas y hechizos", "Eficiencia de maná", "Tropas de 3-5 coste"],
    }
    
    for style, tips in styles.items():
        print(f"\n   {style}:")
        for tip in tips:
            print(f"      • {tip}")


def print_usage_example():
    """Ejemplo de integración."""
    print("\n\n" + "="*120)
    print("🔧 EJEMPLO DE INTEGRACIÓN")
    print("="*120 + "\n")
    
    print("```python")
    print("from src.ai_engine import create_ai_opponent, SmartAI")
    print("from src.game_logic import Game")
    print()
    print("# Crear oponente IA de nivel 7")
    print("champion, deck, config = create_ai_opponent(difficulty_level=7)")
    print()
    print("# Crear jugador IA")
    print("ai_player = Player('IA Gran Maestro', deck, champion)")
    print("ai = SmartAI(difficulty=7)")
    print("ai.set_player(ai_player)")
    print()
    print("# Usar en el juego")
    print("# La IA tomará decisiones según análisis de 1M partidas")
    print("# - Nivel 7 tiene 70% de juego óptimo")
    print("# - Usa champions fuertes (Brutus/Ragnar/Mystara)")
    print("# - Mazo 70% optimizado con mejores cartas")
    print("# - Prioriza habilidad Furia (51.5% WR)")
    print("```")


def main():
    """Ejecuta la demo completa."""
    print_difficulty_showcase()
    print_matchup_analysis()
    print_recommendations()
    print_deck_building_tips()
    print_usage_example()
    
    print("\n\n" + "="*120)
    print("✨ SISTEMA DE IA v2.0 LISTO")
    print("="*120)
    print("\n📈 Mejoras principales:")
    print("   ✅ 10 niveles progresivos de dificultad")
    print("   ✅ Construcción de mazos basada en win rates reales")
    print("   ✅ Toma de decisiones optimizada por nivel")
    print("   ✅ Estrategias específicas por campeón")
    print("   ✅ Sistema de errores ajustable")
    print("   ✅ Agresividad y estilo configurables")
    print("\n🎮 ¡Listo para jugar!")
    print("="*120 + "\n")


if __name__ == "__main__":
    main()
