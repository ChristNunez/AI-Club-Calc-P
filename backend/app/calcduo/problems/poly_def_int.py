from .base import Problem
from ..poly import gen_poly, poly_to_string, eval_poly, antiderivative_coeffs
from ..utils import safe_float, numerically_equal
import random


class DefiniteIntegralProblem(Problem):
    def __init__(self, difficulty):
        super().__init__(difficulty)

        # Degree / coefficient range per difficulty
        if difficulty == "easy":
            deg = 1
            coeff_rng = (-5, 5)
            lo, hi = -3, 3          # integration bounds range
        elif difficulty == "medium":
            deg = 2
            coeff_rng = (-8, 8)
            lo, hi = -5, 5
        else:
            deg = 3
            coeff_rng = (-12, 12)
            lo, hi = -8, 8

        self.coeffs = gen_poly(deg, coeff_range=coeff_rng)

        # Pick bounds with a < b
        a = random.randint(lo, hi)
        b = random.randint(lo, hi)
        while a == b:
            b = random.randint(lo, hi)
        self.a, self.b = (a, b) if a < b else (b, a)

        # Build antiderivative coefficients once
        self.anti = antiderivative_coeffs(self.coeffs)

    def prompt(self):
        expr = poly_to_string(self.coeffs)
        return f"Compute definite integral: ∫_{self.a}^{self.b} {expr} dx"

    def check_answer(self, answer: str):
        ansf = safe_float(answer)
        if ansf is None:
            return False, "Please enter a numeric value."

        true_b = eval_poly(self.anti, self.b)
        true_a = eval_poly(self.anti, self.a)
        true = true_b - true_a

        if numerically_equal(ansf, true, tol=1e-4):
            return True, "Correct!"
        else:
            return False, f"Incorrect. The integral equals {true}."
