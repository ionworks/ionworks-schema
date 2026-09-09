"""Typed ``options`` bags for the objective schemas (issue #1423).

Each objective's ``options`` field was ``dict[str, Any]`` and silently ignored a
misspelt key. Each objective now carries a typed ``*Options`` schema that rejects
unknown keys at construction time. Option keys do not accumulate across the
objective inheritance tree, so each class declares only its own keys.
"""

import ionworks_schema as iws
from pydantic import ValidationError
import pytest


class TestResistanceOptions:
    def test_rejects_unknown_option_key(self):
        with pytest.raises(ValidationError):
            iws.objectives.Resistance(data_input="file:x.csv", options={"modle": {}})

    def test_round_trip_emits_only_set_keys(self):
        cfg = iws.objectives.Resistance(
            data_input="file:x.csv", options={"model": {"type": "SPM"}}
        ).to_config()
        assert cfg["options"] == {"model": {"type": "SPM"}}


class TestEISOptions:
    def test_rejects_unknown_option_key(self):
        with pytest.raises(ValidationError):
            iws.objectives.EIS(data_input="file:x.csv", options={"sim_kwargs": {}})

    def test_round_trip_emits_only_set_keys(self):
        cfg = iws.objectives.EIS(
            data_input="file:x.csv",
            options={"model": {"type": "SPM"}, "simulation_kwargs": {"var_pts": {}}},
        ).to_config()
        assert cfg["options"] == {
            "model": {"type": "SPM"},
            "simulation_kwargs": {"var_pts": {}},
        }


class TestCalendarAgeingOptions:
    def test_rejects_unknown_option_key(self):
        with pytest.raises(ValidationError):
            iws.objectives.CalendarAgeing(
                data_input="file:x.csv", options={"mode": ["LLI [%]"]}
            )

    def test_rejects_invalid_mode_value(self):
        with pytest.raises(ValidationError):
            iws.objectives.CalendarAgeing(
                data_input="file:x.csv", options={"modes": ["not a mode"]}
            )

    def test_round_trip_emits_only_set_keys(self):
        cfg = iws.objectives.CalendarAgeing(
            data_input="file:x.csv",
            options={"model": {"type": "SPM"}, "modes": ["LLI [%]", "LAM_pe [%]"]},
        ).to_config()
        assert cfg["options"] == {
            "model": {"type": "SPM"},
            "modes": ["LLI [%]", "LAM_pe [%]"],
        }


class TestCurrentDrivenOptions:
    def test_rejects_unknown_option_key(self):
        with pytest.raises(ValidationError):
            iws.objectives.CurrentDriven(data_input="file:x.csv", options={"nope": 1})

    def test_rejects_invalid_independent_variable(self):
        with pytest.raises(ValidationError):
            iws.objectives.CurrentDriven(
                data_input="file:x.csv", options={"independent variable": "current"}
            )

    def test_round_trip_spaced_keys(self):
        cfg = iws.objectives.CurrentDriven(
            data_input="file:x.csv",
            options={
                "model": "SPM",
                "independent variable": "voltage",
                "objective variables": ["I"],
            },
        ).to_config()
        assert cfg["options"] == {
            "model": "SPM",
            "independent variable": "voltage",
            "objective variables": ["I"],
        }


class TestPulseOptions:
    def test_rejects_unknown_option_key(self):
        with pytest.raises(ValidationError):
            iws.objectives.Pulse(data_input="file:x.csv", options={"nope": 1})

    def test_callable_objective_variables_excluded_from_config(self):
        cfg = iws.objectives.Pulse(
            data_input="file:x.csv",
            options={
                "model": "SPM",
                "objective variables": lambda m: [],
                "interpolant_lossless": True,
            },
        ).to_config()
        assert "objective variables" not in cfg.get("options", {})
        assert cfg["options"] == {"model": "SPM", "interpolant_lossless": True}


