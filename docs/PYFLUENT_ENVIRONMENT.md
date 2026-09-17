# PyFluent environment probe

Run the read-only probe from the repository root:

```powershell
python scripts/check_pyfluent_environment.py
```

To save the JSON report, including any needed parent directories:

```powershell
python scripts/check_pyfluent_environment.py --output outputs/pyfluent-environment.json
```

The report checks Windows and Python details, `AWP_ROOT242`, the expected Fluent 2024 R2 executable, and whether PyFluent can be imported. It does not launch Fluent, install packages, or inspect unrelated environment variables. `ready` is true only when `AWP_ROOT242` is set, the candidate executable exists, and `ansys.fluent.core` can be imported. Review `missing_requirements` when it is false.

Use `--strict` when a nonzero exit code is required for a non-ready environment:

```powershell
python scripts/check_pyfluent_environment.py --strict
```
