"""Light wrapper schemas for iwp.direct_entries functions.

Each schema validates args/kwargs and serializes to {"name": <name>, **kwargs}
for the pipeline parser. Use via iws.direct_entries.<snake_case_name>(...).
"""

from typing import Any

from pydantic import Field

from ..base import BaseSchema


class DirectEntryFunctionSchema(BaseSchema):
    """Base wrapper for named ``iwp.direct_entries`` helper functions.

    Subclasses set ``__function_name__`` (the snake_case pipeline function
    name) and declare ``Field`` attributes matching that function's
    signature. ``to_config`` serialises to ``{"name": <function_name>,
    **kwargs}`` so the pipeline parser can reconstruct the corresponding
    DirectEntry at run time.

    Examples
    --------
    >>> # every concrete subclass follows the same construction pattern;
    >>> # exposed under its snake_case name in ``iws.direct_entries``
    >>> entry = iws.direct_entries.bruggeman(electrode=1.5, electrolyte=1.5)
    >>> config = iws.Pipeline({"bruggeman": entry}).to_config()
    >>> # then submit `config` via ionworks-api
    """

    def to_config(self) -> dict:
        """Build the dict you submit through ``ionworks-api``.

        The output is ``{"name": "<function_name>", **kwargs}`` where
        ``<function_name>`` is the snake_case name of the helper this
        wraps (``"average_ocp"``, ``"bruggeman"``, …) and ``**kwargs``
        are the arguments you set on this schema. Default and empty
        values are omitted to keep the payload minimal.
        """
        data = self.model_dump(exclude_none=True)
        name = getattr(self.__class__, "__function_name__", "")
        out: dict[str, Any] = {"name": name}
        for k, v in data.items():
            if k == "name" or v == "":
                continue
            out[k] = v
        return out


# ---------------------------------------------------------------------------
# Exchange current density
# ---------------------------------------------------------------------------


class ArrheniusButlerVolmerExchangeCurrentDensity(DirectEntryFunctionSchema):
    """Standard Butler-Volmer exchange-current density with Arrhenius temperature dependence.

    Produces a function of electrolyte concentration, surface concentration,
    maximum solid concentration, and temperature, leaving the reference
    exchange-current density and reaction activation energy as free
    parameters (typically fit to data).
    """

    __function_name__ = "arrhenius_butler_volmer_exchange_current_density"

    electrode: str = Field(
        ...,
        description=(
            "Which electrode to build the exchange-current density for. "
            "Must be ``'negative'`` or ``'positive'``."
        ),
    )
    direction: str = Field(
        default="",
        description=(
            "Optional reaction direction discriminator: ``'lithiation'``, "
            "``'delithiation'``, or ``''`` (single direction). Default is "
            "``''``."
        ),
    )
    phase: str = Field(
        default="",
        description=(
            "Phase prefix for composite electrode models: ``'primary'``, "
            "``'secondary'``, or ``''`` (single phase). Default is ``''``."
        ),
    )


# ---------------------------------------------------------------------------
# Particle diffusivity
# ---------------------------------------------------------------------------


class ArrheniusParticleDiffusivity(DirectEntryFunctionSchema):
    """Particle reference diffusivity with Arrhenius temperature dependence.

    Produces a function of stoichiometry and temperature, leaving the
    reference
    diffusivity and activation energy as free parameters.
    """

    __function_name__ = "arrhenius_particle_diffusivity"

    electrode: str = Field(
        ...,
        description=(
            "Which electrode to build the particle diffusivity for. Must be "
            "``'negative'`` or ``'positive'``."
        ),
    )
    direction: str = Field(
        default="",
        description=(
            "Optional reaction direction discriminator: ``'lithiation'``, "
            "``'delithiation'``, or ``''``. Default is ``''``."
        ),
    )
    phase: str = Field(
        default="",
        description=(
            "Phase prefix for composite electrode models: ``'primary'``, "
            "``'secondary'``, or ``''``. Default is ``''``."
        ),
    )


# ---------------------------------------------------------------------------
# OCP
# ---------------------------------------------------------------------------


class AverageOCP(DirectEntryFunctionSchema):
    """Average of delithiation and lithiation OCP functions for an electrode.

    Produces a single OCP
    function equal to the mean of the electrode's lithiation and
    delithiation OCPs, suitable when hysteresis is not being modelled
    explicitly.
    """

    __function_name__ = "average_ocp"

    electrode: str = Field(
        ...,
        description=(
            "Which electrode to build the averaged OCP for. Must be "
            "``'negative'`` or ``'positive'``."
        ),
    )
    phase: str | None = Field(
        default=None,
        description=(
            "Phase specifier for composite electrode models: ``'primary'``, "
            "``'secondary'``, or ``None`` for single-phase electrodes. "
            "Default is ``None``."
        ),
    )


