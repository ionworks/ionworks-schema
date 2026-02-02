"""Schemas for calculations."""

from typing import Any

from pydantic import Field

from ..base import BaseSchema


class AreaToSquareWidthHeight(BaseSchema):
    """Calculate electrode height and width from area assuming square geometry.

    Computes electrode dimensions as sqrt(area) for both height and width,
    useful when only total electrode area is known.

    Examples
    --------
    >>> calc = iwp.calculations.AreaToSquareWidthHeight()
    >>> params = iwp.ParameterValues({"Electrode area [m2]": 0.01})
    >>> result = calc.run(params)
    >>> result["Electrode height [m]"]
    0.1
    >>> result["Electrode width [m]"]
    0.1"""

    pass


class ArrheniusDiffusivityFromMSMRData(BaseSchema):
    """Calculate the diffusivity from OCP data as

    .. math::
        D = - \frac{F}{RT_{ref}} D_{ref} x (1-x) \frac{dU}{dx} \\exp(E / R (1 / T_{ref} - 1 / T))

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
    data : pd.DataFrame
        OCP data with the following columns:
            * "Stoichiometry" : array
            * "Voltage [V]" : array
    direction : str, optional
        Specifies lithiation or delithiation for hysteresis models.
        Default is an empty string.
    phase : str, optional
        Specifies the phase ("primary" or "secondary") for composite electrode models.
        Default is an empty string.
    options : dict, optional
        Options for the calculation. The available options are:

            * "interpolator" : str
                The interpolator to use. Default is "linear". For more options, see the
                documentation for pybamm.Interpolant
            * "x tolerance" : float
                The tolerance for the stoichiometry values near 0 and 1. Default is 1e-6.
                Data points where x < tolerance or x > (1 - tolerance) are excluded
                from the calculation.
            * "minimum dUdx" : float
                The minimum value for the gradient of the open-circuit potential with
                respect to the stoichiometry. Default is 1e-6. When the absolute value
                of dU/dx is below this minimum, the corresponding y_data = x(1-x)dU/dx
                values are clipped."""

    electrode: Any = Field(...)
    data: Any = Field(...)
    direction: Any = Field(default="")
    phase: Any = Field(default="")
    options: Any | None = Field(default=None)

    def __init__(self, electrode, data, direction="", phase="", options=None):
        super().__init__(
            electrode=electrode,
            data=data,
            direction=direction,
            phase=phase,
            options=options,
        )


class ArrheniusDiffusivityFromMSMRFunction(BaseSchema):
    """Calculate the diffusivity from an OCP function as

    .. math::
        D = - \frac{F}{RT_{ref}} D_{ref} x (1-x) \frac{dU}{dx} \\exp(E / R (1 / T_{ref} - 1 / T))

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
    options : dict, optional
        Options for the calculation. The available options are:

            * "interpolator" : str
                The interpolator to use. Default is "linear". For more options, see the
                documentation for pybamm.Interpolant
            * "x tolerance" : float
                The tolerance for the stoichiometry values near 0 and 1. Default is 1e-6.
                Data points where x < tolerance or x > (1 - tolerance) are excluded
                from the calculation.
            * "minimum dUdx" : float
                The minimum value for the gradient of the open-circuit potential with
                respect to the stoichiometry. Default is 1e-6. When the absolute value
                of dU/dx is below this minimum, the corresponding y_data = x(1-x)dU/dx
                values are clipped."""

    electrode: Any = Field(...)
    voltage_limits: Any = Field(...)
    direction: Any = Field(default="")
    phase: Any = Field(default="")
    options: Any | None = Field(default=None)

    def __init__(self, electrode, voltage_limits, direction="", phase="", options=None):
        super().__init__(
            electrode=electrode,
            voltage_limits=voltage_limits,
            direction=direction,
            phase=phase,
            options=options,
        )


class ArrheniusLogLinear(BaseSchema):
    """Schema for ArrheniusLogLinear."""

    data: Any = Field(...)
    reference_temperature: Any | None = Field(default=None)
    include_func: Any = Field(default=False)

    def __init__(self, data, reference_temperature=None, include_func=False):
        super().__init__(
            data=data,
            reference_temperature=reference_temperature,
            include_func=include_func,
        )


class AverageMSMRParameters(BaseSchema):
    """Averages the MSMR species parameters over the delithiation and lithiation directions
    for the given electrode. The parameters are separated by direction using the
    `iwp.data_fits.objectives.ocp_msmr_util.U0_prefix`, `iwp.data_fits.objectives.ocp_msmr_util.w_prefix`,
    `iwp.data_fits.objectives.ocp_msmr_util.X_prefix`, and `iwp.data_fits.objectives.ocp_msmr_util.Q_prefix`
    functions.

    Parameters
    ----------
    electrode : str
        The name of the electrode.
    options : dict, optional
        A dictionary of options to be passed to the calculation. The following options
        are available:

            * species_format : str, optional
                The format of the species ("Xj" or "Qj"). Default is "Xj".
            * phase : str, optional
                The phase to use for the model. Default is None. Can be "primary" or "secondary"."""

    electrode: Any = Field(...)
    options: Any | None = Field(default=None)

    def __init__(self, electrode, options=None):
        super().__init__(electrode=electrode, options=options)


