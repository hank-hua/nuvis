from pathlib import Path

import streamlit as st

ABOUT_PATH = Path(__file__).resolve().parent / "content" / "about.md"

st.header("About")
st.markdown(ABOUT_PATH.read_text(encoding="utf-8"))
