"""
Servidor Socket.IO para Mini TCG Multiplayer - AUTHORITATIVE SERVER
El servidor mantiene el estado completo del juego y valida todas las acciones
"""

# type: ignore - Flask-SocketIO adds request.sid at runtime

from flask import Flask, request  # type: ignore
from flask_socketio import SocketIO, emit, join_room, leave_room  # type: ignore
from gevent import monkey  # type: ignore
import time
import random
import sys
import os

# Añadir el directorio raíz al path para importar módulos del juego
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Parchear bibliotecas estándar para async
monkey.patch_all()

# Importar componentes del juego
from src.models import Player, Card
from src.game_logic import Game
from src.cards import build_random_deck
from src.champions import CHAMPION_LIST

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mini-tcg-secret-2025'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='gevent')  # type: ignore

# Almacenamiento de salas activas
active_rooms = {}  # {room_id: {'players': [sid1, sid2], 'game': Game, 'player_map': {sid: 'player'/'ai'}, 'mode': 'quick'/'custom'}}
waiting_players = []  # Lista de jugadores esperando matchmaking: [{'sid': str, 'mode': str, 'deck': list, 'champion': dict}]
waiting_custom_players = []  # Jugadores esperando con mazos custom

@app.route('/')
def index():
    """Ruta de prueba"""
    return {
        'status': 'online',
        'message': 'Mini TCG Multiplayer Server',
        'active_rooms': len(active_rooms),
        'waiting_players': len(waiting_players)
    }

@socketio.on('connect')
def handle_connect():
    """Cliente conectado"""
    print(f'✅ Cliente conectado: {request.sid}')  # type: ignore
    emit('connected', {'sid': request.sid, 'message': 'Conexión exitosa al servidor'})  # type: ignore

@socketio.on('disconnect')
def handle_disconnect():
    """Cliente desconectado"""
    print(f'❌ Cliente desconectado: {request.sid}')  # type: ignore
    
    # Remover de jugadores en espera
    waiting_players[:] = [p for p in waiting_players if p['sid'] != request.sid]  # type: ignore
    waiting_custom_players[:] = [p for p in waiting_custom_players if p['sid'] != request.sid]  # type: ignore
    
    # Notificar al oponente si está en una sala
    for room_id, room_data in list(active_rooms.items()):
        if request.sid in room_data['players']:  # type: ignore
            print(f'📢 Jugador {request.sid} desconectado de sala {room_id}')  # type: ignore
            
            # Notificar al otro jugador ANTES de eliminar la sala
            other_player = [p for p in room_data['players'] if p != request.sid]  # type: ignore
            if other_player:
                print(f'📤 Enviando opponent_disconnected a {other_player[0]}')
                socketio.emit('opponent_disconnected', room=other_player[0])  # type: ignore
                
                # Dar tiempo para que el mensaje llegue antes de eliminar la sala
                socketio.sleep(0.5)
            
            # Eliminar sala después de notificar (usar pop para evitar KeyError si ya se eliminó)
            if room_id in active_rooms:
                del active_rooms[room_id]
                print(f'🗑️ Sala eliminada: {room_id}')
            
            # Solo procesar la primera sala encontrada y salir
            break

def serialize_card(card: Card) -> dict:
    """Serializa una carta para enviar al cliente"""
    return {
        'name': card.name,
        'cost': card.cost,
        'damage': card.damage,
        'health': card.health,
        'current_health': card.current_health,
        'ready': card.ready,
        'card_type': card.card_type,
        'ability': card.ability,
        'ability_desc': card.ability_desc,
        'ability_type': card.ability_type,
        'spell_target': card.spell_target,
        'spell_effect': card.spell_effect,
        'description': card.description
    }

