"""Schemas for parameter_estimators."""

from typing import Any

from pydantic import Field

from ..base import BaseSchema


class CMAES(BaseSchema):
    """Covariance Matrix Adaptation Evolution Strategy (CMA-ES). Effective for ill-conditioned and noisy non-linear problems.

    Convenience wrapper around ``Pints(method="CMAES")``.
    See `Pints` class for full parameter documentation.

    Examples
    --------
    >>> optimizer = iwp.optimizers.CMAES(max_iterations=500)
    >>> optimizer.set_objective(my_objective)
    >>> optimizer.set_bounds(([0, 0], [10, 10]))
    >>> result = optimizer.run(x0=[1, 1])"""

    pass


class DummyOptimizer(BaseSchema):
    """Alias for PointEstimate optimizer."""

    pass


class DummySampler(BaseSchema):
    """Alias for PointEstimate sampler."""

    pass


class GridSearch(BaseSchema):
    """Grid search sampler - explores parameter space on a regular grid.

    Evaluates the objective at all combinations of grid points across dimensions.

    Parameters
    ----------
    npts : int, optional
        Number of points to use in each dimension. Default is 10."""

    npts: Any = Field(default=10)

    def __init__(self, npts=10):
        super().__init__(npts=npts)


class Interactive(BaseSchema):
    """Interactive GUI optimizer for exploring the objective function in Jupyter notebooks.

    Creates sliders for each parameter and a submit button to return the current values.

    Parameters
    ----------
    plot_function : callable, optional
        Function that takes a data_fit object and parameter vector x, and plots
        the data and model output. If not provided, a default function is used.
    _testing : bool, optional
        Whether the optimizer is being used for testing. Default is False."""

    plot_function: Any | None = Field(default=None)

    def __init__(self, plot_function=None):
        super().__init__(plot_function=plot_function)


class Optimizer(BaseSchema):
    """Base class for all optimizers.

    Optimizers seek a single optimal point in parameter space that minimizes
    the objective function.

    Parameters
    ----------
    `**kwargs`
        Arguments passed to the underlying optimizer algorithm."""

    pass


class PDFO(BaseSchema):
    """Optimizer using PDFO: Powell's Derivative-Free Optimization solvers.

    Parameters
    ----------
    `**kwargs`
        Arguments passed to pdfo.
        See `pdfo documentation <https://github.com/pdfo/pdfo>`_ for details."""

    pass


class PSO(BaseSchema):
    """Particle Swarm Optimization (PSO). Population-based optimizer inspired by bird flocking behavior.

    Convenience wrapper around ``Pints(method="PSO")``.
    See `Pints` class for full parameter documentation.

    Examples
    --------
    >>> optimizer = iwp.optimizers.PSO(max_iterations=500)
    >>> optimizer.set_objective(my_objective)
    >>> optimizer.set_bounds(([0, 0], [10, 10]))
    >>> result = optimizer.run(x0=[1, 1])"""

    pass


class ParameterEstimator(BaseSchema):
    """Base class for all parameter estimators. Parameter estimators find an optimal set
    of parameters by minimizing an objective function.

    Subclasses should override:
    - `run()`: Execute the estimation algorithm
    - Class attributes for capabilities (scalar_output, probabilistic, etc.)

    Parameters
    ----------
    `**kwargs`
        Arguments passed to the underlying estimation algorithm."""

    pass


