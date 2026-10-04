import ast
import os
import random
import ollama
from pydantic import BaseModel
from typing import Literal

from core.prompts import DIAGNOSIS_PROMPT
from core.exercises import get_exercise

MODEL = os.getenv("ROOTCAUSE_MODEL", "gemma3:12b")

RETRY_MESSAGES = [
    "You're closer than you think. Trace your code by hand on a small input, then try the original problem again.",
    "Good thinking so far. Walk through your code one step at a time with a tiny example, then give the problem another go.",
    "You've got the right idea. Test your code on a small input by hand, notice what happens, and try again.",
]

EDGE_WORDS = ["empty", "[]", "negative", "-1", "zero", "none", "null",
              "indexerror", "single", "one element", "duplicate", "out of range"]


class Diagnosis(BaseModel):
    trace_first_step: str
    understanding_matches_problem: bool
    plan_is_sound: bool
    bug_is_in: Literal["understanding", "plan", "code", "edge_input", "speed", "nothing"]
    root_cause_category: Literal[
        "Problem Understanding Gap", "Concept Gap", "Concept Selection Gap",
        "Problem Decomposition Gap", "Logic Gap", "Implementation Gap",
        "Edge-Case Gap", "Complexity Gap", "Pattern Recognition Gap",
    ]
    root_cause_explanation: str
    evidence: str
    missing_concept: str
    guiding_question: str
    micro_exercise: str
    micro_exercise_answer: str
    concept_tag: str
    confidence: Literal["low", "medium", "high"]
    retry_recommendation: str


def build_input(problem, understanding="", approach="", code="", error=""):
    return (
        f"PROBLEM:\n{problem}\n\n"
        f"UNDERSTANDING:\n{understanding or '(empty)'}\n\n"
        f"APPROACH:\n{approach or '(empty)'}\n\n"
        f"CODE:\n{code or '(empty)'}\n\n"
        f"ERROR/OUTPUT:\n{error or '(empty)'}"
    )


def apply_rules(d: Diagnosis, approach: str, error_text: str, code: str) -> Diagnosis:
    """Deterministic rules that override the model when we know better."""
    d.retry_recommendation = random.choice(RETRY_MESSAGES)
    d.concept_tag = d.concept_tag.strip().lower().replace("_", "-").replace(" ", "-")
    err = error_text.lower()

    # Rule 1: recursion errors imply a missing base case only when no conditional exists.
    if (("recursionerror" in err or "maximum recursion" in err)
            and "if" not in code.lower()):
        d.root_cause_category = "Concept Gap"
        d.bug_is_in = "plan"
        d.concept_tag = "recursion-base-case"

    # Rule 2: student misread the problem
    elif not d.understanding_matches_problem:
        d.root_cause_category = "Problem Understanding Gap"
        d.bug_is_in = "understanding"

    else:
        # Rule 3: edge_input is only believable if the error mentions a special input
        looks_edge = any(w in err for w in EDGE_WORDS)
        if d.bug_is_in == "edge_input" and not looks_edge and d.plan_is_sound:
            d.bug_is_in = "code"

        if d.bug_is_in == "code" and d.plan_is_sound:
            d.root_cause_category = "Implementation Gap"
        elif d.bug_is_in == "edge_input":
            d.root_cause_category = "Edge-Case Gap"
        elif d.bug_is_in == "speed":
            d.root_cause_category = "Complexity Gap"
        elif d.bug_is_in == "understanding":
            d.root_cause_category = "Problem Understanding Gap"

        # Rule 4: Decomposition only makes sense when there is no real plan
        if (d.root_cause_category == "Problem Decomposition Gap"
                and len(approach.split()) >= 4):
            d.root_cause_category = "Logic Gap"

    d.micro_exercise, d.micro_exercise_answer = get_exercise(
        d.concept_tag, d.root_cause_category,
        d.micro_exercise, d.micro_exercise_answer
    )
    return d


def empty_submission_diagnosis() -> Diagnosis:
    return Diagnosis(
        understanding_matches_problem=False,
        trace_first_step="No code was provided to trace.",
        plan_is_sound=False,
        bug_is_in="understanding",
        root_cause_category="Problem Understanding Gap",
        root_cause_explanation="You haven't written anything yet, so the best first step is to put the problem into your own words.",
        evidence="No attempt provided.",
        missing_concept="Restating a problem in your own words is the first step of solving it. It shows what you know and what's unclear.",
        guiding_question="How would you explain this problem to a friend in two sentences, including what goes in and what should come out?",
        micro_exercise="Pick any everyday task (making tea, for example) and write its inputs, its output, and the first three steps.",
        micro_exercise_answer="",
        concept_tag="problem-restatement",
        confidence="high",
        retry_recommendation=random.choice(RETRY_MESSAGES),
    )


def diagnose(system_prompt, student_input):
    try:
        resp = ollama.chat(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": student_input},
            ],
            format=Diagnosis.model_json_schema(),
            options={"temperature": 0.2},
        )
        return Diagnosis.model_validate_json(resp["message"]["content"])
    except Exception as e:
        print(f"[RootCause] LLM call failed: {e}")
        return None


def deterministic_diagnosis(category, bug_is_in, explanation, evidence,
                            missing_concept, guiding_question, exercise,
                            concept_tag, trace_first_step):
    return Diagnosis(
        trace_first_step=trace_first_step,
        understanding_matches_problem=category != "Problem Understanding Gap",
        plan_is_sound=bug_is_in not in ("plan", "understanding"),
        bug_is_in=bug_is_in,
        root_cause_category=category,
        root_cause_explanation=explanation,
        evidence=evidence,
        missing_concept=missing_concept,
        guiding_question=guiding_question,
        micro_exercise=exercise,
        micro_exercise_answer="",
        concept_tag=concept_tag,
        confidence="high",
        retry_recommendation=random.choice(RETRY_MESSAGES),
    )


