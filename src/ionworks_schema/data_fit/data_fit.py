"""Schemas for data_fit."""

from typing import Any

from pydantic import Field, model_validator

from ..base import BaseSchema


class ArrayDataFit(BaseSchema):
    """A pipeline element that fits a model to data for multiple independent variable
    values. The data for each independent variable value is fitted separately.
    The independent variable values should be given as the keys of the `objectives`
    dictionary. The value of each key should be a :class:`ionworkspipeline.data_fits.objectives.BaseObjective`
    object. This objective will be used to fit the data for the corresponding
    independent variable value.

    The user-supplied objectives should assign the independent variable value to the
    `custom_parameters` attribute of the objective as appropriate. This class simply
    calls a separate :class:`ionworkspipeline.DataFit` for each provided objective. It does not
    pass the independent variable value to the objective, so the user must ensure that
    the objective is set up to use the independent variable value correctly.

    For example, this can be used to fit a model to data at multiple temperatures, or
    fit each pulse of a GITT experiment separately, with post-processing to extract
    functional relationships between parameters and the independent variable.

    The rest of the parameters are the same as for :class:`ionworkspipeline.DataFit`."""

    objectives: Any = Field(...)

    def __init__(self, objectives):
        super().__init__(objectives=objectives)


class DataFit(BaseSchema):
    """A pipeline element that fits a model to data.

    The DataFit class sets up an objective function structure upon
    initialization, enabling analysis methods (e.g., sensitivity_analysis, compute_hessian)
    to be used standalone. Call `setup(parameter_values)` to configure for analysis without
    running optimization, or `run(parameter_values)` to execute the full optimization workflow.

    Parameters
    ----------
    objectives : :class:`ionworkspipeline.data_fits.objectives.BaseObjective` or dict[str, :class:`ionworkspipeline.data_fits.objectives.BaseObjective`]
        The objective(s) to use for the fit. This can be a single objective, or a
        dictionary of objectives.
        Each objective can be any class that implements the method `build`, which
        creates a function :meth:`Objective.run` that
        takes a dictionary of parameters and returns a scalar or vector cost.
        In general, we subclass :class:`ionworkspipeline.data_fits.objectives.BaseObjective` to
        implement a particular objective.
    source : str
        A string describing the source of the data.
    parameters : dict, optional
        A dictionary of parameters to fit. The values can be:
            - an `iwp.Parameter` object, e.g. `iwp.Parameter("x")`
            - a pybamm expression, in which case the other parameters should also be
              explicitly provided as `iwp.Parameter` objects, e.g.

              {

              "param": 2 * pybamm.Parameter("half-param"),

              "half-param": iwp.Parameter("half-param")

              }

              works, but

              {"param": 2 * iwp.Parameter("half-param")}
              would not work.
            - a function, containing other parameters, in which case the other
              parameters should again also be explicitly provided as `iwp.Parameter` objects, e.g.

              {

                "main parameter": lambda x: pybamm.Parameter("other parameter") * x**2,

                "other parameter": iwp.Parameter("other parameter")

              }

        The name of the input parameter does not need to match the name of the
        parameter. In all cases, the `DataFit` class will automatically process this
        input to fit for "x".
    cost : :class:`ionworkspipeline.costs.ObjectiveFunction`, optional
        The cost function to use when constructing the objective.
        If None, uses the optimizer's default cost function.
    initial_guesses : dict or list of dicts, optional
        Initial guesses for the parameters. If a single dictionary, then this is used
        as the initial guess for all optimization jobs in each batch. If a list of dictionaries,
        then each dictionary is used as the initial guess for a single job.
    optimizer : :class:`ionworkspipeline.optimizers.Optimizer` or :class:`ionworkspipeline.samplers.Sampler`, optional
        The optimizer to use for the fit. Default is set by the DataFit subclasses.
    cost_logger : :class:`ionworkspipeline.CostLogger`, optional
        A cost logger to use for logging the cost and parameters during the fit.
        Default is :class:`iwp.CostLogger` with default options.
    multistarts : int, optional
        Number of times to run the optimization from different initial guesses.
        If None, only runs once from the provided initial guess.
    num_workers : int, optional
        Number of worker processes to use for parallel processing. Not supported on Windows.
        When multiple optimization jobs are defined (e.g., via `multistarts` or multiple
        `initial_guesses`), they are distributed across `num_workers` processes for
        batch-level parallelism.

        If num_workers = 1, batch-level parallelism is disabled.
        If num_workers = None, defaults to the number of CPU cores.
    parallel : bool, optional
        Controls optimizer-level parallelism (parallel evaluation of the objective function
        within a single optimization job). When True, enables parallel evaluation for
        compatible optimizers (e.g., Pints population-based optimizers), using `num_workers`
        processes. Requires ray to be installed for Pints optimizers.

        If None (default), automatically enables optimizer-level parallelism when:
        - Only one optimization job is running (no multistarts/single initial guess)
        - num_workers > 1
        - The optimizer supports parallelism

        Set to False to explicitly disable optimizer-level parallelism.
        Set to True to explicitly enable it (will warn if incompatible with batch-level parallelism).
    max_batch_size : int, optional
        Maximum number of optimization jobs to include in a single batch.
        If None, defaults to the largest possible batch size, which is the
        ceiling of the total number of jobs divided by the number of workers.
    initial_guess_sampler : :class:`ionworkspipeline.data_fits.distribution_samplers.DistributionSampler`, optional
        Sampler to use for generating initial guesses of multistarted parameter estimations.
        Default is :class:`ionworkspipeline.data_fits.distribution_samplers.LatinHypercube`.
    priors : :class:`ionworkspipeline.priors.Prior` or list[:class:`ionworkspipeline.priors.Prior`], optional
        Priors to use for the fit.
    options : dict, optional
        A dictionary of options to pass to the data fit. By default:

        .. code-block:: python

            options = {
                # Random seed for reproducibility. Defaults to a random seed generated
                # determined by the current time.
                "seed": iwutil.random.generate_seed(),
                # Whether to reduce the size of the log. If True, only append logs if the
                # cost is at least 0.1% better than the best cost so far. Defaults
                # to True if the optimizer is deterministic.
                "low_memory": True,
                # The distributed backend to use for parallel processing. Options are:
                # - "joblib": Uses joblib for parallel processing (default on non-Windows)
                # - "single_process": Runs everything in a single process (default on Windows)
                # - "ray": Uses Ray for distributed processing (requires ray to be installed)
                "distributed_backend": None,
                # Maximum number of iterations for each job.
                "maxiters": None,
                # Maximum time in seconds for each job. If multistarts are enabled, the total
                # time may exceed this value since many jobs are evaluated.
                "maxtime": None,
            }

        Note: These options only have an effect if model.convert_to_format == 'casadi'"""

    objectives: Any = Field(...)
    source: Any = Field(default="")
    parameters: Any | None = Field(default=None)
    cost: Any | None = Field(default=None)
    initial_guesses: Any | None = Field(default=None)
    optimizer: Any | None = Field(default=None)
    cost_logger: Any | None = Field(default=None)
    multistarts: Any | None = Field(default=None)
    num_workers: Any | None = Field(default=None)
    parallel: Any | None = Field(default=None)
    max_batch_size: Any | None = Field(default=None)
    initial_guess_sampler: Any | None = Field(default=None)
    priors: Any | None = Field(default=None)
    options: Any | None = Field(default=None)

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
    def validate_parameters_or_priors(self):
        """Validate that either parameters or priors is specified."""
        parameters = self.parameters
        priors = self.priors
        if not parameters and not priors:
            raise ValueError("Either 'parameters' or 'priors' must be specified")
        if parameters and priors:
            raise ValueError("Only one of 'parameters' or 'priors' can be specified")
        return self
