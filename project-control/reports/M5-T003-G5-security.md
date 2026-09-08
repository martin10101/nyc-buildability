# GATE REPORT — G5 Security/Privacy — M5-T003 (Scenario endpoint)

**Reviewer:** security-reviewer (independent, read-only). **Reviewed SHA:** `30d6e3b4`. **Verdict: PASS.**
(Verbatim reviewer return preserved below.)

---

**Task:** M5-T003 — `GET /api/v1/properties/{bbl}/scenario`
**Reviewed SHA:** `30d6e3b4a9e9fa4e90740b58a57af883c5145b66` (candidate HEAD)
**Reviewer role:** independent security-reviewer (read-only)
**Directive regime:** in-regime, `directive_refs: D-038:ALL`; applicable-to-M5-T003 = **D-038-R003, D-038-R004** (R001/R002/R005/R006/R007 bind `D-038-BOOTSTRAP`, not this task)

## VERDICT: PASS
No critical, high, or medium security/privacy findings. Two low/informational observations; neither blocks acceptance. Independent reproduction matches the orchestrator-captured evidence.

## Reproduction
`cd services/api; python3.11 -m pytest tests/api/test_scenario_api.py -q` => **27 passed** in 2.19s (matches M5-T003-orchestrator-captured-evidence.md). Python 3.11.9. `scenario.py` uses only PEP-604 unions (`str | None`), no PEP-695 — version-safe on 3.11 and 3.12. The unrelated `tests/documents/**` PEP-695 collection failure is out of M5-T003 scope.

## Requirement-by-requirement (security-relevant)
- **D-038-R004 (no Supabase / no Geoclient / offline) — VERIFIED PASS.** Handler consumes only injected `get_pluto_fetcher` + `get_spatial_substrate_provider` (scenario.py:54-66,163-166). Grep of the full request-path closure finds NO Supabase or Geoclient import/call (only docstring refs). Substrate default uses public ArcGIS/SODA and is itself flag-gated off by default. AS-7 runs with `SOCRATA_APP_TOKEN` unset, no network.
- **D-038-R003 (product deliverable)** — real user-facing/domain endpoint with AS-1..AS-7; security substance confirmed. (Formal directive row owned by directive-compliance-verifier.)

## Security checklist
1. **Flag-gate fail-safe — PASS.** `internal_scenario_enabled()` true only for `{1,true,yes,on}`; absent/empty/unknown → False. Flag check is the FIRST handler statement, before correlation id / input / seam calls. Disabled → generic `404 {"detail":"Not Found"}` with no `X-Correlation-ID`, matching an unmounted path; `include_in_schema=False`. Enforced by test_as6_* (parametrized), landmine-seam non-invocation, and OpenAPI-absence tests. No 403/501 leak.
2. **Info leakage — PASS.** Exception + contract-defect paths log only stage/location/correlation_id — never `str(exc)` or traceback. Bodies carry state + fixed generic message + correlation_id only. Tests assert hostile string / "Traceback" / `File "` absent. SOCRATA token is an `X-App-Token` header, never in URL/logs/payload.
3. **Input surface — PASS.** Only `bbl` path param; no body/query/profile. `normalize_bbl` before any connector call → malformed BBL = 422 with zero network I/O. 422 `raw_value` echoes caller input repr()-sanitized under `nosniff` + CSP `default-src 'none'`.
4. **Prompt-injection / untrusted data — PASS.** Scenario rests entirely on server-rebuilt facts. No LLM/AI, no openai/anthropic/httpx, no eval/exec/subprocess in scenario/** or request-path modules. Cap surfaced verbatim from the trace, never recomputed.
5. **Cross-tenant / storage / SSRF / least-privilege / log-redaction — PASS.** No auth/tenancy yet by design (M0-T007/T008 blocked); endpoint touches no user/tenant data and no storage — public BBL-keyed data, no cross-tenant surface. No caller-controlled URL → no SSRF (SODA URL server-built from validated 10-digit BBL). Read-only, two injected read seams, default-off. `Cache-Control: no-store` service-wide.

## Low / informational (non-blocking)
- **INFO-1 (low, pre-existing pattern):** a non-GET to the path when flag OFF returns Starlette 405 (path matched, method not), vs 404 for a truly unmounted path. Discloses only that the PATH is mounted (not that the feature is enabled), identical to the accepted rule_evaluation sibling, moot while internal-only. R-004 concerns the GET 404 indistinguishability, which holds exactly. Optional remedy: catch-all method handler returning generic 404 when flag off. Defer to the exposure/auth milestone; not a G5 blocker.
- **Process note to orchestrator:** `directives/D-038/verification.json` has `task_verifications: []`. The independent directive-compliance verification of D-038-R003/R004 (directive-compliance-verifier; producer ≠ verifier) is not yet recorded; per ADR-005 acceptance must not be recorded until that row exists at reviewed_sha == HEAD. Security substance of R004 verified here independently.

## Modularity spot check
scenario.py 307 SLOC, single responsibility, mirrors accepted rule_evaluation.py, imports the scenario engine read-only, no new dependency. `modularity_check --check` → 0 failures, no M5-T003 warnings.

**VERDICT: PASS** (G5). No critical/high/medium; one low side-channel (INFO-1) deferred; one process note re the not-yet-recorded directive verification row.
