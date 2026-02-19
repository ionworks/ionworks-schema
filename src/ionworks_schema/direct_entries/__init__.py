"""Schemas for direct entries."""

from .direct_entries import (
    DirectEntry,
    NamedDirectEntry,
    PiecewiseInterpolation1D,
    PiecewiseInterpolation2D,
)
from .registry import FUNCTION_ENTRY_NAMES


def __getattr__(name: str):
    """Return a wrapper that builds NamedDirectEntry(name, **kwargs) for registered function names."""
    if name in FUNCTION_ENTRY_NAMES:

        def _wrapper(**kwargs):
            return NamedDirectEntry(name=name, **kwargs)

        return _wrapper
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "DirectEntry",
    "FUNCTION_ENTRY_NAMES",
    "NamedDirectEntry",
    "PiecewiseInterpolation1D",
    "PiecewiseInterpolation2D",
]
