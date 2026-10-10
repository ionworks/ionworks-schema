"""Schemas for direct entries."""

from collections.abc import Mapping
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .._types import NumberLike, ParameterValuesLike
from ..base import BaseSchema


class ProvenanceRecord(BaseModel):
    """Where one parameter of a direct entry was read from."""

    model_config = ConfigDict(extra="forbid")

    #: Where the value was read, e.g. ``anode.properties.thickness``.
    path: str
    #: The value as written there, before unit conversion.
    value: float
    #: The unit it was written in, e.g. ``um``; empty when it has none.
    unit: str = ""


class DirectEntry(BaseSchema):
    """Directly provide parameter values to the pipeline.

    Supplies pre-defined parameter
    values to the pipeline — typically from literature, manufacturer
    specifications, or manual entry. May alternatively reference a completed
    Ionworks Studio pipeline via ``pipeline_id``, in which case the parameter
    values are fetched from that pipeline's results at run time, or a cell
    specification via ``cell_spec_id``, in which case they are read from its
    design values (thicknesses, porosities, ratings and so on).

    Parameters
    ----------
    parameters : Mapping, optional
        Mapping of pybamm parameter names to their values (e.g.
        ``{"Electrode height [m]": 0.1}``). Values may be floats,
        arrays, pybamm-serialisable symbols, or callables (e.g.
        concentration- or temperature-dependent functions) — each is
        converted to the wire form the server reconstructs. A
        ``pybamm.ParameterValues`` is accepted too. Leave empty when
        using ``pipeline_id``.
    source : str, optional
        Free-text reference describing where these parameters came
        from (e.g. paper citation, datasheet reference). Propagated
        through to provenance records.
    pipeline_id : str, optional
        ID of a completed pipeline on Ionworks Studio. When set, the
        parameter values are fetched from that pipeline's results
        instead of from ``parameters``. The referenced pipeline must
        be in the ``completed`` state.
    keep : list of str, optional
        With ``pipeline_id``, the only parameters to take from that pipeline's
        results, e.g. the fitted values. Without it, every parameter the pipeline
        produced is taken.
    cell_spec_id : str, optional
        ID of a cell specification on Ionworks Studio to read the parameter
        values from, using ``mapping``. They are read once, when the pipeline is
        submitted, so later edits to the specification don't change it.
    mapping : dict of str to str, optional
        With ``cell_spec_id``, the JSON path in the specification of each
        parameter's value, e.g. ``anode.properties.thickness``,
        ``anode.material.definition.particle_size_d50`` or ``ratings.capacity``:
        the header of its column in the measurements table. Path segments are
        letters, digits and underscores. Each value is converted to the unit in its
        parameter's name, so ``72.225 um`` becomes ``7.2225e-05`` for
        ``"Negative electrode thickness [m]"`` and ``40 percent`` becomes ``0.4``
        for ``"Negative electrode porosity"``. Every path must name a value the
        specification has.
    provenance : dict of str to ProvenanceRecord, optional
        Where each parameter came from, keyed by parameter name: the ``path`` it
        was read from and the ``value`` and ``unit`` written there. A cell
        specification entry records it, e.g.
        ``{"path": "anode.properties.thickness", "value": 72.225, "unit": "um"}``.

    Examples
    --------
    >>> known = iws.direct_entries.DirectEntry(
    ...     parameters={
    ...         "Ambient temperature [K]": 298.15,
    ...         "Nominal cell capacity [A.h]": 3.0,
    ...     },
    ...     source="datasheet",
    ... )
    >>> config = iws.Pipeline({"known": known}).to_config()

    Geometry read from a cell specification:

    >>> design = iws.direct_entries.DirectEntry(
    ...     cell_spec_id="<cell spec id>",
    ...     mapping={
    ...         "Negative electrode thickness [m]": "anode.properties.thickness",
    ...         "Negative electrode porosity": "anode.properties.porosity",
    ...         "Nominal cell capacity [A.h]": "ratings.capacity",
    ...     },
    ... )
    """

    parameters: ParameterValuesLike = Field(
        default_factory=dict,
        description=(
            "Mapping of pybamm parameter names to their values (e.g. "
            "``{'Electrode height [m]': 0.1}``). Values may be floats, "
            "arrays, pybamm-serialisable symbols, or callables (e.g. "
            "concentration-dependent interpolants); each is converted to the "
            "wire form. A ``pybamm.ParameterValues`` is accepted too. Leave "
            "empty when using ``pipeline_id``."
        ),
    )
    source: str | None = Field(
        default=None,
        description=(
            "Free-text reference describing where these parameters came from "
            "(e.g. paper citation, datasheet reference). Propagated through "
            "to provenance records."
        ),
    )
    pipeline_id: str | None = Field(
        default=None,
        description=(
            "ID of a completed pipeline on Ionworks Studio. When set, the "
            "parameter values are fetched from that pipeline's results "
            "instead of from ``parameters``. The referenced pipeline must be "
            "in the ``completed`` state."
        ),
    )
    keep: list[str] | None = Field(
        default=None,
        description=(
            "With ``pipeline_id``, the only parameters to take from that "
            "pipeline's results, e.g. the fitted values. Without it, every "
            "parameter the pipeline produced is taken."
        ),
    )
    cell_spec_id: str | None = Field(
        default=None,
        description=(
            "ID of a cell specification on Ionworks Studio to read the parameter "
            "values from, using ``mapping``. They are read once, when the pipeline "
            "is submitted, so later edits to the specification don't change it."
        ),
    )
    mapping: dict[str, str] | None = Field(
        default=None,
        description=(
            "With ``cell_spec_id``, the JSON path in the specification of each "
            "parameter's value, e.g. ``anode.properties.thickness``, "
            "``anode.material.definition.particle_size_d50`` or "
            "``ratings.capacity``: the header of its column in the measurements "
            "table. Path segments are letters, digits and underscores. Each value "
            "is converted to the unit in its parameter's name, so ``72.225 um`` "
            "becomes ``7.2225e-05`` for ``'Negative electrode thickness [m]'`` and "
            "``40 percent`` becomes ``0.4`` for ``'Negative electrode porosity'``. "
            "Every path must name a value the specification has."
        ),
    )
    provenance: dict[str, ProvenanceRecord] | None = Field(
        default=None,
        description=(
            "Where each parameter came from, keyed by parameter name: the "
            "``path`` it was read from and the ``value`` and ``unit`` written "
            "there. A cell specification entry records it, e.g. "
            "``{'path': 'anode.properties.thickness', 'value': 72.225, "
            "'unit': 'um'}``."
        ),
    )

    def __init__(
        self,
        parameters: Mapping[str, Any] | None = None,
        source: str | None = None,
        pipeline_id: str | None = None,
        keep: list[str] | None = None,
        cell_spec_id: str | None = None,
        mapping: Mapping[str, str] | None = None,
        **kwargs,
    ):
        super().__init__(
            parameters=parameters if parameters is not None else {},
            source=source,
            pipeline_id=pipeline_id,
            keep=keep,
            cell_spec_id=cell_spec_id,
            mapping=dict(mapping) if mapping is not None else None,
            **kwargs,
        )

    @model_validator(mode="after")
    def _one_source_of_parameters(self):
        """Parameters come from this entry, a referenced pipeline or a cell spec."""
        named = [
            k
            for k, set_ in (
                ("parameters", bool(self.parameters)),
                ("pipeline_id", self.pipeline_id is not None),
                ("cell_spec_id", self.cell_spec_id is not None),
            )
            if set_
        ]
        if len(named) > 1:
            raise ValueError(
                "A DirectEntry takes its parameters from one place, but this one "
                f"sets {' and '.join(named)}. Keep the one you meant."
            )
        if self.keep is not None and not self.keep:
            raise ValueError("keep names no parameters to take from the pipeline")
        if self.keep is not None and self.pipeline_id is None:
            raise ValueError(
                "keep picks parameters from a referenced pipeline's results, so it "
                "needs a pipeline_id"
            )
        if (self.cell_spec_id is None) != (self.mapping is None):
            raise ValueError(
                "A cell spec entry needs both cell_spec_id and mapping: the "
                "specification to read, and the parameter each of its values sets"
            )
        if self.mapping is not None and not self.mapping:
            raise ValueError("mapping names no parameters to read from the cell spec")
        return self

    def to_config(self) -> dict:
        """Build the dict you submit through ``ionworks-api``.

        Carries either the parameter values you supplied (under
        ``"values"``) or a reference to a completed Studio pipeline
        (under ``"pipeline_id"``) plus an optional provenance
        ``"source"``. Tagged as ``"element_type": "entry"`` so the API
        knows where to slot it in the pipeline.
        """
        if self.pipeline_id is not None:
            config = {
                "element_type": "entry",
                "pipeline_id": self.pipeline_id,
            }
            if self.keep is not None:
                config["keep"] = list(self.keep)
            if self.source is not None:
                config["source"] = self.source
            return config
        if self.cell_spec_id is not None:
            config = {
                "element_type": "entry",
                "cell_spec_id": self.cell_spec_id,
                "mapping": dict(self.mapping),
            }
            if self.source is not None:
                config["source"] = self.source
            return config
        # ``self.parameters`` is already wire-native (``__init__`` serialised it,
        # and the ``model_validate`` path receives an already-serialised dict), so
        # no re-serialisation is needed here.
        config = {
            "element_type": "entry",
            "values": dict(self.parameters),
        }
        if self.source is not None:
            config["source"] = self.source
        if self.provenance is not None:
            config["provenance"] = {
                k: v.model_dump() for k, v in self.provenance.items()
            }
        return config


