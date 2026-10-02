"""Prepare a Fluent simulation case from YAML."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from simulation.case_config import load_case_config
from simulation.fluent_session import managed_solver_session
from simulation.mesh_loader import load_mesh
from simulation.solver_setup import apply_solver_setup
from simulation.solver import solve_case
from simulation.zone_inspector import (
    get_zone_summary,
    print_zone_summary_from_zones,
)
from simulation.convergence import (
    evaluate_convergence,
    print_convergence_result,
)

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Prepare a Fluent case from "
            "a YAML configuration."
        )
    )

    parser.add_argument(
        "config",
        help="Path to the case YAML file.",
    )

    parser.add_argument(
        "--inspect-zones",
        action="store_true",
        help=(
            "Load the mesh and print Fluent zone names "
            "without applying solver setup."
        ),
    )
    parser.add_argument(
        "--setup-only",
        action="store_true",
        help=(
            "Apply Fluent setup without "
            "initializing or solving."
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        config = load_case_config(args.config)

        print(f"[CASE] {config.name}")
        print(f"[TYPE] {config.case_type}")
        print(f"[CONFIG] {config.config_path}")
        print(f"[MESH] {config.mesh_path}")

        print("[FLUENT] launching...")

        with managed_solver_session() as session:
            print("[FLUENT] ready")

            load_mesh(
                session=session,
                mesh_path=config.mesh_path,
            )
            # Mesh loading 직후 zone 정보를 한 번만 읽는다.
            print("[FLUENT] reading zone information...")
            zones = get_zone_summary(session)
            print("[FLUENT] zone information ready")

            if args.inspect_zones:
                print_zone_summary_from_zones(zones)

                print("[OK] zone inspection complete")
                return 0
            apply_solver_setup(
                session=session,
                config=config,
                zones=zones,
            )

            print("[CASE] setup complete")

            if args.setup_only:
                print("[OK] setup-only run complete")
                return 0
            
            solve_case(
                    session=session,
                    config=config,
            )
            convergence = evaluate_convergence(
            session=session,
            residual_target=config.solver.residual_target,
            )
            print_convergence_result(convergence)

            print("[CASE] solution complete")

        print("[FLUENT] session closed")
        print("[OK] case run complete")

    except Exception:
        import traceback

        traceback.print_exc()

        return 1


if __name__ == "__main__":
    raise SystemExit(main())