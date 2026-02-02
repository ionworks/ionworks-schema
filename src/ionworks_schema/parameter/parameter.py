"""Schemas for parameter."""

from typing import Any

from pydantic import Field, model_validator

from ..base import BaseSchema


class Parameter(BaseSchema):
    """Parameter object for use in data fits, stores the initial value and bounds

    Inherits from :class:`pybamm.InputParameter` for compatibility with PyBaMM models.

    Parameters
    ----------
    name : str
        The name of the parameter.
    initial_value : float or int, optional
        The initial value to be assigned to the parameter. If not provided and bounds are given,
        will be set to the mean of finite bounds. Defaults to 1 if no bounds are given.
    bounds : tuple, optional
        A tuple defining the lower and upper bounds for the parameter.
        Defaults to (-np.inf, np.inf).
    prior : iwp.stats.Distribution, optional
        The prior distribution for the parameter.
    normalize : bool, optional
        Whether to normalize the parameter by its initial value. Defaults to True.
    fitting_scale : float, optional
        The scale factor for the parameter. If not provided, the parameter
        will be normalized by its initial value.
    check_bounds : bool, optional
        Whether to check the bounds of the parameter. Defaults to True.
    check_initial_value : bool, optional
        Whether to check the initial value of the parameter. Defaults to True.
    initial_guess_distribution : iwp.stats.Distribution, optional
        The initial guess distribution for the parameter. Defaults to a uniform
        distribution between the bounds. The provided distribution must be either a
        `iwp.stats.Uniform` or `iwp.stats.PointMass`."""

    _exclude_fields = {"name"}

    name: Any = Field(...)
    initial_value: Any | None = Field(default=None)
    bounds: Any | None = Field(default=None)
    prior: Any | None = Field(default=None)
    normalize: Any | None = Field(default=None)
    check_bounds: Any | None = Field(default=None)
    check_initial_value: Any | None = Field(default=None)
    initial_guess_distribution: Any | None = Field(default=None)

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
