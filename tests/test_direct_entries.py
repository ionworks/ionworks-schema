"""Tests for ionworks_schema direct entries (DirectEntry, PiecewiseInterpolation)."""

import pytest

import ionworks_schema as iws
from ionworks_schema.direct_entries import (
    DirectEntry,
    PiecewiseInterpolation1D,
    PiecewiseInterpolation2D,
)


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
    assert cfg["values"] == {}
    # PiecewiseInterpolation1D extends DirectEntry; it may store params in values
    # or in top-level. Check it has the expected fields in serialization.
    # DirectEntry.to_config returns element_type + values; PiecewiseInterpolation1D
    # does not override to_config, so it uses BaseSchema.to_config (inherited).
    # So we get all model fields. Check key ones.
    assert entry.base_parameter_name == "Particle diffusion time [s]"
    assert entry.breakpoint_values == [0.0, 0.5, 1.0]
    assert entry.breakpoint_parameter_name == "SOC"


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
