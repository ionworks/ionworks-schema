import ionworks_schema as iws
from ionworks_schema import canonicalize_element_type
from ionworks_schema._element_registry import schema_class_for
import pytest


def test_pipeline_to_config_emits_element_type_for_analysis():
    # Pipeline.to_config must stamp the wire element_type for analysis elements;
    # without it the backend's create loop KeyErrors popping "element_type".
    params = {"D": {"initial_value": 1.0, "bounds": [0.1, 10]}}
    pipeline = iws.Pipeline(
        elements={
            "ci": iws.LinearConfidenceInterval(objectives={}, parameters=params),
            "sobol": iws.SobolSensitivity(objectives={}, parameters=params),
        }
    )
    elements = pipeline.to_config()["elements"]
    assert elements["ci"]["element_type"] == "linear_confidence_interval"
    assert elements["sobol"]["element_type"] == "sobol_sensitivity"
    # Analysis elements are identified by element_type, not a "type" discriminator
    # (like DataFit); a leaked "type" is rejected by the worker's parser.
    assert "type" not in elements["ci"]
    assert "type" not in elements["sobol"]


def test_non_default_subclass_fields_survive_construction():
    # Guards the DataFit.__init__ subclass-field forwarding: a non-default
    # analysis field must survive both direct construction and model_validate.
    params = {"D": {"initial_value": 1.0, "bounds": [0.1, 10]}}
    ci = iws.LinearConfidenceInterval(
        objectives={}, parameters=params, confidence_level=0.9
    )
    assert ci.confidence_level == 0.9
    assert (
        iws.LinearConfidenceInterval.model_validate(ci.model_dump()).confidence_level
        == 0.9
    )
    s = iws.SobolSensitivity(objectives={}, parameters=params, n_samples=128)
    assert s.n_samples == 128


def test_authoring_classes_exist_and_default():
    ci = iws.LinearConfidenceInterval(
        objectives={}, parameters={"D": {"initial_value": 1.0, "bounds": [0.1, 10]}}
    )
    assert ci.confidence_level == 0.95
    assert ci.gauss_newton is True
    s = iws.SobolSensitivity(
        objectives={}, parameters={"D": {"initial_value": 1.0, "bounds": [0.1, 10]}}
    )
    assert s.n_samples == 256
    assert s.calc_second_order is False


def test_registry_resolves_new_types():
    assert (
        canonicalize_element_type("linear_confidence_interval")
        == "linear_confidence_interval"
    )
    assert canonicalize_element_type("sobol_sensitivity") == "sobol_sensitivity"
    assert (
        schema_class_for("linear_confidence_interval") is iws.LinearConfidenceInterval
    )
    assert schema_class_for("sobol_sensitivity") is iws.SobolSensitivity


def test_optimizer_rejected():
    with pytest.raises(ValueError, match="PointEstimate"):
        iws.LinearConfidenceInterval(
            objectives={},
            parameters={"D": {"initial_value": 1.0, "bounds": [0.1, 10]}},
            optimizer={"type": "CMAES"},
        )
