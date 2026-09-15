"""CI guard: no stray extra='allow' on a BaseSchema subclass.

Only walks BaseSchema subclasses, so BaseModel-based models (e.g.
``library.Material``) are out of scope — those are covered by their own
negative tests.
"""

import importlib
import inspect
import pkgutil

import ionworks_schema
from ionworks_schema.base import BaseSchema

# Named passthrough leaves allowed to keep extra='allow'. The guard reads the
# *resolved* config, so the Scipy base AND each Scipy leaf both report "allow".
# ``CMAESOptions`` is a genuine pycma passthrough (``cma.CMAOptions`` is the
# source of truth for its large option surface), so it stays open like the
# Scipy leaves rather than enumerating dozens of pycma keys.
PASSTHROUGH_ALLOWLIST = {
    "_PassthroughOptimizer",
    "ScipyDifferentialEvolution",
    "ScipyMinimize",
    "ScipyLeastSquares",
    "ScipyLsqLinear",
    "ScipyBasinhopping",
    "ScipyDualAnnealing",
    "ScipyShgo",
    "CMAESOptions",
    # GITTModel types "working electrode" but forwards every other key to
    # pybamm's BatteryModelOptions, so it is a genuine hybrid passthrough.
    "GITTModelOptions",
}


def _all_schema_classes():
    pkg = ionworks_schema
    for mod in pkgutil.walk_packages(pkg.__path__, pkg.__name__ + "."):
        module = importlib.import_module(mod.name)
        for _, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, BaseSchema) and obj.__module__ == mod.name:
                yield obj


def test_no_extra_allow_outside_allowlist():
    offenders = [
        cls.__name__
        for cls in _all_schema_classes()
        if cls.model_config.get("extra") == "allow"
        and cls.__name__ not in PASSTHROUGH_ALLOWLIST
    ]
    assert offenders == [], f"extra='allow' not allowed on: {offenders}"
