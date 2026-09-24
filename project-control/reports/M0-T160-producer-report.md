# M0-T160 — producer report (backend-engineer)

Re-pin of the controller install source `tools/controller_update/source_binding.json`
from the certified `a5886dab` to the recertified candidate `a3f24ff3` (M0-T159 accepted
275th). Producer subagent in isolation worktree `wt-m0t160`
(`C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t160`, branch
`task/M0-T160-source-binding-repin`), reset to the claim-seam commit `2e0b2351` before any
work. NO machine change: no supervisor/controller verb, no installer run against real
paths, no touch of `C:\SupervisorController*` / `C:\SupervisorBackup` /
`C:\Program Files\SupervisorConfig` / `%LOCALAPPDATA%\NYCBuildabilitySupervisor` /
`wt-controller-src`. Read-only git plumbing only; the PowerShell contract suite could not be
run (mechanical sandbox denial — see AS-3).

Evidence-status legend: [OBSERVED] I ran it and quote the output; [BLOCKED] I could not run
it (denial recorded + harvest recipe); [PREDICTED] deterministic static inference, not run.

## Deliverables

- `tools/controller_update/source_binding.json` — three identity fields re-pinned + one
  authority sentence appended (diff below).
- `project-control/reports/M0-T160-producer-report.md` — this file.

## Guardrail evidence (worktree identity)

Command (cwd `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t160`):
`git rev-parse --show-toplevel` → `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t160` [OBSERVED].
`git reset --hard 2e0b2351` → `HEAD is now at 2e0b2351 M5-T096/T097/T098 + M0-T160: G0 PASS
at the contract seam 64fce622, claimed (full worktree paths), progress 20` [OBSERVED].

## AS-1 (identity) — [OBSERVED], PASS

All commands cwd `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t160` (worktree shares the primary
object store, so every sha resolves):

| Check | Command | Output | Expected | Verdict |
|---|---|---|---|---|
| commit | `git rev-parse a3f24ff3^{commit}` | `a3f24ff3825c126c038f59b1ea6d2352f29d724a` | same | OK |
| commit tree | `git rev-parse a3f24ff3^{tree}` | `82432361540c3c2a11c55ffa3d6d485426cd45f7` | same | OK |
| subtree | `git rev-parse a3f24ff3:tools/agent_supervisor` | `9c0b14eaa56ce32d241c77f789266035b584380c` | same | OK |
| parent | `git rev-parse a3f24ff3^` | `a5886dab9ad94629a4984199d0766b16dd49e85b` | a5886dab | OK |
| on origin | `git branch -a --contains a3f24ff3` | `task/M0-T159-cli-2-1-281-admission` + `remotes/origin/task/M0-T159-cli-2-1-281-admission` | on origin | OK |
| file count | `git ls-tree -r --name-only a3f24ff3 -- tools/agent_supervisor | wc -l` | `204` | 204 | OK |
| diff scope | `git diff --stat a5886dab a3f24ff3` | 12 files, only M0-T159 paths (see below) | only M0-T159 | OK |

`git diff --stat a5886dab a3f24ff3` (verbatim, 12 files / +673 −45):
```
 project-control/reports/M0-T159-producer-report.md |  97 ++++++++++++++
 project-control/reports/M0-T159-recertification.md | 110 ++++++++++++++++
 project-control/reports/M0-T159-routing-capture.py |  99 +++++++++++++++
 tools/agent_supervisor/event_drift.py              |  18 +--
 ...ility_probe_live_2026-09-24_m0t159_2_1_281.json |  85 +++++++++++++
 .../fixtures/hook_event_catalog_2_1_281.json       |  66 ++++++++++
 ...native_runtime_detection_2026-09-24_m0t159.json |  25 ++++
 .../shell_routing_2026-09-24_m0t159_2_1_281.json   | 141 +++++++++++++++++++++
 tools/test_agent_supervisor_capability_probe.py    |  27 ++--
 tools/test_agent_supervisor_event_bus.py           |  18 +--
 tools/test_agent_supervisor_native_adapter.py      |  13 +-
 tools/test_agent_supervisor_routing_probe.py       |  19 +--
 12 files changed, 673 insertions(+), 45 deletions(-)
```
This matches recertification report section 1 / 5.0 exactly (event_drift.py re-point + four
2.1.281 fixtures + four re-pointed test packs + three M0-T159 reports). The uncertified
integrated ledger commit `cfc3d22c` is NOT the install source (recert 5.0); the binding pins
the material candidate `a3f24ff3`.

All 12 `required_modules` exist at `a3f24ff3` (each `grep -qxF` against the candidate's file
list) [OBSERVED]:
`mrl_runtime_identity.py`, `mrl_subagent_contract.py`, `mrl_provider_schema.py`,
`mrl_one_shot.py`, `mrl_launch_draft.py`, `mrl_launch_manifest.py`, `mrl_launch_path.py`,
`command_docs.py`, `launch_seam.py`, `cli.py`, `manifest.py`, `ps_tests/run_ps_tests.ps1` —
all `OK`.

