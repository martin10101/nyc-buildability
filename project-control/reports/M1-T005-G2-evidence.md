# M1-T005 — G2 producer self-check evidence (orchestrator-verified)

- **Task:** M1-T005 — property-profile API v1
- **Gate:** G2 (permits submission only)
- **Recorded by:** orchestrator (producer = backend-engineer)
- **Date:** 2026-07-16
- **Producer evidence:** `.claude/worktrees/M1-T005` commit `555db54` on `task/M1-T005-property-profile-api`; full packet at `project-control/reports/M1-T005-producer-report.md` (in worktree commit).

## Producer results

S1–S8 all PASS offline via FastAPI dependency-override fixture transport; HTTP semantics table documented (200/404 no_match/422/502 drift/503/504/500); G5 F1–F4 each fixed with adversarial tests; 39 new tests.

## Orchestrator independent re-run (2026-07-16, worktree)

```
python -m pytest tests -q            → 140 passed in 1.15s
python -m ruff check app tests       → All checks passed!
python .github/scripts/secret_scan.py → PASS -- no findings
```

Matches the producer's claims (their run: 140 passed, ruff clean, validate_contracts 0 failures, scan clean).

## Adjudication items carried to G3/G5

1. **Additive contract keys** (coverage_status, data_completeness, reproducibility on profile objects): producer judged draft-2020-12 open-object semantics permit them (same pattern as accepted M1-T002 source_fact additive keys) and did NOT trigger the needs_split stop rule. G3 must adjudicate whether this respects PRD §32.3 one-canonical-contract or whether a contract minor-version task should be spawned.
2. 404-for-no_match (vs 200-with-state) documented choice; drift→502, timeout→504 mappings.
3. Completeness policy: lotarea + zonedist1 designated critical columns — platform policy, explicitly not legal logic.
4. No-auth G5 condition: endpoint marked INTERNAL/DEV in code + OpenAPI; must not be publicly exposed until M0-T007/T008 auth lands (B-001).
5. Transport-test repointing (5 M1-T002 tests updated for the new no-redirect opener) — G3 must confirm no assertion was weakened.
