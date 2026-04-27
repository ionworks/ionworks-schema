"""Schemas for regularizers (e.g. Prior)."""

from typing import Any

from pydantic import Field

from ..base import BaseSchema


class Prior(BaseSchema):
    """
    A function that takes a dictionary of inputs and returns a value.

    Parameters
    ----------
    fun : callable
        The penalty function that takes a dictionary of inputs and returns a value.
    regularizer_weight : float, optional
        The weight applied to the penalty term. Default is 1.0.
    """

    _exclude_fields = {"name"}

    name: Any = Field(...)
    distribution: Any = Field(...)
    regularizer_weight: Any | None = Field(default=None)

    def __init__(self, name, distribution, regularizer_weight=None):
        super().__init__(
            name=name,
            distribution=distribution,
            regularizer_weight=regularizer_weight,
        )
