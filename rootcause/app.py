import re

import streamlit as st
from core.llm import diagnose_attempt


def is_recursion_problem(problem, code):
    context = f"{problem}\n{code}".lower()
    if "recurs" in context or "backtrack" in context:
        return True

    declaration = re.search(
        r"\b(?:def\s+|(?:void|int|long|bool|string|auto)\s+)(\w+)\s*\(",
        code,
    )
    return bool(
        declaration
        and re.search(
            rf"\b{re.escape(declaration.group(1))}\s*\(",
            code[declaration.end():],
        )
    )


st.set_page_config(page_title="RootCause", page_icon="🧠", layout="centered")

st.title("🧠 RootCause")
st.caption("Don't rely on AI. Use AI to learn how to think.")

learning_mode = st.toggle("🧠 Learning Mode", value=True)

st.subheader("1. Problem")
problem = st.text_area("Paste your problem", height=120)

st.subheader("2. Think first")
understanding = st.text_area("What is the problem asking, in your own words?", height=80)
approach = st.text_area("What's your approach? Write steps or pseudocode.", height=100)

st.subheader("3. Your attempt")
code = st.text_area("Paste your code", height=180)
error = st.text_area("Error or wrong output (if any)", height=80)

if st.button("🔍 Diagnose", type="primary", disabled=not problem.strip()):
    with st.spinner("Thinking..."):
        result = diagnose_attempt(problem, understanding, approach, code, error)

    if result is None:
        st.error("Couldn't reach the AI. Is the Ollama app running?")
    else:
        st.session_state["result"] = result

result = st.session_state.get("result")
if result:
    st.divider()
    st.subheader("💡 Think about this")
    st.info(result.guiding_question)
    if (
        result.confidence != "high"
        or (
            is_recursion_problem(problem, code)
            and result.root_cause_category
            not in {"Implementation Gap", "Edge-Case Gap", "Complexity Gap"}
        )
    ):
        st.info("I'm not fully sure about this one. Trust your own trace of the code more than my guess.")
    st.subheader("🎯 Micro exercise")
    st.write(result.micro_exercise)
    with st.expander("Show me what the AI thinks is going on (it can be wrong)"):
        st.markdown(f"**First trace:** {result.trace_first_step}")
        st.markdown(f"**Root cause:** {result.root_cause_category}")
        st.write(result.root_cause_explanation)
        st.markdown(f"**Evidence:** `{result.evidence}`")
        st.markdown(f"**Concept:** {result.missing_concept}")
    st.success(result.retry_recommendation)