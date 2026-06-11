"""Schemas for regularizers (Prior, Constraint, Penalty)."""

from typing import Annotated, Any

import pybamm
from pydantic import Field

from .._types import NumberLike
from ..base import BaseSchema
from ..stats.stats import Distribution

# A schema ``stats.Distribution`` instance, a raw config dict, or a
# runtime ``iwp.stats.Distribution`` on the from_schema path.
_DistributionLike = Annotated[
    dict[str, Any] | Distribution | Any,
    Field(union_mode="left_to_right"),
]
_RegularizerFun = pybamm.Symbol | NumberLike


class Regularizer(BaseSchema):
    """Base class for regularizer terms added to the fit cost.

    Concrete subclasses (``Prior``, ``Constraint``, ``Penalty``) inherit
    the shared ``regularizer_weight`` field.
    """

    regularizer_weight: NumberLike | None = Field(
        default=None,
        description=(
            "Weight applied to the regularizer term in the cost. Defaults "
            "to 1.0 when unset."
        ),
    )


class Prior(Regularizer):
    """Regularization prior on a parameter.

    Parameters
    ----------
    name : str or list of str
        Parameter name(s) the prior applies to.
    distribution : ionworks_schema.stats.Distribution
        Probability distribution describing prior beliefs about the parameter(s).
    regularizer_weight : float, optional
        Weight applied to the prior's contribution to the cost. Default is 1.0.

    Examples
    --------
    >>> prior = iws.priors.Prior("Q_pe", iws.stats.Normal(mean=3.0, std=0.2))
    >>> fit = iws.DataFit(
    ...     objectives={"ocp": iws.objectives.OCPHalfCell(
    ...         electrode="positive", data_input="path/to/ocp.csv",
    ...     )},
    ...     priors={"Q_pe": prior},
    ... )
    """

    _exclude_fields = {"name"}

    name: str | list[str] = Field(
        ...,
        description=(
            "Parameter name or list of names the prior applies to. Supplied "
            "by the dict key in a ``parameters`` mapping and excluded from "
            "the serialized config."
        ),
    )
    distribution: _DistributionLike = Field(
        ...,
        description=(
            "Probability distribution describing prior beliefs about the "
            "parameter(s). Accepts any ``ionworks_schema.stats.Distribution`` "
            "(e.g. ``Normal``, ``LogNormal``, ``Uniform``)."
        ),
    )

    def __init__(self, name, distribution, regularizer_weight=None):
        super().__init__(
            name=name,
            distribution=distribution,
            regularizer_weight=regularizer_weight,
        )


class Constraint(Regularizer):
    """Equality or inequality constraint evaluated at fit time.

    Inequality constraints use ``pybamm`` Heaviside operators (``<=``, ``>=``);
    equality constraints use a ``pybamm.Symbol`` that evaluates to zero when
    satisfied.

    Parameters
    ----------
    fun : pybamm.Symbol or Number
        Constraint expression. For inequality constraints, a Heaviside of the
        form ``g(x) <= h(x)``. For equality constraints, ``f(x)`` evaluating to
        zero when satisfied.
    regularizer_weight : float, optional
        Weight applied to the constraint term. Default is 1.0.

    Examples
    --------
    >>> import pybamm
    >>> x0, x1 = pybamm.InputParameter("x0"), pybamm.InputParameter("x1")
    >>> con = iws.objective_functions.Constraint(fun=x0 - 0.5 * x1)
    >>> obj = iws.objectives.OCPHalfCell(
    ...     electrode="positive", data_input="path/to/ocp.csv",
    ...     constraints=[con],
    ... )
    """

    fun: _RegularizerFun = Field(
        ...,
        description=(
            "Constraint expression. For inequality constraints, a Heaviside "
            "of the form ``g(x) <= h(x)``. For equality constraints, "
            "``f(x)`` evaluating to zero when satisfied."
        ),
    )

    def __init__(self, fun, regularizer_weight=None):
        super().__init__(fun=fun, regularizer_weight=regularizer_weight)


class Penalty(Regularizer):
    """Soft penalty term added to the fit cost.

    Parameters
    ----------
    fun : pybamm.Symbol or Number
        Penalty expression as a ``pybamm.Symbol`` or a constant number.
    regularizer_weight : float, optional
        Weight applied to the penalty term. Default is 1.0.

    Examples
    --------
    >>> import pybamm
    >>> x = pybamm.InputParameter("x")
    >>> pen = iws.objective_functions.Penalty(fun=x ** 2, regularizer_weight=0.1)
    >>> obj = iws.objectives.OCPHalfCell(
    ...     electrode="positive", data_input="path/to/ocp.csv",
    ...     penalties=[pen],
    ... )
    """

    fun: _RegularizerFun = Field(
        ...,
        description=("Penalty expression as a ``pybamm.Symbol`` or a constant number."),
    )

    def __init__(self, fun, regularizer_weight=None):
        super().__init__(fun=fun, regularizer_weight=regularizer_weight)
