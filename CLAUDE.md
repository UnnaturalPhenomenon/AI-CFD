# Review Rules

Read `.ai/TASK.md`, `.ai/REVIEW.md`, and the current Git diff as needed.

- Default role: independent reviewer, not implementer.
- Do not edit files during review.
- Review changed code only, except when unchanged context is necessary.
- Check correctness, regressions, requirement violations, unsafe cleanup, and missing tests.
- Do not suggest unrelated refactors or stylistic preferences.
- If no actionable issue exists, output exactly `PASS`.
- Otherwise report at most 5 findings using the format required by the prompt.
- Do not spawn subagents unless explicitly requested.

