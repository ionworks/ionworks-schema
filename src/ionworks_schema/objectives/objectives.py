"""Schemas for objectives."""

from typing import Annotated, Any

from pydantic import Field, field_validator

from .._types import Electrode, MeasurementInput, ParameterValuesLike
from ..base import BaseSchema
from ..objective_functions.regularizers import Constraint, Penalty

# Cost-function schema, raw dict, name string, or runtime cost object
# (the last via the from_schema passthrough path).
_CostLike = Annotated[
    dict[str, Any] | BaseSchema | str | Any,
    Field(union_mode="left_to_right"),
]
_ConstraintLike = Annotated[
    dict[str, Any] | Constraint | Any,
    Field(union_mode="left_to_right"),
]
_PenaltyLike = Annotated[
    dict[str, Any] | Penalty | Any,
    Field(union_mode="left_to_right"),
]
# ``callbacks`` stays ``Any`` — user-defined Callback classes; runtime enforces the Protocol.

# Shared ``Field(description=...)`` strings. Most objective subclasses inherit
# BaseObjective / FittingObjective and redeclare these fields to keep the
# per-subclass autodoc table self-contained, so the description text is
# duplicated at ~14 call sites. Defining the strings once here keeps wording
# consistent and concentrates future wording changes.
_DATA_INPUT_DESCRIPTION = (
    "The measured data this objective is fit against. Accepts an "
    "``ionworksdata.DataLoader`` (constructed directly from "
    "DataFrames, or via ``DataLoader.from_local(path)`` / "
    "``DataLoader.from_db(measurement_id)``), a path to a data file, "
    "a ``pandas`` or ``polars`` DataFrame, or a dict with keys "
    "``data`` (DataFrame of raw values) and ``metadata`` (dict "
    "describing the experiment, e.g. temperature, electrode area)."
)
_GENERIC_OPTIONS_DESCRIPTION = (
    "Objective-specific settings — typically the pybamm model to "
    "simulate, simulation kwargs, and which variables to compare against "
    "the data. The supported keys and their defaults are listed per "
    "objective below."
)
_CALLBACKS_DESCRIPTION = (
    "A callback (or list of callbacks) whose methods run at various "
    "points during the fit — useful for logging, plotting progress, or "
    "early stopping. Defaults to no callbacks."
)
_CUSTOM_PARAMETERS_DESCRIPTION = (
    "Deprecated alias for ``parameters`` — use ``parameters`` for new fits."
)
_COST_DESCRIPTION = (
    "The cost function used to score how well the model matches the data "
    "(e.g. ``RMSE``, ``MAE``, ``GaussianLogLikelihood``). If ``None``, the "
    "optimizer's default cost is used."
)
_CONSTRAINTS_DESCRIPTION = (
    "Equality or inequality ``Constraint`` terms that must be satisfied "
    "while the parameters are being fit (for example, forcing two "
    "parameters to remain in a fixed ratio)."
)
_PENALTIES_DESCRIPTION = (
    "Soft ``Penalty`` terms added to the cost — use these to gently "
    "discourage parameter combinations rather than forbid them outright."
)
_PARAMETERS_DESCRIPTION = (
    "Parameter values that override the global parameter set just for "
    "this objective (handy if one experiment was run at a different "
    "temperature or current, say). Default is ``None``."
)
_ELECTRODE_DESCRIPTION = (
    "Which electrode the data describes — ``'positive'`` or ``'negative'``."
)

_INTERACTIVE_PREPROCESSING_ERROR = (
    "'interactive_preprocessing' is not supported in schema-built configs. It opens "
    "a local matplotlib UI, which is unavailable when the config runs server-side "
    "or in a notebook. Remove the key from `options`; to tune interpolant "
    "tolerances interactively, run the fit locally with ionworkspipeline instead."
)


def _reject_interactive_preprocessing(options: dict | None) -> dict | None:
    """Reject the ``interactive_preprocessing`` option key — local-only feature."""
    if options is not None and "interactive_preprocessing" in options:
        raise ValueError(_INTERACTIVE_PREPROCESSING_ERROR)
    return options


class BaseObjective(BaseSchema):
    """Shared base for every objective. Not used directly.

    Concrete subclasses (``Pulse``, ``EIS``, ``CycleAgeing``, ``MSMRHalfCell``,
    ``DesignObjective``, …) inherit from here. An objective tells the
    pipeline *what* to fit (or optimize) and *which data* to compare
    against — pick a concrete subclass that matches your experiment.

    Parameters
    ----------
    options : dict, optional
        Objective-specific settings. The supported keys depend on the
        subclass — see each subclass's docstring for the list.
    callbacks : Callback or list of Callback, optional
        Callback(s) that run at various points during the fit (logging,
        plotting, early stopping).
    cost : ObjectiveFunction or str, optional
        The cost function used to score the fit (e.g. ``RMSE``, ``MAE``,
        ``GaussianLogLikelihood``). If ``None``, the optimizer's default
        cost is used.
    constraints : list of Constraint, optional
        Equality or inequality constraints that must hold during the fit.
    penalties : list of Penalty, optional
        Soft penalties added to the cost.
    parameters : dict or pybamm.ParameterValues, optional
        Parameter overrides applied only to this objective."""

    options: dict[str, Any] | None = Field(
        default=None,
        description=_GENERIC_OPTIONS_DESCRIPTION,
    )
    callbacks: Any | None = Field(default=None, description=_CALLBACKS_DESCRIPTION)  # noqa: ANN401
    custom_parameters: dict[str, Any] | None = Field(
        default=None, description=_CUSTOM_PARAMETERS_DESCRIPTION
    )
    cost: _CostLike | None = Field(
        default=None,
        description=(
            "Cost function used to construct the objective (e.g. MLE, RMSE, "
            "GaussianLogLikelihood). If None, the optimizer's default cost function is "
            "used."
        ),
    )
    constraints: list[_ConstraintLike] | None = Field(
        default=None, description=_CONSTRAINTS_DESCRIPTION
    )
    penalties: list[_PenaltyLike] | None = Field(
        default=None, description=_PENALTIES_DESCRIPTION
    )
    parameters: ParameterValuesLike | None = Field(
        default=None, description=_PARAMETERS_DESCRIPTION
    )

    def __init__(
        self,
        options=None,
        callbacks=None,
        custom_parameters=None,
        cost=None,
        constraints=None,
        penalties=None,
        parameters=None,
        **kwargs,
    ):
        super().__init__(
            options=options,
            callbacks=callbacks,
            custom_parameters=custom_parameters,
            cost=cost,
            constraints=constraints,
            penalties=penalties,
            parameters=parameters,
            **kwargs,
        )


