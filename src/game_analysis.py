"""
Game Analysis and Strategy Simulator
Simulates matches between different champion combinations and analyzes strategies.
"""

import random
import sys
from pathlib import Path
from typing import List, Tuple, Dict

# Permitir imports relativos y absolutos
if __name__ == '__main__':
    # Agregar el directorio padre al path para imports
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from src.models import Player, Card, Deck
    from src.champions import CHAMPION_LIST, Champion
    from src.cards import build_random_deck, TROOP_TEMPLATES, SPELL_TEMPLATES
    from src.game_logic import Game
else:
    from .models import Player, Card, Deck
    from .champions import CHAMPION_LIST, Champion
    from .cards import build_random_deck, TROOP_TEMPLATES, SPELL_TEMPLATES
    from .game_logic import Game

import copy


class GameSimulator:
    """Simulates games and collects statistics."""
    
    def __init__(self):
        self.match_results = []
        self.champion_stats = {champ.name: {"wins": 0, "losses": 0, "total_damage": 0, "avg_game_length": []} 
                              for champ in CHAMPION_LIST}
        self.log_file = None
    
    def _log(self, message: str):
        """Escribe un mensaje al archivo de log si está habilitado."""
        if self.log_file:
            self.log_file.write(message + '\n')
            self.log_file.flush()
    
    def simulate_match(self, champ1: Champion, champ2: Champion, verbose: bool = False, log_details: bool = False) -> Dict:
        """Simulate a match between two champions."""
        # Optimize: create decks without checking assets
        import random
        
        if log_details:
            self._log("\n" + "="*80)
            self._log(f"⚔️  NUEVA PARTIDA: {champ1.name} vs {champ2.name}")
            self._log("="*80)
        
        # Build decks faster without create_card
        def quick_deck(size=40, spell_ratio=0.3):
            cards = []
            num_spells = int(size * spell_ratio)
            num_troops = size - num_spells
            
            for _ in range(num_troops):
                name, cost, dmg, ability, ability_desc, ability_type = random.choice(TROOP_TEMPLATES)
                health = dmg + random.randint(0, 2)
                card = Card(name=name, cost=cost, damage=dmg, health=health, 
                           current_health=health, card_type='troop', ability=ability,
                           ability_desc=ability_desc, ability_type=ability_type)
                cards.append(card)
            
            for _ in range(num_spells):
                name, cost, dmg, spell_target, spell_effect, description = random.choice(SPELL_TEMPLATES)
                card = Card(name=name, cost=cost, damage=dmg, health=0, 
                           current_health=0, card_type='spell', spell_target=spell_target,
                           spell_effect=spell_effect, description=description)
                cards.append(card)
            
            return Deck(cards)
        
        deck1 = quick_deck()
        deck2 = quick_deck()
        
        player1 = Player('P1', deck1, champ1)
        player2 = Player('P2', deck2, champ2)
        
        if log_details:
            self._log(f"\n🎴 {champ1.name} ({champ1.starting_life} HP): {champ1.passive_description}")
            self._log(f"🎴 {champ2.name} ({champ2.starting_life} HP): {champ2.passive_description}")
            self._log(f"\n📊 Vida inicial: {player1.life} HP cada uno")
        
        # Simple simulation logic
        turn_count = 0
        max_turns = 50  # Prevent infinite loops
        
        while player1.life > 0 and player2.life > 0 and turn_count < max_turns:
            turn_count += 1
            
            if log_details:
                self._log(f"\n{'='*80}")
                self._log(f"🔄 TURNO {turn_count}")
                self._log(f"{'='*80}")
            
            # Simulate turn for player1
            if log_details:
                self._log(f"\n👤 Turno de {champ1.name}")
                self._log(f"💚 Vida: {player1.life} | 💎 Maná: {player1.mana}/{player1.max_mana} | 🎴 Mano: {len(player1.hand)} | ⚔️ Mesa: {len(player1.active_zone)}")
            if not self._simulate_turn(player1, player2, log_details):
                break
            
            if player2.life <= 0:
                if log_details:
                    self._log(f"\n💀 {champ2.name} ha sido derrotado!")
                break
            
            # Simulate turn for player2
            if log_details:
                self._log(f"\n👤 Turno de {champ2.name}")
                self._log(f"💚 Vida: {player2.life} | 💎 Maná: {player2.mana}/{player2.max_mana} | 🎴 Mano: {len(player2.hand)} | ⚔️ Mesa: {len(player2.active_zone)}")
            if not self._simulate_turn(player2, player1, log_details):
                break
            
            if player1.life <= 0:
                if log_details:
                    self._log(f"\n💀 {champ1.name} ha sido derrotado!")
        
        winner = champ1.name if player1.life > 0 else champ2.name
        
        if log_details:
            self._log(f"\n{'='*80}")
            self._log(f"🏆 FIN DE LA PARTIDA")
            self._log(f"{'='*80}")
            self._log(f"⭐ Ganador: {winner}")
            self._log(f"⏱️  Turnos totales: {turn_count}")
            self._log(f"💚 Vida final {champ1.name}: {player1.life} HP")
            self._log(f"💚 Vida final {champ2.name}: {player2.life} HP")
        
        result = {
            'champion1': champ1.name,
            'champion2': champ2.name,
            'winner': winner,
            'turns': turn_count,
            'final_life_p1': player1.life,
            'final_life_p2': player2.life
        }
        
        if verbose:
            print(f"{champ1.name} vs {champ2.name}: {winner} ganó en {turn_count} turnos")
        
        return result
    
    def _simulate_turn(self, active_player: Player, opponent: Player, log_details: bool = False) -> bool:
        """Simulate a single turn. Returns False if game should end."""
        # Draw card (Tacticus draws 2)
        draw_count = 2 if (active_player.champion and active_player.champion.ability_type == 'card_draw') else 1
        cards_drawn = 0
        for _ in range(draw_count):
            card = active_player.deck.draw()
            if card:
                active_player.hand.append(card)
                cards_drawn += 1
        
        if log_details and cards_drawn > 0:
            self._log(f"  📥 Robó {cards_drawn} carta(s)")
        
        # Increase mana
        active_player.max_mana = min(active_player.max_mana + 1, 10)
        active_player.mana = active_player.max_mana
        
        if log_details:
            self._log(f"  💎 Maná: {active_player.mana}")
        
        # Champion turn start abilities (Mystara, Lumina)
        if active_player.champion:
            if active_player.champion.ability_type == 'summon_token':
                # Mystara: summon 1/1 token
                token = Card(name='Token', cost=0, damage=1, health=1, current_health=1, card_type='troop')
                active_player.active_zone.append(token)
                if log_details:
                    self._log(f"  ✨ {active_player.champion.name}: Invocó un Token 1/1")
            elif active_player.champion.ability_type == 'heal_troops':
                # Lumina: heal all troops
                healed = 0
                for troop in active_player.active_zone:
                    old_health = troop.current_health
                    troop.current_health = min(troop.current_health + 1, troop.health)
                    if troop.current_health > old_health:
                        healed += 1
                if log_details and healed > 0:
                    self._log(f"  ✨ {active_player.champion.name}: Curó {healed} tropa(s)")
        
        # Play cards
        cards_played = 0
        if log_details:
            self._log(f"\n  🎯 Fase de juego:")
        for card in active_player.hand[:]:
            # Apply champion abilities to cost
            card_cost = card.cost
            discount = 0
            if active_player.champion and active_player.champion.ability_type == 'spell_discount' and card.card_type == 'spell':
                discount = active_player.champion.ability_value
                card_cost = max(1, card_cost - discount)
            
            if card_cost <= active_player.mana:
                active_player.hand.remove(card)
                active_player.mana -= card_cost
                
                if log_details:
                    cost_str = f"{card_cost}" if discount == 0 else f"{card_cost} (descuento -{discount})"
                    self._log(f"    🎴 Jugó {card.name} (Costo: {cost_str} maná)")
                
                if card.card_type == 'troop':
                    # Apply champion buffs (Brutus, Shadowblade, Sylvana)
                    buffs_applied = []
                    if active_player.champion:
                        if active_player.champion.ability_type == 'troop_buff_attack':
                            card.damage += active_player.champion.ability_value
                            buffs_applied.append(f"+{active_player.champion.ability_value} ATK")
                        elif active_player.champion.ability_type == 'cheap_troop_buff' and card.cost <= 3:
                            card.damage += 1
                            card.ability = 'Prisa'
                            buffs_applied.append("+1 ATK, Prisa")
                        elif active_player.champion.ability_type == 'big_troop_buff' and card.health >= 4:
                            card.damage += 1
                            card.health += 1
                            card.current_health += 1
                            buffs_applied.append("+1/+1")
                        elif active_player.champion.ability_type == 'all_furia':
                            card.ability = 'Furia'
                            buffs_applied.append("Furia")
                    
                    if log_details:
                        stats = f"{card.damage}/{card.current_health}"
                        buff_str = f" [{', '.join(buffs_applied)}]" if buffs_applied else ""
                        ability_str = f" ({card.ability})" if card.ability else ""
                        self._log(f"      ⚔️ Invocado: {stats}{ability_str}{buff_str}")
                    
                    active_player.active_zone.append(card)
                else:
                    # Simple spell logic: damage opponent
                    if card.spell_effect == 'damage':
                        opponent.life -= card.damage
                        if log_details:
                            self._log(f"      💥 Hechizo de daño: {card.damage} daño al oponente (Vida: {opponent.life})")
                    elif card.spell_effect == 'heal':
                        active_player.life += card.damage
                        if log_details:
                            self._log(f"      💚 Hechizo de curación: +{card.damage} vida (Vida: {active_player.life})")
                    elif card.spell_effect == 'destroy' and opponent.active_zone:
                        # Destroy random enemy troop
                        destroyed = opponent.active_zone.pop(0)
                        if log_details:
                            self._log(f"      ☠️ Hechizo de destrucción: Eliminó {destroyed.name}")
                    elif card.spell_effect == 'draw':
                        drawn_count = 0
                        for _ in range(card.damage):
                            drawn = active_player.deck.draw()
                            if drawn:
                                active_player.hand.append(drawn)
                                drawn_count += 1
                        if log_details:
                            self._log(f"      📚 Hechizo de robo: +{drawn_count} carta(s)")
                
                cards_played += 1
                
                if cards_played >= 4:  # Limit cards per turn
                    break
        
        # Attack with troops
        if log_details and active_player.active_zone:
            self._log(f"\n  ⚔️  Fase de ataque:")
        total_damage = 0
        for troop in active_player.active_zone[:]:
            # Check if can attack (Prisa or ready)
            can_attack = troop.ability == 'Prisa' or troop.ready
            if can_attack:
                damage = troop.damage
                # Furia doubles attacks
                furia_bonus = False
                if troop.ability == 'Furia':
                    damage *= 2
                    furia_bonus = True
                
                # Simple: attack face if no blockers or Ragnar
                opponent.life -= damage
                total_damage += damage
                troop.ready = True
                
                if log_details:
                    furia_str = " (x2 por Furia)" if furia_bonus else ""
                    self._log(f"    ⚔️ {troop.name} ({troop.damage}/{troop.current_health}) atacó por {damage} daño{furia_str}")
        
        if log_details and total_damage > 0:
            self._log(f"    💥 Daño total al oponente: {total_damage} (Vida oponente: {opponent.life})")
        
        # Mark all troops as ready for next turn
        for troop in active_player.active_zone:
            troop.ready = True
        
        return True
    
    def run_tournament(self, matches_per_pair: int = 10000):
        """Run a full tournament with all champion combinations."""
        import time
        start_time = time.time()
        
        print("🏆 INICIANDO TORNEO DE CAMPEONES 🏆\n")
        print("=" * 80)
        print(f"Simulando {matches_per_pair} partidas por cada combinación de campeones...")
        print("Esto tomará varios minutos. Por favor espera...")
        print()
        
        total_matches = len(CHAMPION_LIST) * (len(CHAMPION_LIST) - 1) * matches_per_pair // 2
        match_count = 0
        last_update = 0
        
        for i, champ1 in enumerate(CHAMPION_LIST):
            for champ2 in CHAMPION_LIST[i+1:]:
                # Track head-to-head
                h2h_wins = {champ1.name: 0, champ2.name: 0}
                
                for _ in range(matches_per_pair):
                    match_count += 1
                    result = self.simulate_match(champ1, champ2)
                    self.match_results.append(result)
                    
                    # Update stats
                    winner = result['winner']
                    loser = champ1.name if winner == champ2.name else champ2.name
                    
                    self.champion_stats[winner]['wins'] += 1
                    self.champion_stats[loser]['losses'] += 1
                    self.champion_stats[winner]['avg_game_length'].append(result['turns'])
                    self.champion_stats[loser]['avg_game_length'].append(result['turns'])
                    
                    h2h_wins[winner] += 1
                    
                    # Update every 5%
                    progress = match_count * 100 // total_matches
                    if progress >= last_update + 5:
                        elapsed = time.time() - start_time
                        rate = match_count / elapsed if elapsed > 0 else 0
                        remaining = (total_matches - match_count) / rate if rate > 0 else 0
                        print(f"Progreso: {match_count}/{total_matches} ({progress}%) | "
                              f"{rate:.0f} partidas/seg | ETA: {remaining/60:.1f} min")
                        last_update = progress
                
                # Print head-to-head result
                win_rate = h2h_wins[champ1.name] / matches_per_pair * 100
                print(f"  ✓ {champ1.name} vs {champ2.name}: {h2h_wins[champ1.name]}-{h2h_wins[champ2.name]} ({win_rate:.1f}%)")
        
        elapsed = time.time() - start_time
        print(f"\n✅ {total_matches} partidas simuladas en {elapsed/60:.1f} minutos")
        print(f"⚡ Velocidad promedio: {total_matches/elapsed:.0f} partidas/segundo\n")
    
    def print_statistics(self):
        """Print tournament statistics."""
        print("\n" + "=" * 80)
        print("📊 ESTADÍSTICAS DEL TORNEO - RESULTADOS FINALES")
        print("=" * 80 + "\n")
        
        # Sort by win rate
        sorted_champions = sorted(
            self.champion_stats.items(),
            key=lambda x: x[1]['wins'] / (x[1]['wins'] + x[1]['losses']) if (x[1]['wins'] + x[1]['losses']) > 0 else 0,
            reverse=True
        )
        
        print(f"{'Rank':<6} {'Campeón':<15} {'Victorias':<10} {'Derrotas':<10} {'WR%':<10} {'Turnos Avg':<12} {'Tier':<8}")
        print("-" * 80)
        
        for rank, (champ_name, stats) in enumerate(sorted_champions, 1):
            total_games = stats['wins'] + stats['losses']
            win_rate = (stats['wins'] / total_games * 100) if total_games > 0 else 0
            avg_turns = sum(stats['avg_game_length']) / len(stats['avg_game_length']) if stats['avg_game_length'] else 0
            
            # Determine tier
            if win_rate >= 55:
                tier = "S Tier"
            elif win_rate >= 50:
                tier = "A Tier"
            elif win_rate >= 45:
                tier = "B Tier"
            else:
                tier = "C Tier"
            
            print(f"{rank:<6} {champ_name:<15} {stats['wins']:<10} {stats['losses']:<10} {win_rate:<9.1f}% {avg_turns:<11.1f} {tier:<8}")
        
        print("\n" + "=" * 80)
        print("\n📈 ANÁLISIS DE VELOCIDAD:")
        print("-" * 80)
        
        # Sort by game length
        sorted_by_speed = sorted(
            self.champion_stats.items(),
            key=lambda x: sum(x[1]['avg_game_length']) / len(x[1]['avg_game_length']) if x[1]['avg_game_length'] else 999
        )
        
        print("\n🏃 MÁS RÁPIDOS (Aggro):")
        for champ_name, stats in sorted_by_speed[:3]:
            avg_turns = sum(stats['avg_game_length']) / len(stats['avg_game_length']) if stats['avg_game_length'] else 0
            print(f"   • {champ_name}: {avg_turns:.1f} turnos promedio")
        
        print("\n🐢 MÁS LENTOS (Control/Late Game):")
        for champ_name, stats in sorted_by_speed[-3:]:
            avg_turns = sum(stats['avg_game_length']) / len(stats['avg_game_length']) if stats['avg_game_length'] else 0
            print(f"   • {champ_name}: {avg_turns:.1f} turnos promedio")
        
        print("\n" + "=" * 80)
        
        # Best and worst performers
        best = sorted_champions[0]
        worst = sorted_champions[-1]
        
        best_wr = best[1]['wins'] / (best[1]['wins'] + best[1]['losses']) * 100
        worst_wr = worst[1]['wins'] / (worst[1]['wins'] + worst[1]['losses']) * 100
        
        print(f"\n🏆 MEJOR CAMPEÓN: {best[0]} ({best_wr:.1f}% WR)")
        print(f"💀 PEOR CAMPEÓN: {worst[0]} ({worst_wr:.1f}% WR)")
        print(f"📊 DIFERENCIA: {best_wr - worst_wr:.1f}%")
        print("\n" + "=" * 80)


