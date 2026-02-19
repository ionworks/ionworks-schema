"""Registry of direct-entry function names for function-style schema API.

These names correspond to callables in iwp.direct_entries that can be invoked
by the pipeline parser via config {"name": <name>, **kwargs}. Only names listed
here are exposed as iws.direct_entries.<name>(**kwargs). At parse time, the
pipeline requires the same name to exist in iwp.direct_entries.
"""

# Function names in iwp.direct_entries that return a DirectEntry (or similar).
# Excludes classes: DirectEntry, PiecewiseInterpolation1D, PiecewiseInterpolation2D, etc.
FUNCTION_ENTRY_NAMES = [
    "arrhenius_butler_volmer_exchange_current_density",
    "arrhenius_electrolyte_conductivity",
    "arrhenius_electrolyte_diffusivity",
    "arrhenius_particle_diffusivity",
    "average_ocp",
    "bruggeman",
    "constant_electrolyte",
    "from_json",
    "landesfeind_electrolyte",
    "li_plating_defaults",
    "lithium_metal_anode",
    "mechanical_degradation_defaults",
    "nyman_electrolyte",
    "one_cm2_cell",
    "sei_defaults",
    "spm_defaults",
    "standard_defaults",
    "temperatures",
    "zero_activation_energy",
    "zero_entropic_change",
]
