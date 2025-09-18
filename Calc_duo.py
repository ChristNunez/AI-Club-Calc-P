#!/usr/bin/env python3
"""
Calculus Duo - terminal Duolingo-style game focused on calculus (limits, derivatives, integrals).

Save as: calculus_duo.py
Run: python calculus_duo.py
"""

import json
import math
import random
import sys
from typing import Tuple, List, Dict

LEADERBOARD_FILE = "leaderboard.json"


# ---------------------------
# Utilities
# ---------------------------
def clamp(x, a, b):
    return max(a, min(b, x))


def safe_float(s):
    try:
        return float(s)
    except Exception:
        return None


def round_for_compare(x, places=5):
    return round(x, places)


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def load_json(path, default):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return default


# ---------------------------
# Leaderboard
# ---------------------------
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
            print(f"{i}. {name} — Best: {rec['best']} | Average: {rec['total'] // rec['plays'] if rec['plays'] else 0} | Plays: {rec['plays']}")
        print("===================\n")


# ---------------------------
# Problem base classes
# ---------------------------
class Problem:
    def __init__(self, difficulty: str):
        self.difficulty = difficulty

    def prompt(self) -> str:
        raise NotImplementedError

    def check_answer(self, answer: str) -> Tuple[bool, str]:
        """Return (correct, feedback_text)."""
        raise NotImplementedError

    def xp_reward(self) -> int:
        mapping = {"easy": 10, "medium": 20, "hard": 40}
        return mapping.get(self.difficulty, 10)


# ---------------------------
# Polynomial helpers
# ---------------------------
def gen_poly(degree: int, coeff_range=(-5, 5)):
    # Return coefficients list: highest -> constant
    coeffs = []
    for i in range(degree + 1):
        c = 0
        while c == 0 and i == 0 and degree > 0:
            # make leading coeff non-zero for degree>0
            c = random.randint(coeff_range[0], coeff_range[1])
        if c == 0:
            c = random.randint(coeff_range[0], coeff_range[1])
        coeffs.append(c)
    # If polynomial accidentally all zeros, regenerate
    if all(c == 0 for c in coeffs):
        return gen_poly(degree, coeff_range)
    return coeffs


def poly_to_string(coeffs):
    # coeffs: highest -> constant
    terms = []
    degree = len(coeffs) - 1
    for i, c in enumerate(coeffs):
        powr = degree - i
        if c == 0:
            continue
        sign = "-" if c < 0 else "+"
        abs_c = abs(c)
        if powr == 0:
            term = f"{abs_c}"
        elif powr == 1:
            term = (f"{abs_c}x" if abs_c != 1 else "x")
        else:
            term = (f"{abs_c}x^{powr}" if abs_c != 1 else f"x^{powr}")
        terms.append((sign, term))
    if not terms:
        return "0"
    # build string
    first_sign, first_term = terms[0]
    s = (("-" if first_sign == "-" else "") + first_term)
    for sign, term in terms[1:]:
        s += f" {sign} {term}"
    return s


def eval_poly(coeffs, x):
    degree = len(coeffs) - 1
    s = 0
    for i, c in enumerate(coeffs):
        powr = degree - i
        s += c * (x ** powr)
    return s


def derivative_coeffs(coeffs):
    degree = len(coeffs) - 1
    if degree == 0:
        return [0]
    deriv = []
    for i, c in enumerate(coeffs):
        powr = degree - i
        if powr == 0:
            continue
        deriv.append(c * powr)
    return deriv


def antiderivative_coeffs(coeffs):
    degree = len(coeffs) - 1
    anti = []
    for i, c in enumerate(coeffs):
        powr = degree - i
        anti.append(c / (powr + 1))  # coefficient for x^(powr+1)
    anti.append(0.0)  # constant of integration
    return anti  # highest -> constant


# ---------------------------
# Problem implementations
# ---------------------------

class LimitProblem(Problem):
    def __init__(self, difficulty):
        super().__init__(difficulty)
        # difficulty affects degree and point types
        if difficulty == "easy":
            deg = 1
            a_choices = [0, 1, 2, -1]
        elif difficulty == "medium":
            deg = 2
            a_choices = [0, 1, 2, -1, 3]
        else:
            deg = 3
            a_choices = [0, 1, 2, -1, 3, 4]

        self.coeffs = gen_poly(deg, coeff_range=(-5, 5))
        self.a = random.choice(a_choices)

        # To create a removable 0/0 case sometimes, if difficulty medium/hard:
        if difficulty in ("medium", "hard") and random.random() < 0.25:
            # force polynomial to have (x - a) factor by adjusting constant
            # simple approach: ensure P(a) == 0 by shifting constant
            current = eval_poly(self.coeffs, self.a)
            self.coeffs[-1] -= current  # change constant term
            # now P(a) == 0

    def prompt(self):
        expr = poly_to_string(self.coeffs)
        return f"Compute the limit: lim_{'{x->' + str(self.a) + '}'} {expr}"

    def check_answer(self, answer: str):
        ansf = safe_float(answer)
        if ansf is None:
            return False, "Please enter a numeric value."
        true = eval_poly(self.coeffs, self.a)
        # For removable 0/0 where derivative exists, fallback to value of polynomial after factoring
        # But our generation ensures if P(a)==0, limit equals P(a) (polynomial is continuous) -> it's just P(a)
        if round_for_compare(ansf, 5) == round_for_compare(true, 5):
            return True, "Correct!"
        else:
            return False, f"Incorrect. The limit equals {true}."

