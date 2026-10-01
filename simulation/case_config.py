"""Load and validate simulation case configuration."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


class CaseConfigError(ValueError):
    """Raised when a case configuration is invalid."""


@dataclass(frozen=True)
class CaseConfig:
    """Minimal configuration required to prepare a Fluent case."""

    name: str
    config_path: Path
    mesh_path: Path


def _require_mapping(data: Any, key: str) -> dict:
    value = data.get(key)

    if not isinstance(value, dict):
        raise CaseConfigError(
            f"'{key}' section must exist and must be a mapping."
        )

    return value


def load_case_config(config_path: str | Path) -> CaseConfig:
    """Read a YAML case file and resolve its mesh path."""

    path = Path(config_path).expanduser().resolve()

    if not path.is_file():
        raise FileNotFoundError(f"Case config not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    if not isinstance(data, dict):
        raise CaseConfigError("Case config root must be a mapping.")

    case_section = _require_mapping(data, "case")
    mesh_section = _require_mapping(data, "mesh")

    name = case_section.get("name")
    mesh_file = mesh_section.get("file")

    if not isinstance(name, str) or not name.strip():
        raise CaseConfigError("'case.name' must be a non-empty string.")

    if not isinstance(mesh_file, str) or not mesh_file.strip():
        raise CaseConfigError("'mesh.file' must be a non-empty string.")

    mesh_path = (path.parent / mesh_file).resolve()

    if not mesh_path.is_file():
        raise FileNotFoundError(f"Mesh file not found: {mesh_path}")

    return CaseConfig(
        name=name.strip(),
        config_path=path,
        mesh_path=mesh_path,
    )