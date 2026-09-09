"""Tests for ``SimulationSettings`` and the model ``simulation_settings`` field."""

import json

import ionworks_schema as iws
from ionworks_schema.models import SimulationSettings
import pybamm
import pytest


class TestSimulationSettingsToConfig:
    def test_empty_is_empty(self):
        assert SimulationSettings().to_config() == {}

    def test_no_type_discriminator(self):
        # Persisted blocks are plain nested dicts, not typed schema payloads.
        assert "type" not in SimulationSettings(var_pts={"r_n": 8}).to_config()

    def test_var_pts_plain_dict(self):
        cfg = SimulationSettings(var_pts={"r_n": 16, "r_p": 16}).to_config()
        assert cfg == {"var_pts": {"r_n": 16, "r_p": 16}}

    def test_live_meshgenerator_serialized_flat(self):
        cfg = SimulationSettings(
            submesh_types={
                "negative particle": pybamm.MeshGenerator(
                    pybamm.Exponential1DSubMesh, {"side": "right"}
                )
            }
        ).to_config()
        item = cfg["submesh_types"]["negative particle"]
        assert item["$type"] == "type"
        assert item["class"].endswith("Exponential1DSubMesh")
        assert item["submesh_params"] == {"side": "right"}
        json.dumps(cfg)  # must be jsonb / worker-transport safe

    def test_live_solver_serialized(self):
        cfg = SimulationSettings(solver=pybamm.IDAKLUSolver()).to_config()
        assert cfg["solver"]["type"] == "IDAKLUSolver"
        json.dumps(cfg)

    def test_mesh_and_solver_flat_together(self):
        cfg = SimulationSettings(
            var_pts={"r_n": 16},
            solver={"type": "IDAKLUSolver", "atol": 1e-6},
        ).to_config()
        # Flat bag: solver sits alongside var_pts, not nested under a mesh key.
        assert set(cfg) == {"var_pts", "solver"}

    def test_prebuilt_dict_passthrough(self):
        block = {
            "var_pts": {"r_n": 8},
            "submesh_types": {
                "negative particle": {
                    "$type": "type",
                    "class": "pybamm.meshes.one_dimensional_submeshes.Uniform1DSubMesh",
                    "submesh_params": {},
                }
            },
            "solver": {"type": "CasadiSolver"},
        }
        assert SimulationSettings(**block).to_config() == block


class TestModelSimulationSettingsField:
    def test_typed_wrapper_on_model(self):
        s = SimulationSettings(var_pts={"r_n": 16}, solver={"type": "IDAKLUSolver"})
        cfg = iws.models.GITTModel(simulation_settings=s).to_config()
        assert cfg["type"] == "GITTModel"
        assert cfg["simulation_settings"] == {
            "var_pts": {"r_n": 16},
            "solver": {"type": "IDAKLUSolver"},
        }

    def test_raw_dict_on_model(self):
        cfg = iws.models.LumpedSPMR(
            simulation_settings={"var_pts": {"r_n": 8}}
        ).to_config()
        assert cfg["simulation_settings"] == {"var_pts": {"r_n": 8}}

    def test_absent_when_none(self):
        for cls in (
            iws.models.ECM,
            iws.models.LumpedSPMR,
            iws.models.LumpedSPMeR,
            iws.models.SingleElectrodeLumpedSPMR,
            iws.models.GITTModel,
        ):
            assert "simulation_settings" not in cls().to_config()

    def test_msmr_full_cell_carries_settings(self):
        half = iws.models.MSMRHalfCellModel(electrode="positive")
        cfg = iws.models.MSMRFullCellModel(
            negative_electrode_model=half,
            positive_electrode_model=half,
            simulation_settings={"var_pts": {"r_n": 20, "r_p": 20}},
        ).to_config()
        assert cfg["simulation_settings"] == {"var_pts": {"r_n": 20, "r_p": 20}}

    def test_msmr_half_cell_carries_settings(self):
        cfg = iws.models.MSMRHalfCellModel(
            electrode="negative", simulation_settings={"var_pts": {"r_n": 12}}
        ).to_config()
        assert cfg["simulation_settings"] == {"var_pts": {"r_n": 12}}

    def test_unknown_field_still_rejected(self):
        with pytest.raises(Exception):
            iws.models.GITTModel(nonsense=1)
