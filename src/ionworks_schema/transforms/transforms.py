"""Schemas for transforms."""

from typing import Any

from pydantic import Field

from ..base import BaseSchema


class Exp(BaseSchema):
    """Exponential transform.

    Transforms a parameter by taking e raised to the power of the parameter value.

    Parameters
    ----------
    parameter : Transform or Parameter
        The parameter to transform.

    Notes
    -----
    - The transform is monotonic"""

    parameter: Any = Field(...)

    def __init__(self, parameter):
        super().__init__(parameter=parameter)


class Identity(BaseSchema):
    """Identity transform.

    A transform that returns the input unchanged. Useful as a placeholder or for testing.

    Parameters
    ----------
    parameter : Transform or Parameter
        The parameter to transform.

    Notes
    -----
    - The transform is monotonic"""

    parameter: Any = Field(...)

    def __init__(self, parameter):
        super().__init__(parameter=parameter)


class Inverse(BaseSchema):
    """Inverse (1/x) transform.

    Transforms a parameter by taking its reciprocal (1/x). Cannot be used with zero values.

    Parameters
    ----------
    parameter : Transform or Parameter
        The parameter to transform.

    Notes
    -----
    - The transform is not monotonic
    - Input values cannot be zero"""

    parameter: Any = Field(...)

    def __init__(self, parameter):
        super().__init__(parameter=parameter)


class Log(BaseSchema):
    """Natural logarithm transform.

    Transforms a parameter by taking its natural logarithm. Only works with positive values.

    Parameters
    ----------
    parameter : Transform or Parameter
        The parameter to transform.

    Notes
    -----
    - The transform is monotonic
    - Input values must be positive"""

    parameter: Any = Field(...)

    def __init__(self, parameter):
        super().__init__(parameter=parameter)


class Log10(BaseSchema):
    """Logarithm base 10 transform.

    Transforms a parameter by taking its base-10 logarithm. Only works with positive values.

    Parameters
    ----------
    parameter : Transform or Parameter
        The parameter to transform.

    Notes
    -----
    - The transform is monotonic
    - Input values must be positive"""

    parameter: Any = Field(...)

    def __init__(self, parameter):
        super().__init__(parameter=parameter)


class Negate(BaseSchema):
    """Negate transform.

    Transforms a parameter by negating its value (-x).

    Parameters
    ----------
    parameter : Transform or Parameter
        The parameter to transform.

    Notes
    -----
    - The transform is not monotonic"""

    parameter: Any = Field(...)

    def __init__(self, parameter):
        super().__init__(parameter=parameter)


class Pow10(BaseSchema):
    """Power of 10 transform.

    Transforms a parameter by raising 10 to the power of the parameter value.

    Parameters
    ----------
    parameter : Transform or Parameter
        The parameter to transform.

    Notes
    -----
    - The transform is monotonic"""

    parameter: Any = Field(...)

    def __init__(self, parameter):
        super().__init__(parameter=parameter)


class Transform(BaseSchema):
    """Base class for parameter transformations.

    This class provides functionality to transform parameters between different spaces
    (e.g., log space, exponential space) while maintaining the parameter bounds and
    initial values. Transforms can be chained together.

    Parameters
    ----------
    parameter : Transform or Parameter
        The parameter to transform.

    Attributes
    ----------
    parent : Transform or None
        The parent transform in a chain of transforms.
    child : Transform or Parameter
        The child transform/parameter in a chain of transforms.
    base_parameter : Parameter
        The original parameter being transformed.
    monotonic_transform : bool
        Whether this transform is monotonic."""

    parameter: Any = Field(...)

    def __init__(self, parameter):
        super().__init__(parameter=parameter)
