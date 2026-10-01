"""Tests for Fluent mesh loading."""

from pathlib import Path

import pytest

from simulation.mesh_loader import load_mesh


class FakeFileSettings:
    def __init__(self) -> None:
        self.received_file_name = None

    def read_mesh(self, *, file_name: str) -> None:
        self.received_file_name = file_name


class FakeSettings:
    def __init__(self) -> None:
        self.file = FakeFileSettings()


class FakeSession:
    def __init__(self) -> None:
        self.settings = FakeSettings()


def test_load_mesh_calls_fluent_api(tmp_path: Path) -> None:
    mesh_file = tmp_path / "test.msh"
    mesh_file.write_text("", encoding="utf-8")

    session = FakeSession()

    returned_path = load_mesh(
        session=session,
        mesh_path=mesh_file,
    )

    assert returned_path == mesh_file.resolve()
    assert session.settings.file.received_file_name == str(
        mesh_file.resolve()
    )


def test_load_mesh_rejects_missing_file(tmp_path: Path) -> None:
    session = FakeSession()

    with pytest.raises(FileNotFoundError):
        load_mesh(
            session=session,
            mesh_path=tmp_path / "missing.msh",
        )


def test_load_mesh_rejects_unsupported_extension(
    tmp_path: Path,
) -> None:
    mesh_file = tmp_path / "test.txt"
    mesh_file.write_text("", encoding="utf-8")

    session = FakeSession()

    with pytest.raises(ValueError):
        load_mesh(
            session=session,
            mesh_path=mesh_file,
        )