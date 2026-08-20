# M5-T002 — Producer report

Scenario endpoint + property-screen scenario surface (internal, flag-gated). Producer:
`backend-engineer`. Branch base: `task/M5-T002-scenario-endpoint` @ `5239dcf`. Directive: D-021 (ALL).

This is a producer evidence record only. It does not accept the task or claim gate readiness; an
independent gate decides that.

---

## 1. What I built (all inside the packet's allowed_paths)

### Backend (fully complete; self-checks pass in-worktree)

- **`services/api/app/config.py`** — added `internal_scenario_enabled()` + `INTERNAL_SCENARIO_ENABLED_ENV_VAR`,
  byte-for-byte the same explicit-true-token / fail-safe semantics as `internal_rule_eval_enabled`
  (absent/empty/unknown -> disabled).
- **`services/api/app/api/v1/scenario.py`** (new) — `GET /api/v1/properties/{bbl}/scenario`,
  `include_in_schema=False`, mirroring `rule_evaluation.py` stage by stage:
  - Flag off -> identical generic `404 {"detail":"Not Found"}`, no correlation id, checked FIRST.
  - `bbl` path param ONLY. No request body, no query params. `build_scenario(..., assumptions=None)` — the
    browser can never supply the facts a scenario rests on.
  - `normalize_bbl` -> typed 422; injected `PlutoFetcher` via `Depends(get_pluto_fetcher)` -> the same
    single-sourced `_ERROR_STATUS` map; `no_match` -> the same 404 machine-state body; substrate via
    `Depends(get_spatial_substrate_provider)` **REUSED by import from `rule_evaluation.py`** (the seam is
    not duplicated).
  - `build_property_profile` -> `validate_profile` (typed `internal_contract_error` 500) ->
    `evaluate_property` -> `serialize_rule_evaluation` -> `validate_rule_evaluation_document` (typed 500) ->
    `build_scenario(profile, rule_evaluation_document)` consumed READ-ONLY.
  - **FH-M5T001-S2 (depth bound):** `_document_depth_ok()` — an ITERATIVE explicit-stack depth check (limit
    64), run BEFORE contract validation, so an adversarially deep document returns a typed 500 and never a
    `RecursionError` (the guard itself never recurses).
  - **FH-M5T001-S1 (validate before emit):** ALWAYS calls `validate_scenario_document(document)` before send;
    failure -> typed `internal_contract_error` 500 with no internals.
  - A no_scenario / unsupported / professional-review outcome from `build_scenario` is a NORMAL 200 document.
    200s carry `X-Correlation-ID`. Logging is payload-only (no `str(exc)`/traceback). Everything after fetch
    is inside one generic-500 guard.
  - The surfaced cap is never recomputed or relabeled here — it is whatever `build_scenario` surfaced verbatim
    from the canonical trace.
- **`services/api/app/main.py`** — registered `scenario_v1_router` exactly like `rule_evaluation_v1_router`
  (always mounted; unreachable + absent from OpenAPI unless the flag is explicitly true).
- **`services/api/tests/api/test_scenario_api.py`** (new) — 33 tests (see §3 for the AS map).

### Frontend (surface fully built, wired into the property screen, and unit/component-tested)

> **Amendment (2026-08-20):** the orchestrator amended this task's allowed_paths (pre-gate contract
> correction, recorded in the ledger) to add `apps/web/src/components/property/PropertyLookup.tsx` and
> `apps/web/playwright.config.ts`. B1 and B2 (§4) are now CLOSED — the property-screen render wiring and the
> e2e web-server flag are applied. D1 is orchestrator-APPROVED (keep the non-public `INTERNAL_SCENARIO_UI`).

- **`apps/web/src/lib/scenario-contract.ts`** — runtime validation of a 200 scenario body against the
  GENERATED types (`packages/contracts/generated/scenario.ts`), mirroring `rule-evaluation-contract.ts`
  (two-way `MutuallyEqual` enum proofs; rejects `verified`; bounded problem list).
