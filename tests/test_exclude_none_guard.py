"""CI guard for issue #513: catch a NEW ``exclude_none`` silent-drop risk.

The ``from_schema`` paths build runtime kwargs with
``model_dump(exclude_none=True)``, which silently drops a field a caller set
**explicitly to None**. That only becomes a live bug for a field that is both
Optional (can hold ``None``) *and* has a non-``None`` default — otherwise
explicit-``None`` and the field's default converge and the drop is harmless.

Today every field in that combo lives in the optimizer-settings family
(``_AskTellBase`` subclasses: ``CMAES``, ``PSO``, ``DifferentialEvolution``,
``BayesianOptimization``, ``SOBER``, ``TuRBO``, ``XNES``, ``AskTellOptimizer``).
There it is benign: ``None`` means "use the pints/pybamm library default" and
the runtime optimizers forward ``**kwargs`` straight through, so dropping an
explicit ``None`` yields exactly that library default.

This guard fails if the risky combo appears on **any field other than the
known optimizer settings below**, forcing a deliberate #513 decision at
introduction — either fix that ``from_schema`` path to use ``exclude_unset``
for the field, or (if the drop is genuinely benign) add it to the allowlist
here with a rationale. The exemption is an explicit field-name set (not merely
``issubclass(_AskTellBase)``), so a *new* risky field — a new name on an
existing optimizer, a new ask/tell subclass, or a same-named field elsewhere —
still trips the guard. See #513 for the full audit.
"""

import importlib
import inspect
import pkgutil
import typing

import ionworks_schema
from ionworks_schema.base import BaseSchema
from ionworks_schema.parameter_estimators.parameter_estimators import _AskTellBase
from pydantic_core import PydanticUndefined

# The ask/tell optimizer-settings fields that carry the (benign)
# Optional-with-non-None-default pattern today. Exempt only for the
# ``_AskTellBase`` family AND only by this exact name set: ``None`` there means
# "use the pints/pybamm library default" and the runtime forwards ``**kwargs``,
# so the drop is a no-op. Adding a genuinely new optimizer knob should be a
# conscious #513 decision, so it must be added here explicitly.
_KNOWN_OPTIMIZER_SETTING_FIELDS = frozenset(
    {
        "absolute_tolerance",
        "convergence_patience",
        "log_to_screen",
        "max_evaluations",
        "min_iterations",
        "population_convergence_tol",
        "relative_tolerance",
        "surrogate_convergence_tol",
        "xtol",
    }
)


def _all_schema_classes():
    pkg = ionworks_schema
    for mod in pkgutil.walk_packages(pkg.__path__, pkg.__name__ + "."):
        module = importlib.import_module(mod.name)
        for _, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, BaseSchema) and obj.__module__ == mod.name:
                yield obj


def _is_optional(annotation) -> bool:
    return type(None) in typing.get_args(annotation)


def _has_non_none_default(field) -> bool:
    if field.default_factory is not None:
        return True
    return field.default is not PydanticUndefined and field.default is not None


def _is_vetted_optimizer_field(cls, name: str) -> bool:
    return issubclass(cls, _AskTellBase) and name in _KNOWN_OPTIMIZER_SETTING_FIELDS


def test_no_new_exclude_none_silent_drop_risk():
    unexpected = []
    vetted_seen = 0
    for cls in _all_schema_classes():
        for name, field in cls.model_fields.items():
            if _has_non_none_default(field) and _is_optional(field.annotation):
                if _is_vetted_optimizer_field(cls, name):
                    vetted_seen += 1
                else:
                    unexpected.append(f"{cls.__name__}.{name}")

    # Detection sanity: the known optimizer settings must still be found, so a
    # green result means "no NEW risk" — not "the detector silently broke".
    assert vetted_seen > 0, (
        "exclude_none risk detector matched zero known optimizer fields; the "
        "detector or the allowlist is broken."
    )
    assert not unexpected, (
        "New Optional field(s) with a non-None default, not in the vetted "
        "optimizer-settings allowlist, are exposed to the issue #513 "
        f"exclude_none silent-drop bug: {sorted(unexpected)}. Either make that "
        "from_schema path use exclude_unset for the field, or (if dropping an "
        "explicit None is benign) add it to _KNOWN_OPTIMIZER_SETTING_FIELDS / an "
        "allowlist here with a rationale."
    )
