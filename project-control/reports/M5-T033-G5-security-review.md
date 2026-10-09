# M5-T033 G5 security review (verbatim reviewer return; security-reviewer, read-only, pinned 62dd97cb)

Saved verbatim by the orchestrator per the report-preservation rule.

---

# G5 Security Review — M5-T033

**Task:** M5-T033 (D-059-R004 spatial-failure protocol docs + regression tests)
**Reviewed SHA:** 62dd97cb495dd3d803ee80f447caaf403d5b4828 (HEAD verified == pinned)
**Diff range:** 8ef65c88..00be16d3
**Scope reviewed:** rule_evaluation.py + live_provider.py (comment-only), 3 api test files (new), RENDER_INTERNAL_WEB_DEPLOY_CHECKLIST.md §6a/6b, producer report.

## VERDICT: PASS

No critical/high/medium/low findings. One informational note.

## Findings (by required check)

**1. Secret/URL/credential leakage — PASS.**
Checklist uses the `<nycdf-api-origin>` placeholder convention consistently (docs/RENDER_INTERNAL_WEB_DEPLOY_CHECKLIST.md:340,344,354); no real onrender host or private origin committed. §6b explicitly states the deployed value is "environment-scoped and owner-visible only… this checklist never asserts what a deployed service currently carries." Producer report:135 references only the non-secret localhost code default `http://127.0.0.1:8000`, flagged as non-functional for deploy — reinforcing the owner-pasted convention, not leaking. BBL `1008350041` is a public control parcel (350 Fifth Ave), not sensitive. No token/key/password/bearer strings introduced.

**2. Log-content discipline / hostile-text echo — PASS.**
`_fail_safe` (live_provider.py:182-190) logs ONLY `event`, `type(exc).__name__`, `correlation_id` — never `str(exc)`; docstring: "Never str(exc) (the chain may embed untrusted upstream strings)." This is the actual prompt-injection/hostile-text defense at the log boundary and it is unchanged and correct. The canary assertions are real and verify it: tests assert injected upstream detail (`canary-m5t033-detail`, `canary-m5t033`, `canary-shared`) never appears in the logged line NOR in `response.text` (test_rule_evaluation_api.py new tests; test_live_provider.py:`test_m5t033_flag_on_connector_failure_absent_but_calls_and_logs`, `..._shared_connector_failure...`). Pattern matches the pre-existing M2-T020 `canary-upstream-detail` fence.

**3. Flag doc cannot enable an unauthenticated route — PASS.**
Both internal routes are `include_in_schema=False` and independently env-gated. `LIVE_SPATIAL_PROVIDER_ENABLED` only decides whether the *already-gated* rule-eval route composes a real substrate vs fail-safes to `spatial_intersection_absent`; §6a states the route "must **also** be enabled (§6 step 2)" — INTERNAL_RULE_EVAL_ENABLED warnings preserved. Scenario route: guard checked FIRST (scenario.py:174 → 404 `{"detail":"Not Found"}`, byte-indistinguishable from unmounted, before any input touched); gated by `INTERNAL_SCENARIO_ENABLED` only, verified in config.py. No new reachable surface documented.

**4. No new external hosts / network calls in tests — PASS.**
All connectors are injected doubles: `RecordingLiveFetchers`/`RecordingFetchers` via `monkeypatch.setattr(live_provider_module, "_ACTIVE_FETCHERS", …)` and `install_fetcher(...)`; failures injected via `ZtldbUpstreamError`. Flag-off tests assert ZERO connector calls (`recording.ztldb_calls == []`). No real hosts, DNS, or sockets. Evaluator-level test (test_rules_integration.py) runs pure in-memory `evaluate_property`.

**5. No weakening of fail-safe defaults — PASS.**
`live_spatial_provider_enabled` (live_provider.py:72-80): `None`/absent → `False`; only explicit true token in `_TRUE_TOKENS {1,true,yes,on}` → `True`. `internal_scenario_enabled`/config `_flag_enabled` identical. Comment edits *strengthen* accuracy ("The CODE default, when the variable is absent/empty/unknown, is DISABLED"). No default flipped; unset = disabled everywhere (route absent-substrate, scenario 404, zero connector I/O).

## Cross-cutting

- **Cross-tenant isolation:** BBL-keyed, per-request `correlation_id` minted after guards; no shared mutable state added (fetchers monkeypatched/auto-restored per test). No concern.
- **Least privilege:** internal routes double-gated, off by default, not in OpenAPI. Confirmed.
- **SSRF/injection:** no user-supplied URL/host reaches connectors here; comment-only prod change adds no I/O.
- **Modularity:** comment/docstring-only prod edits; no growth, no responsibility mixing. Producer claim "no code path/signature/token set/contract changed" matches the diff.
- **Test execution:** thin-client env; CI is the execution authority per packet. Static verification of assertions + underlying code confirms behavior; not a BLOCKED condition.

## Informational (no action required)

- I1 — producer-report.md:135 documents the localhost default `http://127.0.0.1:8000` for `NEXT_PUBLIC_API_BASE_URL`. Benign (non-secret, code default) and consistent with the owner-pasted-origin convention; noted only for completeness.

**Recommendation:** Record G5 PASS. Diff is comment + docs + injected-double tests; all fail-safe, log-redaction, route-gating, and no-leak invariants verified against actual source at the pinned SHA.
