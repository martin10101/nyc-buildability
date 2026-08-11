# M2-T016 backend — G3 delta re-review (code-reviewer) — VERDICT: PASS (delta); C1 RESOLVED

Saved verbatim by the orchestrator (transport only). Reviewer: `code-reviewer` (independent, read-only).
Delta reviewed: `5d2ebbb` (prior reviewed head) → `57d8574` (rework head), branch `worktree-agent-a8724b1c4277f23fe`.
Follows the original G3 (PASS with blocking C1) in `M2-T016-backend-G3-code-review.md`.

---

# Gate Report (delta re-review)
- Gate ID: G3 (independent code review — delta re-verification of C1 rework)
- Result: **PASS (delta) — C1 RESOLVED**
- Delta: exactly 2 files (`review_actions.py`, `tests/documents/test_review_actions.py`).

## Steps independently executed
1. `git diff --name-only 5d2ebbb 57d8574` → only the 2 files. Read full diff.
2. `pytest tests/documents/test_review_actions.py test_review_authz.py test_review_events.py -q` → **190 passed** (181→190, +9).
3. `ruff 0.13.0 check …` → All checks passed.
4. `pytest test_review_actions.py -v -k "r1_ or r2_ or r3_ or empty_reason"` → 12 passed.

## Verification (expected vs actual)
1. **C1 fixed — CONFIRMED RESOLVED.** `confirm_document` (review_actions.py:972-988) computes `rejected_ids` (material facts with `_confirmation_state is ProfessionalConfirmationState.REJECTED`) and raises `ConfirmationRejected` (`reject_code="confirmation_rejected"`, `detail.rejected_fact_ids`) BEFORE verdict computation / `_advance_document` / the per-fact confirmation loop — independent of the H5/promotion verdict (a rejected fact is still `PromotionAllowed`, why the gate alone missed it). `read_document_review` (:617-622) adds a fact to `blocking` when `verdict is PromotionRefused OR confirmation_state is REJECTED`, so `blocking_fact_ids` lists it and `confirm_precondition_met` is False. Proven by `test_r1_professionally_rejected_fact_blocks_confirmation_and_is_not_overwritten` + `test_r1_read_model_lists_rejected_fact_as_blocking`. The prior failing behavior (`confirmed` after confirm) is now impossible.
2. **R3 (was A1) — CONFIRMED.** New `ReviewStore.original_fact_value(digest, evidence_id)` seam (:250-258); `correct_fact` fetches `expected_original` independently (:774-780); test store snapshots originals at ingest, never updates on correction. `test_r3_tampered_stored_original_is_detected_by_correction_cross_check` → `validate_correction_history` fires → `CorrectionRejected` (`unresolved_correction_history`), no write. Real, not tautological.
3. **R4 (was A2) — CONFIRMED.** `reject_document` (:1089) / `reopen_document` (:1146) drop the fact-level reason pre-check; empty reason flows into `promotion_gated_transition`→`transition` raising the shipped `TransitionReasonRequired` for edges 11/12. Parameterized over ""/whitespace. PASS.
4. **Regression tests (+9) — CONFIRMED genuine.** Each names + proves its invariant (state, `rejected_fact_ids`, `blocking_fact_ids`, `confirm_precondition_met`, `reject_code`, no-write). All 12 targeted PASS; full 190 PASS.
5. **No regression / still safe — CONFIRMED.** Delta = 2 files. Security machinery untouched. Raw `transition()` still never called from a handler; every edge via `promotion_gated_transition`. R1 refusal is pre-write; R2 `_refuse_post_confirmation_edit` (:556-570) adds a fail-closed guard on `professionally_confirmed` (closes a prior latent silent-edit hole), `auto_extracted`/`needs_review` unchanged. `test_sc_s5_…` still passes.

## R2 note (G5-owned)
R2 (`post_confirmation_edit_refused`; correct/reject refused on a confirmed doc until an explicit audited reopen) is consistent with spec §4 edge 12 and adds no regression; verdict on R2/F1 deferred to G5.

## Defects
None in the delta. C1 resolved; A1/A2 addressed (R3/R4). A3 (principal-from-auth = route wiring) and A4 (CAS token = correction_history) remain non-blocking, unchanged by this delta.

**VERDICT: PASS (delta); C1 RESOLVED; no new finding.**
