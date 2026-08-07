"""Schemas for objective_functions."""

from typing import Annotated, Any, ClassVar, Literal

from pydantic import Field, field_validator, model_validator

from .._types import NamedFloatMap, NumberLike
from ..base import BaseSchema

# Method name (``"mean"``, ``"identity"``, ``"range"``, …) or numeric value.
_NormalizationLike = str | NumberLike

# Mapping of objective name to the variable names to compute for it, or None
# to compute all of that objective's variables.
_CalculationStructure = dict[str, list[str] | None]

# Shared descriptions for fields that appear on every ErrorFunction subclass.
_NORMALIZATION_DESCRIPTION = (
    "How to normalize the model and data for each variable in the cost. "
    "One of ``'mean'`` (mean of the data), ``'range'`` (range of the data), "
    "``'sum_squares'`` (sum of squares), ``'mean_squares'`` (mean sum of "
    "squares), ``'root_mean_squares'`` (root mean square), ``'identity'`` "
    "(use 1), or a float value."
)
_NAN_VALUES_DESCRIPTION = (
    "How to replace NaN values in the model output. ``'mean'`` uses the "
    "mean of the non-NaN model values, ``'min'`` uses the minimum, and a "
    "float uses that fixed value. Defaults to ``'mean'``."
)
_OBJECTIVE_WEIGHTS_DESCRIPTION = (
    "Mapping of objective name to weight. Objectives absent from the dict "
    "receive a weight of 1. If None, all objectives are weighted equally."
)
_VARIABLE_WEIGHTS_DESCRIPTION = (
    "Mapping of variable name to weight. Variables absent from the dict "
    "receive a weight of 1. If None, all variables are weighted equally."
)
_CALCULATION_STRUCTURE_DESCRIPTION = (
    "Explicit objective/variable scoping: a mapping of objective name to the "
    "list of variable names to compute for it, or null to compute all of that "
    "objective's variables (an empty list computes none). When omitted, the "
    "cost computes every objective and variable present in the outputs. Use "
    "this to keep a per-variable cost (e.g. SSE) from consuming variables that "
    "only a weighted Wasserstein should, such as model-axis dQ/dV arrays whose "
    "model and data lengths differ by construction."
)
_OBJECTIVE_NAMES_DEPRECATED_DESCRIPTION = (
    "Deprecated alias for objective-level scoping: a flat list of objective "
    "names this cost applies to (all variables of each). Use "
    "``calculation_structure`` instead."
)


class ObjectiveFunction(BaseSchema):
    """Base class for all cost / objective functions.

    Concrete cost classes (``RMSE``, ``MAE``, ``Max``, ``ChiSquare``,
    ``GaussianLogLikelihood``, ``DesignFunction``, …) all inherit from
    this base. Construct one of those — fields that take "a cost" accept the
    concrete classes, not this base.

    Parameters
    ----------
    objective_weights : dict[str, float], optional
        Mapping of objective name to weight in the combined cost. If
        None, all objectives are weighted equally. Objectives not
        listed in the dict get a weight of 1.
    variable_weights : dict[str, float], optional
        Mapping of variable name to weight. If None, all variables
        are weighted equally. Variables not listed in the dict get a
        weight of 1.
    nan_values : str or float, optional
        How to replace NaN values in the model output.

            * ``"mean"``: use the mean of the non-NaN model values.
            * ``"min"``: use the minimum of the non-NaN model values.
            * float: use that fixed value.

        Defaults to ``"mean"``.
    calculation_structure : dict[str, list[str] or None], optional
        Explicit objective/variable scoping. Maps each objective name to the
        list of variable names to compute for it, or None to compute all of
        that objective's variables (an empty list computes none). When None,
        the cost computes every objective and variable in the outputs.
    objective_names : list[str], optional
        Deprecated. A flat list of objective names this cost applies to (all
        variables of each). Use ``calculation_structure`` instead.
    """

    objective_weights: NamedFloatMap | None = Field(
        default=None,
        description=_OBJECTIVE_WEIGHTS_DESCRIPTION,
    )
    variable_weights: NamedFloatMap | None = Field(
        default=None,
        description=_VARIABLE_WEIGHTS_DESCRIPTION,
    )
    nan_values: _NormalizationLike | None = Field(
        default=None,
        description=_NAN_VALUES_DESCRIPTION,
    )
    calculation_structure: _CalculationStructure | None = Field(
        default=None,
        description=_CALCULATION_STRUCTURE_DESCRIPTION,
    )
    objective_names: list[str] | None = Field(
        default=None,
        description=_OBJECTIVE_NAMES_DEPRECATED_DESCRIPTION,
    )

    # ClassVar avoids Pydantic wrapping an unannotated underscore attr in
    # ModelPrivateAttr (see _COSTS_FORM_HINT below for why that matters).
    _unsupported_fields: ClassVar[frozenset[str]] = frozenset()
    _unsupported_fields_hint: ClassVar[str] = ""

    @model_validator(mode="after")
    def _check_scoping_keys(self):
        if self.calculation_structure is not None and self.objective_names is not None:
            raise ValueError(
                "Specify only one of 'calculation_structure' or the deprecated "
                "'objective_names', not both."
            )
        return self

    @model_validator(mode="after")
    def _check_unsupported_fields(self):
        for field in self._unsupported_fields:
            if getattr(self, field) is not None:
                message = f"{type(self).__name__} does not support '{field}'."
                if self._unsupported_fields_hint:
                    message = f"{message} {self._unsupported_fields_hint}"
                raise ValueError(message)
        return self


