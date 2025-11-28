"""
Champion system for the TCG game.
Each champion represents a player with unique passive abilities.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Champion:
    """Represents a champion with unique abilities."""
    name: str
    title: str
    starting_life: int
    passive_name: str
    passive_description: str
    image_path: Optional[str] = None
    
    # Passive ability identifiers for game logic
    ability_type: str = 'none'  # 'spell_discount', 'troop_buff', 'summon_token', etc.
    ability_value: int = 0  # Numeric value for the ability


# Champion definitions
CHAMPION_LIST = [
    Champion(
        name="Arcanus",
        title="Mago de Batalla",
        starting_life=25,
        passive_name="Maestría Arcana",
        passive_description="Los hechizos cuestan 1 maná menos (mínimo 1)",
        ability_type="spell_discount",
        ability_value=1
    ),
    Champion(
        name="Brutus",
        title="Señor de la Guerra",
        starting_life=35,
        passive_name="Sed de Sangre",
        passive_description="Todas tus tropas tienen +1 ATK",
        ability_type="troop_buff_attack",
        ability_value=1
    ),
    Champion(
        name="Mystara",
        title="Invocadora",
        starting_life=28,
        passive_name="Ejército Infinito",
        passive_description="Al inicio de tu turno, invoca un Token 1/1",
        ability_type="summon_token",
        ability_value=1
    ),
    Champion(
        name="Shadowblade",
        title="Asesino",
        starting_life=22,
        passive_name="Golpe Letal",
        passive_description="Tropas de coste 3 o menos tienen +1 ATK y Prisa",
        ability_type="cheap_troop_buff",
        ability_value=3  # max cost to get buff
    ),
    Champion(
        name="Lumina",
        title="Clérigo",
        starting_life=32,
        passive_name="Bendición Divina",
        passive_description="Al inicio de tu turno, cura 1 HP a todas tus tropas",
        ability_type="heal_troops",
        ability_value=1
    ),
    Champion(
        name="Tacticus",
        title="Estratega",
        starting_life=30,
        passive_name="Visión Táctica",
        passive_description="Empiezas con 6 cartas, robas 2 al inicio del turno",
        ability_type="card_draw",
        ability_value=2
    ),
    Champion(
        name="Ragnar",
        title="Berserker",
        starting_life=40,
        passive_name="Furia Imparable",
        passive_description="No puedes bloquear. Todas tus tropas tienen Furia",
        ability_type="all_furia",
        ability_value=0
    ),
    Champion(
        name="Sylvana",
        title="Druida",
        starting_life=28,
        passive_name="Crecimiento Natural",
        passive_description="Las tropas con 4+ HP ganan +1/+1",
        ability_type="big_troop_buff",
        ability_value=4  # min health to get buff
    )
]


def get_champion_by_name(name: str) -> Optional[Champion]:
    """Get a champion by name."""
    for champion in CHAMPION_LIST:
        if champion.name.lower() == name.lower():
            return champion
    return None


def get_random_champion() -> Champion:
    """Get a random champion from the list."""
    import random
    return random.choice(CHAMPION_LIST)
