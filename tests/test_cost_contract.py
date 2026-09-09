"""Contract tests for the discriminated cost union + scale-alias removal."""

import re

import ionworks_schema as iws
from ionworks_schema.objective_functions.objective_functions import CostUnion
from pydantic import TypeAdapter, ValidationError
import pytest

_cost_adapter = TypeAdapter(CostUnion)


@pytest.mark.parametrize(
    "name",
    [
        "RMSE",
        "MAE",
        "MSE",
        "Max",
        "SSE",
        "Wasserstein",
        "ChiSquare",
        "MultiCost",
        "GaussianLogLikelihood",
        "DesignFunction",
    ],
)
def test_cost_leaf_has_type_discriminator(name):
    # Assert the discriminator default on the class (some leaves require
    # constructor args, so don't instantiate).
    assert getattr(iws.costs, name).model_fields["type"].default == name


def test_constructible_cost_emits_type():
    assert iws.costs.RMSE(normalization="mean").to_config()["type"] == "RMSE"


def test_cost_dict_discriminates():
    cost = _cost_adapter.validate_python({"type": "RMSE", "normalization": "mean"})
    assert type(cost).__name__ == "RMSE"


def test_cost_unknown_key_rejected():
    with pytest.raises(ValidationError):
        iws.costs.RMSE(bogus_key=1)


def test_cost_dict_missing_type_rejected():
    with pytest.raises(ValidationError):
        _cost_adapter.validate_python({"normalization": "mean"})


def test_datafit_cost_dict_valid_string_rejected(min_fit):
    assert min_fit(cost={"type": "RMSE"}).to_config()["cost"]["type"] == "RMSE"
    # A bare name string is rejected (the engine parser can't consume it).
    with pytest.raises(ValidationError):
        min_fit(cost="RMSE")


def test_scale_alias_removed_with_canonical_message():
    with pytest.raises(ValidationError) as exc:
        iws.costs.RMSE(scale="max")
    assert "normalization" in str(exc.value)


def test_constraint_penalty_have_type():
    assert iws.objective_functions.Constraint(fun=1.0).type == "Constraint"
    assert iws.objective_functions.Penalty(fun=1.0).type == "Penalty"


