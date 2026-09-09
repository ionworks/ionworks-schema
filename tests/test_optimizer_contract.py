"""Contract tests for the discriminated optimizer/sampler union."""

from ionworks_schema.parameter_estimators import parameter_estimators as pe
from ionworks_schema.parameter_estimators.parameter_estimators import (
    DifferentialEvolution,
    OptimizerUnion,
)
from pydantic import BaseModel, TypeAdapter, ValidationError
import pytest

_union = TypeAdapter(OptimizerUnion)


def test_de_has_type_and_common_fields():
    de = DifferentialEvolution(max_iterations=50, population_size=12)
    assert de.type == "DifferentialEvolution"
    cfg = de.to_config()
    assert cfg["type"] == "DifferentialEvolution"
    assert cfg["max_iterations"] == 50 and cfg["population_size"] == 12


def test_de_rejects_scipy_only_kwargs():
    with pytest.raises(ValidationError) as exc:
        DifferentialEvolution(popsize=5, maxiter=10)
    msg = str(exc.value)
    assert "popsize" in msg and "maxiter" in msg


@pytest.mark.parametrize(
    "cls_name,type_str",
    [
        ("CMAES", "CMAES"),
        ("PSO", "PSO"),
        ("XNES", "XNES"),
        ("BayesianOptimization", "BayesianOptimization"),
        ("SOBER", "SOBER"),
        ("TuRBO", "TuRBO"),
    ],
)
def test_native_optimizer_has_type(cls_name, type_str):
    obj = getattr(pe, cls_name)()
    assert obj.type == type_str
    assert obj.to_config()["type"] == type_str


@pytest.mark.parametrize(
    "cls_name,type_str",
    [
        ("GridSearch", "GridSearch"),
        ("PointEstimateOptimizer", "PointEstimateOptimizer"),
        ("PointEstimateSampler", "PointEstimateSampler"),
        ("DummyOptimizer", "DummyOptimizer"),
        ("DummySampler", "DummySampler"),
        ("PintsSampler", "PintsSampler"),
    ],
)
def test_sampler_and_noop_has_type(cls_name, type_str):
    obj = getattr(pe, cls_name)()
    assert obj.type == type_str
    assert obj.to_config()["type"] == type_str


def test_optimizers_reject_unknown_key():
    with pytest.raises(ValidationError):
        pe.CMAES(definitely_not_a_real_kwarg=1)


@pytest.mark.parametrize(
    "short_tag,schema_cls",
    [
        ("PointEstimate", "PointEstimateOptimizer"),
        ("Dummy", "DummyOptimizer"),
        ("Pints", "AskTellOptimizer"),
    ],
)
def test_runtime_short_form_tag_accepted_by_union(short_tag, schema_cls, min_fit):
    """The engine/runtime emits short-form optimizer tags (e.g. 'PointEstimate'
    for the class the schema calls 'PointEstimateOptimizer'). The discriminated
    union accepts both so reverse-parsed/round-tripped configs validate; the
    short form resolves to the optimizer variant (matching the engine resolver).
    No schema class was renamed — only the discriminator Literal was widened."""
    fit = min_fit({"type": short_tag})
    assert type(fit.optimizer).__name__ == schema_cls
    # Default serialization is unchanged for schema users (long-form class name).
    assert getattr(pe, schema_cls)().to_config()["type"] == schema_cls


def test_scipy_lsq_linear_has_type():
    assert pe.ScipyLsqLinear().to_config()["type"] == "ScipyLsqLinear"


def test_nested_round_trips_through_union():
    """A serialized Nested config validates through the discriminated union and
    recursively discriminates its children (regression: Nested.__init__ used to
    swallow the ``type`` key, raising TypeError on dict-discrimination)."""
    nested = _union.validate_python(
        {
            "type": "Nested",
            "parameters": ["a"],
            "optimizer": {"type": "CMAES"},
            "inner": {
                "type": "Nested",
                "parameters": ["b"],
                "optimizer": {"type": "ScipyMinimize"},
                "inner": {"type": "ScipyLsqLinear"},
            },
        }
    )
    assert type(nested).__name__ == "Nested"
    assert type(nested.optimizer).__name__ == "CMAES"
    assert type(nested.inner.inner).__name__ == "ScipyLsqLinear"


def test_nested_rejects_invalid_child():
    with pytest.raises(ValidationError):
        _union.validate_python(
            {
                "type": "Nested",
                "parameters": ["a"],
                "optimizer": {"type": "NotAnOptimizer"},
                "inner": {"type": "CMAES"},
            }
        )


@pytest.mark.parametrize(
    "sampler_type", ["GridSearch", "DummySampler", "PointEstimateSampler"]
)
@pytest.mark.parametrize("slot", ["optimizer", "inner"])
def test_nested_rejects_samplers(slot, sampler_type):
    """Nested runs each sub-estimator to a point optimum, so a sampler in either
    slot must be rejected at construction, not fail obscurely at run time."""
    config = {
        "type": "Nested",
        "parameters": ["a"],
        "optimizer": {"type": "CMAES"},
        "inner": {"type": "ScipyLeastSquares"},
    }
    config[slot] = {"type": sampler_type}
    with pytest.raises(ValidationError, match="sampler"):
        _union.validate_python(config)


def test_nested_accepts_optimizers_in_both_slots():
    """The validator must not reject genuine optimizers (no false positives)."""
    pe.Nested(
        parameters=["a"],
        optimizer=pe.CMAES(),
        inner=pe.ScipyLeastSquares(),
    )


def test_async_mode_rejected():
    with pytest.raises(ValidationError):
        pe.DifferentialEvolution(async_mode=True)
    with pytest.raises(TypeError):
        pe.AskTellOptimizer(method="DifferentialEvolution", async_mode=True)


def test_method_string_validates_options():
    pe.AskTellOptimizer(method="DifferentialEvolution", algorithm_options={"F": 0.5})
    with pytest.raises(ValidationError):
        pe.AskTellOptimizer(
            method="DifferentialEvolution", algorithm_options={"n_initial": 4}
        )
    with pytest.raises(ValidationError):
        pe.AskTellOptimizer(method="NotAMethod")


class TestLegacyPintsTag:
    """``"Pints"`` is the wire tag for the ask/tell optimizer, not the sampler.

    The runtime resolves it to an ``AskTellOptimizer`` alias and the app has
    always emitted it for Nelder-Mead, so the contract must agree.
    """

    @staticmethod
    def _validate(payload):
        class Wrapper(BaseModel):
            optimizer: OptimizerUnion

        return Wrapper(optimizer=payload).optimizer

    def test_pints_tag_resolves_to_the_ask_tell_optimizer(self):
        opt = self._validate({"type": "Pints", "method": "Nelder-Mead", "sigma0": 0.1})
        assert isinstance(opt, pe.AskTellOptimizer)
        assert opt.method == "Nelder-Mead"
        assert opt.sigma0 == 0.1

    def test_pints_tag_canonicalises_to_the_class_name(self):
        """Stored configs should converge on the canonical spelling."""
        cfg = pe.AskTellOptimizer(type="Pints", method="Nelder-Mead").to_config()
        assert cfg["type"] == "AskTellOptimizer"

    def test_pints_sampler_keeps_its_own_tag(self):
        assert pe.PintsSampler(type="PintsSampler").type == "PintsSampler"

    def test_pints_sampler_no_longer_claims_the_pints_tag(self):
        with pytest.raises(ValidationError):
            pe.PintsSampler.model_validate({"type": "Pints"})
