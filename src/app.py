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