class PintsOptimizer(BaseSchema):
    """Optimizer using the Pints library: Probabilistic Inference on Noisy Time-Series.

    Wraps Pints optimizers. Supports CMAES, PSO, XNES, SNES, and Nelder-Mead.

    Parameters
    ----------
    method : str, optional
        Optimization method. Default is "CMAES". Must be one of:
        "CMAES", "Nelder-Mead", "PSO", "XNES", or "SNES".
    log_to_screen : bool, optional
        Whether to print optimization progress. Default is False.
    sigma0 : float | np.ndarray, optional
        Initial step size for population-based methods. Default is None.
    max_iterations : int, optional
        Maximum number of iterations. Default is 300.
    max_unchanged_iterations : int, optional
        Stop after this many iterations without improvement. Default is 75.
    max_unchanged_iterations_threshold : float, optional
        Threshold for determining improvement. Default is 1e-5.
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
    use_f_guessed : bool, optional
        Track f_guessed instead of f_best. Default is False.
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
        Additional arguments for the Pints optimizer constructor.

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
    >>> optimizer = iwp.optimizers.Pints(method="CMAES", max_iterations=500)
    >>> optimizer.set_objective(my_objective)
    >>> optimizer.set_bounds(([0, 0], [10, 10]))
    >>> result = optimizer.run(x0=[1, 1])

    Configuring PSO with inertia weight (exploration vs exploitation):

    >>> optimizer = iwp.optimizers.Pints(
    ...     method="PSO",
    ...     algorithm_options={
    ...         "inertia_weight": (0.9, 0.4),  # Linear decay from 0.9 to 0.4
    ...         "boundary_handling": "reflect",
    ...     }
    ... )

    Using PSO with constriction coefficient (alternative to inertia):

    >>> optimizer = iwp.optimizers.Pints(
    ...     method="PSO",
    ...     algorithm_options={
    ...         "constriction": True,
    ...         "c1": 2.05,
    ...         "c2": 2.05,
    ...     }
    ... )

    Using parallel evaluation with standard multiprocessing (default):

    >>> optimizer = iwp.optimizers.Pints(method="CMAES", parallel=True)
    >>> optimizer.set_objective(my_objective)
    >>> optimizer.set_bounds(([0, 0], [10, 10]))
    >>> result = optimizer.run(x0=[1, 1])

    Using Ray for distributed computation:

    >>> iwp.update_settings(use_ray_multiprocessing=True)
    >>> optimizer = iwp.optimizers.Pints(method="CMAES", parallel=True)
    >>> result = optimizer.run(x0=[1, 1])

    Or let DataFit control parallelism via num_workers:

    >>> optimizer = iwp.optimizers.Pints(method="CMAES")
    >>> datafit = iwp.DataFit(
    ...     objective, parameters=params, optimizer=optimizer, num_workers=4
    ... )
    >>> result = datafit.run(parameter_values)"""

    method: Any = Field(default="CMAES")
    log_to_screen: Any = Field(default=False)
    sigma0: Any | None = Field(default=None)
    max_iterations: Any = Field(default=300)
    max_unchanged_iterations: Any = Field(default=75)
    max_unchanged_iterations_threshold: Any | None = Field(default=None)
    min_iterations: Any = Field(default=1)
    max_evaluations: Any = Field(default=1000000)
    population_size: Any | None = Field(default=None)
    threshold: Any | None = Field(default=None)
    absolute_tolerance: Any = Field(default=1e-05)
    relative_tolerance: Any = Field(default=0.01)
    use_f_guessed: Any = Field(default=False)
    algorithm_options: Any | None = Field(default=None)

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
        use_f_guessed=False,
        algorithm_options=None,
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
            use_f_guessed=use_f_guessed,
            algorithm_options=algorithm_options,
        )


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

    method: Any = Field(default="DramACMC")
    log_to_screen: Any = Field(default=False)
    max_iterations: Any = Field(default=1000)
    burnin_iterations: Any | None = Field(default=None)
    initial_phase_iterations: Any | None = Field(default=None)

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
    """Point estimate optimizer - returns the initial guess without optimization.

    Useful for evaluating a single parameter set or initializing pipelines."""

    pass


class PointEstimateSampler(BaseSchema):
    """Point estimate sampler - returns the initial guess as a single sample.

    Useful for evaluating a single parameter set within a sampling framework."""

    pass


class SNES(BaseSchema):
    """Separable Natural Evolution Strategy (sNES). Efficient for high-dimensional problems using diagonal covariance.

    Convenience wrapper around ``Pints(method="SNES")``.
    See `Pints` class for full parameter documentation.

    Examples
    --------
    >>> optimizer = iwp.optimizers.SNES(max_iterations=500)
    >>> optimizer.set_objective(my_objective)
    >>> optimizer.set_bounds(([0, 0], [10, 10]))
    >>> result = optimizer.run(x0=[1, 1])"""

    pass


class Sampler(BaseSchema):
    """Base class for all monte-carlo style samplers.

    Samplers explore the parameter space to identify posterior distributions,
    whereas optimizers provide a point-based solution.

    Parameters
    ----------
    `**kwargs`
        Arguments passed to the underlying sampling algorithm."""

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
    """Global stochastic optimizer using differential evolution with parallel evaluation.

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
    >>> # Basic usage with parallel evaluation
    >>> optimizer = ScipyDifferentialEvolution(workers=-1, maxiter=500)
    >>> optimizer.set_objective(cost_function)
    >>> optimizer.set_bounds((lower, upper))
    >>> result = optimizer.run(x0)  # x0 is ignored
    >>>
    >>> # With callback for progress monitoring
    >>> def log_progress(x_list, cost_list):
    ...     print(f"Best cost: {cost_list[0]:.6f}")
    >>> optimizer.set_evaluation_callback(log_progress)
    >>> result = optimizer.run(x0)"""

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

    Convenience wrapper around ``Pints(method="XNES")``.
    See `Pints` class for full parameter documentation.

    Examples
    --------
    >>> optimizer = iwp.optimizers.XNES(max_iterations=500)
    >>> optimizer.set_objective(my_objective)
    >>> optimizer.set_bounds(([0, 0], [10, 10]))
    >>> result = optimizer.run(x0=[1, 1])"""

    pass
