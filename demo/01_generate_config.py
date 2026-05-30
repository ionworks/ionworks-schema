"""
Generate a pipeline configuration using ionworks_schema.

This script uses ionworks_schema (pydantic schemas) to build a configuration
for half-cell OCP fitting. The output is a JSON file that can be submitted
to the Ionworks API for execution.

No execution logic is needed - ionworks_schema is a lightweight package.
"""

import json
from pathlib import Path

# ionworks_schema provides pydantic schemas for config generation
import ionworks_schema as iws

# ionworksdata is used for data loading
import ionworksdata as iwdata
import pandas as pd
import pybamm


def main():
    # =========================================================================
    # Step 1: Load data
    # =========================================================================
    data_dir = Path(__file__).parent / "data"
    df = pd.read_csv(data_dir / "cathode_ocp.csv")

    data = iwdata.OCPDataLoader(
        df,
        options={"sort": True, "remove_duplicates": True},
    )

    print("Loaded OCP data:")
    print(f"  Shape: {data.data.shape}")
    print(f"  Capacity: {data['Capacity [A.h]'].max():.3f} A.h")

    dUdQ_cutoff = data.calculate_dUdQ_cutoff()
    Q_max = data["Capacity [A.h]"].max()

    # =========================================================================
    # Step 2: Get material parameters from library
    # =========================================================================
    material = iws.Material.from_library("NMC - Verbrugge 2017")
    print(f"\nMaterial: {material.name}")

    # Build initial parameters
    msmr_init = dict(material.parameter_values)
    msmr_init.update(
        {
            "Number of reactions in positive electrode": len(
                material.parameter_values[
                    "Positive electrode host site occupancy fraction"
                ]
            ),
            "Positive electrode capacity [A.h]": Q_max,
            "Positive electrode lower excess capacity [A.h]": 0.0,
            "Ambient temperature [K]": 298.15,
        }
    )
    msmr_init = pybamm.scalarize_dict(msmr_init)

    # =========================================================================
    # Step 3: Define parameters to fit using pydantic schemas
    # =========================================================================
    params = {
        "Ambient temperature [K]": 298.15,
        "Number of reactions in positive electrode": msmr_init[
            "Number of reactions in positive electrode"
        ],
        "Positive electrode capacity [A.h]": iws.Parameter(
            name="Positive electrode capacity [A.h]",
            initial_value=Q_max,
            bounds=(0.98 * Q_max, 1.2 * Q_max),
        ),
        "Positive electrode lower excess capacity [A.h]": iws.Parameter(
            name="Positive electrode lower excess capacity [A.h]",
            initial_value=0.01 * Q_max,
            bounds=(0, 0.05 * Q_max),
        ),
    }

    # Add species parameters
    for k, v in msmr_init.items():
        if "occupancy fraction" in k:
            params[k] = iws.Parameter(name=k, initial_value=v, bounds=(0.01, 0.99))
        elif "standard potential" in k:
            params[k] = iws.Parameter(
                name=k,
                initial_value=v,
                bounds=(max(3.0, v - 0.5), min(5.0, v + 0.5)),
            )
        elif "ideality factor" in k:
            params[k] = iws.Parameter(name=k, initial_value=v, bounds=(0.1, 20.0))

    n_fit = len([p for p in params.values() if isinstance(p, iws.Parameter)])
    print(f"\nParameters to fit: {n_fit}")

    # =========================================================================
    # Step 4: Build pipeline using schemas
    # =========================================================================
    objective = iws.objectives.MSMRHalfCell(
        data_input=data.to_config(),  # Serialize data to config format
        options={
            "dUdQ cutoff": dUdQ_cutoff,
            "model": {
                "type": "MSMRHalfCellModel",
                "electrode": "positive",
                "options": {"species format": "Xj"},
            },
        },
    )

    data_fit = iws.DataFit(
        objectives={"ocp": objective},
        parameters=params,
        multistarts=50,
    )

    pipeline = iws.Pipeline(elements={"cathode_ocp_fit": data_fit})

    # =========================================================================
    # Step 5: Export to JSON
    # =========================================================================
    config = pipeline.to_config()

    output_file = Path(__file__).parent / "config.json"
    with open(output_file, "w") as f:
        json.dump(config, f, indent=2, default=str)

    print(f"\nConfiguration saved: {output_file}")
    print("\nPreview:")
    preview = json.dumps(config, indent=2, default=str)[:1500]
    print(preview + "\n...")


if __name__ == "__main__":
    main()
