# M0-T092 — G4 delta re-review attestation (verbatim reviewer return)

Saved VERBATIM by the orchestrator from the qa-engineer agent-return channel
(report-preservation rule; transport entity-decoding only; HTML entities decoded). Delta
reviewed: 1151a26..4dafa50 (correction round F1–F4 on top of the round-1 identity b940c90).

---

## Delta attestation — M0-T092 correction round (delta 1151a26..4dafa50, on top of the identity I reviewed)

**Reviewer:** qa-engineer (independent, read-only). **Scope:** delta only, against my round-1 findings.

**My own matrix count:** `python -m pytest tools/test_agent_supervisor_controller_succession.py -q` -> **75 passed** (reproduced myself; was 70/70 at round 1, +5).

**Resolution of my findings:**
- **LOW-1 (expired() boundary) — RESOLVED.** `test_expiry_boundary_is_strictly_after_the_deadline` (S2) pins it: at `now == renew_by` (150.0) the lease is `live`/not-`expired`; `now = 150.000001` is `expired`; renewal at the boundary succeeds (renew-by -> 200.0). Source `expired()` unchanged (`>`), now covered.
- **LOW-2 (release idempotency) — RESOLVED.** `test_release_is_idempotent` (S2) releases twice; both `released`, `first == second` (the `return stored` branch is now exercised).
- **LOW-3 (may_dispatch_writes reconciliation gating) — RESOLVED.** `test_write_authority_needs_full_reconciliation` (S5) covers OWN_LEASE_LIVE+effects-reconciled -> True, undrained children -> False, effects=False -> False, and `may_dispatch_writes(outcome)` with no kwarg -> TypeError. Source (F2) makes `external_effects_reconciled` a required keyword (no fail-open default) — I confirmed the change and that no production caller invokes it without the kwarg (only the matrix calls it; `child_handoff.successor_may_dispatch_writes` is the separate mirrored function), so no runtime TypeError is introduced.
- **ADVISORY-3 (acquire_first on a released record) — RESOLVED.** `test_epoch_one_is_taken_at_most_once_even_after_release` (S2): a released record still refuses `acquire_first` with `lease_exists`.

**Other delta items (not mine) sanity-checked for regression:**
- **F1 (blocking-first keyword scan):** `_BLOCKING_KEYWORDS` now scanned before `_TRANSIENT_KEYWORDS`; `test_mixed_reason_text_resolves_toward_blocking` (S11, 5 collision cases) proves mixed reasons resolve to BLOCKING. This is a strictly fail-safer change (ambiguity -> owner hold, matching unknown-fails-closed). The original S11 classification assertions (rate_limit/TRANSIENT, auth/BLOCKING, unrecognized/BLOCKING) still hold in my 75/75 run — no regression.
- **New mutants:** blocking-order-revert (killed by the collision test) and effects-check-dropped (killed by the effects=False assertion) are both meaningful with a killing test — 15/15 credible.

**New defect / coverage regression:** none. The +5 tests are net-additive; the one pre-existing test touched (`test_class_2_anothers_live_lease…`) was correctly updated to pass the now-required `external_effects_reconciled=True` and still exercises the OTHER_LEASE_LIVE False path. Modularity unaffected (test-only + two small source edits). No behavior change outside the corrected surfaces.

**DELTA VERDICT: PASS**
