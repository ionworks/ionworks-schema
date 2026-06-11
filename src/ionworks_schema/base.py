"""Base classes for ionworks_schema."""

from typing import Any

import pybamm
from pybamm.expression_tree.operations.serialise import Serialise
from pydantic import BaseModel, ConfigDict, Field, field_validator


def _get_element_type(comp: Any) -> str | None:
    """Determine the ``element_type`` discriminator for a pipeline component.

    Parameters
    ----------
    comp : Any
        A pipeline element instance (``DirectEntry``, ``DataFit``,
        ``Validation``, ``Calculation``, …).

    Returns
    -------
    str or None
        The canonical ``element_type`` string (``"entry"``, ``"data_fit"``,
        ``"validation"``, or ``"calculation"``), or ``None`` for raw configs
        (e.g. dicts) that are not recognised schema objects, so they pass
        through unchanged.
    """
    cls = type(comp)
    mro_names = {c.__name__ for c in cls.__mro__}
    if "DirectEntry" in mro_names:
        return "entry"
    if "DirectEntryFunctionSchema" in mro_names:
        return "entry"
    if cls.__name__ in ("DataFit", "ArrayDataFit"):
        return "data_fit"
    if cls.__name__ == "Validation":
        return "validation"
    if "Calculation" in mro_names:
        return "calculation"
    return None


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
    # pandas or polars DataFrame -> dict of lists for serialization
    if hasattr(value, "to_dict") and hasattr(value, "columns"):
        cls = type(value)
        mod = getattr(cls, "__module__", "")
        if "pandas" in mod:
            return value.to_dict(orient="list")
        if "polars" in mod:
            return value.to_dict(as_series=False)
        try:
            return value.to_dict(orient="list")
        except TypeError:
            return value.to_dict(as_series=False)
    if isinstance(value, (int, float, str, bool)):
        return value
    if hasattr(value, "tolist"):  # numpy arrays
        return value.tolist()
    return value


class BaseSchema(BaseModel):
    """Shared parent of every schema class in this package.

    You won't usually construct ``BaseSchema`` directly — you'll
    construct one of its concrete subclasses (``iws.Pipeline``,
    ``iws.DataFit``, ``iws.Parameter``, …). It provides the
    ``.to_config()`` method every schema uses to produce the dict you
    submit through ``ionworks-api``, and it rejects unknown fields so
    typos are caught at construction time instead of silently lost on
    the way to the server.
    """

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    # Output-direction field-name mappings for parser compatibility. The
    # symmetric input-direction mapping is provided by Pydantic field
    # aliases (e.g. ``FittingObjective.data_input`` carries
    # ``alias="data"``); together they let the schema accept ``"data"`` on
    # the wire and emit ``"data"`` in ``to_config()`` while keeping
    # ``data_input`` as the Python attribute. New mappings should prefer
    # the alias mechanism (input + output in one place); this dict survives
    # because ``to_config`` does a custom iteration rather than
    # ``model_dump(by_alias=True)``.
    _field_mappings = {"data_input": "data"}
    # Fields to exclude from serialization (comes from dict key in parser)
    _exclude_fields: set = set()
    # When False, to_config omits the "type" discriminator. Set on subclasses
    # whose serialised output must be a plain option dict (e.g. algorithm
    # options passed to pipeline algorithm classes that reject unknown keys).
    _emit_type: bool = True

    def to_config(self) -> dict:
        """Build the dict you submit through ``ionworks-api``.

        This is the bridge between the friendly schema objects you
        construct in Python (``iws.DataFit(...)``, ``iws.Normal(...)``,
        …) and the JSON-shaped payload the Ionworks API expects when
        you submit a job. Build your schema, call ``.to_config()``, and
        pass the result to the API client.

        Nested schemas are converted recursively, ``None`` fields are
        dropped so the payload stays minimal, and a ``"type"`` key
        identifying the concrete class is appended for every component
        that needs to be re-identified at the server.
        """
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
        if self._emit_type and cls_name not in (
            "Pipeline",
            "DataFit",
            "ArrayDataFit",
            "Parameter",
            "DirectEntry",
            "Validation",
            "Calculation",
        ):
            config["type"] = cls_name
        return config

    def run(self, *args, **kwargs):
        raise NotImplementedError(
            "Execution not available. Submit to Ionworks API instead."
        )


