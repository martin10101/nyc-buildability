# G4 RE-REVIEW — INTEGRATION / REGRESSION EVIDENCE VERIFICATION — M5-T012

**Verdict: PASS** at `12fda82f` (no blocking conditions; one correction to my earlier report, recorded below; two pre-existing out-of-packet CI defects restated)

| Field | Value |
|---|---|
| Task | M5-T012 — expose the deterministic scenario optimization toolkit via the internal flag-gated scenario API |
| Reviewed SHA | `12fda82f3f237f2432efc99614c903496a8b2e02` (confirmed via `git rev-parse HEAD`) |
| Branch | `candidate/D-024-mrl-option-b` |
| Previous G4 | PASS at `aafc75fd` (`project-control/reports/M5-T012-G4.md`, left intact); that verdict stands on its own terms but is superseded by this one |
| Commit arc | `c83206c2` (G0 packet) → `edc43f4f` (producer output) → `aafc75fd` (rework 1: AS-7 deadlock) → `12fda82f` (rework 2: G5 BLOCKING-1 surrogate crash, G1 BLOCKING-1 nested fact keys, G1/G5 HIGH-1 unguarded engine call) |
| Gate | G4 — integration / regression evidence (independent) |
| Verifier | ci-evidence-verifier (read-only, independent) |
| Date | 2026-09-10 (UTC) |
| Environment | Windows 11, Python 3.11.9, pytest 8.4.2, ruff 0.13.0, rootdir `services/api` (configfile `pyproject.toml`) |

`aafc75fd` is confirmed an ancestor of `12fda82f` (`git merge-base --is-ancestor` → true), so this is a
true fast-forward rework of the tree I verified before, not a rebase onto different history.

## 0. Statement of independence

Unchanged from my first pass. I am not the producer of M5-T012; I wrote, edited, and advised on
nothing in this change, and I fixed nothing. Every figure below comes from a command I ran myself at
`12fda82f`, in the owner's worktree, after confirming HEAD. I ran both documented suites to completion
before opening the producer's report; the claim audit in section 9 is a post-hoc comparison, not a
source. My only write is this file (`M5-T012-G4.md` from the first pass is untouched). No
`tools/project_control.py`, no git write, no `gh` write, no `pip install`.

## 1. Claim-by-claim result

| # | Material claim | Result | Observed |
|---|---|---|---|
| 1 | `python -m pytest services/api/tests/api` terminates and is green, **312 passed** | **CONFIRMED** | 312 passed in 38.35s, exit 0 (re-run: 312 passed in 36.63s) |
| 2 | `python -m pytest services/api/tests/scenario` terminates and is green, **388 passed** unchanged | **CONFIRMED** | 388 passed in 4.09s, exit 0 (re-run: 388 in 4.05s) |
| 3 | +96 tests, all in this task's own file (75 → 171) | **CONFIRMED** | `test_scenario_analysis_api.py` collects **171**; 75 + 96 = 171; no other file's count moved |
| 4 | `python tools/modularity_check.py --check` exit 0 | **CONFIRMED** | `failures 0; warnings 16`, **exit 0** |
| 5 | A `warn review_signal` now names `scenario_analysis.py` (572 → 666 SLOC, crossed `WARN_SLOC = 600`) | **CONFIRMED — and it corrects my earlier report** | see section 4 |
| 6 | Whole arc confined to the four `allowed_paths` | **CONFIRMED** | `c83206c2..12fda82f`: 4 files, 2799 insertions, **0 deletions** |
| 7 | Nothing in `forbidden_paths` | **CONFIRMED** | all 17 probed paths: 0 changed files (section 5.1) |
| 8 | `services/api/app/main.py` byte-unchanged this round | **CONFIRMED** | blob OID identical at both SHAs (`071f7755…`); rework diff empty |
| 9 | The packet-commit `main.py` edit is still the same +8/-0 additive edit | **CONFIRMED** | `git diff --numstat c83206c2..12fda82f -- …/main.py` → `8  0` |
| 10 | `app/scenario/**` and `app/config.py` byte-unchanged | **CONFIRMED** | empty diffs across the whole arc |
| 11 | OpenAPI document still byte-identical with the flag off and on | **CONFIRMED** | identical SHA-256 across flag absent / empty / `yes` / `true` (section 5.3) |
| 12 | Zero pre-existing test regressed | **CONFIRMED** | 141 baseline passes; 141 + 171 = 312; six pre-existing files keep 4/41/34/3/32/27 |
| 13 | The three files this task owns are still ruff-clean | **CONFIRMED** | All checks passed |
| 14 | `ruff check .` from `services/api` still fails on pre-existing files only | **CONFIRMED** | 27 errors, same 9 already-accepted M5 files, none owned by M5-T012 |
| 15 | 15 `tests/documents` collection errors remain the PEP 695 / 3.11 gap | **CONFIRMED** | same 15 errors, `units.py:276`; neither packet suite imports `app.documents` |
| 16 | A green CI run exists for this SHA | **NOT APPLICABLE / NOT CITABLE** | zero GitHub Actions runs for `12fda82f`; branch local-only by owner hold (section 7) |
| 17 | The rework introduced no new (HTTP status, state) pair | **CONFIRMED** (regression-relevant) | `STATUS_STATE_MATRIX` byte-identical to `aafc75fd` (section 6) |