class ErrorFunction(ObjectiveFunction):
    """Base for residual-based error measures (also known as distance functions).

    Adds ``normalization`` on top of
    ``ObjectiveFunction``. ``RMSE``, ``MAE``, ``MSE``, ``Max``, ``SSE``,
    ``ChiSquare``, ``Wasserstein``, and ``MultiCost`` all inherit from here.

    Parameters
    ----------
    normalization : str or float, optional
        How to normalize the model and data for each variable in the
        cost.

            * ``"mean"`` (default): use the mean of the data.
            * ``"identity"``: use 1 (no normalization).
            * ``"range"``: use the range of the data.
            * ``"sum_squares"``: use the sum of squares of the data.
            * ``"mean_squares"``: use the mean of the sum of squares of
                the data.
            * ``"root_mean_squares"``: use the root mean square of the
                data.
            * float: use that fixed value.
    nan_values : str or float, optional
        How to replace NaN values in the model output — see
        :class:`ObjectiveFunction`.
    objective_weights : dict[str, float], optional
        Per-objective weights — see :class:`ObjectiveFunction`.
    variable_weights : dict[str, float], optional
        Per-variable weights — see :class:`ObjectiveFunction`.
    """

    normalization: _NormalizationLike | None = Field(
        default=None, description=_NORMALIZATION_DESCRIPTION
    )

    @model_validator(mode="before")
    @classmethod
    def _reject_scale_alias(cls, data):
        # Surface the canonical name instead of a bare extra_forbidden error.
        if isinstance(data, dict) and "scale" in data:
            raise ValueError("'scale' is removed; use 'normalization' instead.")
        return data


class RMSE(ErrorFunction):
    """Root-mean-square-error cost function.

    Takes the square root of the MSE to provide a value in the same units as the original data.
    This is often used in scientific and engineering applications when the magnitude of error
    in the original units is important.

    This cost function only supports scalar output, so it cannot be used with a
    least-squares optimizer — including when nested inside a ``MultiCost``.

    Examples
    --------
    >>> cost = iws.costs.RMSE()
    >>> # slot into a DataFit's `cost` or a Validation's `summary_stats`
    >>> val = iws.Validation(
    ...     objectives={"cycle": iws.objectives.CurrentDriven(data_input="path/to/cycle.csv")},
    ...     summary_stats=[cost],
    ... )"""

    type: Literal["RMSE"] = "RMSE"


class MAE(ErrorFunction):
    """Mean-absolute-error cost function.

    Instead of squaring residuals, this cost function uses the absolute values, which
    makes it less sensitive to outliers compared to squared-error metrics.

    For scalar output, it returns the sum of absolute residuals divided by the number of points.
    For array output, it returns the signed square root of the absolute residuals,
    normalized by the square root of the number of points.

    Examples
    --------
    >>> cost = iws.costs.MAE()
    >>> val = iws.Validation(
    ...     objectives={"cycle": iws.objectives.CurrentDriven(data_input="path/to/cycle.csv")},
    ...     summary_stats=[cost],
    ... )"""

    type: Literal["MAE"] = "MAE"


class MSE(ErrorFunction):
    """Mean-square-error cost function.

    Similar to SSE, but normalizes by the number of data points.
    This makes the cost independent of the number of data points.

    For scalar output, it returns the sum of squared residuals divided by the number of points.
    For array output, it returns the SSE residuals divided by the square root of the number of points."""

    type: Literal["MSE"] = "MSE"


