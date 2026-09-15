"""Schemas for models."""

from collections.abc import Callable
from typing import Annotated, Any, Literal

from pydantic import ConfigDict, Field

from .._types import Electrode
from ..base import BaseSchema
from .simulation_settings import SimulationSettingsLike

# An ``MSMRHalfCellModel`` schema instance or its config-dict equivalent.
_HalfCellModelLike = Annotated[
    dict[str, Any] | BaseSchema,
    Field(union_mode="left_to_right"),
]


class _ModelOptions(BaseSchema):
    """Base for a model's typed ``options`` bag.

    A model's ``options`` are merged over the runtime model's own defaults, so
    ``to_config`` emits only the keys the caller set (``_only_set_fields``) and
    no ``type`` discriminator (``_emit_type``) — the output is a plain option
    dict the runtime consumes. Unknown keys are rejected (``extra="forbid"``
    from :class:`BaseSchema`), so a misspelt option fails when you build the
    model rather than being silently dropped.
    """

    _emit_type: bool = False
    _only_set_fields: bool = True


class ECMOptions(_ModelOptions):
    """Options for an :class:`ECM` model. See :class:`ECM` for the physical
    meaning of each key."""

    thermal: Literal["isothermal", "lumped", "two-state"] = Field(
        default="isothermal", description="Thermal submodel."
    )
    rc_pairs: str = Field(
        default="0",
        alias="rc pairs",
        pattern=r"^\d+$",
        description="Number of RC pairs, as a non-negative integer string.",
    )
    capacity: Literal["constant", "function"] = Field(
        default="constant",
        description=(
            "Capacity-degradation model. When 'function', supply the parameter "
            "'Capacity [A.h]' as a function of the degradation inputs; pass a "
            "constant function (e.g. lambda *args: 5.0) for no fade. 'constant' "
            "fixes it at 'Nominal cell capacity [A.h]'."
        ),
    )
    resistance_scale: Literal["constant", "function"] = Field(
        default="constant",
        alias="resistance scale",
        description=(
            "Resistance-growth model. When 'function', all resistances R0 and "
            "R_rc are multiplied by a dimensionless user-supplied 'Resistance "
            "scale' factor (capacitances C_rc are not scaled, so an RC-pair "
            "resistance change also scales its time constant R_rc*C_rc); "
            "'constant' leaves them unchanged."
        ),
    )
    butler_volmer: Literal["false", "true"] = Field(
        default="false",
        alias="butler-volmer",
        description=(
            "Whether to add a Butler-Volmer charge-transfer overpotential. When "
            "'true', adds a symmetric charge-transfer overpotential "
            "eta_ct = (2*R*T/F)*asinh(I/(2*i0)) using the 'Exchange current [A]' "
            "parameter i0, exposed as 'Charge-transfer overpotential [V]'. The "
            "resistance-scale factor does not apply to this term."
        ),
    )
    parameter_dependencies: dict[str, Any] | None = Field(
        default=None,
        description=(
            "Per-parameter state dependencies for the degradation/kinetics terms "
            "(keys OCV, R0, R_rc, C_rc, i0). Validated by the runtime model. A "
            "degradation function receives the inputs 'Capacity throughput [A.h]' "
            "and 'Time [s]' (monotonic accumulators) as positional args. The 'i0' "
            "key defaults to ('soc',) even when omitted, so pre-existing configs "
            "don't flatten the Butler-Volmer term; pass 'i0': () for a constant "
            "exchange current."
        ),
    )


class LumpedSPMROptions(_ModelOptions):
    """Options for a :class:`LumpedSPMR` (and :class:`LumpedSPMeR`) model."""

    thermal: Literal["isothermal", "lumped"] = Field(
        default="isothermal", description="Thermal submodel."
    )
    surface_temperature: Literal["ambient", "lumped"] = Field(
        default="ambient",
        alias="surface temperature",
        description="Surface-temperature submodel.",
    )
    working_electrode: Literal["both"] = Field(
        default="both",
        alias="working electrode",
        description="Cell configuration. Only 'both' (full cell) is supported.",
    )


class SingleElectrodeLumpedSPMROptions(_ModelOptions):
    """Options for a :class:`SingleElectrodeLumpedSPMR` model."""

    thermal: Literal["isothermal", "lumped"] = Field(
        default="isothermal", description="Thermal submodel."
    )
    surface_temperature: Literal["ambient", "lumped"] = Field(
        default="ambient",
        alias="surface temperature",
        description="Surface-temperature submodel.",
    )
    rc_pairs: str = Field(
        default="0",
        alias="rc pairs",
        pattern=r"^\d+$",
        description="Number of RC pairs, as a non-negative integer string.",
    )
    parameter_dependencies: dict[str, Any] | None = Field(
        default=None,
        description=(
            "Per-parameter state dependencies (keys tau, R_rc, C_rc). "
            "Validated by the runtime model."
        ),
    )


