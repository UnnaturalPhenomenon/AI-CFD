"""Unit tests for the PyFluent session lifecycle (no Fluent process is started)."""

import pytest

from simulation.fluent_session import FluentLaunchConfig, managed_solver_session


class FakeSession:
    def __init__(self) -> None:
        self.exit_calls = 0

    def exit(self) -> None:
        self.exit_calls += 1


def test_launches_with_expected_pyfluent_arguments() -> None:
    received = {}
    session = FakeSession()

    def fake_launcher(**kwargs):
        received.update(kwargs)
        return session

    with managed_solver_session(launcher=fake_launcher) as active_session:
        assert active_session is session

    assert received == {
        "product_version": "24.2.0",
        "dimension": 2,
        "precision": "double",
        "processor_count": 1,
        "ui_mode": "no_gui",
        "mode": "solver",
        "start_transcript": False,
    }


def test_closes_session_after_normal_completion() -> None:
    session = FakeSession()

    with managed_solver_session(launcher=lambda **_: session):
        pass

    assert session.exit_calls == 1


def test_closes_session_after_exception() -> None:
    session = FakeSession()

    with pytest.raises(RuntimeError, match="test failure"):
        with managed_solver_session(launcher=lambda **_: session):
            raise RuntimeError("test failure")

    assert session.exit_calls == 1


def test_default_configuration_has_required_values() -> None:
    assert FluentLaunchConfig() == FluentLaunchConfig(
        product_version="24.2.0",
        version="2d",
        precision="double",
        processor_count=1,
        show_gui=False,
        mode="solver",
    )