# ---------------------------------------------------------------------------
# Electrolyte
# ---------------------------------------------------------------------------


class ConstantElectrolyte(DirectEntryFunctionSchema):
    """Constant electrolyte concentration.

    Sets the initial electrolyte concentration to the supplied value.
    """

    __function_name__ = "constant_electrolyte"

    c_e: float = Field(
        ...,
        description="Initial electrolyte concentration in ``mol.m-3``.",
    )


class NymanElectrolyte(DirectEntryFunctionSchema):
    """Nyman et al. (2008) electrolyte parameters with user-specified initial concentration.

    Supplies concentration-dependent electrolyte diffusivity and conductivity
    from Nyman et al.
    (2008), along with transference number and thermodynamic factor.
    """

    __function_name__ = "nyman_electrolyte"

    c_e: float = Field(
        ...,
        description=(
            "Initial electrolyte concentration in ``mol.m-3``. Used to seed "
            "the simulation; the diffusivity/conductivity remain functions "
            "of concentration and temperature."
        ),
    )


class ArrheniusElectrolyteDiffusivity(DirectEntryFunctionSchema):
    """Reference electrolyte diffusivity multiplied by an Arrhenius temperature factor.

    Leaves the reference diffusivity and activation energy as free parameters
    (no
    fields to set on the schema).
    """

    __function_name__ = "arrhenius_electrolyte_diffusivity"


class ArrheniusElectrolyteConductivity(DirectEntryFunctionSchema):
    """Reference electrolyte conductivity multiplied by an Arrhenius temperature factor.

    Leaves the reference conductivity and activation energy as free
    parameters (no fields to set on the schema).
    """

    __function_name__ = "arrhenius_electrolyte_conductivity"


class LandesfeindElectrolyte(DirectEntryFunctionSchema):
    """Landesfeind et al. (2019) electrolyte parameters for a given solvent system.

    Supplies concentration- and temperature-dependent conductivity,
    diffusivity,
    thermodynamic factor, and transference number for one of a fixed list
    of electrolyte systems.
    """

    __function_name__ = "landesfeind_electrolyte"

    c_e: float = Field(
        ...,
        description="Initial electrolyte concentration in ``mol.m-3``.",
    )
    system: str = Field(
        ...,
        description=(
            "Electrolyte system name. Must be one of ``'EC:DMC (1:1)'``, "
            "``'EC:EMC (3:7)'``, or ``'EMC:FEC (19:1)'``."
        ),
    )


# ---------------------------------------------------------------------------
# Thermal
# ---------------------------------------------------------------------------


class Temperatures(DirectEntryFunctionSchema):
    """Set reference, ambient, and initial temperatures to a single value.

    Useful for isothermal simulations where all three temperature parameters
    share the same
    value.
    """

    __function_name__ = "temperatures"

    T: float = Field(
        default=298.15,
        description=(
            "Temperature in Kelvin used for ``Reference temperature [K]``, "
            "``Ambient temperature [K]``, and ``Initial temperature [K]``. "
            "Default is 298.15 K (25 degrees C)."
        ),
    )


class ZeroEntropicChange(DirectEntryFunctionSchema):
    """Zero the negative- and positive-electrode OCP entropic change terms.

    Useful when entropic heating is ignored or the data needed to parameterise
    it is
    unavailable. No fields to set.
    """

    __function_name__ = "zero_entropic_change"


class ZeroActivationEnergy(DirectEntryFunctionSchema):
    """Zero out all diffusivity/kinetic activation energies.

    Disables the
    Arrhenius temperature dependence of diffusivities, reaction rates, and
    electrolyte transport. No fields to set.
    """

    __function_name__ = "zero_activation_energy"


# ---------------------------------------------------------------------------
# Direct entry (file / defaults / geometry / etc.)
# ---------------------------------------------------------------------------


class FromJson(DirectEntryFunctionSchema):
    """Load parameter values from a JSON file.

    Reads a JSON file of
    ``{parameter_name: value}`` pairs and returns a ``DirectEntry`` with
    those values. pybamm-serialised symbols are rehydrated automatically.
    """

    __function_name__ = "from_json"

    file_path: str = Field(
        ...,
        description=(
            "Absolute or relative path to the JSON file containing the "
            "parameter values."
        ),
    )


