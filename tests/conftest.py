"""Shared fixtures for the ionworks_schema test suite."""

import ionworks_schema as iws
import pytest


@pytest.fixture
def min_fit():
    """Return a factory building a minimal valid ``DataFit``.

    Used by the optimizer/cost/objective/data_fit contract tests to exercise the
    contract without re-specifying parameters at every call site. Pass
    ``optimizer=``, ``cost=``, and/or ``objectives=`` to set those fields.
    """

    default_objectives = {
        "ocp": iws.objectives.OCPHalfCell(electrode="positive", data_input="file:x.csv")
    }

    def _make(optimizer=None, cost=None, objectives=None):
        extra = {}
        if optimizer is not None:
            extra["optimizer"] = optimizer
        if cost is not None:
            extra["cost"] = cost
        return iws.DataFit(
            objectives=default_objectives if objectives is None else objectives,
            parameters={"x": iws.Parameter("x", initial_value=1.0, bounds=(0.0, 2.0))},
            **extra,
        )

    return _make
