"""Schemas for data_fit."""

from typing import Annotated, Any

from pydantic import Field, model_validator

from .._types import NumberLike
from ..base import BaseSchema
from ..distribution_samplers.distribution_samplers import DistributionSampler
from ..objective_functions.regularizers import Prior
from ..objectives.objectives import BaseObjective
from ..parameter_estimators.parameter_estimators import ParameterEstimator

# Left-to-right unions: dict / schema first for autodoc, ``Any`` last
# so runtime ``ionworkspipeline`` objects pass through on the
# ``from_schema`` path.
_ObjectiveValue = Annotated[
    dict[str, Any] | BaseObjective | Any,
    Field(union_mode="left_to_right"),
]
_CostLike = Annotated[
    dict[str, Any] | BaseSchema | str | Any,
    Field(union_mode="left_to_right"),
]
_OptimizerLike = Annotated[
    dict[str, Any] | ParameterEstimator | BaseSchema | Any,
    Field(union_mode="left_to_right"),
]
_PriorLike = Annotated[
    dict[str, Any] | Prior | Any,
    Field(union_mode="left_to_right"),
]
_SamplerLike = Annotated[
    dict[str, Any] | DistributionSampler | Any,
    Field(union_mode="left_to_right"),
]
# ``cost_logger`` accepts a runtime ``iwp.CostLogger`` on the parser
# path; the schema package doesn't model ``CostLogger`` itself.
_CostLoggerLike = Annotated[
    dict[str, Any] | BaseSchema | Any,
    Field(union_mode="left_to_right"),
]
_InitialGuesses = dict[str, NumberLike] | list[dict[str, NumberLike]]


