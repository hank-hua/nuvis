"""Module for defining variable settings for plotting."""

from dataclasses import dataclass

@dataclass(frozen=True)
class VariableSetting:
    """Immutable container for variable settings."""

    name: str
    default_value: float
    min_value: float
    max_value: float
    default_low: float
    default_high: float
    num_steps: int
    scale: str = "linear"
    display_format: str = ".4g"

    def __post_init__(self):
        if self.min_value >= self.max_value:
            raise ValueError(f"min_value must be less than max_value, got {self.min_value} >= {self.max_value}")
        if self.num_steps < 2:
            raise ValueError(f"num_steps must be at least 2, got {self.num_steps}")
        if self.scale not in ("linear", "log"):
            raise ValueError(f"scale must be 'linear' or 'log', got {self.scale}")

        try:
            _ = format(self.default_value, self.display_format)
        except ValueError as error:
            raise ValueError(
                f"Invalid display_format {self.display_format!r}"
            ) from error

    def format_value(self, value: float) -> str:
        """Format a value for labels, legends, and other rendered text."""
        return format(value, self.display_format)