def get_game_state_for_player(game: Game, player_sid: str, player_map: dict) -> dict:
    """Obtiene el estado del juego desde la perspectiva de un jugador específico"""
    # Determinar qué lado del juego ve este jugador
    if player_map[player_sid] == 'player':
        my_player = game.player
        opponent_player = game.ai
    else:
        my_player = game.ai
        opponent_player = game.player
    
    return {
        'my_state': {
            'life': my_player.life,
            'mana': my_player.mana,
            'max_mana': my_player.max_mana,
            'hand': [serialize_card(c) for c in my_player.hand],
            'active_zone': [serialize_card(c) for c in my_player.active_zone],
            'deck_count': len(my_player.deck.cards),
            'graveyard_count': len(my_player.graveyard)
        },
        'opponent_state': {
            'life': opponent_player.life,
            'mana': opponent_player.mana,
            'max_mana': opponent_player.max_mana,
            'hand_count': len(opponent_player.hand),  # Solo cantidad, no cartas
            'active_zone': [serialize_card(c) for c in opponent_player.active_zone],
            'deck_count': len(opponent_player.deck.cards),
            'graveyard_count': len(opponent_player.graveyard)
        },
        'turn': game.turn,
        'is_my_turn': (player_map[player_sid] == game.turn) or (game.turn == 'player' and player_map[player_sid] == 'player') or (game.turn == 'ai' and player_map[player_sid] == 'ai')
    }

def send_game_state_to_players(room_id: str):
    """Envía el estado actualizado del juego a ambos jugadores"""
    if room_id not in active_rooms:
        return
    
    room_data = active_rooms[room_id]
    game = room_data['game']
    player_map = room_data['player_map']
    
    print(f'📤 Enviando estado actualizado de {room_id}')
    
    for player_sid in room_data['players']:
        state = get_game_state_for_player(game, player_sid, player_map)
        emit('game_state_update', state, to=player_sid)
        hand_count = len(state['my_state']['hand'])
        active_count = len(state['my_state']['active_zone'])
        opp_hand_count = state['opponent_state']['hand_count']
        print(f'   ✅ Estado enviado a {player_sid[:8]}: Turn={state["turn"]}, MyTurn={state["is_my_turn"]}, MyHand={hand_count}, OppHand={opp_hand_count}, Active={active_count}')

def create_server_game(player1_sid, player2_sid, mode='quick', custom_data=None):
    """Crea una instancia de juego completa en el servidor
    
    Args:
        player1_sid: Session ID del jugador 1
        player2_sid: Session ID del jugador 2
        mode: 'quick' para mazos aleatorios, 'custom' para mazos personalizados
        custom_data: {'player1': {'deck': [...], 'champion': {...}}, 'player2': {...}}
    """
    try:
        if mode == 'custom' and custom_data:
            # Usar mazos y campeones personalizados
            from src.champions import get_champion_by_name
            
            champion1_name = custom_data['player1']['champion']['name']
            champion2_name = custom_data['player2']['champion']['name']
            
            champion1 = get_champion_by_name(champion1_name)
            champion2 = get_champion_by_name(champion2_name)
            
            # Validar que los campeones existan
            if not champion1 or not champion2:
                print(f'❌ Campeones inválidos: {champion1_name}, {champion2_name}')
                return None
            
            # Reconstruir mazos desde datos
            deck1_data = custom_data['player1']['deck']
            deck2_data = custom_data['player2']['deck']
            
            from src.cards import Deck
            deck1 = Deck([Card(**card_dict) for card_dict in deck1_data])
            deck2 = Deck([Card(**card_dict) for card_dict in deck2_data])
            
            print(f'🎨 Modo CUSTOM: {champion1.name} ({len(deck1.cards)} cards) vs {champion2.name} ({len(deck2.cards)} cards)')
        else:
            # Generar campeones y mazos aleatorios (Quick Match)
            champion1 = random.choice(CHAMPION_LIST)
            champion2 = random.choice(CHAMPION_LIST)
            
            # Construir mazos
            deck1 = build_random_deck(size=40, spell_ratio=0.3)
            deck2 = build_random_deck(size=40, spell_ratio=0.3)
            
            print(f'⚡ Modo QUICK MATCH: {champion1.name} vs {champion2.name}')
        
        # Crear jugadores con sus mazos
        player1 = Player(name="Player1", deck=deck1, champion=champion1)
        player2 = Player(name="Player2", deck=deck2, champion=champion2)
        
        # Barajar
        random.shuffle(player1.deck.cards)
        random.shuffle(player2.deck.cards)
        
        # Robar cartas iniciales
        for _ in range(5):
            if player1.deck.cards:
                player1.hand.append(player1.deck.cards.pop(0))
            if player2.deck.cards:
                player2.hand.append(player2.deck.cards.pop(0))
        
        # Crear instancia de juego (sin UI)
        def dummy_update():
            pass
        
        game = Game(player1, player2, on_update=dummy_update)
        game.game_started = True  # Marcar como iniciado
        game.turn = 'player'  # Player1 (HOST) empieza
        
        # Inicializar maná para ambos jugadores
        # Player1 empieza con 1 maná (turno 1)
        # Player2 empieza con 0 maná (para que su primer turno tenga 1 maná)
        player1.max_mana = 1
        player1.mana = 1
        player2.max_mana = 0
        player2.mana = 0
        
        print(f'🎮 Juego creado en servidor: {champion1.name} vs {champion2.name}')
        print(f'   Player1 hand: {len(player1.hand)} cards, life: {player1.life}')
        print(f'   Player2 hand: {len(player2.hand)} cards, life: {player2.life}')
        
        return {
            'game': game,
            'player_map': {
                player1_sid: 'player',  # player1_sid controla game.player
                player2_sid: 'ai'  # player2_sid controla game.ai
            },
            'champion1': champion1,
            'champion2': champion2
        }
    except Exception as e:
        print(f'❌ Error creando juego: {e}')
        import traceback
        traceback.print_exc()
        return None

