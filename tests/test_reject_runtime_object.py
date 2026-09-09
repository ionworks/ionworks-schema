"""The boundary guard rejecting live runtime objects is centralized.

``reject_runtime_object`` (``ionworks_schema.base``) is the single place that
phrases "a live ionworkspipeline runtime object is not accepted inside a
schema". These tests pin the shared message and prove each of the four
resolvers (distribution / sampler / prior / objective) routes its
fall-through branch through it.
"""

from ionworks_schema.base import reject_runtime_object
from ionworks_schema.distribution_samplers.distribution_samplers import _resolve_sampler
from ionworks_schema.objective_functions.regularizers import resolve_prior
from ionworks_schema.objectives.objectives import _resolve_objective
from ionworks_schema.stats.stats import _resolve_distribution
import pytest


class _FakeRuntimeObject:
    """Stand-in for a live ``ionworkspipeline`` runtime object.

    Neither a config dict nor an ``ionworks_schema`` instance, so every
    resolver must reject it via the centralized guard.
    """


def _boom_handler(_value):
    raise AssertionError("handler should not run for a rejected runtime object")


def test_helper_message_shape():
    with pytest.raises(ValueError) as exc:
        reject_runtime_object(
            _FakeRuntimeObject(), "distribution", "a Distribution instance"
        )
    message = str(exc.value)
    assert "Invalid distribution" in message
    assert "expected a config dict or a Distribution instance" in message
    assert "_FakeRuntimeObject" in message
    assert "runtime objects are not accepted inside a schema" in message


def test_helper_never_returns():
    # The guard must always raise, so callers can rely on it for control flow.
    with pytest.raises(ValueError):
        reject_runtime_object(object(), "prior", "a Prior instance")


@pytest.mark.parametrize(
    "resolver, field",
    [
        (_resolve_distribution, "distribution"),
        (_resolve_sampler, "sampler"),
        (_resolve_objective, "objective"),
    ],
)
def test_wrap_validator_resolvers_route_through_guard(resolver, field):
    # Each wrap-validator resolver rejects a runtime object via the one helper,
    # so the message names its field and carries the shared phrasing.
    with pytest.raises(ValueError, match="runtime objects are not accepted") as exc:
        resolver(_FakeRuntimeObject(), _boom_handler)
    assert f"Invalid {field}" in str(exc.value)


def test_resolve_prior_rejects_runtime_object():
    # resolve_prior has a different signature (no handler) but the same guard.
    with pytest.raises(ValueError, match="Invalid prior"):
        resolve_prior(_FakeRuntimeObject())


def test_objective_message_uses_public_vocabulary():
    # The message must use the public vocabulary, not the internal abstract
    # class name (``BaseObjective``), so it points users at the right type.
    with pytest.raises(ValueError) as exc:
        _resolve_objective(_FakeRuntimeObject(), _boom_handler)
    message = str(exc.value)
    assert "ionworks_schema objective instance" in message
    assert "BaseObjective" not in message
