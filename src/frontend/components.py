"""Reusable Streamlit UI components."""

import streamlit as st

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
