"""Post-fit analysis elements (confidence intervals, sensitivity).

Mirror the runtime ``ionworkspipeline.analysis`` recipes: both are DataFit-shaped
elements evaluated at a fitted point. They always run a ``PointEstimate``
optimizer, so any other optimizer is rejected.
"""

from __future__ import annotations

from pydantic import Field, model_validator

from .data_fit.data_fit import DataFit
from .parameter_estimators.parameter_estimators import PointEstimateOptimizer


class _AnalysisElement(DataFit):
    """Shared contract for the post-fit analysis elements."""

    @model_validator(mode="after")
    def _only_point_estimate(self):
        # The runtime recipe always emits a PointEstimate in its own config, so
        # rejecting every optimizer would break that config's round-trip.
        if self.optimizer is not None and not isinstance(
            self.optimizer, PointEstimateOptimizer
        ):
            raise ValueError(
                f"{type(self).__name__} evaluates at an already-fitted point and "
                "always uses a PointEstimate optimizer; do not pass 'optimizer'."
            )
        return self


class LinearConfidenceInterval(_AnalysisElement):
    """Linearized confidence intervals at the fitted point.

    Mirrors ``ionworkspipeline.analysis.LinearConfidenceInterval``.
    """

    confidence_level: float = Field(
        0.95, description="Central probability mass for each interval."
    )
    gauss_newton: bool = Field(
        True, description="Use the Gauss-Newton Hessian approximation."
    )
    use_parameter_bounds: bool = Field(
        True, description="Clip intervals to the parameter bounds."
    )
    variable_standard_deviations: dict | None = Field(
        None, description="Per-variable measurement noise std devs."
    )


class SobolSensitivity(_AnalysisElement):
    """Sobol sensitivity indices at the fitted point.

    Mirrors ``ionworkspipeline.analysis.SobolSensitivity``.
    """

    n_samples: int = Field(256, description="Base sample count for the Sobol design.")
    calc_second_order: bool = Field(
        False, description="Also compute second-order indices."
    )
    use_log_transform: bool = Field(
        False, description="Sample parameters in log space."
    )


__all__ = ["LinearConfidenceInterval", "SobolSensitivity"]