class InitialStateOfCharge(DirectEntry):
    """
    Set the initial state of charge.

    Parameters
    ----------
    value : float
        Initial state of charge as a percentage (0 to 100).

    Examples
    --------
    >>> entry = iws.direct_entries.InitialStateOfCharge(50.0)
    >>> config = iws.Pipeline({"soc": entry}).to_config()
    """

    value: NumberLike = Field(
        ..., description="Initial state of charge as a percentage (0 to 100)"
    )

    def __init__(self, value):
        super().__init__(value=value)

    def to_config(self) -> dict:
        """Build the dict you submit through ``ionworks-api``."""
        return {
            "element_type": "entry",
            "values": {"Initial SOC [%]": self.value},
        }


class InitialTemperature(DirectEntry):
    """
    Set the initial and ambient temperatures.

    Parameters
    ----------
    value : float
        Initial and ambient temperatures in Kelvin.

    Examples
    --------
    >>> entry = iws.direct_entries.InitialTemperature(298.15)
    >>> config = iws.Pipeline({"temp": entry}).to_config()
    """

    value: NumberLike = Field(
        ..., description="Initial and ambient temperatures in Kelvin"
    )

    def __init__(self, value):
        super().__init__(value=value)

    def to_config(self) -> dict:
        """Build the dict you submit through ``ionworks-api``."""
        return {
            "element_type": "entry",
            "values": {
                "Ambient temperature [K]": self.value,
                "Initial temperature [K]": self.value,
            },
        }


