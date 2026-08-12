"""Schemas for models."""

from typing import Annotated, Any

from pydantic import Field, field_validator

from .._types import Electrode
from ..base import BaseSchema
from .simulation_settings import SimulationSettingsLike

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
        Extra options forwarded to the underlying model.
    simulation_settings : :class:`SimulationSettings` or dict, optional
        Persistent simulation settings (mesh + solver) re-applied at simulation
        time. When ``None`` the model defaults are used."""

    negative_electrode_model: _HalfCellModelLike = Field(...)
    positive_electrode_model: _HalfCellModelLike = Field(...)
    options: dict[str, Any] | None = Field(default=None)
    simulation_settings: SimulationSettingsLike | None = Field(default=None)

    def __init__(
        self,
        negative_electrode_model,
        positive_electrode_model,
        options=None,
        simulation_settings=None,
    ):
        super().__init__(
            negative_electrode_model=negative_electrode_model,
            positive_electrode_model=positive_electrode_model,
            options=options,
            simulation_settings=simulation_settings,
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
                composite with primary and secondary phases.
    simulation_settings : :class:`SimulationSettings` or dict, optional
        Persistent simulation settings (mesh + solver) re-applied at simulation
        time. When ``None`` the model defaults are used."""

    electrode: Electrode = Field(...)
    options: dict[str, Any] | None = Field(default=None)
    simulation_settings: SimulationSettingsLike | None = Field(default=None)

    def __init__(self, electrode, options=None, simulation_settings=None):
        super().__init__(
            electrode=electrode,
            options=options,
            simulation_settings=simulation_settings,
        )


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
        submodels have no effect on the physics.
    simulation_settings : :class:`SimulationSettings` or dict, optional
        Persistent simulation settings (mesh + solver) re-applied at simulation
        time. When ``None`` the model defaults are used."""

    options: dict[str, Any] | None = Field(default=None)
    simulation_settings: SimulationSettingsLike | None = Field(default=None)

    def __init__(self, options=None, simulation_settings=None):
        super().__init__(options=options, simulation_settings=simulation_settings)

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
    simulation_settings: SimulationSettingsLike | None = Field(default=None)

    def __init__(self, options=None, simulation_settings=None):
        super().__init__(options=options, simulation_settings=simulation_settings)


class LumpedSPMeR(BaseSchema):
    """A class for the Lumped Single Particle Model with electrolyte and Resistance."""

    options: dict[str, Any] | None = Field(default=None)
    simulation_settings: SimulationSettingsLike | None = Field(default=None)

    def __init__(self, options=None, simulation_settings=None):
        super().__init__(options=options, simulation_settings=simulation_settings)


class SingleElectrodeLumpedSPMR(BaseSchema):
    """A class for the single-electrode Lumped SPM with Resistance."""

    options: dict[str, Any] | None = Field(default=None)
    simulation_settings: SimulationSettingsLike | None = Field(default=None)

    def __init__(self, options=None, simulation_settings=None):
        super().__init__(options=options, simulation_settings=simulation_settings)


class ECM(BaseSchema):
    """A class for the Equivalent Circuit Model.

    Parameters
    ----------
    options : dict, optional
        Model options. Recognised keys:

        * ``"thermal"`` : ``"isothermal"`` (default), ``"lumped"`` or
          ``"two-state"``.
        * ``"rc pairs"`` : number of RC pairs as a non-negative integer string
          (e.g. ``"0"`` (default), ``"1"``, ``"2"``).
        * ``"capacity"`` : degradation model for cell capacity. Either
          ``"constant"`` (default, capacity fixed at ``"Nominal cell capacity
          [A.h]"``) or ``"function"`` (capacity is a user-supplied function of
          the degradation inputs below). When ``"function"``, supply the
          parameter ``"Capacity [A.h]"`` as such a function; pass a constant
          function such as ``lambda *args: 5.0`` for no fade.
        * ``"resistance scale"`` : degradation model for resistance growth.
          Either ``"constant"`` (default, resistances unchanged) or
          ``"function"`` (all resistances ``R0`` and ``R_rc`` are multiplied by
          a dimensionless user-supplied factor; capacitances ``C_rc`` are not
          scaled, so scaling an RC-pair resistance also lengthens its time
          constant ``R_rc * C_rc`` by the same factor). When ``"function"``,
          supply the parameter ``"Resistance scale"`` as a function of the
          degradation inputs below; pass ``lambda *args: 1.0`` for no growth.
        * ``"butler-volmer"`` : either ``"false"`` (default) or ``"true"``.
          When ``"true"``, the series overpotential gains a symmetric
          Butler-Volmer charge-transfer term
          ``eta_ct = (2*R*T/F) * asinh(I / (2*i0))``, so the terminal voltage
          becomes ``V = OCV - I*R0 - eta_ct - sum(RC pair voltages)``. Here
          ``i0`` is the ``"Exchange current [A]"`` parameter, by default a
          function of state of charge (configurable via the
          ``parameter_dependencies`` key ``"i0"``, which defaults to
          ``("soc",)`` — its current dependence is the asinh itself, so a
          current-dependent exchange current would double-count kinetics).
          Unlike the other keys, omitting ``"i0"`` from a supplied
          ``parameter_dependencies`` mapping still yields ``("soc",)`` rather
          than a constant, so a config written before this option existed
          does not silently flatten the charge-transfer overpotential; pass
          ``"i0": ()`` for a constant exchange current.
          The asinh is linear in current at low current (small-signal
          resistance ``R*T / (F*i0)``) and logarithmic (Tafel) at high
          current, so a single SOC-dependent exchange current captures the
          rate-dependent overpotential that a linear ``R0`` cannot. The term
          is exposed as the ``"Charge-transfer overpotential [V]"``
          variable. The ``"resistance scale"`` degradation factor applies
          only to ``R0`` and ``R_rc``, not to the Butler-Volmer term.

        A degradation function receives, as positional arguments in this order,
        the inputs ``"Capacity throughput [A.h]"`` (the running integral of
        absolute current ``int |I| dt`` in A.h) and ``"Time [s]"`` (elapsed
        time), and uses whatever subset it needs (throughput for cycle ageing,
        time for calendar ageing). Both are monotonic accumulators of the past
        trajectory, so a function of them is history-dependent and, for a
        monotonic function, irreversible -- the right shape for degradation.
        Oscillating states such as SOC or voltage are deliberately not exposed,
        because an algebraic function of them would swing up and down every
        cycle rather than accumulate. Appending a new input to the end of that
        list (e.g. an accumulated-stress state) is backward compatible.

        Only ``"Capacity throughput [A.h]"`` requires an extra state; when
        either ``"capacity"`` or ``"resistance scale"`` is ``"function"`` the
        model carries that state (starting at 0). With both ``"constant"`` (the
        default) the model is identical to a non-degrading ECM.
    simulation_settings : :class:`SimulationSettings` or dict, optional
        Persistent simulation settings (mesh + solver) re-applied at simulation
        time. When ``None`` the model defaults are used.
    """

    options: dict[str, Any] | None = Field(default=None)
    simulation_settings: SimulationSettingsLike | None = Field(default=None)

    def __init__(self, options=None, simulation_settings=None):
        super().__init__(options=options, simulation_settings=simulation_settings)