## 2. Reproduced evidence — documented command 1

Run from the repo root `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24`, at `12fda82f`.

```
$ python -m pytest services/api/tests/api
============================= test session starts =============================
platform win32 -- Python 3.11.9, pytest-8.4.2, pluggy-1.6.0
rootdir: C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\services\api
configfile: pyproject.toml
plugins: anyio-4.10.0, beartype-0.2.0, cov-6.0.0
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

============================ 312 passed in 38.35s =============================

real    0m41.097s
EXIT CODE = 0
```

Wall clock: started `2026-09-10T02:52:43Z`, ended `2026-09-10T02:53:25Z` (41.1s process, 38.35s
in-session). **The command TERMINATED normally.** Independent second run: `312 passed in 36.63s`
(`real 0m39.338s`), exit 0 — deterministic, same count.

On timing: the suite is genuinely slower than the 216-test round (24.98s → 38.35s here) and the
increase tracks the new at-cap boundary tests. Unlike my first pass, my wall-clock now closely matches
the producer's (35.48s claimed vs 38.35s / 36.63s observed — ~8% apart, consistent with host load
rather than a different environment).

## 3. Reproduced evidence — documented command 2

```
$ python -m pytest services/api/tests/scenario
============================= test session starts =============================
platform win32 -- Python 3.11.9, pytest-8.4.2, pluggy-1.6.0
rootdir: C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\services\api
configfile: pyproject.toml
plugins: anyio-4.10.0, beartype-0.2.0, cov-6.0.0
collected 388 items

services\api\tests\scenario\test_json_safety.py ........................ [  6%]
......                                                                   [  7%]
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

============================= 388 passed in 4.09s =============================

real    0m6.522s
EXIT CODE = 0
```

Wall clock: started `2026-09-10T02:53:36Z`, ended `2026-09-10T02:53:43Z`. Second run: `388 passed in
4.05s`, exit 0. **388 unchanged from both prior rounds** — the accepted engine suite is untouched and
unaffected.

## 4. Modularity check — and a correction to my first report

```
$ python tools/modularity_check.py --check
selected 366 files; failures 0; warnings 16
  warn symbol_ceiling: apps/web/src/lib/surveyReview/types.ts - many top-level symbols (approximate count); a signal, not a verdict
  warn review_signal: services/api/app/api/v1/scenario_analysis.py - above the warning threshold; consider the module boundary before growing it further
  warn symbol_ceiling: services/api/app/connectors/mappluto_geometry_arcgis.py - many top-level symbols; a signal, not a verdict
  warn review_signal: services/api/app/scenario/breakeven.py - above the warning threshold; ...
  (12 further pre-existing warnings, all in apps/web or tools/)
EXIT CODE = 0
```

