STATUS: READY

# Goal

Verify that Codex implementation and Claude review can operate through the shared Git repository.

# Scope

- Allowed: `docs/agent-integration-check.md`
- Excluded: every other file

# Inputs

- Current repository state

# Requirements

1. Create `docs/agent-integration-check.md`.
2. The file must contain exactly one line:
   `Codex implementation reached the shared repository.`
3. Do not modify any other file.

# Verify

```powershell
$content = (Get-Content .\docs\agent-integration-check.md -Raw).Trim()
if ($content -ne "Codex implementation reached the shared repository.") {
    throw "Integration check failed."
}
```
