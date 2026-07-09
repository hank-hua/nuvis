import numpy as np

from .parameter import ParameterSet

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
