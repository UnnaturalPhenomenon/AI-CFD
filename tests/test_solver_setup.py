"""Behavior tests for Fluent solver setup."""

from types import SimpleNamespace

import pytest

from simulation.solver_setup import SolverSetupError, apply_solver_setup


def _config() -> SimpleNamespace:
    return SimpleNamespace(
        physics=SimpleNamespace(energy=True),
        material=SimpleNamespace(
            name="copper", density=8960.0, specific_heat=385.0,
            thermal_conductivity=401.0,
        ),
        domain=SimpleNamespace(zone="solid-body"),
        boundary_conditions=(
            SimpleNamespace(name="hot", zone="hot-wall", type="temperature", value=350.0),
            SimpleNamespace(name="cool", zone="cool-wall", type="heat_flux", value=120.0),
        ),
    )


def _session(existing: tuple[str, ...] = ()) -> SimpleNamespace:
    materials: dict[str, SimpleNamespace] = {
        name: SimpleNamespace(
            density=SimpleNamespace(value=None), specific_heat=SimpleNamespace(value=None),
            thermal_conductivity=SimpleNamespace(value=None),
        ) for name in existing
    }

    class SolidMaterials(dict):
        def get_object_names(self):
            return list(self)

        def create(self, name):
            self[name] = SimpleNamespace(
                density=SimpleNamespace(value=None), specific_heat=SimpleNamespace(value=None),
                thermal_conductivity=SimpleNamespace(value=None),
            )

    solid_materials = SolidMaterials(materials)
    return SimpleNamespace(
        settings=SimpleNamespace(
            setup=SimpleNamespace(
                models=SimpleNamespace(energy=SimpleNamespace(enabled=None)),
                materials=SimpleNamespace(solid=solid_materials),
                cell_zone_conditions=SimpleNamespace(
                    solid={"solid-body": SimpleNamespace(general=SimpleNamespace(material=None))}
                ),
                boundary_conditions=SimpleNamespace(
                    wall={
                        "hot-wall": SimpleNamespace(thermal=SimpleNamespace(thermal_condition=None, temperature=None, heat_flux=None)),
                        "cool-wall": SimpleNamespace(thermal=SimpleNamespace(thermal_condition=None, temperature=None, heat_flux=None)),
                    }
                ),
            )
        )
    )


def test_apply_setup_creates_material_assigns_properties_and_boundaries() -> None:
    session = _session()

    apply_solver_setup(session, _config(), {"solid": ["solid-body"], "wall": ["hot-wall", "cool-wall"]})

    setup = session.settings.setup
    material = setup.materials.solid["copper"]
    assert setup.models.energy.enabled is True
    assert material.density.value == 8960.0
    assert material.specific_heat.value == 385.0
    assert material.thermal_conductivity.value == 401.0
    assert setup.cell_zone_conditions.solid["solid-body"].general.material == "copper"
    assert setup.boundary_conditions.wall["hot-wall"].thermal.temperature == 350.0
    assert setup.boundary_conditions.wall["cool-wall"].thermal.heat_flux == 120.0


def test_apply_setup_reuses_existing_material() -> None:
    session = _session(("copper",))
    solid_materials = session.settings.setup.materials.solid
    original = solid_materials["copper"]

    apply_solver_setup(session, _config(), {"solid": ["solid-body"], "wall": ["hot-wall", "cool-wall"]})

    assert solid_materials["copper"] is original


@pytest.mark.parametrize("zones", [{}, {"solid": "solid-body", "wall": []}, {"solid": [], "wall": "hot-wall"}])
def test_apply_setup_rejects_missing_or_malformed_zone_lists(zones) -> None:
    with pytest.raises(SolverSetupError):
        apply_solver_setup(_session(), _config(), zones)


@pytest.mark.parametrize(
    "zones",
    [
        {"solid": [], "wall": ["hot-wall", "cool-wall"]},
        {"solid": ["solid-body"], "wall": ["hot-wall"]},
    ],
)
def test_apply_setup_rejects_unavailable_configured_zones(zones) -> None:
    with pytest.raises(SolverSetupError):
        apply_solver_setup(_session(), _config(), zones)
