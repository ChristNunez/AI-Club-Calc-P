
class Lesson:
    def __init__(self, name: str, problem_cls, difficulties=("easy", "medium", "hard")):
        self.name = name
        self.problem_cls = problem_cls
        self.difficulties = difficulties

    def run(self, game):
        print(f"\n--- Lesson: {self.name} ---")
        for difficulty in self.difficulties:
            print(f"\nStage: {difficulty.capitalize()}")
            for _ in range(3):  # 3 problems per stage
                problem = self.problem_cls(difficulty)
                game.ask(problem)
                if game.hearts <= 0:
                    print("You've run out of hearts. Lesson paused.")
                    return
