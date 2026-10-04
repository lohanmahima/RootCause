import streamlit as st
import random
import uuid
import datetime
from core.gym_bank import GYM_BANK
from core.gym_checker import check_answer, check_answer_advanced
from core.xp import save_workout, get_progress, get_topic_mastery
from ui.components import load_css, render_navbar, render_footer, card, badge

load_css()
render_navbar()

st.markdown("""
<style>
/* Base watercolor variables added here safely */
:root {
  --ink: #0E1319;
  --slate: #1B2430;
  --mist: #8FA3B5;
  --mist-deep: #5F7487;
  --cream: #F3EBDD;
  --parchment: #E3D5BD;
  --ember: #C8622B;
  --ember-soft: #E08A52;
  --moss: #8A8450;
  --forest: #2F3A2E;
  --clay: #B4513D;
}
.gym-card {
    background: rgba(27,36,48,0.62);
    backdrop-filter: blur(14px);
    border: 1px solid rgba(243,235,221,0.14);
    border-radius: 18px;
    padding: 28px;
    box-shadow: 0 10px 40px rgba(0,0,0,0.25);
    margin-bottom: 2rem;
}
.badge-diff {
    background: rgba(143,163,181,0.2);
    color: var(--mist);
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}
</style>
""", unsafe_allow_html=True)

# State init
if "gym_active" not in st.session_state:
    st.session_state.gym_active = False

def start_workout():
    st.session_state.gym_active = True
    st.session_state.gym_exercises = random.sample(GYM_BANK, min(5, len(GYM_BANK)))
    st.session_state.gym_idx = 0
    st.session_state.gym_hints = 0
    st.session_state.gym_attempts = 0
    st.session_state.gym_feedback = None
    st.session_state.gym_xp = 0
    st.session_state.gym_score = 0
    st.session_state.gym_results = []
    st.session_state.gym_saved = False
    st.rerun()

def submit_answer(answer):
    ex = st.session_state.gym_exercises[st.session_state.gym_idx]
    
    with st.spinner("Analyzing your answer..."):
        is_correct, judgment = check_answer_advanced(ex, answer)
        
    st.session_state.gym_attempts += 1
    
    xp_base = {"warmup": 5, "easy": 10, "medium": 20, "hard": 35}.get(ex["difficulty"], 10)
    hint_penalty = xp_base * 0.3 * st.session_state.gym_hints
    xp_earned = max(int(xp_base * 0.3), int(xp_base - hint_penalty))
    
    if is_correct and st.session_state.gym_attempts == 1:
        xp_earned += 5
        
    if is_correct or st.session_state.gym_attempts >= 2:
        explanation = ex["explanation"]
        trick = ex["thinking_trick"]
        if judgment:
            explanation = judgment.get("feedback", explanation)
            trick = judgment.get("thinking_trick", trick)
            
        st.session_state.gym_feedback = {
            "correct": is_correct,
            "explanation": explanation,
            "trick": trick,
            "xp": xp_earned if is_correct else 0
        }
        if is_correct:
            st.session_state.gym_xp += xp_earned
            st.session_state.gym_score += 1
            
        st.session_state.gym_results.append({
            "id": str(uuid.uuid4()),
            "exercise_id": ex["id"],
            "type": ex["type"],
            "topic": ex["topic"],
            "difficulty": ex["difficulty"],
            "correct": is_correct,
            "hints_used": st.session_state.gym_hints,
            "attempts": st.session_state.gym_attempts,
            "answer": str(answer)
        })
    else:
        st.session_state.gym_feedback = {"correct": False, "retry_msg": "Not quite. Take one more look, then try again."}


def next_ex():
    st.session_state.gym_idx += 1
    st.session_state.gym_hints = 0
    st.session_state.gym_attempts = 0
    st.session_state.gym_feedback = None
    st.rerun()

def use_hint():
    ex = st.session_state.gym_exercises[st.session_state.gym_idx]
    if st.session_state.gym_hints < len(ex["hints"]):
        st.session_state.gym_hints += 1

