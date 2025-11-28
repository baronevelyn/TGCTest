"""
Demo of Multiplayer UI - Test the interface without network connection
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import tkinter as tk
from src.multiplayer.multiplayer_ui import MultiplayerGameUI, CardDisplay


def demo_ui():
    """Launch UI demo with mock data"""
    root = tk.Tk()
    
    # Create UI with dummy callbacks
    ui = MultiplayerGameUI(
        root=root,
        player_name="Player1",
        opponent_name="Player2",
        on_play_card=lambda idx: ui.log_action(f"🎴 Played card at index {idx}"),
        on_end_turn=lambda: ui.log_action("⏭️ Turn ended"),
        on_declare_attacks=lambda attackers: ui.log_action(f"⚔️ Attacking with: {attackers}"),
        on_send_chat=lambda msg: ui.add_chat_message("Player1", msg)
    )
    
    # Populate with test data
    ui.log_action("🎮 Game started!")
    ui.add_system_message("Match found! Good luck!")
    
    # Set initial stats
    ui.update_player_stats(life=25, mana=3, max_mana=3)
    ui.update_opponent_stats(life=25, mana=2, max_mana=2, hand_count=5)
    
    # Add cards to my hand
    my_hand = [
        CardDisplay(
            name="Goblin",
            cost=1,
            attack=2,
            defense=1,
            card_type="Troop",
            abilities=["Furia"]
        ),
        CardDisplay(
            name="Knight",
            cost=3,
            attack=3,
            defense=3,
            card_type="Troop",
            abilities=[]
        ),
        CardDisplay(
            name="Fireball",
            cost=2,
            attack=0,
            defense=0,
            card_type="Spell",
            abilities=["Deal 3 damage"]
        ),
        CardDisplay(
            name="Dragon",
            cost=5,
            attack=5,
            defense=5,
            card_type="Troop",
            abilities=["Volar", "Furia"]
        ),
    ]
    ui.update_my_hand(my_hand)
    
    # Add cards to my active zone
    my_active = [
        CardDisplay(
            name="Wolf",
            cost=2,
            attack=2,
            defense=2,
            card_type="Troop",
            abilities=["Furia"],
            can_attack=True,
            is_tapped=False
        ),
        CardDisplay(
            name="Archer",
            cost=2,
            attack=1,
            defense=2,
            card_type="Troop",
            abilities=[],
            can_attack=False,
            is_tapped=True
        ),
    ]
    ui.update_my_active(my_active)
    
    # Add cards to opponent's active zone
    opponent_active = [
        CardDisplay(
            name="Skeleton",
            cost=1,
            attack=1,
            defense=1,
            card_type="Troop",
            abilities=[],
            can_attack=False,
            is_tapped=True
        ),
        CardDisplay(
            name="Orc",
            cost=3,
            attack=3,
            defense=2,
            card_type="Troop",
            abilities=["Furia"],
            can_attack=False,
            is_tapped=False
        ),
        CardDisplay(
            name="Giant",
            cost=4,
            attack=4,
            defense=4,
            card_type="Troop",
            abilities=["Taunt"],
            can_attack=False,
            is_tapped=False
        ),
    ]
    ui.update_opponent_active(opponent_active)
    
    # Update opponent hand
    ui.update_opponent_hand(5)
    
    # Set turn
    ui.set_turn(is_my_turn=True)
    
    # Add some action log entries
    ui.log_action("Turn 3 - Your turn")
    ui.log_action("💎 Mana: 3/3")
    ui.log_action("Opponent played 'Orc'")
    ui.log_action("Opponent attacked with 'Skeleton'")
    
    # Add chat messages
    ui.add_chat_message("Player2", "Good luck!")
    ui.add_chat_message("Player1", "You too!")
    ui.add_system_message("Player2 played a card")
    
    # Test buttons after 2 seconds
    def test_interaction():
        ui.log_action("⚡ Testing UI interactions...")
        ui.add_chat_message("System", "UI is fully functional!")
    
    root.after(2000, test_interaction)
    
    root.mainloop()


if __name__ == "__main__":
    print("="*60)
    print("🎮 MULTIPLAYER UI DEMO")
    print("="*60)
    print("\nLaunching UI with test data...")
    print("\nFeatures to test:")
    print("  ✓ Click cards in your hand (when it's your turn)")
    print("  ✓ Click 'DECLARE ATTACKS' to select attackers")
    print("  ✓ Click creatures to select them as attackers")
    print("  ✓ Click 'END TURN' to end your turn")
    print("  ✓ Type in chat and press Enter or click Send")
    print("\n" + "="*60)
    
    demo_ui()
