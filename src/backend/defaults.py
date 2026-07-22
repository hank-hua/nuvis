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
        scale="log",
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

VARIABLES = list(VARIABLE_SETTINGS.keys())

N_NEWTON = 5

COLUMNS = [
    "e_e",
    "e_mu",
    "e_tau",
    "mu_e",
    "mu_mu",
    "mu_tau",
    "tau_e",
    "tau_mu",
    "tau_tau",
    "anti_e_e",
    "anti_e_mu",
    "anti_e_tau",
    "anti_mu_e",
    "anti_mu_mu",
    "anti_mu_tau",
    "anti_tau_e",
    "anti_tau_mu",
    "anti_tau_tau",
]
COLUMNS_LATEX = [
    r"$\nu_e\to\nu_e$",
    r"$\nu_e\to\nu_\mu$",
    r"$\nu_e\to\nu_\tau$",
    r"$\nu_\mu\to\nu_e$",
    r"$\nu_\mu\to\nu_\mu$",
    r"$\nu_\mu\to\nu_\tau$",
    r"$\nu_\tau\to\nu_e$",
    r"$\nu_\tau\to\nu_\mu$",
    r"$\nu_\tau\to\nu_\tau$",
    r"$\bar{\nu}_e\to\bar{\nu}_e$",
    r"$\bar{\nu}_e\to\bar{\nu}_\mu$",
    r"$\bar{\nu}_e\to\bar{\nu}_\tau$",
    r"$\bar{\nu}_\mu\to\bar{\nu}_e$",
    r"$\bar{\nu}_\mu\to\bar{\nu}_\mu$",
    r"$\bar{\nu}_\mu\to\bar{\nu}_\tau$",
    r"$\bar{\nu}_\tau\to\bar{\nu}_e$",
    r"$\bar{\nu}_\tau\to\bar{\nu}_\mu$",
    r"$\bar{\nu}_\tau\to\bar{\nu}_\tau$",
]
COLUMNS_PRETTY = [
    "P(ν_e→ν_e)",
    "P(ν_e→ν_μ)",
    "P(ν_e→ν_τ)",
    "P(ν_μ→ν_e)",
    "P(ν_μ→ν_μ)",
    "P(ν_μ→ν_τ)",
    "P(ν_τ→ν_e)",
    "P(ν_τ→ν_μ)",
    "P(ν_τ→ν_τ)",
    "P(ν̅_e→ν̅_e)",
    "P(ν̅_e→ν̅_μ)",
    "P(ν̅_e→ν̅_τ)",
    "P(ν̅_μ→ν̅_e)",
    "P(ν̅_μ→ν̅_μ)",
    "P(ν̅_μ→ν̅_τ)",
    "P(ν̅_τ→ν̅_e)",
    "P(ν̅_τ→ν̅_μ)",
    "P(ν̅_τ→ν̅_τ)",
]
COLUMN_TO_PRETTY = dict(zip(COLUMNS, COLUMNS_PRETTY))
PRETTY_TO_COLUMN = dict(zip(COLUMNS_PRETTY, COLUMNS))
VARIABLE_TO_PRETTY = {
    "s12sq": "sin²θ₁₂",
    "s13sq": "sin²θ₁₃",
    "s23sq": "sin²θ₂₃",
    "delta": "δ_CP",
    "dmsq21": "Δm²₂₁",
    "dmsq31": "Δm²₃₁",
    "rho": "ρ",
    "ye": "Y_e",
    "E": "E",
    "L": "L",
    "L/E": "L/E",
}
VARIABLES_PRETTY = [VARIABLE_TO_PRETTY[v] for v in VARIABLES]
