# Session Handoff - NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live -
`python tools/project_control.py status` and `python -m tools.agent_supervisor.campaign_continuity
--status` - and reconcile against the remote: **origin may have advanced; do not trust any SHA here
as still-current.** Orientation only; rules/gates live in `CLAUDE.md`. CURRENT-ONLY:
`context-budget` CI fails > ~4000 tok.

## Handoff - seq 76: M0-T141 + M0-T142 ACCEPTED (Draft-7 schema hotfix + settlement identity/Bash restriction); Fable-switch canary script deployed; M0-T140 claimed awaiting the owner-typed run

1. **Generated:** 2026-09-03 by the Amendment 44/45 session (owner ran `/session-handoff`
   mid-close; the close COMPLETED first: reviews reconciled, task accepted, script deployed).
2. **Identity:** root/worktree `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`, branch
   `candidate/D-024-mrl-option-b` (LOCAL ONLY - no upstream). **Frozen corrected CODE candidate:
   `f8f0f0c89ff9c3f7762e144d5d37874b10f2b294`** (tree 23af20d5, subtree ffbde3b6) - supersedes
   2245de74/1489879e as the controller install source; `tools/agent_supervisor` at HEAD is
   byte-identical to it; binding + runbook s4 + ps_test pinnedSha all pin it. Working tree clean;
   nothing pushed; PR #241 untouched. Campaign-continuity record is STALE at seq 71 (rc 1
   fail-closed) - the ledger wins; do not trust its NEXT pointer.
3. **Accepted this session:** M0-T141 (Amendment 44 Draft-7 provider-schema hotfix; accept
   e79d7ccc) and M0-T142 (Amendment 45 settlement runtime-identity + explicit Bash restriction;
   accept a56a12c5 at reviewed head cfe56bba; G3+G4 gate PASS at f2e79cc5 + delta attestations
   PASS at 57dce1a5 + DCV 14/14 + RE-VERIFY PASS; dry-run zero reasons). M0-T142 fix: settlement
   proves the pinned model from the correlation-bound session transcript (modelUsage = aggregate;
   pin[1m] = same-family context tier; typed refusals incl. torn-multibyte); explicit
   neither-allowed-nor-denied tool refusal at profile + draft (default deny Edit/Write/Bash/Agent).
   Amendments 44 (R664-R683) + 45 (R684-R699) captured; validator exit 0. Suite at candidate:
   3593 passed / 2 skipped; mutants M1-M6 + N1-N6 all DETECTED; G4 proved the REAL preserved
   canary-b5-02r1 run now settles.
4. **Ledger:** M0-T140 (canary vehicle) stays **claimed** until the live canary finishes
   (R651/R674). M0-T137 backlog (owner-only R603-R605); M0-T133 rework; M0-T135 backlog.
5. **Owner-run continuation (R697/R699):** ONE deployed script
   `%LOCALAPPDATA%\NYCBuildabilitySupervisor\ctl24-activation\run_m0t142_fable_switch_and_canary.ps1`
   (SHA-256 e8c693ae77fdf16620000bc99c92dd77d40e0b24d0feec700b1b8403f93bd164; PS 5.1 parse 0
   errors; prior scripts renamed `.superseded-*`). Fail-fast: P0 preconditions (incl. stale
   wt-controller-src removal + REUSED b5-01 PASS row) -> backup -> install f8f0f0c8 ->
   record-manifest -> verify-manifest -> **PM canonical owner switch model_selection [claude]
   model -> exact `claude-fable-5`** (backup in activation dir; fallback stays []) -> normal
   doctor (which ALSO asserts its model_selection row reads claude-fable-5; the former
   python-import validation is removed - attempt-3 evidence M0-T140-canary-attempt3-pm-validation-refusal.md) -> conditional s9a clear-recovery -> draft (allow Read/Grep/Glob/Agent, BARE DENY Bash,
   runtime model from selection) -> exactly ONE one-shot `--run-id canary-b5-02r2` -> corrected
   rows (3: Claude auth vs Codex NOT_RUN split; 4: verified primary + `--model claude-fable-5`
   argv proof; 6: Bash absent+never executed; 8: unit accounting) -> harness -> ten-row table +
   token. Rollback (+ model-selection restore) ONLY on install/doctor failure; NEVER on a canary
   product defect (evidence preserved, stop).
6. **Next steps:** (a) owner types the one command (below); (b) after CANARY_PACKAGE_PASS: write
   `project-control/reports/M0-T140-canary-execution-evidence.md`, run M0-T140's independent
   gates, accept; on a FAIL row: preserve evidence, causal-trace first (owner stop-order pattern),
   no rollback, no reinstall loops; (c) push/PR/merge + Tranche C stay owner-gated (R520-R522);
   R603-R605 remain owner-only (the Fable switch in the script is the OWNER exercising them).
7. **Sub-agents at handoff:** all reconciled - G3/G4/DCV wave + delta attestations returned,
   preserved verbatim (`M0-T142-G3-code-review.md`, `-G4-qa-review.md`, `-DCV.md`), gates
   recorded. None running.
8. **Standing restrictions:** R518; R520-R525; never merge PR #241; supervisor commits cite
   `D-024-R###` + AD-093 evidence; no `name:` on producer spawns; no bare `git stash`; thin
   client; Bootstrap Gate 0 before any write; R683/R697 never execute the owner-run script;
   R699 exact `claude-fable-5` only (never the `fable` alias, never claude-fable-5-1, no CLI
   upgrade, fallback []).
9. **Authoritative files:** `project-control/tasks/M0-T142.json` (+ M0-T140/T141),
   `project-control/directives/D-024-fable-codex-loop/source-044-amendment.md` +
   `source-045-amendment.md`, `project-control/reports/M0-T142-*` + `M0-T141-*` +
   `M0-T140-canary-b502r1-causal-trace.md`, `tools/controller_update/source_binding.json`.
10. **Stop conditions:** any push/remote/PR/merge need; legal/credential/payment;
    ledger-vs-prose contradiction (ledger wins); a canary FAIL row (trace, never loop).

## COPY INTO THE NEW SESSION

Resume from durable evidence only. Confirm `git rev-parse --show-toplevel` =
`C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`, branch `candidate/D-024-mrl-option-b`, Bootstrap
Gate 0 (cwd is that root, `/mcp` empty). Read `CLAUDE.md`, this file,
`project-control/tasks/M0-T140.json`, and `project-control/reports/M0-T142-freeze.md`. Run
`python tools/project_control.py status`; the ledger wins (campaign record stale at seq 71).
M0-T141 + M0-T142 are ACCEPTED at frozen corrected candidate f8f0f0c8 (binding pins it).
M0-T140 stays claimed until the owner-typed canary finishes: the owner runs
`run_m0t142_fable_switch_and_canary.ps1` (ctl24-activation; sha e8c693ae...; installs f8f0f0c8,
switches model_selection to exact claude-fable-5, runs ONE canary-b5-02r2 one-shot). Do NOT
push, create/update/merge any PR, execute the owner script, rerun b5-01, change model_selection
yourself, or start Tranche C. After CANARY_PACKAGE_PASS: write M0-T140's canary-execution
evidence, run its independent gates, accept. On any FAIL row: preserve evidence, produce a
causal trace first. Stop for owner-only items (R603-R605 exercised only by the owner).
