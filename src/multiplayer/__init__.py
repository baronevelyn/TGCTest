"""
Módulo de multiplayer para Mini TCG
"""

from .network_manager import NetworkManager
from .game_state_sync import GameStateSync
from .message_protocol import (
    MessageType,
    serialize_card,
    serialize_champion,
    serialize_player_state,
    serialize_game_state
)

__all__ = [
    'NetworkManager',
    'GameStateSync',
    'MessageType',
    'serialize_card',
    'serialize_champion',
    'serialize_player_state',
    'serialize_game_state'
]
