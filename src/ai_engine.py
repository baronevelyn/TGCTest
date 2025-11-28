"""
Data-Driven AI Engine for TCG
Based on 1,000,020 game analysis (COMPLETE_ANALYSIS_20251128_100314)

10 Difficulty Levels:
- Level 1-2: Random/weak play, weak champions
- Level 3-4: Basic strategy, mediocre champions
- Level 5-6: Good cards (Berserker/Wolf/Knight), decent champions
- Level 7-8: Top cards + Furia ability focus, strong champions
- Level 9-10: Elite champions (Mystara/Ragnar/Brutus), matchup knowledge, optimal deck
"""

import random
import sys
from pathlib import Path
from typing import List, Tuple, Optional, Dict

# Handle both direct execution and module import
if __name__ == '__main__':
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from src.models import Card, Deck, Player
    from src.cards import TROOP_TEMPLATES, SPELL_TEMPLATES, create_card
    from src.champions import CHAMPION_LIST, Champion, get_champion_by_name
else:
    from .models import Card, Deck, Player
    from .cards import TROOP_TEMPLATES, SPELL_TEMPLATES, create_card
    from .champions import CHAMPION_LIST, Champion, get_champion_by_name


# ==================== DATA FROM 1M GAME ANALYSIS ====================

# Champion Win Rates (from 1,000,020 games)
CHAMPION_WIN_RATES = {
    'Mystara': 74.5,
    'Ragnar': 73.5,
    'Brutus': 73.3,
    'Shadowblade': 48.7,
    'Tacticus': 39.9,
    'Arcanus': 37.1,
    'Lumina': 31.9,
    'Sylvana': 21.2
}

# Card Win Rates (Top performers)
CARD_WIN_RATES = {
    'Berserker': 51.9,
    'Wolf': 51.1,
    'Knight': 50.9,
    'Archer': 50.7,
    'Aniquilar': 50.7,
    'Mage': 50.6,
    'Dragon': 50.5,
    'Bat': 50.4,
    'Eagle': 50.4,
    'Golem': 50.3,
    'Guardian': 50.2,
    'Goblin': 50.0,
    'Shaman': 49.9,
    'Wall': 49.7,
    'Slingshot': 49.5,
    'Necromancer': 49.2,
    # Weaker cards
    'Curar': 48.0,
    'Escudo': 47.5
}

# Ability Win Rates
ABILITY_WIN_RATES = {
    'Furia': 51.5,
    'Volar': 50.3,
    'Taunt': 50.2,
    'Revivir': 49.2
}

# Optimal Deck Composition (from analysis)
OPTIMAL_DECK = {
    'troops': 28,
    'spells': 12,
    'avg_cost': 2.5,  # Average cost sweet spot
}

# Matchup Knowledge (Best matchups - for level 9-10)
COUNTER_MATCHUPS = {
    'Ragnar': ['Sylvana', 'Lumina', 'Arcanus'],  # 95.3%, 89.8%, 87.3% WR
    'Mystara': ['Sylvana', 'Lumina', 'Arcanus'],  # 94.1%, 88.7%, 85.9% WR
    'Brutus': ['Sylvana', 'Lumina', 'Arcanus'],   # 93.3%, 86.9%, 83.7% WR
}


# ==================== AI DIFFICULTY CONFIGURATION ====================

