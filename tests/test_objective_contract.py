"""Contract tests for the discriminated ``ObjectiveUnion`` (B.1).

Objectives stay public-API-compatible (positional construction preserved); the
``objectives`` field is a ``type``-discriminated union that dispatches config
dicts to the concrete schema leaf and validates them, so the schema is the
single source of truth at every gate. A ``BeforeValidator`` normalizes the
legacy ``objective``/top-level-``model`` shapes before discrimination.
"""

import ionworks_schema as iws
from pydantic import ValidationError
import pytest


def test_config_dict_resolves_with_objective_alias_and_top_level_model(min_fit):
    fit = min_fit(
        objectives={
            "test": {
                "objective": "CurrentDriven",
                "model": {"type": "SPMe"},
                "data": "file:x.csv",
            }
        }
    )
    obj = fit.objectives["test"]
    assert type(obj).__name__ == "CurrentDriven"
    cfg = fit.to_config()["objectives"]["test"]
    assert cfg["type"] == "CurrentDriven"
    assert cfg["options"]["model"] == {"type": "SPMe"}  # moved into options
    assert cfg["data"] == "file:x.csv"


def test_type_key_also_works(min_fit):
    fit = min_fit(
        objectives={
            "t": {"type": "OCPHalfCell", "electrode": "positive", "data": "file:x.csv"}
        }
    )
    assert type(fit.objectives["t"]).__name__ == "OCPHalfCell"


def test_unknown_objective_type_rejected(min_fit):
    with pytest.raises(ValidationError):
        min_fit(objectives={"t": {"type": "NotARealObjective"}})


def test_missing_discriminator_rejected(min_fit):
    with pytest.raises(ValidationError):
        min_fit(objectives={"t": {"electrode": "positive", "data": "file:x.csv"}})


def test_unknown_inner_key_rejected(min_fit):
    with pytest.raises(ValidationError):
        min_fit(
            objectives={
                "t": {
                    "type": "OCPHalfCell",
                    "electrode": "positive",
                    "data": "file:x.csv",
                    "definitely_not_a_field": 1,
                }
            }
        )


def test_instance_passes_through(min_fit):
    obj = iws.objectives.OCPHalfCell(electrode="positive", data_input="file:x.csv")
    fit = min_fit(objectives={"t": obj})
    assert fit.objectives["t"] is obj


def test_positional_construction_still_works():
    # Public API unchanged: positional construction is preserved.
    obj = iws.objectives.OCPHalfCell("positive", "file:x.csv")
    assert obj.electrode == "positive"


def test_design_objective_passes_through_unvalidated(min_fit):
    # Design-optimization is out of scope for the DataFit/Validation contract:
    # a DesignObjective config passes through as a dict (its open shape is
    # handled by a separate path), not hard-validated against the union.
    cfg = {"type": "DesignObjective", "options": {"actions": {}}, "anything": 1}
    fit = min_fit(objectives={"d": cfg})
    assert fit.objectives["d"] == cfg


def test_design_objective_instance_passes_through(min_fit):
    # The instance form is passed through verbatim too (not just the dict form).
    obj = iws.objectives.DesignObjective(actions={})
    fit = min_fit(objectives={"d": obj})
    assert fit.objectives["d"] is obj


def test_validation_objectives_resolve():
    val = iws.Validation(
        objectives={
            "1C": {
                "objective": "CurrentDriven",
                "data": "file:x.csv",
                "options": {"model": "SPM"},
            }
        },
        summary_stats=[iws.costs.RMSE()],
    )
    assert type(val.objectives["1C"]).__name__ == "CurrentDriven"


def test_array_data_fit_objectives_resolve():
    # ArrayDataFit keys its objectives by independent-variable value (floats,
    # not label strings), so the resolver takes the name-mapping branch against
    # non-string keys.
    fit = iws.ArrayDataFit(
        objectives={
            298.15: {
                "type": "CurrentDriven",
                "data": "file:x.csv",
                "options": {"model": "SPM"},
            },
            313.15: {
                "objective": "CurrentDriven",
                "data": "file:y.csv",
                "options": {"model": "SPM"},
            },
        },
        parameters={"x": iws.Parameter("x", initial_value=1.0, bounds=(0.0, 2.0))},
    )
    assert type(fit.objectives[298.15]).__name__ == "CurrentDriven"
    assert type(fit.objectives[313.15]).__name__ == "CurrentDriven"


