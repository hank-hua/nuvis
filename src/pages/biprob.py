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
    page_title="Bi-probability Visualiser",
    layout="wide",
)

st.write("Bi-probability visualiser.")

parameter_setter()

col1, col2 = st.columns([1, 3])
with col1:
    x_chan = osc_channel_selector(default_channel="mu_e", single=True)[0]
    x_chan_pretty = COLUMN_TO_PRETTY.get(x_chan, x_chan)
    y_chan = osc_channel_selector(default_channel="anti_mu_e", single=True)[0]
    y_chan_pretty = COLUMN_TO_PRETTY.get(y_chan, y_chan)

    t_var, t_values = parameter_range_setter(
        "delta",
        key_prefix="biprob_val_",
        use_default_range=True,
        override={"num_steps": 20},
        expander_label="Ellipse parameter",
        expanded=True,
        orientation="vertical",
    )

    with st.popover("Animation settings"):
        do_animate = st.checkbox("Animate", value=True)
        freeze_axes = st.checkbox("Freeze axes", value=False)
        anim_var, anim_values = parameter_range_setter(
            "E",
            key_prefix="biprob_anim_",
            use_default_range=True,
            override={"num_steps": 20},
        )

    with st.popover("Overlay settings"):
        do_overlay = st.checkbox("Overlay", value=False)
        overlay_var, overlay_values = parameter_range_setter(
            "s23sq",
            key_prefix="biprob_overlay_",
            use_default_range=True,
            override={"num_steps": 5},
        )

if do_overlay and overlay_var == t_var:
    st.error("Overlay and ellipse parameters must be different.")
    st.stop()
if do_overlay and overlay_var == "dmsq31":
    st.error("dmsq31 is already represented by the NO/IO line style.")
    st.stop()
if do_animate and anim_var in {t_var, overlay_var if do_overlay else None}:
    st.error("Animation, overlay, and ellipse parameters must be different.")
    st.stop()

# --- Plot configuration -----------------------------------------------------

PLOT_CONFIG = dict(
    t_values=t_values,
    t_var=t_var,
    x_var=x_chan,
    y_var=y_chan,
    x_label=x_chan_pretty,
    y_label=y_chan_pretty,
    title=f"Bi-probability plot: {x_chan_pretty} vs {y_chan_pretty}",
    overlay_var=overlay_var if do_overlay else None,
    overlay_values=overlay_values if do_overlay else None,
    show_dcp_markers=t_var == "delta",
)

# --- Plotting ---------------------------------------------------------------

plotter = Plotter(pars=get_pars_from_session())

if do_animate:
    plotter.animate(
        plot_method="biprob",
        animate_var=anim_var,
        animate_values=anim_values,
        freeze_axes=freeze_axes,
        **PLOT_CONFIG,
    )
else:
    plotter.make_biprob(
        **PLOT_CONFIG,
    )
with col2:
    plotter.show()
