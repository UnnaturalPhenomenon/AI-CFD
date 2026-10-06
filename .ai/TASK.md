# Validate Fluent linear-conduction workflow

STATUS: READY

## Goal

Complete and verify the linear-conduction validation workflow with fake-array
unit tests, a full test run, a real Fluent case run, and an AI review that ends
with `PASS`.

## Scope

- Relevant implementation and configuration: `simulation/validation.py`,
  `simulation/case_config.py`, `scripts/run_case.py`,
  `cases/conduction_square/case.yaml`
- Relevant tests: `tests/test_validation.py`,
  `tests/test_case_config.py`
- Read and review any related changed files required to understand the current
  feature, but do not modify unrelated user changes.
- Preserve all existing staged and unstaged user work. Do not reset, revert,
  stage, commit, or push files.
- Do not add dependencies or perform broad refactoring.

## Inputs

- Example case: `cases/conduction_square/case.yaml`
- Fluent mesh: the mesh path configured by that case file.
- Validation mode: linear conduction using fake centroid and temperature arrays
  in unit tests, and the configured licensed Fluent installation for the manual
  case run.
- Fluent run requires the configured Ansys installation, valid license, and
  project `.venv` dependencies. If unavailable, report the concrete blocker;
  do not claim the integration run passed.

## Requirements

1. Ensure `tests/test_validation.py` uses fake Fluent metadata and fake
   centroid/temperature arrays; unit tests must never start Fluent.
2. Verify an exact linear temperature field returns `passed=True`, a field
   whose maximum error exceeds tolerance returns `passed=False`, and malformed
   centroid dimension or unsupported/unavailable validation axes raise
   `ValidationError`.
3. Verify the test doubles match the installed PyFluent solution-variable API
   used by `simulation/validation.py` and exercise the public
   `validate_linear_conduction` function.
4. Run the focused validation tests first, then the entire test suite. Fix
   failures only when they are caused by this validation workflow; preserve
   unrelated user edits and report unrelated failures as blockers.
5. After all unit tests pass, run the real Fluent case from the project root:

   ```powershell
   .\.venv\Scripts\python.exe .\scripts\run_case.py .\cases\conduction_square\case.yaml
   ```

   Require exit code 0 and successful convergence and physics-validation output.
   Do not treat a printed completion message alone as success if the runner
   reports a failed convergence or validation result.
6. Only after the focused tests, full tests, and real Fluent run pass, run the
   repository AI review:

   ```powershell
   .\ai.ps1 review
   ```

   Read `.ai/REVIEW.md`. If it contains actionable findings, validate them,
   apply only relevant fixes without discarding user work, rerun the affected
   tests and Fluent case, and run `review` again. Repeat until review output is
   exactly `PASS`, with a maximum of two correction rounds; otherwise report a
   concrete blocker.
7. Do not report `PASS` unless both the complete pytest suite and the real
   Fluent run succeeded and `.ai/REVIEW.md` contains exactly `PASS`.

## Verify

```powershell
.\.venv\Scripts\python.exe -m pytest .\tests\test_validation.py .\tests\test_case_config.py -q
.\.venv\Scripts\python.exe -m pytest .\tests -q
.\.venv\Scripts\python.exe .\scripts\run_case.py .\cases\conduction_square\case.yaml
.\ai.ps1 review
Get-Content .\.ai\REVIEW.md -Raw
```

## Done

- Focused validation tests and the full test suite pass.
- The actual Fluent case exits successfully and reports both convergence and
  linear-conduction validation as passing.
- AI review output is exactly `PASS`.
- User changes remain intact; no unrelated files are modified or staged.
- Final report states the test result, Fluent-run result, and review result. If
  any required stage cannot pass, report `BLOCKER` with the exact evidence.
