"""
Massive Game Simulator with Complete Logging
Simula 10,000 partidas de TODOS los matchups posibles guardando logs completos
"""

import random
import sys
from pathlib import Path
from typing import Dict, List
from datetime import datetime
import time

# Imports
sys.path.insert(0, str(Path(__file__).parent))
from src.models import Player, Card, Deck
from src.champions import CHAMPION_LIST, Champion
from src.cards import TROOP_TEMPLATES, SPELL_TEMPLATES


class MassiveSimulator:
    """Simulador masivo con logging completo de todas las partidas."""
    
    def __init__(self, games_per_matchup: int | None = None, total_target: int = 1_000_000):
        # If games_per_matchup is None, compute it to reach approximately total_target games
        self.total_target = total_target
        if games_per_matchup is None:
            import math
            num_matchups = len(CHAMPION_LIST) * (len(CHAMPION_LIST) - 1) // 2
            games_per_matchup = max(1, math.ceil(self.total_target / max(1, num_matchups)))
        self.games_per_matchup: int = int(games_per_matchup)
        self.log_file = None
        self.summary_file = None  # CSV compacto por partida
        self._summary_path = None
        self._card_stats_path = None
        self.total_games = 0
        self.game_count = 0
        # Estadísticas agregadas por carta
        self.card_stats: Dict[str, Dict[str, int]] = {}
        
    def setup_logging(self):
        """Configura el archivo de logging masivo."""
        data_path = Path('data')
        data_path.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = data_path / f'MASSIVE_LOGS_{timestamp}.txt'
        summary_path = data_path / f'MASSIVE_SUMMARY_{timestamp}.csv'
        card_stats_path = data_path / f'MASSIVE_CARD_STATS_{timestamp}.csv'
        
        self.log_file = open(log_path, 'w', encoding='utf-8', buffering=8192*16)  # Buffer grande
        self.summary_file = open(summary_path, 'w', encoding='utf-8', buffering=8192)
        self._summary_path = summary_path
        self._card_stats_path = card_stats_path
        
        self._log("="*120)
        self._log("🎮 MINI TCG - SIMULACIÓN MASIVA CON LOGS COMPLETOS")
        self._log("="*120)
        self._log(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        # Calcular partidas por matchup si no se proporcionó
        num_matchups = len(CHAMPION_LIST) * (len(CHAMPION_LIST) - 1) // 2
        if self.games_per_matchup is None:
            import math
            self.games_per_matchup = max(1, math.ceil(self.total_target / max(1, num_matchups)))
        self._log(f"Partidas por matchup: {self.games_per_matchup}")
        
        # Calcular total de partidas
        self.total_games = num_matchups * self.games_per_matchup
        
        self._log(f"Matchups totales: {num_matchups}")
        self._log(f"Objetivo de partidas: {self.total_target:,}")
        self._log(f"TOTAL DE PARTIDAS (ajustado): {self.total_games:,}")
        self._log(f"⚠️  ADVERTENCIA: Este archivo será EXTREMADAMENTE grande (varios GB)")
        self._log("="*120)
        
        # Encabezado CSV compacto por partida
        if self.summary_file:
            header = [
                'matchup','game_num','winner','turns',
                'p1_cards','p1_troops','p1_spells','p1_attacks','p1_damage','p1_draws','p1_tokens','p1_heals','p1_destroys',
                'p2_cards','p2_troops','p2_spells','p2_attacks','p2_damage','p2_draws','p2_tokens','p2_heals','p2_destroys',
                'p1_avg_cost','p1_spell_ratio','p2_avg_cost','p2_spell_ratio'
            ]
            self.summary_file.write(','.join(header) + '\n')
            self.summary_file.flush()
        
        return log_path
    
    def _log(self, message: str):
        """Escribe en el archivo de log."""
        if self.log_file:
            self.log_file.write(message + '\n')
    
    def flush_log(self):
        """Fuerza el flush del buffer."""
        if self.log_file:
            self.log_file.flush()
        if self.summary_file:
            self.summary_file.flush()

    def _inc_card_stat(self, name: str, key: str, amount: int = 1):
        """Incrementa contadores agregados por carta."""
        if not name:
            return
        d = self.card_stats.setdefault(name, {'drawn': 0, 'played': 0, 'destroyed': 0})
        d[key] = d.get(key, 0) + amount
    
    def quick_deck(self, size=40, spell_ratio=0.3):
        """Crea un mazo aleatorio rápido."""
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
    
    def log_deck_composition(self, deck: Deck, player_name: str):
        """Registra la composición completa del mazo."""
        self._log(f"\n   📦 Mazo de {player_name}:")
        
        troops = [c for c in deck.cards if c.card_type == 'troop']
        spells = [c for c in deck.cards if c.card_type == 'spell']
        
        self._log(f"      Tropas ({len(troops)}):")
        troop_counts = {}
        for t in troops:
            key = f"{t.name} ({t.cost}⚡ {t.damage}/{t.health})"
            if t.ability:
                key += f" [{t.ability}]"
            troop_counts[key] = troop_counts.get(key, 0) + 1
        
        for troop, count in sorted(troop_counts.items()):
            self._log(f"         • {troop} x{count}")
        
        self._log(f"      Hechizos ({len(spells)}):")
        spell_counts = {}
        for s in spells:
            key = f"{s.name} ({s.cost}⚡)"
            spell_counts[key] = spell_counts.get(key, 0) + 1
        
        for spell, count in sorted(spell_counts.items()):
            self._log(f"         • {spell} x{count}")

    def _deck_stats(self, deck: Deck) -> Dict[str, float]:
        """Calcula métricas compactas del mazo."""
        if not deck.cards:
            return {'avg_cost': 0.0, 'spell_ratio': 0.0}
        avg_cost = sum(c.cost for c in deck.cards) / len(deck.cards)
        spells = sum(1 for c in deck.cards if c.card_type == 'spell')
        return {'avg_cost': round(avg_cost, 3), 'spell_ratio': round(spells / len(deck.cards), 3)}
    
    def simulate_match(self, champ1: Champion, champ2: Champion, game_num: int) -> Dict:
        """Simula UNA partida con logging ultra-detallado."""
        self.game_count += 1
        
        self._log("\n" + "="*120)
        self._log(f"⚔️  PARTIDA #{game_num} ({self.game_count}/{self.total_games}) - {champ1.name} vs {champ2.name}")
        self._log("="*120)
        
        # Setup
        deck1 = self.quick_deck()
        deck2 = self.quick_deck()
        
        player1 = Player('P1', deck1, champ1)
        player2 = Player('P2', deck2, champ2)
        
        self._log(f"\n🎴 CAMPEONES:")
        self._log(f"   {champ1.name} ({champ1.starting_life} HP): {champ1.passive_description}")
        self._log(f"   {champ2.name} ({champ2.starting_life} HP): {champ2.passive_description}")
        
        # Log deck composition
        self.log_deck_composition(deck1, champ1.name)
        self.log_deck_composition(deck2, champ2.name)
        
        # Game tracking
        turn_count = 0
        max_turns = 50
        game_actions = {
            'p1': {'cards': 0, 'troops': 0, 'spells': 0, 'attacks': 0, 'damage': 0, 'draws': 0, 'tokens': 0, 'heals': 0, 'destroys': 0},
            'p2': {'cards': 0, 'troops': 0, 'spells': 0, 'attacks': 0, 'damage': 0, 'draws': 0, 'tokens': 0, 'heals': 0, 'destroys': 0}
        }

        # Deck stats for CSV summary
        deck1_stats = self._deck_stats(deck1)
        deck2_stats = self._deck_stats(deck2)
        
        # Game loop
        while player1.life > 0 and player2.life > 0 and turn_count < max_turns:
            turn_count += 1
            
            self._log(f"\n{'='*120}")
            self._log(f"🔄 TURNO {turn_count}")
            self._log(f"{'='*120}")
            self._log(f"Estado: {champ1.name} {player1.life}❤️  vs  {champ2.name} {player2.life}❤️")
            
            # Player 1 turn
            self._log(f"\n👤 TURNO DE {champ1.name}")
            self._log(f"   Estado: {player1.life}❤️ | {player1.mana}/{player1.max_mana}💎 | {len(player1.hand)}🎴 mano | {len(player1.active_zone)}⚔️ mesa | {len(player1.deck.cards)}📚 mazo")
            
            actions1 = self._simulate_turn_detailed(player1, player2, champ1.name, champ2.name)
            for key in game_actions['p1']:
                game_actions['p1'][key] += actions1[key]
            
            if player2.life <= 0:
                self._log(f"\n💀 {champ2.name} HA SIDO ELIMINADO!")
                self._log(f"   Vida final: {player2.life} HP")
                break
            
            # Player 2 turn
            self._log(f"\n👤 TURNO DE {champ2.name}")
            self._log(f"   Estado: {player2.life}❤️ | {player2.mana}/{player2.max_mana}💎 | {len(player2.hand)}🎴 mano | {len(player2.active_zone)}⚔️ mesa | {len(player2.deck.cards)}📚 mazo")
            
            actions2 = self._simulate_turn_detailed(player2, player1, champ2.name, champ1.name)
            for key in game_actions['p2']:
                game_actions['p2'][key] += actions2[key]
            
            if player1.life <= 0:
                self._log(f"\n💀 {champ1.name} HA SIDO ELIMINADO!")
                self._log(f"   Vida final: {player1.life} HP")
                break
        
        # Game end
        winner = champ1.name if player1.life > 0 else champ2.name
        loser = champ2.name if winner == champ1.name else champ1.name
        
        self._log(f"\n{'='*120}")
        self._log(f"🏆 FIN DE LA PARTIDA #{game_num}")
        self._log(f"{'='*120}")
        self._log(f"⭐ GANADOR: {winner}")
        self._log(f"⏱️  Duración: {turn_count} turnos")
        self._log(f"💚 Vida final:")
        self._log(f"   {champ1.name}: {player1.life} HP")
        self._log(f"   {champ2.name}: {player2.life} HP")
        
        self._log(f"\n📊 ESTADÍSTICAS DETALLADAS:")
        self._log(f"\n   {champ1.name}:")
        self._log(f"      Cartas robadas: {game_actions['p1']['draws']}")
        self._log(f"      Cartas jugadas: {game_actions['p1']['cards']}")
        self._log(f"      Tropas invocadas: {game_actions['p1']['troops']}")
        self._log(f"      Hechizos lanzados: {game_actions['p1']['spells']}")
        self._log(f"      Ataques realizados: {game_actions['p1']['attacks']}")
        self._log(f"      Daño total infligido: {game_actions['p1']['damage']}")
        
        self._log(f"\n   {champ2.name}:")
        self._log(f"      Cartas robadas: {game_actions['p2']['draws']}")
        self._log(f"      Cartas jugadas: {game_actions['p2']['cards']}")
        self._log(f"      Tropas invocadas: {game_actions['p2']['troops']}")
        self._log(f"      Hechizos lanzados: {game_actions['p2']['spells']}")
        self._log(f"      Ataques realizados: {game_actions['p2']['attacks']}")
        self._log(f"      Daño total infligido: {game_actions['p2']['damage']}")
        
        # Flush periódicamente
        if self.game_count % 10 == 0:
            self.flush_log()
        
        # Escribir línea compacta al CSV
        if self.summary_file:
            row = [
                f"{champ1.name} vs {champ2.name}", str(game_num), winner, str(turn_count),
                str(game_actions['p1']['cards']), str(game_actions['p1']['troops']), str(game_actions['p1']['spells']), str(game_actions['p1']['attacks']), str(game_actions['p1']['damage']), str(game_actions['p1']['draws']), str(game_actions['p1']['tokens']), str(game_actions['p1']['heals']), str(game_actions['p1']['destroys']),
                str(game_actions['p2']['cards']), str(game_actions['p2']['troops']), str(game_actions['p2']['spells']), str(game_actions['p2']['attacks']), str(game_actions['p2']['damage']), str(game_actions['p2']['draws']), str(game_actions['p2']['tokens']), str(game_actions['p2']['heals']), str(game_actions['p2']['destroys']),
                f"{deck1_stats['avg_cost']}", f"{deck1_stats['spell_ratio']}", f"{deck2_stats['avg_cost']}", f"{deck2_stats['spell_ratio']}"
            ]
            self.summary_file.write(','.join(row) + '\n')

        return {
            'winner': winner,
            'loser': loser,
            'turns': turn_count,
            'actions_p1': game_actions['p1'],
            'actions_p2': game_actions['p2']
        }
    
    def _simulate_turn_detailed(self, active_player: Player, opponent: Player, 
                                 active_name: str, opponent_name: str) -> Dict:
        """Simula un turno con logging ultra-detallado."""
        actions = {'cards': 0, 'troops': 0, 'spells': 0, 'attacks': 0, 'damage': 0, 'draws': 0, 'tokens': 0, 'heals': 0, 'destroys': 0}
        
        # FASE 1: ROBO
        self._log(f"\n   📥 FASE DE ROBO:")
        draw_count = 2 if (active_player.champion and active_player.champion.ability_type == 'card_draw') else 1
        
        if draw_count == 2:
            self._log(f"      ✨ Habilidad {active_name}: Roba 2 cartas")
        
        for i in range(draw_count):
            card = active_player.deck.draw()
            if card:
                active_player.hand.append(card)
                actions['draws'] += 1
                self._inc_card_stat(card.name, 'drawn', 1)
                card_type = "🗡️ " if card.card_type == 'troop' else "⚡"
                self._log(f"      → Robó: {card_type} {card.name} ({card.cost}💎)")
            else:
                self._log(f"      → Mazo vacío, no puede robar")
        
        # FASE 2: MANÁ
        active_player.max_mana = min(active_player.max_mana + 1, 10)
        active_player.mana = active_player.max_mana
        self._log(f"\n   💎 FASE DE MANÁ: {active_player.mana} disponible")
        
        # FASE 3: HABILIDADES PASIVAS
        if active_player.champion:
            if active_player.champion.ability_type == 'summon_token':
                token = Card(name='Token', cost=0, damage=1, health=1, current_health=1, card_type='troop')
                active_player.active_zone.append(token)
                self._log(f"\n   ✨ HABILIDAD PASIVA:")
                self._log(f"      {active_name}: Invocó Token 1/1")
                actions['troops'] += 1
                actions['tokens'] += 1
            elif active_player.champion.ability_type == 'heal_troops':
                healed_count = 0
                healed_list = []
                for troop in active_player.active_zone:
                    old_hp = troop.current_health
                    troop.current_health = min(troop.current_health + 1, troop.health)
                    if troop.current_health > old_hp:
                        healed_count += 1
                        healed_list.append(f"{troop.name} ({old_hp}→{troop.current_health})")
                
                if healed_count > 0:
                    self._log(f"\n   ✨ HABILIDAD PASIVA:")
                    self._log(f"      {active_name}: Curación")
                    for heal in healed_list:
                        self._log(f"         • {heal}")
                    actions['heals'] += healed_count
        
        # FASE 4: JUGAR CARTAS
        self._log(f"\n   🎯 FASE DE JUEGO:")
        self._log(f"      Mano actual ({len(active_player.hand)} cartas):")
        for i, card in enumerate(active_player.hand, 1):
            card_symbol = "🗡️ " if card.card_type == 'troop' else "⚡"
            self._log(f"         {i}. {card_symbol} {card.name} ({card.cost}💎)")
        
        cards_played = 0
        played_this_turn = []
        
        for card in active_player.hand[:]:
            card_cost = card.cost
            discount = 0
            
            # Descuento de hechizos (Arcanus)
            if active_player.champion and active_player.champion.ability_type == 'spell_discount' and card.card_type == 'spell':
                discount = active_player.champion.ability_value
                card_cost = max(1, card_cost - discount)
            
            if card_cost <= active_player.mana:
                active_player.hand.remove(card)
                active_player.mana -= card_cost
                actions['cards'] += 1
                self._inc_card_stat(card.name, 'played', 1)
                
                cost_display = f"{card_cost}💎" if discount == 0 else f"{card_cost}💎 (descuento -{discount})"
                
                if card.card_type == 'troop':
                    actions['troops'] += 1
                    
                    # Aplicar buffs de campeón
                    buffs = []
                    original_atk = card.damage
                    original_hp = card.health
                    
                    if active_player.champion:
                        if active_player.champion.ability_type == 'troop_buff_attack':
                            card.damage += active_player.champion.ability_value
                            buffs.append(f"+{active_player.champion.ability_value} ATK")
                        elif active_player.champion.ability_type == 'cheap_troop_buff' and card.cost <= 3:
                            card.damage += 1
                            card.ability = 'Prisa'
                            buffs.append("+1 ATK, Prisa")
                        elif active_player.champion.ability_type == 'big_troop_buff' and card.health >= 4:
                            card.damage += 1
                            card.health += 1
                            card.current_health += 1
                            buffs.append("+1/+1")
                        elif active_player.champion.ability_type == 'all_furia':
                            card.ability = 'Furia'
                            buffs.append("Furia")
                    
                    buff_display = f" {buffs}" if buffs else ""
                    ability_display = f" [{card.ability}]" if card.ability else ""
                    stats_change = ""
                    if card.damage != original_atk or card.health != original_hp:
                        stats_change = f" ({original_atk}/{original_hp} → {card.damage}/{card.current_health})"
                    
                    self._log(f"      → Jugó: 🗡️  {card.name} {cost_display}{stats_change}{ability_display}{buff_display}")
                    active_player.active_zone.append(card)
                    played_this_turn.append(card.name)
                    
                else:  # Spell
                    actions['spells'] += 1
                    
                    if card.spell_effect == 'damage':
                        opponent.life -= card.damage
                        actions['damage'] += card.damage
                        self._log(f"      → Jugó: ⚡ {card.name} {cost_display}")
                        self._log(f"         💥 {card.damage} daño a {opponent_name} (Vida: {opponent.life}❤️)")
                    elif card.spell_effect == 'heal':
                        active_player.life += card.damage
                        self._log(f"      → Jugó: ⚡ {card.name} {cost_display}")
                        self._log(f"         💚 +{card.damage} vida (Vida: {active_player.life}❤️)")
                    elif card.spell_effect == 'destroy' and opponent.active_zone:
                        destroyed = opponent.active_zone.pop(0)
                        self._log(f"      → Jugó: ⚡ {card.name} {cost_display}")
                        self._log(f"         ☠️ Destruyó: {destroyed.name} ({destroyed.damage}/{destroyed.current_health})")
                        actions['destroys'] += 1
                        self._inc_card_stat(destroyed.name, 'destroyed', 1)
                    elif card.spell_effect == 'draw':
                        drawn_names = []
                        for _ in range(card.damage):
                            d = active_player.deck.draw()
                            if d:
                                active_player.hand.append(d)
                                drawn_names.append(d.name)
                                actions['draws'] += 1
                                self._inc_card_stat(d.name, 'drawn', 1)
                        self._log(f"      → Jugó: ⚡ {card.name} {cost_display}")
                        self._log(f"         📚 Robó: {', '.join(drawn_names) if drawn_names else 'mazo vacío'}")
                    
                    played_this_turn.append(card.name)
                
                cards_played += 1
                if cards_played >= 4:
                    break
        
        if cards_played == 0:
            self._log(f"      (No jugó ninguna carta)")
        
        self._log(f"      Maná restante: {active_player.mana}💎")
        
        # FASE 5: ATAQUE
        if active_player.active_zone:
            self._log(f"\n   ⚔️  FASE DE ATAQUE:")
            self._log(f"      Tropas en mesa:")
            for i, troop in enumerate(active_player.active_zone, 1):
                ready_status = "✓ listo" if (troop.ability == 'Prisa' or troop.ready) else "✗ no listo"
                ability_str = f" [{troop.ability}]" if troop.ability else ""
                self._log(f"         {i}. {troop.name} {troop.damage}/{troop.current_health}{ability_str} - {ready_status}")
            
            total_damage = 0
            attack_count = 0
            
            for troop in active_player.active_zone[:]:
                can_attack = troop.ability == 'Prisa' or troop.ready
                if can_attack:
                    damage = troop.damage
                    is_furia = False
                    
                    if troop.ability == 'Furia':
                        damage *= 2
                        is_furia = True
                    
                    opponent.life -= damage
                    total_damage += damage
                    attack_count += 1
                    troop.ready = True
                    actions['attacks'] += 1
                    actions['damage'] += damage
                    
                    furia_display = " (x2 por Furia)" if is_furia else ""
                    self._log(f"      → {troop.name} ({troop.damage}/{troop.current_health}) atacó por {damage} daño{furia_display}")
            
            if total_damage > 0:
                self._log(f"      💥 DAÑO TOTAL: {total_damage} a {opponent_name}")
                self._log(f"      ❤️  Vida de {opponent_name}: {opponent.life}")
            else:
                self._log(f"      (Ninguna tropa pudo atacar)")
        else:
            self._log(f"\n   ⚔️  FASE DE ATAQUE: (Sin tropas en mesa)")
        
        # Marcar tropas como listas
        for troop in active_player.active_zone:
            troop.ready = True
        
        return actions
    
    def run_massive_simulation(self):
        """Ejecuta la simulación masiva completa."""
        print(f"\n🎮 SIMULADOR MASIVO - {self.total_games:,} PARTIDAS CON LOGS COMPLETOS")
        print("="*100)
        
        log_path = self.setup_logging()
        print(f"\n📝 Archivo de logs: {log_path}")
        print(f"⚠️  ADVERTENCIA: Este proceso generará un archivo GIGANTE (varios GB)")
        print(f"⚠️  TIEMPO ESTIMADO: 30-60 minutos o más")
        print(f"\n¿Deseas continuar? (Presiona Ctrl+C para cancelar en 5 segundos)\n")
        
        try:
            time.sleep(5)
        except KeyboardInterrupt:
            print("\n❌ Simulación cancelada")
            return
        
        print(f"\n🚀 INICIANDO SIMULACIÓN MASIVA...\n")
        
        start_time = time.time()
        results = {}
        
        # Iterar sobre todos los matchups posibles
        matchup_num = 0
        total_matchups = len(CHAMPION_LIST) * (len(CHAMPION_LIST) - 1) // 2
        
        for i, champ1 in enumerate(CHAMPION_LIST):
            for champ2 in CHAMPION_LIST[i+1:]:
                matchup_num += 1
                matchup_key = f"{champ1.name} vs {champ2.name}"
                
                print(f"\n{'='*100}")
                print(f"⚔️  MATCHUP {matchup_num}/{total_matchups}: {matchup_key}")
                print(f"{'='*100}")
                
                self._log(f"\n\n{'#'*120}")
                self._log(f"{'#'*120}")
                self._log(f"⚔️  MATCHUP {matchup_num}/{total_matchups}: {matchup_key}")
                self._log(f"⚔️  Simulando {self.games_per_matchup} partidas...")
                self._log(f"{'#'*120}")
                self._log(f"{'#'*120}")
                
                results[matchup_key] = {champ1.name: 0, champ2.name: 0, 'turns': []}
                
                for game_num in range(1, self.games_per_matchup + 1):
                    result = self.simulate_match(champ1, champ2, game_num)
                    results[matchup_key][result['winner']] += 1
                    results[matchup_key]['turns'].append(result['turns'])
                    
                    if game_num % 100 == 0:
                        elapsed = time.time() - start_time
                        games_done = self.game_count
                        rate = games_done / elapsed
                        remaining = (self.total_games - games_done) / rate if rate > 0 else 0
                        
                        print(f"   Progreso: {game_num}/{self.games_per_matchup} | "
                              f"Total: {games_done:,}/{self.total_games:,} ({games_done*100//self.total_games}%) | "
                              f"Velocidad: {rate:.1f} p/s | ETA: {remaining/60:.1f} min")
                
                # Resumen del matchup
                wins_c1 = results[matchup_key][champ1.name]
                wins_c2 = results[matchup_key][champ2.name]
                avg_turns = sum(results[matchup_key]['turns']) / len(results[matchup_key]['turns'])
                
                print(f"\n   ✅ Completado: {champ1.name} {wins_c1}-{wins_c2} {champ2.name} ({wins_c1/self.games_per_matchup*100:.1f}% WR)")
                print(f"   ⏱️  Duración promedio: {avg_turns:.1f} turnos")
        
        # Finalizar
        elapsed = time.time() - start_time
        
        self._log(f"\n\n{'='*120}")
        self._log(f"🏁 SIMULACIÓN MASIVA COMPLETADA")
        self._log(f"{'='*120}")
        self._log(f"Total de partidas: {self.total_games:,}")
        self._log(f"Tiempo total: {elapsed/60:.1f} minutos")
        self._log(f"Velocidad promedio: {self.total_games/elapsed:.1f} partidas/segundo")
        self._log(f"{'='*120}")
        
        if self.log_file:
            self.log_file.close()
        if self.summary_file:
            self.summary_file.close()

        # Guardar CSV agregado de estadísticas por carta
        if self._card_stats_path:
            with open(self._card_stats_path, 'w', encoding='utf-8') as f:
                f.write('card,drawn,played,destroyed\n')
                for name, stats in sorted(self.card_stats.items()):
                    f.write(f"{name},{stats.get('drawn',0)},{stats.get('played',0)},{stats.get('destroyed',0)}\n")
        
        print(f"\n\n{'='*100}")
        print(f"✅ SIMULACIÓN MASIVA COMPLETADA")
        print(f"{'='*100}")
        print(f"📊 Total de partidas: {self.total_games:,}")
        print(f"⏱️  Tiempo total: {elapsed/60:.1f} minutos ({elapsed/3600:.2f} horas)")
        print(f"⚡ Velocidad promedio: {self.total_games/elapsed:.1f} partidas/segundo")
        print(f"\n📝 Archivo de logs: {log_path}")
        if self._summary_path:
            print(f"🧾 Resumen CSV: {self._summary_path}")
        if self._card_stats_path:
            print(f"🧮 Estadísticas de cartas: {self._card_stats_path}")
        
        # Tamaño del archivo
        file_size = log_path.stat().st_size
        size_mb = file_size / (1024 * 1024)
        size_gb = file_size / (1024 * 1024 * 1024)
        
        if size_gb >= 1:
            print(f"📦 Tamaño del archivo: {size_gb:.2f} GB ({file_size:,} bytes)")
        else:
            print(f"📦 Tamaño del archivo: {size_mb:.2f} MB ({file_size:,} bytes)")
        
        print(f"{'='*100}\n")


def main():
    """Función principal."""
    print("\n" + "="*100)
    print("🎮 MINI TCG - SIMULADOR MASIVO CON LOGS COMPLETOS")
    print("="*100)
    
    # Por requerimiento: simular ~1,000,000 partidas en total (ajustado por matchups)
    simulator = MassiveSimulator()
    simulator.run_massive_simulation()


if __name__ == '__main__':
    main()
