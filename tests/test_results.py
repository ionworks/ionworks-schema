"""Tests for ionworks_schema.results (BaseResults + config round-trip)."""

import ionworks_schema as iws
from ionworks_schema import (
    BaseResults,
    EnsembleResult,
    OptimizationResult,
    ParameterEstimatorResult,
    PassthroughResult,
    PosteriorResult,
    RegressionResult,
    ValidationResult,
    from_config,
)
from ionworks_schema.results import ConfidenceIntervalResult, SensitivityResult
import pytest


def test_base_results_getitem_and_parameter_values():
    r = BaseResults(parameter_values={"a": 1.0})
    assert r["a"] == 1.0
    assert r.parameter_values == {"a": 1.0}


def test_base_results_to_config():
    r = BaseResults(parameter_values={"a": 1.0})
    assert r.to_config() == {
        "type": "element_result",
        "parameter_values": {"a": 1.0},
    }


def test_base_results_config_round_trip():
    r = BaseResults(parameter_values={"a": 1.0, "b": 2.0})
    r2 = from_config(r.to_config())
    assert type(r2) is BaseResults
    assert r2.parameter_values == r.parameter_values
    assert r2.to_config() == r.to_config()


def test_from_config_dispatches_via_registry():
    class DummyResult(BaseResults):
        type = "DummyResult"

    r = DummyResult(parameter_values={"x": 1})
    r2 = from_config(r.to_config())
    assert type(r2) is DummyResult
    assert r2.parameter_values == {"x": 1}


def test_from_config_unknown_type_raises():
    with pytest.raises(ValueError, match="Unknown"):
        from_config({"type": "NotARealType"})


def test_empty_dict_fields_survive_round_trip():
    """An empty (but non-None) dict field must not collapse to None through
    to_config/from_config — the getters distinguish {} from None."""
    r = PosteriorResult(
        parameter_values={"a": 1.0}, r_hat={}, ess={}, posterior_summary={}
    )
    r2 = from_config(r.to_config())
    assert r2.r_hat == {}
    assert r2.ess == {}
    assert r2.posterior_summary == {}


def test_parameter_estimator_result_from_config():
    payload = {
        "type": "ParameterEstimatorResult",
        "parameter_values": {"a": 1.0},
        "cost": 0.5,
        "samples": [[1.0], [2.0]],
        "costs": [0.5, 0.9],
        "initial_guess": {"a": 0.0},
        "job_id": 42,
        "children": None,
    }
    r = from_config(payload)
    assert type(r) is ParameterEstimatorResult
    assert r.type == "ParameterEstimatorResult"
    assert r.cost == 0.5
    assert r.samples == [[1.0], [2.0]]
    assert r.costs == [0.5, 0.9]
    assert r.initial_guess == {"a": 0.0}
    assert r.job_id == 42
    # A leaf stores None (no self-reference — GC safety) but resolves
    # children to [self] on read; to_config emits None for it.
    assert r._children is None
    assert r.children == [r]
    assert r.to_config()["children"] is None


def test_parameter_estimator_result_children_round_trip():
    child_payload = {
        "type": "OptimizationResult",
        "parameter_values": {"a": 1.0},
        "cost": 0.1,
        "x": [1.0],
        "fun": 0.1,
        "success": True,
        "message": "ok",
        "evaluations": 10,
        "iterations": 3,
    }
    parent_payload = {
        "type": "ParameterEstimatorResult",
        "parameter_values": {"a": 1.0},
        "cost": 0.1,
        "children": [child_payload, {**child_payload, "cost": 0.2}],
    }
    r = from_config(parent_payload)
    assert len(r.children) == 2
    assert all(type(c) is OptimizationResult for c in r.children)
    assert r.children[0].cost == 0.1
    assert r.children[1].cost == 0.2

    # round-trip through to_config again
    r2 = from_config(r.to_config())
    assert len(r2.children) == 2
    assert all(type(c) is OptimizationResult for c in r2.children)


def test_parameter_estimator_result_best_results():
    child_a = OptimizationResult(cost=0.1)
    child_b = OptimizationResult(cost=0.2)
    r = ParameterEstimatorResult(cost=0.1, children=[child_a, child_b])
    assert r.best_results(1) == [child_a]
    assert r.best_results() == [child_a, child_b]
    with pytest.raises(ValueError, match="Cannot return"):
        r.best_results(5)


