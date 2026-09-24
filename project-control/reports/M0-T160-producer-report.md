# M0-T160 — producer report (backend-engineer)

Re-pin of the controller install source to the M0-T159-recertified candidate
`a3f24ff3825c126c038f59b1ea6d2352f29d724a` (accepted 275th), delivered as ONE reviewed
3-file lockstep (re-scoped 2026-09-24 per DB-063). Producer subagent in isolation worktree
`wt-m0t160` (`C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t160`, branch
`task/M0-T160-source-binding-repin`). All git commands were issued as
`git -C C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t160 ...` and therefore target the
wt-m0t160 worktree; the wt-m0t160 root is the effective cwd for every recorded command.

NO MACHINE CHANGE: no supervisor/controller verb, no `update_controller_from_candidate.ps1`
in any mode, no touch of `C:\SupervisorController*` / `C:\SupervisorBackup` /
`C:\Program Files\SupervisorConfig` / `%LOCALAPPDATA%\NYCBuildabilitySupervisor` /
`wt-controller-src`. Read-only git plumbing, `grep`, `python`, and file edits of the three
allowed paths only. The PowerShell contract suite is not runnable in this sandbox (AS-3
[BLOCKED], harvest recipe below).

Evidence-status legend: [OBSERVED] I ran it and quote the output; [BLOCKED] I could not run
it (denial recorded + harvest recipe).

## Deliverables (both commits)

- `tools/controller_update/source_binding.json` — three identity fields re-pinned + one
  authority sentence appended. Committed in round 1 (re-applied on the claim seam as part of
  HEAD `4e40eefa`). NOT re-edited this round; re-verified only.
- `docs/CONTROLLER_UPDATE_RUNBOOK.md` — section 4 pin paragraph names `a3f24ff3` with M0-T159
  provenance (round 2).
- `tools/controller_update/ps_tests/test_runbook_parse.ps1` — `$pinnedSha` = the full
  `a3f24ff3` SHA + one adjacent comment (round 2).
- `project-control/reports/M0-T160-producer-report.md` — this file.

## Guardrail evidence (worktree identity)

- `git rev-parse --show-toplevel` → `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t160`
  [OBSERVED]. Not the primary checkout.
- `git rev-parse HEAD` → `4e40eefa811747c6dcdc5e226bba001827f92d23` [OBSERVED] = claim-seam
  `83f86ce0` + the re-applied round-1 binding commit. Not reset.

## Round 1 (binding) — re-verified this round

The binding was re-pinned in round 1 and lives in HEAD `4e40eefa`. I did not touch it; I
re-verified its identity values with git plumbing (cwd wt-m0t160) [OBSERVED]:

| Value | Command | Output |
|---|---|---|
| commit_sha | `git rev-parse a3f24ff3^{commit}` | `a3f24ff3825c126c038f59b1ea6d2352f29d724a` |
| commit_tree_sha | `git rev-parse a3f24ff3^{tree}` | `82432361540c3c2a11c55ffa3d6d485426cd45f7` |
| subtree_tree_sha | `git rev-parse a3f24ff3:tools/agent_supervisor` | `9c0b14eaa56ce32d241c77f789266035b584380c` |

On-disk binding values (`grep -n commit_sha|commit_tree_sha|subtree_tree_sha source_binding.json`)
match all three [OBSERVED]. `subtree_path` unchanged (`tools/agent_supervisor`); schema stays
`controller_update_source_binding/v2`.

`git diff 83f86ce0 4e40eefa -- tools/controller_update/source_binding.json` shows EXACTLY the
three identity values plus ONE appended authority sentence [OBSERVED]:
```
-  "commit_sha": "a5886dab9ad94629a4984199d0766b16dd49e85b",
+  "commit_sha": "a3f24ff3825c126c038f59b1ea6d2352f29d724a",
-  "commit_tree_sha": "65036d3f51cd46dc47e1c359a8dacb486b03eaf1",
+  "commit_tree_sha": "82432361540c3c2a11c55ffa3d6d485426cd45f7",
-  "subtree_tree_sha": "850841ab4d4c2b90ef5f889fd74e461db33fa306",
+  "subtree_tree_sha": "9c0b14eaa56ce32d241c77f789266035b584380c",
```
Authority gains: `; re-pinned by D-024-R287 (Claude Code 2.1.281 admission; task M0-T160):
recertified candidate a3f24ff3 (M0-T159 accepted 275th; recertification report
project-control/reports/M0-T159-recertification.md records 3662 passed / 2 skipped / 0
failed on the certified tree), superseding a5886dab as the install source`.

All 12 `required_modules` exist at `a3f24ff3` — `git cat-file -e a3f24ff3:<path>` returned 0
(exists) for every one [OBSERVED]: `mrl_runtime_identity.py`, `mrl_subagent_contract.py`,
`mrl_provider_schema.py`, `mrl_one_shot.py`, `mrl_launch_draft.py`, `mrl_launch_manifest.py`,
`mrl_launch_path.py`, `command_docs.py`, `launch_seam.py`, `cli.py`, `manifest.py`,
`ps_tests/run_ps_tests.ps1`.

## Round 2 (the two lockstep edits)

`git diff 4e40eefa -- docs/CONTROLLER_UPDATE_RUNBOOK.md tools/controller_update/ps_tests/test_runbook_parse.ps1`
[OBSERVED] — only the intended hunks:

