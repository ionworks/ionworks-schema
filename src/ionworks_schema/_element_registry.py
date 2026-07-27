"""Package-wide pipeline-element resolution.

A single dispatcher that validates a pipeline element config dict against the
matching ``ionworks_schema`` class. The deep ``Pipeline`` before-validator and
(via :func:`schema_class_for`) the engine parsers both resolve elements through
here, so the schema classes stay the one source of truth for a valid element.
"""

from .base import BaseSchema


def entry_schema_for_name(name: str):
    """Resolve an entry ``name`` to its schema class.

    Entry classes are split across ``direct_entries.py`` (class-based, PascalCase)
    and ``function_schemas.py`` (function-based, snake_case via
    ``FUNCTION_SCHEMAS``), so a single ``getattr`` is insufficient.
    """
    from . import direct_entries

    cls = getattr(direct_entries, name, None)
    # Resolve concrete entry classes only — the abstract function-schema base
    # is a BaseSchema subclass but isn't a valid entry type, so exclude it.
    if (
        isinstance(cls, type)
        and issubclass(cls, BaseSchema)
        and cls is not direct_entries.DirectEntryFunctionSchema
    ):
        return cls
    return direct_entries.FUNCTION_SCHEMAS.get(name)


def schema_class_for(element_type: str, type_name: str | None = None):
    """Return the ``ionworks_schema`` class for an ``(element_type, type)`` pair.

    Shared with the engine parsers so element-class lookup lives in one place.
    ``entry`` resolution needs the full config (its shape, not a type name)
    selects the class, so this returns ``None`` for ``entry`` — use
    :func:`validate_element` instead.

    Raises
    ------
    ValueError
        If ``element_type`` is unsupported, or a ``calculation`` ``type_name``
        does not name a known calculation class.
    """
    if element_type == "data_fit":
        from .data_fit.data_fit import DataFit

        return DataFit
    if element_type == "array_data_fit":
        from .data_fit.data_fit import ArrayDataFit

        return ArrayDataFit
    if element_type == "validation":
        from .validation import Validation

        return Validation
    if element_type == "calculation":
        from . import calculations
        from .calculations.calculations import Calculation

        cls = getattr(calculations, type_name, None) if type_name else None
        # Concrete calculations only — the abstract ``Calculation`` base passes
        # ``issubclass`` but isn't a real calculation type, so exclude it.
        if not (
            isinstance(cls, type)
            and issubclass(cls, Calculation)
            and cls is not Calculation
        ):
            raise ValueError(
                f"Unknown calculation type {type_name!r}. Expected a class in "
                "iws.calculations."
            )
        return cls
    if element_type == "entry":
        return None
    raise ValueError(f"Unsupported element_type {element_type!r}.")


def _validate_entry(data: dict):
    """Validate an ``entry`` config, mirroring the engine's shape dispatch.

    Each shape passes its full remaining payload to the schema, so unknown
    sibling keys are caught by ``extra="forbid"``. ``source`` is re-attached
    where the target schema declares it (function schemas don't, matching the
    engine, which keeps source as runtime-only metadata for those).
    """
    from . import direct_entries

    source = data.pop("source", None)
    if data.get("path") is not None and data.get("values") is not None:
        raise ValueError("Entry config cannot set both 'path' and 'values'.")

    if data.get("path") is not None:
        return direct_entries.FUNCTION_SCHEMAS["from_json"].model_validate(
            {"file_path": data.pop("path"), **data}
        )
    if data.get("values") is not None or data.get("pipeline_id") is not None:
        payload = dict(data)
        if "values" in payload:
            payload["parameters"] = payload.pop("values")
        if source is not None:
            payload["source"] = source
        return direct_entries.DirectEntry.model_validate(payload)
    if data.get("name") is not None:
        name = data.pop("name")
        schema_cls = entry_schema_for_name(name)
        if schema_cls is None:
            raise ValueError(
                f"No entry schema for name {name!r}. Expected a class in "
                "iws.direct_entries or a key in FUNCTION_SCHEMAS."
            )
        if source is not None and "source" in schema_cls.model_fields:
            data["source"] = source
        return schema_cls.model_validate(data)
    raise ValueError(
        "Entry config must include one of 'path', 'values', 'name', 'pipeline_id'."
    )


def validate_element(value):
    """Resolve and validate one pipeline element config to a schema instance.

    A dict is dispatched on ``element_type`` to the matching schema class and
    validated against it — including ``array_data_fit``, which round-trips
    through config just like ``data_fit``. An existing ``BaseSchema`` instance
    passes through untouched. A builtin scalar/collection (``None``, ``int``,
    ``str``, ``list``, ...) is never a valid element and is rejected, so a
    malformed element value can't slip past validation.
    """
    if isinstance(value, BaseSchema):
        return value
    if not isinstance(value, dict):
        if type(value).__module__ == "builtins":
            raise ValueError(
                f"Invalid pipeline element {value!r}: expected an element config "
                f"dict or a schema element instance; got {type(value).__name__}."
            )
        return value
    data = dict(value)
    element_type = data.pop("element_type", None)
    try:
        if element_type == "entry":
            return _validate_entry(data)
        if element_type == "calculation":
            # ``calculation`` is the legacy alias for the ``type`` discriminator;
            # pop both so a stale alias can't trip ``extra="forbid"``.
            type_name = data.pop("type", None) or data.pop("calculation", None)
            data.pop("calculation", None)
            return schema_class_for("calculation", type_name).model_validate(data)
        return schema_class_for(element_type).model_validate(data)
    except TypeError as exc:
        # A custom __init__ raises TypeError on an unknown field; surface it as
        # ValueError so the Pipeline gate wraps it into a ValidationError.
        raise ValueError(f"Invalid {element_type!r} element config: {exc}") from exc
