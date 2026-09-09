"""Tests for the model schemas in ``ionworks_schema.models``."""

import ionworks_schema as iws
from pydantic import ValidationError
import pytest


class TestGITTModel:
    def test_to_config_defaults(self):
        config = iws.models.GITTModel().to_config()
        assert config == {"type": "GITTModel"}

    @pytest.mark.parametrize("working_electrode", ["both", "positive"])
    def test_to_config_with_working_electrode(self, working_electrode):
        config = iws.models.GITTModel(
            options={"working electrode": working_electrode}
        ).to_config()
        assert config == {
            "type": "GITTModel",
            "options": {"working electrode": working_electrode},
        }

    def test_to_config_with_options(self):
        config = iws.models.GITTModel(options={"foo": "bar"}).to_config()
        assert config == {"type": "GITTModel", "options": {"foo": "bar"}}

    @pytest.mark.parametrize("working_electrode", ["negative", "lithium"])
    def test_invalid_working_electrode_rejected(self, working_electrode):
        with pytest.raises(ValidationError, match="working electrode"):
            iws.models.GITTModel(options={"working electrode": working_electrode})
