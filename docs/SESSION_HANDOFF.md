# Session Handoff - NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live -
`python tools/project_control.py status` and `python -m tools.agent_supervisor.campaign_continuity
--status` - and reconcile against the remote: **origin may have advanced; do not trust any SHA here
as still-current.** Orientation only; rules/gates live in `CLAUDE.md`. CURRENT-ONLY:
`context-budget` CI fails > ~4000 tok.

## Handoff - seq 77: M0-T143 Codex review-schema repair (Amendment 46); canary-b5-02r2 root cause proven; successor script deployed; M0-T140 still claimed awaiting canary-b5-02r3

1. **Generated:** 2026-09-03 by the Amendment 46 session (canary-b5-02r2 differential trace +
   owner probe + corrective package).
2. **Identity:** root/worktree `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`, branch
   `candidate/D-024-mrl-option-b` (LOCAL ONLY). **Frozen corrected CODE candidate:
   `3f4cee8680ba5c9a167327507af387d316f5dbc3`** (tree 04688351, subtree 209026fd) - supersedes
   f8f0f0c8 as the controller install source; binding + runbook s4 + ps_test pinnedSha all pin
   it; `tools/agent_supervisor` at HEAD is byte-identical to it. Nothing pushed; PR #241
   untouched. Campaign-continuity record still STALE (ledger wins).
3. **canary-b5-02r2 outcome (preserved):** Fable-5 worker leg PASS (primary claude-fable-5,
   argv proof, session fc7ddb4c); Codex review leg FAILED - child spawned, exit 1, empty
   stderr, stdout discarded -> blind no_decision -> review_unavailable. Owner probe
   `codex-schema-probe-20260902-191655532` captured the cause verbatim: `invalid_json_schema`,
   status 400, param `text.format.schema`, "In context=('properties', 'evidence_ref_ids'),
   'uniqueItems' is not permitted." Root cause: review_verdict.schema.json carried constraint
   keywords outside the provider strict Structured-Outputs subset (never live-proven before).
4. **M0-T143 (Amendment 46, R700-R713):** schema flattened (five keywords removed together);
   bounds preserved controller-side in ReviewVerdict.from_provider; pre-spawn strict-subset
   inspection in BOTH reviewers + every-provider-facing-schema sweep test; reviewer failure
   observability (parsed provider error + bounded redacted stdout/stderr tails; typed
   provider_rejected_request / missing_decision_file - never bare no_decision); owner capture
   as regression fixture. Red->green + mutation pair recorded; full suite at 3f4cee86:
   **3626 passed / 2 skipped / 0 failed**. Evidence: `project-control/reports/M0-T143-evidence.md`.
   R709 determination: NO supported review-resume exists (CYCLE_ENTRY_STATES; no pending
   prompt) -> ONE successor full canary via resume-after-answer + start.
5. **Ledger:** M0-T140 (canary vehicle) stays **claimed** until canary-b5-02r3 passes.
   M0-T143 per ledger (gates G0/G2 recorded; G3/G4 + DCV per reports). M0-T137 backlog
   (owner-only R603-R605); M0-T133 rework; M0-T135 backlog.
6. **Owner-run continuation (R711):** ONE deployed script
   `%LOCALAPPDATA%\NYCBuildabilitySupervisor\ctl24-activation\run_m0t143_codex_schema_repair_and_canary.ps1`
   (SHA-256 096ee3ea749ca3b8654561a20aa442b0bac472ad6f1635e430da0116ebfed5de; PS 5.1 parse 0
   errors; prior script renamed `.superseded-by-m0t143`). Fail-fast: P0 preconditions (b5-02/
   -02r1/-02r2 preserved; r3 fresh; REUSED b5-01 row) -> backup -> install 3f4cee86 ->
   record-manifest -> verify-manifest -> **PV model-pin VERIFY-ONLY (claude-fable-5; NEVER
   edits selection)** -> doctor (model_selection row must read claude-fable-5) -> P6 canonical
   recovery (WAIT_FOR_OWNER -> resume-after-answer; PAUSED_RECOVERY -> clear-recovery) ->
   draft (allow Read/Grep/Glob/Agent, BARE DENY Bash) -> ONE one-shot `--run-id canary-b5-02r3`
   -> corrected R708 readout (row 3 split legs + parsed provider error on failure; row 7
   post-review settled family + review-verdict requirement) -> P10 harness -> table + token.
   Rollback ONLY on install/doctor failure; NEVER on a canary defect; model_selection never
   edited in any path.
7. **Next steps:** (a) owner types the one command; (b) after CANARY_PACKAGE_PASS: write
   `project-control/reports/M0-T140-canary-execution-evidence.md`, run M0-T140's independent
   gates, accept; on a FAIL row: preserve evidence, causal-trace first, no rollback/reinstall
   loops; (c) push/PR/merge + Tranche C stay owner-gated (R520-R522); R603-R605 owner-only.
8. **Standing restrictions:** R518; R520-R525; never merge PR #241; supervisor commits cite
   `D-024-R###` + AD-093 evidence; no `name:` on producer spawns; no bare `git stash`; thin
   client; Bootstrap Gate 0 before any write; R712 never execute the owner-run script, never
   push/merge; R707 exact `claude-fable-5` only (never the `fable` alias, never
   claude-fable-5-1, fallback []).
9. **Authoritative files:** `project-control/tasks/M0-T143.json` (+ M0-T140),
   `project-control/directives/D-024-fable-codex-loop/source-046-amendment.md`,
   `project-control/reports/M0-T143-*`, `tools/controller_update/source_binding.json`,
   `docs/CONTROLLER_UPDATE_RUNBOOK.md` s4.
10. **Stop conditions:** any push/remote/PR/merge need; legal/credential/payment;
    ledger-vs-prose contradiction (ledger wins); a canary FAIL row (trace, never loop).

## COPY INTO THE NEW SESSION

Resume from durable evidence only. Confirm `git rev-parse --show-toplevel` =
`C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`, branch `candidate/D-024-mrl-option-b`, Bootstrap
Gate 0 (cwd is that root, `/mcp` empty). Read `CLAUDE.md`, this file,
`project-control/tasks/M0-T143.json`, `project-control/tasks/M0-T140.json`, and
`project-control/reports/M0-T143-evidence.md`. Run `python tools/project_control.py status`;
the ledger wins. M0-T143 (Codex review-schema repair) is the frozen corrected candidate
3f4cee86 (binding pins it). M0-T140 stays claimed until the owner-typed canary finishes: the
owner runs `run_m0t143_codex_schema_repair_and_canary.ps1` (ctl24-activation; sha 096ee3ea...;
installs 3f4cee86, VERIFIES claude-fable-5 without editing, exits WAIT_FOR_OWNER via
resume-after-answer, runs ONE canary-b5-02r3 one-shot). Do NOT push, create/update/merge any
PR, execute the owner script, rerun b5-01, change model_selection, or start Tranche C. After
CANARY_PACKAGE_PASS: write M0-T140's canary-execution evidence, run its independent gates,
accept. On any FAIL row: preserve evidence, produce a causal trace first (the failure record
now carries the parsed provider error + stdout/stderr tails). Stop for owner-only items
(R603-R605 exercised only by the owner).
