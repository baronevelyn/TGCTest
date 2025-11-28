"""
Source package for Mini TCG.
Contains all game logic, models, and UI components.
"""

__version__ = "2.0.0"
__author__ = "Mini TCG Team"

# Core modules
from . import models
from . import cards
from . import champions
from . import game_logic

# AI System
from . import ai_engine
from . import difficulty_selector

# UI modules
from . import game_gui
from . import deck_builder

# Analysis
from . import game_analysis

__all__ = [
    'models',
    'cards',
    'champions',
    'game_logic',
    'ai_player',
    'ai_difficulty',
    'difficulty_selector',
    'game_gui',
    'deck_builder',
    'game_analysis'
]
