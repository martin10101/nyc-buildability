# M1-T005 — G4 Integration and Regression Evidence

- **Task:** M1-T005 — property-profile API v1
- **Gate:** G4 (integration/regression after merge)
- **Recorded by:** orchestrator (CI evidence)
- **Date:** 2026-07-16

## Integration path

Merge `--no-ff` of `task/M1-T005-property-profile-api` (555db54 + D1 fixup fae2b3f) into main at `ae44554`, after G0/G2/G3/G5 PASS and the G3 D1 blocking condition was satisfied (post-fetch exceptions now yield the documented generic 500; 2 new tests; 142 total, orchestrator re-verified in worktree).

## CI evidence (commit `ae44554`)

- **CI workflow: SUCCESS** — web build, api (ruff + pytest incl. the 142-test suite), contracts validation, control-plane regression all green.
- **secret-scan workflow: SUCCESS** (hardened scanner; pragma suppressions visible).

## Regression

- All M1-T002 connector tests intact (101 baseline preserved inside the 142); contracts untouched (`git diff` empty on packages/contracts); no duplicate implementations; low-storage clean (source-only, offline tests).

## Conditions and follow-ups carried in the ledger

- **No-auth G5 condition:** endpoint is INTERNAL/DEV; must not be publicly exposed or routed production traffic until auth (M0-T007/T008, B-001) lands; render.yaml untouched, all `autoDeployTrigger: "off"`.
- **Contract v1.1 follow-up task (MANDATORY before Priority 4 consumes the additive keys)** per G3 adjudication #1; plus D3 missing_inputs filter policy, G5 N1 boundary sanitization, N2 render.yaml health-path reconciliation — all recorded in the M1-T005 progress ledger entry of 2026-07-16.
