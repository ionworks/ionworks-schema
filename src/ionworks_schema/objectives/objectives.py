"""Schemas for objectives."""

from typing import Any

from pydantic import Field

from ..base import BaseSchema


class BaseObjective(BaseSchema):
    """A pipeline element that constructs an objective function for either fitting or
    design optimization.

    Parameters
    ----------
    options : dict, optional
        A dictionary of options to pass to the data fit.
    callbacks : :class:`ionworkspipeline.callbacks.Callback` or list of callbacks
        A class with methods that get called at various points during the data fit
        process
    custom_parameters : dict of str: float or callable, optional
        A dictionary of parameters to use within this objective only. Values in
        this dictionary will override any values for the simulation within this
        objective but will not be passed on as results of the `DataFit` object.
        If a callable is provided, it must take the form of a function that takes in
        a dictionary of parameters and the `data_input` "data" dictionary and returns
        the value of the parameter (which can be a float or function, as in PyBaMM).
    cost : :class:`ionworkspipeline.costs.ObjectiveFunction` or str, optional
        The cost function to use for the objective. If not provided, the default cost
        function will be used.
    constraints : list[Constraint], optional
        A list of equality and inequality constraints to apply to the objective.
    penalties : list[Penalty], optional
        A list of penalties to apply to the objective.
    parameters : dict or :class:`pybamm.ParameterValues`, optional
        Objective-specific parameter values merged into the global parameter values
        before fitting. Unlike ``custom_parameters``, these are static values rather
        than callables. Default is None."""

    options: Any | None = Field(default=None)
    callbacks: Any | None = Field(default=None)
    custom_parameters: Any | None = Field(default=None)
    cost: Any | None = Field(default=None)
    constraints: Any | None = Field(default=None)
    penalties: Any | None = Field(default=None)
    parameters: Any | None = Field(default=None)

    def __init__(
        self,
        data_input=None,
        options=None,
        callbacks=None,
        custom_parameters=None,
        cost=None,
        constraints=None,
        penalties=None,
        parameters=None,
    ):
        super().__init__(
            data_input=data_input,
            options=options,
            callbacks=callbacks,
            custom_parameters=custom_parameters,
            cost=cost,
            constraints=constraints,
            penalties=penalties,
            parameters=parameters,
        )


class FittingObjective(BaseObjective):
    """A pipeline element that constructs an objective function used to fit a model to
    data.

    Parameters
    ----------
    data_input : str or dict
        The data to use for the fit. Can be a string giving the path to the data, or a
        dictionary with keys "data" and "metadata". "data" should be a DataFrame that
        supplies the raw data, and "metadata" should be a dictionary that supplies
        metadata about the data.
    options : dict, optional
        A dictionary of options to pass to the data fit.
    callbacks : :class:`ionworkspipeline.callbacks.Callback` or list of callbacks
        A class with methods that get called at various points during the datafit
        process
    custom_parameters : dict of str: float or callable, optional
        A dictionary of parameters to use within this objective only. Values in
        this dictionary will override any values for the simulation within this
        objective but will not be passed on as results of the `DataFit` object.
        If a callable is provided, it must take the form of a function that takes in
        a dictionary of parameters and the `data_input` "data" dictionary and returns
        the value of the parameter (which can be a float or function, as in PyBaMM).
    cost : :class:`ionworkspipeline.costs.ObjectiveFunction` or str, optional
        The cost function to use for the objective. If not provided, the default cost
        function will be used.
    constraints : list[Constraint], optional
        A list of equality and inequality constraints to apply to the objective.
    penalties : list[Penalty], optional
        A list of penalties to apply to the objective.
    parameters : dict or :class:`pybamm.ParameterValues`, optional
        Objective-specific parameter values merged into the global parameter values
        before fitting. Unlike ``custom_parameters``, these are static values rather
        than callables. Default is None."""

    data_input: Any = Field(...)
    options: Any | None = Field(default=None)
    callbacks: Any | None = Field(default=None)
    custom_parameters: Any | None = Field(default=None)
    cost: Any | None = Field(default=None)
    constraints: Any | None = Field(default=None)
    penalties: Any | None = Field(default=None)
    parameters: Any | None = Field(default=None)

    def __init__(
        self,
        data_input,
        options=None,
        callbacks=None,
        custom_parameters=None,
        cost=None,
        constraints=None,
        penalties=None,
        parameters=None,
    ):
        # Pass data_input through so Pydantic receives it for validation (schema only; pipeline BaseObjective does not take it)
        super().__init__(
            data_input=data_input,
            options=options,
            callbacks=callbacks,
            custom_parameters=custom_parameters,
            cost=cost,
            constraints=constraints,
            penalties=penalties,
            parameters=parameters,
        )