**Exit code 0, `failures 0`.** Warnings went 15 → **16**.

### CORRECTION

My first report (at `aafc75fd`) stated: *"No warning names `app/api/v1/scenario_analysis.py`,
`tests/api/test_scenario_analysis_api.py`, or `app/main.py`."* That was accurate at `aafc75fd` and is
**no longer accurate at `12fda82f`**. The statement is hereby corrected: **one warning now names an
M5-T012 file** —

```
warn review_signal: services/api/app/api/v1/scenario_analysis.py
  - above the warning threshold; consider the module boundary before growing it further
```

Measured with the tool's own counter (`modularity_check.source_lines`), against the tool's own
thresholds:

| | SLOC | `WARN_SLOC` 600 | `JUSTIFY_SLOC` 750 | `HARD_SLOC` 1000 |
|---|---|---|---|---|
| `aafc75fd` | **572** | under | under | under |
| `12fda82f` | **666** | **crossed** → warn | under | under |

So the module grew 94 SLOC (+16.4%) in rework 2 and crossed the warning threshold only. It is **not**
above `JUSTIFY_SLOC`, so no cohesion justification is mandated, and it is far below the CI-enforced
`HARD_SLOC`. `failures` remains 0 and the gate's exit code remains 0, so the AS-8 modularity
requirement still holds — but the file is now on the policy's watch list, and the warning's own advice
("consider the module boundary before growing it further") should be honoured if M5-T012 is ever
extended. `tests/api/test_scenario_analysis_api.py` and `app/main.py` still draw no warning.

## 5. Diff-scope analysis at the new SHA

### 5.1 Whole arc (packet commit to reviewed SHA) and forbidden paths

```
$ git diff --stat c83206c2..12fda82f
 project-control/reports/M5-T012-producer-report.md |  542 ++++++++
 services/api/app/api/v1/scenario_analysis.py       |  807 +++++++++
 services/api/app/main.py                           |    8 +
 .../api/tests/api/test_scenario_analysis_api.py    | 1442 ++++++++++++++++++
 4 files changed, 2799 insertions(+)

$ git diff --name-status c83206c2..12fda82f
A  project-control/reports/M5-T012-producer-report.md
A  services/api/app/api/v1/scenario_analysis.py
M  services/api/app/main.py
A  services/api/tests/api/test_scenario_analysis_api.py
```

Exactly the packet's four `allowed_paths`, **zero deletions across the whole arc**. Rework 2 alone
(`aafc75fd..12fda82f`) is 3 files, 1093 insertions / 125 deletions — the route module (+214/-…), its
test file (+688/-…), and the producer report — matching what the coordinator described.

Every `forbidden_paths` entry probed across the whole arc with
`git diff --name-only c83206c2..12fda82f -- <path>`; all return **0 changed files**:

| Probe | Changed files |
|---|---|
| `services/api/app/scenario/` | 0 |
| `services/api/app/config.py` | 0 |
| `services/api/tests/scenario/` | 0 |
| `services/api/app/api/v1/scenario.py` | 0 |
| `services/api/app/api/v1/rule_evaluation.py` | 0 |
| `services/api/app/api/v1/properties.py` | 0 |
| `services/api/app/profile/` | 0 |
| `services/api/app/rules/` | 0 |
| `services/api/app/spatial/` | 0 |
| `services/api/app/connectors/` | 0 |
| `packages/contracts/` | 0 |
| `apps/web/` | 0 |
| `supabase/` | 0 |
| `tools/` | 0 |
| `services/api/tests/api/test_scenario_api.py` | 0 |
| `services/api/tests/api/test_rule_evaluation_api.py` | 0 |
| `services/api/tests/api/test_properties_v1.py` | 0 |

**Diff scope: CLEAN.** No new feature flag (config.py untouched); the existing
`internal_scenario_enabled` helper is still the only gate.

### 5.2 `main.py` — byte-unchanged this round, and the earlier additive edit still holds

