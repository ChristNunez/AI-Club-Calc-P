import random
from .base import Problem
from ..poly import gen_poly, poly_to_string, eval_poly
from ..utils import safe_float, round_for_compare


class LimitProblem(Problem):
    def __init__(self, difficulty):
        super().__init__(difficulty)

        # Degree and volatility range for the approach point a
        if difficulty == "easy":
            deg = 1
            lo, hi = -5, 5
        elif difficulty == "medium":
            deg = 2
            lo, hi = -10, 10
        else:
            deg = 3
            lo, hi = -15, 15

        # Random polynomial
        self.coeffs = gen_poly(deg, coeff_range=(-5, 5))

        # Pick a more volatile approach point a (wider than -2..2)
        candidates = list(range(lo, hi + 1))
        self.a = random.choice(candidates)

        # Sometimes force P(a) = 0 (still a polynomial; limit equals P(a))
        if difficulty in ("medium", "hard") and random.random() < 0.25:
            current = eval_poly(self.coeffs, self.a)
            self.coeffs[-1] -= current  # shift constant so P(a) == 0

    def prompt(self):
        expr = poly_to_string(self.coeffs)
        return f"Compute the limit: lim_{{x->{self.a}}} {expr}"

    def check_answer(self, answer: str):
        ansf = safe_float(answer)
        if ansf is None:
            return False, "Please enter a numeric value."
        true = eval_poly(self.coeffs, self.a)
        if round_for_compare(ansf, 5) == round_for_compare(true, 5):
            return True, "Correct!"
        else:
            return False, f"Incorrect. The limit equals {true}."