class DerivativeAtPointProblem(Problem):
    def __init__(self, difficulty):
        super().__init__(difficulty)
        if difficulty == "easy":
            deg = 1  # linear
            points = [0, 1, 2]
        elif difficulty == "medium":
            deg = 2
            points = [0, 1, 2, -1]
        else:
            deg = 3
            points = [0, 1, 2, -1, 3]
        self.coeffs = gen_poly(deg, coeff_range=(-5, 5))
        self.x0 = random.choice(points)
        self.deriv_coeffs = derivative_coeffs(self.coeffs)

    def prompt(self):
        expr = poly_to_string(self.coeffs)
        return f"Find f'({self.x0}) for f(x) = {expr}"

    def check_answer(self, answer: str):
        ansf = safe_float(answer)
        if ansf is None:
            return False, "Please enter a numeric value."
        true = eval_poly(self.deriv_coeffs, self.x0)
        if round_for_compare(ansf, 5) == round_for_compare(true, 5):
            return True, "Correct!"
        else:
            return False, f"Incorrect. f'({self.x0}) = {true}."

class DefiniteIntegralProblem(Problem):
    def __init__(self, difficulty):
        super().__init__(difficulty)
        if difficulty == "easy":
            deg = 1
            a, b = 0, 1
        elif difficulty == "medium":
            deg = 2
            a, b = 0, 2
        else:
            deg = 3
            a, b = 0, 3
        self.coeffs = gen_poly(deg, coeff_range=(-4, 6))
        # ensure a < b
        self.a = a
        self.b = b
        self.anti = antiderivative_coeffs(self.coeffs)  # highest -> constant

    def prompt(self):
        expr = poly_to_string(self.coeffs)
        return f"Compute definite integral: ∫_{self.a}^{self.b} {expr} dx"

    def check_answer(self, answer: str):
        ansf = safe_float(answer)
        if ansf is None:
            return False, "Please enter a numeric value."
        # Evaluate antiderivative at b minus at a:
        true_b = eval_poly(self.anti, self.b)
        true_a = eval_poly(self.anti, self.a)
        true = true_b - true_a
        # compare with tolerance
        if abs(ansf - true) < 1e-4:
            return True, "Correct!"
        else:
            return False, f"Incorrect. The integral equals {true}."

# ---------------------------
# Lesson and Game logic
# ---------------------------
class Lesson:
    def __init__(self, name: str, problem_cls, difficulties=("easy", "medium", "hard")):
        self.name = name
        self.problem_cls = problem_cls
        self.difficulties = difficulties

    def run(self, game):
        print(f"\n--- Lesson: {self.name} ---")
        for difficulty in self.difficulties:
            print(f"\nStage: {difficulty.capitalize()}")
            # 3 problems per stage
            for i in range(3):
                problem = self.problem_cls(difficulty)
                game.ask(problem)
                if game.hearts <= 0:
                    print("You've run out of hearts. Lesson paused.")
                    return


