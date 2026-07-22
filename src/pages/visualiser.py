import streamlit as st

from frontend.components import parameter_setter
from frontend.probability_views import render_1d, render_2d, render_biprob

st.set_page_config(
    page_title="Probability Visualiser",
    layout="wide",
)

st.title("Probability Visualiser")
parameter_setter()

tab_1d, tab_2d, tab_biprob = st.tabs(
    ["1D probabilities", "2D probabilities", "Bi-probability"]
)

with tab_1d:
    render_1d()

with tab_2d:
    render_2d()

with tab_biprob:
    render_biprob()
