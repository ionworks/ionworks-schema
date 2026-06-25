"""Schemas for parameter_estimators."""

from typing import Annotated, Literal

from pydantic import ConfigDict, Field, model_validator

from ..base import BaseSchema


class _AlgorithmOptions(BaseSchema):
    """Base class for AskTellOptimizer algorithm_options wrappers.

    Serializes to a plain option dict without the ``type`` discriminator
    (via ``_emit_type = False``), so the output matches what the pipeline
    algorithm classes expect from their ``options`` kwarg.
    """

    _emit_type: bool = False


class _PassthroughOptimizer(BaseSchema):
    """Base for optimizer wrappers that forward kwargs to an underlying
    library (scipy.optimize, pycma, pints, …).

    Uses ``extra="allow"`` because we don't enumerate every accepted kwarg —
    the underlying library is the source of truth for the option surface
    and is responsible for rejecting unknown keys at runtime. Drift on the
    typed fields (where they exist) is still caught by ``extra="forbid"``
    on the rest of the schema package.
    """

    model_config = ConfigDict(extra="allow")


#: Single source of truth for the native ask/tell stopping-criteria defaults.
#: The schema exposes these as the ``_AskTellBase`` field defaults (so users
#: see them) and ``ionworkspipeline`` imports this mapping for its runtime
#: optimizer defaults, so the two never drift. A ``None`` value means the
#: optimizer computes the default adaptively at run time.
ASK_TELL_DEFAULTS: dict[str, object] = {
    "log_to_screen": False,
    "sigma0": None,
    "max_iterations": None,
    "max_unchanged_iterations": None,
    "max_unchanged_iterations_threshold": None,
    "min_iterations": 1,
    "max_evaluations": 1_000_000,
    "population_size": None,
    "threshold": None,
    "absolute_tolerance": 1e-5,
    "relative_tolerance": 1e-2,
    "xtol": 1e-6,
    "population_convergence_tol": 5e-3,
    "flat_fitness_tol": None,
    "convergence_patience": 3,
    "surrogate_convergence_tol": 1e-3,
}


class _AskTellBase(BaseSchema):
    """Common stopping-criteria fields for native ask/tell optimizers.

    Strict (``extra="forbid"`` via ``BaseSchema``). The convenience optimizer
    classes (``CMAES``, ``DifferentialEvolution``, …) and the generic
    ``AskTellOptimizer`` (the ``method=`` form) all inherit these 16 fields and
    add only their ``type`` discriminator and method-specific options. Field
    defaults come from :data:`ASK_TELL_DEFAULTS` (shared with the runtime).
    """

    log_to_screen: bool | None = Field(
        default=ASK_TELL_DEFAULTS["log_to_screen"],
        description="If ``True``, print optimisation progress to stdout each generation.",
    )
    sigma0: float | int | list | tuple | None = Field(
        default=ASK_TELL_DEFAULTS["sigma0"],
        description=(
            "Initial step size for population-based methods. Scalar or "
            "per-dimension list/tuple."
        ),
    )
    max_iterations: int | None = Field(
        default=ASK_TELL_DEFAULTS["max_iterations"],
        description="Maximum number of generations/iterations (``None`` = adaptive).",
    )
    max_unchanged_iterations: int | None = Field(
        default=ASK_TELL_DEFAULTS["max_unchanged_iterations"],
        description=(
            "Stop after this many consecutive generations without objective "
            "improvement beyond ``absolute_tolerance`` / ``relative_tolerance``."
        ),
    )
    max_unchanged_iterations_threshold: float | int | None = Field(
        default=ASK_TELL_DEFAULTS["max_unchanged_iterations_threshold"],
        description=(
            "Legacy alias for ``absolute_tolerance``. Prefer "
            "``absolute_tolerance`` on new code."
        ),
    )
    min_iterations: int | None = Field(
        default=ASK_TELL_DEFAULTS["min_iterations"],
        description=(
            "Minimum number of iterations before any stopping criterion is evaluated."
        ),
    )
    max_evaluations: int | None = Field(
        default=ASK_TELL_DEFAULTS["max_evaluations"],
        description="Hard cap on total objective evaluations across all generations.",
    )
    population_size: int | None = Field(
        default=ASK_TELL_DEFAULTS["population_size"],
        description="Population size for population-based methods.",
    )
    threshold: float | int | None = Field(
        default=ASK_TELL_DEFAULTS["threshold"],
        description=(
            "Target objective value — stop as soon as any evaluated point "
            "reaches this threshold."
        ),
    )
    absolute_tolerance: float | int | None = Field(
        default=ASK_TELL_DEFAULTS["absolute_tolerance"],
        description="Absolute improvement tolerance used with ``max_unchanged_iterations``.",
    )
    relative_tolerance: float | int | None = Field(
        default=ASK_TELL_DEFAULTS["relative_tolerance"],
        description="Relative improvement tolerance used with ``max_unchanged_iterations``.",
    )
    xtol: float | int | None = Field(
        default=ASK_TELL_DEFAULTS["xtol"],
        description=(
            "Parameter-change tolerance. Stops when the L-infinity norm of "
            "the change in the current best guess between generations drops "
            "below this value."
        ),
    )
    population_convergence_tol: float | int | None = Field(
        default=ASK_TELL_DEFAULTS["population_convergence_tol"],
        description=(
            "Population-convergence tolerance. Exact semantics depend on the "
            "algorithm (e.g. DE also checks position-space diversity)."
        ),
    )
    flat_fitness_tol: float | int | None = Field(
        default=ASK_TELL_DEFAULTS["flat_fitness_tol"],
        description=(
            "Flat-fitness tolerance. Stops when at least half of the "
            "population have fitness within this tolerance of the median."
        ),
    )
    convergence_patience: int | None = Field(
        default=ASK_TELL_DEFAULTS["convergence_patience"],
        description=(
            "Number of consecutive generations the population-convergence "
            "check must pass before the optimiser actually stops."
        ),
    )
    surrogate_convergence_tol: float | int | None = Field(
        default=ASK_TELL_DEFAULTS["surrogate_convergence_tol"],
        description=(
            "Relative tolerance on the model-native convergence signal for "
            "surrogate algorithms (BO, SOBER)."
        ),
    )


class CMAESOptions(_AlgorithmOptions):
    """Options for ``AskTellOptimizer(method="CMAES")`` passed through to pycma.

    Accepts any key valid for ``cma.CMAOptions()`` — see
    `pycma documentation <https://github.com/CMA-ES/pycma>`_ for the full
    list. Common keys: ``CMA_diagonal``, ``ftarget``, ``CMA_stds``,
    ``scaling_of_variables``.

    This is a genuine passthrough leaf: ``cma.CMAOptions()`` is the source of
    truth for the (large) option surface and rejects unknown keys at runtime,
    so this class keeps ``extra="allow"`` rather than enumerating dozens of
    pycma keys. It is on the strictness-guard allowlist for this reason.
    """

    model_config = ConfigDict(extra="allow")


class XNESOptions(_AlgorithmOptions):
    """Options for ``AskTellOptimizer(method="XNES")``.

    XNES has no algorithm-specific options today — its search is fully
    parameterised by the top-level ``AskTellOptimizer`` fields (``sigma0``,
    ``population_size``, …). This class exists as a typed marker so the
    same ``algorithm_options=iws.XNESOptions(...)`` pattern works across
    methods. It is strict (``extra="forbid"``): it declares no option keys,
    so any key passed to it is rejected.
    """


