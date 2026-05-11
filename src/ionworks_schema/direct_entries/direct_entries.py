"""Schemas for direct entries."""

from typing import Any

from pydantic import Field

from ..base import BaseSchema


class DirectEntry(BaseSchema):
    """Directly provide parameter values to the pipeline.

    Mirrors ``iwp.direct_entries.DirectEntry``. Supplies pre-defined parameter
    values to the pipeline — typically from literature, manufacturer
    specifications, or manual entry. May alternatively reference a completed
    Ionworks Studio pipeline via ``pipeline_id``, in which case the parameter
    values are fetched from that pipeline's results at run time.
    """

    parameters: dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "Mapping of pybamm parameter names to their values (e.g. "
            "``{'Electrode height [m]': 0.1}``). Values may be floats, "
            "arrays, or pybamm-serialisable symbols. Leave empty when using "
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
        parameters: dict[str, Any] | None = None,
        source: str | None = None,
        pipeline_id: str | None = None,
        **kwargs,
    ):
        super().__init__(
            parameters=parameters or {},
            source=source,
            pipeline_id=pipeline_id,
            **kwargs,
        )

    def to_config(self) -> dict:
        """Convert to parser-compatible format."""
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


class InitialStateOfCharge(BaseSchema):
    """
    Set the initial state of charge.

    Parameters
    ----------
    value : float
        Initial state of charge as a percentage (0 to 100).
    """

    value: Any = Field(
        ..., description="Initial state of charge as a percentage (0 to 100)"
    )

    def __init__(self, value):
        super().__init__(value=value)

    def to_config(self) -> dict:
        """Convert to parser-compatible format."""
        return {
            "element_type": "entry",
            "values": {"Initial SOC [%]": self.value},
        }


class InitialTemperature(BaseSchema):
    """
    Set the initial and ambient temperatures.

    Parameters
    ----------
    value : float
        Initial and ambient temperatures in Kelvin.
    """

    value: Any = Field(..., description="Initial and ambient temperatures in Kelvin")

    def __init__(self, value):
        super().__init__(value=value)

    def to_config(self) -> dict:
        """Convert to parser-compatible format."""
        return {
            "element_type": "entry",
            "values": {
                "Ambient temperature [K]": self.value,
                "Initial temperature [K]": self.value,
            },
        }


class InitialVoltage(BaseSchema):
    """
    Set the initial voltage.

    Parameters
    ----------
    value : float
        Initial voltage in volts.
    """

    value: Any = Field(..., description="Initial voltage in volts")

    def __init__(self, value):
        super().__init__(value=value)

    def to_config(self) -> dict:
        """Convert to parser-compatible format."""
        return {
            "element_type": "entry",
            "values": {"Initial voltage [V]": self.value},
        }


class PiecewiseInterpolation1D(DirectEntry):
    """Piecewise linear interpolation (1D) direct entry.

    Mirrors ``iwp.direct_entries.PiecewiseInterpolation1D``. Creates a smooth
    piecewise linear function for a parameter that varies with respect to a
    single breakpoint parameter (e.g. SOC, temperature, voltage). Smooth
    heaviside transitions keep the interpolation continuous and
    differentiable for use in pybamm models.
    """

    base_parameter_name: str = Field(
        ...,
        description=(
            "Name of the output parameter to create, including units where "
            "applicable (e.g. ``'Particle diffusion time [s]'``)."
        ),
    )
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
    formulation: str = Field(
        default="knots",
        description=(
            "Parameterisation of the interpolant. ``'knots'`` fits the "
            "parameter value at each breakpoint; ``'slopes'`` fits an "
            "initial value plus per-segment slopes."
        ),
    )
    parameters: dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "Optional overrides for named breakpoint parameters. Normally "
            "left empty — the breakpoint parameter names are generated "
            "automatically from ``base_parameter_name`` and "
            "``breakpoint_values``."
        ),
    )
    source: str | None = Field(
        default=None,
        description=(
            "Free-text description of the interpolation source (citation, "
            "dataset, manual entry). Propagated to provenance records."
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
        """Convert to parser-compatible format."""
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


class PiecewiseInterpolation2D(DirectEntry):
    """Piecewise bilinear interpolation (2D) direct entry.

    Mirrors ``iwp.direct_entries.PiecewiseInterpolation2D``. Creates a smooth
    piecewise bilinear function for a parameter that varies with respect to
    two breakpoint parameters (e.g. SOC and temperature). Smooth heaviside
    transitions keep the interpolation continuous and differentiable for use
    in pybamm models.
    """

    base_parameter_name: str = Field(
        ...,
        description=(
            "Name of the output parameter to create, including units where "
            "applicable (e.g. ``'Diffusivity [m2.s-1]'``)."
        ),
    )
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
    formulation: str = Field(
        default="knots",
        description=(
            "Parameterisation of the interpolant. ``'knots'`` fits the "
            "parameter value at each 2D grid point; ``'slopes'`` fits an "
            "initial value plus per-segment slopes along each dimension."
        ),
    )
    parameters: dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "Optional overrides for named grid-point parameters. Normally "
            "left empty — grid-point parameter names are generated "
            "automatically from ``base_parameter_name`` and the breakpoint "
            "values."
        ),
    )
    source: str | None = Field(
        default=None,
        description=(
            "Free-text description of the interpolation source (citation, "
            "dataset, manual entry). Propagated to provenance records."
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
        """Convert to parser-compatible format."""
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