class TestMultiCostGrammar:
    """MultiCost accepts a list of costs (bare, or wrapped in WeightedCost for a
    non-default weight) and rejects malformed input at construction."""

    @pytest.mark.parametrize(
        ("field", "value"),
        [
            ("normalization", "identity"),
            ("nan_values", "mean"),
            ("objective_weights", {"o": 2.0}),
            ("variable_weights", {"v": 2.0}),
        ],
    )
    def test_inherited_tuning_fields_rejected(self, field, value):
        with pytest.raises(ValidationError, match="component costs"):
            iws.costs.MultiCost(costs=[iws.costs.SSE()], **{field: value})

    def test_inherited_tuning_fields_still_allowed_on_components(self):
        mc = iws.costs.MultiCost(costs=[iws.costs.SSE(normalization="identity")])
        assert mc.to_config()["costs"][0]["cost"]["normalization"] == "identity"

    def test_bare_cost_list_roundtrips_to_wire_format(self):
        mc = iws.costs.MultiCost(
            costs=[
                iws.costs.RMSE(normalization=1.0),
                iws.costs.WeightedCost(iws.costs.Max(normalization=1.0), 0.25),
            ]
        )
        assert mc.to_config() == {
            "type": "MultiCost",
            "costs": [
                {"cost": {"normalization": 1.0, "type": "RMSE"}, "weight": 1.0},
                {"cost": {"normalization": 1.0, "type": "Max"}, "weight": 0.25},
            ],
        }

    def test_weighted_cost_positional_construction(self):
        weighted = iws.costs.WeightedCost(iws.costs.Max(), 0.25)
        assert weighted.cost.type == "Max"
        assert weighted.weight == 0.25

    def test_multi_cost_round_trips_through_model_validate(self):
        mc = iws.costs.MultiCost(
            costs=[iws.costs.RMSE(), iws.costs.WeightedCost(iws.costs.Max(), 0.25)]
        )
        rebuilt = iws.costs.MultiCost.model_validate(mc.to_config())
        assert rebuilt.to_config() == mc.to_config()

    @pytest.mark.parametrize(
        ("mc", "expected_costs"),
        [
            pytest.param(
                iws.costs.MultiCost(costs=[iws.costs.RMSE()]),
                [{"cost": {"type": "RMSE"}, "weight": 1.0}],
                id="bare-defaults-to-one",
            ),
            pytest.param(
                iws.costs.MultiCost(
                    costs=[
                        iws.costs.RMSE(),
                        iws.costs.WeightedCost(iws.costs.Max(), 0.25),
                        {"cost": iws.costs.SSE(), "weight": 2.0},
                    ]
                ),
                [
                    {"cost": {"type": "RMSE"}, "weight": 1.0},
                    {"cost": {"type": "Max"}, "weight": 0.25},
                    {"cost": {"type": "SSE"}, "weight": 2.0},
                ],
                id="mixed-bare-weighted-record",
            ),
            pytest.param(
                # .to_config() emits this record shape, so model_validate must keep
                # validating it -- the constructor accepts it too, for round-tripping.
                iws.costs.MultiCost(costs=[{"cost": iws.costs.RMSE(), "weight": 2.0}]),
                [{"cost": {"type": "RMSE"}, "weight": 2.0}],
                id="record-form-alone",
            ),
        ],
    )
    def test_multicost_accepted_forms_give_expected_weights(self, mc, expected_costs):
        """Every accepted MultiCost costs= form serializes to the expected weighted records."""
        assert mc.to_config()["costs"] == expected_costs

    def test_nested_multicost_roundtrips(self):
        inner = iws.costs.MultiCost(costs=[iws.costs.RMSE()])
        outer = iws.costs.MultiCost(costs=[inner])
        assert outer.to_config()["costs"][0]["cost"]["type"] == "MultiCost"

    @pytest.mark.parametrize(
        ("bad_costs", "match", "also_match"),
        [
            pytest.param(
                {"RMSE": 1.0}, "not hashable", "'weight' is optional", id="mapping"
            ),
            pytest.param(
                [{"cost": {"type": "NotACost"}, "weight": 1.0}],
                None,
                None,
                id="unknown-sub-cost-type",
            ),
            pytest.param(
                [{"cost": iws.costs.RMSE(), "wieght": 1.0}],
                None,
                None,
                id="misspelled-weight-key",
            ),
            pytest.param([], None, None, id="empty-costs"),
        ],
    )
    def test_multicost_rejections(self, bad_costs, match, also_match):
        """Every malformed MultiCost costs= input is rejected with a ValidationError."""
        with pytest.raises(ValidationError, match=match) as exc_info:
            iws.costs.MultiCost(costs=bad_costs)
        if also_match:
            assert re.search(also_match, str(exc_info.value))

    @pytest.mark.parametrize("wrap", [False, True], ids=["bare", "wrapped"])
    def test_multicost_repeated_cost_object_rejected(self, wrap):
        """One cost object listed twice is refused, matching the runtime."""
        cost = iws.costs.SSE()
        second = iws.costs.WeightedCost(cost, 0.5) if wrap else cost
        with pytest.raises(ValidationError, match="same cost object"):
            iws.costs.MultiCost(costs=[cost, second])

    def test_multicost_distinct_but_equal_costs_accepted(self):
        """Two separate instances are two components — this is what a config
        validates back to, so identity is what the rejection above keys on."""
        mc = iws.costs.MultiCost(costs=[iws.costs.SSE(), iws.costs.SSE()])
        assert len(iws.costs.MultiCost.model_validate(mc.to_config()).costs) == 2

    def test_multicost_non_numeric_weight_rejected(self):
        with pytest.raises(ValidationError, match="valid number"):
            iws.costs.WeightedCost(iws.costs.RMSE(), weight="heavy")

    def test_weighted_cost_emits_no_type_key(self):
        weighted = iws.costs.WeightedCost(iws.costs.RMSE())
        assert "type" not in weighted.to_config()

    def test_form_hint_is_a_plain_string_not_a_private_attr(self):
        # Without ClassVar, pydantic wraps this and `cls._COSTS_FORM_HINT` in the
        # validator interpolates as `default="..."` instead of the hint itself.
        assert isinstance(iws.costs.MultiCost._COSTS_FORM_HINT, str)

    def test_rejection_message_does_not_leak_the_private_attr_wrapper(self):
        with pytest.raises(ValidationError) as exc:
            iws.costs.MultiCost(costs={"RMSE": 1.0})
        assert 'default="' not in str(exc.value)
        assert "ModelPrivateAttr(" not in repr(exc.value)
