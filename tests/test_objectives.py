"""Tests for ionworks_schema objectives."""

import pytest
from ionworks_schema.objectives import (
    BaseObjective,
    FittingObjective,
    Pulse,
    SimulationObjective,
)


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
    obj = FittingObjective(data_input="data.csv")
    assert obj.data_input == "data.csv"


def test_fitting_objective_to_config_maps_data_input_to_data():
    """FittingObjective to_config outputs 'data' key for parser compatibility."""
    obj = FittingObjective(data_input="path/to/data.csv")
    cfg = obj.to_config()
    assert "data" in cfg
    assert cfg["data"] == "path/to/data.csv"


def test_fitting_objective_with_options():
    """FittingObjective accepts options and serializes them."""
    obj = FittingObjective(
        data_input="data.csv",
        options={"model": None},
        custom_parameters={"x": 1.0},
    )
    cfg = obj.to_config()
    assert cfg.get("options") == {"model": None}
    assert cfg.get("custom_parameters") == {"x": 1.0}


def test_simulation_objective_inherits_from_fitting():
    """SimulationObjective is a FittingObjective with no extra required fields."""
    obj = SimulationObjective(data_input="data.csv")
    assert isinstance(obj, FittingObjective)
    cfg = obj.to_config()
    assert "data" in cfg
    assert cfg["data"] == "data.csv"


def test_pulse_objective_minimal():
    """Pulse (SimulationObjective subclass) requires only data_input and serializes."""
    obj = Pulse(data_input="pulse_data.csv")
    cfg = obj.to_config()
    assert cfg.get("data") == "pulse_data.csv"
    assert "type" in cfg
