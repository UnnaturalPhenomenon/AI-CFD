"""Report whether this machine is ready for PyFluent with Ansys 2024 R2."""

from __future__ import annotations

import argparse
import importlib
import importlib.metadata
import json
import os
import platform
import sys
from pathlib import Path


EXPECTED_ROOT = Path(r"C:\Program Files\ANSYS Inc\v242")


def fluent_executable(root: Path) -> Path:
    """Return the Fluent 2024 R2 Windows executable below *root*."""
    return root / "fluent" / "ntbin" / "win64" / "fluent.exe"


def pyfluent_available() -> bool:
    """Check availability without starting Fluent."""
    try:
        importlib.import_module("ansys.fluent.core")
    except ImportError:
        return False
    return True


def pyfluent_version() -> str | None:
    """Return the installed distribution version, if package metadata exists."""
    try:
        return importlib.metadata.version("ansys-fluent-core")
    except importlib.metadata.PackageNotFoundError:
        return None


def collect_report() -> dict[str, object]:
    """Collect a read-only environment report."""
    configured_root = os.environ.get("AWP_ROOT242")
    root = Path(configured_root) if configured_root else EXPECTED_ROOT
    candidate = fluent_executable(root)
    import_available = pyfluent_available()
    version = pyfluent_version()

    missing = []
    if not configured_root:
        missing.append("AWP_ROOT242 is not set")
    if not candidate.is_file():
        missing.append("Fluent executable was not found")
    if not import_available:
        missing.append("ansys.fluent.core cannot be imported")

    return {
        "operating_system": platform.platform(),
        "python_executable": sys.executable,
        "python_version": platform.python_version(),
        "machine_architecture": platform.machine(),
        "awp_root242": {"present": bool(configured_root), "value": configured_root},
        "pyfluent_importable": import_available,
        "ansys_fluent_core_version": version,
        "candidate_fluent_executable": str(candidate),
        "candidate_fluent_executable_exists": candidate.is_file(),
        "ready": not missing,
        "missing_requirements": missing,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Write the JSON report to this path.")
    parser.add_argument("--strict", action="store_true", help="Fail when requirements are missing.")
    args = parser.parse_args(argv)

    report = collect_report()
    encoded = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 1 if args.strict and not report["ready"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