class SimulationObjective(FittingObjective):
    """A pipeline element that constructs an objective function used to fit a model to
    data. SimulationObjective is a subclass of FittingObjective intended for use with
    objectives that run a pybamm simulation.

    Parameters
    ----------
    data_input : str or dict
        The data to use for the fit. Can be a string giving the path to the data, or a
        dictionary with keys "data" and "metadata". "data" should be a DataFrame that
        supplies the raw data, and "metadata" should be a dictionary that supplies
        metadata about the data.
    options : dict, optional
        A dictionary of options to pass to the data fit.
    callbacks : :class:`ionworkspipeline.callbacks.Callback` or list of callbacks
        A class with methods that get called at various points during the datafit
        process
    custom_parameters : dict of str: float or callable, optional
        A dictionary of parameters to use within this objective only. Values in
        this dictionary will override any values for the simulation within this
        objective but will not be passed on as results of the `DataFit` object.
        If a callable is provided, it must take the form of a function that takes in
        a dictionary of parameters and the `data_input` "data" dictionary and returns
        the value of the parameter (which can be a float or function, as in PyBaMM).
    constraints : list[Constraint], optional
        A list of equality and inequality constraints to apply to the objective.
    penalties : list[Penalty], optional
        A list of penalties to apply to the objective."""

    pass


class CalendarAgeing(SimulationObjective):
    """Objective for fitting LLI and/or LAM to calendar ageing data for a full cell.

    Parameters
    ----------
    data_input : str or dict
        The data to use for the fit, see :class:`FittingObjective`.
    options : dict, optional
        A dictionary of options to pass to the objective.

            * model: :class:``pybamm.BaseModel``
                The model to fit. No default is provided, but this option is required
                (a model must be passed in).
            * modes: list of str
                The degradation modes to fit. Can be any combination of "LLI [%]",
                "LAM_ne [%]", "LAM_pe [%]". Default is ["LLI [%]"].
            * simulation_kwargs: dict
                Keyword arguments to pass to the simulation (:class:`iwp.Simulation`). Default is None.
    callbacks : list of callable, optional
        A class with methods that get called at various points during the datafit
        process
    custom_parameters : dict, optional
        A dictionary of parameters to use within this objective only.
        See :class:`FittingObjective`.
    constraints : list[Constraint], optional
        A list of equality and inequality constraints to apply to the objective.
    penalties : list[Penalty], optional
        A list of penalties to apply to the objective.
    parameters : dict or :class:`pybamm.ParameterValues`, optional
        Objective-specific parameter values merged into the global parameter values
        before fitting. Unlike ``custom_parameters``, these are static values rather
        than callables. Default is None.
    """

    data_input: Any = Field(...)
    options: Any | None = Field(default=None)
    callbacks: Any | None = Field(default=None)
    custom_parameters: Any | None = Field(default=None)
    constraints: Any | None = Field(default=None)
    penalties: Any | None = Field(default=None)
    parameters: Any | None = Field(default=None)

    def __init__(
        self,
        data_input,
        options=None,
        callbacks=None,
        custom_parameters=None,
        constraints=None,
        penalties=None,
        parameters=None,
    ):
        super().__init__(
            data_input=data_input,
            options=options,
            callbacks=callbacks,
            custom_parameters=custom_parameters,
            constraints=constraints,
            penalties=penalties,
            parameters=parameters,
        )


class CurrentDriven(SimulationObjective):
    """Objective for generic current-driven experiment.

    Parameters
    ----------
    data_input : str or dict
        The data to use for the fit, see :class:`FittingObjective`.
    options : dict, optional
        A dictionary of options to pass to the objective.

            * model: :class:``pybamm.BaseModel``
                The model to fit. No default is provided, but this option is required
                (a model must be passed in).
            * independent variable: string
                Whether to use voltage or time as the independent variable. Default is
                "time". In some cases, it may be more appropriate to use voltage as the
                independent variable, and the objective variables will be interpolated
                to match the voltage data.
            * simulation_kwargs: dict
                Keyword arguments to pass to the simulation (:class:`iwp.Simulation`).
                If no experiment is provided, the default is
                {"output_variables": ["Voltage [V]", "Current [A]"]}. Otherwise,
                the default is None.
            * objective variables: list of strings
                The variables to fit to. If independent variable is "time", this
                defaults to ["Voltage [V]"] and can be a list of any variables except
                "Time [s]". If independent variable is "voltage", this defaults to
                ["Time [s]"] and cannot be changed.
            * interpolant_atol: float
                Absolute tolerance for the current interpolant. Default is the solver `atol`
                if a solver is provided in `simulation_kwargs`, otherwise 1e-6.
            * interpolant_rtol: float
                Relative tolerance for the current interpolant. Default is the solver `rtol`
                if a solver is provided in `simulation_kwargs`, otherwise 1e-4.
            * interactive_preprocessing: bool
                Whether to use interactive preprocessing to adjust `interpolant_atol` and
                `interpolant_rtol` based on the current data. Default is False.
            * solver_max_save_points: int, optional
                Maximum number of points to save in the solver. Disabled by default.
    callbacks : list of callable, optional
        A class with methods that get called at various points during the datafit
        process
    custom_parameters : dict, optional
        A dictionary of parameters to use within this objective only.

        The following custom parameters are available:

        * Initial temperature [K]: Function to calculate the initial temperature.
          Default is `iwp.data_fits.custom_parameters.initial_temperature`.
        * Ambient temperature [K]: Function to calculate the ambient temperature.
          Default is `iwp.data_fits.custom_parameters.initial_temperature`.
        * Initial concentration in negative electrode [mol.m-3]: Function to calculate
          the initial concentration in the negative electrode for full cells.
          Default is `iwp.data_fits.custom_parameters.initial_concentration_from_parameter_values("full", "negative")`.
        * Initial concentration in positive electrode [mol.m-3]: Function to calculate
          the initial concentration in the positive electrode for full cells.
          Default is `iwp.data_fits.custom_parameters.initial_concentration_from_parameter_values("full", "positive")`.
        * Initial concentration in {working_electrode} electrode [mol.m-3]: Function to calculate
          the initial concentration in the working electrode for half cells.
          Default is `iwp.data_fits.custom_parameters.initial_concentration_from_parameter_values("half", {working_electrode})`.

        These custom parameters are functions that take `parameter_values` and `data` as arguments
        and return the calculated value. They can be overridden by providing new functions in the
        `custom_parameters` dictionary.
        See :class:`FittingObjective`.
    constraints : list[Constraint], optional
        A list of equality and inequality constraints to apply to the objective.
    penalties : list[Penalty], optional
        A list of penalties to apply to the objective.
    parameters : dict or :class:`pybamm.ParameterValues`, optional
        Objective-specific parameter values merged into the global parameter values
        before fitting. Unlike ``custom_parameters``, these are static values rather
        than callables. Default is None.
    """

    data_input: Any = Field(...)
    options: Any | None = Field(default=None)
    callbacks: Any | None = Field(default=None)
    custom_parameters: Any | None = Field(default=None)
    constraints: Any | None = Field(default=None)
    penalties: Any | None = Field(default=None)
    parameters: Any | None = Field(default=None)

    def __init__(
        self,
        data_input,
        options=None,
        callbacks=None,
        custom_parameters=None,
        constraints=None,
        penalties=None,
        parameters=None,
    ):
        super().__init__(
            data_input=data_input,
            options=options,
            callbacks=callbacks,
            custom_parameters=custom_parameters,
            constraints=constraints,
            penalties=penalties,
            parameters=parameters,
        )


