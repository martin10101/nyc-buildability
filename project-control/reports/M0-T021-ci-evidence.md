# M0-T021 — CI evidence at frozen SHA bd80e72 (orchestrator-captured)

Addresses the non-blocking gate items **G5-L1** and **G4-N1**: the real-uv proof that uv honors the
seeded `--output-file` (including transitive pins like certifi) is the live CI at the frozen code SHA.
Captured by the orchestrator (evidence-capture division of labor) for the reviewers/record.

**Commit:** `bd80e7251537e2a4f57218e91f066064c44e5068` (branch `task/M0-T021-lock-verifier`).
**Result:** all **12/12** required checks GREEN — captured 2026-07-22 while `certifi 2026.7.22` was
published upstream (the exact state that was RED on PR #79 with the pre-fix verifier).

| Conclusion | Check |
|---|---|
| success | Scan repository for credentials |
| success | api (ruff + pytest) |
| success | **api-lock-verify** (requirements.txt is a fresh hash-pinned uv lock) — `lock_requirements.sh --check`, seeded |
| success | **api-tooling-lock-verify** (tooling lock byte-identical + age-gate unit tests) — `lock_tools.sh --check`, seeded; runs `pytest scripts/tests` (28) |
| success | context-budget |
| success | contracts (JSON Schema validation) |
| success | contracts-schema-bundle (runtime schema drift check, byte-identical) |
| success | contracts-typegen (TS drift check, byte-identical) |
| success | control-plane (workflow regression test, ADR-005) |
| success | exact-production-install (Render pip install path + validate_profile + pip-audit) |
| success | web (lint + typecheck + build) |
| success | web-e2e (vitest + Playwright vs recorded-official-fixture API) |

Primary CI workflow run: GitHub Actions run `29891039642` (repo martin10101/nyc-buildability).

**Interpretation:** both lock-verifiers now pass under the hash-pinned uv 0.11.28 on the Linux runner
**despite** certifi 2026.7.22 being available upstream — because the committed lock is seeded as the
existing-output preference and the non-`--upgrade` compile keeps it. A pre-fix (blank-temp) verifier
resolved certifi to 2026.7.22 and failed at this same upstream state (see `M0-T021-diagnosis.md`). This
is the real-resolver confirmation that the offline stub tests could not provide on their own.
