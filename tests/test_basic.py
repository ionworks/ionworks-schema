"""Minimal tests for ionworks_schema: import, instantiate, and to_config()."""

import ionworks_schema as iws
from pydantic import ValidationError
import pytest


def test_import_and_version():
    """Public API imports and has __version__."""
    assert hasattr(iws, "__version__")
    assert isinstance(iws.__version__, str)
    assert iws.Pipeline is not None
    assert iws.Validation is not None
    assert iws.DataFit is not None
    assert iws.BaseSchema is not None


def test_pipeline_empty_to_config():
    """Pipeline with no elements serializes to config with empty elements."""
    pipe = iws.Pipeline(elements={})
    cfg = pipe.to_config()
    assert "elements" in cfg
    assert cfg["elements"] == {}


def test_direct_entry_function_schema_to_config():
    """Direct entry from function-style API has name and kwargs in to_config()."""
    entry = iws.direct_entries.average_ocp(electrode="positive")
    cfg = entry.to_config()
    assert cfg["name"] == "average_ocp"
    assert cfg.get("electrode") == "positive"


def test_pipeline_with_entry_has_element_type():
    """Pipeline containing a direct entry serializes element with element_type entry."""
    entry = iws.direct_entries.average_ocp(electrode="negative")
    pipe = iws.Pipeline(elements={"ocp": entry})
    cfg = pipe.to_config()
    assert "elements" in cfg
    assert "ocp" in cfg["elements"]
    assert cfg["elements"]["ocp"]["element_type"] == "entry"
    assert cfg["elements"]["ocp"]["name"] == "average_ocp"


def test_validation_to_config():
    """Validation with minimal objectives serializes to config."""
    val = iws.Validation(objectives={})
    cfg = val.to_config()
    assert "objectives" in cfg
    assert cfg["objectives"] == {}


# --- Deep Pipeline.elements validation (Task E.2) ---


def _data_fit_elem(**extra):
    return {
        "element_type": "data_fit",
        "objectives": {
            "ocp": {
                "type": "OCPHalfCell",
                "electrode": "positive",
                "data": "file:x.csv",
            }
        },
        "parameters": {"x": {"initial_value": 1.0, "bounds": [0.0, 2.0]}},
        **extra,
    }


def test_pipeline_deep_validates_on_reassignment():
    # Deep validation must run on `pipeline.elements = {...}`, not just
    # construction (the resolver is a field validator, so it re-runs).
    p = iws.Pipeline.model_validate({"elements": {"fit": _data_fit_elem()}})
    with pytest.raises(ValidationError):
        p.elements = {
            "fit": _data_fit_elem(
                optimizer={"type": "DifferentialEvolution", "popsize": 5}
            )
        }
    # A valid reassignment still resolves dicts to instances.
    p.elements = {"fit": _data_fit_elem()}
    assert isinstance(p.elements["fit"], iws.DataFit)


def test_pipeline_deep_validates_data_fit_optimizer():
    # A native optimizer with the scipy-only `popsize` kwarg must be rejected.
    with pytest.raises(ValidationError):
        iws.Pipeline.model_validate(
            {
                "elements": {
                    "fit": _data_fit_elem(
                        optimizer={"type": "DifferentialEvolution", "popsize": 5}
                    )
                }
            }
        )


def test_arraydatafit_instance_preserved():
    fit = iws.ArrayDataFit(
        objectives={
            298.15: iws.objectives.OCPHalfCell(
                electrode="positive", data_input="file:x.csv"
            )
        },
        parameters={"x": iws.Parameter("x", initial_value=1.0, bounds=(0.0, 2.0))},
    )
    p = iws.Pipeline({"fit": fit})
    assert isinstance(p.elements["fit"], iws.ArrayDataFit)


def test_parallelism_fields_accepted():
    # objective_parallelism is a live DataFit field; the deep gate must accept
    # live fields and reject only unknown keys.
    p = iws.Pipeline.model_validate(
        {"elements": {"fit": _data_fit_elem(objective_parallelism="on")}}
    )
    assert p.elements["fit"].objective_parallelism == "on"


def test_unknown_datafit_field_rejected():
    with pytest.raises(ValidationError):
        iws.Pipeline.model_validate(
            {"elements": {"fit": _data_fit_elem(definitely_not_a_field=4)}}
        )
