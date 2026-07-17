# M2-T001 Producer Report — First browser Property screen

- **Task:** M2-T001 (Priority 4: first browser Property screen, real BBL lookup against accepted property-profile API v1.1)
- **Producer:** frontend-engineer
- **Worktree/branch:** `.claude/worktrees/M2-T001` / `task/M2-T001-property-screen` (based on main @ 8b49cad)
- **Requested status:** `awaiting_ci_evidence` (G2 completes only after CI green — see section 8)
- **Date:** 2026-07-16

## 1. What was built

An INTERNAL/DEV-only Next.js Property screen (`/property`) that performs a real
BBL lookup against `GET /api/v1/properties/{bbl}`, consumes ONLY
contract-v1.1-documented keys, and renders: confirmed facts (value + units +
per-fact PRD §12 coverage label, never color-only), `data_completeness`
banner, conflicts (all values with sources, unresolved visible), unsupported
facts + drift signals, missing inputs under a documented filter policy,
per-fact and per-district provenance drill-down, professional-review
affordance, staged loading, and first-class typed failure states. Plus vitest
unit/component tests, Playwright human journeys against a
recorded-official-fixture FastAPI harness, and an additive CI job.

## 2. Files changed (all inside allowed paths)

New application code (`apps/web/src`):
- `src/lib/property-profile.ts` — TS view of contract v1.1 (documented keys ONLY)
- `src/lib/bbl.ts` — client-side BBL mirror validation (documented deliberate gap, see 3.4)
- `src/lib/api.ts` — typed outcome classification for every documented response
- `src/lib/provenance.ts` — fact join + district map/fallback join (D5)
- `src/lib/missing-inputs.ts` — DOCUMENTED missing-inputs filter policy (D3)
- `src/lib/coverage.ts` — PRD §12 enum display vocabulary (verbatim value + gloss + symbol)
- `src/lib/format.ts` — display-only formatting; explicit "no legal logic" rule
- `src/app/globals.css` — design tokens + component styles (hand-rolled, no component library)
- `src/app/layout.tsx` — one-line edit: import globals.css (disclaimer footer untouched)
- `src/app/page.tsx` — home placeholder now links to `/property`
- `src/app/property/page.tsx` — Property screen page + INTERNAL/DEV banner
- `src/components/property/`: `PropertyLookup.tsx`, `FactsTable.tsx`,
  `ZoningSection.tsx`, `ConflictsSection.tsx`, `MissingInputsSection.tsx`,
  `UnsupportedSection.tsx`, `ProfessionalReviewPanel.tsx`,
  `ProvenanceDisclosure.tsx`, `CoverageBadge.tsx`, `LoadingStages.tsx`,
  `FailureState.tsx`

Tests:
- `src/test-support/fixtures.ts` — fixture derivations (documented, test-only)
- `src/lib/__tests__/{bbl,api,provenance,missing-inputs}.test.ts`
- `src/components/property/__tests__/{property-lookup,sections}.test.tsx`
- `vitest.config.ts`, `vitest.setup.ts`
- `e2e/harness/fixture_api.py` — recorded-official-fixture API harness
- `e2e/helpers.ts`, `e2e/{primary-journey,validation,no-match,failures,partial-and-conflict,keyboard,honesty}.spec.ts`
- `playwright.config.ts`

Configuration:
- `apps/web/package.json` — scripts `test`/`test:e2e`; devDependencies added (see 3.6)
- `apps/web/.env.example` — `NEXT_PUBLIC_API_BASE_URL` NAME ONLY, with publishability note
- `apps/web/eslint.config.mjs` — ignore `playwright-report/`, `test-results/`
- `.github/workflows/ci.yml` — ONE additive job `web-e2e`; existing 4 jobs byte-untouched

Not touched: `services/**`, `packages/contracts/**`, `render.yaml`, `docs/**`,
`supabase/**`, `project-control/**` (except this report).

## 3. Design decisions

### 3.1 Missing-inputs filter policy (M1-T005 G3 D3)
Frontend display policy, documented in `src/lib/missing-inputs.ts`:
(1) nothing dropped — total count always in the section heading;
(2) surfaced immediately = criticality `critical` OR field in the
feasibility-relevant list (lot geometry, zoning/overlay/special columns, FAR
family, floor areas, units, landmark/flood, MIH options, e-designations,
development-history linkage); (3) the rest grouped behind an explicit
"Show N more missing fields" toggle (keyboard-accessible, aria-expanded);
(4) presentation-only — never alters data. Chosen frontend-side (not
builder-side) because the packet assigned the policy to this task and the API
is read-only for me.

