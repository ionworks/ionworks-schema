"""Typed plot configs and the matplotlib renderers that draw them.

A :class:`PlotConfig` declares *what is in a panel* (its traces and labels), not
how it looks; style is decided here by trace label, so the same config renders
identically from an in-process fit and from a result decoded over the API.
:func:`render` dispatches on the objective's ``type`` and falls back to a plain
panel grid for an unknown type, so a new server objective cannot break plotting
for an older client. Matplotlib is an optional dependency (the ``plot`` extra).
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

#: Per-trace styling, keyed by the lowercased first word of the trace label.
#: Measured data is faint open markers so an overlaid model line stays readable.
_TRACE_STYLES: dict[str, dict[str, Any]] = {
    "data": {
        "linestyle": "",
        "marker": "o",
        "color": "k",
        "alpha": 0.3,
        "mfc": "none",
    },
    "model": {"linestyle": "-", "color": "tab:red", "linewidth": 2},
    "fit": {"linestyle": "-", "color": "tab:red", "linewidth": 2},
    "error": {"linestyle": "-", "color": "k", "linewidth": 1},
}


class PlotTrace(BaseModel):
    """One labelled series in a panel."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    #: Legend label. Its first word selects the style ("Data", "Model", "Fit", "Error").
    label: str = ""
    #: x values. Any array-like matplotlib accepts.
    x: Any = None
    #: y values, as for :attr:`x`.
    y: Any = None
    #: Overrides the label-derived colour, to distinguish series sharing a role.
    color: str | None = None


class PlotConfig(BaseModel):
    """One panel: what to draw and how to label it, with no styling."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    x_label: str = ""
    y_label: str = ""
    #: Explicit ``(min, max)`` axis bounds; either side may be ``None`` to auto-scale.
    x_range: tuple[float | None, float | None] | None = None
    y_range: tuple[float | None, float | None] | None = None
    traces: list[PlotTrace] = Field(default_factory=list)

    @classmethod
    def from_wire(cls, payload: dict) -> PlotConfig:
        """Build a config from a stored plot payload.

        The backend persists each plot in plotly's vocabulary
        (``{"type", "traces": [{"name", "x", "y"}], "layout": {"xaxis": ...}}``);
        this maps that onto the fields above.

        Parameters
        ----------
        payload : dict
            One plot as returned by ``GET /datafits/{id}/plot_data``.

        Returns
        -------
        PlotConfig
            The equivalent config.
        """

        def _axis(name: str) -> dict:
            entry = (payload.get("layout") or {}).get(name)
            return entry if isinstance(entry, dict) else {}

        def _title(axis: dict) -> str:
            title = axis.get("title")
            if isinstance(title, dict):
                text = title.get("text")
                return text if isinstance(text, str) else ""
            return title if isinstance(title, str) else ""

        def _range(axis: dict):
            rng = axis.get("range")
            if isinstance(rng, (list, tuple)) and len(rng) == 2:
                return (rng[0], rng[1])
            return None

        x_axis, y_axis = _axis("xaxis"), _axis("yaxis")
        return cls(
            x_label=_title(x_axis),
            y_label=_title(y_axis),
            x_range=_range(x_axis),
            y_range=_range(y_axis),
            traces=[
                PlotTrace(
                    label=str(trace.get("name") or ""),
                    x=trace.get("x"),
                    y=trace.get("y"),
                    color=trace.get("color"),
                )
                for trace in (payload.get("traces") or [])
                if isinstance(trace, dict)
            ],
        )


def _as_config(plot: Any) -> PlotConfig:
    """Coerce a plot to a :class:`PlotConfig`, accepting a stored payload."""
    if isinstance(plot, PlotConfig):
        return plot
    if isinstance(plot, dict):
        return PlotConfig.from_wire(plot)
    raise TypeError(f"Expected a PlotConfig or dict, got {type(plot).__name__}")


def error_label(variable: str) -> str:
    """Axis label for a variable's residual, carrying its unit when it has one."""
    unit = variable.split("[")[1].rstrip("]") if "[" in variable else ""
    return f"Error [{unit}]" if unit else "Error"


def _residual(x_data, y_data, x_model, y_model):
    """Model minus measurement, interpolated onto the measured x where they differ."""
    import numpy as np

    y_data = np.asarray(y_data, dtype=float)
    y_model = np.asarray(y_model, dtype=float)
    if x_model is not None and y_model.shape != y_data.shape:
        y_model = np.interp(
            np.asarray(x_data, dtype=float), np.asarray(x_model, dtype=float), y_model
        )
    return y_model - y_data