class StrategyAnalyzer:
    """Analyzes game strategies and synergies."""
    
    def __init__(self):
        self.troop_stats = self._analyze_troops()
        self.spell_stats = self._analyze_spells()
    
    def _analyze_troops(self) -> Dict:
        """Analyze troop efficiency."""
        stats = {}
        
        for name, cost, damage, ability, ability_desc, ability_type in TROOP_TEMPLATES:
            # Calculate efficiency metrics
            health_avg = damage + 1  # Average health (damage + 0-2)
            total_stats = damage + health_avg
            efficiency = total_stats / cost if cost > 0 else 0
            
            stats[name] = {
                'cost': cost,
                'damage': damage,
                'health_avg': health_avg,
                'total_stats': total_stats,
                'efficiency': efficiency,
                'ability': ability,
                'ability_type': ability_type
            }
        
        return stats
    
    def _analyze_spells(self) -> Dict:
        """Analyze spell efficiency."""
        stats = {}
        
        for name, cost, damage, spell_target, spell_effect, description in SPELL_TEMPLATES:
            # Calculate damage per mana
            dpm = damage / cost if cost > 0 else 0
            
            stats[name] = {
                'cost': cost,
                'damage': damage,
                'target': spell_target,
                'effect': spell_effect,
                'dpm': dpm,
                'description': description
            }
        
        return stats
    
    def print_troop_analysis(self):
        """Print troop analysis."""
        print("\n" + "=" * 80)
        print("🛡️ ANÁLISIS DE TROPAS")
        print("=" * 80 + "\n")
        
        # Sort by efficiency
        sorted_troops = sorted(
            self.troop_stats.items(),
            key=lambda x: x[1]['efficiency'],
            reverse=True
        )
        
        print(f"{'Tropa':<18} {'Coste':<7} {'ATK':<6} {'HP Avg':<8} {'Total':<8} {'Eficiencia':<12} {'Habilidad':<20}")
        print("-" * 80)
        
        for name, stats in sorted_troops:
            ability = stats['ability'] if stats['ability'] else 'Ninguna'
            print(f"{name:<18} {stats['cost']:<7} {stats['damage']:<6} {stats['health_avg']:<8} "
                  f"{stats['total_stats']:<8} {stats['efficiency']:<11.2f} {ability:<20}")
        
        print("\n📌 NOTAS:")
        print("• Eficiencia = (ATK + HP Promedio) / Coste")
        print("• Las tropas con habilidades tienen valor adicional no reflejado en números")
        
    def print_spell_analysis(self):
        """Print spell analysis."""
        print("\n" + "=" * 80)
        print("⚡ ANÁLISIS DE HECHIZOS")
        print("=" * 80 + "\n")
        
        # Sort by damage per mana
        sorted_spells = sorted(
            self.spell_stats.items(),
            key=lambda x: x[1]['dpm'],
            reverse=True
        )
        
        print(f"{'Hechizo':<22} {'Coste':<7} {'Daño':<7} {'DPM':<8} {'Objetivo':<20}")
        print("-" * 80)
        
        for name, stats in sorted_spells:
            target = stats['target'] if stats['target'] else stats['effect']
            print(f"{name:<22} {stats['cost']:<7} {stats['damage']:<7} {stats['dpm']:<7.2f} {target:<20}")
        
        print("\n📌 NOTAS:")
        print("• DPM = Daño por Maná (mayor es mejor)")
        print("• Los hechizos de utilidad (curación, destrucción) no tienen DPM directo")
    
    def analyze_champion_synergies(self):
        """Analyze champion synergies with cards."""
        print("\n" + "=" * 80)
        print("🎭 ANÁLISIS DE SINERGIAS POR CAMPEÓN")
        print("=" * 80 + "\n")
        
        synergies = {
            "Arcanus": {
                "best_cards": ["Todos los hechizos", "Especialmente: Bola de Fuego (3→2), Destierro (4→3)"],
                "strategy": "Control con hechizos baratos",
                "best_troops": ["Tropas defensivas", "Guardian", "Wall"],
                "key_insight": "Con -1 coste, puede jugar hechizos caros muy temprano"
            },
            "Brutus": {
                "best_cards": ["Tropas numerosas", "Goblin", "Slingshot", "Wolf"],
                "strategy": "Aggro - Inundar el tablero",
                "best_troops": ["Todas las tropas se benefician", "Priorizar bajo coste"],
                "key_insight": "+1 ATK convierte tropas débiles en amenazas"
            },
            "Mystara": {
                "best_cards": ["Hechizos de AoE enemigos", "Pocas tropas grandes", "Buffs"],
                "strategy": "Token swarm - Acumular 1/1s",
                "best_troops": ["Tropas con Taunt para proteger tokens", "Guardian"],
                "key_insight": "Cada turno = +1 tropa gratis, domina late game"
            },
            "Shadowblade": {
                "best_cards": ["Tropas ≤3 coste", "Wolf", "Berserker", "Archer", "Knight"],
                "strategy": "Tempo - Golpes rápidos y letales",
                "best_troops": ["Bajo coste con Prisa natural", "Wolf se vuelve 3/2 con Prisa"],
                "key_insight": "Maximizar tropas de 3 maná o menos para doble beneficio"
            },
            "Lumina": {
                "best_cards": ["Tropas con alta vida", "Golem", "Knight", "Guardian"],
                "strategy": "Midrange - Tropas resistentes",
                "best_troops": ["Tropas con Taunt", "Benefician más de la curación"],
                "key_insight": "La curación constante hace trades favorables infinitos"
            },
            "Tacticus": {
                "best_cards": ["Combos complejos", "Hechizos situacionales", "Cartas caras"],
                "strategy": "Combo/Control - Buscar piezas clave",
                "best_troops": ["Variedad", "Necromancer para más recursos"],
                "key_insight": "Robas 2/turno = Encuentra combos más rápido"
            },
            "Ragnar": {
                "best_cards": ["TODAS las tropas", "Especialmente: Golem, Dragon, Mage"],
                "strategy": "Hyper Aggro - Todo ataca",
                "best_troops": ["Tropas grandes", "No necesitas Taunt ni defensa"],
                "key_insight": "40 HP compensan no poder bloquear, mata antes de morir"
            },
            "Sylvana": {
                "best_cards": ["Tropas ≥4 HP", "Knight (5/5→6/6)", "Golem (9/9→10/10)", "Dragon"],
                "strategy": "Big Creatures - Imbloqueables",
                "best_troops": ["Cartas caras con stats altas", "Evita tropas pequeñas"],
                "key_insight": "+1/+1 en tropas grandes es valor multiplicativo"
            }
        }
        
        for champ_name, analysis in synergies.items():
            print(f"🎭 {champ_name.upper()}")
            print(f"   Estrategia: {analysis['strategy']}")
            print(f"   Mejores Cartas: {', '.join(analysis['best_cards'])}")
            print(f"   Tropas Clave: {', '.join(analysis['best_troops'])}")
            print(f"   💡 Insight: {analysis['key_insight']}")
            print()
    
    def analyze_matchups(self):
        """Analyze theoretical matchups."""
        print("\n" + "=" * 80)
        print("⚔️ ANÁLISIS DE MATCHUPS TEÓRICOS")
        print("=" * 80 + "\n")
        
        matchups = {
            "Arcanus vs Brutus": "DESFAVORABLE - Brutus inunda muy rápido, hechizos no son suficientes",
            "Arcanus vs Mystara": "FAVORABLE - Hechizos AoE destruyen tokens baratos",
            "Arcanus vs Shadowblade": "NEUTRAL - Depende de si puede sobrevivir early game",
            "Arcanus vs Lumina": "DESFAVORABLE - Curación niega daño de hechizos",
            "Arcanus vs Tacticus": "NEUTRAL - Battle de recursos",
            "Arcanus vs Ragnar": "DESFAVORABLE - No puede bloquear, sufre mucho daño",
            "Arcanus vs Sylvana": "FAVORABLE - Hechizos de destrucción ignoran stats",
            
            "Brutus vs Mystara": "FAVORABLE - +1 ATK mata tokens eficientemente",
            "Brutus vs Shadowblade": "NEUTRAL - Ambos aggro, quien va primero gana",
            "Brutus vs Lumina": "DESFAVORABLE - Curación + Taunt frena aggro",
            "Brutus vs Tacticus": "FAVORABLE - Presión constante no da tiempo a combos",
            "Brutus vs Ragnar": "NEUTRAL - Race de daño puro",
            "Brutus vs Sylvana": "DESFAVORABLE - Tropas grandes bloquean pequeñas buffadas",
            
            "Mystara vs Shadowblade": "DESFAVORABLE - Tokens mueren antes de acumularse",
            "Mystara vs Lumina": "FAVORABLE - Late game vs Midrange",
            "Mystara vs Tacticus": "NEUTRAL - Ambos buscan late game",
            "Mystara vs Ragnar": "DESFAVORABLE - Ragnar mata antes de acumular",
            "Mystara vs Sylvana": "DESFAVORABLE - Tropas grandes matan tokens fácilmente",
            
            "Shadowblade vs Lumina": "NEUTRAL - Prisa ayuda a evitar bloqueos",
            "Shadowblade vs Tacticus": "FAVORABLE - Mata antes de que se active",
            "Shadowblade vs Ragnar": "DESFAVORABLE - Ragnar tiene más HP y daño",
            "Shadowblade vs Sylvana": "DESFAVORABLE - Tropas grandes sobreviven burst",
            
            "Lumina vs Tacticus": "FAVORABLE - Tropas resistentes + curación = sustain infinito",
            "Lumina vs Ragnar": "FAVORABLE - Curación niega daño, Ragnar no bloquea",
            "Lumina vs Sylvana": "NEUTRAL - Midrange vs Big, depende del draw",
            
            "Tacticus vs Ragnar": "DESFAVORABLE - No hay tiempo para combos",
            "Tacticus vs Sylvana": "NEUTRAL - Depende de las cartas que robe",
            
            "Ragnar vs Sylvana": "NEUTRAL - Daño puro vs Stats grandes"
        }
        
        for matchup, result in matchups.items():
            verdict = result.split(' - ')[0]
            reason = result.split(' - ')[1] if ' - ' in result else ''
            
            if "FAVORABLE" in verdict:
                emoji = "✅"
            elif "DESFAVORABLE" in verdict:
                emoji = "❌"
            else:
                emoji = "⚖️"
            
            print(f"{emoji} {matchup}: {verdict}")
            if reason:
                print(f"   └─ {reason}")
            print()
    
    def generate_tier_list(self):
        """Generate theoretical tier list."""
        print("\n" + "=" * 80)
        print("🏆 TIER LIST TEÓRICA DE CAMPEONES")
        print("=" * 80 + "\n")
        
        tiers = {
            "S Tier (Domina la meta)": [
                ("Brutus", "Aggro consistente, +1 ATK es universal, 35 HP sólido"),
                ("Lumina", "32 HP + curación = muy difícil de matar, domina midrange")
            ],
            "A Tier (Muy fuerte)": [
                ("Ragnar", "40 HP permite estrategia única, Furia en todo es devastador"),
                ("Shadowblade", "Burst damage increíble, puede cerrar juegos rápido"),
                ("Tacticus", "Ventaja de cartas es enorme, flexible en estrategias")
            ],
            "B Tier (Balanceado)": [
                ("Arcanus", "Hechizos baratos son buenos, pero limitado sin board"),
                ("Sylvana", "Tropas grandes son fuertes, pero lento y vulnerable a removal")
            ],
            "C Tier (Nicho)": [
                ("Mystara", "Necesita muchos turnos, vulnerable a aggro y AoE")
            ]
        }
        
        for tier, champions in tiers.items():
            print(f"\n📊 {tier}")
            print("-" * 70)
            for champ_name, reason in champions:
                print(f"   🎭 {champ_name}")
                print(f"      └─ {reason}")


