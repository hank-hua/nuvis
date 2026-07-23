import streamlit as st

from frontend.components import parameter_setter
from frontend.probability_views import (
    render_1d,
    render_2d,
    render_biprob,
    reserved_1d_parameters,
    reserved_2d_parameters,
    reserved_biprob_parameters,
)

st.set_page_config(
    page_title="Probability Visualiser",
    layout="wide",
)

st.title("Probability Visualiser")

view = st.segmented_control(
    "Visualisation",
    options=["1D probabilities", "2D probabilities", "Bi-probability"],
    default="1D probabilities",
    key="probability_view",
)

reserved_parameters = {
    "1D probabilities": reserved_1d_parameters,
    "2D probabilities": reserved_2d_parameters,
    "Bi-probability": reserved_biprob_parameters,
}[view]()
parameter_setter(disabled_parameters=reserved_parameters)

if view == "1D probabilities":
    render_1d()
elif view == "2D probabilities":
    render_2d()
else:
    render_biprob()
