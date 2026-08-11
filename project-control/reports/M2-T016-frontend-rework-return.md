# M2-T016 — Frontend rework — producer return (preserved verbatim by orchestrator, transport only)

Producer: `frontend-engineer`. Worktree branch `worktree-agent-a973a7a01a1a58933` @ `dc8c5de` (parent `99f5cc5`, base `37667ff`). `apps/web/**` only; no new deps (SHA-256 hand-rolled to avoid one); gitleaks clean.

## A — Reconciled api-client to the backend contract (57d8574)
Endpoints (digest-keyed, colon URL-encoded): `GET /api/v1/documents/{digest}/review`→`DocumentReviewView`; POST `…/facts/{eid}/accept|correct|reject`; POST `…/{digest}/confirm|reject|reopen` (`reopenDocument` was `requestReExtraction`; edge 12). Mutations return `ReviewActionResult` → client **re-reads** `/review` after every 2xx (single place `finishMutation`→`reReadAsAction`) and renders the settled `ReviewDocument`. Read-model fields mirrored 1:1 flat (`promotable`, `confirm_precondition_met`, `blocking_fact_ids`, per-fact `downstream_impact`, `correction_count`, `is_unconfirmed_evidence`, `baseline_*`, `check_pass/fail/unresolved`, `location`, `state_history`, `confirmation_state`). Error codes 1:1 (`unauthorized_review_action`, `document_record_not_found`, `fact_not_found`, `concurrent_review_modification`, `correction_rejected`, `confirmation_rejected`+`detail.rejected_fact_ids`, `illegal_transition`, `unauthorized_transition_actor`, `transition_reason_required`, `post_confirmation_edit_refused`). New semantics: `confirmation_rejected` lists blocking rejected facts in the confirm panel; `post_confirmation_edit_refused` → the panel offers **Reopen** as the one next action.

## AWAITING-BACKEND read-model gaps (honest degradation; bind to the follow-up HTTP-route/read-model-assembly task, B-001-blocked)
1. **`FactView` has no `history_fingerprint`** — the FE currently derives `accepted_history_fingerprint` from `correction_history` via a dependency-free SHA-256 over Python-style canonical JSON (`fingerprint.ts`) to match backend `history_fingerprint`. **Recommend the backend expose the fingerprint on `FactView`** so the FE echoes it (eliminates the fragile reproduction). Producer states a mismatch fails safe (`concurrent_review_modification`, no data loss) — under code review.
2. `FactView` has no `display_label`/`ai_drafted_label` — FE humanises `fact_type` (label map belongs server-side per AI-boundary rules).
3. **Read returns no principal-capability surface** — FE defaults `capabilities_known:false` (all-enabled) + relies on server `unauthorized_review_action` (403). **Recommend the read model expose per-action capabilities** so the UI disables unauthorized actions up front (SC-S3 clarity in production).
4. **No review-inbox endpoint** — `listInbox` seam preserved; UI degrades to honest empty/failure.
5. Read exposes check counts + `downstream_impact.reason` but no per-check `expected`/`observed` — conflict panel shows the plain-language reason (numeric expected/observed not fabricated).

## B — Human-journey fixes
- **F1**: `model.ts` `openItemCount`/`dominantAction` — clean-but-`unconfirmed` facts no longer "open"; dominant action flips to "confirm or reject" once `confirm_precondition_met`.
- **F3**: correction draft lifted above the `FocusedItem` remount boundary; on `concurrent_review_modification` re-read keeps the editor open with the preserved draft + persistent `stale-notice`.
- **F2**: Accept shows a session affirmation marker; copy says "recalculation … was requested" (no false "recalculated").
- **F4**: overlay marks carry a non-color cue — dashed (conflict) / dotted (unresolved) stroke + a status glyph.
- **F5**: `coerceToSampleType` keeps numeric facts numeric on correction.

## Tests added
F1: `model.test.ts` + component + e2e confirm-flip. F3: component "keeps unsaved correction input when the item changed underneath" + `api.test.ts` stale round-trip. Plus `fingerprint.test.ts` (FIPS SHA-256 vectors + history_fingerprint behavior) and reconciled `api.test.ts` (post_confirmation_edit_refused→reopen, confirmation_rejected+rejected_fact_ids, H5 gate, preparer authz).

Limitation: no local npm/tsc/vitest/Playwright (thin client) — relies on CI.
