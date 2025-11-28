"""
Multiplayer Game UI - Clean interface for online matches
Displays game zones, actions, and chat for two players
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Optional, Callable, List, Dict, Any
from dataclasses import dataclass


@dataclass
class CardDisplay:
    """Visual representation of a card"""
    name: str
    cost: int
    attack: int
    defense: int
    card_type: str
    abilities: List[str]
    can_attack: bool = False
    is_tapped: bool = False
    has_activated_ability: bool = False  # Can activate ability (like Invocar Aliado)


class MultiplayerGameUI:
    """
    Modern UI for multiplayer TCG matches.
    
    Layout:
    ┌─────────────────────────────────────────────┬─────────────┐
    │ OPPONENT INFO (Life, Mana, Cards in hand)  │             │
    ├─────────────────────────────────────────────┤             │
    │ OPPONENT HAND (Card backs)                  │   ACTION    │
    ├─────────────────────────────────────────────┤     LOG     │
    │ OPPONENT ACTIVE ZONE (Visible cards)        │             │
    ├─────────────────────────────────────────────┼─────────────┤
    │ MY ACTIVE ZONE (My creatures)               │             │
    ├─────────────────────────────────────────────┤    CHAT     │
    │ MY HAND (Clickable cards)                   │             │
    ├─────────────────────────────────────────────┤             │
    │ MY INFO (Life, Mana) + ACTION BUTTONS       │             │
    └─────────────────────────────────────────────┴─────────────┘
    """
    
    def __init__(
        self,
        root: tk.Tk | tk.Toplevel,
        player_name: str,
        opponent_name: str,
        on_play_card: Callable[[int, Any], None],
        on_end_turn: Callable[[], None],
        on_declare_attacks: Callable[[List[int], List], None],
        on_send_chat: Callable[[str], None],
        on_activate_ability: Optional[Callable[[int], None]] = None
    ):
        """
        Initialize multiplayer UI.
        
        Args:
            root: Tkinter root window
            player_name: This player's name
            opponent_name: Opponent's name
            on_play_card: Callback(card_index, spell_target) when playing a card
            on_end_turn: Callback when ending turn
            on_declare_attacks: Callback(attacker_indices, targets) when declaring attacks
            on_send_chat: Callback(message) when sending chat message
            on_activate_ability: Callback(card_index) when activating a card ability
        """
        self.root = root
        self.player_name = player_name
        self.opponent_name = opponent_name
        
        # Callbacks
        self.on_play_card = on_play_card  # (card_index, spell_target=None)
        self.on_end_turn = on_end_turn
        self.on_declare_attacks = on_declare_attacks
        self.on_send_chat = on_send_chat
        self.on_activate_ability = on_activate_ability or (lambda idx: None)
        
        # Game state (visual only)
        self.my_life = 25
        self.my_mana = 0
        self.my_max_mana = 0
        self.my_champion_name = "Unknown"
        self.my_champion_ability = ""
        self.opponent_life = 25
        self.opponent_mana = 0
        self.opponent_max_mana = 0
        self.opponent_hand_count = 0
        self.opponent_champion_name = "Unknown"
        self.opponent_champion_ability = ""
        
        self.my_hand: List[CardDisplay] = []
        self.my_active: List[CardDisplay] = []
        self.opponent_active: List[CardDisplay] = []
        
        # UI state
        self.is_my_turn = False
        self.selected_attackers: List[int] = []
        self.attack_mode = False
        self.waiting_for_blockers = False  # True when waiting for opponent to choose blockers
        
        # Cache for preventing unnecessary UI updates
        self._last_update_hash = {
            'my_hand': '',
            'my_active': '',
            'opponent_active': '',
            'my_stats': '',
            'opponent_stats': ''
        }

        # Keep last created widgets for animations
        self.my_active_widgets: List[tk.Frame] = []
        self.opponent_active_widgets: List[tk.Frame] = []
        self.my_hand_widgets: List[tk.Frame] = []

        # Track previous card ids per zone to detect spawns/changes
        self._prev_ids: Dict[str, List[str]] = {
            'my_active': [],
            'opponent_active': [],
            'my_hand': []
        }
        
        # Build UI first (all widgets initialized here)
        self._build_ui()
        
        # UI elements (initialized in _build_ui, so not Optional)
        # These are typed here for clarity but actually set in _build_ui
        self.main_frame: tk.Frame
        self.opponent_info_label: tk.Label
        self.my_info_label: tk.Label
        self.turn_indicator: tk.Label
        
        self.opponent_hand_frame: tk.Frame
        self.opponent_active_frame: tk.Frame
        self.my_active_frame: tk.Frame
        self.my_hand_frame: tk.Frame
        
        self.action_log: scrolledtext.ScrolledText
        self.chat_log: scrolledtext.ScrolledText
        self.chat_entry: tk.Entry
        
        self.end_turn_button: tk.Button
        self.attack_button: tk.Button
        self.cancel_attack_button: tk.Button
    
    def _create_tooltip(self, widget, text):
        """Create a hover tooltip for a widget with delay - uses polling instead of events"""
        tooltip_state = {'tooltip': None, 'after_id': None, 'was_inside': False, 'poll_id': None}
        
        def is_mouse_inside():
            """Check if mouse is currently inside widget bounds"""
            try:
                x = widget.winfo_pointerx() - widget.winfo_rootx()
                y = widget.winfo_pointery() - widget.winfo_rooty()
                w = widget.winfo_width()
                h = widget.winfo_height()
                return 0 <= x <= w and 0 <= y <= h
            except:
                return False
        
        def check_mouse():
            """Continuously poll mouse position"""
            try:
                inside_now = is_mouse_inside()
                
                if inside_now and not tooltip_state['was_inside']:
                    # Mouse just entered - schedule tooltip if not already scheduled
                    tooltip_state['was_inside'] = True
                    if not tooltip_state['after_id'] and not tooltip_state['tooltip']:
                        print(f"🖱️ Mouse entered: {text[:50]}...")
                        tooltip_state['after_id'] = widget.after(300, create_tooltip)
                
                elif not inside_now and tooltip_state['was_inside']:
                    # Mouse just left - hide tooltip
                    tooltip_state['was_inside'] = False
                    hide_tooltip()
                
                elif inside_now and tooltip_state['tooltip']:
                    # Mouse still inside with tooltip showing - keep it visible
                    pass
                
                # Continue polling every 50ms
                tooltip_state['poll_id'] = widget.after(50, check_mouse)
            except:
                # Widget destroyed
                tooltip_state['poll_id'] = None
        
        def create_tooltip():
            """Create the tooltip window"""
            # Clear the after_id since we're executing now
            tooltip_state['after_id'] = None
            
            # Double-check: don't create if already exists or mouse left
            if tooltip_state['tooltip'] is not None:
                print(f"⚠️ Tooltip already exists, skipping creation")
                return
                
            if not is_mouse_inside():
                print(f"⚠️ Mouse left before tooltip could be created")
                return
            
            try:
                print(f"✅ Creating tooltip: {text[:50]}...")
                
                # Get screen dimensions
                screen_width = self.root.winfo_screenwidth()
                screen_height = self.root.winfo_screenheight()
                
                # Tooltip dimensions
                tooltip_width = 350
                tooltip_height = 100  # Approximate height
                
                # Widget position
                widget_x = widget.winfo_rootx()
                widget_y = widget.winfo_rooty()
                widget_width = widget.winfo_width()
                widget_height = widget.winfo_height()
                
                # Get my_active_frame position (to avoid covering player's cards)
                try:
                    my_active_y = self.my_active_frame.winfo_rooty()
                    my_active_height = self.my_active_frame.winfo_height()
                    my_active_bottom = my_active_y + my_active_height
                except:
                    my_active_bottom = screen_height - 300  # Fallback
                
                # Default: above the widget, centered
                tx = widget_x + (widget_width // 2) - (tooltip_width // 2)
                ty = widget_y - tooltip_height - 20
                
                # Adjust horizontal position to stay on screen
                if tx < 10:
                    tx = 10
                elif tx + tooltip_width > screen_width - 10:
                    tx = screen_width - tooltip_width - 10
                
                # Adjust vertical position
                # If tooltip would cover player's active zone, move it up or to the side
                if ty + tooltip_height > my_active_bottom - 20 and widget_y < my_active_bottom:
                    # Try placing it above the my_active zone
                    ty = my_active_y - tooltip_height - 10
                    
                # If still above screen, place below widget instead
                if ty < 10:
                    ty = widget_y + widget_height + 10
                    
                # Final bounds check
                if ty + tooltip_height > screen_height - 10:
                    ty = screen_height - tooltip_height - 10
                
                tooltip = tk.Toplevel(widget)
                tooltip.wm_overrideredirect(True)
                tooltip.wm_geometry(f"+{int(tx)}+{int(ty)}")
                
                border_frame = tk.Frame(tooltip, bg='#f39c12', padx=2, pady=2)
                border_frame.pack()
                
                label = tk.Label(
                    border_frame,
                    text=text,
                    font=('Arial', 10, 'bold'),
                    bg='#2c3e50',
                    fg='#ecf0f1',
                    justify=tk.LEFT,
                    padx=12,
                    pady=8,
                    wraplength=350
                )
                label.pack()
                
                tooltip_state['tooltip'] = tooltip
            except Exception as e:
                print(f"⚠️ Error creating tooltip: {e}")
                tooltip_state['tooltip'] = None
        
        def hide_tooltip():
            """Hide tooltip and cancel any pending show"""
            # Cancel scheduled tooltip creation
            if tooltip_state['after_id']:
                try:
                    widget.after_cancel(tooltip_state['after_id'])
                    print(f"❌ Cancelled tooltip schedule")
                except:
                    pass
                tooltip_state['after_id'] = None
            
            # Destroy existing tooltip
            if tooltip_state['tooltip']:
                try:
                    tooltip_state['tooltip'].destroy()
                    print(f"❌ Destroyed tooltip")
                except:
                    pass
                tooltip_state['tooltip'] = None
        
        # Start polling
        check_mouse()
    
    def _build_ui(self):
        """Build the complete UI layout"""
        self.root.title(f"TCG Multiplayer - {self.player_name}")
        self.root.geometry("1400x900")
        self.root.configure(bg='#1a1a2e')
        
        # Main container
        self.main_frame = tk.Frame(self.root, bg='#1a1a2e')
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left side (game board) and Right side (logs)
        left_frame = tk.Frame(self.main_frame, bg='#1a1a2e')
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        right_frame = tk.Frame(self.main_frame, bg='#16213e', width=300)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, pady=0)
        right_frame.pack_propagate(False)
        
        # Build left side (game zones)
        self._build_opponent_section(left_frame)
        self._build_board_separator(left_frame)
        self._build_my_section(left_frame)
        
        # Build right side (logs and chat)
        self._build_action_log(right_frame)
        self._build_chat(right_frame)

    # ============================================
    # Animation Helpers (non-blocking, using after)
    # ============================================
    def _card_id(self, card: CardDisplay) -> str:
        """Create a lightweight id for card diffing."""
        return f"{card.name}|{card.cost}|{card.attack}|{card.defense}|{card.card_type}"

    def _animate_pulse(self, widget, highlight_color: str = '#f1c40f', cycles: int = 3, interval: int = 90):
        """Pulse the background color a few times and restore it."""
        try:
            original = widget.cget('bg')
        except Exception:
            return

        total_steps = cycles * 2

        def step(n: int):
            if not widget.winfo_exists():
                return
            if n <= 0:
                try:
                    widget.config(bg=original)
                except Exception:
                    pass
                return
            try:
                widget.config(bg=highlight_color if n % 2 == 0 else original)
            except Exception:
                return
            widget.after(interval, lambda: step(n - 1))

        step(total_steps)

    def _animate_flash(self, widget, flash_color: str = '#e74c3c', flashes: int = 2, interval: int = 80):
        """Quick red flash for damage feedback."""
        self._animate_pulse(widget, flash_color, cycles=flashes, interval=interval)

    def _animate_token_spawn(self, widget):
        """Distinctive spawn effect for tokens (Mystara, etc.)."""
        self._animate_pulse(widget, highlight_color='#9b59b6', cycles=4, interval=70)

    def animate_damage_my(self, index: int):
        if 0 <= index < len(self.my_active_widgets):
            self._animate_flash(self.my_active_widgets[index])

    def animate_damage_opp(self, index: int):
        if 0 <= index < len(self.opponent_active_widgets):
            self._animate_flash(self.opponent_active_widgets[index])

    def animate_attack_my(self, indices: List[int]):
        for idx in indices:
            if 0 <= idx < len(self.my_active_widgets):
                self._animate_pulse(self.my_active_widgets[idx], highlight_color='#27ae60', cycles=3, interval=70)

    def animate_attack_opp(self, indices: List[int]):
        for idx in indices:
            if 0 <= idx < len(self.opponent_active_widgets):
                self._animate_pulse(self.opponent_active_widgets[idx], highlight_color='#c0392b', cycles=3, interval=70)

    def animate_my_life_change(self, delta: int):
        """Flash my life label based on delta."""
        if delta < 0:
            self._animate_flash(self.my_info_label, flash_color='#e74c3c', flashes=3, interval=70)
        elif delta > 0:
            self._animate_pulse(self.my_info_label, highlight_color='#2ecc71', cycles=3, interval=70)

    def animate_opp_life_change(self, delta: int):
        """Flash opponent life label based on delta."""
        if delta < 0:
            self._animate_flash(self.opponent_info_label, flash_color='#e74c3c', flashes=3, interval=70)
        elif delta > 0:
            self._animate_pulse(self.opponent_info_label, highlight_color='#2ecc71', cycles=3, interval=70)
    
    def _build_opponent_section(self, parent):
        """Build opponent's section (top of board)"""
        # Opponent info bar
        info_frame = tk.Frame(parent, bg='#e74c3c', height=60)
        info_frame.pack(fill=tk.X, pady=(0, 5))
        info_frame.pack_propagate(False)
        
        # Champion name with hover tooltip
        self.opponent_champion_label = tk.Label(
            info_frame,
            text="👑 Unknown",
            font=('Arial', 12, 'bold'),
            bg='#e74c3c',
            fg='#f1c40f',
            cursor='hand2'
        )
        self.opponent_champion_label.pack(side=tk.TOP, pady=(2, 0))
        self._create_tooltip(self.opponent_champion_label, "Opponent's champion ability")
        
        self.opponent_info_label = tk.Label(
            info_frame,
            text=f"🎮 {self.opponent_name} | ❤️ 25 | 💎 0/0 | 🃏 0 cards",
            font=('Arial', 12, 'bold'),
            bg='#e74c3c',
            fg='white'
        )
        self.opponent_info_label.pack(expand=True)
        
        # Opponent hand (card backs)
        hand_container = tk.Frame(parent, bg='#2c3e50', height=80)
        hand_container.pack(fill=tk.X, pady=(0, 5))
        hand_container.pack_propagate(False)
        
        tk.Label(
            hand_container,
            text="Opponent's Hand",
            font=('Arial', 10, 'bold'),
            bg='#2c3e50',
            fg='#ecf0f1'
        ).pack(side=tk.TOP, pady=2)
        
        self.opponent_hand_frame = tk.Frame(hand_container, bg='#2c3e50')
        self.opponent_hand_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)
        
        # Opponent active zone
        active_container = tk.Frame(parent, bg='#34495e', height=160)
        active_container.pack(fill=tk.X, pady=(0, 5))
        active_container.pack_propagate(False)
        
        tk.Label(
            active_container,
            text="Opponent's Active Zone",
            font=('Arial', 10, 'bold'),
            bg='#34495e',
            fg='#ecf0f1'
        ).pack(side=tk.TOP, pady=2)
        
        self.opponent_active_frame = tk.Frame(active_container, bg='#34495e')
        self.opponent_active_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)
    
    def _build_board_separator(self, parent):
        """Build visual separator between players"""
        separator = tk.Frame(parent, bg='#f39c12', height=3)
        separator.pack(fill=tk.X, pady=10)
    
    def _build_my_section(self, parent):
        """Build player's section (bottom of board)"""
        # My active zone
        active_container = tk.Frame(parent, bg='#2c3e50', height=160)
        active_container.pack(fill=tk.X, pady=(0, 5))
        active_container.pack_propagate(False)
        
        tk.Label(
            active_container,
            text="My Active Zone",
            font=('Arial', 10, 'bold'),
            bg='#2c3e50',
            fg='#ecf0f1'
        ).pack(side=tk.TOP, pady=2)
        
        self.my_active_frame = tk.Frame(active_container, bg='#2c3e50')
        self.my_active_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)
        
        # My hand
        hand_container = tk.Frame(parent, bg='#16213e', height=155)
        hand_container.pack(fill=tk.X, pady=(0, 5))
        hand_container.pack_propagate(False)
        
        tk.Label(
            hand_container,
            text="My Hand",
            font=('Arial', 10, 'bold'),
            bg='#16213e',
            fg='#ecf0f1'
        ).pack(side=tk.TOP, pady=2)
        
        self.my_hand_frame = tk.Frame(hand_container, bg='#16213e')
        self.my_hand_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)
        
        # My info and action buttons
        bottom_frame = tk.Frame(parent, bg='#27ae60', height=80)
        bottom_frame.pack(fill=tk.X, pady=(0, 5))
        bottom_frame.pack_propagate(False)
        
        # Left side: Player info
        info_left = tk.Frame(bottom_frame, bg='#27ae60')
        info_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        # Champion name with hover tooltip
        self.my_champion_label = tk.Label(
            info_left,
            text="👑 Unknown",
            font=('Arial', 13, 'bold'),
            bg='#27ae60',
            fg='#f1c40f',
            anchor='w',
            cursor='hand2'
        )
        self.my_champion_label.pack(side=tk.TOP, fill=tk.X, pady=(5, 2))
        self._create_tooltip(self.my_champion_label, "Your champion ability")
        
        self.my_info_label = tk.Label(
            info_left,
            text=f"🎮 {self.player_name} | ❤️ 25 | 💎 0/0",
            font=('Arial', 14, 'bold'),
            bg='#27ae60',
            fg='white',
            anchor='w'
        )
        self.my_info_label.pack(side=tk.TOP, fill=tk.X, pady=2)
        
        self.turn_indicator = tk.Label(
            info_left,
            text="⏳ Waiting for opponent...",
            font=('Arial', 12),
            bg='#27ae60',
            fg='white',
            anchor='w'
        )
        self.turn_indicator.pack(side=tk.TOP, fill=tk.X, pady=2)
        
        # Right side: Action buttons
        button_frame = tk.Frame(bottom_frame, bg='#27ae60')
        button_frame.pack(side=tk.RIGHT, padx=10, pady=5)
        
        self.end_turn_button = tk.Button(
            button_frame,
            text="END TURN",
            font=('Arial', 12, 'bold'),
            bg='#e67e22',
            fg='white',
            activebackground='#d35400',
            activeforeground='white',
            width=12,
            height=1,
            command=self._on_end_turn_clicked,
            state=tk.DISABLED
        )
        self.end_turn_button.pack(side=tk.LEFT, padx=5)
        
        self.attack_button = tk.Button(
            button_frame,
            text="DECLARE ATTACKS",
            font=('Arial', 11, 'bold'),
            bg='#c0392b',
            fg='white',
            activebackground='#a93226',
            activeforeground='white',
            width=15,
            height=1,
            command=self._on_attack_clicked,
            state=tk.DISABLED
        )
        self.attack_button.pack(side=tk.LEFT, padx=5)
        
        self.cancel_attack_button = tk.Button(
            button_frame,
            text="CANCEL",
            font=('Arial', 11, 'bold'),
            bg='#95a5a6',
            fg='white',
            activebackground='#7f8c8d',
            activeforeground='white',
            width=10,
            height=1,
            command=self._on_cancel_attack_clicked,
            state=tk.DISABLED
        )
        self.cancel_attack_button.pack(side=tk.LEFT, padx=5)

    # ---------------------------------
    # Ability/Effect Emoji Helpers
    # ---------------------------------
    def _ability_badges_from_list(self, abilities: Optional[List[str]]) -> str:
        """Create emoji badges from a troop abilities list.
        Each entry can be like 'Taunt+Regeneracion: desc'. We extract names and map to emojis.
        """
        if not abilities:
            return ''
        names: List[str] = []
        for entry in abilities:
            base = entry.split(':', 1)[0].strip()
            for part in base.replace(',', '+').split('+'):
                t = part.strip().lower()
                if t:
                    names.append(t)
        badges: List[str] = []
        def add(e: str):
            if e and e not in badges:
                badges.append(e)
        for t in names:
            if 'taunt' in t or 'provocar' in t:
                add('🛡️')
            elif 'volar' in t or 'fly' in t or 'volador' in t:
                add('🪽')
            elif 'regener' in t:
                add('♻️')
            elif 'absorber' in t:
                add('🧲')
            elif 'debilit' in t:
                add('📉')
            elif 'curacion' in t or 'curación' in t:
                add('💖')
        return ' '.join(badges)
    
    def _build_action_log(self, parent):
        """Build action log panel"""
        log_frame = tk.Frame(parent, bg='#16213e')
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        tk.Label(
            log_frame,
            text="📜 Action Log",
            font=('Arial', 12, 'bold'),
            bg='#16213e',
            fg='#ecf0f1'
        ).pack(pady=5)
        
        self.action_log = scrolledtext.ScrolledText(
            log_frame,
            font=('Consolas', 9),
            bg='#0f1419',
            fg='#a0d468',
            wrap=tk.WORD,
            height=15,
            state=tk.DISABLED
        )
        self.action_log.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
    
    def _build_chat(self, parent):
        """Build chat panel"""
        chat_frame = tk.Frame(parent, bg='#16213e')
        chat_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            chat_frame,
            text="💬 Chat",
            font=('Arial', 12, 'bold'),
            bg='#16213e',
            fg='#ecf0f1'
        ).pack(pady=5)
        
        self.chat_log = scrolledtext.ScrolledText(
            chat_frame,
            font=('Arial', 9),
            bg='#0f1419',
            fg='#ecf0f1',
            wrap=tk.WORD,
            height=12,
            state=tk.DISABLED
        )
        self.chat_log.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
        
        # Chat input
        input_frame = tk.Frame(chat_frame, bg='#16213e')
        input_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        self.chat_entry = tk.Entry(
            input_frame,
            font=('Arial', 10),
            bg='#2c3e50',
            fg='white',
            insertbackground='white'
        )
        self.chat_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.chat_entry.bind('<Return>', lambda e: self._send_chat())
        
        send_button = tk.Button(
            input_frame,
            text="Send",
            font=('Arial', 9, 'bold'),
            bg='#3498db',
            fg='white',
            command=self._send_chat,
            width=8
        )
        send_button.pack(side=tk.RIGHT)
    
    # ============================================
    # Card Display Methods
    # ============================================
    
    def _create_card_widget(self, card: CardDisplay, parent: tk.Frame, clickable: bool = False, 
                           on_click: Optional[Callable] = None, is_back: bool = False) -> tk.Frame:
        """Create a visual card widget"""
        if is_back:
            # Card back (for opponent's hand)
            card_frame = tk.Frame(parent, bg='#8e44ad', width=80, height=110, relief=tk.RAISED, borderwidth=2)
            card_frame.pack_propagate(False)
            tk.Label(
                card_frame,
                text="🃏",
                font=('Arial', 40),
                bg='#8e44ad',
                fg='white'
            ).pack(expand=True)
        else:
            # Full card display - case insensitive type check
            bg_color = '#3498db' if card.card_type.lower() == 'troop' else '#9b59b6'
            if card.is_tapped:
                bg_color = '#7f8c8d'  # Gray when tapped
            
            card_frame = tk.Frame(parent, bg=bg_color, width=120, height=200, relief=tk.RAISED, borderwidth=2)
            
            # Add TAPPED indicator if tapped
            if card.is_tapped:
                tk.Label(
                    card_frame,
                    text="💤",
                    font=('Arial', 16),
                    bg=bg_color,
                    fg='white'
                ).place(relx=0.5, rely=0.5, anchor='center')
                # Explicit status badge (summoning sick / tapped)
                tk.Label(
                    card_frame,
                    text="⏳ Not Ready",
                    font=('Arial', 7, 'bold'),
                    bg=bg_color,
                    fg='#ecf0f1'
                ).pack(side=tk.BOTTOM, pady=2)
            card_frame.pack_propagate(False)
            
            # Mana cost - frame en esquina superior derecha
            mana_frame = tk.Frame(card_frame, bg=bg_color)
            mana_frame.pack(anchor='ne', padx=2, pady=2)
            
            mana_label = tk.Label(
                mana_frame,
                text=f"💎{card.cost}",
                font=('Arial', 10, 'bold'),
                bg=bg_color,
                fg='white'
            )
            mana_label.pack()
            
            # Name
            name_label = tk.Label(
                card_frame,
                text=card.name[:13],
                font=('Arial', 9, 'bold'),
                bg=bg_color,
                fg='white',
                wraplength=110
            )
            name_label.pack(pady=(15, 2))
            
            # Stats (ALWAYS show for troops, even in hand)
            # Case-insensitive comparison for card type
            if card.card_type.lower() == 'troop':
                print(f"🎨 Creating card widget: {card.name} - ATK:{card.attack} DEF:{card.defense} Type:{card.card_type}")
                stats = tk.Label(
                    card_frame,
                    text=f"⚔️{card.attack} 🛡️{card.defense}",
                    font=('Arial', 11, 'bold'),
                    bg=bg_color,
                    fg='#f1c40f'
                )
                stats.pack(pady=2)
                
                # Abilities display for troops - BEFORE attack indicator
                if card.abilities:
                    # Build emoji badges + compact ability name
                    badges = self._ability_badges_from_list(card.abilities)
                    ability_display = card.abilities[0].split(':')[0] if card.abilities else ''
                    text = f"{badges} {ability_display[:9]}".strip()
                    ability_label = tk.Label(
                        card_frame,
                        text=text if text else '🌟',
                        font=('Arial', 8, 'bold'),
                        bg=bg_color,
                        fg='#f39c12'
                    )
                    ability_label.pack(pady=1)
                
                # Attack indicator (only in active zone)
                if card.can_attack:
                    tk.Label(
                        card_frame,
                        text="⚡",
                        font=('Arial', 11),
                        bg=bg_color,
                        fg='#e74c3c'
                    ).pack(pady=0)
            elif card.card_type.lower() == 'spell':
                # Show spell icon - más pequeño para que no se corte
                spell_label = tk.Label(
                    card_frame,
                    text="✨",
                    font=('Arial', 25),
                    bg=bg_color,
                    fg='#f39c12'
                )
                spell_label.pack(pady=5)
        
        if clickable and on_click:
            # Set cursor only on main frame
            card_frame.config(cursor='hand2')
            
            # Bind click to frame and all children recursively
            def bind_click_recursive(widget):
                def on_click_debug(e):
                    print(f"🖱️ Click detected on widget, calling on_click()")
                    on_click()
                widget.bind('<Button-1>', on_click_debug, add='+')
                for child in widget.winfo_children():
                    bind_click_recursive(child)
            
            bind_click_recursive(card_frame)
            
            # Hover effect - only bind to main frame
            def on_enter(e):
                card_frame.config(relief=tk.SUNKEN, borderwidth=3)
            
            def on_leave(e):
                card_frame.config(relief=tk.RAISED, borderwidth=2)
            
            card_frame.bind('<Enter>', on_enter, add='+')
            card_frame.bind('<Leave>', on_leave, add='+')
        
        # Add tooltips AFTER all other bindings - must be at the end
        if not is_back and card.abilities:
            if card.card_type.lower() == 'spell':
                spell_effects = '\n'.join(card.abilities)
                print(f"🔮 Creating SPELL tooltip for {card.name}: {spell_effects[:50]}...")
                self._create_tooltip(card_frame, f"✨ SPELL EFFECT:\n{spell_effects}")
            elif card.card_type.lower() == 'troop':
                full_abilities = '\n'.join(card.abilities)
                print(f"🔮 Creating TROOP tooltip for {card.name}: {full_abilities[:50]}...")
                self._create_tooltip(card_frame, f"⚡ ABILITY:\n{full_abilities}")
        
        return card_frame
    
    def update_opponent_hand(self, card_count: int):
        """Update opponent's hand display (card backs)"""
        # Clear existing
        for widget in self.opponent_hand_frame.winfo_children():
            widget.destroy()
        
        self.opponent_hand_count = card_count
        
        # Show card backs
        for _ in range(card_count):
            card_frame = tk.Frame(
                self.opponent_hand_frame,
                bg='#8e44ad',
                width=50,
                height=70,
                relief=tk.RAISED,
                borderwidth=2
            )
            card_frame.pack(side=tk.LEFT, padx=2)
            card_frame.pack_propagate(False)
            
            tk.Label(
                card_frame,
                text="🃏",
                font=('Arial', 24),
                bg='#8e44ad',
                fg='white'
            ).pack(expand=True)
    
    def _get_cards_hash(self, cards: List[CardDisplay]) -> str:
        """Generate a hash string from card list to detect changes"""
        if not cards:
            return "empty"
        # Include card count in hash to detect additions/removals
        return f"count:{len(cards)}|" + "|".join([
            f"{c.name}:{c.cost}:{c.attack}:{c.defense}:{c.is_tapped}"
            for c in cards
        ])
    
    def update_opponent_active(self, cards: List[CardDisplay]):
        """Update opponent's active zone"""
        # Check if anything actually changed
        new_hash = self._get_cards_hash(cards)
        if new_hash == self._last_update_hash.get('opponent_active', ''):
            return  # No changes, skip update to prevent flickering
        self._last_update_hash['opponent_active'] = new_hash
        
        # Determine indices that changed/are new for spawn highlight
        prev_ids = self._prev_ids.get('opponent_active', [])
        new_ids = [self._card_id(c) for c in cards]
        changed_indices = {i for i in range(len(new_ids)) if i >= len(prev_ids) or (i < len(prev_ids) and new_ids[i] != prev_ids[i])}

        # Clear existing
        for widget in self.opponent_active_frame.winfo_children():
            widget.destroy()
        
        self.opponent_active = cards  # ¡IMPORTANTE! Guardar la lista
        self.opponent_active_widgets = []
        
        if not cards:
            tk.Label(
                self.opponent_active_frame,
                text="No creatures",
                font=('Arial', 10, 'italic'),
                bg='#34495e',
                fg='#95a5a6'
            ).pack(expand=True)
            self._prev_ids['opponent_active'] = []
            return
        
        for i, card in enumerate(cards):
            w = self._create_card_widget(card, self.opponent_active_frame)
            w.pack(side=tk.LEFT, padx=3, pady=5)
            self.opponent_active_widgets.append(w)
            # Highlight new/changed cards (token spawn gets special color)
            if i in changed_indices:
                if ('mystara' in card.name.lower()) or ('token' in card.name.lower()):
                    self._animate_token_spawn(w)
                else:
                    self._animate_pulse(w)
        self._prev_ids['opponent_active'] = new_ids
    
    def update_my_active(self, cards: List[CardDisplay]):
        """Update my active zone"""
        # Check if anything actually changed (include attack mode state in hash)
        new_hash = self._get_cards_hash(cards) + f":{self.attack_mode}:{len(self.selected_attackers)}"
        if new_hash == self._last_update_hash.get('my_active', ''):
            return  # No changes, skip update to prevent flickering
        self._last_update_hash['my_active'] = new_hash
        
        # Determine indices that changed/are new for spawn highlight
        prev_ids = self._prev_ids.get('my_active', [])
        new_ids = [self._card_id(c) for c in cards]
        changed_indices = {i for i in range(len(new_ids)) if i >= len(prev_ids) or (i < len(prev_ids) and new_ids[i] != prev_ids[i])}

        # Clear existing
        for widget in self.my_active_frame.winfo_children():
            widget.destroy()
        
        self.my_active = cards
        self.my_active_widgets = []
        
        if not cards:
            tk.Label(
                self.my_active_frame,
                text="No creatures",
                font=('Arial', 10, 'italic'),
                bg='#2c3e50',
                fg='#95a5a6'
            ).pack(expand=True)
            self._prev_ids['my_active'] = []
            return
        
        for i, card in enumerate(cards):
            # Card is clickable in attack mode if it's not tapped
            clickable = self.attack_mode and not card.is_tapped
            print(f"🎯 Card {card.name}: attack_mode={self.attack_mode}, is_tapped={card.is_tapped}, clickable={clickable}")
            
            # Only pass on_click if card is actually clickable
            if clickable:
                on_click = lambda idx=i: self._toggle_attacker(idx)
            else:
                on_click = None
            
            card_widget = self._create_card_widget(
                card,
                self.my_active_frame,
                clickable=clickable,
                on_click=on_click
            )
            card_widget.pack(side=tk.LEFT, padx=3, pady=5)
            self.my_active_widgets.append(card_widget)
            # Highlight new/changed cards (token spawn gets special color)
            if i in changed_indices:
                if ('mystara' in card.name.lower()) or ('token' in card.name.lower()):
                    self._animate_token_spawn(card_widget)
                else:
                    self._animate_pulse(card_widget)
            
            # Add ability button if card has activated ability and is ready
            if card.has_activated_ability and not card.is_tapped and self.is_my_turn and not self.attack_mode:
                ability_btn = tk.Button(
                    card_widget,
                    text="⚡",
                    font=('Arial', 10, 'bold'),
                    bg='#f39c12',
                    fg='white',
                    width=2,
                    command=lambda idx=i: self.on_activate_ability(idx)
                )
                ability_btn.place(relx=0.05, rely=0.05)
            
            # Highlight selected attackers
            if self.attack_mode and i in self.selected_attackers:
                times_selected = self.selected_attackers.count(i)
                card_widget.config(borderwidth=4, relief=tk.SOLID, bg='#e74c3c')
                
                # If selected multiple times (Furia), add indicator
                if times_selected > 1:
                    indicator = tk.Label(
                        card_widget,
                        text=f"x{times_selected}",
                        font=('Arial', 16, 'bold'),
                        bg='#e74c3c',
                        fg='white'
                    )
                    indicator.place(relx=0.5, rely=0.5, anchor='center')
        self._prev_ids['my_active'] = new_ids
    
    def update_my_hand(self, cards: List[CardDisplay]):
        """Update my hand"""
        # Check if anything actually changed (include turn state in hash)
        new_hash = self._get_cards_hash(cards) + f":{self.is_my_turn}:{self.attack_mode}"
        if new_hash == self._last_update_hash.get('my_hand', ''):
            return  # No changes, skip update to prevent flickering
        self._last_update_hash['my_hand'] = new_hash
        
        # Clear existing
        for widget in self.my_hand_frame.winfo_children():
            widget.destroy()
        
        self.my_hand = cards
        self.my_hand_widgets = []
        
        if not cards:
            tk.Label(
                self.my_hand_frame,
                text="No cards in hand",
                font=('Arial', 10, 'italic'),
                bg='#16213e',
                fg='#95a5a6'
            ).pack(expand=True)
            self._prev_ids['my_hand'] = []
            return
        
        for i, card in enumerate(cards):
            clickable = self.is_my_turn and not self.attack_mode
            
            # Only pass on_click if card is actually clickable
            if clickable:
                on_click = lambda idx=i: self._on_card_clicked(idx)
            else:
                on_click = None
            
            w = self._create_card_widget(
                card,
                self.my_hand_frame,
                clickable=clickable,
                on_click=on_click
            )
            w.pack(side=tk.LEFT, padx=3, pady=5)
            self.my_hand_widgets.append(w)
        self._prev_ids['my_hand'] = [self._card_id(c) for c in cards]
    
    # ============================================
    # Action Handlers
    # ============================================
    
    def _on_card_clicked(self, index: int):
        """Handle card click in hand"""
        if self.is_my_turn and not self.attack_mode:
            if index >= len(self.my_hand):
                return
            
            card = self.my_hand[index]
            
            # Check if it's a spell that needs target selection
            if card.card_type.lower() == 'spell':
                # Determine spell target type from description
                desc = ' '.join(card.abilities) if card.abilities else ''
                
                # One-target damage spells (can target troops or player)
                if any(name in card.name for name in ['Rayo', 'Bola de Fuego', 'Descarga Electrica']):
                    self._select_spell_target_single(index, can_target_player=True)
                    return
                
                # Destruction spells (troops only)
                elif 'Destierro' in card.name:
                    self._select_spell_target_single(index, can_target_player=False)
                    return
                elif 'Aniquilar' in card.name:
                    self._select_spell_target_aniquilar(index)
                    return
                
                # Freeze spells (enemy troops only)
                elif 'Prision de Luz' in card.name or 'Prisión de Luz' in card.name:
                    self._select_spell_target_single(index, can_target_player=False)
                    return
                
                # Sacrifice spells (friendly troops only)
                elif 'Pacto de Sangre' in card.name:
                    self._select_spell_target_friendly(index)
                    return
                
                # Area damage and self-target spells don't need selection
                # (Rafaga de Flechas, Tormenta de Fuego, Curación, etc.)
            
            # Play card without target (troops or self-target spells)
            self.on_play_card(index, None)
    
    def _on_end_turn_clicked(self):
        """Handle end turn button"""
        if self.is_my_turn:
            self.on_end_turn()
    
    def _on_attack_clicked(self):
        """Handle attack button - enter attack mode"""
        if self.is_my_turn and self.my_active and not self.waiting_for_blockers:
            # Safety: ensure there is at least one eligible attacker
            # Be tolerant of inconsistent 'can_attack' from server; rely on tap state
            if not any((not c.is_tapped) for c in self.my_active):
                self.log_action("⚠️ No creatures are ready to attack")
                self._update_attack_mode_ui()
                return
            self.attack_mode = True
            self.selected_attackers = []
            self._update_attack_mode_ui()
            self.log_action("⚔️ Select creatures to attack with, then click CONFIRM ATTACKS")
    
    def _on_cancel_attack_clicked(self):
        """Cancel attack mode"""
        self.attack_mode = False
        self.selected_attackers = []
        self._update_attack_mode_ui()
        self.log_action("❌ Attack cancelled")
    
    def _toggle_attacker(self, index: int):
        """Toggle creature as attacker"""
        print(f"🔥 _toggle_attacker called with index={index}")
        # Verificar que la criatura puede atacar (no está tappeada)
        if index >= len(self.my_active):
            print(f"❌ Index {index} >= len(my_active) {len(self.my_active)}")
            return
        
        card = self.my_active[index]
        print(f"🔥 Card: {card.name}, can_attack={card.can_attack}, is_tapped={card.is_tapped}")
        # Only block selection if tapped; ignore possibly stale 'can_attack'
        if card.is_tapped:
            self.log_action(f"⚠️ {card.name} cannot attack (tapped)")
            return
        
        # Check if card has Furia ability
        has_furia = any('Furia' in ability or 'Fury' in ability for ability in card.abilities) if card.abilities else False
        times_selected = self.selected_attackers.count(index)
        
        # Toggle selection
        if times_selected > 0:
            # Card is already selected - remove one instance
            if not has_furia:
                # Non-Furia: remove all instances (should only be 1)
                while index in self.selected_attackers:
                    self.selected_attackers.remove(index)
                self.log_action(f"❌ {card.name} removed from attackers")
            elif times_selected >= 2:
                # Furia at max attacks: remove one instance
                self.selected_attackers.remove(index)
                self.log_action(f"❌ {card.name} removed from attackers (attacks: {times_selected - 1}/2)")
            else:
                # Furia with 1 attack: add second attack
                self.selected_attackers.append(index)
                self.log_action(f"⚔️ {card.name} selected to attack TWICE! (Furia)")
        else:
            # First selection - add to list
            self.selected_attackers.append(index)
            message = f"⚔️ {card.name} selected to attack"
            if has_furia:
                message += " (can attack twice - click again for 2nd attack)"
            self.log_action(message)
        
        self.update_my_active(self.my_active)  # Refresh to show selection
    
    def _update_attack_mode_ui(self):
        """Update UI for attack mode"""
        if self.attack_mode:
            self.attack_button.config(text="CONFIRM ATTACKS", bg='#27ae60', command=self._confirm_attacks)
            self.cancel_attack_button.config(state=tk.NORMAL)
            self.end_turn_button.config(state=tk.DISABLED)
        elif self.waiting_for_blockers:
            # Disable all action buttons while waiting for blockers
            self.attack_button.config(text="WAITING FOR BLOCKERS...", bg='#7f8c8d', state=tk.DISABLED)
            self.cancel_attack_button.config(state=tk.DISABLED)
            self.end_turn_button.config(state=tk.DISABLED)
        else:
            # Enable declare button only if there is at least one eligible attacker
            # Be tolerant of server sending stale 'can_attack' values; use tap state
            has_eligible_attackers = any((not c.is_tapped) for c in self.my_active)
            attack_btn_state = tk.NORMAL if (self.is_my_turn and has_eligible_attackers) else tk.DISABLED
            self.attack_button.config(text="DECLARE ATTACKS", bg='#c0392b', state=attack_btn_state, command=self._on_attack_clicked)
            self.cancel_attack_button.config(state=tk.DISABLED)
            if self.is_my_turn:
                self.end_turn_button.config(state=tk.NORMAL)
        
        # Refresh active zone
        self.update_my_active(self.my_active)
    
    def _confirm_attacks(self):
        """Confirm selected attackers and choose targets"""
        if not self.selected_attackers:
            self.log_action("⚠️ No attackers selected")
            return
        
        # Now we need to select targets for each attacker
        self.log_action(f"⚔️ {len(self.selected_attackers)} attackers selected. Choose targets...")
        self._select_attack_targets()
    
    def _select_attack_targets(self):
        """Open dialog to select targets for each attacker"""
        import tkinter as tk
        from tkinter import messagebox
        
        # Debug: Check opponent active zone
        print(f"🔍 DEBUG: Opponent active zone has {len(self.opponent_active)} creatures")
        for i, card in enumerate(self.opponent_active):
            print(f"   {i}: {card.name} (HP: {card.defense})")
        
        # Check for Taunt creatures
        taunt_indices = []
        for i, card in enumerate(self.opponent_active):
            if card.abilities:
                for ability in card.abilities:
                    if 'Taunt' in ability or 'Provocar' in ability:
                        taunt_indices.append(i)
                        break
        
        has_taunt = len(taunt_indices) > 0
        if has_taunt:
            self.log_action(f"⚠️ Enemy has Taunt! Must attack those creatures first!")
        
        # Create target selection window
        target_window = tk.Toplevel(self.root)
        target_window.title("Select Attack Targets")
        target_window.geometry("500x600")
        target_window.configure(bg='#1a1a2e')
        target_window.grab_set()
        
        header_text = "🎯 Select targets for your attackers"
        if has_taunt:
            header_text = "🛡️ Must attack Taunt creatures!"
        
        tk.Label(
            target_window,
            text=header_text,
            font=('Arial', 14, 'bold'),
            bg='#1a1a2e',
            fg='#f39c12' if has_taunt else '#f1c40f'
        ).pack(pady=10)
        
        # Store targets: {attacker_index: "player" | ("card", card_index)}
        attack_targets = {}
        
        # Create frame for each attacker
        attackers_frame = tk.Frame(target_window, bg='#1a1a2e')
        attackers_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        for attacker_idx in self.selected_attackers:
            attacker = self.my_active[attacker_idx]
            
            # Frame for this attacker
            atk_frame = tk.Frame(attackers_frame, bg='#2c3e50', relief=tk.RAISED, borderwidth=2)
            atk_frame.pack(fill=tk.X, pady=5)
            
            # Attacker info
            tk.Label(
                atk_frame,
                text=f"⚔️ {attacker.name} ({attacker.attack} ATK)",
                font=('Arial', 11, 'bold'),
                bg='#2c3e50',
                fg='white'
            ).pack(pady=5)
            
            # Target selection variable - default to first taunt if exists
            default_target = f"card_{taunt_indices[0]}" if has_taunt else "player"
            target_var = tk.StringVar(value=default_target)
            attack_targets[attacker_idx] = target_var
            
            # Button to attack player (only if no taunt)
            if not has_taunt:
                tk.Radiobutton(
                    atk_frame,
                    text=f"🎯 Attack {self.opponent_name} directly",
                    variable=target_var,
                    value="player",
                    font=('Arial', 10),
                    bg='#2c3e50',
                    fg='white',
                    selectcolor='#34495e',
                    activebackground='#2c3e50',
                    activeforeground='white'
                ).pack(anchor='w', padx=20, pady=2)
            
            # Buttons for opponent creatures
            if self.opponent_active:
                if has_taunt:
                    tk.Label(
                        atk_frame,
                        text="Must attack Taunt creatures:",
                        font=('Arial', 9, 'italic'),
                        bg='#2c3e50',
                        fg='#f39c12'
                    ).pack(anchor='w', padx=20, pady=(5, 2))
                else:
                    tk.Label(
                        atk_frame,
                        text="Or attack a creature:",
                        font=('Arial', 9, 'italic'),
                        bg='#2c3e50',
                        fg='#95a5a6'
                    ).pack(anchor='w', padx=20, pady=(5, 2))
                
                for i, opp_card in enumerate(self.opponent_active):
                    # Check if this card has taunt
                    is_taunt = i in taunt_indices
                    
                    # Only show taunt creatures if taunt exists, otherwise show all
                    if has_taunt and not is_taunt:
                        continue
                    
                    card_text = f"  🛡️ {opp_card.name} ({opp_card.defense} HP)"
                    if is_taunt:
                        card_text = f"  🛡️ {opp_card.name} ({opp_card.defense} HP) [TAUNT]"
                    
                    tk.Radiobutton(
                        atk_frame,
                        text=card_text,
                        variable=target_var,
                        value=f"card_{i}",
                        font=('Arial', 9),
                        bg='#2c3e50',
                        fg='#f39c12' if is_taunt else '#ecf0f1',
                        selectcolor='#34495e',
                        activebackground='#2c3e50',
                        activeforeground='white'
                    ).pack(anchor='w', padx=40, pady=1)
        
        # Confirm button
        def confirm_targets():
            # Build targets list
            targets = []
            for attacker_idx in self.selected_attackers:
                target_str = attack_targets[attacker_idx].get()
                if target_str == "player":
                    targets.append("player")
                elif target_str.startswith("card_"):
                    card_idx = int(target_str.split("_")[1])
                    targets.append({"type": "card", "index": card_idx})
                else:
                    targets.append("player")
            
            # Close window
            target_window.destroy()
            
            # Send attack command
            self.on_declare_attacks(self.selected_attackers, targets)
            
            # Check if any attack targets the player (which requires blocker response)
            has_player_attack = any(t == "player" for t in targets)
            
            # Reset attack mode
            self.attack_mode = False
            self.selected_attackers = []
            
            # If attacking player, set waiting state and disable actions
            if has_player_attack:
                print("🔒 Setting waiting_for_blockers = True")
                self.waiting_for_blockers = True
                self.log_action("⚔️ Attacks declared! Waiting for opponent to choose blockers...")
            else:
                self.log_action("⚔️ Attacks declared!")
            
            self._update_attack_mode_ui()
        
        tk.Button(
            target_window,
            text="⚔️ CONFIRM ATTACKS",
            command=confirm_targets,
            font=('Arial', 12, 'bold'),
            bg='#27ae60',
            fg='white',
            width=20,
            height=2
        ).pack(pady=15)
        
        # Cancel button
        def cancel_targets():
            target_window.destroy()
            self.log_action("❌ Target selection cancelled")
        
        tk.Button(
            target_window,
            text="Cancel",
            command=cancel_targets,
            font=('Arial', 10),
            bg='#e74c3c',
            fg='white',
            width=15
        ).pack(pady=5)
    
    def _send_chat(self):
        """Send chat message"""
        message = self.chat_entry.get().strip()
        if message:
            self.on_send_chat(message)
            self.chat_entry.delete(0, tk.END)
    
    def _select_spell_target_single(self, card_index: int, can_target_player: bool):
        """Open dialog to select a single target for a spell"""
        import tkinter as tk
        
        card = self.my_hand[card_index]
        
        # Create target selection window
        target_window = tk.Toplevel(self.root)
        target_window.title(f"Select Target for {card.name}")
        target_window.geometry("400x500")
        target_window.configure(bg='#1a1a2e')
        target_window.grab_set()
        
        tk.Label(
            target_window,
            text=f"🎯 Select target for {card.name}",
            font=('Arial', 14, 'bold'),
            bg='#1a1a2e',
            fg='#f39c12'
        ).pack(pady=10)
        
        target_var = tk.StringVar(value="none")
        
        # Target player option (if allowed)
        if can_target_player:
            tk.Radiobutton(
                target_window,
                text=f"👤 Target {self.opponent_name} ({self.opponent_life} HP)",
                variable=target_var,
                value="player",
                font=('Arial', 11),
                bg='#1a1a2e',
                fg='white',
                selectcolor='#34495e',
                activebackground='#1a1a2e',
                activeforeground='white'
            ).pack(anchor='w', padx=20, pady=5)
        
        # Target opponent troops
        if self.opponent_active:
            tk.Label(
                target_window,
                text="Or target an enemy creature:",
                font=('Arial', 10, 'italic'),
                bg='#1a1a2e',
                fg='#95a5a6'
            ).pack(anchor='w', padx=20, pady=(10, 5))
            
            for i, opp_card in enumerate(self.opponent_active):
                tk.Radiobutton(
                    target_window,
                    text=f"  🎯 {opp_card.name} ({opp_card.attack}/{opp_card.defense})",
                    variable=target_var,
                    value=f"card_{i}",
                    font=('Arial', 10),
                    bg='#1a1a2e',
                    fg='#ecf0f1',
                    selectcolor='#34495e',
                    activebackground='#1a1a2e',
                    activeforeground='white'
                ).pack(anchor='w', padx=40, pady=2)
        
        # Confirm button
        def confirm_target():
            target_str = target_var.get()
            if target_str == "none":
                self.log_action("⚠️ No target selected")
                return
            
            target_window.destroy()
            
            # Parse target
            if target_str == "player":
                self.on_play_card(card_index, "player")
            elif target_str.startswith("card_"):
                card_idx = int(target_str.split("_")[1])
                self.on_play_card(card_index, card_idx)
            
            self.log_action(f"✨ {card.name} cast!")
        
        tk.Button(
            target_window,
            text="✨ CAST SPELL",
            command=confirm_target,
            font=('Arial', 12, 'bold'),
            bg='#9b59b6',
            fg='white',
            width=20,
            height=2
        ).pack(pady=15)
        
        # Cancel button
        tk.Button(
            target_window,
            text="Cancel",
            command=lambda: [target_window.destroy(), self.log_action("❌ Spell cancelled")],
            font=('Arial', 10),
            bg='#e74c3c',
            fg='white',
            width=15
        ).pack(pady=5)
    
    def _select_spell_target_aniquilar(self, card_index: int):
        """Open dialog to select target for Aniquilar (damaged troops only)"""
        import tkinter as tk
        
        card = self.my_hand[card_index]
        
        # Filter damaged troops
        damaged_troops = [(i, c) for i, c in enumerate(self.opponent_active) if c.defense < c.attack]
        
        if not damaged_troops:
            self.log_action("⚠️ No damaged enemy troops to target!")
            return
        
        # Create target selection window
        target_window = tk.Toplevel(self.root)
        target_window.title(f"Select Target for {card.name}")
        target_window.geometry("400x400")
        target_window.configure(bg='#1a1a2e')
        target_window.grab_set()
        
        tk.Label(
            target_window,
            text=f"💀 Select damaged troop to destroy",
            font=('Arial', 14, 'bold'),
            bg='#1a1a2e',
            fg='#e74c3c'
        ).pack(pady=10)
        
        target_var = tk.StringVar(value="none")
        
        # Show only damaged troops
        for i, opp_card in damaged_troops:
            tk.Radiobutton(
                target_window,
                text=f"  💀 {opp_card.name} (HP: {opp_card.defense})",
                variable=target_var,
                value=f"card_{i}",
                font=('Arial', 11),
                bg='#1a1a2e',
                fg='#e74c3c',
                selectcolor='#34495e',
                activebackground='#1a1a2e',
                activeforeground='white'
            ).pack(anchor='w', padx=40, pady=5)
        
        # Confirm button
        def confirm_target():
            target_str = target_var.get()
            if target_str == "none":
                self.log_action("⚠️ No target selected")
                return
            
            target_window.destroy()
            
            # Parse target
            if target_str.startswith("card_"):
                card_idx = int(target_str.split("_")[1])
                self.on_play_card(card_index, card_idx)
            
            self.log_action(f"💀 {card.name} cast!")
        
        tk.Button(
            target_window,
            text="💀 DESTROY",
            command=confirm_target,
            font=('Arial', 12, 'bold'),
            bg='#c0392b',
            fg='white',
            width=20,
            height=2
        ).pack(pady=15)
        
        # Cancel button
        tk.Button(
            target_window,
            text="Cancel",
            command=lambda: [target_window.destroy(), self.log_action("❌ Spell cancelled")],
            font=('Arial', 10),
            bg='#95a5a6',
            fg='white',
            width=15
        ).pack(pady=5)
    
    def _select_spell_target_friendly(self, card_index: int):
        """Open dialog to select a friendly target for sacrifice"""
        import tkinter as tk
        
        card = self.my_hand[card_index]
        
        # Check if there are friendly troops to sacrifice
        if not self.my_active:
            self.log_action("⚠️ No friendly troops to sacrifice!")
            return
        
        # Create target selection window
        target_window = tk.Toplevel(self.root)
        target_window.title(f"Select Target for {card.name}")
        target_window.geometry("400x500")
        target_window.configure(bg='#1a1a2e')
        target_window.grab_set()
        
        tk.Label(
            target_window,
            text=f"🩸 Select friendly troop to sacrifice",
            font=('Arial', 14, 'bold'),
            bg='#1a1a2e',
            fg='#e74c3c'
        ).pack(pady=10)
        
        tk.Label(
            target_window,
            text="Choose one of your creatures:",
            font=('Arial', 10, 'italic'),
            bg='#1a1a2e',
            fg='#95a5a6'
        ).pack(anchor='w', padx=20, pady=(10, 5))
        
        target_var = tk.StringVar(value="none")
        
        # Show friendly troops
        for i, my_card in enumerate(self.my_active):
            tk.Radiobutton(
                target_window,
                text=f"  🩸 {my_card.name} ({my_card.attack}/{my_card.defense})",
                variable=target_var,
                value=f"card_{i}",
                font=('Arial', 11),
                bg='#1a1a2e',
                fg='#ecf0f1',
                selectcolor='#34495e',
                activebackground='#1a1a2e',
                activeforeground='white'
            ).pack(anchor='w', padx=40, pady=5)
        
        # Confirm button
        def confirm_target():
            target_str = target_var.get()
            if target_str == "none":
                self.log_action("⚠️ No target selected")
                return
            
            target_window.destroy()
            
            # Parse target (send as negative index to indicate friendly target)
            if target_str.startswith("card_"):
                card_idx = int(target_str.split("_")[1])
                # Send as negative to distinguish from enemy targets
                self.on_play_card(card_index, -card_idx - 1)
            
            self.log_action(f"🩸 {card.name} cast!")
        
        tk.Button(
            target_window,
            text="🩸 SACRIFICE",
            command=confirm_target,
            font=('Arial', 12, 'bold'),
            bg='#8e44ad',
            fg='white',
            width=20,
            height=2
        ).pack(pady=15)
        
        # Cancel button
        tk.Button(
            target_window,
            text="Cancel",
            command=lambda: [target_window.destroy(), self.log_action("❌ Spell cancelled")],
            font=('Arial', 10),
            bg='#95a5a6',
            fg='white',
            width=15
        ).pack(pady=5)
    
    # ============================================
    # State Update Methods
    # ============================================
    
    def reset_waiting_state(self):
        """Reset waiting for blockers state (called when combat resolves)"""
        if self.waiting_for_blockers:
            print("🔓 Resetting waiting_for_blockers - combat resolved")
            self.waiting_for_blockers = False
            self._update_attack_mode_ui()
            self.log_action("✅ Combat resolved, you can act again")
    
    def set_turn(self, is_my_turn: bool):
        """Update turn state"""
        # Only reset waiting state if turn actually changed
        if self.is_my_turn != is_my_turn:
            self.waiting_for_blockers = False
        
        self.is_my_turn = is_my_turn
        
        if is_my_turn:
            self.turn_indicator.config(text="✅ YOUR TURN - Play cards or attack!", fg='#f1c40f')
            # Use _update_attack_mode_ui to respect waiting_for_blockers state
            self._update_attack_mode_ui()
        else:
            self.turn_indicator.config(text="⏳ Opponent's turn...", fg='white')
            self.end_turn_button.config(state=tk.DISABLED)
            self.attack_button.config(state=tk.DISABLED)
            self.cancel_attack_button.config(state=tk.DISABLED)
        
        # Refresh hand to update clickability
        self.update_my_hand(self.my_hand)
    
    def update_player_stats(self, life: int, mana: int, max_mana: int):
        """Update my stats"""
        # Check if anything changed
        new_hash = f"{life}:{mana}:{max_mana}"
        if new_hash == self._last_update_hash.get('my_stats', ''):
            return  # No changes
        self._last_update_hash['my_stats'] = new_hash
        
        self.my_life = life
        self.my_mana = mana
        self.my_max_mana = max_mana
        self.my_info_label.config(text=f"🎮 {self.player_name} | ❤️ {life} | 💎 {mana}/{max_mana}")
    
    def update_opponent_stats(self, life: int, mana: int, max_mana: int, hand_count: int):
        """Update opponent stats"""
        # Check if anything changed
        new_hash = f"{life}:{mana}:{max_mana}:{hand_count}"
        if new_hash == self._last_update_hash.get('opponent_stats', ''):
            return  # No changes
        self._last_update_hash['opponent_stats'] = new_hash
        
        self.opponent_life = life
        self.opponent_mana = mana
        self.opponent_max_mana = max_mana
        self.opponent_hand_count = hand_count
        self.opponent_info_label.config(
            text=f"🎮 {self.opponent_name} | ❤️ {life} | 💎 {mana}/{max_mana} | 🃏 {hand_count} cards"
        )
    
    def set_my_champion(self, name: str, ability: str):
        """Set my champion info"""
        self.my_champion_name = name
        self.my_champion_ability = ability
        self.my_champion_label.config(text=f"👑 {name}")
        # Update tooltip
        for binding in self.my_champion_label.bind():
            self.my_champion_label.unbind(binding)
        self._create_tooltip(self.my_champion_label, f"{name}\n\n{ability}")
    
    def set_opponent_champion(self, name: str, ability: str):
        """Set opponent champion info"""
        self.opponent_champion_name = name
        self.opponent_champion_ability = ability
        self.opponent_champion_label.config(text=f"👑 {name}")
        # Update tooltip
        for binding in self.opponent_champion_label.bind():
            self.opponent_champion_label.unbind(binding)
        self._create_tooltip(self.opponent_champion_label, f"{name}\n\n{ability}")
    
    # ============================================
    # Log Methods
    # ============================================
    
    def log_action(self, message: str):
        """Add message to action log"""
        self.action_log.config(state=tk.NORMAL)
        self.action_log.insert(tk.END, f"{message}\n")
        self.action_log.see(tk.END)
        self.action_log.config(state=tk.DISABLED)
    
    def add_chat_message(self, sender: str, message: str):
        """Add message to chat"""
        self.chat_log.config(state=tk.NORMAL)
        
        # Color code messages
        if sender == self.player_name:
            color = '#3498db'
        elif sender == self.opponent_name:
            color = '#e74c3c'
        else:
            color = '#95a5a6'
        
        # Insert with tag
        tag_name = f"msg_{sender}"
        self.chat_log.tag_config(tag_name, foreground=color, font=('Arial', 9, 'bold'))
        
        self.chat_log.insert(tk.END, f"{sender}: ", tag_name)
        self.chat_log.insert(tk.END, f"{message}\n")
        self.chat_log.see(tk.END)
        self.chat_log.config(state=tk.DISABLED)
    
    def add_system_message(self, message: str):
        """Add system message to chat"""
        self.chat_log.config(state=tk.NORMAL)
        self.chat_log.tag_config("system", foreground='#f39c12', font=('Arial', 9, 'italic'))
        self.chat_log.insert(tk.END, f"🔔 {message}\n", "system")
        self.chat_log.see(tk.END)
        self.chat_log.config(state=tk.DISABLED)


# ============================================
# Helper function to create CardDisplay from dict
# ============================================

def card_from_dict(data: dict) -> CardDisplay:
    """Convert card data dictionary to CardDisplay"""
    return CardDisplay(
        name=data.get('name', 'Unknown'),
        cost=data.get('cost', 0),
        attack=data.get('attack', 0),
        defense=data.get('defense', 0),
        card_type=data.get('card_type', 'Troop'),
        abilities=data.get('abilities', []),
        can_attack=data.get('can_attack', False),
        is_tapped=data.get('is_tapped', False)
    )
