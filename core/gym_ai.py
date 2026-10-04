import json
import os
import random
import uuid

try:
    import ollama
except ImportError:
    ollama = None

from core.gym_bank import GYM_BANK
from core.gym_checker import verify_exercise_output


def get_weak_spots(session_results):
    # Stub for weak spot detection based on gym results
    # Ideally reads from DB, but we'll mock top 3 for now if memory is small
    pass


def generate_exercise(topic: str, ex_type: str, difficulty: str) -> dict:
    if not ollama:
        return None

    system_prompt = f"""You are a computer science instructor. Generate a coding exercise for a student.
Topic: {topic}
Type: {ex_type}
Difficulty: {difficulty}

Return ONLY a valid JSON object matching this schema exactly:
{{
  "id": "str (generate a random short ID)",
  "type": "{ex_type}",
  "topic": "{topic}",
  "difficulty": "{difficulty}",
  "language": "python",
  "prompt": "str (the question)",
  "code": "str or null (the code snippet if needed)",
  "options_or_steps": null (unless it's 'order' type),
  "answer": "str (the exact answer or output)",
  "rubric": ["keyword1", "keyword2"] (if free-text),
  "hints": ["hint1", "hint2", "hint3"],
  "explanation": "str (why the answer is correct)",
  "thinking_trick": "str (a short reusable mental habit)",
  "source": "generated"
}}
"""
    MODEL = os.getenv("ROOTCAUSE_MODEL", "gemma3:12b")
    for attempt in range(2):
        try:
            resp = ollama.chat(
                model=MODEL,
                messages=[{"role": "system", "content": system_prompt}],
                options={"temperature": 0.7},
            )
            text = resp["message"]["content"]
            # basic extraction in case of markdown blocks
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]

            data = json.loads(text.strip())

            # Validation
            if data["type"] != ex_type or "prompt" not in data or "answer" not in data:
                continue

            # Verify code
            if not verify_exercise_output(data):
                continue

            return data
        except Exception:
            continue

    return None


def build_workout(
    mode: str, count: int = 5, topic=None, ex_type=None, difficulty="medium"
):
    """Builds a list of exercises based on the mode, falling back to bank."""
    exercises = []

    if mode == "Daily Workout":
        # Deterministic based on today's date
        import datetime

        seed = int(datetime.datetime.now().strftime("%Y%m%d"))
        rnd = random.Random(seed)
        exercises = rnd.sample(GYM_BANK, min(3, len(GYM_BANK)))
        return exercises

    elif mode == "Review Mistakes":
        # In a real app we'd pull from DB where correct=0. For now, random.
        exercises = random.sample(GYM_BANK, min(count, len(GYM_BANK)))
        return exercises

    # Weak-spot or Topic or Quick
    # We attempt to mix some generated with bank if AI is available
    for i in range(count):
        t = topic or random.choice(
            [
                "Loops",
                "Conditions",
                "Arrays/Lists",
                "Strings",
                "Functions",
                "Recursion",
                "Sorting and Searching",
            ]
        )
        typ = ex_type or random.choice(
            ["pattern", "trace", "predict", "bug", "order", "edge", "pseudo", "brute"]
        )

        # Try generation 30% of the time to keep speed up, otherwise bank
        ex = None
        if random.random() < 0.3:
            ex = generate_exercise(t, typ, difficulty)

        if not ex:
            # Fallback to bank
            matching = [
                e
                for e in GYM_BANK
                if (not topic or e["topic"] == topic)
                and (not ex_type or e["type"] == ex_type)
            ]
            if matching:
                ex = random.choice(matching)
            else:
                ex = random.choice(GYM_BANK)

        # Ensure unique IDs for this session
        ex = dict(ex)
        ex["id"] = f"{ex['id']}_{uuid.uuid4().hex[:6]}"
        exercises.append(ex)

    return exercises