The producer's claim that C7 was a test gap rather than a code defect is verified two ways:

```
$ git diff aafc75fd..12fda82f -- services/api/app/main.py
(empty)

blob OID at aafc75fd : 071f7755094135a7e66b3109cc41bae8f88cc802
blob OID at 12fda82f : 071f7755094135a7e66b3109cc41bae8f88cc802   → IDENTICAL
```

Identical blob object IDs are proof of byte-identity, not merely of an empty textual diff. And the
additive edit I verified in the first pass still stands unchanged from the packet commit:

```
$ git diff --numstat c83206c2..12fda82f -- services/api/app/main.py
8       0       services/api/app/main.py
```

Eight added lines, zero removed: one import (L34), one six-line comment, one `include_router` (L135,
appended last), with `properties` → `rule_evaluation` → `scenario` order preserved ahead of it. Nothing
in rework 2 disturbed it.

### 5.3 OpenAPI document still byte-identical with the flag off and on

Repeated because rework 2 touched the request-handling path. Built the app in-process at `12fda82f`
with `INTERNAL_SCENARIO_ENABLED` absent, empty, an unknown token, and explicitly `true`:

```
flag=None    paths=2  toolkit/scenario paths in schema=[]  ['/api/v1/health', '/api/v1/properties/{bbl}']
flag=''      paths=2  toolkit/scenario paths in schema=[]  ['/api/v1/health', '/api/v1/properties/{bbl}']
flag='yes'   paths=2  toolkit/scenario paths in schema=[]  ['/api/v1/health', '/api/v1/properties/{bbl}']
flag='true'  paths=2  toolkit/scenario paths in schema=[]  ['/api/v1/health', '/api/v1/properties/{bbl}']

sha256(openapi, sort_keys) flag off : a5c042a6b74b915d7bef2c8efcfc6946cf4ea2cd4ae69e93f7ca7edd1426b739
sha256(openapi, sort_keys) flag on  : a5c042a6b74b915d7bef2c8efcfc6946cf4ea2cd4ae69e93f7ca7edd1426b739
BYTE-IDENTICAL: True
```

Identical digests, two paths, **no scenario or toolkit path in the schema in any flag state**. The
rework changed no published contract and leaks nothing about the internal feature.

### 5.4 Regression — zero pre-existing test regressed

Baseline re-established on the reviewed tree with the new test file excluded (`--ignore`; `--deselect`
with forward-slash node ids silently no-ops on this platform):

```
$ python -m pytest services/api/tests/api --ignore=services/api/tests/api/test_scenario_analysis_api.py
collected 141 items
...
============================ 141 passed in 18.66s =============================
EXIT CODE = 0
```

Per-file collected counts, full run vs baseline at `12fda82f`:

