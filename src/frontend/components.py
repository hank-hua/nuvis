"""Reusable Streamlit UI components."""

import numpy as np
import streamlit as st
from numpy.typing import NDArray

from backend.defaults import VARIABLE_LIST, VARIABLE_SETTINGS
from backend.parameter import ParameterSet
from frontend.session import (
    get_pars_from_session,
    get_session_state,
    update_pars_in_session,
)


def parameter_setter():
    """
    A Streamlit component for setting oscillation parameters in the session state.
    """

    pars = get_pars_from_session()

    with st.expander("Set parameters"):
        cols = st.columns(6)
        for i, key in enumerate(pars.to_dict().keys()):
            with cols[i % 6]:
                parameter_input(key, label=key, format="%g")


def parameter_input(key: str, label: str, format: str = "%g", **kwargs):
    """
    A Streamlit component for setting a single parameter in the session state.
    """
    session_state = get_session_state()
    value = session_state.get(key, 0.0)
    new_value = st.number_input(label, value=value, format=format, **kwargs)
    if new_value != value:
        session_state[key] = new_value


def parameter_range_setter(
    default_var: str,
    orientation: str = "horizontal",
    key_prefix: str = "",
    use_default_range: bool = False,
) -> tuple[str, NDArray[np.float64]]:
    """
    A Streamlit component for generating an array of parameter values based on a range specified by the user.
    """
    if default_var not in VARIABLE_SETTINGS:
        raise ValueError(
            f"Default variable '{default_var}' is not in VARIABLE_SETTINGS."
        )
    var = VARIABLE_SETTINGS[default_var]
    if use_default_range:
        var_min = var.default_low
        var_max = var.default_high
    else:
        var_min = var.min_value
        var_max = var.max_value
    var_steps = var.num_steps
    var_scale = var.scale

    if orientation == "horizontal":
        cols = st.columns(5)
        with cols[0]:
            param_name = st.selectbox(
                "Parameter name",
                options=VARIABLE_LIST,
                index=VARIABLE_LIST.index(default_var),
                key=f"{key_prefix}param_name",
            )
        with cols[1]:
            min_value = st.number_input(
                "Min", value=var_min, format="%g", key=f"{key_prefix}min_value"
            )
        with cols[2]:
            max_value = st.number_input(
                "Max", value=var_max, format="%g", key=f"{key_prefix}max_value"
            )
        with cols[3]:
            num_steps = st.number_input(
                "No. steps",
                value=var_steps,
                min_value=2,
                key=f"{key_prefix}num_steps",
            )
        with cols[4]:
            scale = st.selectbox(
                "Scale",
                options=["linear", "log"],
                index=["linear", "log"].index(var_scale),
                key=f"{key_prefix}scale",
            )
    else:
        param_name = st.selectbox(
            "Parameter name",
            options=VARIABLE_LIST,
            index=VARIABLE_LIST.index(default_var),
            key=f"{key_prefix}param_name",
        )
        min_value = st.number_input(
            "Min", value=var_min, format="%g", key=f"{key_prefix}min_value"
        )
        max_value = st.number_input(
            "Max", value=var_max, format="%g", key=f"{key_prefix}max_value"
        )
        num_steps = st.number_input(
            "No. steps", value=var_steps, min_value=2, key=f"{key_prefix}num_steps"
        )
        scale = st.selectbox(
            "Scale",
            options=["linear", "log"],
            index=["linear", "log"].index(var_scale),
            key=f"{key_prefix}scale",
        )

    values: NDArray[np.float64]
    if scale == "linear":
        values = np.linspace(min_value, max_value, int(num_steps))
    else:
        if min_value <= 0 or max_value <= 0:
            _ = st.error("Log scale requires positive min and max values.")
            values = np.array([], dtype=np.float64)
        else:
            values = np.geomspace(min_value, max_value, int(num_steps))

    return param_name, values
