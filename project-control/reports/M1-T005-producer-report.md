# Producer Report — M1-T005

- Task: M1-T005 — Property-profile API v1: GET /api/v1/properties/{bbl} via pluto-soda connector
- Producer: backend-engineer
- Status requested: **awaiting_gate** (G2 self-check complete; submission only — no self-acceptance)
- Worktree: `.claude/worktrees/M1-T005`, branch `task/M1-T005-property-profile-api` (base `69b5509`)
- Date: 2026-07-16
- Execution location: owner PC worktree, source-only edits; all tests offline on fixture transports; no datasets, no network calls, no artifacts outside the repo (low-storage compliant)

## 1. Files changed

| File | Change |
|---|---|
| `services/api/app/api/__init__.py` | new — API package docstring (thin routes, no legal logic) |
| `services/api/app/api/v1/__init__.py` | new — v1 package |
| `services/api/app/api/v1/properties.py` | new — GET /api/v1/properties/{bbl}: validate-first, injectable fetcher dependency, documented HTTP semantics, typed error bodies, X-Correlation-ID, drift-monitor hook stub, F5 payload-only logging |
| `services/api/app/profile/__init__.py` | new — profile package |
| `services/api/app/profile/builder.py` | new — PlutoFetchResult → canonical property_profile v1 document (provenance-linked fact values, PRD §12 coverage + completeness, conflicts, missing inputs, reproducibility metadata, backend provenance-integrity re-check) |
| `services/api/app/connectors/pluto_soda.py` | G5 F1–F4 hardening ONLY (see §4); no redesign |
| `services/api/app/main.py` | v1 router mount only + INTERNAL/DEV no-auth warning in docstrings/description |
| `services/api/tests/api/__init__.py` | new |
| `services/api/tests/api/test_properties_v1.py` | new — 39 offline tests, S1–S8 |
| `services/api/tests/connectors/test_pluto_soda.py` | 5 existing urllib-transport tests repointed from `urllib.request.urlopen` to the new no-redirect opener (`pluto_soda._OPENER`) — required by F3; `_FakeUrlopenResponse.read` now honors the bounded-read `amt` argument (required by F1). No assertion weakened; all 101 pre-existing tests still pass |
| `project-control/reports/M1-T005-producer-report.md` | this report |

Contracts (`packages/contracts/**`) untouched — confirmed by `git status --porcelain` (§6).

## 2. HTTP semantics (documented in OpenAPI `responses` on the route)

| Connector outcome | HTTP | Body `state` | Notes |
|---|---|---|---|
| profile built (`status=ok`) | 200 | — (body IS the canonical profile) | conflicts included; conflicts are results, not errors |
| malformed BBL | 422 | `validation_error` | typed code (`invalid_borough`, `wrong_length`, `non_numeric`, `non_integer_decimal`, …); **zero connector calls** (test-asserted) |
| `no_match` | **404 (documented choice)** | `no_match` | a RESULT, not an error (G3 carry-forward); body carries bbl, explanation (incl. condo billing-lot text), source/dataset ids, request_url, retrieved_at; distinguishable from routing 404 by `state` |
| `rate_limited` | 503 | `rate_limited` | after bounded connector retries |
| `source_unavailable` | 503 | `source_unavailable` | incl. refused 3xx redirects (F3) and unparseable bodies (F2) |
| `timeout` | 504 | `timeout` | |
| `schema_drift` | **502** | `schema_drift` | distinct status AND state so dataset-contract breakage is never mistaken for transient outage |
| unexpected exception | 500 | `internal_error` | generic body; internals/type/traceback never leave the process |

Every response carries `X-Correlation-ID`. Accepted path input forms (documented in the 422 OpenAPI description): canonical 10-digit BBL and Socrata decimal-serialized form; component form is rejected 422.

## 3. Scenario results (S1–S8)

All commands from `services/api/` in the worktree; runner `python -m pytest`, offline.