- **`apps/web/src/lib/scenario.ts`** — typed client + presentation classifier + feature-flag helper,
  mirroring `lib/rule-evaluation.ts` guarantee-for-guarantee: exact (status, state) pair matrix incl.
  `feature_unavailable` for the flag-off (404, null) pair; runtime contract validation before render;
  bounded/control-stripped reflected text; token-allowlisted correlation id; AbortController + timeout;
  `aborted`/`client_timeout` outcomes.
- **`apps/web/src/components/scenario/{ScenarioPanel,ScenarioResult,ScenarioFailure}.tsx`** + `__tests__/` —
  render the draft cap VERBATIM with its draft-cap label, cap rule/citations/provenance disclosure, the
  rule-coverage map, coverage badge (never "verified"), `needs_review` + `not_verified_disclaimer`, each
  honest typed no-scenario state with the backend-produced reason, and `feature_unavailable` as a benign
  "not available in this environment" note. Focus/announcement discipline mirrors the rule-eval surface
  (own live region, no focus hijack on background load).
- **`apps/web/src/lib/__tests__/scenario.test.ts`** + **`scenario-contract.test.ts`** — client-layer tests
  (flag matrix, pair matrix, envelope classification, verified-rejection, presentation classifier,
  announcements) mirroring `rule-evaluation.test.ts`.
- **`apps/web/e2e/scenario.spec.ts`** + **`scenario-flag-off.spec.ts`** — Playwright journeys patterned on
  the rule-eval specs.
- **`apps/web/e2e/harness/fixture_api.py`** — extended ADDITIVELY: `build_app()` now also sets
  `INTERNAL_SCENARIO_ENABLED=1`. The scenario route REUSES the existing PLUTO fetcher + substrate seams, so
  the existing substrate routing table drives the scenario UI states with no other harness change; existing
  routes are byte-behavior-unchanged.
- **`apps/web/src/components/property/PropertyLookup.tsx`** (amendment, additive) — added an optional
  `scenarioEnabled?: boolean` prop (default false) threaded to `ProfileView`, which renders
  `{scenarioEnabled ? <ScenarioPanel bbl={profile.identity.bbl} /> : null}` immediately after the existing
  rule-eval panel — the EXACT mirror of the rule-eval wiring. Zero change to any existing behavior; flag off
  -> never mounted, no fetch.
- **`apps/web/src/app/property/page.tsx`** (amendment, additive) — computes
  `scenarioSurfaceEnabled({ scenario: params.scenario })` and passes `scenarioEnabled` into `PropertyLookup`,
  parallel to `ruleEvalEnabled`.
- **`apps/web/playwright.config.ts`** (amendment, additive) — added `INTERNAL_SCENARIO_UI: "1"` to the web
  test server's `webServer.env`, exactly parallel to `INTERNAL_RULE_EVAL_UI` (non-public runtime flag; nothing
  else in the config changed).

---

## 2. Hard-boundary compliance (D-021 + packet)

- READ-ONLY honored: **zero edits** to `app/scenario/**`, `app/profile/**`, `app/spatial/**`, `app/rules/**`,
  `packages/contracts/**`. The cap is never recomputed or relabeled (backend or frontend); no "verified" is
  emitted or rendered; no hidden assumptions (`assumptions=None`); deterministic code only, no AI.
- No existing test / CI workflow / security control touched. Unrelated dirty files: none present.
- All 12 changed paths are inside the packet's allowed_paths (verified against `git status`).
- No new public endpoint beyond the single flag-gated internal route.

---

## 3. AS coverage map (evidence)

