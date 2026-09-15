"""Small example datasets bundled for the documentation's worked examples.

These exist so a worked example can be copied out of the docs and run as-is,
with no download and no network. They are **synthetic sample data for
illustration**, not reference measurements — every example that uses one says
so, and a reader is expected to substitute their own export.
"""

from pathlib import Path

_DATA_DIR = Path(__file__).resolve().parent / "_example_data"


def list_example_data() -> list[str]:
    """Return the names of the bundled example datasets.

    Returns
    -------
    list[str]
        Dataset names, sorted, each accepted by :func:`example_data`.
    """
    return sorted(path.stem for path in _DATA_DIR.glob("*.csv"))


def example_data(name: str) -> Path:
    """Return the path to a bundled example dataset.

    The datasets back the worked examples in the documentation. They are
    synthetic sample data for illustration — substitute your own export, or
    read a measurement from the platform with ``client.cell_measurement``.

    Parameters
    ----------
    name : str
        Dataset name without the ``.csv`` suffix, as returned by
        :func:`list_example_data`.

    Returns
    -------
    pathlib.Path
        Absolute path to the CSV inside the installed package, ready to pass
        to ``pandas.read_csv``.

    Raises
    ------
    KeyError
        If no bundled dataset is registered under ``name``.

    Examples
    --------
    >>> import pandas as pd, ionworks_schema as iws
    >>> data = pd.read_csv(iws.example_data("eis_synthetic"))
    """
    path = _DATA_DIR / f"{name}.csv"
    if not path.is_file():
        raise KeyError(
            f"Unknown example dataset: {name}. "
            f"Available: {', '.join(list_example_data())}"
        )
    return path
