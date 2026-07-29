"""Persistent simulation settings (mesh + solver) attached to a model."""

from typing import Annotated, Any

from pydantic import Field

from ..base import BaseSchema


class SimulationSettings(BaseSchema):
    """Persistent simulation settings attached to a model or parameterized model.

    A flat bag of pybamm ``Simulation`` keyword arguments that should be applied
    whenever this (parameterized) model is simulated. The fields mirror the pybamm
    kwargs exactly, so the serialized form is folded straight into
    ``simulation_kwargs`` at solve time with no reshaping.

    The required settings are parameter-dependent: a fitted solid diffusivity with
    a steep near-surface gradient needs a refined, surface-clustered particle mesh
    (and sometimes a specific solver) that the model defaults do not provide. All
    fields are optional; a higher-precedence source merges over a lower one per
    key, so a parameterized model can refine just ``r_n`` / ``r_p`` (or swap the
    solver) without restating everything.

    Parameters
    ----------
    var_pts : dict of str to int, optional
        Number of mesh points per spatial variable, e.g.
        ``{"r_n": 16, "r_p": 16}``. Stored as a plain JSON dict of ints.
    submesh_types : dict, optional
        Mapping of domain name (e.g. ``"negative particle"``) to a serialized
        submesh — a ``pybamm.MeshGenerator.to_config()`` payload
        (``{"$type": "type", "class": ..., "submesh_params": {...}}``). A live
        ``{domain: pybamm.MeshGenerator}`` mapping is accepted at construction and
        serialized to this form by :meth:`to_config`.
    spatial_methods : dict, optional
        Mapping of domain name to a serialized ``pybamm.SpatialMethod``.
    geometry : dict, optional
        Serialized geometry override. Rarely needed; when absent the geometry is
        derived from the model.
    solver : dict, optional
        Serialized solver configuration (``pybamm.BaseSolver.to_config()`` form —
        the solver class name under ``"type"`` plus its tolerances/options). A live
        ``pybamm.BaseSolver`` is accepted and serialized by :meth:`to_config`.

    Notes
    -----
    ``to_config()`` emits the flat canonical form — plain ``var_pts`` ints and
    ``submesh_types`` as a flat per-domain map — with no ``"type"`` discriminator,
    so the block is a plain nested dict ready to use as ``simulation_kwargs``.
    """

    # Persisted settings are a plain nested dict with no "type" key.
    _emit_type: bool = False

    var_pts: dict[str, int] | None = Field(default=None)
    submesh_types: dict[str, Any] | None = Field(default=None)
    spatial_methods: dict[str, Any] | None = Field(default=None)
    geometry: dict[str, Any] | None = Field(default=None)
    # ``Any`` so a live ``pybamm.BaseSolver`` (not a dict) is accepted and
    # serialized to its ``to_config()`` form by ``to_config``; a pre-serialized
    # dict is equally valid.
    solver: Any | None = Field(default=None)

    def __init__(
        self,
        var_pts=None,
        submesh_types=None,
        spatial_methods=None,
        geometry=None,
        solver=None,
        **extra: Any,
    ):
        super().__init__(
            var_pts=var_pts,
            submesh_types=submesh_types,
            spatial_methods=spatial_methods,
            geometry=geometry,
            solver=solver,
            **extra,
        )


# A ``SimulationSettings`` schema instance or its config-dict equivalent. Callers
# may pass either the typed wrapper or a pre-serialized dict; ``union_mode`` tries
# the typed class first and falls back to a raw dict.
SimulationSettingsLike = Annotated[
    SimulationSettings | dict[str, Any],
    Field(union_mode="left_to_right"),
]
