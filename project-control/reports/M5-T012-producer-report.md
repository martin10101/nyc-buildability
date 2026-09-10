# M5-T012 Producer Report

**Task:** Expose the deterministic scenario optimization toolkit (sensitivity / ranking /
comparison / threshold) via the internal flag-gated scenario API.

**Branch:** `task/M5-T012-scenario-analysis-api`
**Producer:** backend-engineer (run lineage persistent-local-28)
**Status:** producer self-check complete; **reworked 2026-09-09** after orchestrator pre-gate
validation found the AS-7 offline test deadlocking the api suite — see section 8 for the root
cause, the new egress-seam mechanism, and the RED/GREEN proof; resubmitted for independent
review (G0/G1/G3/G4/G5).

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

- `python -m pytest services/api/tests/api` — **216 passed in 6.04s** (exit 0, terminated normally)
- `python -m pytest services/api/tests/scenario` — **388 passed in 0.94s** (exit 0, terminated normally)

Modularity: `scenario_analysis.py` is a single cohesive route-adapter responsibility (well under
the 600-SLOC warn threshold; no domain logic, storage, or serialization mixed in). The
`python tools/modularity_check.py --check` run is an orchestrator/CI step (not a
packet-documented producer command); the module was authored to pass it, and it was run as a
self-check: **exit 0** (only pre-existing `tools/**` warn signals, none under `services/api`).

Lint: run the way CI runs it (from `services/api`, with the repo's own config —
`line-length = 100`, `select = ["E", "F", "I", "UP", "B"]`, local ruff 0.13.0 == the version pinned
in `requirements-tools.lock`):
`ruff check tests/api/test_scenario_analysis_api.py` -> **All checks passed**; the longest line this
task added is 97 characters. `ruff format` is NOT a repository gate (CI runs only `ruff check .`,
`.github/workflows/ci.yml` line 211) and this file is not `ruff format`-clean at `line-length = 100`
on the accepted baseline either, so no reformatting churn was introduced.

**Out-of-scope observation for the reviewer — `ruff check .` currently FAILS on this branch, for
reasons unrelated to M5-T012.** From `services/api`, the exact CI command reports **27 errors, none
of them in any file this task touched**, all in files carried in from earlier accepted M5 work and
all outside this packet's `allowed_paths` (so they were deliberately left alone):
`app/scenario/comparison.py` (6x E501), `app/scenario/ranking.py` (2x E501),
`app/scenario/sensitivity.py` (2x E501), `app/scenario/breakeven.py` (1x B905),
`tests/scenario/test_scenario_comparison.py` (7x E501, I001, B905),
`tests/scenario/test_scenario_ranking.py` (3x E501), `tests/scenario/test_json_safety.py`
(2x E501), `tests/scenario/test_scenario_sensitivity.py` (1x E501),
`tests/scenario/test_scenario_derive.py` (I001). 4 of the 27 are ruff-autofixable. The CI job
`api (ruff + pytest)` will fail at its Ruff step until these are cleaned up, independently of this
task.

Environment note: CI's other api step is `pytest -q` from `services/api` (the whole package suite,
wider than the two packet-documented commands). That cannot be collected on this machine's Python
3.11 — `app/documents/units.py:276` uses PEP 695 generic syntax (`def _match_unit[UnitT: ...]`),
which needs 3.12 and raises `SyntaxError` at import, producing 15 collection errors under
`tests/documents`. This is the known 3.11-vs-3.12 local gap, not a regression: neither
`tests/api` nor `tests/scenario` imports `app.documents`, and CI runs 3.12.

### Test results

Recorded from the worktree root (`C:/Users/MLFLL/Downloads/nyc-zoning/wt-m5t012`, branch
`task/M5-T012-scenario-analysis-api`). Python 3.11.9 locally; the repo targets 3.12 — these two
suites are version-independent.

