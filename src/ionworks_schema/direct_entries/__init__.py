"""Schemas for direct entries."""

from .direct_entries import (
    DirectEntry,
    InitialStateOfCharge,
    InitialTemperature,
    InitialVoltage,
    PiecewiseInterpolation1D,
    PiecewiseInterpolation2D,
)
from .function_schemas import (
    FUNCTION_SCHEMAS,
    DirectEntryFunctionSchema,
)

# Expose each function schema under its snake_case name (e.g. landesfeind_electrolyte)
globals().update(FUNCTION_SCHEMAS)

__all__ = [
    "DirectEntry",
    "DirectEntryFunctionSchema",
    "InitialStateOfCharge",
    "InitialTemperature",
    "InitialVoltage",
    "PiecewiseInterpolation1D",
    "PiecewiseInterpolation2D",
    *FUNCTION_SCHEMAS.keys(),
]
