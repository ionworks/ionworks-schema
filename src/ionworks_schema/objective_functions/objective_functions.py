"""Schemas for objective_functions."""

from typing import Any

from pydantic import Field

from ..base import BaseSchema

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


class ChiSquare(BaseSchema):
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

    variable_standard_deviations: Any = Field(
        ...,
        description=(
            "Mapping from variable name to its standard deviation ``sigma``. "
            "Each residual is normalized by ``sigma`` before squaring, so a "
            "well-fitting model yields a chi-square value close to the "
            "number of data points."
        ),
    )
    nan_values: Any | None = Field(
        default=None,
        description=_NAN_VALUES_DESCRIPTION,
    )

    def __init__(self, variable_standard_deviations, nan_values=None):
        super().__init__(
            variable_standard_deviations=variable_standard_deviations,
            nan_values=nan_values,
        )


class DesignFunction(BaseSchema):
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

    objective_weights: Any | None = Field(
        default=None,
        description=_OBJECTIVE_WEIGHTS_DESCRIPTION,
    )

    def __init__(self, objective_weights=None):
        super().__init__(objective_weights=objective_weights)


class ErrorFunction(BaseSchema):
    """A base class for error measures (also known as distance functions)

    Parameters
    ----------
    normalization : string or float, optional
        How to normalize the model and data, for each variable in the cost function.
        The options are
        - "mean" (default): uses the mean of the data.
        - "identity": uses 1 (no normalization).
        - "range": uses the range of the data.
        - "sum_squares": uses the sum of squares of the data.
        - "mean_squares": uses the mean of the sum of squares of the data.
        - "root_mean_squares": uses the root mean square of the data.
        - float: uses the value of the float.
    nan_values : string or float, optional
        How to deal with any NaN values in the model output.
        If "mean", uses the mean of the non-NaN model output values.
        If "min", uses the min of the non-NaN model output values.
        If a float, uses the float value.
    objective_weights : dict, optional
        Dictionary of {name: weight} pairs for each objective in the cost function. If
        None, all objectives are weighted equally. If a name is not in the dictionary,
        it is given a weight of 1.
    variable_weights : dict, optional
        Dictionary of {name: weight} pairs for each variable in the cost function. If
        None, all variables are weighted equally. If a name is not in the dictionary, it
        is given a weight of 1.
    scale : string or float, optional
        Deprecated. Use ``normalization`` instead."""

    normalization: Any | None = Field(
        default=None, description=_NORMALIZATION_DESCRIPTION
    )
    nan_values: Any | None = Field(default=None, description=_NAN_VALUES_DESCRIPTION)
    objective_weights: Any | None = Field(
        default=None, description=_OBJECTIVE_WEIGHTS_DESCRIPTION
    )
    variable_weights: Any | None = Field(
        default=None, description=_VARIABLE_WEIGHTS_DESCRIPTION
    )
    scale: Any | None = Field(default=None, description=_SCALE_DEPRECATED_DESCRIPTION)

    def __init__(
        self,
        normalization=None,
        nan_values=None,
        objective_weights=None,
        variable_weights=None,
        scale=None,
    ):
        super().__init__(
            normalization=normalization,
            nan_values=nan_values,
            objective_weights=objective_weights,
            variable_weights=variable_weights,
            scale=scale,
        )


