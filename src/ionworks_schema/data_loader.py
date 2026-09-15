"""Schema for the options accepted when loading measurement data."""

from typing import Any

from pydantic import Field, model_validator

from .base import BaseSchema


class DataLoaderTransforms(BaseSchema):
    """Preprocessing steps applied to a measurement before a fit sees it.

    Each step may also be given at the top level of the options bag, which is the
    older spelling; both are merged before the transforms run.

    Parameters
    ----------
    gitt_to_ocp : bool, optional
        Reduce a GITT measurement to an OCP curve.
    rest_to_ocp : bool, optional
        Reduce rest periods to an OCP curve. Mutually exclusive with
        ``gitt_to_ocp``.
    sort : bool, optional
        Sort by the independent variable.
    remove_duplicates : bool, optional
        Drop duplicated rows.
    remove_extremes : bool, optional
        Drop the first and last points of an OCP curve.
    filters : dict, optional
        Column filters to apply, keyed by column name.
    interpolate : float or list of float, optional
        Resample onto this spacing or these points.
    keep_first_ocp_point : bool, optional
        Keep the first point when reducing to an OCP curve. Ignored unless
        ``gitt_to_ocp`` or ``rest_to_ocp`` is set.

    Examples
    --------
    >>> iws.DataLoaderTransforms(sort=True, remove_duplicates=True).to_config()
    {'sort': True, 'remove_duplicates': True}
    """

    # Merged into the caller's own transform dict, so no discriminator is wanted.
    _emit_type: bool = False

    gitt_to_ocp: bool | None = Field(
        default=None, description="Reduce a GITT measurement to an OCP curve."
    )
    rest_to_ocp: bool | None = Field(
        default=None,
        description=(
            "Reduce rest periods to an OCP curve. Mutually exclusive with gitt_to_ocp."
        ),
    )
    sort: bool | None = Field(
        default=None, description="Sort by the independent variable."
    )
    remove_duplicates: bool | None = Field(
        default=None, description="Drop duplicated rows."
    )
    remove_extremes: bool | None = Field(
        default=None, description="Drop the first and last points of an OCP curve."
    )
    filters: dict[str, Any] | None = Field(
        default=None, description="Column filters, keyed by column name."
    )
    interpolate: float | list[float] | None = Field(
        default=None, description="Resample onto this spacing or these points."
    )
    keep_first_ocp_point: bool | None = Field(
        default=None,
        description="Keep the first point when reducing to an OCP curve.",
    )


class DataLoaderOptions(BaseSchema):
    """Options controlling how measurement data is loaded and preprocessed.

    Selects a subset of the measurement and applies preprocessing transforms
    before a fit sees it. Every field is optional; unknown keys are rejected, so
    a misspelt option fails when you build the config rather than being silently
    ignored and changing your results.

    Parameters
    ----------
    transforms : dict, optional
        Preprocessing steps to apply, keyed by name — ``sort``,
        ``remove_duplicates``, ``remove_extremes``, ``gitt_to_ocp``,
        ``rest_to_ocp``, ``keep_first_ocp_point``, ``filters``, ``interpolate``.
        Each may also be given at the top level, which is the older spelling.
    first_step : int, str, or dict, optional
        Where to start the slice: a step index, a Polars SQL query against the
        steps table, or the deprecated dict form (``{"cycle": 3}``,
        ``{"step": 7}``).
    last_step : int, str, or dict, optional
        Where to end the slice, in the same form as ``first_step``.
    capacity_column : str, optional
        Name of the column to treat as capacity when the default is not present.
    first_step_dict : dict, optional
        Deprecated spelling of ``first_step``.
    last_step_dict : dict, optional
        Deprecated spelling of ``last_step``.
    gitt_to_ocp : bool, optional
        Reduce a GITT measurement to an OCP curve.
    rest_to_ocp : bool, optional
        Reduce rest periods to an OCP curve. Mutually exclusive with
        ``gitt_to_ocp``.
    sort : bool, optional
        Sort by the independent variable before use.
    remove_duplicates : bool, optional
        Drop duplicated rows.
    remove_extremes : bool, optional
        Drop the first and last points of an OCP curve.
    filters : dict, optional
        Column filters to apply, keyed by column name.
    interpolate : float or list of float, optional
        Resample onto this spacing or these points.
    keep_first_ocp_point : bool, optional
        Keep the first point when reducing to an OCP curve. Ignored unless
        ``gitt_to_ocp`` or ``rest_to_ocp`` is set.

    Examples
    --------
    >>> options = iws.DataLoaderOptions(first_step=2, transforms={"sort": True})
    >>> options.to_config()
    {'transforms': {'sort': True}, 'first_step': 2}
    """

    _emit_type: bool = False

    transforms: DataLoaderTransforms | None = Field(
        default=None, description="Preprocessing steps to apply, keyed by name."
    )
    first_step: int | str | dict[str, Any] | None = Field(
        default=None,
        description=("Where to start the slice: a step index, a SQL query, or a dict."),
    )
    last_step: int | str | dict[str, Any] | None = Field(
        default=None, description="Where to end the slice, as for first_step."
    )
    capacity_column: str | None = Field(
        default=None, description="Column to treat as capacity."
    )
    first_step_dict: int | str | dict[str, Any] | None = Field(
        default=None, description="Deprecated spelling of first_step."
    )
    last_step_dict: int | str | dict[str, Any] | None = Field(
        default=None, description="Deprecated spelling of last_step."
    )
    gitt_to_ocp: bool | None = Field(
        default=None, description="Reduce a GITT measurement to an OCP curve."
    )
    rest_to_ocp: bool | None = Field(
        default=None,
        description=(
            "Reduce rest periods to an OCP curve. Mutually exclusive with gitt_to_ocp."
        ),
    )
    sort: bool | None = Field(
        default=None, description="Sort by the independent variable."
    )
    remove_duplicates: bool | None = Field(
        default=None, description="Drop duplicated rows."
    )
    remove_extremes: bool | None = Field(
        default=None, description="Drop the first and last points of an OCP curve."
    )
    filters: dict[str, Any] | None = Field(
        default=None, description="Column filters, keyed by column name."
    )
    interpolate: float | list[float] | None = Field(
        default=None, description="Resample onto this spacing or these points."
    )
    keep_first_ocp_point: bool | None = Field(
        default=None,
        description="Keep the first point when reducing to an OCP curve.",
    )


