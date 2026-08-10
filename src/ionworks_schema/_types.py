"""Shared type aliases for ``ionworks_schema`` field annotations.

``polars`` and ``ionworksdata`` are optional dependencies. When they
aren't installed we fall back to empty sentinel classes that nothing
will ever ``isinstance``-match, so the type aliases still resolve at
runtime (Pydantic needs a real class to validate against) but the
``isinstance`` checks for the optional types are harmless no-ops.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

import pandas as pd
import pybamm

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


NumberLike = int | float
"""Scalar real number (excludes ``bool`` and ``complex``)."""

NamedFloatMap = dict[str, float]
"""Map of variable name to ``float``."""

Electrode = Literal["positive", "negative"]
"""Electrode side enum used by half-cell objectives and models."""

ElectrodeOrLumped = Literal["positive", "negative", "lumped"]
"""``Electrode`` widened with ``"lumped"`` for OCP calculations that
combine both half-cells into a single curve."""

MeasurementInput = str | pd.DataFrame | pl.DataFrame | DataLoader | dict[str, Any]
"""Inputs accepted by data-driven objectives and calculations.

The parser dispatches on the runtime type:

- ``str``: a path-like spec (``"file:..."``, ``"folder:..."``, or
  ``"db:..."``).
- ``pandas.DataFrame`` / ``polars.DataFrame``: a tabular payload.
- ``ionworksdata.DataLoader``: pre-loaded experiment(s) with metadata.
- ``dict``: parser-recognised payload, e.g. ``{"time_series": ...}``
  or ``{"data": ..., "metadata": ...}``.
"""

ParameterValuesLike = dict[str, Any] | pybamm.ParameterValues
"""A raw ``{name: value}`` mapping or a ``pybamm.ParameterValues``."""
