# G4 Gate Report — M5-T026 (test adequacy)

> Saved VERBATIM by the orchestrator from the qa-engineer agent return (2026-09-14;
> transport entity-decoding only, per the report-preservation rule). Reviewer ≠ producer.

- Gate ID: G4 (test adequacy)
- Task ID: M5-T026 — additive `INTERNAL_RULE_EVAL_DEFAULT_ON` gate mode (D-057)
- Reviewer: qa-engineer (independent; not the producer)
- Producer: frontend-engineer (material commit `0b112357`)
- Result: **PASS**
- Clean environment/worktree used: isolated reviewer worktree (HEAD `d8b3899f`, a control-plane descendant). Primary-checkout git was refused by the worktree-isolation guard, so ALL reviewed content was read via `git show <pinned-sha>:<path>` object reads (identity-equivalent to the pinned checkout). Pinned commits `1087aff6` and `0b112357` both present in the object store.

## Content-identity verification (performed first)

| Artifact | `0b112357` | `1087aff6` (pin) | `2e2f7a1f` (CI head) |
|---|---|---|---|
| `apps/web/src/lib/rule-evaluation.ts` | blob `83545169…` | blob `83545169…` | blob `83545169…` |
| `apps/web/src/lib/__tests__/rule-evaluation.test.ts` | blob `ffe96284…` | blob `ffe96284…` | blob `ffe96284…` |

Byte-stable across all three SHAs. Topology: `0b112357` is an ancestor of CI head `2e2f7a1f`; the pin `1087aff6` is 3 control-plane commits after the CI head (M5-T025 accept + submit records) with no material-file change. The CI run therefore executed exactly the reviewed bytes.

## Acceptance criteria reviewed

S1 (gate_matrix_complete) and S2 (additive_zero_regression) in full; S4 only for its "CI green" executable-authority clause (confirmed read-only). S3 (docs_honest) and the remainder of S4 (scope/NEXT_PUBLIC/deps) are the G3/code-review surface, not this G4.

## Directive/requirement verification

| Requirement ID | Reviewed SHA / content identity | Verdict | Reproduced evidence |
|---|---|---|---|
| D-057-R001 | blob `ffe96284` (test) + `83545169` (impl) at `1087aff6`/`0b112357`/`2e2f7a1f` | PASS | Decision table independently re-derived from `rule-evaluation.ts:131-138`; every row class covered (matrix table below); required harness "unit-test matrix over (main flag × default-on var × param states); fail-safe rows explicit" satisfied — 30 explicit kill-switch rows, all crossed against the var incl. true tokens |
| D-057-R002 | same identity; pre-change semantics from `git show 0b112357^:apps/web/src/lib/rule-evaluation.ts` | PASS | Pre-change function re-derived (below); dedicated equivalence block test.ts:255-302 reproduces pre-change outputs for every param class with the var explicitly absent; test-file diff `0b112357^..0b112357` = **200 insertions, 0 deletions** (only `-` line is the diff header) — every pre-existing describe/assertion byte-unmodified; module-scope hooks test.ts:41-51 force var-absent around every test |
| D-057-R003, D-046-R001/R002 | — | NOT IN THIS GATE'S SURFACE | Doc/process requirements; assigned to G3 / code-review / DCV per the dispatch. No adverse observation made incidentally. |

## Steps independently executed (read-only)

1. `git rev-parse <sha>:<path>` blob comparison across `0b112357`, `1087aff6`, `2e2f7a1f` (table above).
2. `git show 1087aff6:project-control/tasks/M5-T026.json` and `…/D-057-ruleeval-default-on/requirements.json` — S1–S4 and R001/R002 read from source.
3. `git show 1087aff6:apps/web/src/lib/rule-evaluation.ts` — decision table derived myself (below).
4. `git show 0b112357^:apps/web/src/lib/rule-evaluation.ts` — pre-D-057 semantics derived myself.
5. `git show 1087aff6:apps/web/src/lib/__tests__/rule-evaluation.test.ts` — full 492-line read; every case hand-counted.
6. `git diff --numstat 0b112357^ 0b112357 -- <test file>` → `200 0`; grep for `^-` lines → only the header.
7. `gh run view 34814460843 --json headSha,conclusion` → `success`, headSha `2e2f7a1fd126…`, branch `candidate/D-024-mrl-option-b`; all 18 jobs green incl. `web-e2e` (3m7s).
8. `gh run view --job 103882141057 --log` (web-e2e) → vitest line: `✓ src/lib/__tests__/rule-evaluation.test.ts (111 tests) 53ms`; suite totals `32 files / 576 tests passed`; Playwright `83 passed`.

