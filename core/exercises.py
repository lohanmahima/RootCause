EXERCISE_BANK = {
    "loop-boundary": {
        "exercise": "A loop runs `for k in range(2, 6)`. List every value k takes, and say how many times the loop body runs.",
        "answer": "k takes 2, 3, 4, 5. The body runs 4 times.",
    },
    "initialization-edge-cases": {
        "exercise": "A function tracks the smallest temperature in a list by starting with `min_t = 0`. Which kinds of lists make it return a wrong answer?",
        "answer": "Any list where all temperatures are above 0, e.g. [5, 8, 3]. It returns 0, which isn't in the list.",
    },
    "recursion-base-case": {
        "exercise": "A function `f(n)` returns `n + f(n - 1)` and has no other lines. What happens when you call f(3), and why?",
        "answer": "It never stops: n keeps decreasing past 0 into negatives until the program crashes, because nothing tells it to stop.",
    },
    "recursion-state-update": {
        "exercise": "A function `g(n)` calls `g(n + 1)` and is meant to stop when n == 0. If you call g(3), will it ever stop? Why or why not?",
        "answer": "No. n goes 4, 5, 6... and moves away from 0, so the stopping condition is never reached.",
    },
    "off-by-one-slicing": {
        "exercise": "For `letters = ['a','b','c','d','e']`, what does `letters[1:3]` return, and why isn't 'd' included?",
        "answer": "['b', 'c']. The end index of a slice is excluded.",
    },
}

TAG_ALIASES = {
    "loop-boundaries": "loop-boundary",
}

BANK_CATEGORIES = {
    "loop-boundary": ["Implementation Gap", "Logic Gap", "Edge-Case Gap"],
    "initialization-edge-cases": ["Edge-Case Gap", "Implementation Gap"],
    "recursion-base-case": ["Concept Gap", "Logic Gap"],
    "recursion-state-update": ["Implementation Gap", "Logic Gap"],
    "off-by-one-slicing": ["Implementation Gap", "Logic Gap"],
}

BAD_STARTS = ("write", "implement", "create a function", "code")

FALLBACK_EXERCISE = (
    "Pick a tiny input (2 or 3 values) and trace your code line by line. "
    "Write down each variable after every step. Where does it first differ "
    "from what you expected?"
)


def get_exercise(concept_tag, category, model_exercise, model_answer):
    """Return a vetted exercise, or a safe model exercise for unknown concepts."""
    normalized_tag = concept_tag.strip().lower().replace("_", "-").replace(" ", "-")
    normalized_tag = TAG_ALIASES.get(normalized_tag, normalized_tag)

    if (normalized_tag in EXERCISE_BANK
            and category in BANK_CATEGORIES.get(normalized_tag, [])):
        item = EXERCISE_BANK[normalized_tag]
        return item["exercise"], item["answer"]

    exercise = model_exercise.strip()
    lowered_exercise = exercise.lower()
    if lowered_exercise.startswith(BAD_STARTS) or "write a" in lowered_exercise:
        return FALLBACK_EXERCISE, ""

    return model_exercise, model_answer
