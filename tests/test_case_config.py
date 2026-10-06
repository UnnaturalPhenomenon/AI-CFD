"""Tests for simulation case configuration loading."""

"""Tests for simulation case configuration loading."""

from pathlib import Path

import pytest

from simulation.case_config import (
    CaseConfigError,
    load_case_config,
)


def _write_valid_config(
    config_file: Path,
    mesh_file: str = "mesh/test.msh",
    case_name: str = "test_case",
) -> None:
    """Write a minimal valid conduction case configuration."""

    config_file.write_text(
        f"""
case:
  name: {case_name}
  type: steady_conduction

mesh:
  file: {mesh_file}

domain:
  type: solid
  zone: surface_body

physics:
  energy: true

material:
  name: conduction_solid
  density: 1000.0
  specific_heat: 1000.0
  thermal_conductivity: 1.0

boundary_conditions:
  hot:
    zone: wall_hot
    type: temperature
    value: 400.0

  cold:
    zone: wall_cold
    type: temperature
    value: 300.0

  top:
    zone: wall_adiabatic_top
    type: heat_flux
    value: 0.0

  bottom:
    zone: wall_adiabatic_bottom
    type: heat_flux
    value: 0.0

solver:
    initialization: standard
    initial_temperature: 350.0
    max_iterations: 200
    residual_target: 1.0e-8
    
validation:
    type: linear_conduction
    axis: x
    start_coordinate: 0.0
    end_coordinate: 1.0
    start_boundary: hot
    end_boundary: cold
    tolerance: 0.1
""".strip(),
        encoding="utf-8",
    )

def test_loads_valid_case_config(
    tmp_path: Path,
) -> None:
    mesh_dir = tmp_path / "mesh"
    mesh_dir.mkdir()

    mesh_file = mesh_dir / "test.msh"
    mesh_file.write_text("", encoding="utf-8")

    config_file = tmp_path / "case.yaml"

    _write_valid_config(config_file)

    config = load_case_config(config_file)

    assert config.name == "test_case"
    assert config.case_type == "steady_conduction"

    assert config.config_path == config_file.resolve()
    assert config.mesh_path == mesh_file.resolve()

    assert config.domain.type == "solid"
    assert config.domain.zone == "surface_body"

    assert config.physics.energy is True

    assert config.material.name == "conduction_solid"
    assert config.material.thermal_conductivity == 1.0

    assert config.solver.initialization == "standard"
    assert config.solver.initial_temperature == 350.0
    assert config.solver.max_iterations == 200
    assert config.solver.residual_target == pytest.approx(1.0e-8)

    assert config.validation.type == "linear_conduction"
    assert config.validation.axis == "x"
    assert config.validation.start_coordinate == 0.0
    assert config.validation.end_coordinate == 1.0
    assert config.validation.start_boundary == "hot"
    assert config.validation.end_boundary == "cold"
    assert config.validation.tolerance == pytest.approx(0.1)

def test_rejects_missing_mesh(
    tmp_path: Path,
) -> None:
    config_file = tmp_path / "case.yaml"

    _write_valid_config(
        config_file,
        mesh_file="mesh/missing.msh",
    )

    with pytest.raises(
        FileNotFoundError,
        match="Mesh file not found",
    ):
        load_case_config(config_file)

def test_rejects_missing_case_name(
    tmp_path: Path,
) -> None:
    mesh_dir = tmp_path / "mesh"
    mesh_dir.mkdir()

    mesh_file = mesh_dir / "test.msh"
    mesh_file.write_text("", encoding="utf-8")

    config_file = tmp_path / "case.yaml"

    _write_valid_config(config_file)

    text = config_file.read_text(encoding="utf-8")
    text = text.replace(
        "name: test_case",
        "name: ''",
    )
    config_file.write_text(
        text,
        encoding="utf-8",
    )

    with pytest.raises(
        CaseConfigError,
        match="case.name",
    ):
        load_case_config(config_file)