class Calculation(BaseSchema):
    """Base class for calculations that derive new parameters from existing ones.

    Calculations transform input parameters through algebraic or numerical methods
    to produce output parameters. Common uses include computing geometric properties,
    stoichiometry windows, and material concentrations.

    Parameters
    ----------
    source : str
        Reference or description of the calculation method (e.g., paper citation,
        algorithm description).

    Examples
    --------
    Create a custom calculation:

    >>> class CustomCalculation(iwp.Calculation):
    ...     def __init__(self):
    ...         super().__init__(source="Custom method")
    ...
    ...     def run(self, parameter_values: iwp.ParameterValues) -> iwp.ParameterValues:
    ...         result = parameter_values["Input [m]"] * 2
    ...         return iwp.ParameterValues({"Output [m]": result})"""

    source: Any = Field(...)

    def __init__(self, source):
        super().__init__(source=source)


class CellMass(BaseSchema):
    """Calculate the total cell mass in kilograms.

    This method uses the provided parameter set to calculate the mass of different
    components of the cell, such as electrodes, separator, and current collectors,
    based on their densities, porosities, and thicknesses. It then calculates the
    total mass by summing the mass of each component and adds it as a parameter,
    `Cell mass [kg]` in the parameter_values dictionary.

    Note: this class requires an iwp.ParameterValues or pybamm.ParameterValues object

    Parameters
    ----------
    model_options : dict, optional
        The PyBaMM model options to determine if the model has composite electrodes

    Initial credit: PyBOP team"""

    model_options: Any | None = Field(default=None)

    def __init__(self, model_options=None):
        super().__init__(model_options=model_options)