class CycleAgeing(SimulationObjective):
    """Objective for fitting summary variables to cycling data.

    Parameters
    ----------
    data_input : str or dict
        The data to use for the fit, see :class:`FittingObjective`.
    options : dict, optional
        A dictionary of options to pass to the objective.

            * model: :class:``pybamm.BaseModel``
                The model to fit. No default is provided, but this option is required
                (a model must be passed in).
            * experiment: :class:`pybamm.Experiment`
                The experiment to use for the simulation. No default is provided, but
                this option is required (an experiment must be passed in).
            * objective variables: list of strings
                The variables to fit. No default is provided, but this option is
                required (a list of variables must be passed in). The variables must
                be a subset of the keys in the data.
            * metrics: dict of str to BaseMetric
                A dictionary mapping variable names to metric objects that extract
                values from the simulation solution. Each metric should be created
                with ``.by_cycle()`` to evaluate across cycles. The cycles will be
                set automatically from the data. Default metrics are provided for
                "LLI [%]", "LAM_ne [%]", and "LAM_pe [%]".
            * simulation_kwargs: dict
                Keyword arguments to pass to the simulation (:class:`iwp.Simulation`).
                Default is None.
    callbacks : list of callable, optional
        A class with methods that get called at various points during the datafit
        process
    custom_parameters : dict, optional
        A dictionary of parameters to use within this objective only.
        See :class:`FittingObjective`.
    constraints : list[Constraint], optional
        A list of equality and inequality constraints to apply to the objective.
    penalties : list[Penalty], optional
        A list of penalties to apply to the objective.
    parameters : dict or :class:`pybamm.ParameterValues`, optional
        Objective-specific parameter values merged into the global parameter values
        before fitting. Unlike ``custom_parameters``, these are static values rather
        than callables. Default is None.
    """

    data_input: Any = Field(...)
    options: Any | None = Field(default=None)
    callbacks: Any | None = Field(default=None)
    custom_parameters: Any | None = Field(default=None)
    constraints: Any | None = Field(default=None)
    penalties: Any | None = Field(default=None)
    parameters: Any | None = Field(default=None)

    def __init__(
        self,
        data_input,
        options=None,
        callbacks=None,
        custom_parameters=None,
        constraints=None,
        penalties=None,
        parameters=None,
    ):
        super().__init__(
            data_input=data_input,
            options=options,
            callbacks=callbacks,
            custom_parameters=custom_parameters,
            constraints=constraints,
            penalties=penalties,
            parameters=parameters,
        )


