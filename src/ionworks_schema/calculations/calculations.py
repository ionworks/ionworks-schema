"""Schemas for calculations."""

from typing import Any, Literal

from pydantic import Field, model_validator

from .._types import ElectrodeOrLumped, MeasurementInput, NumberLike
from ..base import BaseSchema

# Empty string preserves the existing parser default.
_Direction = Literal["", "delithiation", "lithiation"]
_Phase = Literal["", "primary", "secondary"]
_LimitsPair = tuple[NumberLike, NumberLike] | list[NumberLike]

# Typed ``options`` bags for calculations (issue #1423). The ``phase`` /
# ``direction`` option keys default to ``None`` (no assumption), distinct from
# the module-level ``_Phase`` / ``_Direction`` construction-arg aliases above,
# which encode an empty-string default.
_ParticlePhasesPair = tuple[Literal["1", "2"], Literal["1", "2"]]
_Interpolator = Literal["linear", "cubic", "pchip"]


class _CalculationOptions(BaseSchema):
    """Base for a calculation's typed ``options`` bag.

    Merged over the runtime calculation's own defaults, so ``to_config`` emits
    only the keys the caller set (``_only_set_fields``) and no ``type``
    discriminator (``_emit_type``). Unknown keys are rejected (``extra="forbid"``
    from :class:`BaseSchema`), so a misspelt option fails at construction. Keys
    do not accumulate across calculations — each declares only its own.
    """

    _emit_type: bool = False
    _only_set_fields: bool = True


class ElectrodeSOHOptions(_CalculationOptions):
    """Options for :class:`ElectrodeSOH`."""

    known_value: Literal["cyclable lithium capacity", "cell capacity"] = Field(
        default="cyclable lithium capacity",
        alias="known value",
        description="Which capacity measure is known.",
    )


class AverageMSMRParametersOptions(_CalculationOptions):
    """Options for :class:`AverageMSMRParameters`."""

    species_format: Literal["Xj", "Qj"] = Field(
        default="Xj", description="MSMR species parameterisation."
    )
    phase: Literal["primary", "secondary"] | None = Field(
        default=None, description="Electrode phase."
    )


class CyclableLithiumOptions(_CalculationOptions):
    """Options for :class:`CyclableLithium`."""

    particle_phases: _ParticlePhasesPair = Field(
        default=("1", "1"),
        alias="particle phases",
        description="Phases in the (negative, positive) electrodes.",
    )


class InitialSOCfromMaximumStoichiometryOptions(_CalculationOptions):
    """Options for :class:`InitialSOCfromMaximumStoichiometry`."""

    particle_phases: _ParticlePhasesPair = Field(
        default=("1", "1"),
        alias="particle phases",
        description="Phases in the (negative, positive) electrodes.",
    )
    include_concentration: Literal["true", "false"] = Field(
        default="true",
        alias="include concentration",
        description="Whether to also set initial concentrations.",
    )


class StoichiometryLimitsFromCapacityOptions(_CalculationOptions):
    """Options for :class:`StoichiometryLimitsFromCapacity`."""

    direction: Literal["charge", "discharge"] | None = Field(
        default=None,
        description=(
            "OCV scan direction. When set, the lower/upper excess capacities are "
            "computed based on the direction."
        ),
    )
    particle_phases: _ParticlePhasesPair = Field(
        default=("1", "1"),
        alias="particle phases",
        description="Phases in the (negative, positive) electrodes.",
    )
    negative_voltage_limits: tuple[float, float] = Field(
        default=(0.0, 2.0),
        alias="negative voltage limits",
        description=(
            "(low, high) negative-electrode potential bracket used to solve the "
            "shared window when the negative electrode is composite."
        ),
    )
    positive_voltage_limits: tuple[float, float] = Field(
        default=(2.5, 5.0),
        alias="positive voltage limits",
        description=(
            "(low, high) positive-electrode potential bracket used to solve the "
            "shared window when the positive electrode is composite."
        ),
    )
    usable_capacity: float | None = Field(
        default=None,
        alias="usable capacity",
        description=(
            "Usable capacity to solve the composite window against. Required when "
            "either electrode is composite ('particle phases' contains '2'). This "
            "is per direction: a joint-hysteresis fit uses a different usable "
            "capacity for charge vs discharge, so run one calculation per "
            "direction with that direction's value."
        ),
    )

    @model_validator(mode="after")
    def _require_usable_capacity_when_composite(self):
        if "2" in self.particle_phases and self.usable_capacity is None:
            raise ValueError(
                "'usable capacity' is required when either electrode is composite "
                "('particle phases' contains '2')."
            )
        return self


class InitialConcentrationFromInitialStoichiometryHalfCellOptions(_CalculationOptions):
    """Options for :class:`InitialConcentrationFromInitialStoichiometryHalfCell`."""

    phase: Literal["primary", "secondary"] | None = Field(
        default=None, description="Electrode phase."
    )


class InitialSOCHalfCellOptions(_CalculationOptions):
    """Options for :class:`InitialSOCHalfCell`."""

    phase: Literal["primary", "secondary"] | None = Field(
        default=None, description="Electrode phase."
    )


class MSMRDiffusivityOptions(_CalculationOptions):
    """Options for the MSMR-diffusivity calculations (plain/Arrhenius, data/function)."""

    interpolator: _Interpolator = Field(
        default="linear", description="OCP interpolation method."
    )
    x_tolerance: float = Field(
        default=1e-6,
        alias="x tolerance",
        description=(
            "Exclude data points with stoichiometry within this tolerance of 0 "
            "or 1 (i.e. x <= tol or x >= 1 - tol)."
        ),
    )
    minimum_dudx: float = Field(
        default=1e-6,
        alias="minimum dUdx",
        description=(
            "Floor on |dU/dx| to avoid divide-by-zero; where |dU/dx| falls below "
            "it, the corresponding y = x(1-x)dU/dx values are clipped. The runtime "
            "also accepts None to disable it, but that cannot cross the wire; omit "
            "the key for the default 1e-6."
        ),
    )


class DiffusivityDataInterpolantOptions(_CalculationOptions):
    """Options for :class:`DiffusivityDataInterpolant`."""

    interpolator: _Interpolator = Field(
        default="linear", description="Interpolation method."
    )
    transformation: Literal["none", "log"] = Field(
        default="none", description="Transform applied before interpolation."
    )
    scale_factor: bool = Field(
        default=False,
        alias="scale factor",
        description=(
            "Whether to fit a multiplicative scale factor. When True, leaves the "
            "particle diffusivity scale-factor parameter to be defined (e.g. by "
            "fitting)."
        ),
    )


