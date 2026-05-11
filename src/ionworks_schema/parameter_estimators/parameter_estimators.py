"""Schemas for parameter_estimators."""

from typing import Any

from pydantic import ConfigDict, Field

from ..base import BaseSchema


class _AlgorithmOptions(BaseSchema):
    """Base class for AskTellOptimizer algorithm_options wrappers.

    Serializes to a plain option dict without the ``type`` discriminator
    (via ``_emit_type = False``), so the output matches what the pipeline
    algorithm classes expect from their ``options`` kwarg.
    """

    _emit_type: bool = False


class CMAESOptions(_AlgorithmOptions):
    """Options for ``AskTellOptimizer(method="CMAES")`` passed through to pycma.

    Accepts any key valid for ``cma.CMAOptions()`` — see
    `pycma documentation <https://github.com/CMA-ES/pycma>`_ for the full
    list. Common keys: ``CMA_diagonal``, ``ftarget``, ``CMA_stds``,
    ``scaling_of_variables``.
    """

    model_config = ConfigDict(extra="allow")


class XNESOptions(_AlgorithmOptions):
    """Options for ``AskTellOptimizer(method="XNES")``.

    XNES has no algorithm-specific options today — its search is fully
    parameterised by the top-level ``AskTellOptimizer`` fields (``sigma0``,
    ``population_size``, …). This class exists as a typed marker so the
    same ``algorithm_options=iws.XNESOptions(...)`` pattern works across
    methods, and ``extra="allow"`` keeps the door open for forward
    compatibility if pints exposes new XNES knobs later.
    """

    model_config = ConfigDict(extra="allow")


