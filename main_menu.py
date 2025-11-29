"""
Main menu for the TCG game.
Choose between deck builder, quick play, or play vs AI with difficulty selection.
"""

import tkinter as tk
from tkinter import messagebox
import sys
import os
import subprocess


def start_deck_builder():
    """Launch the deck builder."""
    root.destroy()
    from src import deck_builder
    builder_root = tk.Tk()
    deck_builder.DeckBuilder(builder_root)
    builder_root.mainloop()


def start_vs_ai():
    """Launch game vs AI with deck selection then difficulty selection."""
    try:
        from src.deck_selector import show_deck_selector
        from src.difficulty_selector import show_difficulty_selector
        from src.ai_engine import create_ai_opponent
        from src import game_gui
        from src.game_logic import Game
        from src.models import Player, Deck
        
        def on_deck_selected(player_cards, player_champion):
            """Called when player selects their deck."""
            # Hide root after deck selection
            root.withdraw()
            
            def on_difficulty_selected(level):
                """Called when player selects AI difficulty."""
                # Crear jugador humano con el deck seleccionado
                player_deck = Deck(player_cards[:])
                player = Player('Jugador', player_deck, champion=player_champion)
                
                # Crear IA con dificultad seleccionada
                ai_champion, ai_deck, ai_config = create_ai_opponent(difficulty_level=level)
                ai_player = Player('IA', ai_deck, champion=ai_champion, ai_config=ai_config)
                
                # Crear ventana de juego
                game_root = tk.Toplevel()
                game_root.geometry('1100x700')
                game_root.minsize(900, 600)
                game_root.title(f'Mini TCG - vs IA Nivel {level}')
                
                # Variables necesarias
                player_life_var = tk.StringVar()
                ai_life_var = tk.StringVar()
                player_mana_var = tk.StringVar()
                player_deck_var = tk.StringVar()
                ai_deck_var = tk.StringVar()
                status_var = tk.StringVar()
                
                def on_game_over():
                    result = messagebox.askyesno(
                        "Fin del Juego",
                        "¿Jugar otra partida?",
                        parent=game_root
                    )
                    game_root.destroy()
                    if result:
                        start_vs_ai()
                    else:
                        root.deiconify()
                
                game = Game(player, ai_player, on_game_over)
                
                # Configurar UI
                game_gui.root = game_root
                game_gui.player_life_var = player_life_var
                game_gui.ai_life_var = ai_life_var
                game_gui.player_mana_var = player_mana_var
                game_gui.player_deck_var = player_deck_var
                game_gui.ai_deck_var = ai_deck_var
                game_gui.status_var = status_var
                game_gui.game = game
                
                game_gui.make_ui(game)
                game.start()
                
                def on_close():
                    game_root.destroy()
                    root.deiconify()
                
                game_root.protocol("WM_DELETE_WINDOW", on_close)
            
            # After deck selection, show difficulty selector
            level = show_difficulty_selector(on_difficulty_selected)
            
            if not level:
                root.deiconify()
        
        # First, show deck selector
        # root stays visible, will be hidden after deck selection
        show_deck_selector(on_deck_selected, parent=root, on_cancel=lambda: None)
    
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo iniciar el juego:\n{str(e)}")
        root.deiconify()


def start_multiplayer():
    """Launch multiplayer mode selector."""
    # DON'T hide root - we need it as parent for Toplevel windows
    
    try:
        from src.multiplayer.mode_selector import MultiplayerModeSelector
        
        def on_quick_match():
            """Handle Quick Match selection"""
            print("🎮 Quick Match selected - Starting matchmaking...")
            root.withdraw()  # Hide root AFTER selection
            _start_quick_match()
        
        def on_custom_match():
            """Handle Custom Match selection"""
            print("🎨 Custom Match selected - Opening Deck Selector...")
            # DON'T hide root yet - needed for deck selector
            _start_custom_match()
        
        def on_cancel():
            """Handle cancel"""
            print("❌ Multiplayer cancelled")
            # root stays visible, user back to main menu
        
        # Show mode selector (root stays visible as parent)
        selector = MultiplayerModeSelector(root, on_quick_match, on_custom_match, on_cancel)
        selector.show()
    
    except Exception as e:
        messagebox.showerror("Error", f"Could not start multiplayer:\n{str(e)}")
        root.deiconify()