@socketio.on('find_match')
def handle_find_match(data):
    """Buscar partida - Quick Match (mazos aleatorios)"""
    player_name = data.get('player_name', 'Jugador')
    print(f'🔍 [QUICK MATCH] {player_name} ({request.sid}) busca partida')  # type: ignore
    
    # Buscar otro jugador en Quick Match
    matching_player = None
    for i, waiting in enumerate(waiting_players):
        if waiting['mode'] == 'quick':
            matching_player = waiting_players.pop(i)
            break
    
    if matching_player:
        # Hay alguien esperando - crear partida COMPLETA en servidor
        opponent_sid = matching_player['sid']
        room_id = f'game_{request.sid[:8]}'  # type: ignore
        
        # Crear juego completo en el servidor (modo quick)
        game_data = create_server_game(request.sid, opponent_sid, mode='quick')  # type: ignore
        if not game_data:
            # Error creando juego
            emit('error', {'message': 'Error al crear la partida'}, to=request.sid)  # type: ignore
            emit('error', {'message': 'Error al crear la partida'}, to=opponent_sid)
            return
        
        # Crear sala con el juego
        active_rooms[room_id] = {
            'players': [request.sid, opponent_sid],  # type: ignore
            'ready': [],
            'game': game_data['game'],
            'player_map': game_data['player_map']
        }
        
        # Ambos jugadores se unen a la sala
        join_room(room_id, sid=request.sid)  # type: ignore
        join_room(room_id, sid=opponent_sid)
        
        # Enviar estado INICIAL a los clientes (solo para UI)
        champion1 = game_data['champion1']
        champion2 = game_data['champion2']
        
        emit('match_found', {
            'room_id': room_id,
            'is_host': True,
            'my_champion': {
                'name': champion1.name,
                'title': champion1.title,
                'passive_name': champion1.passive_name,
                'passive_description': champion1.passive_description,
                'ability_type': champion1.ability_type,
                'ability_value': champion1.ability_value,
                'starting_life': champion1.starting_life
            },
            'opponent_champion': {
                'name': champion2.name,
                'title': champion2.title,
                'passive_name': champion2.passive_name,
                'passive_description': champion2.passive_description,
                'ability_type': champion2.ability_type,
                'ability_value': champion2.ability_value,
                'starting_life': champion2.starting_life
            },
            'my_life': champion1.starting_life,
            'opponent_life': champion2.starting_life
        }, room=request.sid)  # type: ignore
        
        emit('match_found', {
            'room_id': room_id,
            'is_host': False,
            'my_champion': {
                'name': champion2.name,
                'title': champion2.title,
                'passive_name': champion2.passive_name,
                'passive_description': champion2.passive_description,
                'ability_type': champion2.ability_type,
                'ability_value': champion2.ability_value,
                'starting_life': champion2.starting_life
            },
            'opponent_champion': {
                'name': champion1.name,
                'title': champion1.title,
                'passive_name': champion1.passive_name,
                'passive_description': champion1.passive_description,
                'ability_type': champion1.ability_type,
                'ability_value': champion1.ability_value,
                'starting_life': champion1.starting_life
            },
            'my_life': champion2.starting_life,
            'opponent_life': champion1.starting_life
        }, to=opponent_sid)
        
        print(f'🎮 Partida creada: {room_id}')
        print(f'   Player 1 (HOST): {champion1.name}')
        print(f'   Player 2 (GUEST): {champion2.name}')
        
        # NO enviar estado inmediatamente - el cliente lo pedirá cuando esté listo
        # send_game_state_to_players(room_id)
    else:
        # Nadie esperando - añadir a cola
        waiting_players.append({
            'sid': request.sid,  # type: ignore
            'mode': 'quick',
            'player_name': player_name
        })
        emit('waiting_for_opponent', {'message': 'Buscando oponente...'})
        print(f'⏳ {player_name} añadido a cola de espera (Quick Match)')

