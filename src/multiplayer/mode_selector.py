"""
Multiplayer Lobby with Game Mode Selection
Allows players to choose between Quick Match (random decks) or Custom Match (custom decks)
"""

import tkinter as tk
from tkinter import messagebox
from typing import Callable, Optional
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class MultiplayerModeSelector:
    """
    UI for selecting multiplayer game mode.
    
    Two modes:
    - Quick Match: Random decks, instant matchmaking
    - Custom Match: Build your own deck, then find match
    """
    
    def __init__(
        self,
        root: tk.Tk,
        on_quick_match: Callable[[], None],
        on_custom_match: Callable[[], None],
        on_cancel: Callable[[], None]
    ):
        """
        Initialize mode selector.
        
        Args:
            root: Parent window
            on_quick_match: Callback when Quick Match selected
            on_custom_match: Callback when Custom Match selected  
            on_cancel: Callback when cancelled
        """
        self.root = root
        self.on_quick_match = on_quick_match
        self.on_custom_match = on_custom_match
        self.on_cancel = on_cancel
        
        self.window: Optional[tk.Toplevel] = None
        
    def show(self):
        """Show the server configuration window first"""
        self._show_server_config()
    
    def _show_server_config(self):
        """Show server configuration dialog"""
        self.window = tk.Toplevel(self.root)
        self.window.title("Multiplayer - Server Configuration")
        self.window.geometry("650x700")
        self.window.configure(bg='#1a1a2e')
        self.window.resizable(False, False)
        
        # Center window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (650 // 2)
        y = (self.window.winfo_screenheight() // 2) - (700 // 2)
        self.window.geometry(f"650x700+{x}+{y}")
        
        # Title
        title_label = tk.Label(
            self.window,
            text="🌐 SERVER CONFIGURATION",
            font=('Arial', 24, 'bold'),
            bg='#1a1a2e',
            fg='#3498db'
        )
        title_label.pack(pady=20)
        
        subtitle = tk.Label(
            self.window,
            text="Configure server connection",
            font=('Arial', 11),
            bg='#1a1a2e',
            fg='#ecf0f1'
        )
        subtitle.pack(pady=(0, 20))
        
        # Connection type selection
        connection_frame = tk.Frame(self.window, bg='#1a1a2e')
        connection_frame.pack(pady=10, padx=30, fill='x')
        
        tk.Label(
            connection_frame,
            text="Select connection type:",
            font=('Arial', 12, 'bold'),
            bg='#1a1a2e',
            fg='#ecf0f1'
        ).pack(anchor='w', pady=(0, 10))
        
        connection_var = tk.StringVar(value="online")
        
        # Online option (Render)
        online_frame = tk.Frame(connection_frame, bg='#2c3e50', relief='raised', borderwidth=2)
        online_frame.pack(fill='x', pady=5)
        tk.Radiobutton(
            online_frame,
            text="🌍 Online (Servidor Render 24/7)",
            variable=connection_var,
            value="online",
            font=('Arial', 11, 'bold'),
            bg='#2c3e50',
            fg='#2ecc71',
            selectcolor='#34495e',
            activebackground='#2c3e50',
            activeforeground='#2ecc71'
        ).pack(anchor='w', padx=10, pady=8)
        tk.Label(
            online_frame,
            text="✅ Recomendado - Juega desde cualquier lugar del mundo",
            font=('Arial', 9, 'italic'),
            bg='#2c3e50',
            fg='#95a5a6'
        ).pack(anchor='w', padx=30, pady=(0, 8))
        
        # Local option
        local_frame = tk.Frame(connection_frame, bg='#2c3e50', relief='raised', borderwidth=2)
        local_frame.pack(fill='x', pady=5)
        tk.Radiobutton(
            local_frame,
            text="🏠 Red Local (Personalizar URL)",
            variable=connection_var,
            value="local",
            font=('Arial', 11),
            bg='#2c3e50',
            fg='white',
            selectcolor='#34495e',
            activebackground='#2c3e50',
            activeforeground='white'
        ).pack(anchor='w', padx=10, pady=8)
        tk.Label(
            local_frame,
            text="Servidor propio o localhost (introduce la URL abajo)",
            font=('Arial', 9, 'italic'),
            bg='#2c3e50',
            fg='#95a5a6'
        ).pack(anchor='w', padx=30, pady=(0, 8))
        
        # Custom IP/URL input (only for local)
        input_frame = tk.Frame(self.window, bg='#1a1a2e')
        input_frame.pack(pady=20, padx=40, fill='x')
        
        tk.Label(
            input_frame,
            text="URL del Servidor (solo para Red Local):",
            font=('Arial', 10),
            bg='#1a1a2e',
            fg='#ecf0f1'
        ).pack(anchor='w', pady=(0, 5))
        
        server_entry = tk.Entry(
            input_frame,
            font=('Arial', 11),
            bg='#2c3e50',
            fg='white',
            insertbackground='white',
            relief='flat'
        )
        server_entry.pack(fill='x', ipady=8, pady=(0, 5))
        server_entry.insert(0, "http://localhost:5000")
        
        hint_label = tk.Label(
            input_frame,
            text="💡 Ejemplos: http://localhost:5000 | http://192.168.1.100:5000 | https://tu-servidor.com",
            font=('Arial', 9, 'italic'),
            bg='#1a1a2e',
            fg='#95a5a6'
        )
        hint_label.pack(anchor='w')
        
        # Buttons
        buttons_frame = tk.Frame(self.window, bg='#1a1a2e')
        buttons_frame.pack(pady=30)
        
        def on_continue():
            """Save config and show mode selector"""
            import os
            
            connection_type = connection_var.get()
            custom_address = server_entry.get().strip()
            
            # Determine server URL
            if connection_type == "online":
                # Use Render server
                server_url = "https://tgctest.onrender.com"
            else:
                # Local network - use custom URL or default
                if custom_address:
                    server_url = custom_address
                else:
                    server_url = "http://localhost:5000"
            
            # Save to config file
            try:
                config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'server_config.txt')
                with open(config_path, 'w', encoding='utf-8') as f:
                    f.write(f"# Configuración del Servidor Multijugador\n")
                    f.write(f"# Configurado desde el menú del juego\n\n")
                    f.write(f"SERVER_URL={server_url}\n")
                print(f"✅ Server configured: {server_url}")
            except Exception as e:
                print(f"⚠️ Could not save config: {e}")
            
            # Close config window and show mode selector
            if self.window:
                self.window.destroy()
            self._show_mode_selector()
        
        tk.Button(
            buttons_frame,
            text="▶ CONTINUE",
            command=on_continue,
            font=('Arial', 12, 'bold'),
            bg='#27ae60',
            fg='white',
            width=15,
            height=2,
            cursor='hand2',
            relief='raised',
            borderwidth=3
        ).pack(side='left', padx=10)
        
        tk.Button(
            buttons_frame,
            text="❌ CANCEL",
            command=self._on_cancel_clicked,
            font=('Arial', 12, 'bold'),
            bg='#e74c3c',
            fg='white',
            width=15,
            height=2,
            cursor='hand2',
            relief='raised',
            borderwidth=3
        ).pack(side='left', padx=10)
    
    def _show_mode_selector(self):
        """Show the game mode selector window"""
        self.window = tk.Toplevel(self.root)
        self.window.title("Multiplayer - Select Mode")
        self.window.geometry("600x500")
        self.window.configure(bg='#1a1a2e')
        self.window.resizable(False, False)
        
        # Center window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.window.winfo_screenheight() // 2) - (500 // 2)
        self.window.geometry(f"600x500+{x}+{y}")
        
        # Title
        title_label = tk.Label(
            self.window,
            text="🎮 MULTIPLAYER MODE",
            font=('Arial', 24, 'bold'),
            bg='#1a1a2e',
            fg='#f39c12'
        )
        title_label.pack(pady=30)
        
        subtitle = tk.Label(
            self.window,
            text="Choose your game mode",
            font=('Arial', 12),
            bg='#1a1a2e',
            fg='#ecf0f1'
        )
        subtitle.pack(pady=(0, 40))
        
        # Mode buttons container
        modes_frame = tk.Frame(self.window, bg='#1a1a2e')
        modes_frame.pack(expand=True, fill=tk.BOTH, padx=40, pady=20)
        
        # Quick Match card
        self._create_mode_card(
            modes_frame,
            title="⚡ QUICK MATCH",
            description="Jump into action with random decks\n\n"
                       "• Instant matchmaking\n"
                       "• Balanced random decks\n"
                       "• Perfect for quick games\n"
                       "• No deck building required",
            color='#27ae60',
            command=self._on_quick_match_clicked,
            side=tk.LEFT
        )
        
        # Custom Match card
        self._create_mode_card(
            modes_frame,
            title="🎨 CUSTOM MATCH",
            description="Build your own deck and compete\n\n"
                       "• Choose your champion\n"
                       "• Build your 30+ card deck\n"
                       "• Strategic deck building\n"
                       "• Show your creativity",
            color='#3498db',
            command=self._on_custom_match_clicked,
            side=tk.RIGHT
        )
        
        # Cancel button
        cancel_button = tk.Button(
            self.window,
            text="← Back to Menu",
            font=('Arial', 11),
            bg='#95a5a6',
            fg='white',
            activebackground='#7f8c8d',
            activeforeground='white',
            command=self._on_cancel_clicked,
            width=20,
            height=2,
            cursor='hand2'
        )
        cancel_button.pack(pady=20)
        
        # Make window modal
        self.window.transient(self.root)
        self.window.grab_set()
        
        # Wait for window to close
        self.root.wait_window(self.window)
        
    def _create_mode_card(self, parent, title, description, color, command, side):
        """Create a mode selection card"""
        card_frame = tk.Frame(
            parent,
            bg=color,
            relief=tk.RAISED,
            borderwidth=3
        )
        card_frame.pack(side=side, expand=True, fill=tk.BOTH, padx=10)
        
        # Title
        title_label = tk.Label(
            card_frame,
            text=title,
            font=('Arial', 18, 'bold'),
            bg=color,
            fg='white'
        )
        title_label.pack(pady=20)
        
        # Description
        desc_label = tk.Label(
            card_frame,
            text=description,
            font=('Arial', 10),
            bg=color,
            fg='white',
            justify=tk.LEFT,
            wraplength=220
        )
        desc_label.pack(pady=10, padx=15)
        
        # Play button
        play_button = tk.Button(
            card_frame,
            text="PLAY",
            font=('Arial', 14, 'bold'),
            bg='white',
            fg=color,
            activebackground='#ecf0f1',
            activeforeground=color,
            command=command,
            width=15,
            height=2,
            cursor='hand2'
        )
        play_button.pack(pady=20)
        
        # Hover effects
        def on_enter(e):
            card_frame.config(relief=tk.SUNKEN, borderwidth=4)
            
        def on_leave(e):
            card_frame.config(relief=tk.RAISED, borderwidth=3)
        
        card_frame.bind('<Enter>', on_enter)
        card_frame.bind('<Leave>', on_leave)
    
    def _on_quick_match_clicked(self):
        """Handle Quick Match button"""
        if self.window:
            self.window.destroy()
        self.on_quick_match()
    
    def _on_custom_match_clicked(self):
        """Handle Custom Match button"""
        if self.window:
            self.window.destroy()
        self.on_custom_match()
    
    def _on_cancel_clicked(self):
        """Handle Cancel button"""
        if self.window:
            self.window.destroy()
        self.on_cancel()


# Demo
if __name__ == "__main__":
    def demo():
        root = tk.Tk()
        root.withdraw()
        
        def on_quick():
            print("Quick Match selected!")
            messagebox.showinfo("Quick Match", "Starting Quick Match matchmaking...")
            root.deiconify()
            root.quit()
        
        def on_custom():
            print("Custom Match selected!")
            messagebox.showinfo("Custom Match", "Opening Deck Builder...")
            root.deiconify()
            root.quit()
        
        def on_cancel():
            print("Cancelled")
            root.deiconify()
            root.quit()
        
        selector = MultiplayerModeSelector(root, on_quick, on_custom, on_cancel)
        selector.show()
        
        root.mainloop()
    
    print("="*60)
    print("🎮 MULTIPLAYER MODE SELECTOR DEMO")
    print("="*60)
    demo()
