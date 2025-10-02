# calcduo/engine/game.py
import random
import re
from typing import Tuple

from ..config import HEARTS_START, STREAK_BONUS_EVERY, STREAK_BONUS_POINTS
from ..io_leaderboard import Leaderboard
from ..problems.base import Problem
from ..problems.poly_limit import LimitProblem
from ..problems.poly_deriv_point import DerivativeAtPointProblem
from ..problems.poly_def_int import DefiniteIntegralProblem
from ..problems.sympy_deriv_form import SymPyDerivativeFormProblem
from ..utils import safe_float
from ..poly import eval_poly, derivative_coeffs
from .lesson import Lesson


# Numeric-only input allowlist (used for numeric problems ONLY)
NUMERIC_INPUT_RE = re.compile(r"[0-9x+\-*/^().\s]+$")


class Game:
    def __init__(self, player_name: str):
        self.player = player_name
        self.score = 0
        self.xp = 0
        self.streak = 0
        self.hearts = HEARTS_START
        self.leaderboard = Leaderboard()
        self.lessons = [
            Lesson("Limits", LimitProblem, difficulties=("easy", "medium")),
            Lesson("Derivatives (value at x0)", DerivativeAtPointProblem, difficulties=("easy", "medium", "hard")),
            Lesson("Derivatives (symbolic, trig/ln/exp)", SymPyDerivativeFormProblem, difficulties=("easy", "medium", "hard")),
            Lesson("Integrals", DefiniteIntegralProblem, difficulties=("easy", "medium", "hard")),
        ]

    def print_status(self):
        print(f"\nPlayer: {self.player} | Score: {self.score} | XP: {self.xp} | Streak: {self.streak} | Hearts: {self.hearts}")

    def _collect_answer(self, problem: Problem) -> str | None:
        """
        Collect free-form input. For problems that declare `supports_letters = True`
        (e.g., symbolic derivatives with sin/cos/ln/e^(...)), we DO NOT gate input.

        For numeric-only problems, we keep a light regex to catch obvious typos.
        Returns the raw input string, or None if rejected (and prints the error).
        """
        raw = input("Your answer: ").strip()

        # If the problem wants letters (sin, cos, ln, e, pi...), skip any strict gating
        if getattr(problem, "supports_letters", False):
            return raw

        # Otherwise, numeric-style problems: apply a light allowlist
        if not NUMERIC_INPUT_RE.fullmatch(raw):
            print("❌ Use x, +, -, *, /, and ** (or ^) for powers.")
            return None
        return raw

    def ask(self, problem: Problem):
        self.print_status()
        print("\n" + problem.prompt())

        # Only offer multiple-choice if the problem allows it
        supports_mc = getattr(problem, "supports_mc", True)
        if supports_mc and random.random() < 0.35:
            mc, correct = self.make_multiple_choice(problem)
            for idx, choice in enumerate(mc, start=1):
                print(f"{idx}. {choice}")
            ans = input("Choose option number (or type numeric answer): ").strip()
            if ans.isdigit():
                i = int(ans)
                if 1 <= i <= len(mc):
                    picked = mc[i - 1]
                    ok, feedback = self.evaluate_mc_pick(picked, correct)
                    if ok:
                        self.on_correct(problem)
                        return
                    else:
                        self.on_incorrect(problem, feedback)
                        return

        # Fallback: ask for free-form answer (numeric or expression depending on problem)
        user = self._collect_answer(problem)
        if user is None:
            # Rejected by numeric input gate
            self.on_incorrect(problem, "Invalid input format.")
            return

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
        if self.streak and self.streak % STREAK_BONUS_EVERY == 0:
            self.score += STREAK_BONUS_POINTS
            self.xp += STREAK_BONUS_POINTS
            print(f"🔥 Streak bonus! +{STREAK_BONUS_POINTS} points.")

    def on_incorrect(self, problem, feedback):
        self.hearts -= 1
        self.streak = 0
        print(f"❌ {feedback} - You lost a heart. Hearts left: {self.hearts}")
        if self.hearts <= 0:
            print("No hearts left. End of run.")

    def evaluate_mc_pick(self, picked: str, correct_value: float) -> Tuple[bool, str]:
        pf = safe_float(picked)
        if pf is None:
            return False, "Invalid multiple choice option."
        if abs(pf - correct_value) < 1e-4:
            return True, "Correct!"
        else:
            return False, f"Incorrect. Correct value was {correct_value}."

    def make_multiple_choice(self, problem: Problem):
        """Build 4 options for numeric-style problems."""
        def clean(val):
            return int(val) if abs(val) % 1 < 1e-6 else round(val, 1)

        # Compute correct & distractors for supported numeric problems
        if isinstance(problem, LimitProblem):
            true_val = eval_poly(problem.coeffs, problem.a)
            distractors = [
                eval_poly(problem.coeffs, problem.a + 1),
                eval_poly(problem.coeffs, problem.a - 1),
                eval_poly(derivative_coeffs(problem.coeffs), problem.a),
            ]
        elif isinstance(problem, DerivativeAtPointProblem):
            true_val = eval_poly(problem.deriv_coeffs, problem.x0)
            distractors = [
                eval_poly(problem.coeffs, problem.x0),              # f(x0) not f'(x0)
                eval_poly(problem.deriv_coeffs, problem.x0 + 1),   # off-by-one
                true_val + random.choice([-2, -1, 1, 2]),          # small noise
            ]
        elif isinstance(problem, DefiniteIntegralProblem):
            true_val = eval_poly(problem.anti, problem.b) - eval_poly(problem.anti, problem.a)
            distractors = [
                eval_poly(problem.anti, problem.b + 1) - eval_poly(problem.anti, problem.a),
                eval_poly(problem.anti, problem.b) - eval_poly(problem.anti, problem.a - 1),
                eval_poly(problem.anti, problem.a) - eval_poly(problem.anti, problem.b),  # swapped bounds
            ]
        else:
            # For symbolic problems or unknown types we shouldn't be here
            true_val = 0.0
            distractors = [1.0, -1.0, 2.0]

        correct = clean(true_val)
        choices_set = {correct}
        choices = [correct]

        for d in distractors:
            val = clean(d)
            if val not in choices_set:
                choices.append(val)
                choices_set.add(val)

        while len(choices) < 4:
            noise = clean(correct + random.choice([-3, -2, -1, 1, 2, 3]))
            if noise not in choices_set:
                choices.append(noise)
                choices_set.add(noise)

        random.shuffle(choices)
        return [str(c) for c in choices], correct

    def choose_lesson(self):
        print("\nAvailable lessons:")
        for i, lesson in enumerate(self.lessons, start=1):
            print(f"{i}. {lesson.name}")
        print(f"{len(self.lessons)+1}. Quick Practice (random problems)")
        selection = input("Choose lesson number: ").strip()
        if not selection.isdigit():
            print("Invalid selection.")
            return
        ch = int(selection)
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
        pool = [
            LimitProblem,
            DerivativeAtPointProblem,
            SymPyDerivativeFormProblem,
            DefiniteIntegralProblem,
        ]
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
