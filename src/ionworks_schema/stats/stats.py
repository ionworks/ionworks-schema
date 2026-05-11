"""Schemas for stats."""

from typing import Any

from pydantic import Field

from ..base import BaseSchema


class _DistributionBase(BaseSchema):
    """Base class for distribution schemas that adds 'distribution' key to config."""

    def to_config(self) -> dict:
        """Convert to parser-compatible format with 'distribution' key."""
        config = {}
        # Process each field, calling to_config on nested schemas
        for key, value in self:
            if value is None:
                continue
            if hasattr(value, "to_config"):
                config[key] = value.to_config()
            elif hasattr(value, "tolist"):
                config[key] = value.tolist()
            else:
                config[key] = value
        # Add 'distribution' key with the class name (NOT 'type')
        config["distribution"] = self.__class__.__name__
        return config


class Dirichlet(_DistributionBase):
    """Dirichlet distribution over the unit simplex.

    Mirrors ``iwp.stats.Dirichlet``. Concentration parameters must be > 1 so
    the distribution's mode (argmin of the negative logpdf) is well-defined.
    """

    alpha: list | tuple = Field(
        ...,
        description=(
            "Concentration parameters of the Dirichlet distribution as a list or "
            "tuple of numbers. All entries must be strictly greater than 1 so "
            "the mode is well-defined."
        ),
    )

    def __init__(self, alpha):
        super().__init__(alpha=alpha)


class Distribution(BaseSchema):
    """Base class for sampling from probability distributions.

    Mirrors ``iwp.stats.Distribution``. Subclasses supply concrete
    distribution parameters; this base only carries an optional underlying
    scipy-style distribution marker.
    """

    distribution: Any | None = Field(
        default=None,
        description=(
            "Underlying distribution object (e.g. a ``scipy.stats`` frozen "
            "distribution). Normally set by subclass constructors; leave "
            "``None`` when configuring via named subclass."
        ),
    )

    def __init__(self, distribution=None):
        super().__init__(distribution=distribution)


class LogNormal(_DistributionBase):
    """Univariate lognormal distribution.

    Mirrors ``iwp.stats.LogNormal``. Parameterised by the ``mean`` and ``std``
    of the *underlying* normal (i.e. values of :math:`\\log X`), matching the
    pipeline's constructor.
    """

    mean: float | int = Field(
        ...,
        description=(
            "Mean of the underlying normal distribution (i.e. mean of "
            "``log(X)``). Must be a finite scalar."
        ),
    )
    std: float | int = Field(
        ...,
        description=(
            "Standard deviation of the underlying normal distribution (i.e. "
            "standard deviation of ``log(X)``). Must be a positive scalar."
        ),
    )

    def __init__(self, mean, std):
        super().__init__(mean=mean, std=std)


class MultivariateLogNormal(_DistributionBase):
    """Multivariate lognormal distribution.

    Mirrors ``iwp.stats.MultivariateLogNormal``. Parameterised by the mean
    vector and covariance matrix of the underlying multivariate normal.
    """

    mean: list | tuple = Field(
        ...,
        description=(
            "Mean vector of the underlying multivariate normal distribution "
            "(i.e. mean of ``log(X)``) as a list or tuple of floats. Length "
            "must match the covariance matrix dimension."
        ),
    )
    cov: list | tuple = Field(
        ...,
        description=(
            "Covariance matrix of the underlying multivariate normal "
            "distribution (i.e. covariance of ``log(X)``) as a nested list "
            "or tuple of floats. Must be square, positive semi-definite, "
            "and dimensionally consistent with ``mean``."
        ),
    )

    def __init__(self, mean, cov):
        super().__init__(mean=mean, cov=cov)


class MultivariateNormal(_DistributionBase):
    """Multivariate normal distribution.

    Mirrors ``iwp.stats.MultivariateNormal``. Requires a positive
    semi-definite covariance matrix of shape matching ``len(mean)``.
    """

    mean: list | tuple = Field(
        ...,
        description=(
            "Mean vector of the multivariate normal distribution as a list "
            "or tuple of floats. Length must match the covariance matrix "
            "dimension."
        ),
    )
    cov: list | tuple = Field(
        ...,
        description=(
            "Covariance matrix of the multivariate normal distribution as a "
            "nested list or tuple of floats. Must be square, positive "
            "semi-definite, and dimensionally consistent with ``mean``."
        ),
    )

    def __init__(self, mean, cov):
        super().__init__(mean=mean, cov=cov)


class Normal(_DistributionBase):
    """Univariate normal distribution.

    Mirrors ``iwp.stats.Normal``. Parameterised by scalar mean and standard
    deviation.
    """

    mean: float | int = Field(
        ...,
        description="Mean of the normal distribution. Must be a finite scalar.",
    )
    std: float | int = Field(
        ...,
        description=(
            "Standard deviation of the normal distribution. Must be a positive scalar."
        ),
    )

    def __init__(self, mean, std):
        super().__init__(mean=mean, std=std)


class PointMass(_DistributionBase):
    """Point mass distribution — a constant value with zero variance.

    Mirrors ``iwp.stats.PointMass``. Useful for pinning a parameter to a fixed
    value while still flowing through a distribution-aware pipeline step.
    """

    value: float | int = Field(
        ...,
        description=(
            "The constant value of the point mass distribution. All "
            "draws/samples equal this value."
        ),
    )

    def __init__(self, value):
        super().__init__(value=value)


class Uniform(_DistributionBase):
    """Uniform distribution on ``[lb, ub]``.

    Mirrors ``iwp.stats.Uniform``. Lower bound must be strictly less than
    upper bound.
    """

    lb: float | int = Field(
        ...,
        description=(
            "Lower bound of the uniform distribution. Must be strictly less "
            "than ``ub``."
        ),
    )
    ub: float | int = Field(
        ...,
        description=(
            "Upper bound of the uniform distribution. Must be strictly "
            "greater than ``lb``."
        ),
    )

    def __init__(self, lb, ub):
        super().__init__(lb=lb, ub=ub)