## AS-2 (nothing else moved) — [OBSERVED], PASS

Edited only `commit_sha`, `commit_tree_sha`, `subtree_tree_sha`, and appended one clause to
`authority`. `git diff -- tools/controller_update/source_binding.json` (cwd worktree root)
shows exactly:
```
-  "commit_sha": "a5886dab9ad94629a4984199d0766b16dd49e85b",
-  "commit_tree_sha": "65036d3f51cd46dc47e1c359a8dacb486b03eaf1",
+  "commit_sha": "a3f24ff3825c126c038f59b1ea6d2352f29d724a",
+  "commit_tree_sha": "82432361540c3c2a11c55ffa3d6d485426cd45f7",
-  "subtree_tree_sha": "850841ab4d4c2b90ef5f889fd74e461db33fa306",
+  "subtree_tree_sha": "9c0b14eaa56ce32d241c77f789266035b584380c",
```
plus the authority line gaining the trailing clause:
`; re-pinned by D-024-R287 (Claude Code 2.1.281 admission; task M0-T160): recertified
candidate a3f24ff3 (M0-T159 accepted 275th; recertification report
project-control/reports/M0-T159-recertification.md records 3662 passed / 2 skipped / 0
failed on the certified tree), superseding a5886dab as the install source`.

Post-edit validation [OBSERVED]:
- `python -c json.load(...)` parses; `schema` = `controller_update_source_binding/v2`
  (unchanged); key order unchanged (18 keys, same sequence); `subtree_path` unchanged
  (`tools/agent_supervisor`); `required_modules` count 12 (unchanged).
- `grep -c $'\r'` = `0` → file stays LF-only (git `text`/`eol` unspecified, no CR before or
  after the edit; formatting/2-space indent preserved).
- Every transaction key (`source_repo`, `expected_origin_url`, `source_worktree`,
  `destination`, `controller_root`, `backup_root`, `a1_runtime_dir`, `backup_evidence`,
  `rollback_evidence`, `controller_manifest`, `evidence_out`) byte-identical.

## AS-3 (contract tests) — [BLOCKED] to run + [PREDICTED] pre-existing red; negative probe [BLOCKED]

### 3a. Suite run — [BLOCKED] (mechanical sandbox denial)

Documented command:
`powershell -NoProfile -ExecutionPolicy Bypass -File tools/controller_update/ps_tests/run_ps_tests.ps1`
(cwd `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t160`).

I read every test file first and confirmed each uses ONLY `$env:TEMP` throwaway git repos
and temp destinations (`New-FixtureWork` → `$env:TEMP\ctl24-srcbind-<guid>`; destinations,
junctions, backup roots, runtime dirs all under `$work`; `test_null_exit.ps1` only edits
`$env:PATH` in-process; `test_mutants_detected.ps1` copies the real script to `$work` mutants).
No test touches any real controller/backup/config/runtime path — they are safe to run.

The sandbox refused every `powershell` invocation of the driver, verbatim (both a plain form
and a `tee`/`PIPESTATUS` form):
> This agent is isolated in the worktree ...\agent-a8d5df3d649a80f97, but this command runs
> powershell in a plain command; what it reads or is handed as shell text cannot be shown not
> to run git. Refusing to run it — a worktree-isolated agent's git operations must target its
> own worktree.

Reason: the contract fixtures internally run `git init` / `git commit` on temp repos, and the
isolation guard cannot statically prove the script stays in-worktree, so it blocks all
`powershell -File` of this driver. Not retried further.

HARVEST RECIPE (orchestrator, from a non-isolated session, cwd
`C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t160`, git + python on PATH):
`powershell -NoProfile -ExecutionPolicy Bypass -File tools/controller_update/ps_tests/run_ps_tests.ps1`

### 3b. [PREDICTED] the suite is RED at `test_runbook_parse.ps1` — a pre-existing cross-file staleness, NOT introduced by this task

This is the load-bearing finding of this task. `test_runbook_parse.ps1` is the only contract
test that reads the REAL `source_binding.json` and the REAL runbook; the other six build
fixture bindings and are independent of the live pin (they pass/fail on git+python
availability alone). `test_runbook_parse.ps1` (read at `2e0b2351`) hardcodes and asserts:
- line 26: `$pinnedSha = '3f4cee8680ba5c9a167327507af387d316f5dbc3'`
- line 86: `Assert-True ($binding.commit_sha -eq $pinnedSha) 'binding contract pins the immutable accepted SHA'`
- line 87: `Assert-True ($runbookText.Contains($pinnedSha)) 'runbook section 4 states the same immutable SHA'`

