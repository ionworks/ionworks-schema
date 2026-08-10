"""Schemas for transforms."""

from typing import Annotated, Any

from pydantic import Field

from ..base import BaseSchema

# A nested transform schema, a leaf ``Parameter`` schema, a config
# dict, or a runtime ``iwp.Parameter`` on the from_schema path.
_TransformParameter = Annotated[
    dict[str, Any] | BaseSchema | Any,
    Field(union_mode="left_to_right"),
]


class Transform(BaseSchema):
    """Base class for parameter transformations.

    Concrete transforms (``Exp``, ``Identity``, ``Inverse``, ``Log``,
    ``Log10``, ``Negate``, ``Pow10``) inherit from this base, so
    anywhere the schema needs to type "a parameter transform" the type
    is ``Transform``.

    Transforms move parameters between different spaces (e.g. log
    space, exponential space) while maintaining the parameter bounds
    and initial values, and can be chained together.

    Parameters
    ----------
    parameter : Transform or Parameter
        The parameter to transform.
    """

    parameter: _TransformParameter = Field(...)

    def __init__(self, parameter):
        super().__init__(parameter=parameter)

    def to_config(self) -> dict:
        """Build the dict you submit through ``ionworks-api``.

        The output is the inner parameter's config with a
        ``"transform"`` key naming this transform (``"Log"``,
        ``"Exp"``, …). Chained transforms collapse into a single dict
        carrying the outermost transform name plus the underlying
        parameter's bounds and initial value.
        """
        param = self.parameter
        if hasattr(param, "to_config"):
            inner = param.to_config()
        else:
            inner = dict(param) if isinstance(param, dict) else {}
        inner = dict(inner)
        inner.pop("type", None)
        inner.pop("parameter", None)
        inner["transform"] = self.__class__.__name__
        return inner


class Exp(Transform):
    """Exponential transform.

    Transforms a parameter by taking e raised to the power of the parameter value.

    Parameters
    ----------
    parameter : Transform or Parameter
        The parameter to transform.

    Notes
    -----
    - The transform is monotonic"""


class Identity(Transform):
    """Identity transform.

    A transform that returns the input unchanged. Useful as a placeholder or for testing.

    Parameters
    ----------
    parameter : Transform or Parameter
        The parameter to transform.

    Notes
    -----
    - The transform is monotonic"""


class Inverse(Transform):
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


class Log(Transform):
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


class Log10(Transform):
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


class Negate(Transform):
    """Negate transform.

    Transforms a parameter by negating its value (-x).

    Parameters
    ----------
    parameter : Transform or Parameter
        The parameter to transform.

    Notes
    -----
    - The transform is not monotonic"""


class Pow10(Transform):
    """Power of 10 transform.

    Transforms a parameter by raising 10 to the power of the parameter value.

    Parameters
    ----------
    parameter : Transform or Parameter
        The parameter to transform.

    Notes
    -----
    - The transform is monotonic"""