class Pipeline(BaseSchema):
    """A sequence of steps that together produce a parameterised cell model.

    Each step (an "element") does one of: pull parameters from a
    source (``DirectEntry``), fit parameters to measured data
    (``DataFit``), compute derived quantities (``Calculation``), or
    check the fitted parameters against held-out data
    (``Validation``). The parameters produced by one element are
    passed on to the next, so the order matters.

    Once you've added every element you need, call ``.to_config()``
    on the pipeline and submit the result through ``ionworks-api`` to
    run the whole job server-side.

    Parameters
    ----------
    elements : dict, optional
        Mapping of element name to pipeline element (``DataFit``,
        ``DirectEntry``, ``Validation``, ``Calculation``, …). The name
        is used to identify the element in the pipeline report.
        ``None`` is treated as an empty pipeline by ``to_config``.
    output_file : str, optional
        Optional file path for persisting the final parameter values
        produced by the pipeline. If ``None``, parameters are not
        written to disk.
    name : str, optional
        Human-readable name for the pipeline, used in reports and logs.
    description : str, optional
        Free-text description of what the pipeline does.

    Examples
    --------
    >>> # known parameters (e.g. ambient temperature)
    >>> known = iws.direct_entries.DirectEntry(
    ...     parameters={"Ambient temperature [K]": 298.15},
    ... )
    >>> # fit one parameter against an OCP measurement
    >>> obj = iws.objectives.OCPHalfCell(
    ...     electrode="positive",
    ...     data_input="path/to/ocp.csv",
    ... )
    >>> fit = iws.DataFit(
    ...     objectives={"ocp": obj},
    ...     parameters={"Positive electrode capacity [A.h]": iws.Parameter(
    ...         "Positive electrode capacity [A.h]", initial_value=3.0, bounds=(2.0, 4.0),
    ...     )},
    ... )
    >>> # validate the fit against held-out cycling data
    >>> val_obj = iws.objectives.CurrentDriven(data_input="path/to/cycle.csv")
    >>> val = iws.Validation(objectives={"cycle": val_obj})
    >>> pipeline = iws.Pipeline({"known": known, "ocp fit": fit, "validate": val})
    >>> config = pipeline.to_config()
    >>> # then submit `config` via ionworks-api
    """

    elements: dict | None = Field(
        default=None,
        description=(
            "Mapping of element name to pipeline element (``DataFit``, "
            "``DirectEntry``, ``Validation``, ``Calculation``, …). The name "
            "is used to identify the element in the pipeline report. "
            "``None`` is treated as an empty pipeline by ``to_config``."
        ),
    )
    output_file: str | None = Field(
        default=None,
        description=(
            "Optional file path for persisting the final parameter values "
            "produced by the pipeline. If None, parameters are not written "
            "to disk."
        ),
    )
    name: str | None = Field(
        default=None,
        description=("Human-readable name for the pipeline, used in reports and logs."),
    )
    description: str | None = Field(
        default=None,
        description="Free-text description of what the pipeline does.",
    )

    def __init__(
        self,
        elements: dict | None = None,
        output_file: str | None = None,
        name: str | None = None,
        description: str | None = None,
        **extra: Any,
    ):
        # Forward extra kwargs to BaseModel.__init__ so Pydantic enforces
        # ``extra='forbid'`` at the field-validation layer (rather than
        # raising a Python-level TypeError that bypasses Pydantic).
        super().__init__(
            elements=elements,
            output_file=output_file,
            name=name,
            description=description,
            **extra,
        )

    def to_config(self) -> dict:
        """Build the pipeline payload you submit through ``ionworks-api``.

        Walks every element you added to ``elements``, serialises it
        (each element's own ``to_config``), and tags it with its kind
        (``"entry"``, ``"data_fit"``, ``"validation"``, …) so the
        server knows how to dispatch it. Pass the returned dict to the
        Ionworks API to run the full pipeline.
        """
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

            # Set element_type only for known schema types; raw configs (e.g. dicts) keep their existing element_type
            elem_type = _get_element_type(comp)
            if elem_type is not None:
                elem_config["element_type"] = elem_type
            config["elements"][name] = elem_config

        # Add other fields
        if self.output_file is not None:
            config["output_file"] = self.output_file
        if self.name is not None:
            config["name"] = self.name
        if self.description is not None:
            config["description"] = self.description

        return config