def _start_quick_match():
    """Start Quick Match with random decks"""
    print("🎮 _start_quick_match called")
    from src.multiplayer.network_manager import NetworkManager
    from src.multiplayer.multiplayer_ui import MultiplayerGameUI
    
    # Connect to server (reads from server_config.txt)
    network = NetworkManager()
    
    print("🔌 Attempting to connect to server...")
    if not network.connect():
        print("❌ Connection failed")
        messagebox.showerror("Connection Error", "Could not connect to server.\nMake sure the server is running.")
        root.deiconify()
        return
    
    print("✅ Connected to server")
    
    # Create waiting window
    wait_window = tk.Toplevel(root)
    wait_window.title("Finding Match...")
    wait_window.geometry("400x200")
    wait_window.configure(bg='#1a1a2e')
    
    print("⏳ Waiting window created")
    
    tk.Label(
        wait_window,
        text="⏳ Searching for opponent...",
        font=('Arial', 14),
        bg='#1a1a2e',
        fg='white'
    ).pack(expand=True)
    
    cancel_btn = tk.Button(
        wait_window,
        text="Cancel",
        command=lambda: [wait_window.destroy(), network.disconnect(), root.deiconify()],
        font=('Arial', 11),
        bg='#e74c3c',
        fg='white'
    )
    cancel_btn.pack(pady=20)
    
    def on_match_found(data):
        """Called when match is found"""
        wait_window.destroy()
        
        # Create game UI
        game_window = tk.Toplevel()
        game_window.geometry("1400x900")
        game_window.title("TCG Multiplayer - Quick Match")
        
        # Get match data
        is_host = data.get('is_host', False)
        my_champ = data.get('my_champion', {})
        opp_champ = data.get('opponent_champion', {})
        
        # Create UI
        ui = MultiplayerGameUI(
            root=game_window,
            player_name="You",
            opponent_name="Opponent",
            on_play_card=lambda idx, spell_target=None: network.send_action({'action': 'play_card', 'card_index': idx, 'spell_target': spell_target}),
            on_end_turn=lambda: network.send_action({'action': 'end_turn'}),
            on_declare_attacks=lambda attackers, targets: network.send_action({'action': 'declare_attacks', 'attackers': attackers, 'targets': targets}),
            on_send_chat=lambda msg: network.sio.emit('chat_message', {'message': msg, 'room_id': network.room_id}),
            on_activate_ability=lambda idx: network.send_action({'action': 'activate_ability', 'card_index': idx})
        )
        # Attach network to UI to receive synchronized events like game_over
        try:
            if hasattr(ui, 'attach_network'):
                ui.attach_network(network)
            # Also register explicit callback for safety (ensure None return type)
            def _on_go(winner: str) -> None:
                game_window.after(0, lambda: ui._handle_game_over(winner))
            network.on_game_over = _on_go
        except Exception:
            pass
        
        # Setup state updates from server (thread-safe)
        def on_server_state(state):
            # Schedule UI update in main thread
            game_window.after(0, lambda: _update_ui_from_state(ui, state))
        
        # Setup chat message handler (thread-safe)
        def on_chat_message(data):
            sender = data.get('sender', 'Unknown')
            message = data.get('message', '')
            is_me = data.get('is_me', False)
            display_sender = "You" if is_me else sender
            # Schedule chat update in main thread
            game_window.after(0, lambda: ui.add_chat_message(display_sender, message))
        
        # Setup blocker request handler (thread-safe)
        def on_request_blockers(data):
            attackers = data.get('attackers', [])
            targets = data.get('targets', [])
            # Schedule blocker dialog in main thread
            game_window.after(0, lambda: _show_blocker_dialog(ui, network, attackers, targets))
        
        network.on_game_state_update = on_server_state
        network.on_chat_message = on_chat_message
        network.on_request_blockers = on_request_blockers
        
        # Handle opponent disconnect
        def on_opponent_disconnected():
            game_window.after(0, lambda: _handle_disconnect(game_window, network, "Quick Match"))
        
        network.on_opponent_disconnected = on_opponent_disconnected
        
        # Set champion info with proper descriptions
        my_champ_ability = f"{my_champ.get('passive_name', 'Unknown')}: {my_champ.get('passive_description', 'No description')}"
        opp_champ_ability = f"{opp_champ.get('passive_name', 'Unknown')}: {opp_champ.get('passive_description', 'No description')}"
        ui.set_my_champion(my_champ.get('name', 'Unknown'), my_champ_ability)
        ui.set_opponent_champion(opp_champ.get('name', 'Unknown'), opp_champ_ability)
        
        # Request initial state
        network.sio.emit('request_initial_state', {'room_id': network.room_id})
        
        # Log match info
        ui.log_action(f"🎮 Quick Match started!")
        ui.log_action(f"Your champion: {my_champ.get('name', 'Unknown')}")
        ui.log_action(f"Opponent: {opp_champ.get('name', 'Unknown')}")
        ui.add_system_message("Match found! Good luck!")
        
        # Set initial turn
        ui.set_turn(is_my_turn=is_host)
        
        def on_close():
            network.disconnect()
            game_window.destroy()
            root.deiconify()
        
        game_window.protocol("WM_DELETE_WINDOW", on_close)
    
    # Wrap callback to execute in main thread
    def safe_on_match_found(data):
        root.after(0, lambda: on_match_found(data))
    
    network.on_match_found = safe_on_match_found
    network.find_match("Player")
    
    print("📡 Match request sent, waiting for response...")
    # Keep the wait window alive until match is found
    wait_window.grab_set()  # Make modal
    root.wait_window(wait_window)  # Wait until destroyed
    print("✅ Wait window closed")


