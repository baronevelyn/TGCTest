"""
Game state synchronization system for multiplayer.
Handles converting game actions to network messages and applying received messages to game state.
"""

from typing import Dict, Any, Optional, Callable
from .message_protocol import (
    MessageType,
    create_play_card_message,
    create_end_turn_message,
    create_declare_attacks_message,
    create_game_state_message,
    serialize_game_state,
    serialize_card,
    serialize_player_state
)
from .network_manager import NetworkManager


class GameStateSync:
    """Manages synchronization of game state between two players."""
    
    def __init__(self, game, network_manager: NetworkManager, is_host: bool):
        """
        Initialize game state synchronization.
        
        Args:
            game: Game object to synchronize
            network_manager: NetworkManager instance for sending messages
            is_host: True if this player is the host (goes first)
        """
        self.game = game
        self.network = network_manager
        self.is_host = is_host
        self.my_turn = is_host  # Host starts first
        self.opponent_ready = False
        # Track if we've already executed local start_turn logic this turn
        self.turn_started = False
        
        # Callbacks for UI updates
        self.on_opponent_action: Optional[Callable[[str, Dict], None]] = None
        self.on_game_sync: Optional[Callable[[], None]] = None
        
        # Register network event handlers
        self._setup_network_handlers()
    
    def _setup_network_handlers(self):
        """Set up handlers for incoming network messages."""
        
        def on_action(data):
            """Handle opponent action."""
            try:
                action = data.get('action', 'unknown')
                print(f"📥 [GAME_SYNC] Received opponent action: {action}")
                print(f"   📦 Full data: {data}")
                self._apply_opponent_action(data)
                print(f"   ✅ Action applied")
            except Exception as e:
                print(f"   ❌ Error handling action: {e}")
                import traceback
                traceback.print_exc()
        
        def on_sync_request(data):
            """Handle game state sync request."""
            self._send_game_state()
        
        def on_disconnect():
            """Handle opponent disconnection."""
            self._handle_opponent_disconnect()

        def on_game_state_update(data):
            """Handle full game state snapshot from server (includes draws)."""
            try:
                print("📦 [GAME_SYNC] Received full game_state_update from server")
                self._apply_full_game_state(data)
                print("   ✅ Full state applied")
            except Exception as e:
                print(f"   ❌ Error applying full state: {e}")
                import traceback
                traceback.print_exc()
        
        # Register callbacks with network manager
        self.network.on_opponent_action = on_action
        self.network.on_sync_request = on_sync_request
        self.network.on_opponent_disconnected = on_disconnect
        self.network.on_game_state_update = on_game_state_update
    
    # ========================================================================
    # OUTGOING ACTIONS (Local player → Network)
    # ========================================================================
    
    def send_play_card(self, card_index: int, spell_target_idx: Optional[int] = None):
        """Send play card action to server (servidor ejecutará y enviará estado)."""
        if not self.my_turn:
            print("❌ [GAME_SYNC] Cannot send play_card: not my turn")
            return False
        
        card = self.game.player.hand[card_index]
        print(f"🎴 [GAME_SYNC] Sending play_card: {card.name} (index {card_index})")
        
        # Solo enviar acción - servidor valida y ejecuta
        action_data = {
            "action": "play_card",
            "card_index": card_index,
            "spell_target": spell_target_idx
        }
        
        self.network.send_action(action_data)
        print(f"   ✅ Acción enviada - esperando estado del servidor...")
        return True
    
    def send_activate_ability(self, card_index: int):
        """Send activate ability action to opponent."""
        if not self.my_turn:
            return False
        
        action_data = {
            "action": "activate_ability",
            "card_index": card_index
        }
        
        self.network.send_action(action_data)
        return True
    
    def send_declare_attacks(self, attacker_indices: list, targets: list):
        """Send declare attacks action to opponent."""
        if not self.my_turn:
            return False
        
        action_data = {
            "action": "declare_attacks",
            "attackers": attacker_indices,
            "targets": targets
        }
        
        self.network.send_action(action_data)
        return True
    
    def send_end_turn(self):
        """Send end turn action to server (servidor ejecutará y enviará estado)."""
        if not self.my_turn:
            print("❌ [GAME_SYNC] Cannot send end_turn: not my turn")
            return False
        
        print("🔄 [GAME_SYNC] === ENDING MY TURN ===")
        print(f"   Current my_turn: {self.my_turn}")
        
        # Solo enviar acción simple - servidor maneja el resto
        action_data = {
            "action": "end_turn"
        }
        
        self.network.send_action(action_data)
        self.my_turn = False
        print(f"   ✅ Acción enviada - esperando estado del servidor...")
        return True
    
    def send_my_champion_info(self, champion_name: str):
        """Send my champion info to opponent."""
        print(f"🎮 [GAME_SYNC] === SENDING MY CHAMPION INFO ===")
        print(f"   My champion: {champion_name}")
        print(f"   I am {'HOST' if self.is_host else 'GUEST'}")
        action_data = {
            "action": "champion_info",
            "champion_name": champion_name,
            "is_host": self.is_host
        }
        self.network.send_action(action_data)
        print(f"   ✅ champion_info sent to server")
    
    def send_surrender(self):
        """Send surrender action."""
        action_data = {
            "action": "surrender"
        }
        self.network.send_action(action_data)
    
    # ========================================================================
    # INCOMING ACTIONS (Network → Apply to game)
    # ========================================================================
    
    def _apply_opponent_action(self, data: Dict[str, Any]):
        """Apply received action from opponent to local game state."""
        action = data.get("action")
        
        if action == "champion_info":
            self._apply_champion_info(data)
        elif action == "play_card":
            self._apply_play_card(data)
        elif action == "activate_ability":
            self._apply_activate_ability(data)
        elif action == "declare_attacks":
            self._apply_declare_attacks(data)
        elif action == "end_turn":
            self._apply_end_turn(data)
        elif action == "surrender":
            self._apply_surrender(data)
        else:
            print(f"Unknown action type: {action}")
        
        # Notify UI to update
        if self.on_opponent_action and action:
            self.on_opponent_action(action, data)
        if self.on_game_sync:
            self.on_game_sync()
    
    def _apply_play_card(self, data: Dict[str, Any]):
        """Apply opponent's play card action."""
        card_index = data.get("card_index", 0)
        spell_target = data.get("spell_target")
        
        print(f"🎴 [GAME_SYNC] Applying opponent's play_card")
        print(f"   Card index: {card_index}")
        print(f"   Opponent hand size: {len(self.game.ai.hand)}")
        
        # AI plays card (opponent is represented as AI in game logic)
        if card_index < len(self.game.ai.hand):
            card_name = self.game.ai.hand[card_index].name if card_index < len(self.game.ai.hand) else "Unknown"
            print(f"   Playing card: {card_name}")
            self.game.play_card_ai(card_index, spell_target)
            self.game.on_update()  # Force UI update
            print(f"   ✅ Card played and UI updated")
        else:
            print(f"   ❌ Invalid card index")
    
    def _apply_activate_ability(self, data: Dict[str, Any]):
        """Apply opponent's activate ability action."""
        card_index = data.get("card_index", 0)
        
        if card_index < len(self.game.ai.active_zone):
            self.game.activate_ability(card_index, owner='ai')
    
    def _apply_declare_attacks(self, data: Dict[str, Any]):
        """Apply opponent's attack declaration."""
        attackers = data.get("attackers", [])
        targets = data.get("targets", [])
        
        # Convert targets back to proper format
        processed_targets = []
        for target in targets:
            if target == "player":
                processed_targets.append("player")
            elif isinstance(target, dict) and target.get("type") == "card":
                processed_targets.append(("card", target.get("index", 0)))
            else:
                processed_targets.append("player")
        
        self.game.declare_attacks_v2(attackers, processed_targets, owner='ai')
    
    def _apply_champion_info(self, data: Dict[str, Any]):
        """Apply opponent's champion info."""
        print(f"🎮 [GAME_SYNC] === RECEIVED OPPONENT'S CHAMPION INFO ===")
        print(f"   Am I host? {self.is_host}")
        print(f"   Data received: {data}")
        
        opponent_champ_name = data.get("champion_name")
        opponent_is_host = data.get("is_host", False)
        
        print(f"   Opponent is {'HOST' if opponent_is_host else 'GUEST'}")
        print(f"   Opponent's champion: {opponent_champ_name}")
        print(f"   My champion: {self.game.player.champion.name if self.game.player.champion else 'None'}")
        print(f"   Current opponent champion: {self.game.ai.champion.name if self.game.ai.champion else 'None'}")
        
        # Update opponent's champion with received info
        if opponent_champ_name and self.game.ai.champion:
            self.game.ai.champion.name = opponent_champ_name
            print(f"   ✅ Opponent champion updated to: {opponent_champ_name}")
        
        print(f"   Final opponent champion: {self.game.ai.champion.name if self.game.ai.champion else 'None'}")
        
        # Update UI - wrapped in try/except to catch any errors
        try:
            print(f"   Calling game.on_update()...")
            print(f"   Player life: {self.game.player.life}")
            print(f"   Opponent life: {self.game.ai.life}")
            print(f"   game_started: {self.game.game_started}")
            self.game.on_update()
            print(f"   ✅ UI updated successfully")
        except Exception as e:
            print(f"   ⚠️ Error updating UI: {e}")
            import traceback
            traceback.print_exc()
    
    def _apply_end_turn(self, data: Dict[str, Any]):
        """Apply opponent's end turn and update their board state."""
        print("🔄 [GAME_SYNC] === RECEIVING OPPONENT'S END TURN ===")
        print(f"   Current my_turn: {self.my_turn}")
        
        # Update opponent's board state from received data
        board_state = data.get("board_state", {})
        if board_state:
            print(f"   📦 Updating opponent board state:")
            print(f"      Hand: {board_state.get('hand_count', 0)} cards")
            print(f"      Active: {len(board_state.get('active_zone', []))} cards")
            print(f"      Mana: {board_state.get('mana', 0)}/{board_state.get('max_mana', 0)}")
            print(f"      Life: {board_state.get('life', 0)}")
            
            # Update opponent's hand count (keep existing cards hidden)
            opponent_hand_count = board_state.get('hand_count', 0)
            current_count = len(self.game.ai.hand)
            if opponent_hand_count > current_count:
                # Opponent drew cards - add dummy cards
                from ..cards import Card
                for _ in range(opponent_hand_count - current_count):
                    dummy_card = Card("Hidden", 0, 0, 0, card_type="troop")
                    self.game.ai.hand.append(dummy_card)
            elif opponent_hand_count < current_count:
                # Opponent played/discarded cards
                self.game.ai.hand = self.game.ai.hand[:opponent_hand_count]
            
            # Update opponent's active zone
            active_zone_data = board_state.get('active_zone', [])
            self.game.ai.active_zone.clear()
            from ..cards import Card
            for card_data in active_zone_data:
                card = Card(
                    name=card_data.get('name', 'Unknown'),
                    cost=card_data.get('cost', 0),
                    damage=card_data.get('attack', 0),
                    health=card_data.get('life', 1),
                    ability=card_data.get('ability'),
                    ability_desc=card_data.get('ability_desc'),
                    card_type=card_data.get('type', 'troop')
                )
                card.current_health = card.health
                card.ready = card_data.get('ready', True)
                self.game.ai.active_zone.append(card)
            
            # Update opponent's mana and life
            self.game.ai.mana = board_state.get('mana', 0)
            self.game.ai.max_mana = board_state.get('max_mana', 0)
            self.game.ai.life = board_state.get('life', 20)
        
        # Switch turn to local player
        self.my_turn = True
        self.turn_started = True  # We'll start the turn now
        print(f"   ✅ my_turn set to True - IT'S MY TURN NOW!")
        self.game.log_action("Your turn!")
        try:
            self.game.start_turn('player')
            self.game.on_update()
            print(f"   ✅ Turn started, UI updated")
        except Exception as e:
            print(f"   ⚠️ Error in turn transition: {e}")
            import traceback
            traceback.print_exc()

    # ========================================================================
    # FULL STATE APPLICATION (from server snapshot)
    # ========================================================================

    def _apply_full_game_state(self, data: Dict[str, Any]):
        """Apply a full game state snapshot (server authoritative)."""
        state = data.get('state', {})
        if not state:
            print("   ⚠️ No 'state' key in game_state_update payload")
            return
        prev_my_turn = self.my_turn
        prev_turn = self.game.turn
        turn = state.get('turn')
        if turn:
            self.game.turn = turn
        player_state = state.get('player', {})
        opponent_state = state.get('opponent', {})

        from ..cards import Card

        # Update local player (hand revealed)
        if player_state:
            self.game.player.life = player_state.get('life', self.game.player.life)
            self.game.player.mana = player_state.get('mana', self.game.player.mana)
            self.game.player.max_mana = player_state.get('max_mana', self.game.player.max_mana)

            # Rebuild hand with real cards if provided
            hand_cards = player_state.get('hand')
            if hand_cards is not None:
                self.game.player.hand.clear()
                for c in hand_cards:
                    card = Card(
                        name=c.get('name', 'Unknown'),
                        cost=c.get('cost', 0),
                        damage=c.get('damage', 0),
                        health=c.get('health', 1),
                        ability=c.get('ability'),
                        ability_desc=c.get('ability_desc'),
                        card_type=c.get('card_type', 'troop')
                    )
                    card.current_health = c.get('current_health', card.health)
                    card.ready = c.get('ready', True)
                    self.game.player.hand.append(card)

            # Active zone
            active_zone = player_state.get('active_zone', [])
            self.game.player.active_zone.clear()
            for c in active_zone:
                card = Card(
                    name=c.get('name', 'Unknown'),
                    cost=c.get('cost', 0),
                    damage=c.get('damage', 0),
                    health=c.get('health', 1),
                    ability=c.get('ability'),
                    ability_desc=c.get('ability_desc'),
                    card_type=c.get('card_type', 'troop')
                )
                card.current_health = c.get('current_health', card.health)
                card.ready = c.get('ready', True)
                self.game.player.active_zone.append(card)

        # Update opponent (hand hidden -> only size)
        if opponent_state:
            self.game.ai.life = opponent_state.get('life', self.game.ai.life)
            self.game.ai.mana = opponent_state.get('mana', self.game.ai.mana)
            self.game.ai.max_mana = opponent_state.get('max_mana', self.game.ai.max_mana)

            opponent_hand_size = opponent_state.get('hand_size', len(self.game.ai.hand))
            current_size = len(self.game.ai.hand)
            if opponent_hand_size > current_size:
                for _ in range(opponent_hand_size - current_size):
                    dummy = Card("Hidden", 0, 0, 0, card_type="troop")
                    self.game.ai.hand.append(dummy)
            elif opponent_hand_size < current_size:
                self.game.ai.hand = self.game.ai.hand[:opponent_hand_size]

            # Active zone
            active_zone = opponent_state.get('active_zone', [])
            self.game.ai.active_zone.clear()
            for c in active_zone:
                card = Card(
                    name=c.get('name', 'Unknown'),
                    cost=c.get('cost', 0),
                    damage=c.get('damage', 0),
                    health=c.get('health', 1),
                    ability=c.get('ability'),
                    ability_desc=c.get('ability_desc'),
                    card_type=c.get('card_type', 'troop')
                )
                card.current_health = c.get('current_health', card.health)
                card.ready = c.get('ready', True)
                self.game.ai.active_zone.append(card)

        # Update local turn flag
        self.my_turn = (self.game.turn == 'player')

        # Detect transition: it is now our turn but we hadn't started it yet (guest draw fix)
        if self.my_turn and (not prev_my_turn) and (not self.turn_started):
            try:
                print("   🔄 Detected turn transition via snapshot -> starting local turn")
                self.turn_started = True
                self.game.start_turn('player')
            except Exception as e:
                print(f"   ⚠️ Could not auto-start turn from snapshot: {e}")
        elif not self.my_turn:
            # Reset flag when it's not our turn
            self.turn_started = False

        try:
            self.game.on_update()
        except Exception as e:
            print(f"   ⚠️ UI update failed after full state apply: {e}")

    
    def _apply_surrender(self, data: Dict[str, Any]):
        """Apply opponent surrender."""
        self.game.log_action("Opponent surrendered!")
        self.game.player.life = 30  # Ensure player wins
        self.game.ai.life = 0
        self.game.check_end()
    
    def _handle_opponent_disconnect(self):
        """Handle opponent disconnection."""
        self.game.log_action("Opponent disconnected!")
        # Award win to remaining player
        if self.game.player.life > 0:
            self.game.ai.life = 0
            self.game.check_end()
    
    # ========================================================================
    # GAME STATE SYNC
    # ========================================================================
    
    def _send_game_state(self):
        """Send full game state to opponent (for reconnection/sync)."""
        state = serialize_game_state(self.game, perspective_player='player')
        message = create_game_state_message(state)
        self.network.send_action(message)
    
    def request_sync(self):
        """Request game state from opponent."""
        action_data = {
            "action": "sync_request"
        }
        self.network.send_action(action_data)
    
    # ========================================================================
    # UTILITY
    # ========================================================================
    
    def is_my_turn(self) -> bool:
        """Check if it's the local player's turn."""
        return self.my_turn
    
    def can_act(self) -> bool:
        """Check if local player can perform actions."""
        return self.my_turn and self.game.turn == 'player'
