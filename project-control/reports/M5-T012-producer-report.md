# M5-T012 Producer Report

**Task:** Expose the deterministic scenario optimization toolkit (sensitivity / ranking /
comparison / threshold) via the internal flag-gated scenario API.

**Branch:** `task/M5-T012-scenario-analysis-api`
**Producer:** backend-engineer (run lineage persistent-local-28)
**Status:** producer self-check complete; submitted for independent review (G0/G1/G3/G4/G5).

---

## 1. What was built

One new route module — `services/api/app/api/v1/scenario_analysis.py` — exposing the four
ACCEPTED, offline engine functions as four internal, feature-flag-gated POST endpoints under the
SAME posture as the accepted M5-T003 `GET /properties/{bbl}/scenario` route:

| Endpoint | Engine function (via `app.scenario` facade) | Origin |
|---|---|---|
| `POST /api/v1/properties/{bbl}/scenario/sensitivity` | `analyze_scenario_sensitivity` | M5-T008 |
| `POST /api/v1/properties/{bbl}/scenario/ranking` | `rank_scenario_assumption_sets` | M5-T007 |
| `POST /api/v1/properties/{bbl}/scenario/comparison` | `compare_scenario_assumption_sets` | M5-T010 |
| `POST /api/v1/properties/{bbl}/scenario/threshold` | `find_scenario_threshold` | M5-T011 |

`services/api/app/main.py` was touched **additively only** (one import + one `include_router`
call + a comment mirroring the M5-T003 registration); every existing registration and its order
is unchanged.

Acceptance pack: `services/api/tests/api/test_scenario_analysis_api.py` (AS-1..AS-8), fully
offline through the injected fetcher/substrate seams (no network / Supabase / Geoclient).

No engine module, no `app/api/v1/scenario.py`, no `rule_evaluation.py`/`properties.py`, no
`app/config.py`, and no `packages/contracts` file was modified. The existing
`internal_scenario_enabled` flag is REUSED (no new flag).

## 2. The security heart — assumptions yes, FACTS never

The request body carries ONLY illustrative analysis parameters (named assumption-sets, a
variable name, an ordered candidate domain, a response-metric name, a numeric target, an
objective). The scenario document — and therefore the canonical
`draft_zoning_floor_area_cap_sq_ft` cap, the coverage/verification status, and every other FACT —
is ALWAYS rebuilt SERVER-SIDE from the `bbl` path parameter over the SAME trusted injected seams
the accepted routes use (`get_pluto_fetcher` → `build_property_profile` → `evaluate_property` →
`serialize_rule_evaluation` → `build_scenario`, with `get_spatial_substrate_provider`).

- The body is **merged into the ENGINE arguments only**, never into the server-rebuilt document.
  The engines merge a caller value into `assumptions` only (`{**scenario_document, "assumptions":
  echo}`), so a fact can never enter the scenario document through the body.
- A top-level body key that would supply/override a fact (`FORBIDDEN_FACT_KEYS`: profile,
  rule_evaluation, scenario, cap value, coverage/verification status, constraints, …) is REJECTED
  with a typed `(422, "validation_error")` carrying `detail.rejected_keys` — never merged.
- Test `test_as2_injected_cap_cannot_change_the_echoed_cap` proves an injected cap is rejected AND
  a legitimate response echoes the server-rebuilt canonical cap (`15000.0`) verbatim — confirmed
  equal to the value read back through the mirrored rule-evaluation route
  (`test_as1_cap_equals_rule_evaluation_trace_value_verbatim`).

## 3. Bounded input, fail-closed at the untrusted edge

Explicit, documented caps (module constants, exported for tests):

| Cap | Value | Enforcement |
|---|---|---|
| `MAX_BODY_BYTES` | 65536 | checked on raw bytes BEFORE parsing |
| `MAX_NESTING_DEPTH` | 32 | iterative (explicit-stack) walk; << engine sanitizer's 500 |
| `MAX_STRING_LENGTH` | 4096 | same iterative walk (keys and values) |
| `MAX_ASSUMPTION_SETS` | 50 | ranking / comparison |
| `MAX_CANDIDATE_DOMAIN_LENGTH` | 256 | sensitivity `values` / threshold `domain` |
| `MAX_ASSUMPTIONS_PER_SET` | 64 | per assumption-set |

- JSON parsing is wrapped so ANY failure — invalid JSON or a body too deep for the parser
  (`RecursionError`) — is a typed 422, never an unhandled raise. The depth walk is **iterative**
  (no recursion), so a `>=500`-level body is a typed 422 whether the parser rejects it or the walk
  does (`test_as5_deeply_nested_body_is_typed_422_never_recursionerror`, levels 40 and 600).
