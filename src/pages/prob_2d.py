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

col1, col2 = st.columns(2)
with col1:
    do_animate = st.checkbox("Animate", value=False)
with col2:
    do_overlay = st.checkbox("Overlay", value=False)

osc_chan = osc_channel_selector(single=True)[0]
osc_chan_pretty = COLUMN_TO_PRETTY.get(osc_chan, osc_chan)

overlay_var = overlay_values = None
if do_overlay:
    overlay_var, overlay_values = parameter_range_setter(
        "s13sq",
        key_prefix="2d_overlay_",
        use_default_range=True,
        override={"num_steps": 3},
    )
    if overlay_var in {x_var, y_var}:
        st.error("Overlay and axis parameters must be different.")
        st.stop()


# --- Plot configuration -----------------------------------------------------

PLOT_CONFIG = dict(
    x_values=x_values,
    y_values=y_values,
    x_var=x_var,
    y_var=y_var,
    z_var=osc_chan,
    x_label=x_var,
    y_label=y_var,
    title=osc_chan_pretty,
    ncontours=3,
    overlay_var=overlay_var,
    overlay_values=overlay_values,
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
        **PLOT_CONFIG,
    )
else:
    plotter.make_2d(**PLOT_CONFIG)

plotter.show()