class Max(ErrorFunction):
    """Cost function that reports the maximum error between the model and the data.

    For scalar output, it returns the maximum absolute value of any residual.
    For array output, it returns a single-element array containing the square root
    of the maximum error.

    Useful when you want to minimize the worst-case error rather than an average.

    Examples
    --------
    >>> cost = iws.costs.Max()
    >>> val = iws.Validation(
    ...     objectives={"cycle": iws.objectives.CurrentDriven(data_input="path/to/cycle.csv")},
    ...     summary_stats=[cost],
    ... )"""

    type: Literal["Max"] = "Max"


class SSE(ErrorFunction):
    """Sum-of-squared-errors cost function.

    Calculates the sum of squared differences between model and data:
    SSE = Σ(model - data)²"""

    type: Literal["SSE"] = "SSE"


class Wasserstein(ErrorFunction):
    """Wasserstein distance cost function.

    By default iterates per-objective-variable and computes the
    Wasserstein-1 distance between each pair of model / data sample
    arrays with uniform weights.

    When both ``position_variable`` and ``weight_variable`` are set, the
    cost switches to a **weighted point-cloud** mode: one variable
    supplies positions, the other supplies (sign-stripped, renormalised)
    weights, and a single Wasserstein-1 call is made per objective with
    ``W1(positions_model, positions_data, w_model, w_data)``. Useful for
    matching densities by position — e.g. lining up dQ/dV peaks in
    voltage rather than comparing sample-by-sample dQ/dV values.

    Both ``position_variable`` and ``weight_variable`` must be provided
    together; setting only one is rejected.

    Parameters
    ----------
    position_variable : str, optional
        Name of the variable supplying point positions in weighted mode.
    weight_variable : str, optional
        Name of the variable supplying point weights in weighted mode.
        Absolute value is used and renormalised internally.
    """

    type: Literal["Wasserstein"] = "Wasserstein"

    position_variable: str | None = Field(
        default=None,
        description=(
            "Variable name to use as Wasserstein positions (weighted "
            "mode). Set together with ``weight_variable`` or leave both "
            "unset."
        ),
    )
    weight_variable: str | None = Field(
        default=None,
        description=(
            "Variable name supplying the (unsigned) point weights "
            "(weighted mode). Set together with ``position_variable`` "
            "or leave both unset."
        ),
    )

    @model_validator(mode="after")
    def _check_weighted_pair(self) -> "Wasserstein":
        if (self.position_variable is None) != (self.weight_variable is None):
            raise ValueError(
                "Wasserstein: ``position_variable`` and ``weight_variable`` must "
                "be set together (both or neither)."
            )
        return self


class ChiSquare(ErrorFunction):
    """Chi-square cost function that measures the weighted sum of squared differences between
    observed and expected values, normalized by their standard deviations.

    The chi-square statistic is calculated as:
    chi2 = sum((observed - expected) / sigma)**2
    where sigma is the standard deviation for each variable.

    Parameters
    ----------
    variable_standard_deviations : dict
        Dictionary mapping variable names to their standard deviations.
        For example: {"a": 0.5, "b": 0.3} means variable "a" has sigma=0.5
        and variable "b" has sigma=0.3.

    Notes
    -----
    For a dataset with N points, if the model fits the data well and the errors
    are normally distributed, the chi-square value should be approximately N
    (the number of degrees of freedom).

    Does not support ``normalization`` (fixed at 1) or ``variable_weights``
    (derived from ``variable_standard_deviations`` instead); ``objective_weights``
    is also unsupported."""

    type: Literal["ChiSquare"] = "ChiSquare"

    _unsupported_fields: ClassVar[frozenset[str]] = frozenset(
        {"normalization", "objective_weights", "variable_weights"}
    )

    variable_standard_deviations: NamedFloatMap = Field(
        ...,
        description=(
            "Mapping from variable name to its standard deviation ``sigma``. "
            "Each residual is normalized by ``sigma`` before squaring, so a "
            "well-fitting model yields a chi-square value close to the "
            "number of data points."
        ),
    )


