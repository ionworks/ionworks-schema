"""Tests for AskTellOptimizer algorithm_options typed wrappers."""

from ionworks_schema.parameter_estimators import (
    SOBER,
    AskTellOptimizer,
    BayesianOptimization,
    BayesianOptimizationOptions,
    CMAESOptions,
    DEOptions,
    PSOOptions,
    SOBEROptions,
    TuRBO,
    TuRBOOptions,
)
import pytest


def test_pso_options_omit_unset_fields_and_no_type_field():
    """PSOOptions.to_config drops None fields and does NOT emit a 'type' key
    (the pipeline algorithms reject unknown option keys)."""
    opts = PSOOptions(c1=2.05, c2=2.05)
    cfg = opts.to_config()
    assert cfg == {"c1": 2.05, "c2": 2.05}
    assert "type" not in cfg


def test_de_options_round_trip():
    """DEOptions exposes the documented SHADE options."""
    opts = DEOptions(mutation_strategy="current_to_pbest_1", F=0.5, CR=0.7)
    cfg = opts.to_config()
    assert cfg == {
        "mutation_strategy": "current_to_pbest_1",
        "F": 0.5,
        "CR": 0.7,
    }


def test_cmaes_options_allow_pycma_extra_keys():
    """CMAESOptions accepts arbitrary pycma keys via extra='allow'.

    It is a genuine passthrough leaf (``cma.CMAOptions`` is the source of truth),
    so it stays open while the other ``*Options`` classes are strict.
    """
    opts = CMAESOptions(CMA_diagonal=True, ftarget=1e-8)
    cfg = opts.to_config()
    assert cfg["CMA_diagonal"] is True
    assert cfg["ftarget"] == 1e-8
    assert "type" not in cfg


def test_strict_options_reject_unknown_key():
    """The non-passthrough options classes reject unknown keys (extra='forbid')."""
    from ionworks_schema.parameter_estimators import XNESOptions
    from pydantic import ValidationError

    for options_cls in (
        TuRBOOptions,
        SOBEROptions,
        BayesianOptimizationOptions,
        XNESOptions,
    ):
        with pytest.raises(ValidationError):
            options_cls(definitely_not_an_option=1)


def test_xnes_options_round_trip_through_asktell_optimizer():
    """XNESOptions is exported and round-trips via AskTellOptimizer(method='XNES')."""
    from ionworks_schema.parameter_estimators import XNESOptions

    opt = AskTellOptimizer(method="XNES", algorithm_options=XNESOptions())
    assert opt.to_config()["method"] == "XNES"


def test_bo_only_key_on_de_rejected():
    """A BO-only option key on a native DifferentialEvolution is rejected."""
    from ionworks_schema.parameter_estimators import DifferentialEvolution
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        DifferentialEvolution(algorithm_options={"n_initial": 4})  # BO-only


def test_scipy_de_accepts_native_scipy_kwargs():
    """ScipyDifferentialEvolution forwards scipy's own maxiter/popsize."""
    from ionworks_schema.parameter_estimators import ScipyDifferentialEvolution

    opt = ScipyDifferentialEvolution(maxiter=10, popsize=5)
    assert opt.to_config()["maxiter"] == 10


def test_sober_options_round_trip():
    """SOBEROptions exposes the n_initial and noise_floor knobs."""
    opts = SOBEROptions(n_initial=64, noise_floor="low")
    cfg = opts.to_config()
    assert cfg == {"n_initial": 64, "noise_floor": "low"}
    assert "type" not in cfg


def test_bayesian_optimization_options_round_trip():
    """BayesianOptimizationOptions exposes the noise_floor knob."""
    opts = BayesianOptimizationOptions(noise_floor="deterministic")
    cfg = opts.to_config()
    assert cfg == {"noise_floor": "deterministic"}
    assert "type" not in cfg


def test_sober_options_serialize_through_asktell_optimizer():
    """A SOBEROptions wrapper serialises to the inner option dict."""
    opt = AskTellOptimizer(method="SOBER", algorithm_options=SOBEROptions(n_initial=64))
    cfg = opt.to_config()
    assert cfg["algorithm_options"] == {"n_initial": 64}


def test_algorithm_options_serialize_through_asktell_optimizer():
    """AskTellOptimizer with a typed options wrapper serialises the inner dict,
    not a nested schema with a 'type' discriminator."""
    opt = AskTellOptimizer(method="PSO", algorithm_options=PSOOptions(c1=1.5))
    cfg = opt.to_config()
    assert cfg["method"] == "PSO"
    assert cfg["algorithm_options"] == {"c1": 1.5}


