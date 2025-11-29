"""Mini TCG source package.

Lightweight package init to avoid circular import issues when freezing
with PyInstaller. Modules are imported lazily on first attribute access.
"""

__version__ = "2.0.0"
__author__ = "Mini TCG Team"

_LAZY_MODULES = [
    'models',
    'cards',
    'champions',
    'game_logic',
    'ai_engine',
    'ai_player',
    'ai_difficulty',
    'difficulty_selector',
    'game_gui',
    'deck_builder',
    'game_analysis'
]

def __getattr__(name):
    if name in _LAZY_MODULES:
        import importlib
        module = importlib.import_module(f'{__name__}.{name}')
        globals()[name] = module  # cache for future lookups
        return module
    raise AttributeError(f'module {__name__} has no attribute {name}')

__all__ = _LAZY_MODULES[:]
