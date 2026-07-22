import numpy as np
import streamlit as st

from frontend.components import (
    osc_channel_selector,
    parameter_range_setter,
    parameter_setter,
)
from frontend.plotter import Plotter
from frontend.session import get_pars_from_session

st.set_page_config(
    page_title="1D Probability Visualiser",
    layout="wide",
)

st.write("1D probability visualiser.")

parameter_setter()

col1, col2 = st.columns([1, 3])
with col1:
    osc_chans = osc_channel_selector()
    x_var, x_values = parameter_range_setter(
        "E",
        key_prefix="1d_x_",
        expander_label="X-axis",
        expanded=True,
        orientation="vertical",
        use_default_range=True,
    )

    with st.popover(
        "Animation settings",
    ):
        do_animate = st.checkbox("Animate", value=True)
        freeze_axes = st.checkbox("Freeze axes", value=False)
        anim_var, anim_values = parameter_range_setter(
            "delta",
            key_prefix="1d_anim_",
            use_default_range=True,
        )

    with st.popover(
        "Overlay settings",
    ):
        do_overlay = st.checkbox("Overlay", value=False)
        overlay_var, overlay_values = parameter_range_setter(
            "s23sq",
            key_prefix="1d_overlay_",
            use_default_range=True,
            override={"num_steps": 5},
        )

# --- Plot configuration -----------------------------------------------------

PLOT_CONFIG = dict(
    x_var=x_var,
    x_values=x_values,
    y_vars=osc_chans,
    line_width=2,
    overlay_var=overlay_var if do_overlay else None,
    overlay_values=overlay_values if do_overlay else None,
)

# --- Plotting ---------------------------------------------------------------

plotter = Plotter(pars=get_pars_from_session())

if do_animate:
    plotter.animate(
        plot_method="1d",
        animate_var=anim_var,
        animate_values=anim_values,
        freeze_axes=freeze_axes,
        **PLOT_CONFIG,
    )
else:
    plotter.make_1d(
        **PLOT_CONFIG,
    )
with col2:
    plotter.show()
