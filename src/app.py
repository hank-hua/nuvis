from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title="Neutrino probability visualiser",
    page_icon="📊",
    layout="wide",
)

pages = [
    st.Page("pages/visualiser.py", title="Visualiser", default=True),
    st.Page("pages/about.py", title="About"),
]

navigation = st.navigation(pages)
navigation.run()

HELP_PATH = Path(__file__).resolve().parent / "pages" / "content" / "help.md"


@st.dialog("Help")
def help_popup() -> None:
    st.markdown(HELP_PATH.read_text(encoding="utf-8"))
with st.sidebar:
    feedback = st.link_button(url="https://github.com/hank-hua/nuvis/issues", label="Feedback")
    if st.button("Help", key="help_button"):
        help_popup()
