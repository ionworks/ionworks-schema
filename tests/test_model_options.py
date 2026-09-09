"""Typed ``options`` bags for the model schemas (issue #1423).

The model ``options`` fields were ``dict[str, Any]`` and silently ignored a
misspelt key. Each closed model now carries a typed ``*Options`` schema that
rejects unknown keys at construction time; ``GITTModel`` is a hybrid that keeps
a typed ``working electrode`` key while passing the rest through to pybamm.
"""

import ionworks_schema as iws
from pydantic import ValidationError
import pytest


class TestECMOptions:
    def test_rejects_unknown_option_key(self):
        with pytest.raises(ValidationError):
            iws.models.ECM(options={"thermnal": "lumped"})  # misspelt "thermal"

    def test_round_trip_emits_only_set_spaced_keys(self):
        cfg = iws.models.ECM(options={"thermal": "lumped", "rc pairs": "2"}).to_config()
        # only the two keys the caller set, under their spaced wire names, no type
        assert cfg["options"] == {"thermal": "lumped", "rc pairs": "2"}

    def test_rejects_invalid_enum_value(self):
        with pytest.raises(ValidationError):
            iws.models.ECM(options={"thermal": "boiling"})

    def test_rejects_non_integer_rc_pairs(self):
        with pytest.raises(ValidationError):
            iws.models.ECM(options={"rc pairs": "two"})

    def test_accepts_parameter_dependencies(self):
        cfg = iws.models.ECM(
            options={"butler-volmer": "true", "parameter_dependencies": {"i0": ["soc"]}}
        ).to_config()
        assert cfg["options"]["parameter_dependencies"] == {"i0": ["soc"]}
        assert cfg["options"]["butler-volmer"] == "true"


class TestLumpedSPMROptions:
    def test_rejects_unknown_option_key(self):
        with pytest.raises(ValidationError):
            iws.models.LumpedSPMR(options={"thermla": "lumped"})

    def test_round_trip_emits_only_set_spaced_keys(self):
        cfg = iws.models.LumpedSPMR(
            options={"thermal": "lumped", "surface temperature": "lumped"}
        ).to_config()
        assert cfg["options"] == {"thermal": "lumped", "surface temperature": "lumped"}

    def test_working_electrode_restricted_to_both(self):
        with pytest.raises(ValidationError):
            iws.models.LumpedSPMR(options={"working electrode": "positive"})


class TestLumpedSPMeROptions:
    def test_rejects_unknown_option_key(self):
        with pytest.raises(ValidationError):
            iws.models.LumpedSPMeR(options={"nope": 1})

    def test_round_trip_emits_only_set_spaced_keys(self):
        cfg = iws.models.LumpedSPMeR(
            options={"surface temperature": "lumped"}
        ).to_config()
        assert cfg["options"] == {"surface temperature": "lumped"}


class TestSingleElectrodeLumpedSPMROptions:
    def test_rejects_unknown_option_key(self):
        with pytest.raises(ValidationError):
            iws.models.SingleElectrodeLumpedSPMR(options={"working electrode": "both"})

    def test_round_trip_emits_only_set_spaced_keys(self):
        cfg = iws.models.SingleElectrodeLumpedSPMR(
            options={"thermal": "lumped", "rc pairs": "1"}
        ).to_config()
        assert cfg["options"] == {"thermal": "lumped", "rc pairs": "1"}

    def test_rejects_non_integer_rc_pairs(self):
        with pytest.raises(ValidationError):
            iws.models.SingleElectrodeLumpedSPMR(options={"rc pairs": "-1"})


class TestMSMRHalfCellModelOptions:
    def test_rejects_unknown_option_key(self):
        with pytest.raises(ValidationError):
            iws.models.MSMRHalfCellModel(
                electrode="positive", options={"partical phases": "2"}
            )

    def test_round_trip_emits_only_set_spaced_keys(self):
        cfg = iws.models.MSMRHalfCellModel(
            electrode="positive",
            options={"species format": "Xj", "particle phases": "2"},
        ).to_config()
        assert cfg["options"] == {"species format": "Xj", "particle phases": "2"}

    def test_rejects_invalid_enum_value(self):
        with pytest.raises(ValidationError):
            iws.models.MSMRHalfCellModel(
                electrode="positive", options={"species format": "Zk"}
            )

    def test_callable_option_accepted_but_excluded_from_config(self):
        m = iws.models.MSMRHalfCellModel(
            electrode="positive",
            options={"capacity function": lambda *a: 1.0, "species format": "Xj"},
        )
        cfg = m.to_config()
        # callables can't cross the wire — omitted, matching the runtime to_config
        assert "capacity function" not in cfg.get("options", {})
        assert cfg["options"] == {"species format": "Xj"}


class TestGITTModelOptions:
    def test_rejects_invalid_working_electrode(self):
        with pytest.raises(ValidationError):
            iws.models.GITTModel(options={"working electrode": "negative"})

    def test_passes_through_unknown_pybamm_key(self):
        # GITT forwards any non-"working electrode" key to pybamm's
        # BatteryModelOptions, so a closed schema would be wrong: extras pass.
        cfg = iws.models.GITTModel(
            options={"working electrode": "positive", "surface form": "differential"}
        ).to_config()
        assert cfg["options"]["working electrode"] == "positive"
        assert cfg["options"]["surface form"] == "differential"

    def test_round_trip_only_set(self):
        cfg = iws.models.GITTModel(
            options={"working electrode": "positive"}
        ).to_config()
        assert cfg["options"] == {"working electrode": "positive"}
