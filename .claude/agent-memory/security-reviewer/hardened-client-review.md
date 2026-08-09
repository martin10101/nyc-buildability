---
name: hardened-client-review
description: G5 probe set and accepted residuals for the M2-T002 hardened frontend API client (pair matrix, bounded reflection, validate-before-render) in apps/web
metadata:
  type: project
---

M2-T002 baseline (apps/web/src/lib): `contract-matrix.ts` mirrors the backend
STATUS_STATE_MATRIX (10 pairs) and `api.ts` routes ANY undocumented
(status,state) pair to `unexpected_response` using the RAW body state (bounded
form for display only). All error-path reflections go through `bounded.ts`
(600-char text cap + control strip; 64-char `[A-Za-z0-9._-]` token allowlist
for correlation ids/states). 200 bodies are fully shape-validated
(`validate-profile.ts`, bounded 20-problem list) before any render. No
dangerouslySetInnerHTML/innerHTML/eval/storage APIs/console logging anywhere in
apps/web/src; only env read is NEXT_PUBLIC_API_BASE_URL.

**Why:** owner-directed S2 regression (HTTP 500 + state=no_match must never
render as no_match); this client is the pattern later screens will copy.

**How to apply (re-review probe set):** grep apps/web/src for
`dangerouslySetInnerHTML|innerHTML|eval|new Function|localStorage|sessionStorage|indexedDB|document.cookie|console\.` (expect only comments); check every new
render of a LookupOutcome field flows through bounded.ts; replay the recorded
fixture packages/contracts/fixtures/client_regression/http500_state_no_match.json.
Accepted residuals (LOW, M2-T002 G5 report): (1) `isDocumentedPair` encodes the
200-with-no-state pair as key `"200:"`, so a 200 body carrying `state: ""`
aliases the documented pair — harmless today because full profile validation
still gates render, but distinguish ""/absent if the matrix encoding is next
touched; (2) length caps do NOT extend to strings inside a validated 200
profile (identity.geometry.type is unvalidated beyond parent isRecord;
fieldLabel() fallback echoes the raw key; formatValue() JSON.stringify is
unbounded) — React escaping prevents XSS, flood-only. D8/CORS carry-forward
stays open: real API (services/api/app/main.py) has no
expose_headers=X-Correlation-ID and no origins configured; only the e2e
harness (apps/web/e2e/harness/fixture_api.py, localhost-only, GET-only, no
credentials) sets it. See [[cors-header-baseline-review]].
