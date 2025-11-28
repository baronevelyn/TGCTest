"""
Deck Builder GUI for the TCG game.
Allows players to create custom decks and choose champions.
"""

import tkinter as tk
from tkinter import messagebox
from typing import List, Optional
import os
from .cards import TROOP_TEMPLATES, SPELL_TEMPLATES, create_card
from .champions import CHAMPION_LIST, Champion
from .models import Card, Deck


# Deck building rules
MIN_DECK_SIZE = 30
MAX_DECK_SIZE = 60
MIN_TROOPS = 15
MIN_SPELLS = 5


class DeckBuilder:
    """Deck builder interface."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Deck Builder - Mini TCG")
        self.root.geometry("1200x800")
        
        # Deck storage
        self.player_deck: List[Card] = []
        self.player_champion: Optional[Champion] = None
        self.ai_deck: List[Card] = []
        self.ai_champion: Optional[Champion] = None
        self.ai_config: Optional[dict] = None
        
        self.setup_ui()

    # ---------------------------
    # Emoji helpers
    # ---------------------------
    def _ability_emojis(self, ability: Optional[str]) -> str:
        """Return emoji badges for a troop ability string (handles combined like 'Taunt+Regeneracion')."""
        if not ability:
            return ""
        tokens = []
        # Normalize separators and split
        for part in ability.replace(',', '+').split('+'):
            t = part.strip().lower()
            if t:
                tokens.append(t)
        emojis = []
        mapping = {
            'taunt': '🛡️', 'provocar': '🛡️',
            'volar': '🪽', 'fly': '🪽', 'volador': '🪽',
            'regeneracion': '♻️', 'regeneración': '♻️',
            'absorber magia': '🧲', 'absorber': '🧲',
            'debilitar': '📉',
            'curacion al entrar': '💖', 'curación al entrar': '💖'
        }
        for t in tokens:
            # map multi-word first
            if t in mapping:
                e = mapping[t]
            else:
                # try partial contains
                if 'taunt' in t or 'provocar' in t:
                    e = '🛡️'
                elif 'volar' in t or 'fly' in t or 'volador' in t:
                    e = '🪽'
                elif 'regener' in t:
                    e = '♻️'
                elif 'absorber' in t:
                    e = '🧲'
                elif 'debilit' in t:
                    e = '📉'
                elif 'curacion' in t or 'curación' in t:
                    e = '💖'
                else:
                    e = ''
            if e and e not in emojis:
                emojis.append(e)
        return ' '.join(emojis)

    def _spell_emojis(self, spell_effect: str = '', description: str = '', name: str = '') -> str:
        """Return emojis for a spell based on effect/description/name."""
        text = f"{spell_effect} {description} {name}".lower()
        badges = []
        def add(e):
            if e not in badges:
                badges.append(e)
        if 'freeze' in text or 'congela' in text or 'prisión de luz' in text or 'prision de luz' in text:
            add('❄️')
        if 'sacrifice' in text or 'sacrificar' in text or 'sacrificio' in text:
            add('🩸')
        if 'heal' in text or 'curación' in text or 'curacion' in text:
            add('💖')
        if 'draw' in text or 'roba' in text or 'robar' in text:
            add('🃏')
        if 'mana' in text or 'maná' in text:
            add('💎')
        if 'destroy' in text or 'aniquila' in text or 'destierro' in text or 'destruir' in text:
            add('💀')
        if 'damage' in text or 'daño' in text or 'fuego' in text or 'rayo' in text:
            add('💥')
        return ' '.join(badges)
    
    def setup_ui(self):
        """Setup the deck builder interface."""
        # Title
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=60)
        title_frame.pack(fill='x')
        title_frame.pack_propagate(False)
        tk.Label(title_frame, text="⚔️ CONSTRUCTOR DE MAZOS ⚔️", 
                bg='#2c3e50', fg='white', font=('Arial', 18, 'bold')).pack(pady=15)
        
        # Main content
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Left: Card pool
        left_frame = tk.Frame(main_frame, relief='solid', bd=2)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        tk.Label(left_frame, text="📚 Cartas Disponibles", font=('Arial', 14, 'bold')).pack(pady=5)
        
        # Tabs for troops and spells
        tab_frame = tk.Frame(left_frame)
        tab_frame.pack(fill='x', padx=5)
        
        self.current_tab = tk.StringVar(value='troops')
        tk.Radiobutton(tab_frame, text="🛡️ Tropas", variable=self.current_tab, 
                      value='troops', command=self.update_card_pool,
                      font=('Arial', 10, 'bold')).pack(side='left', padx=5)
        tk.Radiobutton(tab_frame, text="⚡ Hechizos", variable=self.current_tab, 
                      value='spells', command=self.update_card_pool,
                      font=('Arial', 10, 'bold')).pack(side='left', padx=5)
        
        # Card pool listbox
        pool_frame = tk.Frame(left_frame)
        pool_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        pool_scroll = tk.Scrollbar(pool_frame)
        pool_scroll.pack(side='right', fill='y')
        
        self.pool_listbox = tk.Listbox(pool_frame, yscrollcommand=pool_scroll.set,
                                       font=('Courier', 10), height=20)
        self.pool_listbox.pack(side='left', fill='both', expand=True)
        pool_scroll.config(command=self.pool_listbox.yview)
        
        # Add card button
        tk.Button(left_frame, text="➕ Agregar al Mazo", command=self.add_card_to_deck,
                 bg='#27ae60', fg='white', font=('Arial', 11, 'bold'), height=2).pack(pady=5, fill='x', padx=5)
        
        # Right: Current deck
        right_frame = tk.Frame(main_frame, relief='solid', bd=2)
        right_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        tk.Label(right_frame, text="📋 Tu Mazo", font=('Arial', 14, 'bold')).pack(pady=5)
        
        # Deck stats
        stats_frame = tk.Frame(right_frame, bg='#ecf0f1', relief='solid', bd=1)
        stats_frame.pack(fill='x', padx=5, pady=5)
        
        self.deck_size_var = tk.StringVar(value="Cartas: 0/30-60")
        self.troops_var = tk.StringVar(value="Tropas: 0 (mín. 15)")
        self.spells_var = tk.StringVar(value="Hechizos: 0 (mín. 5)")
        
        tk.Label(stats_frame, textvariable=self.deck_size_var, bg='#ecf0f1', 
                font=('Arial', 10, 'bold')).pack(pady=2)
        tk.Label(stats_frame, textvariable=self.troops_var, bg='#ecf0f1', 
                font=('Arial', 10)).pack(pady=2)
        tk.Label(stats_frame, textvariable=self.spells_var, bg='#ecf0f1', 
                font=('Arial', 10)).pack(pady=2)
        
        # Champion selection
        champion_frame = tk.Frame(right_frame, bg='#34495e', relief='solid', bd=2)
        champion_frame.pack(fill='x', padx=5, pady=5)
        
        tk.Label(champion_frame, text="🎭 CAMPEÓN", bg='#34495e', fg='white', 
                font=('Arial', 11, 'bold')).pack(pady=3)
        
        self.champion_var = tk.StringVar(value="Ninguno")
        champion_label = tk.Label(champion_frame, textvariable=self.champion_var, 
                                 bg='#34495e', fg='#f39c12', font=('Arial', 10, 'bold'))
        champion_label.pack(pady=3)
        
        tk.Button(champion_frame, text="Elegir Campeón", command=self.choose_champion,
                 bg='#9b59b6', fg='white', font=('Arial', 10)).pack(pady=5)
        
        # Deck listbox
        deck_frame = tk.Frame(right_frame)
        deck_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        deck_scroll = tk.Scrollbar(deck_frame)
        deck_scroll.pack(side='right', fill='y')
        
        self.deck_listbox = tk.Listbox(deck_frame, yscrollcommand=deck_scroll.set,
                                       font=('Courier', 10), height=15)
        self.deck_listbox.pack(side='left', fill='both', expand=True)
        deck_scroll.config(command=self.deck_listbox.yview)
        
        # Remove card button
        tk.Button(right_frame, text="➖ Quitar del Mazo", command=self.remove_card_from_deck,
                 bg='#e74c3c', fg='white', font=('Arial', 11, 'bold'), height=2).pack(pady=5, fill='x', padx=5)
        
        # Bottom buttons
        bottom_frame = tk.Frame(self.root, bg='#ecf0f1')
        bottom_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Button(bottom_frame, text="🎲 Generar Mazo Aleatorio", command=self.generate_random_deck,
                 bg='#3498db', fg='white', font=('Arial', 11, 'bold'), width=25).pack(side='left', padx=5)
        
        tk.Button(bottom_frame, text="🗑️ Limpiar Mazo", command=self.clear_deck,
                 bg='#95a5a6', fg='white', font=('Arial', 11, 'bold'), width=20).pack(side='left', padx=5)
        
        tk.Button(bottom_frame, text="💾 GUARDAR MAZO", command=self.start_game,
                 bg='#27ae60', fg='white', font=('Arial', 14, 'bold'), width=15).pack(side='right', padx=5)
        
        # Tooltip support
        self.tooltip = None
        self.pool_listbox.bind('<Motion>', self.show_pool_tooltip)
        self.pool_listbox.bind('<Leave>', self.hide_tooltip)
        self.deck_listbox.bind('<Motion>', self.show_deck_tooltip)
        self.deck_listbox.bind('<Leave>', self.hide_tooltip)
        
        # Initialize
        self.update_card_pool()
        self.update_deck_display()
    
    def update_card_pool(self):
        """Update the card pool display."""
        self.pool_listbox.delete(0, tk.END)
        
        if self.current_tab.get() == 'troops':
            for name, cost, damage, ability, ability_desc, ability_type in TROOP_TEMPLATES:
                # Health is damage + 0-2 range
                health_range = f"{damage}-{damage+2}"
                badges = self._ability_emojis(ability)
                ability_str = f" [{ability}]" if ability else ""
                prefix = f"{badges} " if badges else ""
                line = f"{prefix}{name:20} | Coste:{cost} | {damage}/{health_range}{ability_str}"
                self.pool_listbox.insert(tk.END, line)
        else:
            for name, cost, damage, spell_target, spell_effect, description in SPELL_TEMPLATES:
                badges = self._spell_emojis(spell_effect, description, name)
                prefix = f"{badges} " if badges else ""
                line = f"{prefix}{name:20} | Coste:{cost} | {description}"
                self.pool_listbox.insert(tk.END, line)
    
    def add_card_to_deck(self):
        """Add selected card from pool to deck."""
        selection = self.pool_listbox.curselection()
        if not selection:
            messagebox.showwarning("Sin selección", "Por favor selecciona una carta para agregar.")
            return
        
        if len(self.player_deck) >= MAX_DECK_SIZE:
            messagebox.showwarning("Mazo lleno", f"El mazo no puede tener más de {MAX_DECK_SIZE} cartas.")
            return
        
        idx = selection[0]
        
        if self.current_tab.get() == 'troops':
            name, cost, damage, ability, ability_desc, ability_type = TROOP_TEMPLATES[idx]
            card = create_card(name, cost, damage, ability=ability, ability_desc=ability_desc, 
                             ability_type=ability_type, card_type='troop')
        else:
            name, cost, damage, spell_target, spell_effect, description = SPELL_TEMPLATES[idx]
            card = create_card(name, cost, damage, card_type='spell', 
                             spell_target=spell_target, spell_effect=spell_effect,
                             description=description)
        
        self.player_deck.append(card)
        self.update_deck_display()
    
    def remove_card_from_deck(self):
        """Remove selected card from deck."""
        selection = self.deck_listbox.curselection()
        if not selection:
            messagebox.showwarning("Sin selección", "Por favor selecciona una carta para quitar.")
            return
        
        idx = selection[0]
        del self.player_deck[idx]
        self.update_deck_display()
    
    def update_deck_display(self):
        """Update the deck listbox and stats."""
        self.deck_listbox.delete(0, tk.END)
        
        troop_count = 0
        spell_count = 0
        
        for card in self.player_deck:
            if card.card_type == 'troop':
                troop_count += 1
                badges = self._ability_emojis(getattr(card, 'ability', ''))
                ability_str = f" [{card.ability}]" if getattr(card, 'ability', '') else ""
                prefix = f"{badges} " if badges else ""
                line = f"🛡️ {prefix}{card.name:18} | Coste:{card.cost} | {card.damage}/{card.health}{ability_str}"
            else:
                spell_count += 1
                badges = self._spell_emojis(getattr(card, 'spell_effect', ''), getattr(card, 'description', ''), getattr(card, 'name', ''))
                prefix = f"{badges} " if badges else ""
                line = f"⚡ {prefix}{card.name:18} | Coste:{card.cost} | {card.description}"
            self.deck_listbox.insert(tk.END, line)
        
        # Update stats
        deck_size = len(self.player_deck)
        self.deck_size_var.set(f"Cartas: {deck_size}/{MIN_DECK_SIZE}-{MAX_DECK_SIZE}")
        
        troops_color = "green" if troop_count >= MIN_TROOPS else "red"
        self.troops_var.set(f"Tropas: {troop_count} (mín. {MIN_TROOPS})")
        
        spells_color = "green" if spell_count >= MIN_SPELLS else "red"
        self.spells_var.set(f"Hechizos: {spell_count} (mín. {MIN_SPELLS})")
    
    def show_pool_tooltip(self, event):
        """Show tooltip for card in pool."""
        self.hide_tooltip()
        
        index = self.pool_listbox.nearest(event.y)
        if index < 0:
            return
        
        # Get ability description
        ability_desc = None
        if self.current_tab.get() == 'troops':
            if index < len(TROOP_TEMPLATES):
                name, cost, damage, ability, ability_desc, ability_type = TROOP_TEMPLATES[index]
                if ability and ability_desc:
                    title = f"{self._ability_emojis(ability)} {ability}".strip()
                    self.create_tooltip(event, title, ability_desc)
        else:
            if index < len(SPELL_TEMPLATES):
                name, cost, damage, spell_target, spell_effect, description = SPELL_TEMPLATES[index]
                if description:
                    title = f"{self._spell_emojis(spell_effect, description, name)} {name}".strip()
                    self.create_tooltip(event, title, description)
    
    def show_deck_tooltip(self, event):
        """Show tooltip for card in deck."""
        self.hide_tooltip()
        
        index = self.deck_listbox.nearest(event.y)
        if index < 0 or index >= len(self.player_deck):
            return
        
        card = self.player_deck[index]
        if card.card_type == 'troop' and getattr(card, 'ability', '') and getattr(card, 'ability_desc', ''):
            title = f"{self._ability_emojis(card.ability)} {card.ability}".strip()
            self.create_tooltip(event, title, card.ability_desc)
        elif card.card_type == 'spell' and card.description:
            title = f"{self._spell_emojis(getattr(card, 'spell_effect', ''), getattr(card, 'description', ''), getattr(card, 'name', ''))} {card.name}".strip()
            self.create_tooltip(event, title, card.description)
    
    def create_tooltip(self, event, title, description):
        """Create a tooltip window."""
        x = event.x_root + 10
        y = event.y_root + 10
        
        self.tooltip = tk.Toplevel(self.root)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        
        frame = tk.Frame(self.tooltip, background="#2c3e50", relief='solid', borderwidth=1)
        frame.pack()
        
        title_label = tk.Label(frame, text=title, background="#2c3e50", 
                              foreground="#f39c12", font=('Arial', 10, 'bold'),
                              padx=8, pady=4)
        title_label.pack()
        
        desc_label = tk.Label(frame, text=description, background="#2c3e50", 
                             foreground="#ecf0f1", font=('Arial', 9),
                             wraplength=250, justify='left', padx=8, pady=4)
        desc_label.pack()
    
    def hide_tooltip(self, event=None):
        """Hide the tooltip."""
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None
    
    def choose_champion(self):
        """Open champion selection dialog."""
        dlg = tk.Toplevel(self.root)
        dlg.title("Elegir Campeón")
        dlg.geometry("800x600")
        dlg.transient(self.root)
        dlg.grab_set()
        
        tk.Label(dlg, text="🎭 ELIGE TU CAMPEÓN", font=('Arial', 16, 'bold')).pack(pady=10)
        
        # Create a frame with scrollbar
        canvas = tk.Canvas(dlg)
        scrollbar = tk.Scrollbar(dlg, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Champion buttons
        for i, champion in enumerate(CHAMPION_LIST):
            frame = tk.Frame(scrollable_frame, relief='solid', bd=2, bg='#ecf0f1')
            frame.pack(fill='x', padx=10, pady=5)
            
            def select_champ(c=champion):
                self.player_champion = c
                self.champion_var.set(f"{c.name} - {c.title}")
                dlg.destroy()
            
            # Champion info
            info_frame = tk.Frame(frame, bg='#ecf0f1')
            info_frame.pack(side='left', fill='both', expand=True, padx=10, pady=10)
            
            tk.Label(info_frame, text=f"🎭 {champion.name}", bg='#ecf0f1', 
                    font=('Arial', 12, 'bold'), fg='#2c3e50').pack(anchor='w')
            tk.Label(info_frame, text=champion.title, bg='#ecf0f1', 
                    font=('Arial', 10), fg='#7f8c8d').pack(anchor='w')
            tk.Label(info_frame, text=f"❤️ Vida: {champion.starting_life}", bg='#ecf0f1', 
                    font=('Arial', 10), fg='#e74c3c').pack(anchor='w', pady=2)
            tk.Label(info_frame, text=f"⚡ {champion.passive_name}", bg='#ecf0f1', 
                    font=('Arial', 10, 'bold'), fg='#9b59b6').pack(anchor='w')
            tk.Label(info_frame, text=champion.passive_description, bg='#ecf0f1', 
                    font=('Arial', 9), fg='#34495e', wraplength=500).pack(anchor='w', pady=2)
            
            # Select button
            tk.Button(frame, text="✓ ELEGIR", command=select_champ, bg='#27ae60', 
                     fg='white', font=('Arial', 11, 'bold'), width=12).pack(side='right', padx=10)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def generate_random_deck(self):
        """Generate a random deck."""
        if messagebox.askyesno("Generar Mazo", "¿Generar un mazo aleatorio de 40 cartas (25 tropas, 15 hechizos)?"):
            self.player_deck.clear()
            
            # Add 25 random troops
            import random
            for _ in range(25):
                name, cost, damage, ability, ability_desc, ability_type = random.choice(TROOP_TEMPLATES)
                card = create_card(name, cost, damage, ability=ability, ability_desc=ability_desc, 
                                 ability_type=ability_type, card_type='troop')
                self.player_deck.append(card)
            
            # Add 15 random spells
            for _ in range(15):
                name, cost, damage, spell_target, spell_effect, description = random.choice(SPELL_TEMPLATES)
                card = create_card(name, cost, damage, card_type='spell', 
                                 spell_target=spell_target, spell_effect=spell_effect,
                                 description=description)
                self.player_deck.append(card)
            
            self.update_deck_display()
    
    def clear_deck(self):
        """Clear the current deck."""
        if messagebox.askyesno("Limpiar Mazo", "¿Estás seguro de que quieres limpiar el mazo?"):
            self.player_deck.clear()
            self.update_deck_display()
    
    def start_game(self):
        """Validate deck and save it."""
        deck_size = len(self.player_deck)
        troop_count = sum(1 for c in self.player_deck if c.card_type == 'troop')
        spell_count = sum(1 for c in self.player_deck if c.card_type == 'spell')
        
        # Validate deck
        errors = []
        if deck_size < MIN_DECK_SIZE:
            errors.append(f"• El mazo debe tener al menos {MIN_DECK_SIZE} cartas (tienes {deck_size})")
        if deck_size > MAX_DECK_SIZE:
            errors.append(f"• El mazo no puede tener más de {MAX_DECK_SIZE} cartas (tienes {deck_size})")
        if troop_count < MIN_TROOPS:
            errors.append(f"• Debes tener al menos {MIN_TROOPS} tropas (tienes {troop_count})")
        if spell_count < MIN_SPELLS:
            errors.append(f"• Debes tener al menos {MIN_SPELLS} hechizos (tienes {spell_count})")
        if not self.player_champion:
            errors.append("• Debes elegir un campeón")
        
        if errors:
            messagebox.showerror("Mazo inválido", "Tu mazo no cumple los requisitos:\n\n" + "\n".join(errors))
            return
        
        # Ask for deck name
        self.save_deck_with_name()
    
    def save_deck_with_name(self):
        """Ask for deck name and save the deck."""
        # Create dialog to ask for name
        dlg = tk.Toplevel(self.root)
        dlg.title("Guardar Mazo")
        dlg.geometry("400x200")
        dlg.transient(self.root)
        dlg.grab_set()
        
        tk.Label(dlg, text="💾 Guardar Mazo", font=('Arial', 16, 'bold')).pack(pady=10)
        tk.Label(dlg, text="Ingresa un nombre para tu mazo:", font=('Arial', 11)).pack(pady=5)
        
        name_var = tk.StringVar()
        entry = tk.Entry(dlg, textvariable=name_var, font=('Arial', 12), width=30)
        entry.pack(pady=10)
        entry.focus()
        
        result = {'saved': False}
        
        def save():
            deck_name = name_var.get().strip()
            if not deck_name:
                messagebox.showwarning("Nombre vacío", "Por favor ingresa un nombre para el mazo.", parent=dlg)
                return
            
            from .deck_manager import save_deck
            if save_deck(deck_name, self.player_deck, self.player_champion.name):
                messagebox.showinfo("Éxito", f"¡Mazo '{deck_name}' guardado correctamente!", parent=dlg)
                result['saved'] = True
                dlg.destroy()
                self.root.destroy()
                # Reabrir el menú principal
                self.back_to_menu()
            else:
                messagebox.showerror("Error", "No se pudo guardar el mazo.", parent=dlg)
        
        def cancel():
            dlg.destroy()
        
        btn_frame = tk.Frame(dlg)
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="💾 GUARDAR", command=save,
                 bg='#27ae60', fg='white', font=('Arial', 11, 'bold'), width=12).pack(side='left', padx=5)
        tk.Button(btn_frame, text="❌ CANCELAR", command=cancel,
                 bg='#95a5a6', fg='white', font=('Arial', 11, 'bold'), width=12).pack(side='left', padx=5)
        
        # Bind Enter key
        entry.bind('<Return>', lambda e: save())
    
    def back_to_menu(self):
        """Return to main menu."""
        import subprocess
        import sys
        python_exe = sys.executable
        script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'main_menu.py')
        subprocess.Popen([python_exe, script_path])
    
    def get_deck_data(self) -> List[dict]:
        """Exportar mazo en formato serializable para multiplayer
        
        Returns:
            Lista de diccionarios con datos de cartas
        """
        deck_data = []
        for card in self.player_deck:
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
        return deck_data
    
    def get_champion_data(self) -> Optional[dict]:
        """Exportar campeón en formato serializable para multiplayer
        
        Returns:
            Diccionario con datos del campeón o None
        """
        if not self.player_champion:
            return None
        
        return {
            'name': self.player_champion.name,
            'title': self.player_champion.title,
            'starting_life': self.player_champion.starting_life,
            'passive_name': self.player_champion.passive_name,
            'passive_description': self.player_champion.passive_description,
            'ability_type': self.player_champion.ability_type,
            'ability_value': self.player_champion.ability_value
        }
    
    def validate_deck_for_multiplayer(self) -> tuple[bool, str]:
        """Validar mazo para multiplayer
        
        Returns:
            (es_valido, mensaje_error)
        """
        deck_size = len(self.player_deck)
        troop_count = sum(1 for c in self.player_deck if c.card_type == 'troop')
        spell_count = sum(1 for c in self.player_deck if c.card_type == 'spell')
        
        # Validar deck
        errors = []
        if deck_size < MIN_DECK_SIZE:
            errors.append(f"• El mazo debe tener al menos {MIN_DECK_SIZE} cartas (tienes {deck_size})")
        if deck_size > MAX_DECK_SIZE:
            errors.append(f"• El mazo no puede tener más de {MAX_DECK_SIZE} cartas (tienes {deck_size})")
        if troop_count < MIN_TROOPS:
            errors.append(f"• Debes tener al menos {MIN_TROOPS} tropas (tienes {troop_count})")
        if spell_count < MIN_SPELLS:
            errors.append(f"• Debes tener al menos {MIN_SPELLS} hechizos (tienes {spell_count})")
        if not self.player_champion:
            errors.append("• Debes elegir un campeón")
        
        if errors:
            return False, "Tu mazo no cumple los requisitos:\n\n" + "\n".join(errors)
        
        return True, "Mazo válido"


if __name__ == '__main__':
    root = tk.Tk()
    DeckBuilder(root)
    root.mainloop()
