"""Light wrapper schemas for iwp.direct_entries functions.

Each schema validates args/kwargs and serializes to {"name": <name>, **kwargs}
for the pipeline parser. Use via iws.direct_entries.<snake_case_name>(...).
"""

from typing import Any

from pydantic import Field

from ..base import BaseSchema


class DirectEntryFunctionSchema(BaseSchema):
    """
    Base for direct-entry function wrappers. Subclasses set __function_name__
    and declare fields matching the pipeline function signature.
    """

    def to_config(self) -> dict:
        """Parser format: name + kwargs; omit default/empty for minimal config."""
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
    __function_name__ = "arrhenius_butler_volmer_exchange_current_density"

    electrode: str = Field(..., description="Electrode: 'negative' or 'positive'")
    direction: str = Field(default="", description="'lithiation', 'delithiation', or ''")
    phase: str = Field(default="", description="'primary', 'secondary', or ''")


# ---------------------------------------------------------------------------
# Particle diffusivity
# ---------------------------------------------------------------------------


class ArrheniusParticleDiffusivity(DirectEntryFunctionSchema):
    __function_name__ = "arrhenius_particle_diffusivity"

    electrode: str = Field(..., description="Electrode: 'negative' or 'positive'")
    direction: str = Field(default="", description="Direction or ''")
    phase: str = Field(default="", description="Phase or ''")


# ---------------------------------------------------------------------------
# OCP
# ---------------------------------------------------------------------------


class AverageOcp(DirectEntryFunctionSchema):
    __function_name__ = "average_ocp"

    electrode: str = Field(..., description="Electrode: 'negative' or 'positive'")
    phase: str | None = Field(default=None, description="Phase for composite electrodes")


# ---------------------------------------------------------------------------
# Electrolyte
# ---------------------------------------------------------------------------


class ConstantElectrolyte(DirectEntryFunctionSchema):
    __function_name__ = "constant_electrolyte"

    c_e: float = Field(..., description="Initial electrolyte concentration [mol.m-3]")


class NymanElectrolyte(DirectEntryFunctionSchema):
    __function_name__ = "nyman_electrolyte"

    c_e: float = Field(..., description="Initial electrolyte concentration [mol.m-3]")


class ArrheniusElectrolyteDiffusivity(DirectEntryFunctionSchema):
    __function_name__ = "arrhenius_electrolyte_diffusivity"


class ArrheniusElectrolyteConductivity(DirectEntryFunctionSchema):
    __function_name__ = "arrhenius_electrolyte_conductivity"


class LandesfeindElectrolyte(DirectEntryFunctionSchema):
    __function_name__ = "landesfeind_electrolyte"

    c_e: float = Field(..., description="Initial electrolyte concentration [mol.m-3]")
    system: str = Field(
        ...,
        description="Electrolyte system, e.g. 'EC:DMC (1:1)', 'EC:EMC (3:7)', 'EMC:FEC (19:1)'",
    )


# ---------------------------------------------------------------------------
# Thermal
# ---------------------------------------------------------------------------


class Temperatures(DirectEntryFunctionSchema):
    __function_name__ = "temperatures"

    T: float = Field(default=298.15, description="Temperature [K]")


class ZeroEntropicChange(DirectEntryFunctionSchema):
    __function_name__ = "zero_entropic_change"


class ZeroActivationEnergy(DirectEntryFunctionSchema):
    __function_name__ = "zero_activation_energy"


# ---------------------------------------------------------------------------
# Direct entry (file / defaults / geometry / etc.)
# ---------------------------------------------------------------------------


class FromJson(DirectEntryFunctionSchema):
    __function_name__ = "from_json"

    file_path: str = Field(..., description="Path to JSON file")


class StandardDefaults(DirectEntryFunctionSchema):
    __function_name__ = "standard_defaults"


class OneCm2Cell(DirectEntryFunctionSchema):
    __function_name__ = "one_cm2_cell"


class Bruggeman(DirectEntryFunctionSchema):
    __function_name__ = "bruggeman"

    electrode: float = Field(default=0, description="Bruggeman exponent for electrode")
    electrolyte: float = Field(default=1.5, description="Bruggeman exponent for electrolyte")


class SpmDefaults(DirectEntryFunctionSchema):
    __function_name__ = "spm_defaults"


class LithiumMetalAnode(DirectEntryFunctionSchema):
    __function_name__ = "lithium_metal_anode"


class SeiDefaults(DirectEntryFunctionSchema):
    __function_name__ = "sei_defaults"


class LiPlatingDefaults(DirectEntryFunctionSchema):
    __function_name__ = "li_plating_defaults"


class MechanicalDegradationDefaults(DirectEntryFunctionSchema):
    __function_name__ = "mechanical_degradation_defaults"

    electrode: str = Field(..., description="Electrode: 'negative' or 'positive'")


# ---------------------------------------------------------------------------
# Public mapping: snake_case name -> schema class (for direct_entries module)
# ---------------------------------------------------------------------------

FUNCTION_SCHEMAS = {
    "arrhenius_butler_volmer_exchange_current_density": ArrheniusButlerVolmerExchangeCurrentDensity,
    "arrhenius_electrolyte_conductivity": ArrheniusElectrolyteConductivity,
    "arrhenius_electrolyte_diffusivity": ArrheniusElectrolyteDiffusivity,
    "arrhenius_particle_diffusivity": ArrheniusParticleDiffusivity,
    "average_ocp": AverageOcp,
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
