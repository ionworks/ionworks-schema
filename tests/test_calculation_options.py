"""Typed ``options`` bags for the calculation schemas (issue #1423).

Each calculation's ``options`` field was ``dict[str, Any]`` and silently ignored
a misspelt key. Each now carries a typed ``*Options`` schema that rejects unknown
keys at construction. Keys do not accumulate across calculations, so each class
declares only its own. ``CellMass.model_options`` stays an open pybamm passthrough.
"""

import ionworks_schema as iws
from pydantic import ValidationError
import pytest


class TestElectrodeSOHOptions:
    def test_rejects_unknown_option_key(self):
        with pytest.raises(ValidationError):
            iws.calculations.ElectrodeSOH(options={"known val": "cell capacity"})

    def test_rejects_invalid_enum(self):
        with pytest.raises(ValidationError):
            iws.calculations.ElectrodeSOH(options={"known value": "guess"})

    def test_round_trip_spaced_key(self):
        cfg = iws.calculations.ElectrodeSOH(
            options={"known value": "cell capacity"}
        ).to_config()
        assert cfg["options"] == {"known value": "cell capacity"}


class TestCyclableLithiumOptions:
    def test_particle_phases_round_trip(self):
        cfg = iws.calculations.CyclableLithium(
            options={"particle phases": ("2", "1")}
        ).to_config()
        assert cfg["options"] == {"particle phases": ["2", "1"]}

    def test_rejects_invalid_particle_phase(self):
        with pytest.raises(ValidationError):
            iws.calculations.CyclableLithium(options={"particle phases": ("3", "1")})


class TestStoichiometryLimitsFromCapacityOptions:
    def test_direction_charge_discharge(self):
        cfg = iws.calculations.StoichiometryLimitsFromCapacity(
            options={"direction": "discharge"}
        ).to_config()
        assert cfg["options"] == {"direction": "discharge"}

    def test_rejects_lithiation_direction(self):
        # This calc uses charge/discharge, not lithiation/delithiation.
        with pytest.raises(ValidationError):
            iws.calculations.StoichiometryLimitsFromCapacity(
                options={"direction": "lithiation"}
            )

    def test_requires_usable_capacity_when_composite(self):
        with pytest.raises(ValidationError, match="usable capacity"):
            iws.calculations.StoichiometryLimitsFromCapacity(
                options={"particle phases": ("2", "1")}
            )

    def test_composite_with_usable_capacity_ok(self):
        iws.calculations.StoichiometryLimitsFromCapacity(
            options={"particle phases": ("2", "1"), "usable capacity": 5.0}
        )

    def test_single_phase_without_usable_capacity_ok(self):
        iws.calculations.StoichiometryLimitsFromCapacity(
            options={"particle phases": ("1", "1")}
        )


class TestInitialSOCfromMaximumStoichiometryOptions:
    def test_include_concentration_round_trip(self):
        # 'include concentration' was undocumented in the old schema; now typed.
        cfg = iws.calculations.InitialSOCfromMaximumStoichiometry(
            options={"include concentration": "false"}
        ).to_config()
        assert cfg["options"] == {"include concentration": "false"}

    def test_rejects_unknown_key(self):
        with pytest.raises(ValidationError):
            iws.calculations.InitialSOCfromMaximumStoichiometry(options={"nope": 1})


class TestMSMRDiffusivityOptions:
    def test_round_trip_spaced_keys(self):
        cfg = iws.calculations.DiffusivityFromMSMRData(
            electrode="positive",
            data="file:x.csv",
            options={"x tolerance": 1e-5, "minimum dUdx": 1e-4},
        ).to_config()
        assert cfg["options"] == {"x tolerance": 1e-5, "minimum dUdx": 1e-4}

    def test_rejects_invalid_interpolator(self):
        with pytest.raises(ValidationError):
            iws.calculations.DiffusivityFromMSMRData(
                electrode="positive",
                data="file:x.csv",
                options={"interpolator": "quadratic"},
            )

    def test_shared_class_rejects_unknown_key(self):
        # ArrheniusDiffusivityFromMSMRData shares MSMRDiffusivityOptions.
        with pytest.raises(ValidationError):
            iws.calculations.ArrheniusDiffusivityFromMSMRData(
                electrode="positive", data="file:x.csv", options={"nope": 1}
            )


class TestOCPDataInterpolantOptions:
    def test_direction_lithiation_round_trip(self):
        cfg = iws.calculations.OCPDataInterpolant(
            electrode="positive",
            data="file:x.csv",
            options={"direction": "lithiation", "interpolator": "cubic"},
        ).to_config()
        assert cfg["options"] == {"direction": "lithiation", "interpolator": "cubic"}


class TestDiffusivityFromPulseOptions:
    def test_dt_ir_alias_round_trip(self):
        cfg = iws.calculations.DiffusivityFromPulse(
            electrode="positive",
            data="file:x.csv",
            options={"dt_IR": 0.5, "step number": 3},
        ).to_config()
        assert cfg["options"] == {"dt_IR": 0.5, "step number": 3}


class TestCellMassModelOptionsStaysOpen:
    def test_model_options_is_open_passthrough(self):
        # model_options is a genuine pybamm BatteryModelOptions passthrough — it
        # is deliberately left untyped, so arbitrary keys are accepted.
        cfg = iws.calculations.CellMass(
            model_options={"any pybamm key": "value"}
        ).to_config()
        assert cfg["model_options"] == {"any pybamm key": "value"}
