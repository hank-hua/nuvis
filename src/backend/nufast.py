from dataclasses import dataclass

import numpy as np
import pandas as pd

from _vendor.nufast import NuFast

from .defaults import COLUMNS, N_NEWTON
from .functional_parameters import replace_parameter
from .parameter import ParameterSet


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

    def __getitem__(self, channels: str | list[str]) -> np.ndarray | float:
        """Return probabilities for one or more channels."""
        if isinstance(channels, str):
            idx = COLUMNS.index(channels)  # int index => scalar result
            return self.probs[idx]
        idxs = self._resolve(channels)
        return self.probs[idxs]


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
            pars["dmsq21"],
            pars["dmsq31"],
            pars["L"],
            pars["E"],
        )
        p_anti = NuFast.Probability_Vacuum_LBL(
            pars["s12sq"],
            pars["s13sq"],
            pars["s23sq"],
            pars["delta"],
            pars["dmsq21"],
            pars["dmsq31"],
            pars["L"],
            -pars["E"],
        )

    return OscillationResult(np.concatenate([p.flatten(), p_anti.flatten()]))


def get_probs_1d(
    pars: ParameterSet,
    x_values: np.ndarray,
    x_var: str = "E",
    y_vars: list[str] | None = None,
    matter: bool = True,
) -> pd.DataFrame:
    """Calculate the oscillation probabilities for a 1D range of x_values.
    Returns a DataFrame with columns for x_var and y_var."""
    y_vars = ["mu_mu"] if y_vars is None else y_vars
    df = pd.DataFrame({x_var: x_values})
    results = [
        calc_prob(replace_parameter(pars, x_var, value), matter=matter)
        for value in x_values
    ]
    df[y_vars] = np.array([r[y_vars] for r in results])
    return df


def get_probs_2d(
    pars: ParameterSet,
    x_values: np.ndarray,
    y_values: np.ndarray,
    x_var: str = "E",
    y_var: str = "L",
    z_var: str = "e_mu",
    matter: bool = True,
):
    if z_var not in COLUMNS:
        raise ValueError(f"z_var ({z_var}) must be one of the probability channels")
    X, Y = np.meshgrid(x_values, y_values)
    Z = np.zeros_like(X, dtype=float)
    for idx in np.ndindex(X.shape):
        i, j = idx
        pars_ij = replace_parameter(pars, x_var, float(X[i, j]))
        pars_ij = replace_parameter(pars_ij, y_var, float(Y[i, j]))

        osc_res = calc_prob(pars_ij, matter=matter)
        Z[i, j] = osc_res[z_var]

    return Z, (X, Y)


def get_ellipse(
    pars: ParameterSet,
    t_var: str,
    t_values: np.ndarray,
    x_var: str = "mu_e",
    y_var: str = "anti_mu_e",
    matter: bool = True,
):
    if x_var not in COLUMNS or y_var not in COLUMNS:
        raise ValueError("x_var and y_var must be one of the probability channels")
    ellipse = np.zeros((len(t_values), 2))
    for i, t in enumerate(t_values):
        pars_t = replace_parameter(pars, t_var, t)
        osc_res = calc_prob(pars_t, matter=matter)
        ellipse[i, 0] = osc_res[x_var]
        ellipse[i, 1] = osc_res[y_var]
    return ellipse
