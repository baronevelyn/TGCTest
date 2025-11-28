"""
Analizador completo y mejorado para logs masivos de TCG
Extrae TODAS las estadísticas disponibles: campeones, cartas, mazos, estrategias, etc.
"""

import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path
import time


class CompleteTCGAnalyzer:
    """Analizador completo con todas las métricas posibles."""
    
    def __init__(self, log_file_path: str):
        self.log_file_path = Path(log_file_path)
        self.stats = {
            # Stats generales
            'total_games': 0,
            
            # Stats de campeones
            'champion_stats': defaultdict(lambda: {
                'games': 0, 'wins': 0, 'losses': 0,
                'total_turns_won': 0, 'total_turns_lost': 0,
                'total_damage_dealt': 0, 'total_damage_received': 0,
                'cards_played': 0, 'troops_played': 0, 'spells_cast': 0,
                'cards_drawn': 0, 'attacks_made': 0
            }),
            
            # Stats de cartas
            'card_stats': defaultdict(lambda: {
                'times_played': 0, 'in_winning_decks': 0, 'in_losing_decks': 0
            }),
            
            # Stats de tropas específicas
            'troop_stats': defaultdict(lambda: {
                'times_played': 0, 'wins': 0, 'losses': 0,
                'avg_cost': 0, 'total_cost': 0
            }),
            
            # Stats de hechizos
            'spell_stats': defaultdict(lambda: {
                'times_played': 0, 'wins': 0, 'losses': 0,
                'avg_cost': 0, 'total_cost': 0
            }),
            
            # Habilidades
            'ability_stats': defaultdict(lambda: {
                'times_in_deck': 0, 'wins': 0, 'losses': 0
            }),
            
            # Matchups
            'matchup_matrix': defaultdict(lambda: defaultdict(lambda: {
                'games': 0, 'wins': 0
            })),
            
            # Duración
            'turn_distribution': defaultdict(int),
            
            # Composición de mazos ganadores
            'winning_deck_composition': {
                'troop_counts': [],
                'spell_counts': [],
                'avg_troop_cost': [],
                'avg_spell_cost': []
            },
            
            # Records
            'fastest_wins': [],
            'longest_games': [],
            'highest_damage_game': {'damage': 0, 'info': None}
        }
    
    def process_file(self):
        """Procesa el archivo completo."""
        print(f"📊 Iniciando análisis completo de: {self.log_file_path.name}")
        size_gb = self.log_file_path.stat().st_size / (1024**3)
        print(f"📁 Tamaño: {size_gb:.2f} GB\n")
        
        start_time = time.time()
        current_game_data = []
        games_processed = 0
        
        with open(self.log_file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                # Detectar inicio de partida
                if '⚔️  PARTIDA #' in line:
                    # Procesar partida anterior
                    if current_game_data:
                        self._process_complete_game('\n'.join(current_game_data))
                        games_processed += 1
                        # Progreso periódico sin asumir total fijo
                        if games_processed % 1000 == 0:
                            elapsed = time.time() - start_time
                            rate = games_processed / elapsed if elapsed > 0 else 0
                            print(f"⏳ {games_processed:,} partidas | {rate:.0f} p/s | {elapsed/60:.1f} min")
                    
                    current_game_data = [line]
                elif current_game_data:
                    current_game_data.append(line)
            
            # Última partida
            if current_game_data:
                self._process_complete_game('\n'.join(current_game_data))
                games_processed += 1
        
        self._finalize_stats()
        
        elapsed = time.time() - start_time
        print(f"\n✅ Completado en {elapsed/60:.2f} minutos")
        print(f"📈 {games_processed:,} partidas | {games_processed/elapsed:.1f} p/s")
        
        return elapsed
    
    def _process_complete_game(self, game_text: str):
        """Procesa una partida completa extrayendo TODA la información."""
        self.stats['total_games'] += 1
        
        # === INFORMACIÓN BÁSICA ===
        # Nombres de campeones
        match = re.search(r'PARTIDA #\d+ \(\d+/\d+\) - (.+?) vs (.+?)$', game_text, re.MULTILINE)
        if not match:
            return
        
        champ1, champ2 = match.group(1).strip(), match.group(2).strip()
        
        # Ganador
        winner_match = re.search(r'GANADOR: (.+?)$', game_text, re.MULTILINE)
        if not winner_match:
            return
        winner = winner_match.group(1).strip()
        loser = champ2 if winner == champ1 else champ1
        
        # Turnos
        turn_match = re.search(r'Duración: (\d+) turnos?', game_text)
        turns = int(turn_match.group(1)) if turn_match else 0
        
        # === STATS DE CAMPEONES ===
        self.stats['champion_stats'][winner]['games'] += 1
        self.stats['champion_stats'][winner]['wins'] += 1
        self.stats['champion_stats'][winner]['total_turns_won'] += turns
        
        self.stats['champion_stats'][loser]['games'] += 1
        self.stats['champion_stats'][loser]['losses'] += 1
        self.stats['champion_stats'][loser]['total_turns_lost'] += turns
        
        # === ESTADÍSTICAS DETALLADAS ===
        # Buscar sección de estadísticas
        stats_section = re.search(
            r'📊 ESTADÍSTICAS DETALLADAS:(.+?)(?:={100,}|$)', 
            game_text, re.DOTALL
        )
        
        if stats_section:
            stats_text = stats_section.group(1)
            
            # Extraer stats del ganador y perdedor
            for champ_name in [champ1, champ2]:
                is_winner = (champ_name == winner)
                champ_stats = self.stats['champion_stats'][champ_name]
                
                # Buscar bloque de stats de este campeón
                pattern = rf'{champ_name}:(.+?)(?:{champ1}:|{champ2}:|$)'
                champ_block = re.search(pattern, stats_text, re.DOTALL)
                
                if champ_block:
                    block = champ_block.group(1)
                    
                    # Extraer valores
                    if match := re.search(r'Cartas robadas: (\d+)', block):
                        champ_stats['cards_drawn'] += int(match.group(1))
                    if match := re.search(r'Cartas jugadas: (\d+)', block):
                        champ_stats['cards_played'] += int(match.group(1))
                    if match := re.search(r'Tropas invocadas: (\d+)', block):
                        champ_stats['troops_played'] += int(match.group(1))
                    if match := re.search(r'Hechizos lanzados: (\d+)', block):
                        champ_stats['spells_cast'] += int(match.group(1))
                    if match := re.search(r'Ataques realizados: (\d+)', block):
                        champ_stats['attacks_made'] += int(match.group(1))
                    if match := re.search(r'Daño total infligido: (\d+)', block):
                        damage = int(match.group(1))
                        champ_stats['total_damage_dealt'] += damage
                        
                        # Track highest damage
                        if damage > self.stats['highest_damage_game']['damage']:
                            self.stats['highest_damage_game'] = {
                                'damage': damage,
                                'info': f"{champ_name} vs {champ2 if champ_name == champ1 else champ1} ({turns} turnos)"
                            }
        
        # === COMPOSICIÓN DE MAZOS ===
        # Analizar mazos del ganador y perdedor
        for champ_name in [winner, loser]:
            is_winner = (champ_name == winner)
            
            # Buscar sección de mazo
            deck_pattern = rf'Mazo de {champ_name}:(.+?)(?:Mazo de|={100,}|TURNO 1)'
            deck_match = re.search(deck_pattern, game_text, re.DOTALL)
            
            if deck_match:
                deck_text = deck_match.group(1)
                
                # Contar tropas y hechizos
                troop_match = re.search(r'Tropas \((\d+)\):', deck_text)
                spell_match = re.search(r'Hechizos \((\d+)\):', deck_text)
                
                if troop_match and spell_match:
                    troop_count = int(troop_match.group(1))
                    spell_count = int(spell_match.group(1))
                    
                    if is_winner:
                        self.stats['winning_deck_composition']['troop_counts'].append(troop_count)
                        self.stats['winning_deck_composition']['spell_counts'].append(spell_count)
                
                # Extraer cartas específicas
                # Tropas: • CardName (cost⚡ atk/hp) [ability] xN
                troop_matches = re.findall(
                    r'• ([A-Za-z ]+) \((\d+)⚡ \d+/\d+\)(?: \[([^\]]+)\])? x(\d+)',
                    deck_text
                )
                
                for card_name, cost, ability, count in troop_matches:
                    card_name = card_name.strip()
                    count = int(count)
                    cost = int(cost)
                    
                    # Stats de carta
                    self.stats['card_stats'][card_name]['times_played'] += count
                    if is_winner:
                        self.stats['card_stats'][card_name]['in_winning_decks'] += count
                    else:
                        self.stats['card_stats'][card_name]['in_losing_decks'] += count
                    
                    # Stats de tropa
                    self.stats['troop_stats'][card_name]['times_played'] += count
                    self.stats['troop_stats'][card_name]['total_cost'] += cost * count
                    if is_winner:
                        self.stats['troop_stats'][card_name]['wins'] += count
                    else:
                        self.stats['troop_stats'][card_name]['losses'] += count
                    
                    # Stats de habilidad
                    if ability:
                        self.stats['ability_stats'][ability]['times_in_deck'] += count
                        if is_winner:
                            self.stats['ability_stats'][ability]['wins'] += count
                        else:
                            self.stats['ability_stats'][ability]['losses'] += count
                
                # Hechizos: • SpellName (cost⚡) xN
                spell_matches = re.findall(
                    r'• ([A-Za-z ]+) \((\d+)⚡\) x(\d+)',
                    deck_text
                )
                
                for spell_name, cost, count in spell_matches:
                    spell_name = spell_name.strip()
                    count = int(count)
                    cost = int(cost)
                    
                    # Stats de carta
                    self.stats['card_stats'][spell_name]['times_played'] += count
                    if is_winner:
                        self.stats['card_stats'][spell_name]['in_winning_decks'] += count
                    else:
                        self.stats['card_stats'][spell_name]['in_losing_decks'] += count
                    
                    # Stats de hechizo
                    self.stats['spell_stats'][spell_name]['times_played'] += count
                    self.stats['spell_stats'][spell_name]['total_cost'] += cost * count
                    if is_winner:
                        self.stats['spell_stats'][spell_name]['wins'] += count
                    else:
                        self.stats['spell_stats'][spell_name]['losses'] += count
        
        # === MATCHUPS ===
        self.stats['matchup_matrix'][champ1][champ2]['games'] += 1
        self.stats['matchup_matrix'][champ2][champ1]['games'] += 1
        
        if winner == champ1:
            self.stats['matchup_matrix'][champ1][champ2]['wins'] += 1
        else:
            self.stats['matchup_matrix'][champ2][champ1]['wins'] += 1
        
        # === DURACIÓN ===
        self.stats['turn_distribution'][turns] += 1
        
        # === RECORDS ===
        game_info = {
            'champ1': champ1, 'champ2': champ2,
            'winner': winner, 'turns': turns
        }
        
        # Fastest wins
        self.stats['fastest_wins'].append(game_info)
        if len(self.stats['fastest_wins']) > 20:
            self.stats['fastest_wins'].sort(key=lambda x: x['turns'])
            self.stats['fastest_wins'] = self.stats['fastest_wins'][:20]
        
        # Longest games
        self.stats['longest_games'].append(game_info)
        if len(self.stats['longest_games']) > 20:
            self.stats['longest_games'].sort(key=lambda x: x['turns'], reverse=True)
            self.stats['longest_games'] = self.stats['longest_games'][:20]
    
    def _finalize_stats(self):
        """Calcula promedios y ratios finales."""
        # Win rates de campeones
        for champ, stats in self.stats['champion_stats'].items():
            if stats['games'] > 0:
                stats['win_rate'] = (stats['wins'] / stats['games']) * 100
                stats['avg_turns_won'] = stats['total_turns_won'] / stats['wins'] if stats['wins'] > 0 else 0
                stats['avg_turns_lost'] = stats['total_turns_lost'] / stats['losses'] if stats['losses'] > 0 else 0
                stats['avg_damage_per_game'] = stats['total_damage_dealt'] / stats['games']
                stats['avg_cards_per_game'] = stats['cards_played'] / stats['games']
        
        # Win rates de cartas
        for card, stats in self.stats['card_stats'].items():
            total = stats['in_winning_decks'] + stats['in_losing_decks']
            if total > 0:
                stats['win_rate'] = (stats['in_winning_decks'] / total) * 100
        
        # Costos promedio de tropas
        for troop, stats in self.stats['troop_stats'].items():
            if stats['times_played'] > 0:
                stats['avg_cost'] = stats['total_cost'] / stats['times_played']
                total = stats['wins'] + stats['losses']
                stats['win_rate'] = (stats['wins'] / total * 100) if total > 0 else 0
        
        # Costos promedio de hechizos
        for spell, stats in self.stats['spell_stats'].items():
            if stats['times_played'] > 0:
                stats['avg_cost'] = stats['total_cost'] / stats['times_played']
                total = stats['wins'] + stats['losses']
                stats['win_rate'] = (stats['wins'] / total * 100) if total > 0 else 0
        
        # Win rates de habilidades
        for ability, stats in self.stats['ability_stats'].items():
            total = stats['wins'] + stats['losses']
            if total > 0:
                stats['win_rate'] = (stats['wins'] / total) * 100
    
    def generate_complete_report(self, output_file: str | None = None):
        """Genera reporte super completo."""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"data/COMPLETE_ANALYSIS_{timestamp}.txt"
        
        output_path = Path(output_file)
        output_path.parent.mkdir(exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            self._write_header(f)
            self._write_champion_stats(f)
            self._write_card_stats(f)
            self._write_troop_stats(f)
            self._write_spell_stats(f)
            self._write_ability_stats(f)
            self._write_deck_composition(f)
            self._write_matchup_matrix(f)
            self._write_turn_distribution(f)
            self._write_records(f)
            self._write_strategy_recommendations(f)
        
        print(f"\n📄 Reporte completo guardado en: {output_path}")
        return output_path
    
    def _write_header(self, f):
        f.write("="*120 + "\n")
        f.write("🎮 ANÁLISIS ULTRA-COMPLETO - MINI TCG\n")
        f.write("="*120 + "\n\n")
        f.write(f"📊 Total de partidas: {self.stats['total_games']:,}\n")
        f.write(f"🏆 Campeones analizados: {len(self.stats['champion_stats'])}\n")
        f.write(f"🎴 Cartas únicas: {len(self.stats['card_stats'])}\n")
        f.write(f"⚔️  Tropas únicas: {len(self.stats['troop_stats'])}\n")
        f.write(f"⚡ Hechizos únicos: {len(self.stats['spell_stats'])}\n\n")

    def _write_strategy_recommendations(self, f):
        """Genera recomendaciones de estrategia y balance a partir de las métricas."""
        f.write("\n" + "="*120 + "\n")
        f.write("🧠 RECOMENDACIONES DE ESTRATEGIA Y BALANCE\n")
        f.write("="*120 + "\n\n")

        # Top campeones por WR
        champs = [
            (c, s) for c, s in self.stats['champion_stats'].items() if s.get('games', 0) >= 1000
        ]
        champs.sort(key=lambda x: x[1].get('win_rate', 0), reverse=True)

        if champs:
            f.write("🏆 CAMPEONES A PRIORIZAR\n")
            for c, s in champs[:5]:
                f.write(f"   • {c}: {s.get('win_rate', 0):.1f}% WR | cartas/juego {s.get('avg_cards_per_game', 0):.1f} | daño/juego {s.get('avg_damage_per_game', 0):.1f}\n")
            f.write("\n")

        # Peores campeones para ajustar
        low_champs = champs[-5:] if len(champs) >= 5 else champs
        if low_champs:
            f.write("🛠️  POSIBLES AJUSTES (BUFFS)\n")
            for c, s in sorted(low_champs, key=lambda x: x[1].get('win_rate', 0)):
                if s.get('win_rate', 0) < 45:
                    f.write(f"   • {c}: {s.get('win_rate', 0):.1f}% WR — revisar pasiva o curva de coste\n")
            f.write("\n")

        # Cartas con alta correlación a victoria
        cards = [
            (k, v) for k, v in self.stats['card_stats'].items()
            if (v.get('in_winning_decks', 0) + v.get('in_losing_decks', 0)) >= 200
        ]
        for _, v in cards:
            total = v.get('in_winning_decks', 0) + v.get('in_losing_decks', 0)
            v['win_rate'] = (v.get('in_winning_decks', 0) / total * 100) if total > 0 else 0
        cards.sort(key=lambda x: x[1].get('win_rate', 0), reverse=True)
        if cards:
            f.write("💡 CARTAS QUE SUBEN WR\n")
            for k, v in cards[:10]:
                f.write(f"   • {k}: {v.get('win_rate', 0):.1f}% WR (muestras: {v.get('in_winning_decks', 0)+v.get('in_losing_decks', 0)})\n")
            f.write("\n")

        # Habilidades fuertes
        abilities = [
            (k, v) for k, v in self.stats['ability_stats'].items() if (v.get('wins', 0) + v.get('losses', 0)) >= 200
        ]
        for _, v in abilities:
            total = v.get('wins', 0) + v.get('losses', 0)
            v['win_rate'] = (v.get('wins', 0) / total * 100) if total > 0 else 0
        abilities.sort(key=lambda x: x[1].get('win_rate', 0), reverse=True)
        if abilities:
            f.write("✨ HABILIDADES CLAVE\n")
            for k, v in abilities[:10]:
                f.write(f"   • {k}: {v.get('win_rate', 0):.1f}% WR (muestras: {v.get('wins', 0)+v.get('losses', 0)})\n")
            f.write("\n")

        # Counters de campeones (peor matchup para los top)
        if champs:
            f.write("🛡️  COUNTERS SUGERIDOS\n")
            for c, _ in champs[:5]:
                worst_vs = None
                worst_wr = 101.0
                for opp, data in self.stats['matchup_matrix'].get(c, {}).items():
                    games = data.get('games', 0)
                    if games < 50:
                        continue
                    wr = (data.get('wins', 0) / games * 100) if games > 0 else 0
                    if wr < worst_wr:
                        worst_wr = wr
                        worst_vs = opp
                if worst_vs is not None:
                    f.write(f"   • {c} sufre vs {worst_vs} ({worst_wr:.1f}% WR). Considera estrategias/ajustes contra {worst_vs}.\n")
            f.write("\n")
    
    def _write_champion_stats(self, f):
        f.write("\n" + "="*120 + "\n")
        f.write("🏆 RANKING COMPLETO DE CAMPEONES\n")
        f.write("="*120 + "\n\n")
        
        sorted_champs = sorted(
            self.stats['champion_stats'].items(),
            key=lambda x: x[1]['win_rate'],
            reverse=True
        )
        
        f.write(f"{'#':<4} {'Campeón':<15} {'Partidas':<10} {'Victorias':<10} {'WR%':<8} "
               f"{'Avg Turnos':<12} {'Daño/Juego':<12} {'Cartas/Juego':<12}\n")
        f.write("-"*120 + "\n")
        
        for i, (champ, stats) in enumerate(sorted_champs, 1):
            f.write(f"{i:<4} {champ:<15} {stats['games']:<10,} {stats['wins']:<10,} "
                   f"{stats['win_rate']:<8.2f} {stats['avg_turns_won']:<12.1f} "
                   f"{stats['avg_damage_per_game']:<12.1f} {stats['avg_cards_per_game']:<12.1f}\n")
        
        f.write("\n📊 ESTADÍSTICAS DETALLADAS POR CAMPEÓN:\n")
        f.write("-"*120 + "\n")
        
        for champ, stats in sorted_champs:
            f.write(f"\n🎯 {champ}:\n")
            f.write(f"   Win Rate: {stats['win_rate']:.2f}%\n")
            f.write(f"   Partidas: {stats['games']:,} ({stats['wins']:,}W / {stats['losses']:,}L)\n")
            f.write(f"   Turnos promedio: {stats['avg_turns_won']:.1f} (victoria) / {stats['avg_turns_lost']:.1f} (derrota)\n")
            f.write(f"   Daño total infligido: {stats['total_damage_dealt']:,} ({stats['avg_damage_per_game']:.1f} por juego)\n")
            f.write(f"   Cartas jugadas: {stats['cards_played']:,} ({stats['avg_cards_per_game']:.1f} por juego)\n")
            f.write(f"   Tropas invocadas: {stats['troops_played']:,}\n")
            f.write(f"   Hechizos lanzados: {stats['spells_cast']:,}\n")
            f.write(f"   Ataques realizados: {stats['attacks_made']:,}\n")
            f.write(f"   Cartas robadas: {stats['cards_drawn']:,}\n")
    
    def _write_card_stats(self, f):
        f.write("\n\n" + "="*120 + "\n")
        f.write("🎴 TOP 30 MEJORES CARTAS (Por Win Rate)\n")
        f.write("="*120 + "\n\n")
        
        # Filtrar cartas con suficiente sample size
        significant_cards = {
            card: stats for card, stats in self.stats['card_stats'].items()
            if stats['times_played'] >= 1000
        }
        
        sorted_cards = sorted(
            significant_cards.items(),
            key=lambda x: x[1]['win_rate'],
            reverse=True
        )[:30]
        
        f.write(f"{'#':<4} {'Carta':<25} {'Veces Jugada':<15} {'En Mazos Ganadores':<20} {'Win Rate':<10}\n")
        f.write("-"*120 + "\n")
        
        for i, (card, stats) in enumerate(sorted_cards, 1):
            f.write(f"{i:<4} {card:<25} {stats['times_played']:<15,} "
                   f"{stats['in_winning_decks']:<20,} {stats['win_rate']:<10.2f}%\n")
    
    def _write_troop_stats(self, f):
        f.write("\n\n" + "="*120 + "\n")
        f.write("⚔️  TOP 20 MEJORES TROPAS\n")
        f.write("="*120 + "\n\n")
        
        significant_troops = {
            troop: stats for troop, stats in self.stats['troop_stats'].items()
            if stats['times_played'] >= 500
        }
        
        sorted_troops = sorted(
            significant_troops.items(),
            key=lambda x: x[1]['win_rate'],
            reverse=True
        )[:20]
        
        f.write(f"{'#':<4} {'Tropa':<20} {'Veces Jugada':<15} {'Victorias':<12} {'WR%':<10} {'Costo Avg':<12}\n")
        f.write("-"*120 + "\n")
        
        for i, (troop, stats) in enumerate(sorted_troops, 1):
            f.write(f"{i:<4} {troop:<20} {stats['times_played']:<15,} "
                   f"{stats['wins']:<12,} {stats['win_rate']:<10.2f} {stats['avg_cost']:<12.2f}\n")
    
    def _write_spell_stats(self, f):
        f.write("\n\n" + "="*120 + "\n")
        f.write("⚡ TOP 15 MEJORES HECHIZOS\n")
        f.write("="*120 + "\n\n")
        
        significant_spells = {
            spell: stats for spell, stats in self.stats['spell_stats'].items()
            if stats['times_played'] >= 300
        }
        
        sorted_spells = sorted(
            significant_spells.items(),
            key=lambda x: x[1]['win_rate'],
            reverse=True
        )[:15]
        
        f.write(f"{'#':<4} {'Hechizo':<25} {'Veces Jugado':<15} {'Victorias':<12} {'WR%':<10} {'Costo Avg':<12}\n")
        f.write("-"*120 + "\n")
        
        for i, (spell, stats) in enumerate(sorted_spells, 1):
            f.write(f"{i:<4} {spell:<25} {stats['times_played']:<15,} "
                   f"{stats['wins']:<12,} {stats['win_rate']:<10.2f} {stats['avg_cost']:<12.2f}\n")
    
    def _write_ability_stats(self, f):
        f.write("\n\n" + "="*120 + "\n")
        f.write("✨ RANKING DE HABILIDADES\n")
        f.write("="*120 + "\n\n")
        
        sorted_abilities = sorted(
            self.stats['ability_stats'].items(),
            key=lambda x: x[1]['win_rate'],
            reverse=True
        )
        
        f.write(f"{'#':<4} {'Habilidad':<20} {'Veces en Mazo':<18} {'Victorias':<12} {'Win Rate':<10}\n")
        f.write("-"*120 + "\n")
        
        for i, (ability, stats) in enumerate(sorted_abilities, 1):
            f.write(f"{i:<4} {ability:<20} {stats['times_in_deck']:<18,} "
                   f"{stats['wins']:<12,} {stats['win_rate']:<10.2f}%\n")
    
    def _write_deck_composition(self, f):
        f.write("\n\n" + "="*120 + "\n")
        f.write("📦 COMPOSICIÓN ÓPTIMA DE MAZOS GANADORES\n")
        f.write("="*120 + "\n\n")
        
        if self.stats['winning_deck_composition']['troop_counts']:
            troop_counts = self.stats['winning_deck_composition']['troop_counts']
            spell_counts = self.stats['winning_deck_composition']['spell_counts']
            
            avg_troops = sum(troop_counts) / len(troop_counts)
            avg_spells = sum(spell_counts) / len(spell_counts)
            
            f.write(f"Promedio de tropas en mazos ganadores: {avg_troops:.1f}\n")
            f.write(f"Promedio de hechizos en mazos ganadores: {avg_spells:.1f}\n")
            f.write(f"Ratio Tropas:Hechizos óptimo: {avg_troops/avg_spells:.2f}:1\n")
    
    def _write_matchup_matrix(self, f):
        f.write("\n\n" + "="*120 + "\n")
        f.write("⚔️  MATRIZ DE MATCHUPS\n")
        f.write("="*120 + "\n\n")
        
        # Top matchups
        matchups = []
        for champ1, opponents in self.stats['matchup_matrix'].items():
            for champ2, data in opponents.items():
                if data['games'] >= 100:
                    wr = (data['wins'] / data['games'] * 100) if data['games'] > 0 else 0
                    matchups.append({
                        'champ1': champ1, 'champ2': champ2,
                        'games': data['games'], 'wins': data['wins'], 'wr': wr
                    })
        
        matchups.sort(key=lambda x: x['wr'], reverse=True)
        
        f.write("🔥 TOP 25 MEJORES MATCHUPS:\n")
        f.write("-"*120 + "\n")
        for i, mu in enumerate(matchups[:25], 1):
            f.write(f"{i:2}. {mu['champ1']:<15} vs {mu['champ2']:<15} - "
                   f"{mu['wr']:>6.2f}% ({mu['wins']:>5,}/{mu['games']:>5,})\n")
        
        f.write("\n❄️  TOP 25 PEORES MATCHUPS:\n")
        f.write("-"*120 + "\n")
        for i, mu in enumerate(matchups[-25:], 1):
            f.write(f"{i:2}. {mu['champ1']:<15} vs {mu['champ2']:<15} - "
                   f"{mu['wr']:>6.2f}% ({mu['wins']:>5,}/{mu['games']:>5,})\n")
    
    def _write_turn_distribution(self, f):
        f.write("\n\n" + "="*120 + "\n")
        f.write("⏱️  DISTRIBUCIÓN DE DURACIÓN\n")
        f.write("="*120 + "\n\n")
        
        sorted_turns = sorted(self.stats['turn_distribution'].items())
        max_games = max(self.stats['turn_distribution'].values())
        
        f.write(f"{'Turnos':<10} {'Partidas':<15} {'%':<10} {'Gráfica'}\n")
        f.write("-"*120 + "\n")
        
        for turns, count in sorted_turns[:25]:
            pct = (count / self.stats['total_games']) * 100
            bar_len = int((count / max_games) * 60)
            bar = "█" * bar_len
            f.write(f"{turns:<10} {count:<15,} {pct:<10.2f} {bar}\n")
    
    def _write_records(self, f):
        f.write("\n\n" + "="*120 + "\n")
        f.write("🏅 RÉCORDS Y PARTIDAS DESTACADAS\n")
        f.write("="*120 + "\n\n")
        
        f.write("⚡ TOP 20 PARTIDAS MÁS RÁPIDAS:\n")
        f.write("-"*120 + "\n")
        for i, game in enumerate(self.stats['fastest_wins'], 1):
            opponent = game['champ2'] if game['winner'] == game['champ1'] else game['champ1']
            f.write(f"{i:2}. {game['winner']:<15} vs {opponent:<15} "
                   f"- {game['turns']} turnos\n")
        
        f.write("\n🐢 TOP 20 PARTIDAS MÁS LARGAS:\n")
        f.write("-"*120 + "\n")
        for i, game in enumerate(self.stats['longest_games'], 1):
            opponent = game['champ2'] if game['winner'] == game['champ1'] else game['champ1']
            f.write(f"{i:2}. {game['winner']:<15} vs {opponent:<15} "
                   f"- {game['turns']} turnos\n")
        
        if self.stats['highest_damage_game']['info']:
            f.write(f"\n💥 RÉCORD DE DAÑO EN UNA PARTIDA:\n")
            f.write(f"   {self.stats['highest_damage_game']['damage']:,} puntos de daño\n")
            f.write(f"   {self.stats['highest_damage_game']['info']}\n")


def main():
    # Buscar el archivo de logs más reciente en la carpeta data
    import sys
    
    # Determinar ruta a carpeta data
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / 'data'
    
    if not data_dir.exists():
        print(f"❌ Error: No se encuentra la carpeta {data_dir}")
        print("   Ejecuta primero: python massive_simulator.py")
        sys.exit(1)
    
    # Buscar archivos MASSIVE_LOGS
    log_files = list(data_dir.glob('MASSIVE_LOGS_*.txt'))
    
    if not log_files:
        print(f"❌ Error: No se encontraron archivos MASSIVE_LOGS_*.txt en {data_dir}")
        print("   Ejecuta primero: python massive_simulator.py")
        sys.exit(1)
    
    # Usar el más reciente
    latest_log = max(log_files, key=lambda p: p.stat().st_mtime)
    
    print("\n" + "="*120)
    print("🎮 ANALIZADOR COMPLETO - MINI TCG v2.0")
    print("="*120)
    print(f"📁 Archivo: {latest_log.name}")
    print("="*120 + "\n")
    
    analyzer = CompleteTCGAnalyzer(str(latest_log))
    elapsed = analyzer.process_file()
    
    print("\n📝 Generando reporte ultra-completo...")
    report_path = analyzer.generate_complete_report()
    
    print("\n" + "="*120)
    print("✨ ANÁLISIS COMPLETO TERMINADO")
    print("="*120)
    print(f"⏱️  Tiempo: {elapsed/60:.2f} min")
    print(f"📊 Partidas: {analyzer.stats['total_games']:,}")
    print(f"📄 Reporte: {report_path}")
    print("="*120 + "\n")


if __name__ == "__main__":
    main()