class MultiCost(ErrorFunction):
    """Cost function combining several component costs into one weighted total.

    Each component cost is evaluated on the shared model/data outputs, scaled by
    its weight, and the weighted values are summed.
    Use it to make a fit trade off two error measures at once — for example an
    ``RMSE`` over the whole curve plus a ``Max`` term that punishes the
    worst-case point.

    Parameters
    ----------
    costs : list
        The component costs. A bare cost gets weight 1.0; wrap one in
        :class:`WeightedCost` to give it another. At least one component is
        required. A ``{cost: weight}`` mapping is not accepted — cost objects
        are not hashable. (``.to_config()`` serializes every component to a
        ``{"cost": <cost>, "weight": <float>}`` record, which also validates
        back into this field — that is how a stored config round-trips, not a
        form to write by hand.)

    Notes
    -----
    ``normalization``, ``nan_values``, ``objective_weights`` and
    ``variable_weights`` are rejected here — a ``MultiCost`` only weights and sums
    what its components return, so it cannot apply them. Set them on the component
    costs instead.

    Every component cost must support the output mode (scalar or residuals) that
    the optimizer requests. ``RMSE`` supports scalar output only, so a
    ``MultiCost`` containing it needs a scalar optimizer, not a least-squares one.

    Examples
    --------
    >>> # weight a worst-case term against the overall RMSE
    >>> cost = iws.costs.MultiCost(
    ...     costs=[iws.costs.RMSE(), iws.costs.WeightedCost(iws.costs.Max(), 0.25)],
    ... )
    >>> # equal weights: pass bare costs
    >>> equal = iws.costs.MultiCost(costs=[iws.costs.RMSE(), iws.costs.Max()])
    """

    type: Literal["MultiCost"] = "MultiCost"

    _unsupported_fields: ClassVar[frozenset[str]] = frozenset(
        {"normalization", "nan_values", "objective_weights", "variable_weights"}
    )
    _unsupported_fields_hint: ClassVar[str] = (
        "A MultiCost only weights and sums its components' results; set this on "
        "the component costs instead."
    )

    costs: list[
        Annotated["CostUnion | WeightedCost", Field(union_mode="left_to_right")]
    ] = Field(
        ...,
        min_length=1,
        description=(
            "Component costs. A bare cost gets weight 1.0; wrap one in "
            "``WeightedCost(cost, weight)`` to give it another. Each component "
            "cost is evaluated on the shared outputs, weighted, and summed. At "
            "least one component is required."
        ),
    )

    # ClassVar is required: pydantic wraps an unannotated underscore attribute in
    # ModelPrivateAttr, which then leaks into the message on class access.
    _COSTS_FORM_HINT: ClassVar[str] = (
        "Pass a list of costs: costs=[iws.costs.RMSE(), "
        "iws.costs.WeightedCost(iws.costs.Max(), 0.25)]. A bare cost gets "
        "weight 1.0; 'weight' is optional and defaults to 1.0."
    )

    @field_validator("costs", mode="before")
    @classmethod
    def _reject_weight_mapping(cls, costs):
        """Reject the {cost: weight} mapping with a message naming the accepted form.

        Cost objects are not hashable, so this dict could never actually be
        built with a real cost as a key — but failing here says so plainly
        instead of tripping over the unrelated "not a list" shape further down.
        """
        if isinstance(costs, dict):
            raise ValueError(
                "MultiCost 'costs' must be a list, not a mapping. "
                "ionworks_schema cost objects are not hashable, so a "
                f"{{cost: weight}} dict cannot be built at all. {cls._COSTS_FORM_HINT}"
            )
        return costs

    @field_validator("costs")
    @classmethod
    def _reject_repeated_cost(cls, costs):
        """Reject the same cost object listed twice, as a component or wrapped.

        Identity, not equality: two structurally identical costs are two genuine
        components — that is what a serialized config validates back to — but one
        object appearing twice weights it double by accident.
        """
        seen: set[int] = set()
        for entry in costs:
            cost = entry.cost if isinstance(entry, WeightedCost) else entry
            if id(cost) in seen:
                raise ValueError(
                    "MultiCost 'costs' lists the same cost object more than once. "
                    "Construct a separate cost instance per component, or wrap it "
                    "in WeightedCost(cost, weight) to change its weight."
                )
            seen.add(id(cost))
        return costs

    def to_config(self) -> dict:
        """Serialize to the wire format, normalizing every component to a record.

        Every entry — bare cost or :class:`WeightedCost` — becomes a
        ``{"cost": ..., "weight": ...}`` record so the emitted config matches
        what the pipeline parser reads, regardless of which form was used to
        construct this instance.
        """
        config = super().to_config()
        config["costs"] = [
            entry.to_config()
            if isinstance(entry, WeightedCost)
            else {"cost": entry.to_config(), "weight": 1.0}
            for entry in self.costs
        ]
        return config