class FittingObjective(BaseObjective):
    """Shared base for objectives that fit a model to measured data.

    On top of ``BaseObjective`` this adds ``data_input`` — the experimental
    data the model is compared against. Pick a concrete subclass that
    matches your experiment (``Pulse``, ``EIS``, ``OCPHalfCell``,
    ``CycleAgeing``, …).

    Parameters
    ----------
    data_input : DataLoader, DataFrame, str, or dict
        The measured data. Accepts an ``ionworksdata.DataLoader``
        (constructed directly from DataFrames, or via
        ``DataLoader.from_local(path)`` /
        ``DataLoader.from_db(measurement_id)``), a path to a data
        file, a ``pandas`` or ``polars`` DataFrame, or a dict with
        keys ``data`` (DataFrame of raw values) and ``metadata`` (dict
        describing the experiment).
    options : dict, optional
        Objective-specific settings — see each subclass for supported keys.
    callbacks : Callback or list of Callback, optional
        Callback(s) invoked at various points during the fit.
    cost : ObjectiveFunction or str, optional
        Cost function used to score the fit. If ``None``, the optimizer's
        default cost is used.
    constraints : list of Constraint, optional
        Equality or inequality constraints that must hold during the fit.
    penalties : list of Penalty, optional
        Soft penalties added to the cost.
    parameters : dict or pybamm.ParameterValues, optional
        Parameter overrides applied only to this objective."""

    data_input: MeasurementInput = Field(
        ..., alias="data", description=_DATA_INPUT_DESCRIPTION
    )
    options: dict[str, Any] | None = Field(
        default=None,
        description=_GENERIC_OPTIONS_DESCRIPTION,
    )
    callbacks: Any | None = Field(default=None, description=_CALLBACKS_DESCRIPTION)  # noqa: ANN401
    custom_parameters: dict[str, Any] | None = Field(
        default=None, description=_CUSTOM_PARAMETERS_DESCRIPTION
    )
    cost: _CostLike | None = Field(default=None, description=_COST_DESCRIPTION)
    constraints: list[_ConstraintLike] | None = Field(
        default=None, description=_CONSTRAINTS_DESCRIPTION
    )
    penalties: list[_PenaltyLike] | None = Field(
        default=None, description=_PENALTIES_DESCRIPTION
    )
    parameters: ParameterValuesLike | None = Field(
        default=None, description=_PARAMETERS_DESCRIPTION
    )

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
        **kwargs,
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
            **kwargs,
        )


class SimulationObjective(FittingObjective):
    """Shared base for objectives that run a pybamm simulation and compare
    the output to measured data.

    Subclasses such as ``Pulse``, ``CurrentDriven``, ``CalendarAgeing``, and
    ``CycleAgeing`` inherit from here. The arguments are the same as
    ``FittingObjective`` — pick a concrete subclass that matches your
    experiment.
    """

    pass