class GaussianLogLikelihood(BaseSchema):
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
    """

    sigma: Any = Field(
        ...,
        description=(
            "Mapping from variable name to the noise standard deviation "
            "``sigma``. Each value may be a float (fixed known noise) or a "
            "string naming a fitting parameter to be optimized jointly with "
            "the model parameters."
        ),
    )
    nan_values: Any | None = Field(
        default=None,
        description=_NAN_VALUES_DESCRIPTION,
    )

    def __init__(self, sigma, nan_values=None):
        super().__init__(sigma=sigma, nan_values=nan_values)


class MAE(BaseSchema):
    """Mean-absolute-error cost function.

    Instead of squaring residuals, this cost function uses the absolute values, which
    makes it less sensitive to outliers compared to squared-error metrics.

    For scalar output, it returns the sum of absolute residuals divided by the number of points.
    For array output, it returns the signed square root of the absolute residuals,
    normalized by the square root of the number of points."""

    normalization: Any | None = Field(
        default=None, description=_NORMALIZATION_DESCRIPTION
    )
    nan_values: Any | None = Field(default=None, description=_NAN_VALUES_DESCRIPTION)
    objective_weights: Any | None = Field(
        default=None, description=_OBJECTIVE_WEIGHTS_DESCRIPTION
    )
    variable_weights: Any | None = Field(
        default=None, description=_VARIABLE_WEIGHTS_DESCRIPTION
    )
    scale: Any | None = Field(default=None, description=_SCALE_DEPRECATED_DESCRIPTION)

    def __init__(
        self,
        normalization=None,
        nan_values=None,
        objective_weights=None,
        variable_weights=None,
        scale=None,
    ):
        super().__init__(
            normalization=normalization,
            nan_values=nan_values,
            objective_weights=objective_weights,
            variable_weights=variable_weights,
            scale=scale,
        )


class MSE(BaseSchema):
    """Mean-square-error cost function.

    Similar to SSE, but normalizes by the number of data points.
    This makes the cost independent of the number of data points.

    For scalar output, it returns the sum of squared residuals divided by the number of points.
    For array output, it returns the SSE residuals divided by the square root of the number of points."""

    normalization: Any | None = Field(
        default=None, description=_NORMALIZATION_DESCRIPTION
    )
    nan_values: Any | None = Field(default=None, description=_NAN_VALUES_DESCRIPTION)
    objective_weights: Any | None = Field(
        default=None, description=_OBJECTIVE_WEIGHTS_DESCRIPTION
    )
    variable_weights: Any | None = Field(
        default=None, description=_VARIABLE_WEIGHTS_DESCRIPTION
    )
    scale: Any | None = Field(default=None, description=_SCALE_DEPRECATED_DESCRIPTION)

    def __init__(
        self,
        normalization=None,
        nan_values=None,
        objective_weights=None,
        variable_weights=None,
        scale=None,
    ):
        super().__init__(
            normalization=normalization,
            nan_values=nan_values,
            objective_weights=objective_weights,
            variable_weights=variable_weights,
            scale=scale,
        )


class Max(BaseSchema):
    """Cost function that reports the maximum error between the model and the data.

    For scalar output, it returns the maximum absolute value of any residual.
    For array output, it returns a single-element array containing the square root
    of the maximum error.

    Useful when you want to minimize the worst-case error rather than an average."""

    normalization: Any | None = Field(
        default=None, description=_NORMALIZATION_DESCRIPTION
    )
    nan_values: Any | None = Field(default=None, description=_NAN_VALUES_DESCRIPTION)
    objective_weights: Any | None = Field(
        default=None, description=_OBJECTIVE_WEIGHTS_DESCRIPTION
    )
    variable_weights: Any | None = Field(
        default=None, description=_VARIABLE_WEIGHTS_DESCRIPTION
    )
    scale: Any | None = Field(default=None, description=_SCALE_DEPRECATED_DESCRIPTION)

    def __init__(
        self,
        normalization=None,
        nan_values=None,
        objective_weights=None,
        variable_weights=None,
        scale=None,
    ):
        super().__init__(
            normalization=normalization,
            nan_values=nan_values,
            objective_weights=objective_weights,
            variable_weights=variable_weights,
            scale=scale,
        )


class MultiCost(BaseSchema):
    """Cost function that is a combination of multiple costs

    Parameters
    ----------
    costs : dict of {cost: weight}
        Dict of costs and their weights.
    accumulator : function, optional
        The function to use to combine the costs. Default is sum.

    Examples
    --------
    Create a combined cost that uses both MSE and MAE with different weights:

    >>> mse_cost = MSE()
    >>> mae_cost = MAE()
    >>> combined_cost = MultiCost({mse_cost: 2.0, mae_cost: 0.5})

    Notes
    -----
    All constituent costs must support the output mode (scalar or residuals) selected
    by the optimizer. The default accumulator (sum) combines the weighted costs by
    addition.
    scale : string or float, optional
        Deprecated. Use ``normalization`` instead."""

    costs: Any = Field(
        ...,
        description=(
            "Mapping from cost/objective-function instance to its weight. "
            "Each component cost is evaluated on the shared outputs, "
            "weighted, and combined via ``accumulator`` (default ``sum``)."
        ),
    )
    accumulator: Any | None = Field(
        default=None,
        description=(
            "Callable used to combine the weighted component costs. Defaults "
            "to ``sum``. Only the default is currently supported for "
            "serialization."
        ),
    )
    normalization: Any | None = Field(
        default=None, description=_NORMALIZATION_DESCRIPTION
    )
    nan_values: Any | None = Field(default=None, description=_NAN_VALUES_DESCRIPTION)
    objective_weights: Any | None = Field(
        default=None, description=_OBJECTIVE_WEIGHTS_DESCRIPTION
    )
    variable_weights: Any | None = Field(
        default=None, description=_VARIABLE_WEIGHTS_DESCRIPTION
    )
    scale: Any | None = Field(default=None, description=_SCALE_DEPRECATED_DESCRIPTION)

    def __init__(
        self,
        costs,
        accumulator=None,
        normalization=None,
        nan_values=None,
        objective_weights=None,
        variable_weights=None,
        scale=None,
    ):
        super().__init__(
            costs=costs,
            accumulator=accumulator,
            normalization=normalization,
            nan_values=nan_values,
            objective_weights=objective_weights,
            variable_weights=variable_weights,
            scale=scale,
        )


class ObjectiveFunction(BaseSchema):
    """A base cost class."""

    objective_weights: Any = Field(
        ...,
        description=_OBJECTIVE_WEIGHTS_DESCRIPTION,
    )
    variable_weights: Any = Field(
        ...,
        description=_VARIABLE_WEIGHTS_DESCRIPTION,
    )

    def __init__(self, objective_weights, variable_weights):
        super().__init__(
            objective_weights=objective_weights, variable_weights=variable_weights
        )


class RMSE(BaseSchema):
    """Root-mean-square-error cost function.

    Takes the square root of the MSE to provide a value in the same units as the original data.
    This is often used in scientific and engineering applications when the magnitude of error
    in the original units is important.

    This cost function only supports scalar output."""

    normalization: Any | None = Field(
        default=None, description=_NORMALIZATION_DESCRIPTION
    )
    nan_values: Any | None = Field(default=None, description=_NAN_VALUES_DESCRIPTION)
    objective_weights: Any | None = Field(
        default=None, description=_OBJECTIVE_WEIGHTS_DESCRIPTION
    )
    variable_weights: Any | None = Field(
        default=None, description=_VARIABLE_WEIGHTS_DESCRIPTION
    )
    scale: Any | None = Field(default=None, description=_SCALE_DEPRECATED_DESCRIPTION)

    def __init__(
        self,
        normalization=None,
        nan_values=None,
        objective_weights=None,
        variable_weights=None,
        scale=None,
    ):
        super().__init__(
            normalization=normalization,
            nan_values=nan_values,
            objective_weights=objective_weights,
            variable_weights=variable_weights,
            scale=scale,
        )


class SSE(BaseSchema):
    """Sum-of-squared-errors cost function.

    Calculates the sum of squared differences between model and data:
    SSE = Σ(model - data)²"""

    normalization: Any | None = Field(
        default=None, description=_NORMALIZATION_DESCRIPTION
    )
    nan_values: Any | None = Field(default=None, description=_NAN_VALUES_DESCRIPTION)
    objective_weights: Any | None = Field(
        default=None, description=_OBJECTIVE_WEIGHTS_DESCRIPTION
    )
    variable_weights: Any | None = Field(
        default=None, description=_VARIABLE_WEIGHTS_DESCRIPTION
    )
    scale: Any | None = Field(default=None, description=_SCALE_DEPRECATED_DESCRIPTION)

    def __init__(
        self,
        normalization=None,
        nan_values=None,
        objective_weights=None,
        variable_weights=None,
        scale=None,
    ):
        super().__init__(
            normalization=normalization,
            nan_values=nan_values,
            objective_weights=objective_weights,
            variable_weights=variable_weights,
            scale=scale,
        )
