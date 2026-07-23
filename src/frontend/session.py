import streamlit as st
from streamlit.runtime.state import SessionStateProxy

from backend.defaults import DEFAULT_VALUES
from backend.parameter import ParameterSet


def ensure_session_defaults() -> None:
    for k, v in DEFAULT_VALUES.to_dict().items():
        st.session_state.setdefault(k, v)


def get_session_state() -> SessionStateProxy:
    """Get the current streamlit session state."""
    ensure_session_defaults()
    return st.session_state


def get_pars_from_session() -> ParameterSet:
    """Get the current parameter values from current streamlit session state."""

    session_state = get_session_state()
    pars_dict = {
        key: session_state[key] for key in ParameterSet.__dataclass_fields__.keys()
    }
    return ParameterSet(**pars_dict)


def update_pars_in_session(pars: ParameterSet):
    """Update the current parameter values in current streamlit session state."""

    session_state = get_session_state()
    for key, value in pars.to_dict().items():
        session_state[key] = value
