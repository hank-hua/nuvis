from pathlib import Path

import streamlit as st

st.header("About")
README_PATH = Path(__file__).resolve().parents[2] / "README.md"
st.markdown(README_PATH.read_text(encoding="utf-8"))