| AS | Where covered | Notes |
|----|---------------|-------|
| AS-1 API flag off/absent/unknown -> generic 404, not in OpenAPI | `test_scenario_api.py::test_as1_flag_off_or_unknown_is_generic_404` (8 tokens), `::test_as1_openapi_never_lists_the_internal_route` | byte-equal `{"detail":"Not Found"}`, no correlation id, no hint |
| AS-2 happy path -> 200, cap == canonical trace VERBATIM | `::test_as2_happy_path_surfaces_the_canonical_cap_verbatim` | cap asserted `== canonical_trace_cap()` (rule_evaluation trace rebuilt via the same production path), never recomputed; never "verified"; `needs_review` + disclaimer + `X-Correlation-ID` |
| AS-3 honest no-scenario families -> 200 | real path: `::test_as3_absent_substrate_is_200_professional_review`, `::test_as3_split_lot_is_200_professional_review`; pass-through: `::test_as3_no_scenario_families_pass_through_as_200` (unsupported, conflict, professional_review committed fixtures); builder-only families: `::test_as3_builder_missing_constraint_is_honest_no_scenario`, `::test_as3_builder_malformed_input_is_honest_no_scenario` | the fixed R5 endpoint path can only itself reach preliminary + professional-review; unsupported/conflict/missing/malformed are proven at the pass-through + builder boundary, exactly as the M4-T005 pack proves its unsupported/conflict families at the serializer boundary (documented pattern) |
| AS-4 validate-before-emit + depth bound | `::test_as4_invalid_document_is_typed_500_no_internals`, `::test_as4_adversarially_deep_document_hits_bounded_depth_no_recursionerror` | invalid doc -> typed 500; a 5000-deep doc -> typed 500, no `RecursionError`/traceback |
| AS-5 error-mapping parity + no leakage | `::test_as5_*` (422 malformed x3, 504 timeout, 503 unavailable, 502 schema_drift, 404 no_match, generic 500, token/stack-leak absence) | same single-sourced map as rule-eval; no traceback/secret/path in any body |
| AS-6 no injection surface; POST -> 405 | `::test_as6_post_is_405_method_not_allowed`, `::test_as6_query_supplied_assumptions_are_ignored` | query `?assumptions=...` is inert (byte-identical body) |
| AS-10 determinism + regression | `::test_as10_response_is_deterministic`, `::test_as10_existing_property_route_still_works`, `::test_as10_health_endpoint_unaffected` | identical input -> byte-identical 200 body |
| AS-7 web flag off (no render, no fetch) | `apps/web/src/lib/__tests__/scenario.test.ts` (surface-gate suite) + `apps/web/e2e/scenario-flag-off.spec.ts` | no-opt-in and `?scenario=off` render nothing and fire no `/scenario` request |
| AS-7 web flag off — property-screen integration | `scenario.test.tsx::PropertyLookup — scenario surface gating` (disabled -> panel not mounted, no `/scenario` fetch) | added after the wiring amendment; proves no-render/no-fetch at the real integration point |
| AS-8 web happy path (cap verbatim, runtime-validated) | `apps/web/src/components/scenario/__tests__/scenario.test.tsx` (cap value `15,000` + draft label + never-verified + provenance; PropertyLookup enabled -> panel mounts + calls `/1000010010/scenario`) + `apps/web/src/lib/__tests__/scenario*.test.ts` + `apps/web/e2e/scenario.spec.ts` | wiring applied (B1 CLOSED); component/client logic fully covered |
| AS-9 web honest failure states | component test (feature_unavailable, network_error+retry, no-cap on no-scenario) + `apps/web/e2e/scenario.spec.ts` | wiring applied (B1/B2 CLOSED) |

---

## 4. Limitations / blockers — stated plainly

### B1 — CLOSED by allowed_paths amendment (2026-08-20). Wiring applied.

Resolution: the orchestrator amended allowed_paths to add `apps/web/src/components/property/PropertyLookup.tsx`.
The additive wiring is now applied (exact diff below), mirroring the rule-eval panel line-for-line:

- `apps/web/src/components/property/PropertyLookup.tsx`:
  - `import { ScenarioPanel } from "@/components/scenario/ScenarioPanel";`
  - `ProfileView` gains a `scenarioEnabled: boolean` prop;
  - after the rule-eval panel: `{scenarioEnabled ? <ScenarioPanel bbl={profile.identity.bbl} /> : null}`;
  - `PropertyLookup` gains an optional `scenarioEnabled = false` prop, passed to `ProfileView`.
- `apps/web/src/app/property/page.tsx`:
  - `import { scenarioSurfaceEnabled } from "@/lib/scenario";`
  - `const scenarioEnabled = scenarioSurfaceEnabled({ scenario: params.scenario });`
  - `<PropertyLookup ruleEvalEnabled={ruleEvalEnabled} scenarioEnabled={scenarioEnabled} />`.

No existing behavior in either file changed. A new `PropertyLookup` gating test
(`scenario.test.tsx::PropertyLookup — scenario surface gating`) proves flag-off -> no panel, no fetch, and
flag-on -> panel mounts + fires `/1000010010/scenario`.