class CalendarAgeing(SimulationObjective):
    """Fit degradation parameters (loss of lithium inventory, loss of active
    material) to calendar-ageing data for a full cell.

    Parameters
    ----------
    data_input : DataLoader, DataFrame, str, or dict
        The calendar-ageing data — see :class:`FittingObjective`.
    options : dict, optional
        Calendar-ageing settings:

            * ``model`` (required): the pybamm model to fit.
            * ``modes`` (list of str): which degradation modes to fit. Any
                combination of ``"LLI [%]"``, ``"LAM_ne [%]"``, ``"LAM_pe [%]"``.
                Defaults to ``["LLI [%]"]``.
            * ``simulation_kwargs`` (dict): kwargs forwarded to the
                simulation. May include ``solver_kwargs`` to tune the auto-built
                solver (e.g. ``{"options": {"compile": True}}`` to enable
                compilation), ignored if an explicit ``solver`` is also provided.
                May also include ``solve_kwargs`` forwarded to the runtime
                solve regardless of the solver (e.g. ``starting_solution``).
                Defaults to ``None``.
    callbacks, constraints, penalties, parameters
        Shared with :class:`BaseObjective`.

    Examples
    --------
    >>> obj = iws.objectives.CalendarAgeing(
    ...     data_input="path/to/calendar.csv",
    ...     options={"modes": ["LLI [%]", "LAM_pe [%]"]},
    ... )
    >>> # slot into a DataFit (parameters omitted for brevity)
    """

    data_input: MeasurementInput = Field(
        ..., alias="data", description=_DATA_INPUT_DESCRIPTION
    )
    options: dict[str, Any] | None = Field(
        default=None,
        description=(
            "Calendar-ageing objective options. Supported keys: ``model`` "
            "(required pybamm model), ``modes`` (list of degradation modes to "
            'fit — any combination of "LLI [%]", "LAM_ne [%]", "LAM_pe [%]"; '
            'defaults to ["LLI [%]"]), and ``simulation_kwargs`` (kwargs forwarded '
            "to ``iwp.Simulation``; may include ``solver_kwargs`` to tune the "
            "auto-built solver, e.g. ``{'options': {'compile': True}}`` to "
            "enable compilation; ignored if an explicit ``solver`` is also provided; "
            "and ``solve_kwargs`` forwarded to the runtime solve regardless of "
            "the solver, e.g. ``starting_solution``)."
        ),
    )
    callbacks: Any | None = Field(default=None, description=_CALLBACKS_DESCRIPTION)  # noqa: ANN401
    custom_parameters: dict[str, Any] | None = Field(
        default=None, description=_CUSTOM_PARAMETERS_DESCRIPTION
    )
    constraints: list[_ConstraintLike] | None = Field(
        default=None, description=_CONSTRAINTS_DESCRIPTION
    )
    penalties: list[_PenaltyLike] | None = Field(
        default=None, description=_PENALTIES_DESCRIPTION
    )
    parameters: ParameterValuesLike | None = Field(
        default=None, description=_PARAMETERS_DESCRIPTION
    )

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
    """Fit a model against any current-driven experiment — pulse trains, drive
    cycles, custom load profiles.

    Pass in the recorded current/voltage data along with the model and the
    objective will simulate the same current profile and compare voltages
    (or any other variable you ask for).

    Parameters
    ----------
    data_input : DataLoader, DataFrame, str, or dict
        The current/voltage data — see :class:`FittingObjective`.
    options : dict, optional
        Current-driven settings:

            * ``model`` (required): the pybamm model to fit.
            * ``independent variable`` (str): ``"time"`` (default) or
                ``"voltage"``. Use ``"voltage"`` when matching to a voltage
                trace makes more physical sense than matching to a time trace.
            * ``simulation_kwargs`` (dict): kwargs forwarded to the
                simulation. When no experiment is given, defaults to
                ``{"output_variables": ["Voltage [V]", "Current [A]"]}``.
                May include ``solver_kwargs`` to tune the auto-built solver
                (e.g. ``{"options": {"compile": True}}`` to enable
                compilation), ignored if an explicit ``solver`` is also provided.
                May also include ``solve_kwargs`` forwarded to the runtime
                solve regardless of the solver (e.g. ``starting_solution``).
            * ``objective variables`` (list of str): which variables the fit
                compares. With ``"time"``, defaults to ``["Voltage [V]"]``.
                With ``"voltage"``, defaults to ``["Time [s]"]`` and can't
                be changed.
            * ``interpolant_atol`` / ``interpolant_rtol`` (float): tolerances
                for the current interpolant. Default to the solver's
                ``atol``/``rtol`` if a solver is supplied in
                ``simulation_kwargs``, otherwise ``1e-6`` and ``1e-4``.
            * ``interactive_preprocessing``: not supported in schema-built
                configs — raises a ``ValueError`` if set. The underlying
                pipeline option opens a local matplotlib UI, which is
                unavailable when the config runs server-side or in a
                notebook.
            * ``solver_max_save_points`` (int): cap on solver save points.
                Disabled by default.
    callbacks, constraints, penalties, parameters
        Shared with :class:`BaseObjective`.

    Examples
    --------
    >>> obj = iws.objectives.CurrentDriven(
    ...     data_input="path/to/drive_cycle.csv",
    ...     options={"objective variables": ["Voltage [V]"]},
    ... )
    >>> # slot into a DataFit (parameters omitted for brevity)
    """

    data_input: MeasurementInput = Field(
        ..., alias="data", description=_DATA_INPUT_DESCRIPTION
    )
    options: dict[str, Any] | None = Field(
        default=None,
        description=(
            "Current-driven objective options. Supported keys: ``model`` "
            "(required pybamm model), ``independent variable`` (``'time'`` or "
            "``'voltage'`` — default ``'time'``), ``simulation_kwargs`` (kwargs "
            "forwarded to ``iwp.Simulation``), ``objective variables`` (list of "
            "variables to fit; default depends on ``independent variable``), "
            "``interpolant_atol`` / ``interpolant_rtol`` (tolerances for the "
            "current interpolant), and "
            "``solver_max_save_points`` (max solver save points; disabled by "
            "default). ``simulation_kwargs`` may include ``solver_kwargs`` to tune the "
            "auto-built solver (e.g. ``{'options': {'compile': True}}`` to "
            "enable compilation; ignored if an explicit ``solver`` is also provided) "
            "and ``solve_kwargs`` forwarded to the runtime solve regardless of "
            "the solver (e.g. ``starting_solution``)."
        ),
    )
    _validate_options = field_validator("options")(_reject_interactive_preprocessing)
    callbacks: Any | None = Field(default=None, description=_CALLBACKS_DESCRIPTION)  # noqa: ANN401
    custom_parameters: dict[str, Any] | None = Field(
        default=None, description=_CUSTOM_PARAMETERS_DESCRIPTION
    )
    constraints: list[_ConstraintLike] | None = Field(
        default=None, description=_CONSTRAINTS_DESCRIPTION
    )
    penalties: list[_PenaltyLike] | None = Field(
        default=None, description=_PENALTIES_DESCRIPTION
    )
    parameters: ParameterValuesLike | None = Field(
        default=None, description=_PARAMETERS_DESCRIPTION
    )

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
    """Fit summary variables (capacity, resistance, LLI, LAM) against
    cell-cycling data.

    Each row in the data is one summary measurement across a cycle (or
    a small group of cycles). The objective runs the requested cycling
    experiment, extracts the same summary variables from the simulation,
    and compares the two.

    Parameters
    ----------
    data_input : DataLoader, DataFrame, str, or dict
        The cycling summary data — see :class:`FittingObjective`.
    options : dict, optional
        Cycle-ageing settings:

            * ``model`` (required): the pybamm model to fit.
            * ``experiment`` (required): the ``pybamm.Experiment`` to simulate;
                the string ``"from data"`` to generate the experiment
                automatically from the step information in the data (requires
                ``data_input`` to be an ``ionworksdata.DataLoader``, or a dict
                whose ``"data"`` entry is a DataLoader, with steps); or an
                ``ionworksdata.DataLoader`` to generate the experiment from
                that loader's steps instead — useful when the fitted data
                (e.g. a per-cycle summary table) is a different object from
                the measurement that defines the protocol. Generation happens
                lazily when the fit starts, so step data is only loaded at
                that point.
            * ``objective variables`` (required, list of str): which summary
                variables to compare. Must be a subset of the data columns.
            * ``metrics`` (dict): mapping from variable name to a
                ``.by_cycle()`` metric object that extracts that value from
                the simulation. Defaults are provided for ``"LLI [%]"``,
                ``"LAM_ne [%]"``, and ``"LAM_pe [%]"``. When every metric reads
                only per-step first/last values (the defaults, or any
                ``First``/``Last`` ``.by_cycle()`` metric),
                ``solver_kwargs["store_first_last"]`` defaults to ``True`` so the
                solver stores only step endpoints — much more memory-light for
                long cycling solves. Pass it explicitly to override.
            * ``simulation_kwargs`` (dict): kwargs forwarded to the
                simulation. May include ``solver_kwargs`` to tune the auto-built
                solver (e.g. ``{"options": {"compile": True}}`` to enable
                compilation), ignored if an explicit ``solver`` is also provided.
                May also include ``solve_kwargs`` forwarded to the runtime
                solve regardless of the solver; ``save_at_cycles`` is derived
                automatically from the metrics and a value passed here is ignored
                with a warning (the metrics' cycles must be kept).
                ``experiment_model_mode`` defaults to ``"unified"`` (a single
                switching model for the whole experiment, much cheaper for
                repeated cycling) whenever an experiment is supplied; pass it
                explicitly here to override. Defaults to ``None``.
    callbacks, constraints, penalties, parameters
        Shared with :class:`BaseObjective`.

    Examples
    --------
    >>> obj = iws.objectives.CycleAgeing(
    ...     data_input="path/to/cycling_summary.csv",
    ...     options={"objective variables": ["Discharge capacity [A.h]"]},
    ... )
    >>> # slot into a DataFit (parameters omitted for brevity)
    """

    data_input: MeasurementInput = Field(
        ..., alias="data", description=_DATA_INPUT_DESCRIPTION
    )
    options: dict[str, Any] | None = Field(
        default=None,
        description=(
            "Cycle-ageing objective options. Required keys: ``model`` (pybamm "
            "model), ``experiment`` (pybamm experiment; the string "
            "'from data' to generate it from the data input DataLoader's step "
            "information; or a DataLoader to generate it from that loader's "
            "steps), and ``objective "
            "variables`` (list of summary variables to fit, which must be a "
            "subset of the data columns). Optional keys: ``metrics`` (dict "
            "mapping variable names to ``.by_cycle()`` metric objects; defaults "
            'provided for "LLI [%]", "LAM_ne [%]", "LAM_pe [%]"; when every '
            "metric reads only per-step first/last values, "
            "``solver_kwargs['store_first_last']`` defaults to True so the solver "
            "stores only step endpoints) and "
            "``simulation_kwargs`` (kwargs forwarded to ``iwp.Simulation``; may include "
            "``solver_kwargs`` to tune the auto-built solver, e.g. "
            "``{'options': {'compile': True}}`` to enable compilation; "
            "ignored if an explicit ``solver`` is also provided; and "
            "``solve_kwargs`` forwarded to the runtime solve regardless of the "
            "solver, where ``save_at_cycles`` is derived automatically from the "
            "metrics and a value here is ignored with a warning; and "
            "``experiment_model_mode``, which defaults to 'unified' (a single "
            "switching model for the whole experiment, much cheaper for repeated "
            "cycling) whenever an experiment is supplied, overridable here)."
        ),
    )
    callbacks: Any | None = Field(default=None, description=_CALLBACKS_DESCRIPTION)  # noqa: ANN401
    custom_parameters: dict[str, Any] | None = Field(
        default=None, description=_CUSTOM_PARAMETERS_DESCRIPTION
    )
    constraints: list[_ConstraintLike] | None = Field(
        default=None, description=_CONSTRAINTS_DESCRIPTION
    )
    penalties: list[_PenaltyLike] | None = Field(
        default=None, description=_PENALTIES_DESCRIPTION
    )
    parameters: ParameterValuesLike | None = Field(
        default=None, description=_PARAMETERS_DESCRIPTION
    )

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
    """Objective for design optimisation — maximise (or minimise) one or more
    cell metrics by adjusting design parameters.

    You describe each design target as an ``Action`` wrapping a ``Metric``
    (e.g. maximise energy density, hit a target fast-charge time) and pass
    them in via ``actions``. The optimiser then searches the parameter
    space to find the design that best satisfies all of them, subject to
    any constraints you specify.

    The objective handles simulation failures and edge-case parameter
    combinations automatically — failed simulations receive large penalties
    so the optimiser steers away from those regions.

    Parameters
    ----------
    actions : dict[str, Any]
        Mapping of action name to an ``Action``-wrapped ``Metric`` defining
        each design target.
    constraints : dict[str, BaseAction] or list of Constraint, optional
        Hard limits on the design. For design optimization this may be
        either a dict of ``Action``-wrapped metrics (e.g. minimum capacity)
        or a list of ``Constraint`` terms on pybamm symbols.
    options : dict, optional
        Settings for the design simulation (model, experiment, simulation
        kwargs).
    callbacks : Callback or list of Callback, optional
        Callback(s) invoked at various points during optimisation.
    cost : ObjectiveFunction or str, optional
        Cost function used to combine the actions into a single design
        score. If ``None``, the optimizer's default design cost is used.
    penalties : list of Penalty, optional
        Soft penalties added to the cost.
    parameters : dict or pybamm.ParameterValues, optional
        Parameter overrides applied only to this objective.
    """

    actions: dict[str, Any] = Field(
        ...,
        description=(
            "Dictionary mapping action names to ``Action``-wrapped ``Metric`` "
            "instances that define the design objective and its target values."
        ),
    )
    # DesignObjective also accepts a dict of action-name → ``BaseAction``
    # in addition to the standard list-of-Constraint form.
    constraints: dict[str, Any] | list[_ConstraintLike] | None = Field(
        default=None,
        description=(
            "Equality and inequality constraints applied to the objective. For "
            "design optimization, this may be a dict of ``BaseAction``-wrapped "
            "metrics, or a list of ``Constraint`` terms on pybamm symbols."
        ),
    )
    options: dict[str, Any] | None = Field(
        default=None,
        description=(
            "Dictionary of options passed to the design objective (e.g. model, "
            "experiment, simulation kwargs)."
        ),
    )
    callbacks: Any | None = Field(  # noqa: ANN401
        default=None,
        description=(
            "A single callback or list of callbacks whose methods are invoked at "
            "various points during design optimization."
        ),
    )
    custom_parameters: dict[str, Any] | None = Field(
        default=None,
        description=(
            "Deprecated alias for ``parameters`` — use ``parameters`` for new "
            "optimizations."
        ),
    )
    cost: _CostLike | None = Field(
        default=None,
        description=(
            "Design cost function used to construct the objective. If None, the "
            "optimizer's default design cost function is used."
        ),
    )
    validate_against_experiment_steps: bool = Field(
        default=True,
        description=(
            "When True, validate that the simulation completed all steps of the "
            "configured experiment before scoring the design objective. Default "
            "is True."
        ),
    )
    output_variables_full: list[str] | None = Field(
        default=None,
        description=(
            "List of output variables saved from the full simulation in addition "
            "to the action outputs. If None, defaults are combined with the "
            "variables required by the configured actions."
        ),
    )
    save_at_cycles: list[int] | None = Field(
        default=None,
        description=(
            "Cycle indices at which to save solution output. Default is None "
            "(save every cycle as configured by the simulation)."
        ),
    )
    penalties: list[_PenaltyLike] | None = Field(
        default=None,
        description=(
            "List of ``Penalty`` terms added as soft penalties to the design "
            "objective cost."
        ),
    )
    parameters: ParameterValuesLike | None = Field(
        default=None,
        description=(
            "Objective-specific parameter values merged into the global "
            "``ParameterValues`` before optimization. Default is None."
        ),
    )

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

    def to_config(self) -> dict:
        """Build the dict you submit through ``ionworks-api``.

        Same as the base ``to_config``, with ``actions`` folded under
        the ``"options"`` key so the payload matches the structure the
        Ionworks API expects for cycling objectives.
        """
        config = super().to_config()
        options = config.pop("options", {}) or {}
        if "actions" in config:
            options["actions"] = config.pop("actions")
        if options:
            config["options"] = options
        return config


