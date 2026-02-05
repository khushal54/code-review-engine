from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from ai_service import review_code

app = FastAPI(title="AI Code Review & Rewrite Agent")

class CodeInput(BaseModel):
    code: str
    language: str

@app.post("/review")
def review(input: CodeInput):
    if not input.code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty")

    result = review_code(input.code, input.language)
    return {"review": result}