| ID | Command (test selector) | Expected | Actual | Verdict |
|---|---|---|---|---|
| S1 | `pytest "tests/api/test_properties_v1.py::test_s1_200_profile_validates_against_property_profile_v1" ...` (5 S1 tests) | 200; jsonschema-valid vs property_profile v1 (registry: property_profile+source_fact+common); no dangling provenance_ref; coverage present, never `verified`, independent of confidence=1.0; profile_version + reproducibility present | all asserted; validation ran (not skipped); `lot_facts.lotarea = 23121 sq ft` backed by provenance original_value `"23121"`; builtfar 0.43 informational/unitless | PASS |
| S2 | 4 S2 tests | decimal path input `1000010100.00000000` → 200 canonical, connector called with canonical only, raw record serialization preserved in provenance; borough 0/6 → 422 `invalid_borough` with zero connector calls; borough 5 valid → 404 no_match; component form → 422; OpenAPI documents 200/404/422/500/502/503/504 | all asserted (6 malformed inputs parametrized) | PASS |
| S3 | 4 S3 tests | F03b `5999999999` → 404 `state=no_match` + explanation; F02b condo unit lot `1000041001` → 404 with "BILLING lot"/"7501-7599" text; F04 absent `numfloors` (numbldgs=10) → NOT in existing_building_facts, explicit missing_inputs entry with p.28 reason; synthetic missing `lotarea` → criticality=critical, `data_completeness=missing_critical` | all asserted | PASS |
| S4 | 2 S4 tests | synthetic borocode "3" vs BBL 1…: 200 with conflicts[0] field=borocode, resolution=unresolved, both values verbatim; `lot_facts.borocode`/`lot_facts.bbl` coverage=`data_conflict`; unaffected lotarea stays `conditional`; identity NEVER derived from the conflicting borocode (no borough/borough_code emitted) | all asserted | PASS |
| S5 | 6 S5 tests | 429×3→503 rate_limited; timeout×3→504; network×3→503 source_unavailable; F13 drift→502 schema_drift (distinct); with SOCRATA_APP_TOKEN canary set: no token, no `X-App-Token`, no `Traceback`, no `File "` in any error body; hostile unexpected exception → 500 `internal_error`, message not leaked | all asserted | PASS |
| S6 | 2 S6 tests | same BBL twice on fixture transport → `json.dumps`-identical documents (structure AND key order) after removing `generated_at` + `correlation_id`; provenance ids deterministic and unique | asserted; retrieved_at fixed by injected clock; volatile fields disclosed in §7.3 | PASS |
| S7 | 8 S7 tests | F1: >10 MiB 200 body AND >10 MiB HTTPError body → typed `TransportFailure` "exceeded", no unbounded read; F2: `"["*100000` 200 body → 503 `source_unavailable` with `parse_error=RecursionError` (typed, no stack escape), same for 400 body (error_code=None, not drift); F3: `_NoRedirectHandler.redirect_request` returns None, opener's only redirect handler is the refusing one, refused 302 → typed error after exactly ONE transport call; F4: CRLF errorCode → `repr()`-sanitized in detail, official codes verbatim | all asserted | PASS |
| S8 | full suite + validators (§6) | all M1-T002 tests still pass (101); validate_contracts 0 failures; no contract files modified; health endpoint regression | 140 passed total = 101 baseline + 39 new; validator 0 failures; git status shows no `packages/contracts/**` change | PASS |

## 4. G5 hardening F1–F4 (each with tests)