class EIS(FittingObjective):
    """Fit a model against electrochemical impedance spectroscopy (EIS) data.

    Simulates the model response at the supplied frequencies and compares
    the predicted impedance to the measured spectrum. Uses pybamm's
    frequency-domain EIS simulator under the hood.

    Parameters
    ----------
    data_input : DataLoader, DataFrame, str, or dict
        The EIS data — see :class:`FittingObjective`.
    options : dict, optional
        EIS settings:

            * ``model`` (required): the pybamm model to fit.
            * ``simulation_kwargs`` (dict): kwargs forwarded to the EIS
                simulator. Defaults to ``None``.
    callbacks, constraints, penalties, parameters
        Shared with :class:`BaseObjective`.

    Examples
    --------
    >>> obj = iws.objectives.EIS(data_input="path/to/eis.csv")
    >>> # slot into a DataFit (parameters omitted for brevity)"""

    data_input: MeasurementInput = Field(
        ..., alias="data", description=_DATA_INPUT_DESCRIPTION
    )
    options: dict[str, Any] | None = Field(
        default=None,
        description=(
            "EIS objective options. Supported keys: ``model`` (required pybamm "
            "model) and ``simulation_kwargs`` (kwargs forwarded to "
            "``pybeis.EISSimulation``)."
        ),
    )
    callbacks: Any | None = Field(default=None, description=_CALLBACKS_DESCRIPTION)  # noqa: ANN401
    custom_parameters: dict[str, Any] | None = Field(
        default=None, description=_CUSTOM_PARAMETERS_DESCRIPTION
    )
    constraints: list[_ConstraintLike] | None = Field(
        default=None, description=_CONSTRAINTS_DESCRIPTION
    )
    penalties: list[_PenaltyLike] | None = Field(
        default=None, description=_PENALTIES_DESCRIPTION
    )
    parameters: ParameterValuesLike | None = Field(
        default=None, description=_PARAMETERS_DESCRIPTION
    )

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
    """Find the electrode capacities and stoichiometry windows that best
    reconstruct a full-cell OCV curve from the underlying half-cell OCPs.

    Parameters
    ----------
    data_input : DataLoader, DataFrame, str, or dict
        The full-cell OCV data — see :class:`FittingObjective`.
    options : dict, optional
        Electrode-balancing settings:

            * ``dUdQ cutoff`` (float): ignore data points with very large
                ``dU/dQ`` (typically near the voltage limits). Default ``None``.
            * ``dQdU cutoff`` (float): ignore data points with very large
                ``dQ/dU`` (typically in flat regions of the OCV). Default ``None``.
            * ``direction`` (str): ``"charge"`` or ``"discharge"`` — direction
                of the OCV scan. Default ``None`` (no direction assumed).
            * ``GITT`` (bool): treat the data as sparse GITT data and upsample
                it by interpolation before fitting. Default ``False``.
            * ``objective variables`` (list of str): variables compared between
                model and data. Default ``["Voltage [V]", "Differential voltage
                [V/Ah]"]``. Optionally include ``"Differential capacity [Ah/V]"``
                to also output the model dQ/dU on the data voltage grid, together
                with the masked-axis siblings ``"Voltage [V] (dQdU)"`` and
                ``"Capacity [A.h] (dQdU)"`` so weighted costs (e.g.
                :class:`iws.costs.Wasserstein` with ``position_variable`` and
                ``weight_variable``) can pair positions and weights at equal
                length.
            * ``dQdU model axis`` (bool): additionally emit dQ/dV on the
                model's OWN full-window voltage axis — the variables
                ``"Differential capacity [Ah/V] (model axis)"`` and
                ``"Voltage [V] (model axis)"`` — so a weighted cost (e.g.
                :class:`iws.costs.Wasserstein`) can position-shift, aligning
                dQ/dV peaks in voltage rather than comparing on the data
                voltage grid. The model and data sides have different lengths
                by construction, so only a weighted cost should consume them
                (a sibling per-variable cost must be scoped to skip them). Add
                both names to ``objective variables`` to use them. Default
                ``False``.
    callbacks, constraints, penalties, parameters
        Shared with :class:`BaseObjective`.

    Examples
    --------
    >>> obj = iws.objectives.ElectrodeBalancing(
    ...     data_input="path/to/full_cell_ocv.csv",
    ...     options={"direction": "discharge"},
    ... )
    >>> # slot into a DataFit (parameters omitted for brevity)"""

    data_input: MeasurementInput = Field(
        ..., alias="data", description=_DATA_INPUT_DESCRIPTION
    )
    options: dict[str, Any] | None = Field(
        default=None,
        description=(
            "Electrode-balancing objective options. Supported keys: "
            "``dUdQ cutoff`` (float — ignore data points with very large "
            "``dU/dQ``, typically near the voltage limits; default None), "
            "``dQdU cutoff`` (float — ignore data points with very large "
            "``dQ/dU``, typically in flat regions of the OCV; default None), "
            "``direction`` (``'charge'`` or ``'discharge'`` — direction "
            "of the OCV scan; default None, meaning no direction is assumed), "
            "``GITT`` (bool — treat the data as sparse GITT data and upsample "
            "it by interpolation; default False), and ``objective variables`` "
            "(list of str — variables compared between model and data; default "
            "['Voltage [V]', 'Differential voltage [V/Ah]']; optionally include "
            "'Differential capacity [Ah/V]' to also output the model dQ/dU on "
            "the data voltage grid plus the masked-axis siblings "
            "'Voltage [V] (dQdU)' and 'Capacity [A.h] (dQdU)' for weighted "
            "costs), and ``dQdU model axis`` (bool — additionally emit dQ/dV on "
            "the model's own full-window voltage axis as "
            "'Differential capacity [Ah/V] (model axis)' and "
            "'Voltage [V] (model axis)' so a weighted cost can position-shift, "
            "aligning dQ/dV peaks in voltage rather than the data grid; the two "
            "sides differ in length by construction, so only a weighted cost "
            "should consume them; default False)."
        ),
    )
    callbacks: Any | None = Field(default=None, description=_CALLBACKS_DESCRIPTION)  # noqa: ANN401
    constraints: list[_ConstraintLike] | None = Field(
        default=None, description=_CONSTRAINTS_DESCRIPTION
    )
    penalties: list[_PenaltyLike] | None = Field(
        default=None, description=_PENALTIES_DESCRIPTION
    )
    custom_parameters: dict[str, Any] | None = Field(
        default=None, description=_CUSTOM_PARAMETERS_DESCRIPTION
    )
    parameters: ParameterValuesLike | None = Field(
        default=None, description=_PARAMETERS_DESCRIPTION
    )

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