class DesignObjective(BaseObjective):
    """A pipeline element that constructs a design objective class.

    This class implements a robust failure handling system specifically designed
    for design optimization scenarios. It employs a three-tier penalty hierarchy
    to maintain optimization stability while guiding algorithms away from
    problematic parameter regions:

    Failure Handling Hierarchy
    ---------------------------
    1. **Crossing Detection Fallback** (10x penalty):
       When exact SOC/voltage crossings cannot be found, uses closest match
       with penalty multiplication to discourage these approximate solutions.

    2. **Progressive Penalty Escalation** (1.1x incremental):
       Each subsequent fallback usage increases penalty factors by 10%,
       creating adaptive cost gradients that steer optimization away from
       repeatedly problematic parameter regions.

    3. **Simulation Failure Penalty** (1e6 value):
       Complete solver failures receive maximum penalty values, creating
       strong barriers around parameter combinations that cause crashes
       or numerical instabilities.

    Parameters
    ----------
    actions : dict[str, Any]
        A dictionary of `Action` wrapped `Metrics` to use for this objective and its parameters.
    constraints : dict[str, BaseAction], optional
        A dictionary of equality and inequality constraints to apply to the objective.
    options : dict, optional
        A dictionary of options to pass to the data fit.

    callbacks : :class:`ionworkspipeline.callbacks.Callback` or list of callbacks
        A class with methods that get called at various points during the datafit
        process
    custom_parameters : dict of str: float or callable, optional
        A dictionary of parameters to use within this objective only. Values in
        this dictionary will override any values for the simulation within this
        objective but will not be passed on as results of the `DataFit` object.
        If a callable is provided, it must take the form of a function that takes in
        a dictionary of parameters and the `data_input` "data" dictionary and returns
        the value of the parameter (which can be a float or function, as in PyBaMM).
    cost : :class:`ionworkspipeline.costs.ObjectiveFunction` or str, optional
        The cost function to use for the objective. If not provided, the default cost
        function will be used.
    penalties : list[Penalty], optional
        A list of penalties to apply to the objective.
    parameters : dict or :class:`pybamm.ParameterValues`, optional
        Objective-specific parameter values merged into the global parameter values
        before fitting. Unlike ``custom_parameters``, these are static values rather
        than callables. Default is None.
    """

    actions: Any = Field(...)
    constraints: Any | None = Field(default=None)
    options: Any | None = Field(default=None)
    callbacks: Any | None = Field(default=None)
    custom_parameters: Any | None = Field(default=None)
    cost: Any | None = Field(default=None)
    validate_against_experiment_steps: Any = Field(default=True)
    output_variables_full: Any | None = Field(default=None)
    save_at_cycles: Any | None = Field(default=None)
    penalties: Any | None = Field(default=None)
    parameters: Any | None = Field(default=None)

    def __init__(
        self,
        actions,
        constraints=None,
        options=None,
        callbacks=None,
        custom_parameters=None,
        cost=None,
        validate_against_experiment_steps=True,
        output_variables_full=None,
        save_at_cycles=None,
        penalties=None,
        parameters=None,
    ):
        super().__init__(
            actions=actions,
            constraints=constraints,
            options=options,
            callbacks=callbacks,
            custom_parameters=custom_parameters,
            cost=cost,
            validate_against_experiment_steps=validate_against_experiment_steps,
            output_variables_full=output_variables_full,
            save_at_cycles=save_at_cycles,
            penalties=penalties,
            parameters=parameters,
        )


class EIS(FittingObjective):
    """Objective for electrochemical impedance spectroscopy (EIS) data. Simulates the
    model response at the given frequencies and compares the impedance to the data.

    This objective uses the ``pybamm-eis`` package to simulate the EIS experiment in the
    frequency domain.


    Parameters
    ----------

    data_input : str or dict
        The data to use for the fit, see :class:`FittingObjective`.
    options : dict, optional
        A dictionary of options to pass to the objective.

            * model: :class:``pybamm.BaseModel``
                The model to fit. No default is provided, but this option is required
                (a model must be passed in).
            * simulation_kwargs: dict
                Keyword arguments to pass to the simulation (:class:`pybeis.EISSimulation`). Default is None.
    callbacks : :class:`ionworkspipeline.callbacks.Callback` or list of callbacks
        A class with methods that get called at various points during the datafit
        process
    custom_parameters : dict, optional
        A dictionary of parameters to use within this objective only.
        See :class:`FittingObjective`.
    constraints : list[Constraint], optional
        A list of equality and inequality constraints to apply to the objective.
    penalties : list[Penalty], optional
        A list of penalties to apply to the objective.
    parameters : dict or :class:`pybamm.ParameterValues`, optional
        Objective-specific parameter values merged into the global parameter values
        before fitting. Unlike ``custom_parameters``, these are static values rather
        than callables. Default is None."""

    data_input: Any = Field(...)
    options: Any | None = Field(default=None)
    callbacks: Any | None = Field(default=None)
    custom_parameters: Any | None = Field(default=None)
    constraints: Any | None = Field(default=None)
    penalties: Any | None = Field(default=None)
    parameters: Any | None = Field(default=None)

    def __init__(
        self,
        data_input,
        options=None,
        callbacks=None,
        custom_parameters=None,
        constraints=None,
        penalties=None,
        parameters=None,
    ):
        super().__init__(
            data_input=data_input,
            options=options,
            callbacks=callbacks,
            custom_parameters=custom_parameters,
            constraints=constraints,
            penalties=penalties,
            parameters=parameters,
        )


