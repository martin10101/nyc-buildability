# Session Handoff - NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live -
`python tools/project_control.py status` and `python -m tools.agent_supervisor.campaign_continuity
--status` - and reconcile against the remote: **origin may have advanced; do not trust any SHA here
as still-current.** Orientation only; rules/gates live in `CLAUDE.md`. CURRENT-ONLY:
`context-budget` CI fails > ~4000 tok.

## Handoff - seq 75: M0-T141 (Amendment 44 Draft-7 schema hotfix) ACCEPTED; corrected owner canary script deployed; M0-T140 still claimed awaiting the owner-typed run

1. **Generated:** 2026-09-02 by the M0-T141 session. The owner's second live canary run PASSED
   b5-01 (audit record 17, clean_status refusal, exit 11) but canary-b5-02's claude child exited
   1 BEFORE provider contact: Claude Code 2.1.252 rejects the Draft 2020-12 `$schema` declaration
   on `--json-schema` (provider-contact count zero; evidence preserved in
   `project-control/reports/M0-T141-canary-b502-schema-failure-evidence.md`). Amendment 44
   (R664-R683) authorized ONE bounded hotfix + canary continuation correction.
2. **Identity:** root/worktree `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`, branch
   `candidate/D-024-mrl-option-b` (LOCAL ONLY - no upstream). **Frozen corrected CODE candidate:
   `2245de74232947be919b555fd061ba8a6e6438de`** (tree 63119a9a, subtree edf026b3) - supersedes
   1489879e as the controller install source; `tools/agent_supervisor` at HEAD is byte-identical
   to it. `tools/controller_update/source_binding.json` + runbook s4 + ps_test pinnedSha all pin
   it. Nothing pushed; PR #241 untouched (R520/R521).
3. **Status:** M0-T141 ACCEPTED (independent G3 code-reviewer PASS + G4 qa-engineer PASS + DCV
   PASS 16/16 at reviewed head f8159f10; accept dry-run zero reasons; accept commit e79d7ccc).
   Fix: new `tools/agent_supervisor/mrl_provider_schema.py` projects a deep-copied, explicitly
   Draft-7-declared provider schema at the single `--json-schema` call site (fail-closed
   same-meaning keyword allowlist; canonical `schemas/worker_result.schema.json` +
   `mrl_worker_result.py` byte-identical). Focused tests 89 passed; mutants M1-M6 all DETECTED;
   supervisor suite 3566 passed/2 skipped; both ps harnesses PASS; modularity + registry
   validator clean.
4. **Ledger:** M0-T140 (canary-execution vehicle) stays **claimed** until the live canary
   finishes (R651/R674). M0-T137 backlog (owner-only R603-R605, never interpreted); M0-T133
   rework; M0-T135 backlog.
5. **Owner-run continuation (R680):** ONE external script deployed at
   `%LOCALAPPDATA%\NYCBuildabilitySupervisor\ctl24-activation\run_m0t141_hotfix_and_canary.ps1`
   (SHA-256 77705bc300fa95347ffb7ea646fb0742578a0a2e493e73bedde92796056984ea; PS 5.1 parse 0
   errors; prior script renamed `.superseded-by-m0t141`). Fail-fast order: backup -> install ->
   record-manifest -> verify-manifest -> normal doctor -> conditional s9a clear-recovery (journal
   currently PAUSED_RECOVERY) -> manifest re-draft vs M0-T140 -> exactly ONE provider one-shot
   `--run-id canary-b5-02r1` (correlated successor; b5-01 PASS REUSED from audit record 17, never
   rerun; no park/pending-approval step) -> readout -> harness -> ten-row table + one token.
   Rollback (bound backup only) fires ONLY on install/doctor failure, NEVER on a canary product
   defect (evidence preserved, stop) - R681.
6. **Next steps:** (a) owner types the one command (see M0-T141 return); (b) after the canary,
   record M0-T140 evidence reports + gates and accept under standard gates; (c) push/PR/merge and
   Tranche C stay owner-gated (R520-R522); R603-R605 owner-only.
7. **Standing restrictions:** R518; R520-R525 (no push/PR/merge/auto-accept/deploy/real
   loop/Tranche C); never merge PR #241; supervisor commits cite `D-024-R###` + AD-093
   qualifying evidence; no `name:` on producer spawns; no bare `git stash`; thin client;
   Bootstrap Gate 0 before any write; R683 never execute the owner-run script yourself.
8. **Authoritative files:** `project-control/tasks/M0-T141.json` (+ `M0-T140.json`),
   `project-control/directives/D-024-fable-codex-loop/source-044-amendment.md` (R664-R683),
   `project-control/reports/M0-T141-*` (producer-report, freeze, DCV, G3, G4,
   canary-b502-schema-failure-evidence), `tools/controller_update/source_binding.json`.
9. **Stop conditions:** any push/remote/PR/merge need; legal/credential/payment;
   ledger-vs-prose contradiction (ledger wins); owner rows R603-R605 (never interpreted).

## COPY INTO THE NEW SESSION

Resume from durable evidence only. Confirm `git rev-parse --show-toplevel` =
`C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`, branch `candidate/D-024-mrl-option-b`, Bootstrap
Gate 0 (cwd is that root, `/mcp` empty). Read `CLAUDE.md`, this file,
`project-control/tasks/M0-T140.json`, and `project-control/reports/M0-T141-freeze.md`. Run
`python tools/project_control.py status`; the ledger wins over prose. M0-T141 (Draft-7
provider-schema hotfix) is ACCEPTED at frozen corrected candidate 2245de74; the binding pins it.
M0-T140 stays claimed until the owner-typed canary finishes: the owner runs
`run_m0t141_hotfix_and_canary.ps1` (ctl24-activation; backup/install/verify/doctor/recovery/one
canary-b5-02r1 one-shot). Do NOT push, create/update/merge any PR, execute the owner script,
rerun b5-01, or start Tranche C. After a successful canary: write M0-T140 evidence reports, run
its independent gates, accept. Stop for owner-only items (R603-R605 never interpreted).
