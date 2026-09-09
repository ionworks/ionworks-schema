"""Tests for ionworks_schema.DataLoaderOptions."""

import ionworks_schema as iws
from pydantic import ValidationError
import pytest


class TestDataLoaderOptions:
    """The DataLoader option bag is a closed contract, not a free-form dict."""

    def test_unknown_key_is_rejected(self):
        """A typo used to be accepted and silently ignored."""
        with pytest.raises(ValidationError, match="sortt"):
            iws.DataLoaderOptions(sortt=True)

    def test_live_keys_are_accepted(self):
        opts = iws.DataLoaderOptions(
            transforms={"sort": True},
            first_step=2,
            last_step={"cycle": 3},
            capacity_column="Capacity [A.h]",
        )
        assert opts.transforms.sort is True
        assert opts.transforms.to_config() == {"sort": True}
        assert opts.first_step == 2
        assert opts.last_step == {"cycle": 3}

    @pytest.mark.parametrize(
        "key",
        [
            "gitt_to_ocp",
            "rest_to_ocp",
            "sort",
            "remove_duplicates",
            "remove_extremes",
            "keep_first_ocp_point",
        ],
    )
    def test_legacy_top_level_flags_are_accepted(self, key):
        """These migrate into ``transforms`` at run time, so they stay valid."""
        assert iws.DataLoaderOptions(**{key: True}).to_config() == {key: True}

    def test_deprecated_step_dict_spellings_are_accepted(self):
        opts = iws.DataLoaderOptions(first_step_dict={"step": 1})
        assert opts.first_step_dict == {"step": 1}

    def test_to_config_emits_only_what_was_set(self):
        assert iws.DataLoaderOptions().to_config() == {}
        assert iws.DataLoaderOptions(sort=True).to_config() == {"sort": True}

    def test_to_config_emits_no_type_discriminator(self):
        assert "type" not in iws.DataLoaderOptions(sort=True).to_config()

    def test_sql_query_first_step_is_accepted(self):
        """SQL query form for step selection is live and tested in the loader."""
        opts = iws.DataLoaderOptions(
            first_step='SELECT * FROM steps WHERE "Step count" = 3 LIMIT 1'
        )
        assert opts.first_step == 'SELECT * FROM steps WHERE "Step count" = 3 LIMIT 1'

    def test_sql_query_last_step_is_accepted(self):
        """SQL query form for step selection is live and tested in the loader."""
        opts = iws.DataLoaderOptions(
            last_step='SELECT * FROM steps WHERE "Cycle count" = 0 ORDER BY "Step count" DESC LIMIT 1'
        )
        assert (
            opts.last_step
            == 'SELECT * FROM steps WHERE "Cycle count" = 0 ORDER BY "Step count" DESC LIMIT 1'
        )


class TestNestedTransforms:
    """``transforms`` is the canonical spelling, so it must be closed too.

    Typing only the legacy top-level aliases would have left the documented form
    as the one place a typo is still accepted and silently dropped.
    """

    def test_nested_typo_is_rejected(self):
        with pytest.raises(ValidationError, match="sortt"):
            iws.DataLoaderOptions(transforms={"sortt": True})

    def test_nested_step_is_accepted_and_emitted(self):
        opts = iws.DataLoaderOptions(transforms={"sort": True})
        assert opts.to_config() == {"transforms": {"sort": True}}

    def test_nested_emits_only_the_steps_that_were_set(self):
        assert iws.DataLoaderOptions(transforms={}).to_config() == {"transforms": {}}

    def test_interpolate_still_accepts_an_array(self):
        """An ndarray is a supported, tested input; pydantic coerces it to a list."""
        import numpy as np

        opts = iws.DataLoaderOptions(transforms={"interpolate": np.array([0.0, 0.5])})
        assert opts.transforms.interpolate == [0.0, 0.5]

    def test_top_level_alias_and_nested_form_agree_on_their_keys(self):
        """Both spellings must accept the same steps, or one silently drops them."""
        nested = set(iws.DataLoaderTransforms.model_fields)
        top_level = set(iws.DataLoaderOptions.model_fields) & nested
        assert nested == top_level


class TestNamedPayloadShapes:
    """The named data payload shapes are closed; a column mapping is not."""

    def test_time_series_shape_accepts_its_two_keys(self):
        spec = iws.TimeSeriesSpec(time_series={"Time [s]": [0.0]}, steps=None)
        assert spec.time_series == {"Time [s]": [0.0]}

    def test_time_series_shape_rejects_a_stray_key(self):
        with pytest.raises(ValidationError, match="stpes"):
            iws.TimeSeriesSpec(time_series={"Time [s]": [0.0]}, stpes=None)

    def test_data_payload_shape_types_its_options(self):
        with pytest.raises(ValidationError, match="sortt"):
            iws.DataPayloadSpec(data="db:abc", options={"sortt": True})

    def test_data_payload_shape_accepts_valid_options(self):
        spec = iws.DataPayloadSpec(data="db:abc", options={"sort": True})
        assert spec.options.sort is True

    def test_metadata_shape_accepts_its_two_keys(self):
        spec = iws.MetadataSpec(data={"Time [s]": [0.0]}, metadata={"source": "x"})
        assert spec.metadata == {"source": "x"}