class DiffusivityFromPulseOptions(_CalculationOptions):
    """Options for :class:`DiffusivityFromPulse`."""

    step_number: int | None = Field(
        default=None,
        alias="step number",
        description="Step number to use. Defaults to the first non-rest step.",
    )
    dt_ir: float | None = Field(
        default=None,
        alias="dt_IR",
        description=(
            "Time to establish the IR drop, in seconds. Defaults to the start of "
            "the pulse (first data point of the step)."
        ),
    )
    dt_pulse: float | None = Field(
        default=None,
        description=(
            "Time at which to calculate the diffusion coefficient, in seconds. "
            "Defaults to the end of the pulse."
        ),
    )


class OCPDataInterpolantOptions(_CalculationOptions):
    """Options for :class:`OCPDataInterpolant` and
    :class:`OCPDataInterpolantMSMRExtrapolation`."""

    tolerance: float = Field(
        default=1e-6, description="Stoichiometry de-duplication tolerance."
    )
    direction: Literal["lithiation", "delithiation"] | None = Field(
        default=None, description="OCP direction."
    )
    phase: Literal["primary", "secondary"] | None = Field(
        default=None, description="Electrode phase."
    )
    interpolator: _Interpolator = Field(
        default="linear", description="Interpolation method."
    )


class OCPMSMRInterpolantOptions(_CalculationOptions):
    """Options for :class:`OCPMSMRInterpolant`."""

    interpolator: _Interpolator = Field(
        default="linear", description="Interpolation method."
    )
    tolerance: float = Field(
        default=1e-6, description="Stoichiometry de-duplication tolerance."
    )
    direction: Literal["lithiation", "delithiation"] | None = Field(
        default=None, description="OCP direction."
    )
    phase: Literal["primary", "secondary"] | None = Field(
        default=None, description="Electrode phase."
    )
    create_lithiation_function: bool = Field(
        default=True, description="Also create the lithiation OCP function."
    )


class EntropicChangeInterpolantOptions(_CalculationOptions):
    """Options for :class:`EntropicChangeDataInterpolant` and
    :class:`EntropicChangeFromMSMRFunction`."""

    tolerance: float = Field(
        default=1e-6, description="Stoichiometry de-duplication tolerance."
    )
    interpolator: _Interpolator = Field(
        default="linear", description="Interpolation method."
    )
    phase: Literal["primary", "secondary"] | None = Field(
        default=None, description="Electrode phase."
    )
    scale_factor: float = Field(
        default=1.0,
        alias="scale factor",
        description="Multiplicative scale on the entropic change.",
    )


class ElectrodeSOHHalfCellOptions(_CalculationOptions):
    """Options for :class:`ElectrodeSOHHalfCell`."""

    simulation_kwargs: dict[str, Any] | None = Field(
        default=None, description="Keyword arguments forwarded to the simulation."
    )


class InitialStoichiometryFromVoltageHalfCellOptions(_CalculationOptions):
    """Options for :class:`InitialStoichiometryFromVoltageHalfCell`."""

    simulation_kwargs: dict[str, Any] | None = Field(
        default=None,
        description=(
            "Keyword arguments forwarded to the simulation. The runtime default is "
            "{'solver': pybamm.AlgebraicSolver()} (a live object that can't cross "
            "the wire); omit the key to use it."
        ),
    )
    direction: Literal["lithiation", "delithiation"] | None = Field(
        default=None, description="OCP direction."
    )
    phase: Literal["primary", "secondary"] | None = Field(
        default=None, description="Electrode phase."
    )


class Calculation(BaseSchema):
    """A pipeline step that derives one or more parameters from others without
    fitting to data.

    A calculation reads existing parameters, applies an algebraic or
    numerical recipe, and writes new parameters back into the parameter
    set. Typical uses are computing geometric properties (volume, surface
    area), capacity-related quantities, stoichiometry windows, or
    concentrations.

    Parameters
    ----------
    source : str, optional
        Free-text note describing where the calculation method comes from
        (paper citation, algorithm description). Optional and only used by
        some subclasses."""

    source: str | None = Field(default=None)

    def __init__(self, source=None, **kwargs):
        super().__init__(source=source, **kwargs)


class AreaToSquareWidthHeight(Calculation):
    """Calculate electrode height and width from area assuming square geometry.

    Reads ``"Electrode area [m2]"`` and produces ``"Electrode height [m]"`` and
    ``"Electrode width [m]"`` as ``sqrt(area)``. Useful when only total
    electrode area is known.

    Examples
    --------
    >>> calc = iws.calculations.AreaToSquareWidthHeight()
    >>> config = iws.Pipeline({"geometry": calc}).to_config()"""

    pass


class ArrheniusDiffusivityFromMSMRData(Calculation):
    r"""Calculate the diffusivity from OCP data as

    .. math::
        D = - \frac{F}{RT_{ref}} D_{ref} x (1-x) \frac{dU}{dx} \exp(E / R (1 / T_{ref} - 1 / T))

    where :math:`D_{ref}` is the reference diffusivity, :math:`x` is the stoichiometry,
    :math:`U` is the open-circuit potential, :math:`R` is the gas constant, :math:`F` is
    Faraday's constant, :math:`T` is the temperature, :math:`T_{ref}` is the reference
    temperature, and :math:`E` is the activation energy. This formula is derived from
    the transport equation in the MSMR model.

    This calculation leaves the following parameter to be defined (e.g. by fitting to
    data):

    - Negative/Positive particle reference diffusivity [m2.s-1] ($D_{ref}$)

    Parameters
    ----------
    electrode : str
        The electrode to calculate the diffusivity for (either "positive" or "negative").
    data : DataLoader, DataFrame, str, or dict
        OCP data with the following columns:
            * "Stoichiometry" : array
            * "Voltage [V]" : array
    direction : str, optional
        Specifies lithiation or delithiation for hysteresis models.
        Default is an empty string.
    phase : str, optional
        Specifies the phase ("primary" or "secondary") for composite electrode models.
        Default is an empty string.
    options : MSMRDiffusivityOptions or dict, optional
        See :class:`MSMRDiffusivityOptions` for the available keys."""

    electrode: ElectrodeOrLumped = Field(...)
    data: MeasurementInput = Field(...)
    direction: _Direction = Field(default="")
    phase: _Phase = Field(default="")
    options: MSMRDiffusivityOptions | None = Field(default=None)

    def __init__(self, electrode, data, direction="", phase="", options=None):
        super().__init__(
            electrode=electrode,
            data=data,
            direction=direction,
            phase=phase,
            options=options,
        )