class DataFit(BaseSchema):
    """Fit a model's parameters to measured experimental data.

    A ``DataFit`` step says: "run these experiments through the
    model, compare the result to the measurements I supply, and
    adjust these parameters until the agreement is as good as
    possible". One or more ``objectives`` describe what experiments
    to compare against and which measured curves to match. The
    ``parameters`` dict lists which parameters are free to move
    during the fit, and the optional ``priors`` express what you
    already believe about their plausible values.

    The remaining fields (``cost``, ``optimizer``,
    ``initial_guesses``, ``multistarts``, …) tune *how* the fit runs.
    The defaults are sensible — you only need to set them if you want
    finer control over the optimisation algorithm, parallelism, or
    runtime budget.

    Parameters
    ----------
    objectives : FittingObjective or DesignObjective or dict[str, FittingObjective | DesignObjective | dict]
        What to fit against. Either a single objective (a
        ``CurrentDriven``, ``MSMRHalfCell``, … from
        ``iws.objectives``) or a dict of named objectives if the fit
        spans multiple experiments.
    source : str, optional
        Free-text label for the data source (paper, dataset name,
        instrument). Shown in reports and provenance records.
    parameters : dict[str, Parameter | pybamm.Symbol | callable] | None, optional
        Which parameters are being fitted, and (optionally) how they
        relate to each other through pybamm expressions. At least one
        of ``parameters`` or ``priors`` must be set. Each value can be:

        - an ``iwp.Parameter`` object, e.g. ``iwp.Parameter("x")``
        - a pybamm expression, in which case other referenced
          parameters must also be supplied as ``iwp.Parameter`` objects
          via ``pybamm.Parameter`` wrapping. For example::

              {
                  "param": 2 * pybamm.Parameter("half-param"),
                  "half-param": iwp.Parameter("half-param"),
              }

          works, but ``{"param": 2 * iwp.Parameter("half-param")}``
          does not.
        - a function that constructs a pybamm expression referencing
          other parameters, which must again be explicitly supplied
          as ``iwp.Parameter`` objects::

              {
                  "main parameter": lambda x: (
                      pybamm.Parameter("other parameter") * x**2
                  ),
                  "other parameter": iwp.Parameter("other parameter"),
              }

        The dict key does not need to match the underlying pybamm
        parameter name — ``DataFit`` figures out which variable to fit
        from the ``iwp.Parameter`` reference.
    cost : ObjectiveFunction or str or dict or None, optional
        How disagreement between model and data is summed up into a
        single number (e.g. sum-of-squares, log-likelihood). Leave
        unset for a sensible default.
    initial_guesses : dict[str, float] or list[dict[str, float]] or None, optional
        Starting point(s) for the optimiser. One dict applies to
        every restart; a list of dicts provides one starting point
        per restart.
    optimizer : ParameterEstimator or dict or None, optional
        Which optimisation algorithm to use (e.g. ``CMAES``, ``PSO``,
        ``ScipyMinimize``). Leave unset for the default.
    cost_logger : BaseSchema or dict or None, optional
        Optional logger that records the cost trajectory and
        parameter values across the fit, for later inspection.
    multistarts : int | None, optional
        Number of independent restarts from different initial
        guesses. More restarts is more robust but takes longer.
    num_workers : int | None, optional
        Worker processes for running restarts in parallel.
        ``None`` uses all CPU cores; ``1`` disables parallelism.
        Not supported on Windows.
    parallel : bool | None, optional
        Whether to also parallelise *within* a single restart (for
        population-based optimisers). Auto-detected when ``None``.
    max_batch_size : int | None, optional
        Cap on how many restarts run together in one batch. Leave
        unset for an auto-chosen value.
    initial_guess_sampler : DistributionSampler or dict or None, optional
        How to spread the multistart guesses across the parameter
        space (``LatinHypercube`` by default).
    priors : Prior or list[Prior] or dict or None, optional
        What you already believe about the parameter values. Acts as
        a regulariser on the fit. May be supplied alone (the prior
        names become the fit parameters) or alongside ``parameters``
        (priors regularise the listed fit parameters).
    options : dict[str, Any] | None, optional
        Advanced dict of runtime options: ``seed`` for
        reproducibility, ``maxiters``/``maxtime`` for budgets, and
        ``low_memory`` to trim the log. Defaults are:

        .. code-block:: python

            options = {
                # Random seed for reproducibility. Defaults to a seed
                # generated from the current time.
                "seed": iwutil.random.generate_seed(),
                # Reduce log size: only append entries if the cost
                # improves the best-so-far by at least 0.1%. Defaults
                # to True for deterministic optimizers.
                "low_memory": True,
                # Maximum iterations per optimization job.
                "maxiters": None,
                # Maximum wall time (seconds) per job. With multistarts
                # the total may exceed this since many jobs run.
                "maxtime": None,
            }

        Note: ``maxiters`` and ``maxtime`` only take effect when
        ``model.convert_to_format == 'casadi'``.

    Examples
    --------
    >>> # build the schema with the fields you care about
    >>> obj = iws.objectives.OCPHalfCell(
    ...     electrode="positive",
    ...     data_input="path/to/ocp.csv",
    ... )
    >>> fit = iws.DataFit(
    ...     objectives={"ocp": obj},
    ...     parameters={"Q_pe": iws.Parameter(
    ...         "Positive electrode capacity [A.h]", initial_value=3.0, bounds=(2.0, 4.0),
    ...     )},
    ...     priors={"Q_pe": iws.priors.Prior("Q_pe", iws.stats.Normal(3.0, 0.2))},
    ... )
    >>> config = iws.Pipeline({"ocp fit": fit}).to_config()
    >>> # then submit `config` via ionworks-api
    """

    _exclude_fields = {"source"}

    # Outer union is left-to-right because ``_ObjectiveValue`` ends in ``Any``.
    objectives: Annotated[
        dict[str, _ObjectiveValue] | _ObjectiveValue,
        Field(union_mode="left_to_right"),
    ] = Field(
        ...,
        description=(
            "Objective or mapping of name to objective that defines what is "
            "being fitted. A single objective is auto-wrapped into "
            "``{name: objective}`` by the validator; ``ArrayDataFit`` "
            "requires an explicit dict keyed by independent-variable value."
        ),
    )
    source: str = Field(
        default="",
        description=(
            "Free-text label describing the source of the data (e.g. "
            "dataset name or file path). Excluded from the serialized "
            "config — the parser recovers it from the pipeline element "
            "dict key."
        ),
    )
    # Values are ``iwp.Parameter`` instances, pybamm expressions, or
    # callables — heterogeneous and runtime-validated.
    parameters: dict[str, Any] | None = Field(
        default=None,
        description=(
            "Mapping of parameter name to the quantity being fitted. Values "
            "may be ``iwp.Parameter`` instances, ``pybamm`` expressions "
            "referencing other ``iwp.Parameter`` entries, or Python "
            "callables returning pybamm expressions. At least one of "
            "``parameters`` or ``priors`` must be set; both may be supplied "
            "together (priors then act as regularizers on the fit "
            "parameters)."
        ),
    )
    cost: _CostLike | None = Field(
        default=None,
        description=(
            "Cost/objective-function used when constructing the optimization "
            "objective (e.g. ``SSE``, ``MSE``, ``GaussianLogLikelihood``). "
            "If None, the optimizer's default cost function is used."
        ),
    )
    initial_guesses: _InitialGuesses | None = Field(
        default=None,
        description=(
            "Initial guess(es) for the parameters. A single ``{name: value}`` "
            "dict is used as the guess for every optimization job in each "
            "batch; a list of dicts provides one guess per job."
        ),
    )
    optimizer: _OptimizerLike | None = Field(
        default=None,
        description=(
            "Optimizer or sampler instance used to run the fit. Defaults to "
            "the ``DataFit`` subclass's default (typically ``ScipyMinimize`` "
            "for deterministic fits)."
        ),
    )
    cost_logger: _CostLoggerLike | None = Field(
        default=None,
        description=(
            "Cost logger used to record the cost and parameter trajectory "
            "during the fit. Defaults to ``iwp.CostLogger`` with default "
            "options."
        ),
    )
    multistarts: int | None = Field(
        default=None,
        description=(
            "Number of times to restart the optimization from different "
            "initial guesses. If None, the optimization runs once from the "
            "provided ``initial_guesses``."
        ),
    )
    num_workers: int | None = Field(
        default=None,
        description=(
            "Number of worker processes for batch-level parallelism across "
            "multistarts or multiple initial guesses. ``1`` disables "
            "batch-level parallelism; ``None`` uses all available CPU cores. "
            "Not supported on Windows."
        ),
    )
    parallel: bool | None = Field(
        default=None,
        description=(
            "Controls optimizer-level parallelism (parallel evaluation of "
            "the objective within a single optimization job). True enables "
            "it for compatible optimizers (e.g. AskTellOptimizer "
            "population-based methods); False disables it. If None, it is "
            "auto-enabled when a single job runs with ``num_workers > 1``."
        ),
    )
    max_batch_size: int | None = Field(
        default=None,
        description=(
            "Maximum number of optimization jobs per batch. If None, uses "
            "the largest batch that evenly divides the jobs across workers."
        ),
    )
    initial_guess_sampler: _SamplerLike | None = Field(
        default=None,
        description=(
            "Sampler used to generate initial guesses for multistarted "
            "fits. Defaults to ``LatinHypercube``; ``Uniform`` is also "
            "supported."
        ),
    )
    priors: _PriorLike | list[_PriorLike] | None = Field(
        default=None,
        description=(
            "Prior or list of priors used as regularizers for the fit. When "
            "``priors`` is set without ``parameters``, the parameters being "
            "fitted are inferred from the prior names. When set alongside "
            "``parameters``, the priors act as regularizers on the listed "
            "fit parameters."
        ),
    )
    options: dict[str, Any] | None = Field(
        default=None,
        description=(
            "Optional dict of runtime options: ``seed`` (random seed), "
            "``low_memory`` (drop log entries that don't improve the best "
            "cost by >=0.1%), ``maxiters``, and ``maxtime`` (per-job "
            "budget in seconds)."
        ),
    )

    def __init__(
        self,
        objectives,
        source="",
        parameters=None,
        cost=None,
        initial_guesses=None,
        optimizer=None,
        cost_logger=None,
        multistarts=None,
        num_workers=None,
        parallel=None,
        max_batch_size=None,
        initial_guess_sampler=None,
        priors=None,
        options=None,
    ):
        super().__init__(
            objectives=objectives,
            source=source,
            parameters=parameters,
            cost=cost,
            initial_guesses=initial_guesses,
            optimizer=optimizer,
            cost_logger=cost_logger,
            multistarts=multistarts,
            num_workers=num_workers,
            parallel=parallel,
            max_batch_size=max_batch_size,
            initial_guess_sampler=initial_guess_sampler,
            priors=priors,
            options=options,
        )

    @model_validator(mode="after")
    def wrap_bare_objective(self):
        """Wrap a bare objective in a dict, matching ionworkspipeline behavior.

        Only applies to DataFit, not ArrayDataFit (which requires a dict keyed
        by independent variable values).
        """
        if type(self) is not DataFit:
            return self
        if not isinstance(self.objectives, dict):
            if self.objectives is None:
                raise ValueError("'objectives' must not be None")
            name = self.objectives.__class__.__name__
            self.objectives = {name: self.objectives}
        return self

    @model_validator(mode="after")
    def validate_parameters_or_priors(self):
        """At least one of ``parameters`` or ``priors`` must be supplied.

        The runtime accepts both together — priors then act as regularizers
        on the listed fit parameters — so we mirror the runtime here rather
        than enforce a stricter mutual exclusion at the schema boundary.
        """
        if not self.parameters and not self.priors:
            raise ValueError("Either 'parameters' or 'priors' must be specified")
        return self


class ArrayDataFit(DataFit):
    """Fit the same model separately at each value of an independent variable.

    Use this when you have one experiment repeated at different
    conditions — typically temperatures, C-rates, or pulse indices —
    and you want one fitted parameter set per condition rather than
    one global fit. ``objectives`` is keyed by the independent
    variable value (``{298.15: ..., 313.15: ...}``); each entry is
    fitted independently and the results can be post-processed to
    extract how parameters depend on the variable.

    All other fields behave the same as ``DataFit``.
    """

    # Bare objectives are kept as-is (not auto-wrapped); the dict key
    # type is ``Any`` so independent-variable values (floats, ints) work.
    objectives: Annotated[
        dict[Any, _ObjectiveValue] | _ObjectiveValue,
        Field(union_mode="left_to_right"),
    ] = Field(
        ...,
        description=(
            "Mapping of independent-variable value to objective. Each "
            "entry is fitted separately. Unlike ``DataFit``, a bare "
            "objective is not auto-wrapped — the keys must be the values of "
            "the independent variable (e.g. temperatures or pulse indices)."
        ),
    )

    pass
