"""Tests for ionworks_schema data_fit (DataFit, ArrayDataFit)."""

import pytest
from ionworks_schema.data_fit import ArrayDataFit, DataFit
from ionworks_schema.objectives import FittingObjective


def test_data_fit_requires_parameters_or_priors():
    """DataFit model validator requires either parameters or priors."""
    obj = FittingObjective(data_input="data.csv")
    with pytest.raises(ValueError, match="Either 'parameters' or 'priors'"):
        DataFit(objectives={"fit1": obj}, source="test")
    with pytest.raises(ValueError, match="Only one of"):
        DataFit(
            objectives={"fit1": obj},
            source="test",
            parameters={"k": 1.0},
            priors=[{"param": "x", "mean": 0, "std": 1}],
        )


def test_data_fit_minimal_with_parameters():
    """DataFit with objectives and parameters serializes."""
    obj = FittingObjective(data_input="data.csv")
    df = DataFit(
        objectives={"fit1": obj},
        source="test source",
        parameters={"x": 1.0},
    )
    cfg = df.to_config()
    assert "objectives" in cfg
    assert "source" in cfg
    assert cfg["source"] == "test source"
    assert cfg.get("parameters") == {"x": 1.0}


def test_data_fit_minimal_with_priors():
    """DataFit with objectives and priors (non-empty) is valid."""
    obj = FittingObjective(data_input="data.csv")
    df = DataFit(
        objectives={"fit1": obj},
        source="test",
        priors=[{"param": "Normal", "mean": 0, "std": 1}],
    )
    cfg = df.to_config()
    assert "objectives" in cfg
    assert cfg.get("priors") is not None


def test_data_fit_to_config_includes_objectives():
    """DataFit to_config serializes nested objectives."""
    obj = FittingObjective(data_input="path.csv", options={"key": "value"})
    df = DataFit(objectives={"obj1": obj}, source="", parameters={"p": 1})
    cfg = df.to_config()
    assert "objectives" in cfg
    # Nested schema should be serialized (e.g. to dict with data key)
    objs = cfg["objectives"]
    assert "obj1" in objs
    assert objs["obj1"].get("data") == "path.csv"


def test_array_data_fit_requires_objectives():
    """ArrayDataFit requires objectives dict."""
    with pytest.raises(Exception):  # Pydantic ValidationError
        ArrayDataFit(objectives=None)
    with pytest.raises(Exception):
        ArrayDataFit()


def test_array_data_fit_minimal():
    """ArrayDataFit with objectives dict serializes (inherits DataFit validator: needs parameters or priors)."""
    obj = FittingObjective(data_input="data.csv")
    adf = ArrayDataFit(objectives={"T1": obj}, parameters={"p": 1.0})
    cfg = adf.to_config()
    assert "objectives" in cfg
    assert "T1" in cfg["objectives"]


def test_array_data_fit_multiple_temperatures():
    """ArrayDataFit can hold multiple objectives keyed by independent variable."""
    obj1 = FittingObjective(data_input="T1.csv")
    obj2 = FittingObjective(data_input="T2.csv")
    adf = ArrayDataFit(
        objectives={"298.15": obj1, "318.15": obj2},
        parameters={"p": 1.0},
    )
    cfg = adf.to_config()
    assert set(cfg["objectives"].keys()) == {"298.15", "318.15"}
