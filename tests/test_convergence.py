"""Behavior tests for residual convergence evaluation."""

from types import SimpleNamespace

import pytest

from simulation.convergence import (
    ConvergenceError, ConvergenceResult, evaluate_convergence,
    print_convergence_result,
)


def _session(data, names=("residual",)) -> SimpleNamespace:
    return SimpleNamespace(
        monitors_manager=SimpleNamespace(
            get_monitor_set_names=lambda: names,
            get_monitor_set_data=lambda _: data,
        )
    )


def test_evaluate_uses_latest_energy_residual_and_last_duplicate() -> None:
    result = evaluate_convergence(
        _session(([1, 2, 2, 3], {"energy": [1e-2, 4e-3, 2e-3, 1e-4]})),
        1e-4,
    )

    assert result == ConvergenceResult(3, 1e-4, 1e-4, True)


def test_evaluate_uses_last_value_for_final_duplicate_iteration() -> None:
    result = evaluate_convergence(
        _session(([1, 2, 2], {"energy": [1e-2, 4e-3, 1e-4]})), 1e-4
    )

    assert result.final_iteration == 2
    assert result.energy_residual == 1e-4
    assert result.converged is True


@pytest.mark.parametrize(
    "session,target",
    [
        (SimpleNamespace(), 1e-4),
        (_session(([], {}), names=()), 1e-4),
        (_session(None), 1e-4),
        (_session(([], {"energy": []})), 1e-4),
        (_session(([1], [])), 1e-4),
        (_session(([1], {"continuity": [1e-4]})), 1e-4),
        (_session(([1, 2], {"energy": [1e-4]})), 1e-4),
    ],
)
def test_evaluate_rejects_missing_or_malformed_monitor_data(session, target) -> None:
    with pytest.raises(ConvergenceError):
        evaluate_convergence(session, target)


def test_print_convergence_result_reports_all_fields(capsys) -> None:
    print_convergence_result(ConvergenceResult(12, 2e-5, 1e-4, True))

    output = capsys.readouterr().out
    assert "12" in output
    assert "2.000e-05" in output
    assert "1.000e-04" in output
    assert "PASS" in output
