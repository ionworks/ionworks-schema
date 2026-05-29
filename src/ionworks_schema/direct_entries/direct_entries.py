"""Schemas for direct entries."""

from collections.abc import Mapping
from typing import Any, Literal

import pybamm
from pydantic import Field

from .._types import NumberLike
from ..base import BaseSchema


class DirectEntry(BaseSchema):
    """Directly provide parameter values to the pipeline.

    Supplies pre-defined parameter
    values to the pipeline — typically from literature, manufacturer
    specifications, or manual entry. May alternatively reference a completed
    Ionworks Studio pipeline via ``pipeline_id``, in which case the parameter
    values are fetched from that pipeline's results at run time.

    Parameters
    ----------
    parameters : Mapping, optional
        Mapping of pybamm parameter names to their values (e.g.
        ``{"Electrode height [m]": 0.1}``). Values may be floats,
        arrays, or pybamm-serialisable symbols. To supply callables
        (e.g. concentration- or temperature-dependent interpolants),
        wrap them in a ``pybamm.ParameterValues`` and pass that — its
        own serialisation converts the callables to the form the
        server reconstructs. Leave empty when using ``pipeline_id``.
    source : str, optional
        Free-text reference describing where these parameters came
        from (e.g. paper citation, datasheet reference). Propagated
        through to provenance records.
    pipeline_id : str, optional
        ID of a completed pipeline on Ionworks Studio. When set, the
        parameter values are fetched from that pipeline's results
        instead of from ``parameters``. The referenced pipeline must
        be in the ``completed`` state.

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
    """

    parameters: dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "Mapping of pybamm parameter names to their values (e.g. "
            "``{'Electrode height [m]': 0.1}``). Values may be floats, "
            "arrays, or pybamm-serialisable symbols. To supply callables "
            "(e.g. concentration-dependent interpolants), wrap them in a "
            "``pybamm.ParameterValues`` and pass that. Leave empty when using "
            "``pipeline_id``."
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

    def __init__(
        self,
        parameters: Mapping[str, Any] | None = None,
        source: str | None = None,
        pipeline_id: str | None = None,
        **kwargs,
    ):
        # A pybamm.ParameterValues controls its own serialisation: calling its
        # ``to_json`` converts any callable values (e.g. concentration-dependent
        # interpolants) into the symbol-JSON the server reconstructs.
        if isinstance(parameters, pybamm.ParameterValues):
            parameters = parameters.to_json()
        super().__init__(
            parameters=dict(parameters) if parameters else {},
            source=source,
            pipeline_id=pipeline_id,
            **kwargs,
        )

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
            if self.source is not None:
                config["source"] = self.source
            return config
        config = {
            "element_type": "entry",
            "values": self.parameters,
        }
        if self.source is not None:
            config["source"] = self.source
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
