import streamlit as st
from ui.components import load_css, render_navbar, render_footer, card, stat_tile

load_css()
render_navbar()

# Hero Section
st.markdown(
    """
<div style="text-align: center; margin: 4rem 0;">
    <h1 style="font-size: clamp(2.6rem, 6vw, 4.5rem) !important; margin-bottom: 0.5rem; font-family: 'Fraunces', serif; font-weight: 500; color: var(--cream);">
        Don't rely on AI.<br>Use AI to learn how to <i style="color: var(--ember); font-style: italic;">think</i>.
    </h1>
    <p style="font-size: 1.2rem; color: var(--parchment); max-width: 600px; margin: 0 auto 2rem auto;">
        RootCause doesn't hand you the answer. It finds out why you got stuck, and guides you back to the path, one step at a time.
    </p>
</div>
""",
    unsafe_allow_html=True,
)

# Buttons
st.markdown(
    """
<style>
.hero-buttons {
    display: flex;
    justify-content: center;
    gap: 1rem;
    margin-bottom: 4rem;
}
</style>
""",
    unsafe_allow_html=True,
)

col1, col2, col3, col4 = st.columns([1, 1.5, 1.5, 1])
with col2:
    if st.button("Start solving", type="primary", use_container_width=True):
        st.switch_page("pages/solve.py")
with col3:
    if st.button("Try a sample problem", use_container_width=True):
        st.session_state["load_sample"] = True
        st.switch_page("pages/solve.py")

st.markdown("<br><br>", unsafe_allow_html=True)

# How it works section
st.subheader("How it works")
hw_col1, hw_col2, hw_col3, hw_col4 = st.columns(4)
with hw_col1:
    card("1. Think first", "Explain your approach before writing code.")
with hw_col2:
    card("2. Attempt", "Paste your broken code and error message.")
with hw_col3:
    card("3. Diagnosis", "We find your exact conceptual gap.")
with hw_col4:
    card("4. Hints & retry", "Get Socratic hints and practice exercises.")

st.markdown("<br>", unsafe_allow_html=True)

# Why RootCause section
st.subheader("Why RootCause")
wr_col1, wr_col2, wr_col3 = st.columns(3)
with wr_col1:
    card(
        "Finds WHY you're stuck",
        "Identifies if it's a logic, concept, or edge-case gap.",
    )
with wr_col2:
    card(
        "Never gives the answer",
        "Builds your coding muscles instead of doing the work for you.",
    )
with wr_col3:
    card(
        "Remembers weak spots",
        "Tracks your progress so you can practice what you're bad at.",
    )

st.markdown("<br>", unsafe_allow_html=True)

# Stats row
st.subheader("Your Progress")
# In the future, this will be loaded from SQLite
sessions_done = 0
streak = 0
top_weak_spot = "No sessions yet"

stat_col1, stat_col2, stat_col3 = st.columns(3)
with stat_col1:
    stat_tile("Sessions Done", str(sessions_done))
with stat_col2:
    stat_tile("Day Streak", str(streak))
with stat_col3:
    stat_tile("Top Weak Spot", top_weak_spot)

st.markdown("<br>", unsafe_allow_html=True)

# Why open source strip
st.markdown(
    """
<div class="rc-card" style="text-align: center; margin-top: 2rem;">
    <h3 style="color: var(--mist); margin-top: 0;">Built on Open Source</h3>
    <p style="color: var(--parchment); font-size: 1.1rem; margin-bottom: 0;">
        100% Private &middot; Offline Capable &middot; Free &middot; Powered by swappable local models like Gemma and  via Ollama.
    </p>
</div>
""",
    unsafe_allow_html=True,
)

render_footer()