class ArrheniusDiffusivityFromMSMRFunction(Calculation):
    r"""Calculate the diffusivity from an OCP function as

    .. math::
        D = - \frac{F}{RT_{ref}} D_{ref} x (1-x) \frac{dU}{dx} \exp(E / R (1 / T_{ref} - 1 / T))

    where :math:`D_{ref}` is the reference diffusivity, :math:`x` is the stoichiometry,
    :math:`U` is the open-circuit potential, :math:`R` is the gas constant, :math:`F` is
    Faraday's constant, :math:`T` is the temperature, :math:`T_{ref}` is the reference
    temperature, and :math:`E` is the activation energy. This formula is derived from
    the transport equation in the MSMR model.

    This calculation leaves the following parameter to be defined (e.g. by fitting to
    data):

    - Negative/Positive particle reference diffusivity [m2.s-1] ($D_{ref}$)

    Parameters
    ----------
    electrode : str
        The electrode to calculate the diffusivity for (either "positive" or "negative").
    voltage_limits : tuple[float, float]
        The voltage limits to use for the OCP data.
    direction : str, optional
        Specifies lithiation or delithiation for hysteresis models.
        Default is an empty string.
    phase : str, optional
        Specifies the phase ("primary" or "secondary") for composite electrode models.
        Default is an empty string.
    options : MSMRDiffusivityOptions or dict, optional
        See :class:`MSMRDiffusivityOptions` for the available keys."""

    electrode: ElectrodeOrLumped = Field(...)
    voltage_limits: _LimitsPair = Field(...)
    direction: _Direction = Field(default="")
    phase: _Phase = Field(default="")
    options: MSMRDiffusivityOptions | None = Field(default=None)

    def __init__(self, electrode, voltage_limits, direction="", phase="", options=None):
        super().__init__(
            electrode=electrode,
            voltage_limits=voltage_limits,
            direction=direction,
            phase=phase,
            options=options,
        )


class ArrheniusLogLinear(Calculation):
    """Fit an Arrhenius (log-linear) temperature dependence to a quantity
    measured at several temperatures.

    Parameters
    ----------
    data : DataLoader, DataFrame, str, or dict
        Measured values at each temperature.
    reference_temperature : float, optional
        Reference temperature (in K) used to anchor the Arrhenius fit. If
        ``None``, a default is chosen from the data.
    include_func : bool, optional
        If ``True``, also output an interpolant function so the value can be
        evaluated at any temperature, not just the measured ones. Default
        ``False``.

    Examples
    --------
    >>> calc = iws.calculations.ArrheniusLogLinear(data="path/to/temperature_sweep.csv")
    >>> config = iws.Pipeline({"arrhenius": calc}).to_config()"""

    data: MeasurementInput = Field(...)
    reference_temperature: NumberLike | None = Field(default=None)
    include_func: bool = Field(default=False)

    def __init__(self, data, reference_temperature=None, include_func=False):
        super().__init__(
            data=data,
            reference_temperature=reference_temperature,
            include_func=include_func,
        )


class AverageMSMRParameters(Calculation):
    """Average the MSMR species parameters across the lithiation and
    delithiation directions for one electrode.

    Useful when you've fit the MSMR parameters separately in each direction
    (to capture hysteresis) but now want a single, direction-independent
    parameter set for downstream simulations.

    Parameters
    ----------
    electrode : str
        Electrode whose MSMR parameters are being averaged.
    options : AverageMSMRParametersOptions or dict, optional
        See :class:`AverageMSMRParametersOptions` for the available keys.

    Examples
    --------
    >>> calc = iws.calculations.AverageMSMRParameters(electrode="positive")
    >>> config = iws.Pipeline({"average": calc}).to_config()"""

    electrode: ElectrodeOrLumped = Field(...)
    options: AverageMSMRParametersOptions | None = Field(default=None)

    def __init__(self, electrode, options=None):
        super().__init__(electrode=electrode, options=options)


class CellMass(Calculation):
    """Compute the total cell mass in kilograms by summing the masses of the
    electrodes, separator, and current collectors from their densities,
    porosities, and thicknesses.

    Adds ``Cell mass [kg]`` to the parameter set so downstream calculations
    (e.g. specific heat capacity, gravimetric energy density) can use it.

    Parameters
    ----------
    model_options : dict, optional
        The pybamm model options — needed only when the cell has composite
        electrodes so the right phase masses get summed.

    Initial credit: PyBOP team

    Examples
    --------
    >>> calc = iws.calculations.CellMass()
    >>> config = iws.Pipeline({"cell_mass": calc}).to_config()"""

    model_options: dict[str, Any] | None = Field(default=None)

    def __init__(self, model_options=None):
        super().__init__(model_options=model_options)


class CyclableLithium(Calculation):
    """Calculation of amount of cyclable lithium capacity, either based on previously
    calculated electrode capacities and initial stoichiometries ("electrode capacities"
    option), or based on the initial positive electrode capacity and some formation loss
    ("formation loss" option).

    The latter option assumes that before formation the amount of cyclable lithium
    available is equal to the amount of lithium in the positive electrode (positive
    electrode starts out fully lithiated, negative electrode starts out fully
    delithiated), and that a fixed fraction, f, of that lithium is lost during the
    formation process. Then, the cyclable lithium capacity is given by

    .. math::
        Q_Li = f * Q_p

    where f is the parameter "Formation lithium loss" and Q_p is the parameter "Positive
    electrode capacity [A.h]".

    Parameters
    ----------
    method : str, optional
        The method to use to calculate the cyclable lithium capacity. Either
        "electrode capacities" or "formation loss". Default is "electrode capacities".
    options : CyclableLithiumOptions or dict, optional
        See :class:`CyclableLithiumOptions` for the available keys.

    Examples
    --------
    >>> calc = iws.calculations.CyclableLithium(method="electrode capacities")
    >>> config = iws.Pipeline({"cyclable_li": calc}).to_config()"""

    method: str = Field(default="electrode capacities")
    options: CyclableLithiumOptions | None = Field(default=None)

    def __init__(self, method="electrode capacities", options=None):
        super().__init__(method=method, options=options)


