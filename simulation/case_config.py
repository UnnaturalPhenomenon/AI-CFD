"""Load and validate simulation case configuration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


class CaseConfigError(ValueError):
    """Raised when a case configuration is invalid."""


@dataclass(frozen=True)
class DomainConfig:
    type: str
    zone: str


@dataclass(frozen=True)
class PhysicsConfig:
    energy: bool


@dataclass(frozen=True)
class MaterialConfig:
    name: str
    density: float
    specific_heat: float
    thermal_conductivity: float


@dataclass(frozen=True)
class BoundaryConditionConfig:
    name: str
    zone: str
    type: str
    value: float


@dataclass(frozen=True)
class SolverConfig:
    initialization: str
    initial_temperature: float
    max_iterations: int
    residual_target: float


@dataclass(frozen=True)
class CaseConfig:
    name: str
    case_type: str
    config_path: Path
    mesh_path: Path

    domain: DomainConfig
    physics: PhysicsConfig
    material: MaterialConfig
    boundary_conditions: tuple[BoundaryConditionConfig, ...]
    solver: SolverConfig


def _require_mapping(data: dict[str, Any], key: str) -> dict[str, Any]:
    value = data.get(key)

    if not isinstance(value, dict):
        raise CaseConfigError(
            f"'{key}' section must exist and must be a mapping."
        )

    return value


def _require_string(
    data: dict[str, Any],
    key: str,
    section: str,
) -> str:
    value = data.get(key)

    if not isinstance(value, str) or not value.strip():
        raise CaseConfigError(
            f"'{section}.{key}' must be a non-empty string."
        )

    return value.strip()


def _require_number(
    data: dict[str, Any],
    key: str,
    section: str,
) -> float:
    value = data.get(key)

    if not isinstance(value, (int, float)):
        raise CaseConfigError(
            f"'{section}.{key}' must be a number."
        )

    return float(value)


def load_case_config(config_path: str | Path) -> CaseConfig:
    """Read and validate a YAML simulation case."""

    path = Path(config_path).expanduser().resolve()

    if not path.is_file():
        raise FileNotFoundError(
            f"Case config not found: {path}"
        )

    with path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    if not isinstance(data, dict):
        raise CaseConfigError(
            "Case config root must be a mapping."
        )

    case_section = _require_mapping(data, "case")
    mesh_section = _require_mapping(data, "mesh")
    domain_section = _require_mapping(data, "domain")
    physics_section = _require_mapping(data, "physics")
    material_section = _require_mapping(data, "material")
    bc_section = _require_mapping(
        data,
        "boundary_conditions",
    )
    solver_section = _require_mapping(data, "solver")

    initialization = _require_string(solver_section,"initialization","solver",)
    
    if initialization != "standard":
        raise CaseConfigError(
            "Only 'standard' initialization "
            "is supported in this version."
        )
    
    initial_temperature = _require_number(
        solver_section,
        "initial_temperature",
        "solver",
    )
    
    if initial_temperature <= 0:
        raise CaseConfigError(
            "'solver.initial_temperature' "
            "must be greater than 0 K."
        )
    name = _require_string(
        case_section,
        "name",
        "case",
    )

    case_type = _require_string(
        case_section,
        "type",
        "case",
    )

    if case_type != "steady_conduction":
        raise CaseConfigError(
            "Only 'steady_conduction' is supported "
            "in this version."
        )

    mesh_file = _require_string(
        mesh_section,
        "file",
        "mesh",
    )

    mesh_path = (path.parent / mesh_file).resolve()

    if not mesh_path.is_file():
        raise FileNotFoundError(
            f"Mesh file not found: {mesh_path}"
        )

    domain_type = _require_string(
        domain_section,
        "type",
        "domain",
    )

    if domain_type != "solid":
        raise CaseConfigError(
            "Only solid domains are supported "
            "in this conduction reference case."
        )

    domain = DomainConfig(
        type=domain_type,
        zone=_require_string(
            domain_section,
            "zone",
            "domain",
        ),
    )

    energy = physics_section.get("energy")

    if not isinstance(energy, bool):
        raise CaseConfigError(
            "'physics.energy' must be true or false."
        )

    physics = PhysicsConfig(
        energy=energy,
    )

    material = MaterialConfig(
        name=_require_string(
            material_section,
            "name",
            "material",
        ),
        density=_require_number(
            material_section,
            "density",
            "material",
        ),
        specific_heat=_require_number(
            material_section,
            "specific_heat",
            "material",
        ),
        thermal_conductivity=_require_number(
            material_section,
            "thermal_conductivity",
            "material",
        ),
    )

    boundaries: list[BoundaryConditionConfig] = []

    for boundary_name, boundary_data in bc_section.items():
        if not isinstance(boundary_data, dict):
            raise CaseConfigError(
                f"Boundary '{boundary_name}' "
                "must be a mapping."
            )

        bc_type = _require_string(
            boundary_data,
            "type",
            f"boundary_conditions.{boundary_name}",
        )

        if bc_type not in {
            "temperature",
            "heat_flux",
        }:
            raise CaseConfigError(
                f"Unsupported boundary type: {bc_type}"
            )

        boundaries.append(
            BoundaryConditionConfig(
                name=boundary_name,
                zone=_require_string(
                    boundary_data,
                    "zone",
                    f"boundary_conditions.{boundary_name}",
                ),
                type=bc_type,
                value=_require_number(
                    boundary_data,
                    "value",
                    f"boundary_conditions.{boundary_name}",
                ),
            )
        )

    max_iterations = solver_section.get(
        "max_iterations"
    )

    if (
        not isinstance(max_iterations, int)
        or max_iterations <= 0
    ):
        raise CaseConfigError(
            "'solver.max_iterations' "
            "must be a positive integer."
        )

    residual_target = _require_number(
        solver_section,
        "residual_target",
        "solver",
    )

    if residual_target <= 0:
        raise CaseConfigError(
            "'solver.residual_target' "
            "must be positive."
        )
    
    solver = SolverConfig(
    initialization=initialization,
    initial_temperature=initial_temperature,
    max_iterations=max_iterations,
    residual_target=residual_target,
)

    return CaseConfig(
        name=name,
        case_type=case_type,
        config_path=path,
        mesh_path=mesh_path,
        domain=domain,
        physics=physics,
        material=material,
        boundary_conditions=tuple(boundaries),
        solver=solver,
    )