class PSOOptions(_AlgorithmOptions):
    """Options for ``AskTellOptimizer(method="PSO")``.

    Mirrors the runtime ``PSO`` optimizer's defaults; ``None`` fields fall
    back to those pipeline defaults.

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

    inertia_weight: Any | None = Field(
        default=None,
        description=(
            "Tuple ``(w_start, w_end)`` for linear inertia-weight decay "
            "across iterations. Setting this enables inertia mode and "
            "disables constriction. ``None`` uses the pipeline default."
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

    Mirrors the runtime ``DifferentialEvolution`` optimizer's defaults;
    ``None`` fields fall back to those pipeline defaults.

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
    dither: Any | None = Field(
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


class CMAES(BaseSchema):
    """Covariance Matrix Adaptation Evolution Strategy (CMA-ES). Effective for ill-conditioned and noisy non-linear problems.

    Convenience wrapper around ``AskTellOptimizer(method="CMAES")``.
    See `AskTellOptimizer` class for full parameter documentation.

    Examples
    --------
    >>> optimizer = iwp.optimizers.CMAES(max_iterations=500)
    >>> optimizer.set_objective(my_objective)
    >>> optimizer.set_bounds(([0, 0], [10, 10]))
    >>> result = optimizer.run(x0=[1, 1])"""

    pass


class DifferentialEvolution(BaseSchema):
    """Differential Evolution (DE) with SHADE adaptive control.

    Uses success-history based adaptive F/CR with current-to-pbest/1 mutation by default.
    Convenience wrapper around ``AskTellOptimizer(method="DifferentialEvolution")``.
    See `AskTellOptimizer` class for full parameter documentation."""

    pass


class DummyOptimizer(BaseSchema):
    """Alias for ``PointEstimateOptimizer``.

    Mirrors ``iwp.optimizers.DummyOptimizer``. Returns the supplied initial
    guess without running any optimisation — useful as a no-op in tests
    and pipeline scaffolding.
    """

    pass


class DummySampler(BaseSchema):
    """Alias for ``PointEstimateSampler``.

    Mirrors ``iwp.samplers.DummySampler``. Returns a single sample equal
    to the initial guess — useful as a no-op in sampling pipelines.
    """

    pass


class GridSearch(BaseSchema):
    """Grid search sampler.

    Mirrors ``iwp.samplers.GridSearch``. Evaluates the objective at all
    combinations of grid points across dimensions — a deterministic,
    exhaustive sweep. Cost grows as ``npts ** n_parameters``; keep the
    parameter count small.
    """

    npts: Any = Field(
        default=10,
        description=(
            "Number of evenly spaced points per dimension. Total evaluations "
            "are ``npts ** n_parameters``. Default 10."
        ),
    )

    def __init__(self, npts=10):
        super().__init__(npts=npts)


class Optimizer(BaseSchema):
    """Base class for all optimizers.

    Mirrors ``iwp.optimizers.Optimizer``. Optimisers seek a single optimal
    point in parameter space that minimises the objective. Not used
    directly — pick a concrete subclass such as ``AskTellOptimizer`` or
    one of the ``Scipy*`` wrappers.

    Parameters
    ----------
    `**kwargs`
        Arguments passed to the underlying optimiser algorithm.
    """

    pass


class PSO(BaseSchema):
    """Particle Swarm Optimization (PSO). Population-based optimizer inspired by bird flocking behavior.

    Convenience wrapper around ``AskTellOptimizer(method="PSO")``.
    See `AskTellOptimizer` class for full parameter documentation.

    Examples
    --------
    >>> optimizer = iwp.optimizers.PSO(max_iterations=500)
    >>> optimizer.set_objective(my_objective)
    >>> optimizer.set_bounds(([0, 0], [10, 10]))
    >>> result = optimizer.run(x0=[1, 1])"""

    pass


class ParameterEstimator(BaseSchema):
    """Base class for all parameter estimators.

    Mirrors ``iwp.data_fits.parameter_estimators.ParameterEstimator``.
    Parameter estimators find an optimal (or posterior) parameter set by
    minimising an objective. Not used directly — pick a concrete
    ``Optimizer`` or ``Sampler`` subclass.

    Parameters
    ----------
    `**kwargs`
        Arguments passed to the underlying estimation algorithm.
    """

    pass


class AskTellOptimizer(BaseSchema):
    """Ask/tell optimizer for population-based and simplex optimization.

    Supports CMAES, PSO, DifferentialEvolution, XNES, and Nelder-Mead.

    Parameters
    ----------
    method : str, optional
        Optimization method. Default is "CMAES". Must be one of:
        "CMAES", "Nelder-Mead", "PSO", "DifferentialEvolution", or "XNES".
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
    Parallelism is controlled via DataFit's `parallel` and `num_workers` parameters,
    not through the optimizer directly. DataFit will automatically configure the
    optimizer's parallelism settings based on its own configuration.

    The multiprocessing backend can be configured using package settings:

    - Standard multiprocessing (default): Optimized for local computations, no dependencies
    - Ray: Set `iwp.update_settings(use_ray_multiprocessing=True)` for distributed systems

    Examples
    --------
    >>> optimizer = iwp.optimizers.AskTellOptimizer(method="CMAES", max_iterations=500)
    >>> optimizer.set_objective(my_objective)
    >>> optimizer.set_bounds(([0, 0], [10, 10]))
    >>> result = optimizer.run(x0=[1, 1])

    Configuring PSO with inertia weight (exploration vs exploitation):

    >>> optimizer = iwp.optimizers.AskTellOptimizer(
    ...     method="PSO",
    ...     algorithm_options={
    ...         "inertia_weight": (0.9, 0.4),  # Linear decay from 0.9 to 0.4
    ...         "boundary_handling": "reflect",
    ...     }
    ... )

    Using PSO with constriction coefficient (alternative to inertia):

    >>> optimizer = iwp.optimizers.AskTellOptimizer(
    ...     method="PSO",
    ...     algorithm_options={
    ...         "constriction": True,
    ...         "c1": 2.05,
    ...         "c2": 2.05,
    ...     }
    ... )

    Using parallel evaluation with standard multiprocessing (default):

    >>> optimizer = iwp.optimizers.AskTellOptimizer(method="CMAES", parallel=True)
    >>> optimizer.set_objective(my_objective)
    >>> optimizer.set_bounds(([0, 0], [10, 10]))
    >>> result = optimizer.run(x0=[1, 1])

    Using Ray for distributed computation:

    >>> iwp.update_settings(use_ray_multiprocessing=True)
    >>> optimizer = iwp.optimizers.AskTellOptimizer(method="CMAES", parallel=True)
    >>> result = optimizer.run(x0=[1, 1])

    Or let DataFit control parallelism via num_workers:

    >>> optimizer = iwp.optimizers.AskTellOptimizer(method="CMAES")
    >>> datafit = iwp.DataFit(
    ...     objective, parameters=params, optimizer=optimizer, num_workers=4
    ... )
    >>> result = datafit.run(parameter_values)"""

    method: str = Field(
        default="CMAES",
        description=(
            "Optimisation method. One of ``'CMAES'``, ``'Nelder-Mead'``, "
            "``'PSO'``, ``'DifferentialEvolution'``, or ``'XNES'``. Default "
            "``'CMAES'``."
        ),
    )
    log_to_screen: bool = Field(
        default=False,
        description=(
            "If ``True``, print optimisation progress to stdout each "
            "generation. Default ``False``."
        ),
    )
    sigma0: float | int | list | tuple | None = Field(
        default=None,
        description=(
            "Initial step size for population-based methods. Scalar or "
            "per-dimension list/tuple. Defaults to ``0.3`` of the search "
            "range when left ``None``."
        ),
    )
    max_iterations: int = Field(
        default=300,
        description=("Maximum number of generations/iterations. Default 300."),
    )
    max_unchanged_iterations: int = Field(
        default=75,
        description=(
            "Stop after this many consecutive generations without objective "
            "improvement beyond ``absolute_tolerance`` / "
            "``relative_tolerance``. Default 75."
        ),
    )
    max_unchanged_iterations_threshold: float | int | None = Field(
        default=None,
        description=(
            "Legacy alias for ``absolute_tolerance``. Prefer "
            "``absolute_tolerance`` on new code."
        ),
    )
    min_iterations: int = Field(
        default=1,
        description=(
            "Minimum number of iterations before any stopping criterion is "
            "evaluated. Default 1."
        ),
    )
    max_evaluations: int = Field(
        default=1000000,
        description=(
            "Hard cap on total objective evaluations across all "
            "generations. Default 1e6."
        ),
    )
    population_size: int | None = Field(
        default=None,
        description=(
            "Population size for population-based methods. ``None`` uses the "
            "method-specific default (e.g. CMA-ES uses ``4 + floor(3 * "
            "log(n))``)."
        ),
    )
    threshold: float | int | None = Field(
        default=None,
        description=(
            "Target objective value — stop as soon as any evaluated point "
            "reaches this threshold. Default ``None`` (disabled)."
        ),
    )
    absolute_tolerance: float | int = Field(
        default=1e-05,
        description=(
            "Absolute improvement tolerance used with "
            "``max_unchanged_iterations``. Default 1e-5."
        ),
    )
    relative_tolerance: float | int = Field(
        default=0.01,
        description=(
            "Relative improvement tolerance used with "
            "``max_unchanged_iterations``. Default 0.01."
        ),
    )
    xtol: float | int | None = Field(
        default=1e-6,
        description=(
            "Parameter-change tolerance. Stops when the L-infinity norm of "
            "the change in the current best guess between generations drops "
            "below this value. Default 1e-6."
        ),
    )
    population_convergence_tol: float | int | None = Field(
        default=5e-3,
        description=(
            "Population-convergence tolerance. Exact semantics depend on the "
            "algorithm (e.g. DE also checks position-space diversity). "
            "Default 5e-3."
        ),
    )
    flat_fitness_tol: float | int | None = Field(
        default=None,
        description=(
            "Flat-fitness tolerance. Stops when at least half of the "
            "population have fitness within this tolerance of the median. "
            "Default ``None`` (disabled)."
        ),
    )
    convergence_patience: int = Field(
        default=3,
        description=(
            "Number of consecutive generations the population-convergence "
            "check must pass before the optimiser actually stops. Higher "
            "values guard against transient convergence signals. Default 3."
        ),
    )
    algorithm_options: (
        CMAESOptions | PSOOptions | DEOptions | XNESOptions | dict | None
    ) = Field(
        default=None,
        description=(
            "Algorithm-specific options. Use the typed wrappers "
            "``CMAESOptions``, ``PSOOptions``, ``DEOptions``, or "
            "``XNESOptions`` for field-level validation, or pass a raw "
            "``dict`` for forward compatibility. See each wrapper's "
            "docstring for supported keys."
        ),
    )
    async_mode: bool = Field(
        default=False,
        description=(
            "If ``True``, use the buffered ``ask_one``/``tell_one`` loop "
            "(one point at a time) instead of the synchronous "
            "``ask``/``tell`` pair. Default ``False``."
        ),
    )

    def __init__(
        self,
        method="CMAES",
        log_to_screen=False,
        sigma0=None,
        max_iterations=300,
        max_unchanged_iterations=75,
        max_unchanged_iterations_threshold=None,
        min_iterations=1,
        max_evaluations=1000000,
        population_size=None,
        threshold=None,
        absolute_tolerance=1e-05,
        relative_tolerance=0.01,
        xtol=1e-6,
        population_convergence_tol=5e-3,
        flat_fitness_tol=None,
        convergence_patience=3,
        algorithm_options=None,
        async_mode=False,
    ):
        super().__init__(
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
            algorithm_options=algorithm_options,
            async_mode=async_mode,
        )


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
    ):
        super().__init__(
            method=method,
            log_to_screen=log_to_screen,
            max_iterations=max_iterations,
            burnin_iterations=burnin_iterations,
            initial_phase_iterations=initial_phase_iterations,
        )


class PointEstimateOptimizer(BaseSchema):
    """No-op optimiser — returns the initial guess unchanged.

    Mirrors ``iwp.optimizers.PointEstimateOptimizer``. Useful for
    evaluating a single parameter set or initialising pipelines without
    paying the cost of a real optimiser run.
    """

    pass


class PointEstimateSampler(BaseSchema):
    """No-op sampler — returns the initial guess as a single sample.

    Mirrors ``iwp.samplers.PointEstimateSampler``. Useful for evaluating a
    single parameter set within a sampling-style pipeline without paying
    the cost of real MCMC.
    """

    pass


class Sampler(BaseSchema):
    """Base class for all Monte Carlo-style samplers.

    Mirrors ``iwp.samplers.Sampler``. Samplers explore parameter space to
    characterise the posterior, in contrast to optimisers which return a
    single best point. Not used directly — pick a concrete subclass such
    as ``PintsSampler`` or ``GridSearch``.

    Parameters
    ----------
    `**kwargs`
        Arguments passed to the underlying sampling algorithm.
    """

    pass


class ScipyBasinhopping(BaseSchema):
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
        See scipy documentation for complete options.

    Examples
    --------
    >>> # Basic usage with default L-BFGS-B local minimizer
    >>> optimizer = ScipyBasinhopping(niter=100, T=1.0, seed=42)
    >>> optimizer.set_objective(cost_function)
    >>> optimizer.set_bounds((lower, upper))
    >>> result = optimizer.run(x0)
    >>>
    >>> # Custom local minimizer with constraints
    >>> minimizer_kwargs = {
    ...     'method': 'SLSQP',
    ...     'constraints': {'type': 'eq', 'fun': lambda x: sum(x) - 1}
    ... }
    >>> optimizer = ScipyBasinhopping(
    ...     niter=200, minimizer_kwargs=minimizer_kwargs
    ... )
    >>> result = optimizer.run(x0)
    >>>
    >>> # Higher temperature for more exploration
    >>> optimizer = ScipyBasinhopping(niter=100, T=2.0, stepsize=1.0)
    >>> result = optimizer.run(x0)"""

    pass


