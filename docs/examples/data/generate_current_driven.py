"""Regenerate ``current_driven_discharge.csv``, the discharge ``current_driven.py`` fits.

Run from the repository root::

    uv run python packages/ionworks-schema/docs/examples/data/generate_current_driven.py

A single constant-current step, sampled every 60 s: the fit drives the model
with this recorded current, so a step change in it would land between samples.

This ships in the source distribution and uses only ``ionworks-schema``
dependencies and PyBaMM, so anyone can regenerate the bundled data.
"""

from common import chen2020_with_reference_j0, example_data_path
import pandas as pd
import pybamm

#: The value the example's fit should recover.
TRUE_J0 = 3.0
OUT = example_data_path("current_driven_discharge.csv")


def main() -> None:
    """Simulate the discharge the example fits, at a known ``TRUE_J0``."""
    experiment = pybamm.Experiment(
        [pybamm.step.c_rate(0.5, termination="2.5 V", period=60)]
    )
    sim = pybamm.Simulation(
        pybamm.lithium_ion.SPMe(),
        parameter_values=chen2020_with_reference_j0(TRUE_J0),
        experiment=experiment,
    )
    sol = sim.solve()
    frame = pd.DataFrame(
        {var: sol[var].data for var in ["Time [s]", "Current [A]", "Voltage [V]"]}
    )
    frame.to_csv(OUT, index=False)
    print(f"wrote {len(frame)} rows to {OUT}")


if __name__ == "__main__":
    main()
