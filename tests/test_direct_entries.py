"""Tests for ionworks_schema direct entries (DirectEntry, PiecewiseInterpolation)."""

import ionworks_schema as iws
from ionworks_schema.direct_entries import (
    DirectEntry,
    PiecewiseInterpolation1D,
    PiecewiseInterpolation2D,
)
from pydantic import ValidationError
import pytest


def test_direct_entry_rejects_unknown_field():
    # DirectEntry inherits BaseSchema (extra="forbid"); unknown fields raise.
    with pytest.raises(ValidationError):
        DirectEntry(parameters={"a": 1}, bogus=1)


def test_parameter_rejects_unknown_field():
    # Parameter's custom __init__ has no **kwargs, so an unknown field raises.
    with pytest.raises((ValidationError, TypeError)):
        iws.Parameter("x", initial_value=1.0, bounds=(0.0, 2.0), bogus=1)


def test_direct_entry_to_config():
    """DirectEntry serializes to element_type entry and values."""
    entry = DirectEntry(parameters={"Param [m]": 1.0, "Other": 2.0})
    cfg = entry.to_config()
    assert cfg["element_type"] == "entry"
    assert cfg["values"] == {"Param [m]": 1.0, "Other": 2.0}


def test_direct_entry_with_source():
    """DirectEntry optional source is included when set."""
    entry = DirectEntry(
        parameters={"x": 1.0},
        source="literature",
    )
    cfg = entry.to_config()
    assert cfg["element_type"] == "entry"
    assert cfg["values"] == {"x": 1.0}
    # source may be in config if BaseSchema includes it; DirectEntry.to_config
    # overrides and returns only element_type and values
    assert "values" in cfg


def test_piecewise_interpolation_1d_to_config():
    """PiecewiseInterpolation1D serializes with breakpoints and parameter names."""
    entry = PiecewiseInterpolation1D(
        base_parameter_name="Particle diffusion time [s]",
        breakpoint_values=[0.0, 0.5, 1.0],
        breakpoint_parameter_name="SOC",
    )
    cfg = entry.to_config()
    assert cfg["element_type"] == "entry"
    assert cfg["name"] == "PiecewiseInterpolation1D"
    assert cfg["base_parameter_name"] == "Particle diffusion time [s]"
    assert cfg["breakpoint_values"] == [0.0, 0.5, 1.0]
    assert cfg["breakpoint_parameter_name"] == "SOC"
    assert cfg["smoothing"] == 1e-4
    assert cfg["formulation"] == "knots"


def test_piecewise_interpolation_1d_defaults():
    """PiecewiseInterpolation1D has default smoothing and formulation."""
    entry = PiecewiseInterpolation1D(
        base_parameter_name="D [m2/s]",
        breakpoint_values=[0, 1],
        breakpoint_parameter_name="Temperature [K]",
    )
    assert entry.smoothing == 1e-4
    assert entry.formulation == "knots"


def test_piecewise_interpolation_2d_minimal():
    """PiecewiseInterpolation2D can be constructed with required breakpoint args."""
    entry = PiecewiseInterpolation2D(
        base_parameter_name="Param",
        breakpoint1_values=[0.0, 1.0],
        breakpoint1_parameter_name="x",
        breakpoint2_values=[0.0, 1.0],
        breakpoint2_parameter_name="y",
    )
    assert entry.base_parameter_name == "Param"
    assert entry.breakpoint1_values == [0.0, 1.0]
    assert entry.breakpoint2_values == [0.0, 1.0]


def test_piecewise_interpolation_2d_to_config():
    """PiecewiseInterpolation2D serializes with all breakpoint fields."""
    entry = PiecewiseInterpolation2D(
        base_parameter_name="Diffusivity [m2.s-1]",
        breakpoint1_values=[0.0, 0.5, 1.0],
        breakpoint1_parameter_name="SOC",
        breakpoint2_values=[273.15, 298.15],
        breakpoint2_parameter_name="Temperature [K]",
        smoothing1=1e-4,
        smoothing2=0.1,
        formulation="slopes",
    )
    cfg = entry.to_config()
    assert cfg["element_type"] == "entry"
    assert cfg["name"] == "PiecewiseInterpolation2D"
    assert cfg["base_parameter_name"] == "Diffusivity [m2.s-1]"
    assert cfg["breakpoint1_values"] == [0.0, 0.5, 1.0]
    assert cfg["breakpoint1_parameter_name"] == "SOC"
    assert cfg["breakpoint2_values"] == [273.15, 298.15]
    assert cfg["breakpoint2_parameter_name"] == "Temperature [K]"
    assert cfg["smoothing1"] == 1e-4
    assert cfg["smoothing2"] == 0.1
    assert cfg["formulation"] == "slopes"


def test_direct_entry_with_pipeline_id():
    """DirectEntry with pipeline_id serializes to pipeline_id config."""
    entry = DirectEntry(pipeline_id="abc-123")
    cfg = entry.to_config()
    assert cfg["element_type"] == "entry"
    assert cfg["pipeline_id"] == "abc-123"
    assert "values" not in cfg


def test_direct_entry_pipeline_id_in_pipeline():
    """DirectEntry with pipeline_id is recognized as an entry element in a Pipeline."""
    from ionworks_schema.base import _get_element_type

    entry = DirectEntry(pipeline_id="abc-123")
    assert _get_element_type(entry) == "entry"


def test_direct_entry_rejects_null_parameter_value():
    """None is never a parameter value; it used to serialise straight to the wire."""
    with pytest.raises(ValueError, match="description"):
        DirectEntry(parameters={"description": None, "Electrode height [m]": 0.1})


def test_direct_entry_reload_rejects_a_stored_null():
    """Deliberate: a stored null cannot be loaded through ionworks_schema.

    A null parameter value is invalid in either direction, so reading one back
    is refused as firmly as writing one.
    """
    with pytest.raises(ValidationError, match="description"):
        DirectEntry.model_validate({"parameters": {"description": None}})


def test_pipeline_reload_rejects_a_stored_null():
    """Deliberate: the reload path a stored pipeline config takes also refuses."""
    with pytest.raises(ValidationError, match="description"):
        iws.Pipeline(
            {"known": {"element_type": "entry", "values": {"description": None}}}
        )