class PSOOptions(_AlgorithmOptions):
    """Options for ``AskTellOptimizer(method="PSO")``.

    Any field left as ``None`` falls back to the PSO defaults set by the
    Ionworks pipeline.

    Parameters
    ----------
    inertia_weight : tuple of (float, float), optional
        ``(w_start, w_end)`` for linear decay. When set, enables inertia mode and
        disables constriction.
    constriction : bool, optional
        Use constriction coefficient. Default ``True`` (when ``inertia_weight``
        is not set).
    c1 : float, optional
        Cognitive coefficient (attraction to personal best). Default 2.05.
    c2 : float, optional
        Social coefficient (attraction to global best). Default 2.05.
    boundary_handling : str, optional
        One of ``"absorb"``, ``"reflect"``, ``"random"``, ``"ignore"``. Default
        ``"reflect"``.
    velocity_clamping : str, optional
        One of ``"none"``, ``"fraction"``, ``"adaptive"``. Default ``"fraction"``.
    v_max_fraction : float, optional
        Fraction of search space for max velocity. Default 0.2.
    max_iterations : int, optional
        Horizon used for adaptive parameter scheduling. Default 1000.
    """

    inertia_weight: tuple[float, float] | list[float] | None = Field(
        default=None,
        description=(
            "Tuple ``(w_start, w_end)`` for linear inertia-weight decay "
            "across iterations. Setting this enables inertia mode and "
            "disables constriction. ``None`` uses the default."
        ),
    )
    constriction: bool | None = Field(
        default=None,
        description=(
            "If ``True``, use the constriction coefficient formulation. "
            "Mutually exclusive with ``inertia_weight``. Default ``True`` "
            "(when ``inertia_weight`` is not set)."
        ),
    )
    c1: float | None = Field(
        default=None,
        description=(
            "Cognitive acceleration coefficient — strength of attraction to "
            "each particle's personal best. Default 2.05."
        ),
    )
    c2: float | None = Field(
        default=None,
        description=(
            "Social acceleration coefficient — strength of attraction to "
            "the swarm's global best. Default 2.05."
        ),
    )
    boundary_handling: str | None = Field(
        default=None,
        description=(
            "Strategy for particles that leave the search box. One of "
            "``'absorb'``, ``'reflect'``, ``'random'``, ``'ignore'``. "
            "Default ``'reflect'``."
        ),
    )
    velocity_clamping: str | None = Field(
        default=None,
        description=(
            "Velocity clamping strategy. One of ``'none'``, ``'fraction'``, "
            "``'adaptive'``. Default ``'fraction'``."
        ),
    )
    v_max_fraction: float | None = Field(
        default=None,
        description=(
            "Maximum velocity per dimension as a fraction of the search-"
            "space span. Default 0.2."
        ),
    )
    max_iterations: int | None = Field(
        default=None,
        description=(
            "Iteration horizon used internally for adaptive parameter "
            "scheduling (e.g. inertia decay). Does not itself terminate the "
            "optimiser — use ``AskTellOptimizer.max_iterations`` for that. "
            "Default 1000."
        ),
    )


class DEOptions(_AlgorithmOptions):
    """Options for ``AskTellOptimizer(method="DifferentialEvolution")``.

    Any field left as ``None`` falls back to the Differential-Evolution
    defaults set by the Ionworks pipeline.

    Parameters
    ----------
    mutation_strategy : str, optional
        One of ``"rand_1"``, ``"best_1"``, ``"current_to_best_1"``, ``"rand_2"``,
        ``"best_2"``, ``"current_to_pbest_1"``. Default ``"current_to_pbest_1"``
        (SHADE adaptive).
    crossover_method : str, optional
        One of ``"binomial"``, ``"exponential"``. Default ``"binomial"``.
    F : float, optional
        Mutation scale factor; initial mean for SHADE adaptive sampling.
        Default 0.5.
    CR : float, optional
        Crossover probability; initial mean for SHADE adaptive sampling.
        Default 0.7.
    dither : bool or tuple of (float, float), optional
        Randomise ``F`` per generation when using classic strategies.
        ``True`` uses the default range ``[0.5, 1.0]``. Default ``True``.
    p_best_rate : float, optional
        Fraction of top individuals for pbest selection. Default 0.1.
    archive_size_ratio : float, optional
        Archive size as a multiple of population. Default 1.0.
    memory_size : int, optional
        Number of history entries for F/CR adaptation. Default equal to
        population size.
    boundary_handling : str, optional
        Boundary handling strategy. Default ``"reflect"``.
    """

    mutation_strategy: str | None = Field(
        default=None,
        description=(
            "DE mutation strategy. One of ``'rand_1'``, ``'best_1'``, "
            "``'current_to_best_1'``, ``'rand_2'``, ``'best_2'``, "
            "``'current_to_pbest_1'``. Default ``'current_to_pbest_1'`` "
            "(SHADE adaptive)."
        ),
    )
    crossover_method: str | None = Field(
        default=None,
        description=(
            "Crossover scheme. One of ``'binomial'``, ``'exponential'``. "
            "Default ``'binomial'``."
        ),
    )
    F: float | None = Field(
        default=None,
        description=(
            "Mutation scale factor; also the initial mean of the SHADE "
            "adaptive distribution. Default 0.5."
        ),
    )
    CR: float | None = Field(
        default=None,
        description=(
            "Crossover probability; also the initial mean of the SHADE "
            "adaptive distribution. Default 0.7."
        ),
    )
    dither: bool | tuple[float, float] | list[float] | None = Field(
        default=None,
        description=(
            "Randomise ``F`` per generation for classic (non-SHADE) "
            "strategies. ``True`` uses the default range ``[0.5, 1.0]``; a "
            "tuple ``(lo, hi)`` uses that range; ``False`` disables "
            "dithering. Default ``True``."
        ),
    )
    p_best_rate: float | None = Field(
        default=None,
        description=(
            "Fraction of top individuals considered for pbest selection in "
            "``'current_to_pbest_1'``. Default 0.1."
        ),
    )
    archive_size_ratio: float | None = Field(
        default=None,
        description=(
            "Archive size expressed as a multiple of the population size. Default 1.0."
        ),
    )
    memory_size: int | None = Field(
        default=None,
        description=(
            "Number of history entries retained for F/CR adaptation in "
            "SHADE. Default is equal to the population size."
        ),
    )
    boundary_handling: str | None = Field(
        default=None,
        description=(
            "Strategy for individuals that leave the search box. Default ``'reflect'``."
        ),
    )


