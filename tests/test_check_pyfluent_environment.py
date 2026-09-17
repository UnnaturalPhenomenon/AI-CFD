"""Tests for the read-only PyFluent environment probe."""

import importlib.util
import os
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).parents[1] / "scripts" / "check_pyfluent_environment.py"
SPEC = importlib.util.spec_from_file_location("environment_probe", SCRIPT)
probe = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(probe)


class EnvironmentProbeTests(unittest.TestCase):
    def test_fluent_executable_uses_expected_windows_layout(self):
        root = Path(r"C:\ANSYS Inc\v242")
        self.assertEqual(
            probe.fluent_executable(root),
            root / "fluent" / "ntbin" / "win64" / "fluent.exe",
        )

    @patch.object(probe, "pyfluent_version", return_value=None)
    @patch.object(probe, "pyfluent_available", return_value=False)
    def test_report_identifies_missing_requirements(self, _available, _version):
        with patch.dict(os.environ, {}, clear=True):
            report = probe.collect_report()
        self.assertFalse(report["ready"])
        self.assertFalse(report["awp_root242"]["present"])
        self.assertIn("AWP_ROOT242 is not set", report["missing_requirements"])
        self.assertIn("ansys.fluent.core cannot be imported", report["missing_requirements"])

    @patch.object(probe, "pyfluent_version", return_value="0.30.0")
    @patch.object(probe, "pyfluent_available", return_value=True)
    @patch.object(Path, "is_file", return_value=True)
    def test_report_uses_awp_root_first(self, _exists, _available, _version):
        root = Path(r"C:\ANSYS Inc\v242")
        executable = probe.fluent_executable(root)
        with patch.dict(os.environ, {"AWP_ROOT242": str(root)}, clear=True):
            report = probe.collect_report()
        self.assertTrue(report["ready"])
        self.assertEqual(report["candidate_fluent_executable"], str(executable))
        self.assertEqual(report["ansys_fluent_core_version"], "0.30.0")

    @patch.object(probe, "collect_report", return_value={"ready": False})
    def test_strict_mode_returns_nonzero_when_not_ready(self, _report):
        self.assertEqual(probe.main(["--strict"]), 1)


if __name__ == "__main__":
    unittest.main()
