"""Schemas for objective_functions."""

from typing import Any

from pydantic import Field

from .._types import NamedFloatMap, NumberLike
from ..base import BaseSchema

# Method name (``"mean"``, ``"identity"``, ``"range"``, …) or numeric value.
_NormalizationLike = str | NumberLike

# Shared descriptions for fields that appear on every ErrorFunction subclass.
_NORMALIZATION_DESCRIPTION = (
    "How to normalize the model and data for each variable in the cost. "
    "One of ``'mean'`` (mean of the data), ``'range'`` (range of the data), "
    "``'sum_squares'`` (sum of squares), ``'mean_squares'`` (mean sum of "
    "squares), ``'root_mean_squares'`` (root mean square), ``'identity'`` "
    "(use 1), or a float value."
)
_SCALE_DEPRECATED_DESCRIPTION = (
    "Deprecated alias for ``normalization``. Use ``normalization`` instead."
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


class ObjectiveFunction(BaseSchema):
    """Base class for all cost / objective functions.

    Concrete cost classes (``RMSE``, ``MAE``, ``Max``, ``ChiSquare``,
    ``GaussianLogLikelihood``, ``DesignFunction``, …) all inherit from
    this base, so anywhere the schema needs to type "a list of costs"
    (e.g. ``Validation.summary_stats``) the type is
    ``list[ObjectiveFunction]``.

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


class ErrorFunction(ObjectiveFunction):
    """Base for residual-based error measures (also known as distance functions).

    Adds ``normalization`` (and the deprecated ``scale`` alias) on top of
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
    scale : str or float, optional
        Deprecated alias for ``normalization``. Use ``normalization``
        instead.
    """

    normalization: _NormalizationLike | None = Field(
        default=None, description=_NORMALIZATION_DESCRIPTION
    )
    scale: _NormalizationLike | None = Field(
        default=None, description=_SCALE_DEPRECATED_DESCRIPTION
    )


class RMSE(ErrorFunction):
    """Root-mean-square-error cost function.

    Takes the square root of the MSE to provide a value in the same units as the original data.
    This is often used in scientific and engineering applications when the magnitude of error
    in the original units is important.

    This cost function only supports scalar output.

    Examples
    --------
    >>> cost = iws.costs.RMSE()
    >>> # slot into a DataFit's `cost` or a Validation's `summary_stats`
    >>> val = iws.Validation(
    ...     objectives={"cycle": iws.objectives.CurrentDriven(data_input="path/to/cycle.csv")},
    ...     summary_stats=[cost],
    ... )"""


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


class MSE(ErrorFunction):
    """Mean-square-error cost function.

    Similar to SSE, but normalizes by the number of data points.
    This makes the cost independent of the number of data points.

    For scalar output, it returns the sum of squared residuals divided by the number of points.
    For array output, it returns the SSE residuals divided by the square root of the number of points."""


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


class SSE(ErrorFunction):
    """Sum-of-squared-errors cost function.

    Calculates the sum of squared differences between model and data:
    SSE = Σ(model - data)²"""


class Wasserstein(ErrorFunction):
    """Wasserstein distance cost function.

    The Wasserstein distance is a measure of the distance between two probability distributions.
    It is defined as the minimum amount of work required to transform one distribution into the other."""


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
    (the number of degrees of freedom)."""

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
    """Cost function that is a combination of multiple costs

    Parameters
    ----------
    costs : dict of {cost: weight}
        Dict of costs and their weights.
    accumulator : function, optional
        The function to use to combine the costs. Default is sum.

    Notes
    -----
    All constituent costs must support the output mode (scalar or residuals) selected
    by the optimizer. The default accumulator (sum) combines the weighted costs by
    addition.
    """

    # Either the parser list-of-records form or the runtime
    # ``dict[ObjectiveFunction, float]`` mapping.
    costs: list[dict[str, Any]] | dict[Any, float] = Field(
        ...,
        description=(
            "Component costs and their weights. Either a list of "
            "``{'cost': <ObjectiveFunction>, 'weight': <float>}`` records "
            "or a ``dict`` mapping each cost instance to its weight. Each "
            "component cost is evaluated on the shared outputs, weighted, "
            "and combined via ``accumulator`` (default ``sum``)."
        ),
    )
    accumulator: Any | None = Field(  # noqa: ANN401 - callable, runtime-validated
        default=None,
        description=(
            "Callable used to combine the weighted component costs. Defaults "
            "to ``sum``. Only the default is currently supported for "
            "serialization."
        ),
    )


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
        (default: 1e10), "mean", or "min". The default fills NaN with a large
        penalty value to ensure solver failures produce high costs.

    Examples
    --------
    >>> cost = iws.costs.GaussianLogLikelihood(sigma={"Voltage [V]": 0.005})
    >>> fit = iws.DataFit(
    ...     objectives={"cycle": iws.objectives.CurrentDriven(data_input="path/to/cycle.csv")},
    ...     parameters={"x": iws.Parameter("x", initial_value=1.0, bounds=(0.0, 2.0))},
    ...     cost=cost,
    ... )
    """

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
        it is given a weight of 1."""
