"""Fit MSMR half-cell open-circuit potential parameters from graphite
half-cell data.

Builds the fit with ionworks-schema, submits it through the API client, and
plots the model-vs-data overlay from the typed result.

This fits one direction. For lithiation/delithiation hysteresis, set
``direction`` on :class:`~ionworks_schema.models.MSMRHalfCellModelOptions` and
give each direction its own objective.
"""

from pathlib import Path

from _data import save_first_fig

_PLOT = Path(__file__).resolve().parents[1] / "source/api/examples/_static/msmr_ocp.png"


def main():
    # --8<-- [start:example]
    from ionworks import Ionworks
    import ionworks_schema as iws
    import matplotlib.pyplot as plt
    import pandas as pd
    import pybamm

    # Synthetic example half-cell OCP: cumulative Capacity [A.h], falling Voltage [V].
    # Swap in your own export, or read a measurement with `client.cell_measurement`.
    data = pd.read_csv(iws.example_data("msmr_half_cell_ocp"))

    known = iws.direct_entries.DirectEntry(
        parameters={"Ambient temperature [K]": 298.15},
    )

    # Seed the species from the library material closest to your chemistry.
    material = iws.Material.from_library("Graphite - Verbrugge 2017")

    # The library holds one value per species; scalarize_dict expands each list
    # into the indexed names the model uses, e.g. "... (0) [V]".
    initial_values = pybamm.scalarize_dict(
        {k: v for k, v in material.parameter_values.items() if "host site" in k}
    )

    # Seed capacity and lower excess capacity from the observed window.
    Q_data = float(data["Capacity [A.h]"].max() - data["Capacity [A.h]"].min())
    initial_values["Negative electrode capacity [A.h]"] = Q_data
    initial_values["Negative electrode lower excess capacity [A.h]"] = 0.01 * Q_data

    def bounds_function(var, initial_value):
        if "host site occupancy fraction" in var:
            # allow +/- 0.1 of the initial value, staying a fraction
            return (max(0.0, initial_value - 0.1), min(1.0, initial_value + 0.1))
        elif "ideality factor" in var:
            return (1e-2, 100.0)
        elif "standard potential" in var:
            # allow +/- 200 mV of the initial value
            return (initial_value - 0.2, initial_value + 0.2)
        elif "capacity" in var:
            # allow +/- 2% of the initial value
            return (initial_value * 0.98, initial_value * 1.02)
        else:
            raise ValueError(f"No bounds defined for parameter: {var}")

    def prior_function(var, initial_value):
        if "standard potential" in var:
            return iws.stats.Normal(mean=initial_value, std=0.01)
        else:
            return None

    parameters = {}
    for name, value in initial_values.items():
        parameter = iws.Parameter(
            name,
            initial_value=value,
            bounds=bounds_function(name, value),
            prior=prior_function(name, value),
        )
        # Log10 the ideality factor since it may span several orders of magnitude.
        if "ideality factor" in name:
            parameters[name] = iws.transforms.Log10(parameter)
        else:
            parameters[name] = parameter

    objectives = {
        "msmr": iws.objectives.MSMRHalfCell(
            data=data,
            options=iws.objectives.MSMRHalfCellOptions(
                model=iws.models.MSMRHalfCellModel(
                    electrode="negative", options={"species format": "Xj"}
                )
            ),
        )
    }
    fit = iws.DataFit(
        objectives=objectives,
        parameters=parameters,
        # No cost: MSMRHalfCell's default weights capacity against the
        # differentials. ScipyLeastSquares is its default too, capped for speed.
        optimizer=iws.optimizers.ScipyLeastSquares(max_nfev=50),
    )

    client = Ionworks()
    submission = client.pipeline.create(iws.Pipeline({"known": known, "msmr": fit}))
    client.pipeline.wait_for_completion(submission.id)
    result = client.pipeline.result(submission.id)
    fit_result = result.element("msmr")
    figs = fit_result.plot_fit_results()
    plt.show()
    # --8<-- [end:example]
    save_first_fig(figs, _PLOT)
    return fit_result


if __name__ == "__main__":
    main()
