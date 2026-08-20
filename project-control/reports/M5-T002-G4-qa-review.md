# G4 QA/Integration Gate Report — M5-T002

> Saved VERBATIM by the orchestrator from the qa-engineer agent-return channel
> (transport entity-decoding only). Reviewer ≠ producer.

**Task:** M5-T002 — Scenario endpoint + property-screen scenario surface (internal, flag-gated; D-021 ALL)
**Reviewer:** qa-engineer (independent; not the producer) — READ-ONLY
**Reviewed content identity:** 31e652a (content commits 8872438 + 31e652a); PR #241 head 2fee786 (trailing control-plane-only commit)
**Branch:** task/M5-T002-scenario-endpoint — PR #241 OPEN/MERGEABLE (correctly UNMERGED per D-021-R022)

## 1. VERDICT: **PASS**

No blocking corrections. Five non-blocking Minor/informational findings (§3) for the record. All ten acceptance scenarios are covered by real tests, both API suites reproduce green locally, the full 40-context CI is green (including `web-e2e` and `web`, which are authoritative for the thin-client web tests I cannot execute), every named packet output exists, and every change to an existing file is strictly additive with zero modification to any existing test.

## 2. AS-1..AS-10 coverage matrix

| AS | Proving test(s) | Verdict |
|----|-----------------|---------|
| **AS-1** flag off/absent/unknown → generic 404, not in OpenAPI | `test_scenario_api.py::test_as1_flag_off_or_unknown_is_generic_404` (8 tokens: None,"","0","false","off","maybe","2","  "); `::test_as1_openapi_never_lists_the_internal_route` | COVERED — asserts exact `{"detail":"Not Found"}`, no `X-Correlation-ID` header, no "scenario/cap/flag" hint; route absent from OpenAPI while existing route present |
| **AS-2** happy path, cap verbatim | `::test_as2_happy_path_surfaces_the_canonical_cap_verbatim` | COVERED — **strong teeth**: `doc["draft_zoning_floor_area_cap_sq_ft"] == canonical_trace_cap()`, where `canonical_trace_cap()` independently rebuilds the rule_evaluation via the SAME production path and pulls the trace's `max_residential_floor_area_sq_ft` output (not a FAR×area recompute). Also asserts conditional coverage, draft label, provenance citations, needs_review, disclaimer, header present |
| **AS-3** honest no-scenario families → 200 | real e2e: `::test_as3_absent_substrate_is_200_professional_review`, `::test_as3_split_lot_is_200_professional_review`; pass-through: `::test_as3_no_scenario_families_pass_through_as_200` (unsupported/conflict/professional_review fixtures); builder-direct: `::test_as3_builder_missing_constraint_is_honest_no_scenario`, `::test_as3_builder_malformed_input_is_honest_no_scenario` | COVERED — cap `is None` never fabricated; never verified. Missing/malformed proven at builder boundary; endpoint emission of any no_scenario doc structurally proven by the pass-through test (M4-T005 precedent pattern) |
| **AS-4** validate-before-emit + depth bound | `::test_as4_invalid_document_is_typed_500_no_internals`; `::test_as4_adversarially_deep_document_hits_bounded_depth_no_recursionerror` (5000-deep) | COVERED — invalid doc → typed 500, no traceback; 5000-deep doc → typed 500, no RecursionError. See F2 (Minor) on regression-sentinel strength |
| **AS-5** error-mapping parity + no leakage | `::test_as5_malformed_bbl_is_typed_422_no_connector_call` (3 codes), `::test_as5_upstream_timeout_maps_to_504_typed`, `::_unavailable_maps_to_503`, `::_schema_drift_maps_to_502`, `::test_as5_valid_nonexistent_bbl_is_404_no_match`, `::test_as5_internal_error_is_generic_500_no_internals`, `::test_as5_error_bodies_never_leak_token_or_stack` (canary) | COVERED — reuses single-sourced `_ERROR_STATUS`/`_DEFAULT_ERROR_STATUS` imported from `properties.py` (verified). No secret/traceback/path in any body |
| **AS-6** no injection surface; POST → 405 | `::test_as6_post_is_405_method_not_allowed`, `::test_as6_query_supplied_assumptions_are_ignored` | COVERED — route signature is `bbl` path param only + `build_scenario(assumptions=None)`; query is byte-inert |
| **AS-7** web flag off, no render/no fetch | `lib/__tests__/scenario.test.ts` surface-gate suite (env AND opt-in); `components/scenario/__tests__/scenario.test.tsx::PropertyLookup — scenario surface gating` (disabled → no panel, no `/scenario` fetch); `e2e/scenario-flag-off.spec.ts` (no opt-in + `?scenario=off`, records **zero** scenario requests) | COVERED — CI `web` + `web-e2e` green |
| **AS-8** web happy path, cap verbatim, runtime-validated | `scenario.test.tsx` (cap "15,000", draft label, no `.status-verified`, provenance "23-21", coverage map "height_limit"/"blocks a buildable envelope"); `lib/scenario.test.ts` (cap == fixture value; validate-before-render; rejects `verified`); `scenario-contract.test.ts`; `e2e/scenario.spec.ts` AS-8 | COVERED — CI green. `baseProfile()` BBL is 1000010010, so the gating test's `/1000010010/scenario` URL assertion is sound |
| **AS-9** web honest failure states | `scenario.test.tsx` (feature_unavailable, network_error+retry, no-cap on no_scenario); `ScenarioFailure` per-state; `e2e/scenario.spec.ts` (professional_review journey, recoverable failure + retry, a11y no-focus-steal) | COVERED — CI green |
| **AS-10** regression + determinism | `::test_as10_response_is_deterministic`, `::test_as10_existing_property_route_still_works`, `::test_as10_health_endpoint_unaffected`; plus my diff evidence (§5), modularity 0 failures, full CI green | COVERED — see F1 (Minor) on determinism assertion strength |