def _start_custom_match():
    """Start Custom Match with saved deck selection"""
    from src.deck_selector import show_deck_selector
    
    def on_deck_selected(player_cards, player_champion):
        """Called when player selects their deck."""
        # Hide root after deck selection
        root.withdraw()
        
        # Convert deck to serializable format
        deck_data = []
        for card in player_cards:
            deck_data.append({
                'name': card.name,
                'cost': card.cost,
                'damage': card.damage,
                'health': card.health,
                'card_type': card.card_type,
                'ability': card.ability,
                'ability_desc': getattr(card, 'ability_desc', ''),
                'ability_type': getattr(card, 'ability_type', ''),
                'spell_target': getattr(card, 'spell_target', ''),
                'spell_effect': getattr(card, 'spell_effect', ''),
                'description': getattr(card, 'description', '')
            })
        
        champion_data = {
            'name': player_champion.name,
            'title': player_champion.title,
            'starting_life': player_champion.starting_life,
            'passive_name': player_champion.passive_name,
            'passive_description': player_champion.passive_description,
            'ability_type': player_champion.ability_type,
            'ability_value': player_champion.ability_value
        }
        
        # Start custom match matchmaking
        _find_custom_match(deck_data, champion_data)
    
    # Show deck selector (root stays visible until deck selected)
    show_deck_selector(on_deck_selected, parent=root, on_cancel=lambda: None)