### 3.2 Provenance join (PRD §9/§19; M1-T006 G3 D5)
- Facts: `provenance_ref` → `provenance[].provenance_id`; a dangling ref
  renders an explicit "provenance not linkable" gap (never hidden).
- Districts/overlays/special districts: contract-1.1.0 maps used when present
  for a value; PARTIAL coverage legal — unmapped values fall back to joining
  `provenance[].original_field_name` within the documented column families
  (`zonedist1..4`, `overlay1..2`, `spdist1..3`) matching
  normalized/original value. The live builder emits contract 1.0.0 (no maps;
  verified `PROFILE_CONTRACT_VERSION = "1.0.0"` in builder.py), so the
  fallback is today's production path; the map path (and map-present +
  map-absent mixed case) is exercised via a derived 1.1.0 fixture in unit
  tests. The fallback join is labeled in the UI ("Linked by source column
  name…").
- **Documented-keys discipline:** the builder emits per-record `dataset_id` /
  `request_url` keys that are NOT documented in `source_fact.schema.json`.
  The drill-down therefore takes dataset id and request-URL HOST from the
  documented top-level `reproducibility` object instead. Host only — full
  request URLs are shown nowhere in the fact drill-down.

### 3.3 API outcome classification
`state` is the non-200 discriminator: `no_match`, `validation_error`
(renders `detail.code` + `message`), `rate_limited`/`source_unavailable`/
`timeout`/`schema_drift` (typed, retry affordance, HTTP status shown),
`internal_error` (generic copy + correlation id). Any response without a
recognized `state` — including a routing 404 — maps to a distinct
`unexpected_response` state and is NEVER shown as "no match". Browser-level
fetch failure is a recoverable `network_error` state with retry. A stale
response can never overwrite a newer lookup (monotonic request sequence).

### 3.4 Client-side validation mirror and the deliberate 422 gap
Client mirrors exactly the packet-specified rule (10 digits, borough 1–5)
BEFORE any network call. The server's additional `invalid_block`/
`invalid_lot` checks (all-zero block/lot) are deliberately NOT duplicated, so
the server-422 path remains a real reachable path: e2e submits `1000000000`
(passes client mirror) and asserts the rendered `detail.code =
invalid_block`. No test-only bypass flag exists in app code.

### 3.5 E2E harness architecture (recorded-official-fixture, NOT a mock)
`apps/web/e2e/harness/fixture_api.py` imports the REAL installed FastAPI app
and overrides exactly one seam — the `get_pluto_fetcher` dependency, the same
seam the accepted M1-T005 test suite uses — with a fetcher that runs the REAL
connector (`fetch_by_bbl`) over scripted transports replaying COMMITTED
official captures (`services/api/tests/fixtures/pluto/*.json`). Route,
validation, connector, builder, and error mapping are production code.
Routing table (documented in the file): F05→1000010010 (S1 split zone),
F01→1000010100 (S2/D5), F04→1000010101 (S6 partial), F02b→1000041001 (S4
condo), F03b→5999999999 (S2 boundary); failure-control BBLs 3000010001..5
script transport-level failures (429×3 / timeout×3 / network×3 / drift 400 /
raised exception) — all format-valid BBLs with non-zero block/lot.
Conflict BBL 1000010103 serves a labeled SYNTHETIC variant of F01 (identity
columns rewritten to the control BBL, `borocode` mutated "1"→"3") — the exact
technique of the accepted M1-T005 S4 test; derivation documented in the
harness. `services/**` was not edited; the harness only imports from outside.

**CORS (flag for orchestrator):** the deployed API has no CORS policy and the
browser calls it cross-origin (3000→8000). The harness adds `CORSMiddleware`
for the test origin only, as labeled test infrastructure. Before any real
cross-origin deployment, a reviewed decision is needed: same-origin proxying
(e.g. Next rewrites) or a reviewed CORS allowlist added to the API by an
API-scoped task. Recommend tracking as a follow-up; the owner-directed
`NEXT_PUBLIC_API_BASE_URL` direct-fetch design is kept as specified.

### 3.6 Dependency choices (all devDependencies; installed in CI only)
- `vitest` + `@vitejs/plugin-react` + `jsdom` + `@testing-library/react` +
  `@testing-library/dom` + `@testing-library/jest-dom` — Vitest over Jest for
  Next 15/React 19 compatibility with the smallest chain (no Babel).
  `@testing-library/dom` pinned explicitly (peer of TL React 16).
- `@playwright/test` — required by the packet; chromium only in CI.
- NO runtime dependencies added; NO component library (hand-rolled CSS on
  design-system tokens per docs/PREMIUM_PRODUCT_DESIGN_SYSTEM.md).

### 3.7 Fixture derivations in unit tests (no invented facts)
`src/test-support/fixtures.ts` starts from the committed
`builder_output_m1_t005.json` (byte-exact accepted builder output for the
real official F05 record) and derives in code, documented inline:
`profileWithDistrictMaps()` (contract_version→1.1.0 + PARTIAL maps
referencing EXISTING provenance ids; C4-1 deliberately unmapped) and
`partialProfile()` (removes `identity.address`/`identity.geometry` only).
Test-only module; app code imports nothing from it.

### 3.8 Honesty & UI rules
- INTERNAL DEVELOPMENT BUILD banner on the Property page; PRD §29 disclaimer
  in the shared layout footer (reuses `src/lib/disclaimer.ts`).
- Address entry rendered visibly DISABLED with honest copy (Geoclient
  connector + credentials pending); no pretend address lookup.
- App copy contains no "best" and no "verified" — the string `verified` can
  only ever appear as a coverage badge if the API delivers that enum value
  (it cannot today; coverage policy shown in the review panel). E2E asserts
  both absences on a rendered profile.
- Coverage labels: exact PRD §12 enum value + symbol + plain-language gloss —
  never color alone. `data_completeness` banner shows the exact enum value.
- Loading is staged truthfully (format check done → single API retrieval →
  render); no fake pipeline stages, no fake progress.

## 4. Scenario mapping (S1–S8)

| Scenario | Executable evidence |
|---|---|
| S1 primary (1000010010: loading stages, facts+units+coverage, banner, split-zone districts, provenance drill-down on lot area) | e2e `primary-journey.spec.ts` (3 tests); unit `property-lookup.test.tsx` "renders the split-zone profile"; `provenance.test.ts` fact join |
| S2 boundary (borough 5; zero-valued lot facts; provenance map present AND absent/D5) | e2e `no-match.spec.ts` boundary test + `partial-and-conflict.spec.ts` D5 test (map-absent live path, fallback labeled); unit `provenance.test.ts` (map present, partial map, absent map, dangling refs); `bbl.test.ts` borough 1/5 bounds |
| S3 malformed before network + server 422 via real gap | e2e `validation.spec.ts` ('1-00001-0100', '123' with API-call counter = 0; '1000000000' → rendered `invalid_block`); unit `bbl.test.ts` + `property-lookup.test.tsx` (fetch spy not called; 422 rendering) |
| S4 no-match condo billing-lot explanation | e2e `no-match.spec.ts` (asserts "BILLING lot" and "7501-7599" from the REAL API text); unit `api.test.ts` |
| S5 dependency failures (503 rate_limited / 503 source_unavailable / 504 timeout / 502 schema_drift distinct / 500 generic + correlation id / connection refused + successful retry) | e2e `failures.spec.ts` (6 tests, incl. retry-recovers via route-abort→unroute); unit `api.test.ts` + `property-lookup.test.tsx` (typed states, retry re-fetch, correlation id) |
| S6 partial data + missing-inputs policy + conflicts visible | e2e `partial-and-conflict.spec.ts` (F04 partial; grouped-count toggle; synthetic borocode conflict: both values + sources + unresolved, data_conflict badge, conditional facts unaffected); unit `missing-inputs.test.ts` (nothing-dropped invariant), `sections.test.tsx`, `property-lookup.test.tsx` (absent address/geometry no-crash) |
| S7 honesty (no mocked success path, disabled address entry, internal banner + disclaimer, no invented wording) | e2e `honesty.spec.ts` (4 tests, incl. API-blocked ⇒ no profile reachable); unit `property-lookup.test.tsx` honesty test; code inspection: no fixture import outside `src/test-support`/`e2e` |
| S8 regression + hygiene (existing jobs untouched, lint/typecheck clean, keyboard-only S1, no secrets, nothing heavy local) | e2e `keyboard.spec.ts` (keyboard-only lookup + provenance + visible focus); CI: existing jobs unchanged (additive job only), lint/typecheck/build steps; `.env.example` names-only; local footprint = source files only |

## 5. Commands run locally (owner PC, source-only discipline)

```
python -m py_compile apps/web/e2e/harness/fixture_api.py   -> PY_OK
python (pyyaml) safe_load .github/workflows/ci.yml         -> YAML_OK jobs:
    ['api', 'contracts', 'control-plane', 'web', 'web-e2e']
```

Nothing else was executed locally: NO `npm install`/`npm ci`, no
`node_modules`, no Playwright browsers, no `.next` output (owner PC at
~1.67 GB free, below the 4 GB floor). Every install/build/test/browser run
happens in the GitHub Actions `web-e2e` job.

## 6. Lockfile situation — ORCHESTRATOR ACTION REQUIRED

`apps/web/package.json` gained devDependencies, but I cannot regenerate
`apps/web/package-lock.json` locally (no npm). **Both `web` and `web-e2e`
jobs will fail `npm ci` (lockfile out of sync) until the lockfile is
regenerated.** The repository already has the sanctioned mechanism:
`.github/workflows/generate-lockfile.yml` (workflow_dispatch; runs
`npm install --package-lock-only` on a GitHub runner and commits to the
dispatched branch). Requested sequence:
1. Push `task/M2-T001-property-screen`.
2. Dispatch **Generate web lockfile** on that branch.
3. The bot commit re-triggers CI; use that run as G2 evidence.
No silent `npm install` fallback was added to CI (explicitly disallowed).

## 7. Assumptions, limitations, risks

1. **CORS follow-up** (section 3.5): harness-only CORS is test infrastructure;
   a production cross-origin policy/proxy decision is an open follow-up.
2. Dependency versions are caret ranges pinned at lockfile generation; if a
   just-released major breaks something, I iterate on CI feedback.
3. The map-present district-provenance path cannot appear in e2e because the
   live builder emits contract 1.0.0; covered by unit tests on a documented
   derived 1.1.0 fixture (schema-legal per contract README).
4. S1's packet text mentions "zonedist values from both sources" — the F05
   split-zone capture yields two districts from two source COLUMNS
   (zonedist1/zonedist2, both rendered with provenance) and an EMPTY
   conflicts array from the builder; the conflicts UI is proven with the
   labeled synthetic borocode-conflict journey (M1-T005 S4 technique).
5. `unexpected_response` (routing 404) is unit-tested only; the UI cannot
   emit a malformed route URL itself.
6. The professional-review affordance is an honest status panel (counts,
   coverage policy text, review obligation); no pretend submission workflow
   before M4.
7. Keyboard focus-visibility assertion relies on chromium `:focus-visible`
   behavior (keyboard interaction ⇒ ring): stable in CI chromium.
8. `web-e2e` repeats lint-adjacent work? No — it runs vitest + build +
   Playwright; lint/typecheck stay in the untouched `web` job (no weakening,
   no duplication of authority).

## 8. What CI must prove (my G2 evidence — I ran nothing heavy locally)

G2 is complete when ONE CI run on this branch (after lockfile regeneration)
shows ALL of:
1. `web` job green (lint + typecheck + build with the new code).
2. `web-e2e` job green: vitest suites pass (bbl/api/provenance/
   missing-inputs/property-lookup/sections), production build, Playwright
   14 e2e tests pass on chromium against the harness-served REAL API.
3. `api`, `contracts`, `control-plane` jobs still green (S8 regression:
   nothing outside apps/web + one additive CI job changed).
4. `playwright-evidence` artifact uploaded (traces `trace: "on"` for every
   test + HTML report; retention 7 days) — the G3 reviewer's walkthrough
   evidence.
Orchestrator: please relay the CI run URL + per-job results; I will fix any
failure and resubmit.

## 9. Security / provenance impact

- No secrets introduced; `.env.example` gains a NAME only (a URL, not a
  credential). No privileged key can appear under apps/web (unchanged
  boundary comments preserved).
- No provenance-free value is rendered: every fact row exposes its
  provenance record or an explicit "not linkable" gap.
- The screen remains INTERNAL/DEV (B-001 no-auth condition restated in the
  page banner and page docstring); no deploy config touched (render.yaml
  untouched, B-002 respected).
- Harness CORS is scoped to 127.0.0.1/localhost:3000, GET only, and lives in
  test infrastructure outside the deployable API.
