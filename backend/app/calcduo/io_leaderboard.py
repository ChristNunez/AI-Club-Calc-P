
from .config import LEADERBOARD_FILE
from .utils import load_json, save_json

class Leaderboard:
    def __init__(self, path=LEADERBOARD_FILE):
        self.path = path
        self.data = load_json(path, {})

    def add_score(self, player_name: str, score: int):
        rec = self.data.get(player_name, {"best": 0, "total": 0, "plays": 0})
        rec["best"] = max(rec["best"], score)
        rec["total"] += score
        rec["plays"] += 1
        self.data[player_name] = rec
        save_json(self.path, self.data)

    def top(self, n=10):
        items = sorted(self.data.items(), key=lambda it: it[1]["best"], reverse=True)
        return items[:n]

    def print_board(self, n=10):
        print("\n=== Leaderboard ===")
        top = self.top(n)
        if not top:
            print("No scores yet — be the first!")
            return
        for i, (name, rec) in enumerate(top, start=1):
            avg = (rec['total'] // rec['plays']) if rec['plays'] else 0
            print(f"{i}. {name} — Best: {rec['best']} | Average: {avg} | Plays: {rec['plays']}")
        print("===================\n")
