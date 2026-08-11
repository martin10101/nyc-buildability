# M2-T016 backend — G5 delta re-review (security-reviewer) — VERDICT: PASS (delta); F1 RESOLVED

Saved verbatim by the orchestrator (transport only). Reviewer: `security-reviewer` (independent, read-only).
Delta: `5d2ebbb` (prior reviewed SHA) → `57d8574` (rework head). Additive — only `review_actions.py` +
`test_review_actions.py`; gate modules byte-unchanged vs base `37667ff`. Follows the original G5
(`M2-T016-backend-G5-security-review.md`).

---

## VERDICT: PASS (delta) — F1 RESOLVED

## Reproduction
- `pytest tests/documents/test_review_actions.py test_review_authz.py test_review_events.py -q` → **190 passed** (+9).
- `ruff 0.13.0 check …` → All checks passed.
- Targeted `-k "r1 or r2 or r3 or empty_reason"` → 12 passed.

## Item-by-item
1. **F1 fixed — RESOLVED.** New typed `PostConfirmationEditRefused` (`post_confirmation_edit_refused`) via `_refuse_post_confirmation_edit(record, verb)` when `record.state is PROFESSIONALLY_CONFIRMED`, called at the top of `correct_fact` (:738) and `reject_fact` (:871) — before `load_fact` and any write (fail-closed). Original F1 exploit now refused, doc + value unchanged (`test_r2_fact_edit_on_confirmed_document_is_refused[correct]`/`[reject]` PASS); audited path intact (`test_r2_reopen_then_correct_is_allowed_and_audited` PASS). "Reopening is visible and audited, never silent" now holds.
2. **R1 honesty — CONFIRMED (closes a real residual hole).** `confirm_document` (:972-989) pre-checks: any material fact with `_confirmation_state == REJECTED` raises `ConfirmationRejected` (`confirmation_rejected`, `detail.rejected_fact_ids`) before verdict/transition — fail-closed, no write (the H5 gate alone missed it since a rejected fact is still `PromotionAllowed`). `read_document_review` lists such facts in `blocking_fact_ids`, `confirm_precondition_met=False` (:614-620). Tests PASS. Forge-a-confirmation + principal-from-payload defenses untouched (server-side `store.promotion_verdict`; role from channel-authenticated `principal_kind`; `promotion_gated_transition` sole path; confirmed edges `_HUMAN`-only — all outside the diff).
3. **No new hole — CONFIRMED.** Additive; gate modules byte-unchanged; both refusals fail closed (raise before any write). R3 `original_fact_value` seam returns exactly the one independently-held immutable `original_value` (no bytes, no broader access); strengthens SC-S2 — tampered stored original now detected (`test_r3_…` PASS; fixes prior F4). R4: empty/blank/non-string reason on reject/reopen raises shipped `TransitionReasonRequired`, still fail-closed no write.
4. **F2/F3/F5 correctly DEFERRED (not dropped) — CONFIRMED at code level.** F2 (`confirm_document` still non-atomic: save_document precedes per-fact loop) — open for B-001 transactional store. F3 (CAS token still `expected_correction_history` only) — open for B-001 store. F5 (honesty seams in code: `principal_kind` = channel-resolved never payload; verdicts server-side; `ReviewStore` B-001-honest) — carries the route requirement. **Recommend the orchestrator confirm F2/F3/F5 are logged against the future B-001 route/store task before closing.**

## Minor observation (non-blocking, not a finding)
`_refuse_post_confirmation_edit` guards only `PROFESSIONALLY_CONFIRMED`, not terminal `REJECTED`. Editing a fact on a `rejected` (dead/terminal, never consumed as authoritative) document is still possible — no masquerade, no security impact. Noted for completeness.

## Summary
F1 RESOLVED; R1/R3/R4 verified fail-closed improvements; R1 closes the residual rejected-fact-into-confirmed hole; R3 fixes prior F4; no new holes; forge/principal defenses intact; gate modules byte-unchanged; 190 passed; ruff 0.13.0 clean. F2/F3/F5 correctly deferred to the B-001 route/store task. **VERDICT: PASS (delta); F1 RESOLVED.**