class BayesianOptimizationOptions(_AlgorithmOptions):
    """Options for ``AskTellOptimizer(method="BayesianOptimization")``.

    Any field left as ``None`` falls back to the Bayesian-optimization
    defaults set by the Ionworks pipeline. Strict (``extra="forbid"``): an
    unknown option key is rejected.

    Parameters
    ----------
    n_initial : int, optional
        Number of quasi-random warm-up evaluations before the surrogate model
        is first fitted. ``None`` (default) uses ``max(5, 2 * n_parameters + 1)``.
        Set it to the parallel evaluation capacity (e.g. the batch size on a
        cluster) so the warm-up round uses the full available width.
    noise_floor : str or tuple of (float, float), optional
        Constrain the objective-GP likelihood noise. ``None`` (default) omits the
        key, so the pipeline default applies (``"deterministic"``, i.e. noise
        constrained to ``(1e-8, 1e-3)`` — suited to deterministic simulator
        objectives). Pass ``"standard"`` to restore the uncapped default for
        genuinely noisy objectives; ``"low"`` / ``"deterministic"`` set the low
        interval explicitly; a ``(lo, hi)`` tuple sets a custom interval.
    """

    n_initial: int | None = Field(
        default=None,
        description=(
            "Quasi-random warm-up evaluations before the surrogate is first "
            "fitted. ``None`` uses ``max(5, 2 * n_parameters + 1)``. Set to "
            "the parallel evaluation capacity so the warm-up round uses the "
            "full available width."
        ),
    )
    noise_floor: str | tuple[float, float] | list[float] | None = Field(
        default=None,
        description=(
            "Objective-GP likelihood-noise constraint. ``None`` omits the key, "
            "so the pipeline default applies (``'deterministic'``, noise in "
            "``(1e-8, 1e-3)``). ``'standard'`` restores the uncapped default "
            "for noisy objectives; a ``(lo, hi)`` tuple sets a custom interval."
        ),
    )


class SOBEROptions(_AlgorithmOptions):
    """Options for ``AskTellOptimizer(method="SOBER")``.

    Any field left as ``None`` falls back to the SOBER defaults set by the
    Ionworks pipeline. Strict (``extra="forbid"``): an unknown option key is
    rejected.

    SOBER selects batches by Bayesian quadrature. Its strength is
    quadrature-style estimation rather than pure optimization; when the goal is
    simply the best parameter set, prefer ``method="TuRBO"``,
    ``method="BayesianOptimization"``, or ``method="DifferentialEvolution"`` —
    see the :class:`AskTellOptimizer` Notes for method-selection guidance.

    Parameters
    ----------
    n_initial : int, optional
        Number of quasi-random warm-up evaluations before the surrogate model
        is first fitted — see :class:`BayesianOptimizationOptions`.
    noise_floor : str or tuple of (float, float), optional
        Constrain the objective-GP likelihood noise — see
        :class:`BayesianOptimizationOptions`.
    n_candidates : int, optional
        Number of candidate samples per batch for kernel recombination.
        Default 1024. The recombination's selection pressure is
        ``n_candidates : batch size`` — keep it near ~100:1 (e.g. 20000 at
        batch 200) when running wide batches; the default is only adequate
        for small batches.
    n_nystrom : int, optional
        Number of samples for the Nystrom approximation of the kernel.
        Default ``min(512, n_candidates // 2)``. Must exceed the batch size.
    gp_kernel : str, optional
        Objective-GP kernel style. ``"botorch"`` (default) uses an ARD RBF
        kernel with per-dimension lengthscales — the best general choice,
        especially on anisotropic or constrained problems. ``"reference"``
        uses the isotropic kernel of the original SOBER implementation,
        whose sharper sampling measure converges deeper on smooth
        low-dimensional problems with an interior optimum.
    """

    n_initial: int | None = Field(
        default=None,
        description=(
            "Quasi-random warm-up evaluations before the surrogate is first "
            "fitted — see ``BayesianOptimizationOptions.n_initial``."
        ),
    )
    noise_floor: str | tuple[float, float] | list[float] | None = Field(
        default=None,
        description=(
            "Objective-GP likelihood-noise constraint — see "
            "``BayesianOptimizationOptions.noise_floor``."
        ),
    )
    n_candidates: int | None = Field(
        default=None,
        description=(
            "Candidate samples per batch for kernel recombination. Default "
            "1024. Keep ``n_candidates : batch size`` near ~100:1 for wide "
            "batches (e.g. 20000 at batch 200)."
        ),
    )
    n_nystrom: int | None = Field(
        default=None,
        description=(
            "Samples for the Nystrom approximation of the kernel. Default "
            "``min(512, n_candidates // 2)``. Must exceed the batch size."
        ),
    )
    gp_kernel: str | None = Field(
        default=None,
        description=(
            "Objective-GP kernel style: ``'botorch'`` (default; ARD RBF, "
            "best general choice) or ``'reference'`` (isotropic kernel of "
            "the original SOBER implementation; converges deeper on smooth "
            "low-dimensional problems with an interior optimum)."
        ),
    )


class TuRBOOptions(_AlgorithmOptions):
    """Options for ``AskTellOptimizer(method="TuRBO")``.

    Any field left as ``None`` falls back to the TuRBO defaults set by the
    Ionworks pipeline. Strict (``extra="forbid"``): an unknown option key is
    rejected.

    Parameters
    ----------
    n_initial : int, optional
        Number of quasi-random warm-up evaluations before the surrogate model
        is first fitted — see :class:`BayesianOptimizationOptions`. On a
        parallel cluster, set it to the batch width when that is much larger
        than the dimension-based default so the warm-up round uses the full
        available width.
    noise_floor : str or tuple of (float, float), optional
        Constrain the objective-GP likelihood noise — see
        :class:`BayesianOptimizationOptions`.
    n_candidates : int, optional
        Candidate-pool size for Thompson sampling inside the trust region.
        Default ``min(5000, 200 * n_parameters)``.
    tr_length_init : float, optional
        Initial trust-region edge length in normalized ``[0, 1]`` coordinates.
        Default 0.8.
    tr_length_min : float, optional
        Trust-region edge length below which the region restarts. Default
        ``2**-7``.
    tr_length_max : float, optional
        Maximum trust-region edge length. Default 1.6.
    tr_success_tolerance : int, optional
        Consecutive improving batches before the region doubles. Default 3.
    tr_failure_tolerance : int, optional
        Consecutive non-improving batches before the region halves. Default
        ``ceil(max(4, n_parameters) / batch_size)``.
    gp_max_points : int, optional
        Maximum number of observations used per surrogate refit
        (trust-region-local windowing). Bounds the cubic cost of exact GP
        fitting on long or wide campaigns. Default 1000.
    """

    n_initial: int | None = Field(
        default=None,
        description=(
            "Quasi-random warm-up evaluations before the surrogate is first "
            "fitted — see ``BayesianOptimizationOptions.n_initial``."
        ),
    )
    noise_floor: str | tuple[float, float] | list[float] | None = Field(
        default=None,
        description=(
            "Objective-GP likelihood-noise constraint — see "
            "``BayesianOptimizationOptions.noise_floor``."
        ),
    )
    n_candidates: int | None = Field(
        default=None,
        description=(
            "Candidate-pool size for Thompson sampling inside the trust "
            "region. Default ``min(5000, 200 * n_parameters)``."
        ),
    )
    tr_length_init: float | None = Field(
        default=None,
        description=(
            "Initial trust-region edge length in normalized ``[0, 1]`` "
            "coordinates. Default 0.8."
        ),
    )
    tr_length_min: float | None = Field(
        default=None,
        description=(
            "Trust-region edge length below which the region restarts. "
            "Default ``2**-7``."
        ),
    )
    tr_length_max: float | None = Field(
        default=None,
        description="Maximum trust-region edge length. Default 1.6.",
    )
    tr_success_tolerance: int | None = Field(
        default=None,
        description=(
            "Consecutive improving batches before the region doubles. Default 3."
        ),
    )
    tr_failure_tolerance: int | None = Field(
        default=None,
        description=(
            "Consecutive non-improving batches before the region halves. "
            "Default ``ceil(max(4, n_parameters) / batch_size)``."
        ),
    )
    gp_max_points: int | None = Field(
        default=None,
        description=(
            "Maximum observations used per surrogate refit (trust-region-"
            "local windowing); bounds the cubic exact-GP fitting cost. "
            "Default 1000."
        ),
    )