def _find_custom_match(deck_data: list, champion_data: dict):
    """Find match with custom deck"""
    from src.multiplayer.network_manager import NetworkManager
    from src.multiplayer.multiplayer_ui import MultiplayerGameUI
    
    # Connect to server (reads from server_config.txt)
    network = NetworkManager()
    
    if not network.connect():
        messagebox.showerror("Connection Error", "Could not connect to server.\nMake sure the server is running.")
        root.deiconify()
        return
    
    # Create waiting window
    wait_window = tk.Toplevel(root)
    wait_window.title("Finding Match...")
    wait_window.geometry("400x250")
    wait_window.configure(bg='#1a1a2e')
    
    tk.Label(
        wait_window,
        text="⏳ Searching for opponent...",
        font=('Arial', 14, 'bold'),
        bg='#1a1a2e',
        fg='white'
    ).pack(pady=20)
    
    tk.Label(
        wait_window,
        text=f"Champion: {champion_data.get('name', 'Unknown')}\nDeck: {len(deck_data)} cards",
        font=('Arial', 11),
        bg='#1a1a2e',
        fg='#ecf0f1'
    ).pack(pady=10)
    
    cancel_btn = tk.Button(
        wait_window,
        text="Cancel",
        command=lambda: [wait_window.destroy(), network.disconnect(), root.deiconify()],
        font=('Arial', 11),
        bg='#e74c3c',
        fg='white'
    )
    cancel_btn.pack(pady=20)
    
    def on_match_found(data):
        """Called when custom match is found"""
        wait_window.destroy()
        
        # Create game UI
        game_window = tk.Toplevel()
        game_window.geometry("1400x900")
        game_window.title("TCG Multiplayer - Custom Match")
        
        # Get match data
        is_host = data.get('is_host', False)
        my_champ = data.get('my_champion', {})
        opp_champ = data.get('opponent_champion', {})
        
        # Create UI
        ui = MultiplayerGameUI(
            root=game_window,
            player_name="You",
            opponent_name="Opponent",
            on_play_card=lambda idx, spell_target=None: network.send_action({'action': 'play_card', 'card_index': idx, 'spell_target': spell_target}),
            on_end_turn=lambda: network.send_action({'action': 'end_turn'}),
            on_declare_attacks=lambda attackers, targets: network.send_action({'action': 'declare_attacks', 'attackers': attackers, 'targets': targets}),
            on_send_chat=lambda msg: network.sio.emit('chat_message', {'message': msg, 'room_id': network.room_id}),
            on_activate_ability=lambda idx: network.send_action({'action': 'activate_ability', 'card_index': idx})
        )
        # Attach network to UI to receive synchronized events like game_over
        try:
            if hasattr(ui, 'attach_network'):
                ui.attach_network(network)
            def _on_go2(winner: str) -> None:
                game_window.after(0, lambda: ui._handle_game_over(winner))
            network.on_game_over = _on_go2
        except Exception:
            pass
        
        # Setup state updates from server (thread-safe)
        def on_server_state(state):
            # Schedule UI update in main thread
            game_window.after(0, lambda: _update_ui_from_state(ui, state))
        
        # Setup chat message handler (thread-safe)
        def on_chat_message(data):
            sender = data.get('sender', 'Unknown')
            message = data.get('message', '')
            is_me = data.get('is_me', False)
            display_sender = "You" if is_me else sender
            # Schedule chat update in main thread
            game_window.after(0, lambda: ui.add_chat_message(display_sender, message))
        
        # Setup blocker request handler (thread-safe)
        def on_request_blockers(data):
            attackers = data.get('attackers', [])
            targets = data.get('targets', [])
            # Schedule blocker dialog in main thread
            game_window.after(0, lambda: _show_blocker_dialog(ui, network, attackers, targets))
        
        network.on_game_state_update = on_server_state
        network.on_chat_message = on_chat_message
        network.on_request_blockers = on_request_blockers
        
        # Handle opponent disconnect
        def on_opponent_disconnected():
            game_window.after(0, lambda: _handle_disconnect(game_window, network, "Custom Match"))
        
        network.on_opponent_disconnected = on_opponent_disconnected
        
        # Set champion info with proper descriptions
        my_champ_ability = f"{my_champ.get('passive_name', 'Unknown')}: {my_champ.get('passive_description', 'No description')}"
        opp_champ_ability = f"{opp_champ.get('passive_name', 'Unknown')}: {opp_champ.get('passive_description', 'No description')}"
        ui.set_my_champion(my_champ.get('name', 'Unknown'), my_champ_ability)
        ui.set_opponent_champion(opp_champ.get('name', 'Unknown'), opp_champ_ability)
        
        # Request initial state
        network.sio.emit('request_initial_state', {'room_id': network.room_id})
        
        # Log match info
        ui.log_action(f"🎨 Custom Match started!")
        ui.log_action(f"Your champion: {my_champ.get('name', 'Unknown')}")
        ui.log_action(f"Your deck: {len(deck_data)} cards")
        ui.log_action(f"Opponent: {opp_champ.get('name', 'Unknown')}")
        ui.add_system_message("Match found! Good luck!")
        
        # Set initial turn
        ui.set_turn(is_my_turn=is_host)
        
        def on_close():
            network.disconnect()
            game_window.destroy()
            root.deiconify()
        
        game_window.protocol("WM_DELETE_WINDOW", on_close)
    
    # Wrap callback to execute in main thread
    def safe_on_match_found(data):
        root.after(0, lambda: on_match_found(data))
    
    network.on_match_found = safe_on_match_found
    network.find_custom_match("Player", deck_data, champion_data)


def _handle_disconnect(game_window, network, match_type: str):
    """Handle opponent disconnect - show message and return to main menu"""
    from tkinter import messagebox
    
    # Check if window still exists
    try:
        if not game_window.winfo_exists():
            # Window already destroyed, just disconnect and return
            network.disconnect()
            root.deiconify()
            return
    except:
        # Window is invalid, just disconnect and return
        network.disconnect()
        root.deiconify()
        return
    
    # Disconnect from server
    network.disconnect()
    
    # Show disconnect message with root as parent (safer)
    root.deiconify()  # Show root first
    messagebox.showwarning(
        "Oponente Desconectado",
        f"Tu oponente se ha desconectado de la partida.\n\nSerás devuelto al menú principal.",
        parent=root
    )
    
    # Close game window
    try:
        game_window.destroy()
    except:
        pass  # Window might already be destroyed