def test_optimization_result_from_config():
    payload = {
        "type": "OptimizationResult",
        "parameter_values": {"a": 1.0},
        "x": [1.0, 2.0],
        "fun": 0.05,
        "success": True,
        "message": "converged",
        "evaluations": 100,
        "iterations": 20,
    }
    r = from_config(payload)
    assert type(r) is OptimizationResult
    assert r.x == [1.0, 2.0]
    assert r.fun == 0.05
    assert r.success is True
    assert r.message == "converged"
    assert r.evaluations == 100
    assert r.iterations == 20


def test_ensemble_result_from_config():
    payload = {
        "type": "EnsembleResult",
        "parameter_values": {"a": 1.0},
        "x": [1.0],
        "method": "grid_search",
        "samples": [[1.0], [2.0]],
        "costs": [0.1, 0.2],
    }
    r = from_config(payload)
    assert type(r) is EnsembleResult
    assert r.x == [1.0]
    assert r.method == "grid_search"
    assert r.samples == [[1.0], [2.0]]


def test_posterior_result_from_config_and_stats():
    chains = [[[1.0], [2.0], [3.0], [4.0]]]  # 1 chain, 4 draws, 1 param
    payload = {
        "type": "PosteriorResult",
        "parameter_values": {"a": 1.0},
        "chains": chains,
        "log_pdfs": [[-1.0, -2.0, -3.0, -4.0]],
        "parameter_names": ["a"],
        "burnin": 1,
        "method": "mcmc",
        "acceptance_rate": 0.4,
        "r_hat": {"a": 1.0},
        "ess": {"a": 100.0},
    }
    r = from_config(payload)
    assert type(r) is PosteriorResult
    assert r.parameter_names == ["a"]
    assert r.burnin == 1
    assert r.method == "mcmc"
    assert r.acceptance_rate == 0.4
    assert r.r_hat == {"a": 1.0}
    assert r.ess == {"a": 100.0}

    marginal = r.marginal("a")
    assert list(marginal) == [2.0, 3.0, 4.0]  # burnin=1 drops the first draw

    lower, upper = r.credible_interval("a", level=0.5)
    assert lower <= upper

    means = r.posterior_mean()
    assert means["a"] == pytest.approx(3.0)


def test_credible_interval_from_flat_samples_when_no_chains():
    r = PosteriorResult(parameter_values={"D": 1.0}, parameter_names=["D"])
    assert r._chains is None
    # Simulate the API lazy fetch populating .posterior with flat samples.
    r.set_source(
        posterior=lambda: {
            "samples": {"D": list(range(100))},
            "sample_costs": [],
            "sample_param_names": ["D"],
            "sample_burnin": 10,
        }
    )
    m = r.marginal("D")
    assert len(m) == 90  # 100 minus 10 burn-in
    lo, hi = r.credible_interval("D", level=0.90)
    assert lo < hi


def test_marginal_from_multi_start_flat_samples_drops_burnin_per_start():
    """API-loaded multi-start chains discard warm-up draws from every start."""
    r = PosteriorResult(parameter_values={"D": 1.0}, parameter_names=["D"])
    r.set_source(
        posterior=lambda: {
            "samples": {"D": [[0, 1, 2], [10, 11, 12]]},
            "sample_burnin": 1,
        }
    )

    assert list(r.marginal("D")) == [1.0, 2.0, 11.0, 12.0]


def test_regression_result_from_config():
    payload = {
        "type": "RegressionResult",
        "parameter_values": {"a": 1.0},
        "x": [1.0],
        "results": {"r2": 0.99},
    }
    r = from_config(payload)
    assert type(r) is RegressionResult
    assert r.x == [1.0]
    assert r.results == {"r2": 0.99}


def test_validation_result_from_config():
    payload = {
        "type": "ValidationResult",
        "parameter_values": {"a": 1.0},
        "validation_results": {"obj_a": {"rmse": 0.1}},
        "summary_stats": {"mean_rmse": 0.1},
        "failed_objectives": {"obj_b": "diverged"},
    }
    r = from_config(payload)
    assert type(r) is ValidationResult
    assert r.validation_results == {"obj_a": {"rmse": 0.1}}
    assert r.summary_stats == {"mean_rmse": 0.1}
    assert r.failed_objectives == {"obj_b": "diverged"}


