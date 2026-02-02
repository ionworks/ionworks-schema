"""Schemas for parameter_estimators."""

from typing import Any

from pydantic import Field

from ..base import BaseSchema


class CMAES(BaseSchema):
    """Schema for CMAES."""

    pass


class DummyOptimizer(BaseSchema):
    """Schema for Dummy."""

    pass


class DummySampler(BaseSchema):
    """Schema for Dummy."""

    pass


class GridSearch(BaseSchema):
    """Schema for GridSearch."""

    npts: Any = Field(default=10)

    def __init__(self, npts=10):
        super().__init__(npts=npts)


class Interactive(BaseSchema):
    """Schema for Interactive."""

    plot_function: Any | None = Field(default=None)

    def __init__(self, plot_function=None):
        super().__init__(plot_function=plot_function)


class Optimizer(BaseSchema):
    """Schema for Optimizer."""

    pass


class PDFO(BaseSchema):
    """Schema for PDFO."""

    pass


class PSO(BaseSchema):
    """Schema for PSO."""

    pass


class ParameterEstimator(BaseSchema):
    """Schema for ParameterEstimator."""

    pass


class PintsOptimizer(BaseSchema):
    """Schema for Pints."""

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
    """Schema for Pints."""

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
    """Schema for PointEstimate."""

    pass


class PointEstimateSampler(BaseSchema):
    """Schema for PointEstimate."""

    pass


class SNES(BaseSchema):
    """Schema for SNES."""

    pass


class Sampler(BaseSchema):
    """Schema for Sampler."""

    pass


class ScipyBasinhopping(BaseSchema):
    """Schema for ScipyBasinhopping."""

    pass


class ScipyDifferentialEvolution(BaseSchema):
    """Schema for ScipyDifferentialEvolution."""

    pass


class ScipyDualAnnealing(BaseSchema):
    """Schema for ScipyDualAnnealing."""

    pass


class ScipyLeastSquares(BaseSchema):
    """Schema for ScipyLeastSquares."""

    pass


class ScipyMinimize(BaseSchema):
    """Schema for ScipyMinimize."""

    pass


class ScipyShgo(BaseSchema):
    """Schema for ScipyShgo."""

    pass


class XNES(BaseSchema):
    """Schema for XNES."""

    pass
