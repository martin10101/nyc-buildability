# G5 SECURITY & PRIVACY GATE REPORT — M4-T005

**Task:** M4-T005 — internal flag-gated `GET /api/v1/properties/{bbl}/rule-evaluation`
**Frozen SHA reviewed:** `84b50a722d518d0ae6c233ee38affedbdaaebea3` (PR #84)
**Reviewer role:** security-reviewer (read-only, ADR-005)
**Verdict:** **PASS**

## Setup note (not a defect)
The mandated `git reset --hard 84b50a7…` is blocked by the read-only guard. Verified equivalence: worktree HEAD is `f1e6772`, two commits ahead of the frozen SHA; `git diff --stat 84b50a7..f1e6772` shows those commits touch **only** `project-control/reports/*`, `state.json`, `tasks/M4-T005.json` — zero implementation files. The reviewed tree is byte-identical to the frozen SHA for all code under review.

## Test evidence (executed read-only)
- `pytest tests/api/test_rule_evaluation_api.py tests/contracts/test_rule_evaluation_contract.py tests/rules/test_installed_deployability.py` → **59 passed**
- `pytest tests/rules/test_zr_snapshot_bundle.py` → **6 passed**

## Per-requirement findings

**1. Server-side production-disable, fail-safe — PASS.** `config.py:30` `_TRUE_TOKENS = {"1","true","yes","on"}`; `internal_rule_eval_enabled()` (`:33-44`) returns `False` for `None` and any token not in the closed set (empty/`"0"`/`"maybe"`/whitespace → False). Handler checks the flag **first**, before minting a correlation id or touching input (`rule_evaluation.py:144-145`), returning `_not_found()` = `JSONResponse(404, {"detail":"Not Found"})` with **no** X-Correlation-ID and no feature hint. Route `include_in_schema=False` (`:131`). Test `test_as4_flag_off_or_unknown_is_generic_404` (`:308-324`) covers `None,"","0","false","off","maybe","2","  "` and asserts body == `{"detail":"Not Found"}`, absence of `rule`/`evaluation`/`flag`, no correlation-id header. `test_as4_openapi_never_lists_the_internal_route` confirms the path is absent from `/openapi.json` even with the flag ON. Default production posture = disabled.

**2. Frontend cannot call it when disabled — PASS.** `rule-evaluation.ts:79-95`: `ruleEvaluationFlagEnabled()` reads the flag via **dynamic bracket access** on a name **not** `NEXT_PUBLIC_`-prefixed — never inlined into the client bundle. `ruleEvaluationSurfaceEnabled()` requires BOTH env flag AND `?ruleeval=on`; invoked only from the Server Component `page.tsx:30`, passing a plain boolean prop. `PropertyLookup.tsx:164` mounts `RuleEvaluationPanel` only when true; the fetch lives inside that panel, so when off no request is issued. `rule-evaluation-flag-off.spec.ts` records every request URL and asserts `hits …toEqual([])` for the no-opt-in and `?ruleeval=off` cases.

**3. No browser-supplied authority — PASS.** Handler signature takes only the `bbl` path param + two server-injected dependencies; **no** request body/`Request`/profile parameter. Profile rebuilt server-side via trusted `fetcher → build_property_profile → validate_profile`. Substrate from server-side provider default (returns `None` → honest fail-safe), never from the request.

**4. No sensitive leakage — PASS.** Generic-500 handlers log **type + correlation-id only** (`:194-196, 285-290`), never `logger.exception`, never `str(exc)`/traceback. Grep confirms no `TEMP-DEBUG` and no `logger.exception` anywhere in `services/api/app` at the frozen SHA. `test_as10_internal_error_is_generic_500_no_internals` injects `RuntimeError("secret-internal-path C:\\hostile\r\n::injected")` and asserts none of `hostile`/`secret-internal-path`/`Traceback`/`File "` appear. `test_as10_error_bodies_never_leak_token_or_stack` sets a canary `SOCRATA_APP_TOKEN` and asserts absence across 502/503/504. Frontend reflected text length-capped + control-stripped (`bounded.ts`), correlation ids token-allowlisted. Strict `JSONResponse`.

**5. Injection / SSRF / input validation — PASS.** BBL normalized via `normalize_bbl` before any network I/O; malformed → typed 422 with zero connector calls. Fetcher/connector is the accepted trusted path (URL not request-derived). Finished document strictly validated against the bundled schema before send.

**6. New attack surface from the deployability fix — PASS.** `snapshots.py:47-77` resolves package data from a **hardcoded** package name `app._zr_snapshots.v1` via `importlib.resources.files(...)` globbing `*.snapshot.json` — no request-derived path, no traversal. Snapshots carry `content_digest_sha256` tamper-evidence. `response.py:197-199` loads bundled schemas the same way. Byte-identity proven by the guard tests.

**7. Dependencies / secrets / privacy unchanged — PASS.** `pyproject.toml` adds no new runtime dependency (only package-data declarations). No secrets in code; no service-role key in the frontend.

## Explicit determinations
- **Provably unreachable anonymously in the default/production config:** YES. With `INTERNAL_RULE_EVAL_ENABLED` absent/empty/unknown (the default on every deployed service), the flag-first guard returns a generic 404 identical to an unmounted route, no correlation id, no OpenAPI entry.
- **Can the frontend accidentally call it when disabled:** NO. The non-public env flag is never inlined into the client bundle, the fetch is only mounted behind the two-factor server-decided boolean, and the flag-off e2e spec asserts zero `/rule-evaluation` requests.

## Vulnerabilities
None (Critical/High/Medium/Low): none identified.

## Observations (non-blocking, informational)
- The shared property-route transport (`resilience/transport.py:467`) uses `str(exc)` routed through `hooks.sanitize_network_reason`; pre-existing M2 code outside M4-T005's new surface, not exercised as raw output by this endpoint. No action required.

## Final verdict: **PASS**