**Packet outputs check (all present):** `services/api/app/api/v1/scenario.py`; `config.py internal_scenario_enabled()` + `INTERNAL_SCENARIO_ENABLED_ENV_VAR`; `lib/scenario.ts` + `scenario-contract.ts` + `components/scenario/{ScenarioPanel,ScenarioResult,ScenarioFailure}.tsx` wired into `PropertyLookup.tsx`/`page.tsx`; API pack + web unit tests + `e2e/scenario.spec.ts` + `scenario-flag-off.spec.ts`; additive harness flag; producer report. All exist.

## 3. Findings (all non-blocking)

**F1 — Minor — determinism test under-asserts byte-identity.** `test_scenario_api.py:332` (`test_as10_response_is_deterministic`) and `:631` (`test_as6…assumptions_are_ignored`) compare `json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)`. `sort_keys=True` normalizes key ORDER, so the test proves value-determinism but NOT the AS-10 parenthetical "byte-identical … deterministic ordering preserved from the builder." Identical code paths make real byte-identity hold, but a stricter test would compare `response.text` (raw bytes). No behavior defect.

**F2 — Minor — depth-guard test is not a removal-sentinel.** `scenario.py:319` runs `_document_depth_ok()` BEFORE `validate_scenario_document`, so the 5000-deep dict in `test_as4_adversarially_deep…` does exercise the guard (it returns the 500). But that dict is also malformed at the top level (only key `"n"`), so `validate_scenario_document` would ALSO reject it with `internal_contract_error` if the guard were deleted — the test would still pass without the guard. To lock FH-M5T001-S2 as a true regression sentinel, use an otherwise-valid document deep enough to trip ONLY the guard. Guard code itself is correct (iterative, non-recursing, limit 64; legitimate docs nest ~6-7 and pass via `test_as2`).

**F3 — Minor/informational — stale comment in `e2e/scenario.spec.ts:15-23`.** The header note still says the PropertyLookup/playwright wiring is "OUTSIDE this task's allowed_paths" and the journeys are "gated on that out-of-scope wiring." Post-amendment this is false: the wiring is applied and in allowed_paths, and CI `web-e2e` runs these journeys green. Cosmetic only.

**F4 — Minor — flag-off 404 not compared to a live unmounted GET.** AS-1 asserts the body equals the KNOWN FastAPI default `{"detail":"Not Found"}` (effectively byte-equal) rather than issuing a GET on a genuinely nonexistent path and comparing. Adequate as written; a direct comparison would be marginally stronger.

**F5 — Minor — a few endpoint seams asserted indirectly.** `rate_limited → 503` and the presence of the `X-Correlation-ID` HEADER on error paths (422/no_match/upstream) are not explicitly asserted at the scenario endpoint; they are guaranteed by the shared `_ERROR_STATUS` map and the `_json()` helper (both verified in source) and `rate_limited` is exercised by the web pair-matrix test. No gap in behavior.

## 4. Commands run + last lines (from the review worktree)