@socketio.on('find_custom_match')
def handle_find_custom_match(data):
    """Buscar partida con mazo personalizado"""
    player_name = data.get('player_name', 'Jugador')
    deck_data = data.get('deck', [])
    champion_data = data.get('champion', {})
    
    print(f'🔍 [CUSTOM MATCH] {player_name} ({request.sid}) busca partida con mazo custom')  # type: ignore
    print(f'   Mazo: {len(deck_data)} cartas, Campeón: {champion_data.get("name", "Unknown")}')
    
    # Validar datos del mazo
    if not deck_data or len(deck_data) < 30:
        emit('error', {'message': 'Mazo inválido (mínimo 30 cartas)'}, to=request.sid)  # type: ignore
        return
    
    if not champion_data or 'name' not in champion_data:
        emit('error', {'message': 'Campeón inválido'}, to=request.sid)  # type: ignore
        return
    
    # Buscar otro jugador en Custom Match
    matching_player = None
    for i, waiting in enumerate(waiting_players):
        if waiting['mode'] == 'custom':
            matching_player = waiting_players.pop(i)
            break
    
    if matching_player:
        # Hay alguien esperando con mazo custom - crear partida
        opponent_sid = matching_player['sid']
        room_id = f'game_{request.sid[:8]}'  # type: ignore
        
        # Preparar datos de mazos personalizados
        custom_data = {
            'player1': {
                'deck': deck_data,
                'champion': champion_data
            },
            'player2': {
                'deck': matching_player['deck'],
                'champion': matching_player['champion']
            }
        }
        
        # Crear juego con mazos personalizados
        game_data = create_server_game(request.sid, opponent_sid, mode='custom', custom_data=custom_data)  # type: ignore
        if not game_data:
            # Error creando juego
            emit('error', {'message': 'Error al crear la partida'}, to=request.sid)  # type: ignore
            emit('error', {'message': 'Error al crear la partida'}, to=opponent_sid)
            return
        
        # Crear sala con el juego
        active_rooms[room_id] = {
            'players': [request.sid, opponent_sid],  # type: ignore
            'ready': [],
            'game': game_data['game'],
            'player_map': game_data['player_map'],
            'mode': 'custom'
        }
        
        # Ambos jugadores se unen a la sala
        join_room(room_id, sid=request.sid)  # type: ignore
        join_room(room_id, sid=opponent_sid)
        
        # Enviar estado INICIAL a los clientes
        champion1 = game_data['champion1']
        champion2 = game_data['champion2']
        
        emit('match_found', {
            'room_id': room_id,
            'is_host': True,
            'mode': 'custom',
            'my_champion': {
                'name': champion1.name,
                'title': champion1.title,
                'passive_name': champion1.passive_name,
                'passive_description': champion1.passive_description,
                'ability_type': champion1.ability_type,
                'ability_value': champion1.ability_value,
                'starting_life': champion1.starting_life
            },
            'opponent_champion': {
                'name': champion2.name,
                'title': champion2.title,
                'passive_name': champion2.passive_name,
                'passive_description': champion2.passive_description,
                'ability_type': champion2.ability_type,
                'ability_value': champion2.ability_value,
                'starting_life': champion2.starting_life
            },
            'my_life': champion1.starting_life,
            'opponent_life': champion2.starting_life
        }, room=request.sid)  # type: ignore
        
        emit('match_found', {
            'room_id': room_id,
            'is_host': False,
            'mode': 'custom',
            'my_champion': {
                'name': champion2.name,
                'title': champion2.title,
                'passive_name': champion2.passive_name,
                'passive_description': champion2.passive_description,
                'ability_type': champion2.ability_type,
                'ability_value': champion2.ability_value,
                'starting_life': champion2.starting_life
            },
            'opponent_champion': {
                'name': champion1.name,
                'title': champion1.title,
                'passive_name': champion1.passive_name,
                'passive_description': champion1.passive_description,
                'ability_type': champion1.ability_type,
                'ability_value': champion1.ability_value,
                'starting_life': champion1.starting_life
            },
            'my_life': champion2.starting_life,
            'opponent_life': champion1.starting_life
        }, to=opponent_sid)
        
        print(f'🎮 Partida CUSTOM creada: {room_id}')
        print(f'   Player 1 (HOST): {champion1.name} - {len(deck_data)} cards')
        print(f'   Player 2 (GUEST): {champion2.name} - {len(matching_player["deck"])} cards')
    else:
        # Nadie esperando - añadir a cola
        waiting_players.append({
            'sid': request.sid,  # type: ignore
            'mode': 'custom',
            'player_name': player_name,
            'deck': deck_data,
            'champion': champion_data
        })
        emit('waiting_for_opponent', {'message': 'Buscando oponente con mazo custom...'})
        print(f'⏳ {player_name} añadido a cola de espera (Custom Match)')

