# M5-T012 Producer Report

**Task:** Expose the deterministic scenario optimization toolkit (sensitivity / ranking /
comparison / threshold) via the internal flag-gated scenario API.

**Branch:** `task/M5-T012-scenario-analysis-api`
**Producer:** backend-engineer (run lineage persistent-local-28)
**Status:** producer self-check complete. **Reworked twice.** (1) Pre-gate validation found the
AS-7 offline test deadlocking the api suite — section 8. (2) The G1/G3/G5 gate wave found three
BLOCKING defects (unpaired surrogates crashing all four endpoints, top-level-only fact-key
rejection, an unguarded engine call) plus seven surviving mutations — section 9, with the RED/GREEN
and mutation evidence for each. Resubmitted for independent review (G0/G1/G3/G4/G5).

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
  `json.dumps(envelope, ensure_ascii=False, allow_nan=False).encode("utf-8")` before send
  (`test_as5_nan_inf_values_never_reach_the_response`).
- **Strings must also be ENCODABLE TEXT** (added in the gate rework — see section 9). `json.loads`
  accepts the escape `"\ud800"`, an unpaired surrogate, from 22 pure-ASCII bytes: under every cap
  above, yet not encodable. It is a typed 422 in the same iterative walk. The pre-send check uses
  **the renderer's own encoder settings**, so validation and rendering cannot disagree about what
  is encodable — the original `ensure_ascii=True` check was exactly that disagreement.
- **Fact keys are rejected at EVERY depth**, not only the top level (gate rework, section 9).

## 4. Route posture (mirrors M5-T003 exactly)

- **Flag-gated fail-safe.** Reachable ONLY when `INTERNAL_SCENARIO_ENABLED` is an explicit true
  token; absent/empty/unknown → a generic `404 {"detail":"Not Found"}` byte-identical in body and
  headers to an unmounted path (no `X-Correlation-ID`). Proven for all four routes across 8
  non-true flag values, with landmine seams proving no I/O occurs. **Correction (gate wave):** the
  earlier wording "no header/body/timing hint" overclaimed. Two side channels remain and are
  **inherited from the accepted sibling routes** (M5-T003 / M4-T005), verified identical there, and
  recorded as accepted backlog rather than fixed here: a wrong-method request returns 405 rather
  than 404, which is an existence oracle; and the flag-off path is measurably faster (~1.6x) than
  the flag-on path. The body and headers are indistinguishable; *timing and method* are not.
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
  **This was FALSE as first submitted** and is true only after the gate rework: two stages could
  escape as Starlette's plain-text 500 with no `state` and no correlation id — an unpaired
  surrogate in the body (BLOCKING-1) and any engine raise (BLOCKING-3), both emitting a
  `(500, None)` pair absent from `STATUS_STATE_MATRIX`. Both stages are now inside the same
  generic-500 guard as the trusted rebuild, asserted on all four endpoints
  (`test_as4_engine_raise_is_typed_internal_error_500`,
  `test_as4_finish_stage_defect_is_typed_internal_error_500`,
  `test_as5_unpaired_surrogate_is_typed_422`). See section 9.

## 5. No new logic; facade-only; never Verified

- The route performs no independent legal calculation and no engine maths: it rebuilds,
  validates, adapts the request into the engine's documented arguments, calls the engine
  READ-ONLY, and returns its typed result verbatim inside a thin envelope.
- Engine calls go through the public `app.scenario` facade — asserted by object identity in
  `test_as7_engine_calls_use_the_public_facade`.
- Nothing is ever marked Verified; the canonical `NOT_VERIFIED_DISCLAIMER` is present on every
  analysis response (envelope + engine result); the canonical cap is transported VERBATIM from the
  server-rebuilt document (`test_as6_response_is_strict_json_safe_and_never_verified`).
  **This was FALSE as first submitted.** Because fact keys were checked only at the top level, a
  caller could nest `coverage_status: "verified"` / `verified: true` inside an assumption-set and
  the engines echoed it verbatim into `$.result.candidates[0].assumption_set[0]` of a **200** body
  (G1, reproduced by DCV and G5). The AUTHORITATIVE cap was never forgeable — the envelope's
  `scenario_cap_sq_ft` stayed `15000.0` and the engines merge caller data only as
  `{**doc, "assumptions": ...}` — so this was never cap forgery, but a 200 body that *reads* as
  Verified falsifies AS-6 regardless, and an accepted fact-override *attempt* falsifies AS-2.
  Fact keys are now rejected at every depth, and the never-Verified scan walks every envelope key
  and string value at every depth instead of only `coverage_status`. See section 9.