class InitialVoltage(DirectEntry):
    """
    Set the initial voltage.

    Parameters
    ----------
    value : float
        Initial voltage in volts.

    Examples
    --------
    >>> entry = iws.direct_entries.InitialVoltage(3.7)
    >>> config = iws.Pipeline({"voltage": entry}).to_config()
    """

    value: NumberLike = Field(..., description="Initial voltage in volts")

    def __init__(self, value):
        super().__init__(value=value)

    def to_config(self) -> dict:
        """Build the dict you submit through ``ionworks-api``."""
        return {
            "element_type": "entry",
            "values": {"Initial voltage [V]": self.value},
        }


class BaseInterpolation(DirectEntry):
    """Base class for piecewise interpolation direct entries.

    Carries the fields shared between 1D and 2D piecewise interpolants
    (``base_parameter_name``, ``formulation``); 1D and 2D subclasses
    add their own breakpoint and smoothing fields.
    """

    base_parameter_name: str = Field(
        ...,
        description=(
            "Name of the output parameter to create, including units where "
            "applicable (e.g. ``'Particle diffusion time [s]'``)."
        ),
    )
    formulation: Literal["knots", "slopes"] = Field(
        default="knots",
        description=(
            "Parameterisation of the interpolant. ``'knots'`` fits the "
            "parameter value at each breakpoint; ``'slopes'`` fits an "
            "initial value plus per-segment slopes."
        ),
    )


class PiecewiseInterpolation1D(BaseInterpolation):
    """Piecewise linear interpolation (1D) direct entry.

    Creates a smooth
    piecewise linear function for a parameter that varies with respect to a
    single breakpoint parameter (e.g. SOC, temperature, voltage). Smooth
    heaviside transitions keep the interpolation continuous and
    differentiable for use in pybamm models.

    Examples
    --------
    >>> entry = iws.direct_entries.PiecewiseInterpolation1D(
    ...     base_parameter_name="Particle diffusion time [s]",
    ...     breakpoint_values=[0.0, 0.5, 1.0],
    ...     breakpoint_parameter_name="SOC",
    ... )
    >>> config = iws.Pipeline({"diffusion": entry}).to_config()
    """

    breakpoint_values: list[float] = Field(
        ...,
        description=(
            "Breakpoint values along the independent variable at which the "
            "parameter is defined (e.g. ``[0.0, 0.5, 1.0]`` for SOC). Must "
            "contain at least 2 unique entries."
        ),
    )
    breakpoint_parameter_name: str = Field(
        ...,
        description=(
            "Name of the breakpoint (independent) parameter (e.g. ``'SOC'``, "
            "``'Temperature [K]'``, ``'Voltage [V]'``)."
        ),
    )
    smoothing: float = Field(
        default=1e-4,
        description=(
            "Smoothing parameter for the smooth heaviside transitions "
            "between segments. Larger values give smoother transitions; must "
            "be strictly positive."
        ),
    )

    def __init__(
        self,
        base_parameter_name: str,
        breakpoint_values: list[float],
        breakpoint_parameter_name: str,
        smoothing: float = 1e-4,
        formulation: str = "knots",
        source: str | None = None,
        parameters: dict[str, Any] | None = None,
        **kwargs,
    ):
        super().__init__(
            parameters=parameters or {},
            source=source,
            base_parameter_name=base_parameter_name,
            breakpoint_values=breakpoint_values,
            breakpoint_parameter_name=breakpoint_parameter_name,
            smoothing=smoothing,
            formulation=formulation,
            **kwargs,
        )

    def to_config(self) -> dict:
        """Build the dict you submit through ``ionworks-api``."""
        config = {
            "element_type": "entry",
            "name": "PiecewiseInterpolation1D",
            "base_parameter_name": self.base_parameter_name,
            "breakpoint_values": self.breakpoint_values,
            "breakpoint_parameter_name": self.breakpoint_parameter_name,
            "smoothing": self.smoothing,
            "formulation": self.formulation,
        }
        if self.source is not None:
            config["source"] = self.source
        return config