Historical context (the original blocker, retained for the record): The rule-evaluation panel is wired into
the property screen inside
**`apps/web/src/components/property/PropertyLookup.tsx`** (its `ProfileView` renders
`{ruleEvalEnabled ? <RuleEvaluationPanel .../> : null}`), and `apps/web/src/app/property/page.tsx` computes
the flag and passes it as a prop. To wire the scenario surface "the same way", BOTH of those files must
change — but only `apps/web/src/app/property/**` is in this task's allowed_paths;
`components/property/PropertyLookup.tsx` is **not**. Passing a `scenarioEnabled` prop from `page.tsx` alone
is a TypeScript error until `PropertyLookup` declares/consumes it, so I did **not** modify `page.tsx`
either (leaving it byte-unchanged rather than shipping an unused value that fails `tsc`/eslint).

I did NOT edit either out-of-scope file (respecting the HARD path boundary; editing outside allowed_paths
fails the gate on scope). The scenario surface is fully built, drop-in, and unit/component-tested. The exact
additive wiring needed (mirrors the rule-eval lines verbatim):

- `apps/web/src/app/property/page.tsx`:
  - import `scenarioSurfaceEnabled` from `@/lib/scenario`;
  - `const scenarioEnabled = scenarioSurfaceEnabled({ scenario: params.scenario });`
  - pass `scenarioEnabled` into `<PropertyLookup ... />`.
- `apps/web/src/components/property/PropertyLookup.tsx`:
  - add optional prop `scenarioEnabled?: boolean` (default false) threaded to `ProfileView`;
  - in `ProfileView`, after the rule-eval panel: `{scenarioEnabled ? <ScenarioPanel bbl={profile.identity.bbl} /> : null}` (import from `@/components/scenario/ScenarioPanel`).

