"""Tests for BaseResults plotting: plot_fit_results() and plot_trace()."""

import matplotlib

matplotlib.use("Agg")

from ionworks_schema import BaseResults
import pytest


def _plot(y_label, *, plot_type="model data"):
    return {
        "type": plot_type,
        "traces": [
            {"name": "Data", "x": [0, 1, 2], "y": [3.0, 3.1, 3.2]},
            {"name": "Model", "x": [0, 1, 2], "y": [3.02, 3.09, 3.2]},
        ],
        "layout": {
            "xaxis": {"title": {"text": "Time [s]"}},
            "yaxis": {"title": {"text": y_label}},
        },
    }


def _make_overlay():
    return {
        "voltage": {
            "type": "CurrentDriven",
            "plots": [_plot("Voltage [V]"), _plot("Error [V]", plot_type="error")],
        },
        "temperature": {
            "type": "CurrentDriven",
            "plots": [_plot("Temperature [K]")],
        },
    }


def _make_trace():
    return [
        {
            "best_cost": 10.0,
            "cost": 10.0,
            "inputs_unscaled": {"a": 1.0, "b": 2.0},
        },
        {
            "best_cost": 8.0,
            "cost": 9.0,
            "inputs_unscaled": {"a": 1.2, "b": 1.8},
        },
        {
            "best_cost": 5.0,
            "cost": 5.0,
            "inputs_unscaled": {"a": 1.5, "b": 1.5},
        },
    ]


def test_plot_fit_results_returns_fig_axes_per_objective():
    r = BaseResults()
    r.overlay = _make_overlay()
    result = r.plot_fit_results()
    assert set(result.keys()) == {"voltage", "temperature"}
    # One axes per stored plot, so a multi-panel objective keeps its panels.
    assert len(result["voltage"][1]) == 2
    assert len(result["temperature"][1]) == 1
    # The y label identifies each panel; the objective's name is the suptitle.
    assert [ax.get_ylabel() for ax in result["voltage"][1]] == [
        "Voltage [V]",
        "Error [V]",
    ]


def test_plot_fit_results_skips_objectives_without_plots():
    """An objective the backend stored no plots for is left out rather than
    contributing an empty figure — the ones that do have plots still draw."""
    r = BaseResults()
    r.overlay = {**_make_overlay(), "empty": {"type": "EIS", "plots": []}}
    assert set(r.plot_fit_results()) == {"voltage", "temperature"}


def test_plot_fit_results_raises_when_no_objective_has_plots():
    """Nothing to draw must say so — an empty dict reads as success and leaves
    the caller staring at a blank screen."""
    r = BaseResults()
    r.overlay = {"voltage": {"type": "EIS", "plots": []}}
    with pytest.raises(ValueError, match="nothing to draw"):
        r.plot_fit_results()


def test_plot_fit_results_raises_clear_error_when_overlay_missing():
    r = BaseResults()
    with pytest.raises(ValueError, match="overlay"):
        r.plot_fit_results()


def test_plot_trace_returns_fig_and_axes_per_param():
    r = BaseResults()
    r.trace = _make_trace()
    fig, axes = r.plot_trace()
    assert fig is not None
    # one subplot per parameter ("a", "b") plus the best-cost curve
    assert len(axes) == 3


def test_plot_trace_raises_clear_error_when_trace_missing():
    r = BaseResults()
    with pytest.raises(ValueError, match="trace"):
        r.plot_trace()


def test_plot_fit_results_titles_each_figure_with_its_objective():
    """The objective names the figure, matching how a pipeline fit presents it —
    the panels inside are identified by their axis labels."""
    r = BaseResults()
    r.overlay = _make_overlay()

    figs = r.plot_fit_results()

    assert figs["voltage"][0].get_suptitle() == "voltage"
    assert figs["temperature"][0].get_suptitle() == "temperature"