if not st.session_state.gym_active:
    st.title("Logic Gym")
    st.caption("Train how you think.")
    
    xp, streak, lvl_num, lvl_name, next_xp = get_progress()
    c1, c2, c3 = st.columns(3)
    with c1:
        pct = min(100, (xp / max(1, next_xp)) * 100)
        st.markdown(f"<div class='gym-card' style='padding: 1.5rem;'><h4 style='margin:0 0 0.5rem 0;'>Level {lvl_num}: {lvl_name}</h4><div style='background:rgba(255,255,255,0.1); height:4px; border-radius:2px;'><div style='background:var(--ember); width:{pct}%; height:100%; border-radius:2px;'></div></div><div style='font-size:0.8rem; margin-top:0.5rem; color:var(--parchment);'>{xp} / {next_xp} XP</div></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='gym-card' style='padding: 1.5rem; text-align:center;'><h3 style='margin:0; font-family:Fraunces; font-size:2.5rem;'>{streak}</h3><div style='font-size:0.75rem; letter-spacing:0.1em; color:var(--parchment);'>DAY STREAK</div></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div class='gym-card' style='padding: 1.5rem; text-align:center;'><h3 style='margin:0; font-family:Fraunces; font-size:2.5rem;'>1</h3><div style='font-size:0.75rem; letter-spacing:0.1em; color:var(--parchment);'>WORKOUTS TODAY</div></div>", unsafe_allow_html=True)
        
    st.markdown("### Start a workout")
    if st.button("Quick Workout (5 mixed exercises)", type="primary"):
        start_workout()
        
    st.markdown("### Topic Mastery")
    mastery = get_topic_mastery()
    if mastery:
        for t, m in mastery.items():
            st.markdown(f"**{t}** {m}%")
            st.progress(m / 100)
    else:
        st.info("Complete some workouts to see your topic mastery!")
        
else:
    if st.session_state.gym_idx >= len(st.session_state.gym_exercises):
        # Save workout logic
        if not getattr(st.session_state, "gym_saved", False):
            date_str = datetime.datetime.now().strftime("%Y-%m-%d")
            save_workout(str(uuid.uuid4()), date_str, "Quick Workout", st.session_state.gym_score, len(st.session_state.gym_exercises), st.session_state.gym_xp, st.session_state.gym_results)
            st.session_state.gym_saved = True
            
        st.subheader("Workout done. Your roots go a little deeper.")
        st.markdown(f"**Score:** {st.session_state.gym_score} / {len(st.session_state.gym_exercises)}")
        st.markdown(f"**Total XP Earned:** {st.session_state.gym_xp}")
        if st.button("Back to Gym Home", type="primary"):
            st.session_state.gym_active = False
            st.session_state.gym_saved = False
            st.rerun()
    else:
        ex = st.session_state.gym_exercises[st.session_state.gym_idx]
        st.markdown(f"**Exercise {st.session_state.gym_idx + 1} of {len(st.session_state.gym_exercises)}**")
        
        st.markdown('<div class="gym-card">', unsafe_allow_html=True)
        st.markdown(f'<span class="badge-diff">{ex["difficulty"]}</span> <span style="color:#C8622B; margin-left:8px; font-size:0.8rem; text-transform:uppercase;">{ex["topic"]}</span>', unsafe_allow_html=True)
        st.markdown(f"### {ex['prompt']}")
        
        if ex["code"]:
            st.code(ex["code"], language=ex.get("language", "python"))
            
        feedback = st.session_state.gym_feedback
        done = feedback is not None and "explanation" in feedback
        
        if not done:
            ans = st.text_input("Your answer:", key=f"ans_{ex['id']}_{st.session_state.gym_attempts}")
            
            c1, c2 = st.columns([1, 4])
            with c1:
                if st.button("Submit Answer", type="primary", disabled=not ans):
                    submit_answer(ans)
                    st.rerun()
            with c2:
                if st.button(f"Hint ({st.session_state.gym_hints}/{len(ex['hints'])})", disabled=st.session_state.gym_hints >= len(ex["hints"])):
                    use_hint()
                    st.rerun()
                    
            for i in range(st.session_state.gym_hints):
                st.info(f"**Hint {i+1}:** {ex['hints'][i]}")
                
            if feedback and not feedback.get("correct"):
                st.warning(feedback["retry_msg"])
                
        else:
            if feedback["correct"]:
                st.success("That's it. Here's why it works.")
            else:
                st.error("Let's walk through it together.")
                
            st.markdown(f"**Explanation:** {feedback['explanation']}")
            st.markdown(f"**Thinking Trick:** {feedback['trick']}")
            st.markdown(f"**XP Earned:** +{feedback['xp']}")
            
            if st.button("Next Exercise →", type="primary"):
                next_ex()
        
        st.markdown('</div>', unsafe_allow_html=True)

render_footer()
