# M2-T002 Producer Report — Confirm screen (PRODUCT_FLOW step 2) with hardened API client

- **Task ID:** M2-T002
- **Producer:** frontend-engineer
- **Status requested:** `awaiting_gate` — with the explicit statement that **CI on the task PR is the executable proof**. The owner PC (~1.7 GB free) permits no npm install/build/test and none was performed; every claim below about runtime behavior is "designed and statically self-reviewed, to be proven by the named CI job", not "executed locally".
- **Branch / worktree:** `task/M2-T002-confirm-screen` in `.claude/worktrees/M2-T002` (all edits inside `apps/web/**` plus this report; verified via read-only `git status --porcelain` — output reproduced in section 8).
- **Report path:** `project-control/reports/M2-T002-producer-report.md` (this file, written in the worktree).

## 1. Files changed

Modified (17):
- `apps/web/src/lib/api.ts` — hardened client (pair matrix, runtime validation, bounded reflection, AbortController + timeout)
- `apps/web/src/lib/format.ts` — complete 108-column FIELD_LABELS with provenance note (D1)
- `apps/web/src/lib/missing-inputs.ts` — `extractSharedReason` (D4); contract import
- `apps/web/src/lib/coverage.ts`, `apps/web/src/lib/provenance.ts` — retargeted to generated types (`SourceFact` replaces `ProvenanceRecord`)
- `apps/web/src/test-support/fixtures.ts` — recorded CR-500-no_match fixture wired at the fetch-stub level per its `_consumed_by` note
- `apps/web/src/app/globals.css` — responsive 360/768/1280 rules, table-scroll, legend, confirm grid (D2/D3)
- `apps/web/src/app/property/page.tsx` — shared InternalBanner
- `apps/web/src/components/property/{PropertyLookup,FailureState,MissingInputsSection,ZoningSection,ConflictsSection,UnsupportedSection,FactsTable,ProvenanceDisclosure,CoverageBadge,ProfessionalReviewPanel}.tsx`
- `apps/web/src/components/property/__tests__/{property-lookup,sections}.test.tsx`, `apps/web/src/lib/__tests__/{api,missing-inputs}.test.ts`

Added (15):
- `apps/web/src/lib/contract.ts` — generated-type re-exports + contract-locked runtime enums + open-object runtime narrowing
- `apps/web/src/lib/contract-matrix.ts` — verbatim client mirror of the backend `STATUS_STATE_MATRIX`
- `apps/web/src/lib/validate-profile.ts` — runtime validator for every 200 body
- `apps/web/src/lib/bounded.ts` — length-capped, control-stripped, token-allowlisted reflection
- `apps/web/src/components/property/CoverageLegend.tsx` (D3), `apps/web/src/components/property/InternalBanner.tsx`
- `apps/web/src/components/confirm/ConfirmScreen.tsx`, `apps/web/src/app/property/confirm/page.tsx` — the step-2 screen
- Unit tests: `src/lib/__tests__/{contract-matrix,validate-profile,bounded,format}.test.ts`, `src/components/confirm/__tests__/confirm-screen.test.tsx`
- E2E: `e2e/{client-hardening,confirm-journey,responsive-a11y}.spec.ts`

Deleted (1):
- `apps/web/src/lib/property-profile.ts` — the handwritten profile type module is RETIRED (grep confirms zero remaining imports; only prose mentions survive).

**Not touched:** `services/**`, `packages/contracts/**`, `render.yaml`, `docs/**`, `.github/workflows/ci.yml`, other `project-control/**`, `.claude/**`. **No ci.yml change is needed**: the new vitest suites match the existing `src/**/*.test.{ts,tsx}` include and the new Playwright specs sit in the existing `testDir: ./e2e`, so the current `web` and `web-e2e` jobs pick them up automatically.

## 2. Contracts consumed / changed

