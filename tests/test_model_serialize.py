"""Round-trip regression test for custom pybamm subclass serialisation."""

import json
from pathlib import Path
import tempfile

from ionworks_schema.base import _serialize_pybamm_model
import pybamm
from pybamm.expression_tree.operations.serialise import Serialise
from pybamm.models.full_battery_models.lithium_ion.base_lithium_ion_model import (
    BaseModel as LiIonBaseModel,
)


def _make_minimal_liion_subclass():
    """Return a lithium-ion BaseModel subclass that cannot be re-imported.

    The class is defined inside this function so that, even though its
    ``__module__`` resolves to the test module, ``getattr(module, name)``
    fails — forcing ``Serialise.load_custom_model`` to fall back to the
    recorded MRO when resolving ``base_class``.
    """

    class _MyLiIon(LiIonBaseModel):
        def __init__(self, name="MyLiIon"):
            super().__init__(name=name)
            v = pybamm.Variable("x", domain="positive particle")
            self.rhs = {v: -v}
            self.initial_conditions = {v: 1.0}
            self.variables = {"x": v}

    return _MyLiIon


def _matches_reference(loaded_val, reference_val) -> bool:
    """Compare two ``default_*`` values structurally, tolerant of pybamm types.

    Equality on pybamm objects (``Geometry``, ``ParameterValues``, solvers,
    spatial-method instances) is not reliable, so fall back to a triage that's
    strong enough for this regression: same concrete type, and for collection-
    valued defaults, the same set of keys / same length. Class-instance values
    are taken as a match once the type lines up.
    """
    if type(loaded_val) is not type(reference_val):
        return False
    if isinstance(reference_val, dict):
        return set(loaded_val) == set(reference_val)
    if isinstance(reference_val, list):
        return len(loaded_val) == len(reference_val)
    return True


def test_user_liion_subclass_round_trip_keeps_lithium_ion_defaults():
    """Regression for the discretisation bug fixed by pybamm PR #5485.

    Without that fix (pybamm <26.4.2), serialising a user subclass of
    ``LiIonBaseModel`` and loading it on a system without the subclass
    package silently dropped to bare ``pybamm.BaseModel``. The visible
    failure was a confusing "Spatial method has not been given for variable
    X-averaged positive particle concentration" during discretisation, but
    every Li-ion-specific class default regressed at the same time. Cover
    them all algorithmically so a future serializer change that breaks
    one of them surfaces here too.
    """
    cls = _make_minimal_liion_subclass()
    model = cls()
    cfg = _serialize_pybamm_model(model)

    assert cfg["type"] == "custom"

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "model.json"
        path.write_text(json.dumps(cfg["model"], default=str))
        loaded = Serialise.load_custom_model(str(path))

    # Primary invariant: MRO fallback recovered LiIonBaseModel identity.
    assert isinstance(loaded, LiIonBaseModel)

    # Defensive sweep: every ``default_*`` attribute that differs between
    # bare BaseModel and LiIonBaseModel must match the LiIon reference, not
    # silently fall back to the BaseModel default.
    li_ref = LiIonBaseModel()
    bare_ref = pybamm.BaseModel()
    checked: list[str] = []
    for attr in sorted(a for a in dir(li_ref) if a.startswith("default_")):
        bare_val = getattr(bare_ref, attr, None)
        li_val = getattr(li_ref, attr, None)
        if _matches_reference(bare_val, li_val):
            continue
        loaded_val = getattr(loaded, attr)
        assert _matches_reference(loaded_val, li_val), (
            f"loaded.{attr} regressed: got {type(loaded_val).__name__}, "
            f"expected {type(li_val).__name__}"
        )
        checked.append(attr)
    assert "default_spatial_methods" in checked, (
        "the LiIon-vs-BaseModel diff lost default_spatial_methods — the loop "
        "is no longer covering the original regression"
    )

    # Model-instance state must round-trip too: a subclass that loaded as the
    # right type but came back with empty rhs/ICs/variables would still break.
    assert set(loaded.variables) == set(model.variables)
    assert len(loaded.rhs) == len(model.rhs)
    assert len(loaded.initial_conditions) == len(model.initial_conditions)
