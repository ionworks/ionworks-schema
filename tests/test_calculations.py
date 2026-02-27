"""Tests for ionworks_schema calculations."""

from ionworks_schema.calculations import (
    AreaToSquareWidthHeight,
    ArrheniusDiffusivityFromMSMRData,
    Calculation,
)


def test_calculation_base_to_config():
    """Calculation with optional source serializes."""
    calc = Calculation(source="custom method")
    cfg = calc.to_config()
    assert cfg.get("source") == "custom method"
    # Calculation is in BaseSchema's exclude list for "type", so no type key
    assert isinstance(cfg, dict)


def test_calculation_no_source():
    """Calculation can be constructed with no source."""
    calc = Calculation()
    cfg = calc.to_config()
    assert isinstance(cfg, dict)


def test_area_to_square_width_height():
    """AreaToSquareWidthHeight is a Calculation with no extra required fields."""
    calc = AreaToSquareWidthHeight()
    assert isinstance(calc, Calculation)
    cfg = calc.to_config()
    assert cfg.get("type") == "AreaToSquareWidthHeight"


def test_arrhenius_diffusivity_from_msmr_data_minimal():
    """ArrheniusDiffusivityFromMSMRData requires electrode and data."""
    # Minimal data: dict with required columns (schema uses Any)
    data = {"Stoichiometry": [0.1, 0.5, 0.9], "Voltage [V]": [3.0, 3.4, 3.8]}
    calc = ArrheniusDiffusivityFromMSMRData(
        electrode="positive",
        data=data,
    )
    cfg = calc.to_config()
    assert cfg.get("electrode") == "positive"
    assert cfg.get("data") == data
    assert cfg.get("direction") == ""
    assert cfg.get("phase") == ""
    assert cfg.get("type") == "ArrheniusDiffusivityFromMSMRData"


def test_arrhenius_diffusivity_from_msmr_data_with_options():
    """ArrheniusDiffusivityFromMSMRData accepts options."""
    data = {"Stoichiometry": [0.5], "Voltage [V]": [3.4]}
    calc = ArrheniusDiffusivityFromMSMRData(
        electrode="negative",
        data=data,
        direction="lithiation",
        phase="primary",
        options={"interpolator": "linear"},
    )
    cfg = calc.to_config()
    assert cfg.get("direction") == "lithiation"
    assert cfg.get("phase") == "primary"
    assert cfg.get("options") == {"interpolator": "linear"}
