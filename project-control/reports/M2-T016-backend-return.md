# M2-T016 — Backend review-action API slice — producer return (preserved verbatim by orchestrator, transport only)

Producer: `backend-engineer`. Worktree branch `worktree-agent-a8724b1c4277f23fe` @ `5d2ebbb` (base main `37667ff`). Purely additive (6 new files; `git diff --name-only 37667ff 5d2ebbb` = only those 6). Security machinery + profile contract untouched.

## Files added (exclusive scope)
- `services/api/app/documents/review_authz.py` — per-action authorization (closed principal/role, matrix, fail-closed)
- `services/api/app/documents/review_events.py` — audit event envelope + dependent-recalc trigger + downstream-honesty marker
- `services/api/app/documents/review_actions.py` — request/response DTOs, `ReviewStore` Protocol (storage seam), 7 handlers
- `services/api/tests/documents/test_review_authz.py` (SC-S3/S4)
- `services/api/tests/documents/test_review_events.py` (§7–9 shapes)
- `services/api/tests/documents/test_review_actions.py` (SC-S1,S2,S5,S6,S7 + adversarial/illegal-transition tables)

## Evidence (worktree, Python 3.11 sandbox)
- `pytest tests/documents/test_review_authz.py test_review_events.py test_review_actions.py -q` → **181 passed**
- `pytest tests/documents/ -q --continue-on-collection-errors` → **548 passed, 1 skipped, 15 errors** — the 15 are pre-existing PEP-695 collection failures (`units.py:276` on 3.11), none reference the new modules; they collect on CI 3.12. New modules are deliberately 3.11-clean.
- `ruff 0.13.0 check app/documents tests/documents` → All checks passed.
- gitleaks: no leaks. Commit `5d2ebbb`.

## API CONTRACT (frontend reconciles its typed client against this)
Handlers are pure Python in `documents/**` (HTTP router is a separate unit). Suggested REST binding under `/api/v1`; `document_digest` = `sha256:<64hex>`. All requests carry a channel-authenticated `principal { principal_kind ∈ {"human_user","human_qualified_professional"}, actor_id? }` (resolved by the auth channel, **never** from payload) + aware `occurred_at`, optional `correlation_id`.

1. **GET `/documents/{digest}/review`** → `DocumentReviewView`: `{ document_digest, target_bbl, state, state_history[], facts[FactView], confirm_precondition_met, blocking_fact_ids[], original_available, correlation_id }`
   - `FactView`: `{ evidence_id, fact_type, original_value, baseline_normalized_value, baseline_units, normalized_value, units, confirmation_state("unconfirmed"|"confirmed"|"rejected"), confirmation_note, correction_history[], correction_count, check_pass, check_fail, check_unresolved, location(overlay bbox+coordinate_space), page_number, extraction_method, is_unconfirmed_evidence, promotable, downstream_impact }`
   - `downstream_impact`: `{ impact_kind("blocked"|"provisional"), coverage_status("professional_review_required"|"data_conflict"), reason, provenance_digest, provenance_evidence_ids[], analysis_readiness }`
2. **POST `.../facts/{evidence_id}/accept`** (user|professional) → affirm current value; audit `fact_accepted` + recalc; no state change.
3. **POST `.../facts/{evidence_id}/correct`** (user|professional) — `{ corrected_normalized_value, corrected_units, reason(required), accepted_history_fingerprint }` → appends one correction_history entry; `auto_extracted→needs_review` (edge 6); audit `fact_corrected` + recalc.
4. **POST `.../facts/{evidence_id}/reject`** (**professional only**) — `{ reason(required) }` → `professional_confirmation.state=rejected`; `auto_extracted→needs_review`; blocking downstream_impact; audit `fact_rejected` + recalc.
5. **POST `/documents/{digest}/confirm`** (**professional only**) → edges 9/10 `→professionally_confirmed`, **H5-gated**; sets every material fact confirmed. Verdicts computed **server-side** from stored deterministic results — client cannot forge a `PromotionAllowed`. Audit `document_confirmed` + per-fact `fact_confirmed` + recalc.
6. **POST `/documents/{digest}/reject`** (**professional only**) — `{ reason(required) }` → edge 11 `needs_review→rejected` (terminal). Audit `document_rejected`.
7. **POST `/documents/{digest}/reopen`** (**professional only**) — `{ reason(required) }` → edge 12 `professionally_confirmed→needs_review`. Audit `document_reopened` + recalc.

**Typed errors** (`{reject_code, message, …}` via `to_payload()`; suggested HTTP): `unauthorized_review_action`→403 · `document_record_not_found`/`fact_not_found`→404 · `concurrent_review_modification`→409 · `correction_rejected`/`confirmation_rejected`→422 · shipped `illegal_transition`→409 (H5 refusal) · `unauthorized_transition_actor`→403 · `transition_reason_required`→422.

## Seams left for out-of-scope consumers
1. **Buildability recompute** — every mutating action emits `DependentRecalculationRequested(consumer_bound=False)`; recompute worker not in this slice. Trigger is never a silent no-op.
2. **`ReviewStore` Protocol** — the B-001 storage/auth abstraction; only an in-process test store exists. Note: `confirm_document`'s per-fact loop is not transactional in the local store (single-process CI-acceptable) — production needs atomic multi-fact commit.
3. **`analysis_readiness`** left `None` in computed impacts — criticality decided by the profile consumer that knows the dependency graph.

## Flagged decisions (for the gate)
- `reject_fact` is **professional-only** (sets `professional_confirmation=rejected`), following §12 disclosed-slice contract (stricter than §5.2's "a user may reject a detection"). Fail-closed; a user expresses doubt via `correct`(reason) or leaving unresolved.
- Edge-6 demotion actor on correction/rejection of a clean `auto_extracted` doc = `deterministic_pipeline` (const `review-action-correction-trigger`), never a user labelled `qualified_human`; human attributed at fact level + audit event.
- **§9.3 STOP honored**: no authoritative survey-geometry profile surface designed; only honesty signals via existing 1.4.0 `coverage_status`/`analysis_readiness` vocabulary; never imports/writes `profile/**`.

## Confirmations
- Security machinery reused by call only (`state/promotion/isolation/gate/models/correction_history/errors/taxonomy` unmodified). Every gated edge via `promotion_gated_transition`; raw `transition()` never called from a handler.
- Profile contract (1.4.0) consumed only. No production storage/auth assumed (B-001).