## 6. Acceptance-scenario coverage

- **AS-1** `test_as1_endpoint_returns_engine_result_envelope` (×4, now asserting request→result
  cardinality), `test_as1_cap_equals_rule_evaluation_trace_value_verbatim`,
  `test_as1_result_cardinality_tracks_the_request` (×4 endpoints × 3 counts),
  `test_as1_threshold_default_response_metric_is_the_documented_default`
- **AS-2** `test_as2_fact_injecting_body_is_typed_422` (×11 fact keys),
  `test_as2_injected_cap_cannot_change_the_echoed_cap`,
  `test_as2_nested_fact_key_at_any_depth_is_typed_422` (×4 endpoints × 6 fact keys),
  `test_as2_every_forbidden_fact_key_is_rejected_nested_too` (all 24 keys in the frozenset),
  `test_as2_nested_verified_claim_never_reaches_a_200_body`
- **AS-3** `test_as3_flag_off_or_unknown_is_generic_404` (×4 routes × 8 flag values), `test_as3_openapi_never_lists_any_analysis_route`
- **AS-4** `test_as4_matrix_equals_scenario_route_matrix`, `test_as4_no_scenario_is_a_normal_200_typed_result` (×4), `test_as4_every_emitted_pair_is_in_the_matrix`, `test_as4_internal_defect_leaks_nothing`,
  `test_as4_engine_raise_is_typed_internal_error_500` (×4),
  `test_as4_finish_stage_defect_is_typed_internal_error_500`
- **AS-5** oversized body (many short strings, so the BYTE cap is load-bearing) / deep-nesting
  (40, 600) / oversized string / malformed & non-object / domain-length / assumption-set caps /
  NaN-Inf, plus every cap asserted at its LITERAL value
  (`test_as5_documented_caps_are_the_literal_values`) and exercised at exactly N and N+1
  (`..._is_exact_at_the_boundary` ×6 caps), plus
  `test_as5_unpaired_surrogate_is_typed_422` (×4 endpoints × 8 positions),
  `test_as5_surrogate_body_is_tiny_and_under_every_cap`,
  `test_as5_legitimate_non_ascii_text_is_still_accepted` (×4),
  `test_as5_non_ascii_assumption_text_round_trips_into_the_response`
- **AS-6** `test_as6_response_is_strict_json_safe_and_never_verified` (×4, whole-envelope scan),
  `test_as6_unencodable_engine_result_is_typed_internal_contract_error_500`,
  `test_as6_non_json_safe_engine_result_is_typed_500`
- **AS-7** `test_as7_existing_routes_unaffected`, `test_as7_engine_calls_use_the_public_facade`,
  `test_as7_full_analysis_runs_fully_offline` (×4 endpoints),
  `test_as7_analysis_routes_are_registered_last_and_in_order`
- **AS-8** full `tests/api` + `tests/scenario` suites green; modularity check (see §7)

## 7. Evidence (documented test commands)

- `python -m pytest services/api/tests/api` — **312 passed in 35.48s** (exit 0, terminated
  normally). Was 216 before the gate rework; the 96 added tests are all in this task's own file
  (75 → 171). No pre-existing test changed behaviour.
- `python -m pytest services/api/tests/scenario` — **388 passed in 4.17s** (exit 0, terminated
  normally). Unchanged count: the rework touches no engine module.

Modularity: `python tools/modularity_check.py --check` -> **exit 0**.

