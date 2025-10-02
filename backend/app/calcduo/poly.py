
import random
from typing import List
import sympy as sp

x = sp.symbols('x')   # used if you later want SymPy expressions

def coeffs_to_sympy_expr(coeffs: List[float]):
    """coeffs are highest -> constant; returns a SymPy expression"""
    n = len(coeffs) - 1
    expr = 0
    for i, c in enumerate(coeffs):
        p = n - i
        expr += c * (x ** p)
    return sp.simplify(expr)

def gen_poly(degree: int, coeff_range=(-5, 5)):
    coeffs = []
    for i in range(degree + 1):
        if i == 0 and degree > 0:
            c = 0
            while c == 0:  # leading coeff must be non-zero
                c = random.randint(*coeff_range)
        else:
            c = random.randint(*coeff_range)  # inner zeros allowed
        coeffs.append(c)
    if degree == 0 and coeffs[0] == 0:  # avoid all-zero constant
        coeffs[0] = random.choice([-3, -2, -1, 1, 2, 3])
    return coeffs

def poly_to_string(coeffs):
    terms = []
    degree = len(coeffs) - 1
    for i, c in enumerate(coeffs):
        powr = degree - i
        if c == 0: continue
        sign = "-" if c < 0 else "+"
        abs_c = abs(c)
        if powr == 0:
            term = f"{abs_c}"
        elif powr == 1:
            term = ("x" if abs_c == 1 else f"{abs_c}x")
        else:
            term = (f"x^{powr}" if abs_c == 1 else f"{abs_c}x^{powr}")
        terms.append((sign, term))
    if not terms:
        return "0"
    first_sign, first_term = terms[0]
    s = (("-" if first_sign == "-" else "") + first_term)
    for sign, term in terms[1:]:
        s += f" {sign} {term}"
    return s

def eval_poly(coeffs, xval):
    acc = 0.0
    for c in coeffs:  # Horner's method
        acc = acc * xval + c
    return acc

def derivative_coeffs(coeffs):
    degree = len(coeffs) - 1
    if degree == 0:
        return [0]
    deriv = []
    for i, c in enumerate(coeffs):
        powr = degree - i
        if powr == 0: continue
        deriv.append(c * powr)
    return deriv

def antiderivative_coeffs(coeffs):
    degree = len(coeffs) - 1
    anti = []
    for i, c in enumerate(coeffs):
        powr = degree - i
        anti.append(c / (powr + 1))  # coefficient for x^(powr+1)
    anti.append(0.0)  # +C
    return anti  # highest -> constant
