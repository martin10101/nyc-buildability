# G3 Code Review Gate Report — M5-T002

> Saved VERBATIM by the orchestrator from the code-reviewer agent-return channel
> (transport entity-decoding only). Reviewer ≠ producer.

**Task:** M5-T002 — Scenario endpoint + property-screen scenario surface (internal, flag-gated; R5 pilot; D-021)
**Reviewed content identity:** `31e652a` (content commits `8872438` + `31e652a`; verified `31e652a..2fee786` touches only `project-control/**` — control-plane only)
**Reviewer:** code-reviewer (independent; NOT the producer)
**Branch:** task/M5-T002-scenario-endpoint · HEAD `2fee786`

## VERDICT: PASS

No blocking or major defects. Two minor comment-accuracy nits and three observations are recorded below; none block acceptance. The G3 code-review scope is satisfied. (Full-repository CI green for the web/typegen jobs and the independent D-021 directive-compliance verification remain the orchestrator's / directive-verifier's separate confirmations — see "Could not verify".)

---

## 1. Findings (numbered, with severity and file:line)

**F1 — observation — AS-3 endpoint-level no-scenario families proven by monkeypatch, not natural end-to-end.**
`services/api/tests/api/test_scenario_api.py:371-398` (`test_as3_no_scenario_families_pass_through_as_200`) overrides `build_scenario` with committed canonical fixtures to prove the endpoint passes unsupported/conflict/professional-review documents through as a 200 verbatim. The builder-only families (`:401-450`) call `build_scenario` directly, not through the route. This is because the fixed R5 endpoint path can naturally reach only `preliminary` and `professional_review` outcomes; the substitute-at-the-boundary approach mirrors the accepted M4-T005 pattern and is honestly documented in the module docstring (`:23-31`). The natural end-to-end paths ARE exercised (`test_as3_absent_substrate_is_200_professional_review:340`, `test_as3_split_lot_is_200_professional_review:358`). Adequate coverage; noted for transparency, not a defect.

**F2 — minor — stale comment describing wiring as out-of-scope after the allowed_paths amendment closed it.**
`apps/web/e2e/scenario.spec.ts:16-23` still reads "…both files are OUTSIDE this task's allowed_paths, so these journeys are gated on that out-of-scope wiring," and `apps/web/e2e/scenario-flag-off.spec.ts:12-14` references "the out-of-scope property-screen render wiring." After the pre-gate allowed_paths amendment, `PropertyLookup.tsx` / `playwright.config.ts` wiring is applied and these specs now render. The comments are inaccurate. No functional impact (the tests themselves are correct); comment-discipline nit.

**F3 — minor — producer report retains contradictory historical B1 narrative.**
`project-control/reports/M5-T002-producer-report.md:138-164` keeps a long "original blocker" narrative ("I did NOT edit either out-of-scope file…") after the same section (`:119-136`) declares B1 CLOSED and the wiring applied. Harmless but internally contradictory; report hygiene only (not code).

**F4 — observation — DRAFT banner copy is generic across all presentations.**
`apps/web/src/components/scenario/ScenarioResult.tsx:258-266` renders the DRAFT banner ("…Produced by an unreviewed draft rule pending qualified-human legal approval…") for every presentation including `unsupported` and `missing`, where no draft rule produced a value. The heading (`HEADINGS`, `:28-34`) and intro (`INTROS`, `:36-53`) correctly state the honest no-rule/no-value message for those states, so the net message is honest and no value is shown; the banner sentence is merely less precise for the no-rule cases. Observation only.

**F5 — observation — web test suite not executed in-sandbox.**
vitest/playwright/tsc/eslint were not run (thin-client; npm/node prohibited for this reviewer). Verified by source inspection; execution is CI-authoritative. Backend `tests/api` was independently reproduced (144 passed).

## 2. Positive verification (the load-bearing correctness checks)

