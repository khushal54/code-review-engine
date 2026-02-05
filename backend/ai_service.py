import os
import requests
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

print("GROQ KEY LOADED:", GROQ_API_KEY is not None)


def fallback_review(code: str, language: str):
    issues = []

    if "password" in code.lower():
        issues.append("Security issue: Hardcoded password detected")

    if "print(" in code:
        issues.append("Best practice: Avoid print statements in production")

    if "for" in code:
        issues.append("Performance: Loop optimization may be possible")

    return f"""
⚠️ AI Review (Fallback Mode)

Bugs / Issues:
- {"; ".join(issues) if issues else "No major issues found"}

Optimized Suggestion:
- Use environment variables for secrets
- Add input validation
- Use logging instead of print

Optimized Code (example):
# Refactored {language} code
# (Generated safely without external AI)
"""


def review_code(code: str, language: str):
    if not GROQ_API_KEY:
        return fallback_review(code, language)

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "llama3-8b-8192",
                "messages": [
                    {
                        "role": "user",
                        "content": f"Review this {language} code:\n{code}"
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 500,
            },
            timeout=10,
        )

        data = response.json()

        if response.status_code != 200 or "choices" not in data:
            return fallback_review(code, language)

        return data["choices"][0]["message"]["content"]

    except Exception:
        return fallback_review(code, language)
