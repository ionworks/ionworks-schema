"""The bundled example data behind ``iws.example_data``."""

import ionworks_schema as iws
import pandas as pd
import pytest

# Literal, not globbed: an empty parametrize is a pytest skip, not a failure,
# so globbing would evaporate this guard exactly when the data goes missing.
DATASETS = [
    "current_driven_discharge",
    "cycle_ageing_summary",
    "eis_synthetic",
    "msmr_half_cell_ocp",
]


def test_list_example_data_names_every_bundled_csv():
    assert iws.list_example_data() == DATASETS


def test_example_data_returns_a_readable_csv():
    path = iws.example_data("eis_synthetic")
    assert path.is_file()
    frame = pd.read_csv(path)
    assert list(frame.columns) == ["Frequency [Hz]", "Z_Re [Ohm]", "Z_Im [Ohm]"]


@pytest.mark.parametrize("name", DATASETS)
def test_every_named_dataset_loads(name):
    assert not pd.read_csv(iws.example_data(name)).empty


def test_example_data_unknown_name_lists_the_options():
    with pytest.raises(KeyError, match="eis_synthetic"):
        iws.example_data("not-a-dataset")
