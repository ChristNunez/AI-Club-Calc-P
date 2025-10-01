
from .engine.game import Game

def main():
    print("=== Calculus Duo (terminal) ===")
    name = input("Enter your player name: ").strip() or "Player"
    game = Game(name)
    game.run()
