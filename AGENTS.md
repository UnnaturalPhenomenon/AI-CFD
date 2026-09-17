# Agent Rules

1. Read `.ai/TASK.md` before inspecting source files.
2. Work only when `STATUS: READY` is present in the task file.
3. Inspect only files required by `SCOPE` and `VERIFY`.
4. Do not refactor unrelated code or add speculative features.
5. Prefer existing dependencies and interfaces.
6. Do not spawn subagents unless the task explicitly requests them.
7. Run every command listed under `VERIFY`.
8. Stop when the `DONE` criteria are satisfied.
9. Final response: changed files, verification result, unresolved issues; at most 6 lines.