class DensityFromVolumeAndMass(Calculation):
    """Calculate the density from the mass and volume.

    Examples
    --------
    >>> calc = iws.calculations.DensityFromVolumeAndMass()
    >>> config = iws.Pipeline({"density": calc}).to_config()"""

    pass


class DiameterToSquareWidthHeight(Calculation):
    """Sets the electrode height and width to be the square root of the electrode
    cross-sectional area, calculated from the diameter (for a coin cell).

    Examples
    --------
    >>> calc = iws.calculations.DiameterToSquareWidthHeight()
    >>> config = iws.Pipeline({"geometry": calc}).to_config()"""

    pass


class DiffusivityDataInterpolant(Calculation):
    """A pipeline element that creates an interpolant for the diffusivity from an array
    of diffusivity data. This interpolant can be used to calculate the diffusivity at
    any point within the range of the data.

    Parameters
    ----------
    electrode : str
        The electrode to create the interpolant for (either "positive" or "negative").
    data : DataLoader, DataFrame, str, or dict
        Diffusivity data with the following columns:

            * "Stoichiometry" : array
                The stoichiometry values.
            * "Diffusivity [m2.s-1]" : array
                The corresponding diffusivity values.
    direction : str, optional
        Specifies lithiation or delithiation for hysteresis models.
        Default is an empty string.
    phase : str, optional
        Specifies the phase ("primary" or "secondary") for composite electrode models.
        Default is an empty string.
    options : DiffusivityDataInterpolantOptions or dict, optional
        See :class:`DiffusivityDataInterpolantOptions` for the available keys."""

    electrode: ElectrodeOrLumped = Field(...)
    data: MeasurementInput = Field(...)
    direction: _Direction = Field(default="")
    phase: _Phase = Field(default="")
    options: DiffusivityDataInterpolantOptions | None = Field(default=None)

    def __init__(self, electrode, data, direction="", phase="", options=None):
        super().__init__(
            electrode=electrode,
            data=data,
            direction=direction,
            phase=phase,
            options=options,
        )


class DiffusivityFromMSMRData(Calculation):
    r"""Calculate the diffusivity from OCP data as

    .. math::
        D = - \frac{F}{RT} D_{ref} x (1-x) \frac{dU}{dx}

    where :math:`D_{ref}` is the reference diffusivity, :math:`x` is the stoichiometry,
    :math:`U` is the open-circuit potential, :math:`R` is the gas constant, :math:`F` is
    Faraday's constant, and :math:`T` is the temperature. This formula is derived from
    the transport equation in the MSMR model.

    This calculation leaves the following parameter to be defined (e.g. by fitting to
    data):

    - Negative/Positive particle reference diffusivity [m2.s-1] ($D_{ref}$)

    Parameters
    ----------
    electrode : str
        The electrode to calculate the diffusivity for (either "positive" or "negative").
    data : DataLoader, DataFrame, str, or dict
        OCP data with the following columns:
            * "Stoichiometry" : array
            * "Voltage [V]" : array
    direction : str, optional
        Specifies lithiation or delithiation for hysteresis models.
        Default is an empty string.
    phase : str, optional
        Specifies the phase ("primary" or "secondary") for composite electrode models.
        Default is an empty string.
    options : MSMRDiffusivityOptions or dict, optional
        See :class:`MSMRDiffusivityOptions` for the available keys."""

    electrode: ElectrodeOrLumped = Field(...)
    data: MeasurementInput = Field(...)
    direction: _Direction = Field(default="")
    phase: _Phase = Field(default="")
    options: MSMRDiffusivityOptions | None = Field(default=None)

    def __init__(self, electrode, data, direction="", phase="", options=None):
        super().__init__(
            electrode=electrode,
            data=data,
            direction=direction,
            phase=phase,
            options=options,
        )


class DiffusivityFromMSMRFunction(Calculation):
    r"""Calculate the diffusivity from an OCP function as

    .. math::

        D = - \frac{F}{RT} D_{{ref}} x (1-x) \frac{dU}{dx}

    where :math:`D_{ref}` is the reference diffusivity, :math:`U` is the open-circuit
    potential, :math:`R` is the gas constant, :math:`F` is Faraday's constant, and
    :math:`T` is the temperature. This formula is derived from the transport equation
    in the MSMR model.

    This calculation leaves the following parameter to be defined (e.g. by fitting to
    data):

    - Negative/Positive particle reference diffusivity [m2.s-1] ($D_{ref}$)

    Parameters
    ----------
    electrode : str
        The electrode to calculate the diffusivity for (either "positive" or "negative").
    voltage_limits : tuple[float, float]
        The voltage limits to use for the OCP data.
    direction : str, optional
        Specifies lithiation or delithiation for hysteresis models.
        Default is an empty string.
    phase : str, optional
        Specifies the phase ("primary" or "secondary") for composite electrode models.
        Default is an empty string.
    options : MSMRDiffusivityOptions or dict, optional
        See :class:`MSMRDiffusivityOptions` for the available keys."""

    electrode: ElectrodeOrLumped = Field(...)
    voltage_limits: _LimitsPair = Field(...)
    direction: _Direction = Field(default="")
    phase: _Phase = Field(default="")
    options: MSMRDiffusivityOptions | None = Field(default=None)

    def __init__(self, electrode, voltage_limits, direction="", phase="", options=None):
        super().__init__(
            electrode=electrode,
            voltage_limits=voltage_limits,
            direction=direction,
            phase=phase,
            options=options,
        )


class DiffusivityFromPulse(Calculation):
    """A pipeline element that calculates the diffusion coefficient from pulse data by
    directly using the voltage data from the pulse, without the need for fitting a
    model. This method uses eqn 26 from Wang et al. [Wang2022]_ to calculate the diffusion
    coefficient.
    Advantages of this method are that it is simple and fast.
    Disadvantages are that the calculation relies on assumptions that may not be valid
    in all cases, and the results may be sensitive to noise in the data since we only
    use 4 data points to calculate the diffusion coefficient.

    Parameters
    ----------
    electrode : str
        The electrode to calculate the diffusivity for (either "positive" or "negative").
    data : DataLoader, DataFrame, str, or dict
        The pulse data. Must include columns ``"Current [A]"``,
        ``"Voltage [V]"`` and ``"Step number"``.
    direction : str, optional
        Specifies lithiation or delithiation for hysteresis models.
        Default is an empty string.
    phase : str, optional
        Specifies the phase ("primary" or "secondary") for composite electrode models.
        Default is an empty string.
    options : DiffusivityFromPulseOptions or dict, optional
        See :class:`DiffusivityFromPulseOptions` for the available keys.

    Raises
    ------
    ValueError
        If no rest step is found after the pulse.

    References
    ----------
    .. [Wang2022] Wang, A. A., et al. "Review of parameterisation and a novel database
        (LiionDB) for continuum Li-ion battery models." Progress in Energy 4.3 (2022):
        032004."""

    electrode: ElectrodeOrLumped = Field(...)
    data: MeasurementInput = Field(...)
    direction: _Direction = Field(default="")
    phase: _Phase = Field(default="")
    options: DiffusivityFromPulseOptions | None = Field(default=None)

    def __init__(self, electrode, data, direction="", phase="", options=None):
        super().__init__(
            electrode=electrode,
            data=data,
            direction=direction,
            phase=phase,
            options=options,
        )


