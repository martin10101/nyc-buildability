# Gate Report

> Saved VERBATIM by the orchestrator from the security-reviewer agent-return channel
> (transport entity-decoding only; a harness sanitizer note preceding the report body was
> transport metadata, not reviewer content, and is omitted). Reviewer ≠ producer.

- Gate ID: G5 (security)
- Task ID: M5-T002
- Reviewer: security-reviewer (independent; NOT the producer)
- Producer: backend-engineer
- Result: **PASS**
- Clean environment/worktree used: review worktree `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t064`, branch `task/M5-T002-scenario-endpoint`, HEAD `2fee786`, content identity `31e652a` (verified via `git diff main...HEAD`)

## Acceptance criteria reviewed

All 10 security-relevant checks in the dispatch were independently re-derived from source at the frozen identity (not taken from the producer's map): fail-safe disable, input surface, information leakage, FH-M5T001-S1/S2, frontend XSS/flag posture, supply-chain/policy, and D-021 holds.

## Directive/requirement verification (security-relevant D-021 subset)

The independent directive-compliance-verifier owns the full D-021 verification.json. From the security lens I confirmed the security-bearing D-021 holds at content identity 31e652a:

| Requirement ID | Content identity | Verdict | Reproduced evidence |
|---|---|---|---|
| D-021 R005-R008 (no supervisor/controller/model-selection/context-pipeline/MCP/settings edits) | 31e652a | PASS | `git diff --name-only main...HEAD` grep for `agent_supervisor|controller|model.?selection|context.?pipeline|mcp|.claude/settings` → NONE |
| D-021 R011 (no test/CI/security-control/branch-protection weakening) | 31e652a | PASS | No `.github/`, workflow, lockfile, pre-commit, gitleaks, or branch-protection file in the diff; every changed test file is NEW (`scenario*`); `fixture_api.py`/`playwright.config.ts` changes are strictly additive env-var additions |
| READ-ONLY backend modules (app/scenario, app/profile, app/spatial, app/rules, packages/contracts) | 31e652a | PASS | `git diff --name-only` grep → NONE touched |

## Steps independently executed

1. Read the full diff (31 files, +4968/-4) and every security-critical source file: `scenario.py`, `config.py`, `main.py`, `scenario.ts`, `scenario-contract.ts`, `bounded.ts`, `ScenarioPanel/Result/Failure.tsx`, `page.tsx`, `PropertyLookup.tsx`, and the reference `rule_evaluation.py` / `bbl.py`.
2. Diffed the endpoint stage-by-stage against the accepted M4-T005 `rule_evaluation.py` posture.
3. Ran the API test suite.
4. Grepped for XSS sinks, secrets, dependency/CI/security-control changes, forbidden-path edits, and non-public-flag leakage into client code.
5. Read the adversarial security tests (flag-off matrix, depth bound, leak-absence, injection) and confirmed they assert the claimed guarantees rather than just exercising happy paths.

## Expected versus actual (findings by review axis)

1. **Fail-safe disable — PASS.** `get_scenario` (`services/api/app/api/v1/scenario.py:188-189`) checks `if not internal_scenario_enabled(): return _not_found()` as the FIRST statement — before `correlation_id` is minted (`:191`) and before any input is touched. `_not_found()` (`:136-140`) returns `JSONResponse(404, {"detail":"Not Found"})` with **no** `X-Correlation-ID` header. Route is `include_in_schema=False` (`:174`). Flag semantics (`config.py:56-68`) are byte-identical to `internal_rule_eval_enabled`: closed true-token set `{"1","true","yes","on"}` (`config.py:39`); absent/empty/unknown → False. Test `test_as1_flag_off_or_unknown_is_generic_404` parametrizes `[None,"","0","false","off","maybe","2","  "]` and asserts byte-equal `{"detail":"Not Found"}`, no `x-correlation-id`, and no `scenario`/`cap`/`flag` substring; `test_as1_openapi_never_lists_the_internal_route` confirms absence from OpenAPI even with the flag ON.

2. **Input surface — PASS.** Signature takes only `bbl: str` path param plus two `Depends()` server-side providers (`:175-181`); no request body, no query model. `build_scenario(..., assumptions=None)` (`:312-314`) — assumptions can never be caller-supplied. `test_as6_post_is_405_method_not_allowed` (POST+body → 405) and `test_as6_query_supplied_assumptions_are_ignored` (byte-identical body with a crafted `?assumptions=...`) prove it. No header is read anywhere in the handler. BBL flows through `normalize_bbl` (`connectors/bbl.py`), which forces a strict `^[1-5][0-9]{5}[0-9]{4}$` 10-digit canonical form before it ever reaches the injected fetcher — closing SoQL/SSRF/path-traversal injection at the trust boundary.

3. **Information leakage — PASS.** Every error path is typed and hand-built (`_json`, `_internal_error_500`, `_internal_contract_error_500`, `_not_found`). Logging is payload-only: only error type/location + `correlation_id` are logged, never `str(exc)`/traceback (`:199-201,221-223,238-240,278-280,300-302,320-322,334-336,346-348`). The flag-off 404 carries no correlation id (verified). `test_as5_internal_error_is_generic_500_no_internals` injects `RuntimeError("secret-internal-path C:\\hostile\r\n::injected")` and asserts `hostile`/`secret-internal-path`/`Traceback`/`File "` are all absent from the response; `test_as5_error_bodies_never_leak_token_or_stack` sets a `SOCRATA_APP_TOKEN` canary and asserts it never appears in 502/503/504 bodies. Consistent with the M1-T002 G5 F5 payload-only policy.

4. **FH-M5T001-S1/S2 — PASS.** `validate_scenario_document(document)` is called before every 200 (`:332`), inside a guard that maps failure to typed `internal_contract_error` 500 with no internals. The bounded-depth guard `_document_depth_ok` (`:110-125`) runs BEFORE contract validation (`:319`), is genuinely iterative (explicit `stack`, never recurses), and rejects any nested dict/list deeper than `_MAX_SCENARIO_DEPTH = 64` — walking the ENTIRE assembled document, so adversarial nesting in any embedded sub-object (citation.provenance / competing_rules / spatial_uncertainty.*) is caught. `test_as4_adversarially_deep_document_hits_bounded_depth_no_recursionerror` builds a 5000-deep document, forces it through `build_scenario`, and asserts typed 500 with no `RecursionError`/`Traceback`. 64 levels is comfortably below Python's ~1000 recursion ceiling for the downstream jsonschema/json.dumps recursion, and any recursion that could occur earlier (e.g., in `validate_rule_evaluation_document` on a server-produced document) is caught by the outer `except Exception` (`:345`, RecursionError ⊂ Exception) → typed 500, never a leaked crash.

5. **Frontend — PASS.** No `dangerouslySetInnerHTML`/`innerHTML`/`eval`/`__html` in any scenario component (grep clean). All server strings render as React-escaped text nodes. Error-path reflected text is length-capped + control-stripped via `boundedText` (600-char cap, C0/C1 strip) and the correlation id/state via `boundedToken` (`[A-Za-z0-9._-]`, 64/48 cap) in `lib/scenario.ts:302,327,354,367,378,386,397`; the 200 body is runtime-contract-validated (`validateScenarioDocument`, `scenario-contract.ts:292`) before render, and `verified` is structurally rejected (absent from `SCENARIO_COVERAGE_STATUSES`). `urlHost()` renders only `new URL(url).host` as text (no `href` sink). The `INTERNAL_SCENARIO_UI` flag is **non-public**: not `NEXT_PUBLIC_*`, read only via a dynamic `process.env[INTERNAL_SCENARIO_UI_ENV_VAR]` access in `scenarioFlagEnabled`/`scenarioSurfaceEnabled`, which are imported ONLY by `app/property/page.tsx` (a Server Component — no `"use client"`, async) and never by any client component (grep confirmed). `page.tsx` passes a plain boolean prop into the client tree. Flag-off = no render AND no fetch: the panel is `{scenarioEnabled ? <ScenarioPanel .../> : null}` and `e2e/scenario-flag-off.spec.ts` records every request URL and asserts zero `/scenario` calls for both no-opt-in and `?scenario=off`.

6. **Supply chain / policy — PASS.** ZERO new dependencies: no `package.json`, `package-lock`, `pnpm-lock`, `yarn.lock`, `requirements.txt`, `poetry`, or `Pipfile` in the diff (the lone `requirements.json` hit is the D-021 directive requirements record, not a Python manifest). No `.github/`/workflow/pre-commit/gitleaks/branch-protection/CodeQL/dependabot changes. No secrets in code/fixtures — the only secret-shaped strings are a fake canary (`secretscan:allow`) and an injected hostile string inside the leak-ABSENCE test. Harness/playwright changes are additive test-only (`INTERNAL_SCENARIO_ENABLED=1` in `fixture_api.build_app`, `INTERNAL_SCENARIO_UI:"1"` in the webServer env), parallel to the existing rule-eval flags; existing routes are behavior-unchanged.

7. **D-021 holds — PASS.** Diff contains nothing under `tools/agent_supervisor/**`, controller/model-selection config, the context pipeline, or the MCP policy (grep NONE). No `.claude/settings.json` edit.

Cross-tenant isolation / service-role secrecy / private storage are N/A for this change: the endpoint performs no Supabase/storage/DB access, uses no service-role credential, and there is no tenant model yet (auth blocked M0-T007/T008). The relevant posture — no new authenticated/exposed surface — is satisfied because the route is OFF by default (generic 404 in production) and `include_in_schema=False`, matching the accepted M4-T005 internal-endpoint precedent. Least privilege holds (server-side injected fetcher/substrate default to None; no elevated access).

## Steps / commands independently executed

```
$ git -C <wt> diff --stat main...HEAD                → 31 files, +4968/-4
$ git -C <wt> diff --name-only main...HEAD | grep -iE 'package.json|lock|requirements|.github/|workflow|pre-commit|gitleaks|branch|codeql|dependabot'
    → only project-control/directives/.../requirements.json (directive record; false positive)
$ git -C <wt> diff --name-only main...HEAD | grep -iE 'agent_supervisor|controller|model.?selection|context.?pipeline|mcp|.claude/settings'
    → NONE (clean)
$ git -C <wt> diff --name-only main...HEAD | grep -iE 'app/scenario/|app/profile/|app/spatial/|app/rules/|packages/contracts/'
    → NONE (read-only honored)
$ grep -rn dangerouslySetInnerHTML|innerHTML|eval\(|__html apps/web/src/components/scenario
    → No matches found
$ grep -rn 'scenarioSurfaceEnabled|scenarioFlagEnabled' apps/web/src (excl. lib/scenario.ts, __tests__)
    → only app/property/page.tsx (Server Component)
$ cd services/api && python -m pytest tests/api -q
    → 144 passed in 4.56s
```

Last lines of the authoritative run:
```
........................................................................ [ 50%]
........................................................................ [100%]
144 passed in 4.56s
```
This reproduces the orchestrator-captured integration evidence (tests/api 144 passed at 31e652a).

## Evidence paths

- `services/api/app/api/v1/scenario.py` (endpoint; flag-first gate, depth guard, validate-before-emit, typed error map, payload-only logging)
- `services/api/app/config.py:56-68` (fail-safe flag helper)
- `services/api/tests/api/test_scenario_api.py` (flag-off matrix, AS-4 depth/RecursionError, AS-5 leak-absence, AS-6 injection)
- `apps/web/src/lib/scenario.ts`, `apps/web/src/lib/scenario-contract.ts`, `apps/web/src/lib/bounded.ts`
- `apps/web/src/components/scenario/{ScenarioPanel,ScenarioResult,ScenarioFailure}.tsx`
- `apps/web/src/app/property/page.tsx` (non-public flag read server-side), `apps/web/e2e/scenario-flag-off.spec.ts` (no-fetch proof)

## Human-style walkthrough findings

Web unit/component/e2e suites were not executed here (thin-client; no npm/node per policy). Their design was inspected and mirrors the accepted rule-eval patterns; CI is authoritative for their execution (see residual risks).

## Regression/security/provenance findings

No critical/high/medium security findings. Two informational/low residuals (non-blocking, consistent with accepted M4-T005 precedent):

- **L1 (informational).** For the 200-document path, the individual scenario fields rendered in `ScenarioResult.tsx` (e.g. `citation.quote`, `citation.section`, `not_verified_disclaimer`, `evaluated_input.*`, coverage-matrix rows) are not per-field length-bounded/control-stripped on the client; XSS is prevented by React auto-escaping and content is shape-validated by `validateScenarioDocument` + the server-side `validate_scenario_document`. A hostile-length server string on the 200 path is bounded only by the backend contract, not the frontend. Same posture as the accepted rule-eval result surface; no security impact.
- **L2 (informational).** `scenario-contract.ts` validates some nested shapes shallowly (`checkConstraint` accepts any `provenance` object incl. arrays; `cap_provenance.citations` only checks `Array.isArray`, not element shape). Consumers use `typeof` guards + React escaping, so no injection/XSS results; matches rule-eval contract depth.

## Defects

None blocking.

## Required rework

None.

## Reviewer conclusion

**PASS.** The internal scenario endpoint is fail-safe OFF by default (flag checked first, no correlation id, `include_in_schema=False`, generic 404 indistinguishable from unmounted), accepts only a strictly-normalized `bbl` path param (no body/query/header influence), fully types every error with payload-only logging (no traceback/secret/path/str(exc) leakage — proven by adversarial leak tests), and closes FH-M5T001-S1/S2 with a validate-before-emit plus a genuinely iterative bounded-depth guard (RecursionError-proof, proven by a 5000-deep adversarial test). The frontend has no XSS sink, bounds/allowlists all reflected error text, runtime-validates the 200 body and rejects `verified`, and gates the surface behind a non-public server-read flag whose off state yields no render and no fetch. Zero new dependencies, no CI/security-control/branch-protection changes, no secrets, and every D-021 hold (supervisor/controller/model-selection/context-pipeline/MCP/settings/read-only backend modules) is honored. The change strengthens the accepted M4-T005 posture (it adds a depth guard the rule-eval route lacks) and introduces no exposed surface.

Residual / could-not-verify: web vitest/Playwright suites were not executed in this read-only sandbox (thin-client policy) — CI is authoritative for their green status; their designs were inspected and match accepted precedent. The full D-021 requirement-by-requirement PASS is owned by the independent directive-compliance-verifier's `verification.json`; this report verifies only the security-bearing D-021 holds.