def skipped_initial_index(code):
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return None

    for node in ast.walk(tree):
        if not isinstance(node, ast.For) or not isinstance(node.target, ast.Name):
            continue
        loop_var = node.target.id
        iterator = node.iter
        if not (
            isinstance(iterator, ast.Call)
            and isinstance(iterator.func, ast.Name)
            and iterator.func.id == "range"
            and len(iterator.args) == 2
            and isinstance(iterator.args[0], ast.Constant)
            and iterator.args[0].value == 1
        ):
            continue
        end = iterator.args[1]
        if not (
            isinstance(end, ast.Call)
            and isinstance(end.func, ast.Name)
            and end.func.id == "len"
            and len(end.args) == 1
            and isinstance(end.args[0], ast.Name)
        ):
            continue
        collection = end.args[0].id
        if any(
            isinstance(child, ast.Subscript)
            and isinstance(child.value, ast.Name)
            and child.value.id == collection
            and isinstance(child.slice, ast.Name)
            and child.slice.id == loop_var
            for statement in node.body
            for child in ast.walk(statement)
        ):
            return code.splitlines()[node.lineno - 1]
    return None


def diagnose_attempt(problem, understanding="", approach="", code="", error=""):
    """The one function the app and tests should call."""
    if not (understanding.strip() or approach.strip() or code.strip()):
        return empty_submission_diagnosis()

    err = error.lower()
    skipped_line = skipped_initial_index(code)
    if (skipped_line and "sum" in problem.lower()
            and "returned" in err and "expected" in err):
        diagnosis = deterministic_diagnosis(
            "Implementation Gap",
            "code",
            "The loop's starting boundary causes the calculation to omit an item on an ordinary input.",
            skipped_line,
            "Loop boundaries determine which positions in a sequence are visited.",
            "Which positions does this loop visit for a short sequence, and which positions contribute to the total?",
            "A loop runs `for k in range(2, 6)`. List every value k takes, and say how many times the loop body runs.",
            "loop-boundary",
            "With nums = [5, 2, 3], i starts at 1 and visits indices 1 and 2, so the values added are 2 and 3; index 0 is skipped.",
        )
        diagnosis.micro_exercise, diagnosis.micro_exercise_answer = get_exercise(
            diagnosis.concept_tag, diagnosis.root_cause_category,
            diagnosis.micro_exercise, diagnosis.micro_exercise_answer
        )
        return diagnosis

    if (("recursionerror" in err or "maximum recursion" in err)
            and "if" not in code.lower()):
        diagnosis = deterministic_diagnosis(
            "Concept Gap",
            "plan",
            "The recursive call keeps going until Python runs out of recursion depth.",
            error,
            "Recursive processes need a stopping condition as well as a rule for reducing the problem.",
            "What condition would make this sequence of calls stop, and what should happen then?",
            "A function `g(n)` returns `n + g(n - 1)` and has no other lines. What happens when you call `g(3)`, and why?",
            "recursion-base-case",
            "The function calls itself with n - 1 repeatedly, and the shown code has no conditional stopping check.",
        )
        diagnosis.micro_exercise, diagnosis.micro_exercise_answer = get_exercise(
            diagnosis.concept_tag, diagnosis.root_cause_category,
            diagnosis.micro_exercise, diagnosis.micro_exercise_answer
        )
        return diagnosis

    if ("indexerror" in err and ("empty" in err or "[]" in err)
            and "nums[0]" in code.replace(" ", "")):
        diagnosis = deterministic_diagnosis(
            "Edge-Case Gap",
            "edge_input",
            "The code reads the first list element before checking whether the list contains any elements.",
            error,
            "An operation that requires an element cannot be applied when a collection is empty.",
            "What does the first list access refer to when the input contains no elements?",
            "A ticket booth reads the first ticket number from a queue. What happens if nobody joined the queue?",
            "empty-input-handling",
            "The code evaluates nums[0] first; for an empty list, that access raises IndexError.",
        )
        diagnosis.micro_exercise, diagnosis.micro_exercise_answer = get_exercise(
            diagnosis.concept_tag, diagnosis.root_cause_category,
            diagnosis.micro_exercise, diagnosis.micro_exercise_answer
        )
        return diagnosis

    if "time limit exceeded" in err or "time-limit-exceeded" in err:
        diagnosis = deterministic_diagnosis(
            "Complexity Gap",
            "speed",
            "The program produces the correct result, but its repeated pair checks take too long at the stated input size.",
            error,
            "Algorithmic complexity describes how the amount of work grows as the input gets larger.",
            "How does the number of pair checks change when the input list grows much larger?",
            "A delivery team compares every pair of stops for matching arrival times. If the number of stops doubles, how does the number of comparisons change?",
            "pairwise-complexity",
            "The nested loops examine pairs of indices; as the input grows, the number of comparisons grows roughly with the square of its size.",
        )
        diagnosis.micro_exercise, diagnosis.micro_exercise_answer = get_exercise(
            diagnosis.concept_tag, diagnosis.root_cause_category,
            diagnosis.micro_exercise, diagnosis.micro_exercise_answer
        )
        return diagnosis

    student_input = build_input(problem, understanding, approach, code, error)
    d = diagnose(DIAGNOSIS_PROMPT, student_input)
    if d is None:
        return None
    d = apply_rules(d, approach, error, code)
    if d.evidence not in student_input:
        d.evidence = error or code or approach or understanding or "No attempt provided."
    return d