Recommended resolution (orchestrator's call, per ADR-005): amend allowed_paths to add
`apps/web/src/components/property/PropertyLookup.tsx` (M0-T077 allowed_paths-amendment precedent) so I apply
the ~2-line additive wiring, OR split a small wiring follow-up task. Until then the property-screen live
journeys (AS-8/AS-9 happy/failure) cannot render; the flag-off no-render/no-fetch guarantee (AS-7) holds
regardless and is proven.

### B2 — CLOSED by allowed_paths amendment (2026-08-20). Config applied.

`apps/web/playwright.config.ts` `webServer.env` now includes `INTERNAL_SCENARIO_UI: "1"`, added additively
exactly parallel to `INTERNAL_RULE_EVAL_UI` (nothing else in the config changed). Combined with the B1 wiring
and the harness server flag (`INTERNAL_SCENARIO_ENABLED=1`), `scenario.spec.ts` now has the full env it needs
to render in the CI web-e2e job. `scenario-flag-off.spec.ts` was already correct and needs no config.

### D1 — ORCHESTRATOR-APPROVED (2026-08-20): keep the non-public `INTERNAL_SCENARIO_UI` flag as built

The orchestrator accepted D1 as resolved: the stronger (non-public server-read) guarantee wins, and reviewers
will be told this was an orchestrator-approved resolution of the packet's self-conflict. Detail retained below.

The packet's item 6 says two things that conflict: (a) "mirroring `lib/rule-evaluation.ts`
guarantee-for-guarantee" and (b) "use an analogous `NEXT_PUBLIC_*` var". Rule-eval DELIBERATELY uses a
non-public server-read var (`INTERNAL_RULE_EVAL_UI`) precisely so Next never inlines the flag into the client
bundle (its own module comment states this). A `NEXT_PUBLIC_*` var would inline the flag/endpoint hint into
the browser bundle — a weaker posture than the pattern I was told to mirror, and a security-guarantee
reduction on a legally-sensitive platform. I preserved the stronger guarantee (non-public runtime var,
mirroring rule-eval exactly) and am flagging the deviation here for the reviewer to confirm or send back.
The functional guarantee is identical either way: off by default (var unset -> off) + per-request `?scenario=on`
opt-in; the endpoint is independently server-gated, so the defense-in-depth frontend flag never gates data.

### N1 (non-blocking, environment): `python -m pytest tests` (whole services/api) cannot collect on this sandbox

Pre-existing PEP 695 generic syntax under `tests/documents/**` requires Python 3.12; this sandbox is 3.11.9,
so those 15 collection errors are unrelated to this task (`SyntaxError: expected '('`). CI runs 3.12 and is
authoritative. I ran `tests/api` and `tests/scenario` (both collect and pass — see §5).

### N2 (thin-client): web tests written, not executed

Per the packet + thin-client policy, no npm/node/npx/playwright was run. The vitest unit/component tests and
Playwright e2e specs are written to mirror the accepted rule-eval patterns; CI is authoritative for them.

---

## 5. Commands run (in-worktree) with real output

```
$ git rev-parse --show-toplevel
C:/Users/MLFLL/Downloads/.../.claude/worktrees/agent-a7d83133a1fce5dab   (contains .claude/worktrees/agent- : PASS)

$ python --version
Python 3.11.9

$ cd services/api && python -m pytest tests/api/test_scenario_api.py -q
.................................                                         [100%]
33 passed in 7.35s

$ python -m pytest tests/api -q
........................................................................ [ 50%]
........................................................................ [100%]
144 passed in 4.64s

$ python -m pytest tests/api tests/scenario -q
........................................................................ [ 36%]
........................................................................ [ 72%]
......................................................                   [100%]
198 passed in 4.69s

$ python -m pytest tests -q        # whole services/api (see N1)
... 15 errors in 10.11s            # PRE-EXISTING PEP695/3.12 collection errors in tests/documents/** ONLY

$ python tools/modularity_check.py --check        # from repo root
selected 265 files; failures 0; warnings 5
  (all 5 warnings are pre-existing, UNTOUCHED files; scenario.py and the new tests are not flagged)

$ cd services/api && python -m ruff --version && python -m ruff check app/api/v1/scenario.py app/config.py app/main.py tests/api/test_scenario_api.py
ruff 0.13.0
All checks passed!

$ python -m ruff check ../../apps/web/e2e/harness/fixture_api.py
All checks passed!
```

Ruff local version (0.13.0) matches CI. Web `tsc`/eslint/vitest/playwright: NOT run (thin-client; CI authoritative).

### Re-verification after the B1/B2 wiring increment (2026-08-20)

```
$ cd services/api && python -m pytest tests/api -q
........................................................................ [ 50%]
........................................................................ [100%]
144 passed in 17.54s          # unchanged (111 prior api + 33 scenario); no backend impact from the web wiring

$ python tools/modularity_check.py --check        # from repo root
selected 271 files; failures 0; warnings 5        # +6 files picked up (the new scenario TS); 0 failures; none of my files flagged
```

The wiring is TypeScript-only (PropertyLookup.tsx, page.tsx, playwright.config.ts) — no Python/ruff impact.
The added `PropertyLookup` gating test + the e2e specs align with the wiring shape actually applied (verified
by re-reading: the panel is `<ScenarioPanel bbl={profile.identity.bbl} />`, testid `scenario-panel`, gated by
the `scenarioEnabled` boolean). Web tests remain unexecuted (thin-client; CI authoritative).

---

## 6. Modularity

`scenario.py` is a focused route module mirroring `rule_evaluation.py`'s shape and size (well under the
~600 SLOC ceiling); `modularity_check --check` reports 0 failures and does not flag any new file.

---

# D-022 correction — scenario-contract validator faithful enforcement

Owner blocking finding (directive D-022, `project-control/directives/D-022-scenario-contract-validator-correction/source-001.md`):
`validateScenarioDocument` claimed to enforce the canonical scenario contract before casting an HTTP-200 body
to `Scenario`, but adversarial execution proved it accepted eight malformed bodies, and `fetchScenario`
classified a negative-cap 200 body as `kind="scenario"`. Correction is bounded to the four files in scope; no
schema fork, no new dependency, no backend change.

## What was broken (and why the original tests missed it)

The original validator sampled a few fields per object instead of enforcing the schema's
`additionalProperties:false` + `required` at every level, and used loose type tests:

