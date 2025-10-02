import random
from .base import Problem
from ..poly import gen_poly, poly_to_string, eval_poly, derivative_coeffs
from ..utils import safe_float, numerically_equal


class DerivativeAtPointProblem(Problem):
    def __init__(self, difficulty):
        super().__init__(difficulty)

        # Degree / coefficient range and x0 range per difficulty
        if difficulty == "easy":
            deg = 1
            coeff_rng = (-5, 5)
            x_lo, x_hi = -5, 5
        elif difficulty == "medium":
            deg = 2
            coeff_rng = (-8, 8)
            x_lo, x_hi = -10, 10
        else:
            deg = 3
            coeff_rng = (-12, 12)
            x_lo, x_hi = -15, 15

        self.coeffs = gen_poly(deg, coeff_range=coeff_rng)

        # Volatile evaluation point x0 (wider than -2..2)
        self.x0 = random.randint(x_lo, x_hi)

        # Precompute derivative coefficients
        self.deriv_coeffs = derivative_coeffs(self.coeffs)

    def prompt(self):
        expr = poly_to_string(self.coeffs)
        return f"Find f'({self.x0}) for f(x) = {expr}"

    def check_answer(self, answer: str):
        ansf = safe_float(answer)
        if ansf is None:
            return False, "Please enter a numeric value."

        true = eval_poly(self.deriv_coeffs, self.x0)

        if numerically_equal(ansf, true, tol=1e-4):
            return True, "Correct!"
        else:
            return False, f"Incorrect. f'({self.x0}) = {true}."
