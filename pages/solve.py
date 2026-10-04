import streamlit as st
import time
from core.llm import diagnose_attempt
from ui.components import load_css, render_navbar, render_footer, card, badge

load_css()
render_navbar()

# Initialize state
if "solve_step" not in st.session_state:
    st.session_state.solve_step = 1
if "problem_text" not in st.session_state:
    st.session_state.problem_text = ""
if "lang" not in st.session_state:
    st.session_state.lang = "Python"
if "understanding" not in st.session_state:
    st.session_state.understanding = ""
if "approach" not in st.session_state:
    st.session_state.approach = ""
if "code_attempt" not in st.session_state:
    st.session_state.code_attempt = ""
if "error_msg" not in st.session_state:
    st.session_state.error_msg = ""
if "diagnosis_result" not in st.session_state:
    st.session_state.diagnosis_result = None
if "hint_level" not in st.session_state:
    st.session_state.hint_level = 0
if "practice_answer" not in st.session_state:
    st.session_state.practice_answer = ""
if "practice_checked" not in st.session_state:
    st.session_state.practice_checked = False

# Handle Load Sample from home page
if st.session_state.get("load_sample"):
    st.session_state.problem_text = "Return the largest number in a list."
    st.session_state.understanding = "Find the biggest value."
    st.session_state.approach = "Keep a maximum and compare every value."
    st.session_state.code_attempt = "m = 0\nfor x in nums:\n  if x > m:\n    m = x\nreturn m"
    st.session_state.error_msg = "[-5, -2, -8] gives 0"
    st.session_state.solve_step = 1
    st.session_state.load_sample = False

def next_step():
    st.session_state.solve_step += 1

def prev_step():
    st.session_state.solve_step -= 1

def clear_all():
    for key in ["solve_step", "problem_text", "understanding", "approach", "code_attempt", 
                "error_msg", "diagnosis_result", "hint_level", "practice_answer", "practice_checked"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

# Top bar buttons
col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 4])
with col1:
    if st.button("New Problem"):
        clear_all()
with col2:
    if st.button("Load Sample"):
        st.session_state.load_sample = True
        st.rerun()
with col3:
    if st.button("Clear All"):
        clear_all()
with col4:
    st.button("Save Session", disabled=True) # Mock for now

st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin: 1rem 0;'>", unsafe_allow_html=True)

# Progress Stepper UI
steps = ["Problem", "Think", "Attempt", "Diagnosis", "Hints", "Practice", "Retry"]
stepper_html = "<div style='display: flex; justify-content: space-between; margin-bottom: 2rem;'>"
for i, name in enumerate(steps, 1):
    color = "#d8b4fe" if i == st.session_state.solve_step else ("#4ade80" if i < st.session_state.solve_step else "#555")
    weight = "bold" if i == st.session_state.solve_step else "normal"
    stepper_html += f"<div style='color: {color}; font-weight: {weight}; font-size: 0.9rem;'>{i}. {name}</div>"
stepper_html += "</div>"
st.markdown(stepper_html, unsafe_allow_html=True)


step = st.session_state.solve_step

if step == 1:
    st.subheader("1. What's the problem?")
    st.session_state.problem_text = st.text_area("Paste your problem description here", value=st.session_state.problem_text, height=150)
    st.session_state.lang = st.selectbox("Language", ["Python", "JavaScript", "C++", "Java", "Other"], index=["Python", "JavaScript", "C++", "Java", "Other"].index(st.session_state.lang) if st.session_state.lang in ["Python", "JavaScript", "C++", "Java", "Other"] else 0)
    
    if st.button("Continue →", type="primary", disabled=not st.session_state.problem_text.strip()):
        next_step()
        st.rerun()

elif step == 2:
    st.subheader("2. Think first")
    st.markdown("Don't write code yet. Explain your logic.")
    st.session_state.understanding = st.text_area("What is the problem asking, in your own words?", value=st.session_state.understanding, height=100)
    st.session_state.approach = st.text_area("What's your approach? Write steps or pseudocode.", value=st.session_state.approach, height=150)
    
    c1, c2, _ = st.columns([1, 1, 4])
    with c1:
        if st.button("← Back"):
            prev_step()
            st.rerun()
    with c2:
        if st.button("Continue →", type="primary"):
            next_step()
            st.rerun()

elif step == 3:
    st.subheader("3. Your attempt")
    st.session_state.code_attempt = st.text_area("Paste your code", value=st.session_state.code_attempt, height=200)
    st.session_state.error_msg = st.text_area("Error message or wrong output (if any)", value=st.session_state.error_msg, height=100)
    
    c1, c2, _ = st.columns([1, 2, 3])
    with c1:
        if st.button("← Back"):
            prev_step()
            st.rerun()
    with c2:
        if st.button("🧠 Find My Root Cause", type="primary", disabled=not st.session_state.code_attempt.strip()):
            with st.spinner("Thinking like a mentor... diagnosing your logic..."):
                try:
                    res = diagnose_attempt(
                        st.session_state.problem_text, 
                        st.session_state.understanding, 
                        st.session_state.approach, 
                        st.session_state.code_attempt, 
                        st.session_state.error_msg
                    )
                    if res:
                        st.session_state.diagnosis_result = res
                        next_step()
                        st.rerun()
                    else:
                        st.toast("Error: Couldn't reach the AI. Is Ollama running?", icon="🔴")
                except Exception as e:
                    st.toast(f"An error occurred while calling the model.", icon="🔴")

elif step == 4:
    res = st.session_state.diagnosis_result
    st.subheader("4. Diagnosis")
    
    badge(res.root_cause_category)
    st.markdown(f"### {res.root_cause_explanation}")
    st.markdown(f"**Evidence from your attempt:** `{res.evidence}`")
    
    st.info("I've found where you got stuck. Ready for a hint?")
    
    if st.button("Show Hint 1 →", type="primary"):
        st.session_state.hint_level = 1
        next_step()
        st.rerun()

elif step == 5:
    res = st.session_state.diagnosis_result
    st.subheader("5. Socratic Hints")
    
    if st.session_state.hint_level >= 1:
        st.markdown("#### Hint 1: The Guiding Question")
        st.info(res.guiding_question)
    
    if st.session_state.hint_level >= 2:
        st.markdown("#### Hint 2: The Missing Concept")
        st.warning(res.missing_concept)
        
    c1, c2 = st.columns(2)
    with c1:
        if st.session_state.hint_level < 2:
            if st.button("I need another hint"):
                st.session_state.hint_level += 1
                st.rerun()
    with c2:
        if st.button("I got it, give me practice →", type="primary"):
            next_step()
            st.rerun()

elif step == 6:
    res = st.session_state.diagnosis_result
    st.subheader("6. Practice")
    card("Micro-Exercise", res.micro_exercise)
    
    st.session_state.practice_answer = st.text_area("Your answer:")
    
    if st.button("Check My Answer"):
        st.session_state.practice_checked = True
        
    if st.session_state.practice_checked:
        st.success(f"**Mentor's Answer:** {res.micro_exercise_answer}")
        if st.button("Continue to Retry →", type="primary"):
            next_step()
            st.rerun()

elif step == 7:
    res = st.session_state.diagnosis_result
    st.subheader("7. Retry")
    
    st.success(res.retry_recommendation)
    
    st.markdown("### Session Summary")
    card("Gap Identified", f"{res.root_cause_category} ({res.concept_tag})")
    
    c1, c2 = st.columns(2)
    with c1:
        st.button("Save to My Memory", type="primary", disabled=True)
    with c2:
        if st.button("Start Another Problem"):
            clear_all()

render_footer()
