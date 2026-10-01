"""Tests for simulation case configuration loading."""

from pathlib import Path

import pytest

from simulation.case_config import CaseConfigError, load_case_config


def test_loads_valid_case_config(tmp_path: Path) -> None:
    mesh_dir = tmp_path / "mesh"
    mesh_dir.mkdir()

    mesh_file = mesh_dir / "test.msh"
    mesh_file.write_text("", encoding="utf-8")

    config_file = tmp_path / "case.yaml"
    config_file.write_text(
        """
case:
  name: test_case

mesh:
  file: mesh/test.msh
""".strip(),
        encoding="utf-8",
    )

    config = load_case_config(config_file)

    assert config.name == "test_case"
    assert config.config_path == config_file.resolve()
    assert config.mesh_path == mesh_file.resolve()


def test_rejects_missing_mesh(tmp_path: Path) -> None:
    config_file = tmp_path / "case.yaml"
    config_file.write_text(
        """
case:
  name: test_case

mesh:
  file: mesh/missing.msh
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(FileNotFoundError):
        load_case_config(config_file)


def test_rejects_missing_case_name(tmp_path: Path) -> None:
    mesh_file = tmp_path / "test.msh"
    mesh_file.write_text("", encoding="utf-8")

    config_file = tmp_path / "case.yaml"
    config_file.write_text(
        """
case: {}

mesh:
  file: test.msh
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(CaseConfigError):
        load_case_config(config_file)