class TimeSeriesSpec(BaseSchema):
    """A measurement given as its time-series table, optionally with steps.

    Parameters
    ----------
    time_series : Any
        The time-series table, as a DataFrame or a column mapping.
    steps : Any, optional
        The step table, in the same form.
    """

    # Consumer validates exact keys; must not emit "type" key.
    _emit_type: bool = False

    time_series: Any = Field(..., description="The time-series table.")
    steps: Any = Field(default=None, description="The step table.")


class TimeRangeSpec(BaseSchema):
    """A window of elapsed seconds restricting which samples a source yields.

    Bounds are ``Time [s]`` values — the measurement's own sample clock — not
    wall-clock datetimes. That keeps the window meaningful for a measurement
    with no recorded start, and independent of ``start_time``, which is
    editable metadata a pin must not silently re-anchor to.

    Parameters
    ----------
    start : float
        Inclusive lower bound, in seconds from the first sample.
    end : float
        Inclusive upper bound, in seconds. Must not precede *start*.
    """

    _emit_type: bool = False

    start: float = Field(
        ..., description="Inclusive lower bound, in seconds from the first sample."
    )
    end: float = Field(..., description="Inclusive upper bound, in seconds.")

    @model_validator(mode="after")
    def validate_ordering(self):
        """Reject a window that ends before it starts."""
        if self.end < self.start:
            raise ValueError(
                f"time_range end must be at or after start; got start={self.start} "
                f"and end={self.end}"
            )
        return self


class DataPayloadSpec(BaseSchema):
    """A measurement plus the options controlling how it is loaded.

    Parameters
    ----------
    data : Any
        The measurement itself — a path spec, a table, or a nested payload.
    options : DataLoaderOptions, optional
        How to slice and preprocess it. Unknown keys are rejected.
    time_range : TimeRangeSpec, optional
        Elapsed-seconds window pinning a ``db:`` source to the samples it held
        when the run was first pinned, so a re-run is unaffected by a later
        extend.
    """

    # A payload wrapper, not a union member; no consumer reads a type here.
    _emit_type: bool = False
    # This class *is* the "data" wrapper; a DataFrame in its own "data" field
    # must not also get the bare-DataFrame wrap (that would nest it twice).
    _wrap_bare_dataframe: bool = False

    data: Any = Field(..., description="The measurement itself.")
    options: DataLoaderOptions | None = Field(
        default=None, description="How to slice and preprocess the measurement."
    )
    time_range: TimeRangeSpec | None = Field(
        default=None,
        description="Elapsed-seconds window pinning a 'db:' source.",
    )


class MetadataSpec(BaseSchema):
    """A measurement carried alongside its provenance metadata.

    Parameters
    ----------
    data : Any
        The measurement itself.
    metadata : dict
        Provenance recorded when the measurement was loaded.
    """

    # A payload wrapper, not a union member; no consumer reads a type here.
    _emit_type: bool = False
    # This class *is* the "data" wrapper; a DataFrame in its own "data" field
    # must not also get the bare-DataFrame wrap (that would nest it twice).
    _wrap_bare_dataframe: bool = False

    data: Any = Field(..., description="The measurement itself.")
    metadata: dict[str, Any] = Field(..., description="Provenance metadata.")
