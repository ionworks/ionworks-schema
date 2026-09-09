"""Tests for SimplePipeline: construction, validation, and serialization."""

import ionworks_schema as iws
from pydantic import ValidationError
import pytest


def test_importable():
    """SimplePipeline is accessible from the top-level package."""
    assert hasattr(iws, "SimplePipeline")
    assert iws.SimplePipeline is not None


def test_construct_no_elements():
    """SimplePipeline with None elements succeeds (inherits Pipeline behavior)."""
    sp = iws.SimplePipeline()
    cfg = sp.to_config()
    assert cfg["elements"] == {}


def test_construct_empty_elements():
    """SimplePipeline with an empty dict succeeds."""
    sp = iws.SimplePipeline(elements={})
    cfg = sp.to_config()
    assert cfg["elements"] == {}


def test_construct_zero_expensive():
    """Pipeline with only DirectEntry elements (no expensive) is valid."""
    sp = iws.SimplePipeline(
        elements={
            "a": iws.direct_entries.DirectEntry(parameters={"Param A [m]": 1.0}),
            "b": iws.direct_entries.DirectEntry(parameters={"Param B [m]": 2.0}),
        },
    )
    assert len(sp.to_config()["elements"]) == 2


def test_construct_one_datafit():
    """Pipeline with exactly one DataFit is valid."""
    sp = iws.SimplePipeline(
        elements={
            "entry": iws.direct_entries.DirectEntry(parameters={"X [m]": 1.0}),
            "fit": iws.DataFit(
                objectives={},
                parameters={"X [m]": iws.Parameter("X [m]", bounds=(0, 2))},
            ),
        },
        name="one datafit",
    )
    cfg = sp.to_config()
    assert cfg["elements"]["fit"]["element_type"] == "data_fit"
    assert cfg["name"] == "one datafit"


def test_construct_one_validation():
    """Pipeline with exactly one Validation is valid."""
    sp = iws.SimplePipeline(
        elements={
            "val": iws.Validation(objectives={}),
        },
    )
    cfg = sp.to_config()
    assert cfg["elements"]["val"]["element_type"] == "validation"


def test_reject_two_expensive_datafit_and_validation():
    """Two expensive elements (DataFit + Validation) are rejected."""
    with pytest.raises(ValueError, match="at most one"):
        iws.SimplePipeline(
            elements={
                "fit": iws.DataFit(
                    objectives={},
                    parameters={"X [m]": iws.Parameter("X [m]", bounds=(0, 1))},
                ),
                "val": iws.Validation(objectives={}),
            },
        )


def test_reject_two_datafits():
    """Two DataFit elements are rejected."""
    with pytest.raises(ValueError, match="at most one"):
        iws.SimplePipeline(
            elements={
                "fit1": iws.DataFit(
                    objectives={},
                    parameters={"X [m]": iws.Parameter("X [m]", bounds=(0, 1))},
                ),
                "fit2": iws.DataFit(
                    objectives={},
                    parameters={"Y [m]": iws.Parameter("Y [m]", bounds=(0, 1))},
                ),
            },
        )


def test_reject_arraydatafit_and_validation():
    """ArrayDataFit + Validation is rejected."""
    with pytest.raises(ValueError, match="at most one"):
        iws.SimplePipeline(
            elements={
                "fit": iws.ArrayDataFit(
                    objectives={},
                    parameters={"X [m]": iws.Parameter("X [m]", bounds=(0, 1))},
                ),
                "val": iws.Validation(objectives={}),
            },
        )


def test_construct_one_arraydatafit():
    """Pipeline with exactly one ArrayDataFit is valid."""
    sp = iws.SimplePipeline(
        elements={
            "fit": iws.ArrayDataFit(
                objectives={},
                parameters={"X [m]": iws.Parameter("X [m]", bounds=(0, 2))},
            ),
        },
    )
    cfg = sp.to_config()
    assert cfg["elements"]["fit"]["element_type"] == "array_data_fit"


def _raw_data_fit():
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
    }


def _raw_validation():
    return {
        "element_type": "validation",
        "objectives": {
            "ocp": {
                "type": "OCPHalfCell",
                "electrode": "positive",
                "data": "file:x.csv",
            }
        },
    }


def test_reject_two_raw_dict_expensive():
    """Two raw-dict elements with expensive element_type are rejected."""
    with pytest.raises(ValueError, match="at most one"):
        iws.SimplePipeline(
            elements={"fit": _raw_data_fit(), "val": _raw_validation()},
        )


def test_construct_one_raw_dict_expensive():
    """A single raw-dict expensive element alongside an entry is valid."""
    sp = iws.SimplePipeline(
        elements={
            "entry": {"element_type": "entry", "values": {"X [m]": 1.0}},
            "fit": _raw_data_fit(),
        },
    )
    assert len(sp.to_config()["elements"]) == 2


def test_reject_two_expensive_on_reassignment():
    """The constraint re-runs when elements is reassigned post-construction."""
    sp = iws.SimplePipeline(
        elements={
            "fit": iws.DataFit(
                objectives={},
                parameters={"X [m]": iws.Parameter("X [m]", bounds=(0, 1))},
            ),
        },
    )
    with pytest.raises(ValueError, match="at most one"):
        sp.elements = {
            "fit1": iws.DataFit(
                objectives={},
                parameters={"X [m]": iws.Parameter("X [m]", bounds=(0, 1))},
            ),
            "fit2": iws.DataFit(
                objectives={},
                parameters={"Y [m]": iws.Parameter("Y [m]", bounds=(0, 1))},
            ),
        }


def test_to_config_matches_pipeline():
    """SimplePipeline.to_config() produces identical output to Pipeline.to_config()."""
    elements = {
        "entry": iws.direct_entries.DirectEntry(parameters={"X [m]": 1.0}),
        "fit": iws.DataFit(
            objectives={},
            parameters={"X [m]": iws.Parameter("X [m]", bounds=(0, 2))},
        ),
    }
    sp_cfg = iws.SimplePipeline(elements=elements, name="test").to_config()
    p_cfg = iws.Pipeline(elements=elements, name="test").to_config()
    assert sp_cfg == p_cfg


# --- Type-appropriate gate validation: Pipeline vs SimplePipeline (Task E.4) ---


def _e4_data_fit_elem():
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
    }


def test_bad_optimizer_rejected_by_both():
    # Shared contract: the deep before-validator SimplePipeline inherits.
    bad = {
        "elements": {
            "fit": {
                **_e4_data_fit_elem(),
                "optimizer": {"type": "DifferentialEvolution", "popsize": 5},
            }
        }
    }
    with pytest.raises(ValidationError):
        iws.Pipeline.model_validate(bad)
    with pytest.raises(ValidationError):
        iws.SimplePipeline.model_validate(bad)


def test_two_expensive_elements_diverge_by_type():
    # Divergence: Pipeline allows many expensive elements; SimplePipeline at most one.
    two = {"elements": {"fit1": _e4_data_fit_elem(), "fit2": _e4_data_fit_elem()}}
    iws.Pipeline.model_validate(two)  # accepted
    with pytest.raises(ValidationError):
        iws.SimplePipeline.model_validate(two)