def test_turbo_options_round_trip():
    """TuRBOOptions exposes the trust-region and GP-window knobs."""
    opts = TuRBOOptions(
        noise_floor="low",
        n_initial=500,
        gp_max_points=1000,
        tr_length_init=0.8,
        tr_failure_tolerance=4,
    )
    cfg = opts.to_config()
    assert cfg == {
        "noise_floor": "low",
        "n_initial": 500,
        "gp_max_points": 1000,
        "tr_length_init": 0.8,
        "tr_failure_tolerance": 4,
    }
    assert "type" not in cfg


def test_turbo_options_serialize_through_asktell_optimizer():
    """A TuRBOOptions wrapper serialises to the inner option dict."""
    opt = AskTellOptimizer(
        method="TuRBO",
        algorithm_options=TuRBOOptions(noise_floor="low", n_initial=128),
    )
    cfg = opt.to_config()
    assert cfg["algorithm_options"] == {"noise_floor": "low", "n_initial": 128}


def test_bo_options_declare_only_pipeline_consumed_fields():
    """Every declared BO field must be consumed by the pipeline algorithm.

    The EI-only refactor removed the acquisition/exploration knobs from the
    pipeline; declaring them here would validate-then-silently-ignore them.
    """
    from ionworks_schema.parameter_estimators.parameter_estimators import (
        _AlgorithmOptions,
    )

    own = set(BayesianOptimizationOptions.model_fields) - set(
        _AlgorithmOptions.model_fields
    )
    assert own == {"n_initial", "noise_floor"}


def test_sober_options_declare_only_pipeline_consumed_fields():
    """Every declared SOBER field must be consumed by the pipeline algorithm.

    The acquisition-guided recombination knob was removed from the pipeline;
    declaring acquisition/ucb_beta here would validate-then-silently-ignore.
    ``n_candidates``/``n_nystrom`` are consumed again since the pool-size
    options were plumbed through ``SOBERAlgorithm`` (selection-pressure fix
    for wide batches).
    """
    from ionworks_schema.parameter_estimators.parameter_estimators import (
        _AlgorithmOptions,
    )

    own = set(SOBEROptions.model_fields) - set(_AlgorithmOptions.model_fields)
    assert own == {
        "n_initial",
        "noise_floor",
        "n_candidates",
        "n_nystrom",
        "gp_kernel",
    }


@pytest.mark.parametrize(
    "cls, options_cls",
    [
        (BayesianOptimization, BayesianOptimizationOptions),
        (SOBER, SOBEROptions),
        (TuRBO, TuRBOOptions),
    ],
)
def test_surrogate_convenience_class_emits_method_type(cls, options_cls):
    """The surrogate convenience optimizers emit a ``type`` discriminator (the
    pipeline parser resolves it to ``AskTellOptimizer(method=<name>)``) plus the
    inherited ``_AskTellBase`` defaults, sourced from the shared
    ``ASK_TELL_DEFAULTS`` (single source of truth, also used by the runtime)."""
    from ionworks_schema.parameter_estimators.parameter_estimators import (
        ASK_TELL_DEFAULTS,
    )

    cfg = cls().to_config()
    assert cfg["type"] == cls.__name__
    # Concrete defaults are visible; adaptive (None) ones are omitted.
    assert cfg["absolute_tolerance"] == ASK_TELL_DEFAULTS["absolute_tolerance"]
    assert "max_iterations" not in cfg  # None default → omitted

    cfg_opts = cls(algorithm_options=options_cls(n_initial=8)).to_config()
    assert cfg_opts["type"] == cls.__name__
    assert cfg_opts["algorithm_options"] == {"n_initial": 8}


def test_to_config_carries_only_the_options_the_caller_set():
    """An options leaf must not write its own defaults into a stored config.

    Every field here defaults to None, so the emitted bag stays empty until the
    caller sets something — the algorithm then applies its own defaults.
    """
    assert PSOOptions(c1=1.5).to_config() == {"c1": 1.5}
    assert PSOOptions().to_config() == {}


def test_to_config_preserves_passthrough_extra_keys():
    """CMAESOptions is extra='allow'; pycma keys must survive to_config."""
    assert CMAESOptions(ftarget=1e-9).to_config() == {"ftarget": 1e-9}


def test_to_config_still_emits_no_type_discriminator():
    assert "type" not in PSOOptions(c1=1.5).to_config()


def test_explicit_none_means_use_the_runtime_default():
    """An explicitly-set None is dropped, so the runtime default applies.

    ``Options(x=cfg.get("x"))`` is a realistic way to build a bag, and the
    algorithms coerce their options to numbers — emitting the None would make
    them fail on a value the caller never meant to set.
    """
    assert PSOOptions(c1=None).to_config() == {}
