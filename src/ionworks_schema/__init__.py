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
    plots,
    priors,
    results,
    stats,
    transforms,
    validation,
)

# Element-resolution registry — the stable, engine-facing surface for resolving
# a pipeline element config to its schema class (the engine parsers reuse these).
from ._element_registry import (
    LEGACY_ELEMENT_TYPE_ALIASES,
    canonicalize_element_type,
    entry_schema_for_name,
    schema_class_for,
    validate_element,
)

# Top-level schema entry points.
from .analysis import LinearConfidenceInterval, SobolSensitivity
from .base import BaseSchema, Pipeline, SimplePipeline
from .data_fit import ArrayDataFit, DataFit, DataFitOptions
from .data_loader import (
    DataLoaderOptions,
    DataLoaderTransforms,
    DataPayloadSpec,
    MetadataSpec,
    TimeSeriesSpec,
)
from .library import Library, Material
from .parameter import Parameter
from .results import (
    BaseResults,
    ConfidenceIntervalResult,
    EnsembleResult,
    OptimizationResult,
    ParameterEstimatorResult,
    PassthroughResult,
    PosteriorResult,
    RegressionResult,
    SensitivityResult,
    ValidationResult,
    from_config,
)
from .validation import Validation

# Alias so ``iws.optimizers`` is available as a top-level accessor.
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
    "BaseResults",
    "BaseSchema",
    "ConfidenceIntervalResult",
    "DataFit",
    "DataFitOptions",
    "DataLoaderOptions",
    "DataLoaderTransforms",
    "DataPayloadSpec",
    "EnsembleResult",
    "LEGACY_ELEMENT_TYPE_ALIASES",
    "Library",
    "LinearConfidenceInterval",
    "Material",
    "MetadataSpec",
    "OptimizationResult",
    "Parameter",
    "ParameterEstimatorResult",
    "PassthroughResult",
    "Pipeline",
    "PosteriorResult",
    "RegressionResult",
    "SensitivityResult",
    "SimplePipeline",
    "SobolSensitivity",
    "TimeSeriesSpec",
    "Validation",
    "ValidationResult",
    "base",
    "calculations",
    "canonicalize_element_type",
    "costs",
    "core",
    "data_fit",
    "direct_entries",
    "distribution_samplers",
    "entry_schema_for_name",
    "from_config",
    "library",
    "models",
    "objective_functions",
    "objectives",
    "optimizers",
    "parameter",
    "parameter_estimators",
    "plots",
    "priors",
    "results",
    "schema_class_for",
    "stats",
    "transforms",
    "validate_element",
    "validation",
]