class ElectrodeBalancing(FittingObjective):
    """Objective for electrode balancing (finding electrode capacities and
    stoichiometries that give the best fit to the full cell data).

    Parameters
    ----------
    data_input : str or dict
        The data to use for the fit, see :class:`FittingObjective`.
    options : dict, optional
        A dictionary of options to pass to the objective.
            * dUdQ cutoff: float
                The cutoff dUdQ value to use for fitting (i.e. ignore large values near
                the ends that the solver tries to fit to). Default is None.
            * direction: str
                The direction of the full-cell OCV, either "charge" or "discharge".
                Default is None, which means no directionality is assumed.
    callbacks : :class:`ionworkspipeline.callbacks.Callback` or list of callbacks
        A class with methods that get called at various points during the datafit
        process
    custom_parameters : dict, optional
        A dictionary of parameters to use within this objective only.
        See :class:`FittingObjective`.
    constraints : list[Constraint], optional
        A list of equality and inequality constraints to apply to the objective.
    penalties : list[Penalty], optional
        A list of penalties to apply to the objective."""

    data_input: Any = Field(...)
    options: Any | None = Field(default=None)
    callbacks: Any | None = Field(default=None)
    custom_parameters: Any | None = Field(default=None)
    constraints: Any | None = Field(default=None)
    penalties: Any | None = Field(default=None)

    def __init__(
        self,
        data_input,
        options=None,
        callbacks=None,
        custom_parameters=None,
        constraints=None,
        penalties=None,
    ):
        super().__init__(
            data_input=data_input,
            options=options,
            callbacks=callbacks,
            custom_parameters=custom_parameters,
            constraints=constraints,
            penalties=penalties,
        )


class ElectrodeBalancingHalfCell(FittingObjective):
    """Objective for finding the starting capacity and total capacity of an electrode,
    given an known OCV function. For example, this can be used to fit the starting
    capacity and total capacity for a GITT experiment to align with a previously
    measured OCV curve.

    Parameters
    ----------
    electrode : str
        The electrode to fit ("positive" or "negative").
    data_input : str or dict
        The data to use for the fit, see :class:`FittingObjective`.
    options : dict, optional
        A dictionary of options to pass to the objective.
            * direction: str
                The direction of the OCP, either "lithiation" or "delithiation".
                Default is None, which means no directionality is assumed.
    callbacks : :class:`ionworkspipeline.callbacks.Callback` or list of callbacks
        A class with methods that get called at various points during the datafit
        process
    custom_parameters : dict, optional
        A dictionary of parameters to use within this objective only.
        See :class:`FittingObjective`.
    constraints : list[Constraint], optional
        A list of equality and inequality constraints to apply to the objective.
    penalties : list[Penalty], optional
        A list of penalties to apply to the objective."""

    electrode: Any = Field(...)
    data_input: Any = Field(...)
    options: Any | None = Field(default=None)
    callbacks: Any | None = Field(default=None)
    custom_parameters: Any | None = Field(default=None)
    constraints: Any | None = Field(default=None)
    penalties: Any | None = Field(default=None)

    def __init__(
        self,
        electrode,
        data_input,
        options=None,
        callbacks=None,
        custom_parameters=None,
        constraints=None,
        penalties=None,
    ):
        super().__init__(
            electrode=electrode,
            data_input=data_input,
            options=options,
            callbacks=callbacks,
            custom_parameters=custom_parameters,
            constraints=constraints,
            penalties=penalties,
        )


class MSMRFullCell(FittingObjective):
    """Objective for the open-circuit potential (OCP) of a full cell, using the
    MSMR model.

    The objective consists of the capacity (as a function of voltage) of the full cell,
    and the differential voltage (dU/dQ) of the full cell, as recommended in [1]_.

    Parameters
    ----------
    data_input : str or dict
        The data to use for the fit, see :class:`FittingObjective`.
    options : dict, optional
        A dictionary of options to pass to the objective.
            * model
                The model to use for the full-cell OCV. Default is
                :class:`MSMRFullCellModel` with the negative and positive electrode models
                specified by :class:`MSMRHalfCellModel` with the "species format" option
                set to "Xj". This model should be a class with methods `build`, which
                takes in a parameter values object and the processed data, and `solve`,
                which takes in a dictionary of inputs and returns a dictionary of
                outputs. The `solve` method should return at least the objective variables.
            * dUdQ cutoff
                The cutoff dUdQ value to use for fitting (i.e. ignore large values near
                the ends that the solver tries to fit to).
                If "none", no cutoff is applied. If a float, this is used as the cutoff.
                If a function, the result of calling the function with the data is used
                as the cutoff. Default is the function
                :meth:`iwp.data_fits.util.calculate_dUdQ_cutoff` with default arguments.
            * negative voltage limits
                Tuple of voltage limits for the negative electrode. This option is required.
            * positive voltage limits
                Tuple of voltage limits for the positive electrode. This option is required.

    callbacks : :class:`ionworkspipeline.callbacks.Callback` or list of callbacks
        A class with methods that get called at various points during the datafit
        process
    custom_parameters : dict, optional
        A dictionary of parameters to use within this objective only.
        See :class:`FittingObjective`.
    constraints : list[Constraint], optional
        A list of equality and inequality constraints to apply to the objective.
    penalties : list[Penalty], optional
        A list of penalties to apply to the objective.

    References
    ----------
    .. [1] Hu, Victor W., and Daniel T. Schwartz. Low error estimation of half-cell
        thermodynamic parameters from whole-cell Li-ion battery experiments: Physics-based
        model formulation, experimental demonstration, and an open software tool. Journal
        of The Electrochemical Society 169.3 (2022): 030539."""

    data_input: Any = Field(...)
    options: Any | None = Field(default=None)
    callbacks: Any | None = Field(default=None)
    custom_parameters: Any | None = Field(default=None)
    constraints: Any | None = Field(default=None)
    penalties: Any | None = Field(default=None)

    def __init__(
        self,
        data_input,
        options=None,
        callbacks=None,
        custom_parameters=None,
        constraints=None,
        penalties=None,
    ):
        super().__init__(
            data_input=data_input,
            options=options,
            callbacks=callbacks,
            custom_parameters=custom_parameters,
            constraints=constraints,
            penalties=penalties,
        )


