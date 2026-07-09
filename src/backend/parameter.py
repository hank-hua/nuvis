"""Parameter containers and helpers for physics calculations."""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass, fields
from dataclasses import replace as dc_replace
from typing import Dict, Iterator


@dataclass(frozen=True)
class ParameterSet:
    """Immutable parameter container for nufast."""

    s12sq: float
    s13sq: float
    s23sq: float
    delta: float
    dmsq21: float
    dmsq31: float
    rho: float
    ye: float
    E: float
    L: float

    def __post_init__(self):
        if not (0.0 <= self.s12sq <= 1.0):
            raise ValueError(f"s12sq must be in [0, 1], got {self.s12sq}")
        if not (0.0 <= self.s13sq <= 1.0):
            raise ValueError(f"s13sq must be in [0, 1], got {self.s13sq}")
        if not (0.0 <= self.s23sq <= 1.0):
            raise ValueError(f"s23sq must be in [0, 1], got {self.s23sq}")
        if self.E < 0:
            raise ValueError(f"Energy E must be positive, got {self.E}")
        if self.L < 0:
            raise ValueError(f"Baseline L must be positive, got {self.L}")
        if self.rho < 0:
            raise ValueError(f"Density rho must be non-negative, got {self.rho}")

    def __getitem__(self, key: str) -> float:
        try:
            return getattr(self, key)
        except AttributeError:
            raise KeyError(key)

    def __iter__(self) -> Iterator[str]:
        return iter(f.name for f in fields(self))

    def replace(self, **kwargs) -> ParameterSet:
        """Return a new ParameterSet with the specified fields replaced."""
        return dc_replace(self, **kwargs)

    def to_dict(self) -> Dict[str, float]:
        """Convert the ParameterSet to a dictionary."""
        return asdict(self)
