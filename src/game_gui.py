"""
Main GUI for the TCG minigame.
Refactored to use modular components.
"""

import os
import tkinter as tk
from tkinter import messagebox
from typing import List, Optional, Dict, Union, Tuple

# Import game components
from .models import Card, Player, CardWidget
from .game_logic import Game
from .cards import build_random_deck

# Optional Pillow support for nicer images
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False


def make_ui(game: Game):
    selected_attackers = set()
    attack_targets: Dict[int, Union[str, Tuple[str, int]]] = {}  # Maps attacker index -> 'player' or ('card', card_index)
    # image caches to keep PhotoImage references (avoid attaching dynamic attrs to tk widgets)
    hand_images: List = []
    ai_hand_images: List = []
    ai_active_images: List = []
    player_active_images: List = []
    # tooltip management
    tooltip_window = None
    tooltip_after_id = None
    tooltip_widget = None

    def show_tooltip(widget, card: Card):
        nonlocal tooltip_window, tooltip_after_id, tooltip_widget
        if tooltip_after_id:
            root.after_cancel(tooltip_after_id)
        tooltip_widget = widget
        def _show():
            nonlocal tooltip_window
            if tooltip_window:
                tooltip_window.destroy()
            # Check if widget still exists before trying to get its position
            try:
                if not widget.winfo_exists():
                    return
            except Exception:
                return
            if card.ability and card.ability_desc:
                try:
                    tooltip_window = tk.Toplevel(root)
                    tooltip_window.wm_overrideredirect(True)
                    tooltip_window.wm_overrideredirect(True)
                    tooltip_window.wm_geometry(f"+{widget.winfo_rootx()+10}+{widget.winfo_rooty()+10}")
                    lbl = tk.Label(tooltip_window, text=f"{card.ability}: {card.ability_desc}", bg='lightyellow', relief='solid', bd=1, padx=6, pady=4, font=('Arial', 10))
                    lbl.pack()
                except Exception:
                    # Widget was destroyed, ignore
                    pass
        tooltip_after_id = root.after(1000, _show)

    def hide_tooltip(event=None):
        nonlocal tooltip_window, tooltip_after_id, tooltip_widget
        if tooltip_after_id:
            root.after_cancel(tooltip_after_id)
            tooltip_after_id = None
        if tooltip_window:
            tooltip_window.destroy()
            tooltip_window = None
        tooltip_widget = None

    def toggle_attacker(idx: int):
        # idx refers to index in player.active_zone
        if idx < 0 or idx >= len(game.player.active_zone):
            return
        card = game.player.active_zone[idx]
        if not card.ready:
            return
        if idx in selected_attackers:
            selected_attackers.remove(idx)
        else:
            selected_attackers.add(idx)
        status_var.set(f"Selected attackers: {[game.player.active_zone[i].name for i in sorted(selected_attackers)]}")

    # Animation helpers
    def _widget_root_coords(w):
        # return coordinates relative to root window
        try:
            rx = w.winfo_rootx() - root.winfo_rootx()
            ry = w.winfo_rooty() - root.winfo_rooty()
            return rx, ry, w.winfo_width(), w.winfo_height()
        except Exception:
            return 0, 0, 0, 0

    def animate_move(photo: Optional[tk.PhotoImage], x0: int, y0: int, x1: int, y1: int, duration=400, steps=20, on_done=None):
        if photo is None:
            if on_done:
                root.after(1, on_done)
            return
        lbl = tk.Label(root, image=photo, bd=0)
        lbl.place(x=x0, y=y0)
        dx = (x1 - x0) / steps
        dy = (y1 - y0) / steps
        i = 0
        def step():
            nonlocal i
            i += 1
            try:
                lbl.place(x=x0 + dx * i, y=y0 + dy * i)
            except Exception:
                pass
            if i < steps:
                root.after(int(duration/steps), step)
            else:
                lbl.destroy()
                if on_done:
                    on_done()
        step()

    def animate_play_from_hand(hand_idx: int, on_complete=None):
        # find source widget in hand_frame
        slaves = hand_frame.grid_slaves(row=0, column=hand_idx)
        if slaves:
            src = slaves[0]
        else:
            # fallback: no widget, just complete
            if on_complete:
                root.after(1, on_complete)
            return
        sx, sy, sw, sh = _widget_root_coords(src)
        # target: center of player_active_frame area
        tx = player_active_frame.winfo_rootx() - root.winfo_rootx() + 10
        ty = player_active_frame.winfo_rooty() - root.winfo_rooty() + 10
        # pick image for hand if available
        photo = None
        try:
            photo = hand_images[hand_idx]
        except Exception:
            photo = None
        animate_move(photo, sx, sy, tx, ty, duration=450, steps=18, on_done=on_complete)

    def animate_play_from_ai(card: Card, on_complete=None):
        # find widget in ai_hand_frame that was associated to this card
        src_widget = None
        for w in ai_hand_frame.winfo_children():
            if getattr(w, 'card', None) is card:
                src_widget = w
                break
        if src_widget is None:
            # fallback: complete immediately
            if on_complete:
                root.after(1, on_complete)
            return
        sx, sy, sw, sh = _widget_root_coords(src_widget)
        tx = ai_active_frame.winfo_rootx() - root.winfo_rootx() + 10
        ty = ai_active_frame.winfo_rooty() - root.winfo_rooty() + 10
        # find photo for this ai hand index
        photo = None
        try:
            # locate index of card in ai.hand
            idx = game.ai.hand.index(card)
            photo = ai_hand_images[idx]
        except Exception:
            photo = None
        animate_move(photo, sx, sy, tx, ty, duration=450, steps=18, on_done=on_complete)

    def cancel_selection():
        selected_attackers.clear()
        attack_targets.clear()
        status_var.set(f"Turn: {game.turn}")

    def declare_attack():
        if not selected_attackers:
            return
        
        # Ask for targets for each attacker
        for atk_idx in sorted(selected_attackers):
            target = ask_attack_target(atk_idx)
            if target is not None:
                attack_targets[atk_idx] = target
        
        # Execute attacks
        attacker_indices = sorted(selected_attackers)
        ids = attacker_indices[:]
        def animate_one(idx_list):
            if not idx_list:
                # after all animations, perform resolution
                game.declare_attacks_with_targets(attack_targets, owner='player')
                selected_attackers.clear()
                attack_targets.clear()
                update_ui()
                return
            idx = idx_list.pop(0)
            # get widget for attacker (calculate row/col from index)
            cards_per_row = 8
            row = idx // cards_per_row
            col = idx % cards_per_row
            slaves = player_active_frame.grid_slaves(row=row, column=col)
            if not slaves:
                # skip animation if widget missing
                root.after(1, lambda: animate_one(idx_list))
                return
            atk_w = slaves[0]
            ax, ay, aw, ah = _widget_root_coords(atk_w)
            # small forward movement towards AI
            target_x = ax
            target_y = ay - 30
            # use associated image if available
            photo = None
            try:
                photo = player_active_images[idx]
            except Exception:
                photo = None
            def after_move_back():
                # short pause then next
                root.after(120, lambda: animate_one(idx_list))
            # move forward then back
            animate_move(photo, ax, ay, target_x, target_y, duration=160, steps=8, on_done=lambda: animate_move(photo, target_x, target_y, ax, ay, duration=160, steps=8, on_done=after_move_back))
        animate_one(ids)

    def update_ui():
        p = game.player
        a = game.ai
        player_life_var.set(f'Player Life: {p.life}')
        ai_life_var.set(f'AI Life: {a.life}')
        player_mana_var.set(f'Mana: {p.mana}/{p.max_mana}')
        player_deck_var.set(f'Deck: {p.deck.count()}')
        ai_deck_var.set(f'Deck: {a.deck.count()}')
        for widget in hand_frame.winfo_children():
            widget.destroy()
        # Preload images if possible for player's hand
        hand_images.clear()
        for i, card in enumerate(p.hand):
            if card.card_type == 'spell':
                # Show adjusted cost for spells if champion has discount
                actual_cost = game.get_spell_cost(card, p)
                cost_text = f"{actual_cost}" if actual_cost == card.cost else f"{actual_cost} ({card.cost})"
                text = f"⚡ {card.name} (Cost:{cost_text})\n{card.description or ''}"
            else:
                text = f"{card.name} (Cost:{card.cost} Dmg:{card.damage})"
            image_path = getattr(card, 'image_path', None)
            if PIL_AVAILABLE and image_path and os.path.isfile(image_path):
                try:
                    img = Image.open(image_path).resize((64, 96))
                    photo = ImageTk.PhotoImage(img)
                    hand_images.append(photo)
                    btn = tk.Button(hand_frame, image=photo, text=text, compound='top', command=lambda idx=i: on_play(idx))
                except Exception:
                    btn = tk.Button(hand_frame, text=text, command=lambda idx=i: on_play(idx), width=30)
            else:
                btn = tk.Button(hand_frame, text=text, command=lambda idx=i: on_play(idx), width=20, height=5)
            # Color code spell cards
            if card.card_type == 'spell':
                try:
                    btn.config(bg='#9c27b0', fg='white')
                except Exception:
                    pass
            # attach tooltip for ability
            btn.bind('<Enter>', lambda e, c=card, w=btn: (hide_tooltip(), show_tooltip(w, c)))
            btn.bind('<Leave>', hide_tooltip)
            # place hand cards using grid to keep layout stable inside the canvas window
            btn.grid(row=0, column=i, padx=4, pady=4)
        # update canvas scrollregion to encompass new content
        try:
            hand_frame.update_idletasks()
            hand_canvas.config(scrollregion=hand_canvas.bbox('all'))
        except Exception:
            pass
        # Update AI hand (show backs)
        for widget in ai_hand_frame.winfo_children():
            widget.destroy()
        ai_hand_images.clear()
        back_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'cards', 'card_back.png')
        for i in range(len(a.hand)):
            lbl = None
            if PIL_AVAILABLE and os.path.isfile(back_path):
                try:
                    img = Image.open(back_path).resize((48, 72))
                    photo = ImageTk.PhotoImage(img)
                    ai_hand_images.append(photo)
                    lbl = CardWidget(ai_hand_frame, image=photo, bg='#ddd')
                    # associate widget with card object for animations
                    try:
                        lbl.card = a.hand[i]
                    except Exception:
                        pass
                except Exception as e:
                    print(f"⚠️ Error loading card back: {e}")
                    lbl = CardWidget(ai_hand_frame, text='[Back]', bg='#666', fg='white', width=6, height=3)
            else:
                lbl = CardWidget(ai_hand_frame, text='[Back]', bg='#666', fg='white', width=6, height=3)
            
            if lbl:
                lbl.grid(row=0, column=i, padx=2)
        # Rest zone removed: cards now enter `active_zone` tapped, so no rest UI

        # Update active areas (try to show images when available)
        for widget in ai_active_frame.winfo_children():
            widget.destroy()
        ai_active_images.clear()
        cards_per_row = 8
        for i, card in enumerate(game.ai.active_zone):
            row = i // cards_per_row
            col = i % cards_per_row
            txt = f"{card.name}\nATK: {card.damage}  HP: {card.current_health}"
            image_path = getattr(card, 'image_path', None)
            if PIL_AVAILABLE and image_path and os.path.isfile(image_path):
                try:
                    img = Image.open(image_path)
                    # if tapped (not ready) show rotated image
                    if not card.ready:
                        img = img.rotate(90, expand=True)
                    img = img.resize((64, 96))
                    photo = ImageTk.PhotoImage(img)
                    ai_active_images.append(photo)
                    lbl = tk.Label(ai_active_frame, image=photo, text=f"{card.name}\nATK: {card.damage}  HP: {card.current_health}", compound='top', relief='ridge')
                except Exception:
                    lbl = tk.Label(ai_active_frame, text=txt, relief='ridge', width=10, height=5)
            else:
                lbl = tk.Label(ai_active_frame, text=txt, relief='ridge', width=10, height=5)
            lbl.bind('<Enter>', lambda e, c=card, w=lbl: (hide_tooltip(), show_tooltip(w, c)))
            lbl.bind('<Leave>', hide_tooltip)
            lbl.grid(row=row, column=col, padx=4, pady=2)
        # update AI active canvas scrollregion
        try:
            ai_active_frame.update_idletasks()
            ai_active_canvas.config(scrollregion=ai_active_canvas.bbox('all'))
        except Exception:
            pass

        for widget in player_active_frame.winfo_children():
            widget.destroy()
        player_active_images.clear()
        cards_per_row = 8
        for i, card in enumerate(game.player.active_zone):
            row = i // cards_per_row
            col = i % cards_per_row
            txt = f"{card.name}\nATK: {card.damage}  HP: {card.current_health}"
            image_path = getattr(card, 'image_path', None)
            if PIL_AVAILABLE and image_path and os.path.isfile(image_path):
                try:
                    img = Image.open(image_path)
                    # if tapped (not ready) show rotated image
                    if not card.ready:
                        img = img.rotate(90, expand=True)
                    img = img.resize((64, 96))
                    photo = ImageTk.PhotoImage(img)
                    player_active_images.append(photo)
                    if card.ready:
                        # Check if card has activated ability
                        if card.ability and card.ability_type == 'activated':
                            # Create frame to hold both buttons
                            card_frame = tk.Frame(player_active_frame, bg='#c8c8f0')
                            btn = tk.Button(card_frame, image=photo, text=f"{card.name}\nATK: {card.damage}  HP: {card.current_health}", compound='top', relief='raised', command=lambda idx=i: toggle_attacker(idx))
                            btn.pack()
                            ability_btn = tk.Button(card_frame, text='⚡', command=lambda idx=i: on_activate_ability(idx), width=3, bg='#ffeb3b', font=('Arial', 10, 'bold'))
                            ability_btn.pack()
                            btn = card_frame
                        else:
                            btn = tk.Button(player_active_frame, image=photo, text=f"{card.name}\nATK: {card.damage}  HP: {card.current_health}", compound='top', relief='raised', command=lambda idx=i: toggle_attacker(idx))
                    else:
                        btn = tk.Label(player_active_frame, image=photo, text=f"{card.name}\nATK: {card.damage}  HP: {card.current_health}", compound='top', relief='sunken')
                except Exception:
                    if card.ready:
                        if card.ability and card.ability_type == 'activated':
                            card_frame = tk.Frame(player_active_frame, bg='#c8c8f0')
                            btn = tk.Button(card_frame, text=txt, relief='raised', command=lambda idx=i: toggle_attacker(idx), width=10, height=5)
                            btn.pack()
                            ability_btn = tk.Button(card_frame, text='⚡', command=lambda idx=i: on_activate_ability(idx), width=3, bg='#ffeb3b')
                            ability_btn.pack()
                            btn = card_frame
                        else:
                            btn = tk.Button(player_active_frame, text=txt, relief='raised', command=lambda idx=i: toggle_attacker(idx), width=10, height=5)
                    else:
                        btn = tk.Label(player_active_frame, text=txt, relief='sunken', width=10, height=5)
            else:
                if card.ready:
                    if card.ability and card.ability_type == 'activated':
                        card_frame = tk.Frame(player_active_frame, bg='#c8c8f0')
                        btn = tk.Button(card_frame, text=txt, relief='raised', command=lambda idx=i: toggle_attacker(idx), width=10, height=5)
                        btn.pack()
                        ability_btn = tk.Button(card_frame, text='⚡', command=lambda idx=i: on_activate_ability(idx), width=3, bg='#ffeb3b')
                        ability_btn.pack()
                        btn = card_frame
                    else:
                        btn = tk.Button(player_active_frame, text=txt, relief='raised', command=lambda idx=i: toggle_attacker(idx), width=10, height=5)
                else:
                    btn = tk.Label(player_active_frame, text=txt, relief='sunken', width=10, height=5)
            # highlight if selected
            if card.ready and i in selected_attackers:
                try:
                    btn.config(bg='lightgreen')
                except Exception:
                    pass
            btn.bind('<Enter>', lambda e, c=card, w=btn: (hide_tooltip(), show_tooltip(w, c)))
            btn.bind('<Leave>', hide_tooltip)
            btn.grid(row=row, column=col, padx=4, pady=2)
        # update player active canvas scrollregion
        try:
            player_active_frame.update_idletasks()
            player_active_canvas.config(scrollregion=player_active_canvas.bbox('all'))
        except Exception:
            pass
        # Update action log
        log_listbox.delete(0, tk.END)
        for entry in game.action_log[-30:]:
            log_listbox.insert(tk.END, entry)
        status_var.set(f"Turn: {game.turn}")

    def on_play(index):
        # only animate/play if the player can afford the card
        if index < 0 or index >= len(game.player.hand):
            return
        card = game.player.hand[index]
        if card.cost > game.player.mana:
            status_var.set('Not enough mana!')
            root.after(800, lambda: status_var.set(f"Turn: {game.turn}"))
            return

        # Handle spells differently - ask for target first
        if card.card_type == 'spell':
            def cast_spell_with_target(target_idx):
                game.play_card(index, spell_target_idx=target_idx)
                root.after(80, update_ui)
            
            # Ask for spell target based on spell_target type
            ask_spell_target(card, cast_spell_with_target)
        else:
            # animate then play troop
            def _do_play():
                game.play_card(index)
                # small delay to let UI refresh after play
                root.after(80, update_ui)

            # start animation from hand to active area then call play
            animate_play_from_hand(index, on_complete=_do_play)

    def on_activate_ability(index):
        if game.turn != 'player':
            return
        if index < 0 or index >= len(game.player.active_zone):
            return
        card = game.player.active_zone[index]
        if not card.ready:
            status_var.set('Card is tapped!')
            root.after(800, lambda: status_var.set(f"Turn: {game.turn}"))
            return
        game.activate_ability(index, owner='player')
        update_ui()

    # UI callback to choose attack target (card or player)
    def ask_attack_target(attacker_idx: int):
        """Ask player where this attacker should attack."""
        attacker = game.player.active_zone[attacker_idx]
        sel: Dict[str, Optional[Union[str, Tuple[str, int]]]] = {'choice': None}
        dlg = tk.Toplevel(root)
        dlg.title(f"{attacker.name} - Choose Target")
        tk.Label(dlg, text=f"Where should {attacker.name} attack?", font=('Arial', 12, 'bold')).pack(pady=6)
        
        # Check for Taunt cards
        taunt_cards = [i for i, c in enumerate(game.ai.active_zone) if c.ability == 'Taunt']
        
        if taunt_cards:
            # Must attack Taunt cards only
            tk.Label(dlg, text='⚠ TAUNT: Must attack these cards first!', 
                    font=('Arial', 11, 'bold'), fg='red').pack(pady=6)
            card_frame = tk.Frame(dlg)
            card_frame.pack(pady=4)
            for i in taunt_cards:
                card = game.ai.active_zone[i]
                txt = f"{card.name} [TAUNT]\nATK:{card.damage} HP:{card.current_health}"
                def attack_card(idx=i):
                    sel['choice'] = ('card', idx)
                    dlg.destroy()
                btn = tk.Button(card_frame, text=txt, command=attack_card, 
                              width=15, height=4, bg='#ffa500', fg='white', font=('Arial', 10, 'bold'))
                btn.grid(row=0, column=len([x for x in taunt_cards if x < i]), padx=3, pady=3)
        else:
            # Normal targeting - can attack player or any card
            # Button to attack player
            def attack_player():
                sel['choice'] = 'player'
                dlg.destroy()
            tk.Button(dlg, text='⚔ Attack AI Player', command=attack_player, 
                     width=20, height=2, bg='#ff6b6b', fg='white', font=('Arial', 11, 'bold')).pack(pady=8)
            
            # Buttons to attack AI cards
            if game.ai.active_zone:
                tk.Label(dlg, text='Or attack an AI card:', font=('Arial', 10)).pack(pady=(10, 4))
                card_frame = tk.Frame(dlg)
                card_frame.pack(pady=4)
                for i, card in enumerate(game.ai.active_zone):
                    txt = f"{card.name}\nATK:{card.damage} HP:{card.current_health}"
                    def attack_card(idx=i):
                        sel['choice'] = ('card', idx)
                        dlg.destroy()
                    btn = tk.Button(card_frame, text=txt, command=attack_card, width=15, height=4, bg='#4ecdc4')
                    btn.grid(row=i // 4, column=i % 4, padx=3, pady=3)
        
        # Cancel option
        def cancel():
            sel['choice'] = None
            dlg.destroy()
        tk.Button(dlg, text='Cancel', command=cancel, width=15).pack(pady=6)
        
        dlg.transient(root)
        dlg.grab_set()
        root.wait_window(dlg)
        return sel['choice']

    def ask_spell_target(spell: Card, callback):
        """Ask player to choose target for a spell."""
        # If spell doesn't need a target, cast immediately
        if spell.spell_target in ('all_enemies', 'self'):
            callback(None)
            return
        
        sel: Dict[str, Optional[Union[str, int]]] = {'choice': None, 'cancelled': False}
        dlg = tk.Toplevel(root)
        dlg.title(f"{spell.name} - Choose Target")
        tk.Label(dlg, text=f"Choose target for {spell.name}", font=('Arial', 12, 'bold')).pack(pady=6)
        tk.Label(dlg, text=spell.description or '', font=('Arial', 10), fg='purple').pack(pady=4)
        
        has_valid_targets = False
        
        if spell.spell_target == 'enemy_or_player':
            # Can target enemy troops OR enemy player
            has_valid_targets = True
            
            # Button to target enemy player
            def target_player():
                sel['choice'] = 'player'
                dlg.destroy()
            tk.Button(dlg, text='💥 Attack Enemy Player', command=target_player, 
                     width=25, height=2, bg='#ff6b6b', fg='white', font=('Arial', 11, 'bold')).pack(pady=8)
            
            # Or target enemy troops
            if game.ai.active_zone:
                tk.Label(dlg, text='Or target an enemy troop:', font=('Arial', 10)).pack(pady=(10, 4))
                card_frame = tk.Frame(dlg)
                card_frame.pack(pady=4)
                for i, card in enumerate(game.ai.active_zone):
                    txt = f"{card.name}\nATK:{card.damage} HP:{card.current_health}"
                    def target_card(idx=i):
                        sel['choice'] = idx
                        dlg.destroy()
                    btn = tk.Button(card_frame, text=txt, command=target_card, width=15, height=4, bg='#e74c3c', fg='white')
                    btn.grid(row=i // 4, column=i % 4, padx=3, pady=3)
        
        elif spell.spell_target == 'enemy':
            # Can target any enemy troop
            if game.ai.active_zone:
                has_valid_targets = True
                tk.Label(dlg, text='Choose an enemy troop:', font=('Arial', 10)).pack(pady=(10, 4))
                card_frame = tk.Frame(dlg)
                card_frame.pack(pady=4)
                for i, card in enumerate(game.ai.active_zone):
                    txt = f"{card.name}\nATK:{card.damage} HP:{card.current_health}"
                    def target_card(idx=i):
                        sel['choice'] = idx
                        dlg.destroy()
                    btn = tk.Button(card_frame, text=txt, command=target_card, width=15, height=4, bg='#e74c3c', fg='white')
                    btn.grid(row=i // 4, column=i % 4, padx=3, pady=3)
            else:
                tk.Label(dlg, text='No valid targets!', font=('Arial', 10), fg='red').pack(pady=10)
        
        elif spell.spell_target == 'friendly':
            # Can target any friendly troop
            if game.player.active_zone:
                has_valid_targets = True
                tk.Label(dlg, text='Choose one of your troops:', font=('Arial', 10)).pack(pady=(10, 4))
                card_frame = tk.Frame(dlg)
                card_frame.pack(pady=4)
                for i, card in enumerate(game.player.active_zone):
                    txt = f"{card.name}\nATK:{card.damage} HP:{card.current_health}/{card.health}"
                    def target_card(idx=i):
                        sel['choice'] = idx
                        dlg.destroy()
                    btn = tk.Button(card_frame, text=txt, command=target_card, width=15, height=4, bg='#2ecc71', fg='white')
                    btn.grid(row=i // 4, column=i % 4, padx=3, pady=3)
            else:
                tk.Label(dlg, text='No valid targets!', font=('Arial', 10), fg='red').pack(pady=10)
        
        # Cancel option
        def cancel():
            sel['choice'] = None
            sel['cancelled'] = True
            dlg.destroy()
        
        if has_valid_targets:
            tk.Button(dlg, text='Cancel', command=cancel, width=15).pack(pady=6)
        else:
            # No valid targets, just show OK button
            tk.Button(dlg, text='OK', command=cancel, width=15).pack(pady=6)
        
        dlg.transient(root)
        dlg.grab_set()
        root.wait_window(dlg)
        
        # Only call callback if a valid choice was made (not cancelled and not no targets)
        if not sel['cancelled'] and sel['choice'] is not None:
            callback(sel['choice'])

    # UI callback for Game to ask which card blocks an attacker (when AI attacks player)
    def ask_blocker_ui(attacker: Card):
        # Check if player champion prevents blocking (Ragnar)
        if game.player.champion and game.player.champion.ability_type == 'all_furia':
            return None  # Cannot block
        
        # modal dialog that returns index of chosen blocker or None
        # only ready (untapped) active cards that haven't blocked yet can block
        ready_indexes = [i for i, c in enumerate(game.player.active_zone) if c.ready and not getattr(c, 'blocked_this_combat', False)]
        if not ready_indexes:
            return None
        choices = [game.player.active_zone[i] for i in ready_indexes]
        sel = {'choice': None}
        dlg = tk.Toplevel(root)
        dlg.title(f"Block {attacker.name}?")
        tk.Label(dlg, text=f"AI attacker: {attacker.name} ({attacker.damage} dmg) targeting YOU", font=('Arial', 11, 'bold')).pack(pady=6)
        frame = tk.Frame(dlg)
        frame.pack(pady=4)
        def choose(i):
            # i refers to index in displayed choices -> map back to active_zone index
            sel['choice'] = ready_indexes[i]
            dlg.destroy()
        for i, card in enumerate(choices):
            txt = f"{card.name}\nATK:{card.damage} HP:{card.current_health}"
            btn = tk.Button(frame, text=txt, command=lambda idx=i: choose(idx), width=18, height=4)
            btn.grid(row=0, column=i, padx=4)
        # option to not block
        def no_block():
            sel['choice'] = None
            dlg.destroy()
        tk.Button(dlg, text='No block (take damage)', command=no_block, bg='#ff6b6b', fg='white').pack(pady=6)
        # make modal
        dlg.transient(root)
        dlg.grab_set()
        root.wait_window(dlg)
        return sel['choice']

    # attach to game so AI can call it
    game.ask_blocker = ask_blocker_ui

    def on_end_turn():
        # Start AI turn as a sequence of animated steps (use generator)
        if game.turn != 'player':
            return
        
        # Run AI turn animation
        game.turn = 'ai'
        ai_steps = game.ai_turn_steps()
        delay_ms = 500
        def run_step():
            try:
                next(ai_steps)
                # refresh UI after this step
                update_ui()
                # if AI produced a played-card event, animate it first
                if getattr(game, 'ai_played', None):
                    try:
                        card_to_anim = game.ai_played.pop(0)
                    except Exception:
                        card_to_anim = None
                    if card_to_anim is not None:
                        def _after_ai_anim():
                            root.after(delay_ms, run_step)
                        animate_play_from_ai(card_to_anim, on_complete=_after_ai_anim)
                        return
                # otherwise schedule next step
                root.after(delay_ms, run_step)
            except StopIteration:
                # AI finished: switch back to player and start player turn
                game.turn = 'player'
                game.start_turn('player')
                update_ui()
        # begin sequence
        run_step()

    # Top area: AI info
    top = tk.Frame(root)
    top.pack(pady=6, fill='x')
    info_left = tk.Frame(top)
    info_left.pack(side='left', padx=8)
    # AI Champion info
    if game.ai.champion:
        champion_lbl = tk.Label(info_left, text=f"🎭 {game.ai.champion.name}", font=('Arial', 11, 'bold'), fg='#d32f2f', cursor='hand2')
        champion_lbl.pack()
        title_lbl = tk.Label(info_left, text=f"{game.ai.champion.title}", font=('Arial', 9), fg='#666')
        title_lbl.pack()
        # Add tooltip for champion
        def show_champion_tooltip(e, champ=game.ai.champion):
            hide_tooltip()
            nonlocal tooltip_window
            tooltip_window = tk.Toplevel(root)
            tooltip_window.wm_overrideredirect(True)
            tooltip_window.wm_geometry(f"+{e.widget.winfo_rootx()+10}+{e.widget.winfo_rooty()+30}")
            frame = tk.Frame(tooltip_window, bg='#2c3e50', bd=2, relief='solid')
            frame.pack()
            tk.Label(frame, text=f"⚔ {champ.name} - {champ.title}", bg='#2c3e50', fg='#ecf0f1', font=('Arial', 10, 'bold'), padx=8, pady=4).pack()
            tk.Label(frame, text=f"❤ Vida Inicial: {champ.starting_life}", bg='#2c3e50', fg='#e74c3c', font=('Arial', 9), padx=8, pady=2).pack(anchor='w')
            tk.Label(frame, text=f"⚡ {champ.passive_name}", bg='#2c3e50', fg='#f39c12', font=('Arial', 9, 'bold'), padx=8, pady=2).pack(anchor='w')
            tk.Label(frame, text=champ.passive_description, bg='#2c3e50', fg='#bdc3c7', font=('Arial', 9), padx=8, pady=4, wraplength=250).pack()
        champion_lbl.bind('<Enter>', show_champion_tooltip)
        champion_lbl.bind('<Leave>', hide_tooltip)
        title_lbl.bind('<Enter>', show_champion_tooltip)
        title_lbl.bind('<Leave>', hide_tooltip)
    tk.Label(info_left, textvariable=ai_life_var, font=('Arial', 12)).pack()
    tk.Label(info_left, textvariable=ai_deck_var, font=('Arial', 10)).pack()
    info_center = tk.Frame(top)
    info_center.pack(side='left', expand=True)
    tk.Label(info_center, textvariable=status_var, font=('Arial', 12)).pack()
    info_right = tk.Frame(top)
    info_right.pack(side='right', padx=8)
    # Player Champion info
    if game.player.champion:
        champion_lbl = tk.Label(info_right, text=f"🎭 {game.player.champion.name}", font=('Arial', 11, 'bold'), fg='#1976d2', cursor='hand2')
        champion_lbl.pack()
        title_lbl = tk.Label(info_right, text=f"{game.player.champion.title}", font=('Arial', 9), fg='#666')
        title_lbl.pack()
        passive_lbl = tk.Label(info_right, text=f"⚡ {game.player.champion.passive_name}", font=('Arial', 9), fg='#9c27b0')
        passive_lbl.pack()
        # Add tooltip for champion
        def show_player_champion_tooltip(e, champ=game.player.champion):
            hide_tooltip()
            nonlocal tooltip_window
            tooltip_window = tk.Toplevel(root)
            tooltip_window.wm_overrideredirect(True)
            tooltip_window.wm_geometry(f"+{e.widget.winfo_rootx()-260}+{e.widget.winfo_rooty()+30}")
            frame = tk.Frame(tooltip_window, bg='#1565c0', bd=2, relief='solid')
            frame.pack()
            tk.Label(frame, text=f"⚔ {champ.name} - {champ.title}", bg='#1565c0', fg='#ffffff', font=('Arial', 10, 'bold'), padx=8, pady=4).pack()
            tk.Label(frame, text=f"❤ Vida Inicial: {champ.starting_life}", bg='#1565c0', fg='#ffcdd2', font=('Arial', 9), padx=8, pady=2).pack(anchor='w')
            tk.Label(frame, text=f"⚡ {champ.passive_name}", bg='#1565c0', fg='#ffd54f', font=('Arial', 9, 'bold'), padx=8, pady=2).pack(anchor='w')
            tk.Label(frame, text=champ.passive_description, bg='#1565c0', fg='#e3f2fd', font=('Arial', 9), padx=8, pady=4, wraplength=250).pack()
        champion_lbl.bind('<Enter>', show_player_champion_tooltip)
        champion_lbl.bind('<Leave>', hide_tooltip)
        title_lbl.bind('<Enter>', show_player_champion_tooltip)
        title_lbl.bind('<Leave>', hide_tooltip)
        passive_lbl.bind('<Enter>', show_player_champion_tooltip)
        passive_lbl.bind('<Leave>', hide_tooltip)
    tk.Label(info_right, textvariable=player_life_var, font=('Arial', 12)).pack()
    tk.Label(info_right, textvariable=player_mana_var, font=('Arial', 10)).pack()

    # Main content: left center game area + right log
    content_frame = tk.Frame(root)
    content_frame.pack(fill='both', expand=True)
    # center_frame will hold the game board; right_panel will be fixed on the right
    center_frame = tk.Frame(content_frame)
    center_frame.pack(side='left', fill='both', expand=True)

    # AI hand frame (show backs) inside content
    global ai_hand_frame
    ai_hand_frame = tk.Frame(center_frame, relief='solid', bd=2, bg='#f0f0f0')
    ai_hand_frame.pack(pady=4)
    ai_hand_frame.config(height=48)
    ai_hand_frame.pack_propagate(False)

    # Board area: put rest + active zones inside a centered fixed-size frame
    # so they cannot grow and push the hand below out of view.
    board_frame = tk.Frame(center_frame, relief='solid', bd=2, bg='#e8e8e8')
    board_frame.pack(pady=4, fill='both', expand=True)

    # Active zone area (cards that can act) - centered within board_frame
    active_frame = tk.Frame(board_frame, relief='solid', bd=2, bg='#d8d8d8')
    active_frame.pack(pady=4, fill='both', expand=True)
    tk.Label(active_frame, text='AI Active:', bg='#d8d8d8').pack(anchor='w')
    # make AI active area a horizontal canvas so many cards don't grow the window
    ai_active_canvas = tk.Canvas(active_frame, height=160, relief='solid', bd=2, bg='#c8f0c8')
    ai_active_hscroll = tk.Scrollbar(active_frame, orient='horizontal', command=ai_active_canvas.xview)
    ai_active_canvas.configure(xscrollcommand=ai_active_hscroll.set)
    ai_active_hscroll.pack(side='bottom', fill='x')
    ai_active_canvas.pack(side='top', fill='both', expand=True)
    ai_active_inner = tk.Frame(ai_active_canvas, bg='#c8f0c8')
    ai_active_canvas.create_window((0, 0), window=ai_active_inner, anchor='nw')
    global ai_active_frame
    ai_active_frame = ai_active_inner
    tk.Label(active_frame, text='Player Active:', bg='#d8d8d8').pack(anchor='w')
    # player active area as horizontal canvas - INCREASED HEIGHT for ability buttons
    player_active_canvas = tk.Canvas(active_frame, height=220, relief='solid', bd=2, bg='#c8c8f0')
    player_active_hscroll = tk.Scrollbar(active_frame, orient='horizontal', command=player_active_canvas.xview)
    player_active_canvas.configure(xscrollcommand=player_active_hscroll.set)
    player_active_hscroll.pack(side='bottom', fill='x')
    player_active_canvas.pack(side='top', fill='both', expand=True)
    player_active_inner = tk.Frame(player_active_canvas, bg='#c8c8f0')
    player_active_canvas.create_window((0, 0), window=player_active_inner, anchor='nw')
    global player_active_frame
    player_active_frame = player_active_inner

    # Main hand area: collapsible panel that expands on hover using place() to overlay
    hand_container = tk.Frame(root, relief='solid', bd=2, bg='#f0f0d8')
    hand_container.place(x=0, y=root.winfo_height()-60, relwidth=0.7, height=50)
    
    # Canvas for hand cards
    hand_canvas = tk.Canvas(hand_container, relief='solid', bd=1, bg='#ffffc8', highlightthickness=0)
    hand_hscroll = tk.Scrollbar(hand_container, orient='horizontal', command=hand_canvas.xview)
    hand_canvas.configure(xscrollcommand=hand_hscroll.set)
    hand_hscroll.pack(side='bottom', fill='x')
    hand_canvas.pack(side='top', fill='both', expand=True)
    hand_inner = tk.Frame(hand_canvas, bg='#ffffc8')
    hand_canvas.create_window((0, 0), window=hand_inner, anchor='nw')
    global hand_frame
    hand_frame = hand_inner
    
    # Hover expand/collapse behavior - overlays without pushing other elements
    def expand_hand(event=None):
        hand_container.place(x=0, y=root.winfo_height()-170, relwidth=0.7, height=160)
    
    def collapse_hand(event=None):
        hand_container.place(x=0, y=root.winfo_height()-60, relwidth=0.7, height=50)
    
    def update_hand_position(event=None):
        # Update position when window resizes
        if hand_container.winfo_height() > 100:
            hand_container.place(x=0, y=root.winfo_height()-170, relwidth=0.7, height=160)
        else:
            hand_container.place(x=0, y=root.winfo_height()-60, relwidth=0.7, height=50)
    
    root.bind('<Configure>', update_hand_position)
    hand_container.bind('<Enter>', expand_hand)
    hand_container.bind('<Leave>', collapse_hand)
    hand_canvas.bind('<Enter>', expand_hand)
    hand_canvas.bind('<Leave>', collapse_hand)

    # Right panel for log (fixed area) inside content_frame
    right_panel = tk.Frame(content_frame)
    right_panel.pack(side='right', fill='y', padx=8, pady=8)
    right_panel.config(width=340)
    right_panel.pack_propagate(False)
    # Controls toolbar at top of right panel to ensure visibility
    toolbar = tk.Frame(right_panel)
    toolbar.pack(pady=4)
    tk.Label(toolbar, text='Controls').grid(row=0, column=0, columnspan=3)
    btn_font = ('Arial', 10, 'bold')
    tb_end = tk.Button(toolbar, text='End Turn', command=on_end_turn, width=12, height=1, bg='#ff8c42', font=btn_font)
    tb_end.grid(row=1, column=0, padx=4, pady=2)
    tb_declare = tk.Button(toolbar, text='Declare Attack', command=declare_attack, width=14, height=1, bg='#4CAF50', fg='white', font=btn_font)
    tb_declare.grid(row=1, column=1, padx=4, pady=2)
    tb_cancel = tk.Button(toolbar, text='Cancel', command=cancel_selection, width=10, height=1, bg='#b0b0b0')
    tb_cancel.grid(row=1, column=2, padx=4, pady=2)

    log_frame = tk.Frame(right_panel)
    log_frame.pack()
    tk.Label(log_frame, text='Action Log').pack()
    global log_listbox
    log_listbox = tk.Listbox(log_frame, width=40, height=20)
    log_listbox.pack()
    # Small footer hint (controls live in the right toolbar)
    footer = tk.Frame(root, bd=1, relief='groove')
    footer.pack(pady=6, fill='x')
    hint = tk.Label(footer, text='Select attackers (click) then use the Controls panel to declare attacks or end turn.', font=('Arial', 9))
    hint.pack()

    game.on_update = update_ui
    update_ui()


if __name__ == '__main__':
    from champions import get_random_champion
    
    root = tk.Tk()
    # set a reasonable default size so controls are visible
    root.geometry('1100x700')
    root.minsize(900, 600)
    root.title('Mini TCG Prototype')
    
    # Select random champions for player and AI
    player_champion = get_random_champion()
    ai_champion = get_random_champion()
    
    player_deck = build_random_deck(10)
    ai_deck = build_random_deck(10)
    player = Player('Player', player_deck, champion=player_champion)
    ai = Player('AI', ai_deck, champion=ai_champion)
    
    player_life_var = tk.StringVar()
    ai_life_var = tk.StringVar()
    player_mana_var = tk.StringVar()
    player_deck_var = tk.StringVar()
    ai_deck_var = tk.StringVar()
    status_var = tk.StringVar()
    game = Game(player, ai, lambda: None)
    make_ui(game)
    game.start()
    root.mainloop()
