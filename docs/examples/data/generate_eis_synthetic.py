"""Regenerate ``eis_synthetic.csv``, the spectrum ``eis.py`` fits.

Run from the repository root::

    uv run python packages/ionworks-schema/docs/examples/data/generate_eis_synthetic.py

Ten points per decade: a Nyquist arc read by eye needs enough points to show the
high-frequency semicircle as a curve rather than a polygon.

This ships in the source distribution and uses only ``ionworks-schema``
dependencies and PyBaMM, so anyone can regenerate the bundled data.
"""

from common import chen2020_with_reference_j0, example_data_path
import numpy as np
import pandas as pd
import pybamm

#: The value the example's fit should recover.
TRUE_J0 = 3.0
OUT = example_data_path("eis_synthetic.csv")


def main() -> None:
    """Simulate the spectrum the example fits, at a known ``TRUE_J0``."""
    model = pybamm.lithium_ion.DFN(options={"surface form": "differential"})
    frequencies = np.logspace(-2, 3, 51)
    sim = pybamm.EISSimulation(
        model, parameter_values=chen2020_with_reference_j0(TRUE_J0)
    )
    impedance = np.asarray(sim.solve(frequencies).impedance)
    pd.DataFrame(
        {
            "Frequency [Hz]": frequencies,
            "Z_Re [Ohm]": impedance.real,
            "Z_Im [Ohm]": impedance.imag,
        }
    ).to_csv(OUT, index=False)
    print(f"wrote {len(frequencies)} frequencies to {OUT}")


if __name__ == "__main__":
    main()