def fit_panels(
    variables: list[str],
    x_key: str,
    data: dict,
    model: dict,
    *,
    x_label: str | None = None,
) -> list[PlotConfig]:
    """Panels for a fit: measured against fitted per variable, then the residuals.

    Residuals come last as a block, so laying the result out in
    ``len(variables)`` columns puts each residual under the curve it came from.

    Parameters
    ----------
    variables : list of str
        Keys to plot, one panel each. A ``"Name [unit]"`` key gives the residual
        panel its unit.
    x_key : str
        Key of the independent variable. Taken from ``model`` when it carries its
        own, else shared with ``data``.
    data : dict
        The measurement, keyed by variable.
    model : dict
        The fitted model's output, keyed the same way.
    x_label : str, optional
        Axis label for the independent variable. Defaults to ``x_key``.

    Returns
    -------
    list of PlotConfig
        One config per variable, then one residual config per variable.
    """
    x_data = data[x_key]
    panels = [
        PlotConfig(
            x_label=x_label or x_key,
            y_label=var,
            traces=[
                PlotTrace(label=label, x=output.get(x_key, x_data), y=output[var])
                for label, output in (("Data", data), ("Fit", model))
            ],
        )
        for var in variables
    ]
    return panels + [
        PlotConfig(
            x_label=x_label or x_key,
            y_label=error_label(var),
            traces=[
                PlotTrace(
                    label="Error",
                    x=x_data,
                    y=_residual(x_data, data[var], model.get(x_key), model[var]),
                )
            ],
        )
        for var in variables
    ]


def _import_matplotlib():
    """Return ``matplotlib.pyplot``, or raise a pointed ImportError.

    Returns
    -------
    module
        The ``matplotlib.pyplot`` module.

    Raises
    ------
    ImportError
        If matplotlib is not installed.
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise ImportError(
            "Plotting requires matplotlib. Install it with the 'plot' "
            "extra: pip install ionworks-schema[plot]"
        ) from exc
    return plt


def _subplots_autolayout(n: int, n_cols: int | None = None, share_x: bool = False):
    """Create a grid of ``n`` axes, returned flattened.

    Parameters
    ----------
    n : int
        Number of axes needed. Surplus axes in the grid are hidden.
    n_cols : int, optional
        Column count. Defaults to a roughly square grid. Set it when the panel
        order is meaningful — panels fill row by row, so a column count makes
        each column a known group.
    share_x : bool, optional
        Share the x axis down each column, so stacked panels of the same
        quantity line up and only the bottom one carries the axis. Defaults to
        False.

    Returns
    -------
    tuple
        ``(fig, axes)`` where ``axes`` is a flat list of length ``>= n``; the
        first ``n`` are visible.
    """
    import math

    plt = _import_matplotlib()

    n = max(int(n), 1)
    if n_cols is None:
        n_rows = max(int(n // math.sqrt(n)), 1)
        n_cols = int(math.ceil(n / n_rows))
    else:
        n_cols = max(int(n_cols), 1)
        n_rows = int(math.ceil(n / n_cols))
    figsize = (min(15, 4 * n_cols), min(8, 1 + 3 * n_rows))

    fig, axes = plt.subplots(
        n_rows,
        n_cols,
        figsize=figsize,
        layout="constrained",
        sharex="col" if share_x else False,
    )
    axes = list(axes.flatten()) if hasattr(axes, "flatten") else [axes]
    for ax in axes[n:]:
        ax.set_visible(False)
    return fig, axes


def _style_for(name: str) -> dict[str, Any]:
    """Style for a trace, matched on the first word of its name."""
    key = name.strip().lower().split(" ")[0] if name else ""
    return dict(_TRACE_STYLES.get(key, {}))


def _draw_plot(ax, plot: PlotConfig, *, equal_aspect: bool = False) -> None:
    """Draw one config's traces onto ``ax``, styled by trace label."""
    for trace in plot.traces:
        # A population-based fit has no single initial guess worth drawing.
        if trace.label.strip().lower().startswith("initial"):
            continue
        style = _style_for(trace.label)
        if trace.color:
            style["color"] = trace.color
        # None checks, not truthiness — a numpy array is neither.
        ax.plot(
            [] if trace.x is None else trace.x,
            [] if trace.y is None else trace.y,
            label=trace.label or None,
            **style,
        )

    if plot.x_label:
        ax.set_xlabel(plot.x_label)
    if plot.y_label:
        ax.set_ylabel(plot.y_label)
    if plot.x_range is not None:
        ax.set_xlim(*plot.x_range)
    if plot.y_range is not None:
        ax.set_ylim(*plot.y_range)
    if equal_aspect:
        # Equal data units, so a Nyquist arc reads as the semicircle it is.
        ax.set_box_aspect(1)
        ax.set_aspect("equal", adjustable="datalim")
    ax.grid(alpha=0.5)
    if ax.get_legend_handles_labels()[0]:
        ax.legend()