- **Pattern fidelity to `rule_evaluation.py`:** `scenario.py` mirrors the accepted route stage-by-stage — flag-first generic 404 checked before any input (`:188-189`); `bbl` path param only; `assumptions=None` hardcoded (`:313`); substrate seam **imported** from `rule_evaluation.py` not duplicated (`:62-65`); error maps single-sourced from `properties.py` (`_ERROR_STATUS`/`_DEFAULT_ERROR_STATUS`, `:56-61`); `no_match` → 404 machine-state body; one generic-500 guard wrapping everything post-fetch (`:246-349`); payload-only logging (no `str(exc)`/traceback — grep confirms hits are docstrings only); `X-Correlation-ID` on every non-generic-404 response.
- **Canonical-value invariant:** surfaced cap is `build_scenario`'s output verbatim. Backend never recomputes/relabels; frontend `ScenarioResult.tsx:55-76` renders `draft_zoning_floor_area_cap_sq_ft` through `formatValue` (digit-grouping only — `apps/web/src/lib/format.ts:13-16`, no arithmetic) with the server `cap_label`. `classifyScenario` reads only backend discriminators. `assumptions=None` always. Read-only dirs (`app/scenario`, `app/profile`, `app/spatial`, `app/rules`, `packages/contracts`) are byte-unchanged — `git diff d8b3899..31e652a` on those paths is empty.
- **FH-M5T001-S1/S2:** `validate_scenario_document` called before every emit (`:332`); iterative explicit-stack `_document_depth_ok` (`:110-125`, limit 64) runs BEFORE contract validation (`:319`) so an adversarially deep document fails to a typed `internal_contract_error` 500, never a RecursionError; the guard cannot recurse. Tested at `test_as4_*` (invalid doc → typed 500; 5000-deep doc → typed 500, no RecursionError).
- **Frontend guarantee-for-guarantee mirror of `rule-evaluation.ts`:** identical (status,state) pair matrix consistent with the backend `_ERROR_STATUS` map; runtime contract validation before render (`scenario-contract.ts` validates against the real generated `packages/contracts/generated/scenario.ts` — every checked field exists in the contract, no guessed schema; `verified` rejected via enum exclusion); bounded/control-stripped reflected text; token-allowlisted correlation id; AbortController + timeout with `aborted`/`client_timeout`; `feature_unavailable` for the (404,null) pair. Components render honest typed states with never-`verified` framing and CoverageBadge-by-value (not color alone).
- **Flag posture:** `INTERNAL_SCENARIO_ENABLED` (backend) and `INTERNAL_SCENARIO_UI` (frontend) both fail-safe explicit-true-token, off by default; `INTERNAL_SCENARIO_UI` is confirmed non-public (not `NEXT_PUBLIC_`, server-read once per request — the orchestrator-approved deviation). Wiring in `PropertyLookup.tsx`/`page.tsx` is strictly additive (optional prop defaulting false; flag off → panel never mounted, no fetch — proven by the gating vitest and the flag-off e2e spec).
- **Modularity:** `python tools/modularity_check.py --check` → 0 failures; `scenario.py` (349 SLOC) and new TS files are not flagged; the 5 warnings are pre-existing untouched files.
- **D-021 holds (code-level):** no forbidden-path files touched (grep for `.github/`, `agent_supervisor`, `settings.local`, `mcp`, `model_selection`, `context_pipeline` → none); no existing test/CI/security control modified; harness/playwright changes additive; branch unmerged (main still `d8b3899`).

## 3. Exact commands run (last lines)

- `git -C … diff d8b3899..31e652a --name-only` / `--stat` → 28 files, `4785 insertions(+), 4 deletions(-)`; production changes confined to allowed paths.
- `git -C … log --oneline d8b3899..2fee786` → content = `8872438` + `31e652a`; `2fee786` = "control-plane batch".
- `git -C … diff 31e652a..2fee786 --name-only` → **only** `project-control/**` (confirms reviewed content identity).
- `git -C … diff d8b3899..31e652a --name-only -- services/api/app/scenario … packages/contracts` → **empty** (read-only dirs byte-unchanged).
- `cd services/api && python -m pytest tests/api -q` → **`144 passed in 16.30s`** (matches orchestrator-captured integration evidence: tests/api 144 at 31e652a).
- `python tools/modularity_check.py --check` → **`selected 271 files; failures 0; warnings 5`** (none in this task's files).
- `python -c "…preliminary_r5_cap.json…"` → `cap: 15000.0`, `cap_label: DRAFT maximum residential ZONING-FLOOR-AREA CAP under ZR 23-21…`, `scenario_kind: preliminary`, `coverage_status: conditional` (matches test/e2e assertions of `15,000` and the draft label).
- `grep -n "str(exc)|traceback|format_exc|repr(exc)" services/api/app/api/v1/scenario.py` → matches only in docstrings/comments (no leakage code path).

## 4. What I could NOT verify (and why)

- **Web test EXECUTION** (vitest unit/component, Playwright e2e, `tsc`, eslint): not runnable in this reviewer sandbox (npm/node prohibited by policy). Verified the tests by reading — they are fixture-backed (committed canonical M5-T001 scenario fixtures, confirmed to exist) and substantive (pair matrix incl. verified-rejection, envelope classification, two-factor flag, no-fetch gating, focus discipline, verbatim cap). **The orchestrator must confirm the web-e2e / contracts-typegen / vitest CI jobs are green** before acceptance (AS-10 "full repository CI green").
- **Playwright harness substrate routing for the exact e2e BBLs** (e.g. F04 `1000010101` → no substrate → professional_review): relies on existing harness infrastructure I could not execute; logic is consistent by inspection, CI-authoritative.
- **The D-021 per-requirement directive-compliance verdict** (applicable set R001, R005-R011, R019-R023, R025) is the independent `directive-compliance-verifier`'s pass recorded in `verification.json`, not this G3 code review. At the code level I confirmed no violation of the protected-path holds (R005-R008), no test/CI/security weakening (R011), unrelated files preserved, and the PR is unmerged (R022) — but the formal per-ID directive attestation must come from that separate verifier.

**Relevant absolute paths:**
- `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t064/services/api/app/api/v1/scenario.py`
- `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t064/services/api/app/config.py`
- `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t064/services/api/app/main.py`
- `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t064/services/api/tests/api/test_scenario_api.py`
- `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t064/apps/web/src/lib/scenario.ts`
- `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t064/apps/web/src/lib/scenario-contract.ts`
- `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t064/apps/web/src/components/scenario/{ScenarioPanel,ScenarioResult,ScenarioFailure}.tsx`
- `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t064/apps/web/src/components/property/PropertyLookup.tsx`
- `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t064/apps/web/src/app/property/page.tsx`
- `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t064/apps/web/e2e/scenario.spec.ts` · `scenario-flag-off.spec.ts` · `harness/fixture_api.py` · `playwright.config.ts`

**Recommended non-blocking follow-ups (not gate conditions):** correct the stale out-of-scope comments in the two e2e specs (F2) and, optionally, tighten the DRAFT banner copy for the no-rule presentations (F4).