class StandardDefaults(DirectEntryFunctionSchema):
    """Standard defaults for series/parallel cell multipliers.

    Sets
    ``Number of cells connected in series to make a battery`` and
    ``Number of electrodes connected in parallel to make a cell`` to 1. No
    fields to set.
    """

    __function_name__ = "standard_defaults"


class OneCm2Cell(DirectEntryFunctionSchema):
    """Geometry for a 1 cm^2 cell.

    Sets ``Electrode height
    [m]`` and ``Electrode width [m]`` to 1 cm so current in A equals current
    density in A.cm^-2. No fields to set.
    """

    __function_name__ = "one_cm2_cell"


class Bruggeman(DirectEntryFunctionSchema):
    """Bruggeman coefficients for electrode and electrolyte tortuosity.

    Sets the Bruggeman exponents
    used to derive effective electrolyte and electrode transport properties
    from their bulk values.
    """

    __function_name__ = "bruggeman"

    electrode: float = Field(
        default=0,
        description=(
            "Bruggeman exponent for the electrode solid phase. Default 0 "
            "(no tortuosity correction on the solid phase)."
        ),
    )
    electrolyte: float = Field(
        default=1.5,
        description=(
            "Bruggeman exponent for the electrolyte phase in both "
            "electrodes and separator. Default 1.5 (the classic Bruggeman "
            "value)."
        ),
    )


class SpmDefaults(DirectEntryFunctionSchema):
    """Non-voltage-affecting defaults required by the SPM model.

    Sets parameters (e.g.
    separator/positive-electrode geometry, entropic change) to values that
    do not affect voltage but are still required by the SPM parameter
    set. No fields to set.
    """

    __function_name__ = "spm_defaults"


class LithiumMetalAnode(DirectEntryFunctionSchema):
    """Generic lithium-metal counter-electrode parameter set.

    Supplies parameter
    values that do not add overpotential, for use as a counter electrode in
    half-cell fits. No fields to set.
    """

    __function_name__ = "lithium_metal_anode"


class SeiDefaults(DirectEntryFunctionSchema):
    """Default SEI-layer degradation parameters.

    Provides the SEI kinetic
    and transport parameters from O'Kane et al. (2022). No fields to set.
    """

    __function_name__ = "sei_defaults"


class LiPlatingDefaults(DirectEntryFunctionSchema):
    """Default lithium-plating parameters.

    Provides plating /
    stripping exchange-current densities and SEI-limited dead-lithium decay
    rates from O'Kane et al. (2022). No fields to set.
    """

    __function_name__ = "li_plating_defaults"


class MechanicalDegradationDefaults(DirectEntryFunctionSchema):
    """Default mechanical-degradation parameters for one electrode.

    Supplies crack-growth, volume-change, and LAM parameters from
    O'Kane et al. (2022) for either the negative or positive electrode.
    """

    __function_name__ = "mechanical_degradation_defaults"

    electrode: str = Field(
        ...,
        description=(
            "Which electrode the mechanical-degradation parameters apply "
            "to. Must be ``'negative'`` or ``'positive'``."
        ),
    )


# ---------------------------------------------------------------------------
# Public mapping: snake_case name -> schema class (for direct_entries module)
# ---------------------------------------------------------------------------

FUNCTION_SCHEMAS = {
    "arrhenius_butler_volmer_exchange_current_density": ArrheniusButlerVolmerExchangeCurrentDensity,
    "arrhenius_electrolyte_conductivity": ArrheniusElectrolyteConductivity,
    "arrhenius_electrolyte_diffusivity": ArrheniusElectrolyteDiffusivity,
    "arrhenius_particle_diffusivity": ArrheniusParticleDiffusivity,
    "average_ocp": AverageOCP,
    "bruggeman": Bruggeman,
    "constant_electrolyte": ConstantElectrolyte,
    "from_json": FromJson,
    "landesfeind_electrolyte": LandesfeindElectrolyte,
    "li_plating_defaults": LiPlatingDefaults,
    "lithium_metal_anode": LithiumMetalAnode,
    "mechanical_degradation_defaults": MechanicalDegradationDefaults,
    "nyman_electrolyte": NymanElectrolyte,
    "one_cm2_cell": OneCm2Cell,
    "sei_defaults": SeiDefaults,
    "spm_defaults": SpmDefaults,
    "standard_defaults": StandardDefaults,
    "temperatures": Temperatures,
    "zero_activation_energy": ZeroActivationEnergy,
    "zero_entropic_change": ZeroEntropicChange,
}
