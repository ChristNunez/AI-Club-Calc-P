
from typing import Tuple
from ..config import XP_BY_DIFFICULTY

class Problem:
    def __init__(self, difficulty: str):
        self.difficulty = difficulty

    def prompt(self) -> str:
        raise NotImplementedError

    def check_answer(self, answer: str) -> Tuple[bool, str]:
        raise NotImplementedError

    def xp_reward(self) -> int:
        return XP_BY_DIFFICULTY.get(self.difficulty, 10)
