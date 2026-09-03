# G4 Integration & Regression Gate Report — M0-T107 (D-024 unit J portability plan)

> Orchestrator note: reviewer return saved verbatim (transport entity-decoding only). Reviewer: independent qa-engineer agent (read-only), returned 2026-09-03.

**Reviewer role:** Independent G4 (integration & regression), read-only
**Task:** M0-T107 — governance/planning; deliverables `docs/D024_PORTABILITY_PLAN.md` and `project-control/reports/M0-T107-portability-plan.md`
**Repository:** ctl24 shared object store (reviewed from a linked reviewer worktree; same object database)
**Branch:** `candidate/D-024-mrl-option-b`
**Frozen reviewed submit identity:** `93a7157f` (submit `awaiting_gate`); adoption identity `96f1b89b`; task-branch tip `777ef5e4` (`task/M0-T107-plugin-portability`)
**ctl24 HEAD reviewed (current live tip):** `c50fab0e` — the branch advanced two commits past `93a7157f` during review (03a9b911 G0/G2 PASS records; c50fab0e frozen submit-evidence record); both are M0-T107 gate/control-plane records verified within the allowed footprint. Baseline for the wave: `99165bc2`.
**Date:** 2026-09-02

## Scope

G4 verifies that adopting the reviewed task-branch content onto the candidate branch did not alter the deliverables, did not exceed a bounded control-plane footprint, and produced no code/test/schema/dependency/live-system side effects. Content-quality (G3) and per-requirement directive compliance (DCV) are out of G4 scope.

## Results by check

### 1. Blob identity — PASS
`git diff 777ef5e4 <tip> -- <two deliverables>` is EMPTY at both the frozen submit SHA and the current tip:
```
git diff 777ef5e4 93a7157f -- docs/... reports/...   -> (empty) exit 0
git diff 777ef5e4 c50fab0e -- docs/... reports/...   -> (empty) exit 0
```
Tree blob hashes match on both sides:
```
docs/D024_PORTABILITY_PLAN.md                 blob a0f1790f...  (777ef5e4 == 93a7157f)
project-control/reports/M0-T107-portability... blob 0392f0af...  (777ef5e4 == 93a7157f)
```
The adopted content is byte-identical to the independently reviewed task-branch content, and remains so through the current tip (added at `96f1b89b` as `A`, never subsequently `M`).

### 2. Bounded footprint — PASS
Adoption commit `96f1b89b` touches exactly the two files:
```
A  docs/D024_PORTABILITY_PLAN.md
A  project-control/reports/M0-T107-portability-plan.md
```
Cumulative footprint of the whole wave, baseline `99165bc2` → current tip `c50fab0e` (12 unique path-status lines), every one inside the allowed set:
```
A  docs/D024_PORTABILITY_PLAN.md                                            (deliverable)
A  project-control/directives/D-024-fable-codex-loop/source-050-amendment.md (Amendment 50 registry)
M  project-control/directives/D-024-fable-codex-loop/manifest.json           (registry)
M  project-control/directives/D-024-fable-codex-loop/requirements.json        (registry)
A  project-control/gates/M0-T107-G2.json                                     (M0-T107 gate)
M  project-control/gates/M0-T107-G0.json                                     (M0-T107 gate)
A  project-control/reports/M0-T107-G0.md                                     (M0-T107 report)
A  project-control/reports/M0-T107-evidence-map.json                         (M0-T107 report)
A  project-control/reports/M0-T107-portability-plan.md                       (deliverable)
A  project-control/reports/M0-T107.json                                      (M0-T107 report)
M  project-control/state.json                                               (control plane)
M  project-control/tasks/M0-T107.json                                        (M0-T107 task)
```
Explicit negative check for production/tooling paths over the same range returns empty:
```
git diff --name-only 99165bc2 c50fab0e -- tools/ apps/ services/ packages/ supabase/ .claude/ scripts/ model_selection
  -> (empty)
```
No changes under `tools/`, `apps/`, `services/`, `packages/`, `supabase/`, `.claude/` (incl. hooks), `scripts/`, or `model_selection`, and no other production source. Note: `project-control/gates/M0-T107-G0.json` and `-G2.json` — which the packet said "may not exist yet" — now exist as G0/G2 PASS records; both are within the allowed `project-control/gates/M0-T107-*` set.

