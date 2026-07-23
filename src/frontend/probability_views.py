"""Tab renderers for probability visualisations."""

import streamlit as st

from backend.defaults import COLUMN_TO_PRETTY
from frontend.components import osc_channel_selector, parameter_range_setter
from frontend.plotter import Plotter
from frontend.session import get_pars_from_session


def reserved_1d_parameters() -> set[str]:
    """Return session-configured parameters controlled by the 1D plot."""
    reserved = {st.session_state.get("1d_x_param_name", "E")}
    if st.session_state.get("prob_1d_animate", True):
        reserved.add(st.session_state.get("1d_anim_param_name", "delta"))
    if st.session_state.get("prob_1d_overlay", False):
        reserved.add(st.session_state.get("1d_overlay_param_name", "s23sq"))
    return reserved


def reserved_2d_parameters() -> set[str]:
    """Return session-configured parameters controlled by the 2D plot."""
    reserved = {
        st.session_state.get("2d_x_param_name", "s23sq"),
        st.session_state.get("2d_y_param_name", "delta"),
    }
    if st.session_state.get("prob_2d_animate", False):
        reserved.add(st.session_state.get("2d_anim_param_name", "E"))
    if st.session_state.get("prob_2d_overlay", False):
        reserved.add(st.session_state.get("2d_overlay_param_name", "s13sq"))
    return reserved


def reserved_biprob_parameters() -> set[str]:
    """Return session-configured parameters controlled by the bi-probability plot."""
    reserved = {st.session_state.get("biprob_val_param_name", "delta")}
    if st.session_state.get("biprob_animate", True):
        reserved.add(st.session_state.get("biprob_anim_param_name", "E"))
    if st.session_state.get("biprob_overlay", False):
        reserved.add(st.session_state.get("biprob_overlay_param_name", "s23sq"))
    return reserved


def render_1d() -> None:
    """Render the 1D probability visualiser tab."""
    controls, plot = st.columns([1, 3])
    with controls:
        osc_chans = osc_channel_selector(key="prob_1d_channels")
        x_var, x_values = parameter_range_setter(
            "E",
            key_prefix="1d_x_",
            expander_label="X-axis",
            expanded=True,
            orientation="vertical",
            use_default_range=True,
        )

        with st.popover("Animation settings"):
            do_animate = st.checkbox("Animate", value=True, key="prob_1d_animate")
            freeze_axes = st.checkbox(
                "Freeze axes", value=False, key="prob_1d_freeze_axes"
            )
            anim_var, anim_values = parameter_range_setter(
                "delta",
                key_prefix="1d_anim_",
                use_default_range=True,
                override={"num_steps": 50},
            )

        with st.popover("Overlay settings"):
            do_overlay = st.checkbox("Overlay", value=False, key="prob_1d_overlay")
            overlay_var, overlay_values = parameter_range_setter(
                "s23sq",
                key_prefix="1d_overlay_",
                use_default_range=True,
                override={"num_steps": 5},
            )

    if do_overlay and overlay_var == x_var:
        with plot:
            st.error("Overlay and x-axis parameters must be different.")
        return
    if do_animate and anim_var in {x_var, overlay_var if do_overlay else None}:
        with plot:
            st.error("Animation, overlay, and x-axis parameters must be different.")
        return

    plot_config = dict(
        x_var=x_var,
        x_values=x_values,
        y_vars=osc_chans,
        line_width=2,
        overlay_var=overlay_var if do_overlay else None,
        overlay_values=overlay_values if do_overlay else None,
    )
    plotter = Plotter(pars=get_pars_from_session())

    if do_animate:
        plotter.animate(
            plot_method="1d",
            animate_var=anim_var,
            animate_values=anim_values,
            freeze_axes=freeze_axes,
            **plot_config,
        )
    else:
        plotter.make_1d(**plot_config)

    with plot:
        plotter.show()


