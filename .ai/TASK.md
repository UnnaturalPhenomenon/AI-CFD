# Minimal case-loading workflow

STATUS: READY

## Goal

Implement a minimal workflow that reads `case.yaml`, resolves its mesh path,
starts the existing managed Fluent solver session, and loads the `.msh` mesh.
The workflow must stop after mesh loading; it must not configure or solve the
case.

## Scope

- Allowed: `simulation/case_config.py`, `simulation/mesh_loader.py`,
  `scripts/run_case.py`, `tests/test_case_config.py`,
  `tests/test_mesh_loader.py`
- Reuse `simulation/fluent_session.py` as-is unless a blocking issue is found.
- Excluded: solver setup, initialization, iterations, ML code, dependency
  upgrades, and unrelated refactoring.

## Inputs

- Input file: a YAML case configuration with `case.name` and `mesh.file`.
- Mesh path: resolve a relative `mesh.file` from the directory containing
  `case.yaml`.
- Assumption: the input mesh is an existing Fluent `.msh` file and the current
  managed solver session exposes Fluent's mesh-loading API.

## Requirements

1. Load and validate the case name and mesh path from `case.yaml`.
2. Resolve the mesh path relative to `case.yaml` and fail clearly if the
   configuration or mesh file is invalid or missing.
3. Launch Fluent through the existing `managed_solver_session` context manager
   and load the resolved mesh using the Fluent mesh-reading API.
4. Close the managed session on both successful mesh loading and errors.
5. Do not load a case file, configure models or boundary conditions, initialize
   the solution, or run solver iterations.
6. Unit tests must cover valid configuration loading and path resolution,
   invalid or missing configuration inputs, mesh loading through a fake session,
   and missing or unsupported mesh files. Pytest must not launch Fluent.
7. Review the final git diff and test result. Report `PASS` or `BLOCKER` only,
   with concrete reasons for any blocker.

## Verify

```powershell
.\.venv\Scripts\python.exe -m pytest .\tests\test_case_config.py .\tests\test_mesh_loader.py -q
```

## Done

- The focused verification command exits with code 0.
- The workflow loads only the configured mesh and leaves solver setup and
  calculation untouched.
- Unit tests use temporary files and fake Fluent sessions; they do not start a
  Fluent process.
- The final git diff is reviewed and the final report follows the required
  `PASS` or `BLOCKER` format.
