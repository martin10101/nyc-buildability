# M1-T002 — G4 Integration and Regression Evidence

- **Task:** M1-T002 — PLUTO SODA connector
- **Gate:** G4 (integration/regression after merge)
- **Recorded by:** orchestrator (CI evidence)
- **Date:** 2026-07-16

## Integration path

- Merge `--no-ff` of `task/M1-T002-pluto-soda-connector` (base `9e22839` + review-fixup `fe87b99`) into main at `4a3537a`.
- Post-merge hardened secret-scan flagged the fake token in the leak-absence test → pragma-allowlisted with visible notice (`3ffa9f9`); the pragma comment then broke ruff E501 in CI → shortened (`69b5509`). Both incidents are the new hardening working as designed; history preserved.

## CI evidence (commit `69b5509`, full connector + fixup integrated)

- **CI workflow: SUCCESS** — jobs: web (lint+typecheck+build) ✓, api (ruff + pytest, 101 tests incl. 61 connector tests) ✓, contracts (JSON Schema validation) ✓, control-plane (ADR-005 workflow regression) ✓.
- **secret-scan workflow: SUCCESS** (hardened M0-T005-R1 scanner; 6 justified pragma suppressions repo-wide, all visible in the log).
- Local orchestrator re-runs matched at every step (pytest 101 passed; validate_contracts 0 failures; ruff clean; scan exit 0).

## Regression

- Pre-existing suites unaffected (test_health, contracts fixtures, control-plane test all green).
- No duplicate/contradictory implementations (single connector module; contracts untouched).
- Low-storage: fixtures 273 KB committed text; producer temp dir `%TEMP%\pluto_cap` deleted; no persistent local artifacts.
- Idempotency: fixture-driven determinism tests (S6) green in CI.

## Carried forward (non-blocking, tracked in M1-T005 packet)

G5 F1–F4 hardening (bounded read, RecursionError guard, redirect pinning, errorCode sanitization) + F5 logging guidance; G3 carry-forwards (no_match is a result; confidence never maps to coverage; persist conflicts/drift_signals/absent_columns; drift-monitor hook).