def main():
    """Run full game analysis."""
    print("🎮 MINI TCG - ANÁLISIS COMPLETO Y SIMULACIÓN DE ESTRATEGIAS 🎮\n")
    print("=" * 80)
    
    # Tournament Simulation with 10000 matches
    print("\n🎲 SIMULACIÓN DE TORNEO MASIVO - 10,000 PARTIDAS POR MATCHUP")
    print("=" * 80)
    print("\n⚠️  ADVERTENCIA: Esto tomará varios minutos.")
    print("    Se simularán 280,000 partidas totales.")
    print("    Por favor NO interrumpas el proceso.\n")
    
    import time
    time.sleep(2)  # Give user time to read
    
    simulator = GameSimulator()
    simulator.run_tournament(matches_per_pair=10000)
    simulator.print_statistics()
    
    # Detailed matchup matrix
    print("\n" + "=" * 80)
    print("🔍 MATRIZ DE MATCHUPS DETALLADA")
    print("=" * 80)
    print("\nAnalizando head-to-head entre todos los campeones...\n")
    
    # Create matchup matrix
    matchup_matrix = {}
    for result in simulator.match_results:
        pair = tuple(sorted([result['champion1'], result['champion2']]))
        if pair not in matchup_matrix:
            matchup_matrix[pair] = {result['champion1']: 0, result['champion2']: 0}
        matchup_matrix[pair][result['winner']] += 1
    
    # Print ALL matchups sorted by win rate difference
    matchup_list = []
    for pair, results in matchup_matrix.items():
        total = sum(results.values())
        champ1, champ2 = pair
        wr1 = results[champ1] / total * 100
        wr2 = results[champ2] / total * 100
        diff = abs(wr1 - wr2)
        matchup_list.append((diff, champ1, champ2, wr1, wr2, results[champ1], results[champ2]))
    
    matchup_list.sort(reverse=True)
    
    print("\n📊 TODOS LOS MATCHUPS (ordenados por desequilibrio):\n")
    print(f"{'Matchup':<30} {'WR':<12} {'Score':<15} {'Desequilibrio':<15}")
    print("-" * 80)
    
    for diff, c1, c2, wr1, wr2, w1, w2 in matchup_list:
        if wr1 > wr2:
            indicator = "✅" if diff > 10 else "⚖️"
            print(f"{indicator} {c1:<12} > {c2:<12} {wr1:>5.1f}% {w1:>4}-{w2:<4} ({diff:>4.1f}% diff)")
        else:
            indicator = "✅" if diff > 10 else "⚖️"
            print(f"{indicator} {c2:<12} > {c1:<12} {wr2:>5.1f}% {w2:>4}-{w1:<4} ({diff:>4.1f}% diff)")
    
    # Save detailed results to file
    print("\n" + "=" * 80)
    print("💾 GUARDANDO RESULTADOS DETALLADOS...")
    print("=" * 80)
    
    import os
    os.makedirs('../data', exist_ok=True)
    with open('../data/SIMULACION_10000_RESULTADOS.txt', 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("       🎮 MINI TCG - RESULTADOS DE SIMULACIÓN MASIVA (10,000 PARTIDAS)\n")
        f.write("=" * 80 + "\n\n")
        
        # Champion stats
        sorted_champions = sorted(
            simulator.champion_stats.items(),
            key=lambda x: x[1]['wins'] / (x[1]['wins'] + x[1]['losses']) if (x[1]['wins'] + x[1]['losses']) > 0 else 0,
            reverse=True
        )
        
        f.write("\n📊 RANKING FINAL DE CAMPEONES:\n")
        f.write("-" * 80 + "\n")
        for rank, (champ_name, stats) in enumerate(sorted_champions, 1):
            total_games = stats['wins'] + stats['losses']
            win_rate = (stats['wins'] / total_games * 100) if total_games > 0 else 0
            avg_turns = sum(stats['avg_game_length']) / len(stats['avg_game_length']) if stats['avg_game_length'] else 0
            f.write(f"{rank}. {champ_name}: {win_rate:.2f}% WR ({stats['wins']}-{stats['losses']}) | {avg_turns:.1f} turnos avg\n")
        
        # All matchups
        f.write("\n\n📋 MATRIZ COMPLETA DE MATCHUPS:\n")
        f.write("-" * 80 + "\n")
        for diff, c1, c2, wr1, wr2, w1, w2 in matchup_list:
            if wr1 > wr2:
                f.write(f"{c1} vs {c2}: {wr1:.1f}% ({w1}-{w2}) | Diff: {diff:.1f}%\n")
            else:
                f.write(f"{c2} vs {c1}: {wr2:.1f}% ({w2}-{w1}) | Diff: {diff:.1f}%\n")
    
    print("✅ Resultados guardados en: data/SIMULACION_10000_RESULTADOS.txt")
    print("\n" + "=" * 80)
    print("🏁 ANÁLISIS COMPLETO FINALIZADO - 280,000 PARTIDAS")
    print("=" * 80)
    print("\n📚 Archivos disponibles:")
    print("   • ESTRATEGIAS_AVANZADAS.txt - Guías de construcción de mazos")
    print("   • data/SIMULACION_10000_RESULTADOS.txt - Resultados detallados (10K)")
    print("   • CAMPEONES.txt - Información de campeones")
    print("\n⚔️  ¡Usa estos datos para dominar el juego!")
    print("=" * 80)


if __name__ == '__main__':
    main()
