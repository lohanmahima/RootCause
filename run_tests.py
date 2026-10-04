import json
import sys

from core.llm import diagnose_attempt, build_input, MODEL

RUNS = int(sys.argv[1]) if len(sys.argv) > 1 else 1


def norm(s):
    return " ".join(s.split()).lower()


with open("tests.json", encoding="utf-8") as f:
    cases = json.load(f)

print(f"MODEL: {MODEL} | runs per case: {RUNS}\n")
total = passed = 0

for case in cases:
    student_input = build_input(
        case["problem"], case["understanding"], case["approach"],
        case["code"], case["error"],
    )
    for run in range(1, RUNS + 1):
        total += 1
        r = diagnose_attempt(case["problem"], case["understanding"], case["approach"],
                             case["code"], case["error"])
        if r is None:
            print(f"FAIL  {case['name']} (run {run}): LLM call failed")
            continue

        cat_ok = r.root_cause_category in case["expected"]
        ev_ok = (r.evidence.strip() == "No attempt provided."
                 or norm(r.evidence) in norm(student_input))
        trace_ok = bool(r.trace_first_step.strip())
        leaked = [w for w in case["forbidden"]
                  if w.lower() in (r.guiding_question + " " + r.micro_exercise).lower()]
        leak_ok = not leaked

        ok = cat_ok and ev_ok and trace_ok and leak_ok
        passed += ok
        print(f"{'PASS' if ok else 'FAIL'}  {case['name']} (run {run})")
        print(f"      category: {r.root_cause_category}  {'OK' if cat_ok else 'FAIL expected ' + str(case['expected'])}")
        print(f"      trace present: {'OK' if trace_ok else 'FAIL'}")
        print(f"      evidence real: {'OK' if ev_ok else 'FAIL ' + r.evidence}")
        print(f"      no leak: {'OK' if leak_ok else 'FAIL found ' + str(leaked)}")

print(f"\nSCORE: {passed}/{total}")