class ElectrodeCapacity(Calculation):
    """A pipeline element that calculates variables related to the capacity. Automatically
    determines the method and unknown.

    Solves the algebraic equation:
    c_max * eps * L * A_cc * (stoich_max - stoich_min) * F / 3600 = capacity,

    where capacity can be the electrode capacity, the electrode loading times the area,
    or the theoretical capacity from the crystal density, fraction of Li per mole of material,
    and molecular mass of active material. All but one of c_max, eps, L, A_cc, stoich_max,
    and stoich_min must be provided (stoich_min and stoich_max are only required if
    use_stoich_window is True). Either capacity, loading, or the crystal density, fraction of Li per mole of material,
    and molecular mass of active material must be provided.

    Parameters
    ----------
    electrode : str
        Electrode to calculate capacity for: "positive" or "negative".
    use_stoich_window : bool, default=False
        Whether to use stoichiometry limits in the calculation. Set True if capacity
        is based on a voltage window (e.g., 0-100% SOC from RPT). Set False if
        capacity represents the full material limit (e.g., from OCP fitting).
    method : str, default="auto"
        Calculation method. Use "auto" to automatically determine based on inputs.
    phase : str | None, default=None
        Phase for multi-phase materials: "primary" or "secondary".

    Examples
    --------
    >>> calc = iws.calculations.ElectrodeCapacity(electrode="positive")
    >>> config = iws.Pipeline({"capacity": calc}).to_config()"""

    electrode: ElectrodeOrLumped = Field(...)
    use_stoich_window: bool = Field(default=False)
    method: str = Field(default="auto")
    phase: _Phase | None = Field(default=None)

    def __init__(self, electrode, use_stoich_window=False, method="auto", phase=None):
        super().__init__(
            electrode=electrode,
            use_stoich_window=use_stoich_window,
            method=method,
            phase=phase,
        )


class ElectrodeSOH(Calculation):
    """Calculate electrode stoichiometry windows from capacity using electrode SOH algorithm.

    Reads ``"Nominal cell capacity [A.h]"`` (or ``"Cyclable lithium capacity
    [A.h]"``), the electrode OCPs, and electrode dimensions/concentrations, and
    produces the stoichiometries at 0% and 100% SOC for both electrodes. Uses
    the algorithm from Mohtat et al. (2019) [Mohtat2019]_.

    Parameters
    ----------
    options : ElectrodeSOHOptions or dict, optional
        See :class:`ElectrodeSOHOptions` for the available keys.

    References
    ----------
    .. [Mohtat2019] Mohtat, P., Lee, S., Siegel, J. B., & Stefanopoulou, A. G. (2019).
        Towards better estimability of electrode-specific state of health: Decoding
        the cell expansion. Journal of Power Sources, 427, 101-111.

    Examples
    --------
    >>> calc = iws.calculations.ElectrodeSOH()
    >>> config = iws.Pipeline({"esoh": calc}).to_config()"""

    options: ElectrodeSOHOptions | None = Field(default=None)

    def __init__(self, options=None):
        super().__init__(options=options)


class ElectrodeSOHHalfCell(Calculation):
    """Calculate minimum and maximum electrode stoichiometries for a half-cell using the
    electrode-specific SOH algorithm.

    See :class:`ElectrodeSOH` for more details.

    Parameters
    ----------
    electrode : str
        The electrode to calculate the initial concentration for, either "positive" or
        "negative".
    options : ElectrodeSOHHalfCellOptions or dict, optional
        See :class:`ElectrodeSOHHalfCellOptions` for the available keys."""

    electrode: ElectrodeOrLumped = Field(...)
    options: ElectrodeSOHHalfCellOptions | None = Field(default=None)

    def __init__(self, electrode, options=None):
        super().__init__(electrode=electrode, options=options)


class ElectrodeVolumeFractionFromLoading(Calculation):
    """Calculate the volume fraction of active material in the electrodes from the loading and maximum concentration or from the coating mass and crystal density.

    Parameters
    ----------
    electrode : ["positive", "negative", "both"]
        The electrode to calculate the volume fraction for.
    method : ["loading", "coating mass"]
        The method to use to calculate the volume fraction."""

    electrode: ElectrodeOrLumped = Field(...)
    method: str = Field(...)

    def __init__(self, electrode, method):
        super().__init__(electrode=electrode, method=method)


class ElectrodeVolumeFractionFromPorosity(Calculation):
    """Calculate the volume fraction of active material in the electrodes from the
    porosity and the active volume fraction of solid.

    Parameters
    ----------
    electrode : str
        The electrode to calculate the volume fraction for. Must be either "negative"
        or "positive"."""

    electrode: ElectrodeOrLumped = Field(...)

    def __init__(self, electrode):
        super().__init__(electrode=electrode)


class EntropicChangeDataInterpolant(Calculation):
    """Create an interpolant for the open-circuit entropic change from data.

    Parameters
    ----------
    electrode : str
        The electrode to create the interpolant for, either "positive", "negative",
        or "lumped". If "lumped", assumes a single electrode and modifies parameter
        names accordingly.
    data : DataLoader, DataFrame, str, or dict
        The data to use for the interpolant. Must have columns
        ``"Stoichiometry"`` and ``"Entropic change [V.K-1]"``.
    options : EntropicChangeInterpolantOptions or dict, optional
        See :class:`EntropicChangeInterpolantOptions` for the available keys."""

    electrode: ElectrodeOrLumped = Field(...)
    data: MeasurementInput = Field(...)
    options: EntropicChangeInterpolantOptions | None = Field(default=None)

    def __init__(self, electrode, data, options=None):
        super().__init__(electrode=electrode, data=data, options=options)