**Correction + new warn signal the reviewer should weigh.** The earlier wording "well under the
600-SLOC warn threshold" is no longer true. The gate rework grew `scenario_analysis.py` from
**572 to 666 SLOC** (measured with the tool's own `source_lines`), which crosses `WARN_SLOC = 600`
and now emits:

> `warn review_signal: services/api/app/api/v1/scenario_analysis.py - above the warning threshold;
> consider the module boundary before growing it further`

It is a **warn signal, not a failure** — the check still exits 0, and 666 is well below
`JUSTIFY_SLOC = 750` and `HARD_SLOC = 1000`, so no reviewed exception is required. Recording the
cohesion justification the policy asks for at this band:

- The responsibility did not change. The module is still one route-adapter: flag-gate, correlation
  id, untrusted-body boundary, server-side rebuild over injected seams, facade engine call,
  envelope. No domain logic, no legal calculation, no storage, no serialization format lives here.
- The growth is +94 SLOC across three *boundary* additions the gate required
  (`_fact_injection_error`, `_string_boundary_error`, `_guarded_analysis` — ~35 SLOC of code) plus
  ~60 SLOC of docstring prose explaining WHY each boundary exists (the validator/renderer
  `ensure_ascii` disagreement; the guard asymmetry). That prose is reviewer-facing rationale the
  gate asked for; it was deliberately NOT trimmed to get back under 600, because shrinking an
  explanation to game a line count is the wrong trade.
- If a split is wanted, the natural seam is the untrusted-body boundary
  (`_prepare_request`, `_structural_error`, `_string_boundary_error`, `_fact_injection_error`, the
  cap helpers and the cap constants) into e.g. `app/api/v1/scenario_analysis_input.py`. That would
  create a NEW file and therefore busts this packet's `allowed_paths`, so it is flagged here rather
  than done. Four top-level symbols short of the symbol ceiling either way (18 symbols).

Lint: run the way CI runs it (from `services/api`, with the repo's own config —
`line-length = 100`, `select = ["E", "F", "I", "UP", "B"]`, local ruff 0.13.0 == the version pinned
in `requirements-tools.lock`): `ruff check app/api/v1/scenario_analysis.py app/main.py
tests/api/test_scenario_analysis_api.py` -> **All checks passed**. `ruff format` is NOT a repository gate (CI runs only `ruff check .`,
`.github/workflows/ci.yml` line 211) and the test file is not `ruff format`-clean at
`line-length = 100` on the accepted baseline either, so no reformatting churn was introduced.

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
collected 312 items

services\api\tests\api\test_contract_schema_packaging.py ....            [  1%]
services\api\tests\api\test_properties_v1.py ........................... [  9%]
..............                                                           [ 14%]
services\api\tests\api\test_property_contract.py ....................... [ 21%]
...........                                                              [ 25%]
services\api\tests\api\test_provenance_boundary_api.py ...               [ 26%]
services\api\tests\api\test_rule_evaluation_api.py ..................... [ 33%]
...........                                                              [ 36%]
services\api\tests\api\test_scenario_analysis_api.py ................... [ 42%]
........................................................................ [ 65%]
........................................................................ [ 88%]
........                                                                 [ 91%]
services\api\tests\api\test_scenario_api.py ...........................  [100%]

============================ 312 passed in 35.48s =============================
```

```
$ python -m pytest services/api/tests/scenario
services\api\tests\scenario\test_scenario_breakeven.py ................. [ 12%]
................................................                         [ 24%]
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

============================= 388 passed in 4.17s =============================
```

Both commands exit 0 and **terminate**. `python tools/modularity_check.py --check` → exit 0.
`ruff check` from `services/api` on the three files this task owns
(`app/api/v1/scenario_analysis.py`, `app/main.py`, `tests/api/test_scenario_analysis_api.py`) →
**All checks passed**.

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

## 9. Gate-wave rework (G1 FAIL / G5 FAIL / G3 PASS-with-corrections)

Three BLOCKING defects and seven surviving mutations, fixed in one pass. `app/main.py` was **not**
modified (the registration-order finding is a test gap, not a code defect), and no engine module or
`app/config.py` was touched.

### BLOCKING-1 (G5) — unpaired surrogates crashed all four endpoints

**Defect.** `{"variable": "\ud800"}` — 22 pure-ASCII bytes, under every documented cap — raised an
unhandled `UnicodeEncodeError` and returned Starlette's `500 text/plain "Internal Server Error"`:
no `X-Correlation-ID`, a `(500, None)` pair absent from `STATUS_STATE_MATRIX`, full framework
traceback logged.

**Root cause.** `_finish` validated with `json.dumps(envelope, allow_nan=False)` —
`ensure_ascii=True`, which *escapes* surrogates and therefore never raises — while Starlette renders
with `ensure_ascii=False` + `.encode("utf-8")`, which *does* raise. The pre-send check and the
renderer disagreed about what is encodable, which made the "strict-JSON-safe before send"
assurance false rather than merely incomplete.

**Fix.** Two halves, as the gate specified. (1) The existing iterative walk now checks encodability
of every string value and every dict key (`_string_boundary_error`), returning the existing
`(422, "validation_error")` pair — no new constant, no new matrix pair. (2) The pre-send check is
now `json.dumps(envelope, ensure_ascii=False, allow_nan=False).encode("utf-8")`, so it uses the
renderer's own settings; `UnicodeEncodeError` subclasses `ValueError`, so the existing
`except (ValueError, TypeError)` maps an engine-produced surrogate to the documented
`(500, "internal_contract_error")` pair as a backstop.

**RED → GREEN** (32 hostile bodies = 8 positions × 4 endpoints, driven in-process):

```
RED   B1 surrogate: 1/33 PASS
  sensitivity/variable        500 state=None cid=NO  ct=text/plain       in_matrix=False
  sensitivity/candidate_value 500 state=None cid=NO  ct=text/plain       in_matrix=False
  ranking/objective           500 state=None cid=NO  ct=text/plain       in_matrix=False
  threshold/variable          500 state=None cid=NO  ct=text/plain       in_matrix=False
  (the remaining 28 returned 200 - the surrogate sat in a field that endpoint does not read,
   so it was silently dropped rather than rejected)
GREEN B1 surrogate: 33/33 PASS        (every position x every endpoint -> 422 validation_error + cid)
RED/GREEN B1 non-ASCII ok: 4/4 PASS   (unchanged - the fix rejects ONLY unencodable text)
RED   B1 engine surrogate:  500 state=None ct=text/plain cid=NO
GREEN B1 engine surrogate:  500 state='internal_contract_error' ct=application/json cid=yes
```

### BLOCKING-2 (G1, reproduced by DCV and G5) — `FORBIDDEN_FACT_KEYS` was top-level only

**Defect.** The boundary checked only `body.keys()`. One level down, inside an assumption-set, a
fact-shaped object was accepted and echoed verbatim into a **200** body —
`draft_zoning_floor_area_cap_sq_ft: 987654321`, `coverage_status: "verified"`, `verified: true`, a
fake `rule_evaluation` — at `$.result.candidates[0].assumption_set[0]`.

Not cap forgery: the envelope's `scenario_cap_sq_ft` stayed `15000.0`. But AS-2 requires a body that
*attempts* a fact override to be a typed 422, and AS-6 requires nothing be marked Verified, so both
were falsified. The report's own AS-6 claim is corrected in section 5 accordingly.

**Fix.** Fact-key rejection moved *into* the single iterative walk, so it applies at every depth.
The top-level-only check was deleted rather than duplicated — the body object is the first node
popped, so top-level precedence and the exact 422 message and `detail.rejected_keys` shape are
unchanged. Docstrings and the `FORBIDDEN_FACT_KEYS` comment were corrected from "top-level".

**RED → GREEN:**

```
RED   B2 nested fact: 0/24 PASS   (all 200; echoed_in_200=True for 14 of the 24)
GREEN B2 nested fact: 24/24 PASS  (422 validation_error, fact key named in detail.rejected_keys)

RED   B2 G1 repro  ranking/verified+cap: 200  verified_in_body=True  cap_987654321_echoed=True
GREEN B2 G1 repro  ranking/verified+cap: 422  cap_987654321_echoed=False
```

### BLOCKING-3 (G1 HIGH-1 = G5 HIGH-1) — the engine call and `_finish` had no guard

**Defect.** The four engine calls and `_finish` sat outside any `try/except` while the *trusted*
rebuild stage was guarded — the asymmetry backwards, since the engine is the stage that processes
untrusted input, and this is what let BLOCKING-1 escape as an untyped 500.

**Fix.** One new helper, `_guarded_analysis`, runs the engine call *and* `_finish` inside the same
`except Exception` → `_internal_error_500` guard the rebuild stage uses. All four endpoints route
through it. The engine is still called READ-ONLY through the public `app.scenario` facade; the
callable only defers the call so it lands inside the guard
(`test_as7_engine_calls_use_the_public_facade` still passes on object identity).

**RED → GREEN:**

```
RED   B3 engine raise: 0/4 PASS   500 state=None cid=NO ct=text/plain in_matrix=False  (x4)
GREEN B3 engine raise: 4/4 PASS   500 state='internal_error' cid=yes ct=application/json in_matrix=True
RED   B3 _finish raise: 500 state=None cid=NO
GREEN B3 _finish raise: 500 state='internal_error' cid=yes
```

Aggregate: the same in-process harness reported **63 failures before** the three fixes and
**0 after**, with the legitimate non-ASCII control group passing in both runs (so the encodability
boundary rejects only unencodable text, never real UTF-8).

### Test corrections — mutation-resistance evidence

G3 ran 38 mutations and 7 survived. Each is now guarded, and each guard was *verified* by applying
the mutation to product code, running the guarding tests, and restoring the file byte-exact. **21
mutations applied, 21 caught, 0 survived:**

| id | mutation | caught by |
|---|---|---|
| C1a–C1d | each endpoint drops its cardinality-bearing engine argument (`values`/`assumption_sets`/`domain` → `None`) | `test_as1_endpoint_returns_engine_result_envelope`, `test_as1_result_cardinality_tracks_the_request` |
| C2 | assumption-set cap emits an undocumented `(422, "too_many_sets")` | `test_as5_assumption_set_caps` |
| C3 | envelope gains `verified: True` + `verification_status: "verified"` | `test_as6_response_is_strict_json_safe_and_never_verified`, `test_as1_...envelope` |
| C4 | the `MAX_BODY_BYTES` check is deleted entirely | `test_as5_oversized_body_is_typed_422` |
| C5a/C5b | caps loosened (64 KiB → 256 KiB; domain 256 → 1024) | `test_as5_documented_caps_are_the_literal_values` |
| C6a–C6f | off-by-one `>` → `>=` on all six caps | the six `..._is_exact_at_the_boundary` tests |
| C7 | `main.py` registers the analysis router *before* the pre-existing routers | `test_as7_analysis_routes_are_registered_last_and_in_order` |
| C9 | threshold's default `response_metric` changed POINT → MAX | `test_as1_threshold_default_response_metric_is_the_documented_default` |
| B1/B1b/B2/B3 | each BLOCKING fix reverted individually | the new BLOCKING tests above |

Notes on the corrections:

- **C1** asserts request→result cardinality per endpoint (`point_count` = `len(values)`,
  `candidate_count` = `len(assumption_sets)`, `set_count` = `len(assumption_sets)`,
  `candidate_count` = `len(domain)`), at three different counts, so neither a hardcoded nor a
  defaulted count satisfies it.
- **C4** builds the oversized body from many short strings (`["q"*100]*1200`) in an *uncapped*
  field, so `MAX_STRING_LENGTH` and the list caps cannot fire in the byte cap's place; it also
  asserts the message names bytes. With the cap deleted the body now reaches the landmined rebuild
  stage and the test fails.
- **C6** required a byte-exact body builder: `body_of_exact_size(n)` produces a valid body of
  exactly *n* bytes out of many short strings, and `nested_levels_body(n)` produces exactly *n*
  container levels (the body object counts as level 1).
- **C3** scans every envelope key and string value at every depth. One real finding while writing
  it: the accepted M5-T011 threshold engine deliberately emits `verified: False` on its
  illustrative bracket midpoint (`app.scenario.breakeven._bracket_midpoint`) as an honesty marker,
  so the scan requires every verification-claim key to **deny** verification (`False`/`None`)
  rather than forbidding the key — which still catches `True`, a truthy number, and the string
  `"verified"`.
- **G5 LOW-4**: the AS-7 egress-landmine test is now parametrized over all four endpoints.

### Explicitly carried as backlog (not fixed here)

Per the coordinator, recorded as accepted backlog rather than widened into this change: full-body
buffering before the 64 KiB cap (needs middleware/streaming); no output bound (2,118 B → 925,029 B,
+160…430 ms caller-controlled CPU); the 405-vs-404 method oracle and the ~1.6× flag-off timing
delta (both verified identical on the accepted M5-T003/M4-T005 routes, so inherited); unbounded
raw-BBL reflection in the 422 body (inherited from `bbl.py`) and unenforced `Content-Type`; and the
~27 pre-existing `ruff` errors in earlier accepted M5 files (see section 7).

### Files changed by this rework

- `services/api/app/api/v1/scenario_analysis.py` — BLOCKING-1 (`_string_boundary_error` +
  `ensure_ascii=False` pre-send check), BLOCKING-2 (fact keys folded into the one iterative walk,
  top-level-only check removed), BLOCKING-3 (`_guarded_analysis` wrapping each engine call and
  `_finish`), plus the docstring/comment corrections.
- `services/api/tests/api/test_scenario_analysis_api.py` — 75 → 171 tests: C1–C7/C9 corrections,
  G5 LOW-4, and coverage for all three BLOCKING fixes.
- `project-control/reports/M5-T012-producer-report.md` — the three overclaim corrections, the new
  counts, and this section.
- `services/api/app/main.py` — **unchanged** (confirmed `git diff` empty).
