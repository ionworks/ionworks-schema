"""Schemas for objective_functions."""

from typing import Any

from pydantic import Field

from ..base import BaseSchema


class ChiSquare(BaseSchema):
    """Schema for ChiSquare."""

    variable_standard_deviations: Any = Field(...)
    nan_values: Any | None = Field(default=None)

    def __init__(self, variable_standard_deviations, nan_values=None):
        super().__init__(
            variable_standard_deviations=variable_standard_deviations,
            nan_values=nan_values,
        )


class Cost(BaseSchema):
    """Schema for Cost."""

    pass


class DesignFunction(BaseSchema):
    """Schema for DesignFunction."""

    objective_weights: Any | None = Field(default=None)

    def __init__(self, objective_weights=None):
        super().__init__(objective_weights=objective_weights)


class Difference(BaseSchema):
    """Schema for Difference."""

    pass


class ErrorFunction(BaseSchema):
    """Schema for ErrorFunction."""

    scale: Any = Field(default="mean")
    nan_values: Any | None = Field(default=None)
    objective_weights: Any | None = Field(default=None)
    variable_weights: Any | None = Field(default=None)

    def __init__(
        self,
        scale="mean",
        nan_values=None,
        objective_weights=None,
        variable_weights=None,
    ):
        super().__init__(
            scale=scale,
            nan_values=nan_values,
            objective_weights=objective_weights,
            variable_weights=variable_weights,
        )


class MAE(BaseSchema):
    """Schema for MAE."""

    scale: Any = Field(default="mean")
    nan_values: Any | None = Field(default=None)
    objective_weights: Any | None = Field(default=None)
    variable_weights: Any | None = Field(default=None)

    def __init__(
        self,
        scale="mean",
        nan_values=None,
        objective_weights=None,
        variable_weights=None,
    ):
        super().__init__(
            scale=scale,
            nan_values=nan_values,
            objective_weights=objective_weights,
            variable_weights=variable_weights,
        )


class MLE(BaseSchema):
    """Schema for MLE."""

    scale: Any = Field(default="mean")
    nan_values: Any | None = Field(default=None)
    objective_weights: Any | None = Field(default=None)
    variable_weights: Any | None = Field(default=None)

    def __init__(
        self,
        scale="mean",
        nan_values=None,
        objective_weights=None,
        variable_weights=None,
    ):
        super().__init__(
            scale=scale,
            nan_values=nan_values,
            objective_weights=objective_weights,
            variable_weights=variable_weights,
        )


class MSE(BaseSchema):
    """Schema for MSE."""

    scale: Any = Field(default="mean")
    nan_values: Any | None = Field(default=None)
    objective_weights: Any | None = Field(default=None)
    variable_weights: Any | None = Field(default=None)

    def __init__(
        self,
        scale="mean",
        nan_values=None,
        objective_weights=None,
        variable_weights=None,
    ):
        super().__init__(
            scale=scale,
            nan_values=nan_values,
            objective_weights=objective_weights,
            variable_weights=variable_weights,
        )


class Max(BaseSchema):
    """Schema for Max."""

    scale: Any = Field(default="mean")
    nan_values: Any | None = Field(default=None)
    objective_weights: Any | None = Field(default=None)
    variable_weights: Any | None = Field(default=None)

    def __init__(
        self,
        scale="mean",
        nan_values=None,
        objective_weights=None,
        variable_weights=None,
    ):
        super().__init__(
            scale=scale,
            nan_values=nan_values,
            objective_weights=objective_weights,
            variable_weights=variable_weights,
        )


class MultiCost(BaseSchema):
    """Schema for MultiCost."""

    costs: Any = Field(...)
    accumulator: Any | None = Field(default=None)
    scale: Any = Field(default="mean")
    nan_values: Any | None = Field(default=None)
    objective_weights: Any | None = Field(default=None)
    variable_weights: Any | None = Field(default=None)

    def __init__(
        self,
        costs,
        accumulator=None,
        scale="mean",
        nan_values=None,
        objective_weights=None,
        variable_weights=None,
    ):
        super().__init__(
            costs=costs,
            accumulator=accumulator,
            scale=scale,
            nan_values=nan_values,
            objective_weights=objective_weights,
            variable_weights=variable_weights,
        )


class ObjectiveFunction(BaseSchema):
    """Schema for ObjectiveFunction."""

    objective_weights: Any = Field(...)
    variable_weights: Any = Field(...)

    def __init__(self, objective_weights, variable_weights):
        super().__init__(
            objective_weights=objective_weights, variable_weights=variable_weights
        )


class RMSE(BaseSchema):
    """Schema for RMSE."""

    scale: Any = Field(default="mean")
    nan_values: Any | None = Field(default=None)
    objective_weights: Any | None = Field(default=None)
    variable_weights: Any | None = Field(default=None)

    def __init__(
        self,
        scale="mean",
        nan_values=None,
        objective_weights=None,
        variable_weights=None,
    ):
        super().__init__(
            scale=scale,
            nan_values=nan_values,
            objective_weights=objective_weights,
            variable_weights=variable_weights,
        )


class SSE(BaseSchema):
    """Schema for SSE."""

    scale: Any = Field(default="mean")
    nan_values: Any | None = Field(default=None)
    objective_weights: Any | None = Field(default=None)
    variable_weights: Any | None = Field(default=None)

    def __init__(
        self,
        scale="mean",
        nan_values=None,
        objective_weights=None,
        variable_weights=None,
    ):
        super().__init__(
            scale=scale,
            nan_values=nan_values,
            objective_weights=objective_weights,
            variable_weights=variable_weights,
        )
