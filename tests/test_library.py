"""Tests for ionworks_schema.library.Material strictness (Task D.1)."""

import ionworks_schema as iws
from pydantic import ValidationError
import pytest


def test_material_rejects_unknown_field():
    # Material subclasses BaseModel (not BaseSchema); extra="forbid" is set
    # explicitly so an unknown sibling field is rejected rather than swallowed.
    with pytest.raises(ValidationError):
        iws.library.Material(name="x", bogus=1)


def test_material_accepts_known_fields_and_open_parameter_values():
    material = iws.library.Material(
        name="NMC",
        description="test",
        parameter_values={"Any pybamm key [m]": 1.0, "Another": 2.0},
    )
    assert material.name == "NMC"
    # parameter_values stays an open pybamm parameter set.
    assert material.parameter_values == {"Any pybamm key [m]": 1.0, "Another": 2.0}
