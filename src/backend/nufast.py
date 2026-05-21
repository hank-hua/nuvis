from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
from pathlib import Path

import numpy as np
import pandas as pd

_nufast_path = (
    Path(__file__).resolve().parents[2] / "external" / "nufast" / "py" / "NuFast.py"
)
if not _nufast_path.exists():
    raise FileNotFoundError(f"NuFast.py not found at {_nufast_path}")

_spec = spec_from_loader(
    "nufast_external", SourceFileLoader("nufast_external", str(_nufast_path))
)
if _spec is None or _spec.loader is None:
    raise ImportError("Unable to load NuFast module from external submodule")

_module = module_from_spec(_spec)
_spec.loader.exec_module(_module)

NuFast = _module

columns = [
    "e_e",
    "e_mu",
    "e_tau",
    "mu_e",
    "mu_mu",
    "mu_tau",
    "tau_e",
    "tau_mu",
    "tau_tau",
]
columns_latex = [
    r"$\nu_e\to\nu_e$",
    r"$\nu_e\to\nu_\mu$",
    r"$\nu_e\to\nu_\tau$",
    r"$\nu_\mu\to\nu_e$",
    r"$\nu_\mu\to\nu_\mu$",
    r"$\nu_\mu\to\nu_\tau$",
    r"$\nu_\tau\to\nu_e$",
    r"$\nu_\tau\to\nu_\mu$",
    r"$\nu_\tau\to\nu_\tau$",
]
columns_pretty = [
    "P(ν_e→ν_e)",
    "P(ν_e→ν_μ)",
    "P(ν_e→ν_τ)",
    "P(ν_μ→ν_e)",
    "P(ν_μ→ν_μ)",
    "P(ν_μ→ν_τ)",
    "P(ν_τ→ν_e)",
    "P(ν_τ→ν_μ)",
    "P(ν_τ→ν_τ)",
]
columns_anti_pretty = [
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
column_to_pretty = dict(zip(columns, columns_pretty))
pretty_to_column = dict(zip(columns_pretty, columns))
column_to_anti_pretty = dict(zip(columns, columns_anti_pretty))
columns_e = ["e_e", "e_mu", "e_tau"]
columns_mu = ["mu_e", "mu_mu", "mu_tau"]
columns_tau = ["tau_e", "tau_mu", "tau_tau"]


def prob_calcer_full(pars, n_newton=5, matter=True, anti=False):
    E = -abs(pars["E"]) if anti else abs(pars["E"])
    if matter:
        p = NuFast.Probability_Matter_LBL(
            pars["s12sq"],
            pars["s13sq"],
            pars["s23sq"],
            pars["delta"],
            pars["Dmsq21"],
            pars["Dmsq31"],
            pars["L"],
            E,
            pars["rho"],
            pars["Ye"],
            n_newton,
        )
    else:
        p = NuFast.Probability_Vacuum_LBL(
            pars["s12sq"],
            pars["s13sq"],
            pars["s23sq"],
            pars["delta"],
            pars["Dmsq21"],
            pars["Dmsq31"],
            pars["L"],
            E,
        )
    return p.flatten()


def get_probs_df(pars, x_values, x_var="E", y_var="mu_mu", matter=True, anti=False):
    x_var_calc = x_var
    x_values_calc = x_values
    if x_var == "L/E":
        x_values_calc = pars["L"] / x_values
        x_var_calc = "E"
    data = {x_var: x_values}
    y_index = columns.index(y_var)
    y_values = np.zeros_like(x_values)
    for i in range(x_values.size):
        y_values[i] = prob_calcer_full(
            {**pars, x_var_calc: x_values_calc[i]}, matter=matter, anti=anti
        )[y_index]
    data[y_var] = y_values
    return pd.DataFrame(data)


def get_probs_mesh(
    pars,
    x_values,
    y_values,
    x_var="E",
    y_var="L",
    z_var="e_mu",
    matter=True,
    anti=False,
):
    x_var_calc = x_var
    x_values_calc = x_values
    if x_var == "L/E":
        x_values_calc = pars["L"] / x_values
        x_var_calc = "E"
    y_var_calc = y_var
    y_values_calc = y_values
    if y_var == "L/E":
        y_values_calc = pars["L"] / y_values
        y_var_calc = "E"
    if z_var not in columns:
        raise ValueError("z_var must be one of the probability channels")
    X, Y = np.meshgrid(x_values, y_values)
    Z = np.zeros_like(X)
    z_index = columns.index(z_var)
    for idx in np.ndindex(X.shape):
        i, j = idx
        params = {
            **pars,
            x_var_calc: x_values_calc[j],
            y_var_calc: y_values_calc[i],
        }
        Z[i, j] = prob_calcer_full(params, matter=matter, anti=anti)[z_index]

    return Z, (X, Y)


def get_ellipse(
    pars,
    t_var,
    t_values,
    x_var="mu_e",
    y_var="mu_e",
    x_anti=False,
    y_anti=False,
    matter=True,
):
    if x_var not in columns or y_var not in columns:
        raise ValueError("x_var and y_var must be one of the probability channels")
    x_index = columns.index(x_var)
    y_index = columns.index(y_var)
    ellipse = np.zeros((len(t_values), 2))
    if t_var == "L/E":
        t_values = pars["L"] / t_values
        t_var = "E"
    for i, t in enumerate(t_values):
        pars_t = {**pars, t_var: t}
        ellipse[i, 0] = prob_calcer_full(pars_t, matter=matter, anti=x_anti)[x_index]
        ellipse[i, 1] = prob_calcer_full(pars_t, matter=matter, anti=y_anti)[y_index]
    return ellipse
