from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class EvalRequest(BaseModel):
    section_type: str
    output: str

@app.post("/api/evaluate")
def evaluate(req: EvalRequest):
    return {
        "section_type": req.section_type,
        "output": req.output,
        "status": "Evaluation received"
    }
