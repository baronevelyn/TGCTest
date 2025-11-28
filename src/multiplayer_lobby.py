"""
Multiplayer lobby UI for TCG Game.
Allows players to create or join rooms, then start multiplayer matches.
"""

import tkinter as tk
from tkinter import messagebox, ttk
import random
import string
from typing import Optional, Callable
from .multiplayer.network_manager import NetworkManager
from .multiplayer.game_state_sync import GameStateSync


class MultiplayerLobby:
    """UI for multiplayer lobby - create/join rooms and start games."""
    
    def __init__(self, root, on_game_start: Callable, server_url: str = "http://localhost:5000"):
        """
        Initialize multiplayer lobby.
        
        Args:
            root: Tkinter root window
            on_game_start: Callback(network_manager, is_host) when match is ready
            server_url: Server URL to connect to
        """
        self.root = root
        self.on_game_start = on_game_start
        self.server_url = server_url
        
        self.network = NetworkManager(server_url)
        self.window: Optional[tk.Toplevel] = None
        self.status_label: Optional[tk.Label] = None
        self.is_host = False
        self.room_code = ""
        self.server_game_state: dict = {}  # Game state from server
        
        # Setup network callbacks
        self._setup_callbacks()
    
    def _setup_callbacks(self):
        """Setup network event callbacks."""
        self.network.on_match_found = self._on_match_found
        self.network.on_room_created = self._on_room_created
        self.network.on_room_joined = self._on_room_joined
        self.network.on_room_error = self._on_room_error
        self.network.on_opponent_disconnected = self._on_opponent_disconnected
    
    def show(self):
        """Show the multiplayer lobby window."""
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return
        
        self.window = tk.Toplevel(self.root)
        self.window.title("Multiplayer Lobby")
        self.window.geometry("500x400")
        self.window.resizable(False, False)
        
        # Title
        title_label = tk.Label(
            self.window,
            text="Multiplayer Lobby",
            font=("Arial", 20, "bold")
        )
        title_label.pack(pady=20)
        
        # Server connection section
        connection_frame = tk.Frame(self.window)
        connection_frame.pack(pady=10)
        
        tk.Label(connection_frame, text="Server:").grid(row=0, column=0, padx=5)
        self.server_entry = tk.Entry(connection_frame, width=30)
        self.server_entry.insert(0, self.server_url)
        self.server_entry.grid(row=0, column=1, padx=5)
        
        connect_btn = tk.Button(
            connection_frame,
            text="Connect",
            command=self._connect_to_server,
            bg="#4CAF50",
            fg="white",
            width=10
        )
        connect_btn.grid(row=0, column=2, padx=5)
        
        # Status label
        self.status_label = tk.Label(
            self.window,
            text="Not connected",
            fg="red",
            font=("Arial", 10)
        )
        self.status_label.pack(pady=5)
        
        # Separator
        ttk.Separator(self.window, orient='horizontal').pack(fill='x', pady=15)
        
        # Matchmaking section
        matchmaking_frame = tk.Frame(self.window)
        matchmaking_frame.pack(pady=10)
        
        tk.Label(
            matchmaking_frame,
            text="Quick Match",
            font=("Arial", 14, "bold")
        ).pack()
        
        tk.Label(
            matchmaking_frame,
            text="Find a random opponent"
        ).pack(pady=5)
        
        find_match_btn = tk.Button(
            matchmaking_frame,
            text="Find Match",
            command=self._find_match,
            bg="#2196F3",
            fg="white",
            width=20,
            height=2
        )
        find_match_btn.pack(pady=5)
        
        # Private room section
        ttk.Separator(self.window, orient='horizontal').pack(fill='x', pady=15)
        
        room_frame = tk.Frame(self.window)
        room_frame.pack(pady=10)
        
        tk.Label(
            room_frame,
            text="Private Room",
            font=("Arial", 14, "bold")
        ).pack()
        
        # Create room button
        create_btn = tk.Button(
            room_frame,
            text="Create Room",
            command=self._create_room,
            bg="#FF9800",
            fg="white",
            width=20
        )
        create_btn.pack(pady=5)
        
        # Join room section
        join_frame = tk.Frame(room_frame)
        join_frame.pack(pady=10)
        
        tk.Label(join_frame, text="Room Code:").pack(side=tk.LEFT, padx=5)
        self.room_code_entry = tk.Entry(join_frame, width=10)
        self.room_code_entry.pack(side=tk.LEFT, padx=5)
        
        join_btn = tk.Button(
            join_frame,
            text="Join Room",
            command=self._join_room,
            bg="#9C27B0",
            fg="white",
            width=10
        )
        join_btn.pack(side=tk.LEFT, padx=5)
        
        # Close button
        close_btn = tk.Button(
            self.window,
            text="Close",
            command=self._close,
            width=15
        )
        close_btn.pack(pady=15)
        
        # Auto-connect
        self._connect_to_server()
    
    def _connect_to_server(self):
        """Connect to the multiplayer server."""
        server_url = self.server_entry.get().strip()
        if not server_url:
            messagebox.showerror("Error", "Please enter a server URL")
            return
        
        self.server_url = server_url
        self.network.server_url = server_url
        
        if self.status_label:
            self.status_label.config(text="Connecting...", fg="orange")
        if self.window:
            self.window.update()
        
        try:
            success = self.network.connect()
            if self.status_label:
                if success:
                    self.status_label.config(text="✓ Connected to server", fg="green")
                else:
                    self.status_label.config(text="✗ Connection failed", fg="red")
                    messagebox.showerror("Connection Error", "Could not connect to server")
        except Exception as e:
            if self.status_label:
                self.status_label.config(text="✗ Connection failed", fg="red")
            messagebox.showerror("Connection Error", f"Error connecting: {e}")
    
    def _find_match(self):
        """Start matchmaking to find a random opponent."""
        if not self.network.connected:
            messagebox.showerror("Error", "Not connected to server")
            return
        
        if self.status_label:
            self.status_label.config(text="Searching for opponent...", fg="blue")
        # is_host will be set by server in match_found callback
        self.network.find_match(player_name="Player")
    
    def _create_room(self):
        """Create a private room."""
        if not self.network.connected:
            messagebox.showerror("Error", "Not connected to server")
            return
        
        # Generate 6-character room code
        self.room_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        if self.status_label:
            self.status_label.config(text=f"Creating room {self.room_code}...", fg="blue")
        self.is_host = True
        self.network.create_room(self.room_code, player_name="Player")
    
    def _join_room(self):
        """Join a private room by code."""
        if not self.network.connected:
            messagebox.showerror("Error", "Not connected to server")
            return
        
        room_code = self.room_code_entry.get().strip().upper()
        if len(room_code) != 6:
            messagebox.showerror("Error", "Room code must be 6 characters")
            return
        
        self.room_code = room_code
        if self.status_label:
            self.status_label.config(text=f"Joining room {room_code}...", fg="blue")
        self.is_host = False
        self.network.join_room(room_code, player_name="Player")
    
    # Network event handlers
    
    def _on_match_found(self, data: dict):
        """Called when matchmaking finds an opponent."""
        room_id = data.get('room_id', 'unknown')
        is_host = data.get('is_host', False)
        self.room_code = room_id
        
        # Store game state from server
        self.is_host = is_host
        self.server_game_state = data  # Store all game state data
        
        print(f"🎮 [LOBBY] Match found! I am {'HOST' if self.is_host else 'GUEST'}")
        print(f"   My champion: {data.get('my_champion', {}).get('name', 'Unknown')}")
        print(f"   Opponent champion: {data.get('opponent_champion', {}).get('name', 'Unknown')}")
        
        if self.status_label:
            role = "Host (you start)" if self.is_host else "Guest (opponent starts)"
            self.status_label.config(text=f"✓ Match found! Room: {room_id}\nRole: {role}", fg="green")
        
        # Small delay before starting game
        if self.window:
            self.window.after(1000, self._start_game)
    
    def _on_room_created(self, data: dict):
        """Called when private room is created."""
        room_code = data.get('room_code', self.room_code)
        if self.status_label:
            self.status_label.config(
                text=f"✓ Room created: {room_code}\nWaiting for opponent...",
                fg="green"
            )
        messagebox.showinfo(
            "Room Created",
            f"Room Code: {room_code}\n\nShare this code with your opponent!"
        )
    
    def _on_room_joined(self, data: dict):
        """Called when successfully joined a room."""
        room_code = data.get('room_code', self.room_code)
        if self.status_label:
            self.status_label.config(text=f"✓ Joined room: {room_code}", fg="green")
        
        # Small delay before starting game
        if self.window:
            self.window.after(1000, self._start_game)
    
    def _on_room_error(self, data: dict):
        """Called when room operation fails."""
        error_msg = data.get('message', 'Unknown error')
        if self.status_label:
            self.status_label.config(text=f"✗ Error: {error_msg}", fg="red")
        messagebox.showerror("Room Error", error_msg)
    
    def _on_opponent_disconnected(self, data: dict):
        """Called when opponent disconnects."""
        messagebox.showwarning("Opponent Disconnected", "Your opponent has disconnected.")
        self._close()
    
    def _start_game(self):
        """Start the multiplayer game."""
        if self.window and self.window.winfo_exists():
            self.window.destroy()
        
        # Call the game start callback with server game state
        if self.on_game_start:
            self.on_game_start(self.network, self.is_host, self.server_game_state)
    
    def _close(self):
        """Close the lobby window."""
        if self.network.connected:
            self.network.disconnect()
        
        if self.window and self.window.winfo_exists():
            self.window.destroy()
        
        self.window = None
