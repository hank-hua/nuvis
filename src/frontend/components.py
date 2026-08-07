"""Reusable Streamlit UI components."""

import numpy as np
import streamlit as st
from numpy.typing import NDArray

from backend.defaults import (
    COLUMNS,
    COLUMNS_PRETTY,
    EXPERIMENT_PRESETS,
    OSC_PRESETS,
    VARIABLE_SETTINGS,
    VARIABLE_TO_PRETTY,
    VARIABLES,
    VARIABLES_PRETTY,
)
from frontend.session import (
    get_pars_from_session,
    get_session_state,
)


def hide_number_input_buttons() -> None:
    """Hide Streamlit number-input step buttons without adding layout height."""
    st.html("<style>[data-testid='stNumberInput'] button { display: none; }</style>")


def _apply_experiment_preset() -> None:
    """Apply the selected experiment's energy and baseline to session state."""
    preset = EXPERIMENT_PRESETS.get(st.session_state["experiment_preset"], {})
    for key, value in preset.items():
        st.session_state[key] = value


def _apply_osc_preset() -> None:
    """Apply the selected oscillation parameter preset to session state."""
    preset = OSC_PRESETS.get(st.session_state["osc_preset"], {})
    for key, value in preset.items():
        st.session_state[key] = value


def parameter_setter(
    title: str = "Set oscillation parameters",
    disabled_parameters: set[str] | None = None,
) -> None:
    """Render session-backed oscillation parameters and presets.

    Parameters controlled by the active plot can be supplied in
    ``disabled_parameters`` to prevent confusing edits that do not affect it.
    """
    hide_number_input_buttons()
    pars = get_pars_from_session()
    disabled_parameters = disabled_parameters or set()

    with st.expander(title, expanded=False):
        cols = st.columns(3)
        with cols[0]:
            _ = st.selectbox(
                "Parameter preset",
                options=OSC_PRESETS.keys(),
                key="osc_preset",
                on_change=_apply_osc_preset,
                help="Sets the oscillation parameters to the selected preset values.",
            )
        with cols[1]:
            _ = st.selectbox(
                "Experiment preset",
                options=EXPERIMENT_PRESETS.keys(),
                key="experiment_preset",
                on_change=_apply_experiment_preset,
                help="Sets the energy E and baseline L for the selected experiment.",
            )
        with cols[2]:
            _ = st.toggle(
                "Matter effects",
                value=st.session_state.get("matter_effects", True),
                key="matter_effects",
            )
        cols = st.columns(6)
        for i, key in enumerate(pars.to_dict().keys()):
            with cols[i % 6]:
                is_mass_splitting = key in {"dmsq21", "dmsq31"}
                parameter_input(
                    key,
                    label=(
                        f"{VARIABLES_PRETTY[i]} [eV²]"
                        if is_mass_splitting
                        else VARIABLES_PRETTY[i]
                    ),
                    disabled=key in disabled_parameters,
                )


def parameter_input(key: str, label: str, disabled: bool = False) -> None:
    """Render a session-backed input using the variable's display metadata."""
    session_state = get_session_state()
    setting = VARIABLE_SETTINGS[key]
    value = session_state.get(key, 0.0)
    new_value = st.number_input(
        label,
        value=value,
        format=f"%{setting.display_format}",
        disabled=disabled,
    )
    if new_value != value:
        session_state[key] = new_value


def _range_number_input(
    label: str,
    value: float,
    variable: str,
    key: str,
) -> float:
    """Render a range bound using the selected variable's numeric metadata."""
    setting = VARIABLE_SETTINGS[variable]
    return st.number_input(
        label,
        value=float(value),
        format=f"%{setting.display_format}",
        key=key,
    )


def _reset_range_to_defaults(
    param_name_key: str,
    key_prefix: str,
    use_default_range: bool,
    override: dict[str, float | str] | None = None,
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
    override: dict[str, float | str] | None = None,
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
        var_min = float(override.get("min_value", var_min))
        var_max = float(override.get("max_value", var_max))
        var_steps = int(override.get("num_steps", var_steps))
        var_scale = str(override.get("scale", var_scale))

    param_name_key = f"{key_prefix}param_name"
    selected = st.session_state.get(param_name_key)
    if selected in VARIABLES_PRETTY:
        st.session_state[param_name_key] = VARIABLES[VARIABLES_PRETTY.index(selected)]

    container = (
        st.expander(expander_label, expanded=expanded)
        if expander_label is not None
        else st.container()
    )
    with container:
        if orientation == "horizontal":
            cols = st.columns(5)
            with cols[0]:
                param_name = st.selectbox(
                    "Parameter name",
                    options=VARIABLES,
                    format_func=VARIABLE_TO_PRETTY.__getitem__,
                    index=VARIABLES.index(default_var),
                    key=param_name_key,
                    on_change=_reset_range_to_defaults,
                    args=(param_name_key, key_prefix, use_default_range, override),
                )
            with cols[1]:
                min_value = _range_number_input(
                    "Min", var_min, param_name, f"{key_prefix}min_value"
                )
            with cols[2]:
                max_value = _range_number_input(
                    "Max", var_max, param_name, f"{key_prefix}max_value"
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
                    "Step scale",
                    options=["linear", "log"],
                    index=["linear", "log"].index(var_scale),
                    key=f"{key_prefix}scale",
                )
        else:
            param_name = st.selectbox(
                "Parameter name",
                options=VARIABLES,
                format_func=VARIABLE_TO_PRETTY.__getitem__,
                index=VARIABLES.index(default_var),
                key=param_name_key,
                on_change=_reset_range_to_defaults,
                args=(param_name_key, key_prefix, use_default_range, override),
            )
            min_value = _range_number_input(
                "Min", var_min, param_name, f"{key_prefix}min_value"
            )
            max_value = _range_number_input(
                "Max", var_max, param_name, f"{key_prefix}max_value"
            )
            num_steps = st.number_input(
                "No. steps", value=var_steps, min_value=2, key=f"{key_prefix}num_steps"
            )
            scale = st.selectbox(
                "Step scale",
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
