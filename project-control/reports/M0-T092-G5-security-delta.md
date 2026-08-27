# M0-T092 — G5 delta re-review attestation (verbatim reviewer return)

Saved VERBATIM by the orchestrator from the security-reviewer agent-return channel
(report-preservation rule; transport entity-decoding only). Delta reviewed:
1151a26..4dafa50 (correction round F1–F4 on top of the round-1 identity b940c90).

---

# Delta Re-Review Attestation — M0-T092 (G5 security)

- **Reviewed delta:** `1151a26..4dafa50` (correction round on top of the b940c90 identity I passed)
- **Scope:** delta only — F1 (classification ordering), F2–F4 (`may_dispatch_writes` keyword-required + tests). Read-only.

## LOW-1 (F1) — resolved fail-closed: YES

- `outage_policy.py:55-81` now defines `_BLOCKING_KEYWORDS` and `_TRANSIENT_KEYWORDS` separately and builds `_REASON_KEYWORDS = (*_BLOCKING_KEYWORDS, *_TRANSIENT_KEYWORDS)`. The `classify_reason_text` body is **unchanged** (still first-match-wins over `_REASON_KEYWORDS`), so a blocking token anywhere now outranks every transient token.
- Traced my exact reproduced case through the new order: `"Authentication error: connection refused by auth endpoint (401)"` -> `_BLOCKING_KEYWORDS` scanned first -> `"401"` matches before any transient token -> `("auth", BLOCKING)`. The former `("network", TRANSIENT)` misclassification is gone. Locked in by the new `test_mixed_reason_text_resolves_toward_blocking` (5 cases, including my verbatim string), and `test_the_classification_is_closed_and_fails_closed` still passes the transient/unrecognized cases.
- **Direction check (no new hole):** the residual ambiguity now moves TRANSIENT->BLOCKING (a transient message that also mentions billing/auth is held for the owner instead of retried). That is the safe direction — R033 forbids a retry loop for auth/billing/revoked/incompatibility — and matches the module's unknown-fails-closed stance. No unlimited loop, no dispatch bypass, no fail-open introduced.

## F2 (my/G3 concern on the one permissive default) — resolved fail-closed: YES

- `epoch_lease.may_dispatch_writes` (`epoch_lease.py:350-357`): `external_effects_reconciled` lost its `= True` default and is now a required keyword-only argument. Omitting it raises `TypeError` (asserted by `test_write_authority_needs_full_reconciliation`) rather than silently assuming "reconciled." This closes the single fail-open door in the succession write-authority path.
- All call sites verified: the only callers of `epoch_lease.may_dispatch_writes` are the matrix tests, each passing `external_effects_reconciled` explicitly; `child_handoff.successor_may_dispatch_writes` is a distinct, unchanged function. No live-loop caller exists — **SHADOW-ONLY posture is intact**.

## New security concerns introduced by the delta: NONE

The delta touches only classification keyword ordering, one keyword-required parameter, and tests. No new imports, no subprocess/network/exec surface, no guard-pack/hook/settings change, no fixture or path change, zero new dependencies. Public-repo hygiene unaffected (the other changed files are control-plane gate records/reports). My ADVISORY-2 (journal `reason` re-redaction boundary) and ADVISORY-3 (diagnosis terminal-escaping) remain correctly carried as live-wiring-time residuals — appropriate while shadow-only.

DELTA VERDICT: PASS
