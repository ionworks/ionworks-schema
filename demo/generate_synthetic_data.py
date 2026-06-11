"""Generate synthetic OCP data for the demo."""

from pathlib import Path

import numpy as np
import pandas as pd
import pybamm


def main():
    data_dir = Path(__file__).parent / "data"
    data_dir.mkdir(exist_ok=True)

    print("Generating synthetic OCP data...")

    # Use PyBaMM to generate realistic OCP curves
    model = pybamm.lithium_ion.SPM()
    parameter_values = pybamm.ParameterValues("Chen2020")

    # Cathode discharge (lithiation)
    experiment = pybamm.Experiment(["Discharge at C/20 until 2.5 V"])
    sim = pybamm.Simulation(
        model, parameter_values=parameter_values, experiment=experiment
    )
    sol = sim.solve()

    # Extract data
    capacity = sol["Discharge capacity [A.h]"].entries
    voltage = sol["Voltage [V]"].entries

    # Add small noise
    np.random.seed(42)
    voltage += np.random.normal(0, 0.002, len(voltage))

    # Save cathode data
    df = pd.DataFrame(
        {
            "Capacity [A.h]": capacity,
            "Voltage [V]": voltage,
        }
    )
    df.to_csv(data_dir / "cathode_ocp.csv", index=False)
    print(f"  Saved: {data_dir / 'cathode_ocp.csv'}")
    print(f"  Points: {len(df)}, Capacity: {capacity.max():.3f} A.h")


if __name__ == "__main__":
    main()