class CMAES(_AskTellBase):
    """Covariance Matrix Adaptation Evolution Strategy (CMA-ES).

    A strong default for ill-conditioned, noisy, non-linear fits.
    Convenience wrapper around ``AskTellOptimizer(method="CMAES")``; see
    :class:`AskTellOptimizer` for the full list of accepted kwargs.

    Examples
    --------
    >>> opt = iws.parameter_estimators.CMAES()
    >>> fit = iws.DataFit(
    ...     objectives={"ocp": iws.objectives.OCPHalfCell(
    ...         electrode="positive", data_input="path/to/ocp.csv",
    ...     )},
    ...     parameters={"x": iws.Parameter("x", initial_value=1.0, bounds=(0.0, 2.0))},
    ...     optimizer=opt,
    ... )"""

    type: Literal["CMAES"] = "CMAES"
    algorithm_options: CMAESOptions | None = Field(
        default=None, description="CMA-ES-specific options (see CMAESOptions)."
    )


class DifferentialEvolution(_AskTellBase):
    """Differential Evolution (DE) with SHADE adaptive control.

    Uses success-history based adaptive F/CR with current-to-pbest/1 mutation by default.
    Convenience wrapper around ``AskTellOptimizer(method="DifferentialEvolution")``.
    See `AskTellOptimizer` class for full parameter documentation.

    Examples
    --------
    >>> opt = iws.parameter_estimators.DifferentialEvolution()
    >>> fit = iws.DataFit(
    ...     objectives={"ocp": iws.objectives.OCPHalfCell(
    ...         electrode="positive", data_input="path/to/ocp.csv",
    ...     )},
    ...     parameters={"x": iws.Parameter("x", initial_value=1.0, bounds=(0.0, 2.0))},
    ...     optimizer=opt,
    ... )"""

    type: Literal["DifferentialEvolution"] = "DifferentialEvolution"
    algorithm_options: DEOptions | None = Field(
        default=None, description="DE-specific options (see DEOptions)."
    )


class BayesianOptimization(_AskTellBase):
    """Bayesian Optimization with a Gaussian-process surrogate.

    Sample-efficient for expensive black-box objectives with fewer than ~30
    parameters. Convenience wrapper around
    ``AskTellOptimizer(method="BayesianOptimization")``; see
    :class:`AskTellOptimizer` for the full list of accepted kwargs and pass
    ``algorithm_options=iws.BayesianOptimizationOptions(...)`` to configure the
    surrogate.

    Examples
    --------
    >>> opt = iws.parameter_estimators.BayesianOptimization()
    >>> fit = iws.DataFit(
    ...     objectives={"ocp": iws.objectives.OCPHalfCell(
    ...         electrode="positive", data_input="path/to/ocp.csv",
    ...     )},
    ...     parameters={"x": iws.Parameter("x", initial_value=1.0, bounds=(0.0, 2.0))},
    ...     optimizer=opt,
    ... )"""

    type: Literal["BayesianOptimization"] = "BayesianOptimization"
    algorithm_options: BayesianOptimizationOptions | None = Field(
        default=None,
        description="BO-specific options (see BayesianOptimizationOptions).",
    )


class SOBER(_AskTellBase):
    """SOBER: batch Bayesian optimization via quadrature-style recombination.

    Selects whole batches by Bayesian quadrature; strongest when the goal is
    quadrature-style estimation rather than pure optimization. Convenience
    wrapper around ``AskTellOptimizer(method="SOBER")``; see
    :class:`AskTellOptimizer` for the full list of accepted kwargs and pass
    ``algorithm_options=iws.SOBEROptions(...)`` to configure the surrogate.

    Examples
    --------
    >>> opt = iws.parameter_estimators.SOBER()
    >>> fit = iws.DataFit(
    ...     objectives={"ocp": iws.objectives.OCPHalfCell(
    ...         electrode="positive", data_input="path/to/ocp.csv",
    ...     )},
    ...     parameters={"x": iws.Parameter("x", initial_value=1.0, bounds=(0.0, 2.0))},
    ...     optimizer=opt,
    ... )"""

    type: Literal["SOBER"] = "SOBER"
    algorithm_options: SOBEROptions | None = Field(
        default=None, description="SOBER-specific options (see SOBEROptions)."
    )


class TuRBO(_AskTellBase):
    """TuRBO: trust-region Bayesian optimization.

    Suited to expensive parallel or constrained problems, scaling to higher
    dimensions than global BO via a local trust region. Convenience wrapper
    around ``AskTellOptimizer(method="TuRBO")``; see :class:`AskTellOptimizer`
    for the full list of accepted kwargs and pass
    ``algorithm_options=iws.TuRBOOptions(...)`` to configure the surrogate.

    Examples
    --------
    >>> opt = iws.parameter_estimators.TuRBO()
    >>> fit = iws.DataFit(
    ...     objectives={"ocp": iws.objectives.OCPHalfCell(
    ...         electrode="positive", data_input="path/to/ocp.csv",
    ...     )},
    ...     parameters={"x": iws.Parameter("x", initial_value=1.0, bounds=(0.0, 2.0))},
    ...     optimizer=opt,
    ... )"""

    type: Literal["TuRBO"] = "TuRBO"
    algorithm_options: TuRBOOptions | None = Field(
        default=None, description="TuRBO-specific options (see TuRBOOptions)."
    )


class DummyOptimizer(BaseSchema):
    """Alias for ``PointEstimateOptimizer``.

    Returns the supplied initial guess without running any optimisation —
    useful as a no-op in tests
    and pipeline scaffolding.
    """

    # Accept the runtime short-form tag ("Dummy") as well as the schema class
    # name so engine/reverse-parsed configs validate; default stays the class
    # name (unchanged serialization for schema users).
    type: Literal["DummyOptimizer", "Dummy"] = "DummyOptimizer"


class DummySampler(BaseSchema):
    """Alias for ``PointEstimateSampler``.

    Returns a single sample equal to the initial guess — useful as a no-op
    in sampling pipelines.
    """

    type: Literal["DummySampler"] = "DummySampler"


class GridSearch(BaseSchema):
    """Grid search sampler.

    Evaluates the objective at all combinations of grid points across
    dimensions — a deterministic,
    exhaustive sweep. Cost grows as ``npts ** n_parameters``; keep the
    parameter count small.
    """

    type: Literal["GridSearch"] = "GridSearch"
    npts: int = Field(
        default=10,
        description=(
            "Number of evenly spaced points per dimension. Total evaluations "
            "are ``npts ** n_parameters``. Default 10."
        ),
    )

    def __init__(self, npts=10, type="GridSearch"):
        # ``type`` is forwarded so dict-discrimination (which constructs via
        # ``cls(**data)`` for models with a custom __init__) can pass it through.
        super().__init__(npts=npts, type=type)


