"""Schemas for calculations."""

from typing import Any

from pydantic import Field

from ..base import BaseSchema


class AreaToSquareWidthHeight(BaseSchema):
    """Schema for AreaToSquareWidthHeight."""

    pass


class ArrheniusDiffusivityFromMSMRData(BaseSchema):
    """Schema for ArrheniusDiffusivityFromMSMRData."""

    electrode: Any = Field(...)
    data: Any = Field(...)
    direction: Any = Field(default="")
    phase: Any = Field(default="")
    options: Any | None = Field(default=None)

    def __init__(self, electrode, data, direction="", phase="", options=None):
        super().__init__(
            electrode=electrode,
            data=data,
            direction=direction,
            phase=phase,
            options=options,
        )


class ArrheniusDiffusivityFromMSMRFunction(BaseSchema):
    """Schema for ArrheniusDiffusivityFromMSMRFunction."""

    electrode: Any = Field(...)
    voltage_limits: Any = Field(...)
    direction: Any = Field(default="")
    phase: Any = Field(default="")
    options: Any | None = Field(default=None)

    def __init__(self, electrode, voltage_limits, direction="", phase="", options=None):
        super().__init__(
            electrode=electrode,
            voltage_limits=voltage_limits,
            direction=direction,
            phase=phase,
            options=options,
        )


class ArrheniusLogLinear(BaseSchema):
    """Schema for ArrheniusLogLinear."""

    data: Any = Field(...)
    reference_temperature: Any | None = Field(default=None)
    include_func: Any = Field(default=False)

    def __init__(self, data, reference_temperature=None, include_func=False):
        super().__init__(
            data=data,
            reference_temperature=reference_temperature,
            include_func=include_func,
        )


class AverageMSMRParameters(BaseSchema):
    """Schema for AverageMSMRParameters."""

    electrode: Any = Field(...)
    options: Any | None = Field(default=None)

    def __init__(self, electrode, options=None):
        super().__init__(electrode=electrode, options=options)


class Calculation(BaseSchema):
    """Schema for Calculation."""

    source: Any = Field(...)

    def __init__(self, source):
        super().__init__(source=source)


class CellMass(BaseSchema):
    """Schema for CellMass."""

    model_options: Any | None = Field(default=None)

    def __init__(self, model_options=None):
        super().__init__(model_options=model_options)


class CyclableLithium(BaseSchema):
    """Schema for CyclableLithium."""

    method: Any = Field(default="electrode capacities")
    options: Any | None = Field(default=None)

    def __init__(self, method="electrode capacities", options=None):
        super().__init__(method=method, options=options)


class DensityFromVolumeAndMass(BaseSchema):
    """Schema for DensityFromVolumeAndMass."""

    pass


class DiameterToSquareWidthHeight(BaseSchema):
    """Schema for DiameterToSquareWidthHeight."""

    pass


class DiffusivityDataInterpolant(BaseSchema):
    """Schema for DiffusivityDataInterpolant."""

    electrode: Any = Field(...)
    data: Any = Field(...)
    direction: Any = Field(default="")
    phase: Any = Field(default="")
    options: Any | None = Field(default=None)

    def __init__(self, electrode, data, direction="", phase="", options=None):
        super().__init__(
            electrode=electrode,
            data=data,
            direction=direction,
            phase=phase,
            options=options,
        )


class DiffusivityFromMSMRData(BaseSchema):
    """Schema for DiffusivityFromMSMRData."""

    electrode: Any = Field(...)
    data: Any = Field(...)
    direction: Any = Field(default="")
    phase: Any = Field(default="")
    options: Any | None = Field(default=None)

    def __init__(self, electrode, data, direction="", phase="", options=None):
        super().__init__(
            electrode=electrode,
            data=data,
            direction=direction,
            phase=phase,
            options=options,
        )


class DiffusivityFromMSMRFunction(BaseSchema):
    """Schema for DiffusivityFromMSMRFunction."""

    electrode: Any = Field(...)
    voltage_limits: Any = Field(...)
    direction: Any = Field(default="")
    phase: Any = Field(default="")
    options: Any | None = Field(default=None)

    def __init__(self, electrode, voltage_limits, direction="", phase="", options=None):
        super().__init__(
            electrode=electrode,
            voltage_limits=voltage_limits,
            direction=direction,
            phase=phase,
            options=options,
        )


class DiffusivityFromPulse(BaseSchema):
    """Schema for DiffusivityFromPulse."""

    electrode: Any = Field(...)
    data: Any = Field(...)
    direction: Any = Field(default="")
    phase: Any = Field(default="")
    options: Any | None = Field(default=None)

    def __init__(self, electrode, data, direction="", phase="", options=None):
        super().__init__(
            electrode=electrode,
            data=data,
            direction=direction,
            phase=phase,
            options=options,
        )


