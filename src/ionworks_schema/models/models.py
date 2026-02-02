"""Schemas for models."""

from typing import Any

from pydantic import Field

from ..base import BaseSchema


class MSMRFullCellModel(BaseSchema):
    """A class for the MSMR full-cell model of the open-circuit potential (OCP).

    Parameters
    ----------
    negative_electrode_model : :class:`MSMRHalfCellModel`
        The model for the negative electrode.
    positive_electrode_model : :class:`MSMRHalfCellModel`
        The model for the positive electrode."""

    negative_electrode_model: Any = Field(...)
    positive_electrode_model: Any = Field(...)
    options: Any | None = Field(default=None)

    def __init__(
        self, negative_electrode_model, positive_electrode_model, options=None
    ):
        super().__init__(
            negative_electrode_model=negative_electrode_model,
            positive_electrode_model=positive_electrode_model,
            options=options,
        )


class MSMRHalfCellModel(BaseSchema):
    """A class for the MSMR half-cell model of the open-circuit potential (OCP).

    Parameters
    ----------
    electrode : str
        The electrode to use for the model.
    options : dict, optional
        A dictionary of options to pass to the model. The options include:
            * capacity function
                The capacity function to use for the model. Default is None.
            * species format
                The species format to use for the model. Can be "Qj" for capacity or "Xj" for
                mole fraction. Default is "Qj".
            * direction
                The direction to use for the model. Can be None, "delithiation" or "lithiation".
                Default is None.
            * particle phases
                How many particle phases are present in the electrode. Can be "1" (default)
                or "2" for composite electrodes with Primary and Secondary phases."""

    electrode: Any = Field(...)
    options: Any | None = Field(default=None)

    def __init__(self, electrode, options=None):
        super().__init__(electrode=electrode, options=options)
