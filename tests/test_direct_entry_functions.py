"""Tests for direct entry function-style API and DirectEntryFunctionSchema classes."""

import ionworks_schema as iws
from ionworks_schema.direct_entries import FUNCTION_SCHEMAS
from ionworks_schema.direct_entries.function_schemas import (
    ArrheniusButlerVolmerExchangeCurrentDensity,
    AverageOcp,
    Bruggeman,
    ConstantElectrolyte,
    FromJson,
    LandesfeindElectrolyte,
    MechanicalDegradationDefaults,
    StandardDefaults,
    Temperatures,
    ZeroEntropicChange,
)


def test_function_schemas_exposed_on_module():
    """All FUNCTION_SCHEMAS names are available as iws.direct_entries.<name>."""
    for name in FUNCTION_SCHEMAS:
        assert hasattr(iws.direct_entries, name), f"missing {name}"
        cls = getattr(iws.direct_entries, name)
        assert cls is FUNCTION_SCHEMAS[name]


def test_direct_entry_function_schema_to_config_has_name():
    """Every DirectEntryFunctionSchema to_config() returns dict with 'name' key."""
    entry = AverageOcp(electrode="positive")
    cfg = entry.to_config()
    assert "name" in cfg
    assert cfg["name"] == "average_ocp"


def test_average_ocp_omits_default_phase():
    """AverageOcp with phase=None omits phase from to_config for minimal output."""
    entry = AverageOcp(electrode="negative")
    cfg = entry.to_config()
    assert cfg["name"] == "average_ocp"
    assert cfg["electrode"] == "negative"
    assert "phase" not in cfg or cfg.get("phase") is None


def test_average_ocp_includes_phase_when_set():
    """AverageOcp includes phase in to_config when provided."""
    entry = AverageOcp(electrode="positive", phase="primary")
    cfg = entry.to_config()
    assert cfg["phase"] == "primary"


def test_arrhenius_butler_volmer_required_electrode():
    """ArrheniusButlerVolmerExchangeCurrentDensity requires electrode."""
    entry = ArrheniusButlerVolmerExchangeCurrentDensity(electrode="positive")
    cfg = entry.to_config()
    assert cfg["name"] == "arrhenius_butler_volmer_exchange_current_density"
    assert cfg["electrode"] == "positive"
    # default direction and phase are "" so omitted
    assert "direction" not in cfg or cfg.get("direction") == ""


def test_arrhenius_butler_volmer_with_direction_phase():
    """ArrheniusButlerVolmerExchangeCurrentDensity includes direction/phase when set."""
    entry = ArrheniusButlerVolmerExchangeCurrentDensity(
        electrode="negative",
        direction="lithiation",
        phase="primary",
    )
    cfg = entry.to_config()
    assert cfg["direction"] == "lithiation"
    assert cfg["phase"] == "primary"


def test_constant_electrolyte_requires_c_e():
    """ConstantElectrolyte requires c_e."""
    entry = ConstantElectrolyte(c_e=1000.0)
    cfg = entry.to_config()
    assert cfg["name"] == "constant_electrolyte"
    assert cfg["c_e"] == 1000.0


def test_temperatures_default_T():
    """Temperatures has default T=298.15, included in to_config if set."""
    entry = Temperatures()
    cfg = entry.to_config()
    assert cfg["name"] == "temperatures"
    assert cfg.get("T") == 298.15


def test_temperatures_custom_T():
    """Temperatures with custom T serializes it."""
    entry = Temperatures(T=310.0)
    cfg = entry.to_config()
    assert cfg["T"] == 310.0


def test_zero_entropic_change_no_required_fields():
    """ZeroEntropicChange has no required fields beyond name."""
    entry = ZeroEntropicChange()
    cfg = entry.to_config()
    assert cfg["name"] == "zero_entropic_change"
    assert len(cfg) == 1


def test_standard_defaults_no_required_fields():
    """StandardDefaults has no required fields."""
    entry = StandardDefaults()
    cfg = entry.to_config()
    assert cfg["name"] == "standard_defaults"


def test_bruggeman_defaults():
    """Bruggeman has default electrode=0, electrolyte=1.5."""
    entry = Bruggeman()
    cfg = entry.to_config()
    assert cfg["name"] == "bruggeman"
    assert cfg.get("electrode") == 0
    assert cfg.get("electrolyte") == 1.5


def test_bruggeman_custom():
    """Bruggeman with custom exponents."""
    entry = Bruggeman(electrode=0.5, electrolyte=2.0)
    cfg = entry.to_config()
    assert cfg["electrode"] == 0.5
    assert cfg["electrolyte"] == 2.0


def test_landesfeind_electrolyte_required_fields():
    """LandesfeindElectrolyte requires c_e and system."""
    entry = LandesfeindElectrolyte(c_e=2000.0, system="EC:DMC (1:1)")
    cfg = entry.to_config()
    assert cfg["name"] == "landesfeind_electrolyte"
    assert cfg["c_e"] == 2000.0
    assert cfg["system"] == "EC:DMC (1:1)"


def test_from_json_requires_file_path():
    """FromJson requires file_path."""
    entry = FromJson(file_path="/path/to/params.json")
    cfg = entry.to_config()
    assert cfg["name"] == "from_json"
    assert cfg["file_path"] == "/path/to/params.json"


def test_mechanical_degradation_defaults_requires_electrode():
    """MechanicalDegradationDefaults requires electrode."""
    entry = MechanicalDegradationDefaults(electrode="positive")
    cfg = entry.to_config()
    assert cfg["name"] == "mechanical_degradation_defaults"
    assert cfg["electrode"] == "positive"


def test_pipeline_with_function_entry_roundtrip():
    """Pipeline with a function-style entry serializes with element_type entry."""
    entry = iws.direct_entries.arrhenius_particle_diffusivity(
        electrode="positive",
        direction="",
        phase="",
    )
    pipe = iws.Pipeline(elements={"D": entry})
    cfg = pipe.to_config()
    assert cfg["elements"]["D"]["element_type"] == "entry"
    assert cfg["elements"]["D"]["name"] == "arrhenius_particle_diffusivity"
    assert cfg["elements"]["D"]["electrode"] == "positive"
    # empty direction/phase omitted
    assert (
        "direction" not in cfg["elements"]["D"] or not cfg["elements"]["D"]["direction"]
    )
    assert "phase" not in cfg["elements"]["D"] or not cfg["elements"]["D"]["phase"]