class EntropicChangeFromMSMRFunction(Calculation):
    """Create an interpolant for the open-circuit entropic change from MSMR parameters.

    Parameters
    ----------
    electrode : str
        The electrode to create the interpolant for, either "positive" or "negative".
    voltage_limits : tuple of float
        The voltage limits to use to generate data for the interpolant.
    options : EntropicChangeInterpolantOptions or dict, optional
        See :class:`EntropicChangeInterpolantOptions` for the available keys."""

    electrode: ElectrodeOrLumped = Field(...)
    voltage_limits: _LimitsPair = Field(...)
    options: EntropicChangeInterpolantOptions | None = Field(default=None)

    def __init__(self, electrode, voltage_limits, options=None):
        super().__init__(
            electrode=electrode, voltage_limits=voltage_limits, options=options
        )


class HalfCellNominalCapacity(Calculation):
    """Set nominal cell capacity and current function equal to electrode capacity.

    For half-cell models, the cell capacity is determined by the working
    electrode capacity. Reads ``"Positive electrode capacity [A.h]"`` (or the
    negative-electrode equivalent) and writes the same value to ``"Nominal cell
    capacity [A.h]"`` and ``"Current function [A]"``, providing the cell-level
    parameters required by PyBaMM.

    Parameters
    ----------
    electrode : str
        Working electrode: "negative" or "positive"."""

    electrode: ElectrodeOrLumped = Field(...)

    def __init__(self, electrode):
        super().__init__(electrode=electrode)


class InitialConcentrationFromInitialStoichiometryHalfCell(Calculation):
    """Calculate the initial concentration in the given electrode from the initial
    stoichiometry and maximum concentration.

    Parameters
    ----------
    electrode : str
        The electrode to calculate the initial concentration for, either "positive" or
        "negative".
    options : InitialConcentrationFromInitialStoichiometryHalfCellOptions or dict, optional
        See :class:`InitialConcentrationFromInitialStoichiometryHalfCellOptions` for
        the available keys."""

    electrode: ElectrodeOrLumped = Field(...)
    options: InitialConcentrationFromInitialStoichiometryHalfCellOptions | None = Field(
        default=None
    )

    def __init__(self, electrode, options=None):
        super().__init__(electrode=electrode, options=options)


class InitialSOC(Calculation):
    """Calculate initial electrode concentrations from target SOC.

    Reads the stoichiometry windows (``"Negative/Positive electrode
    stoichiometry at 0%/100% SOC"``) and maximum concentrations for both
    electrodes, and produces ``"Initial stoichiometry in negative/positive
    electrode"`` and the corresponding ``"Initial concentration in
    negative/positive electrode [mol.m-3]"``.

    Parameters
    ----------
    soc : float
        Target state of charge (0.0 to 1.0).

    Examples
    --------
    >>> calc = iws.calculations.InitialSOC(soc=0.5)
    >>> config = iws.Pipeline({"initial_soc": calc}).to_config()"""

    soc: NumberLike | str = Field(...)

    def __init__(self, soc):
        super().__init__(soc=soc)


class InitialSOCHalfCell(Calculation):
    """Calculate initial electrode concentration from target SOC for half-cell.

    Reads the working electrode's stoichiometry window and maximum
    concentration, and produces ``"Initial stoichiometry in positive/negative
    electrode"`` and ``"Initial concentration in positive/negative electrode
    [mol.m-3]"``.

    Parameters
    ----------
    electrode : str
        Working electrode: "negative" or "positive".
    soc : float | int | str
        Target SOC. Can be numeric (0.0-1.0) or string ("0%", "100%",
        "minimum", "maximum").
    options : InitialSOCHalfCellOptions or dict, optional
        See :class:`InitialSOCHalfCellOptions` for the available keys."""

    electrode: ElectrodeOrLumped = Field(...)
    soc: NumberLike | str = Field(...)
    options: InitialSOCHalfCellOptions | None = Field(default=None)

    def __init__(self, electrode, soc, options=None):
        super().__init__(electrode=electrode, soc=soc, options=options)


class InitialSOCfromMaximumStoichiometry(Calculation):
    """Calculate the initial concentration in the negative and positive electrodes from
    the initial SOC and stoichiometry windows in each electrode.

    Parameters
    ----------
    options : InitialSOCfromMaximumStoichiometryOptions or dict, optional
        See :class:`InitialSOCfromMaximumStoichiometryOptions` for the available keys."""

    options: InitialSOCfromMaximumStoichiometryOptions | None = Field(default=None)

    def __init__(self, options=None):
        super().__init__(options=options)


class InitialStoichiometryFromVoltageHalfCell(Calculation):
    """Calculate the initial stoichiometry in the given electrode from the initial
    voltage (i.e. find the stoichiometry that gives the correct voltage).

    Parameters
    ----------
    electrode : str
        The electrode to calculate the initial concentration for, either "positive" or
        "negative".
    options : InitialStoichiometryFromVoltageHalfCellOptions or dict, optional
        See :class:`InitialStoichiometryFromVoltageHalfCellOptions` for the available
        keys."""

    electrode: ElectrodeOrLumped = Field(...)
    options: InitialStoichiometryFromVoltageHalfCellOptions | None = Field(default=None)

    def __init__(self, electrode, options=None):
        super().__init__(electrode=electrode, options=options)


class InitialStoichiometryFromVoltageMSMRHalfCell(Calculation):
    """Calculate the initial stoichiometry in the given electrode from the initial
    voltage (i.e. find the stoichiometry that gives the correct voltage) using the
    MSMR framework.

    Parameters
    ----------
    electrode : str
        The electrode to calculate the initial concentration for, either "positive" or
        "negative"."""

    electrode: ElectrodeOrLumped = Field(...)

    def __init__(self, electrode):
        super().__init__(electrode=electrode)


class InitialVoltageFromConcentration(Calculation):
    """Calculate initial voltage from target concentration using OCP inversion.

    Reads ``"Positive/Negative electrode lithiation"`` (the OCP function),
    ``"Maximum concentration in positive/negative electrode [mol.m-3]"``, and
    ``"Initial concentration in positive/negative electrode [mol.m-3]"``, and
    produces ``"Initial voltage in positive/negative electrode [V]"`` by
    numerically inverting the lithiation function.

    Parameters
    ----------
    electrode : str
        Electrode: "negative" or "positive"."""

    electrode: ElectrodeOrLumped = Field(...)

    def __init__(self, electrode):
        super().__init__(electrode=electrode)


