"""Test rápido para game_analysis.py"""
from src.game_analysis import GameSimulator
from src.champions import get_champion_by_name

print("🧪 Probando game_analysis.py...")

# Crear simulador
sim = GameSimulator()

# Simular una partida
champ1 = get_champion_by_name('Ragnar')
champ2 = get_champion_by_name('Mystara')

if champ1 and champ2:
    result = sim.simulate_match(champ1, champ2, verbose=True)
    print(f"\n✅ Simulación exitosa!")
    print(f"   Ganador: {result['winner']}")
    print(f"   Turnos: {result['turns']}")
    print(f"   Vida final {champ1.name}: {result['final_life_p1']} HP")
    print(f"   Vida final {champ2.name}: {result['final_life_p2']} HP")
    print(f"\n✅ game_analysis.py funciona correctamente!")
else:
    print("❌ Error: No se pudieron cargar los campeones")