class CyclableLithium(BaseSchema):
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
    options : dict, optional
        Options for the calculation. The available options are:
            * particle phases: tuple of str
                Specifies the number of phases for each electrode as a tuple
                (negative, positive). Each element can be "1" (single phase) or "2"
                (composite with Primary and Secondary phases). Default is ("1", "1")."""

    method: Any = Field(default="electrode capacities")
    options: Any | None = Field(default=None)

    def __init__(self, method="electrode capacities", options=None):
        super().__init__(method=method, options=options)


class DensityFromVolumeAndMass(BaseSchema):
    """Calculate the density from the mass and volume."""

    pass


class DiameterToSquareWidthHeight(BaseSchema):
    """Sets the electrode height and width to be the square root of the electrode
    cross-sectional area, calculated from the diameter (for a coin cell)."""

    pass


class DiffusivityDataInterpolant(BaseSchema):
    """A pipeline element that creates an interpolant for the diffusivity from an array
    of diffusivity data. This interpolant can be used to calculate the diffusivity at
    any point within the range of the data.

    Parameters
    ----------
    electrode : str
        The electrode to create the interpolant for (either "positive" or "negative").
    data : pd.DataFrame
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
    options : dict, optional
        Options for the calculation. The available options are:

            * "interpolator" : str
                The interpolator to use. Default is "linear". For more options, see the
                documentation for pybamm.Interpolant
            * "transformation" : str
                The transformation to apply to the data before creating the interpolant.
                Options are "none" (default) or "log" (interpolant is created in log10
                space).
            * "scale factor" : bool
                Whether to multiply the diffusivity by a scale factor. Default is False.
                If True, this leaves the following parameter to be defined (e.g. by
                fitting to data):

                 - Negative/Positive particle diffusivity scale factor"""

    electrode: Any = Field(...)
    data: Any = Field(...)
    direction: Any = Field(default="")
    phase: Any = Field(default="")
    options: Any | None = Field(default=None)

    def __init__(self, electrode, data, direction="", phase="", options=None):
        super().__init__(
            electrode=electrode,
            data=data,
            direction=direction,
            phase=phase,
            options=options,
        )


class DiffusivityFromMSMRData(BaseSchema):
    """Calculate the diffusivity from OCP data as

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
    data : pd.DataFrame
        OCP data with the following columns:
            * "Stoichiometry" : array
            * "Voltage [V]" : array
    direction : str, optional
        Specifies lithiation or delithiation for hysteresis models.
        Default is an empty string.
    phase : str, optional
        Specifies the phase ("primary" or "secondary") for composite electrode models.
        Default is an empty string.
    options : dict, optional
        Options for the calculation. The available options are:

            * "interpolator" : str
                The interpolator to use. Default is "linear". For more options, see the
                documentation for pybamm.Interpolant
            * "x tolerance" : float
                The tolerance for the stoichiometry values near 0 and 1. Default is 1e-6.
                Data points where x < tolerance or x > (1 - tolerance) are excluded
                from the calculation.
            * "minimum dUdx" : float
                The minimum value for the gradient of the open-circuit potential with
                respect to the stoichiometry. Default is 1e-6. When the absolute value
                of dU/dx is below this minimum, the corresponding y_data = x(1-x)dU/dx
                values are clipped."""

    electrode: Any = Field(...)
    data: Any = Field(...)
    direction: Any = Field(default="")
    phase: Any = Field(default="")
    options: Any | None = Field(default=None)

    def __init__(self, electrode, data, direction="", phase="", options=None):
        super().__init__(
            electrode=electrode,
            data=data,
            direction=direction,
            phase=phase,
            options=options,
        )


class DiffusivityFromMSMRFunction(BaseSchema):
    """Calculate the diffusivity from an OCP function as

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
    options : dict, optional
        Options for the calculation. The available options are:

            * "interpolator" : str
                The interpolator to use. Default is "linear". For more options, see the
                documentation for pybamm.Interpolant
            * "x tolerance" : float
                The tolerance for the stoichiometry values near 0 and 1. Default is 1e-6.
                Data points where x < tolerance or x > (1 - tolerance) are excluded
                from the calculation.
            * "minimum dUdx" : float
                The minimum value for the gradient of the open-circuit potential with
                respect to the stoichiometry. Default is 1e-6. When the absolute value
                of dU/dx is below this minimum, the corresponding y_data = x(1-x)dU/dx
                values are clipped."""

    electrode: Any = Field(...)
    voltage_limits: Any = Field(...)
    direction: Any = Field(default="")
    phase: Any = Field(default="")
    options: Any | None = Field(default=None)

    def __init__(self, electrode, voltage_limits, direction="", phase="", options=None):
        super().__init__(
            electrode=electrode,
            voltage_limits=voltage_limits,
            direction=direction,
            phase=phase,
            options=options,
        )


class DiffusivityFromPulse(BaseSchema):
    """A pipeline element that calculates the diffusion coefficient from pulse data by
    directly using the voltage data from the pulse, without the need for fitting a
    model. This method uses eqn 26 from Wang et al. [1]_ to calculate the diffusion
    coefficient.
    Advantages of this method are that it is simple and fast.
    Disadvantages are that the calculation relies on assumptions that may not be valid
    in all cases, and the results may be sensitive to noise in the data since we only
    use 4 data points to calculate the diffusion coefficient.

    Parameters
    ----------
    electrode : str
        The electrode to calculate the diffusivity for (either "positive" or "negative").
    data : dict
        A dictionary containing the pulse data. Should have columns "Current [A]",
        "Voltage [V]" and "Step number".
    direction : str, optional
        Specifies lithiation or delithiation for hysteresis models.
        Default is an empty string.
    phase : str, optional
        Specifies the phase ("primary" or "secondary") for composite electrode models.
        Default is an empty string.
    options : dict, optional
        Options for the calculation. The available options are:
            * "step number" : int
                The step number to use for the calculation. If not provided, the first
                non-rest step is used.
            * "dt_IR" : float
                The time to establish the IR drop, in seconds. If not provided, the IR drop
                is assumed to be established at the start of the pulse (first data point
                with that step number)
            * "dt_pulse" : float
                The time at which to calculate the diffusion coefficient, in seconds.
                If not provided, the diffusion coefficient will be calculated at the end of
                the pulse.

    Raises
    ------
    ValueError
        If no rest step is found after the pulse.

    References
    ----------
    .. [1] Wang, A. A., et al. "Review of parameterisation and a novel database (LiionDB)
        for continuum Li-ion battery models." Progress in Energy 4.3 (2022): 032004."""

    electrode: Any = Field(...)
    data: Any = Field(...)
    direction: Any = Field(default="")
    phase: Any = Field(default="")
    options: Any | None = Field(default=None)

    def __init__(self, electrode, data, direction="", phase="", options=None):
        super().__init__(
            electrode=electrode,
            data=data,
            direction=direction,
            phase=phase,
            options=options,
        )


