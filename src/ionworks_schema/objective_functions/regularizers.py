"""Schemas for regularizers (Prior, Constraint, Penalty)."""

from typing import Any

from pydantic import Field

from ..base import BaseSchema


class Prior(BaseSchema):
    """Regularization prior on a parameter.

    Mirrors ``iwp.priors.Prior``.

    Parameters
    ----------
    name : str or list of str
        Parameter name(s) the prior applies to.
    distribution : ionworks_schema.stats.Distribution
        Probability distribution describing prior beliefs about the parameter(s).
    regularizer_weight : float, optional
        Weight applied to the prior's contribution to the cost. Default is 1.0.
    """

    _exclude_fields = {"name"}

    name: Any = Field(
        ...,
        description=(
            "Parameter name or list of names the prior applies to. Supplied "
            "by the dict key in a ``parameters`` mapping and excluded from "
            "the serialized config."
        ),
    )
    distribution: Any = Field(
        ...,
        description=(
            "Probability distribution describing prior beliefs about the "
            "parameter(s). Accepts any ``ionworks_schema.stats.Distribution`` "
            "(e.g. ``Normal``, ``LogNormal``, ``Uniform``)."
        ),
    )
    regularizer_weight: Any | None = Field(
        default=None,
        description=(
            "Weight applied to the prior's contribution to the cost. "
            "Defaults to 1.0 when unset."
        ),
    )

    def __init__(self, name, distribution, regularizer_weight=None):
        super().__init__(
            name=name,
            distribution=distribution,
            regularizer_weight=regularizer_weight,
        )


class _FunRegularizer(BaseSchema):
    """Shared base for regularizers wrapping a single ``pybamm.Symbol`` or number.

    Subclasses (`Constraint`, `Penalty`) exist only to drive the ``type`` tag in
    ``to_config`` so the pipeline parser can dispatch to the right regularizer
    class. Do not use this base directly.
    """

    fun: Any = Field(
        ...,
        description=(
            "Regularizer expression as a ``pybamm.Symbol`` or a constant "
            "number. See the ``Constraint`` / ``Penalty`` subclasses for the "
            "specific semantics expected of this expression."
        ),
    )
    regularizer_weight: Any | None = Field(
        default=None,
        description=(
            "Weight applied to the regularizer term in the cost. Defaults "
            "to 1.0 when unset."
        ),
    )

    def __init__(self, fun, regularizer_weight=None):
        super().__init__(fun=fun, regularizer_weight=regularizer_weight)


class Constraint(_FunRegularizer):
    """Equality or inequality constraint evaluated at fit time.

    Mirrors ``iwp.data_fits.objective_functions.regularizers.Constraint``.
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
    """


class Penalty(_FunRegularizer):
    """Soft penalty term added to the fit cost.

    Mirrors ``iwp.data_fits.objective_functions.regularizers.Penalty``.

    Parameters
    ----------
    fun : pybamm.Symbol or Number
        Penalty expression as a ``pybamm.Symbol`` or a constant number.
    regularizer_weight : float, optional
        Weight applied to the penalty term. Default is 1.0.
    """
