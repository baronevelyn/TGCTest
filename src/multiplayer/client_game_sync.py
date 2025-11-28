"""
Client Game Synchronization - Aplica estado del servidor al cliente
En arquitectura autoritativa, el cliente solo VISUALIZA el estado del servidor
"""

from typing import Dict, Any
from ..models import Card
from ..game_logic import Game


class ClientGameSync:
    """Sincroniza el juego del cliente con el estado autoritativo del servidor"""
    
    def __init__(self, game: Game):
        self.game = game
    
    def apply_server_state(self, state: Dict[str, Any]):
        """
        Aplica el estado completo del servidor al juego local.
        El servidor es la fuente de verdad - el cliente solo visualiza.
        
        Args:
            state: Estado del juego desde el servidor con estructura:
                {
                    'my_state': {vida, maná, mano, zona activa, etc},
                    'opponent_state': {vida, maná, zona activa, etc},
                    'turn': 'player' | 'ai',
                    'is_my_turn': bool
                }
        """
        try:
            print(f"🔄 [CLIENT_SYNC] Aplicando estado del servidor...")
            
            my_state = state.get('my_state', {})
            opp_state = state.get('opponent_state', {})
            
            # Actualizar mi lado
            self._update_player_state(self.game.player, my_state, is_mine=True)
            
            # Actualizar lado del oponente
            self._update_player_state(self.game.ai, opp_state, is_mine=False)
            
            # Actualizar turno
            self.game.turn = state.get('turn', 'player')
            
            # Actualizar UI
            self.game.on_update()
            
            print(f"   ✅ Estado aplicado - Turn: {self.game.turn}")
            print(f"   Player: {self.game.player.life}HP, {len(self.game.player.hand)} cartas")
            print(f"   AI: {self.game.ai.life}HP, {len(self.game.ai.hand)} cartas")
            
        except Exception as e:
            print(f"   ❌ Error aplicando estado: {e}")
            import traceback
            traceback.print_exc()
    
    def _update_player_state(self, player, state: Dict[str, Any], is_mine: bool):
        """Actualiza el estado de un jugador"""
        # Vida y maná
        player.life = state.get('life', player.life)
        player.mana = state.get('mana', player.mana)
        player.max_mana = state.get('max_mana', player.max_mana)
        
        if is_mine:
            # Es mi lado - actualizo mi mano completa
            hand_data = state.get('hand', [])
            print(f"      📋 Actualizando MI mano: {len(hand_data)} cartas")
            player.hand.clear()
            for card_data in hand_data:
                card = self._create_card_from_data(card_data)
                player.hand.append(card)
                print(f"         ✅ Carta añadida: {card.name} (cost={card.cost})")
        else:
            # Es el oponente - solo actualizo cantidad de cartas (ocultas)
            hand_count = state.get('hand_count', 0)
            current_count = len(player.hand)
            
            if hand_count > current_count:
                # Añadir cartas ocultas
                from ..cards import Card as CardClass
                for _ in range(hand_count - current_count):
                    dummy = CardClass("Hidden", 0, 0, 0, card_type="troop")
                    player.hand.append(dummy)
            elif hand_count < current_count:
                # Reducir cartas
                player.hand = player.hand[:hand_count]
        
        # Zona activa (visible para ambos)
        active_data = state.get('active_zone', [])
        player.active_zone.clear()
        for card_data in active_data:
            card = self._create_card_from_data(card_data)
            player.active_zone.append(card)
    
    def _create_card_from_data(self, card_data: Dict[str, Any]) -> Card:
        """Crea una instancia de Card desde los datos del servidor"""
        from ..cards import Card as CardClass
        
        card = CardClass(
            name=card_data.get('name', 'Unknown'),
            cost=card_data.get('cost', 0),
            damage=card_data.get('damage', 0),
            health=card_data.get('health', 0),
            card_type=card_data.get('card_type', 'troop'),
            ability=card_data.get('ability'),
            ability_desc=card_data.get('ability_desc'),
            ability_type=card_data.get('ability_type'),
            spell_target=card_data.get('spell_target'),
            spell_effect=card_data.get('spell_effect'),
            description=card_data.get('description')
        )
        
        card.current_health = card_data.get('current_health', card.health)
        card.ready = card_data.get('ready', False)
        
        return card
