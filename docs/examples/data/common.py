"""Public PyBaMM setup shared by the synthetic-data generators."""

from pathlib import Path

import pybamm

_EXAMPLE_DATA = (
    Path(__file__).resolve().parents[3] / "src/ionworks_schema/_example_data"
)


def example_data_path(name: str) -> Path:
    """Return the path in this checkout to write the dataset ``name`` to.

    Deliberately not ``iws.example_data``, which resolves inside the installed
    package: a generator has to rewrite the copy that ships.
    """
    return _EXAMPLE_DATA / name


def chen2020_with_reference_j0(reference_j0: float) -> pybamm.ParameterValues:
    """Return Chen2020 with the example's Arrhenius Butler-Volmer kinetics.

    The normalisation by ``c_e0`` and ``c_s_max`` mirrors the example's
    ``arrhenius_butler_volmer_exchange_current_density`` direct entry: the same
    ``reference_j0`` [A.m-2] against an unnormalised form is a different cell,
    so the generated data and the fit would drift apart with no error anywhere.
    """
    values = pybamm.ParameterValues("Chen2020")

    def j0(c_e, c_s_surf, c_s_max, temperature):
        return (
            pybamm.Parameter(
                "Negative electrode reference exchange-current density [A.m-2]"
            )
            * (c_e / pybamm.Parameter("Initial concentration in electrolyte [mol.m-3]"))
            ** 0.5
            * (c_s_surf / c_s_max) ** 0.5
            * (1 - c_s_surf / c_s_max) ** 0.5
            * pybamm.exp(
                pybamm.Parameter(
                    "Negative electrode reaction activation energy [J.mol-1]"
                )
                / pybamm.constants.R
                * (1 / pybamm.Parameter("Reference temperature [K]") - 1 / temperature)
            )
        )

    values.update(
        {"Negative electrode exchange-current density [A.m-2]": j0},
        check_already_exists=True,
    )
    values.update(
        {
            "Negative electrode reference exchange-current density [A.m-2]": reference_j0,
            "Negative electrode reaction activation energy [J.mol-1]": 0.0,
        },
        check_already_exists=False,
    )
    return values
