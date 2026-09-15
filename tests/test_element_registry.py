"""Contract tests for the package-wide element resolver (Task E.1)."""

import ionworks_schema as iws
from ionworks_schema._element_registry import (
    canonicalize_element_type,
    schema_class_for,
    validate_element,
)
from pydantic import ValidationError
import pytest


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("Direct Entry", "entry"),
        ("Data Fit", "data_fit"),
        ("Array Data Fit", "array_data_fit"),
        ("Calculation", "calculation"),
        ("Validation", "validation"),
        ("datafit", "data_fit"),
        ("arraydatafit", "array_data_fit"),
        # canonical values pass through unchanged
        ("entry", "entry"),
        ("data_fit", "data_fit"),
    ],
)
def test_canonicalize_element_type(raw, expected):
    assert canonicalize_element_type(raw) == expected


def test_canonicalize_element_type_rejects_unknown():
    with pytest.raises(ValueError):
        canonicalize_element_type("frobnicate")


@pytest.mark.parametrize("raw", [["data_fit"], {"type": "data_fit"}, 5, None])
def test_canonicalize_element_type_rejects_non_string(raw):
    """Unhashable input must raise ValueError, not TypeError.

    Callers translate ValueError into a client-facing error; a TypeError from
    the alias lookup would escape that translation as a server error.
    """
    with pytest.raises(ValueError):
        canonicalize_element_type(raw)


def test_canonicalize_element_type_is_exported():
    assert iws.canonicalize_element_type is canonicalize_element_type


def test_resolves_calculation_by_type():
    obj = validate_element({"element_type": "calculation", "type": "CellMass"})
    assert isinstance(obj, iws.calculations.CellMass)


def test_resolves_calculation_legacy_alias():
    obj = validate_element({"element_type": "calculation", "calculation": "CellMass"})
    assert isinstance(obj, iws.calculations.CellMass)


def test_unknown_element_type_rejected():
    with pytest.raises(ValueError):
        validate_element({"element_type": "frobnicate"})


def test_unknown_calculation_type_rejected():
    with pytest.raises(ValueError):
        validate_element({"element_type": "calculation", "type": "NotACalc"})


def test_resolves_data_fit_and_validation():
    fit = validate_element(
        {
            "element_type": "data_fit",
            "objectives": {
                "ocp": {
                    "type": "OCPHalfCell",
                    "electrode": "positive",
                    "data": "file:x.csv",
                }
            },
            "parameters": {"x": {"initial_value": 1.0, "bounds": [0.0, 2.0]}},
        }
    )
    assert isinstance(fit, iws.DataFit)
    val = validate_element(
        {
            "element_type": "validation",
            "objectives": {
                "ocp": {
                    "type": "OCPHalfCell",
                    "electrode": "positive",
                    "data": "file:x.csv",
                }
            },
        }
    )
    assert isinstance(val, iws.Validation)


def test_resolves_entry_shapes():
    values = validate_element({"element_type": "entry", "values": {"P [m]": 1.0}})
    assert isinstance(values, iws.direct_entries.DirectEntry)
    assert values.parameters == {"P [m]": 1.0}
    pid = validate_element({"element_type": "entry", "pipeline_id": "abc"})
    assert pid.pipeline_id == "abc"


def test_entry_function_name_resolves_and_rejects_unknown():
    bruggeman = validate_element({"element_type": "entry", "name": "bruggeman"})
    assert type(bruggeman).__name__ == "Bruggeman"
    with pytest.raises(ValueError):
        validate_element({"element_type": "entry", "name": "not_a_function"})


def test_entry_requires_a_recognised_shape():
    with pytest.raises(ValueError):
        validate_element({"element_type": "entry"})


def test_basemodel_instance_passes_through():
    fit = iws.ArrayDataFit(
        objectives={
            298.15: iws.objectives.OCPHalfCell(
                electrode="positive", data_input="file:x.csv"
            )
        },
        parameters={"x": iws.Parameter("x", initial_value=1.0, bounds=(0.0, 2.0))},
    )
    assert validate_element(fit) is fit


def test_unknown_data_fit_field_rejected():
    # DataFit's custom __init__ raises TypeError on an unknown field; the
    # resolver surfaces it as ValueError (the Pipeline gate wraps it further).
    with pytest.raises((ValueError, ValidationError)):
        validate_element(
            {
                "element_type": "data_fit",
                "definitely_not_a_field": 1,
                "objectives": {
                    "ocp": {
                        "type": "OCPHalfCell",
                        "electrode": "positive",
                        "data": "file:x.csv",
                    }
                },
                "parameters": {"x": {"initial_value": 1.0, "bounds": [0.0, 2.0]}},
            }
        )


def test_entry_values_preserves_source_and_rejects_extra_keys():
    entry = validate_element(
        {"element_type": "entry", "values": {"P [m]": 1.0}, "source": "datasheet"}
    )
    assert entry.source == "datasheet"
    with pytest.raises((ValueError, ValidationError)):
        validate_element({"element_type": "entry", "values": {"P": 1.0}, "typo": 1})


def test_entry_path_rejects_extra_keys():
    with pytest.raises((ValueError, ValidationError)):
        validate_element({"element_type": "entry", "path": "x.json", "typo": 1})


def test_schema_class_for_shared_lookup():
    assert schema_class_for("data_fit") is iws.DataFit
    assert schema_class_for("calculation", "CellMass") is iws.calculations.CellMass
    assert schema_class_for("entry") is None


def test_abstract_calculation_base_rejected():
    # The abstract ``Calculation`` base passes ``issubclass`` but isn't a real
    # calculation type — it must not resolve.
    with pytest.raises(ValueError):
        schema_class_for("calculation", "Calculation")


def test_abstract_entry_function_base_not_resolved():
    # The abstract function-schema base must not resolve as an entry name.
    from ionworks_schema._element_registry import entry_schema_for_name

    assert entry_schema_for_name("DirectEntryFunctionSchema") is None


@pytest.mark.parametrize("bad", [None, 5, "x", [1, 2]])
def test_non_dict_element_value_rejected(bad):
    # A builtin element value (None/int/str/list) is never a valid element —
    # reject it rather than passing it through unvalidated.
    with pytest.raises((ValueError, ValidationError)):
        validate_element(bad)
