---
name: ci-api-job-runs-ruff-before-pytest
description: G4/S6 trap - the api CI job runs `ruff check .` from services/api BEFORE pytest, so a lint-only defect in a new file fails "CI green" even when every test passes
metadata:
  type: feedback
---

When a rules/backend task's S6 (or any "CI api job green") acceptance scenario is in play,
independently run ruff the way CI runs it, not just pytest. Do not treat "N passed" +
modularity + snapshot-sync as sufficient evidence for "CI green."

**Why:** `.github/workflows/ci.yml` job `api` (name "api (ruff + pytest)") has
`defaults.run.working-directory: services/api` and runs `ruff check .` as the step BEFORE
`pytest -q`. Ruff config lives in `services/api/pyproject.toml`: `line-length = 100`,
`[tool.ruff.lint] select = ["E","F","I","UP","B"]`, target-version py312, and there is NO
`per-file-ignores`/`exclude` for `tests/`. So the whole `services/api` tree including
`tests/rules/**` is linted, and E501 (line >100) or F841 (unused variable) in a NEW test
file makes ruff exit 1 -> the api job fails -> "CI green" (S6) is NOT satisfied even if all
tests pass. Seen on M4-T012 (2026-09-13): producer + orchestrator pre-gate ran pytest
(558 passed), modularity (EXIT 0), sync_zr_snapshots --check (EXIT 0) but NONE ran ruff;
the new `test_r1_r2_height_setback.py` had 5 E501 + 1 F841 = 6 ruff errors -> CI api job
would fail on the Ruff step. The accepted discipline-bar files (M4-T006/M4-T014) are
ruff-clean, so a new file with lint errors is BELOW the bar.

**How to apply:** For any task touching `services/api/**`, reproduce CI's exact lint step:
`cd services/api && python -m ruff check .` (or `--statistics`), read the real exit code
(beware pipes: `$?` after `| tail` is tail's exit, not ruff's; use `--statistics` plain or
`${PIPESTATUS[0]}`). Ruff 0.13.0 locally matches CI; target-version is baked into the
config so a 3.11 sandbox reproduces CI's ruff faithfully even though pytest COLLECTION needs
3.12 (PEP 695) for some files. A reproducible ruff failure in a task's new file is a
BLOCKING S6 defect; report it, do not fix it (reviewer is read-only, ADR-005).