class ElectrodeCapacity(BaseSchema):
    """Schema for ElectrodeCapacity."""

    electrode: Any = Field(...)
    use_stoich_window: Any = Field(default=False)
    method: Any = Field(default="auto")
    phase: Any | None = Field(default=None)

    def __init__(self, electrode, use_stoich_window=False, method="auto", phase=None):
        super().__init__(
            electrode=electrode,
            use_stoich_window=use_stoich_window,
            method=method,
            phase=phase,
        )


class ElectrodeSOH(BaseSchema):
    """Schema for ElectrodeSOH."""

    options: Any | None = Field(default=None)

    def __init__(self, options=None):
        super().__init__(options=options)


class ElectrodeSOHHalfCell(BaseSchema):
    """Schema for ElectrodeSOHHalfCell."""

    electrode: Any = Field(...)
    options: Any | None = Field(default=None)

    def __init__(self, electrode, options=None):
        super().__init__(electrode=electrode, options=options)


class ElectrodeVolumeFractionFromLoading(BaseSchema):
    """Schema for ElectrodeVolumeFractionFromLoading."""

    electrode: Any = Field(...)
    method: Any = Field(...)

    def __init__(self, electrode, method):
        super().__init__(electrode=electrode, method=method)


class ElectrodeVolumeFractionFromPorosity(BaseSchema):
    """Schema for ElectrodeVolumeFractionFromPorosity."""

    electrode: Any = Field(...)

    def __init__(self, electrode):
        super().__init__(electrode=electrode)


class EntropicChangeDataInterpolant(BaseSchema):
    """Schema for EntropicChangeDataInterpolant."""

    electrode: Any = Field(...)
    data: Any = Field(...)
    options: Any | None = Field(default=None)

    def __init__(self, electrode, data, options=None):
        super().__init__(electrode=electrode, data=data, options=options)


class EntropicChangeFromMSMRFunction(BaseSchema):
    """Schema for EntropicChangeFromMSMRFunction."""

    electrode: Any = Field(...)
    voltage_limits: Any = Field(...)
    options: Any | None = Field(default=None)

    def __init__(self, electrode, voltage_limits, options=None):
        super().__init__(
            electrode=electrode, voltage_limits=voltage_limits, options=options
        )


class HalfCellNominalCapacity(BaseSchema):
    """Schema for HalfCellNominalCapacity."""

    electrode: Any = Field(...)

    def __init__(self, electrode):
        super().__init__(electrode=electrode)


class InitialConcentrationFromInitialStoichiometryHalfCell(BaseSchema):
    """Schema for InitialConcentrationFromInitialStoichiometryHalfCell."""

    electrode: Any = Field(...)
    options: Any | None = Field(default=None)

    def __init__(self, electrode, options=None):
        super().__init__(electrode=electrode, options=options)


class InitialSOC(BaseSchema):
    """Schema for InitialSOC."""

    soc: Any = Field(...)

    def __init__(self, soc):
        super().__init__(soc=soc)


class InitialSOCHalfCell(BaseSchema):
    """Schema for InitialSOCHalfCell."""

    electrode: Any = Field(...)
    soc: Any = Field(...)
    options: Any | None = Field(default=None)

    def __init__(self, electrode, soc, options=None):
        super().__init__(electrode=electrode, soc=soc, options=options)


class InitialSOCfromMaximumStoichiometry(BaseSchema):
    """Schema for InitialSOCfromMaximumStoichiometry."""

    options: Any | None = Field(default=None)

    def __init__(self, options=None):
        super().__init__(options=options)


class InitialStoichiometryFromVoltageHalfCell(BaseSchema):
    """Schema for InitialStoichiometryFromVoltageHalfCell."""

    electrode: Any = Field(...)
    options: Any | None = Field(default=None)

    def __init__(self, electrode, options=None):
        super().__init__(electrode=electrode, options=options)


class InitialStoichiometryFromVoltageMSMRHalfCell(BaseSchema):
    """Schema for InitialStoichiometryFromVoltageMSMRHalfCell."""

    electrode: Any = Field(...)

    def __init__(self, electrode):
        super().__init__(electrode=electrode)


class InitialVoltageFromConcentration(BaseSchema):
    """Schema for InitialVoltageFromConcentration."""

    electrode: Any = Field(...)

    def __init__(self, electrode):
        super().__init__(electrode=electrode)


class JellyRollThermalDimensions(BaseSchema):
    """Schema for JellyRollThermalDimensions."""

    pass


class LumpedHeatCapacityAndDensity(BaseSchema):
    """Schema for LumpedHeatCapacityAndDensity."""

    pass


