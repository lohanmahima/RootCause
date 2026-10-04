import json

def check_answer(exercise, user_answer):
    """
    Check if the user answer is correct for the given exercise.
    This is a simple stub implementation for Step 1.
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
        # Simple rubric check for text answers
        if exercise.get("rubric"):
            user_text = str(user_answer).lower()
            return any(keyword.lower() in user_text for keyword in exercise["rubric"])
        else:
            return str(user_answer).strip().lower() == str(correct_answer).strip().lower()
            
    return False
