# M4-T004 — G0 readiness

- **Task:** M4-T004 — Pre-endpoint fail-closed safeguards FH-1/FH-2/FH-3.
- **Milestone:** M4. **Depends on:** M4-T002 (merged). **Base:** main `58432cf`.
- **Producer:** rules-engineer. **Reviewers (independent):** code-reviewer (G3), qa-engineer (G4),
  security-reviewer (G5) — all distinct from the producer.
- **Worktree:** `.claude/worktrees/M4-T004-safeguards`, branch `task/M4-T004-safeguards`.

## Why now
Owner directive 2026-07-22: address the recorded FH-1/FH-2/FH-3 safeguards
(`M4-RULES-FUTURE-HARDENING.md`) in the smallest properly controlled task **before** exposing the
rules-evaluation result through any public property-analysis endpoint/UI. Each is a fail-closed
safeguard against an untrusted/ambiguous input reaching the evaluator.

## Scope (three additive fail-closed guards + tests)
- **FH-1** `evaluator.py _valid_iso_date`: reject impossible calendar dates via `datetime.date(y,m,d)`
  in try/except ValueError → malformed `as_of_date` fails closed to `professional_review_required`.
- **FH-3** `integration.py assert_not_verified`: guard `evaluations` / `family_coverage` with an
  isinstance/list check so a foreign non-list payload fails safe instead of raising `TypeError`.
- **FH-2** `registry.py` (and/or the integration selection): CONSERVATIVE fail-closed guard — if >1
  in-effect rule in a family would BOTH apply to the same inputs over overlapping windows, surface
  `professional_review_required`/a typed conflict rather than silently pick or combine. **NOT** a
  `rule_series` redesign (explicit future work); MUST NOT reject legitimate DIFFERENT-applicability
  multi-district families (the G4-L1 constraint).

## Legal-interpretation boundary (principle #1)
FH-2 is legal-adjacent: it affects which rules produce a result. The guard is deliberately
**fail-closed only** — it surfaces ambiguity for qualified professional review; it never makes a legal
pick between overlapping rules. No rule content changes; nothing Published/Verified.

## Readiness checklist
- Requirement refs, evidence files, and the three exact code sites named (packet inputs).
- Exclusive write scope (`allowed_paths` = evaluator.py, registry.py, integration.py, tests/rules/**);
  forbidden: coverage/models/lifecycle, contracts, scripts, lock/manifest, rule JSON, CI. No overlap
  with any open task.
- Acceptance scenarios AS-1..AS-6 recorded (impossible-date, boundary, non-list guard, same-applicability
  overlap fail-closed, different-applicability no-false-positive, regression).
- No unresolved blockers. Additive only; no lock/contract/dependency change.

**G0 verdict: PASS (ready to claim).**
