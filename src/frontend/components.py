"""Reusable Streamlit UI components."""

import numpy as np
import streamlit as st
from numpy.typing import NDArray

from backend.defaults import (
    COLUMNS,
    COLUMNS_PRETTY,
    VARIABLE_SETTINGS,
    VARIABLES,
    VARIABLES_PRETTY,
)
from backend.parameter import ParameterSet
from frontend.session import (
    get_pars_from_session,
    get_session_state,
)


def parameter_setter(title: str = "Set oscillation parameters") -> None:
    """
    A Streamlit component for setting oscillation parameters in the session state.
    """

    pars = get_pars_from_session()

    with st.expander(title, expanded=False):
        cols = st.columns(6)
        for i, key in enumerate(pars.to_dict().keys()):
            with cols[i % 6]:
                parameter_input(key, label=VARIABLES_PRETTY[i], format="%g")


def parameter_input(key: str, label: str, format: str = "%g", **kwargs):
    """
    A Streamlit component for setting a single parameter in the session state.
    """
    session_state = get_session_state()
    value = session_state.get(key, 0.0)
    new_value = st.number_input(label, value=value, format=format, **kwargs)
    if new_value != value:
        session_state[key] = new_value


def _reset_range_to_defaults(
    param_name_key: str,
    key_prefix: str,
    use_default_range: bool,
    override: dict[str, float] | None = None,
):
    """on_change callback — overwrites range widget state with defaults for the newly selected parameter."""
    selected = st.session_state[param_name_key]
    if selected not in VARIABLE_SETTINGS:
        return
    var = VARIABLE_SETTINGS[selected]
    st.session_state[f"{key_prefix}min_value"] = (
        var.default_low if use_default_range else var.min_value
    )
    st.session_state[f"{key_prefix}max_value"] = (
        var.default_high if use_default_range else var.max_value
    )
    st.session_state[f"{key_prefix}num_steps"] = var.num_steps
    st.session_state[f"{key_prefix}scale"] = var.scale
    if override is not None:
        for key in override:
            st.session_state[f"{key_prefix}{key}"] = override.get(
                key, st.session_state[f"{key_prefix}{key}"]
            )


def parameter_range_setter(
    default_var: str,
    orientation: str = "horizontal",
    key_prefix: str = "",
    use_default_range: bool = False,
    override: dict[str, float] | None = None,
    expander_label: str | None = None,
    expanded: bool = False,
) -> tuple[str, NDArray[np.float64]]:
    """Generate parameter values from a user-configured range.

    When ``expander_label`` is provided, the range controls are grouped in a
    Streamlit expander with that label.
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

    if override is not None:
        var_min = override.get("min_value", var_min)
        var_max = override.get("max_value", var_max)
        var_steps = override.get("num_steps", var_steps)
        var_scale = override.get("scale", var_scale)

    container = (
        st.expander(expander_label, expanded=expanded)
        if expander_label is not None
        else st.container()
    )
    with container:
        if orientation == "horizontal":
            cols = st.columns(5)
            with cols[0]:
                param_name_pretty = st.selectbox(
                    "Parameter name",
                    options=VARIABLES_PRETTY,
                    index=VARIABLES.index(default_var),
                    key=f"{key_prefix}param_name",
                    on_change=_reset_range_to_defaults,
                    args=(
                        f"{key_prefix}param_name",
                        key_prefix,
                        use_default_range,
                        override,
                    ),
                )
                param_name = VARIABLES[VARIABLES_PRETTY.index(param_name_pretty)]
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
            param_name_pretty = st.selectbox(
                "Parameter name",
                options=VARIABLES_PRETTY,
                index=VARIABLES.index(default_var),
                key=f"{key_prefix}param_name",
                on_change=_reset_range_to_defaults,
                args=(
                    f"{key_prefix}param_name",
                    key_prefix,
                    use_default_range,
                    override,
                ),
            )
            param_name = VARIABLES[VARIABLES_PRETTY.index(param_name_pretty)]
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


def osc_channel_selector(
    title: str | None = None,
    default_channel: str = "mu_e",
    single: bool = False,
    key: str | None = None,
) -> list[str]:
    """
    A Streamlit component for selecting the oscillation channel.
    """
    default_index = -1
    if default_channel in COLUMNS:
        default_index = COLUMNS.index(default_channel)
    if default_index in COLUMNS_PRETTY:
        default_index = COLUMNS_PRETTY.index(default_channel)
    if default_index == -1:
        raise ValueError(
            f"Default channel '{default_channel}' is not in COLUMNS, COLUMNS_PRETTY."
        )

    if single:
        channels = st.selectbox(
            "Select oscillation channel" if not title else title,
            options=COLUMNS_PRETTY,
            index=default_index,
            key=key,
        )
        channels = [COLUMNS[COLUMNS_PRETTY.index(channels)]]
    else:
        channels = st.multiselect(
            "Select oscillation channel(s)" if not title else title,
            options=COLUMNS_PRETTY,
            default=[COLUMNS_PRETTY[default_index]],
            key=key,
        )

        channels = [COLUMNS[COLUMNS_PRETTY.index(c)] for c in channels]

    return channels
