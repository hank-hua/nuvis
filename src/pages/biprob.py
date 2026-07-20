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

t_var, t_values = parameter_range_setter(
    "delta",
    key_prefix="biprob_val_",
    use_default_range=True,
    override={"num_steps": 20},
)

do_animate = st.checkbox("Animate", value=True)

col1, col2 = st.columns(2)
with col1:
    x_chan = osc_channel_selector(default_channel="mu_e", single=True)[0]
    x_chan_pretty = COLUMN_TO_PRETTY.get(x_chan, x_chan)
with col2:
    y_chan = osc_channel_selector(default_channel="anti_mu_e", single=True)[0]
    y_chan_pretty = COLUMN_TO_PRETTY.get(y_chan, y_chan)

# --- Plot configuration -----------------------------------------------------

PLOT_CONFIG = dict(
    t_values=t_values,
    t_var=t_var,
    x_var=x_chan,
    y_var=y_chan,
    x_label=x_chan_pretty,
    y_label=y_chan_pretty,
    title=f"Bi-probability plot: {x_chan_pretty} vs {y_chan_pretty}",
)

# --- Plotting ---------------------------------------------------------------

plotter = Plotter(pars=get_pars_from_session())

if do_animate:
    freeze_axes = st.checkbox("Freeze axes", value=False)
    anim_var, anim_values = parameter_range_setter(
        "E", key_prefix="1d_anim_", use_default_range=True, override={"num_steps": 20}
    )
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
plotter.show()