def _show_blocker_dialog(ui, network, attackers, targets):
    """Show dialog for defender to select blockers"""
    import tkinter as tk
    
    # Create blocker selection window
    blocker_window = tk.Toplevel()
    blocker_window.title("Declare Blockers")
    blocker_window.geometry("600x700")
    blocker_window.configure(bg='#1a1a2e')
    blocker_window.grab_set()
    
    tk.Label(
        blocker_window,
        text="🛡️ The opponent is attacking! Declare blockers",
        font=('Arial', 14, 'bold'),
        bg='#1a1a2e',
        fg='#e74c3c'
    ).pack(pady=10)
    
    # Store blockers: {attacker_idx: blocker_idx}
    blockers = {}
    
    # Create frame for attackers and blocker selection
    scroll_frame = tk.Frame(blocker_window, bg='#1a1a2e')
    scroll_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
    
    # Show each attacking card that targets the player
    for i, attacker_idx in enumerate(attackers):
        if i >= len(targets):
            continue
        
        target = targets[i]
        if target != "player":
            continue  # Skip attacks targeting opponent's creatures
        
        # Frame for this attacker
        atk_frame = tk.Frame(scroll_frame, bg='#2c3e50', relief=tk.RAISED, borderwidth=2)
        atk_frame.pack(fill=tk.X, pady=5)
        
        # Attacker info (get from opponent active zone)
        if attacker_idx < len(ui.opponent_active):
            attacker_card = ui.opponent_active[attacker_idx]
            
            tk.Label(
                atk_frame,
                text=f"⚔️ Incoming attack: {attacker_card.name} ({attacker_card.attack} ATK)",
                font=('Arial', 11, 'bold'),
                bg='#2c3e50',
                fg='#e74c3c'
            ).pack(pady=5)
            
            # Blocker selection variable
            blocker_var = tk.StringVar(value="none")
            
            # Option to not block
            tk.Radiobutton(
                atk_frame,
                text="❌ Don't block (take damage)",
                variable=blocker_var,
                value="none",
                font=('Arial', 10),
                bg='#2c3e50',
                fg='white',
                selectcolor='#34495e',
                activebackground='#2c3e50',
                activeforeground='white'
            ).pack(anchor='w', padx=20, pady=2)
            
            # Options for available blockers
            if ui.my_active:
                tk.Label(
                    atk_frame,
                    text="Or block with:",
                    font=('Arial', 9, 'italic'),
                    bg='#2c3e50',
                    fg='#95a5a6'
                ).pack(anchor='w', padx=20, pady=(5, 2))
                
                for j, my_card in enumerate(ui.my_active):
                    if not my_card.is_tapped:  # Solo tropas no tappeadas pueden bloquear
                        tk.Radiobutton(
                            atk_frame,
                            text=f"  🛡️ {my_card.name} ({my_card.defense} HP / {my_card.attack} ATK)",
                            variable=blocker_var,
                            value=f"card_{j}",
                            font=('Arial', 9),
                            bg='#2c3e50',
                            fg='#ecf0f1',
                            selectcolor='#34495e',
                            activebackground='#2c3e50',
                            activeforeground='white'
                        ).pack(anchor='w', padx=40, pady=1)
            
            # Store the blocker selection for this attacker
            blockers[attacker_idx] = blocker_var
    
    # Confirm button
    def confirm_blockers():
        # Build blockers dict
        final_blockers = {}
        for attacker_idx, blocker_var in blockers.items():
            blocker_str = blocker_var.get()
            if blocker_str.startswith("card_"):
                blocker_idx = int(blocker_str.split("_")[1])
                final_blockers[attacker_idx] = blocker_idx
        
        # Send blockers to server
        network.send_action({'action': 'declare_blockers', 'blockers': final_blockers})
        
        # Log
        if final_blockers:
            ui.log_action(f"🛡️ Declared {len(final_blockers)} blocker(s)")
        else:
            ui.log_action(f"🛡️ No blockers declared")
        
        # Close window
        blocker_window.destroy()
    
    tk.Button(
        blocker_window,
        text="🛡️ CONFIRM BLOCKERS",
        command=confirm_blockers,
        font=('Arial', 12, 'bold'),
        bg='#27ae60',
        fg='white',
        width=20,
        height=2
    ).pack(pady=15)
    
    # Cancel button (no blockers)
    def cancel_blockers():
        # Send empty blockers
        network.send_action({'action': 'declare_blockers', 'blockers': {}})
        ui.log_action(f"🛡️ No blockers declared")
        blocker_window.destroy()
    
    tk.Button(
        blocker_window,
        text="Skip Blocking",
        command=cancel_blockers,
        font=('Arial', 10),
        bg='#e74c3c',
        fg='white',
        width=15
    ).pack(pady=5)