Runbook section 4, pin sentence only (4 old lines → 6 new lines; "The installer …" and every
fenced block untouched):
```
-The copy source is pinned to the immutable accepted production candidate commit
-`3f4cee8680ba5c9a167327507af387d316f5dbc3` (M0-T143 Codex --output-schema strict-subset
-repair + reviewer failure observability; D-024 Amendment 46, superseding the
-M0-T142/M0-T141/M0-T136 candidates) by the checked-in binding contract `...source_binding.json`. The installer
+The copy source is pinned to the immutable recertified production candidate commit
+`a3f24ff3825c126c038f59b1ea6d2352f29d724a` (M0-T159 recertification: the D-024-R287
+admission of Claude Code 2.1.281, accepted 275th, report
+`project-control/reports/M0-T159-recertification.md`; re-pinned by task M0-T160,
+superseding a5886dab (M0-T148), e0dd4a3a (M0-T146) and 3f4cee86 (M0-T143) as the
+install source) by the checked-in binding contract `...source_binding.json`. The installer
```

Test file, `$pinnedSha` line + one comment:
```
-$pinnedSha = '3f4cee8680ba5c9a167327507af387d316f5dbc3'
+# M0-T160 (D-024-R287): re-pinned to the M0-T159-recertified candidate a3f24ff3.
+$pinnedSha = 'a3f24ff3825c126c038f59b1ea6d2352f29d724a'
```

Line endings: both files are stored LF (blob), checkout smudges to CRLF on disk
(`core.autocrlf=true` [OBSERVED]); the committed blob stays LF. Blob-level
`git diff --stat 83f86ce0 -- <both files>` = `runbook 10 (+6/-4)`, `test 3 (+2/-1)` — only
the pin paragraph and the pinnedSha line move [OBSERVED].

### Static self-checks (no PowerShell)

A scratch Python check (LF-normalized to blob equivalence) [OBSERVED]:
- 3-WAY EQUALITY OK: `binding.commit_sha == test.$pinnedSha == runbook section-4 40-hex ==
  a3f24ff3825c126c038f59b1ea6d2352f29d724a`.
- SECTION-4 '<' CHECK OK: no `<` anywhere in section 4 (prose or fenced blocks).
- FENCED POWERSHELL BLOCKS OK: all 14 fenced ```powershell blocks byte-identical to
  `83f86ce0`'s runbook.
- Result line: `RESULT: ALL STATIC CHECKS PASS`.

## Per-acceptance-scenario evidence

### AS-1 (identity) — [OBSERVED], PASS
commit_sha / commit_tree_sha / subtree_tree_sha equal the git-plumbing values of `a3f24ff3`
(table above). `a3f24ff3` is on origin (round-1 `git branch -a --contains` →
`remotes/origin/task/M0-T159-cli-2-1-281-admission`). Every `required_modules` path exists at
`a3f24ff3` (12/12 `cat-file -e`). The runbook section 4 and the test's `$pinnedSha` both carry
the same full 40-hex SHA as the binding (3-way equality check).

### AS-2 (nothing else moved) — [OBSERVED], PASS
- source_binding.json: only the three identity values + one appended authority sentence;
  schema `controller_update_source_binding/v2`; every transaction key byte-identical (round-1
  diff above).
- CONTROLLER_UPDATE_RUNBOOK.md: only the section-4 pin paragraph; all 14 fenced blocks
  byte-identical to `83f86ce0`.
- test_runbook_parse.ps1: only the `$pinnedSha` line + one adjacent comment line.

### AS-3 (contract tests) — [BLOCKED] to run
This sandbox cannot run `powershell.exe` on the suite (the fixtures run git in `%TEMP%`; a
worktree-isolated agent's git operations must stay in-worktree, which the driver cannot be
statically proven to do). Per the packet HARNESS input this is expected; recorded [BLOCKED].
Static analysis: at the pre-rescope head `test_runbook_parse.ps1` was RED (binding.commit_sha
`≠` the hardcoded `3f4cee86`; DB-063, orchestrator-observed "1 assertion failure(s)"). This
lockstep makes the binding, the runbook section-4 SHA, and `$pinnedSha` name the same
`a3f24ff3`, so lines 86–87 assertions now hold — the lockstep is load-bearing (GREEN
expected after harvest).

HARVEST RECIPE (orchestrator, non-isolated session, cwd
`C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t160`, git + python on PATH):
`powershell -NoProfile -ExecutionPolicy Bypass -File tools/controller_update/ps_tests/run_ps_tests.ps1`
Expect every test file GREEN, including `test_runbook_parse.ps1` (RED→GREEN) and
`test_source_binding.ps1` (its tree_mismatch/subtree_mismatch cases run on throwaway fixture
bindings, never the live controller).

### AS-4 (no machine change + scope) — [OBSERVED], PASS
No supervisor/controller verb or installer was run; no read/write of any controller, backup,
config, or runtime directory. `git status --short` shows only ` M docs/CONTROLLER_UPDATE_RUNBOOK.md`
and ` M tools/controller_update/ps_tests/test_runbook_parse.ps1` (the report is untracked until
commit; the binding is already committed in HEAD). Across both producer commits exactly the
four allowed paths change; no forbidden path touched.

## DISCOVERIES (out of scope — not fixed)

1. `test_runbook_parse.ps1` hardcodes `$pinnedSha` and requires this manual 3-file lockstep on
   every re-pin (this is the third stale-pin drift: M0-T146/M0-T148 moved the binding without
   the runbook/test following — DB-063). Consider having the test READ the pinned SHA from
   `source_binding.json` (single source of truth) and assert only that the runbook contains it,
   so a future binding re-pin cannot leave the test/runbook stale.
2. The `tools/controller_update/ps_tests/` suite is not run by CI (DB-063: RED latently for two
   re-pins before anyone noticed). Consider adding it to CI so pin-drift fails a check.

END-OF-REPORT
