"""Library schemas with embedded material data."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

_MATERIALS = {
    "Graphite (Coal derived) - Paul 2024": {
        "name": "Graphite (Coal derived) - Paul 2024",
        "description": "Thermodynamic parameters for coal-derived graphite from Abigail Paul et al 2024 J. Electrochem. Soc. 171 023501",
        "parameter values": {
            "Negative electrode host site standard potential [V]": [
                0.3954,
                0.1868,
                0.1191,
                0.1172,
                0.0846,
                0.0839,
            ],
            "Negative electrode host site occupancy fraction": [
                0.1271,
                0.1601,
                0.3016,
                0.1612,
                0.2179,
                0.0321,
            ],
            "Negative electrode host site ideality factor": [
                5.6791,
                1.0823,
                0.7244,
                0.1017,
                0.1482,
                0.052,
            ],
        },
    },
    "Graphite (Commercial) - Paul 2024": {
        "name": "Graphite (Commercial) - Paul 2024",
        "description": "Thermodynamic parameters for commercial graphite from Abigail Paul et al 2024 J. Electrochem. Soc. 171 023501",
        "parameter values": {
            "Negative electrode host site standard potential [V]": [
                0.3329,
                0.2098,
                0.1281,
                0.1263,
                0.0886,
                0.0888,
            ],
            "Negative electrode host site occupancy fraction": [
                0.0723,
                0.0846,
                0.3254,
                0.159,
                0.26,
                0.0987,
            ],
            "Negative electrode host site ideality factor": [
                3.9609,
                0.2425,
                0.6571,
                0.086,
                0.1598,
                0.0469,
            ],
        },
    },
    "Graphite - Verbrugge 2017": {
        "name": "Graphite - Verbrugge 2017",
        "description": "Thermodynamic parameters for LixC6 from Mark Verbrugge et al 2017 J.Electrochem.Soc. 164 E3243",
        "parameter values": {
            "Negative electrode host site standard potential [V]": [
                0.088,
                0.13,
                0.14,
                0.17,
                0.21,
                0.36,
            ],
            "Negative electrode host site occupancy fraction": [
                0.431294,
                0.240722,
                0.150451,
                0.055165,
                0.067202,
                0.055165,
            ],
            "Negative electrode host site ideality factor": [
                0.086,
                0.08,
                0.72,
                2.5,
                0.095,
                6.0,
            ],
        },
    },
    "LFP - Verbrugge 2017": {
        "name": "LFP - Verbrugge 2017",
        "description": "Thermodynamic parameters for LixFePO4 from Mark Verbrugge et al 2017 J.Electrochem.Soc. 164 E3243",
        "parameter values": {
            "Negative electrode host site standard potential [V]": [3.42977, 3.42977],
            "Negative electrode host site occupancy fraction": [0.82584, 0.17416],
            "Negative electrode host site ideality factor": [0.06098, 0.35868],
        },
    },
    "Manganese oxide - Verbrugge 2017": {
        "name": "Manganese oxide - Verbrugge 2017",
        "description": "Thermodynamic parameters for LixMn2O4 from Mark Verbrugge et al 2017 J.Electrochem.Soc. 164 E3243",
        "parameter values": {
            "Positive electrode host site standard potential [V]": [
                4.01326,
                4.14834,
                4.1445,
            ],
            "Positive electrode host site occupancy fraction": [
                0.55286,
                0.39411,
                0.05303,
            ],
            "Positive electrode host site ideality factor": [1.46502, 1.06156, 0.39293],
        },
    },
    "NMC - Verbrugge 2017": {
        "name": "NMC - Verbrugge 2017",
        "description": "Thermodynamic parameters for NMC622 from Mark Verbrugge et al 2017 J.Electrochem.Soc. 164 E3243",
        "parameter values": {
            "Positive electrode host site standard potential [V]": [3.6, 3.7, 3.9, 4.2],
            "Positive electrode host site occupancy fraction": [
                0.131313,
                0.323232,
                0.212121,
                0.333333,
            ],
            "Positive electrode host site ideality factor": [1, 1.4, 3.5, 5.5],
        },
    },
    "Silicon (delithiation) - Verbrugge 2017": {
        "name": "Silicon (delithiation) - Verbrugge 2017",
        "description": "Thermodynamic parameters for Delithiation of LixSi4.4 from Mark Verbrugge et al 2017 J.Electrochem.Soc. 164 E3243",
        "parameter values": {
            "Negative electrode host site standard potential [V]": [
                0.2807,
                0.47931,
                0.45049,
                0.71796,
            ],
            "Negative electrode host site occupancy fraction": [
                0.286,
                0.059,
                0.452,
                0.203,
            ],
            "Negative electrode host site ideality factor": [
                1.11628,
                0.88258,
                3.07196,
                4.27128,
            ],
        },
    },
    "Silicon (lithiation) - Verbrugge 2017": {
        "name": "Silicon (lithiation) - Verbrugge 2017",
        "description": "Thermodynamic parameters for Lithiation of LixSi4.4 from Mark Verbrugge et al 2017 J.Electrochem.Soc. 164 E3243",
        "parameter values": {
            "Negative electrode host site standard potential [V]": [
                0.08216,
                0.2329,
                0.12606,
                0.42638,
            ],
            "Negative electrode host site occupancy fraction": [
                0.21834,
                0.23264,
                0.42492,
                0.1241,
            ],
            "Negative electrode host site ideality factor": [
                0.70934,
                0.9597,
                3.02803,
                4.68406,
            ],
        },
    },
}


class Material(BaseModel):
    """Material configuration."""

    model_config = ConfigDict(extra="allow")

    name: str = Field(...)
    description: str | None = Field(default=None)
    parameter_values: dict[str, Any] = Field(default_factory=dict)

    def __init__(
        self,
        name: str,
        description: str | None = None,
        parameter_values: dict[str, Any] | None = None,
        **kwargs,
    ):
        super().__init__(
            name=name,
            description=description,
            parameter_values=parameter_values or {},
            **kwargs,
        )

    @classmethod
    def from_library(cls, name: str) -> "Material":
        if name not in _MATERIALS:
            raise KeyError(f"Unknown material: {name}")
        data = _MATERIALS[name]
        return cls(
            name=data["name"],
            description=data["description"],
            parameter_values=dict(data["parameter values"]),
        )


class Library(BaseModel):
    """Material library access."""

    @staticmethod
    def list_materials() -> list[str]:
        return list(_MATERIALS.keys())

    @staticmethod
    def get_material(name: str) -> Material:
        return Material.from_library(name)


__all__ = ["Material", "Library"]
