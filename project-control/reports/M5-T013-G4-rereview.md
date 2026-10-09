# G4 RE-REVIEW — INTEGRATION / REGRESSION EVIDENCE VERIFICATION — M5-T013

**Verdict: PASS** at `209b9548` (no blocking conditions; all six published digests reproduce; my earlier timing correction is retired with the explanation confirmed; two pre-existing out-of-packet CI conditions restated as facts)

| Field | Value |
|---|---|
| Task | M5-T013 — evidence / provenance endpoint |
| Reviewed SHA | `209b9548a18fa45f27c5b87f4af7989939645d81` (confirmed via `git rev-parse HEAD`) |
| Branch | `candidate/D-024-mrl-option-b` (fast-forwarded from the task branch) |
| Previous G4 | PASS at `29ca7bca` (`project-control/reports/M5-T013-G4.md`, left intact); stands on its own terms, superseded by this one |
| Commit arc | `9a84d392` (G0 packet) → `29ca7bca` (producer output) → `209b9548` (rework: G1 BLOCKING-1 silent projection, BLOCKING-2 `rule_conflict`, G3 H-1..H-5) |
| Gate | G4 — integration / regression evidence (independent) |
| Verifier | ci-evidence-verifier (read-only, independent) |
| Date | 2026-09-10 (UTC) |
| Environment | Windows 11, Python 3.11.9, pytest 8.4.2, ruff 0.13.0, rootdir `services/api` (configfile `pyproject.toml`) |

`29ca7bca` is confirmed an ancestor of `209b9548` (`git merge-base --is-ancestor` → true): a true
fast-forward rework of the tree I verified before, not a rebase onto different history.

## 0. Statement of independence

I am not the producer of M5-T013. I wrote, edited, and advised on nothing in this change, and I fixed
nothing. Every figure below comes from a command I ran myself at `209b9548`, after confirming HEAD. I
ran both documented suites to completion before opening the producer's report; the claim audit
(section 9) and the digest verification (section 6) are post-hoc comparisons against values the
producer published, not sources for my own numbers. My only write is this file; `M5-T013-G4.md` is
untouched. No `tools/project_control.py`, no git write, no `gh` write, no `pip install`.

## 1. Claim-by-claim result

| # | Material claim | Result | Observed |
|---|---|---|---|
| 1 | `pytest services/api/tests/api` terminates and is green, **371 passed** | **CONFIRMED** | 371 passed in 10.36s, exit 0 (re-run: 371 in 14.23s) |
| 2 | `pytest services/api/tests/scenario` terminates and is green, **388 passed** unchanged | **CONFIRMED** | 388 passed in 1.36s, exit 0 (re-run: 1.78s) |
| 3 | 312 pre-existing unchanged + 59 evidence (was 37) | **CONFIRMED** | baseline 312; new file collects **59**; 312 + 59 = 371 |
| 4 | The ~43s I measured earlier was CPU contention, not a scoping error | **CONFIRMED — my earlier correction is retired** | same command, 22 *more* tests, now **10.36s**; see section 2 |
| 5 | `modularity_check --check` exit 0, new module still no warn | **CONFIRMED** | `selected 367; failures 0; warnings 16`, exit 0; no warn names the new module |
| 6 | New module 410 → 418 SLOC, under the 600 threshold | **CONFIRMED** | measured 410 at `29ca7bca`, **418** at `209b9548`; 182 under `WARN_SLOC` |
| 7 | The only `evidence.py` warn is `tools/agent_supervisor/evidence.py` at 603 SLOC | **CONFIRMED** | exactly one warning line contains "evidence"; 603 SLOC; pre-existing |
| 8 | Change confined to `allowed_paths` | **CONFIRMED** | rework: 3 files; whole arc: 4 files, 2170 insertions, **0 deletions** |
| 9 | Nothing in `forbidden_paths` | **CONFIRMED** | all 20 probed paths: 0 changed files (section 5.1) |
| 10 | `main.py` byte-unchanged this round, still carrying the +8 additive edit | **CONFIRMED (blob OID)** | `128593c6…` at both `29ca7bca` and `209b9548`; `8 insertions / 0 deletions` from `9a84d392` |
| 11 | OpenAPI byte-identical across the four flag states | **CONFIRMED** | one SHA-256 across absent / empty / unknown / true; no evidence path in any state |
| 12 | Still the same OpenAPI digest as at M5-T012's accepted SHA | **CONFIRMED** | `a5c042a6…` — published contract unchanged across **three** tasks |
| 13 | Zero pre-existing test regressed | **CONFIRMED** | 312 baseline passes; seven pre-existing files keep 4/41/34/3/32/171/27 |
| 14 | CI-wide collection 2229 → 2251 (+22) | **CONFIRMED** | exactly 2251 collected, 15 errors unchanged |
| 15 | **All six published digests (two bases × three files)** | **CONFIRMED — every one reproduces** | section 6 |
| 16 | `main.py`'s on-disk digest equals the previously published value | **CONFIRMED** | `97be9148…` at both revisions — independent corroboration of claim 10 |
| 17 | `ruff` count still 27 and unmoved; this task's files clean | **CONFIRMED** | 27 errors, same 9 pre-existing files, same rule mix; owned files "All checks passed" |
| 18 | 15 `tests/documents` PEP 695 collection errors unchanged | **CONFIRMED** | 15, `units.py:276` |
| 19 | A green CI run exists for this SHA | **NOT APPLICABLE / NOT CITABLE** | zero runs for `209b9548`; branch local-only by owner hold (section 7) |
| 20 | The rework introduced no new (HTTP status, state) pair | **CONFIRMED** (contract surface) | `STATUS_STATE_MATRIX` byte-identical to `29ca7bca`; imports identical |

