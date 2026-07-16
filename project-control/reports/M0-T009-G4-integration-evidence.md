# M0-T009 G4 integration evidence (orchestrator-captured)

Merged to main at fe6cc21 (`git merge --no-ff task/M0-T009-contracts-v1`, head 522d3b2). One trivial add/add conflict in `.claude/agent-memory/backend-engineer/MEMORY.md` (both task branches created the index); resolved by combining both lines — no implementation file conflicted.

## Post-merge CI (run 29463721845, push of fe6cc21)

All 4 jobs success (1m12s total):

| Job | Result |
|---|---|
| web (lint + typecheck + build) | success |
| contracts (JSON Schema validation) | success |
| control-plane (workflow regression test, ADR-005) | success |
| api (ruff + pytest) | success |

secret-scan workflow on the same push: success (10s) — first post-merge interaction of the two new workflows, no interference.

## Contracts job log (validator first CI execution)

```
meta-schema engines : stdlib-structural + jsonschema 4.10.3
instance engines    : stdlib mini-validator + jsonschema 4.10.3 (cross-checked)
OK   packages/contracts/schemas/v1/*.schema.json          (6 schemas)
OK   packages/contracts/fixtures/valid/**                 (5 fixtures)
...  (invalid fixtures correctly rejected; job exit 0)
```

## Material finding for M0-T005-R1 (priority raised)

The GitHub runner's preinstalled Python ships **jsonschema 4.10.3** — older than 4.18. Consequences:

1. The G5 adjudication of finding 1 (legacy `RefResolver` fallback in `validate_contracts.py:90-99`) assumed the branch is dead code under jsonschema >= 4.18 and that CI runs pure stdlib. **Both assumptions are false in CI**: 4.10.3 predates the `referencing` package, so the legacy `RefResolver` path is the LIVE path in every CI run.
2. Remaining mitigations still hold: zero remote `$ref`s in shipped schemas (all relative/#-fragment), schemas are review-gated, workflow permissions are `contents: read`. Severity stays LOW, but R1 item 10 (delete or scheme-guard the legacy branch) moves from "hardening" to "required before any schema PR from an untrusted source".
3. The validator's loud engine banner worked exactly as designed — this discovery came directly from it.

## G4 checklist

- Full build/lint/type-check/test suite: PASS (4/4 jobs above)
- Contract compatibility: PASS (validator green on merged main; D4 disclaimer byte-check previously verified)
- Migrations: N/A (no schema/database changes)
- Golden-property regression: N/A (suite does not exist yet)
- Idempotency/retry: N/A
- No duplicate/contradictory implementations: PASS (single validator; ci.yml contracts job path matches)
- Performance: PASS (contracts job ~2s of runtime inside 1m12s total)
- Low-storage/cleanup: PASS (fixtures are small text files; no local artifacts; worktree removed after acceptance)
