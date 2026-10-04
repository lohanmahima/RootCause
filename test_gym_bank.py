from core.gym_bank import GYM_BANK
from core.gym_checker import check_answer

def run_tests():
    passed = 0
    total = len(GYM_BANK)
    print(f"Running tests on {total} exercises in the Gym Bank...")
    
    for ex in GYM_BANK:
        # Test with the exact correct answer provided in the bank
        is_correct = check_answer(ex, ex["answer"])
        if is_correct:
            passed += 1
        else:
            print(f"Failed test for {ex['id']}. Type: {ex['type']}")
            print(f"Expected: {ex['answer']}, but check_answer returned False")
            
    print(f"\nSCORE: {passed}/{total}")
    return passed == total

if __name__ == "__main__":
    success = run_tests()
    if not success:
        exit(1)
