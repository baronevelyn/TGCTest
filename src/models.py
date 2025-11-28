"""
Data models for the TCG game.
Contains Card, Deck, and Player classes.
"""

import random
from dataclasses import dataclass
from typing import List, Optional
import tkinter as tk


@dataclass
class Card:
    """Represents a card in the game."""
    name: str
    cost: int
    damage: int
    health: int = 0
    current_health: int = 0
    ready: bool = False
    in_play: bool = False
    card_type: str = 'troop'  # 'troop', 'spell', 'equipment', 'enchantment', etc.
    image_path: Optional[str] = None
    blocked_this_combat: bool = False
    ability: Optional[str] = None
    ability_desc: Optional[str] = None
    ability_type: Optional[str] = None  # 'triggered', 'activated', 'instant'
    spell_target: Optional[str] = None  # For spells: 'enemy_troop', 'own_troop', 'player', 'all_enemy_troops', etc.
    spell_effect: Optional[str] = None  # For spells: 'damage', 'heal', 'buff', 'destroy', etc.
    description: Optional[str] = None  # Card description text (especially for spells)
    attacked_count: int = 0  # for Furia: track attacks this turn


class CardWidget(tk.Label):
    """Typed widget to allow attaching a Card reference (helps static type checkers)."""
    card: Optional[Card] = None


class Deck:
    """Represents a deck of cards."""
    
    def __init__(self, cards: List[Card]):
        self.cards = cards[:]
        random.shuffle(self.cards)

    def draw(self) -> Optional[Card]:
        """Draw a card from the deck."""
        if self.cards:
            return self.cards.pop()
        return None

    def count(self) -> int:
        """Get the number of cards remaining in the deck."""
        return len(self.cards)


class Player:
    """Represents a player in the game."""
    
    def __init__(self, name: str, deck: Deck, champion=None, ai_config=None):
        self.name = name
        self.deck = deck
        self.champion = champion  # Champion object with passive abilities
        self.ai_config = ai_config  # AI difficulty configuration (for AI players)
        self.hand: List[Card] = []
        # zones
        self.rest_zone: List[Card] = []
        self.active_zone: List[Card] = []
        self.graveyard: List[Card] = []
        # Life based on champion (default 20 if no champion)
        self.max_life = champion.starting_life if champion else 20
        self.life = self.max_life
        self.max_mana = 0
        self.mana = 0

    def draw_card(self):
        """Draw a card from the deck and add it to hand."""
        card = self.deck.draw()
        if card:
            self.hand.append(card)