class ElectrodeBalancingHalfCell(FittingObjective):
    """Find the starting capacity and total capacity of one electrode, given a
    known OCV function for that electrode.

    Useful for aligning a fresh experiment (for example a GITT scan) to a
    previously measured OCV curve — the fit slides and scales the data so
    it lines up with the OCV in stoichiometry.

    Parameters
    ----------
    electrode : str
        The electrode to fit — ``"positive"`` or ``"negative"``.
    data_input : DataLoader, DataFrame, str, or dict
        The half-cell data — see :class:`FittingObjective`.
    options : dict, optional
        Settings:

            * ``direction`` (str): ``"lithiation"`` or ``"delithiation"`` —
                direction of the OCP. Default ``None`` (no direction assumed).
    callbacks, constraints, penalties, parameters
        Shared with :class:`BaseObjective`.

    Examples
    --------
    >>> obj = iws.objectives.ElectrodeBalancingHalfCell(
    ...     electrode="positive",
    ...     data_input="path/to/half_cell.csv",
    ... )
    >>> # slot into a DataFit (parameters omitted for brevity)"""

    electrode: Electrode = Field(..., description=_ELECTRODE_DESCRIPTION)
    data_input: MeasurementInput = Field(
        ..., alias="data", description=_DATA_INPUT_DESCRIPTION
    )
    options: dict[str, Any] | None = Field(
        default=None,
        description=(
            "Electrode-balancing-half-cell objective options. Supported "
            "keys: ``direction`` (``'lithiation'`` or ``'delithiation'`` — "
            "direction of the OCP; default None, meaning no direction is "
            "assumed)."
        ),
    )
    callbacks: Any | None = Field(default=None, description=_CALLBACKS_DESCRIPTION)  # noqa: ANN401
    custom_parameters: dict[str, Any] | None = Field(
        default=None, description=_CUSTOM_PARAMETERS_DESCRIPTION
    )
    constraints: list[_ConstraintLike] | None = Field(
        default=None, description=_CONSTRAINTS_DESCRIPTION
    )
    penalties: list[_PenaltyLike] | None = Field(
        default=None, description=_PENALTIES_DESCRIPTION
    )
    parameters: ParameterValuesLike | None = Field(
        default=None, description=_PARAMETERS_DESCRIPTION
    )

    def __init__(
        self,
        electrode,
        data_input,
        options=None,
        callbacks=None,
        custom_parameters=None,
        constraints=None,
        penalties=None,
        parameters=None,
    ):
        super().__init__(
            electrode=electrode,
            data_input=data_input,
            options=options,
            callbacks=callbacks,
            custom_parameters=custom_parameters,
            constraints=constraints,
            penalties=penalties,
            parameters=parameters,
        )


