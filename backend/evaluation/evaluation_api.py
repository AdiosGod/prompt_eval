from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# ================================
# CREATE FASTAPI APP
# ================================

app = FastAPI()

# ================================
# ENABLE CORS
# ================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================================
# REQUEST MODEL
# ================================

class EvalRequest(BaseModel):
    section_type: str
    output: str

# ================================
# ROOT ENDPOINT
# ================================

@app.get("/")
def home():
    return {
        "message": "Evaluation API is running successfully"
    }

# ================================
# EVALUATION ENDPOINT
# ================================

@app.post("/api/evaluate")
def evaluate(req: EvalRequest):

    score = 0
    checks = {}

    # =================================
    # CHECK 1 — Contains CIBIL
    # =================================

    if "CIBIL" in req.output.upper():

        checks["contains_cibil"] = True
        score += 1

    else:

        checks["contains_cibil"] = False

    # =================================
    # CHECK 2 — Word Limit
    # =================================

    if len(req.output.split()) <= 80:

        checks["within_limit"] = True
        score += 1

    else:

        checks["within_limit"] = False

    # =================================
    # FINAL SCORE
    # =================================

    final_score = round((score / 2) * 5, 1)

    # =================================
    # PASS / FAIL
    # =================================

    passed = final_score >= 4.0

    # =================================
    # RETURN RESPONSE
    # =================================

    return {

        "section_type": req.section_type,

        "score": final_score,

        "max_score": 5.0,

        "checks": checks,

        "passed": passed
    }
