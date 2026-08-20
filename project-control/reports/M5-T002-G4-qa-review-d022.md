# G4 QA/Integration Gate Report — M5-T002 (D-022 correction re-review)

> Saved VERBATIM by the orchestrator from the qa-engineer agent-return channel
> (transport entity-decoding only). Reviewer ≠ producer. Supersedes the invalidated
> M5-T002-G4-qa-review.md conclusions (prior identity 2fee786/31e652a, D-022-R016).
> Orchestrator note: a harness sanitizer flagged this reviewer's own agent-memory note
> for guard-bypass framing; the orchestrator neutralized that framing in the reviewer's
> untracked memory file (never committed). The flag concerned the memory write only —
> not this report's evidence, which was independently spot-checked.

**Task:** M5-T002 — Scenario endpoint + property-screen scenario surface (internal, flag-gated; D-021 ALL) — re-review after owner directive D-022 correction
**Reviewer:** qa-engineer (independent; NOT the producer) — READ-ONLY
**Frozen corrected identity:** commit `69558cd` / tree `ee6dce0f29416e6637dd46382872a88a25578ce1` (matches the claimed tree exactly)
**PR #241 head:** `7f9231e` — OPEN / MERGEABLE (correctly UNMERGED)
**Prior G4 PASS at 2fee786/31e652a is INVALIDATED (D-022-R016); this verdict stands alone.**

## 1. VERDICT: **PASS**

No blocking corrections. Two non-blocking findings (§3). Every one of the owner's 8 reproduced bypasses is now rejected by a test with real teeth; the 3 fetchScenario proofs genuinely execute the real client + real validator; all 4 valid fixtures pass and all 3 invalid fail (embedded explicit); the correction is strictly additive to existing tests; backend is untouched (144 pytest pass, modularity 0 failures); and all 20 CI contexts are green at HEAD `7f9231e` with the web-e2e vitest+Playwright suites executing the new tests (370 vitest pass, 80 Playwright pass).

## 2. Identity & scope verification (item 6)

