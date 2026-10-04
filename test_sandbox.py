from core.gym_checker import verify_exercise_output, run_sandboxed
from core.gym_bank import GYM_BANK

passed = 0
total_predict = 0
for ex in GYM_BANK:
    if ex["type"] == "predict":
        total_predict += 1
        if verify_exercise_output(ex):
            passed += 1
        else:
            actual = run_sandboxed(ex["code"])
            print(f"Sandbox failed for {ex['id']}. Claimed answer: {ex['answer']}. Actual output: {actual}")

print(f"Sandbox verify predict score: {passed}/{total_predict}")
