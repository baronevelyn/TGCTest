"""
Deck Selector - Permite elegir entre mazo aleatorio o un deck guardado.
"""
import tkinter as tk
from tkinter import messagebox
from typing import Optional, Callable, Tuple, List
from .deck_manager import get_saved_decks, load_deck, get_deck_info
from .cards import build_random_deck
from .champions import get_random_champion, CHAMPION_LIST


def show_deck_selector(callback: Callable[[List, object], None], parent=None, on_cancel: Optional[Callable] = None):
    """
    Muestra el selector de deck.
    
    Args:
        callback: Función a llamar con (deck_cards, champion) cuando se seleccione
        parent: Ventana padre
        on_cancel: Función a llamar cuando se cancele
    
    Returns:
        Ventana del selector
    """
    if parent:
        window = tk.Toplevel(parent)
        window.transient(parent)
    else:
        window = tk.Tk()
    
    window.title("Seleccionar Mazo")
    window.geometry("700x650")
    window.configure(bg='#0f0f1e')
    
    # Centrar ventana
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry(f'{width}x{height}+{x}+{y}')
    
    # Title
    title_frame = tk.Frame(window, bg='#1a1a2e', height=80)
    title_frame.pack(fill='x')
    title_frame.pack_propagate(False)
    
    tk.Label(title_frame, text="🃏 SELECCIONA TU MAZO", 
            bg='#1a1a2e', fg='#00ffcc', font=('Arial', 18, 'bold')).pack(pady=25)
    
    # Main content
    content_frame = tk.Frame(window, bg='#0f0f1e')
    content_frame.pack(fill='both', expand=True, padx=20, pady=20)
    
    # Random deck button
    random_frame = tk.Frame(content_frame, bg='#1a1a2e', relief='raised', borderwidth=3)
    random_frame.pack(fill='x', pady=10)
    
    tk.Label(random_frame, text="🎲 MAZO ALEATORIO", 
            bg='#1a1a2e', fg='#3498db', font=('Arial', 14, 'bold')).pack(pady=10)
    tk.Label(random_frame, text="Genera un mazo aleatorio de 40 cartas\ncon un campeón aleatorio", 
            bg='#1a1a2e', fg='#cccccc', font=('Arial', 9), justify='center').pack(pady=5)
    
    def use_random_deck():
        deck = build_random_deck(40)
        champion = get_random_champion()
        window.destroy()
        callback(deck.cards, champion)
    
    tk.Button(random_frame, text="▶ USAR MAZO ALEATORIO", command=use_random_deck,
             bg='#3498db', fg='white', font=('Arial', 11, 'bold'), width=25).pack(pady=10)
    
    # Saved decks section
    saved_frame = tk.Frame(content_frame, bg='#1a1a2e', relief='raised', borderwidth=3)
    saved_frame.pack(fill='both', expand=True, pady=10)
    
    tk.Label(saved_frame, text="📚 MAZOS GUARDADOS", 
            bg='#1a1a2e', fg='#2ecc71', font=('Arial', 14, 'bold')).pack(pady=10)
    
    # List of saved decks
    list_frame = tk.Frame(saved_frame, bg='#1a1a2e')
    list_frame.pack(fill='both', expand=True, padx=10, pady=5)
    
    scrollbar = tk.Scrollbar(list_frame)
    scrollbar.pack(side='right', fill='y')
    
    deck_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set,
                              font=('Arial', 10), bg='#2c3e50', fg='white',
                              selectmode='single', height=8)
    deck_listbox.pack(side='left', fill='both', expand=True)
    scrollbar.config(command=deck_listbox.yview)
    
    # Load saved decks
    saved_decks = get_saved_decks()
    
    if not saved_decks:
        tk.Label(saved_frame, text="No hay mazos guardados.\nCrea uno en el Constructor de Mazos.", 
                bg='#1a1a2e', fg='#888888', font=('Arial', 10), justify='center').pack(pady=10)
    else:
        for deck_name in saved_decks:
            info = get_deck_info(deck_name)
            if info:
                display_text = f"{info['name']} - {info['champion']} ({info['card_count']} cartas)"
                deck_listbox.insert(tk.END, display_text)
        
        def use_saved_deck():
            selection = deck_listbox.curselection()
            if not selection:
                messagebox.showwarning("Sin selección", "Por favor selecciona un mazo.", parent=window)
                return
            
            deck_filename = saved_decks[selection[0]]
            deck_data = load_deck(deck_filename)
            
            if not deck_data:
                messagebox.showerror("Error", "No se pudo cargar el mazo.", parent=window)
                return
            
            # Find champion
            champion = None
            for champ in CHAMPION_LIST:
                if champ.name == deck_data['champion']:
                    champion = champ
                    break
            
            if not champion:
                champion = get_random_champion()
            
            window.destroy()
            callback(deck_data['cards'], champion)
        
        tk.Button(saved_frame, text="▶ USAR MAZO SELECCIONADO", command=use_saved_deck,
                 bg='#2ecc71', fg='white', font=('Arial', 11, 'bold'), width=25).pack(pady=10)
    
    # Cancel button
    def cancel():
        window.destroy()
        if on_cancel:
            on_cancel()
    
    tk.Button(content_frame, text="❌ CANCELAR", command=cancel,
             bg='#95a5a6', fg='white', font=('Arial', 10, 'bold'), width=20).pack(pady=10)
    
    # Handle window close button (X)
    window.protocol("WM_DELETE_WINDOW", cancel)
    
    return window
