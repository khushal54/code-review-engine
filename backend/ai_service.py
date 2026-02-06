import os
import re
import ast
import logging
import requests
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# --------------------------------------------------
# PYTHON SYNTAX CHECK
# --------------------------------------------------
def check_python_syntax(code: str):
    try:
        ast.parse(code)
        return None
    except SyntaxError as e:
        return {
            "type": "Syntax",
            "severity": "Critical",
            "message": f"Syntax error at line {e.lineno}: {e.msg}"
        }

# --------------------------------------------------
# DETECTION HELPERS
# --------------------------------------------------
def contains_eval(code: str):
    return bool(re.search(r"\beval\s*\(", code))

def contains_exec(code: str):
    return bool(re.search(r"\bexec\s*\(", code))

def contains_hardcoded_secret(code: str):
    return bool(re.search(r'password\s*=\s*[\'"].+?[\'"]', code, re.I))

def contains_print(code: str):
    return "print(" in code

def contains_safe_eval(code: str):
    return "def safe_eval" in code

def is_already_optimized(code: str):
    return (
        "safe_eval(" in code
        or "logging.info" in code
        or "os.getenv" in code
    )

# --------------------------------------------------
# SAFE OPTIMIZATION ENGINE
# --------------------------------------------------
def optimize_python_code(code: str) -> str:
    optimized_lines = []
    needs_safe_eval = False

    for line in code.splitlines():
        # Replace print → logging
        line = re.sub(r'print\((.*?)\)', r'logging.info(\1)', line)

        # Replace eval with safe_eval
        if contains_eval(line):
            needs_safe_eval = True
            line = re.sub(r'eval\((.*?)\)', r'safe_eval(\1)', line)

        # Remove exec completely
        if contains_exec(line):
            line = "# exec removed for security reasons"

        # Replace hardcoded password
        line = re.sub(
            r'password\s*=\s*[\'"].+?[\'"]',
            'PASSWORD = os.getenv("APP_PASSWORD")',
            line,
            flags=re.I
        )

        optimized_lines.append(line)

    header = """# ✅ Optimized Python Code
import os
import logging
import ast
import operator

logging.basicConfig(level=logging.INFO)

"""

    safe_eval_block = ""
    if needs_safe_eval and not contains_safe_eval(code):
        safe_eval_block = """
# Safe arithmetic expression evaluator
_ALLOWED_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}

def safe_eval(expr):
    def _eval(node):
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.UnaryOp):
            return _ALLOWED_OPS[type(node.op)](_eval(node.operand))
        if isinstance(node, ast.BinOp):
            return _ALLOWED_OPS[type(node.op)](
                _eval(node.left),
                _eval(node.right)
            )
        raise ValueError("Unsafe expression")

    tree = ast.parse(expr, mode='eval')
    return _eval(tree.body)
"""

    return header + safe_eval_block + "\n".join(optimized_lines).strip()

# --------------------------------------------------
# FALLBACK REVIEW ENGINE (OFFLINE)
# --------------------------------------------------
def fallback_review(code: str, language: str):
    issues = []
    recommendations = []

    # Syntax check
    if language.lower() == "python":
        syntax_issue = check_python_syntax(code)
        if syntax_issue:
            return {
                "summary": "Syntax error detected",
                "issues": [syntax_issue],
                "recommendations": ["Fix syntax errors before optimization"],
                "optimized_code": "❌ Optimization skipped due to syntax errors"
            }

    # Already optimized detection
    if is_already_optimized(code):
        return {
            "summary": "Code is already optimized and secure",
            "issues": [],
            "recommendations": ["No further action required"],
            "optimized_code": code
        }

    if contains_eval(code):
        issues.append({
            "type": "Security",
            "severity": "Critical",
            "message": "Use of dangerous function eval"
        })
        recommendations.append("Replace eval with safe expression parsing")

    if contains_exec(code):
        issues.append({
            "type": "Security",
            "severity": "Critical",
            "message": "Use of dangerous function exec"
        })
        recommendations.append("Remove exec entirely")

    if contains_hardcoded_secret(code):
        issues.append({
            "type": "Security",
            "severity": "High",
            "message": "Hardcoded secret detected"
        })
        recommendations.append("Use environment variables")

    if contains_print(code):
        issues.append({
            "type": "Best Practice",
            "severity": "Medium",
            "message": "Avoid print statements in production"
        })
        recommendations.append("Use logging instead of print")

    optimized_code = optimize_python_code(code)

    return {
        "summary": f"{len(issues)} issue(s) detected",
        "issues": issues,
        "recommendations": list(set(recommendations)),
        "optimized_code": optimized_code
    }

# --------------------------------------------------
# MAIN ENTRY
# --------------------------------------------------
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
                        "role": "system",
                        "content": "You are a secure static code analysis engine."
                    },
                    {
                        "role": "user",
                        "content": f"""
Return STRICT JSON only:
summary, issues[], recommendations[], optimized_code.

RULES:
- NEVER use eval or exec
- If already safe, say so
- Optimized code must be runnable

Analyze this {language} code:
{code}
"""
                    }
                ],
                "temperature": 0.1,
                "max_tokens": 900,
            },
            timeout=10,
        )

        data = response.json()
        if response.status_code != 200 or "choices" not in data:
            return fallback_review(code, language)

        return eval(data["choices"][0]["message"]["content"])

    except Exception:
        return fallback_review(code, language)