Observed facts [OBSERVED]:
- `grep -c 3f4cee86… docs/CONTROLLER_UPDATE_RUNBOOK.md` = `1` (line 84, inside Section 4:
  "The copy source is pinned to the immutable accepted production candidate commit
  `3f4cee86…`"). `grep -c a5886dab…` = `0`; `grep -c a3f24ff3…` = `0`.
- `source_binding.json.commit_sha` was `a5886dab` before this task and is `a3f24ff3` after —
  neither equals `3f4cee86`.

Therefore line 86 (`a3f24ff3 -eq 3f4cee86`) is FALSE → `ASSERT-FAIL` → `test_runbook_parse.ps1`
exits 1 → the fail-fast driver (`run_ps_tests.ps1`, alphabetical order; `test_runbook_parse.ps1`
is the 6th of 7, before `test_source_binding.ps1`) stops with that non-zero code. This was
ALREADY the state before M0-T160 (`a5886dab -ne 3f4cee86`): the runbook Section 4 and the
test's `$pinnedSha` were never re-pinned across the `e0dd4a3a` (Amendment 54 / M0-T146) and
`a5886dab` (D-032 Amendment 3 / M0-T148) binding re-pins. The suite has been red at this test
since those re-pins; M0-T160 re-pinning only the binding cannot cure it.

CONSEQUENCE FOR AS-3: "the offline PowerShell contract suite ... passes" is UNSATISFIABLE
within M0-T160's allowed scope. To make `test_runbook_parse.ps1` green, three files must name
the SAME sha (`a3f24ff3`): the binding (done here), `docs/CONTROLLER_UPDATE_RUNBOOK.md`
Section 4 line 84, and `tools/controller_update/ps_tests/test_runbook_parse.ps1` `$pinnedSha`
(line 26). The latter two are in M0-T160 `forbidden_paths` — I did not and must not touch
them. This is a scope gap for the orchestrator (see "Requested status").

### 3c. Negative probe (wrong tree sha refused) — [BLOCKED]

Marked [BLOCKED] per the packet's own condition ("Do this only if you can call that
validation without any install action; otherwise ... mark it [BLOCKED]"):
1. The sandbox blocks all `powershell` (3a), so I cannot run `update_controller_from_candidate.ps1`
   against even a scratch copy.
2. The installer exposes no install-free "validate binding only" phase — the `tree_mismatch` /
   `subtree_mismatch` refusals only fire inside `-Phase install`, which the NO-MACHINE-CHANGE
   rule forbids running (even the fixture form is a `-Phase install` invocation).

Standing committed coverage for exactly this negative behavior already exists and needs no new
scratch artifact — `test_source_binding.ps1` (read at `2e0b2351`):
- case b (lines 76-79): `commit_sha=shaC, commit_tree_sha=treeB` → `REFUSED tree_mismatch`,
  nothing installed;
- case d (lines 82-84): wrong `subtree_tree_sha` → `REFUSED subtree_mismatch`;
and `test_mutants_detected.ps1` `m_tree` proves the tree check is load-bearing (disabling it
lets the wrong commit install). These run against fixture repos in the same [BLOCKED] driver;
harvest them via the 3a recipe.

## AS-4 (no machine change + scope) — [OBSERVED], PASS

- No supervisor/controller verb, no `update_controller_from_candidate.ps1`, no `doctor`/`launch`/
  `start`/`repin-cli-identity` was run (all `powershell` was refused by the sandbox before any
  ran; nothing was attempted against real controller paths). No read or write of
  `C:\SupervisorController*`, `C:\SupervisorBackup`, `C:\Program Files\SupervisorConfig`,
  `%LOCALAPPDATA%\NYCBuildabilitySupervisor`, or `wt-controller-src`.
- Only commands run: read-only git plumbing (`rev-parse`, `ls-tree`, `diff`, `branch
  --contains`, `check-attr`, `status`), `grep`, `python -c json.load`, and file reads/edits of
  the two allowed paths.
- `git status --short` = ` M tools/controller_update/source_binding.json` (report is new/
  untracked until commit); exactly the two allowed paths change. No forbidden path touched.

## Requested status

Requested: **needs_split** (binding edit itself is complete and gate-ready).

- AS-1, AS-2, AS-4 fully [OBSERVED] and PASS; the binding is correctly re-pinned to `a3f24ff3`
  with byte-exact formatting.
- AS-3 cannot be satisfied within scope: (i) the contract suite is [BLOCKED] to run here by a
  mechanical sandbox denial (harvest recipe provided); (ii) even when run, it is [PREDICTED] to
  fail at `test_runbook_parse.ps1` because of a PRE-EXISTING cross-file staleness (runbook
  Section 4 + the test's `$pinnedSha` still name the Amendment-46 `3f4cee86`, never re-pinned
  across the two later re-pins), and curing it requires editing two `forbidden_paths`.

Recommendation for the orchestrator: either expand M0-T160's scope to also re-pin
`docs/CONTROLLER_UPDATE_RUNBOOK.md` Section 4 (line 84) and
`tools/controller_update/ps_tests/test_runbook_parse.ps1` `$pinnedSha` (line 26) to
`a3f24ff3` in the same reviewed commit, OR contract a tightly-coupled companion task for those
two files, so the offline suite (AS-3) can go green. The binding-only change delivered here is
correct and can be accepted/gated independently if AS-3 is re-scoped accordingly.

END-OF-REPORT
