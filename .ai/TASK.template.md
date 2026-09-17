STATUS: DRAFT

# Goal

One sentence describing the required outcome.

# Scope

- Allowed: `path/to/file.py`, `tests/test_file.py`
- Excluded: unrelated modules, dependency upgrades, broad refactors

# Inputs

- Input files:
- Parameter ranges:
- Assumptions:

# Requirements

1. Requirement with an observable result.
2. Existing API/format that must remain unchanged.
3. Failure behavior that must be handled.

# Verify

```powershell
python -m pytest tests/test_file.py -q
```

# Done

- Verification exits with code 0.
- Required output exists and has the specified fields.
- Final report lists changed files and unresolved issues only.