def test_experiment_named_objective_is_a_mapping_not_a_bare_objective(min_fit):
    # An experiment label of "objective"/"type" must not be misread as a bare
    # single-objective dict — its value is an objective, not a class-name string.
    obj = iws.objectives.OCPHalfCell(electrode="positive", data_input="file:x.csv")
    fit = min_fit(objectives={"objective": obj})
    assert fit.objectives["objective"] is obj


def test_both_type_and_objective_keys_resolve(min_fit):
    # Carrying both the canonical key and the legacy alias must not trip
    # extra="forbid" — the alias is dropped before validation.
    fit = min_fit(
        objectives={
            "t": {
                "type": "OCPHalfCell",
                "objective": "OCPHalfCell",
                "electrode": "positive",
                "data": "file:x.csv",
            }
        }
    )
    assert type(fit.objectives["t"]).__name__ == "OCPHalfCell"


def test_conflicting_type_and_objective_keys_rejected(min_fit):
    # type and the legacy objective alias disagreeing is a hard error, not a
    # silent "type wins".
    with pytest.raises(ValidationError, match="Conflicting objective discriminators"):
        min_fit(
            objectives={
                "t": {
                    "type": "OCPHalfCell",
                    "objective": "CurrentDriven",
                    "electrode": "positive",
                    "data": "file:x.csv",
                }
            }
        )


@pytest.mark.parametrize(
    "base_type", ["BaseObjective", "FittingObjective", "SimulationObjective"]
)
def test_abstract_base_type_rejected(min_fit, base_type):
    # Abstract bases are not concrete objectives — they must not validate as one.
    with pytest.raises(ValidationError):
        min_fit(objectives={"t": {"type": base_type, "data": "file:x.csv"}})


def test_inherited_cost_round_trips(min_fit):
    # An objective carrying an inherited ``cost`` must survive to_config ->
    # re-validate through the discriminated union (regression: the old
    # narrow-constructor resolver rejected configs with inherited fields).
    obj = iws.objectives.MSMRHalfCell(data_input="file:x.csv", cost=iws.costs.RMSE())
    fit = min_fit(objectives={"m": obj.to_config()})
    resolved = fit.objectives["m"]
    assert type(resolved).__name__ == "MSMRHalfCell"
    assert type(resolved.cost).__name__ == "RMSE"


def test_bare_objective_dict_resolves_to_instance():
    # A single bare objective config (not wrapped in a {name: objective} map)
    # must resolve to a concrete instance and be auto-wrapped under its class
    # name — the resolver must reject the string values so the outer
    # ``dict[str, ...]`` arm fails and the bare-objective arm wins.
    fit = iws.DataFit(
        objectives={
            "type": "CurrentDriven",
            "data": "file:x.csv",
            "options": {"model": "SPM"},
        },
        parameters={"x": iws.Parameter("x", initial_value=1.0, bounds=(0.0, 2.0))},
    )
    assert list(fit.objectives) == ["CurrentDriven"]
    assert type(fit.objectives["CurrentDriven"]).__name__ == "CurrentDriven"


def test_bogus_string_objective_value_rejected(min_fit):
    # A clearly-incorrect value (a bare string, not an objective config/instance)
    # must be rejected, not silently passed through the union.
    with pytest.raises(ValidationError):
        min_fit(objectives={"bad": "not an objective"})


def test_bogus_scalar_objective_value_rejected():
    # Same for a non-string scalar on the Validation surface.
    with pytest.raises(ValidationError):
        iws.Validation(objectives={"bad": 123}, summary_stats=[iws.costs.RMSE()])


@pytest.mark.parametrize("name", ["CurrentDriven", "Pulse", "CycleAgeing", "EIS"])
def test_objective_preserves_positional_options(name):
    # Regression: concrete objectives must still accept the second positional
    # ``options`` argument (was lost when the forwarder __init__s were removed).
    # Checked via the wire form so it holds whether ``options`` is a typed bag
    # (#1423) or still a plain dict.
    obj = getattr(iws.objectives, name)("file:x.csv", {"model": {"type": "SPMe"}})
    assert obj.to_config()["options"] == {"model": {"type": "SPMe"}}


def test_ocp_half_cell_preserves_positional_options():
    # Electrode-leading objectives keep (electrode, data, options) positional.
    obj = iws.objectives.OCPHalfCell(
        "positive", "file:x.csv", {"direction": "lithiation"}
    )
    assert obj.electrode == "positive"
    assert obj.to_config()["options"] == {"direction": "lithiation"}