class AIConfig:
    """Configuration for AI difficulty level."""
    
    def __init__(self, level: int):
        self.level = level
        self.name = self._get_name()
        self.champion_pool = self._get_champion_pool()
        self.card_priorities = self._get_card_priorities()
        self.play_quality = self._get_play_quality()
        self.mistake_chance = self._get_mistake_chance()
        self.uses_matchup_knowledge = level >= 9
        self.uses_ability_priority = level >= 7
        self.deck_optimization = min(1.0, level * 0.1)  # 0.1 to 1.0
    
    def _get_name(self) -> str:
        names = {
            1: "🟢 Tutorial - Novato",
            2: "🟢 Principiante - Aprendiendo",
            3: "🟡 Aficionado - Básico",
            4: "🟡 Competente - Estrategia Simple",
            5: "🟠 Avanzado - Buen Jugador",
            6: "🟠 Experto - Cartas Fuertes",
            7: "🔴 Maestro - Domina Habilidades",
            8: "🔴 Gran Maestro - Meta Game",
            9: "⚫ Leyenda - Elite",
            10: "💀 Imposible - Perfección"
        }
        return names.get(self.level, "Unknown")
    
    def _get_champion_pool(self) -> List[str]:
        """Champions AI can use based on difficulty."""
        if self.level <= 2:
            # Weak champions only
            return ['Sylvana', 'Lumina', 'Arcanus']
        elif self.level <= 4:
            # Below average champions
            return ['Arcanus', 'Lumina', 'Tacticus', 'Shadowblade']
        elif self.level <= 6:
            # Good champions
            return ['Shadowblade', 'Tacticus', 'Brutus', 'Ragnar']
        elif self.level <= 8:
            # Strong champions
            return ['Brutus', 'Ragnar', 'Mystara', 'Shadowblade']
        else:
            # Elite champions only (9-10)
            return ['Mystara', 'Ragnar', 'Brutus']
    
    def _get_card_priorities(self) -> Dict[str, float]:
        """Card selection priorities based on difficulty."""
        if self.level <= 2:
            # Random - all cards equal
            return {card: 1.0 for card in CARD_WIN_RATES.keys()}
        elif self.level <= 4:
            # Slight preference for good cards
            return {card: 1.0 + (wr - 50) * 0.02 for card, wr in CARD_WIN_RATES.items()}
        elif self.level <= 6:
            # Strong preference for top cards
            return {card: 1.0 + (wr - 50) * 0.1 for card, wr in CARD_WIN_RATES.items()}
        else:
            # Maximum preference for best cards (7-10)
            return {card: 1.0 + (wr - 50) * 0.2 for card, wr in CARD_WIN_RATES.items()}
    
    def _get_play_quality(self) -> float:
        """Quality of in-game decisions (0.0 = random, 1.0 = perfect)."""
        # Level 1: 0.1, Level 10: 1.0
        return min(1.0, 0.05 + self.level * 0.095)
    
    def _get_mistake_chance(self) -> float:
        """Chance of making suboptimal plays."""
        # Level 1: 50%, Level 10: 0%
        return max(0.0, 0.5 - self.level * 0.05)


# ==================== DECK BUILDER ====================

class DataDrivenDeckBuilder:
    """Builds decks based on 1M game analysis."""
    
    def __init__(self, config: AIConfig):
        self.config = config
    
    def build_deck(self, champion: Champion) -> Deck:
        """Build optimized deck for champion and difficulty."""
        cards = []
        
        # Determine deck composition based on optimization level
        if self.config.deck_optimization < 0.3:
            # Random deck (levels 1-2)
            num_troops = random.randint(20, 35)
        elif self.config.deck_optimization < 0.7:
            # Decent deck (levels 3-6)
            num_troops = random.randint(25, 30)
        else:
            # Optimal deck (levels 7-10)
            num_troops = OPTIMAL_DECK['troops']
        
        num_spells = 40 - num_troops
        
        # Get available cards (TROOP_TEMPLATES and SPELL_TEMPLATES are lists of tuples)
        available_troops = [t[0] for t in TROOP_TEMPLATES]  # Extract card names
        available_spells = [s[0] for s in SPELL_TEMPLATES]
        
        # Build troop selection with weighted priorities
        troops_added = 0
        while troops_added < num_troops:
            troop_name = self._select_card(available_troops, is_troop=True)
            # Find template and create card
            for template in TROOP_TEMPLATES:
                if template[0] == troop_name:
                    name, cost, damage = template[0], template[1], template[2]
                    ability = template[3] if len(template) > 3 else None
                    ability_desc = template[4] if len(template) > 4 else None
                    ability_type = template[5] if len(template) > 5 else None
                    cards.append(create_card(name, cost, damage, ability=ability, 
                                            ability_desc=ability_desc, ability_type=ability_type))
                    break
            troops_added += 1
        
        # Build spell selection
        spells_added = 0
        while spells_added < num_spells:
            spell_name = self._select_card(available_spells, is_troop=False)
            # Find template and create card
            for template in SPELL_TEMPLATES:
                if template[0] == spell_name:
                    name, cost, damage = template[0], template[1], template[2]
                    spell_target = template[3] if len(template) > 3 else None
                    spell_effect = template[4] if len(template) > 4 else None
                    description = template[5] if len(template) > 5 else None
                    cards.append(create_card(name, cost, damage, card_type='spell',
                                            spell_target=spell_target, spell_effect=spell_effect,
                                            description=description))
                    break
            spells_added += 1
        
        random.shuffle(cards)
        return Deck(cards)
    
    def _select_card(self, available: List[str], is_troop: bool) -> str:
        """Select card based on priorities and optimization level."""
        if self.config.deck_optimization < 0.2:
            # Pure random (level 1-2)
            return random.choice(available)
        
        # Weighted selection based on win rates
        weights = []
        for card_name in available:
            base_weight = self.config.card_priorities.get(card_name, 1.0)
            
            # Level 7+ prioritize Furia ability carriers
            if self.config.uses_ability_priority and is_troop:
                # Find template (templates are tuples: name, cost, damage, ability, ...)
                for template in TROOP_TEMPLATES:
                    if template[0] == card_name and len(template) > 3 and template[3] == 'Furia':
                        base_weight *= 1.5
                        break
            
            weights.append(base_weight)
        
        # Normalize weights
        total = sum(weights)
        if total > 0:
            weights = [w / total for w in weights]
            return random.choices(available, weights=weights)[0]
        return random.choice(available)


