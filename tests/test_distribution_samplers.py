"""Tests for ionworks_schema.distribution_samplers."""

import ionworks_schema as iws
from ionworks_schema.distribution_samplers import (
    DistributionSampler,
    HypercubeSampler,
    LatinHypercube,
    Uniform,
)
import pytest


def test_distribution_samplers_module_is_exposed():
    """Submodule appears on top-level ionworks_schema."""
    assert iws.distribution_samplers is not None


@pytest.mark.parametrize(
    "sampler_cls,expected_type",
    [(LatinHypercube, "LatinHypercube"), (Uniform, "Uniform")],
)
def test_sampler_to_config_has_type_discriminator(sampler_cls, expected_type):
    """Sampler.to_config includes the type tag so the parser can dispatch."""
    assert sampler_cls().to_config() == {"type": expected_type}


def test_sampler_inheritance():
    """Concrete samplers subclass HypercubeSampler → DistributionSampler."""
    assert issubclass(LatinHypercube, HypercubeSampler)
    assert issubclass(HypercubeSampler, DistributionSampler)
