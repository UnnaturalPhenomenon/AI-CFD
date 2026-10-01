"""Utilities for loading Fluent mesh files."""

from pathlib import Path
from typing import Any


def load_mesh(session: Any, mesh_path: str | Path) -> Path:
    """Load a Fluent mesh into an existing solver session."""

    path = Path(mesh_path).expanduser().resolve()

    if not path.is_file():
        raise FileNotFoundError(f"Mesh file not found: {path}")

    lower_name = path.name.lower()

    if not (
        lower_name.endswith(".msh")
        or lower_name.endswith(".msh.h5")
    ):
        raise ValueError(
            f"Unsupported mesh format: {path.name}"
        )

    print(f"[MESH] loading: {path}")

    session.settings.file.read_mesh(
        file_name=str(path)
    )

    print("[MESH] loaded")

    return path