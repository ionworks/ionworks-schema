"""Schemas for objective_functions."""

from typing import Any

from pydantic import Field

from ..base import BaseSchema


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

    variable_standard_deviations: Any = Field(...)
    nan_values: Any | None = Field(default=None)

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

    objective_weights: Any | None = Field(default=None)

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

    normalization: Any | None = Field(default=None)
    nan_values: Any | None = Field(default=None)
    objective_weights: Any | None = Field(default=None)
    variable_weights: Any | None = Field(default=None)
    scale: Any | None = Field(default=None)

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
    """
    Gaussian negative log-likelihood cost function.

    Computes the Gaussian NLL:

        NLL = 0.5 * Σ_vars [ N_i * log(2π * σ_i²) + Σ_j (y_ij - ŷ_ij)² / σ_i² ]

    This enables MLE with noise estimation, MAP estimation, and Bayesian
    posterior sampling (MCMC).

    Parameters
    ----------
    sigma : dict[str, float | str]
        Mapping of variable names to noise standard deviations (σ). Values
        can be:
        - A float: fixed known noise standard deviation
        - A string: name of a fitting parameter to be optimised (looked up
          from the current inputs at evaluation time via ``set_current_inputs``)
    nan_values : str or float, optional
        How to handle NaN values in model output. Options: a float constant
        (default: 1e10), "mean", or "min". The default fills NaN with a large
        penalty value to ensure solver failures produce high costs.
    """

    sigma: Any = Field(...)
    nan_values: Any | None = Field(default=None)

    def __init__(self, sigma, nan_values=None):
        super().__init__(sigma=sigma, nan_values=nan_values)


class MAE(BaseSchema):
    """Mean-absolute-error cost function.

    Instead of squaring residuals, this cost function uses the absolute values, which
    makes it less sensitive to outliers compared to squared-error metrics.

    For scalar output, it returns the sum of absolute residuals divided by the number of points.
    For array output, it returns the signed square root of the absolute residuals,
    normalized by the square root of the number of points."""

    normalization: Any | None = Field(default=None)
    nan_values: Any | None = Field(default=None)
    objective_weights: Any | None = Field(default=None)
    variable_weights: Any | None = Field(default=None)
    scale: Any | None = Field(default=None)

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

    normalization: Any | None = Field(default=None)
    nan_values: Any | None = Field(default=None)
    objective_weights: Any | None = Field(default=None)
    variable_weights: Any | None = Field(default=None)
    scale: Any | None = Field(default=None)

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

    normalization: Any | None = Field(default=None)
    nan_values: Any | None = Field(default=None)
    objective_weights: Any | None = Field(default=None)
    variable_weights: Any | None = Field(default=None)
    scale: Any | None = Field(default=None)

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

    costs: Any = Field(...)
    accumulator: Any | None = Field(default=None)
    normalization: Any | None = Field(default=None)
    nan_values: Any | None = Field(default=None)
    objective_weights: Any | None = Field(default=None)
    variable_weights: Any | None = Field(default=None)
    scale: Any | None = Field(default=None)

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

    objective_weights: Any = Field(...)
    variable_weights: Any = Field(...)

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

    normalization: Any | None = Field(default=None)
    nan_values: Any | None = Field(default=None)
    objective_weights: Any | None = Field(default=None)
    variable_weights: Any | None = Field(default=None)
    scale: Any | None = Field(default=None)

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

    normalization: Any | None = Field(default=None)
    nan_values: Any | None = Field(default=None)
    objective_weights: Any | None = Field(default=None)
    variable_weights: Any | None = Field(default=None)
    scale: Any | None = Field(default=None)

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
