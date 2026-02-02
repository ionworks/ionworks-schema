"""Schemas for objectives."""

from typing import Any

from pydantic import Field

from ..base import BaseSchema


class BaseObjective(BaseSchema):
    """Schema for BaseObjective."""

    options: Any | None = Field(default=None)
    callbacks: Any | None = Field(default=None)
    custom_parameters: Any | None = Field(default=None)
    cost: Any | None = Field(default=None)
    constraints: Any | None = Field(default=None)
    penalties: Any | None = Field(default=None)

    def __init__(
        self,
        options=None,
        callbacks=None,
        custom_parameters=None,
        cost=None,
        constraints=None,
        penalties=None,
    ):
        super().__init__(
            options=options,
            callbacks=callbacks,
            custom_parameters=custom_parameters,
            cost=cost,
            constraints=constraints,
            penalties=penalties,
        )


class CalendarAgeing(BaseSchema):
    """Schema for CalendarAgeing."""

    data_input: Any = Field(...)
    options: Any | None = Field(default=None)
    callbacks: Any | None = Field(default=None)
    custom_parameters: Any | None = Field(default=None)
    constraints: Any | None = Field(default=None)
    penalties: Any | None = Field(default=None)

    def __init__(
        self,
        data_input,
        options=None,
        callbacks=None,
        custom_parameters=None,
        constraints=None,
        penalties=None,
    ):
        super().__init__(
            data_input=data_input,
            options=options,
            callbacks=callbacks,
            custom_parameters=custom_parameters,
            constraints=constraints,
            penalties=penalties,
        )


class CurrentDriven(BaseSchema):
    """Schema for CurrentDriven."""

    data_input: Any = Field(...)
    options: Any | None = Field(default=None)
    callbacks: Any | None = Field(default=None)
    custom_parameters: Any | None = Field(default=None)
    constraints: Any | None = Field(default=None)
    penalties: Any | None = Field(default=None)

    def __init__(
        self,
        data_input,
        options=None,
        callbacks=None,
        custom_parameters=None,
        constraints=None,
        penalties=None,
    ):
        super().__init__(
            data_input=data_input,
            options=options,
            callbacks=callbacks,
            custom_parameters=custom_parameters,
            constraints=constraints,
            penalties=penalties,
        )


class CycleAgeing(BaseSchema):
    """Schema for CycleAgeing."""

    data_input: Any = Field(...)
    options: Any | None = Field(default=None)
    callbacks: Any | None = Field(default=None)
    custom_parameters: Any | None = Field(default=None)
    constraints: Any | None = Field(default=None)
    penalties: Any | None = Field(default=None)

    def __init__(
        self,
        data_input,
        options=None,
        callbacks=None,
        custom_parameters=None,
        constraints=None,
        penalties=None,
    ):
        super().__init__(
            data_input=data_input,
            options=options,
            callbacks=callbacks,
            custom_parameters=custom_parameters,
            constraints=constraints,
            penalties=penalties,
        )


class DesignObjective(BaseSchema):
    """Schema for DesignObjective."""

    actions: Any = Field(...)
    constraints: Any | None = Field(default=None)
    options: Any | None = Field(default=None)
    callbacks: Any | None = Field(default=None)
    custom_parameters: Any | None = Field(default=None)
    cost: Any | None = Field(default=None)
    validate_against_experiment_steps: Any = Field(default=True)
    output_variables_full: Any | None = Field(default=None)
    save_at_cycles: Any | None = Field(default=None)
    penalties: Any | None = Field(default=None)

    def __init__(
        self,
        actions,
        constraints=None,
        options=None,
        callbacks=None,
        custom_parameters=None,
        cost=None,
        validate_against_experiment_steps=True,
        output_variables_full=None,
        save_at_cycles=None,
        penalties=None,
    ):
        super().__init__(
            actions=actions,
            constraints=constraints,
            options=options,
            callbacks=callbacks,
            custom_parameters=custom_parameters,
            cost=cost,
            validate_against_experiment_steps=validate_against_experiment_steps,
            output_variables_full=output_variables_full,
            save_at_cycles=save_at_cycles,
            penalties=penalties,
        )


class EIS(BaseSchema):
    """Schema for EIS."""

    data_input: Any = Field(...)
    options: Any | None = Field(default=None)
    callbacks: Any | None = Field(default=None)
    custom_parameters: Any | None = Field(default=None)
    constraints: Any | None = Field(default=None)
    penalties: Any | None = Field(default=None)

    def __init__(
        self,
        data_input,
        options=None,
        callbacks=None,
        custom_parameters=None,
        constraints=None,
        penalties=None,
    ):
        super().__init__(
            data_input=data_input,
            options=options,
            callbacks=callbacks,
            custom_parameters=custom_parameters,
            constraints=constraints,
            penalties=penalties,
        )


class ElectrodeBalancing(BaseSchema):
    """Schema for ElectrodeBalancing."""

    data_input: Any = Field(...)
    options: Any | None = Field(default=None)
    callbacks: Any | None = Field(default=None)
    custom_parameters: Any | None = Field(default=None)
    constraints: Any | None = Field(default=None)
    penalties: Any | None = Field(default=None)

    def __init__(
        self,
        data_input,
        options=None,
        callbacks=None,
        custom_parameters=None,
        constraints=None,
        penalties=None,
    ):
        super().__init__(
            data_input=data_input,
            options=options,
            callbacks=callbacks,
            custom_parameters=custom_parameters,
            constraints=constraints,
            penalties=penalties,
        )