- Consumed: `packages/contracts/generated/property_profile.ts` (M2-T003 output) is now the ONLY profile type vocabulary. `src/lib/contract.ts` re-exports it **type-only** (`import type`, erased at build time, so `next build` never compiles files outside `apps/web`) and derives all named aliases by indexed access (`Conflict = PropertyProfile["conflicts"][number]`, etc.). Runtime enum arrays are locked to the generated unions with `satisfies` **plus a two-way exhaustiveness assertion type** — any future contract enum change fails `tsc` here. This automatically widened the stale handwritten `contract_version` pin `"1.0.0"|"1.1.0"` to the generated `"1.0.0"|"1.1.0"|"1.2.0"`.
- Consumed: `services/api/app/api/v1/properties.py::STATUS_STATE_MATRIX` (read-only) mirrored verbatim as `DOCUMENTED_STATUS_STATE_PAIRS` (10 pairs, 200 recorded with the `null` sentinel exactly like the backend's `None`).
- Consumed: `packages/contracts/fixtures/client_regression/http500_state_no_match.json` at BOTH levels its `_consumed_by` note names: vitest fetch-stub (`cr500NoMatchResponse()` in `src/test-support/fixtures.ts`, replaying recorded status/headers/body) and Playwright network layer (`route.fulfill` with the recorded document in `e2e/client-hardening.spec.ts`).
- No schema, API, or contract file was created or edited.

## 3. Scenario-by-scenario implementation and proof

All proofs run in CI: **`web`** = lint + typecheck + `next build`; **`web-e2e`** = vitest (all unit suites) + Playwright against the recorded-official-fixture harness (`e2e/harness/fixture_api.py`, unchanged — real FastAPI app, real builder, committed official PLUTO captures).

| Scenario | Implementation | Proof (test file → CI job) |
|---|---|---|
| S1 primary | Confirm screen reachable from the profile's single next action (`confirm-link`); compact card: identity + honest BIN/geometry, lot/building summaries with units + coverage badges + per-fact provenance drill-down, zoning chips (split-zone R3-2/C4-1/GI), landmark/flood values from the F05 capture, honest pending-actions row, conflicts, always-visible legend, questions section | `e2e/confirm-journey.spec.ts` (4 journeys) → web-e2e; `confirm-screen.test.tsx` → web-e2e (vitest) |
| S2 BLOCKING (owner-directed) | Exact pair enforcement in `api.ts`: RAW body state (never sanitized-before-compare, so control characters cannot launder a state) checked against the mirrored matrix; any mismatch → `unexpected_response` with HTTP status, bounded received-state token, and correlation id. (500, no_match) is structurally absent from the matrix — it can never reach the no-match renderer | Recorded fixture at fetch-stub level: `api.test.ts` "S2 BLOCKING" + 7 undocumented-pair cases; component level: `property-lookup.test.tsx` S2 test; browser network level: `client-hardening.spec.ts` S2 tests; matrix identity hardcoded independently in `contract-matrix.test.ts` → both CI jobs |
| S3 malformed 200 | `validate-profile.ts` checks every documented key/type/enum of the generated types before anything renders; failure returns only a bounded problem list (`validation_failure` state); the e2e mutates a REAL builder payload via `route.fetch()` then edit — not an invented document | `validate-profile.test.ts` (5 valid + 14 rejection classes); `property-lookup.test.tsx` S3; `confirm-screen.test.tsx` S3; `client-hardening.spec.ts` two S3 journeys (removed required key; unpublished contract_version `9.9.9`) → web-e2e |
| S4 D5 + cancellation + timeout | Last-good result held separately from form error: client-invalid submit keeps the profile rendered with the inline error, error clears on retype; each lookup aborts the previous request (AbortController; `aborted` outcome ignored + monotonic seq); 12s budget → recoverable `client_timeout` state with retry | `property-lookup.test.tsx` D5 + supersession (asserts the first request's signal really aborted); `api.test.ts` cancellation/timeout unit cases; `client-hardening.spec.ts` D5 journey (proves zero network calls on invalid submit), supersession journey (3.5s late-arrival watch), 14s hang → timeout state → retry recovery → web-e2e |
| S5 D1 labels | `FIELD_LABELS` now covers the full 108-column official inventory (verified programmatically against the connector's `PLUTO_COLUMN_TYPES`, itself CI-cross-checked against the committed `/api/views` snapshot F08); fallback label is an explicit "(source column — label pending review)" marker, never silently raw | `format.test.ts` (all D1-named keys, all fixture fact/missing keys, full policy list, ≥108 count, honest fallback); `sections.test.tsx` asserts labels render and raw keys do NOT; e2e journeys assert labeled text ("Number of floors", "Commercial overlay 1" etc.) → web-e2e. Producer-side inventory cross-check output: `connector columns: 108 / label keys: 108 / missing: [] / extra: []` |
| S6 D2/D3/D4 | CSS: `.table-scroll` wrappers, 767px/480px breakpoints, stacked confirm rows/chips/form at phone width; legend card always visible; shared missing-reason stated once with per-field exceptions inline | `responsive-a11y.spec.ts`: 6 viewport journeys (Property + Confirm at 360/768/1280, asserting `scrollWidth <= clientWidth+1`), keyboard-only grouped-toggle (Tab+Enter+Space, aria-expanded assertions), keyboard-only retry (Tab+Enter with request-count poll), D4 shared-reason-once + `numfloors_not_available` exception, D3 legend glosses without hover on the conflict profile; unit: `sections.test.tsx` D4 test, `missing-inputs.test.ts` extractSharedReason (majority/tie/empty) → web-e2e |
| S7 honesty | Confirm affordance is a visibly disabled control + explicit copy ("cannot be saved yet… no fact has been auto-confirmed"); questions limited to development intent, critical gaps, unresolved conflicts; BIN/geometry/pending flags honestly unknown; internal banner on both screens; PRD §29 disclaimer in the shared layout; legend never emits a `status-verified` badge for absent statuses (collapsed vocabulary is plain text, keeping the M2-T001 honesty assertions green) | `confirm-screen.test.tsx` honesty test; `confirm-journey.spec.ts` S1 assertions; existing `honesty.spec.ts` unchanged and expected green → web-e2e |
| S8 regression + hygiene | All 8 M2-T001 spec files untouched except none; component/testid/copy contracts they assert were preserved (verified line-by-line against each spec — see section 5 risk notes); lint/typecheck/build in CI; no storage APIs, no dangerouslySetInnerHTML, only `NEXT_PUBLIC_API_BASE_URL` env read (grep outputs in section 8) | full `web` + `web-e2e` jobs on the task PR; protected-main PR flow is the orchestrator's step |

## 4. D1–D5 resolutions (M2-T001 G3 carry-forwards)

- **D1** — FIELD_LABELS extended from 48 to 108 entries covering every surfaced key including the ~20 named verbatim in the defect (`residfar…condono`) and the grouped admin/vintage columns (`basempdate`, `dcasdate`, …). **Provenance basis** (also documented in the module docstring): column inventory = official `/api/views/64uk-42ks.json` 108-column snapshot (committed fixture F08, CI-cross-checked constant in `pluto_soda.py`); meanings = official "PLUTO DATA DICTIONARY May 2026 (26v1)" PDF (G1-verified direct read) + README 26v1 as cited with page numbers in `docs/research/pluto-mappluto-2026-07-16.md` §3.2/§3.4/§4.1–4.3 and in the M2-T004 builder's per-column citations. Labels are NAME EXPANSIONS, never legal interpretations; code-list values (BldgClass/LandUse/SPDist/LtdHeight appendices) are deliberately untranslated (research OQ-5 residual). **Disclosed for reviewer spot-check:** the expansions "community facility" (facilfar), "apportionment" (appbbl/appdate), "E-designation" (edesignum) follow the official dictionary field names but their exact wording is not quoted verbatim in the committed research; the acronyms DCAS/MAS/RPAD are passed through unexpanded (no committed expansion exists — inventing one would violate the no-invented-interpretations rule); `tract2010` is labeled "2010 census tract (alternate format)" purely to disambiguate from `ct2010` (a naming choice, not a dictionary claim).
- **D2** — responsive CSS + 6 viewport e2e journeys + keyboard-only toggle/retry e2e (see S6 row).
- **D3** — `CoverageLegend`: gloss for every status present on the profile visible with zero interaction; full vocabulary in a keyboard-accessible disclosure rendered as plain text so no badge exists for a status no on-screen fact carries.
- **D4** — shared boilerplate reason stated once (`shared-missing-reason` note, majority-with-≥2 deterministic extraction); per-field exceptions (e.g. the official numfloors/yearbuilt unknown notes) always inline; presentation-only, nothing dropped or altered.
- **D5** — previous profile survives a client-invalid submit with the inline error; error clears on retype; plus active cancellation of superseded requests.

## 5. Commands run (all read-only or file writes; exact outputs)

No package installation, build, or test execution occurred on this machine. Commands executed:

1. `git -C <worktree> status --porcelain` → the 33-line change list reproduced in section 1 (all paths `apps/web/**`), confirming scope compliance.
2. FIELD_LABELS inventory cross-check (Python regex over `pluto_soda.py` + `format.ts`):
   `connector columns: 108` / `label keys: 108` / `missing labels for columns: []` / `label keys not in inventory: []`
3. Hygiene greps over `apps/web/src`:
   - `dangerouslySetInnerHTML|innerHTML` → only the explanatory comment in `bounded.ts`
   - `localStorage|sessionStorage|indexedDB|document.cookie` → none
   - `process.env` → single hit: `NEXT_PUBLIC_API_BASE_URL` (publishable name, unchanged from M2-T001)
   - `from "@/lib/property-profile"` after migration → zero hits
   - unescaped-apostrophe pattern scan over JSX → none
4. Brace/paren balance scan over the 10 largest new files → all balanced.
5. Read-only reads of the binding packet, G3 report, backend matrix, schemas, fixtures, research docs, all existing specs (basis for the regression-preservation analysis).

Static self-review (in lieu of impossible local execution) specifically verified: every import path resolves against the real tree; the generated-type import is type-only (SWC-erased under `isolatedModules`, so `next build` is unaffected by files outside `apps/web`); TS narrowing in every discriminated-union ternary; the raw-state (non-laundered) pair comparison; each M2-T001 spec's selectors/copy against the changed components (notably: `getByText` direct-text-node semantics for conflict `derivation`, Playwright `locator.count()` counting collapsed-DOM nodes — which drove the plain-text legend vocabulary decision, and `innerText` excluding collapsed `<details>` for the S7 "verified" check).

## 6. Assumptions and defaults

1. **Open-schema keys**: conflict-value `derivation` and mapped-feature `feature/value/provenance_ref/coverage_status` are undocumented in the canonical schema (open objects) but emitted by the accepted builder and their display was G3-accepted in M2-T001. They are read ONLY through documented runtime-narrowing helpers in `contract.ts` (typeof-guarded, absence always tolerated). Dropping them would break accepted journeys; documenting them in the schema is a recommended contracts follow-up.
2. **12s client timeout** (`DEFAULT_TIMEOUT_MS`) chosen to be provable inside Playwright's 30s default budget without CI configuration; overridable per-call.
3. **Confirm screen re-fetches by BBL** (stateless route `?bbl=`) rather than passing in-memory state — matches the no-browser-persistence rule and keeps the URL shareable inside the internal build.
4. **Reason-deduplication policy** (D4): majority reason with ≥2 occurrences, lexicographic tie-break — deterministic and disclosed in the module docstring.
5. The committed `builder_output_m1_t005.json` unit fixture declares `contract_version 1.0.0` while carrying 1.2.0-era optional keys; the client validator accepts it by design (optional keys, closed published-version set). Live e2e profiles are validated as emitted by the real 1.2.0 builder.
6. Lot/building summary field selections on the Confirm card are a labeled DISPLAY choice with explicit copy pointing to the complete tables on the Property screen — not a data filter.

## 7. Known limitations

1. **Local execution impossible — CI is the proof.** No lint/typecheck/build/vitest/Playwright ran on the owner PC (disk floor). G2 evidence must be captured from the task-PR CI run (`web`, `web-e2e`; `contracts-typegen` guards that the consumed generated types are drift-free). If any suite fails in CI, rework will be needed; the static self-review above is thorough but is not execution.
2. Label-expansion disclosures listed in section 4 (D1) for reviewer spot-check against the dictionary PDF.
3. `status_dimensions` (contract 1.2.0) are validated but not yet displayed; recommended follow-up.
4. The timeout e2e adds ~15s and the supersession e2e ~4s to `web-e2e` runtime.
5. The disabled "Confirm facts" affordance performs nothing by design (honest); real confirmation persistence depends on the future analysis-run/user-confirmation endpoint.
6. CORS (M2-T001 D8) unchanged: test-origin CORS lives only in the e2e harness; a reviewed proxy/CORS decision remains REQUIRED before any real cross-origin deployment.
7. `aborted` outcomes render nothing by design; if a future screen needs "cancelled" UI, it must opt in.

## 8. Security / provenance impact

- **Improved:** exact pair matrix prevents body-state spoofing across statuses (including the recorded proxy/CDN-style 500+no_match attack shape); every 200 is contract-validated before render (an invalid payload can no longer partially render); all reflected server text is length-capped and control-stripped; correlation ids and state tokens are charset-allowlisted for display; truncation is explicit. React escaping retained; no `dangerouslySetInnerHTML`; no browser storage APIs; no secrets in the bundle (only `NEXT_PUBLIC_API_BASE_URL`).
- **Unchanged:** the API remains unauthenticated INTERNAL/DEV (B-001) — the Confirm screen adds no new exposure but inherits the no-deploy restriction; provenance rendering still uses only documented keys plus the two disclosed narrowing helpers; every material value on the Confirm card keeps its drill-down (source, original field/value, dataset version, retrieved-at).

## 9. Recommended next tasks

1. Contracts task: document `derivation` and mapped-feature keys in the canonical schema; regenerate types; then delete the narrowing helpers.
2. CORS/proxy decision task (carry-forward D8) — blocking for any deployment.
3. Analysis-run/user-confirmation persistence (activates the Confirm affordances honestly).
4. Status-dimensions display (five independent dimensions, never collapsed — GDS §3.3).
5. Geoclient address resolution to replace the disabled address input (blocked on credentials).

## 10. For the orchestrator

- Ledger: claim → progress 75% (all producer scenarios written; local execution impossible) → submit `awaiting_gate` once the task-PR CI run is green; that CI run constitutes the G2 evidence to record.
- No ci.yml edit was made and none is required.
- Reviewer dispatch per packet: human-journey-reviewer + visual-quality-reviewer (G3, from the CI Playwright artifact `playwright-evidence`), security-reviewer (G5: bounded reflection, pair matrix, no-storage, no-secrets).

---

## 11. REWORK — CI run 87990692660 Playwright failures (2 of 43), 2026-07-17

Vitest was fully green; Playwright was 41 passed / 2 failed. Both failures diagnosed statically (no local execution — disk floor); CI re-run on the task PR is the re-proof.

### 11.1 Failure 1 — `e2e/client-hardening.spec.ts:18` (S2 BLOCKING, correlation id not found)

- **Verdict: TEST BUG (network-stub infidelity). The component and client are correct.**
- Evidence chain:
  - `FailureState.tsx` `Meta` renders `<code data-testid="correlation-id">` in `UnexpectedResponseState` whenever `outcome.correlationId` is non-null — the SAME established testid the passing `e2e/failures.spec.ts` S5 test asserts against the real harness (BBL 3000010005). So the render path exists and works when the id reaches it.
  - `src/lib/api.ts:209` reads `response.headers.get("X-Correlation-ID")` through `boundedToken`; the fixture value `cr500nomatch00000000000000000000` (32 chars, `[a-z0-9]`) passes the allowlist.
  - Root cause: the spec's `route.fulfill` replaces the real harness response but set only `Content-Type` + `X-Correlation-ID`. The page (127.0.0.1:3000) calls the API (127.0.0.1:8000) **cross-origin**; the real harness middleware (`e2e/harness/fixture_api.py`, `expose_headers=["X-Correlation-ID"]`) is bypassed by the stub, and without `Access-Control-Expose-Headers` Chromium filters the non-safelisted header out of `fetch()` responses. The client honestly got `null` and `Meta` correctly rendered nothing. The body/status stayed readable through the interception path, which is exactly why the line-38/39 assertions passed and only line 40 failed.
- Fix (spec only): the stub now faithfully replays what the browser receives from the real harness — fixture headers PLUS the harness CORS response headers (`Access-Control-Allow-Origin: http://127.0.0.1:3000`, `Access-Control-Expose-Headers: X-Correlation-ID`), with an in-file comment explaining why. No component/client change; no testid change (existing convention kept).

### 11.2 Failure 2 — `e2e/confirm-journey.spec.ts:14` (S1, geometry copy drift)

- **Verdict: BOTH sides were wrong in different ways.** The spec asserted a phrase ("never drawn from assumptions") that only existed in the geometry-ABSENT branch of `ConfirmScreen.tsx`, while the live F05 path carries a Point geometry and took the PRESENT branch — whose copy ("Geometry of type Point is recorded for this lot.") was truthful but did not state the honesty limitation (a recorded Point is not a parcel outline).
- Fix: ONE canonical honest sentence now used in both files:
  - Component (`ConfirmScreen.tsx`, geometry-present branch): `Geometry of type ${type} is recorded for this lot from the official source — only recorded geometry is shown; a parcel outline is never drawn from assumptions.`
  - Spec (`confirm-journey.spec.ts` S1): asserts the full Point-instantiated sentence verbatim.
  - The geometry-absent branch copy is unchanged (still carries its own honest "never drawn from assumptions" statement).

### 11.3 Files changed in rework (minimal diff, 3 files)

1. `apps/web/e2e/client-hardening.spec.ts` — added the 2 CORS replay headers + comment to the S2 BLOCKING test's `route.fulfill` only.
2. `apps/web/src/components/confirm/ConfirmScreen.tsx` — geometry-present sentence replaced with the canonical honest sentence (one line).
3. `apps/web/e2e/confirm-journey.spec.ts` — geometry assertion pinned to the canonical sentence.

### 11.4 Whack-a-mole checks (static, exact greps)

- `correlation-id` across `apps/web`: only `FailureState.tsx` (renderer), `client-hardening.spec.ts:48` (fixed test), `failures.spec.ts:57` (real-harness test, passed in CI, untouched), and vitest `property-lookup.test.tsx` (Node fetch stub — no browser CORS header filtering, passed in CI, untouched).
- Geometry copy across `apps/web`: only `ConfirmScreen.tsx:204` (component) and `confirm-journey.spec.ts:37` (spec) — now the identical canonical sentence; the absent-branch copy at `ConfirmScreen.tsx:205` is asserted nowhere else.
- `confirm-screen.test.tsx` (vitest) asserts identity/BIN but NOT the geometry copy — vitest remains unaffected.
- The other stubbed tests in `client-hardening.spec.ts` (503 pair, both S3 mutations) assert no correlation id and were green; left untouched per minimal-diff discipline.

### 11.5 Rework limitations

- Chromium's exact interception semantics (body readable while non-exposed headers are filtered) are inferred from the CI evidence itself (lines 38–39 passed, line 40 failed) plus fetch/CORS spec behavior; the CI re-run is the executable proof.
- No local lint/typecheck/build ran (owner-PC disk floor); the edits are copy/header-literal changes inside existing well-typed expressions.