class ElectrodeCapacity(BaseSchema):
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
    Calculate maximum concentration from capacity:

    >>> calc = iwp.calculations.ElectrodeCapacity("positive", use_stoich_window=False)
    >>> params = iwp.ParameterValues({
    ...     "Positive electrode capacity [A.h]": 3.0,
    ...     "Positive electrode active material volume fraction": 0.65,
    ...     "Positive electrode thickness [m]": 80e-6,
    ...     "Electrode area [m2]": 0.1,
    ...     "Positive electrode stoichiometry at maximum SOC": 1.0,
    ...     "Positive electrode stoichiometry at minimum SOC": 0.0,
    ... })
    >>> result = calc.run(params)
    >>> result["Maximum concentration in positive electrode [mol.m-3]"]"""

    electrode: Any = Field(...)
    use_stoich_window: Any = Field(default=False)
    method: Any = Field(default="auto")
    phase: Any | None = Field(default=None)

    def __init__(self, electrode, use_stoich_window=False, method="auto", phase=None):
        super().__init__(
            electrode=electrode,
            use_stoich_window=use_stoich_window,
            method=method,
            phase=phase,
        )


class ElectrodeSOH(BaseSchema):
    """Calculate electrode stoichiometry windows from capacity using electrode SOH algorithm.

    Determines minimum and maximum stoichiometries in both electrodes from OCP curves,
    electrode dimensions, and either cyclable lithium capacity or cell capacity.
    Uses the algorithm from Mohtat et al. (2019) [1]_.

    Parameters
    ----------
    options : dict, optional
        Calculation options:

        - known value : str, default="cyclable lithium capacity"
            What capacity measure is known: "cyclable lithium capacity" or "cell capacity".

    Examples
    --------
    Calculate stoichiometry windows from cell capacity:

    >>> calc = iwp.calculations.ElectrodeSOH(
    ...     options={"known value": "cell capacity"}
    ... )
    >>> params = iwp.ParameterValues({
    ...     "Nominal cell capacity [A.h]": 3.0,
    ...     "Negative electrode OCP [V]": ocp_neg,
    ...     "Positive electrode OCP [V]": ocp_pos,
    ...     # ... other required parameters
    ... })
    >>> result = calc.run(params)
    >>> result["Negative electrode stoichiometry at 100% SOC"]
    0.95

    References
    ----------
    .. [1] Mohtat, P., Lee, S., Siegel, J. B., & Stefanopoulou, A. G. (2019). Towards
           better estimability of electrode-specific state of health: Decoding the cell
           expansion. Journal of Power Sources, 427, 101-111."""

    options: Any | None = Field(default=None)

    def __init__(self, options=None):
        super().__init__(options=options)


class ElectrodeSOHHalfCell(BaseSchema):
    """Calculate minimum and maximum electrode stoichiometries for a half-cell using the
    electrode-specific SOH algorithm.

    See :class:`ElectrodeSOH` for more details.

    Parameters
    ----------
    electrode : str
        The electrode to calculate the initial concentration for, either "positive" or
        "negative".
    options : dict, optional
        A dictionary of options to be passed to the calculation. The following options
        are available:

            * simulation_kwargs: dict
                Keyword arguments to pass to the simulation (:class:`iwp.Simulation`).
                Default is None."""

    electrode: Any = Field(...)
    options: Any | None = Field(default=None)

    def __init__(self, electrode, options=None):
        super().__init__(electrode=electrode, options=options)


class ElectrodeVolumeFractionFromLoading(BaseSchema):
    """Calculate the volume fraction of active material in the electrodes from the loading and maximum concentration or from the coating mass and crystal density.

    Parameters
    ----------
    electrode : ["positive", "negative", "both"]
        The electrode to calculate the volume fraction for.
    method : ["loading", "coating mass"]
        The method to use to calculate the volume fraction."""

    electrode: Any = Field(...)
    method: Any = Field(...)

    def __init__(self, electrode, method):
        super().__init__(electrode=electrode, method=method)


class ElectrodeVolumeFractionFromPorosity(BaseSchema):
    """Calculate the volume fraction of active material in the electrodes from the
    porosity and the active volume fraction of solid.

    Parameters
    ----------
    electrode : str
        The electrode to calculate the volume fraction for. Must be either "negative"
        or "positive"."""

    electrode: Any = Field(...)

    def __init__(self, electrode):
        super().__init__(electrode=electrode)


class EntropicChangeDataInterpolant(BaseSchema):
    """Create an interpolant for the open-circuit entropic change from data.

    Parameters
    ----------
    electrode : str
        The electrode to create the interpolant for, either "positive", "negative",
        or "lumped". If "lumped", assumes a single electrode and modifies parameter
        names accordingly.
    data : pandas.DataFrame
        The data to use for the interpolant. Must have columns "Stoichiometry" and
        "Entropic change [V.K-1]".
    options : dict, optional
        A dictionary of options to pass to the calculation.

        * interpolator: str, optional
            The interpolator to use for the interpolant. Can be "linear" or
            "cubic". Default is "linear".
        * tolerance: float
            The tolerance to use when restricting the data to avoid interpolation
            issues. Default is 1e-6.
        * phase: str, optional
            The phase of the electrode, either "primary" or "secondary".
            Default is None, which means no phase is assumed.
        * scale factor: float, optional
            The scale factor to apply to the entropic change. Default is 1."""

    electrode: Any = Field(...)
    data: Any = Field(...)
    options: Any | None = Field(default=None)

    def __init__(self, electrode, data, options=None):
        super().__init__(electrode=electrode, data=data, options=options)


class EntropicChangeFromMSMRFunction(BaseSchema):
    """Create an interpolant for the open-circuit entropic change from MSMR parameters.

    Parameters
    ----------
    electrode : str
        The electrode to create the interpolant for, either "positive" or "negative".
    voltage_limits : tuple of float
        The voltage limits to use to generate data for the interpolant.
    options : dict, optional
        A dictionary of options to pass to the calculation.

        * interpolator: str, optional
            The interpolator to use for the interpolant. Can be "linear" or
            "cubic". Default is "linear".
        * tolerance: float
            The tolerance to use when restricting the data to avoid interpolation
            issues. Default is 1e-6.
        * phase: str, optional
            The phase of the electrode, either "primary" or "secondary".
            Default is None, which means no phase is assumed.
        * scale factor: float, optional
            The scale factor to apply to the entropic change. Default is 1."""

    electrode: Any = Field(...)
    voltage_limits: Any = Field(...)
    options: Any | None = Field(default=None)

    def __init__(self, electrode, voltage_limits, options=None):
        super().__init__(
            electrode=electrode, voltage_limits=voltage_limits, options=options
        )


class HalfCellNominalCapacity(BaseSchema):
    """Set nominal cell capacity and current function equal to electrode capacity.

    For half-cell models, the cell capacity is determined by the working electrode
    capacity. This calculation copies the electrode capacity to the cell-level
    parameters required by PyBaMM.

    Parameters
    ----------
    electrode : str
        Working electrode: "negative" or "positive".

    Examples
    --------
    >>> calc = iwp.calculations.HalfCellNominalCapacity("positive")
    >>> params = iwp.ParameterValues({"Positive electrode capacity [A.h]": 3.0})
    >>> result = calc.run(params)
    >>> result["Nominal cell capacity [A.h]"]
    3.0"""

    electrode: Any = Field(...)

    def __init__(self, electrode):
        super().__init__(electrode=electrode)


class InitialConcentrationFromInitialStoichiometryHalfCell(BaseSchema):
    """Calculate the initial concentration in the given electrode from the initial
    stoichiometry and maximum concentration.

    Parameters
    ----------
    electrode : str
        The electrode to calculate the initial concentration for, either "positive" or
        "negative".
    options : dict, optional
        A dictionary of options to be passed to the calculation. The following options
        are available:

            * phase: str
                The phase to solve for the initial concentration. Can be "primary" or
                "secondary". Default is None."""

    electrode: Any = Field(...)
    options: Any | None = Field(default=None)

    def __init__(self, electrode, options=None):
        super().__init__(electrode=electrode, options=options)


class InitialSOC(BaseSchema):
    """Calculate initial electrode concentrations from target SOC.

    Converts a state-of-charge value to electrode stoichiometries and absolute
    concentrations using stoichiometry windows and maximum concentrations.

    Parameters
    ----------
    soc : float
        Target state of charge (0.0 to 1.0).

    Examples
    --------
    >>> calc = iwp.calculations.InitialSOC(soc=0.5)
    >>> params = iwp.ParameterValues({
    ...     "Negative electrode stoichiometry at 0% SOC": 0.05,
    ...     "Negative electrode stoichiometry at 100% SOC": 0.95,
    ...     "Maximum concentration in negative electrode [mol.m-3]": 28000,
    ...     # ... positive electrode parameters
    ... })
    >>> result = calc.run(params)
    >>> result["Initial stoichiometry in negative electrode"]
    0.5"""

    soc: Any = Field(...)

    def __init__(self, soc):
        super().__init__(soc=soc)


class InitialSOCHalfCell(BaseSchema):
    """Calculate initial electrode concentration from target SOC for half-cell.

    Converts SOC to stoichiometry and absolute concentration for the working
    electrode in half-cell models.

    Parameters
    ----------
    electrode : str
        Working electrode: "negative" or "positive".
    soc : float | int | str
        Target SOC. Can be numeric (0.0-1.0) or string ("0%", "100%",
        "minimum", "maximum").
    options : dict, optional
        Calculation options:

        - phase : str | None, default=None
            Phase for multi-phase materials: "primary" or "secondary".

    Examples
    --------
    Numeric SOC:

    >>> calc = iwp.calculations.InitialSOCHalfCell("positive", soc=0.5)
    >>> result = calc.run(params)
    >>> result["Initial stoichiometry in positive electrode"]
    0.5

    String SOC:

    >>> calc = iwp.calculations.InitialSOCHalfCell("positive", soc="100%")
    >>> result = calc.run(params)
    >>> result["Initial stoichiometry in positive electrode"]
    0.95"""

    electrode: Any = Field(...)
    soc: Any = Field(...)
    options: Any | None = Field(default=None)

    def __init__(self, electrode, soc, options=None):
        super().__init__(electrode=electrode, soc=soc, options=options)


class InitialSOCfromMaximumStoichiometry(BaseSchema):
    """Calculate the initial concentration in the negative and positive electrodes from
    the initial SOC and stoichiometry windows in each electrode.

    Parameters
    ----------
    options : dict, optional
        A dictionary of options to be passed to the calculation. The following options
        are available:

            * particle phases: tuple of str
                Specifies the number of phases for each electrode as a tuple
                (negative, positive). Each element can be "1" (single phase) or "2"
                (composite with Primary and Secondary phases). Default is ("1", "1")."""

    options: Any | None = Field(default=None)

    def __init__(self, options=None):
        super().__init__(options=options)


class InitialStoichiometryFromVoltageHalfCell(BaseSchema):
    """Calculate the initial stoichiometry in the given electrode from the initial
    voltage (i.e. find the stoichiometry that gives the correct voltage).

    Parameters
    ----------
    electrode : str
        The electrode to calculate the initial concentration for, either "positive" or
        "negative".
    options : dict, optional
        A dictionary of options to be passed to the calculation. The following options
        are available:

            * simulation_kwargs: dict
                Keyword arguments to pass to the simulation (:class:`iwp.Simulation`).
                Default is `{"solver": pybamm.AlgebraicSolver()}`.
            * direction: str
                The direction to solve for the initial stoichiometry. Can be "lithiation"
                or "delithiation". Default is None, which means no directionality is
                assumed.
            * phase: str
                The phase to solve for the initial stoichiometry. Can be "primary" or
                "secondary". Default is None."""

    electrode: Any = Field(...)
    options: Any | None = Field(default=None)

    def __init__(self, electrode, options=None):
        super().__init__(electrode=electrode, options=options)


class InitialStoichiometryFromVoltageMSMRHalfCell(BaseSchema):
    """Calculate the initial stoichiometry in the given electrode from the initial
    voltage (i.e. find the stoichiometry that gives the correct voltage) using the
    MSMR framework.

    Parameters
    ----------
    electrode : str
        The electrode to calculate the initial concentration for, either "positive" or
        "negative"."""

    electrode: Any = Field(...)

    def __init__(self, electrode):
        super().__init__(electrode=electrode)


class InitialVoltageFromConcentration(BaseSchema):
    """Calculate initial voltage from target concentration using OCP inversion.

    Finds the voltage that produces a target electrode concentration by
    numerically inverting the lithiation function.

    Parameters
    ----------
    electrode : str
        Electrode: "negative" or "positive".

    Examples
    --------
    >>> calc = iwp.calculations.InitialVoltageFromConcentration("positive")
    >>> params = iwp.ParameterValues({
    ...     "Positive electrode lithiation": lambda U: ...,  # OCP function
    ...     "Maximum concentration in positive electrode [mol.m-3]": 50000,
    ...     "Initial concentration in positive electrode [mol.m-3]": 25000,
    ... })
    >>> result = calc.run(params)
    >>> result["Initial voltage in positive electrode [V]"]
    3.8"""

    electrode: Any = Field(...)

    def __init__(self, electrode):
        super().__init__(electrode=electrode)


class JellyRollThermalDimensions(BaseSchema):
    """Calculate thermal properties of cylindrical jelly roll cell.

    Computes volume and surface area from jelly roll radius and height,
    assuming cylindrical geometry for thermal modeling.

    Examples
    --------
    >>> calc = iwp.calculations.JellyRollThermalDimensions()
    >>> params = iwp.ParameterValues({
    ...     "Jelly roll height [m]": 0.065,
    ...     "Jelly roll radius [m]": 0.009,
    ... })
    >>> result = calc.run(params)
    >>> result["Cell volume [m3]"]
    1.65e-5"""

    pass


class LumpedHeatCapacityAndDensity(BaseSchema):
    """Sets the specific heat capacity and density for each cell component to the lumped
    (cell-level) values."""

    pass


class MSMRElectrodeSOHHalfCell(BaseSchema):
    """Calculate minimum and maximum electrode stoichiometries for a half-cell by
    evaluating the extent of lithiation at the minimum and maximum OCV.

    See :class:`ElectrodeSOH` for more details.

    Parameters
    ----------
    electrode : str
        The electrode to calculate the minimum and maximum stoichiometries for."""

    electrode: Any = Field(...)

    def __init__(self, electrode):
        super().__init__(electrode=electrode)


class MSMRFullCellCapacities(BaseSchema):
    """A pipeline element that calculates variables related to the capacity from the MSMR
    full-cell balance.

    Parameters
    ----------
    data : str or dict
        The data to use to calculate the useable capacity, see :class:`FittingObjective`.
    parameter_format : str, optional
        The format of the parameters to fit. One parameter is always the lower excess
        capacity, and this option determines the other parameter, which can be either
        the total capacity or the upper excess capacity. Default is "total capacity".
        (Q_tot = Q_lowex + Q_use + Q_uppex)"""

    data: Any = Field(...)
    method: Any = Field(default="total capacity")

    def __init__(self, data, method="total capacity"):
        super().__init__(data=data, method=method)


class MSMRFunction(BaseSchema):
    """Specifies the MSMR function for the open-circuit potential for the given electrode.

    Parameters
    ----------
    electrode : str
        The name of the electrode.
    direction : str, optional
        The direction of the MSMR function.
    phase : str, optional
        The phase of the MSMR function."""

    electrode: Any = Field(...)
    direction: Any | None = Field(default=None)
    phase: Any | None = Field(default=None)

    def __init__(self, electrode, direction=None, phase=None):
        super().__init__(electrode=electrode, direction=direction, phase=phase)


class OCPDataInterpolant(BaseSchema):
    """Create an interpolant for the open-circuit voltage (OCP) from data.

    Parameters
    ----------
    electrode : str
        The electrode to create the interpolant for, either "positive", "negative",
        or "lumped". If "lumped", assumes a single electrode and modifies parameter
        names accordingly.
    data : pd.DataFrame | iwdata.OCPDataLoader
        The data to use for the interpolant. Must have columns "Stoichiometry" and
        "Voltage [V]".
    options : dict, optional
        A dictionary of options to pass to the calculation.

        * interpolator: str, optional
            The interpolator to use for the interpolant. Can be "linear" or
            "cubic". Default is "linear".
        * tolerance: float
            The tolerance to use when restricting the data to avoid interpolation
            issues. Default is 1e-6.
        * direction: str
            The direction of the OCP, either "lithiation" or "delithiation".
            Default is None, which means no directionality is assumed.
        * phase: str, optional
            The phase of the electrode, either "primary" or "secondary".
            Default is None, which means no phase is assumed."""

    electrode: Any = Field(...)
    data: Any = Field(...)
    options: Any | None = Field(default=None)

    def __init__(self, electrode, data, options=None):
        super().__init__(electrode=electrode, data=data, options=options)


class OCPDataInterpolantMSMRExtrapolation(BaseSchema):
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
    data : pd.DataFrame | iwdata.OCPDataLoader
        The data to use for the interpolant. Must have columns "Capacity [A.h]" and
        "Voltage [V]".
    voltage_limits : tuple of float
        The voltage limits to use to generate MSMR data for extrapolation.
    options : dict, optional
        A dictionary of options to pass to the calculation.

        * interpolator: str, optional
            The interpolator to use for the interpolant. Can be "linear" or
            "cubic". Default is "linear".
        * tolerance: float
            The tolerance to use when restricting the data to avoid interpolation
            issues. Default is 1e-6.
        * direction: str
            The direction of the OCP, either "lithiation" or "delithiation".
            Default is None, which means no directionality is assumed.
        * phase: str, optional
            The phase of the electrode, either "primary" or "secondary".
            Default is None, which means no phase is assumed."""

    electrode: Any = Field(...)
    data: Any = Field(...)
    voltage_limits: Any = Field(...)
    options: Any | None = Field(default=None)

    def __init__(self, electrode, data, voltage_limits, options=None):
        super().__init__(
            electrode=electrode,
            data=data,
            voltage_limits=voltage_limits,
            options=options,
        )