class ElectrodeBalancingHalfCell(BaseSchema):
    """Schema for ElectrodeBalancingHalfCell."""

    electrode: Any = Field(...)
    data_input: Any = Field(...)
    options: Any | None = Field(default=None)
    callbacks: Any | None = Field(default=None)
    custom_parameters: Any | None = Field(default=None)
    constraints: Any | None = Field(default=None)
    penalties: Any | None = Field(default=None)

    def __init__(
        self,
        electrode,
        data_input,
        options=None,
        callbacks=None,
        custom_parameters=None,
        constraints=None,
        penalties=None,
    ):
        super().__init__(
            electrode=electrode,
            data_input=data_input,
            options=options,
            callbacks=callbacks,
            custom_parameters=custom_parameters,
            constraints=constraints,
            penalties=penalties,
        )


class FittingObjective(BaseSchema):
    """Schema for FittingObjective."""

    data_input: Any = Field(...)
    options: Any | None = Field(default=None)
    callbacks: Any | None = Field(default=None)
    custom_parameters: Any | None = Field(default=None)
    cost: Any | None = Field(default=None)
    constraints: Any | None = Field(default=None)
    penalties: Any | None = Field(default=None)

    def __init__(
        self,
        data_input,
        options=None,
        callbacks=None,
        custom_parameters=None,
        cost=None,
        constraints=None,
        penalties=None,
    ):
        super().__init__(
            data_input=data_input,
            options=options,
            callbacks=callbacks,
            custom_parameters=custom_parameters,
            cost=cost,
            constraints=constraints,
            penalties=penalties,
        )


class MSMRFullCell(BaseSchema):
    """Schema for MSMRFullCell."""

    data_input: Any = Field(...)
    options: Any | None = Field(default=None)
    callbacks: Any | None = Field(default=None)
    custom_parameters: Any | None = Field(default=None)
    constraints: Any | None = Field(default=None)
    penalties: Any | None = Field(default=None)

    def __init__(
        self,
        data_input,
        options=None,
        callbacks=None,
        custom_parameters=None,
        constraints=None,
        penalties=None,
    ):
        super().__init__(
            data_input=data_input,
            options=options,
            callbacks=callbacks,
            custom_parameters=custom_parameters,
            constraints=constraints,
            penalties=penalties,
        )


class MSMRHalfCell(BaseSchema):
    """Schema for MSMRHalfCell."""

    data_input: Any = Field(...)
    options: Any | None = Field(default=None)
    callbacks: Any | None = Field(default=None)
    custom_parameters: Any | None = Field(default=None)
    constraints: Any | None = Field(default=None)
    penalties: Any | None = Field(default=None)

    def __init__(
        self,
        data_input,
        options=None,
        callbacks=None,
        custom_parameters=None,
        constraints=None,
        penalties=None,
    ):
        super().__init__(
            data_input=data_input,
            options=options,
            callbacks=callbacks,
            custom_parameters=custom_parameters,
            constraints=constraints,
            penalties=penalties,
        )


class OCPHalfCell(BaseSchema):
    """Schema for OCPHalfCell."""

    electrode: Any = Field(...)
    data_input: Any = Field(...)
    options: Any | None = Field(default=None)
    callbacks: Any | None = Field(default=None)
    custom_parameters: Any | None = Field(default=None)
    constraints: Any | None = Field(default=None)
    penalties: Any | None = Field(default=None)

    def __init__(
        self,
        electrode,
        data_input,
        options=None,
        callbacks=None,
        custom_parameters=None,
        constraints=None,
        penalties=None,
    ):
        super().__init__(
            electrode=electrode,
            data_input=data_input,
            options=options,
            callbacks=callbacks,
            custom_parameters=custom_parameters,
            constraints=constraints,
            penalties=penalties,
        )


class Objective(BaseSchema):
    """Schema for Objective."""

    pass


class Pulse(BaseSchema):
    """Schema for Pulse."""

    data_input: Any = Field(...)
    options: Any | None = Field(default=None)
    callbacks: Any | None = Field(default=None)
    custom_parameters: Any | None = Field(default=None)
    constraints: Any | None = Field(default=None)
    penalties: Any | None = Field(default=None)

    def __init__(
        self,
        data_input,
        options=None,
        callbacks=None,
        custom_parameters=None,
        constraints=None,
        penalties=None,
    ):
        super().__init__(
            data_input=data_input,
            options=options,
            callbacks=callbacks,
            custom_parameters=custom_parameters,
            constraints=constraints,
            penalties=penalties,
        )


class Resistance(BaseSchema):
    """Schema for Resistance."""

    data_input: Any = Field(...)
    options: Any | None = Field(default=None)
    callbacks: Any | None = Field(default=None)
    custom_parameters: Any | None = Field(default=None)
    constraints: Any | None = Field(default=None)
    penalties: Any | None = Field(default=None)

    def __init__(
        self,
        data_input,
        options=None,
        callbacks=None,
        custom_parameters=None,
        constraints=None,
        penalties=None,
    ):
        super().__init__(
            data_input=data_input,
            options=options,
            callbacks=callbacks,
            custom_parameters=custom_parameters,
            constraints=constraints,
            penalties=penalties,
        )


class SimulationObjective(BaseSchema):
    """Schema for SimulationObjective."""

    data_input: Any = Field(...)
    options: Any | None = Field(default=None)
    callbacks: Any | None = Field(default=None)
    custom_parameters: Any | None = Field(default=None)
    cost: Any | None = Field(default=None)
    constraints: Any | None = Field(default=None)
    penalties: Any | None = Field(default=None)

    def __init__(
        self,
        data_input,
        options=None,
        callbacks=None,
        custom_parameters=None,
        cost=None,
        constraints=None,
        penalties=None,
    ):
        super().__init__(
            data_input=data_input,
            options=options,
            callbacks=callbacks,
            custom_parameters=custom_parameters,
            cost=cost,
            constraints=constraints,
            penalties=penalties,
        )
