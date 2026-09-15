"""Fit an exchange-current density from constant-current discharge data.

Builds the fit with ionworks-schema, submits it through the API client, and
plots the model-vs-data overlay from the typed result.
"""

from pathlib import Path

from _data import save_first_fig

_PLOT = (
    Path(__file__).resolve().parents[1]
    / "source/api/examples/_static/current_driven.png"
)


def main():
    # --8<-- [start:example]
    from ionworks import Ionworks
    import ionworks_schema as iws
    import matplotlib.pyplot as plt
    import pandas as pd
    import pybamm

    # Synthetic example discharge data (Time [s], Current [A], Voltage [V]) per C-rate.
    # Swap in your own export, or read a measurement with `client.cell_measurement`.
    data = {"0.5 C": pd.read_csv(iws.example_data("current_driven_discharge"))}

    # The Arrhenius form below needs an activation energy, which Chen2020
    # does not define; zero gives j0 no temperature dependence.
    baseline = pybamm.ParameterValues("Chen2020")
    baseline["Negative electrode reaction activation energy [J.mol-1]"] = 0.0
    known = iws.direct_entries.DirectEntry(parameters=baseline)

    # j0 = j0_ref (c_e/c_e0)^0.5 (c_s/c_smax)^0.5 (1 - c_s/c_smax)^0.5
    #      exp(E_r/R (1/T_ref - 1/T)), replacing Chen2020's own j0 function.
    j0_function = iws.direct_entries.arrhenius_butler_volmer_exchange_current_density(
        electrode="negative"
    )

    # We fit j0_ref.
    parameters = {
        "Negative electrode reference exchange-current density [A.m-2]": iws.Parameter(
            "Negative electrode reference exchange-current density [A.m-2]",
            initial_value=1.0,
            bounds=(0.1, 10.0),
        ),
    }

    fit = iws.DataFit(
        objectives={
            rate: iws.objectives.CurrentDriven(
                data=df,
                options=iws.objectives.CurrentDrivenOptions(
                    model=pybamm.lithium_ion.SPMe()
                ),
            )
            for rate, df in data.items()
        },
        parameters=parameters,
        cost=iws.costs.RMSE(),
        # Capped to keep the example quick; a harder fit needs more.
        optimizer=iws.optimizers.ScipyMinimize(method="Nelder-Mead", max_iterations=20),
    )

    client = Ionworks()
    submission = client.pipeline.create(
        iws.Pipeline({"known": known, "j0_function": j0_function, "fit": fit})
    )
    client.pipeline.wait_for_completion(submission.id)
    result = client.pipeline.result(submission.id)
    fit_result = result.element("fit")
    figs = fit_result.plot_fit_results()
    plt.show()
    # --8<-- [end:example]
    save_first_fig(figs, _PLOT)
    return fit_result


if __name__ == "__main__":
    main()
