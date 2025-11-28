"""
Test rapido del deck builder
"""
import tkinter as tk
from src.deck_builder import DeckBuilder

if __name__ == '__main__':
    print("Iniciando Deck Builder...")
    root = tk.Tk()
    builder = DeckBuilder(root)
    print("Deck Builder creado exitosamente!")
    print("\nInstrucciones:")
    print("1. Selecciona un campeón")
    print("2. Agrega al menos 30 cartas (15 tropas, 5 hechizos)")
    print("3. Haz clic en 'JUGAR'")
    root.mainloop()