def test_passthrough_result_from_config():
    payload = {"type": "PassthroughResult", "parameter_values": {"a": 1.0}}
    r = from_config(payload)
    assert type(r) is PassthroughResult
    assert r.parameter_values == {"a": 1.0}


class _CountingFetcher:
    """Zero-arg callable that counts how many times it was invoked."""

    def __init__(self, value):
        self.value = value
        self.calls = 0

    def __call__(self):
        self.calls += 1
        return self.value


@pytest.mark.parametrize("field", ["overlay", "trace", "posterior", "series"])
def test_lazy_field_fetched_once_and_cached(field):
    fetcher = _CountingFetcher({"fetched": True})
    r = BaseResults()
    r.attach_source({field: fetcher})

    assert getattr(r, field) == {"fetched": True}
    assert getattr(r, field) == {"fetched": True}
    assert fetcher.calls == 1


@pytest.mark.parametrize("field", ["overlay", "trace", "posterior", "series"])
def test_lazy_field_direct_assignment_takes_precedence(field):
    fetcher = _CountingFetcher({"fetched": True})
    r = BaseResults()
    setattr(r, field, {"direct": True})
    r.attach_source({field: fetcher})

    assert getattr(r, field) == {"direct": True}
    assert fetcher.calls == 0


@pytest.mark.parametrize("field", ["overlay", "trace", "posterior", "series"])
def test_lazy_field_defaults_to_none_without_fetcher(field):
    r = BaseResults()
    assert getattr(r, field) is None


def test_set_source_is_kwarg_alias_for_attach_source():
    overlay_fetcher = _CountingFetcher({"overlay": True})
    trace_fetcher = _CountingFetcher({"trace": True})
    r = BaseResults()
    r.set_source(overlay=overlay_fetcher, trace=trace_fetcher)

    assert r.overlay == {"overlay": True}
    assert r.trace == {"trace": True}
    assert overlay_fetcher.calls == 1
    assert trace_fetcher.calls == 1


def test_plot_fit_results_works_off_lazily_fetched_overlay():
    def make_overlay():
        return {
            "voltage": {
                "type": "CurrentDriven",
                "plots": [
                    {
                        "type": "model data",
                        "traces": [{"name": "Data", "x": [0, 1], "y": [3.0, 3.1]}],
                        "layout": {"xaxis": {"title": {"text": "Time [s]"}}},
                    }
                ],
            }
        }

    r = BaseResults()
    r.attach_source({"overlay": make_overlay})
    result = r.plot_fit_results()
    assert set(result.keys()) == {"voltage"}


def test_attach_source_rejects_unknown_field():
    r = BaseResults()
    with pytest.raises(ValueError, match="overlaay"):
        r.attach_source({"overlaay": lambda: None})


def test_confidence_interval_result_round_trip():
    r = ConfidenceIntervalResult(
        parameter_values={"D": 1e-14},
        method="linear",
        confidence_level=0.95,
        intervals={"D": {"lower": 0.9e-14, "upper": 1.1e-14}},
        covariance=[[1.0]],
    )
    cfg = r.to_config()
    assert cfg["type"] == "ConfidenceIntervalResult"
    restored = from_config(cfg)
    assert type(restored) is ConfidenceIntervalResult
    assert restored.confidence_level == 0.95
    assert restored.bounds_for("D") == (0.9e-14, 1.1e-14)
    assert restored.width("D") == 1.1e-14 - 0.9e-14
    assert iws.results._REGISTRY["ConfidenceIntervalResult"] is ConfidenceIntervalResult


def test_sensitivity_result_round_trip_and_contributors():
    r = SensitivityResult(
        parameter_values={"a": 1.0, "b": 2.0},
        first_order={"a": 0.1, "b": 0.5},
        total_order={"a": 0.2, "b": 0.7},
        n_samples=256,
    )
    cfg = r.to_config()
    assert cfg["type"] == "SensitivityResult"
    restored = from_config(cfg)
    assert type(restored) is SensitivityResult
    assert restored.total_order == {"a": 0.2, "b": 0.7}
    assert restored.top_contributors(1) == [("b", 0.7)]
    assert restored.n_samples == 256
    assert iws.results._REGISTRY["SensitivityResult"] is SensitivityResult


