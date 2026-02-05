import os
import requests

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL = "llama-3.3-70b"

def review_code(code: str, language: str):
    prompt = f"""
You are an expert code reviewer.
Review the following {language} code.

Tasks:
- Detect bugs
- Find security issues
- Find performance issues
- Suggest best practices
- Rewrite optimized code

Code:
{code}
"""

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 800
        }
    )

    return response.json()["choices"][0]["message"]["content"]
