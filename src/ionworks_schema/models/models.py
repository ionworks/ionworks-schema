"""Schemas for models."""

from typing import Any

from pydantic import Field

from ..base import BaseSchema


class MSMRFullCellModel(BaseSchema):
    """Schema for MSMRFullCellModel."""

    negative_electrode_model: Any = Field(...)
    positive_electrode_model: Any = Field(...)
    options: Any | None = Field(default=None)

    def __init__(
        self, negative_electrode_model, positive_electrode_model, options=None
    ):
        super().__init__(
            negative_electrode_model=negative_electrode_model,
            positive_electrode_model=positive_electrode_model,
            options=options,
        )


class MSMRHalfCellModel(BaseSchema):
    """Schema for MSMRHalfCellModel."""

    electrode: Any = Field(...)
    options: Any | None = Field(default=None)

    def __init__(self, electrode, options=None):
        super().__init__(electrode=electrode, options=options)