def test_an_empty_lazy_answer_is_retried_not_cached():
    """A job still writing its plots answers empty. Caching that would leave the
    result blank for its whole life, so the next read asks again."""
    answers = [{}, {"voltage": {"type": None, "plots": [{"traces": [1]}]}}]
    calls = []

    def fetch():
        calls.append(1)
        return answers[min(len(calls) - 1, len(answers) - 1)]

    r = BaseResults()
    r.set_source(overlay=fetch)

    assert r.overlay == {}  # nothing stored yet
    assert r.overlay == answers[1]  # retried, and got it
    assert len(calls) == 2
    r.overlay  # noqa: B018 — now cached; no third call
    assert len(calls) == 2


def _large_chain_result():
    """A PosteriorResult as the backend sends it when the chains are too large
    to inline: no ``chains``, a storage ref, and the sample payload arriving
    later on the lazy ``posterior`` field."""
    r = PosteriorResult(
        parameter_values={"a": 3.0, "b": 30.0},
        chains_storage_ref="org/job/chains.parquet",
        parameter_names=["a", "b"],
    )
    r.posterior = {
        # Two chains of four draws, keyed by parameter name.
        "samples": {
            "a": [[1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0]],
            "b": [[10.0, 20.0, 30.0, 40.0], [50.0, 60.0, 70.0, 80.0]],
        },
        "sample_costs": [[0.4, 0.3, 0.2, 0.9], [0.8, 0.7, 0.6, 0.5]],
        "sample_param_names": ["a", "b"],
        "sample_burnin": 1,
    }
    return r


def test_marginal_recovers_from_posterior_when_chains_are_offloaded():
    r = _large_chain_result()
    # burnin=1 drops the first draw of each chain, then both chains flatten.
    assert list(r.marginal("a")) == [2.0, 3.0, 4.0, 6.0, 7.0, 8.0]


def test_credible_interval_recovers_from_posterior_when_chains_are_offloaded():
    # Post-burnin marginal is [20, 30, 40, 60, 70, 80]; its 0.25/0.75 quantiles.
    lower, upper = _large_chain_result().credible_interval("b", level=0.5)
    assert (lower, upper) == pytest.approx((32.5, 67.5))


def test_x_recovers_from_posterior_when_chains_are_offloaded():
    # Lowest cost is 0.2, the third draw of the first chain.
    assert list(_large_chain_result().x) == [3.0, 30.0]


def test_posterior_mean_recovers_from_posterior_when_chains_are_offloaded():
    means = _large_chain_result().posterior_mean()
    assert means["a"] == pytest.approx(5.0)
    assert means["b"] == pytest.approx(50.0)


def test_offloaded_recovery_runs_the_posterior_fetcher():
    """The recovery must go through the lazy ``posterior`` property, so a
    result whose samples are still behind a fetcher recovers too."""
    r = PosteriorResult(
        parameter_values={"a": 1.0},
        chains_storage_ref="org/job/chains.parquet",
        parameter_names=["a"],
    )
    calls = []

    def fetch():
        calls.append(1)
        return {
            "samples": {"a": [[1.0, 2.0, 3.0]]},
            "sample_costs": [[0.3, 0.1, 0.2]],
            "sample_param_names": ["a"],
            "sample_burnin": 0,
        }

    r.set_source(posterior=fetch)
    assert list(r.marginal("a")) == [1.0, 2.0, 3.0]
    assert list(r.x) == [2.0]
    assert len(calls) == 1  # fetched once, then cached


def test_inline_chains_win_over_the_posterior_payload():
    """Recovery is a fallback: a result that already carries chains must not
    consult ``posterior`` at all."""
    r = PosteriorResult(
        parameter_values={"a": 1.0},
        chains=[[[1.0], [2.0]]],
        parameter_names=["a"],
    )
    r.set_source(posterior=lambda: pytest.fail("posterior must not be fetched"))
    assert list(r.marginal("a")) == [1.0, 2.0]