### 3. Registry integrity (validator) — PASS
The validator tool `tools/validate_directive_compliance.py` is byte-identical between my worktree and the candidate (`git diff --stat d8b3899f 93a7157f -- <tool>` empty). Because my isolated worktree HEAD (d8b3899f) is not the candidate state, I reproduced the check faithfully against a read-only full-tree export of the candidate at `93a7157f` (scratchpad only; nothing written to the repo), so the script's `ROOT` resolves to the candidate content with all M0-T107 evidence present:
```
python <snapshot>/tools/validate_directive_compliance.py --check   -> exit 0
python <snapshot>/tools/validate_directive_compliance.py           ->
  directive registry OK: 29 directive(s), 29 active; source hashes, ID append-only,
  and producer/verifier separation verified.  (exit 0)
```
The git-independent c8 evidence-path-existence check ran fully faithfully (all referenced files present in the snapshot). c17's empty-identity *git*-arm self-skips on a non-git export by design ("when this checkout is not a git work tree the empty-resolution arm is skipped; … the project_control.py guard remains the fail-closed backstop"); that concern is independently covered by the footprint proofs in check 2 (allowed_paths resolve to real tracked files). The D-024 registry (`requirements.json`, `manifest.json`, `source-050-amendment.md`) is byte-identical between the validated SHA `93a7157f` and the current tip `c50fab0e` (`git diff 93a7157f c50fab0e -- <registry> = empty`), so the exit-0 result holds for the live tip.
- Advisory (not blocking): for a belt-and-suspenders authoritative record, the orchestrator may run the canonical `python tools/validate_directive_compliance.py --check` in the real ctl24 git checkout at the tip (which additionally exercises the c17 git-arm and CLI identity path); exit 0 is expected.

### 4. Worker-tree state — PASS
```
git rev-parse task/M0-T107-plugin-portability          -> 777ef5e4...   (matches)
git config branch.task/....remote                      -> (unset)
git config branch.task/....merge                       -> (unset)
git rev-parse --abbrev-ref task/M0-T107...@{upstream}  -> fatal: no upstream configured
git -C wt-m0t107 status --porcelain                    -> (empty) => clean working tree
```
`wt-m0t107` is clean at `777ef5e4` on branch `task/M0-T107-plugin-portability` with no upstream configured. `777ef5e4` is the bounded-correction-pass tip (Amendment 50).

### 5. Live-system side effects — PASS
Listing `%LOCALAPPDATA%\NYCBuildabilitySupervisor\9aca7075…f713b6a\mrl\` (times, newest last):
```
14:24  canary-b5-01
14:25  canary-b5-02
16:15  canary-b5-02r1
18:36  canary-b5-02r2
20:46  canary-b5-02r3
22:50  journey-m0t107-01   <-- newest
```
`journey-m0t107-01` (mtime 2026-09-02 22:50:34) is the newest run directory; no run directory newer than it exists. The adoption/continuation/gate-prep work created no new supervised run.

### 6. Regression posture — PASS
The change adds no code, no tests, no schema, and no dependency. The 9 files changed in the wave (12 including the parallel gate records) are 4 markdown + 5 JSON control-plane records; both deliverables are prose planning docs (headers: "Status: PLAN ONLY", "This document authorizes nothing", 253 and 158 lines). Targeted negative check finds no test/schema/dependency/lockfile/migration files:
```
git diff --name-only 99165bc2 c50fab0e -- '**/package.json' '**/package-lock.json' \
  '**/requirements*.txt' '**/pyproject.toml' 'supabase/migrations/**' \
  '**/*.test.*' '**/*.spec.*' 'tests/**' '**/test_*.py'   -> (empty)
```
No test suite is affected (docs-only change). The CI-relevant control-plane validator is green (check 3, exit 0). No modularity boundary answers apply (no handwritten production source changed).

## Findings
None. No defects, no out-of-scope edits, no regressions.

## Reviewer independence / constraints
Read-only throughout: only `git log/show/diff/status/rev-parse/ls-tree/merge-base`, directory listing, and a read-only validator run against a scratchpad export were used. No `tools/project_control.py` state changes, no `git add/commit`, no `gh`, no writes to the repository. The branch advanced from `93a7157f` to `c50fab0e` during the review; both new commits are M0-T107 gate/control-plane records confirmed within the allowed footprint, and the deliverables and directive registry are byte-identical across that advance.

VERDICT: PASS — ctl24 HEAD reviewed: c50fab0e (frozen M0-T107 submit identity 93a7157f, adoption identity 96f1b89b; task-branch tip 777ef5e4)
