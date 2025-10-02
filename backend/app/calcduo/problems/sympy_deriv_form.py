# calcduo/problems/sympy_deriv_form.py
import random
import re
import sympy as sp
from .base import Problem
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
    convert_xor,
)

x = sp.symbols("x")


def _rand_int(lo, hi, exclude_zero=False):
    n = random.randint(lo, hi)
    if exclude_zero:
        while n == 0:
            n = random.randint(lo, hi)
    return n


def _random_term(difficulty: str):
    """
    Return a SymPy term chosen from:
      A*x^n, A*sin(kx+b), A*cos(kx+b), A*e^(kx+b), A*ln(ax+b)
    Parameter ranges grow with difficulty.
    """
    if difficulty == "easy":
        A_rng = (-5, 5)
        n_rng = (1, 3)
        k_rng = (1, 3)
        b_rng = (-3, 3)
        a_rng = (1, 3)
        choices = ["poly", "sin", "cos"]
    elif difficulty == "medium":
        A_rng = (-7, 7)
        n_rng = (1, 4)
        k_rng = (1, 4)
        b_rng = (-5, 5)
        a_rng = (1, 4)
        choices = ["poly", "sin", "cos", "exp"]
    else:  # hard
        A_rng = (-9, 9)
        n_rng = (1, 5)
        k_rng = (1, 5)
        b_rng = (-6, 6)
        a_rng = (1, 5)
        choices = ["poly", "sin", "cos", "exp", "ln"]

    kind = random.choice(choices)
    A = _rand_int(*A_rng, exclude_zero=True)

    if kind == "poly":
        n = _rand_int(*n_rng)
        return A * (x ** n)

    k = _rand_int(*k_rng)
    b = _rand_int(*b_rng)

    if kind == "sin":
        return A * sp.sin(k * x + b)
    if kind == "cos":
        return A * sp.cos(k * x + b)
    if kind == "exp":
        # Use E**(kx+b) instead of exp(kx+b) so formatting shows e^(...)
        return A * (sp.E ** (k * x + b))
    if kind == "ln":
        a = _rand_int(*a_rng, exclude_zero=True)
        return A * sp.log(a * x + b)

    return A * x


def _random_expr(difficulty: str):
    """Sum 2–4 random terms depending on difficulty."""
    if difficulty == "easy":
        tmin, tmax = 2, 2
    elif difficulty == "medium":
        tmin, tmax = 2, 3
    else:
        tmin, tmax = 3, 4
    num_terms = random.randint(tmin, tmax)
    terms = [_random_term(difficulty) for _ in range(num_terms)]
    return sp.simplify(sum(terms))


def math_str(expr: sp.Expr) -> str:
    """
    Pretty inline formatting for the classroom style:
    - '**' -> '^'
    - collapse 'k * x' -> 'kx'
    - collapse 'k * sin|cos|tan|log' -> 'ksin(...), ...'
    - show exponentials as e^(...)
    """
    s = sp.sstr(expr)  # compact single-line string from SymPy

    # Replace powers
    s = s.replace("**", "^")

    # If SymPy printed exp(...), convert to e^(...)
    s = re.sub(r'\bexp\(([^()]+)\)', r'e^(\1)', s)

    # If SymPy printed E^(...), normalize E -> e
    s = re.sub(r'\bE\b', 'e', s)

    # collapse k * x  ->  kx
    s = re.sub(r'(?<![A-Za-z0-9_])(-?\d+)\s*\*\s*x\b', r'\1x', s)

    # collapse k * func( ... ) for common funcs (leave e^(...) already handled)
    s = re.sub(r'(?<![A-Za-z0-9_])(-?\d+)\s*\*\s*(sin|cos|tan|log)\(', r'\1\2(', s)

    # collapse k * e^(...) -> k e^(...)
    s = re.sub(r'(?<![A-Za-z0-9_])(-?\d+)\s*\*\s*e\^\(', r'\1 e^(', s)

    return s


class SymPyDerivativeFormProblem(Problem):
    """
    Ask the player to enter the full symbolic derivative f'(x) for a
    randomly generated mixed expression f(x) (poly/trig/exp/log).
    """
    supports_mc = False  # no multiple choice
    supports_letters = True  # hint for the engine: allow letters like sin, cos, ln, e, pi

    def __init__(self, difficulty: str):
        super().__init__(difficulty)
        self.f = _random_expr(difficulty)
        self.fprime = sp.diff(self.f, x)

    def prompt(self):
        expr_str = math_str(self.f)
        return f"Given f(x) = {expr_str}\nEnter f'(x):"

    def check_answer(self, answer: str):
        # --- 1) Normalize common input quirks ---
        normalized = (answer or "").strip()
        normalized = (
            normalized.replace("−", "-")  # unicode minus
            .replace("–", "-")            # en dash
            .replace("—", "-")            # em dash
            .replace("×", "*")            # unicode times
            .replace("·", "*")            # middle dot
            .replace("^", "**")           # accept ^ as power
        )

        # --- 2) SymPy parser configuration ---
        transformations = standard_transformations + (
            implicit_multiplication_application,  # allow 2x, 3sin(x), cos(3x+1), 2(x+1)
            convert_xor,
        )

        local_dict = {
            # variable
            "x": x,
            # functions
            "sin": sp.sin, "cos": sp.cos, "tan": sp.tan,
            "exp": sp.exp, "log": sp.log, "ln": sp.log,
            "sqrt": sp.sqrt, "sec": sp.sec, "csc": sp.csc, "cot": sp.cot,
            # constants
            "pi": sp.pi, "e": sp.E, "E": sp.E,
        }

        def _try_parse(s: str):
            return parse_expr(
                s,
                transformations=transformations,
                local_dict=local_dict,
                evaluate=True,
            )

        # --- 3) First attempt: tolerant parse with implicit multiplication ---
        try:
            user_expr = _try_parse(normalized)
        except Exception:
            # --- 4) Fallback: insert '*' where implicit mult may be missing, then parse ---
            s = normalized

            # number followed by (x or '(' or a function)  -> insert '*'
            s = re.sub(r'(\d)\s*(?=x\b|\()', r'\1*', s)
            s = re.sub(r'(\d)\s*(?=(sin|cos|tan|exp|log|ln|sqrt|sec|csc|cot)\()', r'\1*', s)

            # closing paren followed by (x or digit or '(' or function) -> insert '*'
            s = re.sub(r'\)\s*(?=x\b|\d|\()', r')*', s)
            s = re.sub(r'\)\s*(?=(sin|cos|tan|exp|log|ln|sqrt|sec|csc|cot)\()', r')*', s)

            # x followed by '(' -> x*(...)
            s = re.sub(r'\bx\s*(?=\()', r'x*', s)

            try:
                user_expr = _try_parse(s)
            except Exception:
                return (
                    False,
                    "Couldn't parse that. Examples I accept: 3x, 3*sin(x), cos(3x+1), "
                    "x^2 (or x**2), e^(3x+1), ln(x)."
                )

        # --- 5) Equivalence check: algebraic simplify ---
        diff = sp.simplify(sp.together(sp.expand(user_expr - self.fprime)))
        if diff == 0:
            return True, "Correct!"
        return False, f"Not quite. One correct form is: {math_str(self.fprime)}"
