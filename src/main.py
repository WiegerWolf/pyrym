"""
main.py
Main entry point for the game.
"""
from .core.game import Game

def main():
    """Initialises and runs the game."""
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
