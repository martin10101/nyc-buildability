# Session Handoff - NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live -
`python tools/project_control.py status` and `python -m tools.agent_supervisor.campaign_continuity
--status` - and reconcile against the remote: **origin may have advanced; do not trust any SHA here
as still-current.** Orientation only; rules/gates live in `CLAUDE.md`. CURRENT-ONLY:
`context-budget` CI fails > ~4000 tok.

## Handoff - seq 71: M0-T136 Tranche B (Amendment 40) mid-C-B5; B0-B4 + C-B5 part 1 committed locally

1. **Generated:** 2026-09-01 by the Tranche-B producer/integrator session `ctl24-94 [71712a]`
   (session_01Bc5Kqa74kPZ4h6nJaXM63k), owner-invoked `/session-handoff` (no argument) after "stop"
   and "Explain why you keep compacting" (context-compaction turnover). NOTE: D-024-R595 says
   regenerate this file only at the final frozen B candidate; this regeneration is owner-invoked
   mid-tranche, the frozen-candidate regeneration is still owed.
2. **Identity (live at generation):** root/worktree `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`, branch
   `candidate/D-024-mrl-option-b` (LOCAL ONLY - `git ls-remote` shows no such remote head), HEAD
   `d39c49bb` (chain: 895cfbe5 B0 freeze -> 2bcd9aa8 survey -> 0e37e115 B1 -> 9c8be98d B2 -> 0e0c4bcc
   + 5319c50a B3 -> 4bf845cd B4 -> a57802cc/472ae045 packet scope -> d39c49bb C-B5 part 1). Origin
   `https://github.com/martin10101/nyc-buildability.git`; `control/D-024-fable-codex-loop` = 6f5d12a6
   (base, untouched). Nothing pushed (R520). PR #241 untouched.
3. **Dirty files (uncommitted, leave as-is):** `tools/agent_supervisor/command_docs.py` (M) and
   `tools/test_agent_supervisor_command_docs.py` (M, rewritten). Uncommitted because the test module
   runs 6 failed / 38 passed: five `LivingRunbookTests` need files not yet written
   (`docs/MRL_LAUNCH_RUNBOOK.md`, obsoleted CONTROLLER_UPDATE_RUNBOOK s11,
   `project-control/reports/M0-T136-canary-package.md`) and ONE real mismatch:
   `ManifestFormWithRealFileTests::test_unfilled_base_ref_is_refused` expects verdict code
   `launch_manifest_base_ref_missing` but `command_docs.py` returns `launch_manifest_invalid` - decide
   whether the tooth must surface the loader's specific code or the test expectation is wrong.
4. **Ledger/lease:** M0-T136 `claimed` (campaign D-024 seq 71, directive_refs D-024:ALL, worktree ctl24);
   M0-T137 (model-selection addendum R599-R606) backlog until owner decides R603/R604/R605; M0-T133
   REWORK/unaccepted (R480); M0-T135 backlog. Packet allowed/forbidden paths: see
   `project-control/tasks/M0-T136.json` (edited only in orchestrator capacity).
5. **Objective:** D-024 Amendment 40 (`source-040-amendment.md`, R515-R606): ONE bounded Tranche-B
   workflow B0-B5, local commits only, then freeze one candidate SHA, run the complete affected +
   repository verification once via `tools/gate_runner.py`, finish with exactly
   `TRANCHE_B_OFFLINE_COMPLETE_CANARIES_READY` or `CONSOLIDATED_BLOCKED`, `/submit-checkpoint`
   (never self-accept).
6. **Completed with evidence:** B0-B4 (commits above; gate records in
   `project-control/reports/M0-T136-gates/`; survey in `M0-T136-failure-surface.md` draft commit
   2bcd9aa8). C-B5 part 1 (d39c49bb): `mrl_launch_draft.py` subagent-contract flags
   (`--tool/--allow-tool/--deny-tool/--agent/--max-concurrent/--max-total`; None keeps the default
   verbatim, a value replaces wholesale; refusals for empty names, bad limits, allow-rule outside the
   inventory, R574) + 28 tests; `mrl_one_shot.py` `permission_denials_of()` (cap 50) into unit record +
   settled audit detail, `launch_record.child_env_updater` measured from the exact Popen env + 60 tests.
7. **Validation at d39c49bb (exact):** `python -m pytest tools/test_agent_supervisor_mrl_launch_draft.py
   tools/test_agent_supervisor_mrl_one_shot.py -p no:cacheprovider -q` -> 88 passed, exit 0;
   `python -m pytest tools/test_agent_supervisor_command_docs.py -p no:cacheprovider -q` -> 6 failed /
   38 passed, exit 1 (item 3); `python tools/modularity_check.py --check` -> exit 0 (warn-only signals on
   pre-existing files); `python -m ruff check <6 dirty files>` -> exit 0. Whole suite NOT run (R592).
