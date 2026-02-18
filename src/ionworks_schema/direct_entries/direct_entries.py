"""Schemas for direct entries."""

from typing import Any

from pydantic import Field

from ..base import BaseSchema


class DirectEntry(BaseSchema):
    """
    Schema for DirectEntry - directly provide parameters without calculation or fitting.

    DirectEntry elements supply pre-defined parameter values to the pipeline,
    typically from literature, manufacturer specifications, or manual entry.

    Parameters
    ----------
    parameters : dict
        Dictionary of parameter names and values to provide.
    source : str, optional
        Reference or description of where these parameters came from.
    """

    parameters: dict[str, Any] = Field(
        ..., description="Dictionary of parameter names and values to provide"
    )
    source: str | None = Field(
        default=None,
        description="Reference or description of where these parameters came from",
    )

    def __init__(
        self,
        parameters: dict[str, Any],
        source: str | None = None,
        **kwargs,
    ):
        super().__init__(parameters=parameters, source=source, **kwargs)

    def to_config(self) -> dict:
        """Convert to parser-compatible format."""
        return {
            "element_type": "entry",
            "values": self.parameters,
        }


class InitialStateOfCharge(BaseSchema):
    """
    Set the initial state of charge.

    Parameters
    ----------
    value : float
        Initial state of charge as a percentage (0 to 100).
    """

    value: Any = Field(..., description="Initial state of charge as a percentage (0 to 100)")

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
    """
    Schema for piecewise linear interpolation (1D) direct entry.

    Creates a piecewise linear interpolation function for a parameter that varies
    with respect to a breakpoint parameter (e.g., SOC, temperature, voltage).

    Parameters
    ----------
    base_parameter_name : str
        The name of the parameter to create (e.g., "Particle diffusion time [s]").
    breakpoint_values : list[float]
        List of breakpoint values at which the parameter is defined.
    breakpoint_parameter_name : str
        Name of the breakpoint parameter (e.g., "SOC", "Temperature [K]").
    smoothing : float, optional
        Smoothing parameter for heaviside transitions (default: 1e-4).
    formulation : str, optional
        "knots" (fit values at each breakpoint) or "slopes" (fit initial value and slopes).
    source : str, optional
        Description of the interpolation source.
    """

    base_parameter_name: str = Field(..., description="Name of the parameter to create")
    breakpoint_values: list[float] = Field(..., description="Breakpoint values")
    breakpoint_parameter_name: str = Field(
        ..., description="Name of the breakpoint parameter"
    )
    smoothing: float = Field(
        default=1e-4, description="Smoothing for heaviside transitions"
    )
    formulation: str = Field(default="knots", description="'knots' or 'slopes'")
    parameters: dict[str, Any] = Field(default_factory=dict)
    source: str | None = Field(default=None)

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


class PiecewiseInterpolation2D(DirectEntry):
    """
    Schema for 2D piecewise bilinear interpolation direct entry.

    Creates a parameter that varies with respect to two breakpoint parameters
    (e.g., SOC and temperature).

    Parameters
    ----------
    base_parameter_name : str
        The name of the parameter to create.
    breakpoint1_values : list[float]
        List of first breakpoint values.
    breakpoint1_parameter_name : str
        Name of the first breakpoint parameter.
    breakpoint2_values : list[float]
        List of second breakpoint values.
    breakpoint2_parameter_name : str
        Name of the second breakpoint parameter.
    smoothing1 : float, optional
        Smoothing for first dimension (default: 1e-4).
    smoothing2 : float, optional
        Smoothing for second dimension (default: 1e-4).
    formulation : str, optional
        "knots" or "slopes".
    source : str, optional
        Description of the interpolation source.
    """

    base_parameter_name: str = Field(..., description="Name of the parameter to create")
    breakpoint1_values: list[float] = Field(
        ..., description="First dimension breakpoint values"
    )
    breakpoint1_parameter_name: str = Field(
        ..., description="First breakpoint parameter name"
    )
    breakpoint2_values: list[float] = Field(
        ..., description="Second dimension breakpoint values"
    )
    breakpoint2_parameter_name: str = Field(
        ..., description="Second breakpoint parameter name"
    )
    smoothing1: float = Field(default=1e-4, description="Smoothing for first dimension")
    smoothing2: float = Field(
        default=1e-4, description="Smoothing for second dimension"
    )
    formulation: str = Field(default="knots", description="'knots' or 'slopes'")
    parameters: dict[str, Any] = Field(default_factory=dict)
    source: str | None = Field(default=None)

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
