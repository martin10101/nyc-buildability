# M0-T092 — G3 delta re-review attestation (verbatim reviewer return)

Saved VERBATIM by the orchestrator from the code-reviewer agent-return channel
(report-preservation rule; transport entity-decoding only). Delta reviewed:
1151a26..4dafa50 (correction round F1–F4 on top of the round-1 identity b940c90).

---

# Delta Re-Review Attestation — M0-T092 (G3)

- **Delta reviewed:** `git diff 1151a26..4dafa50` (confirmed `1151a26` is ancestor of `4dafa50`)
- **Reviewer:** code-reviewer (read-only)
- **Scope:** production changes limited to `tools/agent_supervisor/outage_policy.py` and `tools/agent_supervisor/epoch_lease.py`, plus `tools/test_agent_supervisor_controller_succession.py` and control-plane records/reports. No scope creep; no other production module touched.

## LOW-1 (F1) — RESOLVED
`_REASON_KEYWORDS` is now `(*_BLOCKING_KEYWORDS, *_TRANSIENT_KEYWORDS)` so blocking tokens are scanned first; `classify_reason_text` (body unchanged, still first-match-wins over the reordered tuple) now resolves mixed strings toward BLOCKING. Independently reproduced against the delta source — my three originally-reported strings now all classify BLOCKING:
- `"authentication failed: connection reset"` -> `('auth','blocking')`
- `"billing problem, request timed out"` -> `('billing','blocking')`
- `"revoked access after timeout"` -> `('revoked_access','blocking')`
- also `"rate limit on authentication service"` -> `('auth','blocking')` (transient-first ordering no longer defeats the hold)

No over-blocking regression: unambiguous transient strings still classify TRANSIENT (`"network error"`->network/transient, `"HTTP 429 rate limit"`->rate_limit/transient). All 25 original keywords preserved (11 blocking + 14 transient), none dropped or added. `classify_cause` (known-cause path) and the `unknown->BLOCKING` behavior are unchanged.

## LOW-2 (F2) — RESOLVED
`epoch_lease.may_dispatch_writes` makes `external_effects_reconciled` a keyword-only argument with **no default**, matching `child_handoff.successor_may_dispatch_writes`. Reproduced: omission now raises `TypeError`; `external_effects_reconciled=False` refuses even on an owned-live epoch; `=True` on an owned-live epoch allows. Verified the only callers of this predicate are the succession tests (no production caller existed, so the required-arg change breaks nothing).

## New-defect check — none
- Both edits are the recommended hardening in the fail-closed direction; neither weakens exact-once succession, the state machine, Gate-0, or additive discipline.
- No public interface broke (the sole `may_dispatch_writes` callers are the tests, one of which now asserts the `TypeError`).
- Matrix reproduced: **75 passed** (was 70; +5 targeted tests, including the mixed-reason collision cases with my exact three strings and the `TypeError`-on-omission gate). F3/F4 additions (`expired()` boundary, double-release idempotency, acquire-after-release refusal) are test-only.

Commands run: `python -m pytest tools/test_agent_supervisor_controller_succession.py -q` -> 75 passed; plus a stdin behavioral probe against the delta source (outputs quoted above).

**DELTA VERDICT: PASS**
