"""
Deck Manager - Sistema para guardar y cargar decks personalizados.
"""
import json
import os
from typing import List, Dict, Optional


DECKS_DIR = "data/saved_decks"


def ensure_decks_directory():
    """Asegura que el directorio de decks existe."""
    if not os.path.exists(DECKS_DIR):
        os.makedirs(DECKS_DIR)


def save_deck(deck_name: str, cards: List, champion_name: str) -> bool:
    """
    Guarda un deck con su nombre.
    
    Args:
        deck_name: Nombre del deck
        cards: Lista de objetos Card
        champion_name: Nombre del campeón
    
    Returns:
        True si se guardó correctamente, False en caso contrario
    """
    try:
        ensure_decks_directory()
        
        # Convertir las cartas a un formato serializable
        cards_data = []
        for card in cards:
            card_dict = {
                'name': card.name,
                'cost': card.cost,
                'card_type': card.card_type,
                'attack': card.damage,
                'health': card.health,
                'damage': card.damage,
                'ability': getattr(card, 'ability', ''),
                'ability_desc': getattr(card, 'ability_desc', ''),
                'ability_type': getattr(card, 'ability_type', ''),
                'description': getattr(card, 'description', ''),
                'spell_effect': getattr(card, 'spell_effect', ''),
                'spell_target': getattr(card, 'spell_target', '')
            }
            cards_data.append(card_dict)
        
        deck_data = {
            'name': deck_name,
            'champion': champion_name,
            'cards': cards_data
        }
        
        # Sanitizar el nombre del archivo
        safe_filename = "".join(c for c in deck_name if c.isalnum() or c in (' ', '-', '_')).strip()
        if not safe_filename:
            safe_filename = "deck"
        
        filepath = os.path.join(DECKS_DIR, f"{safe_filename}.json")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(deck_data, f, indent=2, ensure_ascii=False)
        
        return True
    except Exception as e:
        print(f"Error guardando deck: {e}")
        return False


def load_deck(deck_name: str) -> Optional[Dict]:
    """
    Carga un deck guardado.
    
    Args:
        deck_name: Nombre del archivo del deck (sin extensión)
    
    Returns:
        Dict con 'name', 'champion' y 'cards' o None si no se pudo cargar
    """
    try:
        from .cards import create_card
        
        filepath = os.path.join(DECKS_DIR, f"{deck_name}.json")
        
        if not os.path.exists(filepath):
            return None
        
        with open(filepath, 'r', encoding='utf-8') as f:
            deck_data = json.load(f)
        
        # Reconstruir las cartas
        cards = []
        for card_dict in deck_data['cards']:
            card = create_card(
                name=card_dict['name'],
                cost=card_dict['cost'],
                damage=card_dict['damage'],
                health=card_dict['health'],
                card_type=card_dict['card_type'],
                ability=card_dict.get('ability'),
                ability_desc=card_dict.get('ability_desc'),
                ability_type=card_dict.get('ability_type'),
                spell_target=card_dict.get('spell_target'),
                spell_effect=card_dict.get('spell_effect'),
                description=card_dict.get('description')
            )
            cards.append(card)
        
        return {
            'name': deck_data['name'],
            'champion': deck_data['champion'],
            'cards': cards
        }
    except Exception as e:
        print(f"Error cargando deck: {e}")
        return None


def get_saved_decks() -> List[str]:
    """
    Obtiene la lista de nombres de decks guardados.
    
    Returns:
        Lista de nombres de archivo (sin extensión)
    """
    try:
        ensure_decks_directory()
        
        decks = []
        for filename in os.listdir(DECKS_DIR):
            if filename.endswith('.json'):
                decks.append(filename[:-5])  # Remover .json
        
        return sorted(decks)
    except Exception as e:
        print(f"Error listando decks: {e}")
        return []


def delete_deck(deck_name: str) -> bool:
    """
    Elimina un deck guardado.
    
    Args:
        deck_name: Nombre del archivo del deck (sin extensión)
    
    Returns:
        True si se eliminó correctamente
    """
    try:
        filepath = os.path.join(DECKS_DIR, f"{deck_name}.json")
        
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        
        return False
    except Exception as e:
        print(f"Error eliminando deck: {e}")
        return False


def get_deck_info(deck_name: str) -> Optional[Dict]:
    """
    Obtiene información básica de un deck sin cargar todas las cartas.
    
    Args:
        deck_name: Nombre del archivo del deck (sin extensión)
    
    Returns:
        Dict con 'name', 'champion' y 'card_count' o None
    """
    try:
        filepath = os.path.join(DECKS_DIR, f"{deck_name}.json")
        
        if not os.path.exists(filepath):
            return None
        
        with open(filepath, 'r', encoding='utf-8') as f:
            deck_data = json.load(f)
        
        return {
            'name': deck_data['name'],
            'champion': deck_data['champion'],
            'card_count': len(deck_data['cards'])
        }
    except Exception as e:
        print(f"Error obteniendo info del deck: {e}")
        return None