class Optimizer(BaseSchema):
    """Base class for all optimizers.

    Optimisers seek a single optimal point in parameter space that
    minimises the objective. Not used
    directly — pick a concrete subclass such as ``AskTellOptimizer`` or
    one of the ``Scipy*`` wrappers.

    Parameters
    ----------
    `**kwargs`
        Arguments passed to the underlying optimiser algorithm.
    """

    pass


class PSO(_AskTellBase):
    """Particle Swarm Optimization (PSO). Population-based optimiser inspired by
    bird-flocking behaviour.

    Convenience wrapper around ``AskTellOptimizer(method="PSO")``; see
    :class:`AskTellOptimizer` for the full list of accepted kwargs.

    Examples
    --------
    >>> opt = iws.parameter_estimators.PSO()
    >>> fit = iws.DataFit(
    ...     objectives={"ocp": iws.objectives.OCPHalfCell(
    ...         electrode="positive", data_input="path/to/ocp.csv",
    ...     )},
    ...     parameters={"x": iws.Parameter("x", initial_value=1.0, bounds=(0.0, 2.0))},
    ...     optimizer=opt,
    ... )"""

    type: Literal["PSO"] = "PSO"
    algorithm_options: PSOOptions | None = Field(
        default=None, description="PSO-specific options (see PSOOptions)."
    )


class ParameterEstimator(BaseSchema):
    """Base class for all parameter estimators.

    Parameter estimators find an optimal (or posterior) parameter set by
    minimising an objective. Not used directly — pick a concrete
    ``Optimizer`` or ``Sampler`` subclass.

    Parameters
    ----------
    `**kwargs`
        Arguments passed to the underlying estimation algorithm.
    """

    pass


class AskTellOptimizer(_AskTellBase):
    """Ask/tell optimizer for population-based and simplex optimization.

    Supports CMAES, PSO, DifferentialEvolution, XNES, Nelder-Mead,
    BayesianOptimization, SOBER, and TuRBO.

    Parameters
    ----------
    method : str, optional
        Optimization method. Default is "CMAES". Must be one of:
        "CMAES", "Nelder-Mead", "PSO", "DifferentialEvolution", "XNES",
        "BayesianOptimization", "SOBER", or "TuRBO".
    log_to_screen : bool, optional
        Whether to print optimization progress. Default is False.
    sigma0 : float | np.ndarray, optional
        Initial step size for population-based methods. Default is None.
    max_iterations : int, optional
        Maximum number of iterations. Default is 300.
    max_unchanged_iterations : int, optional
        Stop after this many iterations without improvement. Default is 75.
    max_unchanged_iterations_threshold : float, optional
        Legacy alias for ``absolute_tolerance``. Prefer
        ``absolute_tolerance`` on new code.
    min_iterations : int, optional
        Minimum iterations before checking stopping criteria. Default is 1.
    max_evaluations : int, optional
        Maximum number of function evaluations. Default is 1e6.
    population_size : int, optional
        Population size for population-based methods. Default is method-specific.
    threshold : float, optional
        Target objective value to stop optimization. Default is None.
    absolute_tolerance : float, optional
        Absolute tolerance for unchanged iterations. Default is 1e-5.
    relative_tolerance : float, optional
        Relative tolerance for unchanged iterations. Default is 1e-2.
    xtol : float, optional
        Parameter change tolerance (L-inf norm). Default is 1e-6.
    population_convergence_tol : float, optional
        Population convergence tolerance. The exact convergence semantics
        are algorithm-dependent (e.g. DE also checks position-space
        diversity). Default is 5e-3.
    flat_fitness_tol : float, optional
        Flat fitness tolerance. Default is None (disabled).
    convergence_patience : int, optional
        Number of consecutive generations the population convergence check
        must pass before actually stopping. Default is 3.
    surrogate_convergence_tol : float, optional
        Relative tolerance on the model-native convergence signal for
        surrogate algorithms (BO, SOBER). Fires when the expected improvement
        at the algorithm's best candidate is below ``tol`` times the range of
        observed costs for ``convergence_patience`` consecutive iterations.
        Default 1e-3. Set to ``None`` to disable.
    algorithm_options : dict, optional
        Algorithm-specific configuration options. For PSO, supported keys are:

        - ``inertia_weight``: tuple[float, float] - (w_start, w_end) for linear decay.
          Enables inertia mode and disables constriction.
        - ``constriction``: bool - Use constriction coefficient (default: True)
        - ``c1``: float - Cognitive coefficient (default: 2.05)
        - ``c2``: float - Social coefficient (default: 2.05)
        - ``boundary_handling``: str | BoundaryHandling - "absorb", "reflect", "random", "ignore"
        - ``velocity_clamping``: str | VelocityClamping - "none", "fraction", "adaptive"
        - ``v_max_fraction``: float - Fraction of search space for max velocity (default: 0.2)
        - ``max_iterations``: int - For adaptive parameter scheduling (default: 1000)

    `**kwargs`
        Additional arguments for the AskTellOptimizer constructor.

    Notes
    -----
    **Choosing a method.** ``"CMAES"`` (the default) is a robust general-purpose
    choice. For cheap, fast-evaluating objectives with many parameters (e.g.
    high-dimensional parameter fits), ``"DifferentialEvolution"`` with a small
    population and many generations makes the most progress per evaluation. For
    expensive simulations with a small evaluation budget and few parameters
    (roughly ten or fewer, e.g. design optimization), ``"BayesianOptimization"``
    is the most sample-efficient and reliable. When expensive evaluations run in
    parallel at wide batch sizes, or the problem is high-dimensional and
    constrained, ``"TuRBO"`` is the recommended surrogate — set
    :class:`TuRBOOptions` ``n_initial`` to the batch width so the warm-up round
    uses the full parallel capacity. ``"SOBER"`` selects batches by Bayesian
    quadrature; its strength is quadrature-style estimation rather than pure
    optimization — prefer ``"TuRBO"``, ``"BayesianOptimization"``, or
    ``"DifferentialEvolution"`` when the goal is simply the best parameter set.

    Parallelism is owned by the execution engine; optimizers run a single algorithm loop.

    Examples
    --------
    >>> opt = iws.parameter_estimators.AskTellOptimizer(
    ...     method="CMAES", max_iterations=200,
    ... )
    >>> fit = iws.DataFit(
    ...     objectives={"ocp": iws.objectives.OCPHalfCell(
    ...         electrode="positive", data_input="path/to/ocp.csv",
    ...     )},
    ...     parameters={"x": iws.Parameter("x", initial_value=1.0, bounds=(0.0, 2.0))},
    ...     optimizer=opt,
    ... )
    """

    type: Literal["AskTellOptimizer"] = "AskTellOptimizer"
    method: str = Field(
        default="CMAES",
        description=(
            "Optimisation method. One of ``'CMAES'``, ``'Nelder-Mead'``, "
            "``'PSO'``, ``'DifferentialEvolution'``, ``'XNES'``, "
            "``'BayesianOptimization'``, ``'SOBER'``, or ``'TuRBO'``. "
            "Default ``'CMAES'``. See the class Notes for guidance on "
            "choosing a method."
        ),
    )
    algorithm_options: (
        dict
        | CMAESOptions
        | PSOOptions
        | DEOptions
        | XNESOptions
        | BayesianOptimizationOptions
        | SOBEROptions
        | TuRBOOptions
        | None
    ) = Field(
        default=None,
        # ``dict`` first (left-to-right) so a raw dict stays a dict rather than
        # being greedily coerced into ``CMAESOptions`` (which is ``extra="allow"``
        # and would accept any dict regardless of ``method``);
        # ``_validate_options_for_method`` then checks it against the method's leaf.
        union_mode="left_to_right",
        description=(
            "Algorithm-specific options. Use the typed wrappers "
            "``CMAESOptions``, ``PSOOptions``, ``DEOptions``, ``XNESOptions``, "
            "``BayesianOptimizationOptions``, ``SOBEROptions``, or "
            "``TuRBOOptions`` for field-level validation, or pass a raw "
            "``dict`` for forward compatibility. See each wrapper's docstring "
            "for supported keys."
        ),
    )

    def __init__(
        self,
        method="CMAES",
        log_to_screen=ASK_TELL_DEFAULTS["log_to_screen"],
        sigma0=ASK_TELL_DEFAULTS["sigma0"],
        max_iterations=ASK_TELL_DEFAULTS["max_iterations"],
        max_unchanged_iterations=ASK_TELL_DEFAULTS["max_unchanged_iterations"],
        max_unchanged_iterations_threshold=ASK_TELL_DEFAULTS[
            "max_unchanged_iterations_threshold"
        ],
        min_iterations=ASK_TELL_DEFAULTS["min_iterations"],
        max_evaluations=ASK_TELL_DEFAULTS["max_evaluations"],
        population_size=ASK_TELL_DEFAULTS["population_size"],
        threshold=ASK_TELL_DEFAULTS["threshold"],
        absolute_tolerance=ASK_TELL_DEFAULTS["absolute_tolerance"],
        relative_tolerance=ASK_TELL_DEFAULTS["relative_tolerance"],
        xtol=ASK_TELL_DEFAULTS["xtol"],
        population_convergence_tol=ASK_TELL_DEFAULTS["population_convergence_tol"],
        flat_fitness_tol=ASK_TELL_DEFAULTS["flat_fitness_tol"],
        convergence_patience=ASK_TELL_DEFAULTS["convergence_patience"],
        surrogate_convergence_tol=ASK_TELL_DEFAULTS["surrogate_convergence_tol"],
        algorithm_options=None,
        type="AskTellOptimizer",
    ):
        # ``type`` is forwarded so dict-discrimination can construct this model
        # (which has a custom __init__) with the discriminator key present.
        super().__init__(
            type=type,
            method=method,
            log_to_screen=log_to_screen,
            sigma0=sigma0,
            max_iterations=max_iterations,
            max_unchanged_iterations=max_unchanged_iterations,
            max_unchanged_iterations_threshold=max_unchanged_iterations_threshold,
            min_iterations=min_iterations,
            max_evaluations=max_evaluations,
            population_size=population_size,
            threshold=threshold,
            absolute_tolerance=absolute_tolerance,
            relative_tolerance=relative_tolerance,
            xtol=xtol,
            population_convergence_tol=population_convergence_tol,
            flat_fitness_tol=flat_fitness_tol,
            convergence_patience=convergence_patience,
            surrogate_convergence_tol=surrogate_convergence_tol,
            algorithm_options=algorithm_options,
        )

    @model_validator(mode="after")
    def _validate_options_for_method(self):
        if self.method not in _OPTIONS_BY_METHOD:
            raise ValueError(
                f"Unknown method {self.method!r}. One of {sorted(_OPTIONS_BY_METHOD)}."
            )
        expected = _OPTIONS_BY_METHOD[self.method]
        opts = self.algorithm_options
        # Already exactly the right typed leaf (the common case via the field
        # union or an explicit ``*Options`` instance) → pydantic validated it on
        # construction; nothing more to do. Exact type, not isinstance: a
        # subclass leaf (e.g. CMAESOptions) must still be rejected when the
        # method expects the base ``_AlgorithmOptions`` (e.g. Nelder-Mead).
        if type(opts) is expected:
            return self
        # A raw dict (or a foreign *Options instance) hasn't been checked against
        # this method's leaf — validate it. ``model_validate`` of a foreign model
        # instance does not re-validate, so dump it to a plain dict first
        # (``_AlgorithmOptions`` emits no "type", so to_config() is a plain dict).
        if isinstance(opts, BaseSchema):
            opts = opts.to_config()
        expected.model_validate(opts or {})
        return self