class OCPMSMRInterpolant(BaseSchema):
    """Create an interpolant for the open-circuit voltage (OCP) from MSMR parameters.

    Parameters
    ----------
    electrode : str
        The electrode to create the interpolant for, either "positive" or "negative".
    voltage_limits : tuple of float
        The voltage limits to use to generate data for the interpolant.
    options : dict, optional
        A dictionary of options to pass to the calculation.

        * interpolator: str, optional
            The interpolator to use for the interpolant. Can be "linear" or
            "cubic". Default is "linear".
        * tolerance: float
            The tolerance to use when restricting the data to avoid interpolation
            issues. Default is 1e-6.
        * direction: str
            The direction of the OCP, either "lithiation" or "delithiation".
            Default is None, which means no directionality is assumed.
        * phase: str, optional
            The phase of the electrode, either "primary" or "secondary".
            Default is None, which means no phase is assumed.
        * create_lithiation_function: bool
            Whether to create a lithiation function from the interpolant.
            Default is True."""

    electrode: Any = Field(...)
    voltage_limits: Any = Field(...)
    options: Any | None = Field(default=None)

    def __init__(self, electrode, voltage_limits, options=None):
        super().__init__(
            electrode=electrode, voltage_limits=voltage_limits, options=options
        )


class OpenCircuitLimits(BaseSchema):
    """Set OCV limits equal to voltage cutoffs for SOC calculations.

    Copies voltage cutoff parameters to OCV limit parameters, establishing the
    relationship between SOC and voltage windows.

    Examples
    --------
    >>> calc = iwp.calculations.OpenCircuitLimits()
    >>> params = iwp.ParameterValues({
    ...     "Lower voltage cut-off [V]": 2.5,
    ...     "Upper voltage cut-off [V]": 4.2,
    ... })
    >>> result = calc.run(params)
    >>> result["Open-circuit voltage at 0% SOC [V]"]
    2.5"""

    pass


