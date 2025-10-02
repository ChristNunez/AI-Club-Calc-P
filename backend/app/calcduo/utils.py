
import json

def clamp(x, a, b):
    return max(a, min(b, x))

def safe_float(s):
    try:
        return float(s)
    except Exception:
        return None

def round_for_compare(x, places=5):
    return round(x, places)

def numerically_equal(a, b, tol=1e-4):
    return abs(a - b) <= tol

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def load_json(path, default):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return default
