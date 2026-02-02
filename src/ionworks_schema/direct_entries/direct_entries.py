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

    def __init__(self, parameters: dict[str, Any], source: str | None = None):
        super().__init__(parameters=parameters, source=source)

    def to_config(self) -> dict:
        """Convert to parser-compatible format."""
        return {
            "element_type": "entry",
            "values": self.parameters,
        }