class MSMRFullCell(FittingObjective):
    """Fit an MSMR model to full-cell open-circuit voltage data.

    Compares both the capacity-vs-voltage curve and the differential
    voltage ``dU/dQ`` of the full cell — fitting both together gives much
    tighter constraints on the underlying half-cell MSMR parameters than
    fitting the OCV alone [1]_.

    Parameters
    ----------
    data_input : DataLoader, DataFrame, str, or dict
        The full-cell OCV data — see :class:`FittingObjective`.
    options : dict, optional
        MSMR full-cell settings:

            * ``model``: the full-cell OCV model. Defaults to
                :class:`MSMRFullCellModel` with both electrodes set to
                :class:`MSMRHalfCellModel` using ``"Xj"`` species format.
            * ``dUdQ cutoff``: clip data points with very large ``dU/dQ``
                near the voltage limits. ``"none"`` disables it, a float
                sets a fixed cutoff, a function is called on the data to
                derive one. Defaults to an automatic cutoff function.
            * ``negative voltage limits`` (required): tuple of voltage
                limits for the negative electrode.
            * ``positive voltage limits`` (required): tuple of voltage
                limits for the positive electrode.
    callbacks, constraints, penalties, parameters
        Shared with :class:`BaseObjective`.

    References
    ----------
    .. [1] Hu, Victor W., and Daniel T. Schwartz. Low error estimation of half-cell
        thermodynamic parameters from whole-cell Li-ion battery experiments: Physics-based
        model formulation, experimental demonstration, and an open software tool. Journal
        of The Electrochemical Society 169.3 (2022): 030539.

    Examples
    --------
    >>> obj = iws.objectives.MSMRFullCell(
    ...     data_input="path/to/full_cell_ocv.csv",
    ...     options={
    ...         "negative voltage limits": (0.005, 1.5),
    ...         "positive voltage limits": (3.0, 4.3),
    ...     },
    ... )
    >>> # slot into a DataFit (parameters omitted for brevity)"""

    data_input: MeasurementInput = Field(
        ..., alias="data", description=_DATA_INPUT_DESCRIPTION
    )
    options: dict[str, Any] | None = Field(
        default=None,
        description=(
            "MSMR full-cell objective options. Supported keys: ``model`` "
            "(full-cell OCV model; defaults to ``MSMRFullCellModel`` pairing "
            "two ``MSMRHalfCellModel`` instances with ``'Xj'`` species "
            "format), ``dUdQ cutoff`` (``'none'``, a float, or a function "
            "called on the data to derive a cutoff; defaults to an automatic "
            "cutoff function), ``negative voltage limits`` (required tuple), "
            "and ``positive voltage limits`` (required tuple)."
        ),
    )
    callbacks: Any | None = Field(default=None, description=_CALLBACKS_DESCRIPTION)  # noqa: ANN401
    constraints: list[_ConstraintLike] | None = Field(
        default=None, description=_CONSTRAINTS_DESCRIPTION
    )
    penalties: list[_PenaltyLike] | None = Field(
        default=None, description=_PENALTIES_DESCRIPTION
    )
    custom_parameters: dict[str, Any] | None = Field(
        default=None, description=_CUSTOM_PARAMETERS_DESCRIPTION
    )
    parameters: ParameterValuesLike | None = Field(
        default=None, description=_PARAMETERS_DESCRIPTION
    )

    def __init__(
        self,
        data_input,
        options=None,
        callbacks=None,
        constraints=None,
        penalties=None,
        custom_parameters=None,
        parameters=None,
    ):
        super().__init__(
            data_input=data_input,
            options=options,
            callbacks=callbacks,
            constraints=constraints,
            penalties=penalties,
            custom_parameters=custom_parameters,
            parameters=parameters,
        )


