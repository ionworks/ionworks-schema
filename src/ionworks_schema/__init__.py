"""ionworks_schema — typed building blocks for Ionworks pipelines.

This is the package you import (as ``iws``) to describe an Ionworks
job in Python before submitting it through ``ionworks-api``. Build up
a job by constructing the schema objects you need
(``iws.Pipeline``, ``iws.DataFit``, ``iws.Parameter``,
``iws.objectives.MSMRHalfCell``, …), then call ``.to_config()`` on the
top-level object to get the dict you submit through the API.

The schemas validate as you build them: bad field types or missing
required fields raise immediately, so you find mistakes locally
before they reach the server.
"""

import warnings

try:
    from importlib.metadata import version

    __version__ = version("ionworks-schema")
except Exception:
    __version__ = "0.0.0"

from . import (
    base,
    calculations,
    core,
    costs,
    data_fit,
    direct_entries,
    distribution_samplers,
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
    "distribution_samplers",
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
