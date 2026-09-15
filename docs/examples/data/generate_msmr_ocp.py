"""Regenerate ``msmr_half_cell_ocp.csv``, the OCP curve ``msmr_ocp.py`` fits.

Run from the repository root::

    uv run python packages/ionworks-schema/docs/examples/data/generate_msmr_ocp.py

The window reaches 1.2 V so the true capacity stays inside the 2% band the
example bounds it to; graphite's widest species has a long tail.

This ships in the source distribution and uses only ``ionworks-schema``
dependencies and PyBaMM, so anyone can regenerate the bundled data.
"""

from common import example_data_path
import ionworks_schema as iws
import numpy as np
import pandas as pd
import pybamm

# Offsets from the library seed the example starts at: generating at the seed
# itself would put the optimum on the initial guess.
TRUE_U0_SHIFT = -0.025
TRUE_W_SCALE = 1.05
TRUE_CAPACITY = 1.0
TRUE_LOWER_EXCESS = 0.01

ELECTRODE = "Negative"
HOST_SITE = f"{ELECTRODE} electrode host site"
VOLTAGE_LIMITS = (0.01, 1.2)
POINTS = 289
OUT = example_data_path("msmr_half_cell_ocp.csv")


def true_parameter_values() -> dict:
    """Return the library seed shifted to the values the fit must recover."""
    material = iws.Material.from_library("Graphite - Verbrugge 2017")
    species = {k: v for k, v in material.parameter_values.items() if "host site" in k}
    species[f"{HOST_SITE} standard potential [V]"] = [
        U0 + TRUE_U0_SHIFT for U0 in species[f"{HOST_SITE} standard potential [V]"]
    ]
    species[f"{HOST_SITE} ideality factor"] = [
        w * TRUE_W_SCALE for w in species[f"{HOST_SITE} ideality factor"]
    ]
    # The library's fractions sum to 0.999999, and the fit projects them onto
    # the simplex, so state the truth on the simplex the fit searches.
    occupancy = species[f"{HOST_SITE} occupancy fraction"]
    species[f"{HOST_SITE} occupancy fraction"] = [X / sum(occupancy) for X in occupancy]
    values = pybamm.scalarize_dict(species)
    values[f"{ELECTRODE} electrode capacity [A.h]"] = TRUE_CAPACITY
    values[f"{ELECTRODE} electrode lower excess capacity [A.h]"] = TRUE_LOWER_EXCESS
    values["Ambient temperature [K]"] = 298.15
    return values


def species_arrays(values: dict) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return the per-site standard potentials [V], ideality factors, and
    occupancy fractions, read back out of their indexed scalar names.
    """
    sites = range(
        sum(1 for key in values if key.startswith(f"{HOST_SITE} standard potential"))
    )
    return (
        np.array([values[f"{HOST_SITE} standard potential ({j}) [V]"] for j in sites]),
        np.array([values[f"{HOST_SITE} ideality factor ({j})"] for j in sites]),
        np.array([values[f"{HOST_SITE} occupancy fraction ({j})"] for j in sites]),
    )


def msmr_occupancy(
    voltage: np.ndarray,
    U0: np.ndarray,
    w: np.ndarray,
    x: np.ndarray,
    temperature: float,
) -> np.ndarray:
    """Sum the host-site occupancies at each voltage [V], at ``temperature`` [K].

    Each site's Fermi-Dirac term is written so the exponent is never positive,
    which the 0.01 V end of the window would otherwise overflow.
    """
    f = pybamm.constants.F.value / (pybamm.constants.R.value * temperature)
    occupancy = np.zeros_like(voltage)
    for u0, wj, xj in zip(U0, w, x / x.sum(), strict=True):
        inner = f * (voltage - u0) / wj
        z = np.exp(-np.abs(inner))
        occupancy += xj * ((inner >= 0) * z + (inner < 0)) / (1 + z)
    return occupancy


def main() -> None:
    """Evaluate the OCP curve the example fits, at the true parameters."""
    voltage = np.linspace(VOLTAGE_LIMITS[1], VOLTAGE_LIMITS[0], POINTS)
    values = true_parameter_values()
    U0, w, x = species_arrays(values)
    occupancy = msmr_occupancy(voltage, U0, w, x, values["Ambient temperature [K]"])
    capacity = (
        values[f"{ELECTRODE} electrode capacity [A.h]"] * occupancy
        - values[f"{ELECTRODE} electrode lower excess capacity [A.h]"]
    )
    pd.DataFrame({"Capacity [A.h]": capacity, "Voltage [V]": voltage}).to_csv(
        OUT, index=False
    )
    print(f"wrote {POINTS} points to {OUT}")


if __name__ == "__main__":
    main()