class MSMRHalfCell(FittingObjective):
    """Fit an MSMR model to half-cell open-circuit potential data.

    Compares the capacity-vs-voltage curve and (optionally) the
    differential voltage ``dU/dQ`` of one electrode to a measured
    half-cell OCP.

    Parameters
    ----------
    data_input : DataLoader, DataFrame, str, or dict
        The half-cell OCP data — see :class:`FittingObjective`.
    options : dict, optional
        MSMR half-cell settings:

            * ``model``: the half-cell OCP model. Defaults to
                :class:`MSMRHalfCellModel` for the specified electrode.
                The model class controls the species format, direction and
                capacity function.
            * ``voltage limits``: tuple of voltage limits to fit over.
                Defaults to the range present in the data.
            * ``dUdQ cutoff``: clip data points with very large ``dU/dQ``
                near the voltage limits. ``"none"`` disables it, a float
                sets a fixed cutoff, a function is called on the data to
                derive one. Defaults to an automatic cutoff function.
            * ``dQdU cutoff``: same idea as ``dUdQ cutoff`` but on
                ``dQ/dU``. Defaults to ``None``.
            * ``objective variables`` (list of str): variables compared by
                the fit. Defaults to
                ``["Capacity [A.h]", "Differential voltage [V/Ah]"]``.
            * ``GITT`` (bool): set ``True`` for sparse GITT data so it can
                be interpolated and upsampled first. Default ``False``.
            * ``constrain Xj method``: how to constrain the Xj parameters to
                sum to 1 — ``"explicit"`` (adds an equality constraint) or
                ``"reformulate"`` (eliminates the last Xj by substitution).
                Default ``"explicit"``. Only used with the ``"Xj"`` species
                format.
            * ``preserve U0j order`` (bool): if ``True``, add inequality
                constraints to keep the U0j parameters in descending order.
                Default ``False`` — initial values must already be in
                descending order if this is enabled.
    callbacks, constraints, penalties, parameters
        Shared with :class:`BaseObjective`.

    Examples
    --------
    >>> obj = iws.objectives.MSMRHalfCell(
    ...     data_input="path/to/half_cell.csv",
    ...     options={"electrode": "positive"},
    ... )
    >>> # slot into a DataFit (parameters omitted for brevity)"""

    data_input: MeasurementInput = Field(
        ..., alias="data", description=_DATA_INPUT_DESCRIPTION
    )
    options: dict[str, Any] | None = Field(
        default=None,
        description=(
            "MSMR half-cell objective options. Supported keys: ``model`` "
            "(half-cell OCP model; defaults to ``MSMRHalfCellModel`` for "
            "the specified electrode), ``voltage limits`` (tuple to fit "
            "over; defaults to the data range), ``dUdQ cutoff`` and "
            "``dQdU cutoff`` (``'none'``, float, or function — defaults to "
            "an automatic cutoff for ``dUdQ`` and ``None`` for ``dQdU``), "
            "``objective variables`` (list of variables to compare; "
            'defaults to ["Capacity [A.h]", "Differential voltage [V/Ah]"]), '
            "``GITT`` (bool — interpolate/upsample sparse GITT data; "
            "default False), ``constrain Xj method`` (``'explicit'`` or "
            "``'reformulate'``; default ``'explicit'``; only used with "
            "``'Xj'`` species format), and ``preserve U0j order`` (bool — "
            "add inequality constraints to keep U0j parameters in "
            "descending order; default False)."
        ),
    )
    callbacks: Any | None = Field(default=None, description=_CALLBACKS_DESCRIPTION)  # noqa: ANN401
    constraints: list[_ConstraintLike] | None = Field(
        default=None, description=_CONSTRAINTS_DESCRIPTION
    )
    penalties: list[_PenaltyLike] | None = Field(
        default=None, description=_PENALTIES_DESCRIPTION
    )
    custom_parameters: dict[str, Any] | None = Field(
        default=None, description=_CUSTOM_PARAMETERS_DESCRIPTION
    )
    parameters: ParameterValuesLike | None = Field(
        default=None, description=_PARAMETERS_DESCRIPTION
    )

    def __init__(
        self,
        data_input,
        options=None,
        callbacks=None,
        constraints=None,
        penalties=None,
        custom_parameters=None,
        parameters=None,
    ):
        super().__init__(
            data_input=data_input,
            options=options,
            callbacks=callbacks,
            constraints=constraints,
            penalties=penalties,
            custom_parameters=custom_parameters,
            parameters=parameters,
        )


class OCPHalfCell(FittingObjective):
    """Fit a smooth open-circuit-potential function to half-cell OCP data.

    Parameters
    ----------
    electrode : str
        The electrode to fit — ``"positive"`` or ``"negative"``.
    data_input : DataLoader, DataFrame, str, or dict
        The half-cell OCP data — see :class:`FittingObjective`.
    options : dict, optional
        OCP fitting settings:

            * ``theta_ref`` (float): reference lithiation used to map
                between capacity and stoichiometry ``theta``.

                For the **positive** electrode the reference defaults to ``1``
                at the lowest potential in the data (we assume the electrode
                is fully lithiated there), giving ``0 <= theta <= theta_ref``.

                For the **negative** electrode the reference defaults to ``0``
                at the highest potential in the data (we assume the electrode
                is fully delithiated there), giving ``theta_ref <= theta <= 1``.
            * ``stoichiometry limits`` (2-tuple of floats): stoichiometry
                range used by the fit. Default ``(0, 1)`` — the whole range.
                If the fit struggles near the endpoints, narrow this to
                e.g. ``(0.02, 0.98)`` or ``(0.05, 0.95)``.
            * ``voltage limits`` (2-tuple of floats): voltage range used by
                the fit. Default ``None`` (uses the full data range).
            * ``dUdQ cutoff`` (float): ignore data points with very large
                ``dU/dQ`` near the limits. Default ``None``.
            * ``direction`` (str): ``"lithiation"`` or ``"delithiation"`` —
                direction of the OCP. Default ``None`` (no direction assumed).
    callbacks, constraints, penalties, parameters
        Shared with :class:`BaseObjective`.

    Examples
    --------
    >>> obj = iws.objectives.OCPHalfCell(
    ...     electrode="positive",
    ...     data_input="path/to/ocp.csv",
    ...     options={"stoichiometry limits": (0.05, 0.95)},
    ... )
    >>> # slot into a DataFit (parameters omitted for brevity)
    """

    electrode: Electrode = Field(..., description=_ELECTRODE_DESCRIPTION)
    data_input: MeasurementInput = Field(
        ..., alias="data", description=_DATA_INPUT_DESCRIPTION
    )
    options: dict[str, Any] | None = Field(
        default=None,
        description=(
            "OCP half-cell objective options. Supported keys: ``theta_ref`` "
            "(float — reference lithiation mapping capacity to ``theta``; "
            "positive electrode defaults so that ``0 <= theta <= theta_ref``, "
            "negative electrode defaults so that ``theta_ref <= theta <= 1``), "
            "``stoichiometry limits`` (2-tuple of floats — stoichiometry "
            "range; default ``(0, 1)``), ``voltage limits`` (2-tuple of "
            "floats — voltage range; default None, uses full data range), "
            "``dUdQ cutoff`` (float — ignore data points with very large "
            "``dU/dQ`` near the limits; default None), and ``direction`` "
            "(``'lithiation'`` or ``'delithiation'`` — direction of the "
            "OCP; default None, no direction assumed)."
        ),
    )
    callbacks: Any | None = Field(default=None, description=_CALLBACKS_DESCRIPTION)  # noqa: ANN401
    custom_parameters: dict[str, Any] | None = Field(
        default=None, description=_CUSTOM_PARAMETERS_DESCRIPTION
    )
    constraints: list[_ConstraintLike] | None = Field(
        default=None, description=_CONSTRAINTS_DESCRIPTION
    )
    penalties: list[_PenaltyLike] | None = Field(
        default=None, description=_PENALTIES_DESCRIPTION
    )
    parameters: ParameterValuesLike | None = Field(
        default=None, description=_PARAMETERS_DESCRIPTION
    )

    def __init__(
        self,
        electrode,
        data_input,
        options=None,
        callbacks=None,
        custom_parameters=None,
        constraints=None,
        penalties=None,
        parameters=None,
    ):
        super().__init__(
            electrode=electrode,
            data_input=data_input,
            options=options,
            callbacks=callbacks,
            custom_parameters=custom_parameters,
            constraints=constraints,
            penalties=penalties,
            parameters=parameters,
        )