def test_marginal_still_raises_when_nothing_can_supply_chains():
    r = PosteriorResult(parameter_values={"a": 1.0}, parameter_names=["a"])
    with pytest.raises(ValueError, match="chains"):
        r.marginal("a")


def test_chains_recovers_like_the_other_lazy_fields():
    """`overlay`/`trace`/`posterior` all populate on access; `chains` does too,
    rather than reporting None while `marginal()` quietly works."""
    r = _large_chain_result()
    assert r.chains is not None
    assert r.chains.shape == (2, 4, 2)  # (chain, draw, parameter)


def test_recovery_does_not_leak_the_chains_back_into_to_config():
    """Recovery caches off to the side, not into `_chains`: a result whose
    chains were offloaded must still serialize as offloaded, however many times
    the stats have been read."""
    r = _large_chain_result()
    r.marginal("a")
    assert r.chains is not None
    assert r.to_config()["chains"] is None
    assert r.to_config()["chains_storage_ref"] == "org/job/chains.parquet"


def test_chains_is_none_when_nothing_can_supply_them():
    r = PosteriorResult(parameter_values={"a": 1.0}, parameter_names=["a"])
    assert r.chains is None


def test_reassigning_posterior_invalidates_the_recovered_chains():
    """The recovery caches; `posterior` has a public setter. A second payload
    must win rather than being masked by the first one's cached arrays."""
    r = _large_chain_result()
    assert list(r.marginal("a")) == [2.0, 3.0, 4.0, 6.0, 7.0, 8.0]
    r.posterior = {
        "samples": {"a": [[100.0, 200.0]], "b": [[1.0, 2.0]]},
        "sample_costs": [[0.2, 0.1]],
        "sample_param_names": ["a", "b"],
        "sample_burnin": 0,
    }
    assert list(r.marginal("a")) == [100.0, 200.0]
    assert list(r.x) == [200.0, 2.0]


def test_recovery_rebuilds_once_across_many_parameters():
    """`posterior_mean` reads every parameter; the payload is reshaped once,
    not once per parameter."""
    r = _large_chain_result()
    r.posterior_mean()
    first = r._recovered
    r.marginal("a")
    r.credible_interval("b")
    assert r._recovered is first


def test_posterior_summary_wins_over_offloaded_chains_for_the_mean():
    """A real offloaded fit carries both a summary and the sample payload.
    `posterior_mean` reports the stored summary; `marginal` rebuilds. Pinning
    the precedence so a change to it is deliberate."""
    r = _large_chain_result()
    r._posterior_summary = {"a": {"mean": 99.0}, "b": {"mean": 999.0}}
    assert r.posterior_mean() == {"a": 99.0, "b": 999.0}
    assert list(r.marginal("a")) == [2.0, 3.0, 4.0, 6.0, 7.0, 8.0]


def test_marginal_names_the_offload_target_when_it_cannot_recover():
    r = PosteriorResult(
        parameter_values={"a": 1.0},
        chains_storage_ref="org/job/chains.parquet",
        parameter_names=["a"],
    )
    with pytest.raises(ValueError, match=r"offloaded to 'org/job/chains.parquet'"):
        r.marginal("a")


def test_marginal_rejects_an_unknown_name_without_fetching():
    """The name check runs before recovery, so a typo cannot trigger a fetch."""
    r = PosteriorResult(parameter_values={"a": 1.0}, parameter_names=["a"])
    r.set_source(posterior=lambda: pytest.fail("must not fetch for a bad name"))
    with pytest.raises(KeyError):
        r.marginal("nope")


def test_burnin_reports_the_constructed_value_not_the_recovered_one():
    """`burnin` is what this result was built with, so it round-trips through
    to_config unchanged. Recovery may apply the payload's own `sample_burnin`
    instead — here 1 against a constructed 0 — and that difference is visible
    in `marginal()`'s length rather than on this field."""
    r = _large_chain_result()  # burnin unset (0); payload's sample_burnin is 1
    assert r.burnin == 0
    assert r.to_config()["burnin"] == 0
    # Four draws per chain, two chains; the payload's burnin drops one of each.
    assert len(r.marginal("a")) == 6