class MSMRHalfCell(FittingObjective):
    """Objective for the open-circuit potential (OCP) of a half-cell, using the
    MSMR model.

    Parameters
    ----------
    data_input : str or dict
        The data to use for the fit, see :class:`FittingObjective`.
    options : dict, optional
        A dictionary of options to pass to the objective.
            * model
                The half-cell OCP model to use for the fit. Default is
                :class:`MSMRHalfCellModel` with the electrode specified. The model class is
                used to specify the species format, direction and capacity function. This
                model should be a class with methods `build`, which takes in a parameter
                values object and the processed data, and `solve`, which takes in a
                dictionary of inputs and returns a dictionary of outputs. The `solve`
                method should return at least the objective variables.
            * voltage limits
                Tuple of voltage limits to use for the fit. If not provided, the range of
                the data is used.
            * dUdQ cutoff
                The cutoff dUdQ value to use for fitting (i.e. ignore large values near
                the ends that the solver tries to fit to).
                If "none", no cutoff is applied. If a float, this is used as the cutoff.
                If a function, the result of calling the function with the data is used
                as the cutoff. Default is the function
                :meth:`iwp.data_fits.util.calculate_dUdQ_cutoff` with default arguments.
            * dQdU cutoff
                The cutoff dQdU value to use for fitting (i.e. ignore large values near
                the ends that the solver tries to fit to).
                If "none", no cutoff is applied. If a float, this is used as the cutoff.
                If a function, the result of calling the function with the data is used
                as the cutoff. Default is `None`.
            * objective variables
                The variables to use for the objective. Default is
                ["Capacity [A.h]", "Differential voltage [V/Ah]"].
            * voltage limits
                The voltage limits for the electrode. Default is None, in which case
                the limits are taken from the data. The limits are not used for
                fitting, but only for plotting.
            * GITT
                Whether the data comes from sparse GITT data. If True, the data is
                interpolated and upsampled. Default is False.
            * constrain Xj method
                The method to use to constrain the Xj values, either "explicit" or
                "reformulate". "explicit" adds an equality constraint to the model to
                ensure that the Xj values sum to 1. "reformulate" reformulates the model
                by replacing the final Xj parameter, Xj_N, with 1 - sum(Xj_n) for n < N.
                Default is "explicit". This option is only used if the species format is
                "Xj".
            * preserve U0j order
                Whether to preserve the order of the U0j parameters. If True, adds
                inequality constraints to the model to ensure that the U0j parameters
                remain in descending order. Default is False. Raises an error if the
                initial values of the U0j parameters are not in descending order.
    callbacks : :class:`ionworkspipeline.callbacks.Callback` or list of callbacks
        A class with methods that get called at various points during the datafit
        process
    custom_parameters : dict, optional
        A dictionary of parameters to use within this objective only.
        See :class:`FittingObjective`.
    constraints : list[Constraint], optional
        A list of equality and inequality constraints to apply to the objective.
    penalties : list[Penalty], optional
        A list of penalties to apply to the objective."""

    data_input: Any = Field(...)
    options: Any | None = Field(default=None)
    callbacks: Any | None = Field(default=None)
    custom_parameters: Any | None = Field(default=None)
    constraints: Any | None = Field(default=None)
    penalties: Any | None = Field(default=None)

    def __init__(
        self,
        data_input,
        options=None,
        callbacks=None,
        custom_parameters=None,
        constraints=None,
        penalties=None,
    ):
        super().__init__(
            data_input=data_input,
            options=options,
            callbacks=callbacks,
            custom_parameters=custom_parameters,
            constraints=constraints,
            penalties=penalties,
        )