def _update_ui_from_state(ui, state: dict):
    """Update UI from server state"""
    from src.multiplayer.multiplayer_ui import CardDisplay, MultiplayerGameUI
    
    # Update player stats
    my_state = state.get('my_state', {})
    opponent_state = state.get('opponent_state', {})
    
    print(f"📊 Update UI - My hand: {len(my_state.get('hand', []))} cards, Opponent hand: {opponent_state.get('hand_count', 0)} cards")
    
    # Life change animations: capture previous values
    prev_my_life = ui.my_life
    prev_opp_life = ui.opponent_life

    ui.update_player_stats(
        life=my_state.get('life', 25),
        mana=my_state.get('mana', 0),
        max_mana=my_state.get('max_mana', 0)
    )
    
    ui.update_opponent_stats(
        life=opponent_state.get('life', 25),
        mana=opponent_state.get('mana', 0),
        max_mana=opponent_state.get('max_mana', 0),
        hand_count=opponent_state.get('hand_count', 0)
    )

    # Trigger life animations if changed
    try:
        new_my_life = my_state.get('life', 25)
        new_opp_life = opponent_state.get('life', 25)
        if isinstance(prev_my_life, int) and isinstance(new_my_life, int):
            delta_my = new_my_life - prev_my_life
            if delta_my != 0:
                ui.animate_my_life_change(delta_my)
        if isinstance(prev_opp_life, int) and isinstance(new_opp_life, int):
            delta_opp = new_opp_life - prev_opp_life
            if delta_opp != 0:
                ui.animate_opp_life_change(delta_opp)
    except Exception:
        pass
    
    # Update hand
    hand_cards = []
    for card_data in my_state.get('hand', []):
        # DEBUG: Print card data
        print(f"🃏 HAND CARD: {card_data.get('name')} - ATK:{card_data.get('damage')} HP:{card_data.get('health')} Type:{card_data.get('card_type')}")
        
        # Build abilities list with descriptions (for troops and spells)
        abilities_list = []
        card_type = card_data.get('card_type', 'troop').lower()
        
        if card_type == 'spell':
            # For spells, use description or spell_effect
            spell_desc = card_data.get('description', '') or card_data.get('spell_effect', '')
            if spell_desc:
                abilities_list.append(spell_desc)
        elif card_data.get('ability'):
            # For troops, use ability and ability_desc
            ability_name = card_data.get('ability', '')
            ability_desc = card_data.get('ability_desc', '')
            if ability_desc:
                abilities_list.append(f"{ability_name}: {ability_desc}")
            else:
                abilities_list.append(ability_name)
        
        hand_cards.append(CardDisplay(
            name=card_data.get('name', 'Unknown'),
            cost=card_data.get('cost', 0),
            attack=card_data.get('damage', 0),
            defense=card_data.get('health', 0),
            card_type=card_data.get('card_type', 'Troop'),
            abilities=abilities_list
        ))
    ui.update_my_hand(hand_cards)
    
    # Update active zones
    my_active = []
    for card_data in my_state.get('active_zone', []):
        # Build abilities list with descriptions (for troops and spells)
        abilities_list = []
        card_type = card_data.get('card_type', 'troop').lower()
        
        if card_type == 'spell':
            # For spells, use description or spell_effect
            spell_desc = card_data.get('description', '') or card_data.get('spell_effect', '')
            if spell_desc:
                abilities_list.append(spell_desc)
        elif card_data.get('ability'):
            # For troops, use ability and ability_desc
            ability_name = card_data.get('ability', '')
            ability_desc = card_data.get('ability_desc', '')
            if ability_desc:
                abilities_list.append(f"{ability_name}: {ability_desc}")
            else:
                abilities_list.append(ability_name)
        
        # Check if has activated ability (like Invocar Aliado)
        has_activated = card_data.get('ability_type', '') == 'activated'
        
        my_active.append(CardDisplay(
            name=card_data.get('name', 'Unknown'),
            cost=card_data.get('cost', 0),
            attack=card_data.get('damage', 0),
            defense=card_data.get('current_health', 0),
            card_type=card_data.get('card_type', 'Troop'),
            abilities=abilities_list,
            can_attack=card_data.get('ready', False),
            is_tapped=not card_data.get('ready', True),
            has_activated_ability=has_activated
        ))
    # Capture previous state for animations
    prev_my_active = list(getattr(ui, 'my_active', []))
    prev_opp_active = list(getattr(ui, 'opponent_active', []))
    prev_my_ready = [not c.is_tapped for c in prev_my_active]
    prev_opp_ready = [not c.is_tapped for c in prev_opp_active]
    prev_my_def = [c.defense for c in prev_my_active]
    prev_opp_def = [c.defense for c in prev_opp_active]

    ui.update_my_active(my_active)
    
    opp_active = []
    for card_data in opponent_state.get('active_zone', []):
        # Build abilities list with descriptions (for troops and spells)
        abilities_list = []
        card_type = card_data.get('card_type', 'troop').lower()
        
        if card_type == 'spell':
            # For spells, use description or spell_effect
            spell_desc = card_data.get('description', '') or card_data.get('spell_effect', '')
            if spell_desc:
                abilities_list.append(spell_desc)
        elif card_data.get('ability'):
            # For troops, use ability and ability_desc
            ability_name = card_data.get('ability', '')
            ability_desc = card_data.get('ability_desc', '')
            if ability_desc:
                abilities_list.append(f"{ability_name}: {ability_desc}")
            else:
                abilities_list.append(ability_name)
        
        opp_active.append(CardDisplay(
            name=card_data.get('name', 'Unknown'),
            cost=card_data.get('cost', 0),
            attack=card_data.get('damage', 0),
            defense=card_data.get('current_health', 0),
            card_type=card_data.get('card_type', 'Troop'),
            abilities=abilities_list,
            can_attack=False,
            is_tapped=not card_data.get('ready', True)
        ))
    ui.update_opponent_active(opp_active)
    
    # --- Post-update animations based on diffs ---
    # Build new readiness/defense from server data
    new_my_ready = [c.get('ready', False) for c in my_state.get('active_zone', [])]
    new_opp_ready = [c.get('ready', False) for c in opponent_state.get('active_zone', [])]
    new_my_def = [c.get('current_health', 0) for c in my_state.get('active_zone', [])]
    new_opp_def = [c.get('current_health', 0) for c in opponent_state.get('active_zone', [])]

    # Detect my attackers that became tapped (attack/block resolved)
    my_tapped_after = []
    for i in range(min(len(prev_my_ready), len(new_my_ready))):
        if prev_my_ready[i] and not new_my_ready[i]:
            my_tapped_after.append(i)
    if my_tapped_after:
        ui.animate_attack_my(my_tapped_after)

    # Detect opponent attackers that became tapped
    opp_tapped_after = []
    for i in range(min(len(prev_opp_ready), len(new_opp_ready))):
        if prev_opp_ready[i] and not new_opp_ready[i]:
            opp_tapped_after.append(i)
    if opp_tapped_after:
        ui.animate_attack_opp(opp_tapped_after)

    # Damage flashes for cards that lost defense
    for i in range(min(len(prev_my_def), len(new_my_def))):
        if new_my_def[i] < prev_my_def[i]:
            ui.animate_damage_my(i)
    for i in range(min(len(prev_opp_def), len(new_opp_def))):
        if new_opp_def[i] < prev_opp_def[i]:
            ui.animate_damage_opp(i)

    # Update opponent hand count
    ui.update_opponent_hand(opponent_state.get('hand_count', 0))
    
    # Update turn
    ui.set_turn(state.get('is_my_turn', False))
    
    # Check if waiting for blockers should be reset
    # Reset if we were waiting AND at least one of our creatures is now tapped (combat resolved)
    if ui.waiting_for_blockers and state.get('is_my_turn', False):
        # Check if any active creature is tapped (indicating combat happened)
        has_tapped_creatures = any(not card.get('ready', True) for card in my_state.get('active_zone', []))
        if has_tapped_creatures:
            ui.reset_waiting_state()


