from dataclasses import dataclass
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
from pathlib import Path

import numpy as np
import pandas as pd

from .defaults import COLUMNS, N_NEWTON
from .parameter import ParameterSet

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


@dataclass
class OscillationResult:
    probs: np.ndarray

    def _resolve(self, channels: str | list[str]) -> list[int]:
        """Resolve one or more channel names to indices."""
        if isinstance(channels, str):
            channels = [channels]
        invalid = [c for c in channels if c not in COLUMNS]
        if invalid:
            raise ValueError(f"Unknown channels: {invalid}. Must be one of {COLUMNS}")
        return [COLUMNS.index(c) for c in channels]

    def __getitem__(self, channels: str | list[str]) -> np.ndarray:
        """Return probabilities for one or more channels."""
        return self.probs[self._resolve(channels)]


def calc_prob(
    pars: ParameterSet, n_newton: int = N_NEWTON, matter: bool = True
) -> OscillationResult:
    """
    Calculate the oscillation probabilities for given parameters.
    Returns an OscillationResult containing neutrino and antineutrino probabilities for all channels.
    """
    if matter:
        p = NuFast.Probability_Matter_LBL(
            pars["s12sq"],
            pars["s13sq"],
            pars["s23sq"],
            pars["delta"],
            pars["dmsq21"],
            pars["dmsq31"],
            pars["L"],
            pars["E"],
            pars["rho"],
            pars["ye"],
            n_newton,
        )
        p_anti = NuFast.Probability_Matter_LBL(
            pars["s12sq"],
            pars["s13sq"],
            pars["s23sq"],
            pars["delta"],
            pars["dmsq21"],
            pars["dmsq31"],
            pars["L"],
            -pars["E"],
            pars["rho"],
            pars["ye"],
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
            pars["E"],
        )
        p_anti = NuFast.Probability_Vacuum_LBL(
            pars["s12sq"],
            pars["s13sq"],
            pars["s23sq"],
            pars["delta"],
            pars["Dmsq21"],
            pars["Dmsq31"],
            pars["L"],
            -pars["E"],
        )

    return OscillationResult(np.concatenate([p.flatten(), p_anti.flatten()]))


def get_probs_1d(
    pars: ParameterSet,
    x_values: np.ndarray,
    x_var: str = "E",
    y_vars: list[str] = ["mu_mu"],
    matter: bool = True,
) -> pd.DataFrame:
    """Calculate the oscillation probabilities for a 1D range of x_values.
    Returns a DataFrame with columns for x_var and y_var."""
    x_var_calc = x_var
    x_values_calc = x_values
    if x_var == "L/E":
        x_values_calc = pars["L"] / x_values
        x_var_calc = "E"
    df = pd.DataFrame({x_var: x_values})
    results = [
        calc_prob(pars.replace(**{x_var_calc: x}), matter=matter) for x in x_values_calc
    ]
    df[y_vars] = np.array([r[y_vars] for r in results])
    return df


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
    if z_var not in COLUMNS:
        raise ValueError("z_var must be one of the probability channels")
    X, Y = np.meshgrid(x_values, y_values)
    Z = np.zeros_like(X)
    z_index = COLUMNS.index(z_var)
    for idx in np.ndindex(X.shape):
        i, j = idx
        params = {
            **pars,
            x_var_calc: x_values_calc[j],
            y_var_calc: y_values_calc[i],
        }
        Z[i, j] = calc_prob(params, matter=matter, anti=anti)[z_index]

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
    if x_var not in COLUMNS or y_var not in COLUMNS:
        raise ValueError("x_var and y_var must be one of the probability channels")
    x_index = COLUMNS.index(x_var)
    y_index = COLUMNS.index(y_var)
    ellipse = np.zeros((len(t_values), 2))
    if t_var == "L/E":
        t_values = pars["L"] / t_values
        t_var = "E"
    for i, t in enumerate(t_values):
        pars_t = {**pars, t_var: t}
        ellipse[i, 0] = calc_prob(pars_t, matter=matter, anti=x_anti)[x_index]
        ellipse[i, 1] = calc_prob(pars_t, matter=matter, anti=y_anti)[y_index]
    return ellipse