```
$ cd .../wt-m0t064/services/api && python -m pytest tests/api -q
144 passed in 16.20s

$ python -m pytest tests/api tests/scenario -q
198 passed in 17.76s

$ python -m pytest tests/api/test_scenario_api.py -q
33 passed in 1.88s

$ cd .../wt-m0t064 && python tools/modularity_check.py --check
selected 271 files; failures 0; warnings 5   # all 5 warnings pre-existing/untouched; no scenario file flagged

$ python -m ruff check app/api/v1/scenario.py app/config.py app/main.py tests/api/test_scenario_api.py ../../apps/web/e2e/harness/fixture_api.py
All checks passed!

$ wc -l app/api/v1/scenario.py
349   # focused route module, well under the 600 warn threshold

$ gh pr checks 241 --repo martin10101/nyc-buildability
# ALL 40 contexts pass, including:
#   api (ruff + pytest)                    pass
#   web (lint + typecheck + build)         pass
#   web-e2e (vitest + Playwright vs recorded-official-fixture API)  pass
#   modularity / contracts-typegen (TS drift) / control-plane  pass

$ gh pr view 241 --repo martin10101/nyc-buildability
head: 2fee786…  branch: task/M5-T002-scenario-endpoint  state: OPEN  mergeable: MERGEABLE
```

Regression evidence (base d8b3899 in my own worktree vs review worktree):
- `diff -rq services/api/tests/api` → only additions: `test_scenario_api.py` (+ generated `__pycache__`). **Zero existing API test modified.**
- `config.py`, `main.py`, `page.tsx`, `PropertyLookup.tsx`, `playwright.config.ts`, `e2e/harness/fixture_api.py` → all diffs strictly ADDITIVE (new imports/prop/env-line/router registration/comment); no existing branch or existing-route behavior altered. `app/api/v1/__init__.py` unchanged (empty diff).

## 5. Integration & boundary checks
- **Router registration** exercised by AS-1/AS-2 (200 + 404 reachable) and OpenAPI-exclusion test. **OpenAPI exclusion** (`include_in_schema=False`) directly asserted.
- **Correlation-id** on 200 (header-only, keeping the body deterministic — good design) and on 500 asserted; flag-off 404 correctly carries none.
- **READ-ONLY boundary honored:** zero edits under `app/scenario/**`, `app/profile/**`, `app/spatial/**`, `app/rules/**`, `packages/contracts/**`; the surfaced cap is consumed verbatim (`build_scenario(profile, rule_evaluation_document, assumptions=None)`), never recomputed/relabeled. "verified" is rejected both server-side (`validate_scenario_document`) and client-side (`scenario-contract.ts`); the `_coverage_values` helper checks every `coverage_status` field at any depth (correctly NOT a blanket string-grep, since legitimate disclaimer text contains "Verified").
- **Modularity:** `scenario.py` (349 SLOC) is a focused route module mirroring `rule_evaluation.py`; checker 0 failures, none of the new files flagged.

## 6. What I could NOT verify (and how it was resolved)
- **Web unit/component/e2e execution locally:** not run (thin-client; no npm/node/npx/playwright, per policy). **Resolved by CI:** the `web` and `web-e2e` jobs are green on PR head 2fee786, which is the authoritative execution of `scenario.test.ts(x)`, `scenario-contract.test.ts`, `scenario.spec.ts`, and `scenario-flag-off.spec.ts` against the real recorded-official-fixture harness. I verified their assertions against the actual wiring (PropertyLookup `scenarioEnabled` prop, `scenario-panel`/`scenario-announcer` testids, harness `INTERNAL_SCENARIO_ENABLED=1`, playwright `INTERNAL_SCENARIO_UI=1`) and found them correct and self-consistent.
- **`tests/documents/**` (whole `pytest tests`):** pre-existing PEP 695 collection errors on the sandbox's Python 3.11 (repo needs 3.12) — known, out of scope, unrelated to this task; CI runs 3.12 and is green.
- **Git-native diff at the frozen SHA:** the isolated-reviewer git-guard blocked `git`/`git -C` against the shared checkout; substituted with base-vs-review directory `diff` (above), which is sufficient to confirm additive-only / no-existing-test-modification.

**Note for the orchestrator:** CI is fully green (not pending), so no orchestrator-captured evidence is outstanding. Record G4 = PASS. The PR must remain UNMERGED (D-021-R022); merge identity is the orchestrator's to report to the owner.