class MSMRHalfCellModelOptions(_ModelOptions):
    """Options for a :class:`MSMRHalfCellModel`."""

    # Callables can't be serialised, so drop them from to_config — the runtime
    # to_config filters to str/int/float/bool for the same reason.
    _exclude_fields: set = {"capacity_function", "differential_capacity_function"}

    capacity_function: Callable | None = Field(
        default=None,
        alias="capacity function",
        description=(
            "Capacity function. A live callable used locally only; it is dropped "
            "by to_config/from_schema and never reaches the runtime over the wire."
        ),
    )
    differential_capacity_function: Callable | None = Field(
        default=None,
        alias="differential capacity function",
        description=(
            "Differential-capacity function. Same local-only callable caveat as "
            "capacity_function."
        ),
    )
    species_format: Literal["Qj", "Xj"] = Field(
        default="Qj",
        alias="species format",
        description=(
            "How each MSMR species is parameterised: 'Qj' (capacity) or 'Xj' "
            "(mole fraction)."
        ),
    )
    direction: Literal["delithiation", "lithiation"] | None = Field(
        default=None,
        description="Reaction direction, or None for no direction assumed.",
    )
    particle_phases: Literal["1", "2"] = Field(
        default="1",
        alias="particle phases",
        description="Number of electrode phases: '1' (single-phase) or '2' (composite).",
    )


class GITTModelOptions(_ModelOptions):
    """Options for a :class:`GITTModel`.

    A hybrid bag: ``working electrode`` is typed, and any other key is forwarded
    to the underlying pybamm ``BatteryModelOptions`` unchanged (``extra=allow``).
    """

    # Non-"working electrode" keys pass through to pybamm's BatteryModelOptions,
    # so extras are allowed rather than rejected (registered on the strictness
    # guard's allowlist for this reason).
    model_config = ConfigDict(extra="allow")

    working_electrode: Literal["both", "positive"] = Field(
        default="both",
        alias="working electrode",
        description=(
            "Cell configuration: 'both' (full cell) or 'positive' (half cell "
            "against a lithium-metal counter electrode)."
        ),
    )


class MSMRFullCellModel(BaseSchema):
    """Full-cell MSMR model of the open-circuit potential — pairs a negative and
    positive half-cell MSMR model into one full-cell OCV.

    Use this with :class:`MSMRFullCell` to fit an MSMR description of a
    full cell from full-cell OCV data.

    Parameters
    ----------
    negative_electrode_model : :class:`MSMRHalfCellModel`
        MSMR model for the negative electrode.
    positive_electrode_model : :class:`MSMRHalfCellModel`
        MSMR model for the positive electrode.
    options : dict, optional
        Extra options forwarded to the underlying model.
    simulation_settings : :class:`SimulationSettings` or dict, optional
        Persistent simulation settings (mesh + solver) re-applied at simulation
        time. When ``None`` the model defaults are used."""

    negative_electrode_model: _HalfCellModelLike = Field(...)
    positive_electrode_model: _HalfCellModelLike = Field(...)
    options: dict[str, Any] | None = Field(default=None)
    simulation_settings: SimulationSettingsLike | None = Field(default=None)

    def __init__(
        self,
        negative_electrode_model,
        positive_electrode_model,
        options=None,
        simulation_settings=None,
    ):
        super().__init__(
            negative_electrode_model=negative_electrode_model,
            positive_electrode_model=positive_electrode_model,
            options=options,
            simulation_settings=simulation_settings,
        )


class MSMRHalfCellModel(BaseSchema):
    """Half-cell MSMR (Multi-Species Multi-Reaction) model for one electrode's
    open-circuit potential.

    Parameters
    ----------
    electrode : str
        Electrode the model describes — ``"positive"`` or ``"negative"``.
    options : MSMRHalfCellModelOptions or dict, optional
        See :class:`MSMRHalfCellModelOptions` for the available keys.
    simulation_settings : :class:`SimulationSettings` or dict, optional
        Persistent simulation settings (mesh + solver) re-applied at simulation
        time. When ``None`` the model defaults are used.

    For a composite electrode (``particle phases`` = ``"2"``) the lower excess
    may be given either as a per-phase split (``Primary/Secondary: {Electrode}
    electrode lower excess capacity [A.h]``, summed) when it is known from
    another source, or as a single electrode-level ``{Electrode} electrode
    lower excess capacity [A.h]`` when it is not."""

    electrode: Electrode = Field(...)
    options: MSMRHalfCellModelOptions | None = Field(default=None)
    simulation_settings: SimulationSettingsLike | None = Field(default=None)

    def __init__(self, electrode, options=None, simulation_settings=None):
        super().__init__(
            electrode=electrode,
            options=options,
            simulation_settings=simulation_settings,
        )