class PiecewiseInterpolation2D(BaseInterpolation):
    """Piecewise bilinear interpolation (2D) direct entry.

    Creates a smooth
    piecewise bilinear function for a parameter that varies with respect to
    two breakpoint parameters (e.g. SOC and temperature). Smooth heaviside
    transitions keep the interpolation continuous and differentiable for use
    in pybamm models.

    Examples
    --------
    >>> entry = iws.direct_entries.PiecewiseInterpolation2D(
    ...     base_parameter_name="Diffusivity [m2.s-1]",
    ...     breakpoint1_values=[0.0, 0.5, 1.0],
    ...     breakpoint1_parameter_name="SOC",
    ...     breakpoint2_values=[273.15, 298.15, 323.15],
    ...     breakpoint2_parameter_name="Temperature [K]",
    ... )
    >>> config = iws.Pipeline({"diffusivity": entry}).to_config()
    """

    breakpoint1_values: list[float] = Field(
        ...,
        description=(
            "Breakpoint values along the first independent variable (e.g. "
            "``[0.0, 0.5, 1.0]`` for SOC). Must contain at least 2 unique "
            "entries."
        ),
    )
    breakpoint1_parameter_name: str = Field(
        ...,
        description=(
            "Name of the first breakpoint (independent) parameter (e.g. ``'SOC'``)."
        ),
    )
    breakpoint2_values: list[float] = Field(
        ...,
        description=(
            "Breakpoint values along the second independent variable (e.g. "
            "``[273.15, 298.15, 323.15]`` for temperature). Must contain at "
            "least 2 unique entries."
        ),
    )
    breakpoint2_parameter_name: str = Field(
        ...,
        description=(
            "Name of the second breakpoint (independent) parameter (e.g. "
            "``'Temperature [K]'``)."
        ),
    )
    smoothing1: float = Field(
        default=1e-4,
        description=(
            "Smoothing parameter for heaviside transitions along the first "
            "dimension. Must be strictly positive."
        ),
    )
    smoothing2: float = Field(
        default=1e-4,
        description=(
            "Smoothing parameter for heaviside transitions along the second "
            "dimension. Set larger than ``smoothing1`` when the second "
            "dimension spans a much wider range (e.g. temperature in K vs "
            "SOC)."
        ),
    )

    def __init__(
        self,
        base_parameter_name: str,
        breakpoint1_values: list[float],
        breakpoint1_parameter_name: str,
        breakpoint2_values: list[float],
        breakpoint2_parameter_name: str,
        smoothing1: float = 1e-4,
        smoothing2: float = 1e-4,
        formulation: str = "knots",
        source: str | None = None,
        parameters: dict[str, Any] | None = None,
        **kwargs,
    ):
        super().__init__(
            parameters=parameters or {},
            source=source,
            base_parameter_name=base_parameter_name,
            breakpoint1_values=breakpoint1_values,
            breakpoint1_parameter_name=breakpoint1_parameter_name,
            breakpoint2_values=breakpoint2_values,
            breakpoint2_parameter_name=breakpoint2_parameter_name,
            smoothing1=smoothing1,
            smoothing2=smoothing2,
            formulation=formulation,
            **kwargs,
        )

    def to_config(self) -> dict:
        """Build the dict you submit through ``ionworks-api``."""
        config = {
            "element_type": "entry",
            "name": "PiecewiseInterpolation2D",
            "base_parameter_name": self.base_parameter_name,
            "breakpoint1_values": self.breakpoint1_values,
            "breakpoint1_parameter_name": self.breakpoint1_parameter_name,
            "breakpoint2_values": self.breakpoint2_values,
            "breakpoint2_parameter_name": self.breakpoint2_parameter_name,
            "smoothing1": self.smoothing1,
            "smoothing2": self.smoothing2,
            "formulation": self.formulation,
        }
        if self.source is not None:
            config["source"] = self.source
        return config
