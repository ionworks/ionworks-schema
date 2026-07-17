"""Schema for Validation pipeline element."""

from pydantic import Field

from .base import BaseSchema
from .objective_functions.objective_functions import CostUnion
from .objectives.objectives import ObjectiveUnion

# Each objective is validated by the discriminated ``ObjectiveUnion`` — dispatched
# on its ``type`` to the concrete leaf; unknown/base types and bogus keys reject.
# Summary stats are cost functions discriminated by ``type``; the trailing
# ``str`` arm mirrors the ``cost`` fields (bare-name shorthand parity).
_SummaryStatLike = CostUnion | str


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
    objectives : dict of name to objective or dict
        One entry per experiment you want to compare against. The key
        is a human-readable label (used in the report); the value is
        the objective describing what to simulate and what to compare.
    summary_stats : list[Cost | dict], optional
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

    objectives: dict[str, ObjectiveUnion] = Field(
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
        objectives: dict[str, ObjectiveUnion],
        summary_stats: list[_SummaryStatLike] | None = None,
    ):
        super().__init__(objectives=objectives, summary_stats=summary_stats)
