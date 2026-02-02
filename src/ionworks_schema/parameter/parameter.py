"""Schemas for parameter."""

from typing import Any

from pydantic import Field, model_validator

from ..base import BaseSchema


class Parameter(BaseSchema):
    """Schema for Parameter."""

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
