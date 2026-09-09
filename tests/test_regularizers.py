"""Tests for ionworks_schema regularizers (Prior, Constraint, Penalty)."""

from ionworks_schema.objective_functions import Constraint, Penalty, Prior
from ionworks_schema.stats import Normal


def test_prior_to_config_matches_parser_shape():
    """Prior.to_config emits {distribution, type} and excludes name."""
    prior = Prior(name="k", distribution=Normal(mean=0.0, std=1.0))
    cfg = prior.to_config()
    assert "name" not in cfg
    assert cfg["type"] == "Prior"
    assert "distribution" in cfg


def test_constraint_to_config_matches_parser_shape():
    """Constraint.to_config emits {fun, type} matching parse_constraints()."""
    constraint = Constraint(fun=0.0)
    cfg = constraint.to_config()
    assert cfg["type"] == "Constraint"
    assert cfg["fun"] == 0.0


def test_constraint_and_penalty_configs_round_trip():
    """A to_config dict (carrying the `type` discriminator) re-validates."""
    for cls in (Constraint, Penalty):
        cfg = cls(fun=0.0).to_config()
        assert cls(**cfg).type == cls.__name__


def test_constraint_regularizer_weight_included_when_set():
    """Optional regularizer_weight appears in to_config only when set."""
    c1 = Constraint(fun=0.0)
    assert "regularizer_weight" not in c1.to_config()

    c2 = Constraint(fun=0.0, regularizer_weight=2.5)
    cfg = c2.to_config()
    assert cfg["regularizer_weight"] == 2.5


def test_penalty_to_config_matches_parser_shape():
    """Penalty.to_config emits {fun, type} matching parse_penalties()."""
    penalty = Penalty(fun=1.0, regularizer_weight=0.5)
    cfg = penalty.to_config()
    assert cfg["type"] == "Penalty"
    assert cfg["fun"] == 1.0
    assert cfg["regularizer_weight"] == 0.5
