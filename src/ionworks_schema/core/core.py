"""Schemas for core."""

from ..base import BaseSchema


class ConfigMixin(BaseSchema):
    """Mixin that automatically captures __init__ parameters for subclasses.

    When a class inherits from this mixin, any subclass that defines its own
    __init__ method will have its parameters automatically captured and stored
    in `self._init_params`. This is useful for serialization/deserialization
    (e.g., `to_config` methods for reverse parsing).

    Additionally, if the __init__ has an "options" parameter, it captures which
    option keys were explicitly passed in `self._options_keys_passed` before
    calling the original __init__.

    The captured parameters exclude `self` and filter out `None` values.

    This mixin also provides `config_schema()` classmethod that generates a
    pydantic schema from the class's __init__ signature. This is used by
    ionworksschema generation."""

    pass