## 2. Reproduced evidence — documented command 1, and the timing question settled

```
$ python -m pytest services/api/tests/api
============================= test session starts =============================
platform win32 -- Python 3.11.9, pytest-8.4.2, pluggy-1.6.0
rootdir: C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\services\api
configfile: pyproject.toml
plugins: anyio-4.10.0, beartype-0.2.0, cov-6.0.0
collected 371 items

services\api\tests\api\test_contract_schema_packaging.py ....            [  1%]
services\api\tests\api\test_evidence_api.py ............................ [  8%]
...............................                                          [ 16%]
services\api\tests\api\test_properties_v1.py ........................... [ 24%]
..............                                                           [ 28%]
services\api\tests\api\test_property_contract.py ....................... [ 34%]
...........                                                              [ 37%]
services\api\tests\api\test_provenance_boundary_api.py ...               [ 38%]
services\api\tests\api\test_rule_evaluation_api.py ..................... [ 43%]
...........                                                              [ 46%]
services\api\tests\api\test_scenario_analysis_api.py ................... [ 51%]
........................................................................ [ 71%]
........................................................................ [ 90%]
........                                                                 [ 92%]
services\api\tests\api\test_scenario_api.py ...........................  [100%]

============================ 371 passed in 10.36s =============================

real    0m11.372s
EXIT CODE = 0
```

Wall clock: started `2026-09-10T05:15:41Z`, ended `2026-09-10T05:15:52Z`. **TERMINATED normally.**
Second run: `371 passed in 14.23s` (`real 0m15.704s`), exit 0 — same count.

### My earlier timing correction is retired, and the contention explanation is confirmed