class GITTModel(BaseSchema):
    """Diffusion-only model for fitting solid diffusivities to GITT or pulse data.

    The model solves x-averaged spherical particle diffusion in each modelled
    electrode, with the surface flux set by the applied current, and computes the
    cell voltage from the electrode open-circuit potentials evaluated at the
    particle surface stoichiometries, minus an ohmic drop through a single lumped
    ``"Ohmic resistance [Ohm]"`` parameter. There are no reaction kinetics
    (Butler-Volmer), no electrolyte dynamics, and no thermal effects; all
    parameters are constant except the open-circuit potentials.

    The ``"working electrode"`` option selects the cell configuration:

    - ``"both"`` (default): full cell. Both electrodes are modelled and the
      voltage is the difference of their open-circuit potentials minus the ohmic
      drop. A positive (discharge) current delithiates the negative electrode and
      lithiates the positive electrode.
    - ``"positive"``: half-cell against a lithium-metal counter electrode,
      following the pybamm half-cell convention. Only the working electrode is
      modelled (the counter electrode contributes no overpotential) and the
      voltage is its open-circuit potential minus the ohmic drop. A positive
      (discharge) current lithiates the working electrode. As in pybamm,
      anode-material half cells are also expressed with ``"positive"`` — rename
      the anode's parameters to the positive convention first.

    This is a fitting model intended for extracting solid-phase diffusivities
    (and the lumped ohmic resistance) from GITT or pulse-relaxation measurements
    — it is not a general-purpose simulation model. Each modelled electrode is
    parameterised with the standard full-cell parameter names (thickness, active
    material volume fraction, particle radius, diffusivity, OCP, maximum and
    initial concentrations) plus the current function, electrode cross-sectional
    area, initial temperature, and ``"Ohmic resistance [Ohm]"``.

    Parameters
    ----------
    options : GITTModelOptions or dict, optional
        See :class:`GITTModelOptions` for the available keys.
    simulation_settings : :class:`SimulationSettings` or dict, optional
        Persistent simulation settings (mesh + solver) re-applied at simulation
        time. When ``None`` the model defaults are used."""

    options: GITTModelOptions | None = Field(default=None)
    simulation_settings: SimulationSettingsLike | None = Field(default=None)

    def __init__(self, options=None, simulation_settings=None):
        super().__init__(options=options, simulation_settings=simulation_settings)


class LumpedSPMR(BaseSchema):
    """A class for the Lumped Single Particle Model with Resistance."""

    options: LumpedSPMROptions | None = Field(default=None)
    simulation_settings: SimulationSettingsLike | None = Field(default=None)

    def __init__(self, options=None, simulation_settings=None):
        super().__init__(options=options, simulation_settings=simulation_settings)


class LumpedSPMeR(BaseSchema):
    """A class for the Lumped Single Particle Model with electrolyte and Resistance."""

    options: LumpedSPMROptions | None = Field(default=None)
    simulation_settings: SimulationSettingsLike | None = Field(default=None)

    def __init__(self, options=None, simulation_settings=None):
        super().__init__(options=options, simulation_settings=simulation_settings)


class SingleElectrodeLumpedSPMR(BaseSchema):
    """A class for the single-electrode Lumped SPM with Resistance."""

    options: SingleElectrodeLumpedSPMROptions | None = Field(default=None)
    simulation_settings: SimulationSettingsLike | None = Field(default=None)

    def __init__(self, options=None, simulation_settings=None):
        super().__init__(options=options, simulation_settings=simulation_settings)


class ECM(BaseSchema):
    """A class for the Equivalent Circuit Model.

    Parameters
    ----------
    options : ECMOptions or dict, optional
        See :class:`ECMOptions` for the available keys.
    simulation_settings : :class:`SimulationSettings` or dict, optional
        Persistent simulation settings (mesh + solver) re-applied at simulation
        time. When ``None`` the model defaults are used.
    """

    options: ECMOptions | None = Field(default=None)
    simulation_settings: SimulationSettingsLike | None = Field(default=None)

    def __init__(self, options=None, simulation_settings=None):
        super().__init__(options=options, simulation_settings=simulation_settings)
