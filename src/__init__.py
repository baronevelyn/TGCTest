"""
Source package for Mini TCG.
Contains all game logic, models, and UI components.
"""

__version__ = "2.0.0"
__author__ = "Mini TCG Team"

# Core modules (headless-safe)
from . import models
from . import cards
from . import champions
from . import game_logic

# AI System (headless-safe)
from . import ai_engine

# UI modules (only import if tkinter is available - skip on server)
try:
    from . import difficulty_selector
    from . import game_gui
    from . import deck_builder
    _UI_AVAILABLE = True
except Exception:
    _UI_AVAILABLE = False

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
