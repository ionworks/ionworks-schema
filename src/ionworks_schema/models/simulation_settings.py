"""Persistent simulation settings (mesh + solver) attached to a model."""

from typing import Annotated, Any

from pydantic import Field

from ..base import BaseSchema


class SimulationSettings(BaseSchema):
    """pybamm ``Simulation`` keyword arguments for a model, parameterized model or run.

    A finely resolved fit (e.g. a steep near-surface concentration gradient) can need
    a refined particle mesh or a specific solver that the model defaults lack. Every
    field is optional; a higher-precedence source overrides a lower one key by key.

    Parameters
    ----------
    var_pts : dict of str to int, optional
        Mesh points per spatial variable, e.g. ``{"r_n": 16, "r_p": 16}``.
    submesh_types : dict, optional
        Domain name (e.g. ``"negative particle"``) to a serialized submesh
        (``pybamm.MeshGenerator.to_config()``); a live ``MeshGenerator`` is
        serialized to it.
    spatial_methods : dict, optional
        Domain name to a serialized ``pybamm.SpatialMethod``.
    geometry : dict, optional
        Serialized geometry override; when absent it is derived from the model.
    solver : dict, optional
        Serialized solver (``pybamm.BaseSolver.to_config()``: the class name under
        ``"type"`` plus its options); a live ``BaseSolver`` is serialized to it.
    discretisation_kwargs : dict of str to bool, optional
        ``pybamm.Discretisation`` options (``check_model``,
        ``remove_independent_variables_from_rhs``, ``resolve_coupled_variables``).
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
    discretisation_kwargs: dict[str, bool] | None = Field(default=None)

    def __init__(
        self,
        var_pts=None,
        submesh_types=None,
        spatial_methods=None,
        geometry=None,
        solver=None,
        discretisation_kwargs=None,
        **extra: Any,
    ):
        super().__init__(
            var_pts=var_pts,
            submesh_types=submesh_types,
            spatial_methods=spatial_methods,
            geometry=geometry,
            solver=solver,
            discretisation_kwargs=discretisation_kwargs,
            **extra,
        )


# A ``SimulationSettings`` schema instance or its config-dict equivalent. Callers
# may pass either the typed wrapper or a pre-serialized dict; ``union_mode`` tries
# the typed class first and falls back to a raw dict.
SimulationSettingsLike = Annotated[
    SimulationSettings | dict[str, Any],
    Field(union_mode="left_to_right"),
]