8. **C-B5 part 2 = exact next work (R585-R587, R589), design decided:**
   - `docs/MRL_LAUNCH_RUNBOOK.md` (new): concrete absolute paths only (no `<...>` - the doc-check tooth
     treats `<...>` as a template and skips validation). Step 1, from `C:\SupervisorController`:
     `python -m tools.agent_supervisor.mrl_launch_draft --worktree C:\Users\MLFLL\Downloads\nyc-zoning\ctl24
     --task-packet C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\tasks\M0-T136.json --mode
     supervised --claude-executable C:\Users\MLFLL\.local\bin\claude.exe --codex-executable
     C:\Users\MLFLL\AppData\Roaming\npm\codex.cmd --config "C:\Program Files\SupervisorConfig\config.toml"
     --model-selection C:\SupervisorController\model_selection.toml --controller-manifest
     C:\Users\MLFLL\AppData\Local\NYCBuildabilitySupervisor\ctl24-activation\controller_manifest.json
     --base-ref refs/heads/main --claude-runtime-model-from-selection --out
     C:\SupervisorController\mrl\launch_manifest.json --force`. Step 2, the ONE fenced start:
     `python -m tools.agent_supervisor start --mode supervised --checkout C:\SupervisorController
     --launch-manifest C:\SupervisorController\mrl\launch_manifest.json --max-cycles 1` (`--mode` must
     equal the manifest's mode; `--repin-cli-identity` remedy in prose only). Refusal table (exit 11:
     launch_manifest_invalid/_conflict/_single_task/_base_ref_missing/_mismatch/_unobservable,
     cwd_primary_checkout, cwd_mismatch, codex_model/version_mismatch, claude_version_mismatch; exit 13
     illegal_transition when parked at WAIT_FOR_OWNER; runtime-identity mismatch lands in
     `one_shot_unit.json`), exit-code table (0/1/2/3/10-16), WAIT_FOR_OWNER exit via
     `resume-pending-prompt --approve-prompt-digest` (CONTROLLER_UPDATE_RUNBOOK s9a) then a fresh start,
     run-dir lookup `python -c "from tools.agent_supervisor.durable_state import runtime_dir_for;
     print(runtime_dir_for(r'C:\SupervisorController'))"` + `\mrl\<run_id>\`, `doctor --live` as the only
     probe, how to run ps_tests.
   - `docs/CONTROLLER_UPDATE_RUNBOOK.md` s11 (lines ~221-256): remove the fenced legacy start; OBSOLETE
     banner pointing to `docs/MRL_LAUNCH_RUNBOOK.md`; rewrite the "five load-bearing flags"/`--manifest`
     prose to the manifest form. Test requires: no `start` command, contains "OBSOLETE" and the runbook path.
   - `tools/agent_supervisor/README.md`: pointer (placeholders allowed there).
   - `tools/agent_supervisor/ps_tests/`: harness `Invoke-RawExit -FilePath -ArgumentList` (`$global:LASTEXITCODE=$null`
     reset, unpiped `&`, stdout/stderr to files, null -> fail closed, JSON record); `run_ps_tests.ps1`
     iterating `test_*.ps1` via `powershell.exe -NoProfile -ExecutionPolicy Bypass -File`, ending
     `exit $LASTEXITCODE`; tests: raw 7 preserved from `python -c "import sys; sys.exit(7)"`;
     `mutants/`: `$?`/pipeline greens on 7, `-File` script ending `native | Tee-Object` without `exit` ->
     0, `cmd /c` pipe -> 1 (asserted as DETECTED); doc-check `--doc docs/MRL_LAUNCH_RUNBOOK.md` -> 0 and a
     mutated temp copy -> 1. Measured PS 5.1 facts: `& python` sets `$LASTEXITCODE`; `| Tee-Object` keeps
     the code but `$?` is False; CommandNotFoundException leaves `$LASTEXITCODE` unchanged.
   - `project-control/reports/M0-T136-canary-package.md`: ten R587 items verbatim, exact PowerShell, NOT
     executed; every `start` manifest-form + `--mode supervised` + distinct `--run-id canary-b5-NN` +
     `--max-cycles 1`; prerequisites = owner-typed controller update from the frozen candidate
     (CONTROLLER_UPDATE_RUNBOOK s3-s8), draft re-run AFTER the final commit. Evidence map: item 1 exit 0
     from a clean base; item 2 create an untracked file in ctl24 -> `clean_status` mismatch exit 11 ->
     delete it (run before the one-shot); items 3-9 all read from ONE supervised `--max-cycles 1` run
     (exit 0, `stopped_because` in operator_declined/ask_blocking/stage_complete/...):
     `one_shot_unit.json` session_id + no worker_failed (Claude auth), `codex_decision.json` (Codex auth),
     `observed_models`/`model_mismatch`/`launch.version` (identity), `launch.child_env_updater`
     (updater), `permission_denials` >= 1 (prompt asks for one Bash call; Bash in inventory, not allowed
     under dontAsk), `subagent_ledger.json` accounting `subagents_denied >= 1`, `subagents_issued <=
     max_total`, `processes_total <= 1+max_total` (draft with `--allow-tool Read --allow-tool Grep
     --allow-tool Glob --allow-tool Agent --agent Explore --max-concurrent 2 --max-total 2`, prompt asks
     for three sequential Explore subagents), `descendant_proof.proven`/`containment`/`tree_terminated`
     (cleanup); item 10 via the ps_tests harness (NEVER present `--no-such-flag` supervisor commands in a
     checked doc - the tooth fails them `parser_rejected`). Worker `--prompt` must contain no `<`/`>`.
   - Checks before the C-B5 commit: the 5-module pytest (command_docs, draft, one_shot, launch_manifest,
     launch_path), `python tools/supervisor_command_doc_check.py`, `--doc docs/MRL_LAUNCH_RUNBOOK.md`,
     `--doc project-control/reports/M0-T136-canary-package.md`, `powershell -NoProfile -ExecutionPolicy
     Bypass -File tools\agent_supervisor\ps_tests\run_ps_tests.ps1`, modularity, ruff. Commit citing
     `D-024-R585, R586, R587, R589` via `git commit -q -F <scratchpad msg>` (stdin is null in PS).
9. **Then (final):** freeze candidate SHA; ONE complete affected + repository verification (R593) via
   `tools/gate_runner.py` into `M0-T136-gates/` (positive + paired mutation records, R590/R591);
   `M0-T136-failure-surface.md`, `-tranche-b-evidence.json`, `-G2-self-check.md`, `-producer-report.md`;
   regenerate this file (R595); report all R597 items + every blocker together + one terminal token;
   `/submit-checkpoint`. Any later code change invalidates the final verification (R594).
10. **Rejected:** editing `tools/supervisor_command_doc_check.py`, `.claude/**`, `.github/workflows/**`
    (out of packet scope); an extra "empty --agent with Agent in inventory" refusal in the draft (removed
    as over-constraining); `Write` rewrites / whole-file reads (context growth - use range reads + `Edit`).
11. **Blockers/follow-ups to report together (none stop C-B5):** doc-check DEFAULT_DOCS lacks the MRL
    runbook (not editable here; CI covers it only via `--doc`); `.claude/skills/loop-start/SKILL.md` and
    `.claude/hooks/loop_command_interceptor.py:202` still reference the legacy launch shape; ps_tests
    not in CI (workflows forbidden); CONTROLLER_UPDATE_RUNBOOK s9/s10 still name `wt-m0t063`; amendment
    silent on the canary `--mode` (supervised chosen, state it); live CLI `--allowedTools`/dontAsk/
    `permission_denials` shapes are proven only by the owner-run canary (R579); R595-vs-handoff timing
    (item 1).
12. **Sub-agents:** none active or pending (no Agent spawns outstanding). Peer sessions offline.
13. **Standing restrictions:** R518 never run the rejected `git switch && git checkout` line; R520-R522
    no push/PR/merge/auto-accept/deploy/real loop/Tranche C; R523 no live canaries (present + stop);
    R524/R525 foreground in-scope subagents only, this session sole integrator, no subagent git; never
    merge PR #241; supervisor commits cite `D-024-R###`; no `name:` on producer spawns; no bare
    `git stash`; thin client; Bootstrap Gate 0 (cwd = ctl24, `/mcp` empty) before any write.
14. **Authoritative files:** `project-control/tasks/M0-T136.json`, `project-control/campaigns/*.json`,
    `project-control/directives/D-024-fable-codex-loop/source-040-amendment.md` + `requirements.json`,
    `project-control/reports/M0-T136-*`, git log of `candidate/D-024-mrl-option-b`.
15. **Stop conditions:** any push/remote/PR/merge need; a legal/credential/payment item; a contradiction
    between this file and the ledger (ledger wins); owner decision rows R603-R605 (never interpret).

## COPY INTO THE NEW SESSION

Resume M0-T136 (D-024 Amendment 40 Tranche B) from durable evidence only. First: confirm `git rev-parse
--show-toplevel` = `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`, branch `candidate/D-024-mrl-option-b`,
HEAD d39c49bb (or a later local commit), Bootstrap Gate 0 (cwd is that root, `/mcp` empty). Read
`CLAUDE.md`, `docs/SESSION_HANDOFF.md`, `project-control/tasks/M0-T136.json`, and
`project-control/directives/D-024-fable-codex-loop/source-040-amendment.md` lines 100-160. Run
`python tools/project_control.py status` and `python -m tools.agent_supervisor.campaign_continuity
--status`; the ledger wins over prose. Expect exactly two dirty files (`tools/agent_supervisor/command_docs.py`,
`tools/test_agent_supervisor_command_docs.py`) and 6 failing command_docs tests. Report `READY TO RESUME` or
`BLOCKED`. If ready, continue C-B5 part 2 exactly per handoff item 8 (runbook -> s11 obsoletion -> README
-> ps_tests -> canary package -> checks -> one local commit), resolve the `launch_manifest_base_ref_missing`
test/code mismatch, then item 9. Read line ranges, use `Edit`, delegate broad tracing to foreground
subagents. No push, PR, merge, live canary, Tranche C, or self-acceptance; stop for anything owner-only.
