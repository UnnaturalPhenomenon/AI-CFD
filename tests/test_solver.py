"""Behavior tests for the Fluent solver workflow."""

from types import SimpleNamespace

from simulation import solver


def _config() -> SimpleNamespace:
    return SimpleNamespace(
        solver=SimpleNamespace(
            initial_temperature=325.0,
            max_iterations=75,
            residual_target=2e-5,
        )
    )


def test_initialize_sets_temperature_before_standard_initialization() -> None:
    events: list[object] = []

    class Initialization:
        def __init__(self) -> None:
            self.defaults = {"temperature": None}

        def standard_initialize(self) -> None:
            events.append(self.defaults["temperature"])

    initialization = Initialization()
    session = SimpleNamespace(
        settings=SimpleNamespace(
            solution=SimpleNamespace(initialization=initialization)
        )
    )

    solver.initialize_case(session, _config())

    assert initialization.defaults["temperature"] == 325.0
    assert events == [325.0]


def test_configure_convergence_only_checks_energy() -> None:
    energy = SimpleNamespace(
        monitor=False, check_convergence=False, absolute_criteria=None
    )
    continuity = SimpleNamespace(check_convergence=True)
    class Equations(dict):
        def get_object_names(self):
            return list(self)

    equations = Equations(energy=energy, continuity=continuity)
    session = SimpleNamespace(
        settings=SimpleNamespace(
            solution=SimpleNamespace(
                monitor=SimpleNamespace(
                    residual=SimpleNamespace(equations=equations)
                )
            )
        )
    )

    solver.configure_convergence(session, _config())

    assert energy.monitor is True
    assert energy.check_convergence is True
    assert energy.absolute_criteria == 2e-5
    assert continuity.check_convergence is False


def test_run_iterations_passes_configured_limit() -> None:
    calls: list[int] = []
    session = SimpleNamespace(
        settings=SimpleNamespace(
            solution=SimpleNamespace(
                run_calculation=SimpleNamespace(
                    iterate=lambda *, iter_count: calls.append(iter_count)
                )
            )
        )
    )

    solver.run_iterations(session, _config())

    assert calls == [75]


def test_solve_case_runs_workflow_in_order(monkeypatch) -> None:
    calls: list[str] = []
    monkeypatch.setattr(
        solver, "configure_convergence", lambda **_: calls.append("convergence")
    )
    monkeypatch.setattr(
        solver, "initialize_case", lambda **_: calls.append("initialize")
    )
    monkeypatch.setattr(
        solver, "run_iterations", lambda **_: calls.append("iterations")
    )

    solver.solve_case(SimpleNamespace(), _config())

    assert calls == ["convergence", "initialize", "iterations"]
