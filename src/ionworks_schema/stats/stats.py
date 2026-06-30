"""Schemas for stats."""

from typing import Annotated, Literal

from pydantic import Field, WrapValidator

from ..base import BaseSchema


class Distribution(BaseSchema):
    """A probability distribution you can sample from.

    This is the shared parent of every named distribution
    (``Normal``, ``LogNormal``, ``Uniform``, ``PointMass``,
    ``Dirichlet``, ``MultivariateNormal``, ``MultivariateLogNormal``).
    Anywhere a schema field is typed as ``Distribution``
    (e.g. ``Prior.distribution`` or
    ``Parameter.initial_guess_distribution``), you can pass any of
    those named subclasses.
    """

    def to_config(self) -> dict:
        """Build the dict you submit through ``ionworks-api``.

        The output carries a ``"distribution"`` key set to the name of
        this distribution (``"Normal"``, ``"Uniform"``, …), plus one
        entry per parameter you supplied (``mean``, ``std``, ``lb``,
        ``ub``, ``alpha``, …). Pass this dict wherever the Ionworks
        API expects a distribution payload.
        """
        config = {}
        for key, value in self:
            if value is None:
                continue
            if hasattr(value, "to_config"):
                config[key] = value.to_config()
            elif hasattr(value, "tolist"):
                config[key] = value.tolist()
            else:
                config[key] = value
        config["distribution"] = self.__class__.__name__
        return config


class Dirichlet(Distribution):
    """Dirichlet distribution over the unit simplex.

    Concentration parameters must be > 1 so the distribution's mode
    (argmin of the negative logpdf) is well-defined.

    Examples
    --------
    >>> dist = iws.stats.Dirichlet(alpha=[2.0, 2.0, 2.0])
    >>> param = iws.Parameter("Xj", initial_value=0.33, bounds=(0.0, 1.0), prior=dist)
    """

    distribution: Literal["Dirichlet"] = Field(default="Dirichlet", exclude=True)

    alpha: list | tuple = Field(
        ...,
        description=(
            "Concentration parameters of the Dirichlet distribution as a list or "
            "tuple of numbers. All entries must be strictly greater than 1 so "
            "the mode is well-defined."
        ),
    )

    def __init__(self, alpha=None, **kwargs):
        # Widened for the union: accept the 'distribution' discriminator via **kwargs.
        super().__init__(alpha=alpha, **kwargs)


class LogNormal(Distribution):
    """Univariate lognormal distribution.

    Parameterised by the ``mean`` and ``std`` of the *underlying* normal
    (i.e. values of :math:`\\log X`).

    Examples
    --------
    >>> prior = iws.stats.LogNormal(mean=-32.2, std=2.0)
    >>> param = iws.Parameter(
    ...     "Negative particle diffusivity [m2.s-1]",
    ...     initial_value=1e-14, bounds=(1e-16, 1e-12), prior=prior,
    ... )
    """

    distribution: Literal["LogNormal"] = Field(default="LogNormal", exclude=True)

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

    def __init__(self, mean=None, std=None, **kwargs):
        # Widened for the union: accept the 'distribution' discriminator via **kwargs.
        super().__init__(mean=mean, std=std, **kwargs)


class MultivariateLogNormal(Distribution):
    """Multivariate lognormal distribution.

    Parameterised by the mean vector and covariance matrix of the
    underlying multivariate normal.

    Examples
    --------
    >>> prior = iws.stats.MultivariateLogNormal(
    ...     mean=[-32.0, -33.0],
    ...     cov=[[1.0, 0.0], [0.0, 1.0]],
    ... )
    >>> param = iws.Parameter("D", initial_value=1.0, bounds=(0.1, 10.0), prior=prior)
    """

    distribution: Literal["MultivariateLogNormal"] = Field(
        default="MultivariateLogNormal", exclude=True
    )

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

    def __init__(self, mean=None, cov=None, **kwargs):
        # Widened for the union: accept the 'distribution' discriminator via **kwargs.
        super().__init__(mean=mean, cov=cov, **kwargs)


