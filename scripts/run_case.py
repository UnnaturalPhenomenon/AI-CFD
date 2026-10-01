"""Prepare a Fluent simulation case from a YAML configuration."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


# Allow this script to import modules from the project root when executed as:
#
# python scripts/run_case.py ...
PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from simulation.case_config import load_case_config
from simulation.fluent_session import managed_solver_session
from simulation.mesh_loader import load_mesh


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare a Fluent case from a YAML configuration."
    )

    parser.add_argument(
        "config",
        help="Path to the case YAML file.",
    )

    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        config = load_case_config(args.config)

        print(f"[CASE] {config.name}")
        print(f"[CONFIG] {config.config_path}")
        print(f"[MESH] {config.mesh_path}")

        print("[FLUENT] launching...")

        with managed_solver_session() as session:
            print("[FLUENT] ready")

            load_mesh(
                session=session,
                mesh_path=config.mesh_path,
            )

            print("[CASE] preparation complete")

        print("[FLUENT] session closed")
        print("[OK] case preparation complete")

        return 0

    except Exception as exc:
        print(
            f"[ERROR] {type(exc).__name__}: {exc}",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())