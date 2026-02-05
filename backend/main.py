from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from ai_service import review_code

app = FastAPI(title="AI Code Review & Rewrite Agent")

# -------------------- CORS CONFIG --------------------
# Allows frontend (localhost) to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Hackathon-safe
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------- REQUEST MODEL --------------------
class CodeInput(BaseModel):
    code: str
    language: str

# -------------------- HEALTH CHECK --------------------
@app.get("/")
def home():
    return {"message": "AI Code Review & Rewrite Agent is running"}

# -------------------- REVIEW ENDPOINT --------------------
@app.post("/review")
def review(input: CodeInput):
    if not input.code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty")

    result = review_code(input.code, input.language)

    return {
        "mode": "Fallback AI Review",
        "analysis": result
    }