def render_2d() -> None:
    """Render the 2D probability visualiser tab."""
    controls, plot = st.columns([1, 3])
    with controls:
        osc_chan = osc_channel_selector(single=True, key="prob_2d_channel")[0]
        osc_chan_pretty = COLUMN_TO_PRETTY.get(osc_chan, osc_chan)

        x_var, x_values = parameter_range_setter(
            "s23sq",
            key_prefix="2d_x_",
            use_default_range=True,
            expander_label="X-axis",
            expanded=True,
            orientation="vertical",
            override={"num_steps": 50},
        )
        y_var, y_values = parameter_range_setter(
            "delta",
            key_prefix="2d_y_",
            use_default_range=True,
            expander_label="Y-axis",
            expanded=True,
            orientation="vertical",
            override={"num_steps": 50},
        )

        with st.popover("Animation settings"):
            do_animate = st.checkbox("Animate", value=False, key="prob_2d_animate")
            anim_var, anim_values = parameter_range_setter(
                "E",
                key_prefix="2d_anim_",
                use_default_range=True,
                override={"num_steps": 10},
            )

        with st.popover("Overlay settings"):
            do_overlay = st.checkbox("Overlay", value=False, key="prob_2d_overlay")
            overlay_var, overlay_values = parameter_range_setter(
                "s13sq",
                key_prefix="2d_overlay_",
                use_default_range=True,
                override={"num_steps": 3},
            )

    if do_overlay and overlay_var in {x_var, y_var}:
        with plot:
            st.error("Overlay and axis parameters must be different.")
        return
    if do_animate and anim_var in {x_var, y_var, overlay_var if do_overlay else None}:
        with plot:
            st.error("Animation, overlay, and axis parameters must be different.")
        return

    plot_config = dict(
        x_values=x_values,
        y_values=y_values,
        x_var=x_var,
        y_var=y_var,
        z_var=osc_chan,
        title=osc_chan_pretty,
        ncontours=3,
        overlay_var=overlay_var if do_overlay else None,
        overlay_values=overlay_values if do_overlay else None,
    )
    plotter = Plotter(pars=get_pars_from_session())

    if do_animate:
        plotter.animate(
            plot_method="2d",
            animate_var=anim_var,
            animate_values=anim_values,
            **plot_config,
        )
    else:
        plotter.make_2d(**plot_config)

    with plot:
        plotter.show()


def render_biprob() -> None:
    """Render the bi-probability visualiser tab."""
    controls, plot = st.columns([1, 3])
    with controls:
        x_chan = osc_channel_selector(
            title="X-axis channel",
            default_channel="mu_e",
            single=True,
            key="biprob_x_channel",
        )[0]
        x_chan_pretty = COLUMN_TO_PRETTY.get(x_chan, x_chan)
        y_chan = osc_channel_selector(
            title="Y-axis channel",
            default_channel="anti_mu_e",
            single=True,
            key="biprob_y_channel",
        )[0]
        y_chan_pretty = COLUMN_TO_PRETTY.get(y_chan, y_chan)

        t_var, t_values = parameter_range_setter(
            "delta",
            key_prefix="biprob_val_",
            use_default_range=True,
            override={"num_steps": 20},
            expander_label="Ellipse parameter",
            expanded=True,
            orientation="vertical",
        )

        with st.popover("Animation settings"):
            do_animate = st.checkbox("Animate", value=True, key="biprob_animate")
            freeze_axes = st.checkbox(
                "Freeze axes", value=False, key="biprob_freeze_axes"
            )
            anim_var, anim_values = parameter_range_setter(
                "E",
                key_prefix="biprob_anim_",
                use_default_range=True,
                override={"num_steps": 20},
            )

        with st.popover("Overlay settings"):
            do_overlay = st.checkbox("Overlay", value=False, key="biprob_overlay")
            overlay_var, overlay_values = parameter_range_setter(
                "s23sq",
                key_prefix="biprob_overlay_",
                use_default_range=True,
                override={"num_steps": 5},
            )

    if do_overlay and overlay_var == t_var:
        with plot:
            st.error("Overlay and ellipse parameters must be different.")
        return
    if do_overlay and overlay_var == "dmsq31":
        with plot:
            st.error("dmsq31 is already represented by the NO/IO line style.")
        return
    if do_animate and anim_var in {t_var, overlay_var if do_overlay else None}:
        with plot:
            st.error("Animation, overlay, and ellipse parameters must be different.")
        return

    plot_config = dict(
        t_values=t_values,
        t_var=t_var,
        x_var=x_chan,
        y_var=y_chan,
        x_label=x_chan_pretty,
        y_label=y_chan_pretty,
        title=f"Bi-probability plot: {x_chan_pretty} vs {y_chan_pretty}",
        overlay_var=overlay_var if do_overlay else None,
        overlay_values=overlay_values if do_overlay else None,
        show_dcp_markers=t_var == "delta",
    )
    plotter = Plotter(pars=get_pars_from_session())

    if do_animate:
        plotter.animate(
            plot_method="biprob",
            animate_var=anim_var,
            animate_values=anim_values,
            freeze_axes=freeze_axes,
            **plot_config,
        )
    else:
        plotter.make_biprob(**plot_config)

    with plot:
        plotter.show()
