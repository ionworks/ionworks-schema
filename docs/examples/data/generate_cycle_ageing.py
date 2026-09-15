"""Regenerate ``cycle_ageing_summary.csv``, the LLI summary ``cycle_ageing.py`` fits.

Run from the repository root::

    uv run python packages/ionworks-schema/docs/examples/data/generate_cycle_ageing.py

One row per RPT, so the cycle numbers here are the cycle numbers the example's
experiment reports an LLI at.

This ships in the source distribution and uses only ``ionworks-schema``
dependencies and PyBaMM, so anyone can regenerate the bundled data.
"""

from common import example_data_path
import pandas as pd
import pybamm

#: The value the example's fit should recover.
TRUE_DIFFUSIVITY = 2e-19
FITTED = "SEI solvent diffusivity [m2.s-1]"
RPT_CYCLES = [0, 4, 8]
OUT = example_data_path("cycle_ageing_summary.csv")


def experiment() -> pybamm.Experiment:
    """Return the explicit PyBaMM experiment that the example fits."""
    rpt = (
        pybamm.step.c_rate(0.2, termination="2.5 V", period=60),
        pybamm.step.rest("10 minutes"),
    )
    cc_cycle = (
        pybamm.step.c_rate(1.0, termination="2.5 V"),
        pybamm.step.c_rate(-0.5, termination="4.2 V"),
    )
    return pybamm.Experiment([rpt] + ([cc_cycle] * 3 + [rpt]) * 2)


def main() -> None:
    """Simulate the LLI the example fits, at a known ``TRUE_DIFFUSIVITY``.

    ``CycleAgeing`` uses the first LLI value of each RPT. The first RPT starts
    at zero; later RPTs start at the final value of their preceding ageing cycle.
    """
    values = pybamm.ParameterValues("Chen2020")
    values.update({FITTED: TRUE_DIFFUSIVITY})
    solution = pybamm.Simulation(
        pybamm.lithium_ion.SPMe(options={"SEI": "solvent-diffusion limited"}),
        parameter_values=values,
        experiment=experiment(),
        # CycleAgeing uses PyBaMM's unified experiment model by default.
        experiment_model_mode="unified",
    ).solve(calc_esoh=False)
    lli_by_cycle = solution.summary_variables["Loss of lithium inventory [%]"]
    assert RPT_CYCLES[0] == 0, "the leading 0.0 assumes the first RPT precedes ageing"
    lli = [0.0] + [lli_by_cycle[cycle - 1] for cycle in RPT_CYCLES[1:]]
    pd.DataFrame(
        {"Cycle number": RPT_CYCLES, "LLI [%]": [round(value, 6) for value in lli]}
    ).to_csv(OUT, index=False)
    print(f"wrote {len(RPT_CYCLES)} RPTs to {OUT}")


if __name__ == "__main__":
    main()
