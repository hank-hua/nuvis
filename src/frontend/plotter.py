"""Plotting utilities for neutrino oscillation probabilities."""

from __future__ import annotations

from typing import Callable, Sequence

import numpy as np
import plotly.graph_objects as go
import streamlit as st
from plotly.colors import sample_colorscale

from backend.defaults import COLUMN_TO_PRETTY, VARIABLE_TO_PRETTY
from backend.nufast import calc_prob, get_ellipse, get_probs_1d, get_probs_2d
from backend.parameter import ParameterSet


class Plotter:
    """Builds and displays Plotly figures for neutrino oscillation probabilities."""

    DEFAULT_TOTAL_ANIMATION_DURATION: int = 5_000  # milliseconds
    DEFAULT_LINE_WIDTH: int = 2
    DEFAULT_HEATMAP_COLORSCALE: str = "ice"
    DEFAULT_CONTOUR_COLORSCALE: str = "greys"
    DEFAULT_CONTOUR_COUNT: int = 5
    DEFAULT_CONTOUR_LINE_WIDTH: int = 1
    DEFAULT_OVERLAY_COLORSCALE: str = "Oryel"

    def __init__(
        self,
        pars: ParameterSet,
        matter: bool = True,
        anti: bool = False,
    ):
        self.pars: ParameterSet = pars
        self.matter: bool = matter
        self.fig: go.Figure | None = None

    # --- Private helpers ----------------------------------------------------

    def _resolve_label(self, var_name: str, var_label: str | None) -> str:
        if var_label:
            return var_label
        if var_name in COLUMN_TO_PRETTY:
            return COLUMN_TO_PRETTY[var_name]
        if var_name in VARIABLE_TO_PRETTY:
            return VARIABLE_TO_PRETTY[var_name]
        return var_name

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
            x_var = plot_kwargs["x_var"]
            x_label = self._resolve_label(x_var, x_label)
            y_label = "Probability"
            title = title or f"Oscillation probabilities vs {x_label}"
        elif plot_method == "2d":
            x_var = plot_kwargs["x_var"]
            y_var = plot_kwargs["y_var"]
            x_label = self._resolve_label(x_var, x_label)
            y_label = self._resolve_label(y_var, y_label)
            title = title or "Probability"
        elif plot_method == "biprob":
            x_var = plot_kwargs["x_var"]
            y_var = plot_kwargs["y_var"]
            x_label = self._resolve_label(x_var, x_label)
            y_label = self._resolve_label(y_var, y_label)
            title = title or f"{x_label} vs {y_label}"
        return x_label, y_label, title

    @property
    def _frame_builders(self) -> dict[str, Callable]:
        """Dispatch map from plot method name to frame-data builder."""
        return {
            "1d": self._get_1d_frame_data,
            "2d": self._get_2d_frame_data,
            "biprob": self._get_ellipse_frame_data,
        }

    def _replace_parameter(
        self, pars: ParameterSet, variable: str, value: float
    ) -> ParameterSet:
        """Return parameters with one plotting variable replaced."""
        if variable == "L/E":
            if value <= 0:
                raise ValueError("L/E must be positive when used as a parameter sweep")
            return pars.replace(E=pars["L"] / value)
        if variable not in pars:
            raise ValueError(f"Unknown parameter: {variable!r}")
        return pars.replace(**{variable: value})

    def _build_traces(
        self,
        plot_method: str,
        plot_kwargs: dict,
        pars: ParameterSet,
        overlay_var: str | None = None,
        overlay_values: Sequence[float] | None = None,
        overlay_colorscale: str = DEFAULT_OVERLAY_COLORSCALE,
    ) -> list:
        """Build traces, optionally repeating them for an overlay parameter."""
        builder = self._frame_builders.get(plot_method)
        if builder is None:
            raise ValueError(
                f"Unknown plot method: {plot_method!r}. "
                f"Choose from: {list(self._frame_builders)}"
            )

        if overlay_var is None and overlay_values is None:
            return builder(pars=pars, **plot_kwargs)
        if overlay_var is None or overlay_values is None:
            raise ValueError("overlay_var and overlay_values must be provided together")

        values = list(overlay_values)
        if not values:
            raise ValueError("overlay_values cannot be empty")

        if plot_method == "1d":
            swept_vars = {plot_kwargs["x_var"]}
        elif plot_method == "2d":
            swept_vars = {
                plot_kwargs["x_var"],
                plot_kwargs["y_var"],
            }
        else:
            swept_vars = {plot_kwargs["t_var"]}
        if overlay_var in swept_vars:
            raise ValueError(f"{overlay_var!r} is already swept by the plot")
        if plot_method == "biprob" and overlay_var == "dmsq31":
            raise ValueError("dmsq31 is already represented by the NO/IO line style")

        positions = (
            [0.5] if len(values) == 1 else np.linspace(0, 1, len(values)).tolist()
        )
        colors = sample_colorscale(overlay_colorscale, positions)
        kwargs = dict(plot_kwargs)
        if plot_method == "2d":
            kwargs.update(draw_heatmap=False, draw_contours=True)
        elif plot_method == "biprob":
            kwargs["show_dcp_markers"] = False

        frame_data = []
        for value, color in zip(values, colors):
            traces = builder(
                pars=self._replace_parameter(pars, overlay_var, value),
                **kwargs,
            )
            label = f"{self._resolve_label(overlay_var, None)}={value:.4g}"

            for trace_index, trace in enumerate(traces):
                if plot_method == "2d":
                    trace.update(
                        colorscale=[[0, color], [1, color]],
                        showlegend=True,
                        name=label,
                        hoverinfo="all",
                        hovertemplate=(
                            "x: %{x}<br>y: %{y}<br>Probability: %{z:.4f}"
                            f"<br>{label}<extra></extra>"
                        ),
                    )
                else:
                    trace.update(
                        line_color=color,
                        line_dash=(
                            ["solid", "dash", "dot", "dashdot"][trace_index % 4]
                            if plot_method == "1d"
                            else trace.line.dash
                        ),
                        name=f"{trace.name}, {label}",
                    )
                    hover = trace.hovertemplate or ""
                    detail = f"<br>{label}"
                    trace.hovertemplate = (
                        hover.replace("<extra>", f"{detail}<extra>", 1)
                        if "<extra>" in hover
                        else f"{hover}{detail}<extra></extra>"
                    )

            frame_data.extend(traces)

        return frame_data

    # --- Frame data builders ------------------------------------------------

    def _get_1d_frame_data(
        self,
        x_values: Sequence[float],
        x_var: str = "E",
        y_vars: list[str] = ["mu_mu"],
        line_colors: list[str] | None = None,
        line_width: int = DEFAULT_LINE_WIDTH,
        pars: ParameterSet | None = None,
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
        pars = self.pars if pars is None else pars
        df = get_probs_1d(
            pars,
            x_values,
            x_var=x_var,
            y_vars=y_vars,
            matter=self.matter,
        )
        x_label = self._resolve_label(x_var, None)
        y_labels = [COLUMN_TO_PRETTY[y_var] for y_var in y_vars]
        return [
            go.Scatter(
                x=df[x_var],
                y=df[y_vars[i]],
                mode="lines",
                line=dict(
                    width=line_width, color=line_colors[i] if line_colors else None
                ),
                name=y_labels[i],
                hovertemplate=(
                    f"{x_label}: %{{x}}<br>{y_labels[i]}: %{{y:.4f}}<extra></extra>"
                ),
            )
            for i in range(len(y_vars))
        ]

    def _get_2d_frame_data(
        self,
        x_values: Sequence[float],
        x_var: str = "E",
        y_values: Sequence[float] | None = None,
        y_var: str = "L",
        z_var: str = "mu_e",
        draw_heatmap: bool = True,
        draw_contours: bool = True,
        heatmap_colorscale: str = DEFAULT_HEATMAP_COLORSCALE,
        contour_colorscale: str = DEFAULT_CONTOUR_COLORSCALE,
        contour_range: tuple[float, float, float] | None = None,
        ncontours: int = DEFAULT_CONTOUR_COUNT,
        contour_line_width: int = DEFAULT_CONTOUR_LINE_WIDTH,
        pars: ParameterSet | None = None,
    ) -> list[go.Heatmap | go.Contour]:
        """
        Build frame data for a 2D probability heatmap.

        Parameters
        ----------
        x_values : Sequence[float]
            Values for the x-axis.
        x_var : str
            Variable for the x-axis.
        y_values : Sequence[float]
            Values for the y-axis.
        y_var : str
            Variable for the y-axis.
        z_var : str
            Probability channel for the z-axis.

        Returns
        -------
        list[go.Heatmap | go.Contour]
            List containing the heatmap trace and optional contour trace.
        """
        pars = self.pars if pars is None else pars
        x_label = self._resolve_label(x_var, None)
        y_label = self._resolve_label(y_var, None)
        z_label = self._resolve_label(z_var, None)
        Z, _ = get_probs_2d(
            pars,
            x_values,
            y_values,
            x_var=x_var,
            y_var=y_var,
            z_var=z_var,
            matter=self.matter,
        )
        traces: list[go.Heatmap | go.Contour] = []
        if draw_heatmap:
            traces.append(
                go.Heatmap(
                    x=x_values,
                    y=y_values,
                    z=Z,
                    colorscale=heatmap_colorscale,
                    colorbar=dict(title=z_label),
                    hovertemplate=(
                        f"{x_label}: %{{x}}<br>{y_label}: %{{y}}<br>{z_label}: %{{z:.4f}}<extra></extra>"
                    ),
                )
            )
        if draw_contours:
            contour_config: dict[str, object] = dict(
                coloring="lines",
                showlabels=True,
                labelfont=dict(size=12),
            )
            if contour_range is None:
                contour_options: dict[str, object] = {"ncontours": ncontours}
            else:
                start, end, size = contour_range
                contour_config.update(start=start, end=end, size=size)
                contour_options = {"autocontour": False}

            traces.append(
                go.Contour(
                    x=x_values,
                    y=y_values,
                    z=Z,
                    contours=contour_config,
                    colorscale=contour_colorscale,
                    showscale=False,
                    line_width=contour_line_width,
                    hoverinfo="skip",
                    **contour_options,
                )
            )
        return traces

    def _get_ellipse_frame_data(
        self,
        t_values: Sequence[float],
        t_var: str,
        x_var: str,
        y_var: str,
        show_dcp_markers: bool = True,
        line_width: int = DEFAULT_LINE_WIDTH,
        pars: ParameterSet | None = None,
    ) -> list[go.Scatter]:
        """
        Build frame data for a bi-probability ellipse plot.

        Parameters
        ----------
        t_values : Sequence[float]
            Values for the animated parameter.
        t_var : str
            Name of the animated parameter.
        x_var : str
            Variable for the x-axis.
        y_var : str
            Variable for the y-axis.

        Returns
        -------
        list[go.Scatter]
            Single-element list containing the scatter trace.
        """
        pars = self.pars if pars is None else pars
        traces: list[go.Scatter] = []
        ellipse_NO = get_ellipse(
            pars,
            t_var=t_var,
            t_values=t_values,
            x_var=x_var,
            y_var=y_var,
            matter=self.matter,
        )
        ellipse_IO = get_ellipse(
            pars.replace(dmsq31=-pars["dmsq31"]),
            t_var=t_var,
            t_values=t_values,
            x_var=x_var,
            y_var=y_var,
            matter=self.matter,
        )
        t_label = self._resolve_label(t_var, None)
        x_label = self._resolve_label(x_var, None)
        y_label = self._resolve_label(y_var, None)
        labels = ["NO", "IO"]
        for i, ellipse in enumerate([ellipse_NO, ellipse_IO]):
            traces.append(
                go.Scatter(
                    x=ellipse[:, 0],
                    y=ellipse[:, 1],
                    mode="lines",
                    name=labels[i],
                    line=dict(width=line_width, dash="solid" if i == 0 else "dash"),
                    customdata=t_values,
                    hovertemplate=(
                        f"{x_label}: %{{x:.4f}}<br>{y_label}: %{{y:.4f}}"
                        f"<br>{t_label}: %{{customdata:.4f}}"
                    ),
                )
            )
        if show_dcp_markers:
            dcp_list = [-np.pi / 2, 0, np.pi / 2, np.pi]
            symbols_list = ["◕", "○", "◔", "◑"]
            sizes_list = [12, 18, 12, 12]
            for dcp in dcp_list:
                no_pars = pars.replace(delta=dcp)
                io_pars = pars.replace(delta=dcp, dmsq31=-pars["dmsq31"])
                no_oscres = calc_prob(no_pars, matter=self.matter)
                io_oscres = calc_prob(io_pars, matter=self.matter)
                traces.append(
                    go.Scatter(
                        x=[no_oscres[x_var], io_oscres[x_var]],
                        y=[no_oscres[y_var], io_oscres[y_var]],
                        mode="text",
                        text=[symbols_list[dcp_list.index(dcp)]] * 2,
                        textfont=dict(size=sizes_list[dcp_list.index(dcp)]),
                        hovertemplate=(
                            f"{x_label}: %{{x:.4f}}<br>{y_label}: %{{y:.4f}}"
                            f"<br>δ_CP: {dcp:.4f}<extra></extra>"
                        ),
                        showlegend=False,
                    )
                )
        return traces

    def _compute_frame_ranges(self, frame_data, pad_fraction: float = 0.05):
        """Compute padded x/y ranges for a frame from its trace data."""
        x_all = []
        y_all = []

        for trace in frame_data:
            if getattr(trace, "x", None) is not None:
                x_all.extend(
                    float(value)
                    for value in trace.x
                    if value is not None and np.isfinite(value)
                )
            if getattr(trace, "y", None) is not None:
                y_all.extend(
                    float(value)
                    for value in trace.y
                    if value is not None and np.isfinite(value)
                )

        if not x_all or not y_all:
            return None, None

        x_min, x_max = min(x_all), max(x_all)
        y_min, y_max = min(y_all), max(y_all)

        x_pad = (x_max - x_min) * pad_fraction
        y_pad = (y_max - y_min) * pad_fraction

        if x_pad == 0:
            x_pad = 1e-6
        if y_pad == 0:
            y_pad = 1e-6

        return [x_min - x_pad, x_max + x_pad], [y_min - y_pad, y_max + y_pad]

    # --- Public API ---------------------------------------------------------

    def make_1d(
        self,
        x_values: Sequence[float],
        x_var: str = "E",
        y_vars: list[str] = ["mu_mu"],
        x_label: str | None = None,
        y_label: str | None = None,
        title: str | None = None,
        line_colors: list[str] | None = None,
        line_width: int = DEFAULT_LINE_WIDTH,
        overlay_var: str | None = None,
        overlay_values: Sequence[float] | None = None,
        overlay_colorscale: str = DEFAULT_OVERLAY_COLORSCALE,
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
            {"x_var": x_var, "y_var": "Probability"},
            x_label,
            y_label,
            title,
        )
        traces = self._build_traces(
            "1d",
            dict(
                x_values=x_values,
                x_var=x_var,
                y_vars=y_vars,
                line_colors=line_colors,
                line_width=line_width,
            ),
            pars=self.pars,
            overlay_var=overlay_var,
            overlay_values=overlay_values,
            overlay_colorscale=overlay_colorscale,
        )
        self.fig = go.Figure(data=traces)
        self.fig.update_layout(
            title=title,
            xaxis_title=x_label,
            yaxis_title=y_label,
        )
        return self.fig

    def make_2d(
        self,
        x_values: Sequence[float],
        y_values: Sequence[float],
        x_var: str = "E",
        y_var: str = "L",
        z_var: str = "mu_e",
        x_label: str | None = None,
        y_label: str | None = None,
        z_label: str | None = None,
        title: str | None = None,
        heatmap_colorscale: str = DEFAULT_HEATMAP_COLORSCALE,
        contour_colorscale: str = DEFAULT_CONTOUR_COLORSCALE,
        contour_range: tuple[float, float, float] | None = None,
        ncontours: int = DEFAULT_CONTOUR_COUNT,
        contour_line_width: int = DEFAULT_CONTOUR_LINE_WIDTH,
        overlay_var: str | None = None,
        overlay_values: Sequence[float] | None = None,
        overlay_colorscale: str = DEFAULT_OVERLAY_COLORSCALE,
    ) -> go.Figure:
        """
        Create a 2D probability heatmap.

        Parameters
        ----------
        x_values : Sequence[float]
            Values for the x-axis.
        y_values : Sequence[float]
            Values for the y-axis.
        x_var : str
            Variable for x-axis (e.g., 'E', 'L', 'L/E').
        y_var : str
            Variable for y-axis (e.g., 'E', 'L', 'L/E').
        z_var : str
            Probability channel for z-axis (e.g., 'mu_mu', 'e_mu').
        x_label : str, optional
            Label for x-axis.
        y_label : str, optional
            Label for y-axis.
        title : str, optional
            Title for the plot.
        """
        x_label, y_label, title = self._resolve_labels(
            "2d",
            {"x_var": x_var, "y_var": y_var, "z_var": z_var},
            x_label,
            y_label,
            title,
        )
        traces = self._build_traces(
            "2d",
            dict(
                x_values=x_values,
                x_var=x_var,
                y_values=y_values,
                y_var=y_var,
                z_var=z_var,
                heatmap_colorscale=heatmap_colorscale,
                contour_colorscale=contour_colorscale,
                contour_range=contour_range,
                ncontours=ncontours,
                contour_line_width=contour_line_width,
            ),
            pars=self.pars,
            overlay_var=overlay_var,
            overlay_values=overlay_values,
            overlay_colorscale=overlay_colorscale,
        )
        self.fig = go.Figure(data=traces)
        self.fig.update_layout(
            title=title,
            xaxis_title=x_label,
            yaxis_title=y_label,
        )
        return self.fig

    def make_biprob(
        self,
        t_values: Sequence[float],
        t_var: str,
        x_var: str,
        y_var: str,
        x_label: str | None = None,
        y_label: str | None = None,
        title: str | None = None,
        line_width: int = DEFAULT_LINE_WIDTH,
        show_dcp_markers: bool = True,
        overlay_var: str | None = None,
        overlay_values: Sequence[float] | None = None,
        overlay_colorscale: str = DEFAULT_OVERLAY_COLORSCALE,
    ) -> go.Figure:
        """Create a bi-probability plot (x_var vs y_var) for a range of t_values."""

        x_label, y_label, title = self._resolve_labels(
            "biprob",
            {"x_var": x_var, "y_var": y_var},
            x_label,
            y_label,
            title,
        )
        traces = self._build_traces(
            "biprob",
            dict(
                t_values=t_values,
                t_var=t_var,
                x_var=x_var,
                y_var=y_var,
                line_width=line_width,
                show_dcp_markers=show_dcp_markers,
            ),
            pars=self.pars,
            overlay_var=overlay_var,
            overlay_values=overlay_values,
            overlay_colorscale=overlay_colorscale,
        )
        self.fig = go.Figure(data=traces)
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
        title: str | None = None,
        x_label: str | None = None,
        y_label: str | None = None,
        freeze_axes: bool = True,
        overlay_var: str | None = None,
        overlay_values: Sequence[float] | None = None,
        overlay_colorscale: str = DEFAULT_OVERLAY_COLORSCALE,
        total_duration: int = DEFAULT_TOTAL_ANIMATION_DURATION,
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
        title : str, optional
            Title for the plot.
        x_label : str, optional
            Label for x-axis.
        y_label : str, optional
            Label for y-axis.
        freeze_axes : bool, optional
            If True, use the same x/y axis ranges for all frames.
            If False, fit axes separately for each frame.
        total_duration : int, optional
            Total playback duration in milliseconds. It is divided equally
            across all animation frames.
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
        if overlay_var == animate_var:
            raise ValueError("Animation and overlay parameters must be different")
        if total_duration <= 0:
            raise ValueError("total_duration must be positive")

        if len(animate_values) == 0:
            raise ValueError("animate_values cannot be empty")
        frame_duration = max(10, round(total_duration / len(animate_values)))

        frames = []
        frame_ranges: list[tuple[list[float] | None, list[float] | None]] = []

        for val in animate_values:
            frame_pars = self._replace_parameter(self.pars, animate_var, val)
            frame_data = self._build_traces(
                plot_method,
                plot_kwargs,
                pars=frame_pars,
                overlay_var=overlay_var,
                overlay_values=overlay_values,
                overlay_colorscale=overlay_colorscale,
            )
            x_range, y_range = self._compute_frame_ranges(frame_data)
            frame_ranges.append((x_range, y_range))
            frames.append(
                go.Frame(
                    data=frame_data,
                    name=f"{val:.2f}",
                )
            )

        if freeze_axes and frame_ranges:
            x_mins = [xr[0] for xr, _ in frame_ranges if xr is not None]
            x_maxs = [xr[1] for xr, _ in frame_ranges if xr is not None]
            y_mins = [yr[0] for _, yr in frame_ranges if yr is not None]
            y_maxs = [yr[1] for _, yr in frame_ranges if yr is not None]

            global_x_range = [min(x_mins), max(x_maxs)] if x_mins and x_maxs else None
            global_y_range = [min(y_mins), max(y_maxs)] if y_mins and y_maxs else None

            frames = [
                go.Frame(
                    data=frame.data,
                    name=frame.name,
                    layout=go.Layout(
                        xaxis=dict(range=global_x_range),
                        yaxis=dict(range=global_y_range),
                    ),
                )
                for frame in frames
            ]
        else:
            frames = [
                go.Frame(
                    data=frame.data,
                    name=frame.name,
                    layout=go.Layout(
                        xaxis=dict(range=x_range),
                        yaxis=dict(range=y_range),
                    ),
                )
                for frame, (x_range, y_range) in zip(frames, frame_ranges)
            ]

        x_label, y_label, title = self._resolve_labels(
            plot_method, plot_kwargs, x_label, y_label, title
        )
        updatemenus, sliders = self._create_animation_controls(
            frames, animate_var, frame_duration
        )

        self.fig = go.Figure(data=frames[0].data, frames=frames)
        self.fig.update_layout(
            title=title,
            xaxis_title=x_label,
            yaxis_title=y_label,
            updatemenus=updatemenus,
            sliders=sliders,
        )

        if frames and frames[0].layout:
            self.fig.update_xaxes(range=frames[0].layout.xaxis.range)
            self.fig.update_yaxes(range=frames[0].layout.yaxis.range)

        return self.fig

    def show(self):
        """Display the current figure in Streamlit."""
        if self.fig is not None:
            st.plotly_chart(self.fig, width="stretch")
        else:
            st.write("No plot to display.")

    # --- Animation controls -------------------------------------------------

    def _create_animation_controls(
        self,
        frames: list[go.Frame],
        animate_var: str,
        frame_duration: int,
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
                showactive=False,
                buttons=[
                    dict(
                        label="Play",
                        method="animate",
                        args=[
                            None,
                            {
                                "frame": {
                                    "duration": frame_duration,
                                    "redraw": True,
                                },
                                "fromcurrent": True,
                                "mode": "immediate",
                                "transition": {"duration": 0},
                            },
                        ],
                    ),
                    dict(
                        label="Pause",
                        method="animate",
                        args=[
                            [None],
                            {
                                "frame": {"duration": 0, "redraw": True},
                                "mode": "immediate",
                            },
                        ],
                    ),
                ],
                x=0,
                xanchor="left",
                y=-0.4,
                yanchor="bottom",
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
                                    "duration": 0,
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
                    "duration": 0,
                },
                x=0.3,
                xanchor="left",
                y=-0.5,
                yanchor="bottom",
                pad=dict(t=0, b=0),
                currentvalue=dict(
                    font=dict(size=12),
                    prefix=f"{self._resolve_label(animate_var, None)}: ",
                    visible=True,
                    xanchor="left",
                    offset=0,
                ),
                len=0.7,
            )
        ]
        return updatemenus, sliders
