from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from ai_service import review_code

app = FastAPI(title="AI Code Review & Rewrite Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class CodeInput(BaseModel):
    code: str
    language: str

@app.get("/")
def health():
    return {"status": "ok"}

@app.post("/review")
def review(input: CodeInput):
    if not input.code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty")

    return {
        "mode": "AI Review",
        "analysis": review_code(input.code, input.language)
    }
