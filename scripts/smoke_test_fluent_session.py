"""Launch and close a minimal Fluent solver session without running a CFD job."""

from __future__ import annotations

import argparse
import json
import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from simulation.fluent_session import managed_solver_session


def _pyfluent_version() -> str:
    try:
        return version("ansys-fluent-core")
    except PackageNotFoundError:
        return "unknown"


def run_smoke_test() -> dict[str, Any]:
    """Perform only server queries; no case, mesh, initialization, or iteration."""
    result: dict[str, Any] = {
        "ready": False,
        "pyfluent_version": _pyfluent_version(),
        "fluent_version": None,
        "server_healthy": False,
        "session_closed": False,
    }
    try:
        with managed_solver_session() as session:
            result["fluent_version"] = str(session.get_fluent_version())
            # A second remote query explicitly verifies that the server responds.
            result["server_healthy"] = bool(session.get_fluent_version())
            result["ready"] = result["server_healthy"]
        result["session_closed"] = True
    except Exception as error:
        result["error"] = f"{type(error).__name__}: {error}"
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Optional path for the JSON result.")
    args = parser.parse_args()
    result = run_smoke_test()
    rendered = json.dumps(result, separators=(",", ":"), sort_keys=True)
    print(rendered)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    return 0 if result["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
