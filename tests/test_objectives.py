"""Tests for ionworks_schema objectives."""

import ionworks_schema as iws
from ionworks_schema.objectives import (
    BaseObjective,
    CurrentDriven,
    FittingObjective,
    Pulse,
    SimulationObjective,
)
import pybamm
from pydantic import ValidationError
import pytest


def test_base_objective_to_config():
    """BaseObjective serializes optional fields."""
    obj = BaseObjective()
    cfg = obj.to_config()
    assert isinstance(cfg, dict)
    assert "type" in cfg
    assert cfg["type"] == "BaseObjective"


def test_fitting_objective_requires_data_input():
    """FittingObjective requires data_input."""
    with pytest.raises(Exception):  # Pydantic ValidationError
        FittingObjective()
    obj = FittingObjective(data_input="file:data.csv")
    assert obj.data_input == "file:data.csv"


def test_fitting_objective_to_config_maps_data_input_to_data():
    """FittingObjective to_config outputs 'data' key for parser compatibility."""
    obj = FittingObjective(data_input="file:path/to/data.csv")
    cfg = obj.to_config()
    assert "data" in cfg
    assert cfg["data"] == "file:path/to/data.csv"


def test_fitting_objective_with_options():
    """FittingObjective accepts options and serializes them."""
    obj = FittingObjective(
        data_input="file:data.csv",
        options={"model": None},
        custom_parameters={"x": 1.0},
    )
    cfg = obj.to_config()
    assert cfg.get("options") == {"model": None}
    assert cfg.get("custom_parameters") == {"x": 1.0}


def test_simulation_objective_inherits_from_fitting():
    """SimulationObjective is a FittingObjective with no extra required fields."""
    obj = SimulationObjective(data_input="file:data.csv", options={"model": "SPM"})
    assert isinstance(obj, FittingObjective)
    cfg = obj.to_config()
    assert "data" in cfg
    assert cfg["data"] == "file:data.csv"


def test_pulse_objective_minimal():
    """Pulse (SimulationObjective subclass) requires data_input and a model."""
    obj = Pulse(data_input="file:pulse_data.csv", options={"model": "SPM"})
    cfg = obj.to_config()
    assert cfg.get("data") == "file:pulse_data.csv"
    assert "type" in cfg


@pytest.mark.parametrize("cls", [CurrentDriven, Pulse])
@pytest.mark.parametrize("value", [True, False])
def test_interactive_preprocessing_rejected(cls, value):
    """Setting interactive_preprocessing raises — local-only pipeline feature."""
    with pytest.raises(ValueError, match="interactive_preprocessing"):
        cls(data_input="file:data.csv", options={"interactive_preprocessing": value})


def test_objective_rejects_null_parameter_value():
    """BaseObjective serialises parameters only in to_config, so guard __init__."""
    with pytest.raises(ValueError, match="Ambient temperature"):
        iws.objectives.CurrentDriven(
            data_input="file:cycle_1C.csv",
            options={"model": "SPM"},
            parameters={"Ambient temperature [K]": None},
        )


def test_objective_rejects_null_parameter_value_in_parameter_values():
    """A ``pybamm.ParameterValues`` carrying a null must be caught too.

    It satisfies ``ParameterValuesLike`` but registers as neither ``dict`` nor
    ``Mapping``, so only a duck-typed guard sees inside it.
    """
    with pytest.raises(ValueError, match="'x'"):
        iws.objectives.CurrentDriven(
            data_input="file:cycle_1C.csv",
            options={"model": "SPM"},
            parameters=pybamm.ParameterValues({"x": None}),
        )


def test_objective_rejects_null_custom_parameter_value():
    """custom_parameters is a deprecated alias for parameters and gets the same
    null check -- it is never routed through serialize_parameters in
    to_config, so it needs its own call to the null guard.
    """
    with pytest.raises(ValueError, match="'x'"):
        iws.objectives.CurrentDriven(
            data_input="file:cycle_1C.csv",
            options={"model": "SPM"},
            custom_parameters={"x": None},
        )


@pytest.mark.parametrize("cls", [CurrentDriven, Pulse])
def test_options_without_interactive_preprocessing_accepted(cls):
    """Other option keys still pass validation."""
    obj = cls(
        data_input="file:data.csv", options={"interpolant_atol": 1e-7, "model": "SPM"}
    )
    assert obj.to_config()["options"] == {"interpolant_atol": 1e-7, "model": "SPM"}


SIMULATION_OBJECTIVES = [
    "CalendarAgeing",
    "CurrentDriven",
    "CycleAgeing",
    "EIS",
    "Pulse",
]


@pytest.mark.parametrize("name", SIMULATION_OBJECTIVES)
def test_simulation_objective_requires_a_model(name):
    """Without a model the objective fails only at run time, deep in the job."""
    cls = getattr(iws.objectives, name)
    with pytest.raises(ValidationError, match="model"):
        cls(data_input="file:cycle_1C.csv")


@pytest.mark.parametrize("name", SIMULATION_OBJECTIVES)
def test_simulation_objective_rejects_an_explicit_none_model(name):
    cls = getattr(iws.objectives, name)
    with pytest.raises(ValidationError, match="model"):
        cls(data_input="file:cycle_1C.csv", options={"model": None})


@pytest.mark.parametrize("name", SIMULATION_OBJECTIVES)
def test_simulation_objective_accepts_a_model(name):
    cls = getattr(iws.objectives, name)
    obj = cls(data_input="file:cycle_1C.csv", options={"model": "SPM"})
    assert obj.options.model == "SPM"


@pytest.mark.parametrize("name", SIMULATION_OBJECTIVES)
def test_simulation_objective_accepts_a_parameterized_model_id(name):
    """Studio sends this instead of a model; the backend resolves it at job time."""
    cls = getattr(iws.objectives, name)
    obj = cls(
        data_input="file:cycle_1C.csv", options={"parameterized_model_id": "abc-123"}
    )
    assert obj.to_config()["options"] == {"parameterized_model_id": "abc-123"}


def test_design_objective_still_needs_no_model():
    """A design template is model-agnostic until a user instantiates it (#1482)."""
    obj = iws.objectives.DesignObjective(actions={})
    assert (obj.options or {}).get("model") is None
