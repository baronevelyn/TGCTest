"""
Card definitions and deck building for the TCG game.
Contains all card templates and deck generation functions.
"""

import os
import random
from typing import Optional
from .models import Card, Deck


# Card templates with thematic abilities
# Format for troops: (name, cost, damage, ability, ability_desc, ability_type)
TROOP_TEMPLATES = [
    # Basic cards without abilities
    ('Goblin', 1, 2, None, None, None),
    ('Slingshot', 1, 1, None, None, None),
    ('Archer', 2, 3, None, None, None),
    ('Knight', 3, 5, None, None, None),
    ('Mage', 4, 7, None, None, None),
    ('Golem', 5, 9, None, None, None),
    
    # Cards with triggered abilities (passive/automatic)
    ('Berserker', 3, 4, 'Furia', 'Puede atacar dos veces por turno', 'triggered'),
    ('Wolf', 2, 2, 'Furia', 'Puede atacar dos veces por turno', 'triggered'),
    ('Dragon', 5, 6, 'Volar', 'Solo puede ser bloqueado por otras cartas con Volar', 'triggered'),
    ('Eagle', 2, 2, 'Volar', 'Solo puede ser bloqueado por otras cartas con Volar', 'triggered'),
    ('Bat', 1, 1, 'Volar', 'Solo puede ser bloqueado por otras cartas con Volar', 'triggered'),
    ('Guardian', 3, 3, 'Taunt', 'Los atacantes deben atacar esta carta primero', 'triggered'),
    ('Wall', 2, 1, 'Taunt', 'Los atacantes deben atacar esta carta primero', 'triggered'),
    
    # Cards with activated abilities (tap to use)
    ('Necromancer', 4, 3, 'Invocar Aliado', 'Tap: Invoca un Token 1/1', 'activated'),
    ('Shaman', 3, 2, 'Invocar Aliado', 'Tap: Invoca un Token 1/1', 'activated'),
    
    # New cards - Support for weak champions
    ('Guardian del Bosque', 3, 2, 'Taunt+Regeneracion', 'Bloquea primero y se cura 1 vida al inicio de tu turno', 'triggered'),
    ('Hada Sanadora', 2, 1, 'Curacion al Entrar', 'Cuando entra al campo, cura 3 de vida al campeon', 'on_play'),
    ('Cazador de Bestias', 3, 3, 'Debilitar', 'Al dañar al campeón enemigo, reduce su vida máxima en 1', 'triggered'),
    ('Ladron de Almas', 4, 3, 'Absorber Magia', 'Cuando el oponente lanza un hechizo, gana +1/+1', 'triggered'),
]

# Spell templates
# Format: (name, cost, damage, spell_target, spell_effect, description)
SPELL_TEMPLATES = [
    # Direct damage spells (can target troops or player)
    ('Rayo', 2, 3, 'enemy_or_player', 'damage', 'Hace 3 de daño a una tropa o jugador'),
    ('Bola de Fuego', 3, 4, 'enemy_or_player', 'damage', 'Hace 4 de daño a una tropa o jugador'),
    ('Descarga Electrica', 1, 2, 'enemy_or_player', 'damage', 'Hace 2 de daño a una tropa o jugador'),
    
    # Area damage
    ('Rafaga de Flechas', 3, 1, 'all_enemies', 'damage', 'Hace 1 de daño a todas las tropas enemigas'),
    ('Tormenta de Fuego', 5, 2, 'all_enemies', 'damage', 'Hace 2 de daño a todas las tropas enemigas'),
    
    # Healing
    ('Curación', 1, 3, 'self', 'heal', 'Restaura 3 puntos de vida'),
    ('Curación Mayor', 3, 7, 'self', 'heal', 'Restaura 7 puntos de vida'),
    
    # Destruction (troops only)
    ('Destierro', 4, 0, 'enemy', 'destroy', 'Destruye una tropa enemiga'),
    ('Aniquilar', 2, 0, 'enemy', 'destroy', 'Destruye una tropa enemiga dañada'),
    
    # Utility
    ('Dibujar Cartas', 2, 2, 'self', 'draw', 'Roba 2 cartas'),
    
    # New spells
    ('Prision de Luz', 2, 0, 'enemy', 'freeze', 'Congela una tropa enemiga por 2 turnos (no puede atacar ni bloquear)'),
    ('Pacto de Sangre', 3, 0, 'friendly', 'sacrifice', 'Destruye una tropa aliada. Roba 2 cartas y gana +2 de maná este turno'),
]

