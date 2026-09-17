STATUS: READY

# Goal

Create a read-only environment probe for a future PyFluent automation
project targeting Ansys Fluent 2024 R2 Academic on Windows.

This task must not launch Fluent or modify the Python environment.

# Scope

- Allowed:

  - `scripts/check_pyfluent_environment.py`
  - `tests/test_check_pyfluent_environment.py`
  - `docs/PYFLUENT_ENVIRONMENT.md`
- Excluded:

  - `scripts/ai-cycle.ps1`
  - `ai.ps1`
  - `AGENTS.md`
  - `CLAUDE.md`
  - dependency installation
  - Fluent launch
  - solver setup
  - geometry, mesh, CFD, dataset, and ML implementation

# Inputs

- Operating system: Windows x64
- Target Ansys release: Fluent 2024 R2
- Ansys version code: V242
- Expected environment variable: `AWP_ROOT242`
- Typical installation root:
  `C:\Program Files\ANSYS Inc\v242`

# Requirements

1. Use only the Python standard library.
2. Create `scripts/check_pyfluent_environment.py`.
3. The probe must report:

   - operating system
   - Python executable
   - Python version
   - machine architecture
   - presence and value of `AWP_ROOT242`
   - whether `ansys.fluent.core` can be imported
   - installed `ansys-fluent-core` package version, when available
   - candidate Fluent executable path
   - whether the candidate executable exists
   - overall `ready` Boolean
   - a list of missing requirements
4. Detect the Fluent executable from `AWP_ROOT242` first.
5. If `AWP_ROOT242` is absent, inspect only the expected V242
   installation path under `C:\Program Files\ANSYS Inc\v242`.
6. Do not enumerate unrelated environment variables.
7. Do not read or print license server values, API keys, credentials,
   account information, or network configuration.
8. Do not launch Fluent.
9. Do not install or update packages.
10. Support:

    ```powershell
    python scripts/check_pyfluent_environment.py
    ```
11. Support JSON file output:

    ```powershell
    python scripts/check_pyfluent_environment.py `
        --output outputs/pyfluent-environment.json
    ```
12. Create the output parent directory when necessary.
13. The normal probe must exit with code 0 even when requirements are
    missing. Missing requirements must be represented in the JSON report.
14. Add `--strict`. In strict mode, return a nonzero exit code when
    `ready` is false.
15. Add standard-library `unittest` coverage without requiring Fluent
    or PyFluent to be installed on the test runner.
16. Document usage and interpretation in
    `docs/PYFLUENT_ENVIRONMENT.md`.

# Verify

```powershell
python -m unittest discover `
    -s tests `
    -p "test_check_pyfluent_environment.py" `
    -v

python scripts/check_pyfluent_environment.py `
    --output outputs/pyfluent-environment.json

python -m json.tool `
    outputs/pyfluent-environment.json |
    Out-Null

if ($LASTEXITCODE -ne 0) {
    throw "Environment report is not valid JSON."
}
```

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


# Done

* All unit tests pass.
* The environment probe completes without launching Fluent.
* `outputs/pyfluent-environment.json` is valid JSON.
* The report contains `ready` and `missing_requirements`.
* No secrets or license-server values are printed.
* Only files listed under Scope are modified.

<pre class="overflow-visible! px-0!" data-start="4480" data-end="4584"><div class="relative w-full mt-4 mb-1"><div class=""><div class="contents"><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-(--code-block-surface) corner-superellipse/1.1 overflow-clip rounded-3xl [--code-block-surface:var(--bg-elevated-secondary)] dark:[--code-block-surface:var(--composer-surface-primary)] lxnfua_clipPathFallback"><div class="pointer-events-none absolute end-1.5 top-1 z-2 md:end-2 md:top-1"></div><div class="relative"><div class="pe-11 pt-3"><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼd ͼr"><div class="cm-scroller"><pre class="cm-content q9tKkq_readonly m-0"></pre></div></div></div></div></div></div></div></div></div></div></div></div></div></pre>
