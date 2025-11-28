"""
Game Simulator with Detailed Logging
Runs simulations with complete action logs for deep statistical analysis
"""

import random
import sys
from pathlib import Path
from typing import List, Tuple, Dict
from datetime import datetime

# Imports
if __name__ == '__main__':
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from src.models import Player, Card, Deck
    from src.champions import CHAMPION_LIST, Champion, get_champion_by_name
    from src.cards import TROOP_TEMPLATES, SPELL_TEMPLATES
else:
    from .models import Player, Card, Deck
    from .champions import CHAMPION_LIST, Champion, get_champion_by_name
    from .cards import TROOP_TEMPLATES, SPELL_TEMPLATES


class LoggedGameSimulator:
    """Simulator que registra todas las acciones en archivos de log."""
    
    def __init__(self, num_games: int = 100):
        self.num_games = num_games
        self.log_file = None
        self.stats_file = None
        self.detailed_stats = {
            'total_games': 0,
            'by_champion': {},
            'by_matchup': {},
            'turn_distribution': {},
            'action_counts': {
                'cards_played': 0,
                'troops_summoned': 0,
                'spells_cast': 0,
                'attacks': 0,
                'damage_dealt': 0,
                'healing': 0,
                'cards_drawn': 0,
                'tokens_created': 0
            },
            'ability_triggers': {},
            'game_endings': {}
        }
        
    def setup_logging(self):
        """Configura archivos de logging."""
        import os
        from pathlib import Path
        
        # Determinar la ruta correcta
        if __name__ == '__main__':
            data_path = Path(__file__).parent.parent / 'data'
        else:
            data_path = Path('../data')
        
        data_path.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = open(data_path / f'GAME_LOGS_{timestamp}.txt', 'w', encoding='utf-8')
        self.stats_file = open(data_path / f'STATS_{timestamp}.txt', 'w', encoding='utf-8')
        
        self._log("="*100)
        self._log("🎮 MINI TCG - REGISTRO DETALLADO DE SIMULACIONES")
        self._log("="*100)
        self._log(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self._log(f"Total de partidas a simular: {self.num_games}")
        self._log("="*100)
        
    def _log(self, message: str):
        """Escribe en el archivo de log."""
        if self.log_file:
            self.log_file.write(message + '\n')
            self.log_file.flush()
    
    def _log_stats(self, message: str):
        """Escribe en el archivo de estadísticas."""
        if self.stats_file:
            self.stats_file.write(message + '\n')
            self.stats_file.flush()
    
    def quick_deck(self, size=40, spell_ratio=0.3):
        """Crea un mazo rápido."""
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
    
    def simulate_match(self, champ1: Champion, champ2: Champion, game_number: int) -> Dict:
        """Simula una partida con logging completo."""
        self._log("\n" + "="*100)
        self._log(f"⚔️  PARTIDA #{game_number}: {champ1.name} vs {champ2.name}")
        self._log("="*100)
        
        # Setup
        deck1 = self.quick_deck()
        deck2 = self.quick_deck()
        player1 = Player('P1', deck1, champ1)
        player2 = Player('P2', deck2, champ2)
        
        self._log(f"\n🎴 {champ1.name} ({champ1.starting_life} HP): {champ1.passive_description}")
        self._log(f"🎴 {champ2.name} ({champ2.starting_life} HP): {champ2.passive_description}")
        
        # Game stats tracking
        game_stats = {
            'game_id': game_number,
            'champion1': champ1.name,
            'champion2': champ2.name,
            'actions_p1': {'cards': 0, 'troops': 0, 'spells': 0, 'attacks': 0, 'damage': 0},
            'actions_p2': {'cards': 0, 'troops': 0, 'spells': 0, 'attacks': 0, 'damage': 0},
            'ability_triggers': {'p1': 0, 'p2': 0},
            'turns': 0
        }
        
        turn_count = 0
        max_turns = 50
        
        while player1.life > 0 and player2.life > 0 and turn_count < max_turns:
            turn_count += 1
            self._log(f"\n{'='*100}")
            self._log(f"🔄 TURNO {turn_count}")
            self._log(f"{'='*100}")
            
            # Player 1 turn
            self._log(f"\n👤 Turno de {champ1.name}")
            self._log(f"   💚 Vida: {player1.life} | 💎 Maná: {player1.mana}/{player1.max_mana} | 🎴 Mano: {len(player1.hand)} | ⚔️ Mesa: {len(player1.active_zone)}")
            
            p1_actions = self._simulate_turn_logged(player1, player2, champ1.name)
            game_stats['actions_p1']['cards'] += p1_actions['cards']
            game_stats['actions_p1']['troops'] += p1_actions['troops']
            game_stats['actions_p1']['spells'] += p1_actions['spells']
            game_stats['actions_p1']['attacks'] += p1_actions['attacks']
            game_stats['actions_p1']['damage'] += p1_actions['damage']
            game_stats['ability_triggers']['p1'] += p1_actions['abilities']
            
            if player2.life <= 0:
                self._log(f"\n💀 {champ2.name} ha sido eliminado!")
                self._log(f"   Vida final: {player2.life} HP")
                break
            
            # Player 2 turn
            self._log(f"\n👤 Turno de {champ2.name}")
            self._log(f"   💚 Vida: {player2.life} | 💎 Maná: {player2.mana}/{player2.max_mana} | 🎴 Mano: {len(player2.hand)} | ⚔️ Mesa: {len(player2.active_zone)}")
            
            p2_actions = self._simulate_turn_logged(player2, player1, champ2.name)
            game_stats['actions_p2']['cards'] += p2_actions['cards']
            game_stats['actions_p2']['troops'] += p2_actions['troops']
            game_stats['actions_p2']['spells'] += p2_actions['spells']
            game_stats['actions_p2']['attacks'] += p2_actions['attacks']
            game_stats['actions_p2']['damage'] += p2_actions['damage']
            game_stats['ability_triggers']['p2'] += p2_actions['abilities']
            
            if player1.life <= 0:
                self._log(f"\n💀 {champ1.name} ha sido eliminado!")
                self._log(f"   Vida final: {player1.life} HP")
                break
        
        # Game end
        winner = champ1.name if player1.life > 0 else champ2.name
        loser = champ2.name if winner == champ1.name else champ1.name
        
        game_stats['winner'] = winner
        game_stats['loser'] = loser
        game_stats['turns'] = turn_count
        game_stats['final_life_winner'] = player1.life if winner == champ1.name else player2.life
        game_stats['final_life_loser'] = player2.life if winner == champ1.name else player1.life
        
        self._log(f"\n{'='*100}")
        self._log(f"🏆 FIN DE LA PARTIDA")
        self._log(f"{'='*100}")
        self._log(f"⭐ GANADOR: {winner}")
        self._log(f"⏱️  Turnos: {turn_count}")
        self._log(f"💚 Vida final {champ1.name}: {player1.life} HP")
        self._log(f"💚 Vida final {champ2.name}: {player2.life} HP")
        self._log(f"\n📊 Estadísticas {champ1.name}:")
        self._log(f"   Cartas jugadas: {game_stats['actions_p1']['cards']} | Tropas: {game_stats['actions_p1']['troops']} | Hechizos: {game_stats['actions_p1']['spells']}")
        self._log(f"   Ataques: {game_stats['actions_p1']['attacks']} | Daño total: {game_stats['actions_p1']['damage']}")
        self._log(f"   Habilidades activadas: {game_stats['ability_triggers']['p1']}")
        self._log(f"\n📊 Estadísticas {champ2.name}:")
        self._log(f"   Cartas jugadas: {game_stats['actions_p2']['cards']} | Tropas: {game_stats['actions_p2']['troops']} | Hechizos: {game_stats['actions_p2']['spells']}")
        self._log(f"   Ataques: {game_stats['actions_p2']['attacks']} | Daño total: {game_stats['actions_p2']['damage']}")
        self._log(f"   Habilidades activadas: {game_stats['ability_triggers']['p2']}")
        
        return game_stats
    
    def _simulate_turn_logged(self, active_player: Player, opponent: Player, champ_name: str) -> Dict:
        """Simula un turno con logging detallado."""
        actions = {'cards': 0, 'troops': 0, 'spells': 0, 'attacks': 0, 'damage': 0, 'abilities': 0}
        
        # Draw
        draw_count = 2 if (active_player.champion and active_player.champion.ability_type == 'card_draw') else 1
        if draw_count == 2:
            actions['abilities'] += 1
        
        cards_drawn = 0
        for _ in range(draw_count):
            card = active_player.deck.draw()
            if card:
                active_player.hand.append(card)
                cards_drawn += 1
        
        if cards_drawn > 0:
            self._log(f"   📥 Robó {cards_drawn} carta(s)")
        
        # Mana
        active_player.max_mana = min(active_player.max_mana + 1, 10)
        active_player.mana = active_player.max_mana
        self._log(f"   💎 Maná disponible: {active_player.mana}")
        
        # Champion abilities (start of turn)
        if active_player.champion:
            if active_player.champion.ability_type == 'summon_token':
                token = Card(name='Token', cost=0, damage=1, health=1, current_health=1, card_type='troop')
                active_player.active_zone.append(token)
                self._log(f"   ✨ {champ_name}: Invocó Token 1/1")
                actions['abilities'] += 1
                actions['troops'] += 1
            elif active_player.champion.ability_type == 'heal_troops':
                healed = 0
                for troop in active_player.active_zone:
                    old_health = troop.current_health
                    troop.current_health = min(troop.current_health + 1, troop.health)
                    if troop.current_health > old_health:
                        healed += 1
                if healed > 0:
                    self._log(f"   ✨ {champ_name}: Curó {healed} tropa(s)")
                    actions['abilities'] += 1
        
        # Play cards
        self._log(f"\n   🎯 FASE DE JUEGO:")
        cards_played = 0
        for card in active_player.hand[:]:
            card_cost = card.cost
            discount = 0
            
            if active_player.champion and active_player.champion.ability_type == 'spell_discount' and card.card_type == 'spell':
                discount = active_player.champion.ability_value
                card_cost = max(1, card_cost - discount)
                if discount > 0:
                    actions['abilities'] += 1
            
            if card_cost <= active_player.mana:
                active_player.hand.remove(card)
                active_player.mana -= card_cost
                actions['cards'] += 1
                
                cost_str = f"{card_cost}" if discount == 0 else f"{card_cost} (descuento -{discount})"
                self._log(f"      🎴 Jugó {card.name} (Costo: {cost_str} maná)")
                
                if card.card_type == 'troop':
                    actions['troops'] += 1
                    buffs = []
                    
                    if active_player.champion:
                        if active_player.champion.ability_type == 'troop_buff_attack':
                            card.damage += active_player.champion.ability_value
                            buffs.append(f"+{active_player.champion.ability_value} ATK")
                            actions['abilities'] += 1
                        elif active_player.champion.ability_type == 'cheap_troop_buff' and card.cost <= 3:
                            card.damage += 1
                            card.ability = 'Prisa'
                            buffs.append("+1 ATK, Prisa")
                            actions['abilities'] += 1
                        elif active_player.champion.ability_type == 'big_troop_buff' and card.health >= 4:
                            card.damage += 1
                            card.health += 1
                            card.current_health += 1
                            buffs.append("+1/+1")
                            actions['abilities'] += 1
                        elif active_player.champion.ability_type == 'all_furia':
                            card.ability = 'Furia'
                            buffs.append("Furia")
                            actions['abilities'] += 1
                    
                    buff_str = f" [{', '.join(buffs)}]" if buffs else ""
                    ability_str = f" ({card.ability})" if card.ability else ""
                    self._log(f"         ⚔️ {card.damage}/{card.current_health}{ability_str}{buff_str}")
                    
                    active_player.active_zone.append(card)
                else:
                    actions['spells'] += 1
                    if card.spell_effect == 'damage':
                        opponent.life -= card.damage
                        actions['damage'] += card.damage
                        self._log(f"         💥 Daño: {card.damage} al oponente (Vida oponente: {opponent.life})")
                    elif card.spell_effect == 'heal':
                        active_player.life += card.damage
                        self._log(f"         💚 Curación: +{card.damage} vida (Vida: {active_player.life})")
                    elif card.spell_effect == 'destroy' and opponent.active_zone:
                        destroyed = opponent.active_zone.pop(0)
                        self._log(f"         ☠️ Destrucción: Eliminó {destroyed.name}")
                    elif card.spell_effect == 'draw':
                        drawn = 0
                        for _ in range(card.damage):
                            d = active_player.deck.draw()
                            if d:
                                active_player.hand.append(d)
                                drawn += 1
                        self._log(f"         📚 Robo: +{drawn} carta(s)")
                
                cards_played += 1
                if cards_played >= 4:
                    break
        
        if cards_played == 0:
            self._log(f"      (No jugó cartas)")
        
        # Attack
        if active_player.active_zone:
            self._log(f"\n   ⚔️  FASE DE ATAQUE:")
            total_damage = 0
            attack_count = 0
            
            for troop in active_player.active_zone[:]:
                can_attack = troop.ability == 'Prisa' or troop.ready
                if can_attack:
                    damage = troop.damage
                    furia = False
                    if troop.ability == 'Furia':
                        damage *= 2
                        furia = True
                    
                    opponent.life -= damage
                    total_damage += damage
                    attack_count += 1
                    troop.ready = True
                    actions['attacks'] += 1
                    actions['damage'] += damage
                    
                    furia_str = " (x2 Furia)" if furia else ""
                    self._log(f"      ⚔️ {troop.name} ({troop.damage}/{troop.current_health}) → {damage} daño{furia_str}")
            
            if total_damage > 0:
                self._log(f"      💥 Daño total: {total_damage} | Vida oponente: {opponent.life}")
            else:
                self._log(f"      (No atacó)")
        
        # Mark ready
        for troop in active_player.active_zone:
            troop.ready = True
        
        return actions
    
    def run_simulation(self, champ1_name: str, champ2_name: str):
        """Ejecuta simulación entre dos campeones."""
        champ1 = get_champion_by_name(champ1_name)
        champ2 = get_champion_by_name(champ2_name)
        
        if not champ1 or not champ2:
            print("❌ Error: Campeón no encontrado")
            return
        
        self.setup_logging()
        
        print(f"\n🎮 Iniciando {self.num_games} partidas entre {champ1.name} y {champ2.name}")
        print("📝 Logs detallados en: data/GAME_LOGS_*.txt")
        print("📊 Estadísticas en: data/STATS_*.txt\n")
        
        results = {champ1.name: 0, champ2.name: 0}
        all_game_stats = []
        
        for i in range(1, self.num_games + 1):
            game_stats = self.simulate_match(champ1, champ2, i)
            all_game_stats.append(game_stats)
            results[game_stats['winner']] += 1
            
            if i % 10 == 0:
                print(f"   Progreso: {i}/{self.num_games} partidas ({i*100//self.num_games}%)")
        
        # Análisis estadístico
        self.analyze_statistics(all_game_stats, champ1.name, champ2.name)
        
        print(f"\n✅ Simulación completada!")
        print(f"📊 Resultados: {champ1.name} {results[champ1.name]} - {results[champ2.name]} {champ2.name}")
        print(f"📈 WR {champ1.name}: {results[champ1.name]/self.num_games*100:.1f}%")
        
        if self.log_file:
            self.log_file.close()
        if self.stats_file:
            self.stats_file.close()
    
    def analyze_statistics(self, games: List[Dict], champ1: str, champ2: str):
        """Analiza estadísticas de las partidas."""
        self._log_stats("\n" + "="*100)
        self._log_stats("📊 ANÁLISIS ESTADÍSTICO DETALLADO")
        self._log_stats("="*100)
        
        # Resultados generales
        wins_c1 = sum(1 for g in games if g['winner'] == champ1)
        wins_c2 = sum(1 for g in games if g['winner'] == champ2)
        
        self._log_stats(f"\n🏆 RESULTADOS GENERALES:")
        self._log_stats(f"   Total de partidas: {len(games)}")
        self._log_stats(f"   {champ1}: {wins_c1} victorias ({wins_c1/len(games)*100:.1f}%)")
        self._log_stats(f"   {champ2}: {wins_c2} victorias ({wins_c2/len(games)*100:.1f}%)")
        
        # Duración de partidas
        avg_turns = sum(g['turns'] for g in games) / len(games)
        min_turns = min(g['turns'] for g in games)
        max_turns = max(g['turns'] for g in games)
        
        self._log_stats(f"\n⏱️  DURACIÓN DE PARTIDAS:")
        self._log_stats(f"   Promedio: {avg_turns:.1f} turnos")
        self._log_stats(f"   Mínimo: {min_turns} turnos")
        self._log_stats(f"   Máximo: {max_turns} turnos")
        
        # Acciones por partida
        self._log_stats(f"\n🎯 ACCIONES PROMEDIO POR PARTIDA:")
        
        avg_cards_c1 = sum(g['actions_p1']['cards'] for g in games) / len(games)
        avg_troops_c1 = sum(g['actions_p1']['troops'] for g in games) / len(games)
        avg_spells_c1 = sum(g['actions_p1']['spells'] for g in games) / len(games)
        avg_attacks_c1 = sum(g['actions_p1']['attacks'] for g in games) / len(games)
        avg_damage_c1 = sum(g['actions_p1']['damage'] for g in games) / len(games)
        avg_abilities_c1 = sum(g['ability_triggers']['p1'] for g in games) / len(games)
        
        self._log_stats(f"\n   {champ1}:")
        self._log_stats(f"      Cartas jugadas: {avg_cards_c1:.1f}")
        self._log_stats(f"      Tropas invocadas: {avg_troops_c1:.1f}")
        self._log_stats(f"      Hechizos lanzados: {avg_spells_c1:.1f}")
        self._log_stats(f"      Ataques realizados: {avg_attacks_c1:.1f}")
        self._log_stats(f"      Daño total infligido: {avg_damage_c1:.1f}")
        self._log_stats(f"      Habilidades activadas: {avg_abilities_c1:.1f}")
        
        avg_cards_c2 = sum(g['actions_p2']['cards'] for g in games) / len(games)
        avg_troops_c2 = sum(g['actions_p2']['troops'] for g in games) / len(games)
        avg_spells_c2 = sum(g['actions_p2']['spells'] for g in games) / len(games)
        avg_attacks_c2 = sum(g['actions_p2']['attacks'] for g in games) / len(games)
        avg_damage_c2 = sum(g['actions_p2']['damage'] for g in games) / len(games)
        avg_abilities_c2 = sum(g['ability_triggers']['p2'] for g in games) / len(games)
        
        self._log_stats(f"\n   {champ2}:")
        self._log_stats(f"      Cartas jugadas: {avg_cards_c2:.1f}")
        self._log_stats(f"      Tropas invocadas: {avg_troops_c2:.1f}")
        self._log_stats(f"      Hechizos lanzados: {avg_spells_c2:.1f}")
        self._log_stats(f"      Ataques realizados: {avg_attacks_c2:.1f}")
        self._log_stats(f"      Daño total infligido: {avg_damage_c2:.1f}")
        self._log_stats(f"      Habilidades activadas: {avg_abilities_c2:.1f}")
        
        # Análisis por victoria/derrota
        c1_wins = [g for g in games if g['winner'] == champ1]
        c2_wins = [g for g in games if g['winner'] == champ2]
        
        if c1_wins:
            avg_turns_c1_wins = sum(g['turns'] for g in c1_wins) / len(c1_wins)
            self._log_stats(f"\n📈 {champ1} - Victorias:")
            self._log_stats(f"      Turnos promedio: {avg_turns_c1_wins:.1f}")
        
        if c2_wins:
            avg_turns_c2_wins = sum(g['turns'] for g in c2_wins) / len(c2_wins)
            self._log_stats(f"\n📈 {champ2} - Victorias:")
            self._log_stats(f"      Turnos promedio: {avg_turns_c2_wins:.1f}")
        
        self._log_stats(f"\n{'='*100}\n")


def main():
    """Función principal."""
    print("🎮 MINI TCG - SIMULADOR CON LOGGING DETALLADO\n")
    print("="*80)
    
    # Configuración
    print("\n📝 Este simulador guarda logs COMPLETOS de cada partida")
    print("⚠️  ADVERTENCIA: Los archivos de log pueden ser MUY grandes (varios MB)")
    print()
    
    # Ejemplo: Simular 100 partidas entre dos campeones
    simulator = LoggedGameSimulator(num_games=100)
    
    # Puedes cambiar los campeones aquí
    simulator.run_simulation("Ragnar", "Mystara")
    
    print("\n✅ Proceso completado!")
    print("📂 Revisa la carpeta data/ para ver los logs y estadísticas")


if __name__ == '__main__':
    main()