class PorosityFromElectrodeVolumeFraction(BaseSchema):
    """Calculate the porosity from the active material volume fraction.

    Parameters
    ----------
    electrode : str
        The electrode to calculate the porosity for. Must be either "negative"
        or "positive"."""

    electrode: Any = Field(...)

    def __init__(self, electrode):
        super().__init__(electrode=electrode)


class PouchCellThermalDimensions(BaseSchema):
    """Calculate thermal properties of rectangular pouch cell.

    Computes volume and surface area from pouch dimensions, assuming
    rectangular prism geometry for thermal modeling.

    Examples
    --------
    >>> calc = iwp.calculations.PouchCellThermalDimensions()
    >>> params = iwp.ParameterValues({
    ...     "Pouch height [m]": 0.1,
    ...     "Pouch width [m]": 0.08,
    ...     "Pouch thickness [m]": 0.006,
    ... })
    >>> result = calc.run(params)
    >>> result["Cell cooling surface area [m2]"]
    0.0256"""

    pass


class SlopesToKnots(BaseSchema):
    """Converts slopes and initial value to knot values for piecewise linear interpolation.

    This calculation takes as input:
    - An initial value at the first breakpoint
    - Slopes for each segment between consecutive breakpoints

    And outputs:
    - The value at each breakpoint (knot values)

    The conversion follows: y_{i+1} = y_i + slope_i * (x_{i+1} - x_i)

    Parameters
    ----------
    base_parameter_name : str
        The name of the parameter (e.g., "Particle diffusion time [s]")
    breakpoint_values : list[float]
        List of breakpoint values (e.g., [0.0, 0.5, 1.0])
    breakpoint_parameter_name : str
        Name of the breakpoint parameter (e.g., "SOC", "Temperature [K]")

    Example
    -------
    >>> # Convert slopes to knots
    >>> calc = SlopesToKnots(
    ...     base_parameter_name="Particle diffusion time [s]",
    ...     breakpoint_values=[0.0, 0.5, 1.0],
    ...     breakpoint_parameter_name="SOC"
    ... )
    >>> # Provide initial value and slopes
    >>> param_values = {
    ...     "Particle diffusion time at SOC 0 [s]": 500.0,
    ...     "Particle diffusion time slope from SOC 0 to 0.5 [s]": 1000.0,
    ...     "Particle diffusion time slope from SOC 0.5 to 1 [s]": 2000.0,
    ... }
    >>> result = calc.run(param_values)
    >>> # Result will contain:
    >>> # {
    >>> #     "Particle diffusion time at SOC 0 [s]": 500.0,
    >>> #     "Particle diffusion time at SOC 0.5 [s]": 1500.0,  # 500 + 1000*(0.5-0)
    >>> #     "Particle diffusion time at SOC 1 [s]": 3500.0,    # 1500 + 2000*(1-0.5)
    >>> # }"""

    base_parameter_name: Any = Field(...)
    breakpoint_values: Any = Field(...)
    breakpoint_parameter_name: Any = Field(...)

    def __init__(
        self, base_parameter_name, breakpoint_values, breakpoint_parameter_name
    ):
        super().__init__(
            base_parameter_name=base_parameter_name,
            breakpoint_values=breakpoint_values,
            breakpoint_parameter_name=breakpoint_parameter_name,
        )


