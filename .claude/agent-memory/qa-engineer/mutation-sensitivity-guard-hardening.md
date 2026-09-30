---
name: mutation-sensitivity-guard-hardening
description: How to prove a hardening/attestation-tightening regression test is genuinely mutation-sensitive during a G4 review
metadata:
  type: feedback
---

For a G4 review of a guard-hardening / attestation-tightening task (e.g. "the safe path now
REQUIRES flag=True"), do NOT accept a green regression test at face value. Prove the test is
mutation-sensitive: reconstruct the OLD guard from the parent commit
(`git show <parent-sha>:<file>` into scratchpad) and hand-trace the new test's exact fixture
through BOTH old and new predicate. If the assertions would still pass on the old code, the test
does not force the fix — that's a BLOCKING adequacy gap.

**Why:** a hardening change can ship with a test that only exercises the new-code path, giving
false confidence; the only way to know it locks the fix in is to run the fixture against the old
predicate. On M5-T043 (DB-028 c/d) the old `_elevated_exceptions_checked` returned bare
`all(decisions)` (so empty decisions → vacuous `all(())→True`) and `named_pending` was
`may_touch AND NOT implemented`; the new tests (empty-decisions fixture; hand-built
implemented=False/may_touch=False fixture) each failed all their assertions on the old code —
genuinely mutation-sensitive.

**Also:** a FIXTURE value changed in the same commit as the guard is NOT automatically
test-weakening. Verify the new fixture value matches what the real producer/builder actually
emits. On M5-T043 the shared `OVERRIDE_CLEAR` fixture flipped `implemented=False→True`; that made
it MATCH the builder's real all-clear output (`build_named_street_override_status` emits
`implemented=True, may_touch=False` for the clear path), so it became more realistic, and it was
required to keep the ~475 consumer + 101 wiring tests green under the tightened guard. Confirm the
flip against the builder's return shapes before calling it a hack.

**How to apply:** whenever a task title/scope says "harden", "tighten", "require", "guard",
"fail-closed", or "no longer clears", pull the parent-commit predicate and trace. Confirm the
change is monotonically at-least-as-strict for EVERY producer-emitted shape (only the illegitimate
hand-built shape should change outcome). See also [[named-spawns-are-readonly]]-style discipline:
reviewer stays read-only, reconstruct via `git show`, never check out.