- **No top-level `additionalProperties:false` / required-presence.** An unexpected top-level property (bypass 7)
  and the committed `embedded_property_profile.json` fixture (bypass 8, which adds a root `property_profile`)
  both passed.
- **Draft cap checked only `typeof === "number"`.** `-1` (bypass 1) and `0` (bypass 2) — and `NaN`/`±Infinity` —
  all passed, even though the schema is `exclusiveMinimum: 0` (strictly positive) or `null`.
- **`evaluated_input.bbl` accepted any non-empty string.** `"x"` (bypass 3) passed; the schema requires the
  canonical BBL pattern `^[1-5][0-9]{5}[0-9]{4}$` or `null`.
- **`cap_provenance.rule_status` was only checked `typeof === "string"`.** `"verified"` (bypass 4) passed; the
  schema enum is exactly `["discovered","extracted_draft","needs_review","published"]`.
- **`cap_provenance.citations` was only checked `Array.isArray`.** The item shape was never validated, so
  `[null]` (bypass 5) passed and a null citation could then crash citation rendering in `ScenarioResult`.
- **`assumptions` was only checked `Array.isArray`.** The item shape was never validated, so `[null]`
  (bypass 6) passed.
- **`constraint.provenance` used `typeof value === "object"`,** which is `true` for an array — arrays slipped
  through the intended object-or-null gate.
- No `additionalProperties`/required enforcement on `evaluated_input`, `cap_provenance`, `citation`,
  `constraint`, `assumption`, `coverage_matrix` rows, or `integrity_check`; `integrity_check.tolerance`
  accepted non-finite numbers.

Why the original tests missed it: the pack asserted the happy-path fixtures passed and a *handful* of negative
cases (wrong `contract_version`, `verified` top-level `coverage_status`, non-numeric cap, bad constraint
`state`), but had **no adversarial test per bypass** and **no committed-fixture sweep**, so the invalid
fixtures (including `embedded_property_profile.json`) were never fed through the validator, and the loose
per-field checks were never probed at their boundaries. No existing assertion encoded acceptance of a bypass,
so **no test needed to be flipped** — the gap was missing coverage, not wrong coverage. All prior assertions are
retained unchanged.

## The fix (faithful enforcement, before casting `unknown` to `Scenario`)

`apps/web/src/lib/scenario-contract.ts`:
- Added `checkKnownAndRequiredKeys` enforcing `additionalProperties:false` + `required` at every object level
  (root, `evaluated_input`, `cap_provenance`, `citation`, `constraint`, `assumption`, `coverage_matrix` rows,
  `integrity_check`). Root allowed keys = the 16 required keys + the optional fixture-only `_expected_failure`
  (string).
- `draft_zoning_floor_area_cap_sq_ft`: `null` OR a **finite** number strictly `> 0` (`isFiniteNumber` +
  `> 0`).
- `evaluated_input.bbl`: `null` or the canonical `BBL_PATTERN`; `input_fingerprint`: `null` or
  `DIGEST_SHA256_PATTERN`; versions non-empty strings.
- `cap_provenance.rule_status`: new `CAP_PROVENANCE_RULE_STATUSES` enum; `citations` every item validated via
  `checkCitation` (required `{snapshot_id,section,quote,provenance}` strings + `provenance` via `isRecord`,
  optional `last_amended` string|null, `additionalProperties:false`).
- `constraint.provenance` and `citation.provenance`: `isRecord`-or-null (arrays now fail).
- `assumptions[]`: new `checkAssumption` (required shape; `[null]` fails).
- `coverage_matrix` rows + `integrity_check`: added `additionalProperties`/required-presence; `tolerance` must
  be finite; `rule_status_today` locked to a new `COVERAGE_MATRIX_RULE_STATUSES` enum.
- All numeric checks route through `Number.isFinite` (`isFiniteNumber`); scalar values use `isContractScalar`
  (finite number | string | boolean | null).
- Failure stays **total** and the bounded `Problems`/`MAX_REPORTED_PROBLEMS` mechanism is unchanged.
- Added two `MutuallyEqual` compile-time proofs to `ScenarioEnumAssertions`: `rule_status` locked to the
  generated `CapProvenance["rule_status"]` union (exact generated type name confirmed in
  `packages/contracts/generated/scenario.ts`), and `rule_status_today` locked to
  `CoverageMatrixRow["rule_status_today"]`.

