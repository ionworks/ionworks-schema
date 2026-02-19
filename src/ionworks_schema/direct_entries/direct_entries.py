"""Schemas for direct entries."""

from typing import Any

from pydantic import Field

from ..base import BaseSchema


class NamedDirectEntry(BaseSchema):
    """
    Schema for a direct entry that references a function in iwp.direct_entries by name.

    When serialized via to_config(), produces the format consumed by parse_entry:
    {"name": <name>, **kwargs}. Pipeline.to_config() adds element_type: "entry".
    Only names that exist in iwp.direct_entries will work at pipeline parse time.
    """

    name: str = Field(..., description="Name of function in iwp.direct_entries to call")

    def __init__(self, name: str, **kwargs: Any):
        super().__init__(name=name, **kwargs)

    def to_config(self) -> dict:
        """Convert to parser-compatible format (name + kwargs). Omits default/empty kwargs for minimal config."""
        data = self.model_dump(exclude_none=True)
        out: dict[str, Any] = {"name": data["name"]}
        for k, v in data.items():
            if k == "name" or v == "":
                continue
            out[k] = v
        return out


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
