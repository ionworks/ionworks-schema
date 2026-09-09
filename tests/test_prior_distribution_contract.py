"""Contract tests for the prior / distribution / sampler resolvers (C.1).

Each tree (distributions in ``iws.stats``, samplers in
``iws.distribution_samplers``, priors in ``iws.objective_functions``) is
resolved from config dicts against its concrete schema class at the validation
gate, so unknown / typeless keys hard-error instead of being swallowed.
"""

import ionworks_schema as iws
from ionworks_schema.objective_functions.regularizers import Prior
from pydantic import ValidationError
import pytest


def _fit(**kwargs):
    return iws.DataFit(
        objectives={
            "ocp": iws.objectives.OCPHalfCell(
                electrode="positive", data_input="file:x.csv"
            )
        },
        **kwargs,
    )


# --- Distributions (discriminator key: "distribution") ---


def test_distribution_dict_resolves_via_prior():
    prior = Prior("Q_pe", {"distribution": "Normal", "mean": 3.0, "std": 0.2})
    assert type(prior.distribution).__name__ == "Normal"
    assert prior.distribution.mean == 3.0


def test_distribution_unknown_key_rejected():
    with pytest.raises(ValidationError):
        Prior("Q_pe", {"distribution": "Normal", "mean": 3.0, "std": 0.2, "bogus": 1})


def test_distribution_unknown_type_rejected():
    with pytest.raises(ValidationError):
        Prior("Q_pe", {"distribution": "NotADistribution", "mean": 3.0})


def test_distribution_instance_passes_through():
    n = iws.stats.Normal(mean=3.0, std=0.2)
    prior = Prior("Q_pe", n)
    assert prior.distribution is n


def test_distribution_legacy_type_alias_resolves():
    # ``type`` is accepted as a legacy alias for the ``distribution`` discriminator.
    prior = Prior("Q_pe", {"type": "Normal", "mean": 3.0, "std": 0.2})
    assert type(prior.distribution).__name__ == "Normal"


def test_distribution_discriminator_in_to_config_not_model_dump():
    # to_config carries the discriminator (round-trip); model_dump omits it so
    # the engine's parse_distribution doesn't forward it to the runtime ctor.
    n = iws.stats.Normal(mean=3.0, std=0.2)
    assert n.to_config()["distribution"] == "Normal"
    assert "distribution" not in n.model_dump()


# --- Samplers (discriminator key: "type") ---


def test_sampler_dict_resolves_and_round_trips():
    fit = _fit(
        parameters={"x": iws.Parameter("x", initial_value=1.0, bounds=(0.0, 2.0))},
        initial_guess_sampler={"type": "LatinHypercube"},
    )
    assert type(fit.initial_guess_sampler).__name__ == "LatinHypercube"
    assert fit.to_config()["initial_guess_sampler"] == {"type": "LatinHypercube"}


def test_sampler_unknown_key_rejected():
    with pytest.raises(ValidationError):
        _fit(
            parameters={"x": iws.Parameter("x", initial_value=1.0, bounds=(0.0, 2.0))},
            initial_guess_sampler={"type": "LatinHypercube", "bogus": 1},
        )


def test_sampler_unknown_type_rejected():
    with pytest.raises(ValidationError):
        _fit(
            parameters={"x": iws.Parameter("x", initial_value=1.0, bounds=(0.0, 2.0))},
            initial_guess_sampler={"type": "NotASampler"},
        )


# --- Priors (mapping name-from-key; flat + nested distribution forms) ---


def test_priors_mapping_instance_round_trips_with_name_from_key():
    fit = _fit(priors={"Q_pe": Prior("Q_pe", iws.stats.Normal(3.0, 0.2))})
    assert type(fit.priors["Q_pe"]).__name__ == "Prior"
    # to_config excludes name (it is the key); round-trip must re-inject it.
    cfg = fit.to_config()["priors"]
    round_tripped = _fit(priors=cfg)
    assert round_tripped.priors["Q_pe"].name == "Q_pe"


def test_priors_nested_distribution_form_resolves():
    fit = _fit(
        priors={
            "Q_pe": {
                "distribution": {"distribution": "Normal", "mean": 3.0, "std": 0.2},
                "regularizer_weight": 2.0,
            }
        }
    )
    assert fit.priors["Q_pe"].regularizer_weight == 2.0
    assert type(fit.priors["Q_pe"].distribution).__name__ == "Normal"


def test_priors_flat_distribution_form_resolves():
    # Engine ``parse_priors`` flat form: distribution is a string, params inline.
    fit = _fit(priors={"Q_pe": {"distribution": "Normal", "mean": 3.0, "std": 0.2}})
    assert fit.priors["Q_pe"].name == "Q_pe"
    assert type(fit.priors["Q_pe"].distribution).__name__ == "Normal"


def test_priors_junk_rejected():
    with pytest.raises(ValidationError):
        _fit(priors={"Q_pe": {"bogus": 1}})


def test_priors_list_form_with_flat_distribution_resolves():
    fit = _fit(
        priors=[{"name": "Q_pe", "distribution": "Normal", "mean": 3.0, "std": 0.2}]
    )
    assert type(fit.priors[0]).__name__ == "Prior"
    assert fit.priors[0].name == "Q_pe"


def test_priors_mapping_key_overrides_embedded_name():
    # The mapping key is authoritative; a disagreeing embedded name is ignored.
    fit = _fit(
        priors={
            "Q_pe": {"name": "WRONG", "distribution": "Normal", "mean": 3.0, "std": 0.2}
        }
    )
    assert fit.priors["Q_pe"].name == "Q_pe"


def test_priors_mapping_key_named_distribution_is_a_mapping():
    # A parameter literally named "distribution" must be read as a mapping key,
    # not mistaken for a single prior's distribution field.
    fit = _fit(
        priors={"distribution": {"distribution": "Normal", "mean": 3.0, "std": 0.2}}
    )
    assert fit.priors["distribution"].name == "distribution"
    assert type(fit.priors["distribution"].distribution).__name__ == "Normal"


# --- Clearly-invalid values are rejected, not passed through ---
# Mirrors the objective resolver fix: a bare builtin scalar/collection can never
# be a distribution / prior / sampler, so the resolver rejects it rather than
# silently passing it through.


def test_distribution_bogus_scalar_rejected():
    with pytest.raises(ValidationError):
        Prior("Q_pe", 123)


def test_prior_bogus_scalar_rejected():
    with pytest.raises(ValidationError):
        _fit(priors={"Q_pe": 123})


def test_sampler_bogus_scalar_rejected():
    with pytest.raises(ValidationError):
        _fit(
            parameters={"x": iws.Parameter("x", initial_value=1.0, bounds=(0.0, 2.0))},
            initial_guess_sampler=123,
        )


def test_prior_type_penalty_rejected():
    # The prior resolver must validate the `type` discriminator, not discard it:
    # a sibling Penalty (or unknown type) must not be silently coerced to Prior.
    with pytest.raises(ValidationError):
        _fit(
            priors={
                "Q_pe": {"type": "Penalty", "distribution": iws.stats.Normal(3.0, 0.2)}
            }
        )


def test_prior_type_unknown_rejected():
    with pytest.raises(ValidationError):
        _fit(
            priors={
                "Q_pe": {
                    "type": "NotAPrior",
                    "distribution": iws.stats.Normal(3.0, 0.2),
                }
            }
        )
