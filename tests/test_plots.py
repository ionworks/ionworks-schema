"""Tests for the per-objective matplotlib renderers in ``ionworks_schema.plots``."""

import matplotlib

matplotlib.use("Agg")

from ionworks_schema import plots
import pytest


def _plot(
    *, plot_type="model data", x_label="Time [s]", y_label="Voltage [V]", names=None
):
    names = names if names is not None else ["Data", "Model"]
    return {
        "type": plot_type,
        "traces": [
            {"name": name, "x": [0.0, 1.0, 2.0], "y": [3.0, 3.1, 3.2]} for name in names
        ],
        "layout": {
            "xaxis": {"title": {"text": x_label}},
            "yaxis": {"title": {"text": y_label}},
        },
    }


def test_panels_one_axes_per_plot_with_labels_and_traces():
    fig, axes = plots.plot_panels(
        [_plot(), _plot(plot_type="error", y_label="Error [V]")]
    )
    assert fig is not None
    assert len(axes) == 2
    # Both panels are against time, so they stack under one x axis; the y
    # labels tell them apart and no panel title repeats them.
    assert [ax.get_ylabel() for ax in axes] == ["Voltage [V]", "Error [V]"]
    assert [ax.get_xlabel() for ax in axes] == ["", "Time [s]"]
    assert not any(ax.get_title() for ax in axes)
    assert len(axes[0].get_lines()) == 2
    assert [t.get_text() for t in axes[0].get_legend().get_texts()] == ["Data", "Model"]


def test_panels_keep_their_own_x_when_the_quantity_differs():
    """A curve and its inverse differential are against different quantities, so
    they must not be forced onto one shared x axis."""
    fig, axes = plots.plot_panels(
        [_plot(), _plot(x_label="dQ/dU [A.h/V]", y_label="Voltage [V]")]
    )
    assert [ax.get_xlabel() for ax in axes] == ["Time [s]", "dQ/dU [A.h/V]"]
    assert not axes[0].get_shared_x_axes().joined(axes[0], axes[1])


def test_initial_trace_is_dropped():
    """Population-based fits have no single meaningful starting point, so an
    ``initial`` trace is not drawn even when the payload carries one."""
    fig, axes = plots.plot_panels([_plot(names=["Data", "Initial", "Model"])])
    assert [line.get_label() for line in axes[0].get_lines()] == ["Data", "Model"]


def test_data_and_model_are_styled_apart():
    fig, axes = plots.plot_panels([_plot()])
    data_line, model_line = axes[0].get_lines()
    assert data_line.get_marker() == "o"
    assert data_line.get_linestyle() == "None"
    assert model_line.get_marker() == "None"
    assert model_line.get_linestyle() == "-"


def test_eis_uses_equal_aspect():
    """A distorted Nyquist arc misrepresents the semicircle being judged."""
    fig, axes = plots.plot_eis([_plot(x_label="Z_Re [Ohm]", y_label="-Z_Im [Ohm]")])
    assert axes[0].get_aspect() == 1.0


def test_plain_string_axis_titles_are_accepted():
    """The API emits ``{"title": {"text": ...}}``; a plain string must work too."""
    plot = {
        "traces": [{"name": "Data", "x": [0, 1], "y": [1, 2]}],
        "layout": {"xaxis": {"title": "Cycle number"}, "yaxis": {"title": "Capacity"}},
    }
    fig, axes = plots.plot_panels([plot])
    assert axes[0].get_xlabel() == "Cycle number"
    assert axes[0].get_ylabel() == "Capacity"


def test_render_dispatches_on_objective_type():
    """EIS needs the equal-aspect Nyquist; every other type wants a plain grid."""
    _fig, axes = plots.render("EIS", [_plot()])
    assert axes[0].get_aspect() == 1.0

    _fig, axes = plots.render("CycleAgeing", [_plot()])
    assert axes[0].get_aspect() == "auto"


@pytest.mark.parametrize("objective_type", [None, "SomeFutureObjective"])
def test_render_falls_back_for_unknown_objective_type(objective_type):
    """An objective type this client predates must still plot, not raise — the
    traces carry everything needed to draw the panels."""
    fig, axes = plots.render(objective_type, [_plot()])
    assert len(axes) == 1
    assert len(axes[0].get_lines()) == 2


def test_render_raises_on_no_plots():
    with pytest.raises(ValueError, match="No plot data"):
        plots.render("EIS", [])


def test_share_x_labels_only_the_bottom_of_each_column():
    """A residual stacked under its data panel shares the quantity on x, so only
    the bottom panel of each column carries that axis."""
    configs = [
        _plot(y_label="Capacity"),
        _plot(y_label="Resistance"),
        _plot(plot_type="error", y_label="Error [A.h]"),
        _plot(plot_type="error", y_label="Error [Ohm]"),
    ]
    _fig, axes = plots.plot_panels(configs, n_cols=2, share_x=True)

    assert [ax.get_xlabel() for ax in axes] == ["", "", "Time [s]", "Time [s]"]
    assert axes[0].get_shared_x_axes().joined(axes[0], axes[2])


def test_share_x_keeps_every_column_its_y_ticks():
    """Only x is shared — each column plots a different quantity, so hiding the
    right-hand column's y tick labels would make it unreadable."""
    configs = [_plot(y_label="Capacity"), _plot(y_label="Resistance")]
    _fig, axes = plots.plot_panels(configs, n_cols=2, share_x=True)

    assert all(ax.get_yticklabels() for ax in axes)
    assert [ax.get_ylabel() for ax in axes] == ["Capacity", "Resistance"]
