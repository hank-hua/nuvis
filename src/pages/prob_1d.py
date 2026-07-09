import numpy as np
import streamlit as st

from frontend.components import parameter_setter
from frontend.plotter import Plotter
from frontend.session import get_pars_from_session

st.set_page_config(
    page_title="1D Probability Visualiser",
    layout="wide",
)

st.write("1D probability visualiser.")

parameter_setter()

# --- Plot configuration -----------------------------------------------------

ENERGY_MIN_GEV = 0.0
ENERGY_MAX_GEV = 10.0
ENERGY_STEPS = 100
DELTA_STEPS = 100

PLOT_CONFIG = dict(
    x_var="E",
    y_var="mu_e",
    x_label="Energy (GeV)",
    y_label="P(ν_μ→ν_e)",
    title="Muon Neutrino Survival Probability",
    line_color="blue",
    line_width=2,
)

# --- Plotting ---------------------------------------------------------------

x_values = np.linspace(ENERGY_MIN_GEV, ENERGY_MAX_GEV, ENERGY_STEPS)
animate_values = np.linspace(-np.pi, np.pi, DELTA_STEPS)

plotter = Plotter(pars=get_pars_from_session())

plotter.animate(
    plot_method="1d",
    animate_var="delta",
    animate_values=animate_values,
    x_values=x_values,
    **PLOT_CONFIG,
)
plotter.show()