class Game:
    def __init__(self, player_name: str):
        self.player = player_name
        self.score = 0
        self.xp = 0
        self.streak = 0
        self.hearts = 3
        self.leaderboard = Leaderboard()
        self.lessons = [
            Lesson("Limits", LimitProblem, difficulties=("easy", "medium")),
            Lesson("Derivatives", DerivativeAtPointProblem, difficulties=("easy", "medium", "hard")),
            Lesson("Integrals", DefiniteIntegralProblem, difficulties=("easy", "medium", "hard")),
        ]

    def print_status(self):
        print(f"\nPlayer: {self.player} | Score: {self.score} | XP: {self.xp} | Streak: {self.streak} | Hearts: {self.hearts}")

    def ask(self, problem: Problem):
        self.print_status()
        print("\n" + problem.prompt())
        # present as multiple-choice sometimes to simplify
        if random.random() < 0.35:
            mc, correct = self.make_multiple_choice(problem)
            for idx, choice in enumerate(mc, start=1):
                print(f"{idx}. {choice}")
            ans = input("Choose option number (or type numeric answer): ").strip()
            picked = None
            if ans.isdigit():
                idx = int(ans)
                if 1 <= idx <= len(mc):
                    picked = mc[idx - 1]
                    # see if picked equals correct (compare numeric)
                    ok, feedback = self.evaluate_mc_pick(picked, correct)
                    if ok:
                        self.on_correct(problem)
                    else:
                        self.on_incorrect(problem, feedback)
                    return
            # else fallback to numeric parse
        # Generic numeric answer:
        user = input("Your answer: ").strip()
        ok, feedback = problem.check_answer(user)
        if ok:
            self.on_correct(problem)
        else:
            self.on_incorrect(problem, feedback)

    def on_correct(self, problem):
        gained = problem.xp_reward()
        self.score += gained
        self.xp += gained
        self.streak += 1
        print(f"✅ Correct! +{gained} points.")
        # small streak bonus
        if self.streak and self.streak % 5 == 0:
            bonus = 20
            self.score += bonus
            self.xp += bonus
            print(f"🔥 Streak bonus! +{bonus} points.")

    def on_incorrect(self, problem, feedback):
        self.hearts -= 1
        self.streak = 0
        print(f"❌ {feedback} - You lost a heart. Hearts left: {self.hearts}")
        if self.hearts <= 0:
            print("No hearts left. End of run.")

    def evaluate_mc_pick(self, picked: str, correct_value: float) -> Tuple[bool, str]:
        # picked may be string expression; try to parse numeric
        pf = safe_float(picked)
        if pf is None:
            return False, "Invalid multiple choice option."
        if abs(pf - correct_value) < 1e-4:
            return True, "Correct!"
        else:
            return False, f"Incorrect. Correct value was {correct_value}."

    def make_multiple_choice(self, problem: Problem):
        # create MC options by computing true value and adding distractors
        # We'll attempt numeric true value by evaluating at appropriate points
        # For LimitProblem and DerivativeAtPointProblem and IntegralProblem, compute true
        true_val = None
        if isinstance(problem, LimitProblem):
            true_val = eval_poly(problem.coeffs, problem.a)
        elif isinstance(problem, DerivativeAtPointProblem):
            true_val = eval_poly(problem.deriv_coeffs, problem.x0)
        elif isinstance(problem, DefiniteIntegralProblem):
            true_val = eval_poly(problem.anti, problem.b) - eval_poly(problem.anti, problem.a)
        else:
            true_val = 0.0

        choices = [round_for_compare(true_val, 5)]
        # generate distractors
        for _ in range(3):
            delta = random.choice([-3, -2, -1, 1, 2, 3]) * random.random()
            distract = round_for_compare(true_val + delta, 5)
            if distract in choices:
                distract += round(random.choice([1, -1, 2]), 5)
            choices.append(distract)
        random.shuffle(choices)
        # Return choices as strings
        return [str(c) for c in choices], round_for_compare(true_val, 5)

    def choose_lesson(self):
        print("\nAvailable lessons:")
        for i, lesson in enumerate(self.lessons, start=1):
            print(f"{i}. {lesson.name}")
        print(f"{len(self.lessons)+1}. Quick Practice (random problems)")
        choice = input("Choose lesson number: ").strip()
        if not choice.isdigit():
            print("Invalid selection.")
            return
        ch = int(choice)
        if ch == len(self.lessons) + 1:
            self.quick_practice()
            return
        if 1 <= ch <= len(self.lessons):
            lesson = self.lessons[ch - 1]
            lesson.run(self)
        else:
            print("Invalid selection.")

    def quick_practice(self, rounds=5):
        print("\n--- Quick Practice ---")
        pool = [LimitProblem, DerivativeAtPointProblem, DefiniteIntegralProblem]
        for _ in range(rounds):
            cls = random.choice(pool)
            dif = random.choice(["easy", "medium", "hard"])
            p = cls(dif)
            self.ask(p)
            if self.hearts <= 0:
                break

    def run(self):
        print(f"Welcome, {self.player}! Let's learn Calculus. You have {self.hearts} hearts.")
        while self.hearts > 0:
            self.choose_lesson()
            cont = input("Continue playing? (y/n): ").strip().lower()
            if cont != "y":
                break
        print(f"\nRun ended. Score: {self.score} | XP: {self.xp}")
        self.leaderboard.add_score(self.player, self.score)
        self.leaderboard.print_board(10)
        print("Thanks for playing! Come back to improve your best score.")


# ---------------------------
# CLI entry point
# ---------------------------
def main():
    print("=== Calculus Duo (terminal) ===")
    name = input("Enter your player name: ").strip()
    if not name:
        name = "Player"
    game = Game(name)
    game.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nGoodbye!")
        sys.exit(0)