class MultivariateNormal(Distribution):
    """Multivariate normal distribution.

    Requires a positive semi-definite covariance matrix of shape
    matching ``len(mean)``.

    Examples
    --------
    >>> prior = iws.stats.MultivariateNormal(
    ...     mean=[1.0, 2.0],
    ...     cov=[[0.04, 0.0], [0.0, 0.09]],
    ... )
    >>> param = iws.Parameter("x", initial_value=1.0, bounds=(0.0, 5.0), prior=prior)
    """

    distribution: Literal["MultivariateNormal"] = Field(
        default="MultivariateNormal", exclude=True
    )

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

    def __init__(self, mean=None, cov=None, **kwargs):
        # Widened for the union: accept the 'distribution' discriminator via **kwargs.
        super().__init__(mean=mean, cov=cov, **kwargs)


class Normal(Distribution):
    """Univariate normal distribution.

    Parameterised by scalar mean and standard deviation.

    Examples
    --------
    >>> prior = iws.stats.Normal(mean=3.0, std=0.2)
    >>> param = iws.Parameter(
    ...     "Positive electrode capacity [A.h]",
    ...     initial_value=3.0, bounds=(2.0, 4.0), prior=prior,
    ... )
    """

    distribution: Literal["Normal"] = Field(default="Normal", exclude=True)

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

    def __init__(self, mean=None, std=None, **kwargs):
        # Widened for the union: accept the 'distribution' discriminator via **kwargs.
        super().__init__(mean=mean, std=std, **kwargs)


class PointMass(Distribution):
    """Point mass distribution — a constant value with zero variance.

    Useful for pinning a parameter to a fixed value while still flowing
    through a distribution-aware pipeline step.

    Examples
    --------
    >>> guess = iws.stats.PointMass(value=1.0)
    >>> param = iws.Parameter(
    ...     "x", initial_value=1.0, bounds=(0.0, 2.0),
    ...     initial_guess_distribution=guess,
    ... )
    """

    distribution: Literal["PointMass"] = Field(default="PointMass", exclude=True)

    value: float | int = Field(
        ...,
        description=(
            "The constant value of the point mass distribution. All "
            "draws/samples equal this value."
        ),
    )

    def __init__(self, value=None, **kwargs):
        # Widened for the union: accept the 'distribution' discriminator via **kwargs.
        super().__init__(value=value, **kwargs)


class Uniform(Distribution):
    """Uniform distribution on ``[lb, ub]``.

    Lower bound must be strictly less than upper bound.

    Examples
    --------
    >>> guess = iws.stats.Uniform(lb=0.0, ub=2.0)
    >>> param = iws.Parameter(
    ...     "x", initial_value=1.0, bounds=(0.0, 2.0),
    ...     initial_guess_distribution=guess,
    ... )
    """

    distribution: Literal["Uniform"] = Field(default="Uniform", exclude=True)

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

    def __init__(self, lb=None, ub=None, **kwargs):
        # Widened for the union: accept the 'distribution' discriminator via **kwargs.
        super().__init__(lb=lb, ub=ub, **kwargs)


def _resolve_distribution(value, handler):
    """Validate one distribution against the discriminated union.

    A dict (the wire form) is discriminated on its ``distribution`` key — with
    ``type`` accepted as a legacy alias — and hard-errors on an unknown name or
    bogus key. A ``Distribution`` instance validates through the union.

    Anything else is rejected. The contract holds only ``ionworks_schema``
    objects (a config dict or a ``Distribution`` instance) — a live
    ``ionworkspipeline`` runtime distribution must be converted before it enters
    a schema, not embedded raw.
    """
    if isinstance(value, dict):
        data = dict(value)
        if "distribution" not in data and "type" in data:
            data["distribution"] = data.pop("type")  # legacy alias
        return handler(data)
    if isinstance(value, Distribution):
        return handler(value)
    raise ValueError(
        f"Invalid distribution {value!r}: expected a distribution config dict "
        f"or a Distribution instance; got {type(value).__name__}. Live "
        f"ionworkspipeline runtime objects are not accepted inside a schema."
    )


# Discriminated union over the concrete distributions, keyed on the
# ``distribution`` discriminator (``to_config`` emits ``{"distribution": ...}``).
DistributionUnion = Annotated[
    Annotated[
        Dirichlet
        | LogNormal
        | MultivariateLogNormal
        | MultivariateNormal
        | Normal
        | PointMass
        | Uniform,
        Field(discriminator="distribution"),
    ],
    WrapValidator(_resolve_distribution),
]