# Keep in sync with the backend's EXPENSIVE_ELEMENT_TYPES
# (backend/src/pydantic_models/simple_pipelines.py).
_EXPENSIVE_TYPES = frozenset({"data_fit", "validation"})


class SimplePipeline(Pipeline):
    """A pipeline that permits at most one expensive element.

    ``SimplePipeline`` is identical to :class:`Pipeline` except that it
    rejects configurations containing more than one expensive element
    (``DataFit``, ``ArrayDataFit``, or ``Validation``) at construction time.
    Use it when you intend to submit via the SimplePipeline API endpoint,
    which enforces the same constraint server-side.

    Parameters
    ----------
    elements : dict, optional
        Mapping of element name to pipeline element (``DataFit``,
        ``DirectEntry``, ``Validation``, ``Calculation``, …). At most
        one element may be a ``DataFit``, ``ArrayDataFit``, or ``Validation``.
    output_file : str, optional
        Optional file path for persisting the final parameter values
        produced by the pipeline. If ``None``, parameters are not
        written to disk.
    name : str, optional
        Human-readable name for the pipeline, used in reports and logs.
    description : str, optional
        Free-text description of what the pipeline does.

    Raises
    ------
    ValueError
        If ``elements`` contains more than one ``DataFit``, ``ArrayDataFit``,
        or ``Validation`` element.

    Examples
    --------
    >>> entry = iws.direct_entries.DirectEntry(
    ...     parameters={"Ambient temperature [K]": 298.15},
    ... )
    >>> obj = iws.objectives.OCPHalfCell(
    ...     electrode="positive",
    ...     data_input="path/to/ocp.csv",
    ... )
    >>> fit = iws.DataFit(
    ...     objectives={"ocp": obj},
    ...     parameters={"Positive electrode capacity [A.h]": iws.Parameter(
    ...         "Positive electrode capacity [A.h]",
    ...         initial_value=3.0,
    ...         bounds=(2.0, 4.0),
    ...     )},
    ... )
    >>> pipeline = iws.SimplePipeline(
    ...     elements={"known": entry, "ocp fit": fit},
    ...     name="Single OCP fit",
    ... )
    >>> config = pipeline.to_config()
    """

    @field_validator("elements")
    @classmethod
    def _validate_at_most_one_expensive_element(
        cls, elements: dict | None
    ) -> dict | None:
        # A field (not model) validator so the constraint also re-runs on
        # reassignment (``sp.elements = ...``), since BaseSchema enables
        # ``validate_assignment``.
        if elements is None:
            return elements
        # Raw dicts carry their own element_type; schema objects are classified
        # via _get_element_type (the same mapping to_config uses).
        expensive = [
            name
            for name, elem in elements.items()
            if (
                elem.get("element_type")
                if isinstance(elem, dict)
                else _get_element_type(elem)
            )
            in _EXPENSIVE_TYPES
        ]
        if len(expensive) > 1:
            raise ValueError(
                f"SimplePipeline allows at most one DataFit, ArrayDataFit, or Validation "
                f"element, but got {len(expensive)}: {expensive}"
            )
        return elements
