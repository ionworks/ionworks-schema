"""Shared type aliases for ``ionworks_schema`` field annotations.

``polars`` and ``ionworksdata`` are optional dependencies. When they
aren't installed we fall back to empty sentinel classes that nothing
will ever ``isinstance``-match, so the type aliases still resolve at
runtime (Pydantic needs a real class to validate against) but the
``isinstance`` checks for the optional types are harmless no-ops.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Any, Literal

import pandas as pd
import pybamm
from pydantic import BeforeValidator

from .data_loader import DataPayloadSpec, MetadataSpec, TimeSeriesSpec

if TYPE_CHECKING:
    from ionworksdata import DataLoader
    import polars as pl
else:
    try:
        import polars as pl  # type: ignore[no-redef]
    except ImportError:  # pragma: no cover

        class pl:  # type: ignore[no-redef]
            class DataFrame:
                pass

    try:
        from ionworksdata import DataLoader  # type: ignore[no-redef]
    except ImportError:  # pragma: no cover

        class DataLoader:  # type: ignore[no-redef]
            pass


#: Locator prefixes a string measurement must carry, saying where to read it from.
DATA_PREFIXES = ("file:", "folder:", "db:")


def _route_measurement_input(value: Any) -> Any:
    """Dispatch a dict payload to whichever named shape its keys identify.

    A plain column mapping is left alone: its keys are column names, so it
    cannot be validated against a closed set. ``time_series``, ``steps``,
    ``data``, ``options`` and ``metadata`` are therefore reserved — a column
    named one of these is read as a payload key.

    A string is checked for its locator prefix. The loader already requires one
    and rejects anything else, so this only moves that rejection to where the
    config is built.
    """
    if isinstance(value, str) and not value.startswith(DATA_PREFIXES):
        raise ValueError(
            f"A string measurement must start with one of "
            f"{', '.join(DATA_PREFIXES)} to say where to read it from; got "
            f"{value!r}. For a local file use 'file:{value}'."
        )
    if not isinstance(value, dict):
        return value
    keys = set(value)
    if "metadata" in keys and "data" in keys:
        return MetadataSpec.model_validate(value)
    if keys & {"time_series", "steps"}:
        return TimeSeriesSpec.model_validate(value)
    if keys & {"data", "options"}:
        return DataPayloadSpec.model_validate(value)
    return value


NumberLike = int | float
"""Scalar real number (excludes ``bool`` and ``complex``)."""

NamedFloatMap = dict[str, float]
"""Map of variable name to ``float``."""

Electrode = Literal["positive", "negative"]
"""Electrode side enum used by half-cell objectives and models."""

ElectrodeOrLumped = Literal["positive", "negative", "lumped"]
"""``Electrode`` widened with ``"lumped"`` for OCP calculations that
combine both half-cells into a single curve."""

MeasurementInput = Annotated[
    str
    | pd.DataFrame
    | pl.DataFrame
    | DataLoader
    | TimeSeriesSpec
    | DataPayloadSpec
    | MetadataSpec
    | dict[str, Any],
    BeforeValidator(_route_measurement_input),
]
"""Inputs accepted by data-driven objectives and calculations.

The parser dispatches on the runtime type:

- ``str``: a path-like spec (``"file:..."``, ``"folder:..."``, or
  ``"db:..."``).
- ``pandas.DataFrame`` / ``polars.DataFrame``: a tabular payload.
- ``ionworksdata.DataLoader``: pre-loaded experiment(s) with metadata.
- ``dict``: routed by its keys to one of three named shapes —
  :class:`~ionworks_schema.data_loader.TimeSeriesSpec` (``time_series``,
  optionally ``steps``), :class:`~ionworks_schema.data_loader.DataPayloadSpec`
  (``data``, optionally ``options``), or
  :class:`~ionworks_schema.data_loader.MetadataSpec` (``data`` and
  ``metadata``) — each validated strictly, so a misspelt key or option is
  rejected at construction. A dict matching none of these is left open as a
  plain column mapping (its keys are column names, so they cannot be
  restricted to a closed set). Consequently ``time_series``, ``steps``,
  ``data``, ``options`` and ``metadata`` are reserved keys: a column
  literally named one of these is read as a payload key instead, not as a
  column.
"""

ParameterValuesLike = dict[str, Any] | pybamm.ParameterValues
"""A raw ``{name: value}`` mapping or a ``pybamm.ParameterValues``."""
