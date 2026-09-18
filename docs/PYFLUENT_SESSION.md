# PyFluent solver-session smoke test

The smoke test launches Fluent 2024 R2 as a 2D, double-precision, single-process solver with no GUI. It only asks Fluent for its version twice (the second call is the server-health probe), then closes the session. It never loads a case or mesh, initializes, or runs iterations.

Run unit tests without launching Fluent:

```powershell
.\.venv\Scripts\python.exe -m pytest .\tests\test_fluent_session.py -q
```

Run the manual integration test on a licensed machine:

```powershell
.\.venv\Scripts\python.exe .\scripts\smoke_test_fluent_session.py --output .\.ai\logs\fluent-session-smoke.json
```

Expected successful compact output resembles:

```json
{"fluent_version":"24.2.0","pyfluent_version":"0.25.0","ready":true,"server_healthy":true,"session_closed":true}
```

The exact PyFluent version can differ. A missing or exhausted Fluent license normally produces a nonzero exit and an `error` field mentioning licensing. Launch failures can also be caused by an unavailable 24.2 installation, a mismatched `AWP_ROOT242` environment, blocked local ports, or an unsupported Python/PyFluent installation. The JSON result is still written when `--output` is used.