class Objective(FittingObjective):
    """Deprecated alias for `FittingObjective`."""

    pass


class Pulse(SimulationObjective):
    """Fit a model against pulse experiments — GITT, HPPC, ICI, and similar.

    By default the fit compares simulated voltage against measured voltage,
    but you can swap in a different ``objective variables`` function to
    compare overpotentials, resistances, or ICI/GITT features instead.

    Parameters
    ----------
    data_input : DataLoader, DataFrame, str, or dict
        The pulse data — see :class:`FittingObjective`.
    options : dict, optional
        Pulse-fitting settings:

            * ``model`` (required): the pybamm model to fit.
            * ``simulation_kwargs`` (dict): kwargs forwarded to the
                simulation. May include ``solver_kwargs`` to tune the auto-built
                solver (e.g. ``{"options": {"compile": True}}`` to enable
                compilation), ignored if an explicit ``solver`` is also provided.
                May also include ``solve_kwargs`` forwarded to the runtime
                solve regardless of the solver (e.g. ``starting_solution``).
                Defaults to ``None``.
            * ``objective variables`` (callable): function returning the
                dict of variables the fit compares. Defaults to
                ``voltage_objective_variables`` (compares voltage). Other
                useful options:

                    * ``overpotential_objective_variables`` — overpotential
                        sampled at various points in the pulses.
                    * ``resistances_objective_variables`` — resistance
                        sampled at various points in the pulses.
                    * ``ici_features_objective_variables`` — ICI features
                        (concentration overpotential and ICI square-root
                        slope).
                    * ``gitt_features_objective_variables`` — GITT features
                        (concentration overpotential, relaxation time, ohmic
                        voltage drop, GITT and ICI square-root slopes).
            * ``interpolant_atol`` / ``interpolant_rtol`` (float): tolerances
                for the current interpolant. Default to the solver's
                ``atol``/``rtol`` if a solver is supplied in
                ``simulation_kwargs``, otherwise ``1e-6`` and ``1e-4``.
            * ``interactive_preprocessing``: not supported in schema-built
                configs — raises a ``ValueError`` if set. The underlying
                pipeline option opens a local matplotlib UI, which is
                unavailable when the config runs server-side or in a
                notebook.
            * ``solver_max_save_points`` (int): cap on solver save points.
                Disabled by default.
    callbacks, constraints, penalties, parameters
        Shared with :class:`BaseObjective`.

    Examples
    --------
    >>> obj = iws.objectives.Pulse(data_input="path/to/gitt.csv")
    >>> # slot into a DataFit (parameters omitted for brevity)"""

    data_input: MeasurementInput = Field(
        ..., alias="data", description=_DATA_INPUT_DESCRIPTION
    )
    options: dict[str, Any] | None = Field(
        default=None,
        description=(
            "Pulse objective options. Supported keys: ``model`` (required "
            "pybamm model), ``simulation_kwargs`` (kwargs forwarded to "
            "``iwp.Simulation``; default None), ``objective variables`` "
            "(callable returning the dict of variables compared; defaults "
            "to ``voltage_objective_variables``; other useful options are "
            "``overpotential_objective_variables``, "
            "``resistances_objective_variables``, "
            "``ici_features_objective_variables``, "
            "``gitt_features_objective_variables``), "
            "``interpolant_atol`` / ``interpolant_rtol`` (tolerances for "
            "the current interpolant; default to solver ``atol``/``rtol`` "
            "if a solver is supplied, otherwise ``1e-6`` / ``1e-4``), "
            "and "
            "``solver_max_save_points`` (max solver save points; disabled "
            "by default). ``simulation_kwargs`` may include ``solver_kwargs`` to tune the "
            "auto-built solver (e.g. ``{'options': {'compile': True}}`` to "
            "enable compilation; ignored if an explicit ``solver`` is also provided) "
            "and ``solve_kwargs`` forwarded to the runtime solve regardless of "
            "the solver (e.g. ``starting_solution``)."
        ),
    )
    _validate_options = field_validator("options")(_reject_interactive_preprocessing)
    callbacks: Any | None = Field(default=None, description=_CALLBACKS_DESCRIPTION)  # noqa: ANN401
    custom_parameters: dict[str, Any] | None = Field(
        default=None, description=_CUSTOM_PARAMETERS_DESCRIPTION
    )
    constraints: list[_ConstraintLike] | None = Field(
        default=None, description=_CONSTRAINTS_DESCRIPTION
    )
    penalties: list[_PenaltyLike] | None = Field(
        default=None, description=_PENALTIES_DESCRIPTION
    )
    parameters: ParameterValuesLike | None = Field(
        default=None, description=_PARAMETERS_DESCRIPTION
    )

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
    """Fit a cell-resistance curve against measured resistance vs SOC.

    Parameters
    ----------
    data_input : DataLoader, DataFrame, str, or dict
        Resistance data — see :class:`FittingObjective`. Must contain
        columns ``"SOC"`` and ``"Resistance [Ohm]"``, plus any extra
        columns the resistance model needs.
    options : dict, optional
        Resistance-fit settings:

            * ``model`` (required): the pybamm model to fit.
    callbacks, constraints, penalties, parameters
        Shared with :class:`BaseObjective`.

    Examples
    --------
    >>> obj = iws.objectives.Resistance(data_input="path/to/resistance.csv")
    >>> # slot into a DataFit (parameters omitted for brevity)"""

    data_input: MeasurementInput = Field(
        ..., alias="data", description=_DATA_INPUT_DESCRIPTION
    )
    options: dict[str, Any] | None = Field(
        default=None,
        description=(
            "Resistance objective options. Supported keys: ``model`` "
            "(required pybamm model — no default)."
        ),
    )
    callbacks: Any | None = Field(default=None, description=_CALLBACKS_DESCRIPTION)  # noqa: ANN401
    custom_parameters: dict[str, Any] | None = Field(
        default=None, description=_CUSTOM_PARAMETERS_DESCRIPTION
    )
    constraints: list[_ConstraintLike] | None = Field(
        default=None, description=_CONSTRAINTS_DESCRIPTION
    )
    penalties: list[_PenaltyLike] | None = Field(
        default=None, description=_PENALTIES_DESCRIPTION
    )
    parameters: ParameterValuesLike | None = Field(
        default=None, description=_PARAMETERS_DESCRIPTION
    )

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
