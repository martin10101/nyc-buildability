# M0-T048 G2 self-check (producer evidence + orchestrator reproduction)

**Task:** M0-T048 - close G5-C2 (owner am.14, D-010 R134-R143).
**Recorded by:** orchestrator (role: self_check). **Date:** 2026-08-08 (UTC).
**Code identity:** branch `task/M0-T048-c2-close`, head `ec0f55d28da90d57467321ad65c922fdde09f043`
(base = origin/main `9c2ec25`, which contains accepted M0-T046); merged into the control branch as
`360dc50` so the submit/gate/accept identity covers the reviewed code from the start.

## Producer self-checks (from M0-T048-producer-report.md)

- Full suite AFTER: 1374 passed / 2 skipped (baseline at branch base: 1363 / 2; delta +11).
- Touched-module subset: 215 passed; new C2 file alone: 10 passed.
- Design: hybrid of BOTH owner R137 candidates - deterministic timestamp-free forwarded body
  (pure function of the five approval_digest-covered fields, canonicalised identically),
  FORWARDED-AT stamped only at actual forward time, approved_digest bound to the OPERATOR-NAMED
  digest, verify_covered_instruction reconstruction check at approve AND resume with distinct
  fail-closed reason codes (pending_prompt_uncovered vs pending_prompt_tampered).
- Determinism inventory: one non-covered non-clock input found (packet_reference, deliberately
  outside approval_digest per ApprovalDigestStabilityTests) - REMOVED from the forwarded body
  (provenance retained in outbox payload/audit); every remaining byte derives from
  operator-covered material + the forward-time clock stamp (excluded from the binding).
- Non-vacuity: test_non_vacuity_pre_fix_checks_pass proves the two-field forgery satisfies BOTH
  pre-fix acceptance predicates (pre-fix code would have forwarded the injection).
- R139(d) grep-proof: no forwarding-guard/activation/tier surface changes.

## Orchestrator reproduction (independent execution, this session)

1. **Scope check:** worktree diff = 8 paths (codex_reviewer.py, loop.py, cli.py, 4 test files,
   producer report), all inside packet allowed_paths; no forbidden-path or manifest edits.
   Committed `ec0f55d` with exact-path staging; merged to control branch `360dc50` cleanly.
2. **Targeted tests:** c2_binding + park_approve_binding + pending_prompt + reviewer
   -> 112 passed in 12.72s.
3. **Full suite reproduced:** 1374 passed / 2 skipped in 86.28s - matches the producer exactly;
   zero regressions; the 2 skips are the pre-existing POSIX guards.
4. **IDE diagnostics triage:** the batch of Pyright items raised during the increment reproduces
   the established stale/pre-existing pattern (run_unit, model_available tuple, os_acl import
   resolution - all present on origin/main pre-task); the "Expected 0 positional arguments" items
   at loop.py:1706/1719/1784 point at ordinary machine.transition/self._touch call sites inside
   untouched control flow and do not reproduce as runtime failures anywhere in the 1374-test
   suite, which exercises those paths.
5. **Evidence-map completeness:** M0-T048-evidence-map.json carries a row for EVERY bound
   requirement D-010-R134..R143, including the conduct/sequencing rows (R142/R143).

## Known open items handed to the independent gates

- **Old-shape refusal coverage (AS-6):** the producer reports distinct reason codes
  (pending_prompt_uncovered / pending_prompt_tampered) with FailClosedReasonCodes tests -
  reviewers should specifically confirm an OLD-shape record (parked pre-fix, no
  approved_instruction) refuses and can never fall back to journal-resident-only verification.
- **Canonicalisation equivalence:** verify the reconstruction canonicalisation (sorted paths/
  stops, stripped action) is exactly the approval_digest canonicalisation - any divergence would
  be a fail-closed false-refusal (availability) or worse a bypass (soundness). G3/G5 question.
- **packet_reference removal:** confirm removing it from the forwarded body loses no
  load-bearing reviewer context (it remains in outbox payload/audit); G4 evidence question.

**G2 result: PASS (self-check + orchestrator reproduction consistent; independent G3/G4/G5 + DCV
proceed on this identity).**
