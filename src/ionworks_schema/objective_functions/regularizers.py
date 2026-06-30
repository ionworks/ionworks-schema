"""Schemas for regularizers (Prior, Constraint, Penalty)."""

from typing import Literal

import pybamm
from pydantic import Field

from .._types import NumberLike
from ..base import BaseSchema
from ..stats.stats import DistributionUnion

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

    type: Literal["Prior"] = Field(default="Prior", exclude=True)
    name: str | list[str] = Field(
        ...,
        description=(
            "Parameter name or list of names the prior applies to. Supplied "
            "by the dict key in a ``parameters`` mapping and excluded from "
            "the serialized config."
        ),
    )
    distribution: DistributionUnion = Field(
        ...,
        description=(
            "Probability distribution describing prior beliefs about the "
            "parameter(s). Accepts any ``ionworks_schema.stats.Distribution`` "
            "(e.g. ``Normal``, ``LogNormal``, ``Uniform``)."
        ),
    )

    def __init__(self, name=None, distribution=None, regularizer_weight=None, **kwargs):
        # Widened for dict-config validation: keep positional name/distribution,
        # accept the ``type`` discriminator + forward via **kwargs.
        super().__init__(
            name=name,
            distribution=distribution,
            regularizer_weight=regularizer_weight,
            **kwargs,
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

    type: Literal["Constraint"] = "Constraint"
    fun: _RegularizerFun = Field(
        ...,
        description=(
            "Constraint expression. For inequality constraints, a Heaviside "
            "of the form ``g(x) <= h(x)``. For equality constraints, "
            "``f(x)`` evaluating to zero when satisfied."
        ),
    )

    # ``type`` is an __init__ param (shadowing the builtin is intentional and
    # matches AskTellOptimizer/GridSearch) so a round-tripped config carrying
    # the ``type`` discriminator validates instead of raising.
    def __init__(self, fun, regularizer_weight=None, type="Constraint"):
        super().__init__(fun=fun, regularizer_weight=regularizer_weight, type=type)


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

    type: Literal["Penalty"] = "Penalty"
    fun: _RegularizerFun = Field(
        ...,
        description=("Penalty expression as a ``pybamm.Symbol`` or a constant number."),
    )

    def __init__(self, fun, regularizer_weight=None, type="Penalty"):
        super().__init__(fun=fun, regularizer_weight=regularizer_weight, type=type)


def resolve_prior(value, name=None):
    """Resolve one prior config to a validated ``Prior`` instance.

    The parameter ``name`` the prior applies to comes from the mapping key when
    priors are given as a ``{name: prior}`` mapping; it is injected when the
    config dict omits it (``to_config`` excludes ``name`` — it is the key).
    A ``Prior`` instance passes through unchanged. Anything else that isn't a
    config dict is rejected: the contract holds only ``ionworks_schema`` objects,
    so a live ``ionworkspipeline`` runtime prior must be converted before it
    enters a schema, not embedded raw.
    """
    if isinstance(value, Prior):
        return value
    if not isinstance(value, dict):
        raise ValueError(
            f"Invalid prior {value!r}: expected a prior config dict or a Prior "
            f"instance; got {type(value).__name__}. Live ionworkspipeline "
            f"runtime objects are not accepted inside a schema."
        )
    data = dict(value)
    # ``type`` is the discriminator: validate it rather than discarding it, so a
    # sibling (``Penalty``) or unknown type can't be silently coerced to a Prior.
    declared_type = data.pop("type", None)
    if declared_type is not None and declared_type != "Prior":
        raise ValueError(
            f"Invalid prior type {declared_type!r}: expected 'Prior'. "
            f"Constraints and penalties are separate fields, not priors."
        )
    # The mapping key is the authoritative parameter name (matches the engine's
    # parse_datafit_priors) — it overrides any name embedded in the config.
    if name is not None:
        data["name"] = name
    # Flat form (engine ``parse_priors``): a string ``distribution`` with its
    # params inline; lift them into a nested distribution config to validate.
    if isinstance(data.get("distribution"), str):
        reserved = {"name", "regularizer_weight"}
        data["distribution"] = {k: data.pop(k) for k in list(data) if k not in reserved}
    try:
        return Prior.model_validate(data)
    except TypeError as exc:
        raise ValueError(f"Invalid config for prior: {exc}") from exc


def resolve_priors_field(priors):
    """Resolve the ``priors`` field — a ``{name: prior}`` mapping, a list of
    priors, or a single prior instance.

    A dict is always a ``{name: prior}`` mapping (matching the engine's
    ``parse_datafit_priors``, which keys on the mapping), so the parameter name
    is taken from the key — including when a parameter is named ``distribution``.
    """
    if isinstance(priors, dict):
        return {key: resolve_prior(val, name=key) for key, val in priors.items()}
    if isinstance(priors, list):
        return [resolve_prior(p) for p in priors]
    return resolve_prior(priors)