**Inspected vs taken from CI:** all source/test/packet/directive content inspected directly at pinned identity via git plumbing. Test *execution* evidence taken from CI run 34814460843 only (thin client — no node_modules, no local vitest; per dispatch, CI is the executable authority). No writes, no state changes, no project_control verbs.

## My independently derived decision table (from `rule-evaluation.ts:131-138`)

```
A  !flagEnabled                                   -> false   (short-circuit; param & var never read)
B  flag on, raw === undefined                     -> defaultOnEnabled()   [B1 var true-token -> true; B2 var absent/""/garbage -> false]
C  flag on, param present, (array-first) true tok -> true    (regardless of var)
D  flag on, param present, not a true token       -> false   (kill switch; regardless of var; [] lands here: raw[0]=undefined)
Token rule (both vars, :106-118): typeof string && TRUE_TOKENS.has(trim().toLowerCase()); TRUE_TOKENS={1,true,yes,on} (:89)
```

### Matrix-coverage audit (test.ts evidence)

| Row class | Covered by | Verdict |
|---|---|---|
| A: flag {unset,"0","banana"} × var=**"1"** × param absent | test.ts:223-232 (3 rows) | PASS |
| A: flag {unset,"0"} × var="1" × param "on" / "off" | test.ts:234-242, 244-252 (4 rows) | PASS |
| A: flag off × var absent × param {none, "on", "off"} | test.ts:87-91 (var absent via module hook :41-44), :270-275 | PASS |
| B1: flag on, param absent, var {"1","true"} → **true** | matrix :170-206 ("absent" × those var rows) | PASS |
| B2: flag on, param absent, var {unset,"garbage",""} → false | matrix "absent" × those var rows; also :277-281 | PASS |
| C: param "on", "ON " (case+trailing space), ["on","off"] → true × ALL 5 var states | matrix (15 rows) — proves opt-in var-independent | PASS |
| D kill switch: "off","0","","banana",["off"],[] → false × ALL 5 var states incl. "1"/"true" | matrix (30 explicit rows) — kill switch holds regardless of the new var | PASS |
| New-var token classification: "1","true","on","YES" → true; "0","off","","maybe",absent → false | test.ts:135-151 (9 cases, literal expected) | PASS |
| New var read from `process.env` (not just via explicit arg) | matrix sets `process.env[INTERNAL_RULE_EVAL_DEFAULT_ON_ENV_VAR]` :202-203 and B1 rows return true — env binding proven | PASS |

No missing row class. S1's enumerated tokens ("off","0","banana",empty,array forms; var absent/empty/garbage; whitespace/case) all present — whitespace+case at surface level via param `"ON "`; var case via `"YES"` (whitespace gap noted as NB-1).

## S2 / D-057-R002 equivalence proof (my derivation)

Pre-change (`0b112357^`): `if (!flag) return false; value = Array.isArray(raw) ? raw[0] : raw; return typeof value === "string" && TRUE_TOKENS.has(…)` — param-absent falls through to `typeof undefined === "string"` → **false always**. Post-change differs ONLY at `raw === undefined` → `ruleEvaluationDefaultOnEnabled()`, which is false whenever the var is unset. Hence var-unset ⇒ byte-identical behavior on every input.

The dedicated block (test.ts:255-302) asserts exactly my hand-derived pre-change outputs for every param class (flag-off×3; flag-on absent — labeled "the exact pre-D-057 default", both no-arg and explicit-undefined call shapes; "off"; "on"+["on"]; "0"/""/"banana"/["off"]/[]) with the var deleted (:263 plus module hook). Module-scope `beforeEach` (:41-44) saves-then-**deletes** the var before EVERY test in the file and `afterEach` (:45-51) restores it (correct undefined→delete handling), and vitest runs file-level beforeEach before suite-level ones / file-level afterEach last — so all 40 pre-existing tests are guaranteed var-absent even if CI env carried the var. Pre-existing blocks byte-unmodified (200/0 diff).