class MSMRElectrodeSOHHalfCell(BaseSchema):
    """Schema for MSMRElectrodeSOHHalfCell."""

    electrode: Any = Field(...)

    def __init__(self, electrode):
        super().__init__(electrode=electrode)


class MSMRFullCellCapacities(BaseSchema):
    """Schema for MSMRFullCellCapacities."""

    data: Any = Field(...)
    method: Any = Field(default="total capacity")

    def __init__(self, data, method="total capacity"):
        super().__init__(data=data, method=method)


class MSMRFunction(BaseSchema):
    """Schema for MSMRFunction."""

    electrode: Any = Field(...)
    direction: Any | None = Field(default=None)
    phase: Any | None = Field(default=None)

    def __init__(self, electrode, direction=None, phase=None):
        super().__init__(electrode=electrode, direction=direction, phase=phase)


class OCPDataInterpolant(BaseSchema):
    """Schema for OCPDataInterpolant."""

    electrode: Any = Field(...)
    data: Any = Field(...)
    options: Any | None = Field(default=None)

    def __init__(self, electrode, data, options=None):
        super().__init__(electrode=electrode, data=data, options=options)


class OCPDataInterpolantMSMRExtrapolation(BaseSchema):
    """Schema for OCPDataInterpolantMSMRExtrapolation."""

    electrode: Any = Field(...)
    data: Any = Field(...)
    voltage_limits: Any = Field(...)
    options: Any | None = Field(default=None)

    def __init__(self, electrode, data, voltage_limits, options=None):
        super().__init__(
            electrode=electrode,
            data=data,
            voltage_limits=voltage_limits,
            options=options,
        )


class OCPMSMRInterpolant(BaseSchema):
    """Schema for OCPMSMRInterpolant."""

    electrode: Any = Field(...)
    voltage_limits: Any = Field(...)
    options: Any | None = Field(default=None)

    def __init__(self, electrode, voltage_limits, options=None):
        super().__init__(
            electrode=electrode, voltage_limits=voltage_limits, options=options
        )


class OpenCircuitLimits(BaseSchema):
    """Schema for OpenCircuitLimits."""

    pass


class PorosityFromElectrodeVolumeFraction(BaseSchema):
    """Schema for PorosityFromElectrodeVolumeFraction."""

    electrode: Any = Field(...)

    def __init__(self, electrode):
        super().__init__(electrode=electrode)


class PouchCellThermalDimensions(BaseSchema):
    """Schema for PouchCellThermalDimensions."""

    pass


class SlopesToKnots(BaseSchema):
    """Schema for SlopesToKnots."""

    base_parameter_name: Any = Field(...)
    breakpoint_values: Any = Field(...)
    breakpoint_parameter_name: Any = Field(...)

    def __init__(
        self, base_parameter_name, breakpoint_values, breakpoint_parameter_name
    ):
        super().__init__(
            base_parameter_name=base_parameter_name,
            breakpoint_values=breakpoint_values,
            breakpoint_parameter_name=breakpoint_parameter_name,
        )


class SlopesToKnots2D(BaseSchema):
    """Schema for SlopesToKnots2D."""

    base_parameter_name: Any = Field(...)
    breakpoint1_values: Any = Field(...)
    breakpoint1_parameter_name: Any = Field(...)
    breakpoint2_values: Any = Field(...)
    breakpoint2_parameter_name: Any = Field(...)

    def __init__(
        self,
        base_parameter_name,
        breakpoint1_values,
        breakpoint1_parameter_name,
        breakpoint2_values,
        breakpoint2_parameter_name,
    ):
        super().__init__(
            base_parameter_name=base_parameter_name,
            breakpoint1_values=breakpoint1_values,
            breakpoint1_parameter_name=breakpoint1_parameter_name,
            breakpoint2_values=breakpoint2_values,
            breakpoint2_parameter_name=breakpoint2_parameter_name,
        )


class SpecificHeatCapacity(BaseSchema):
    """Schema for SpecificHeatCapacity."""

    pass


class StoichiometryAtMinimumSOC(BaseSchema):
    """Schema for StoichiometryAtMinimumSOC."""

    electrode: Any = Field(...)

    def __init__(self, electrode):
        super().__init__(electrode=electrode)


class StoichiometryLimitsFromCapacity(BaseSchema):
    """Schema for StoichiometryLimitsFromCapacity."""

    options: Any | None = Field(default=None)

    def __init__(self, options=None):
        super().__init__(options=options)


class SurfaceAreaToVolumeRatio(BaseSchema):
    """Schema for SurfaceAreaToVolumeRatio."""

    electrode: Any = Field(...)

    def __init__(self, electrode):
        super().__init__(electrode=electrode)