class GaussianLogLikelihood(ObjectiveFunction):
    """Gaussian negative log-likelihood cost function.

    Computes the Gaussian NLL:

        NLL = 0.5 * Σ_vars [ N_i * log(2π * σ_i²) + Σ_j (y_ij - ŷ_ij)² / σ_i² ]

    This enables MLE with noise estimation, MAP estimation, and Bayesian
    posterior sampling (MCMC).

    Parameters
    ----------
    sigma : dict[str, float | str]
        Mapping of variable names to noise standard deviations (σ). Values
        can be:

        - A float: fixed known noise standard deviation.
        - A string: name of a fitting parameter to be optimised (looked up
          from the current inputs at evaluation time via
          ``set_current_inputs``).
    nan_values : str or float, optional
        How to handle NaN values in model output. Options: a float constant
        (default: 1e6), "mean", or "min". The default fills NaN with a large
        penalty value to ensure solver failures produce high costs.

    Notes
    -----
    Does not support ``objective_weights`` or ``variable_weights``: every
    variable already carries its own noise scale via ``sigma``, so a separate
    weight would double-count it.

    Examples
    --------
    >>> cost = iws.costs.GaussianLogLikelihood(sigma={"Voltage [V]": 0.005})
    >>> fit = iws.DataFit(
    ...     objectives={"cycle": iws.objectives.CurrentDriven(data_input="path/to/cycle.csv")},
    ...     parameters={"x": iws.Parameter("x", initial_value=1.0, bounds=(0.0, 2.0))},
    ...     cost=cost,
    ... )
    """

    type: Literal["GaussianLogLikelihood"] = "GaussianLogLikelihood"

    _unsupported_fields: ClassVar[frozenset[str]] = frozenset(
        {"objective_weights", "variable_weights"}
    )

    sigma: dict[str, NumberLike | str] = Field(
        ...,
        description=(
            "Mapping from variable name to the noise standard deviation "
            "``sigma``. Each value may be a float (fixed known noise) or a "
            "string naming a fitting parameter to be optimized jointly with "
            "the model parameters."
        ),
    )


class DesignFunction(ObjectiveFunction):
    """A generalized design cost function for optimization problems.

    This class serves as a base for design optimization objectives where
    the goal is to maximize (or minimize) certain design metrics like
    energy density, power density, etc.

    Parameters
    ----------
    objective_weights : dict, optional
        Dictionary of {name: weight} pairs for each objective in the cost function. If
        None, all objectives are weighted equally. If a name is not in the dictionary,
        it is given a weight of 1.

    Notes
    -----
    Does not support ``nan_values`` or ``variable_weights``: design metrics are
    scalar-per-objective, so there is no per-variable axis to weight or fill NaNs
    on."""

    type: Literal["DesignFunction"] = "DesignFunction"

    _unsupported_fields: ClassVar[frozenset[str]] = frozenset(
        {"nan_values", "variable_weights"}
    )


#: Discriminated union of concrete cost functions, keyed on ``type``.
CostUnion = Annotated[
    RMSE
    | MAE
    | MSE
    | Max
    | SSE
    | Wasserstein
    | ChiSquare
    | MultiCost
    | GaussianLogLikelihood
    | DesignFunction,
    Field(discriminator="type"),
]


class WeightedCost(BaseSchema):
    """A cost paired with the weight applied to it in a :class:`MultiCost`.

    Wrap a cost in ``WeightedCost(cost, weight)`` to give it a weight other than
    the default of 1.0 inside ``MultiCost(costs=[...])``. It serializes to a bare
    ``{"cost": ..., "weight": ...}`` record, with no ``"type"`` key, so the
    emitted config matches what the pipeline parser reads.

    Parameters
    ----------
    cost : ObjectiveFunction
        The component cost function.
    weight : float, optional
        Multiplier applied to this component before the weighted components are
        combined. Defaults to 1.0.

    Examples
    --------
    >>> weighted = iws.costs.WeightedCost(iws.costs.Max(), 0.25)
    >>> cost = iws.costs.MultiCost(costs=[iws.costs.RMSE(), weighted])
    """

    # The wire format for a component is a bare {"cost", "weight"} record, so this
    # schema must not append the "type" discriminator BaseSchema adds by default.
    _emit_type = False

    cost: CostUnion = Field(..., description="The component cost function.")
    weight: float = Field(
        default=1.0,
        description=(
            "Multiplier applied to this component cost before the weighted "
            "components are combined. Defaults to 1.0."
        ),
    )

    def __init__(self, cost=None, weight: float = 1.0, **extra: Any):
        super().__init__(cost=cost, weight=weight, **extra)


MultiCost.model_rebuild()
WeightedCost.model_rebuild()
