# M5-T033 G3 code review (verbatim reviewer return; code-reviewer, read-only, pinned 62dd97cb)

Saved verbatim by the orchestrator per the report-preservation rule.

---

## G3 CODE REVIEW — M5-T033 — VERDICT: PASS

Reviewed at pinned HEAD `62dd97cb` (confirmed via `git rev-parse HEAD`). Material commit `00be16d3`, diff `git diff 8ef65c88..00be16d3`. Static verification against source; test execution is deferred to the api CI job at the seam per packet AS-6 (thin-client — I did not run pytest, this is not a BLOCKED condition).

### 1. Production deltas are behavior-neutral (VERIFIED, byte-level)
Stripping comment (`^\s*#`) and blank lines from both file versions yields **IDENTICAL** output for `services/api/app/api/v1/rule_evaluation.py` and `services/api/app/spatial/live_provider.py`. Both hunks are entirely inside `#` comment blocks (rule_evaluation.py lines 78–95; live_provider.py lines 61–64). Zero executable-line change. The "comment-only correction" claim holds.

### 2. AS-1 / AS-2 signatures — observably distinct, both parcels, no network (PASS)
- **Flag-off (branch A):** `test_live_provider.py::test_m5t033_flag_off_absent_for_every_bbl_zero_calls_no_log` (parametrized `_D059_BBLS = ("3052960043","3022647515")`) asserts `None` + `ztldb/lot/layer_calls == []` + `_fail_safe_lines(caplog) == []`. Counts asserted *after* return (an exception would be swallowed by the fail-safe `except` — comment on that is correct). Verified against source: `default_live_substrate` short-circuits at line 245 before touching `_ACTIVE_FETCHERS`.
- **Flag-on failure (branch B):** `test_m5t033_flag_on_connector_failure_absent_but_calls_and_logs` (both parcels) asserts `None` + `ztldb_calls == [(bbl, CID)]` + exactly one line `event=connector_error` / `error_type=UpstreamError` / no canary. Matches source `_fail_safe` format (live_provider.py:186) and call order ztldb→lot→layer (build_live_substrate:207–231).
- **End-to-end route parity:** `test_rule_evaluation_api.py` reproduces both branches through the DEFAULT seam; branch B additionally binds `recording.ztldb_calls == [(BBL, X-Correlation-ID)]`, proving the logged `correlation_id` equals the response header — a real discriminator, not a coincidence.
- **No network / no flakiness:** connector doubles via `monkeypatch.setattr(live_provider, "_ACTIVE_FETCHERS", …)`; env via `monkeypatch.delenv/setenv`. Matches the module's per-call `os.environ` read (live_provider.py:76), so the monkeypatch contract is sound. Deterministic fixtures; no timing/random dependence.

### 3. Counter-example defeats the false inference (PASS)
`test_m5t033_shared_connector_failure_is_uniform_absent_flag_on` sets the flag ON and injects the SAME ZTLDB error across both D-059 parcels **and** the control `1008350041`, asserting `results == [None, None, None]`, one `connector_error` line per parcel, connector consulted each time. This concretely demonstrates that uniform-and-fast absence does NOT imply flag-off — exactly the D-059-R004 warning. Reinforced by `test_m5t033_flag_on_healthy_connectors_resolves_not_absent` (flag-on CAN resolve). The distinction (zero-calls-no-log vs calls+one-typed-line) is the pinned discriminator.

### 4. Report / checklist ↔ code contract (CONSISTENT)
Verified every cross-reference the checklist rests on:
- `config.py:34,60` — `INTERNAL_SCENARIO_ENABLED_ENV_VAR` + `internal_scenario_enabled()` exist.
- `integration.py:81` — `FAILSAFE_SPATIAL_ABSENT = "spatial_intersection_absent"`.
- `scenario.py:160,174` — route `include_in_schema=False`, gated by `internal_scenario_enabled()` (not the rule-eval flag) — matches §6a claim.
- Live-capture commit `f0e7d82f` (M5-T033-live-capture.md:5) matches checklist §6b's captured-deployment caveat.
- Producer report AS-4 does not overclaim: states runtime cause "UNCONFIRMED", and "M4-T020/B4 does NOT fix this" (report §1 lines 42,49–50). Epistemically disciplined; the §6b table and "absence of a connector-error log does NOT prove flag-off" caveat are logically sound.

### Standing licence — consumers of changed modules
`rule_evaluation.py:65` imports `default_live_substrate`; used in the DEFAULT provider seam at line 101. Depth-1 consumer claim in the packet's navigation block is accurate. Because both edits are comment-only, behavioral blast radius is nil. **D-066-R002:** the code-graph navigation block was accurate and useful — its depth-1 consumers (rule_evaluation.py + the two test modules) and the `integration.py:81 FAILSAFE_SPATIAL_ABSENT` pointer all matched source on verification.

### Non-blocking observations (no action required)
- `test_rules_integration.py` asserts both `== ri.FAILSAFE_SPATIAL_ABSENT` and the literal `== "spatial_intersection_absent"` — a deliberate belt-and-suspenders pin that would catch an accidental constant-value drift. Good.
- API-level D-059-parcel coverage runs on the module fixture BBL by design (the route fetches a PLUTO row keyed to that BBL); per-parcel coverage is delegated to the provider and evaluator levels where no PLUTO fetch occurs and the real parcels flow through unmodified. Documented in-test and in the report; AS-3 is satisfied.
- Modularity: no new production lines (comments only) + new tests/doc; no threshold or responsibility concern.

**Verdict: PASS.** No FAIL/BLOCKED findings. Production deltas are byte-verified behavior-neutral; the two failure signatures are pinned as observably distinct across both D-059 parcels with no network; the shared-failure counter-example prevents the uniform-absence⟹flag-off misinference; report/checklist are internally consistent with the verified code contract. Execution authority for the suite remains the api CI job on the pushed head (AS-6), captured by the orchestrator at the seam.