#: Maps each ``AskTellOptimizer(method=...)`` to its strict ``*Options`` class.
#: ``Nelder-Mead`` has no method-specific options, so it validates against the
#: empty ``_AlgorithmOptions`` (which forbids any key).
_OPTIONS_BY_METHOD = {
    "CMAES": CMAESOptions,
    "PSO": PSOOptions,
    "XNES": XNESOptions,
    "DifferentialEvolution": DEOptions,
    "BayesianOptimization": BayesianOptimizationOptions,
    "SOBER": SOBEROptions,
    "TuRBO": TuRBOOptions,
    "Nelder-Mead": _AlgorithmOptions,
}


#: Deprecated alias — use ``AskTellOptimizer`` instead.
PintsOptimizer = AskTellOptimizer


class PintsSampler(BaseSchema):
    """Sampler using the Pints library: Probabilistic Inference for Bayesian Models.

    Wraps Pints' MCMCController class for MCMC sampling.

    Parameters
    ----------
    method : str, optional
        Sampling method. Default is "DramACMC". Must be one of:
        "DramACMC", "HamiltonianMCMC", "HaarioBardenetACMC", "MALAMCMC",
        "MetropolisRandomWalkMCMC", "MonomialGammaHamiltonianMCMC", "NoUTurnMCMC",
        "PopulationMCMC", "RelativisticMCMC", "SliceDoublingMCMC",
        "SliceRankShrinkingMCMC", or "SliceStepoutMCMC".
    log_to_screen : bool, optional
        Whether to print information at runtime. Default is False.
    max_iterations : int, optional
        Maximum number of iterations. Default is 1000.
    burnin_iterations : int, optional
        Number of initial iterations to discard. Default is 10% of max_iterations.
    initial_phase_iterations : int, optional
        Number of iterations in initial phase. Only used for methods that need an initial phase.
        Default is equal to burnin_iterations.
    `**kwargs`
        Additional parameters passed to the pints MCMC sampler.
        See `pints documentation <https://github.com/pints-team/pints>`_ for details.

    Notes
    -----
    - The log PDF values are cached internally to work around a pints limitation.
    - For methods that need an initial phase, initial_phase_iterations must not exceed
      burnin_iterations, which in turn must not exceed max_iterations."""

    # Accept the runtime short-form tag ("Pints") as well as the schema name.
    type: Literal["PintsSampler", "Pints"] = "PintsSampler"
    method: str = Field(
        default="DramACMC",
        description=(
            "MCMC sampling method from Pints. One of ``'DramACMC'``, "
            "``'HamiltonianMCMC'``, ``'HaarioBardenetACMC'``, ``'MALAMCMC'``, "
            "``'MetropolisRandomWalkMCMC'``, "
            "``'MonomialGammaHamiltonianMCMC'``, ``'NoUTurnMCMC'``, "
            "``'PopulationMCMC'``, ``'RelativisticMCMC'``, "
            "``'SliceDoublingMCMC'``, ``'SliceRankShrinkingMCMC'``, or "
            "``'SliceStepoutMCMC'``. Default ``'DramACMC'``."
        ),
    )
    log_to_screen: bool = Field(
        default=False,
        description=(
            "If ``True``, print Pints runtime information to stdout. Default ``False``."
        ),
    )
    max_iterations: int = Field(
        default=1000,
        description=(
            "Total number of MCMC iterations (including burn-in). Default 1000."
        ),
    )
    burnin_iterations: int | None = Field(
        default=None,
        description=(
            "Number of initial iterations to discard before collecting the "
            "posterior samples. Default is 10 percent of ``max_iterations`` (i.e. "
            "``None`` resolves to ``max_iterations // 10``)."
        ),
    )
    initial_phase_iterations: int | None = Field(
        default=None,
        description=(
            "Length of the adaptive initial phase for samplers that require "
            "one. Must satisfy ``initial_phase_iterations <= "
            "burnin_iterations <= max_iterations``. Default is equal to "
            "``burnin_iterations``."
        ),
    )

    def __init__(
        self,
        method="DramACMC",
        log_to_screen=False,
        max_iterations=1000,
        burnin_iterations=None,
        initial_phase_iterations=None,
        type="PintsSampler",
    ):
        # ``type`` is forwarded so dict-discrimination can construct this model
        # (which has a custom __init__) with the discriminator key present.
        super().__init__(
            type=type,
            method=method,
            log_to_screen=log_to_screen,
            max_iterations=max_iterations,
            burnin_iterations=burnin_iterations,
            initial_phase_iterations=initial_phase_iterations,
        )


