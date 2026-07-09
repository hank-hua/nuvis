import numpy as np
import streamlit as st

from frontend.components import parameter_range_setter, parameter_setter
from frontend.plotter import Plotter
from frontend.session import get_pars_from_session

st.set_page_config(
    page_title="1D Probability Visualiser",
    layout="wide",
)

st.write("1D probability visualiser.")

parameter_setter()

x_var, x_values = parameter_range_setter("E", key_prefix="1d_x_")

do_animate = st.checkbox("Animate", value=True)

# --- Plot configuration -----------------------------------------------------

PLOT_CONFIG = dict(
    x_var=x_var,
    y_var="mu_e",
    x_label=x_var,
    y_label="P(ν_μ→ν_e)",
    title="Muon Neutrino Survival Probability",
    line_color="blue",
    line_width=2,
)

# --- Plotting ---------------------------------------------------------------

plotter = Plotter(pars=get_pars_from_session())

if do_animate:
    anim_var, anim_values = parameter_range_setter(
        "delta", key_prefix="1d_anim_", use_default_range=True
    )
    plotter.animate(
        plot_method="1d",
        animate_var=anim_var,
        animate_values=anim_values,
        x_values=x_values,
        **PLOT_CONFIG,
    )
plotter.show()