class OCPHalfCell(FittingObjective):
    """Objective for the open-circuit potential (OCP) of a half-cell.

    Parameters
    ----------
    electrode : str
        The electrode to fit ("positive" or "negative").
    data_input : str or dict
        The data to use for the fit, see :class:`FittingObjective`.
    options : dict, optional
        A dictionary of options to pass to the objective.

            * theta_ref: float
                The reference value of lithiation used to map between capacity and
                extent of lithiation (theta).

                For the positive electrode the reference value
                is by default assumed to be 1 at the lowest potential observed in the
                data (i.e. we assume that upon lithiation we obtain fully lithiated
                electrode). As a result, for the positive electrode we have
                0 <= theta <= theta_ref.

                For the negative electrode the reference value is by default
                assumed to be 0 at the highest potential observed in the data (i.e. we
                assume that upon delithiation we obtain fully delithiated electrode).
                electrode is fully delithiated in the data). As a result, for the
                negative electrode we have theta_ref <= theta <= 1.
            * stoichiometry limits: 2-tuple of floats
                The limits of the stoichiometry (theta) to use for the fit, if fitting
                a smooth function to the data. Default is (0, 1) - i.e. the fit will
                use the whole range of theta. If the default does not give a good fit,
                we recommend restricting the fit to a smaller range of theta, e.g.
                (0.02, 0.98) or (0.05, 0.95).
            * voltage limits: 2-tuple of floats
                The voltage limits to use for fitting. Default is None, which uses the
                full range of voltage in the data.
            * dUdQ cutoff: float
                The cutoff dUdQ value to use for fitting (i.e. ignore large values near
                the ends that the solver tries to fit to). Default is None.
            * direction: str
                The direction of the OCP, either "lithiation" or "delithiation".
                Default is None, which means no directionality is assumed.
    callbacks : :class:`ionworkspipeline.callbacks.Callback` or list of callbacks
        A class with methods that get called at various points during the datafit
        process
    custom_parameters : dict, optional
        A dictionary of parameters to use within this objective only.
        See :class:`FittingObjective`
    constraints : list[Constraint], optional
        A list of equality and inequality constraints to apply to the objective.
    penalties : list[Penalty], optional
        A list of penalties to apply to the objective."""

    electrode: Any = Field(...)
    data_input: Any = Field(...)
    options: Any | None = Field(default=None)
    callbacks: Any | None = Field(default=None)
    custom_parameters: Any | None = Field(default=None)
    constraints: Any | None = Field(default=None)
    penalties: Any | None = Field(default=None)

    def __init__(
        self,
        electrode,
        data_input,
        options=None,
        callbacks=None,
        custom_parameters=None,
        constraints=None,
        penalties=None,
    ):
        super().__init__(
            electrode=electrode,
            data_input=data_input,
            options=options,
            callbacks=callbacks,
            custom_parameters=custom_parameters,
            constraints=constraints,
            penalties=penalties,
        )


class Objective(FittingObjective):
    """Deprecated alias for `FittingObjective`."""

    pass


class Pulse(SimulationObjective):
    """Objective for pulse experiments (e.g. GITT, HPPC, ICI). By default, the objective
    compares the model voltage to the data voltage. However, it can also compute other
    variables, such as overpotentials, resistances, and ICI features, and these can be
    selected by passing the appropriate objective variables function.

    Parameters
    ----------
    data_input : str or dict
        The data to use for the fit, see :class:`FittingObjective`.
    options : dict, optional
        A dictionary of options to pass to the objective.

            * model: :class:``pybamm.BaseModel``
                The model to fit. No default is provided, but this option is required
                (a model must be passed in).
            * correct OCV difference: str
                Whether to correct for the difference between the true OCV and the
                simulated OCV in the objective function. Default is false, but
                correcting for this difference can improve the fit.
            * simulation_kwargs: dict
                Keyword arguments to pass to the simulation (:class:`iwp.Simulation`). Default is None.
            * objective variables: callable
                A function that takes the model or data and returns a dictionary of
                objective variables. Default is voltage_objective_variables,
                which returns the voltage.
                Other useful functions are

                    * overpotential_objective_variables, which returns the  overpotential
                        at various points in the pulses
                    * resistances_objective_variables, which returns the resistance at
                        various points in the pulses
                    * ici_features_objective_variables, which returns the ICI features
                        (concentration overpotential and ICI square-root slope)
                    * gitt_features_objective_variables, which returns the GITT features
                        (concentration overpotential, relaxation time, ohmic voltage drop,
                        GITT and ICI square-root slopes)
            * interpolant_atol: float
                Absolute tolerance for the current interpolant. Default is the solver `atol`
                if a solver is provided in `simulation_kwargs`, otherwise 1e-6.
            * interpolant_rtol: float
                Relative tolerance for the current interpolant. Default is the solver `rtol`
                if a solver is provided in `simulation_kwargs`, otherwise 1e-4.
            * interactive_preprocessing: bool
                Whether to use interactive preprocessing to adjust `interpolant_atol` and
                `interpolant_rtol` based on the current data. Default is False.
            * solver_max_save_points: int, optional
                Maximum number of points to save in the solver. Disabled by default.
            * Initial SOC: float, optional
                Initial state of charge (0 to 1). Applied before the simulation via
                :class:`~ionworkspipeline.direct_entries.InitialStateOfCharge`.
                Default is None.
            * Initial voltage [V]: float, optional
                Initial voltage in Volts. Cannot be used together with
                ``Initial SOC``. Applied via
                :class:`~ionworkspipeline.direct_entries.InitialVoltage`.
                Default is None.
    callbacks : list of callable, optional
        A class with methods that get called at various points during the datafit
        process
    custom_parameters : dict, optional
        A dictionary of parameters to use within this objective only. The following
        default custom parameters are used:

        For all models:

        * Initial temperature [K]: Function to calculate the initial temperature.
          Default is `iwp.data_fits.custom_parameters.initial_temperature`.
        * Ambient temperature [K]: Function to calculate the ambient temperature.
          Default is `iwp.data_fits.custom_parameters.initial_temperature`.

        For full-cell models:

        * Initial concentration in negative electrode [mol.m-3]: Function to calculate
          the initial concentration in the negative electrode for full cells.
          Default is `iwp.data_fits.custom_parameters.initial_concentration_from_voltage("full", "negative")`.
        * Initial concentration in positive electrode [mol.m-3]: Function to calculate
          the initial concentration in the positive electrode for full cells.
          Default is `iwp.data_fits.custom_parameters.initial_concentration_from_voltage("full", "positive")`.

        For half-cell models:

        * Initial concentration in {working_electrode} electrode [mol.m-3]: Function to calculate
          the initial concentration in the working electrode for half cells.
          Default is `iwp.data_fits.custom_parameters.initial_concentration_from_voltage("half", {working_electrode})`.

        These custom parameters are functions that take `parameter_values` and `data` as arguments
        and return the calculated value. They can be overridden by providing new functions in the
        `custom_parameters` dictionary.

        See :class:`FittingObjective` for more details.
    constraints : list[Constraint], optional
        A list of equality and inequality constraints to apply to the objective.
    penalties : list[Penalty], optional
        A list of penalties to apply to the objective.
    parameters : dict or :class:`pybamm.ParameterValues`, optional
        Objective-specific parameter values merged into the global parameter values
        before fitting. Unlike ``custom_parameters``, these are static values rather
        than callables. Default is None."""

    data_input: Any = Field(...)
    options: Any | None = Field(default=None)
    callbacks: Any | None = Field(default=None)
    custom_parameters: Any | None = Field(default=None)
    constraints: Any | None = Field(default=None)
    penalties: Any | None = Field(default=None)
    parameters: Any | None = Field(default=None)

    def __init__(
        self,
        data_input,
        options=None,
        callbacks=None,
        custom_parameters=None,
        constraints=None,
        penalties=None,
        parameters=None,
    ):
        super().__init__(
            data_input=data_input,
            options=options,
            callbacks=callbacks,
            custom_parameters=custom_parameters,
            constraints=constraints,
            penalties=penalties,
            parameters=parameters,
        )


