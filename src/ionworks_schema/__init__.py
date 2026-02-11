"""ionworks_schema - Pydantic schemas for ionworkspipeline."""

import warnings

try:
    from ionworks_schema._version import __version__
except ModuleNotFoundError:
    __version__ = "0.0.0"

from . import (
    base,
    calculations,
    core,
    data_fit,
    direct_entries,
    library,
    models,
    objective_functions,
    objectives,
    parameter,
    parameter_estimators,
    stats,
    transforms,
)

# Top-level (match ionworkspipeline: iwp.Pipeline, iwp.DataFit, iwp.Parameter, iwp.Library, iwp.Material)
from .base import BaseSchema, Pipeline
from .data_fit import ArrayDataFit, DataFit
from .library import Library, Material
from .parameter import Parameter

# Objectives are only via iws.objectives.X (like iwp.objectives.MSMRHalfCell).
# Top-level access to objective classes is deprecated and will warn.
_TOP_LEVEL_DEPRECATED_OBJECTIVES = {
    "MSMRHalfCell",
    "MSMRFullCell",
}


def __getattr__(name: str):
    if name in _TOP_LEVEL_DEPRECATED_OBJECTIVES:
        warnings.warn(
            f"Top-level access to {name!r} is deprecated and will be removed in a future version. "
            f"Use the objectives submodule instead: iws.objectives.{name} or "
            f"from ionworks_schema.objectives import {name}.",
            category=DeprecationWarning,
            stacklevel=2,
        )
        return getattr(objectives, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "BaseSchema",
    "Pipeline",
    "DataFit",
    "ArrayDataFit",
    "Parameter",
    "Library",
    "Material",
    "base",
    "calculations",
    "core",
    "data_fit",
    "direct_entries",
    "library",
    "models",
    "objective_functions",
    "objectives",
    "parameter",
    "parameter_estimators",
    "stats",
    "transforms",
]
