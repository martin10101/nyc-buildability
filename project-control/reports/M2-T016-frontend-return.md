# M2-T016 — Frontend review screens — producer return (preserved verbatim by orchestrator, transport only)

Producer: `frontend-engineer`. Worktree branch `worktree-agent-a973a7a01a1a58933` @ `99f5cc5` (base main `37667ff`). In scope (`apps/web/**` + tests). No `services/api/app/profile/**` touched; no deps added; one additive Playwright env flag `INTERNAL_SURVEY_REVIEW_ENABLED`.

## Files
- Seam `apps/web/src/lib/surveyReview/`: `types.ts`, `api.ts` (hardened fetch: timeout/abort, runtime validation before render), `validate.ts`, `labels.ts`, `model.ts` (pure urgency ordering, H5 mirror — no legal logic), `errorCopy.ts`, `config.ts` (`INTERNAL_SURVEY_REVIEW_ENABLED`), `context.tsx`.
- Components `apps/web/src/components/survey-review/`: `SurveyReviewScreen`, `DocumentOverlay` (SVG anchored to bboxes + text alt-summary + extraction-unavailable honesty), `FactList`/`FactRow`, `FocusedItem`, `CorrectionForm`, `ReasonForm`, `ChecksPanel` (conflict, unresolvable-by-click), `CorrectionHistory` (immutable side-by-side), `DownstreamImpact`, `ConfirmDocumentPanel`, `StateHistory`, `ReadFailureState`, `StatusBadge`, `ReviewInbox`.
- Routes `apps/web/src/app/survey/review/page.tsx` + `[documentId]/page.tsx` (flag-gated, 404 when off) + `survey-review.css`.
- Tests: vitest (`model/validate/config/api` + `survey-review.test.tsx`) + Playwright (`survey-review-journey` S1/S2/S5/S6, `survey-review-authorization` S3/S4, `survey-review-recovery-a11y` S7) + shared spec-shaped fixtures + stateful mock backend `src/test-support/survey-review/`.

## A11y
Single persistent `OutcomeAnnouncer` live region; programmatic focus to outcome/focused headings; every control labelled; overlay keyboard-focusable + text aria-labels + full text alt-summary; status never by color alone (label+symbol+gloss); reduced-motion honored.

## The FE-assumed API-client interface (RECONCILE against the backend `M2-T016-backend-return.md`)
Isolated in `apps/web/src/lib/surveyReview/{types,api}.ts`. Methods: `readDocument`, `listInbox`, `acceptFact`, `correctFact`, `rejectFact`, `rejectDocument`, `confirmDocument`, `requestReExtraction`. Every mutation is assumed to return the FULL settled `ReviewDocument` (state+facts+downstream).

### Known deltas vs the actual backend contract (to fix in api.ts/types.ts at integration)
1. **Endpoint paths**: FE assumes `/api/v1/documents/{id}/review`, `.../facts/{eid}/accept|correct|reject`, `.../confirm|reject|reextract`, and `GET /api/v1/documents/review-inbox?state=`. Backend actual: `GET /documents/{digest}/review`, POST `.../facts/{eid}/accept|correct|reject`, `.../confirm|reject|reopen`. No inbox endpoint exists in the backend slice yet.
2. **Identifier**: FE uses `document_id`; backend keys on `document_digest = sha256:<64hex>`. Reconcile to the digest (URL-encode the colon).
3. **`reextract` vs `reopen`**: FE has `requestReExtraction`; backend edge 12 is `reopen` (`professionally_confirmed→needs_review`). Map FE action to `reopen`; re-extraction (new upload) is a separate pipeline concern.
4. **Mutation response**: FE expects the full `ReviewDocument`; backend returns `ReviewActionResult` (+ the read endpoint returns `DocumentReviewView`). Either the route returns the settled view, or the FE re-reads after each mutation — decide at integration.
5. **Error-code vocabulary**: FE `reject_code` set (unauthorized | illegal_transition | unauthorized_transition_actor | transition_reason_required | promotion_gate_unmet | correction_tampered | correction_chain_mismatch | correction_no_op | correction_reason_required | stale_history | not_found | validation_error) vs backend actual (`unauthorized_review_action`, `document_record_not_found`, `fact_not_found`, `concurrent_review_modification`, `correction_rejected`, `confirmation_rejected`, `illegal_transition`, `unauthorized_transition_actor`, `transition_reason_required`). Map the FE error copy to the backend codes.
6. **Read-model additions** FE expects (`promotion` verdict, `material`, `display_label`/`ai_drafted_label`, `accepted_history_fingerprint`, `downstream[]`, `principal.capabilities`, `pages[]`, `extraction_available`, `concurrency_token`) mostly correspond to backend `DocumentReviewView`/`FactView` fields (`promotable`, `downstream_impact`, `correction_count`, `confirm_precondition_met`, `blocking_fact_ids`, `location`) — map field names. `display_label`/`ai_drafted_label` are a server-side label-map responsibility (kept out of React per AI-boundary rules) — confirm the read endpoint supplies them.
7. **New confirmation rule (backend rework R1)**: a professionally-rejected fact now BLOCKS `confirm_document` and appears in `blocking_fact_ids` — the FE already renders `blocking_fact_ids`/`confirm_precondition_met`, so this maps cleanly; ensure the confirm panel surfaces the rejected-fact block reason.

## STOPs honored
Qualifying-professional role gated purely on server-derived `can_confirm_document` capability (owner/Tier-D decision §5.5 — not hardcoded); no auto-path to `professionally_confirmed`; no original mutation; **no profile-contract change** (authoritative survey geometry remains the §9.3 STOP — consumed only as honesty signals); no production storage/auth assumed (B-001; identities nullable). No STOP hit.

## Limitation
Could not run npm/tsc/vitest/Playwright locally (thin-client). Written to the repo's existing lint/TS/test conventions; relies on CI. No dependencies added.
