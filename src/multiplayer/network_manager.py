"""
Network Manager - Gestiona la conexión Socket.IO del cliente
"""

import socketio  # type: ignore
import threading
import os
from typing import Callable, Optional, Dict, Any

class NetworkManager:
    """Gestiona la conexión de red y comunicación con el servidor"""
    
    def __init__(self, server_url: str = None):
        # Try to read server URL from config file
        if server_url is None:
            server_url = self._read_server_config()
        self.server_url = server_url
        # Configurar cliente con reconexión robusta para conexiones inestables
        self.sio: socketio.Client = socketio.Client(  # type: ignore
            reconnection=True,
            reconnection_attempts=10,
            reconnection_delay=1.0,
            reconnection_delay_max=10.0,
            randomization_factor=0.2
        )
        self.connected = False
        self.room_id: Optional[str] = None
        self.player_name: str = "Jugador"
        
        # Callbacks
        self.on_match_found: Optional[Callable] = None
        self.on_opponent_action: Optional[Callable] = None
        self.on_opponent_disconnected: Optional[Callable] = None
        self.on_error: Optional[Callable] = None
        self.on_room_created: Optional[Callable] = None
        self.on_room_joined: Optional[Callable] = None
        self.on_room_error: Optional[Callable] = None
        self.on_sync_request: Optional[Callable] = None
        self.on_game_state_update: Optional[Callable] = None  # NEW: Estado desde servidor
        self.on_chat_message: Optional[Callable] = None  # NEW: Mensajes de chat
        self.on_request_blockers: Optional[Callable] = None  # NEW: Solicitud de bloqueadores
        self.on_game_over: Optional[Callable[[str], None]] = None  # NEW: ganador ('YOU'/'OPPONENT')
        
        # Configurar event handlers
        self._setup_handlers()
    
    def _read_server_config(self) -> str:
        """Lee la URL del servidor desde el archivo de configuración"""
        default_url = 'http://localhost:5000'
        
        # Buscar server_config.txt en múltiples ubicaciones
        # 1. Directorio del ejecutable (cuando está empaquetado con PyInstaller)
        # 2. Directorio de trabajo actual
        # 3. Directorio raíz del proyecto (para desarrollo)
        search_paths = [
            os.path.join(os.path.dirname(os.path.abspath(os.sys.executable if getattr(os.sys, 'frozen', False) else __file__)), 'server_config.txt'),
            os.path.join(os.getcwd(), 'server_config.txt'),
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'server_config.txt')
        ]
        
        for config_path in search_paths:
            try:
                if os.path.exists(config_path):
                    print(f'📄 Intentando leer config de: {config_path}')
                    with open(config_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            line = line.strip()
                            if line.startswith('SERVER_URL=') and not line.startswith('#'):
                                url = line.split('=', 1)[1].strip()
                                if url:
                                    print(f'📡 Usando servidor desde config: {url}')
                                    return url
            except Exception as e:
                print(f'⚠️ Error leyendo {config_path}: {e}')
                continue
        
        print(f'⚠️ No se encontró server_config.txt, usando {default_url}')
        return default_url
    
    def _setup_handlers(self):
        """Configurar handlers de eventos de Socket.IO"""
        
        @self.sio.on('connect')  # type: ignore
        def on_connect():
            self.connected = True
            print('✅ Conectado al servidor')
        
        @self.sio.on('connect_error')  # type: ignore
        def on_connect_error(data):
            print(f'❌ Error de conexión: {data}')
            self.connected = False
        
        @self.sio.on('disconnect')  # type: ignore
        def on_disconnect():
            self.connected = False
            print('❌ Desconectado del servidor')
        
        @self.sio.on('connected')  # type: ignore
        def on_connected_msg(data):
            print(f'📡 {data.get("message")}')
        
        @self.sio.on('match_found')  # type: ignore
        def on_match_found(data):
            self.room_id = data.get('room_id')
            print(f'🎮 Partida encontrada: {self.room_id}')
            if self.on_match_found:
                self.on_match_found(data)
        
        @self.sio.on('waiting_for_opponent')  # type: ignore
        def on_waiting(data):
            print(f'⏳ {data.get("message")}')
        
        @self.sio.on('room_created')  # type: ignore
        def on_room_created(data):
            self.room_id = data.get('room_code')
            print(f'🏠 Sala creada: {self.room_id}')
            if self.on_room_created:
                self.on_room_created(data)
        
        @self.sio.on('room_joined')  # type: ignore
        def on_room_joined(data):
            self.room_id = data.get('room_code')
            print(f'👥 Te uniste a sala: {self.room_id}')
            if self.on_room_joined:
                self.on_room_joined(data)
        
        @self.sio.on('opponent_joined')  # type: ignore
        def on_opponent_joined(data):
            print(f'👥 Oponente se unió: {data.get("opponent")}')
            if self.on_match_found:
                self.on_match_found(data)
        
        @self.sio.on('opponent_action')  # type: ignore
        def on_opponent_action(data):
            print(f'📥 Acción del oponente: {data.get("action_type")}')
            if self.on_opponent_action:
                self.on_opponent_action(data)
        
        @self.sio.on('opponent_disconnected')  # type: ignore
        def handle_opponent_disconnected():
            print('❌ Oponente desconectado')
            if self.on_opponent_disconnected:
                self.on_opponent_disconnected()
        
        @self.sio.on('error')  # type: ignore
        def on_error(data):
            print(f'⚠️ Error: {data.get("message")}')
            if self.on_room_error:
                self.on_room_error(data)
            if self.on_error:
                self.on_error(data)
        
        @self.sio.on('game_state_update')  # type: ignore
        def on_game_state_update(data):
            print(f'📦 Estado del juego recibido del servidor')
            if self.on_game_state_update:
                self.on_game_state_update(data)
        
        @self.sio.on('chat_message')  # type: ignore
        def on_chat_message(data):
            sender = data.get('sender', 'Unknown')
            message = data.get('message', '')
            is_me = data.get('is_me', False)
            print(f'💬 Chat - {sender}: {message}')
            if self.on_chat_message:
                self.on_chat_message(data)
        
        @self.sio.on('request_blockers')  # type: ignore
        def on_request_blockers(data):
            attackers = data.get('attackers', [])
            targets = data.get('targets', [])
            print(f'🛡️ Solicitud de bloqueadores - {len(attackers)} atacantes')
            if self.on_request_blockers:
                self.on_request_blockers(data)
        
        @self.sio.on('pong')  # type: ignore
        def on_pong(data):
            import time
            latency = (time.time() - data.get('timestamp', 0)) * 1000
            print(f'🏓 Latencia: {latency:.0f}ms')

        @self.sio.on('game_over')  # type: ignore
        def on_game_over(data):
            winner = 'OPPONENT'
            if isinstance(data, dict) and 'winner' in data:
                winner = str(data['winner'])
            if self.on_game_over:
                try:
                    self.on_game_over(winner)
                except Exception:
                    pass
            else:
                print(f"[network] game_over received: winner={winner}")

    def emit_game_over(self, winner: str):
        """Emite un evento game_over al servidor para sincronizar fin de partida."""
        try:
            payload = { 'winner': winner }
            if self.room_id:
                payload['room_id'] = self.room_id
            self.sio.emit('game_over', payload)
        except Exception as e:
            print(f"[network] emit_game_over failed: {e}")
    
    def connect(self) -> bool:
        """Conectar al servidor con reintentos y mayor tolerancia a frío/latencia."""
        import time
        attempts = 0
        delays = [2, 4, 6]
        timeouts = [15, 20, 30]
        while attempts < len(timeouts):
            try:
                if attempts == 0:
                    print(f'🔌 Conectando a {self.server_url}...')
                else:
                    print(f'🔄 Reintentando conexión ({attempts+1}/{len(timeouts)})...')
                self.sio.connect(
                    self.server_url,
                    transports=['websocket', 'polling'],
                    wait=True,
                    wait_timeout=timeouts[attempts]
                )
                return True
            except Exception as e:
                print(f'❌ Error al conectar (intento {attempts+1}): {e}')
                if attempts < len(delays):
                    time.sleep(delays[attempts])
                attempts += 1
        return False
    
    def disconnect(self):
        """Desconectar del servidor"""
        if self.connected:
            self.sio.disconnect()
    
    def find_match(self, player_name: str):
        """Buscar partida automática (Quick Match - mazos aleatorios)"""
        self.player_name = player_name
        self.sio.emit('find_match', {'player_name': player_name})
        print(f'🔍 Buscando Quick Match como {player_name}...')
    
    def find_custom_match(self, player_name: str, deck_data: list, champion_data: dict):
        """Buscar partida con mazo personalizado (Custom Match)
        
        Args:
            player_name: Nombre del jugador
            deck_data: Lista de diccionarios con datos de cartas
            champion_data: Diccionario con datos del campeón
        """
        self.player_name = player_name
        
        # Serializar mazos para enviar al servidor
        serialized_deck = []
        for card in deck_data:
            if isinstance(card, dict):
                serialized_deck.append(card)
            else:
                # Si es un objeto Card, convertir a dict
                serialized_deck.append({
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
        
        self.sio.emit('find_custom_match', {
            'player_name': player_name,
            'deck': serialized_deck,
            'champion': champion_data
        })
        print(f'🔍 Buscando Custom Match como {player_name}...')
        print(f'   📦 Mazo: {len(serialized_deck)} cartas')
        print(f'   🎭 Campeón: {champion_data.get("name", "Unknown")}')
    
    def create_room(self, room_code: str, player_name: str):
        """Crear sala privada"""
        self.player_name = player_name
        self.sio.emit('create_room', {
            'room_code': room_code,
            'player_name': player_name
        })
    
    def join_room(self, room_code: str, player_name: str):
        """Unirse a sala privada"""
        self.player_name = player_name
        self.sio.emit('join_room', {
            'room_code': room_code,
            'player_name': player_name
        })
    
    def send_action(self, action_data: Dict[str, Any]):
        """Enviar acción de juego al oponente"""
        if not self.room_id:
            print('❌ [CLIENT] No estás en una sala')
            return
        
        # Añadir room_id a los datos
        action_data['room_id'] = self.room_id
        action = action_data.get('action', 'unknown')
        print(f'📤 [CLIENT] Enviando acción: {action}')
        print(f'   📦 Data completa: {action_data}')
        
        self.sio.emit('game_action', action_data)
        print(f'   ✅ Acción enviada al servidor')
    
    def ping(self):
        """Medir latencia"""
        import time
        self.sio.emit('ping', {'timestamp': time.time()})
