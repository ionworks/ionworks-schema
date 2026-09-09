"""CI guard: ``__all__`` must be honest in both directions.

A name in ``__all__`` that is not a module attribute breaks
``from ... import *`` — and ``ruff`` does not flag it, so nothing else does.
A public schema class defined in a submodule but never re-exported by its
package is invisible to the same readers, which is how every ``*Options``
companion went unexported.

Export is checked by identity, not name: ``direct_entries`` publishes its
function schemas under snake_case aliases, so a class's own name is
legitimately absent from ``__all__``.
"""

import importlib
import pkgutil

import ionworks_schema
from pydantic import BaseModel
import pytest


def _modules_with_all() -> list[str]:
    names = []
    for info in pkgutil.walk_packages(
        ionworks_schema.__path__, prefix="ionworks_schema."
    ):
        if hasattr(importlib.import_module(info.name), "__all__"):
            names.append(info.name)
    return sorted(names)


def _packages_with_all() -> list[str]:
    return sorted(
        name
        for name in _modules_with_all()
        if hasattr(importlib.import_module(name), "__path__")
    )


@pytest.mark.parametrize("module_name", _modules_with_all())
def test_every_all_entry_resolves(module_name):
    """No ``__all__`` entry may be a name the module does not have."""
    module = importlib.import_module(module_name)
    missing = [name for name in module.__all__ if not hasattr(module, name)]
    assert not missing, (
        f"{module_name}.__all__ lists names that are not attributes: {missing}. "
        "A splat such as `*FUNCTION_SCHEMAS.keys()` must not be quoted."
    )


@pytest.mark.parametrize("package_name", _packages_with_all())
def test_every_public_schema_class_is_exported(package_name):
    """Every schema class a subpackage defines must be reachable from it."""
    package = importlib.import_module(package_name)
    exported = {
        id(getattr(package, name)) for name in package.__all__ if hasattr(package, name)
    }

    unexported = set()
    for info in pkgutil.iter_modules(package.__path__, prefix=f"{package_name}."):
        module = importlib.import_module(info.name)
        for name in dir(module):
            if name.startswith("_"):
                continue
            obj = getattr(module, name)
            if (
                isinstance(obj, type)
                and issubclass(obj, BaseModel)
                and getattr(obj, "__module__", "") == module.__name__
                and id(obj) not in exported
            ):
                unexported.add(name)

    assert not unexported, (
        f"{package_name} defines public schema classes that it does not export: "
        f"{sorted(unexported)}. Add each to both the import list and __all__ — "
        "attribute access goes through the import, not __all__."
    )