@socketio.on('create_room')
def handle_create_room(data):
    """Crear sala privada"""
    room_code = data.get('room_code', '').upper()
    player_name = data.get('player_name', 'Jugador')
    
    if not room_code or len(room_code) != 6:
        emit('error', {'message': 'Código de sala inválido (debe ser 6 caracteres)'})
        return
    
    if room_code in active_rooms:
        emit('error', {'message': 'Esta sala ya existe'})
        return
    
    # Crear sala privada
    active_rooms[room_code] = {
        'players': [request.sid],  # type: ignore
        'ready': [],
        'host': request.sid  # type: ignore
    }
    
    join_room(room_code)
    emit('room_created', {
        'room_code': room_code,
        'message': 'Sala creada. Esperando oponente...'
    })
    print(f'🏠 Sala privada creada: {room_code} por {player_name}')

@socketio.on('join_room')
def handle_join_room(data):
    """Unirse a sala privada"""
    room_code = data.get('room_code', '').upper()
    player_name = data.get('player_name', 'Jugador')
    
    if room_code not in active_rooms:
        emit('error', {'message': 'Sala no encontrada'})
        return
    
    room_data = active_rooms[room_code]
    
    if len(room_data['players']) >= 2:
        emit('error', {'message': 'Sala llena'})
        return
    
    # Unirse a la sala
    room_data['players'].append(request.sid)  # type: ignore
    join_room(room_code)
    
    # Notificar a ambos jugadores
    host_sid = room_data['host']
    
    emit('opponent_joined', {
        'opponent': player_name,
        'you_start': True
    }, room=host_sid)  # type: ignore
    
    emit('room_joined', {
        'room_code': room_code,
        'you_start': False,
        'message': 'Conectado a la sala'
    })
    
    print(f'👥 {player_name} se unió a sala {room_code}')

