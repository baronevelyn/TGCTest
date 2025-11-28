"""
Message protocol for multiplayer game synchronization.
Defines all message types that can be sent between clients through the server.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict


# ============================================================================
# MESSAGE TYPES
# ============================================================================

class MessageType:
    """All possible message types in the protocol."""
    
    # Game initialization
    GAME_START = "game_start"
    GAME_STATE = "game_state"
    
    # Turn management
    START_TURN = "start_turn"
    END_TURN = "end_turn"
    
    # Card actions
    PLAY_CARD = "play_card"
    ACTIVATE_ABILITY = "activate_ability"
    
    # Combat actions
    DECLARE_ATTACKS = "declare_attacks"
    CHOOSE_BLOCKER = "choose_blocker"
    
    # Spell targeting
    TARGET_SPELL = "target_spell"
    
    # Game state changes
    DRAW_CARD = "draw_card"
    MANA_CHANGE = "mana_change"
    LIFE_CHANGE = "life_change"
    CARD_DESTROYED = "card_destroyed"
    
    # Game end
    GAME_OVER = "game_over"
    
    # Player actions
    PLAYER_SURRENDER = "player_surrender"
    PLAYER_DISCONNECTED = "player_disconnected"


# ============================================================================
# MESSAGE BUILDERS
# ============================================================================

def create_game_start_message(player_data: Dict[str, Any], opponent_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create message to initialize game state for both players."""
    return {
        "type": MessageType.GAME_START,
        "player": player_data,
        "opponent": opponent_data,
        "initial_cards": 5
    }


def create_game_state_message(game_state: Dict[str, Any]) -> Dict[str, Any]:
    """Create full game state snapshot message."""
    return {
        "type": MessageType.GAME_STATE,
        "state": game_state
    }


def create_start_turn_message(player: str) -> Dict[str, Any]:
    """Notify that a player's turn has started."""
    return {
        "type": MessageType.START_TURN,
        "player": player
    }


def create_end_turn_message(player: str) -> Dict[str, Any]:
    """Notify that a player has ended their turn."""
    return {
        "type": MessageType.END_TURN,
        "player": player
    }


def create_play_card_message(player: str, card_index: int, card_data: Dict[str, Any]) -> Dict[str, Any]:
    """Notify that a player played a card."""
    return {
        "type": MessageType.PLAY_CARD,
        "player": player,
        "card_index": card_index,
        "card": card_data
    }


def create_activate_ability_message(player: str, card_index: int) -> Dict[str, Any]:
    """Notify that a player activated a card ability."""
    return {
        "type": MessageType.ACTIVATE_ABILITY,
        "player": player,
        "card_index": card_index
    }


def create_declare_attacks_message(player: str, attacker_indices: List[int], 
                                   targets: List[Any]) -> Dict[str, Any]:
    """Notify declared attacks."""
    return {
        "type": MessageType.DECLARE_ATTACKS,
        "player": player,
        "attackers": attacker_indices,
        "targets": targets
    }


def create_choose_blocker_message(player: str, attacker_index: int, blocker_index: Optional[int]) -> Dict[str, Any]:
    """Notify blocker choice."""
    return {
        "type": MessageType.CHOOSE_BLOCKER,
        "player": player,
        "attacker": attacker_index,
        "blocker": blocker_index
    }


def create_target_spell_message(player: str, spell_index: int, target: Any) -> Dict[str, Any]:
    """Notify spell targeting."""
    return {
        "type": MessageType.TARGET_SPELL,
        "player": player,
        "spell_index": spell_index,
        "target": target
    }


def create_draw_card_message(player: str, card_count: int) -> Dict[str, Any]:
    """Notify cards drawn (opponent sees count, not actual cards)."""
    return {
        "type": MessageType.DRAW_CARD,
        "player": player,
        "count": card_count
    }


def create_mana_change_message(player: str, current_mana: int, max_mana: int) -> Dict[str, Any]:
    """Notify mana change."""
    return {
        "type": MessageType.MANA_CHANGE,
        "player": player,
        "current": current_mana,
        "max": max_mana
    }


def create_life_change_message(player: str, current_life: int) -> Dict[str, Any]:
    """Notify life change."""
    return {
        "type": MessageType.LIFE_CHANGE,
        "player": player,
        "life": current_life
    }


def create_card_destroyed_message(player: str, card_index: int) -> Dict[str, Any]:
    """Notify card destroyed."""
    return {
        "type": MessageType.CARD_DESTROYED,
        "player": player,
        "card_index": card_index
    }


def create_game_over_message(winner: str, reason: str) -> Dict[str, Any]:
    """Notify game end."""
    return {
        "type": MessageType.GAME_OVER,
        "winner": winner,
        "reason": reason
    }


def create_player_surrender_message(player: str) -> Dict[str, Any]:
    """Notify player surrender."""
    return {
        "type": MessageType.PLAYER_SURRENDER,
        "player": player
    }


def create_player_disconnected_message(player: str) -> Dict[str, Any]:
    """Notify player disconnection."""
    return {
        "type": MessageType.PLAYER_DISCONNECTED,
        "player": player
    }


# ============================================================================
# SERIALIZATION HELPERS
# ============================================================================

def serialize_card(card) -> Dict[str, Any]:
    """Convert a Card object to a dictionary for network transmission."""
    return {
        "name": card.name,
        "cost": card.cost,
        "damage": card.damage,
        "health": card.health,
        "current_health": card.current_health,
        "card_type": card.card_type,
        "ability": card.ability,
        "ability_desc": card.ability_desc,
        "ability_type": card.ability_type,
        "ready": card.ready,
        "in_play": card.in_play,
        "attacked_count": getattr(card, 'attacked_count', 0),
        "spell_effect": getattr(card, 'spell_effect', None),
        "spell_target": getattr(card, 'spell_target', None)
    }


def serialize_champion(champion) -> Optional[Dict[str, Any]]:
    """Convert a Champion object to a dictionary."""
    if champion is None:
        return None
    return {
        "name": champion.name,
        "passive_name": champion.passive_name,
        "passive_desc": champion.passive_desc,
        "ability_type": champion.ability_type,
        "ability_value": champion.ability_value
    }


def serialize_player_state(player, reveal_hand: bool = False) -> Dict[str, Any]:
    """
    Convert a Player object to a dictionary.
    
    Args:
        player: Player object
        reveal_hand: If True, include actual hand cards. If False, only send hand size.
    """
    return {
        "name": player.name,
        "life": player.life,
        "mana": player.mana,
        "max_mana": player.max_mana,
        "hand_size": len(player.hand),
        "hand": [serialize_card(c) for c in player.hand] if reveal_hand else None,
        "active_zone": [serialize_card(c) for c in player.active_zone],
        "deck_size": len(player.deck.cards),
        "graveyard_size": len(player.graveyard),
        "champion": serialize_champion(player.champion)
    }


def serialize_game_state(game, perspective_player: str) -> Dict[str, Any]:
    """
    Serialize full game state from a player's perspective.
    
    Args:
        game: Game object
        perspective_player: 'player' or 'ai' - determines whose hand is revealed
    """
    return {
        "turn": game.turn,
        "player": serialize_player_state(game.player, reveal_hand=(perspective_player == 'player')),
        "opponent": serialize_player_state(game.ai, reveal_hand=(perspective_player == 'ai')),
        "action_log": game.action_log[-10:]  # Last 10 actions
    }
