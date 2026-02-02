"""Schemas for transforms."""

from typing import Any

from pydantic import Field

from ..base import BaseSchema


class Exp(BaseSchema):
    """Schema for Exp."""

    parameter: Any = Field(...)

    def __init__(self, parameter):
        super().__init__(parameter=parameter)


class Identity(BaseSchema):
    """Schema for Identity."""

    parameter: Any = Field(...)

    def __init__(self, parameter):
        super().__init__(parameter=parameter)


class Inverse(BaseSchema):
    """Schema for Inverse."""

    parameter: Any = Field(...)

    def __init__(self, parameter):
        super().__init__(parameter=parameter)


class Log(BaseSchema):
    """Schema for Log."""

    parameter: Any = Field(...)

    def __init__(self, parameter):
        super().__init__(parameter=parameter)


class Log10(BaseSchema):
    """Schema for Log10."""

    parameter: Any = Field(...)

    def __init__(self, parameter):
        super().__init__(parameter=parameter)


class Negate(BaseSchema):
    """Schema for Negate."""

    parameter: Any = Field(...)

    def __init__(self, parameter):
        super().__init__(parameter=parameter)


class Pow10(BaseSchema):
    """Schema for Pow10."""

    parameter: Any = Field(...)

    def __init__(self, parameter):
        super().__init__(parameter=parameter)


class Transform(BaseSchema):
    """Schema for Transform."""

    parameter: Any = Field(...)

    def __init__(self, parameter):
        super().__init__(parameter=parameter)
