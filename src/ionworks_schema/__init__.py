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
    costs,
    data_fit,
    direct_entries,
    library,
    models,
    objective_functions,
    objectives,
    parameter,
    parameter_estimators,
    priors,
    stats,
    transforms,
    validation,
)

# Top-level (match ionworkspipeline: iwp.Pipeline, iwp.DataFit, iwp.Parameter, iwp.Library, iwp.Material, iwp.Validation)
from .base import BaseSchema, Pipeline
from .data_fit import ArrayDataFit, DataFit
from .library import Library, Material
from .parameter import Parameter
from .validation import Validation

# Alias so iws.optimizers matches iwp.optimizers (pipeline has top-level optimizers)
optimizers = parameter_estimators


# Deprecated top-level names: use the submodule path instead (e.g. iws.objectives.MSMRHalfCell).
# Map name -> (submodule, submodule_path for message)
_TOP_LEVEL_DEPRECATED = {
    "MSMRHalfCell": (objectives, "objectives"),
    "MSMRFullCell": (objectives, "objectives"),
    "DirectEntry": (direct_entries, "direct_entries"),
}


def __getattr__(name: str):
    if name in _TOP_LEVEL_DEPRECATED:
        submodule, submodule_path = _TOP_LEVEL_DEPRECATED[name]
        warnings.warn(
            f"Top-level access to {name!r} is deprecated and will be removed in a future version. "
            f"Use iws.{submodule_path}.{name} or from ionworks_schema.{submodule_path} import {name}.",
            category=DeprecationWarning,
            stacklevel=2,
        )
        return getattr(submodule, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "ArrayDataFit",
    "BaseSchema",
    "DataFit",
    "Library",
    "Material",
    "Parameter",
    "Pipeline",
    "Validation",
    "base",
    "calculations",
    "costs",
    "core",
    "data_fit",
    "direct_entries",
    "library",
    "models",
    "objective_functions",
    "objectives",
    "optimizers",
    "parameter",
    "parameter_estimators",
    "priors",
    "stats",
    "transforms",
    "validation",
]
