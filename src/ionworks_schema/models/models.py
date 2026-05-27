"""Schemas for models."""

from typing import Annotated, Any

from pydantic import Field

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