class TestOCPHalfCellOptions:
    def test_rejects_unknown_option_key(self):
        # OCPHalfCell has no ``model`` option — a stray key is now rejected.
        with pytest.raises(ValidationError):
            iws.objectives.OCPHalfCell(
                electrode="positive", data_input="file:x.csv", options={"model": {}}
            )

    def test_rejects_wrong_direction_enum(self):
        # OCP half-cell uses lithiation/delithiation, not charge/discharge.
        with pytest.raises(ValidationError):
            iws.objectives.OCPHalfCell(
                electrode="positive",
                data_input="file:x.csv",
                options={"direction": "charge"},
            )

    def test_round_trip_spaced_keys(self):
        cfg = iws.objectives.OCPHalfCell(
            electrode="positive",
            data_input="file:x.csv",
            options={"dUdQ cutoff": 0.5, "stoichiometry limits": (0.1, 0.9)},
        ).to_config()
        assert cfg["options"] == {
            "dUdQ cutoff": 0.5,
            "stoichiometry limits": [0.1, 0.9],
        }


class TestElectrodeBalancingOptions:
    def test_rejects_unknown_option_key(self):
        with pytest.raises(ValidationError):
            iws.objectives.ElectrodeBalancing(data_input="file:x.csv", options={"x": 1})

    def test_rejects_wrong_direction_enum(self):
        # Full-cell electrode balancing uses charge/discharge, not lithiation.
        with pytest.raises(ValidationError):
            iws.objectives.ElectrodeBalancing(
                data_input="file:x.csv", options={"direction": "lithiation"}
            )

    def test_round_trip_spaced_keys(self):
        cfg = iws.objectives.ElectrodeBalancing(
            data_input="file:x.csv",
            options={"GITT": True, "dQdU model axis": True},
        ).to_config()
        assert cfg["options"] == {"GITT": True, "dQdU model axis": True}


class TestElectrodeBalancingHalfCellOptions:
    def test_rejects_unknown_option_key(self):
        with pytest.raises(ValidationError):
            iws.objectives.ElectrodeBalancingHalfCell(
                electrode="positive", data_input="file:x.csv", options={"x": 1}
            )

    def test_round_trip_spaced_keys(self):
        cfg = iws.objectives.ElectrodeBalancingHalfCell(
            electrode="positive",
            data_input="file:x.csv",
            options={"direction": "lithiation", "GITT": True},
        ).to_config()
        assert cfg["options"] == {"direction": "lithiation", "GITT": True}


class TestMSMRHalfCellOptions:
    def test_rejects_unknown_option_key(self):
        with pytest.raises(ValidationError):
            iws.objectives.MSMRHalfCell(data_input="file:x.csv", options={"x": 1})

    def test_rejects_invalid_constrain_xj_method(self):
        with pytest.raises(ValidationError):
            iws.objectives.MSMRHalfCell(
                data_input="file:x.csv", options={"constrain Xj method": "guess"}
            )

    def test_cutoff_accepts_none_string_and_float(self):
        cfg = iws.objectives.MSMRHalfCell(
            data_input="file:x.csv",
            options={"dUdQ cutoff": "none", "dQdU cutoff": 0.2},
        ).to_config()
        assert cfg["options"] == {"dUdQ cutoff": "none", "dQdU cutoff": 0.2}


class TestMSMRFullCellOptions:
    def test_rejects_unknown_option_key(self):
        with pytest.raises(ValidationError):
            iws.objectives.MSMRFullCell(data_input="file:x.csv", options={"x": 1})

    def test_round_trip_spaced_keys(self):
        cfg = iws.objectives.MSMRFullCell(
            data_input="file:x.csv",
            options={"negative voltage limits": (0.0, 1.5)},
        ).to_config()
        assert cfg["options"] == {"negative voltage limits": [0.0, 1.5]}


class TestCycleAgeingOptions:
    def test_rejects_unknown_option_key(self):
        with pytest.raises(ValidationError):
            iws.objectives.CycleAgeing(data_input="file:x.csv", options={"nope": 1})

    def test_round_trip_spaced_keys(self):
        cfg = iws.objectives.CycleAgeing(
            data_input="file:x.csv",
            options={"model": "SPM", "objective variables": ["LLI [%]"]},
        ).to_config()
        assert cfg["options"] == {"model": "SPM", "objective variables": ["LLI [%]"]}