# Backward compatibility
CARD_TEMPLATES = TROOP_TEMPLATES


def create_card(name: str, cost: int, damage: int, health: Optional[int] = None, 
                ability: Optional[str] = None, ability_desc: Optional[str] = None, 
                ability_type: Optional[str] = None, card_type: str = 'troop',
                spell_target: Optional[str] = None, spell_effect: Optional[str] = None,
                description: Optional[str] = None) -> Card:
    """
    Create a card with the specified attributes.
    If health is not provided and it's a troop, it defaults to damage + random(0-2).
    Spells have 0 health.
    """
    if health is None:
        if card_type == 'troop':
            health = damage + random.randint(0, 2)
        else:
            health = 0
    
    card = Card(
        name=name,
        cost=cost,
        damage=damage,
        health=health,
        current_health=health,
        card_type=card_type,
        ability=ability,
        ability_desc=ability_desc,
        ability_type=ability_type,
        spell_target=spell_target,
        spell_effect=spell_effect,
        description=description
    )
    
    # Try to attach an image path if assets exist
    # First try root assets folder (TGCTest/assets/cards/)
    project_root = os.path.dirname(os.path.dirname(__file__))
    assets_dir = os.path.join(project_root, 'assets', 'cards')
    
    # Fallback to src/assets/cards if not found
    if not os.path.isdir(assets_dir):
        assets_dir = os.path.join(os.path.dirname(__file__), 'assets', 'cards')
    
    if os.path.isdir(assets_dir):
        try:
            for fname in os.listdir(assets_dir):
                if fname.lower().startswith(name.lower()) and fname.lower().endswith('.png'):
                    card.image_path = os.path.join(assets_dir, fname)
                    break
        except Exception:
            # If assets folder has issues, just skip images
            pass
    
    return card


def build_random_deck(size: int = 10, spell_ratio: float = 0.3) -> Deck:
    """
    Build a random deck with the specified number of cards.
    Cards are randomly selected from templates.
    
    Args:
        size: Total number of cards in deck
        spell_ratio: Proportion of spells (default 0.3 = 30% spells, 70% troops)
    """
    cards = []
    num_spells = int(size * spell_ratio)
    num_troops = size - num_spells
    
    # Add troops
    for _ in range(num_troops):
        name, cost, dmg, ability, ability_desc, ability_type = random.choice(TROOP_TEMPLATES)
        card = create_card(name, cost, dmg, ability=ability, ability_desc=ability_desc, 
                          ability_type=ability_type, card_type='troop')
        cards.append(card)
    
    # Add spells
    for _ in range(num_spells):
        name, cost, dmg, spell_target, spell_effect, description = random.choice(SPELL_TEMPLATES)
        card = create_card(name, cost, dmg, card_type='spell', 
                          spell_target=spell_target, spell_effect=spell_effect,
                          description=description)
        cards.append(card)
    
    return Deck(cards)


def build_themed_deck(theme: str, size: int = 10) -> Deck:
    """
    Build a themed deck focusing on specific card types.
    Themes: 'aggro', 'flying', 'defensive', 'mixed'
    """
    if theme == 'aggro':
        # Focus on low-cost aggressive cards with Furia
        pool = [t for t in CARD_TEMPLATES if t[1] <= 3 or t[3] == 'Furia']
    elif theme == 'flying':
        # Focus on cards with Volar ability
        pool = [t for t in CARD_TEMPLATES if t[3] == 'Volar' or t[1] <= 2]
    elif theme == 'defensive':
        # Focus on high-health cards and Taunt
        pool = [t for t in CARD_TEMPLATES if t[3] == 'Taunt' or t[1] >= 3]
    else:  # mixed
        pool = CARD_TEMPLATES
    
    cards = []
    for _ in range(size):
        name, cost, dmg, ability, ability_desc, ability_type = random.choice(pool)
        card = create_card(name, cost, dmg, ability=ability, ability_desc=ability_desc, ability_type=ability_type)
        cards.append(card)
    
    return Deck(cards)
