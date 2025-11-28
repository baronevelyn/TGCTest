"""
Difficulty Selection Menu for AI opponents.
Allows player to choose AI difficulty level before starting a game.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable
from .ai_engine import get_difficulty_info


class DifficultySelector:
    """GUI for selecting AI difficulty level."""
    
    def __init__(self, on_select: Callable[[int], None]):
        self.on_select = on_select
        self.selected_level = None
        self.root = tk.Toplevel()
        self.root.title("Seleccionar Dificultad de IA")
        self.root.geometry("700x800")
        self.root.configure(bg='#1a1a2e')
        
        # Centrar ventana
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the difficulty selection UI."""
        
        # Título
        title_frame = tk.Frame(self.root, bg='#1a1a2e')
        title_frame.pack(pady=20)
        
        title_label = tk.Label(
            title_frame,
            text="🤖 SELECCIONAR DIFICULTAD DE IA",
            font=('Arial', 20, 'bold'),
            bg='#1a1a2e',
            fg='#00ff88'
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_frame,
            text="Basado en 280,000 simulaciones de partidas",
            font=('Arial', 10),
            bg='#1a1a2e',
            fg='#888888'
        )
        subtitle_label.pack()
        
        # Frame para los botones de dificultad
        buttons_frame = tk.Frame(self.root, bg='#1a1a2e')
        buttons_frame.pack(pady=10, padx=20, fill='both', expand=True)
        
        # Canvas con scrollbar para los niveles
        canvas = tk.Canvas(buttons_frame, bg='#1a1a2e', highlightthickness=0)
        scrollbar = ttk.Scrollbar(buttons_frame, orient='vertical', command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#1a1a2e')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Obtener información real de cada nivel desde el sistema v2
        levels_info = []
        colors = ['#2ecc71', '#27ae60', '#f39c12', '#e67e22', '#d35400', 
                  '#c0392b', '#e74c3c', '#c0392b', '#7f8c8d', '#2c3e50']
        
        for level in range(1, 11):
            info = get_difficulty_info(level)
            levels_info.append({
                'level': level,
                'name': info['name'],
                'color': colors[level - 1],
                'champions': ', '.join(info['champions']),
                'desc': f"{info['deck_quality']} mazo • {info['play_quality']} juego • {info['mistake_rate']} errores"
            })
        
        # Crear botón para cada nivel
        for info in levels_info:
            self.create_difficulty_button(scrollable_frame, info)
        
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Recomendaciones
        rec_frame = tk.Frame(self.root, bg='#16213e', relief='solid', borderwidth=2)
        rec_frame.pack(pady=10, padx=20, fill='x')
        
        rec_title = tk.Label(
            rec_frame,
            text="💡 RECOMENDACIONES",
            font=('Arial', 12, 'bold'),
            bg='#16213e',
            fg='#00ff88'
        )
        rec_title.pack(pady=5)
        
        recommendations = [
            "Principiantes: Nivel 1-2",
            "Jugadores casuales: Nivel 3-5",
            "Competitivos: Nivel 6-8",
            "Maestros: Nivel 9-10"
        ]
        
        for rec in recommendations:
            rec_label = tk.Label(
                rec_frame,
                text=f"• {rec}",
                font=('Arial', 9),
                bg='#16213e',
                fg='#ffffff'
            )
            rec_label.pack(anchor='w', padx=20)
        
        rec_frame.pack_configure(pady=(5, 10))
    
    def create_difficulty_button(self, parent, info):
        """Create a button for a specific difficulty level."""
        
        button_frame = tk.Frame(
            parent,
            bg='#16213e',
            relief='raised',
            borderwidth=2
        )
        button_frame.pack(pady=5, padx=10, fill='x')
        
        # Nivel y nombre
        level_label = tk.Label(
            button_frame,
            text=f"NIVEL {info['level']}: {info['name']}",
            font=('Arial', 11, 'bold'),
            bg='#16213e',
            fg=info['color'],
            anchor='w'
        )
        level_label.pack(pady=(10, 5), padx=10, fill='x')
        
        # Campeones
        champ_label = tk.Label(
            button_frame,
            text=f"Campeones: {info['champions']}",
            font=('Arial', 9),
            bg='#16213e',
            fg='#cccccc',
            anchor='w'
        )
        champ_label.pack(padx=10, fill='x')
        
        # Descripción
        desc_label = tk.Label(
            button_frame,
            text=info['desc'],
            font=('Arial', 9, 'italic'),
            bg='#16213e',
            fg='#888888',
            anchor='w'
        )
        desc_label.pack(padx=10, fill='x')
        
        # Botón de selección
        select_button = tk.Button(
            button_frame,
            text="▶ SELECCIONAR",
            font=('Arial', 10, 'bold'),
            bg=info['color'],
            fg='#ffffff',
            activebackground=info['color'],
            activeforeground='#ffffff',
            cursor='hand2',
            command=lambda: self.select_difficulty(info['level'])
        )
        select_button.pack(pady=10, padx=10)
        
        # Hover effects
        def on_enter(e):
            button_frame.configure(relief='sunken', borderwidth=3)
            select_button.configure(font=('Arial', 11, 'bold'))
        
        def on_leave(e):
            button_frame.configure(relief='raised', borderwidth=2)
            select_button.configure(font=('Arial', 10, 'bold'))
        
        button_frame.bind('<Enter>', on_enter)
        button_frame.bind('<Leave>', on_leave)
        select_button.bind('<Enter>', on_enter)
        select_button.bind('<Leave>', on_leave)
    
    def select_difficulty(self, level: int):
        """Handle difficulty selection."""
        self.selected_level = level
        # Destroy window first, then call callback
        try:
            self.root.destroy()
        except:
            pass
        self.on_select(level)
    
    def show(self):
        """Show the difficulty selector and wait for selection."""
        self.root.transient()
        self.root.grab_set()
        self.root.wait_window()
        return self.selected_level


def show_difficulty_selector(on_select: Callable[[int], None]) -> Optional[int]:
    """
    Show difficulty selector dialog.
    
    Args:
        on_select: Callback function that receives the selected difficulty level
    
    Returns:
        Selected difficulty level (1-10) or None if cancelled
    """
    selector = DifficultySelector(on_select)
    return selector.show()


if __name__ == '__main__':
    # Test the difficulty selector
    root = tk.Tk()
    root.withdraw()
    
    def on_difficulty_selected(level):
        print(f"\n✅ Dificultad seleccionada: Nivel {level}")
        info = get_difficulty_info(level)
        print(f"   Nombre: {info['name']}")
        print(f"   Campeones: {', '.join(info['champions'])}")
        print(f"   Calidad de mazo: {info['deck_quality']}")
        print(f"   Calidad de juego: {info['play_quality']}")
        print(f"   Tasa de errores: {info['mistake_rate']}")
    
    level = show_difficulty_selector(on_difficulty_selected)
    
    if level:
        print("\n🎮 ¡Listo para jugar!")
    else:
        print("\n❌ Selección cancelada")
