"""Evaluate Fluent residual convergence."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


class ConvergenceError(RuntimeError):
    """Raised when convergence data cannot be evaluated."""


@dataclass(frozen=True)
class ConvergenceResult:
    final_iteration: int
    energy_residual: float
    target: float
    converged: bool


def _get_monitors(session: Any) -> Any:
    """Return the monitor interface supported by this PyFluent version."""

    manager = getattr(session, "monitors_manager", None)

    if manager is not None:
        return manager

    monitors = getattr(session, "monitors", None)

    if monitors is not None:
        return monitors

    raise ConvergenceError(
        "No Fluent monitor interface is available."
    )


def evaluate_convergence(
    session: Any,
    residual_target: float,
) -> ConvergenceResult:
    """Read the residual monitor and evaluate energy convergence."""

    monitors = _get_monitors(session)

    monitor_names = list(
        monitors.get_monitor_set_names()
    )

    if "residual" not in monitor_names:
        raise ConvergenceError(
            "Residual monitor data is not available. "
            f"Available monitors: {monitor_names}"
        )

    data = monitors.get_monitor_set_data("residual")

    if not data or len(data) < 2:
        raise ConvergenceError(
            "Residual monitor returned no usable data."
        )

    iterations = list(data[0])
    residual_data = data[1]

    if not iterations:
        raise ConvergenceError(
            "Residual history contains no iterations."
        )

    if not isinstance(residual_data, dict):
        raise ConvergenceError(
            "Unexpected residual monitor data format."
        )

    energy_key = None

    for key in residual_data:
        if str(key).lower() == "energy":
            energy_key = key
            break

    if energy_key is None:
        raise ConvergenceError(
            "Energy residual was not found. "
            f"Available residuals: {list(residual_data)}"
        )

    energy_values = list(
        residual_data[energy_key]
    )

    if len(energy_values) != len(iterations):
        raise ConvergenceError(
            "Iteration and residual history lengths do not match."
        )

    # Streaming monitor data can contain duplicate iteration entries.
    history: dict[int, float] = {}

    for iteration, residual in zip(
        iterations,
        energy_values,
    ):
        history[int(iteration)] = float(residual)

    if not history:
        raise ConvergenceError(
            "Energy residual history is empty."
        )

    final_iteration = max(history)
    final_residual = history[final_iteration]

    converged = (
        final_residual <= residual_target
    )

    return ConvergenceResult(
        final_iteration=final_iteration,
        energy_residual=final_residual,
        target=residual_target,
        converged=converged,
    )


def print_convergence_result(
    result: ConvergenceResult,
) -> None:
    """Print a compact convergence report."""

    status = (
        "PASS"
        if result.converged
        else "NOT CONVERGED"
    )

    print()
    print("[CONVERGENCE]")
    print(
        f"  final iteration : "
        f"{result.final_iteration}"
    )
    print(
        f"  energy residual : "
        f"{result.energy_residual:.3e}"
    )
    print(
        f"  target          : "
        f"{result.target:.3e}"
    )
    print(
        f"  status          : "
        f"{status}"
    )
    print()