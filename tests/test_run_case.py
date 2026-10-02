"""Tests for the case runner's Fluent session lifecycle."""

from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace

from scripts import run_case


def test_setup_only_applies_setup_before_session_closes(
    monkeypatch,
    tmp_path: Path,
) -> None:
    session = SimpleNamespace(closed=True)
    config = SimpleNamespace(
        name="test_case",
        case_type="steady_conduction",
        config_path=tmp_path / "case.yaml",
        mesh_path=tmp_path / "mesh.msh",
    )
    setup_calls = []

    @contextmanager
    def fake_managed_session():
        session.closed = False
        try:
            yield session
        finally:
            session.closed = True

    def fake_apply_solver_setup(*, session, config, zones):
        assert session.closed is False
        setup_calls.append(True)

    monkeypatch.setattr(
        "sys.argv",
        ["run_case.py", "case.yaml", "--setup-only"],
    )
    monkeypatch.setattr(run_case, "load_case_config", lambda _: config)
    monkeypatch.setattr(
        run_case,
        "managed_solver_session",
        fake_managed_session,
    )
    monkeypatch.setattr(run_case, "load_mesh", lambda **_: None)
    monkeypatch.setattr(run_case, "get_zone_summary", lambda _: {})
    monkeypatch.setattr(
        run_case,
        "apply_solver_setup",
        fake_apply_solver_setup,
    )

    assert run_case.main() == 0
    assert setup_calls == [True]
    assert session.closed is True