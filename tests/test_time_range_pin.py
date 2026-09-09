"""``time_range`` pins on a measurement payload.

An extend mutates the live series, so a ``db:`` ref names whatever the
measurement holds now. A pin fixes the window a run reads, which only works if
the pin survives validation everywhere a payload is accepted — the objective's
``data_input`` included.
"""

from ionworks_schema._types import _route_measurement_input as route
from ionworks_schema.data_loader import DataPayloadSpec
import pytest

SPAN = {"start": 0.0, "end": 20.0}


def test_a_pinned_payload_is_accepted():
    """`data_input` is strict, so an undeclared pin fails the whole pipeline."""
    spec = route({"data": "db:m-1", "options": {}, "time_range": SPAN})

    assert isinstance(spec, DataPayloadSpec)
    assert spec.time_range is not None
    assert spec.time_range.start == 0.0
    assert spec.time_range.end == 20.0


def test_an_unpinned_payload_keeps_working():
    assert route({"data": "db:m-1", "options": {}}).time_range is None


def test_an_inverted_window_is_rejected():
    with pytest.raises(ValueError, match="at or after start"):
        DataPayloadSpec(
            data="db:m-1", time_range={"start": SPAN["end"], "end": SPAN["start"]}
        )


def test_an_unknown_key_in_the_window_is_rejected():
    """Catches a typo'd bound, which would otherwise pin nothing silently."""
    with pytest.raises(ValueError):
        DataPayloadSpec(data="db:m-1", time_range={**SPAN, "strat": "x"})


def test_a_column_named_time_range_is_still_reserved():
    """Documented tradeoff: payload keys win over column names."""
    frame = {"Time [s]": [0.0, 1.0], "Voltage [V]": [4.2, 4.1]}

    assert route(frame) == frame
