# M2-T016 backend slice — G3 code-review gate (code-reviewer) — VERDICT: PASS (C1 blocking for acceptance)

Saved verbatim by the orchestrator (transport only) per the report-preservation rule. Reviewer:
`code-reviewer` (independent, read-only; ≠ producer `backend-engineer`). Reviewed producer worktree branch
`worktree-agent-a8724b1c4277f23fe` @ `5d2ebbb` (base main `37667ff`). Per gate-verdict semantics, recorded
PASS with **C1 a blocking required correction** gating acceptance/next gate.

---

# Gate Report

- Gate ID: G3 (independent code review)
- Task ID: M2-T016 (backend review-action API slice, Packet C / U1)
- Reviewer: code-reviewer (independent; read-only)
- Producer: backend-engineer
- Result: **PASS** — with one blocking required correction (C1) that must be resolved before acceptance

## Steps independently executed
1. `git -C .claude/worktrees/agent-a8724b1c4277f23fe diff --name-only 37667ff 5d2ebbb` → exactly the 6 named files. Additive confirmed; no existing file modified.
2. Read all 3 new modules + 3 new tests; read shipped `state.py`, `promotion.py`, `correction_history.py`, `models.py`, `errors.py`.
3. `python -c "import app.documents.review_actions, review_authz, review_events"` → IMPORT_OK under 3.11 (import chain avoids PEP-695 `units.py`).
4. `pytest tests/documents/test_review_actions.py test_review_authz.py test_review_events.py -q` → 181 passed (reproduces producer evidence).
5. Reproduced the reject→confirm interaction using the shipped code.

## Verification points (expected vs actual)
1. Additive-only / reuse — PASS. No shipped module edited/reimplemented; all security logic called (`promotion_gated_transition` review_actions.py:70-76,:445; correction-history validators :704/:724/:728; `PromotionAllowed/Refused` :59; record re-validated via `dataclasses.replace` :453-458).
2. Gated transitions — PASS. Raw `transition()` never imported/called; every edge via `_advance_document`→`promotion_gated_transition` (:429-458). Illegal edges fail closed (`IllegalTransition`).
3. Immutability — PASS (SC-S2). `correct_fact` preserves `original_value` (not in the request DTO); correction is an append (`validate_history_extension`); read view returns original + baseline beside the chain. (See A1: `expected_original` cross-check is tautological.)
4. Authorization / no-auto-confirm — PASS (SC-S3/S4). Principal is closed `CorrectingPrincipal` resolved by the channel, never a payload role; `professionally_confirmed`/per-fact confirmed only via `_PRO`-only rows + H5 gate; verdicts server-computed via `store.promotion_verdict`→`evaluate_promotion`; client cannot submit a `PromotionAllowed`; import-time completeness guard.
5. Dependent-recalc — PASS (SC-S5). Every mutating handler emits `enqueue_recalc` and returns the trigger; `consumer_bound=False` is an honest, tested seam.
6. Error handling — PASS. Short typed errors with stable `reject_code` + structured payload; dual concurrency guard (`history_fingerprint` + `save_fact` CAS); fail-closed.
7. Tests — PASS. Parameterized adversarial tables; each names its invariant; assertions meaningful. One coverage gap correlates with C1.
8. Correctness/maintainability — PASS with C1. `ReviewStore` Protocol + recalc/`analysis_readiness` seams documented and honest. Flagged decisions defensible (reject_fact professional-only; edge-6 actor = deterministic_pipeline). Exception: confirm/reject interaction — C1.

## Reproduced defect (C1)
Fully-resolved facts in `needs_review`; a professional rejects one, then confirms the document:
```
after reject, ev-1 confirmation = rejected
read model blocking_fact_ids   = ()
read model confirm_precondition= True
doc state after confirm        = professionally_confirmed
ev-1 confirmation AFTER confirm = confirmed        <-- rejection silently overwritten
per_fact_confirmations         = ('ev-1', 'ev-2')
```
Because `promotion_verdict` weighs only deterministic validator results (not the professional rejection), a rejected-but-resolved fact is `PromotionAllowed`, so (a) the read model never lists it in `blocking_fact_ids`/`confirm_precondition_met` (review_actions.py:577-578,:611), and (b) `confirm_document` unconditionally overwrites each material fact's `professional_confirmation` to `confirmed` (:937-965, esp. :947-952). Net: a detection the professional marked unusable is silently relabeled "confirmed" inside a `professionally_confirmed` document, with no audited reversal. Contradicts spec §7.2/§10.4 and the no-silent-defaults doctrine. It faithfully implements the literal §12 table — §12 vs §7.2/§10.4 is a genuine spec tension the fix should reconcile.

## Defects
- **C1 (blocking, required before acceptance):** `confirm_document` + read model do not treat a professionally-rejected material fact as blocking, and confirm silently overwrites its `rejected` state to `confirmed`. Remediate by either: refuse confirmation while any material fact's `professional_confirmation.state == rejected` (and add it to `blocking_fact_ids`/clear `confirm_precondition_met`), or require an explicit audited un-reject before the fact can be confirmed; add a spec §12 note reconciling with §7.2/§10.4; add a regression test (`reject resolved fact → confirm refused`).
- **A1 (advisory):** `correct_fact` passes `expected_original=OriginalValueReference(fact.get("original_value"))` against `original_value=fact.get("original_value")` (:728-735) — same source, so the immutability tamper-check can never fire. Immutability still holds structurally; supply an independently-held original from the immutable-original store so the check is real.
- **A2 (advisory):** Empty reason on `reject_document`/`reopen_document` raises `CorrectionRejected` (`correction_rejected`) instead of the shipped `TransitionReasonRequired` (`transition_reason_required`). Fail-closed; only the label is off-domain.
- **A3 (advisory / hand-off):** Principal-from-auth is a convention at this layer — `ReviewPrincipal` embedded in each request DTO. The FastAPI route must populate it from auth context, never the request body.
- **A4 (advisory):** reject_fact/confirm_document use `expected_correction_history` as the CAS token but mutate `professional_confirmation`, not `correction_history`, so two concurrent confirmations/rejections aren't detected as conflicting. Low impact.

## Regression/security/provenance
No profile-contract mutation; DownstreamImpact/coverage use existing 1.4.0 wire strings only, validated closed; provenance mandatory; B-001-honest; audit payloads metadata-only. Good.

## Reviewer conclusion
Strictly additive; reuses shipped machinery without reimplementation; all edges via `promotion_gated_transition`; corrections append-only and originals immutable; verdicts server-computed with no AI/confidence channel; honest seams; strong adversarial tests (181 passed, reproduced). One safety-relevant honesty gap — a professional rejection silently overwritten to "confirmed" during document confirmation (C1) — must be corrected/reconciled before acceptance. **VERDICT: PASS; C1 is a blocking required correction gating acceptance.**