| Finding | Fix (location) | Tests |
|---|---|---|
| F1 bounded response read | `_bounded_read()` reads `MAX_RESPONSE_BYTES + 1` (10 MiB cap) and raises typed `TransportFailure` on oversize; applied to BOTH the 200 path and the HTTPError body path (`pluto_soda.py`, `urllib_transport`) | `test_s7_f1_oversized_200_body_is_refused_bounded_read`, `test_s7_f1_oversized_error_body_is_refused_bounded_read` |
| F2 RecursionError / hostile JSON → typed error | `RecursionError` added to the except clauses in `fetch_by_bbl` body parse (→ `SourceUnavailableError`, `parse_error: RecursionError`) and `_classify_400` (→ unparseable/None) | `test_s7_f2_hostile_deeply_nested_json_is_typed_error`, `test_s7_f2_hostile_deeply_nested_400_body_classifies_as_unparseable` |
| F3 redirects disabled | `_NoRedirectHandler(HTTPRedirectHandler)` whose `redirect_request` returns None; module opener `_OPENER = build_opener(_NoRedirectHandler)`; transport uses `_OPENER.open`. A 3xx surfaces as `TransportResponse(3xx)` → typed `source_unavailable`; the X-App-Token header is never re-sent to ANY redirect target, same-host or cross-host | `test_s7_f3_redirect_handler_refuses_all_redirects`, `test_s7_f3_opener_has_only_the_no_redirect_handler`, `test_s7_f3_refused_redirect_surfaces_as_typed_error_single_call` |
| F4 untrusted errorCode sanitized | `_sanitize_error_code()`: official dotted-token allowlist `^[A-Za-z0-9._-]{1,120}$` passes verbatim; anything else `repr()`-sanitized before entering `detail` (consistent with `version_raw`/`record_bbl_raw`) | `test_s7_f4_hostile_errorcode_is_sanitized_in_detail`, `test_s7_f4_official_errorcode_passes_verbatim` (+ existing S5b tests confirm official codes unchanged) |
| F5 (info, consumer contract) | Route logs `exc.to_payload()` via `json.dumps` (control chars escaped) — never `traceback.format_exception`; unexpected exceptions log exception TYPE + correlation id only | `test_s5_error_responses_never_leak_token_or_stack_trace`, `test_s5_unexpected_exception_is_500_generic_no_internals` |

## 5. M1-T002 G3 carry-forwards honored

- `no_match` is a result, not an error → 404 with machine-readable `state=no_match` + condo billing explanation (S3).
- `conflicts`/`drift_signals`/`absent_columns`/`notes` persist into the profile: `conflicts[]` (unresolved, both values verbatim), `reproducibility.drift_signals`, `missing_inputs` (from absent_columns + notes), `reproducibility.connector_notes`.
- confidence NEVER maps to a coverage label: `_coverage_status()` uses only review/conflict/drift state; test proves confidence=1.0 facts stay `conditional`; policy text embedded in `reproducibility.coverage_policy`.
- drift-monitor hook: `_drift_monitor_hook()` in `properties.py` — a DOCUMENTED STUB that logs structured WARNING with drift signals per request; the scheduled monitor calling `check_columns_for_drift` against live /api/views metadata belongs to the M2 ingestion/connector-health tasks (recommended next task below).
- D1 taxonomy respected: route treats `validation_error` as caller error only (422, pre-network); record-level corruption arrives as `schema_drift` (502).

## 6. Self-check commands and exact outputs (G2)

From `services/api/`:

```
> python -m pytest tests -q
140 passed in 1.39s

> python -m pytest tests/api/test_properties_v1.py -q
39 passed in 1.03s

> python -m pytest tests/connectors tests/test_health.py -q
101 passed in 0.90s

> python -m ruff check app tests
All checks passed!
```

From the worktree root:

```
> python .github/scripts/validate_contracts.py
Checked 6 schema file(s); 0 failure(s).

> python .github/scripts/secret_scan.py
secret-scan: inline pragma allowed 6 line(s):  [5 pre-existing gate-report lines + test_pluto_soda.py:398]
secret-scan: PASS -- no findings

> git status --porcelain
 M services/api/app/connectors/pluto_soda.py
 M services/api/app/main.py
 M services/api/tests/connectors/test_pluto_soda.py
?? services/api/app/api/
?? services/api/app/profile/
?? services/api/tests/api/
```

(Baseline before any change: `101 passed in 2.31s` — reproduced first.)

## 7. Assumptions and defaults (disclosed for the gate)

