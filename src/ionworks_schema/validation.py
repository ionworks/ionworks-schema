"""Schema for Validation pipeline element."""

from typing import Annotated, Any

from pydantic import Field

from .base import BaseSchema
from .objective_functions.objective_functions import ObjectiveFunction
from .objectives.objectives import DesignObjective, FittingObjective

# ``dict`` first so raw configs validate as-is; trailing ``Any``
# accepts runtime objects on the from_schema path.
_ObjectiveLike = Annotated[
    dict[str, Any] | FittingObjective | DesignObjective | Any,
    Field(union_mode="left_to_right"),
]
# Cost classes (``RMSE``, ``MAE``, ``Max``, …) all inherit from
# ``ObjectiveFunction``; trailing ``Any`` accepts runtime cost objects
# on the from_schema path.
_SummaryStatLike = Annotated[
    dict[str, Any] | ObjectiveFunction | Any,
    Field(union_mode="left_to_right"),
]


class Validation(BaseSchema):
    """Check a fitted model against held-out experimental data.

    A ``Validation`` step takes the parameters produced earlier in the
    pipeline, simulates the experiments listed in ``objectives``, and
    compares those simulations to the measured data. The result tells
    you how well the model generalises beyond the data you fit on.

    Each ``objective`` describes one comparison (e.g. "current vs.
    time for this discharge"). The ``summary_stats`` list controls
    which scalar error metrics — RMSE, MAE, max error, … — get
    reported alongside the full time-series comparison.

    Parameters
    ----------
    objectives : dict[str, FittingObjective | DesignObjective | dict]
        One entry per experiment you want to compare against. The key
        is a human-readable label (used in the report); the value is
        the objective describing what to simulate and what to compare.
    summary_stats : list[ObjectiveFunction | dict], optional
        Which scalar error metrics to report (e.g. ``RMSE()``,
        ``MAE()``, ``Max()``). If you leave this unset, sensible
        defaults are filled in for fitting-style objectives so the
        report carries the same physical units as the measurements.

    Examples
    --------
    >>> obj1 = iws.objectives.CurrentDriven(data_input="path/to/cycle_1C.csv")
    >>> obj2 = iws.objectives.CurrentDriven(data_input="path/to/cycle_C2.csv")
    >>> val = iws.Validation(
    ...     objectives={"1C": obj1, "C/2": obj2},
    ...     summary_stats=[iws.costs.RMSE(), iws.costs.MAE()],
    ... )
    >>> config = iws.Pipeline({"validate": val}).to_config()
    >>> # then submit `config` via ionworks-api
    """

    objectives: dict[str, _ObjectiveLike] = Field(
        ...,
        description=(
            "One entry per experiment you want to validate against. "
            "The key is the label that appears in the validation "
            "report; the value is an ``iws.objectives.*`` instance "
            "(e.g. ``CurrentDriven``, ``MSMRHalfCell``) describing "
            "what to simulate and which measured curve to compare to."
        ),
    )
    summary_stats: list[_SummaryStatLike] | None = Field(
        default=None,
        description=(
            "Scalar error metrics (e.g. ``RMSE()``, ``MAE()``, "
            "``Max()``) to report alongside the time-series comparison. "
            "Leave unset to get sensible defaults for fitting "
            "objectives — the metrics will then carry the same physical "
            "units as the underlying measurements."
        ),
    )

    def __init__(
        self,
        objectives: dict[str, _ObjectiveLike],
        summary_stats: list[_SummaryStatLike] | None = None,
    ):
        super().__init__(objectives=objectives, summary_stats=summary_stats)
