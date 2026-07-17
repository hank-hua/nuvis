import numpy as np
import streamlit as st

from backend.defaults import COLUMN_TO_PRETTY
from frontend.components import (
    osc_channel_selector,
    parameter_range_setter,
    parameter_setter,
)
from frontend.plotter import Plotter
from frontend.session import get_pars_from_session

st.set_page_config(
    page_title="2D Probability Visualiser",
    layout="wide",
)

st.write("2D probability visualiser.")

parameter_setter()

x_var, x_values = parameter_range_setter(
    "s23sq", key_prefix="2d_x_", use_default_range=True
)

y_var, y_values = parameter_range_setter(
    "delta", key_prefix="2d_y_", use_default_range=True
)

do_animate = st.checkbox("Animate", value=False)

osc_chan = osc_channel_selector(single=True)[0]
osc_chan_pretty = COLUMN_TO_PRETTY.get(osc_chan, osc_chan)

# --- Plot configuration -----------------------------------------------------

PLOT_CONFIG = dict(
    x_var=x_var,
    y_var=y_var,
    z_var=osc_chan,
    x_label=x_var,
    y_label=y_var,
    title=osc_chan_pretty,
)

# --- Plotting ---------------------------------------------------------------

plotter = Plotter(pars=get_pars_from_session())

if do_animate:
    anim_var, anim_values = parameter_range_setter(
        "E", key_prefix="2d_anim_", use_default_range=True, override={"num_steps": 10}
    )
    plotter.animate(
        plot_method="2d",
        animate_var=anim_var,
        animate_values=anim_values,
        x_values=x_values,
        y_values=y_values,
        **PLOT_CONFIG,
    )
else:
    plotter.make_2d(x_values=x_values, y_values=y_values, **PLOT_CONFIG)

plotter.show()
