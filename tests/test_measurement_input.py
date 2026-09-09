"""MeasurementInput recognises the named payload shapes and rejects their typos."""

import ionworks_schema as iws
import pandas as pd
from pydantic import ValidationError
import pytest

_TS = {"Time [s]": [0.0, 1.0], "Voltage [V]": [4.0, 3.9]}


def _objective(data_input):
    return iws.objectives.Objective(data_input=data_input)


def test_bad_dataloader_option_is_rejected_at_submission():
    """The whole point of this PR: caught when built, not mid-job."""
    with pytest.raises(ValidationError, match="sortt"):
        _objective({"data": {"time_series": _TS}, "options": {"sortt": True}})


def test_good_dataloader_option_is_accepted():
    obj = _objective({"data": {"time_series": _TS}, "options": {"sort": True}})
    assert obj.to_config()["data"]["options"] == {"sort": True}


def test_plain_column_mapping_stays_open():
    """Column names are arbitrary, so this arm cannot forbid unknown keys."""
    obj = _objective({"Time [s]": [0.0], "Some Odd Column": [1.0]})
    assert obj.to_config()["data"]["Some Odd Column"] == [1.0]


def test_time_series_shape_rejects_a_stray_sibling():
    with pytest.raises(ValidationError):
        _objective({"time_series": _TS, "stpes": None})


def test_metadata_shape_routes_through_the_objective_without_double_wrapping():
    """The MetadataSpec arm is checked first and is the most common real shape.

    Goes through ``_objective`` (the router), not ``iws.MetadataSpec`` directly,
    because constructing the shape directly would skip the router entirely and
    miss both a routing regression (e.g. the ``and`` above turning into ``or``)
    and a re-wrap regression on this class's own "data" field.
    """
    df = pd.DataFrame({"Voltage [V]": [4.2, 3.5], "Capacity [A.h]": [0.0, 1.0]})
    obj = _objective({"data": df, "metadata": {"temperature": 298.15}})
    assert isinstance(obj.data_input, iws.MetadataSpec)
    cfg = obj.to_config()
    assert cfg["data"]["data"] == df.to_dict(orient="list")
    assert cfg["data"]["metadata"] == {"temperature": 298.15}


class TestStringLocatorPrefix:
    """A string measurement says where to read itself from.

    The loader already requires this and rejects anything else, so these move an
    existing rejection from job-parse time to config-build time.
    """

    @pytest.mark.parametrize("spec", ["file:x.csv", "folder:/tmp/run", "db:9f0c-1234"])
    def test_each_locator_prefix_is_accepted(self, spec):
        assert _objective(spec).data_input == spec

    def test_a_bare_path_is_rejected(self):
        with pytest.raises(ValidationError, match="file:"):
            _objective("path/to/discharge.csv")

    def test_the_message_shows_how_to_fix_it(self):
        """The bare path is the mistake people actually make, so name the fix."""
        with pytest.raises(ValidationError) as exc:
            _objective("data.csv")
        assert "file:data.csv" in str(exc.value)

    def test_an_unknown_prefix_is_rejected(self):
        with pytest.raises(ValidationError, match="file:"):
            _objective("s3://bucket/data.csv")
