"""Schemas for parameter."""

from typing import Any

from pydantic import Field, model_validator

from .._types import NumberLike
from ..base import BaseSchema

# Tuple from Python construction; list when round-tripped through JSON.
_Bounds = tuple[NumberLike, NumberLike] | list[NumberLike]


class Parameter(BaseSchema):
    """A model parameter that is free to move during a data fit.

    Wrap any quantity you want the fit to adjust in a ``Parameter``
    so the pipeline knows it's a free variable: its starting value,
    its plausible range, and (optionally) what you already believe
    about its likely value. Anything *not* wrapped in a ``Parameter``
    is treated as a fixed input.

    Parameters
    ----------
    name : str
        The name of the parameter. Should match the name used inside
        the model (e.g. ``"Particle diffusion time [s]"``).
    initial_value : float | None, optional
        The value the optimiser starts from. If you leave it unset,
        the midpoint of finite bounds is used (or ``1`` when there
        are no bounds).
    bounds : tuple[float, float] | list[float] | None, optional
        ``(lower, upper)`` tuple bracketing where you believe the
        true value lies. Defaults to no bounds. The upper bound must
        be strictly greater than the lower bound.
    prior : Distribution or Prior or None, optional
        A probability distribution describing what you already
        believe about the parameter. Used by Bayesian and
        regularised fits.
    normalize : bool | None, optional
        Rescale by the initial value before optimisation so the
        optimiser sees comparable magnitudes. Defaults to ``True``.
    check_bounds : bool | None, optional
        Validate the bounds at construction time. Defaults to ``True``.
    check_initial_value : bool | None, optional
        Validate that the initial value falls inside the bounds at
        construction time. Defaults to ``True``.
    initial_guess_distribution : Distribution or None, optional
        When running multistart fits, this is the distribution the
        starting points are drawn from. Defaults to a uniform
        distribution over the bounds.

    Examples
    --------
    >>> # build the parameter with bounds, a prior, and a log transform
    >>> raw = iws.Parameter(
    ...     "Negative particle diffusivity [m2.s-1]",
    ...     initial_value=1e-14,
    ...     bounds=(1e-16, 1e-12),
    ...     prior=iws.stats.LogNormal(mean=-32.2, std=2.0),
    ... )
    >>> param = iws.transforms.Log10(parameter=raw)
    >>> # slot it into a DataFit
    >>> obj = iws.objectives.Pulse(data_input="path/to/gitt.csv")
    >>> fit = iws.DataFit(objectives={"gitt": obj}, parameters={raw.name: param})
    """

    _exclude_fields = {"name"}

    name: str = Field(
        ...,
        description=(
            "Name of the parameter as it appears inside the model "
            "(e.g. ``'Particle diffusion time [s]'``). When this "
            "parameter is added to a ``parameters`` mapping, the "
            "mapping key is used and this field is omitted from the "
            "submitted payload."
        ),
    )
    initial_value: NumberLike | None = Field(
        default=None,
        description=(
            "Initial value assigned to the parameter. If not provided and "
            "bounds are given, defaults to the mean of finite bounds; "
            "otherwise defaults to 1."
        ),
    )
    bounds: _Bounds | None = Field(
        default=None,
        description=(
            "Two-tuple ``(lower, upper)`` giving the lower and upper bounds "
            "for the parameter. Defaults to ``(-inf, inf)``. The upper bound "
            "must be strictly greater than the lower bound."
        ),
    )
    # ``prior`` and ``initial_guess_distribution`` are typed ``Any``
    # because the parser path also feeds in already-built runtime
    # distribution objects (not just schema instances).
    prior: Any | None = Field(  # noqa: ANN401
        default=None,
        description=(
            "What you already believe about the parameter's likely "
            "value. Pass an ``iws.stats`` distribution "
            "(``Normal(mean, std)``, ``LogNormal(...)``, …) or a "
            "``Prior`` for finer control over the regulariser weight. "
            "Used by Bayesian and regularised fits."
        ),
    )
    normalize: bool | None = Field(
        default=None,
        description=(
            "Whether to normalize the parameter by its initial value before "
            "optimization. Defaults to True."
        ),
    )
    check_bounds: bool | None = Field(
        default=None,
        description=(
            "Whether to validate the bounds at construction time. Defaults to True."
        ),
    )
    check_initial_value: bool | None = Field(
        default=None,
        description=(
            "Whether to validate that the initial value lies within the "
            "bounds at construction time. Defaults to True."
        ),
    )
    initial_guess_distribution: Any | None = Field(  # noqa: ANN401
        default=None,
        description=(
            "Distribution that multistart starting points are drawn "
            "from. Defaults to a uniform distribution over the bounds. "
            "Must be either ``iws.stats.Uniform`` or "
            "``iws.stats.PointMass``."
        ),
    )

    def __init__(
        self,
        name,
        initial_value=None,
        bounds=None,
        prior=None,
        normalize=None,
        check_bounds=None,
        check_initial_value=None,
        initial_guess_distribution=None,
    ):
        super().__init__(
            name=name,
            initial_value=initial_value,
            bounds=bounds,
            prior=prior,
            normalize=normalize,
            check_bounds=check_bounds,
            check_initial_value=check_initial_value,
            initial_guess_distribution=initial_guess_distribution,
        )

    @model_validator(mode="after")
    def upper_bound_greater_than_lower(self):
        """Validate that upper bound is greater than lower bound."""
        if self.bounds is not None:
            if self.bounds[0] >= self.bounds[1]:
                raise ValueError("Bounds must be strictly increasing")
        return self
