from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid

# Import your SymPy derivative problem class from your package we just copied
from app.calcduo.problems.sympy_deriv_form import SymPyDerivativeFormProblem

app = FastAPI()

# Allow your Expo app to call this API (relax in dev; restrict in prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store for problems (good enough for dev)
PROBLEMS = {}

class NewReq(BaseModel):
    difficulty: str = "easy"

class AnswerReq(BaseModel):
    problem_id: str
    answer: str

@app.get("/healthz")
def health():
    return {"ok": True}

@app.post("/new-problem")
def new_problem(req: NewReq):
    p = SymPyDerivativeFormProblem(req.difficulty)
    pid = str(uuid.uuid4())
    PROBLEMS[pid] = p
    return {"problem_id": pid, "prompt": p.prompt()}

@app.post("/answer")
def answer(req: AnswerReq):
    p = PROBLEMS.get(req.problem_id)
    if not p:
        return {"ok": False, "feedback": "Problem expired. Start a new one."}
    ok, feedback = p.check_answer(req.answer)
    return {"ok": ok, "feedback": feedback}
