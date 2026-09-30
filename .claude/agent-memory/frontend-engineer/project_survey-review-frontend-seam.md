---
name: survey-review-frontend-seam
description: M2-T016 survey-review UI seam + how to mock it in Playwright without a live backend / @ alias
metadata:
  type: project
---

Survey-review frontend (M2-T016, apps/web) patterns worth reusing.

**Why:** these are non-obvious integration seams the orchestrator reconciles
with the real backend, and one Playwright gotcha that would silently break e2e.

**How to apply:**
- ALL survey-review server calls go through ONE typed seam:
  `src/lib/surveyReview/{types.ts,api.ts,context.tsx}`. Components read the
  `SurveyReviewClient` from React context (`useSurveyReviewClient`), never a raw
  fetch. Tests/e2e inject a client; production uses `createHttpSurveyReviewClient`.
  RECONCILED to the shipped slice `services/api/app/documents/review_actions.py`:
  DIGEST-keyed (`document_digest = sha256:<64hex>`, colon URL-encoded), endpoints
  `GET /documents/{digest}/review`, POST `.../facts/{eid}/{accept|correct|reject}`,
  POST `.../{digest}/{confirm|reject|reopen}` (reopen = edge 12; NOT "reextract").
  Mutating handlers return a `ReviewActionResult`, NOT the settled doc, so the
  client RE-READS `/review` after every 2xx mutation (one place in api.ts). Read
  model mirrors `DocumentReviewView`/`FactView` (flat `FactView`, no nested
  `.fact`): `promotable`, `confirm_precondition_met`, `blocking_fact_ids`,
  `downstream_impact` (PER-FACT blocked/provisional; there is no document-level
  conclusions array), `is_unconfirmed_evidence`, `baseline_*`, check COUNTS
  (`check_pass/fail/unresolved`) — no per-check expected/observed in the read.
- The H5 precondition is CONSUMED from `confirm_precondition_met` +
  `blocking_fact_ids` (never computed). Confirm gated on
  `principal.capabilities.can_confirm_document` (owner role decision pending).
- AWAITING-BACKEND fields the read does NOT return: `display_label`/
  `ai_drafted_label` (client humanises `fact_type`), the principal CAPABILITY
  surface (default `capabilities_known:false`, all-enabled + rely on server
  `unauthorized_review_action`), and a review-inbox endpoint. Marked in types.ts,
  never fabricated.
- `accepted_history_fingerprint` is NOT returned by the backend `FactView`; the
  client DERIVES it from `correction_history` via `src/lib/surveyReview/fingerprint.ts`
  — a dependency-free SHA-256 (thin-client: no new deps) over Python-style
  canonical JSON, matching backend `history_fingerprint`. Validated by FIPS
  vectors. Mismatch fails SAFE (`concurrent_review_modification`), never data loss.
  On that error the client re-reads and attaches `currentDocument`.
- reject_fact is PROFESSIONAL-ONLY in the shipped slice (stricter than §5.2);
  a rejected material fact BLOCKS confirm with `confirmation_rejected`
  (`detail.rejected_fact_ids`). Editing a fact on a confirmed doc returns
  `post_confirmation_edit_refused` → guide to reopen first.
- Playwright e2e mocks the client with `page.route('**/api/v1/documents/**')`
  whose handler holds closure store state across requests (real browser, no live
  backend). The reducer lives in `src/test-support/survey-review/mockBackend.ts`
  which imports the app ONLY via `import type` (erased by esbuild) so Playwright
  needs no runtime `@/` alias. `mockClient.ts` (component tests, vitest) wraps the
  REAL http client with a store-backed `fetch`, so the client decode path is
  exercised too. KEEP that type-only split — a value import of `@/lib/...` in the
  e2e-imported module breaks Playwright resolution.
- Internal route gate `INTERNAL_SURVEY_REVIEW_ENABLED` (fail-safe off, 404 when
  unset), mirrors the dashboard/rule-eval flag; it is added to the Playwright
  webServer `env` alongside INTERNAL_RULE_EVAL_UI / INTERNAL_OWNER_DASHBOARD_ENABLED.
- Honesty check discipline: the UI intentionally SAYS "never Verified" in copy, so
  a "no verified" test must assert `getByText("Verified", { exact: true })` count 0
  (a standalone Verified STATUS), not a `/verified/i` substring.