class SlopesToKnots2D(BaseSchema):
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
        Name of the second breakpoint parameter (e.g., "Temperature [K]")

    Example
    -------
    >>> # Convert 2D slopes to knots
    >>> calc = SlopesToKnots2D(
    ...     base_parameter_name="Diffusivity [m2.s-1]",
    ...     breakpoint1_values=[0.0, 1.0],
    ...     breakpoint1_parameter_name="SOC",
    ...     breakpoint2_values=[273.15, 323.15],
    ...     breakpoint2_parameter_name="Temperature [K]"
    ... )
    >>> # Provide initial value and slopes
    >>> param_values = {
    ...     "Diffusivity at SOC 0, Temperature [K] 273.15 [m2.s-1]": 1e-14,
    ...     "Diffusivity SOC-slope from SOC 0 to 1 at Temperature [K] 273.15 [m2.s-1]": 2e-14,
    ...     "Diffusivity Temperature [K]-slope from Temperature [K] 273.15 to 323.15 at SOC 0 [m2.s-1]": 2e-15,
    ...     "Diffusivity Temperature [K]-slope from Temperature [K] 273.15 to 323.15 at SOC 1 [m2.s-1]": 2e-15,
    ... }
    >>> result = calc.run(param_values)
    >>> # Result will contain knot values at all 4 grid points"""

    base_parameter_name: Any = Field(...)
    breakpoint1_values: Any = Field(...)
    breakpoint1_parameter_name: Any = Field(...)
    breakpoint2_values: Any = Field(...)
    breakpoint2_parameter_name: Any = Field(...)

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