1. **Additive keys on the canonical contract (KEY ADJUDICATION ITEM).** property_profile v1 has no dedicated coverage/completeness/reproducibility fields. Draft 2020-12 objects without `additionalProperties: false` permit additional properties, and the ACCEPTED M1-T002 connector already uses exactly this pattern on source_fact ("additive provenance extensions"). I therefore added, additively and documented in `builder.py`: per-fact-value `coverage_status`, top-level `data_completeness`, top-level `reproducibility`. The required v1 field set is complete and unchanged; the S1 test proves the document still validates against the untouched schema. I judged this NOT to trigger the "schema lacks a field you need → needs_split" stop rule because the schema permits (and the accepted precedent establishes) additive extension; if the gate reads the hard rule more strictly, the fallback is a contract-extension task for a `coverage` section, and the builder isolates the change to `_fact_value()`/`build_property_profile()`.
2. **404 for no_match** (documented choice; alternative 200-with-state rejected because the resource genuinely does not exist in the official dataset and REST/`GET /properties/{id}` semantics should stay conventional for downstream consumers).
3. **Status mapping**: schema_drift→502, timeout→504, rate_limited/source_unavailable→503 (packet allowed "502/424-style"; 424 rejected as it implies a failed prior request by the client).
4. **Column bucketing** (`LOT_FACT_COLUMNS`/`BUILDING_FACT_COLUMNS`/`MAPPED_FEATURE_COLUMNS` in builder.py) is deterministic presentation grouping, not legal logic; identity columns (bbl/borocode/borough/block/lot) are bucketed as lot facts so identifier conflicts are visible as `data_conflict` on concrete fact values (S4). Unbucketed columns remain fully available in `provenance`.
5. **Completeness policy**: `lotarea` and `zonedist1` are the critical columns (prerequisites for any FAR/feasibility calculation); all other absent columns are `missing_noncritical`. Platform policy, documented in builder.py — flagged for reviewer sanity-check.
6. **zip_code zero-padding** (`f"{v:05d}"`): deterministic inverse of Socrata number-typing stripping leading zeros — same class of rule as the accepted BBL decimal-tail normalization; raw value stays verbatim in provenance.
7. **`profile_revision` is always 1**: stateless build; monotonic per-property revisions require the M2 persistence tables (documented in builder.py).
8. **borough name mapping** (1→Manhattan…) grounded in common.schema.json / Geoclient User Guide §2.2.1, not invented.

## 8. Known limitations

- No authentication/authorization/organization scoping (see §9) and no rate limiting on the endpoint itself.
- Profile contains PLUTO facts only — no Geoclient address resolution, no geometry beyond the PLUTO point coordinates, no DOB/DOF/ACRIS facts (M2 scope). `zoning.districts` are PLUTO-reported strings, not GIS-verified districts.
- S6 idempotency is "identical modulo volatile fields": `profile_version.generated_at` (real clock in the route) and `reproducibility.correlation_id` (fresh per request, by design for tracing) differ between calls; everything else including provenance ids is byte-identical.
- Drift monitor is a logging stub (documented above), not a scheduled job.
- No live smoke test in this task (offline fixtures only, consistent with M1-T002; connector live behavior was verified at M1-T002 G1/G3).
- `conflict_status="resolved"` and `user_confirmations` flows are contract-present but always empty here (no user-confirmation workflow until M2).

## 9. Security and provenance impact (G5 notes)

- **G5 CONDITION — no auth yet**: M0-T007/T008 (Supabase auth) are blocked on the Supabase token. The endpoint and app are marked INTERNAL/DEV in `main.py` and `properties.py` docstrings + OpenAPI description and must not be exposed publicly until auth lands. This is the packet's declared risk; it needs explicit tracking at the gate.
- All four M1-T002 G5 findings (F1–F4) implemented with adversarial tests; F5 consumer contract implemented in the route (payload-only logging; unexpected exceptions logged as type+correlation_id only, because their chains may embed untrusted upstream strings).
- Responses never contain: stack traces, exception chains, header material, the app token (canary-tested end-to-end with env token set), or unsanitized untrusted strings (errorCode repr-sanitized; BBL raw_value repr-sanitized by the existing bbl.py payload).
- Provenance: every fact value's `provenance_ref` resolves (S1 test + builder's own `_assert_provenance_integrity` enforcing the schema's backend-enforcement rule at runtime); no fact exists without a source_fact v1 record; conflicts never silently resolved; identity is never derived from a conflicting component.
- No new runtime dependency (route/builder use FastAPI + stdlib; jsonschema stays dev-only).