@socketio.on('game_action')
def handle_game_action(data):
    """Ejecuta acción en el servidor y envía estado actualizado"""
    room_id = data.get('room_id')
    action = data.get('action')
    
    if not room_id or room_id not in active_rooms:
        emit('error', {'message': 'Sala no encontrada'})
        return
    
    room_data = active_rooms[room_id]
    game = room_data['game']
    player_map = room_data['player_map']
    
    # Verificar que el jugador está en la sala
    if request.sid not in room_data['players']:  # type: ignore
        emit('error', {'message': 'No estás en esta sala'})
        return
    
    # Determinar qué lado del juego controla este jugador
    player_role = player_map.get(request.sid)  # type: ignore
    if not player_role:
        emit('error', {'message': 'Error de mapeo de jugador'})
        return
    
    print(f'🎮 [{room_id[:12]}] Acción: {action} de {player_role}')
    
    try:
        # VALIDAR Y EJECUTAR ACCIÓN EN EL SERVIDOR
        if action == 'play_card':
            card_index = data.get('card_index', 0)
            spell_target = data.get('spell_target')
            
            # Validar turno
            if game.turn != player_role:
                emit('error', {'message': 'No es tu turno'}, to=request.sid)  # type: ignore
                print(f'   ❌ No es turno de {player_role}')
                return
            
            # Ejecutar en el servidor
            if player_role == 'player':
                if card_index < len(game.player.hand):
                    card_name = game.player.hand[card_index].name
                    hand_before = len(game.player.hand)
                    active_before = len(game.player.active_zone)
                    print(f'   🃏 Player juega: {card_name} (spell_target={spell_target})')
                    print(f'      Antes: Hand={hand_before}, Active={active_before}')
                    game.play_card(card_index, spell_target_idx=spell_target)
                    print(f'      Después: Hand={len(game.player.hand)}, Active={len(game.player.active_zone)}')
                else:
                    emit('error', {'message': 'Índice de carta inválido'}, to=request.sid)  # type: ignore
                    return
            else:  # 'ai'
                if card_index < len(game.ai.hand):
                    card_name = game.ai.hand[card_index].name
                    hand_before = len(game.ai.hand)
                    active_before = len(game.ai.active_zone)
                    print(f'   🃏 AI juega: {card_name}')
                    print(f'      Antes: Hand={hand_before}, Active={active_before}')
                    game.play_card_ai(card_index, spell_target_idx=spell_target)
                    print(f'      Después: Hand={len(game.ai.hand)}, Active={len(game.ai.active_zone)}')
                else:
                    emit('error', {'message': 'Índice de carta inválido'}, to=request.sid)  # type: ignore
                    return
        
        elif action == 'end_turn':
            # Validar turno
            if game.turn != player_role:
                emit('error', {'message': 'No es tu turno'}, to=request.sid)  # type: ignore
                print(f'   ❌ No es turno de {player_role}')
                return
            
            print(f'   🔄 {player_role} termina turno')
            # Cambiar turno
            if player_role == 'player':
                game.turn = 'ai'
                game.start_turn('ai')
            else:
                game.turn = 'player'
                game.start_turn('player')
        
        elif action == 'declare_attacks':
            attackers = data.get('attackers', [])
            targets = data.get('targets', [])
            
            # Validar turno
            if game.turn != player_role:
                emit('error', {'message': 'No es tu turno'}, to=request.sid)  # type: ignore
                return
            
            # Procesar objetivos
            processed_targets = []
            for target in targets:
                if target == "player":
                    processed_targets.append("player")
                elif isinstance(target, dict) and target.get("type") == "card":
                    processed_targets.append(("card", target.get("index", 0)))
                else:
                    processed_targets.append("player")
            
            # SIEMPRE guardar datos de ataque pendiente y solicitar bloqueadores
            room_data['pending_attacks'] = {
                'attackers': attackers,
                'targets': processed_targets,
                'attacker': player_role
            }
            
            # Solicitar bloqueadores al defensor
            defender_role = 'ai' if player_role == 'player' else 'player'
            defender_sid = None
            for sid, role in room_data['player_map'].items():
                if role == defender_role:
                    defender_sid = sid
                    break
            
            if defender_sid:
                # Enviar solicitud de bloqueadores
                emit('request_blockers', {
                    'attackers': attackers,
                    'targets': processed_targets
                }, to=defender_sid)
                
                print(f'   ⚔️ {player_role} declara {len(attackers)} ataques - esperando bloqueadores')
                
                # NO enviar estado todavía - esperar respuesta de bloqueadores
                return
        
        elif action == 'declare_blockers':
            # El defensor declara bloqueadores
            blockers = data.get('blockers', {})  # {attacker_idx: blocker_idx}
            
            # Recuperar ataque pendiente
            pending = room_data.get('pending_attacks')
            if not pending:
                emit('error', {'message': 'No hay ataques pendientes'}, to=request.sid)  # type: ignore
                return
            
            attackers = pending['attackers']
            targets = pending['targets']
            attacker_role = pending['attacker']
            
            print(f'   🛡️ {player_role} declara {len(blockers)} bloqueadores')
            
            # Ejecutar ataques con bloqueadores
            game.declare_attacks_with_blockers(attackers, targets, blockers, owner=attacker_role)
            
            # Limpiar ataque pendiente
            room_data.pop('pending_attacks', None)
        
        elif action == 'activate_ability':
            card_index = data.get('card_index', 0)
            
            # Validar turno
            if game.turn != player_role:
                emit('error', {'message': 'No es tu turno'}, to=request.sid)  # type: ignore
                return
            
            print(f'   ✨ {player_role} activa habilidad')
            game.activate_ability(card_index, owner=player_role)
        
        elif action == 'surrender':
            print(f'   🏳️ {player_role} se rinde')
            if player_role == 'player':
                game.player.life = 0
            else:
                game.ai.life = 0
            game.check_end()
        
        else:
            print(f'   ⚠️ Acción no implementada: {action}')
        
        # Enviar estado actualizado a ambos jugadores
        send_game_state_to_players(room_id)
        
    except Exception as e:
        print(f'   ❌ Error ejecutando acción: {e}')
        import traceback
        traceback.print_exc()
        emit('error', {'message': f'Error: {str(e)}'}, to=request.sid)  # type: ignore