```
$ python -m pytest services/api/tests/api
collected 216 items

services\api\tests\api\test_contract_schema_packaging.py ....            [  1%]
services\api\tests\api\test_properties_v1.py ........................... [ 14%]
..............                                                           [ 20%]
services\api\tests\api\test_property_contract.py ....................... [ 31%]
...........                                                              [ 36%]
services\api\tests\api\test_provenance_boundary_api.py ...               [ 37%]
services\api\tests\api\test_rule_evaluation_api.py ..................... [ 47%]
...........                                                              [ 52%]
services\api\tests\api\test_scenario_analysis_api.py ................... [ 61%]
........................................................                 [ 87%]
services\api\tests\api\test_scenario_api.py ...........................  [100%]

============================= 216 passed in 6.04s =============================
```

```
$ python -m pytest services/api/tests/scenario
services\api\tests\scenario\test_scenario_comparison.py ................ [ 28%]
.......................................................                  [ 42%]
services\api\tests\scenario\test_scenario_contract.py .................. [ 47%]
.....                                                                    [ 48%]
services\api\tests\scenario\test_scenario_derive.py .................... [ 53%]
..................................................                       [ 66%]
services\api\tests\scenario\test_scenario_foundation.py ................ [ 70%]
...............                                                          [ 74%]
services\api\tests\scenario\test_scenario_ranking.py ................... [ 79%]
..............................                                           [ 87%]
services\api\tests\scenario\test_scenario_sensitivity.py ............... [ 91%]
..................................                                       [100%]

============================= 388 passed in 0.94s =============================
```

Both commands exit 0 and **terminate** — which is the whole point of section 8: on the first
submission this AS-7 test made `python -m pytest services/api/tests/api` hang forever, so neither
count could be recorded at all. `python tools/modularity_check.py --check` -> exit 0.

## 8. Rework (2026-09-09): the AS-7 offline test deadlocked the api suite

