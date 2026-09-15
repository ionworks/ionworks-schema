"""Schema tests for the weighted-point-cloud mode of ``iws.costs.Wasserstein``."""

import ionworks_schema as iws
import pytest


def test_wasserstein_default_has_no_variable_fields():
    """Default construction leaves ``position_variable`` /
    ``weight_variable`` unset and omits them from the config."""
    cost = iws.costs.Wasserstein()
    cfg = cost.to_config()
    assert cfg["type"] == "Wasserstein"
    assert "position_variable" not in cfg
    assert "weight_variable" not in cfg


def test_wasserstein_weighted_mode_to_config_carries_fields():
    """Setting both variable names switches to weighted mode and the
    config round-trips them."""
    cost = iws.costs.Wasserstein(
        position_variable="Voltage [V]",
        weight_variable="Differential capacity [Ah/V]",
    )
    cfg = cost.to_config()
    assert cfg["type"] == "Wasserstein"
    assert cfg["position_variable"] == "Voltage [V]"
    assert cfg["weight_variable"] == "Differential capacity [Ah/V]"


def test_wasserstein_rejects_partial_weighted_options():
    """Providing only one of ``position_variable`` / ``weight_variable``
    is rejected at construction so the cost can't be ambiguously
    half-configured."""
    with pytest.raises(Exception):
        iws.costs.Wasserstein(position_variable="Voltage [V]")
    with pytest.raises(Exception):
        iws.costs.Wasserstein(weight_variable="Differential capacity [Ah/V]")


def test_wasserstein_weighted_mode_accepts_error_function_options():
    """``normalization``, ``objective_weights`` and the inherited
    :class:`ErrorFunction` knobs flow through unchanged."""
    cost = iws.costs.Wasserstein(
        position_variable="Voltage [V]",
        weight_variable="Differential capacity [Ah/V]",
        normalization="identity",
        objective_weights={"cell": 2.0},
    )
    cfg = cost.to_config()
    assert cfg["normalization"] == "identity"
    assert cfg["objective_weights"] == {"cell": 2.0}