@socketio.on('request_initial_state')
def handle_request_initial_state(data):
    """Cliente pide el estado inicial cuando está listo"""
    room_id = data.get('room_id')
    if room_id and room_id in active_rooms:
        print(f'📥 Cliente {request.sid[:8]} pide estado inicial de {room_id}')  # type: ignore
        send_game_state_to_players(room_id)

@socketio.on('chat_message')
def handle_chat_message(data):
    """Envía mensaje de chat a ambos jugadores en la sala"""
    room_id = data.get('room_id')
    message = data.get('message', '').strip()
    
    if not room_id or room_id not in active_rooms:
        return
    
    if not message:
        return
    
    room_data = active_rooms[room_id]
    player_map = room_data['player_map']
    
    # Determinar quién envió el mensaje
    sender_sid = request.sid  # type: ignore
    if sender_sid not in player_map:
        return
    
    # Identificar al remitente (Player 1 o Player 2)
    sender_role = player_map[sender_sid]
    sender_name = "Player 1" if sender_role == 'player' else "Player 2"
    
    print(f'💬 [{room_id[:12]}] {sender_name}: {message}')
    
    # Enviar a ambos jugadores
    for player_sid in room_data['players']:
        is_sender = (player_sid == sender_sid)
        emit('chat_message', {
            'sender': sender_name,
            'message': message,
            'is_me': is_sender
        }, to=player_sid)

@socketio.on('game_over')
def handle_game_over(data):
    """Sincroniza fin de partida: broadcast del ganador y cierre de sala."""
    room_id = data.get('room_id')
    winner = data.get('winner', 'OPPONENT')
    if not room_id or room_id not in active_rooms:
        # Si no hay room, intentar deducir desde el jugador
        # Broadcast directo a todos (fallback)
        emit('game_over', {'winner': winner})
        return
    print(f'🏁 [{room_id[:12]}] game_over recibido, winner={winner}')
    room_data = active_rooms[room_id]
    # Avisar a ambos jugadores
    for player_sid in room_data['players']:
        emit('game_over', {'winner': winner}, to=player_sid)
    # Dar un pequeño tiempo por si los clientes necesitan limpiar
    socketio.sleep(0.5)
    # Eliminar la sala
    if room_id in active_rooms:
        del active_rooms[room_id]
        print(f'🗑️ Sala eliminada tras game_over: {room_id}')

@socketio.on('ping')
def handle_ping(data):
    """Responder a ping para medir latencia"""
    emit('pong', {'timestamp': data.get('timestamp', time.time())})

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    print(f'🚀 Servidor Socket.IO iniciado en http://0.0.0.0:{port}')
    print('📡 Esperando conexiones...')
    socketio.run(app, host='0.0.0.0', port=port, debug=os.environ.get('DEBUG', 'False') == 'True')
