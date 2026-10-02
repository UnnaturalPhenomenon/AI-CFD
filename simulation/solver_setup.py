"""Apply YAML-driven solver setup to Fluent."""

from __future__ import annotations

from typing import Any

from simulation.case_config import CaseConfig
from simulation.zone_inspector import get_zone_summary_from_setup


class SolverSetupError(RuntimeError):
    """Raised when Fluent setup cannot be applied."""


def _validate_zones(
    zones: dict[str, list[str]],
    config: CaseConfig,
) -> None:
    """Validate required Fluent zone groups and configured zones."""

    solid_zones = zones.get("solid")
    wall_zones = zones.get("wall")

    if not isinstance(solid_zones, list):
        raise SolverSetupError(
            "Zone summary is missing a valid 'solid' list."
        )

    if not isinstance(wall_zones, list):
        raise SolverSetupError(
            "Zone summary is missing a valid 'wall' list."
        )

    if config.domain.zone not in solid_zones:
        available = ", ".join(solid_zones) or "<none>"

        raise SolverSetupError(
            f"Solid cell zone '{config.domain.zone}' "
            f"was not found. "
            f"Available solid zones: {available}"
        )

    for boundary in config.boundary_conditions:
        if boundary.zone not in wall_zones:
            available = ", ".join(wall_zones) or "<none>"

            raise SolverSetupError(
                f"Wall zone '{boundary.zone}' "
                f"for boundary '{boundary.name}' "
                f"was not found. "
                f"Available wall zones: {available}"
            )


def _setup_energy(
    session: Any,
    config: CaseConfig,
) -> None:
    """Enable or disable the Fluent energy equation."""

    enabled = config.physics.energy

    print(f"[SETUP] energy = {enabled}")

    session.settings.setup.models.energy.enabled = enabled

    print("[SETUP] energy model configured")


def _setup_material(
    session: Any,
    config: CaseConfig,
) -> None:
    materials = session.settings.setup.materials
    material = config.material

    existing_materials = (
        materials.solid.get_object_names()
    )

    if material.name not in existing_materials:
        print(
            f"[SETUP] creating solid material: "
            f"{material.name}"
        )

        materials.solid.create(material.name)

    solid = materials.solid[material.name]

    solid.density.value = material.density
    solid.specific_heat.value = (
        material.specific_heat
    )
    solid.thermal_conductivity.value = (
        material.thermal_conductivity
    )

    print("[SETUP] material properties:")
    print(f"  density = {material.density}")
    print(f"  cp = {material.specific_heat}")
    print(f"  k = {material.thermal_conductivity}")

    solid_zone = (
        session.settings.setup.cell_zone_conditions.solid[
            config.domain.zone
        ]
    )

    solid_zone.general.material = material.name

    print(
        f"[SETUP] material assigned to "
        f"{config.domain.zone}"
    )


def _setup_boundaries(
    session: Any,
    config: CaseConfig,
) -> None:
    walls = (
        session.settings.setup.boundary_conditions.wall
    )

    for boundary in config.boundary_conditions:
        wall = walls[boundary.zone]

        if boundary.type == "temperature":
            wall.thermal.thermal_condition = (
                "Temperature"
            )
            wall.thermal.temperature = boundary.value

            print(
                f"[BC] {boundary.name}: "
                f"{boundary.zone} = "
                f"{boundary.value} K"
            )

        elif boundary.type == "heat_flux":
            wall.thermal.thermal_condition = (
                "Heat Flux"
            )
            wall.thermal.heat_flux = boundary.value

            print(
                f"[BC] {boundary.name}: "
                f"{boundary.zone} = "
                f"{boundary.value} W/m^2"
            )


def apply_solver_setup(
    session: Any,
    config: CaseConfig,
    zones: dict[str, list[str]],
) -> None:
    """Apply the conduction setup described by YAML."""

    print("[SETUP] validating Fluent zones...")
    _validate_zones(
        zones=zones,
        config=config,
    )

    print("[SETUP] applying physics...")
    _setup_energy(
        session=session,
        config=config,
    )

    print("[SETUP] applying material...")
    _setup_material(
        session=session,
        config=config,
    )

    print("[SETUP] applying boundaries...")
    _setup_boundaries(
        session=session,
        config=config,
    )

    print("[SETUP] complete")