In my `29ca7bca` report I flagged that the documented command took 43.00s on this host against an
expected ~10s, and attributed the gap structurally (M5-T012's 171 tests still in the suite). That
structural reasoning was wrong, and the CPU-contention explanation is right. The proof is in my own
numbers at this SHA:

| Measurement | At `29ca7bca` (contended) | At `209b9548` (uncontended) |
|---|---|---|
| `pytest services/api/tests/api` | 43.00s / 42.77s (349 tests) | **10.36s** / 14.23s (**371** tests) |
| `pytest services/api/tests/scenario` | 4.49s / 4.29s | **1.36s** / 1.78s |
| baseline without the evidence file | 37.31s (312 tests) | **9.52s** (312 tests) |
| evidence test file alone | 9.52s (37 tests) | **4.10s** (59 tests) |

The same 312-test baseline runs 37.31s then 9.52s — a ~3.9× spread on an identical test set, which can
only be host load, not scope. With 22 more tests the full suite is now 4× faster than I measured
before, and my 10.36s lands within 6% of the producer's 9.80s. **The producer's and coordinator's ~10s
figures were correct; my earlier 43s was measured under contention from concurrent reviewer runs.** The
two runs at this SHA (10.36s, 14.23s) show the residual variance directly. I record this as a
correction to my own prior report, not to anyone else's claim.

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

============================= 388 passed in 1.36s =============================

real    0m2.144s
EXIT CODE = 0
```

Second run: `388 passed in 1.78s`, exit 0. **388 unchanged across all four rounds I have verified** —
`tests/scenario/**` is a forbidden path with 0 changed files.

## 4. Modularity — exit 0, and the filename collision still resolved the same way

```
$ python tools/modularity_check.py --check
selected 367 files; failures 0; warnings 16
  ...
  warn review_signal: tools/agent_supervisor/evidence.py - above the warning threshold; ...
  ...
EXIT CODE = 0
```

**Exit 0, `failures 0`, warnings 16** — unchanged from `29ca7bca`, so the rework added no modularity
signal. `grep` of the output for `api/v1/evidence|test_evidence_api` returns **no match** (exit 1).

| File | Status | SLOC | vs `WARN_SLOC` 600 | Result |
|---|---|---|---|---|
| `services/api/app/api/v1/evidence.py` | this task's module | **418** (was **410** at `29ca7bca`) | **182 under** | **no warning** |
| `tools/agent_supervisor/evidence.py` | pre-existing (`ed04c4bb`, M0-T149); `tools/**` forbidden, 0 changed files | **603** | 3 over | **this is the warned file** |

The producer's 410 → 418 figure is exactly right (measured with the tool's own
`modularity_check.source_lines`; +8 SLOC for a change that net-added 138 lines to the file, the rest
being docstring and comment). `scenario_analysis.py` (M5-T012) still carries its own pre-existing warn
at 666 SLOC.

## 5. Diff-scope analysis

### 5.1 Scope and forbidden paths

Rework only (`29ca7bca..209b9548`) — the first round in this arc with deletions:

```
 project-control/reports/M5-T013-producer-report.md | 233 ++++++++--
 services/api/app/api/v1/evidence.py                | 138 +++---
 services/api/tests/api/test_evidence_api.py        | 506 +++++++++++++++++++--
 3 files changed, 749 insertions(+), 128 deletions(-)
```

All three are `allowed_paths` entries. The 128 deletions are rewrites *inside files this task created
in the same arc*, so measured from the packet commit the whole change remains purely additive:

```
$ git diff --stat 9a84d392..209b9548
 project-control/reports/M5-T013-producer-report.md |  322 +++++
 services/api/app/api/v1/evidence.py                |  548 +++++++++
 services/api/app/main.py                           |    8 +
 services/api/tests/api/test_evidence_api.py        | 1292 ++++++++++++++++++++
 4 files changed, 2170 insertions(+)
```

Exactly the four `allowed_paths`, **zero deletions across the arc**. Every `forbidden_paths` entry
probed with `git diff --name-only 9a84d392..209b9548 -- <path>`; all **0 changed files**:

| Probe | Changed | | Probe | Changed |
|---|---|---|---|---|
| `services/api/app/config.py` | 0 | | `services/api/app/resilience/` | 0 |
| `services/api/app/api/v1/properties.py` | 0 | | `services/api/tests/api/test_properties_v1.py` | 0 |
| `services/api/app/api/v1/rule_evaluation.py` | 0 | | `services/api/tests/api/test_rule_evaluation_api.py` | 0 |
| `services/api/app/api/v1/scenario.py` | 0 | | `services/api/tests/api/test_scenario_api.py` | 0 |
| `services/api/app/api/v1/scenario_analysis.py` | 0 | | `services/api/tests/api/test_scenario_analysis_api.py` | 0 |
| `services/api/app/profile/` | 0 | | `services/api/tests/scenario/` | 0 |
| `services/api/app/rules/` | 0 | | `packages/contracts/` | 0 |
| `services/api/app/scenario/` | 0 | | `apps/web/` | 0 |
| `services/api/app/spatial/` | 0 | | `supabase/` | 0 |
| `services/api/app/connectors/` | 0 | | `tools/` | 0 |

**Diff scope: CLEAN.** The four sibling routes, `config.py`, and the profile / rules / scenario /
spatial / connectors / resilience packages are byte-untouched: the module remains a read-only consumer
and no new flag exists.

### 5.2 `main.py` byte-unchanged this round — blob-OID method

```
blob OID at 9a84d392 : 071f7755094135a7e66b3109cc41bae8f88cc802
blob OID at 29ca7bca : 128593c65bc96a03b5a7e9c547880c6545b6732f
blob OID at 209b9548 : 128593c65bc96a03b5a7e9c547880c6545b6732f   → IDENTICAL to 29ca7bca

$ git diff 29ca7bca..209b9548 -- services/api/app/main.py
(empty)

$ git diff --numstat 9a84d392..209b9548 -- services/api/app/main.py
8       0       services/api/app/main.py
```

Identical blob OIDs are proof of byte-identity, not merely an empty textual diff: **`main.py` is
unmodified by this rework** and still carries exactly the `+8/-0` additive edit I verified at
`29ca7bca` (one import, one `include_router` appended last, a six-line comment, with all four
pre-existing registrations keeping their order). This is corroborated independently by the producer's
published on-disk digest (section 6).

### 5.3 OpenAPI — byte-identical in every flag state, and unchanged across three tasks

```
flag=None    paths=2  evidence in schema=[]  ['/api/v1/health', '/api/v1/properties/{bbl}']
flag=''      paths=2  evidence in schema=[]  ['/api/v1/health', '/api/v1/properties/{bbl}']
flag='yes'   paths=2  evidence in schema=[]  ['/api/v1/health', '/api/v1/properties/{bbl}']
flag='true'  paths=2  evidence in schema=[]  ['/api/v1/health', '/api/v1/properties/{bbl}']

sha256 (all four) : a5c042a6b74b915d7bef2c8efcfc6946cf4ea2cd4ae69e93f7ca7edd1426b739
ALL FOUR BYTE-IDENTICAL: True
MATCHES M5-T012 accepted digest a5c042a6...: True
```

One digest across all four `INTERNAL_RULE_EVAL_ENABLED` states, two paths, **no evidence path in the
schema in any state** — `include_in_schema=False` holds regardless of the flag. The digest is the same
value I recorded at M5-T012's `12fda82f` and at M5-T013's `29ca7bca`: **the published contract is
byte-unchanged across three consecutive tasks** (M5-T012, M5-T013 output, M5-T013 rework). No
consumer-visible regression.

### 5.4 Regression — zero pre-existing test regressed

```
$ python -m pytest services/api/tests/api --ignore=services/api/tests/api/test_evidence_api.py
collected 312 items
...
============================= 312 passed in 9.52s =============================
EXIT CODE = 0
```

| Test file | Full suite | Baseline (evidence file ignored) | Delta |
|---|---|---|---|
| `tests/api/test_contract_schema_packaging.py` | 4 | 4 | 0 |
| `tests/api/test_properties_v1.py` | 41 | 41 | 0 |
| `tests/api/test_property_contract.py` | 34 | 34 | 0 |
| `tests/api/test_provenance_boundary_api.py` | 3 | 3 | 0 |
| `tests/api/test_rule_evaluation_api.py` | 32 | 32 | 0 |
| `tests/api/test_scenario_analysis_api.py` | 171 | 171 | 0 |
| `tests/api/test_scenario_api.py` | 27 | 27 | 0 |
| `tests/api/test_evidence_api.py` | **59** | absent | +59 (this task's file) |
| **Total** | **371** | **312** | **+59** |

**312 + 59 = 371**, exactly. The seven pre-existing files hold
**4 / 41 / 34 / 3 / 32 / 171 / 27 = 312** — identical to M5-T012's accepted total and to my two earlier
rounds — and all 312 pass with the reworked route registered. The arc edits no pre-existing test file
(5.1), so those 312 tests are byte-identical to their pre-change selves: a true before/after comparison.

CI-wide cross-check, third consecutive round: collection **2229 → 2251 (+22)**, exactly the evidence
file's 37 → 59 growth, with no other file's count moving and the error count unchanged at 15.

**Pre-existing tests regressed: 0. Newly skipped, xfailed, or deselected: 0.**

## 6. The published-digest claim — verified, all six, both bases

This was flagged for my gate specifically, so I verified every published value against the actual
files rather than accepting the table. The producer publishes two digests per file, labelled
"on-disk bytes (CRLF)" and "LF-normalised (git blob)". I recomputed all six independently:

| File | Basis | Published | Observed | Result |
|---|---|---|---|---|
| `app/api/v1/evidence.py` | on-disk CRLF | `fa37a6b8…7c15` | `fa37a6b8…7c15` | **MATCH** |
| `app/api/v1/evidence.py` | LF / git blob | `53b11558…49a6` | `53b11558…49a6` | **MATCH** |
| `app/main.py` | on-disk CRLF | `97be9148…e875` | `97be9148…e875` | **MATCH** |
| `app/main.py` | LF / git blob | `b6930f0c…4809` | `b6930f0c…4809` | **MATCH** |
| `tests/api/test_evidence_api.py` | on-disk CRLF | `45c22b98…dc62` | `45c22b98…dc62` | **MATCH** |
| `tests/api/test_evidence_api.py` | LF / git blob | `b1c1a74d…d5c6` | `b1c1a74d…d5c6` | **MATCH** |

**All six reproduce.** Method: on-disk column `sha256(Path(f).read_bytes())`; LF column the same bytes
with `\r\n` → `\n`. I additionally confirmed the LF column equals `sha256(git show 209b9548:<file>)`
for all three files, so the "LF-normalised (git blob)" label is accurate, and that all three files are
genuinely CRLF on disk (evidence.py 26612 disk / 26064 LF bytes; main.py 7495 / 7342;
test_evidence_api.py 58345 / 57053).

**The `main.py` continuity claim holds.** The previous report revision (at `29ca7bca`) published
`97be914803e6ea93a4e8c9a603eedf2b59a78b762bf5c40a7c04b2f2e10ce875` for `main.py`; the current on-disk
digest is byte-identical to it. That is an independent confirmation — on a different basis entirely —
of the blob-OID evidence in 5.2 that `main.py` is unmodified by this rework.

**The producer's account of its own earlier defect is accurate.** It states that at `29ca7bca` the two
published digests used different bases. I tested that against the blobs at `29ca7bca`: the published
`evidence.py` digest (`0329a469…`) matches the **LF / git-blob** basis, while the published `main.py`
digest (`97be9148…`) matches the **on-disk CRLF** basis. Exactly as described — the DCV finding is
substantiated, the self-report is honest, and the corrected table is now reproducible on either basis
without ambiguity.

## 6b. Contract-surface regression (product code changed this round)

* **No new (HTTP status, state) pair.** `STATUS_STATE_MATRIX` in `evidence.py` is **byte-identical**
  to `29ca7bca` — the same nine pairs, themselves an identical set to the accepted
  `scenario_analysis.py` matrix. The new `rule_conflict` marker (G1 HIGH-1) is a typed gap marker
  inside a normal 200 document, not a new status/state pair: `rule_conflict` appears 5 times in the
  module and `source_field_routing` 3 times, both as response content.
* **Imports byte-identical** to `29ca7bca` — the fix pulled in no new module, so the read-only
  consumption boundary is unchanged.
* **Whitespace:** 0 trailing-whitespace lines in `evidence.py`, `test_evidence_api.py`, and the
  producer report (committed blobs, CR-stripped). Ruff, which enforces the W-class rules under
  `select = ["E","F","I","UP","B"]`, passes on all three files this task owns.

## 7. CI honesty — no CI run is citable for this SHA, and why

**There is no CI run to cite for `209b9548`, and nothing here should be read as a green pipeline.**

* `git branch -r --contains 209b9548` → **empty**. No remote ref contains the commit.
* `git rev-parse --abbrev-ref --symbolic-full-name @{u}` → `fatal: no upstream configured for branch
  'candidate/D-024-mrl-option-b'`.
* `git rev-list --count origin/main..HEAD` → **872**; `git rev-list --count --all --not --remotes` →
  **358**. The branch is local-only by **owner hold**; GitHub is intentionally stale (`origin/main`
  head `d8b3899f`, PR #240).
* `gh run list` → runs whose `headSha` is `209b9548`: **0**.

The two conditions affecting the CI job `api (ruff + pytest)` are unchanged; **both pre-existing, both
outside `allowed_paths`, both byte-untouched by this arc, neither M5-T013's to fix.**

### 7.1 PRE-EXISTING — `ruff` debt, count still 27 and unmoved

```
$ cd services/api && ruff check .
Found 27 errors.
[*] 4 fixable with the `--fix` option.
EXIT CODE = 1
```

**Still exactly 27**, identical to all three prior rounds: 23 × E501, 2 × I001, 2 × B905, in the same
nine already-accepted M5 engine files (`tests/scenario/test_scenario_comparison.py` 9,
`app/scenario/comparison.py` 6, `tests/scenario/test_scenario_ranking.py` 3,
`tests/scenario/test_json_safety.py` 2, `app/scenario/sensitivity.py` 2, `app/scenario/ranking.py` 2,
`tests/scenario/test_scenario_sensitivity.py` 1, `tests/scenario/test_scenario_derive.py` 1,
`app/scenario/breakeven.py` 1). All nine are `forbidden_paths` for this task and byte-unchanged in the
arc — **the rework touched no forbidden engine file and added no lint debt.** This task's three files:

```
$ cd services/api && ruff check app/api/v1/evidence.py tests/api/test_evidence_api.py app/main.py
All checks passed!
EXIT CODE = 0
```

Recorded as a **fact, not a gate failure** (cleanup task queued separately): CI's
`api (ruff + pytest)` job would still fail at its Ruff step on this branch, independently of M5-T013.

### 7.2 PRE-EXISTING — CI's wider `pytest -q` uncollectable on Python 3.11

```
$ cd services/api && python -m pytest -q --collect-only
...
!!!!!!!!!!!!!!!!!! Interrupted: 15 errors during collection !!!!!!!!!!!!!!!!!!!
2251 tests collected, 15 errors in 2.93s
EXIT CODE = 2
```

Same **15** collection errors, all under `tests/documents`, from PEP 695 generic-function syntax at
`app/documents/units.py:276` — valid on CI's Python 3.12, a `SyntaxError` on this 3.11.9 sandbox. Not a
regression, unrelated to this task; collection rising to 2251 while errors stayed at 15 is the
cross-check that the 22 new tests were added cleanly.

## 8. Worktree / read-only discipline

`git status --porcelain` captured before any command I ran, compared after all of them: **identical
apart from this report**. Everything else present is pre-existing and none of it is mine:

```
 M project-control/state.json                       (pre-existing, orchestrator's ledger edit)
 M project-control/tasks/M5-T013.json               (pre-existing, orchestrator's ledger edit)
?? .claude/agent-memory/qa-engineer/*               (pre-existing, left alone)
?? project-control/gates/M5-T013-G1|G3|G4|G5.json   (pre-existing gate records, left alone)
?? project-control/reports/M5-T013-DCV|G1|G3|G4|G5.md (pre-existing reports, left alone)
?? scratchpad/                                      (pre-existing, left alone)
```

`M5-T013-G4.md` (my first-pass report) is untouched. `git rev-parse HEAD` is still
`209b9548a18fa45f27c5b87f4af7989939645d81`. No commit, push, stash, checkout, install, or ledger write
occurred. My scratch snapshots live outside the repo in the session scratchpad.

## 9. Producer-report claim audit

| Producer claim | My observation | Status |
|---|---|---|
| `tests/api` → **371 passed** in 9.80s (59 evidence + 312 pre-existing) | 371 passed in 10.36s / 14.23s, exit 0 | **CONFIRMED** (within 6% on the faster run) |
| `tests/scenario` → **388 passed** in 0.99s, 0 regression | 388 passed in 1.36s / 1.78s, exit 0 | **CONFIRMED** |
| "pre-existing count unchanged at 312 (371 − 59)" | baseline 312, per-file counts unmoved | **CONFIRMED** |
| `evidence.py` 518 → 548 lines, **410 → 418 SLOC** | 410 at `29ca7bca`, 418 now | **CONFIRMED** |
| `main.py` unchanged by this rework | identical blob OID, plus the digest continuity in section 6 | **CONFIRMED twice over** |
| Six digests, two bases, labelled | all six reproduce | **CONFIRMED** |
| Its own earlier table mixed the two bases (DCV finding) | verified against the `29ca7bca` blobs | **CONFIRMED — honest self-report** |

No claim I checked is contradicted. The only correction in this report is to **my own** prior timing
analysis (section 2).

## 10. Verdict

**PASS at `209b9548a18fa45f27c5b87f4af7989939645d81`.**

Both documented commands run to completion and are green, twice each: **371 passed**
(`services/api/tests/api`, 10.36s then 14.23s) and **388 passed** (`services/api/tests/scenario`,
1.36s then 1.78s), both exit 0. The whole arc from the packet commit stays inside the four
`allowed_paths` with **zero deletions**; all 20 forbidden-path probes return 0 changed files; `main.py`
is byte-unchanged this round by identical blob OID (`128593c6…`) and still carries exactly the `+8/-0`
additive edit. The published OpenAPI document is byte-identical across all four flag states and carries
the **same digest as at M5-T012's accepted SHA** — unchanged across three tasks. **Zero pre-existing
tests regressed**: 312 baseline holds with per-file counts unmoved (4/41/34/3/32/171/27),
312 + 59 = 371, CI-wide collection 2229 → 2251 (+22), 388 engine tests unchanged.
`modularity_check.py --check` exits 0 with `failures 0`; the new module is 418 SLOC and draws no warn,
and the only `evidence.py` warning remains `tools/agent_supervisor/evidence.py` at 603 SLOC.
`STATUS_STATE_MATRIX` and the module's imports are byte-identical to `29ca7bca`, so the rework added no
pair to the contract surface and no new dependency.

**Digest claim: fully verified.** All six published digests (on-disk CRLF and LF/git-blob for three
files) reproduce exactly; the LF column equals `sha256(git show 209b9548:<file>)` in every case;
`main.py`'s on-disk digest is byte-identical to the value published at `29ca7bca`, independently
corroborating that it is unmodified; and the producer's account of its own earlier mixed-basis defect
checks out against the `29ca7bca` blobs (evidence.py was the LF basis, main.py the CRLF basis).

**Correction to my own earlier report:** the ~43s api-suite timing I flagged at `29ca7bca` was CPU
contention, not scope. The identical 312-test baseline ran 37.31s there and 9.52s here, and the full
suite is now 10.36s with 22 more tests — so the producer's and coordinator's ~10s figures were right
and my structural explanation was wrong. The flag itself was still correct to raise; the conclusion
needed this second data point to settle.

Recorded for follow-up, **not** blocking M5-T013 (both pre-existing, outside `allowed_paths`,
byte-untouched by this arc):

1. **Fact, cleanup task already queued:** `ruff check .` from `services/api` → **27 errors** (23 E501,
   2 I001, 2 B905) in nine already-accepted M5 engine files; count unmoved across four rounds; this
   task added none and may not touch those files. CI's `api (ruff + pytest)` fails at its Ruff step
   independently of M5-T013.
2. **Informational:** CI's wider `pytest -q` cannot be collected on this 3.11 sandbox
   (`app/documents/units.py:276` needs 3.12 for PEP 695 syntax; 15 `tests/documents` collection
   errors). CI runs 3.12; neither this task's route nor its tests import `app.documents`.

No CI run is citable for `209b9548`: the branch is local-only under the owner hold, no remote ref
contains the commit, and `gh` reports zero runs for this SHA.

---
*G4 integration / regression evidence gate, re-review — independent, read-only. Supersedes
`M5-T013-G4.md` (PASS at `29ca7bca`), which is left intact. Every figure above is reproducible from the
commands quoted, at `209b9548`.*
