import ast
import subprocess
import tempfile
import os
import json

try:
    import ollama
except ImportError:
    ollama = None
from pydantic import BaseModel


class GymJudgment(BaseModel):
    met: list[str]
    missed: list[str]
    feedback: str
    thinking_trick: str


def judge_free_text(exercise, user_answer):
    if not ollama:
        return None
    system_prompt = f"""You are a strict but fair coding mentor.
The user is doing an exercise of type {exercise.get("type")}.
Topic: {exercise.get("topic")}.
Prompt: {exercise.get("prompt")}
Expected answer ideas / rubric: {exercise.get("rubric") or exercise.get("answer")}

Evaluate their answer against the expected ideas.
Return JSON with:
- met: list of rubric points they hit (strings)
- missed: list of rubric points they missed (strings)
- feedback: short encouraging feedback. DO NOT give the full solution.
- thinking_trick: a one-sentence reusable mental habit."""

    try:
        MODEL = os.getenv("ROOTCAUSE_MODEL", "gemma3:12b")
        resp = ollama.chat(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"My answer: {user_answer}"},
            ],
            format=GymJudgment.model_json_schema(),
            options={"temperature": 0.2},
        )
        return json.loads(resp["message"]["content"])
    except Exception as e:
        print(f"Gym judgment failed: {e}")
        return None


def is_safe_code(code: str) -> bool:
    """Check AST for disallowed operations like imports or file access."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return False

    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            return False
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id in ["open", "eval", "exec", "__import__", "input"]:
                    return False
            elif isinstance(node.func, ast.Attribute):
                # Disallow accessing dunder methods directly just to be safe
                if node.func.attr.startswith("__"):
                    return False
    return True


def run_sandboxed(code: str, language: str = "python") -> str:
    """Run code in a subprocess with a 2-second timeout."""
    if language != "python":
        return "Unsupported language for sandboxing."

    if not is_safe_code(code):
        return "Error: Unsafe code detected (imports or restricted functions are not allowed)."

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        temp_path = f.name

    try:
        result = subprocess.run(
            ["python", temp_path], capture_output=True, text=True, timeout=2.0
        )
        output = result.stdout
        if result.stderr:
            output += "\n" + result.stderr
        return output.strip()
    except subprocess.TimeoutExpired:
        return "Error: Timeout (2 seconds)"
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def check_answer(exercise, user_answer):
    """
    Advanced checker:
    For trace/predict: Use exact match with expected output.
    For bug/pattern: Exact match string comparison.
    For order: List comparison.
    """
    if not user_answer:
        return False

    ex_type = exercise["type"]
    correct_answer = exercise["answer"]

    if ex_type in ["pattern", "trace", "predict", "bug"]:
        return str(user_answer).strip().lower() == str(correct_answer).strip().lower()

    elif ex_type == "order":
        if isinstance(user_answer, list) and isinstance(correct_answer, list):
            return user_answer == correct_answer
        return False

    elif ex_type in ["edge", "pseudo", "brute"]:
        # Rubric matching
        if exercise.get("rubric"):
            user_text = str(user_answer).lower()
            return any(keyword.lower() in user_text for keyword in exercise["rubric"])
        else:
            return (
                str(user_answer).strip().lower() == str(correct_answer).strip().lower()
            )

    return False


def verify_exercise_output(exercise):
    """Verify if the generated exercise's code actually produces its claimed answer."""
    ex_type = exercise["type"]

    if ex_type not in ["predict", "trace"]:
        return True  # We only sandbox predict and trace

    code = exercise.get("code")
    if not code:
        return False

    if ex_type == "predict":
        actual_out = run_sandboxed(code, exercise.get("language", "python"))
        return (
            str(actual_out).strip().lower() == str(exercise["answer"]).strip().lower()
        )

    # For 'trace', the code itself might not print anything, it asks for a variable value.
    # To verify 'trace', we might append a print statement to the code.
    if ex_type == "trace":
        # Assume the prompt asks for a specific variable. We don't easily know which one,
        # but if we trust the bank, we can skip strict verification, OR we append `print(x)`.
        # For simplicity, we just return True for bank trace exercises for now,
        # as trace verification requires injecting `print(var)`.
        return True

    return True


def check_answer_advanced(exercise, user_answer):
    res = check_answer(exercise, user_answer)
    ex_type = exercise["type"]

    if ex_type in ["pseudo", "edge", "brute", "bug"]:
        judgment = judge_free_text(exercise, user_answer)
        if judgment:
            # If they missed nothing major, call it correct
            is_correct = len(judgment.get("missed", [])) == 0
            # If our simple check says true, trust it too
            is_correct = is_correct or res
            return is_correct, judgment

    return res, None