## 10. New risks / dependencies

- Additive-keys adjudication (assumption 1) — if rejected, a small contract task + builder tweak is needed.
- The 10 MiB F1 cap is a constant; a legitimate future bulk endpoint (M2) must use pagination, not a bigger cap.
- Repointing transport tests to `_OPENER` means any future transport change must keep that seam stable.

## 11. Recommended next tasks

1. M2: scheduled connector-health/drift monitor job calling `check_columns_for_drift` (replaces the documented hook stub) + source-registry health record updates.
2. Auth/organization enforcement on /api/v1 (unblocks the public-exposure condition) once the Supabase token arrives.
3. Property/Confirm browser screen (Owner Priority 4) consuming this endpoint.
4. M2 persistence: property_profiles table + monotonic profile_revision + user-confirmation flow.

## 12. Report path

`project-control/reports/M1-T005-producer-report.md` (this file)

---

## 13. D1 fixup 2026-07-16 (G3 review defect D1, Medium)

**Defect (from `project-control/reports/M1-T005-G3-review.md` D1):** `_drift_monitor_hook()`, the no_match mapping, `build_property_profile()`, and the 200-response construction ran OUTSIDE the route's `try/except`, so any exception there bypassed the documented 500 contract (Starlette plain-text 500, no `state=internal_error` body, no `X-Correlation-ID` header, full-traceback logging contrary to the M1-T002 G5 F5 payload-only policy).

**Change — `services/api/app/api/v1/properties.py`:**

- Extracted the generic-500 construction into a new helper `_internal_error_500(exc, correlation_id)` (after `_json`, ~lines 107-127): logs `type(exc).__name__` + correlation id ONLY (never `str(exc)`/traceback), returns the documented body (`state=internal_error`, message, `correlation_id`) with the `X-Correlation-ID` header.
- The fetch block's `except Exception` now delegates to that helper (~lines 236-237).
- Step 3 (drift hook + no_match 404 mapping + builder + 200 construction, ~lines 239-267) is now wrapped in its own `try: ... except Exception as exc: return _internal_error_500(exc, correlation_id)`. Deliberately a SEPARATE try so the `except PlutoConnectorError` mapping stays scoped to fetcher-raised errors only; any post-fetch exception maps to the generic 500, exactly per the documented semantics table.

**Tests — `services/api/tests/api/test_properties_v1.py`:**

- New `raw_client` fixture: `TestClient(app, raise_server_exceptions=False)` so the tests assert the wire-visible HTTP behavior instead of the harness re-raising.
- New shared assertion helper `_assert_documented_generic_500`: 500 status, `X-Correlation-ID` header present, JSON body (`response.json()` would raise on Starlette's plain-text default), `state=internal_error`, body `correlation_id` == header value, and leak-absence (`secret-internal-path`, `hostile`, `Traceback`, `File "` all absent from body).
- `test_s5_builder_exception_is_500_generic_no_internals` — monkeypatches `app.api.v1.properties.build_property_profile` to raise `RuntimeError("secret-internal-path C:\hostile\r\n::injected")` over the real F01 fixture fetch; asserts the documented generic 500.
- `test_s5_drift_hook_exception_is_500_generic_no_internals` — same for `_drift_monitor_hook` raising `ValueError`.

**Evidence (exact commands from the worktree):**

```
$ cd services/api && python -m pytest tests -q
........................................................................ [ 50%]
......................................................................   [100%]
142 passed in 1.55s

$ python -m pytest tests/api/test_properties_v1.py -q -k "builder_exception or drift_hook_exception"
tests\api\test_properties_v1.py ..                                       [100%]
====================== 2 passed, 39 deselected in 0.70s =======================

$ python -m ruff check app tests
All checks passed!
```

142 = the reviewer-reproduced 140 + the 2 new D1 regression tests; 0 failures, 0 skips. Files touched by this fixup: `services/api/app/api/v1/properties.py`, `services/api/tests/api/test_properties_v1.py`, this report section. No contract, builder, or connector changes. D2-D6 untouched (D2/D4 belong to the contract v1.1 follow-up task per the G3 adjudication).