No schema fork (types remain a type-only import of the generated module); no new dependency; no feature-flag,
component, backend, or config change.

## Per-bypass mapping (bypass → rejecting check → test)

| # | Reproduced bypass | Rejecting check (scenario-contract.ts) | Test |
|---|---|---|---|
| 1 | `draft_..._cap_sq_ft = -1` | finite `> 0` gate | contract: "bypass 1: … = -1"; scenario: "negative cap … validation_failure" |
| 2 | `draft_..._cap_sq_ft = 0` | finite `> 0` gate | contract: "bypass 2: … = 0" |
| 3 | `evaluated_input.bbl = "x"` | `BBL_PATTERN` in `checkEvaluatedInput` | contract: "bypass 3: … bbl = 'x'" |
| 4 | `cap_provenance.rule_status = "verified"` | `checkEnum` vs `CAP_PROVENANCE_RULE_STATUSES` | contract: "bypass 4: … rule_status = 'verified'" |
| 5 | `cap_provenance.citations = [null]` | `checkCitation` (item is `isRecord`) | contract: "bypass 5: … citations = [null]"; scenario: "null citation … validation_failure" |
| 6 | `assumptions = [null]` | `checkAssumption` (item is `isRecord`) | contract: "bypass 6: … assumptions = [null]" |
| 7 | unexpected top-level property | root `checkKnownAndRequiredKeys` (`additionalProperties:false`) | contract: "bypass 7: an unexpected top-level property" |
| 8 | `embedded_property_profile.json` | root `additionalProperties:false` (`property_profile`) | contract: "bypass 8: … embedded_property_profile.json"; scenario: "embedded_property_profile.json body … validation_failure" |

Extra adversarial coverage: `+Infinity`/`NaN` caps and a `constraints[0].provenance = []` array (the `typeof`
hole) are also asserted rejected. Fixture sweeps assert every committed valid fixture (4) passes and every
committed invalid fixture (3) fails, with `embedded_property_profile.json` asserted present and rejected
explicitly.

## Tests added (additive; nothing weakened or deleted)

- `apps/web/src/lib/__tests__/scenario-contract.test.ts`: all original assertions retained; added the 8
  per-bypass adversarial tests + extra `Infinity`/`NaN`/array-provenance case + the committed-fixture sweep
  (static imports of all 4 valid + 3 invalid fixtures — deterministic and `tsc`-clean; `import.meta.glob` was
  deliberately avoided because there is no `vite/client` ambient-types reference and the test files are inside
  the `tsc --noEmit` include, so a glob call would break the CI typecheck).
- `apps/web/src/lib/__tests__/scenario.test.ts`: original assertions retained; added three `fetchScenario`
  tests proving a 200 body with (i) cap `-1`, (ii) a null citation item, (iii) the `embedded_property_profile`
  body classifies as `kind="validation_failure"`, never `kind="scenario"` (mirroring the existing mocked-HTTP
  `stub(jsonResponse(...))` pattern).

## Verification (measured in this worktree; vitest is CI-proven)

- `cd services/api && python -m pytest tests/api -q` → **144 passed in 5.83s** (zero backend impact).
- `python tools/modularity_check.py --check` (repo root) → **selected 271 files; failures 0; warnings 5**
  (the 5 warnings are pre-existing and unrelated; `scenario-contract.ts` is not flagged).
- **vitest / tsc / lint / build / Playwright are NOT run locally** — the owner's thin-client policy forbids
  installing `node_modules` on this machine; those jobs are authoritative from the clean-checkout CI run. Each
  changed test was re-read line-by-line against the new validator (imports, fixture paths — five `../` from the
  test file, exact problem-path prefixes, and `boundedText` preserving those prefixes so the `fetchScenario`
  `startsWith` assertions hold) for consistency.

## Could not verify locally
- Frontend unit execution (vitest), `tsc --noEmit`, ESLint, `next build`, and Playwright journeys — deferred to
  CI per thin-client policy. The static-import sweep and the avoidance of `import.meta.glob` were chosen
  specifically to keep the CI `tsc --noEmit` typecheck green without a config or ambient-types change.
