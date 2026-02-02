"""Schemas for data_fit."""

from typing import Any

from pydantic import Field, model_validator

from ..base import BaseSchema


class ArrayDataFit(BaseSchema):
    """Schema for ArrayDataFit."""

    objectives: Any = Field(...)

    def __init__(self, objectives):
        super().__init__(objectives=objectives)


class DataFit(BaseSchema):
    """Schema for DataFit."""

    objectives: Any = Field(...)
    source: Any = Field(default="")
    parameters: Any | None = Field(default=None)
    cost: Any | None = Field(default=None)
    initial_guesses: Any | None = Field(default=None)
    optimizer: Any | None = Field(default=None)
    cost_logger: Any | None = Field(default=None)
    multistarts: Any | None = Field(default=None)
    num_workers: Any | None = Field(default=None)
    parallel: Any | None = Field(default=None)
    max_batch_size: Any | None = Field(default=None)
    initial_guess_sampler: Any | None = Field(default=None)
    priors: Any | None = Field(default=None)
    options: Any | None = Field(default=None)

    def __init__(
        self,
        objectives,
        source="",
        parameters=None,
        cost=None,
        initial_guesses=None,
        optimizer=None,
        cost_logger=None,
        multistarts=None,
        num_workers=None,
        parallel=None,
        max_batch_size=None,
        initial_guess_sampler=None,
        priors=None,
        options=None,
    ):
        super().__init__(
            objectives=objectives,
            source=source,
            parameters=parameters,
            cost=cost,
            initial_guesses=initial_guesses,
            optimizer=optimizer,
            cost_logger=cost_logger,
            multistarts=multistarts,
            num_workers=num_workers,
            parallel=parallel,
            max_batch_size=max_batch_size,
            initial_guess_sampler=initial_guess_sampler,
            priors=priors,
            options=options,
        )

    @model_validator(mode="after")
    def validate_parameters_or_priors(self):
        """Validate that either parameters or priors is specified."""
        parameters = self.parameters
        priors = self.priors
        if not parameters and not priors:
            raise ValueError("Either 'parameters' or 'priors' must be specified")
        if parameters and priors:
            raise ValueError("Only one of 'parameters' or 'priors' can be specified")
        return self
