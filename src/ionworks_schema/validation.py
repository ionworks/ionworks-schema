"""Schema for Validation pipeline element."""

from typing import Any

from pydantic import Field

from .base import BaseSchema


class Validation(BaseSchema):
    """Schema for Validation - validate model performance against experimental data.

    Evaluates model accuracy by comparing predictions to data using specified
    objectives and computing summary statistics. Results include time-series
    comparisons and scalar metrics (RMSE, MAE, etc.).

    Parameters
    ----------
    objectives : dict or ObjectivesConfigSchema
        Objectives defining what to validate. Keys are objective names, values are
        objective instances or configs with data and model configuration.
    summary_stats : list, optional
        Error metrics to compute (e.g. RMSE, MAE, Max). For FittingObjective,
        defaults to [RMSE, MAE, Max] when parsed by the pipeline.
    """

    objectives: Any = Field(
        ...,
        description=(
            "Objectives defining what to validate. Keys are objective names, "
            "values are objective instances or configs with data and model "
            "configuration (``FittingObjective`` or ``DesignObjective``)."
        ),
    )
    summary_stats: list[Any] | None = Field(
        default=None,
        description=(
            "Scalar error metrics (cost/objective-function instances with "
            "scalar output, e.g. ``RMSE``, ``MAE``, ``Max``) computed from "
            "the validation results. Defaults to "
            "``[RMSE(normalization=1.0), MAE(normalization=1.0), "
            "Max(normalization=1.0)]`` for ``FittingObjective`` inputs when "
            "left unset, so metrics carry the same physical units as their "
            "labels."
        ),
    )

    def __init__(self, objectives: Any, summary_stats: list[Any] | None = None):
        super().__init__(objectives=objectives, summary_stats=summary_stats)