class JellyRollThermalDimensions(Calculation):
    """Calculate thermal properties of cylindrical jelly roll cell.

    Reads ``"Jelly roll height [m]"`` and ``"Jelly roll radius [m]"`` and
    produces ``"Cell volume [m3]"`` and ``"Cell cooling surface area [m2]"``
    assuming cylindrical geometry for thermal modeling.

    Examples
    --------
    >>> calc = iws.calculations.JellyRollThermalDimensions()
    >>> config = iws.Pipeline({"thermal": calc}).to_config()"""

    pass


class LumpedHeatCapacityAndDensity(Calculation):
    """Sets the specific heat capacity and density for each cell component to the lumped
    (cell-level) values."""

    pass


class MSMRElectrodeSOHHalfCell(Calculation):
    """Calculate minimum and maximum electrode stoichiometries for a half-cell by
    evaluating the extent of lithiation at the minimum and maximum OCV.

    See :class:`ElectrodeSOH` for more details.

    Parameters
    ----------
    electrode : str
        The electrode to calculate the minimum and maximum stoichiometries for."""

    electrode: ElectrodeOrLumped = Field(...)

    def __init__(self, electrode):
        super().__init__(electrode=electrode)


class MSMRFullCellCapacities(Calculation):
    """A pipeline element that calculates variables related to the capacity from the MSMR
    full-cell balance.

    Parameters
    ----------
    data : DataLoader, DataFrame, str, or dict
        The data to use to calculate the useable capacity, see :class:`FittingObjective`.
    parameter_format : str, optional
        The format of the parameters to fit. One parameter is always the lower excess
        capacity, and this option determines the other parameter, which can be either
        the total capacity or the upper excess capacity. Default is "total capacity".
        (Q_tot = Q_lowex + Q_use + Q_uppex)"""

    data: MeasurementInput = Field(...)
    method: str = Field(default="total capacity")

    def __init__(self, data, method="total capacity"):
        super().__init__(data=data, method=method)


class MSMRFunction(Calculation):
    """Specifies the MSMR function for the open-circuit potential for the given electrode.

    Parameters
    ----------
    electrode : str
        The name of the electrode.
    direction : str, optional
        The direction of the MSMR function.
    phase : str, optional
        The phase of the MSMR function."""

    electrode: ElectrodeOrLumped = Field(...)
    direction: _Direction | None = Field(default=None)
    phase: _Phase | None = Field(default=None)

    def __init__(self, electrode, direction=None, phase=None):
        super().__init__(electrode=electrode, direction=direction, phase=phase)


class OCPDataInterpolant(Calculation):
    """Create an interpolant for the open-circuit voltage (OCP) from data.

    Parameters
    ----------
    electrode : str
        The electrode to create the interpolant for, either "positive", "negative",
        or "lumped". If "lumped", assumes a single electrode and modifies parameter
        names accordingly.
    data : DataLoader, DataFrame, str, or dict
        The data to use for the interpolant. Must have columns "Stoichiometry" and
        "Voltage [V]".
    options : OCPDataInterpolantOptions or dict, optional
        See :class:`OCPDataInterpolantOptions` for the available keys."""

    electrode: ElectrodeOrLumped = Field(...)
    data: MeasurementInput = Field(...)
    options: OCPDataInterpolantOptions | None = Field(default=None)

    def __init__(self, electrode, data, options=None):
        super().__init__(electrode=electrode, data=data, options=options)


class OCPDataInterpolantMSMRExtrapolation(Calculation):
    """Create an interpolant for the open-circuit voltage (OCP) from data and use MSMR
    parameters to extrapolate outside the data range and to convert capacity to
    stoichiometry.

    The blending uses smooth weight functions to transition between OCP data in the
    observed stoichiometry range and MSMR extrapolation outside it. Mathematical
    formulation:

        V(x) = w(x)·V_ocp(x) + (1-w(x))·V_msmr_corrected(x)

    where w(x) is a smooth bump function based on the error function, and
    V_msmr_corrected includes a linear offset to ensure C⁰ continuity at the OCP
    boundaries.

    Parameters
    ----------
    electrode : str
        The electrode to create the interpolant for, either "positive" or "negative".
    data : DataLoader, DataFrame, str, or dict
        The data to use for the interpolant. Must have columns "Capacity [A.h]" and
        "Voltage [V]".
    voltage_limits : tuple of float
        The voltage limits to use to generate MSMR data for extrapolation.
    options : OCPDataInterpolantOptions or dict, optional
        See :class:`OCPDataInterpolantOptions` for the available keys."""

    electrode: ElectrodeOrLumped = Field(...)
    data: MeasurementInput = Field(...)
    voltage_limits: _LimitsPair = Field(...)
    options: OCPDataInterpolantOptions | None = Field(default=None)

    def __init__(self, electrode, data, voltage_limits, options=None):
        super().__init__(
            electrode=electrode,
            data=data,
            voltage_limits=voltage_limits,
            options=options,
        )


class OCPMSMRInterpolant(Calculation):
    """Create an interpolant for the open-circuit voltage (OCP) from MSMR parameters.

    Parameters
    ----------
    electrode : str
        The electrode to create the interpolant for, either "positive" or "negative".
    voltage_limits : tuple of float
        The voltage limits to use to generate data for the interpolant.
    options : OCPMSMRInterpolantOptions or dict, optional
        See :class:`OCPMSMRInterpolantOptions` for the available keys."""

    electrode: ElectrodeOrLumped = Field(...)
    voltage_limits: _LimitsPair = Field(...)
    options: OCPMSMRInterpolantOptions | None = Field(default=None)

    def __init__(self, electrode, voltage_limits, options=None):
        super().__init__(
            electrode=electrode, voltage_limits=voltage_limits, options=options
        )


class OpenCircuitLimits(Calculation):
    """Set OCV limits equal to voltage cutoffs for SOC calculations.

    Reads ``"Lower voltage cut-off [V]"`` and ``"Upper voltage cut-off [V]"``
    and produces ``"Open-circuit voltage at 0% SOC [V]"`` and ``"Open-circuit
    voltage at 100% SOC [V]"``, establishing the relationship between SOC and
    voltage windows."""

    pass


class PorosityFromElectrodeVolumeFraction(Calculation):
    """Calculate the porosity from the active material volume fraction.

    Parameters
    ----------
    electrode : str
        The electrode to calculate the porosity for. Must be either "negative"
        or "positive"."""

    electrode: ElectrodeOrLumped = Field(...)

    def __init__(self, electrode):
        super().__init__(electrode=electrode)


