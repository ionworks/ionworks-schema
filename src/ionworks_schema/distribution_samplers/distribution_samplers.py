"""Schemas for initial-guess distribution samplers.

Mirrors ``iwp.data_fits.distribution_samplers``. Used as
``DataFit.initial_guess_sampler`` to drive multi-start initial-guess
generation across the parameter bounds.
"""

from ..base import BaseSchema


class DistributionSampler(BaseSchema):
    """Base class for initial-guess distribution samplers.

    Mirrors ``iwp.data_fits.distribution_samplers.DistributionSampler``. Not
    typically used directly — configure via one of the concrete subclasses
    below.
    """

    pass


class HypercubeSampler(DistributionSampler):
    """Base class for hypercube-style samplers over the parameter bounds.

    Mirrors ``iwp.data_fits.distribution_samplers.HypercubeSampler``.
    Samples are drawn from the unit hypercube and then mapped through each
    parameter's distribution to produce scaled initial guesses spanning the
    parameter bounds.
    """

    pass


class LatinHypercube(HypercubeSampler):
    """Latin Hypercube sampler over the parameter bounds.

    Mirrors ``iwp.data_fits.distribution_samplers.LatinHypercube``. Each of
    the ``multistarts`` initial guesses is drawn from a different stratum
    of the hypercube formed by the parameter bounds, giving better space-
    filling than plain uniform sampling. Under the hood uses
    ``scipy.stats.qmc.LatinHypercube``.
    """

    pass


class Uniform(HypercubeSampler):
    """Uniform sampler over the parameter bounds.

    Mirrors ``iwp.data_fits.distribution_samplers.Uniform``. Each initial
    guess is drawn i.i.d. uniformly from the box defined by the parameter
    bounds. Simpler but less space-filling than ``LatinHypercube``.
    """

    pass