class ScipyDifferentialEvolution(BaseSchema):
    """
    Global stochastic optimizer using differential evolution with parallel evaluation.

    Differential evolution is a robust global optimization algorithm that evolves a
    population of candidate solutions across generations. It excels at handling
    multi-modal, non-convex objective landscapes and requires no gradient information.

    Notes
    -----
    - Does not support custom equality or inequality constraints
    - Parallel workers significantly speed up optimization (use DataFits' `num_workers` arg)
    - Initial guess `x0` is ignored; initial population is generated from bounds
    - Polish option disabled by default as it conventionally significantly decreases performance
    - Callback logs only best solution per generation (not individual evaluations)

    Parameters
    ----------
    workers : int, default=1
        Number of parallel workers for function evaluations. Use -1 for all CPU cores.
    maxiter : int, default=1000
        Maximum number of generations.
    popsize : int, default=15
        Population size multiplier (total population = popsize * dimensionality).
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
    Basic usage (single worker for doctests):

    >>> optimizer = ScipyDifferentialEvolution(maxiter=50, seed=42)
    >>> optimizer.set_objective(sphere)
    >>> optimizer.set_bounds((lower, upper))
    >>> result = optimizer.run(x0)
    >>> result.fun < 1e-3
    True

    Integration with DataFit:

    >>> optimizer = ScipyDifferentialEvolution(maxiter=500)
    >>> isinstance(optimizer, ScipyDifferentialEvolution)
    True
    """

    pass