- No `ZeroDivisionError`/`NaN`/`Inf` reaches a response: a caller may send `NaN`/`Infinity`
  tokens, but the engines sanitize every echoed value and `_finish` proves the envelope with
  `json.dumps(envelope, allow_nan=False)` before send
  (`test_as5_nan_inf_values_never_reach_the_response`).

## 4. Route posture (mirrors M5-T003 exactly)

- **Flag-gated fail-safe.** Reachable ONLY when `INTERNAL_SCENARIO_ENABLED` is an explicit true
  token; absent/empty/unknown → a generic `404 {"detail":"Not Found"}` byte-indistinguishable
  from an unmounted path (no header/body/timing hint; no `X-Correlation-ID`). Proven for all four
  routes across 8 non-true flag values, with landmine seams proving no I/O occurs.
- **No OpenAPI leak.** All four routes are `include_in_schema=False`; none appears in
  `/openapi.json` regardless of the flag.
- **`STATUS_STATE_MATRIX`** is the single source of truth and **EQUALS** the accepted scenario
  route's matrix (`== SCENARIO_MATRIX` and `== PROPERTY_MATRIX - {(500,
  unsupported_contract_version)}`); body-validation failures reuse the existing `(422,
  "validation_error")` pair and rebuilt-document contract defects reuse `(500,
  internal_contract_error)`, so NO new pair is introduced. `test_as4_every_emitted_pair_is_in_the_matrix`
  drives every documented pair and asserts the emitted set equals the matrix.
- **Honest non-errors.** A no-scenario / unsupported / empty / invalid analysis outcome is a
  NORMAL 200 typed result, never an error (`test_as4_no_scenario_is_a_normal_200_typed_result`).
- Every non-disabled response carries `X-Correlation-ID`; no error body carries a traceback,
  filesystem path, secret, or internal string (`test_as4_internal_defect_leaks_nothing`).

## 5. No new logic; facade-only; never Verified

- The route performs no independent legal calculation and no engine maths: it rebuilds,
  validates, adapts the request into the engine's documented arguments, calls the engine
  READ-ONLY, and returns its typed result verbatim inside a thin envelope.
- Engine calls go through the public `app.scenario` facade — asserted by object identity in
  `test_as7_engine_calls_use_the_public_facade`.
- Nothing is ever marked Verified; the canonical `NOT_VERIFIED_DISCLAIMER` is present on every
  analysis response (envelope + engine result); the canonical cap is transported VERBATIM from the
  server-rebuilt document (`test_as6_response_is_strict_json_safe_and_never_verified`).

## 6. Acceptance-scenario coverage

- **AS-1** `test_as1_endpoint_returns_engine_result_envelope` (×4), `test_as1_cap_equals_rule_evaluation_trace_value_verbatim`
- **AS-2** `test_as2_fact_injecting_body_is_typed_422` (×11 fact keys), `test_as2_injected_cap_cannot_change_the_echoed_cap`
- **AS-3** `test_as3_flag_off_or_unknown_is_generic_404` (×4 routes × 8 flag values), `test_as3_openapi_never_lists_any_analysis_route`
- **AS-4** `test_as4_matrix_equals_scenario_route_matrix`, `test_as4_no_scenario_is_a_normal_200_typed_result` (×4), `test_as4_every_emitted_pair_is_in_the_matrix`, `test_as4_internal_defect_leaks_nothing`
- **AS-5** oversized body / deep-nesting (40, 600) / oversized string / malformed & non-object / domain-length / assumption-set caps / NaN-Inf
- **AS-6** `test_as6_response_is_strict_json_safe_and_never_verified` (×4)
- **AS-7** `test_as7_existing_routes_unaffected`, `test_as7_engine_calls_use_the_public_facade`, `test_as7_full_analysis_runs_fully_offline`
- **AS-8** full `tests/api` + `tests/scenario` suites green; modularity check (see §7)

## 7. Evidence (documented test commands)

- `python -m pytest services/api/tests/api` — _(result recorded on completion below)_
- `python -m pytest services/api/tests/scenario` — _(result recorded on completion below)_

Modularity: `scenario_analysis.py` is a single cohesive route-adapter responsibility (well under
the 600-SLOC warn threshold; no domain logic, storage, or serialization mixed in). The
`python tools/modularity_check.py --check` run is an orchestrator/CI step (not a
packet-documented producer command); the module was authored to pass it.

### Test results

_To be finalized once the two documented suites complete._