- `git rev-parse 69558cd^{tree}` → `ee6dce0f…` — matches the frozen tree.
- `git diff --name-only 69558cd 7f9231e` → **only** `project-control/reports/M5-T002-evidence-map.json`, `M5-T002.json`, `state.json`, `tasks/M5-T002.json` — HEAD differs from frozen ONLY in `project-control/**`. ✓
- `git diff --name-only 2d9eb74 69558cd` → exactly **4 files**: `apps/web/src/lib/scenario-contract.ts` (impl), `.../scenario-contract.test.ts`, `.../scenario.test.ts` (both tests), `project-control/reports/M5-T002-producer-report.md`. No backend/scenario/rules/profile/contracts/deps/flags/agent/supervisor/MCP file touched (owner CORRECTION #9 satisfied). `test_scenario_api.py`, `scenario.test.tsx`, `scenario.spec.ts`, `scenario-flag-off.spec.ts`, `scenario.ts` are **unchanged** → original AS-1..AS-10 coverage undisturbed. ✓

## 3. Bypass → test matrix with teeth judgment (item 1)

For each: I confirmed the test starts from `mutable()` = `structuredClone(preliminaryFixture)` (a structurally valid doc), injects exactly ONE defect, and `expectRejectedAt` asserts `ok:false` AND a problem whose path **names the defective field** (`startsWith("<path>:")` or `"<path>["`). Thought-experiment against the OLD validator (`2d9eb74`) confirms each would return `ok:true` there — so every test **fails if the fix is reverted**.

| # | Bypass | New rejecting check | Test (file::name) | Teeth vs OLD validator |
|---|--------|---------------------|-------------------|------------------------|
| 1 | cap = -1 | `isFiniteNumber && > 0` (line 522-533) | contract::"bypass 1 … = -1" | OLD accepted any `number` → `ok:true`; test asserts `ok:false` + names `draft_zoning_floor_area_cap_sq_ft`. **Real teeth** |
| 2 | cap = 0 | same `> 0` gate | contract::"bypass 2 … = 0" | OLD accepted `0` → `ok:true`. **Real teeth** |
| 3 | bbl = "x" | `BBL_PATTERN /^[1-5][0-9]{5}[0-9]{4}$/` (line 292) | contract::"bypass 3 … bbl = 'x'" | OLD only `isNonEmptyString` → `"x"` passed. **Real teeth** |
| 4 | rule_status="verified" | `checkEnum` vs `CAP_PROVENANCE_RULE_STATUSES` (line 418) | contract::"bypass 4 … 'verified'" | OLD only `typeof==="string"` → passed. **Real teeth** |
| 5 | citations=[null] | per-item `checkCitation`→`isRecord` (line 422-424) | contract::"bypass 5 … [null]" | OLD only `Array.isArray` → `[null]` passed. **Real teeth**; names `cap_provenance.citations[0]` |
| 6 | assumptions=[null] | per-item `checkAssumption`→`isRecord` (line 542) | contract::"bypass 6 … [null]" | OLD only `Array.isArray` → passed. **Real teeth**; names `assumptions[0]` |
| 7 | unexpected top-level key | root `checkKnownAndRequiredKeys` additionalProperties:false (line 490) | contract::"bypass 7 …" | OLD had NO root key check → passed. **Real teeth** |
| 8 | embedded_property_profile.json | root additionalProperties:false catches `property_profile` | contract::"bypass 8 …" | OLD passed the whole fixture; NEW names `property_profile`. **Real teeth** (fixture confirmed to carry a top-level undocumented `property_profile` key) |
| + | +Infinity / NaN cap; `constraints[0].provenance=[]` | `isFiniteNumber`; `isRecord` (not `typeof==="object"`) | contract::"also rejects a +Infinity/NaN cap and a provenance ARRAY" | OLD: numbers/`typeof [] ==="object"` passed. **Real teeth** |

**Faithful-enforcement cross-check (owner CORRECTION #2):** I diffed the validator's hand-written key sets/enums/patterns against the canonical `scenario.schema.json` + `common.schema.json`. All match EXACTLY: root `additionalProperties:false` + the same 16 required keys + `_expected_failure` as the only optional; cap `exclusiveMinimum 0`/null; `evaluated_input`/`cap_provenance`/`citation`/`constraint`/`assumption`/`coverage_matrix` row/`integrity_check` required-key sets and `additionalProperties:false`; `rule_status` enum `[discovered,extracted_draft,needs_review,published]`; `rule_status_today` enum `[draft,missing,out_of_scope]`; BBL `^[1-5][0-9]{5}[0-9]{4}$`; digest `^sha256:[0-9a-f]{64}$`. This is genuine schema enforcement, not sampling.

## 3b. fetchScenario proofs (item 2)

`scenario.test.ts` imports the REAL `fetchScenario` and REAL `validateScenarioDocument` (no `vi.mock` of the validator anywhere). At HTTP 200, `fetchScenario` (scenario.ts:332-343) calls the real validator and returns `kind:"validation_failure"` on failure, else `kind:"scenario"`. HTTP is mocked via the suite's existing `stub(jsonResponse(...))` convention. Three added tests:
- negative cap (-1) → asserts `kind==="validation_failure"` + problem `draft_zoning_floor_area_cap_sq_ft` (never `"scenario"`);
- null citation `[null]` → `validation_failure` + `cap_provenance.citations[0]`;
- embedded_property_profile.json body → `validation_failure` + `property_profile`.
The embedded fixture has **no top-level `state` key**, so the (200, null) documented pair holds and the body genuinely reaches the validator (not short-circuited as `unexpected_response`). All three would classify as `kind:"scenario"` under the OLD validator. **Genuine, real-path teeth.**

## 3c. Fixture sweeps (item 3)

Directory listing confirmed: 4 valid (`preliminary_r5_cap`, `no_scenario_conflict`, `no_scenario_professional_review`, `unsupported_family`), 3 invalid (`coverage_status_verified`, `embedded_property_profile`, `missing_scenario_kind`). The sweep statically imports all 7, asserts every valid `ok:true` and every invalid `ok:false`, and asserts `embedded_property_profile.json` present AND rejected with a `property_profile:` problem — explicitly (twice: dedicated test + bypass 8 + fetchScenario). The `_expected_failure` annotation is an allowed optional key, so each invalid fixture fails for the RIGHT reason (property_profile / verified / missing scenario_kind), not incidentally.

## 4. Findings (all non-blocking)

**F1 — Minor — count-guard is a tripwire, not a directory diff.** The sweep asserts `validFixtures.length===4` / `invalidFixtures.length===3` against hardcoded literals, not against a live directory read. A NEW fixture dropped into `fixtures/{valid,invalid}/scenario/` but not added to the array would be silently unswept (length still 4/3). The producer/comment claim that the counts "must equal the directory listings" overstates enforcement: it loudly catches an array/import edit-desync, but not a directory-only addition. At the frozen identity the arrays DO equal the actual listings (verified: 4 and 3), so the owner requirement is met now; this is a future-maintenance gap. The static-import choice (over `import.meta.glob`) was a deliberate, justified tradeoff to keep `tsc --noEmit` green. No behavior defect.

**F2 — Informational — vitest CI reporter is file-level.** The web-e2e log names test FILES with counts, not individual describe/test names, so I could not literally quote a "bypass 1 …" line. Execution is instead proven by the exact per-file counts (`scenario-contract.test.ts (25 tests) ✓` = 7 original + 9 adversarial + 9 sweep; `scenario.test.ts (42 tests) ✓` = 39 original + 3 new fetchScenario) and the run-level `Tests 370 passed (370)`, combined with my line-by-line read of the frozen source. Not a defect.

## 5. Commands run + last lines

```
$ git rev-parse 69558cd^{tree}                          → ee6dce0f29416e6637dd46382872a88a25578ce1  (matches frozen tree)
$ git diff --name-only 69558cd 7f9231e                  → project-control/** ONLY (4 files)
$ git diff --name-only 2d9eb74 69558cd                  → 4 files (scenario-contract.ts + 2 tests + producer report)
$ git diff 2d9eb74 69558cd -- <both test files>         → strictly additive; no existing assertion weakened/deleted (only docstring reflow)
$ cd wt-m0t064/services/api && python -m pytest tests/api -q     → 144 passed in 3.93s   (zero backend impact)
$ cd wt-m0t064 && python tools/modularity_check.py --check       → selected 271 files; failures 0; warnings 5 (all pre-existing; scenario-contract.ts not flagged)
$ python inspect_schema.py (canonical schema cross-check)         → all nested required-key sets, enums, and patterns match the validator EXACTLY

$ gh pr view 241 --json headRefOid,state,mergeable
  {"headRefOid":"7f9231edbd04aaf33e68b986dd643af4aa2ff916","state":"OPEN","mergeable":"MERGEABLE"}
$ gh run view 32338679546 --json headSha,event,conclusion  → {headSha:7f9231e…, event:push,         conclusion:success}
$ gh run view 32338682833 --json headSha,event,conclusion  → {headSha:7f9231e…, event:pull_request, conclusion:success}
$ gh pr checks 241   → all 20 distinct contexts pass at HEAD 7f9231e (both the push and pull_request runs)
```

**CI web-e2e job log (run 32338679546, job 96333164863, HEAD 7f9231e) — quoted lines (item 5):**
```
✓ src/lib/__tests__/scenario.test.ts (42 tests) 29ms
✓ src/lib/__tests__/scenario-contract.test.ts (25 tests) 16ms
✓ src/components/scenario/__tests__/scenario.test.tsx (16 tests) 1371ms
 Test Files  25 passed (25)
      Tests  370 passed (370)
Playwright human journeys:
 ✓ 64 e2e/scenario-flag-off.spec.ts:26 › no opt-in: surface absent, browser never calls the endpoint (1.0s)
 ✓ 65 e2e/scenario-flag-off.spec.ts:41 › explicit ?scenario=off: kill switch keeps surface off (1.0s)
 ✓ 66 e2e/scenario.spec.ts:31 › AS-8: preliminary journey — draft cap shown VERBATIM, never Verified (780ms)
 ✓ 67 e2e/scenario.spec.ts:62 › AS-9: professional-review journey — honest no_scenario (589ms)
 ✓ 68 e2e/scenario.spec.ts:74 › AS-9 recoverable failure: profile usable and retries (744ms)
 ✓ 69 e2e/scenario.spec.ts:97 › a11y: announces politely, NEVER steals focus (546ms)
   80 passed (1.4m)
```
The `scenario-contract.test.ts (25 tests)` and `scenario.test.ts (42 tests)` counts exactly account for the 9 adversarial + 9 sweep + 3 fetchScenario tests; zero failures across all 370 unit tests and 80 Playwright journeys. Log retrieval SUCCEEDED (no orchestrator capture needed).

## 6. What I could NOT verify (and how resolved)

- **Individual vitest test-name lines in CI** — the reporter is file-level (F2). Resolved by exact per-file counts + run summary + my source read + OLD-validator thought-experiment.
- **Local vitest/tsc/lint/build/Playwright execution** — thin-client policy forbids npm/node/npx/playwright. Resolved by the clean-checkout CI run at HEAD `7f9231e` (web + web-e2e both green), which is authoritative for the web tests.
- **`python -m pytest tests` (whole services/api)** — not run; pre-existing PEP 695 collection errors under `tests/documents/**` on sandbox Python 3.11 (repo needs 3.12), unrelated to this task; `tests/api` (the relevant suite) runs and is 144 green; CI runs 3.12 and is green.

**Note for the orchestrator:** CI is fully green at the frozen HEAD (`7f9231e`), all owner D-022 CORRECTION items #1–#10 and the VERIFICATION freeze/reproduce/keep-unmerged requirements are satisfied, and no evidence is outstanding. Record **G4 = PASS**. Keep PR #241 UNMERGED per the owner directive; the two F-findings are non-blocking record items. This report is verbatim reviewer content; the reviewer did not run `project_control.py`, git-write, or `gh`-write.

---

Relevant absolute paths:
- Frozen validator: `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t064/apps/web/src/lib/scenario-contract.ts`
- Frozen tests: `.../apps/web/src/lib/__tests__/scenario-contract.test.ts`, `.../scenario.test.ts`
- Client under test: `.../apps/web/src/lib/scenario.ts`
- Fixtures: `.../packages/contracts/fixtures/{valid,invalid}/scenario/`
- Canonical schema: `.../packages/contracts/schemas/v1/scenario.schema.json` + `common.schema.json`
- Producer report: `.../project-control/reports/M5-T002-producer-report.md`
- Owner finding: `.../project-control/directives/D-022-scenario-contract-validator-correction/source-001.md`
- CI web-e2e log (reviewer capture): scratchpad `web-e2e.log`
