"""Derived plotting parameters and their transformations."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from .parameter import ParameterSet


@dataclass(frozen=True)
class FunctionalParameter:
    """A plotting variable derived from one or more physical parameters."""

    name: str
    apply: Callable[[ParameterSet, float], ParameterSet]
    get_value: Callable[[ParameterSet], float]


def _l_over_e(pars: ParameterSet, value: float) -> ParameterSet:
    """Set E based on L/E ratio, keeping L constant."""
    if pars["L"] <= 0:
        raise ValueError("L must be positive to sweep L/E")
    if value <= 0:
        raise ValueError("L/E must be positive")
    return pars.replace(E=pars["L"] / value)


def _l_at_constant_l_over_e(pars: ParameterSet, value: float) -> ParameterSet:
    """Set L while keeping L/E ratio constant."""
    if pars["L"] <= 0 or pars["E"] <= 0:
        raise ValueError("L and E must be positive to hold L/E constant")
    if value <= 0:
        raise ValueError("L must be positive when sweeping at constant L/E")
    return pars.replace(L=value, E=value * pars["E"] / pars["L"])


FUNCTIONAL_PARAMETERS: dict[str, FunctionalParameter] = {
    "L/E": FunctionalParameter(
        "L/E", _l_over_e, lambda pars: pars["L"] / pars["E"]
    ),
    "L_constLE": FunctionalParameter(
        "L_constLE", _l_at_constant_l_over_e, lambda pars: pars["L"]
    ),
}


def get_parameter_value(pars: ParameterSet, parameter: str) -> float:
    """Return the current value of a physical or registered functional parameter."""
    functional_parameter = FUNCTIONAL_PARAMETERS.get(parameter)
    if functional_parameter is not None:
        return functional_parameter.get_value(pars)
    if parameter not in pars:
        raise ValueError(f"Unknown parameter: {parameter!r}")
    return pars[parameter]


def replace_parameter(pars: ParameterSet, parameter: str, value: float) -> ParameterSet:
    """Return ``pars`` with a physical or registered functional parameter updated."""
    functional_parameter = FUNCTIONAL_PARAMETERS.get(parameter)
    if functional_parameter is not None:
        return functional_parameter.apply(pars, value)
    if parameter not in pars:
        raise ValueError(f"Unknown parameter: {parameter!r}")
    return pars.replace(**{parameter: value})
