"""Plotting utilities for neutrino oscillation probabilities."""

from __future__ import annotations

from typing import Callable, Sequence

import plotly.graph_objects as go
import streamlit as st

from backend.defaults import COLUMN_TO_PRETTY
from backend.nufast import get_probs_1d
from backend.parameter import ParameterSet


class Plotter:
    """Builds and displays Plotly figures for neutrino oscillation probabilities."""

    DEFAULT_FRAME_DURATION = 100  # milliseconds

    def __init__(
        self,
        pars: ParameterSet,
        matter: bool = True,
        anti: bool = False,
        frame_duration: int = DEFAULT_FRAME_DURATION,
    ):
        self.pars = pars
        self.matter = matter
        self.frame_duration = frame_duration
        self.fig: go.Figure | None = None

    # --- Private helpers ----------------------------------------------------

    def _resolve_label(self, fallback: str, override: str | None) -> str:
        """Return override if provided, otherwise return fallback."""
        return override if override is not None else fallback

    def _resolve_labels(
        self,
        plot_method: str,
        plot_kwargs: dict,
        x_label: str | None,
        y_label: str | None,
        title: str | None,
    ) -> tuple[str, str, str]:
        """
        Resolve axis labels and title for a given plot method.

        Parameters
        ----------
        plot_method : str
            The plot type ('1d', '2d', 'ellipse').
        plot_kwargs : dict
            Keyword arguments for the plot method, used to extract axis variables.
        x_label : str, optional
            Override for the x-axis label.
        y_label : str, optional
            Override for the y-axis label.
        title : str, optional
            Override for the plot title.

        Returns
        -------
        tuple[str, str, str]
            Resolved (x_label, y_label, title).
        """
        if plot_method == "1d":
            x_var = plot_kwargs.get("x_var", "E")
            y_var = plot_kwargs.get("y_var", "Probability")
            x_label = self._resolve_label(x_var, x_label)
            y_label = self._resolve_label(y_var, y_label)
            title = title or y_label
        elif plot_method == "2d":
            x_var = plot_kwargs.get("x_var", "E")
            y_var = plot_kwargs.get("y_var", "L")
            z_var = plot_kwargs.get("z_var", "Probability")
            x_label = self._resolve_label(x_var, x_label)
            y_label = self._resolve_label(y_var, y_label)
            title = title or self._resolve_label(z_var, None)
        elif plot_method == "ellipse":
            x_var = plot_kwargs.get("x_var", "mu_e")
            y_var = plot_kwargs.get("y_var", "mu_e")
            x_label = self._resolve_label(x_var, x_label)
            y_label = self._resolve_label(y_var, y_label)
            title = title or f"{x_label} vs {y_label}"
        return x_label, y_label, title

    def _build_scatter(
        self,
        df,
        x_var: str,
        y_var: str,
        y_label: str,
        line_color: str | None,
        line_width: int,
    ) -> go.Scatter:
        """
        Build a Plotly Scatter trace from a probability DataFrame.

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame containing x_var and y_var columns.
        x_var : str
            Column name for the x-axis.
        y_var : str
            Column name for the y-axis.
        y_label : str
            Display label for the y-axis (used in hover).
        line_color : str, optional
            Line colour.
        line_width : int
            Line width.

        Returns
        -------
        go.Scatter
            Plotly scatter trace.
        """
        return go.Scatter(
            x=df[x_var],
            y=df[y_var],
            mode="lines",
            line=dict(width=line_width, color=line_color),
            name=y_label,
            hovertemplate=(f"{x_var}: %{{x}}<br>{y_label}: %{{y:.4f}}<extra></extra>"),
        )

    @property
    def _frame_builders(self) -> dict[str, Callable]:
        """Dispatch map from plot method name to frame-data builder."""
        return {
            "1d": self._get_1d_frame_data,
            # "2d": self._get_2d_frame_data,
            # "ellipse": self._get_ellipse_frame_data,
        }

    # --- Frame data builders ------------------------------------------------

    def _get_1d_frame_data(
        self,
        x_values: Sequence[float],
        x_var: str = "E",
        y_vars: list[str] = ["mu_mu"],
        line_colors: list[str] | None = None,
        line_width: int = 2,
        **kwargs,
    ) -> list[go.Scatter]:
        """
        Build frame data for a 1D probability plot.

        Parameters
        ----------
        x_values : Sequence[float]
            Values for the x-axis.
        x_var : str
            Variable for the x-axis.
        y_var : str
            Probability channel for the y-axis.
        line_color : str, optional
            Line colour.
        line_width : int
            Line width.

        Returns
        -------
        list[go.Scatter]
            Single-element list containing the scatter trace.
        """
        df = get_probs_1d(
            self.pars,
            x_values,
            x_var=x_var,
            y_vars=y_vars,
            matter=self.matter,
        )
        y_labels = [COLUMN_TO_PRETTY[y_var] for y_var in y_vars]
        return [
            self._build_scatter(
                df,
                x_var,
                y_vars[i],
                y_labels[i],
                line_colors[i] if line_colors else None,
                line_width,
            )
            for i in range(len(y_vars))
        ]

    # --- Public API ---------------------------------------------------------

    def make_1d(
        self,
        x_values: Sequence[float],
        x_var: str = "E",
        y_vars: list[str] = ["mu_mu"],
        x_label: str | None = None,
        y_label: str | None = None,
        title: str | None = None,
        line_colors: llist[str] | None = None,
        line_width: int = 2,
    ) -> go.Figure:
        """
        Create a 1D probability plot.

        Parameters
        ----------
        x_values : Sequence[float]
            Values for the x-axis.
        x_var : str
            Variable for x-axis (e.g., 'E', 'L', 'L/E').
        y_var : str
            Probability channel for y-axis (e.g., 'mu_mu', 'e_mu').
        x_label : str, optional
            Label for x-axis.
        y_label : str, optional
            Label for y-axis.
        title : str, optional
            Title for the plot.
        line_color : str, optional
            Color for the line.
        line_width : int
            Width of the line.

        Returns
        -------
        go.Figure
            Plotly figure object.
        """
        x_label, y_label, title = self._resolve_labels(
            "1d",
            {"x_var": x_var, "y_var": y_vars},
            x_label,
            y_label,
            title,
        )
        trace = self._get_1d_frame_data(
            x_values, x_var, y_vars, line_colors, line_width
        )
        self.fig = go.Figure(data=trace)
        self.fig.update_layout(
            title=title,
            xaxis_title=x_label,
            yaxis_title=y_label,
        )
        return self.fig

    def animate(
        self,
        plot_method: str,
        animate_var: str,
        animate_values: Sequence[float],
        x_values: Sequence[float],
        title: str | None = None,
        x_label: str | None = None,
        y_label: str | None = None,
        **plot_kwargs,
    ) -> go.Figure:
        """
        Create an animated plot by stepping through values of a single parameter.

        Parameters
        ----------
        plot_method : str
            Name of the plot method to animate ('1d', '2d', or 'ellipse').
        animate_var : str
            Parameter to animate over.
        animate_values : Sequence[float]
            Values to animate through.
        x_values : Sequence[float]
            Values for the x-axis of each frame.
        title : str, optional
            Title for the plot.
        x_label : str, optional
            Label for x-axis.
        y_label : str, optional
            Label for y-axis.
        **plot_kwargs
            Additional keyword arguments passed to the frame builder.

        Returns
        -------
        go.Figure
            Animated Plotly figure object.

        Raises
        ------
        ValueError
            If plot_method is not recognised.
        """
        builder = self._frame_builders.get(plot_method)
        if builder is None:
            raise ValueError(
                f"Unknown plot method: {plot_method!r}. "
                f"Choose from: {list(self._frame_builders)}"
            )

        original_pars = self.pars
        frames = []
        try:
            for val in animate_values:
                self.pars = self.pars.replace(**{animate_var: val})
                frame_data = builder(x_values=x_values, **plot_kwargs)
                frames.append(go.Frame(data=frame_data, name=f"{val:.2f}"))
                self.pars = original_pars  # reset each iteration
        finally:
            self.pars = original_pars  # guaranteed restore on exception

        x_label, y_label, title = self._resolve_labels(
            plot_method, plot_kwargs, x_label, y_label, title
        )
        updatemenus, sliders = self._create_animation_controls(frames, animate_var)

        self.fig = go.Figure(data=frames[0].data, frames=frames)
        self.fig.update_layout(
            title=title,
            xaxis_title=x_label,
            yaxis_title=y_label,
            updatemenus=updatemenus,
            sliders=sliders,
        )
        return self.fig

    def show(self):
        """Display the current figure in Streamlit."""
        if self.fig is not None:
            st.plotly_chart(self.fig, width="stretch")
        else:
            st.write("No plot to display.")

    # --- Animation controls -------------------------------------------------

    def _create_animation_controls(
        self, frames: list[go.Frame], animate_var: str
    ) -> tuple[list, list]:
        """
        Build Plotly updatemenus and sliders for animation controls.

        Parameters
        ----------
        frames : list[go.Frame]
            Animation frames.
        animate_var : str
            Name of the animated variable, used as the slider prefix.

        Returns
        -------
        tuple[list, list]
            (updatemenus, sliders) ready for fig.update_layout().
        """
        updatemenus = [
            dict(
                type="buttons",
                direction="left",
                buttons=[
                    dict(
                        label="Play",
                        method="animate",
                        args=[
                            None,
                            {
                                "frame": {
                                    "duration": self.frame_duration,
                                    "redraw": True,
                                },
                                "fromcurrent": True,
                            },
                        ],
                    ),
                    dict(
                        label="Pause",
                        method="animate",
                        args=[
                            [None],
                            {
                                "frame": {"duration": 0, "redraw": False},
                                "mode": "immediate",
                            },
                        ],
                    ),
                ],
                x=0,
                y=-0.15,
            )
        ]
        sliders = [
            dict(
                steps=[
                    dict(
                        method="animate",
                        args=[
                            [f.name],
                            {
                                "frame": {
                                    "duration": self.frame_duration,
                                    "redraw": True,
                                },
                                "mode": "immediate",
                            },
                        ],
                        label=f.name,
                    )
                    for f in frames
                ],
                transition={
                    "duration": self.frame_duration,
                    "easing": "cubic-in-out",
                },
                x=0.1,
                y=-0.15,
                currentvalue=dict(
                    font=dict(size=12),
                    prefix=f"{animate_var}: ",
                    visible=True,
                    xanchor="center",
                ),
                len=0.9,
            )
        ]
        return updatemenus, sliders