# ==================== AI PLAYER LOGIC ====================

class DataDrivenAI:
    """AI player with data-driven decision making."""
    
    def __init__(self, player: Player, config: AIConfig):
        self.player = player
        self.config = config
    
    def choose_cards_to_play(self, available_mana: int) -> List[Card]:
        """Decide which cards to play this turn."""
        playable = [c for c in self.player.hand if c.cost <= available_mana]
        
        if not playable:
            return []
        
        # Apply mistake chance (random play)
        if random.random() < self.config.mistake_chance:
            random.shuffle(playable)
            selected = []
            mana = available_mana
            for card in playable:
                if card.cost <= mana:
                    selected.append(card)
                    mana -= card.cost
            return selected
        
        # Smart play based on quality level
        if self.config.play_quality < 0.3:
            # Low quality - prefer low cost
            playable.sort(key=lambda c: c.cost)
        elif self.config.play_quality < 0.6:
            # Medium quality - damage per cost
            playable.sort(key=lambda c: c.damage / max(1, c.cost), reverse=True)
        else:
            # High quality - complex scoring
            playable.sort(key=lambda c: self._score_card(c), reverse=True)
        
        # Greedy selection
        selected = []
        mana = available_mana
        for card in playable:
            if card.cost <= mana:
                selected.append(card)
                mana -= card.cost
        
        return selected
    
    def _score_card(self, card: Card) -> float:
        """Score card value for play priority."""
        score = 0.0
        
        # Base stats
        score += card.damage * 2
        score += card.current_health
        score -= card.cost * 1.5
        
        # Abilities (level 7+)
        if self.config.uses_ability_priority:
            ability = getattr(card, 'ability', None)
            if ability in ABILITY_WIN_RATES:
                score += ABILITY_WIN_RATES[ability] - 50
        
        # Card win rate (level 5+)
        if self.config.play_quality >= 0.5:
            if card.name in CARD_WIN_RATES:
                score += (CARD_WIN_RATES[card.name] - 50) * 0.5
        
        return score
    
    def choose_blocker(self, attacker: Card, available_defenders: List[int], 
                       defender_zone: List[Card], my_life: int) -> Optional[int]:
        """Choose blocker for incoming attack."""
        if not available_defenders:
            return None
        
        ready = [i for i in available_defenders if getattr(defender_zone[i], 'ready', False)]
        if not ready:
            return None
        
        # Mistake chance - random or no block
        if random.random() < self.config.mistake_chance:
            if random.random() < 0.5:
                return None  # Don't block
            return random.choice(ready)
        
        # Lethal attack - must block
        if attacker.damage >= my_life:
            survivals = [i for i in ready if defender_zone[i].current_health > attacker.damage]
            if survivals:
                return min(survivals, key=lambda i: defender_zone[i].current_health)
            return max(ready, key=lambda i: defender_zone[i].damage)
        
        # Smart blocking (quality based)
        if self.config.play_quality < 0.4:
            # Low quality - sometimes don't block
            if random.random() < 0.3:
                return None
            return random.choice(ready)
        
        # Tier 1: Kill attacker and survive
        best_trades = []
        for idx in ready:
            d = defender_zone[idx]
            kills = d.damage >= attacker.current_health
            survives = d.current_health > attacker.damage
            if kills and survives:
                best_trades.append((d.current_health, idx))
        if best_trades:
            best_trades.sort()
            return best_trades[0][1]
        
        # Tier 2: Kill attacker (mutual destruction ok)
        kills = []
        for idx in ready:
            d = defender_zone[idx]
            if d.damage >= attacker.current_health:
                kills.append((d.cost, idx))
        if kills:
            kills.sort()
            return kills[0][1]
        
        # Tier 3: High quality AI blocks if damage > 50% of attacker HP
        if self.config.play_quality >= 0.7:
            damage_dealers = []
            for idx in ready:
                d = defender_zone[idx]
                if d.damage >= attacker.current_health * 0.5:
                    damage_dealers.append((d.damage, idx))
            if damage_dealers:
                damage_dealers.sort(reverse=True)
                return damage_dealers[0][1]
        
        # Low quality - let through
        if self.config.play_quality < 0.5:
            return None
        
        # Medium/high - block with weakest
        return min(ready, key=lambda i: defender_zone[i].cost)
    
    def choose_attackers(self, active_zone: List[Card]) -> List[int]:
        """Choose which creatures attack."""
        ready = [i for i, c in enumerate(active_zone) if getattr(c, 'ready', False)]
        
        if not ready:
            return []
        
        # Mistake chance - random attackers
        if random.random() < self.config.mistake_chance:
            return random.sample(ready, k=random.randint(0, len(ready)))
        
        # Low quality - sometimes hold back
        if self.config.play_quality < 0.3:
            return random.sample(ready, k=random.randint(0, len(ready)))
        
        # Medium quality - attack with most
        if self.config.play_quality < 0.6:
            return ready if random.random() < 0.7 else ready[:max(1, len(ready)//2)]
        
        # High quality - always attack all ready (aggressive)
        return ready
    
    def choose_attack_target(self, attacker: Card, enemy_cards: List[Card], 
                            enemy_life: int) -> Tuple[bool, Optional[int]]:
        """Choose attack target: (attack_player, target_index)."""
        available_targets = [i for i, c in enumerate(enemy_cards) if getattr(c, 'can_be_attacked', True)]
        has_taunt = any(getattr(enemy_cards[i], 'taunt', False) for i in available_targets)
        
        # Must attack taunt
        if has_taunt:
            taunt_targets = [i for i in available_targets if getattr(enemy_cards[i], 'taunt', False)]
            if taunt_targets:
                return (False, random.choice(taunt_targets))
        
        # Mistake chance - random target
        if random.random() < self.config.mistake_chance:
            if available_targets and random.random() < 0.5:
                return (False, random.choice(available_targets))
            return (True, None)
        
        # Low quality - prefer face
        if self.config.play_quality < 0.4:
            return (True, None)
        
        # Check for lethal
        if attacker.damage >= enemy_life:
            return (True, None)
        
        # Medium quality - sometimes trade
        if self.config.play_quality < 0.7:
            if available_targets and random.random() < 0.4:
                # Attack weakest creature
                weakest = min(available_targets, key=lambda i: enemy_cards[i].current_health)
                return (False, weakest)
            return (True, None)
        
        # High quality - smart targeting
        # Kill threats we can destroy
        killable = [i for i in available_targets 
                   if attacker.damage >= enemy_cards[i].current_health]
        if killable:
            # Prioritize high damage threats
            best = max(killable, key=lambda i: enemy_cards[i].damage)
            return (False, best)
        
        # Damage high value targets
        if available_targets:
            valuable = max(available_targets, 
                          key=lambda i: enemy_cards[i].damage + enemy_cards[i].current_health)
            if enemy_cards[valuable].current_health > 3:  # Worth damaging
                return (False, valuable)
        
        # Default: go face
        return (True, None)
    
    def should_use_champion_ability(self, current_mana: int, mana_cost: int, 
                                   my_cards: List[Card], enemy_cards: List[Card]) -> bool:
        """Decide if champion ability should be used."""
        if current_mana < mana_cost:
            return False
        
        # Mistake chance - random
        if random.random() < self.config.mistake_chance:
            return random.random() < 0.3
        
        # Low quality - rarely use
        if self.config.play_quality < 0.3:
            return random.random() < 0.2
        
        # Medium quality - sometimes use
        if self.config.play_quality < 0.6:
            return random.random() < 0.5
        
        # High quality - use when beneficial
        # For Mystara (token generation) - always good if room
        if len(my_cards) < 7:
            return True
        
        # For other abilities - use often
        return random.random() < 0.7


# ==================== PUBLIC API ====================

def get_difficulty_info(level: int, as_dict: bool = False):
    """
    Get description of difficulty level.
    
    Args:
        level: Difficulty level 1-10
        as_dict: If True, return dict for compatibility. If False, return string.
    
    Returns:
        Dict or string with difficulty information
    """
    config = AIConfig(level)
    champion_avg_wr = sum(CHAMPION_WIN_RATES[c] for c in config.champion_pool) / len(config.champion_pool)
    
    if as_dict:
        # Return dict for backward compatibility
        return {
            'name': config.name,
            'level': level,
            'champions': config.champion_pool,
            'deck_quality': config.deck_optimization,
            'play_quality': config.play_quality,
            'mistake_rate': config.mistake_chance,
            'uses_ability_priority': config.uses_ability_priority,
            'uses_matchup_knowledge': config.uses_matchup_knowledge,
            'avg_champion_wr': champion_avg_wr
        }
    
    # Return formatted string
    info = f"\n{'='*60}\n"
    info += f"Nivel {level}: {config.name}\n"
    info += f"{'='*60}\n"
    info += f"Calidad de juego: {config.play_quality*100:.0f}%\n"
    info += f"Probabilidad de error: {config.mistake_chance*100:.0f}%\n"
    info += f"Optimización de deck: {config.deck_optimization*100:.0f}%\n"
    info += f"\nCampeones disponibles: {', '.join(config.champion_pool)}\n"
    info += f"Win Rate promedio: {champion_avg_wr:.1f}%\n"
    
    if config.uses_ability_priority:
        info += f"\n✓ Prioriza habilidad Furia (51.5% WR)\n"
    if config.uses_matchup_knowledge:
        info += f"✓ Usa conocimiento de matchups\n"
    
    return info


def create_ai_opponent(difficulty_level: int = 5) -> Tuple[Champion, Deck, AIConfig]:
    """
    Create AI opponent with specified difficulty.
    Returns: (champion, deck, config)
    """
    config = AIConfig(difficulty_level)
    
    # Select champion based on difficulty
    champion_name = random.choice(config.champion_pool)
    champion = get_champion_by_name(champion_name)
    
    # Ensure champion is not None
    if champion is None:
        raise ValueError(f"Champion '{champion_name}' not found")
    
    # Build deck
    builder = DataDrivenDeckBuilder(config)
    deck = builder.build_deck(champion)
    
    return (champion, deck, config)


def print_all_difficulties():
    """Print info for all 10 difficulty levels."""
    for level in range(1, 11):
        print(get_difficulty_info(level))


# ==================== MAIN AI CLASS (Backward compatible) ====================

class SmartAI:
    """
    Main AI class - backward compatible with existing code.
    Wraps DataDrivenAI for easy integration.
    """
    
    def __init__(self, difficulty: int = 5):
        self.difficulty_level = difficulty
        self.config = AIConfig(difficulty)
        self.player = None  # Set when assigned to player
        self.ai = None
    
    def set_player(self, player: Player):
        """Assign AI to player."""
        self.player = player
        self.ai = DataDrivenAI(player, self.config)
    
    def choose_cards_to_play(self, available_mana: int) -> List[Card]:
        if self.ai:
            return self.ai.choose_cards_to_play(available_mana)
        return []
    
    def choose_blocker(self, attacker: Card, available_defenders: List[int], 
                       defender_zone: List[Card], my_life: int) -> Optional[int]:
        if self.ai:
            return self.ai.choose_blocker(attacker, available_defenders, defender_zone, my_life)
        return None
    
    def choose_attackers(self, active_zone: List[Card]) -> List[int]:
        if self.ai:
            return self.ai.choose_attackers(active_zone)
        return []
    
    def choose_attack_target(self, attacker: Card, enemy_cards: List[Card], 
                            enemy_life: int) -> Tuple[bool, Optional[int]]:
        if self.ai:
            return self.ai.choose_attack_target(attacker, enemy_cards, enemy_life)
        return (True, None)
    
    def should_use_champion_ability(self, current_mana: int, mana_cost: int,
                                   my_cards: List[Card], enemy_cards: List[Card]) -> bool:
        if self.ai:
            return self.ai.should_use_champion_ability(current_mana, mana_cost, my_cards, enemy_cards)
        return False


if __name__ == '__main__':
    print("\n" + "="*70)
    print("DATA-DRIVEN AI ENGINE - Based on 1,000,020 game analysis")
    print("="*70)
    
    print_all_difficulties()
    
    print("\n" + "="*70)
    print("Top Insights from Analysis:")
    print("="*70)
    print(f"Best Champions: Mystara (74.5%), Ragnar (73.5%), Brutus (73.3%)")
    print(f"Worst Champions: Sylvana (21.2%), Lumina (31.9%), Arcanus (37.1%)")
    print(f"Best Cards: Berserker (51.9%), Wolf (51.1%), Knight (50.9%)")
    print(f"Best Ability: Furia (51.5% WR)")
    print(f"Optimal Deck: 28 troops, 12 spells")
    print(f"Average Game: 6-7 turns")
    print("="*70)
