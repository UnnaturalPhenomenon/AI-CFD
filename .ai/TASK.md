
# TASK

STATUS: READY

TITLE:
V0.1B - PyFluent solver session smoke test

GOAL:
Implement a minimal and safely managed PyFluent solver session.
Confirm that Fluent 2024 R2 can be launched, queried, and terminated
without loading a case or running a calculation.

CONTEXT:

- Windows 11
- Project virtual environment: .venv
- Python: 3.12
- Fluent installation: 2024 R2 / 24.2.0
- PyFluent environment check: ready=True
- This task must not create a CFD model or run a solver iteration.

SCOPE:

- simulation/__init__.py
- simulation/fluent_session.py
- scripts/smoke_test_fluent_session.py
- tests/test_fluent_session.py
- docs/PYFLUENT_SESSION.md

REQUIREMENTS:

1. Create a Fluent launch configuration with these defaults:

   - product_version: "24.2.0"
   - version: "2d"
   - precision: "double"
   - processor_count: 1
   - show_gui: false
   - mode: "solver"
2. Implement a managed solver session in
   simulation/fluent_session.py.
3. Use ansys.fluent.core.launch_fluent.
4. The managed session must terminate Fluent in a finally block.
5. Fluent termination must also occur when an exception is raised
   inside the managed session.
6. Allow launcher dependency injection so unit tests can use a fake
   launcher without starting Fluent.
7. Create scripts/smoke_test_fluent_session.py that:

   - launches Fluent
   - reads the Fluent version
   - checks that the server responds
   - does not load a case
   - does not initialize or iterate
   - exits Fluent
   - prints a compact result
   - optionally saves the result as JSON using --output
   - exits with code 0 on success and nonzero on failure
8. The smoke-test result must contain:

   - ready
   - pyfluent_version
   - fluent_version
   - server_healthy
   - session_closed
   - error, when applicable
9. Unit tests must verify:

   - correct launch arguments
   - cleanup after normal completion
   - cleanup after an exception
   - no real Fluent process is launched by pytest
10. Document:

    - unit-test command
    - manual integration-test command
    - expected successful output
    - common license and launch failures

DO NOT:

- modify ai.ps1
- modify scripts/ai-cycle.ps1
- modify AGENTS.md or CLAUDE.md
- modify .ai/REVIEW.md
- load a Fluent case or mesh
- perform initialization or solver iterations
- add ML code
- add dependencies other than existing test dependencies
- run the manual Fluent integration test from an agent sandbox

VERIFY:
.\.venv\Scripts\python.exe -m pytest .\tests\test_fluent_session.py -q

MANUAL_VERIFY:
.\.venv\Scripts\python.exe .\scripts\smoke_test_fluent_session.py --output .\.ai\logs\fluent-session-smoke.json

DONE:

- VERIFY passes.
- Only scoped implementation files are changed.
- The manual command is documented but is not executed by Codex.
- Fluent is guaranteed to close through cleanup logic.

<pre class="overflow-visible! px-0!" data-start="4480" data-end="4584"><div class="relative w-full mt-4 mb-1"><div class=""><div class="contents"><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-(--code-block-surface) corner-superellipse/1.1 overflow-clip rounded-3xl [--code-block-surface:var(--bg-elevated-secondary)] dark:[--code-block-surface:var(--composer-surface-primary)] lxnfua_clipPathFallback"><div class="pointer-events-none absolute end-1.5 top-1 z-2 md:end-2 md:top-1"></div><div class="relative"><div class="pe-11 pt-3"><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼd ͼr"><div class="cm-scroller"><pre class="cm-content q9tKkq_readonly m-0"></pre></div></div></div></div></div></div></div></div></div></div></div></div></div></pre>
