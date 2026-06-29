"""Schemas for initial-guess distribution samplers.

Used as ``DataFit.initial_guess_sampler`` to drive multi-start
initial-guess generation across the parameter bounds.
"""

from typing import Annotated, Literal

from pydantic import Field, WrapValidator

from ..base import BaseSchema


class DistributionSampler(BaseSchema):
    """Base class for initial-guess distribution samplers.

    Not typically used directly — configure via one of the concrete
    subclasses below.
    """

    pass


class HypercubeSampler(DistributionSampler):
    """Base class for hypercube-style samplers over the parameter bounds.

    Samples are drawn from the unit hypercube and then mapped through each
    parameter's distribution to produce scaled initial guesses spanning the
    parameter bounds.
    """

    pass


class LatinHypercube(HypercubeSampler):
    """Latin Hypercube sampler over the parameter bounds.

    Each of the ``multistarts`` initial guesses is drawn from a
    different stratum of the hypercube formed by the parameter bounds,
    giving better space-filling than plain uniform sampling. Backed by
    ``scipy.stats.qmc.LatinHypercube``.
    """

    type: Literal["LatinHypercube"] = Field(default="LatinHypercube", exclude=True)
    _emit_type = False


class Uniform(HypercubeSampler):
    """Uniform sampler over the parameter bounds.

    Each initial guess is drawn i.i.d. uniformly from the box defined
    by the parameter bounds. Simpler but less space-filling than
    ``LatinHypercube``.
    """

    type: Literal["Uniform"] = Field(default="Uniform", exclude=True)
    _emit_type = False


def _resolve_sampler(value, handler):
    """Validate one sampler against the discriminated union.

    A dict (the wire form) is dispatched on its ``type`` to the concrete leaf
    and hard-errors on an unknown type or bogus key. A concrete leaf instance
    validates through the union.

    Anything else is rejected. The contract holds only ``ionworks_schema``
    objects (a config dict or a ``DistributionSampler`` instance) — a live
    ``ionworkspipeline`` runtime sampler must be converted before it enters a
    schema, not embedded raw.
    """
    if isinstance(value, dict) or isinstance(value, DistributionSampler):
        return handler(value)
    raise ValueError(
        f"Invalid sampler {value!r}: expected a sampler config dict or a "
        f"DistributionSampler instance; got {type(value).__name__}. Live "
        f"ionworkspipeline runtime objects are not accepted inside a schema."
    )


# Discriminated union over the concrete samplers (abstract ``DistributionSampler``
# / ``HypercubeSampler`` excluded). The wrap validator accepts only config dicts
# and schema instances — runtime objects are rejected, not passed through.
SamplerUnion = Annotated[
    Annotated[LatinHypercube | Uniform, Field(discriminator="type")],
    WrapValidator(_resolve_sampler),
]
