"""Minimal tests for ionworks_schema: import, instantiate, and to_config()."""

import ionworks_schema as iws


def test_import_and_version():
    """Public API imports and has __version__."""
    assert hasattr(iws, "__version__")
    assert isinstance(iws.__version__, str)
    assert iws.Pipeline is not None
    assert iws.Validation is not None
    assert iws.DataFit is not None
    assert iws.BaseSchema is not None


def test_pipeline_empty_to_config():
    """Pipeline with no elements serializes to config with empty elements."""
    pipe = iws.Pipeline(elements={})
    cfg = pipe.to_config()
    assert "elements" in cfg
    assert cfg["elements"] == {}


def test_direct_entry_function_schema_to_config():
    """Direct entry from function-style API has name and kwargs in to_config()."""
    entry = iws.direct_entries.average_ocp(electrode="positive")
    cfg = entry.to_config()
    assert cfg["name"] == "average_ocp"
    assert cfg.get("electrode") == "positive"


def test_pipeline_with_entry_has_element_type():
    """Pipeline containing a direct entry serializes element with element_type entry."""
    entry = iws.direct_entries.average_ocp(electrode="negative")
    pipe = iws.Pipeline(elements={"ocp": entry})
    cfg = pipe.to_config()
    assert "elements" in cfg
    assert "ocp" in cfg["elements"]
    assert cfg["elements"]["ocp"]["element_type"] == "entry"
    assert cfg["elements"]["ocp"]["name"] == "average_ocp"


def test_validation_to_config():
    """Validation with minimal objectives serializes to config."""
    val = iws.Validation(objectives={})
    cfg = val.to_config()
    assert "objectives" in cfg
    assert cfg["objectives"] == {}