class SpecificHeatCapacity(BaseSchema):
    """Calculate the specific heat capacity from the lumped heat capacity and cell mass"""

    pass


class StoichiometryAtMinimumSOC(BaseSchema):
    """Calculate the stoichiometry at the minimum SOC based on the stoichiometry at the
    maximum SOC, the electrode capacities, and the useable capacity.

    Parameters
    ----------
    electrode : str
        The electrode to calculate the initial concentration for, either "positive" or
        "negative"."""

    electrode: Any = Field(...)

    def __init__(self, electrode):
        super().__init__(electrode=electrode)


class StoichiometryLimitsFromCapacity(BaseSchema):
    """Calculate the minimum and maximum stoichiometries for each electrode in a full-cell
    based on the electrode total capacity, lower and upper excess capacities.

    Parameters
    ----------
    options : dict, optional
        A dictionary of options to be passed to the calculation. The following options
        are available:

            * direction: str
                The direction to use for the calculation. Can be "charge" or "discharge".
                Default is None. If a direction is specified, the lower and upper excess
                capacities are calculated based on the direction.
            * particle phases: tuple of str
                Specifies the number of phases for each electrode as a tuple
                (negative, positive). Each element can be "1" (single phase) or "2"
                (composite with Primary and Secondary phases). Default is ("1", "1")."""

    options: Any | None = Field(default=None)

    def __init__(self, options=None):
        super().__init__(options=options)


class SurfaceAreaToVolumeRatio(BaseSchema):
    """Calculate the surface area to volume ratio for the electrodes from the active
    material volume fraction and particle radius, assuming spherical particles.

    Parameters
    ----------
    electrode : str
        The electrode to calculate the surface area to volume ratio for, either
        "positive", "negative" or "both"."""

    electrode: Any = Field(...)

    def __init__(self, electrode):
        super().__init__(electrode=electrode)