# Main menu
root = tk.Tk()
root.title("Mini TCG - Menú Principal")
root.geometry("850x700")
root.configure(bg='#0f0f1e')

# Centrar ventana
root.update_idletasks()
width = root.winfo_width()
height = root.winfo_height()
x = (root.winfo_screenwidth() // 2) - (width // 2)
y = (root.winfo_screenheight() // 2) - (height // 2)
root.geometry(f'{width}x{height}+{x}+{y}')

# Title
title_frame = tk.Frame(root, bg='#0f0f1e')
title_frame.pack(pady=20)

tk.Label(title_frame, text="🎮 MINI TCG", 
        bg='#0f0f1e', fg='#00ffcc', font=('Arial', 28, 'bold')).pack()

tk.Label(title_frame, text="Trading Card Game con Sistema de IA Inteligente", 
        bg='#0f0f1e', fg='#888888', font=('Arial', 11)).pack(pady=3)

# Menu options container
menu_container = tk.Frame(root, bg='#0f0f1e')
menu_container.pack(expand=True, pady=10)

# Botones principales (fila única)
buttons_frame = tk.Frame(menu_container, bg='#0f0f1e')
buttons_frame.pack(pady=5)

# Botón: Constructor de Mazos
btn1_frame = tk.Frame(buttons_frame, bg='#1a1a2e', relief='raised', borderwidth=3)
btn1_frame.pack(side='left', padx=10, pady=5)
tk.Label(btn1_frame, text="🃏 CREAR MAZO", 
        bg='#1a1a2e', fg='#3498db', font=('Arial', 14, 'bold')).pack(pady=(10, 3))
tk.Label(btn1_frame, text="Construye tu mazo\npersonalizado carta por carta", 
        bg='#1a1a2e', fg='#cccccc', font=('Arial', 8), justify='center').pack(pady=(0, 8))
btn1 = tk.Button(btn1_frame, text="▶ CREAR", command=start_deck_builder,
         bg='#3498db', fg='white', font=('Arial', 9, 'bold'),
         width=18, cursor='hand2')
btn1.pack(pady=8)

# Botón: Jugar vs IA
btn2_frame = tk.Frame(buttons_frame, bg='#1a1a2e', relief='raised', borderwidth=3)
btn2_frame.pack(side='left', padx=10, pady=5)
tk.Label(btn2_frame, text="🎯 JUGAR VS IA", 
        bg='#1a1a2e', fg='#2ecc71', font=('Arial', 14, 'bold')).pack(pady=(10, 3))
tk.Label(btn2_frame, text="Elige dificultad (1-10)\ny enfrenta a la IA optimizada", 
        bg='#1a1a2e', fg='#cccccc', font=('Arial', 8), justify='center').pack(pady=(0, 8))
btn2 = tk.Button(btn2_frame, text="▶ JUGAR", command=start_vs_ai,
         bg='#2ecc71', fg='white', font=('Arial', 9, 'bold'),
         width=18, cursor='hand2')
btn2.pack(pady=8)

# Botón: Multijugador
btn3_frame = tk.Frame(buttons_frame, bg='#1a1a2e', relief='raised', borderwidth=3)
btn3_frame.pack(side='left', padx=10, pady=5)
tk.Label(btn3_frame, text="🌐 MULTIJUGADOR", 
        bg='#1a1a2e', fg='#e74c3c', font=('Arial', 14, 'bold')).pack(pady=(10, 3))
tk.Label(btn3_frame, text="Juega contra otros\njugadores en línea", 
        bg='#1a1a2e', fg='#cccccc', font=('Arial', 8), justify='center').pack(pady=(0, 8))
btn3 = tk.Button(btn3_frame, text="▶ MULTIJUGADOR", command=start_multiplayer,
         bg='#e74c3c', fg='white', font=('Arial', 9, 'bold'),
         width=18, cursor='hand2')
btn3.pack(pady=8)

# Footer
footer_frame = tk.Frame(root, bg='#0f0f1e')
footer_frame.pack(side='bottom', pady=20)

tk.Label(footer_frame, text="8 Campeones • 10 Niveles de Dificultad • Sistema de IA Optimizado", 
        bg='#0f0f1e', fg='#666666', font=('Arial', 9)).pack()

root.mainloop()