| Test file | Full suite | Baseline (new file ignored) | Delta |
|---|---|---|---|
| `tests/api/test_contract_schema_packaging.py` | 4 | 4 | 0 |
| `tests/api/test_properties_v1.py` | 41 | 41 | 0 |
| `tests/api/test_property_contract.py` | 34 | 34 | 0 |
| `tests/api/test_provenance_boundary_api.py` | 3 | 3 | 0 |
| `tests/api/test_rule_evaluation_api.py` | 32 | 32 | 0 |
| `tests/api/test_scenario_api.py` | 27 | 27 | 0 |
| `tests/api/test_scenario_analysis_api.py` | **171** | absent | +171 (this task's file) |
| **Total** | **312** | **141** | **+171** |

**141 + 171 = 312**, exactly. The six pre-existing api files hold their counts at
**4 / 41 / 34 / 3 / 32 / 27 = 141**, identical to both prior rounds, and all 141 pass with the reworked
route registered. Because the arc edits no pre-existing test file (5.1), those 141 tests are
byte-identical to their pre-change selves — a true before/after comparison. The task's own file grew
75 → 171 (+96), matching the claim; every added test is inside the file this task owns.

Scenario suite: 388 collected, 388 passed, directory byte-unchanged.

**Pre-existing tests regressed: 0. Newly skipped, xfailed, or deselected: 0.** Cross-check from an
independent direction: the CI-wide collection count rose 2096 → 2192 (+96), the same delta, with no
other file's count moving.

## 6. Rework-2 regression surface (product code)

Rework 2 is the first round to change product code since my last pass, so I checked what it could
break beyond the suites:

* **No new (HTTP status, state) pair.** The module-level `STATUS_STATE_MATRIX` is **byte-identical**
  to `aafc75fd` (nine pairs: `(200,None)`, `(422,"validation_error")`, `(404,"no_match")`,
  `(502,"schema_drift")`, `(503,"rate_limited")`, `(503,"source_unavailable")`, `(504,"timeout")`,
  `(500,"internal_error")`, `(500,"internal_contract_error")`). The three fixes reuse existing pairs,
  as claimed: surrogate strings/keys and nested fact keys land on the existing
  `(422,"validation_error")`, and the guarded engine call falls back to the existing
  `(500,"internal_error")` via `_internal_error_500`. No new emission pair enters the contract.
* **Imports: one stdlib addition, no new engine reach.** The module's import block differs from
  `aafc75fd` by exactly one line, `from collections.abc import Callable`. Engine access is still
  the `app.scenario` facade plus the `app.scenario.contract` pair that the accepted M5-T003 route
  imports identically. No new module, no new connector, no engine internals.
* **The three claimed fixes are present** in the diff: `_string_boundary_error` rejects unencodable
  text ("an unpaired surrogate") and over-length strings; `_structural_error` walks the whole parsed
  body **iteratively** with an explicit stack (the docstring notes this cannot raise `RecursionError`),
  checking `FORBIDDEN_FACT_KEYS` against dict keys **at every depth**, plus depth, string length and
  encodability; and the engine call plus `_finish` now sit inside `try: … except Exception: … return
  _internal_error_500(correlation_id)`. These are the G1/G5 BLOCKING items, implemented where claimed.
* **Whitespace / line endings:** 0 trailing-whitespace lines in the route module, the test file, and
  the producer report (measured on the committed blobs, CR-stripped). Both new blobs remain CRLF
  (807 CR / 806 lines; 1442 CR / 1441 lines), matching the repo-wide convention I recorded last time.
  `.gitattributes` imposes no `eol` rule on `services/api/**` or `project-control/reports/**`.

## 7. CI honesty — no CI run is citable for this SHA, and why

**There is no CI run to cite for `12fda82f`, and nothing in this report should be read as a green
pipeline.** Evidence:

* `git branch -r --contains 12fda82f` → **empty**. No remote ref contains the reviewed commit.
* `git rev-parse --abbrev-ref --symbolic-full-name @{u}` → `fatal: no upstream configured for branch
  'candidate/D-024-mrl-option-b'`.
* `git rev-list --count origin/main..HEAD` → **868**; `git rev-list --count --all --not --remotes` →
  **354**. The branch is local-only by **owner hold**; GitHub is intentionally stale (`origin/main`
  head is `d8b3899f`, PR #240).
* `gh run list` → runs whose `headSha` is `12fda82f`: **0** (only unrelated scheduled audits against
  the stale `d8b3899f`).

CI-readiness is therefore a local-evidence judgement. The two conditions affecting the CI job
`api (ruff + pytest)` are unchanged from my first pass — **both pre-existing, both outside this
packet's `allowed_paths`, both untouched by the whole arc, neither M5-T012's to fix.**

### 7.1 PRE-EXISTING DEFECT — `ruff check .` still fails (not M5-T012's)

Run exactly as CI runs it (`working-directory: services/api`, step `ruff check .`,
`.github/workflows/ci.yml` L187-L211) with ruff **0.13.0**, the CI pin:

```
$ cd services/api && ruff check .
Found 27 errors.
[*] 4 fixable with the `--fix` option.
EXIT CODE = 1
```

**Identical to my first pass: 27 errors** — 23 × E501, 2 × I001, 2 × B905 — in the same nine
already-accepted M5 files: `tests/scenario/test_scenario_comparison.py` (9),
`app/scenario/comparison.py` (6), `tests/scenario/test_scenario_ranking.py` (3),
`tests/scenario/test_json_safety.py` (2), `app/scenario/sensitivity.py` (2),
`app/scenario/ranking.py` (2), `tests/scenario/test_scenario_sensitivity.py` (1),
`tests/scenario/test_scenario_derive.py` (1), `app/scenario/breakeven.py` (1). All nine live under
`app/scenario/**` / `tests/scenario/**` — this packet's **`forbidden_paths`** — and all nine are
byte-unchanged across `c83206c2..12fda82f`. **None of the 27 is in a file M5-T012 owns**, and the
count did not move despite the rework, which is itself evidence the rework added no lint debt.

The three files this task owns or touched are clean at the new SHA:

```
$ cd services/api && ruff check app/api/v1/scenario_analysis.py tests/api/test_scenario_analysis_api.py app/main.py
All checks passed!
EXIT CODE = 0
```

**Stated plainly: the CI job `api (ruff + pytest)` would fail at its Ruff step on this branch
independently of M5-T012** — a real pre-existing defect in accepted M5 code, deserving its own
follow-up task (23 of 27 are trivial line-length wraps; 4 are ruff-autofixable). M5-T012 may not
legally touch those files, so it cannot be the vehicle for the fix.

### 7.2 PRE-EXISTING ENVIRONMENT GAP — CI's wider `pytest -q` still uncollectable locally

```
$ cd services/api && python -m pytest -q --collect-only
app\documents\units.py:276
    def _match_unit[UnitT: enum.Enum](
                   ^
SyntaxError: expected '('
...
ERROR tests/documents/test_checks_area.py   (+ 14 more, all tests/documents)
!!!!!!!!!!!!!!!!!! Interrupted: 15 errors during collection !!!!!!!!!!!!!!!!!!!
2192 tests collected, 15 errors in 11.35s
EXIT CODE = 2
```

Same **15** collection errors, all under `tests/documents`, from PEP 695 generic-function syntax at
`app/documents/units.py:276` — valid on CI's Python 3.12, a `SyntaxError` on this 3.11.9 sandbox.
`units.py` was last touched by `561d2899` (M2-T015), long before this packet. A precise import grep
for `^\s*(from|import)\s+app\.documents` across `tests/api`, `tests/scenario`, and
`app/api/v1/scenario_analysis.py` returns **no matches**, so neither packet suite can reach it; both
are fully collectible and green on 3.11. Not a regression, and unrelated to this task. (Collected
total rose 2096 → 2192, the +96 new tests, while the error count stayed at 15.)

## 8. Worktree / read-only discipline

`git status --porcelain` was captured before any command I ran and compared after all of them:
**identical**. Everything present is pre-existing and none of it is mine, beyond this report:

```
 M project-control/state.json                      (pre-existing, orchestrator's ledger edit)
 M project-control/tasks/M5-T012.json              (pre-existing, orchestrator's ledger edit)
?? .claude/agent-memory/qa-engineer/*              (pre-existing, left alone)
?? project-control/gates/M5-T012-G1|G3|G4|G5.json  (pre-existing gate records, left alone)
?? project-control/reports/M5-T012-DCV|G1|G3|G4|G5.md (pre-existing reports, left alone)
?? scratchpad/                                     (pre-existing, left alone)
```

`M5-T012-G4.md` (my first-pass report) is untouched. `git rev-parse HEAD` is still
`12fda82f3f237f2432efc99614c903496a8b2e02`. No commit, push, stash, checkout, install, or ledger
write occurred; tracked bytes are unchanged. My scratch snapshots live outside the repo in the session
scratchpad.

## 9. Producer-report claim audit

| Producer claim | My observation | Status |
|---|---|---|
| `tests/api` → **312 passed in 35.48s**, exit 0, terminated | 312 passed in 38.35s / 36.63s, exit 0, terminated twice | **CONFIRMED** |
| `tests/scenario` → **388 passed in 4.17s**, exit 0 | 388 passed in 4.09s / 4.05s, exit 0 | **CONFIRMED** |
| "Was 216 before… the 96 added tests are all in this task's own file (75 → 171)" | new file collects 171; 141 baseline unchanged; 141+171=312 | **CONFIRMED** |
| "No pre-existing test changed behaviour" | per-file counts identical; all 141 pass | **CONFIRMED** |
| `modularity_check.py --check` → exit 0 | exit 0, failures 0 (warnings 16, one now naming this module) | **CONFIRMED** (with the section-4 nuance) |
| 141 api baseline without the new file | 141 passed | **CONFIRMED** |
| C7 was a test gap, not a code defect (`main.py` unchanged) | identical blob OID at both SHAs | **CONFIRMED** |
| Fixes reuse existing `(422,"validation_error")` and `_internal_error_500` | `STATUS_STATE_MATRIX` byte-identical; fixes present as described | **CONFIRMED** |

Unlike the first round, the producer's wall-clocks now reproduce on this host (within ~8%). No claim I
checked is contradicted, and no material figure rests on the producer's report rather than my own runs.

## 10. Verdict

**PASS at `12fda82f3f237f2432efc99614c903496a8b2e02`.**

Both packet-documented commands run to completion and are green, reproduced twice each by me:
**312 passed** (`services/api/tests/api`, 38.35s then 36.63s) and **388 passed**
(`services/api/tests/scenario`, 4.09s then 4.05s), both exit 0. The whole arc stays inside the
packet's four `allowed_paths` with **zero deletions**; all 17 `forbidden_paths` probes return 0 changed
files; `main.py` is byte-identical to `aafc75fd` (same blob OID) while still carrying exactly the
`+8/-0` additive edit from the packet commit; the engine package and `config.py` are untouched; and the
published OpenAPI document is byte-identical (same SHA-256) with the flag absent, empty, unknown, and
true. **Zero pre-existing tests regressed**: the 141-test api baseline holds with identical per-file
counts (4/41/34/3/32/27), 141 + 171 = 312, and the 388 engine tests are unchanged. Rework 2 introduced
no new `(status, state)` pair and no new engine import. `modularity_check.py --check` exits 0 with
`failures 0`.

**Correction carried forward:** my first report's claim that no modularity warning named an M5-T012
file is no longer true. `scenario_analysis.py` grew 572 → 666 SLOC and crossed `WARN_SLOC = 600`, so
it now draws `warn review_signal`. It remains below `JUSTIFY_SLOC` (750) and `HARD_SLOC` (1000);
failures stay 0 and the gate still exits 0, so AS-8's modularity requirement is met — but the module is
now on the policy's watch list and its boundary should be reconsidered before any further growth.

Recorded for follow-up, **not** blocking M5-T012 (both pre-existing, both outside `allowed_paths`,
both byte-untouched by the arc, both identical to my first pass):

1. **Recommend a new task:** `ruff check .` from `services/api` fails with 27 errors (23 E501, 2 I001,
   2 B905) in nine already-accepted M5 files under `app/scenario/**` and `tests/scenario/**`. CI's
   `api (ruff + pytest)` job will fail at its Ruff step until that is cleaned up, independently of
   M5-T012, which may not legally touch those files.
2. **Informational:** CI's wider `pytest -q` cannot be collected on this 3.11 sandbox
   (`app/documents/units.py:276` needs 3.12 for PEP 695 syntax; 15 `tests/documents` collection
   errors). CI runs 3.12 and neither packet suite imports `app.documents` — the known environment gap,
   not a regression.

No CI run is citable for `12fda82f`: the branch is local-only under the owner hold, no remote ref
contains the commit, and `gh` reports zero runs for this SHA.

---
*G4 integration / regression evidence gate, re-review — independent, read-only. Supersedes
`M5-T012-G4.md` (PASS at `aafc75fd`), which is left intact. Every figure above is reproducible from the
commands quoted, at `12fda82f`.*