**Defect (blocking, found by orchestrator pre-gate validation).**
`services/api/tests/api/test_scenario_analysis_api.py::test_as7_full_analysis_runs_fully_offline`
never returned — it neither passed nor failed. The packet-documented command
`python -m pytest services/api/tests/api` therefore never terminated, AS-8 ("both suites stay
green") was objectively unmet, and the AS-7 offline guarantee rested on a test that could not run.
Everything else was already green (74 passed with that one test deselected; 141 passed for the api
suite without the new file; 388 passed for `tests/scenario`; modularity check exit 0).

**Root cause (one sentence).** The test asserted the offline guarantee by replacing the
`socket.socket` *class* globally, but Starlette's `TestClient` drives the ASGI app through an anyio
blocking portal on a second thread whose event-loop wakeup needs `socket.socket` for its own
`socket.socketpair()` — emulated over a real AF_INET localhost pair on Windows — so the portal
thread could never service the request and the main thread waited on its future forever.

Confirmed directly, not inferred: a `faulthandler` dump of the hung process shows the main thread
parked in `test_scenario_analysis_api.py:723` -> `starlette/testclient.py:337 handle_request` ->
`anyio/from_thread.py:291 call` -> `_backends/_asyncio.py:2538 run_sync_from_thread` ->
`concurrent/futures/_base.py:451 result` -> `threading.py:327 wait`, and the run had to be killed
(exit 124). `inspect.getsource(socket.socketpair)` on this interpreter (CPython 3.11.9, Windows)
shows the AF_INET emulation calling `socket(family, type, proto)` / `bind` / `listen` / `connect`.
Blocking socket *construction* is therefore the wrong seam: it is infrastructure the in-process
test harness itself requires, not egress.

**New mechanism — assert at the egress seam.** The test now installs *recording* landmines on the
places where outbound I/O actually happens, none of which the anyio portal ever touches:

| Landmine | Why this is the real egress seam |
|---|---|
| `pluto_soda._OPENER.open` | the accepted monkeypatch seam the PLUTO connector opens every URL through (`urllib_transport` reads `_OPENER` at call time) — the same seam `tests/api/test_properties_v1.py` already uses |
| `app.resilience.transport.DEFAULT_OPENER` | the shared fallback opener any other connector resolves at call time |
| `http.client.HTTPConnection.connect` / `HTTPSConnection.connect` | the single socket-connect choke point of every stdlib / urllib / httpx-style client |
| `socket.create_connection` | the lower-level outbound connect helper those call |

Each landmine **records** the attempt into an `egress` list *and* raises `AssertionError`; the
load-bearing assertion is `assert egress == []`. Recording as well as raising is essential rather
than belt-and-braces: the route wraps its fetch stage in `except Exception:` ->
`_internal_error_500` (`services/api/app/api/v1/scenario_analysis.py:443`), so a raise-only
landmine is **swallowed into a typed 500** and a naive test would still pass. The test additionally
asserts *positively* that the two injected seams were the only sources consulted
(`sorted(set(consulted)) == ["pluto_fetcher", "spatial_substrate"]`, with the fixture transport
proven to have been exercised) and that no Socrata credential existed to read
(`pluto_soda.APP_TOKEN_ENV_VAR not in os.environ`) or reached an outbound header (no
`x-app-token` on any header dict handed to the transport).

No `sleep`, timeout, extra thread, `pytest.mark.timeout`, `setrecursionlimit`, skip, or xfail was
used; the test was not deleted or weakened; and `socket.socket` construction is no longer blocked.

**RED/GREEN proof that the new assertion is load-bearing.** Two deliberate egress attempts were
injected into the request path of the final shipped test (temporarily, then reverted), and each
made the test FAIL.

*RED-1 — drop the fetcher override so the route uses the **real** PLUTO connector:*

```
>       assert egress == []
E       AssertionError: assert ['urllib opener.open'] == []
E         Left contains one more item: 'urllib opener.open'
------------------------------ Captured log call ------------------------------
ERROR    app.api.v1.scenario_analysis:scenario_analysis.py:444 scenario_analysis_v1 unexpected_error stage=fetch correlation_id=d4c270ac5cd340878619f397d2609363
FAILED services\api\tests\api\test_scenario_analysis_api.py::test_as7_full_analysis_runs_fully_offline
1 failed, 74 deselected in 0.97s
```

The captured log line is the proof that the *recording* list is what catches the egress: the route
translated the landmine's raise into a generic 500, exactly as predicted, so a raise-only landmine
would have been invisible.

*RED-2 — a direct `http.client.HTTPSConnection(...).request("GET", "/")` in the request path, i.e.
an egress route that bypasses the connector's opener entirely:*

```
>       assert egress == []
E       AssertionError: assert ['http.client...tion.connect'] == []
E         Left contains one more item: 'http.client.HTTPSConnection.connect'
FAILED services\api\tests\api\test_scenario_analysis_api.py::test_as7_full_analysis_runs_fully_offline
1 failed, 74 deselected in 1.05s
```

*GREEN — the shipped test with both injections reverted (and it terminates):*

```
$ python -m pytest services/api/tests/api/test_scenario_analysis_api.py -q -k "full_analysis_runs_fully_offline"
.                                                                        [100%]
1 passed, 74 deselected in 0.93s
```

**No product-code change was required, and no security finding.** The RED/GREEN proof exposed no
egress path in `services/api/app/api/v1/scenario_analysis.py`: with the injected fixture seams in
place the route makes zero outbound connection attempts on any of the four monitored seams. This
was a test-harness defect, not a defect in the route.

**Files changed by the rework** (both inside the packet's allowed paths):

- `services/api/tests/api/test_scenario_analysis_api.py` — 4 added imports
  (`http.client`, `os`, `app.connectors.pluto_soda`, `app.resilience.transport`) plus the rewritten
  `test_as7_full_analysis_runs_fully_offline`; nothing else in the file was touched.
- `project-control/reports/M5-T012-producer-report.md` — real recorded counts/timings in section 7
  and this section 8.
