import streamlit as st

# App entry point config
st.set_page_config(page_title="RootCause", page_icon="🧠", layout="centered")

# Inject the visual background effect

# Define multi-page routing
pages = [
    st.Page("pages/home.py", title="Home", default=True),
    st.Page("pages/solve.py", title="Solve"),
    st.Page("pages/gym.py", title="Logic Gym"),
    st.Page("pages/memory.py", title="My Memory"),
    st.Page("pages/about.py", title="About"),
]

# Use hidden navigation so we can use our custom top navbar
pg = st.navigation(pages, position="hidden")
pg.run()
