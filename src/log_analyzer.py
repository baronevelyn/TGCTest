"""
Advanced Log Analyzer
Analiza logs detallados de partidas para generar estadísticas profundas
"""

import re
from collections import defaultdict
from typing import Dict, List
from pathlib import Path


class LogAnalyzer:
    """Analizador avanzado de logs de partidas."""
    
    def __init__(self, log_file_path: str):
        self.log_file_path = log_file_path
        self.total_games = 0
        self.statistics = {
            'wins_by_champion': defaultdict(int),
            'total_damage_by_champion': defaultdict(int),
            'total_attacks_by_champion': defaultdict(int),
            'total_troops_by_champion': defaultdict(int),
            'total_spells_by_champion': defaultdict(int),
            'total_abilities_by_champion': defaultdict(int),
            'turn_distribution': defaultdict(int),
            'damage_by_turn': defaultdict(list),
            'cards_played_by_turn': defaultdict(list),
            'winning_strategies': defaultdict(int),
            'troop_stats': defaultdict(lambda: {'played': 0, 'damage_dealt': 0}),
            'spell_stats': defaultdict(lambda: {'cast': 0, 'total_damage': 0}),
            'furia_damage': 0,
            'token_damage': 0,
            'total_healing': 0,
            'ability_triggers': defaultdict(int),
            'matchup_details': {}
        }
    
    def analyze(self):
        """Analiza el archivo de logs completo."""
        print(f"\n📊 Analizando logs: {Path(self.log_file_path).name}")
        print(f"   Leyendo archivo... ", end='', flush=True)
        
        with open(self.log_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"✓ ({len(content)} caracteres)")
        
        # Dividir en partidas individuales
        games = content.split('⚔️  PARTIDA #')[1:]  # Skip header
        self.total_games = len(games)
        
        print(f"   Encontradas {self.total_games} partidas")
        print(f"   Procesando", end='', flush=True)
        
        for i, game in enumerate(games):
            if (i + 1) % 10 == 0:
                print('.', end='', flush=True)
            self._analyze_game(game, i + 1)
        
        print(" ✓")
        print(f"\n✅ Análisis completado!\n")
    
    def _analyze_game(self, game_text: str, game_num: int):
        """Analiza una partida individual."""
        # Extraer información básica
        lines = game_text.split('\n')
        
        # Encontrar campeones
        champ_match = re.search(r'(\w+) vs (\w+)', lines[0])
        if not champ_match:
            return
        
        champ1, champ2 = champ_match.groups()
        
        # Encontrar ganador
        winner_match = re.search(r'⭐ GANADOR: (\w+)', game_text)
        if not winner_match:
            return
        
        winner = winner_match.group(1)
        loser = champ2 if winner == champ1 else champ1
        
        self.statistics['wins_by_champion'][winner] += 1
        
        # Encontrar número de turnos
        turns_match = re.search(r'⏱️  Turnos: (\d+)', game_text)
        if turns_match:
            turns = int(turns_match.group(1))
            self.statistics['turn_distribution'][turns] += 1
        
        # Analizar estadísticas finales de cada jugador
        stats_pattern = r'📊 Estadísticas (\w+):\s+Cartas jugadas: (\d+) \| Tropas: (\d+) \| Hechizos: (\d+)\s+Ataques: (\d+) \| Daño total: (\d+)\s+Habilidades activadas: (\d+)'
        
        for match in re.finditer(stats_pattern, game_text):
            champ_name = match.group(1)
            cards = int(match.group(2))
            troops = int(match.group(3))
            spells = int(match.group(4))
            attacks = int(match.group(5))
            damage = int(match.group(6))
            abilities = int(match.group(7))
            
            self.statistics['total_damage_by_champion'][champ_name] += damage
            self.statistics['total_attacks_by_champion'][champ_name] += attacks
            self.statistics['total_troops_by_champion'][champ_name] += troops
            self.statistics['total_spells_by_champion'][champ_name] += spells
            self.statistics['total_abilities_by_champion'][champ_name] += abilities
        
        # Analizar tropas jugadas
        troop_pattern = r'Jugó (\w+(?: \w+)*) \(Costo:.*?⚔️ (\d+)/(\d+)(?: \((\w+)\))?'
        for match in re.finditer(troop_pattern, game_text):
            troop_name = match.group(1)
            attack = int(match.group(2))
            health = int(match.group(3))
            ability = match.group(4) if match.group(4) else 'None'
            
            self.statistics['troop_stats'][troop_name]['played'] += 1
        
        # Analizar hechizos
        spell_damage_pattern = r'Jugó ([\w\s]+) \(Costo:.*?💥 Daño: (\d+)'
        for match in re.finditer(spell_damage_pattern, game_text):
            spell_name = match.group(1).strip()
            damage = int(match.group(2))
            
            self.statistics['spell_stats'][spell_name]['cast'] += 1
            self.statistics['spell_stats'][spell_name]['total_damage'] += damage
        
        # Detectar daño de Furia
        furia_pattern = r'(\d+) daño \(x2 Furia\)'
        for match in re.finditer(furia_pattern, game_text):
            damage = int(match.group(1))
            self.statistics['furia_damage'] += damage
        
        # Detectar tokens
        token_attacks = game_text.count('Token (1/1) → 1 daño')
        self.statistics['token_damage'] += token_attacks
        
        # Detectar curación
        healing_pattern = r'💚 Hechizo de curación: \+(\d+)'
        for match in re.finditer(healing_pattern, game_text):
            healing = int(match.group(1))
            self.statistics['total_healing'] += healing
        
        # Detectar activaciones de habilidades
        ability_patterns = [
            (r'Invocó Token 1/1', 'Mystara Token Generation'),
            (r'Curó (\d+) tropa', 'Lumina Healing'),
            (r'descuento', 'Arcanus Spell Discount'),
            (r'\[Furia\]', 'Ragnar Furia Buff'),
            (r'\[\+1 ATK, Prisa\]', 'Shadowblade Cheap Buff'),
            (r'\[\+1/\+1\]', 'Sylvana Big Buff'),
            (r'\[\+\d+ ATK\]', 'Brutus Attack Buff')
        ]
        
        for pattern, ability_name in ability_patterns:
            matches = len(re.findall(pattern, game_text))
            if matches > 0:
                self.statistics['ability_triggers'][ability_name] += matches
        
        # Guardar matchup
        matchup_key = f"{champ1} vs {champ2}"
        if matchup_key not in self.statistics['matchup_details']:
            self.statistics['matchup_details'][matchup_key] = {
                'total_games': 0,
                'wins': {champ1: 0, champ2: 0},
                'avg_turns': []
            }
        
        self.statistics['matchup_details'][matchup_key]['total_games'] += 1
        self.statistics['matchup_details'][matchup_key]['wins'][winner] += 1
        if turns_match:
            self.statistics['matchup_details'][matchup_key]['avg_turns'].append(turns)
    
    def print_advanced_statistics(self):
        """Imprime estadísticas avanzadas."""
        print("="*100)
        print("📈 ESTADÍSTICAS AVANZADAS - ANÁLISIS PROFUNDO")
        print("="*100)
        
        # Resultados generales
        print(f"\n🏆 ANÁLISIS GENERAL:")
        print(f"   Total de partidas analizadas: {self.total_games}")
        print(f"\n   Victorias por campeón:")
        for champ, wins in sorted(self.statistics['wins_by_champion'].items(), key=lambda x: x[1], reverse=True):
            win_rate = wins / self.total_games * 100
            print(f"      • {champ}: {wins} victorias ({win_rate:.1f}% WR)")
        
        # Distribución de turnos
        print(f"\n⏱️  DISTRIBUCIÓN DE DURACIÓN:")
        total_turns = sum(turn * count for turn, count in self.statistics['turn_distribution'].items())
        avg_turns = total_turns / self.total_games if self.total_games > 0 else 0
        print(f"   Turnos promedio: {avg_turns:.1f}")
        print(f"   Distribución:")
        for turn in sorted(self.statistics['turn_distribution'].keys()):
            count = self.statistics['turn_distribution'][turn]
            pct = count / self.total_games * 100
            bar = '█' * int(pct / 2)
            print(f"      {turn} turnos: {count:3d} partidas ({pct:5.1f}%) {bar}")
        
        # Daño infligido
        print(f"\n💥 DAÑO TOTAL INFLIGIDO:")
        for champ in sorted(self.statistics['total_damage_by_champion'].keys()):
            total_damage = self.statistics['total_damage_by_champion'][champ]
            avg_damage = total_damage / self.total_games
            print(f"   • {champ}: {total_damage} daño total ({avg_damage:.1f} por partida)")
        
        # Eficiencia de ataques
        print(f"\n⚔️  EFICIENCIA DE COMBATE:")
        for champ in sorted(self.statistics['total_attacks_by_champion'].keys()):
            attacks = self.statistics['total_attacks_by_champion'][champ]
            damage = self.statistics['total_damage_by_champion'][champ]
            if attacks > 0:
                dmg_per_attack = damage / attacks
                avg_attacks = attacks / self.total_games
                print(f"   • {champ}: {avg_attacks:.1f} ataques/partida, {dmg_per_attack:.1f} daño/ataque")
        
        # Composición de mazos
        print(f"\n🎴 COMPOSICIÓN DE JUEGO:")
        for champ in sorted(self.statistics['total_troops_by_champion'].keys()):
            troops = self.statistics['total_troops_by_champion'][champ]
            spells = self.statistics['total_spells_by_champion'][champ]
            total = troops + spells
            if total > 0:
                troop_pct = troops / total * 100
                spell_pct = spells / total * 100
                avg_troops = troops / self.total_games
                avg_spells = spells / self.total_games
                print(f"   • {champ}: {avg_troops:.1f} tropas, {avg_spells:.1f} hechizos por partida")
                print(f"      └─ Ratio: {troop_pct:.1f}% tropas, {spell_pct:.1f}% hechizos")
        
        # Habilidades de campeones
        print(f"\n✨ ACTIVACIONES DE HABILIDADES:")
        for ability, count in sorted(self.statistics['ability_triggers'].items(), key=lambda x: x[1], reverse=True):
            avg = count / self.total_games
            print(f"   • {ability}: {count} veces ({avg:.1f} por partida)")
        
        # Top tropas
        print(f"\n🛡️ TROPAS MÁS JUGADAS:")
        sorted_troops = sorted(self.statistics['troop_stats'].items(), key=lambda x: x[1]['played'], reverse=True)
        for i, (troop, stats) in enumerate(sorted_troops[:10], 1):
            count = stats['played']
            avg = count / self.total_games
            print(f"   {i:2d}. {troop}: {count} veces ({avg:.2f} por partida)")
        
        # Top hechizos
        print(f"\n⚡ HECHIZOS MÁS USADOS:")
        sorted_spells = sorted(self.statistics['spell_stats'].items(), key=lambda x: x[1]['cast'], reverse=True)
        for i, (spell, stats) in enumerate(sorted_spells[:10], 1):
            count = stats['cast']
            avg_dmg = stats['total_damage'] / count if count > 0 else 0
            print(f"   {i:2d}. {spell}: {count} veces, {avg_dmg:.1f} daño promedio")
        
        # Métricas especiales
        print(f"\n🔥 MÉTRICAS ESPECIALES:")
        print(f"   • Daño total de Furia: {self.statistics['furia_damage']}")
        print(f"   • Daño de Tokens (Mystara): {self.statistics['token_damage']}")
        print(f"   • Curación total: {self.statistics['total_healing']}")
        
        # Análisis de matchup
        print(f"\n⚔️  ANÁLISIS DE MATCHUP:")
        for matchup, details in self.statistics['matchup_details'].items():
            champs = matchup.split(' vs ')
            total = details['total_games']
            wins_c1 = details['wins'][champs[0]]
            wins_c2 = details['wins'][champs[1]]
            wr = wins_c1 / total * 100 if total > 0 else 0
            avg_t = sum(details['avg_turns']) / len(details['avg_turns']) if details['avg_turns'] else 0
            
            print(f"   • {matchup}:")
            print(f"      └─ {champs[0]}: {wins_c1}-{wins_c2} ({wr:.1f}% WR) | Duración media: {avg_t:.1f} turnos")
        
        print(f"\n{'='*100}\n")
    
    def generate_summary_file(self, output_path: str):
        """Genera un archivo resumen con todas las estadísticas."""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("="*100 + "\n")
            f.write("📊 RESUMEN COMPLETO DE ANÁLISIS\n")
            f.write("="*100 + "\n\n")
            
            # Redirigir print a archivo
            import sys
            old_stdout = sys.stdout
            sys.stdout = f
            
            self.print_advanced_statistics()
            
            sys.stdout = old_stdout
        
        print(f"✅ Resumen guardado en: {output_path}")


def main():
    """Función principal."""
    import sys
    from pathlib import Path
    
    # Buscar el archivo de logs más reciente
    data_folder = Path(__file__).parent.parent / 'data'
    log_files = list(data_folder.glob('GAME_LOGS_*.txt'))
    
    if not log_files:
        print("❌ No se encontraron archivos de logs")
        print("   Ejecuta primero: python src/game_simulator_with_logging.py")
        return
    
    # Usar el más reciente
    latest_log = max(log_files, key=lambda p: p.stat().st_mtime)
    
    print(f"\n🔍 ANALIZADOR AVANZADO DE LOGS")
    print(f"{'='*100}\n")
    
    # Analizar
    analyzer = LogAnalyzer(str(latest_log))
    analyzer.analyze()
    analyzer.print_advanced_statistics()
    
    # Guardar resumen
    timestamp = latest_log.stem.replace('GAME_LOGS_', '')
    summary_path = data_folder / f'ANALISIS_AVANZADO_{timestamp}.txt'
    analyzer.generate_summary_file(str(summary_path))
    
    print(f"\n✨ Análisis completado exitosamente!")


if __name__ == '__main__':
    main()