class PointEstimateOptimizer(BaseSchema):
    """No-op optimiser — returns the initial guess unchanged.

    Useful for evaluating a single parameter set or initialising pipelines
    without
    paying the cost of a real optimiser run.

    Examples
    --------
    >>> opt = iws.parameter_estimators.PointEstimateOptimizer()
    >>> fit = iws.DataFit(
    ...     objectives={"ocp": iws.objectives.OCPHalfCell(
    ...         electrode="positive", data_input="path/to/ocp.csv",
    ...     )},
    ...     parameters={"x": iws.Parameter("x", initial_value=1.0, bounds=(0.0, 2.0))},
    ...     optimizer=opt,
    ... )
    """

    # Accept the runtime short-form tag ("PointEstimate") as well; the short
    # form resolves to the optimizer (matching the engine resolver default).
    type: Literal["PointEstimateOptimizer", "PointEstimate"] = "PointEstimateOptimizer"


class PointEstimateSampler(BaseSchema):
    """No-op sampler — returns the initial guess as a single sample.

    Useful for evaluating a single parameter set within a sampling-style
    pipeline without paying
    the cost of real MCMC.
    """

    type: Literal["PointEstimateSampler"] = "PointEstimateSampler"


class Sampler(BaseSchema):
    """Base class for all Monte Carlo-style samplers.

    Samplers explore parameter space to
    characterise the posterior, in contrast to optimisers which return a
    single best point. Not used directly — pick a concrete subclass such
    as ``PintsSampler`` or ``GridSearch``.

    Parameters
    ----------
    `**kwargs`
        Arguments passed to the underlying sampling algorithm.
    """

    pass


class ScipyBasinhopping(_PassthroughOptimizer):
    """Global optimizer using basin-hopping with local minimization.

    Basin-hopping is a two-phase stochastic algorithm that combines random perturbations
    with local minimization to escape local minima. It repeatedly applies random
    perturbations to the current minimum, accepts or rejects based on the Metropolis
    criterion, and performs local minimization from the perturbed position. This approach
    efficiently explores the energy landscape while refining solutions locally.

    Notes
    -----
    - Accepts initial guess `x0` as the starting point for optimization
    - More efficient than pure global search for moderately complex landscapes
    - Local minimizer can be customized via `minimizer_kwargs` parameter
    - Stochastic algorithm (use `seed` parameter for reproducibility)
    - Supports constraints through the local minimizer (via `minimizer_kwargs`)
    - Temperature parameter controls acceptance of uphill moves (higher = more exploration)

    Parameters
    ----------
    niter : int, default=100
        Number of basin-hopping iterations.
    T : float, default=1.0
        Temperature parameter for the Metropolis acceptance criterion.
        Higher values increase the probability of accepting uphill moves.
    stepsize : float, default=0.5
        Initial step size for random displacement of coordinates.
    minimizer_kwargs : dict, optional
        Extra keyword arguments passed to the local minimizer (scipy.optimize.minimize).
        Can specify the local method, bounds, constraints, and convergence criteria.
        Default uses L-BFGS-B with provided bounds.
    take_step : callable, optional
        Custom step-taking function. If None, uses random displacement.
    accept_test : callable, optional
        Custom acceptance test function. If None, uses Metropolis criterion.
    interval : int, default=50
        Interval for updating stepsize (adaptive step size adjustment).
    seed : int, optional
        Random seed for reproducible results.
    `**kwargs`
        Additional arguments passed to `scipy.optimize.basinhopping`.
        See scipy documentation for complete options."""

    type: Literal["ScipyBasinhopping"] = "ScipyBasinhopping"


class ScipyDifferentialEvolution(_PassthroughOptimizer):
    """
    Global stochastic optimizer using differential evolution with parallel evaluation.

    Differential evolution is a robust global optimization algorithm that evolves a
    population of candidate solutions across generations. It excels at handling
    multi-modal, non-convex objective landscapes and requires no gradient information.

    Notes
    -----
    - Does not support custom equality or inequality constraints
    - Initial guess `x0` is ignored; initial population is generated from bounds
    - Polish option disabled by default as it conventionally significantly decreases performance
    - Callback logs only best solution per generation (not individual evaluations)
    - ``workers`` parallelises evaluations within scipy's DE loop; fit-level
      parallelism (multistarts, objectives) is managed by the execution engine

    Parameters
    ----------
    workers : int, default=1
        Number of parallel workers for function evaluations. Use -1 for all CPU cores.
    max_iterations : int, default=1000
        Maximum number of generations. Passed to scipy as ``maxiter``.
    population_size : int, default=15
        Population size multiplier (total population = population_size *
        dimensionality). Passed to scipy as ``popsize``.
    strategy : str, default='best1bin'
        Differential evolution strategy. Options include 'best1bin', 'rand1bin',
        'best2bin', 'rand2bin', 'currenttobest1bin'.
    mutation : float or tuple, default=(0.5, 1)
        Mutation constant. Can be float or (min, max) tuple for adaptive mutation.
    recombination : float, default=0.7
        Crossover probability for parameter mixing.
    seed : int, optional
        Random seed for reproducible results.
    atol, tol : float, optional
        Absolute and relative tolerance for convergence.
    `**kwargs`
        Additional arguments passed to `scipy.optimize.differential_evolution`.
        See scipy documentation for complete options.

    Examples
    --------
    >>> opt = iws.parameter_estimators.ScipyDifferentialEvolution()
    >>> fit = iws.DataFit(
    ...     objectives={"ocp": iws.objectives.OCPHalfCell(
    ...         electrode="positive", data_input="path/to/ocp.csv",
    ...     )},
    ...     parameters={"x": iws.Parameter("x", initial_value=1.0, bounds=(0.0, 2.0))},
    ...     optimizer=opt,
    ... )
    """

    type: Literal["ScipyDifferentialEvolution"] = "ScipyDifferentialEvolution"


