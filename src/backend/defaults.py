import numpy as np

from .parameter import ParameterSet
from .variables import VariableSetting

DEFAULT_VALUES = ParameterSet(
    s12sq=0.31,
    s13sq=0.02,
    s23sq=0.55,
    delta=0.7 * np.pi,
    dmsq21=7.5e-5,
    dmsq31=2.5e-3,
    rho=3,  # g/cc
    ye=0.5,
    E=2.3,  # GeV
    L=1300,  # km
)

NOVA_LIKE = {
    "E": 2.0,
    "L": 810,
}

T2K_LIKE = {
    "E": 0.6,  # GeV
    "L": 295,  # km
}

VARIABLE_SETTINGS = {
    "s12sq": VariableSetting(
        name="s12sq",
        default_value=DEFAULT_VALUES["s12sq"],
        min_value=0.0,
        default_low=0.1,
        default_high=0.5,
        max_value=1.0,
        num_steps=100,
    ),
    "s13sq": VariableSetting(
        name="s13sq",
        default_value=DEFAULT_VALUES["s13sq"],
        min_value=0.0,
        max_value=1.0,
        default_low=0.01,
        default_high=0.05,
        num_steps=100,
    ),
    "s23sq": VariableSetting(
        name="s23sq",
        default_value=DEFAULT_VALUES["s23sq"],
        min_value=0.0,
        max_value=1.0,
        default_low=0.4,
        default_high=0.6,
        num_steps=100,
    ),
    "delta": VariableSetting(
        name="delta",
        default_value=DEFAULT_VALUES["delta"],
        min_value=-np.pi,
        max_value=2 * np.pi,
        default_low=-np.pi,
        default_high=np.pi,
        num_steps=100,
    ),
    "dmsq21": VariableSetting(
        name="dmsq21",
        default_value=DEFAULT_VALUES["dmsq21"],
        min_value=0.0,
        max_value=1e-4,
        default_low=7e-5,
        default_high=8e-5,
        num_steps=100,
    ),
    "dmsq31": VariableSetting(
        name="dmsq31",
        default_value=DEFAULT_VALUES["dmsq31"],
        min_value=-5e-3,
        max_value=5e-3,
        default_low=-2.6e-3,
        default_high=2.6e-3,
        num_steps=100,
    ),
    "rho": VariableSetting(
        name="rho",
        default_value=DEFAULT_VALUES["rho"],
        min_value=0.0,
        max_value=10.0,
        default_low=1.0,
        default_high=5.0,
        num_steps=100,
    ),
    "ye": VariableSetting(
        name="ye",
        default_value=DEFAULT_VALUES["ye"],
        min_value=0.0,
        max_value=1.0,
        default_low=0.4,
        default_high=0.6,
        num_steps=100,
    ),
    "E": VariableSetting(
        name="E",
        default_value=DEFAULT_VALUES["E"],
        min_value=0.01,
        max_value=10.0,
        default_low=0.1,
        default_high=10.0,
        num_steps=100,
    ),
    "L": VariableSetting(
        name="L",
        default_value=DEFAULT_VALUES["L"],
        min_value=0.0,
        max_value=2000,
        default_low=0.0,
        default_high=2000,
        num_steps=100,
    ),
    "L/E": VariableSetting(
        name="L/E",
        default_value=DEFAULT_VALUES["L"] / DEFAULT_VALUES["E"],
        min_value=0.0,
        max_value=2000 / 0.01,
        default_low=0.0,
        default_high=2000 / 0.01,
        num_steps=100,
    ),
}

VARIABLE_LIST = list(VARIABLE_SETTINGS.keys())
