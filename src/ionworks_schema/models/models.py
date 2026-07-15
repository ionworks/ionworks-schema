"""Schemas for models."""

from typing import Annotated, Any

from pydantic import Field, field_validator

from .._types import Electrode
from ..base import BaseSchema

# An ``MSMRHalfCellModel`` schema instance or its config-dict equivalent.
_HalfCellModelLike = Annotated[
    dict[str, Any] | BaseSchema,
    Field(union_mode="left_to_right"),
]


class MSMRFullCellModel(BaseSchema):
    """Full-cell MSMR model of the open-circuit potential — pairs a negative and
    positive half-cell MSMR model into one full-cell OCV.

    Use this with :class:`MSMRFullCell` to fit an MSMR description of a
    full cell from full-cell OCV data.

    Parameters
    ----------
    negative_electrode_model : :class:`MSMRHalfCellModel`
        MSMR model for the negative electrode.
    positive_electrode_model : :class:`MSMRHalfCellModel`
        MSMR model for the positive electrode.
    options : dict, optional
        Extra options forwarded to the underlying model."""

    negative_electrode_model: _HalfCellModelLike = Field(...)
    positive_electrode_model: _HalfCellModelLike = Field(...)
    options: dict[str, Any] | None = Field(default=None)

    def __init__(
        self, negative_electrode_model, positive_electrode_model, options=None
    ):
        super().__init__(
            negative_electrode_model=negative_electrode_model,
            positive_electrode_model=positive_electrode_model,
            options=options,
        )


class MSMRHalfCellModel(BaseSchema):
    """Half-cell MSMR (Multi-Species Multi-Reaction) model for one electrode's
    open-circuit potential.

    Parameters
    ----------
    electrode : str
        Electrode the model describes — ``"positive"`` or ``"negative"``.
    options : dict, optional
        Model settings:

            * ``capacity function``: capacity function used by the model.
                Default ``None``.
            * ``species format``: how each MSMR species is parameterised —
                ``"Qj"`` (capacity) or ``"Xj"`` (mole fraction). Default ``"Qj"``.
            * ``direction``: ``"delithiation"``, ``"lithiation"``, or ``None``
                (no direction assumed). Default ``None``.
            * ``particle phases``: number of phases in the electrode —
                ``"1"`` for a single-phase electrode (default) or ``"2"`` for a
                composite with primary and secondary phases."""

    electrode: Electrode = Field(...)
    options: dict[str, Any] | None = Field(default=None)

    def __init__(self, electrode, options=None):
        super().__init__(electrode=electrode, options=options)


class GITTModel(BaseSchema):
    """Diffusion-only model for fitting solid diffusivities to GITT or pulse data.

    The model solves x-averaged spherical particle diffusion in each modelled
    electrode, with the surface flux set by the applied current, and computes the
    cell voltage from the electrode open-circuit potentials evaluated at the
    particle surface stoichiometries, minus an ohmic drop through a single lumped
    ``"Ohmic resistance [Ohm]"`` parameter. There are no reaction kinetics
    (Butler-Volmer), no electrolyte dynamics, and no thermal effects; all
    parameters are constant except the open-circuit potentials.

    The ``"working electrode"`` option selects the cell configuration:

    - ``"both"`` (default): full cell. Both electrodes are modelled and the
      voltage is the difference of their open-circuit potentials minus the ohmic
      drop. A positive (discharge) current delithiates the negative electrode and
      lithiates the positive electrode.
    - ``"positive"``: half-cell against a lithium-metal counter electrode,
      following the pybamm half-cell convention. Only the working electrode is
      modelled (the counter electrode contributes no overpotential) and the
      voltage is its open-circuit potential minus the ohmic drop. A positive
      (discharge) current lithiates the working electrode. As in pybamm,
      anode-material half cells are also expressed with ``"positive"`` — rename
      the anode's parameters to the positive convention first.

    This is a fitting model intended for extracting solid-phase diffusivities
    (and the lumped ohmic resistance) from GITT or pulse-relaxation measurements
    — it is not a general-purpose simulation model. Each modelled electrode is
    parameterised with the standard full-cell parameter names (thickness, active
    material volume fraction, particle radius, diffusivity, OCP, maximum and
    initial concentrations) plus the current function, electrode cross-sectional
    area, initial temperature, and ``"Ohmic resistance [Ohm]"``.

    Parameters
    ----------
    options : dict, optional
        Model options. ``"working electrode"`` may be ``"both"`` (default) or
        ``"positive"`` and selects the cell configuration as described above.
        Any remaining options are forwarded to the underlying
        battery-model options for parameter bookkeeping; the governing equations
        of this model are fixed (diffusion-only), so options that select
        submodels have no effect on the physics."""

    options: dict[str, Any] | None = Field(default=None)

    def __init__(self, options=None):
        super().__init__(options=options)

    @field_validator("options")
    @classmethod
    def _validate_working_electrode(cls, options):
        if options is not None and "working electrode" in options:
            working_electrode = options["working electrode"]
            if working_electrode not in ("both", "positive"):
                raise ValueError(
                    "GITTModel 'working electrode' option is "
                    f"'{working_electrode}', but should be one of "
                    "['both', 'positive']"
                )
        return options


class LumpedSPMR(BaseSchema):
    """A class for the Lumped Single Particle Model with Resistance."""

    options: dict[str, Any] | None = Field(default=None)

    def __init__(self, options=None):
        super().__init__(options=options)


class LumpedSPMeR(BaseSchema):
    """A class for the Lumped Single Particle Model with electrolyte and Resistance."""

    options: dict[str, Any] | None = Field(default=None)

    def __init__(self, options=None):
        super().__init__(options=options)


class SingleElectrodeLumpedSPMR(BaseSchema):
    """A class for the single-electrode Lumped SPM with Resistance."""

    options: dict[str, Any] | None = Field(default=None)

    def __init__(self, options=None):
        super().__init__(options=options)


class ECM(BaseSchema):
    """A class for the Equivalent Circuit Model."""

    options: dict[str, Any] | None = Field(default=None)

    def __init__(self, options=None):
        super().__init__(options=options)
