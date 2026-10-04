from core.prompts import DIAGNOSIS_PROMPT
from core.llm import diagnose, build_input


student_input = build_input(
    problem="Write a function that returns the sum of all numbers in a list.",
    understanding="I need to add up every number in the list.",
    approach="Loop through the list and keep adding to a total.",
    code=(
        "def total(nums):\n"
        "    s = 0\n"
        "    for i in range(1, len(nums)):\n"
        "        s += nums[i]\n"
        "    return s"
    ),
    error="total([5, 2, 3]) returned 5 but expected 10",
)


result = diagnose(DIAGNOSIS_PROMPT, student_input)


if result:
    print("REASONING:", result.plan_is_sound, "|", result.bug_is_in)
    print("CATEGORY:", result.root_cause_category)
    print("WHY:", result.root_cause_explanation)
    print("EVIDENCE:", result.evidence)
    print("CONCEPT:", result.missing_concept)
    print("THINK:", result.guiding_question)
    print("EXERCISE:", result.micro_exercise)
    print("TAG:", result.concept_tag)
    print("CONFIDENCE:", result.confidence)
    print("RETRY:", result.retry_recommendation)

else:
    print("Diagnosis failed. Is Ollama running?")