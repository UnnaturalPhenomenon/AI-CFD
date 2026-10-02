# Add solver workflow unit tests

STATUS: READY

## Goal

Replace the empty solver, solver-setup, and convergence test stubs with focused
unit tests that verify their behavior without launching Fluent.

## Scope

- Allowed: `tests/test_solver.py`, `tests/test_solver_setup.py`,
  `tests/test_convergence.py`
- Read-only implementation references: `simulation/solver.py`,
  `simulation/solver_setup.py`, `simulation/convergence.py`, and
  `simulation/case_config.py`
- Do not modify `scripts/run_case.py`, `simulation/solver_setup.py`, other
  implementation files, existing tests, or the staged fixes for review finding
  2.
- Do not add dependencies, format unrelated files, or create a commit.
- Do not start Fluent or run a manual integration test.

## Inputs

- The current solver setup, initialization, iteration, and convergence
  implementations in `simulation/`.
- Case/config data should be represented with small fixtures or
  `SimpleNamespace` objects as appropriate.
- Fluent sessions and settings must be fake objects; tests must not depend on an
  Ansys installation, license, network access, or live Fluent process.

## Requirements

1. Add tests to `tests/test_solver_setup.py` verifying energy is set from the
   config, material is created only when absent, configured density/specific
   heat/thermal conductivity are assigned, the configured solid zone receives
   the material, and temperature/heat-flux boundary conditions are applied.
2. Add tests verifying solver setup rejects a missing or malformed solid/wall
   zone list and rejects configured zones that are unavailable.
3. Add tests to `tests/test_solver.py` verifying the initialization temperature
   is set before standard initialization, the configured maximum iteration
   count is passed to Fluent, energy convergence criteria use the configured
   residual target while non-energy equations are not convergence-checked, and
   `solve_case` invokes convergence configuration, initialization, and iteration
   in that order.
4. Add tests to `tests/test_convergence.py` verifying the latest energy
   residual and iteration are selected, duplicate iteration entries resolve
   to the last value, convergence uses an inclusive `residual <= target`
   comparison, and the printed result reports iteration, residual, target, and
   status.
5. Add convergence error tests for missing monitor interfaces, missing residual
   monitor sets, empty or malformed data, absent energy residuals, and
   mismatched iteration/residual lengths.
6. Keep assertions focused on observable API calls, assigned values, ordering,
   and raised exceptions. Do not merely test private implementation details
   when a public function can cover the behavior.
7. Run the three new test files and the complete existing test suite. If a test
   exposes an implementation defect, do not change implementation files under
   this task; report the exact failing behavior as a blocker.
8. Review the diff and ensure only the three allowed test files were changed.

## Verify

```powershell
.\.venv\Scripts\python.exe -m pytest .\tests\test_solver.py .\tests\test_solver_setup.py .\tests\test_convergence.py -q
.\.venv\Scripts\python.exe -m pytest .\tests -q
git diff --check
```

## Done

- All three previously empty test files contain meaningful behavior-focused
  tests.
- New tests pass without launching Fluent.
- The full test-suite result is recorded accurately.
- No implementation files or unrelated staged changes are modified.
- Final report says `PASS` or `BLOCKER`; any blocker names the exact failing
  test or uncovered behavior.