class ScipyDualAnnealing(_PassthroughOptimizer):
    """Global stochastic optimizer using dual annealing.

    Dual annealing combines generalized simulated annealing with fast local search.
    It's designed for global optimization with a good balance between exploration
    and exploitation, particularly effective for rugged objective landscapes.

    Notes
    -----
    - Does not support custom equality or inequality constraints
    - Accepts optional initial guess `x0` to seed the search
    - Stochastic algorithm (use `seed` parameter for reproducibility)
    - Generally faster convergence than pure simulated annealing
    - Good choice when gradient information is unavailable

    Parameters
    ----------
    max_iterations : int, default=1000
        Maximum number of global search iterations. Passed to scipy as ``maxiter``.
    initial_temp : float, default=5230
        Initial temperature for the annealing schedule.
    restart_temp_ratio : float, default=2e-5
        Temperature ratio for restart condition during local search.
    visit : float, default=2.62
        Parameter for the visiting distribution (higher = more exploration).
    accept : float, default=-5.0
        Parameter for the acceptance distribution (lower = more exploitation).
    seed : int, optional
        Random seed for reproducible results.
    no_local_search : bool, default=False
        If True, skip local minimization (pure generalized simulated annealing).
    `**kwargs`
        Additional arguments passed to `scipy.optimize.dual_annealing`.
        See scipy documentation for complete options."""

    type: Literal["ScipyDualAnnealing"] = "ScipyDualAnnealing"


class ScipyLeastSquares(_PassthroughOptimizer):
    """Nonlinear least squares optimizer using scipy's Trust Region Reflective algorithm.

    This optimizer is designed for problems where the objective returns a residual vector
    rather than a scalar cost. It minimizes the sum of squares of the residuals. Best
    suited for well-behaved, smooth problems with a clear residual structure.

    Notes
    -----
    - Requires objective functions that return an array (residual vector)
    - Automatically handles linear algebra errors by returning NaN values
    - More efficient than general minimization for least-squares structure
    - Supports bound constraints but not general equality/inequality constraints

    Parameters
    ----------
    method : str, optional
        Algorithm to use. Options: 'trf' (default), 'dogbox', 'lm'.
    ftol, xtol, gtol : float, optional
        Tolerance parameters for convergence criteria.
    max_nfev : int, optional
        Maximum number of function evaluations.
    `**kwargs`
        Additional arguments passed to `scipy.optimize.least_squares`.
        See scipy documentation for complete options."""

    type: Literal["ScipyLeastSquares"] = "ScipyLeastSquares"


class ScipyMinimize(_PassthroughOptimizer):
    """General-purpose scalar minimization with support for constraints.

    Wraps scipy's `minimize` function, providing access to multiple local optimization
    algorithms (e.g., L-BFGS-B, SLSQP, trust-constr, COBYQA). Suitable for smooth,
    scalar-valued objectives with optional equality and inequality constraints.

    Notes
    -----
    - Requires objective functions that return a scalar value
    - Supports bound constraints and custom equality/inequality constraints
    - Choice of method depends on problem structure and constraint types
    - Some methods (e.g., 'L-BFGS-B') support bounds only, not general constraints

    Parameters
    ----------
    method : str, optional
        Optimization algorithm. Common choices:
        - 'L-BFGS-B': Bound-constrained, gradient-based (default for bounded problems)
        - 'SLSQP': Sequential Least Squares, supports all constraint types
        - 'trust-constr': Modern trust-region method, supports all constraints
        - 'COBYQA': Derivative-free, supports nonlinear constraints
    max_iterations : int, optional
        Maximum number of iterations. Passed to scipy as ``maxiter``.
    tol : float, optional
        Tolerance for termination.
    `**kwargs`
        Additional arguments passed to `scipy.optimize.minimize`.
        See scipy documentation for complete options.

    Examples
    --------
    >>> opt = iws.parameter_estimators.ScipyMinimize(method="L-BFGS-B")
    >>> fit = iws.DataFit(
    ...     objectives={"ocp": iws.objectives.OCPHalfCell(
    ...         electrode="positive", data_input="path/to/ocp.csv",
    ...     )},
    ...     parameters={"x": iws.Parameter("x", initial_value=1.0, bounds=(0.0, 2.0))},
    ...     optimizer=opt,
    ... )"""

    type: Literal["ScipyMinimize"] = "ScipyMinimize"


class ScipyShgo(_PassthroughOptimizer):
    """Global optimizer using simplicial homology techniques.

    SHGO (Simplicial Homology Global Optimization) uses topological techniques to
    identify and sample from all local minima basins. It's particularly effective
    for problems with many local minima and supports general nonlinear constraints.

    Notes
    -----
    - Deterministic algorithm (reproducible results without random seed)
    - Efficiently handles problems with many local optima
    - Supports bound, equality, and inequality constraints
    - May be slower than stochastic methods for high-dimensional problems
    - Initial guess `x0` is ignored; sampling points determined by algorithm

    Parameters
    ----------
    n : int, default=100
        Number of sampling points used in the algorithm.
    iters : int, default=1
        Number of iterations for algorithm convergence.
    sampling_method : str, default='simplicial'
        Sampling strategy: 'simplicial' (default) or 'sobol'.
    minimizer_kwargs : dict, optional
        Additional arguments passed to the local minimizer.
    `**kwargs`
        Additional arguments passed to `scipy.optimize.shgo`.
        See scipy documentation for complete options."""

    type: Literal["ScipyShgo"] = "ScipyShgo"


class XNES(_AskTellBase):
    """Exponential Natural Evolution Strategy (xNES). Adapts its covariance
    matrix to the local fitness landscape.

    Convenience wrapper around ``AskTellOptimizer(method="XNES")``; see
    :class:`AskTellOptimizer` for the full list of accepted kwargs.

    Examples
    --------
    >>> opt = iws.parameter_estimators.XNES()
    >>> fit = iws.DataFit(
    ...     objectives={"ocp": iws.objectives.OCPHalfCell(
    ...         electrode="positive", data_input="path/to/ocp.csv",
    ...     )},
    ...     parameters={"x": iws.Parameter("x", initial_value=1.0, bounds=(0.0, 2.0))},
    ...     optimizer=opt,
    ... )"""

    type: Literal["XNES"] = "XNES"
    algorithm_options: XNESOptions | None = Field(
        default=None, description="XNES-specific options (see XNESOptions)."
    )


#: Discriminated union of every concrete optimizer/sampler, keyed on ``type``.
#: ``PintsSampler`` is load-bearing — the engine resolves MCMC-sampling configs
#: via the ``optimizer`` field, so omitting it breaks them. The abstract bases
#: ``Optimizer``/``Sampler``/``ParameterEstimator`` are intentionally excluded.
OptimizerUnion = Annotated[
    DifferentialEvolution
    | CMAES
    | PSO
    | XNES
    | BayesianOptimization
    | SOBER
    | TuRBO
    | AskTellOptimizer
    | ScipyDifferentialEvolution
    | ScipyMinimize
    | ScipyLeastSquares
    | ScipyBasinhopping
    | ScipyDualAnnealing
    | ScipyShgo
    | GridSearch
    | PointEstimateOptimizer
    | PointEstimateSampler
    | DummyOptimizer
    | DummySampler
    | PintsSampler,
    Field(discriminator="type"),
]
