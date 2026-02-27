"""Base classes for ionworks_schema."""

from typing import Any

import pybamm
from pybamm.expression_tree.operations.serialise import Serialise
from pydantic import BaseModel, ConfigDict


def _get_element_type(cls_name: str) -> str:
    """Determine element_type for a pipeline component based on class name."""
    if cls_name in ("DataFit", "ArrayDataFit"):
        return "data_fit"
    if cls_name == "Validation":
        return "validation"
    if cls_name == "DirectEntry":
        return "entry"
    # Calculations and other pipeline elements
    return "calculation"


def _serialize_pybamm_model(model):
    """Serialize a pybamm model to a config dict.

    Built-in models (those in pybamm.lithium_ion) are serialized as
    {"type": "ClassName", "options": {...}}. Custom models are serialized
    using pybamm's Serialise to {"type": "custom", "model": ...}.
    """
    class_name = model.__class__.__name__
    if hasattr(pybamm.lithium_ion, class_name):
        config = {"type": class_name}
        if hasattr(model, "options"):
            options = {k: v for k, v in model.options.items() if v is not None}
            if options:
                config["options"] = options
        return config

    config = {
        "type": "custom",
        "model": Serialise.serialise_custom_model(model),
    }
    if hasattr(model, "default_geometry"):
        config["geometry"] = Serialise.serialise_custom_geometry(model.default_geometry)
    if hasattr(model, "default_var_pts"):
        config["var_pts"] = Serialise.serialise_var_pts(model.default_var_pts)
    if hasattr(model, "default_spatial_methods"):
        config["spatial_methods"] = Serialise.serialise_spatial_methods(
            model.default_spatial_methods
        )
    if hasattr(model, "default_submesh_types"):
        config["submesh_types"] = Serialise.serialise_submesh_types(
            model.default_submesh_types
        )
    return config


def _serialize_value(value):
    """Recursively serialize a value, calling to_config on schemas."""
    if value is None:
        return None
    if isinstance(value, BaseSchema):
        return value.to_config()
    if isinstance(value, dict):
        return {k: _serialize_value(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_serialize_value(v) for v in value]
    if hasattr(value, "to_config"):
        return value.to_config()
    if hasattr(value, "model_dump"):
        return value.model_dump(exclude_none=True)
    if isinstance(value, pybamm.BaseModel):
        return _serialize_pybamm_model(value)
    if isinstance(value, (int, float, str, bool)):
        return value
    if hasattr(value, "tolist"):  # numpy arrays
        return value.tolist()
    return value


class BaseSchema(BaseModel):
    """Base schema for all configurations."""

    model_config = ConfigDict(
        extra="allow",
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    # Field name mappings for parser compatibility
    _field_mappings = {"data_input": "data"}
    # Fields to exclude from serialization (comes from dict key in parser)
    _exclude_fields: set = set()

    def to_config(self) -> dict:
        """Convert to configuration dictionary."""
        config = {}
        # Process each field, calling to_config on nested schemas
        for key, value in self:
            if value is None:
                continue
            # Skip excluded fields
            if key in self._exclude_fields:
                continue
            # Apply field name mappings for parser compatibility
            output_key = self._field_mappings.get(key, key)
            config[output_key] = _serialize_value(value)
        # Add type field based on class name (except for top-level containers)
        cls_name = self.__class__.__name__
        if cls_name not in (
            "Pipeline",
            "DataFit",
            "ArrayDataFit",
            "Parameter",
            "DirectEntry",
        ):
            config["type"] = cls_name
        return config

    def run(self, *args, **kwargs):
        raise NotImplementedError(
            "Execution not available. Submit to Ionworks API instead."
        )


class Pipeline(BaseSchema):
    """Schema for Pipeline with special to_config handling."""

    elements: Any | None = None
    output_file: Any | None = None
    name: Any | None = None
    description: Any | None = None

    def __init__(
        self,
        elements: dict | None = None,
        output_file: str | None = None,
        name: str | None = None,
        description: str | None = None,
    ):
        super().__init__(
            elements=elements,
            output_file=output_file,
            name=name,
            description=description,
        )

    def to_config(self) -> dict:
        """Convert to parser-compatible format with elements."""
        config = {"elements": {}}

        for name, comp in (self.elements or {}).items():
            # Serialize the component
            if hasattr(comp, "to_config"):
                elem_config = comp.to_config()
            elif hasattr(comp, "model_dump"):
                elem_config = comp.model_dump(exclude_none=True)
            elif isinstance(comp, dict):
                elem_config = dict(comp)
            else:
                elem_config = {}

            # Determine element_type from class name
            cls_name = type(comp).__name__
            elem_config["element_type"] = _get_element_type(cls_name)
            config["elements"][name] = elem_config

        # Add other fields
        if self.output_file is not None:
            config["output_file"] = self.output_file
        if self.name is not None:
            config["name"] = self.name
        if self.description is not None:
            config["description"] = self.description

        return config