class Resistance(FittingObjective):
    """Objective for fitting the resistance.

    Parameters
    ----------
    data_input : :class:`pd.DataFrame`
        The data to use for the fit, see :class:`FittingObjective`. Should have columns
        "SOC" and "Resistance [Ohm]", plus any additional columns required by the
        resistance model.
    options : dict, optional
        A dictionary of options to pass to the objective.

            * model: :class:``pybamm.BaseModel``
                The model to fit. No default is provided, but this option is required
                (a model must be passed in).
    callbacks : list of callable, optional
        A class with methods that get called at various points during the datafit
        process
    custom_parameters : dict, optional
        A dictionary of parameters to use within this objective only.
        See :class:`FittingObjective`.
    constraints : list[Constraint], optional
        A list of equality and inequality constraints to apply to the objective.
    penalties : list[Penalty], optional
        A list of penalties to apply to the objective.
    parameters : dict or :class:`pybamm.ParameterValues`, optional
        Objective-specific parameter values merged into the global parameter values
        before fitting. Unlike ``custom_parameters``, these are static values rather
        than callables. Default is None."""

    data_input: Any = Field(...)
    options: Any | None = Field(default=None)
    callbacks: Any | None = Field(default=None)
    custom_parameters: Any | None = Field(default=None)
    constraints: Any | None = Field(default=None)
    penalties: Any | None = Field(default=None)
    parameters: Any | None = Field(default=None)

    def __init__(
        self,
        data_input,
        options=None,
        callbacks=None,
        custom_parameters=None,
        constraints=None,
        penalties=None,
        parameters=None,
    ):
        super().__init__(
            data_input=data_input,
            options=options,
            callbacks=callbacks,
            custom_parameters=custom_parameters,
            constraints=constraints,
            penalties=penalties,
            parameters=parameters,
        )


class SimulationObjective(FittingObjective):
    """A pipeline element that constructs an objective function used to fit a model to
    data. SimulationObjective is a subclass of FittingObjective intended for use with
    objectives that run a pybamm simulation.

    Parameters
    ----------
    data_input : str or dict
        The data to use for the fit. Can be a string giving the path to the data, or a
        dictionary with keys "data" and "metadata". "data" should be a DataFrame that
        supplies the raw data, and "metadata" should be a dictionary that supplies
        metadata about the data.
    options : dict, optional
        A dictionary of options to pass to the data fit.
    callbacks : :class:`ionworkspipeline.callbacks.Callback` or list of callbacks
        A class with methods that get called at various points during the datafit
        process
    custom_parameters : dict of str: float or callable, optional
        A dictionary of parameters to use within this objective only. Values in
        this dictionary will override any values for the simulation within this
        objective but will not be passed on as results of the `DataFit` object.
        If a callable is provided, it must take the form of a function that takes in
        a dictionary of parameters and the `data_input` "data" dictionary and returns
        the value of the parameter (which can be a float or function, as in PyBaMM).
    constraints : list[Constraint], optional
        A list of equality and inequality constraints to apply to the objective.
    penalties : list[Penalty], optional
        A list of penalties to apply to the objective.
    parameters : dict or :class:`pybamm.ParameterValues`, optional
        Objective-specific parameter values merged into the global parameter values
        before fitting. Unlike ``custom_parameters``, these are static values rather
        than callables. Default is None."""
