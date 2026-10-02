"""Inspect Fluent cell and boundary zone names."""

from __future__ import annotations

from typing import Any


def get_zone_summary_from_setup(
    setup: Any,
) -> dict[str, list[str]]:
    """Return important zone names from a Fluent setup object."""

    solid_zones = list(
        setup.cell_zone_conditions.solid.get_object_names()
    )

    fluid_zones = list(
        setup.cell_zone_conditions.fluid.get_object_names()
    )

    wall_zones = list(
        setup.boundary_conditions.wall.get_object_names()
    )

    return {
        "solid": solid_zones,
        "fluid": fluid_zones,
        "wall": wall_zones,
    }


def get_zone_summary(session: Any) -> dict[str, list[str]]:
    """Backward-compatible session-based helper."""

    setup = session.settings.setup

    return get_zone_summary_from_setup(setup)


def print_zone_summary_from_zones(
    zones: dict[str, list[str]],
) -> None:
    """Print a previously collected zone summary."""

    print()
    print("[ZONES] Solid cell zones:")
    for name in zones["solid"]:
        print(f"  - {name}")

    print()
    print("[ZONES] Fluid cell zones:")
    for name in zones["fluid"]:
        print(f"  - {name}")

    print()
    print("[ZONES] Wall boundaries:")
    for name in zones["wall"]:
        print(f"  - {name}")

    print()


def print_zone_summary(session: Any) -> None:
    """Print cell and wall zone names."""

    zones = get_zone_summary(session)
    print_zone_summary_from_zones(zones)