## Tautology check

No assertion derives its expected value by calling the code under test. Token blocks and the R002/flag-off blocks use literal expecteds. The 50-row matrix composes expecteds from two hand-literal tables (`PARAM_ROWS` outcome column, `DEFAULT_ON_ROWS` isTrueToken column) via `depends ? dIsTrue : pOutcome` (:191-197) — this mirrors the *spec's* precedence (hand-derived from D-057-R001), not the implementation, and each generated expected is a concrete literal at run time; a broken kill switch, ignored var, or inverted precedence would each fail concrete rows. The non-generated R002 and flag-off blocks additionally anchor the precedence with fully literal rows. Not tautological.

## Isolation / hygiene / order-independence

- Every env mutation is paired: module-scope var hook (:41-51); per-describe MAIN-flag save/restore (:79-85, :156-163, :211-217, :261-268); retired-name test try/finally (:110-121). Tests that set the var in their bodies (:202-203, :230/240/250) are cleaned by the module afterEach. No `it.concurrent`; sequential execution makes the shared `savedDefaultOnAtModuleScope` safe.
- Every test establishes its full precondition in its own hook chain/body; token-classification blocks use explicit arguments; no test consumes another's residue. Order-independent.

## Producer-claim count audit

| Claim | My count | Evidence | Verdict |
|---|---|---|---|
| 9 new token cases | 8 `it.each` + 1 `it` = 9 | test.ts:135-152 | MATCH |
| 50 matrix cases | 10 param rows × 5 var rows = 50 | :170-206 | MATCH |
| 7 flag-OFF cases | 3+2+2 = 7 | :209-253 | MATCH |
| 5 R002 cases | 5 `it` | :255-302 | MATCH |
| 71 new total / 4 new describes | 71 / 4 (+module hooks, disclosed) | — | MATCH |
| File total consistency | 40 pre-existing (9+4+2+14+5+5+1) + 71 = **111** | CI log: `rule-evaluation.test.ts (111 tests)` all pass | MATCH (exact) |

## Defects

**Blocking: none.**

Non-blocking:
- **NB-1** — New-var whitespace token untested: `ruleEvaluationDefaultOnEnabled(" TRUE ")`-style row absent (case covered via `"YES"` test.ts:139; whitespace `trim()` proven only for the param path via `"ON "` :173). The two functions are textually identical one-liners (impl :106-118) and the new block exactly mirrors the pre-existing flag block, so risk is minimal. Suggested future addition, no rework required.
- **NB-2** — The matrix's only param-absent TRUE rows use `{ ruleeval: undefined }` (:171, :204); the no-arg/property-missing call shapes are asserted only on false paths (:231, :272, :279). Language-equivalent under `params?.ruleeval` today; a future refactor to `"ruleeval" in params` would dodge the true-path matrix. Hardening suggestion only.
- **NB-3** — Producer report prose "All four pre-existing describe blocks" (report §R002): there are 7 pre-existing describes. The parenthetical "plus everything below" and the 0-deletion diff make the material claim true; prose miscount only.
- **NB-4** — Trivial comment drift in the test file: safety-net comment says "pre-D-057 tests **above**" (:37) though they sit below the hook; file-header docstring (:26) still says "two-factor frontend flag" (header was not a packet deliverable). Cosmetic.

## Required rework

None.

## Reviewer conclusion

**PASS.** The unit matrix is complete against my independently derived decision table (every S1 row class explicit, all 30 kill-switch rows held against the new var including true tokens); the R002 zero-behavior-change proof is genuine (pre-change semantics re-derived from `0b112357^`, dedicated equivalence block matches them exactly, module-scope hooks guarantee var-absence for all 40 unmodified pre-existing tests, diff is 200/0 purely additive); no tautological assertions; isolation is correct and order-independent; the producer's 71/9+50+7+5/4-describe claim is exact and reconciles to the CI-executed 111-test file count in green run 34814460843 at `2e2f7a1f`, which ran byte-identical content to the pin `1087aff6`.