class PouchCellThermalDimensions(Calculation):
    """Calculate thermal properties of rectangular pouch cell.

    Reads ``"Pouch height [m]"``, ``"Pouch width [m]"``, and ``"Pouch thickness
    [m]"``, and produces ``"Cell volume [m3]"`` and ``"Cell cooling surface
    area [m2]"`` assuming rectangular prism geometry for thermal modeling.

    Examples
    --------
    >>> calc = iws.calculations.PouchCellThermalDimensions()
    >>> config = iws.Pipeline({"thermal": calc}).to_config()"""

    pass


class SlopesToKnots(Calculation):
    """Converts slopes and initial value to knot values for piecewise linear interpolation.

    This calculation takes as input:
    - An initial value at the first breakpoint
    - Slopes for each segment between consecutive breakpoints

    And outputs:
    - The value at each breakpoint (knot values)

    The conversion follows: y_{i+1} = y_i + slope_i * (x_{i+1} - x_i)

    Reads the initial value at the first breakpoint and the slopes between
    consecutive breakpoints (e.g. ``"Particle diffusion time at SOC 0 [s]"``,
    ``"Particle diffusion time slope from SOC 0 to 0.5 [s]"``), and produces
    the knot value at every breakpoint (e.g. ``"Particle diffusion time at SOC
    0.5 [s]"``, ``"Particle diffusion time at SOC 1 [s]"``).

    Parameters
    ----------
    base_parameter_name : str
        The name of the parameter (e.g., "Particle diffusion time [s]")
    breakpoint_values : list[float]
        List of breakpoint values (e.g., [0.0, 0.5, 1.0])
    breakpoint_parameter_name : str
        Name of the breakpoint parameter (e.g., "SOC", "Temperature [K]")"""

    base_parameter_name: str = Field(...)
    breakpoint_values: list[NumberLike] = Field(...)
    breakpoint_parameter_name: str = Field(...)

    def __init__(
        self, base_parameter_name, breakpoint_values, breakpoint_parameter_name
    ):
        super().__init__(
            base_parameter_name=base_parameter_name,
            breakpoint_values=breakpoint_values,
            breakpoint_parameter_name=breakpoint_parameter_name,
        )


class SlopesToKnots2D(Calculation):
    """Converts slopes and initial value to knot values for 2D piecewise linear interpolation.

    This calculation takes as input:
    - An initial value at (bp1_0, bp2_0)
    - Slopes along dimension 1 for the first row (at bp2_0)
    - Slopes along dimension 2 for all subsequent rows

    And outputs:
    - The value at each 2D grid point (knot values)

    The conversion follows the same strategy as PiecewiseInterpolation2D slopes mode:
    1. Start with initial value at (bp1_0, bp2_0)
    2. Use bp1-slopes to fill first row
    3. Use bp2-slopes to fill remaining rows

    Reads the initial value at ``(bp1_0, bp2_0)``, the bp1-slopes along the
    first row (e.g. ``"Diffusivity SOC-slope from SOC 0 to 1 at Temperature [K]
    273.15 [m2.s-1]"``), and the bp2-slopes for each bp1 grid point (e.g.
    ``"Diffusivity Temperature [K]-slope from Temperature [K] 273.15 to 323.15
    at SOC 0 [m2.s-1]"``), and produces the knot value at every 2D grid point.

    Parameters
    ----------
    base_parameter_name : str
        The name of the parameter (e.g., "Diffusivity [m2.s-1]")
    breakpoint1_values : list[float]
        List of first dimension breakpoint values (e.g., [0.0, 0.5, 1.0])
    breakpoint1_parameter_name : str
        Name of the first breakpoint parameter (e.g., "SOC")
    breakpoint2_values : list[float]
        List of second dimension breakpoint values (e.g., [273.15, 298.15])
    breakpoint2_parameter_name : str
        Name of the second breakpoint parameter (e.g., "Temperature [K]")"""

    base_parameter_name: str = Field(...)
    breakpoint1_values: list[NumberLike] = Field(...)
    breakpoint1_parameter_name: str = Field(...)
    breakpoint2_values: list[NumberLike] = Field(...)
    breakpoint2_parameter_name: str = Field(...)

    def __init__(
        self,
        base_parameter_name,
        breakpoint1_values,
        breakpoint1_parameter_name,
        breakpoint2_values,
        breakpoint2_parameter_name,
    ):
        super().__init__(
            base_parameter_name=base_parameter_name,
            breakpoint1_values=breakpoint1_values,
            breakpoint1_parameter_name=breakpoint1_parameter_name,
            breakpoint2_values=breakpoint2_values,
            breakpoint2_parameter_name=breakpoint2_parameter_name,
        )


class SpecificHeatCapacity(Calculation):
    """Calculate the specific heat capacity from the lumped heat capacity and cell mass.

    Examples
    --------
    >>> calc = iws.calculations.SpecificHeatCapacity()
    >>> config = iws.Pipeline({"cp": calc}).to_config()"""

    pass


class StoichiometryAtMinimumSOC(Calculation):
    """Calculate the stoichiometry at the minimum SOC based on the stoichiometry at the
    maximum SOC, the electrode capacities, and the useable capacity.

    Parameters
    ----------
    electrode : str
        The electrode to calculate the initial concentration for, either "positive" or
        "negative"."""

    electrode: ElectrodeOrLumped = Field(...)

    def __init__(self, electrode):
        super().__init__(electrode=electrode)


class StoichiometryLimitsFromCapacity(Calculation):
    """Calculate the minimum and maximum stoichiometries for each electrode in a full-cell
    based on the electrode total capacity, lower and upper excess capacities.

    Parameters
    ----------
    options : StoichiometryLimitsFromCapacityOptions or dict, optional
        See :class:`StoichiometryLimitsFromCapacityOptions` for the available keys."""

    options: StoichiometryLimitsFromCapacityOptions | None = Field(default=None)

    def __init__(self, options=None):
        super().__init__(options=options)


class SurfaceAreaToVolumeRatio(Calculation):
    """Calculate the surface area to volume ratio for the electrodes from the active
    material volume fraction and particle radius, assuming spherical particles.

    Parameters
    ----------
    electrode : str
        The electrode to calculate the surface area to volume ratio for, either
        "positive", "negative" or "both"."""

    electrode: ElectrodeOrLumped = Field(...)

    def __init__(self, electrode):
        super().__init__(electrode=electrode)