def plot_panels(
    plots: list[PlotConfig | dict],
    *,
    equal_aspect: bool = False,
    fig_axes: tuple | None = None,
    n_cols: int | None = None,
    share_x: bool = False,
) -> tuple:
    """Draw one panel per plot config, in a grid.

    Parameters
    ----------
    plots : list of PlotConfig or dict
        The panels, in the order they should appear. A dict is coerced — a
        stored plot payload via :meth:`PlotConfig.from_wire`, otherwise as
        :class:`PlotConfig` fields.
    equal_aspect : bool, optional
        Force a 1:1 data aspect ratio on every panel. Defaults to False.
    fig_axes : tuple, optional
        An existing ``(fig, axes)`` to draw onto, so several datasets can be
        overlaid on shared panels. A new figure is created when omitted.
    n_cols : int, optional
        Column count. Defaults to a roughly square grid. Panels fill row by row,
        so pass it when the order groups panels into columns.
    share_x : bool, optional
        Share the x axis down each column and label only the bottom panel of
        each. Only meaningful with ``n_cols``, which is what puts panels of the
        same quantity in one column. Defaults to False.

    Returns
    -------
    tuple
        ``(fig, axes)`` where ``axes`` is a flat list, one entry per panel.

    Raises
    ------
    ValueError
        If ``plots`` is empty.
    """
    if not plots:
        raise ValueError("No plot data to render.")
    configs = [_as_config(plot) for plot in plots]
    if n_cols is None and len(configs) == 2:
        # A curve and its residual against one quantity: stack under one x axis.
        if configs[0].x_label and configs[0].x_label == configs[1].x_label:
            n_cols, share_x = 1, True
    if fig_axes is None:
        fig, axes = _subplots_autolayout(len(configs), n_cols=n_cols, share_x=share_x)
    else:
        fig, axes = fig_axes
        axes = list(axes) if hasattr(axes, "__len__") else [axes]
    for ax, config in zip(axes, configs, strict=False):
        _draw_plot(ax, config, equal_aspect=equal_aspect)
    if share_x and fig_axes is None and n_cols:
        # Sharing hides the inner rows' tick labels; drop their x label too.
        for i, ax in enumerate(axes[: len(configs)]):
            if i + n_cols < len(configs):
                ax.set_xlabel("")
    return fig, axes[: len(configs)]


def plot_eis(plots: list[PlotConfig | dict], **kwargs) -> tuple:
    """Nyquist plot(s) for an EIS objective.

    Impedance is plotted with an equal aspect ratio: a distorted Nyquist arc
    misrepresents the semicircle a reader is judging.

    Parameters
    ----------
    plots : list of PlotConfig or dict
        The objective's panels.

    Returns
    -------
    tuple
        ``(fig, axes)``.
    """
    return plot_panels(plots, equal_aspect=True, **kwargs)


#: Objective ``type`` discriminator -> renderer, where a panel grid won't do.
_RENDERERS: dict[str, Callable[..., tuple]] = {"EIS": plot_eis}


def render(
    objective_type: str | None, plots: list[PlotConfig | dict], **kwargs
) -> tuple:
    """Draw an objective's plots with the renderer for its type.

    Parameters
    ----------
    objective_type : str or None
        The objective's ``type`` discriminator (e.g. ``"EIS"``). An unknown or
        missing type falls back to a plain panel grid.
    plots : list of PlotConfig or dict
        The objective's panels.

    Returns
    -------
    tuple
        ``(fig, axes)``.

    Raises
    ------
    ValueError
        If ``plots`` is empty.
    """
    return _RENDERERS.get(objective_type or "", plot_panels)(plots, **kwargs)


__all__ = [
    "PlotConfig",
    "PlotTrace",
    "error_label",
    "fit_panels",
    "plot_eis",
    "plot_panels",
    "render",
]