class ScipyDualAnnealing(BaseSchema):
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
    maxiter : int, default=1000
        Maximum number of global search iterations.
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
        See scipy documentation for complete options.

    Examples
    --------
    >>> # Basic usage with initial guess
    >>> optimizer = ScipyDualAnnealing(maxiter=500, seed=42)
    >>> optimizer.set_objective(cost_function)
    >>> optimizer.set_bounds((lower, upper))
    >>> result = optimizer.run(x0)
    >>>
    >>> # Pure simulated annealing (no local search)
    >>> optimizer = ScipyDualAnnealing(no_local_search=True, maxiter=2000)
    >>> result = optimizer.run(x0)"""

    pass


class ScipyLeastSquares(BaseSchema):
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
        See scipy documentation for complete options.

    Examples
    --------
    >>> optimizer = ScipyLeastSquares(method='trf', max_nfev=1000)
    >>> optimizer.set_objective(residual_function)
    >>> optimizer.set_bounds((lower, upper))
    >>> result = optimizer.run(x0)"""

    pass


class ScipyMinimize(BaseSchema):
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
    maxiter : int, optional
        Maximum number of iterations.
    tol : float, optional
        Tolerance for termination.
    `**kwargs`
        Additional arguments passed to `scipy.optimize.minimize`.
        See scipy documentation for complete options.

    Examples
    --------
    >>> optimizer = ScipyMinimize(method='SLSQP', maxiter=1000)
    >>> optimizer.set_objective(cost_function)
    >>> optimizer.set_bounds((lower, upper))
    >>> optimizer.set_eq_constraints([lambda x: sum(x) - 1])
    >>> result = optimizer.run(x0)"""

    pass


class ScipyShgo(BaseSchema):
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
        See scipy documentation for complete options.

    Examples
    --------
    >>> optimizer = ScipyShgo(n=200, iters=3)
    >>> optimizer.set_objective(cost_function)
    >>> optimizer.set_bounds((lower, upper))
    >>> optimizer.set_ineq_constraints([lambda x: x[0] + x[1] - 1])
    >>> result = optimizer.run(x0)  # x0 is ignored"""

    pass


class XNES(BaseSchema):
    """Exponential Natural Evolution Strategy (xNES). Adapts covariance matrix to the local fitness landscape.

    Convenience wrapper around ``AskTellOptimizer(method="XNES")``.
    See `AskTellOptimizer` class for full parameter documentation.

    Examples
    --------
    >>> optimizer = iwp.optimizers.XNES(max_iterations=500)
    >>> optimizer.set_objective(my_objective)
    >>> optimizer.set_bounds(([0, 0], [10, 10]))
    >>> result = optimizer.run(x0=[1, 1])"""

    pass
