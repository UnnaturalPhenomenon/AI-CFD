"""Initialize and run a Fluent solution."""

from __future__ import annotations

from typing import Any

from simulation.case_config import CaseConfig


class SolverRunError(RuntimeError):
    """Raised when the Fluent solution cannot be run."""


def initialize_case(
    session: Any,
    config: CaseConfig,
) -> None:
    """Initialize the steady thermal solution."""

    initial_temperature = (
        config.solver.initial_temperature
    )

    print(
        "[SOLVER] initial temperature = "
        f"{initial_temperature} K"
    )

    initialization = (
        session.settings.solution.initialization
    )

    initialization.defaults["temperature"] = (
        initial_temperature
    )

    print("[SOLVER] initializing...")

    initialization.standard_initialize()

    print("[SOLVER] initialization complete")

def configure_convergence(
    session: Any,
    config: CaseConfig,
) -> None:
    """Apply thermal-only convergence criteria."""

    target = config.solver.residual_target

    equations = (
        session.settings.solution.monitor.residual.equations
    )

    names = equations.get_object_names()

    for name in names:
        equation = equations[name]

        if name == "energy":
            equation.monitor = True
            equation.check_convergence = True
            equation.absolute_criteria = target
        else:
            equation.check_convergence = False

    print(
        "[SOLVER] convergence:"
        f" energy <= {target:.3e}"
    )

def run_iterations(
    session: Any,
    config: CaseConfig,
) -> None:
    """Run the requested maximum number of iterations."""

    iterations = config.solver.max_iterations

    print(
        f"[SOLVER] running up to "
        f"{iterations} iterations..."
    )

    session.settings.solution.run_calculation.iterate(
        iter_count=iterations
    )

    print("[SOLVER] calculation complete")


def solve_case(
    session: Any,
    config: CaseConfig,
) -> None:
    """Configure convergence, initialize, and solve."""

    configure_convergence(
        session=session,
        config=config,
    )

    initialize_case(
        session=session,
        config=config,
    )

    run_iterations(
        session=session,
        config=config,
    )

    print("[SOLVER] complete")