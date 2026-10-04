import streamlit as st

def load_css():
    """Load the global CSS."""
    with open("ui/theme.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def render_navbar():
    """Render the top navbar using columns and page links."""
    st.markdown("""
        <style>
        .nav-logo {
            font-weight: 800;
            font-size: 1.5rem;
            color: white;
            background: linear-gradient(90deg, #d8b4fe 0%, #c084fc 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-top: 5px;
        }
        .status-pill {
            background: rgba(0, 255, 0, 0.1);
            color: #4ade80;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: bold;
            display: inline-block;
            margin-top: 10px;
        }
        hr.nav-divider {
            margin-top: 0.5rem;
            margin-bottom: 2rem;
            border-color: rgba(255,255,255,0.1);
        }
        </style>
    """, unsafe_allow_html=True)
    
    cols = st.columns([2.5, 1, 1, 1.2, 1, 1.5, 1.5])
    
    with cols[0]:
        st.markdown('<div class="nav-logo">🧠 RootCause</div>', unsafe_allow_html=True)
    with cols[1]:
        st.page_link("pages/home.py", label="Home")
    with cols[2]:
        st.page_link("pages/solve.py", label="Solve")
    with cols[3]:
        st.page_link("pages/gym.py", label="Logic Gym")
    with cols[4]:
        st.page_link("pages/memory.py", label="Memory")
    with cols[5]:
        st.session_state.learning_mode = st.toggle("Learning Mode", value=st.session_state.get('learning_mode', True), key="nav_lm")
    with cols[6]:
        # Mocking the ready status. Could add a check to Ollama later.
        st.markdown('<div class="status-pill">🟢 Model ready</div>', unsafe_allow_html=True)

    st.markdown('<hr class="nav-divider">', unsafe_allow_html=True)

def render_footer():
    """Render the global footer."""
    st.markdown("""
        <div style="text-align: center; margin-top: 4rem; padding: 2rem 0; border-top: 1px solid rgba(255,255,255,0.1); color: #888; font-size: 0.9rem;">
            <p>Built for Ojju 💜 &middot; Runs 100% locally on open-source Gemma &middot; Your data never leaves your laptop</p>
        </div>
    """, unsafe_allow_html=True)
    
    # About page link using native st.page_link for routing safety
    col1, col2, col3 = st.columns([4, 1, 4])
    with col2:
        st.page_link("pages/about.py", label="About RootCause")

def card(title, content):
    st.markdown(f"""
    <div class="rc-card">
        <h3 style="margin-top: 0; font-size: 1.2rem;">{title}</h3>
        <p style="color: #ddd; margin-bottom: 0;">{content}</p>
    </div>
    """, unsafe_allow_html=True)

def stat_tile(label, value):
    st.markdown(f"""
    <div class="rc-stat">
        <div class="rc-stat-value">{value}</div>
        <div class="rc-stat-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)

def badge(text):
    st.markdown(f'<div class="rc-badge">{text}</div>', unsafe_allow_html=True)
