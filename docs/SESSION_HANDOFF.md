# Session Handoff - NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live -
`python tools/project_control.py status` and `python -m tools.agent_supervisor.campaign_continuity
--status` - and reconcile against the remote: **origin may have advanced; do not trust any SHA here
as still-current.** Orientation only; rules/gates live in `CLAUDE.md`. CURRENT-ONLY:
`context-budget` CI fails > ~4000 tok.

## Handoff - seq 72: M0-T136 Tranche B COMPLETE OFFLINE at the frozen candidate; submitted, awaiting independent review

1. **Generated:** 2026-09-01 by the Tranche-B producer/integrator session at the FINAL frozen
   Tranche-B candidate (the R595-conformant regeneration; the seq-71 mid-tranche one was
   owner-invoked and is superseded).
2. **Identity:** root/worktree `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`, branch
   `candidate/D-024-mrl-option-b` (LOCAL ONLY - no upstream, no remote head). **Frozen Tranche-B
   CODE candidate: `1489879e1f6787a9d53ed74db4524b24039e03a2`** (chain: 895cfbe5 B0 freeze ->
   2bcd9aa8 survey -> 0e37e115 B1 -> 9c8be98d B2 -> 0e0c4bcc+5319c50a B3 -> 4bf845cd B4 ->
   a57802cc/472ae045 packet scope -> d39c49bb C-B5 part 1 -> aa63a50f seq-71 handoff -> 1489879e
   C-B5 part 2). HEAD may be one control-plane evidence commit past 1489879e (reports + this file
   only, NO code/tests - R594 intact). Remote `control/D-024-fable-codex-loop` = 6f5d12a6
   (untouched base); PR #241 head 4174a3b2 untouched; nothing pushed (R520/R521).
3. **Status:** ALL Tranche-B clusters B0-B5 delivered offline. The ONE complete affected +
   repository verification (R593) ran at 1489879e: 17 `final-freeze-*.json` gate_runner records
   (86-module supervisor suite rc0; 77 Tranche-A cases rc0; modularity, ruff changed/CI-scope,
   all validators, doc-checks, ps_tests rc0; root ruff rc1 = pre-existing F28, stdout
   byte-identical to B0; doc-check mutation killed). Producer terminal token reported:
   TRANCHE_B_OFFLINE_COMPLETE_CANARIES_READY. Submitted via `/submit-checkpoint`
   (requested `awaiting_gate`, evidence map `M0-T136-evidence-map.json`, 82 applicable
   D-024 requirement rows). NO self-acceptance (R596-R598).
4. **Ledger:** M0-T136 awaiting independent review (G3 code-reviewer, G4 qa-engineer,
   directive-compliance-verifier; reviewers read-only, orchestrator records gates and decides).
   M0-T137 (model-selection addendum) BACKLOG until owner decides R603/R604/R605 - never
   interpreted. M0-T133 REWORK/unaccepted (R480); M0-T135 backlog.
5. **Deliverables (all committed):** `docs/MRL_LAUNCH_RUNBOOK.md` (the ONE operator launch path;
   tooth-validated), CONTROLLER_UPDATE_RUNBOOK s11 OBSOLETE (no start presented), package README
   pointer, `tools/agent_supervisor/ps_tests/` (raw-$LASTEXITCODE harness + runner + 3 tests +
   3 mutants, all mutations DETECTED), `project-control/reports/M0-T136-canary-package.md`
   (ten R587 items verbatim, owner-run only, NOT executed), failure-surface closure (s6),
   `M0-T136-tranche-b-evidence.json` (32 records indexed), `M0-T136-G2-self-check.md`,
   `M0-T136-producer-report.md` (all R597 items + all blockers together),
   `M0-T136-evidence-map.json`.
6. **Next steps (in order):** (a) independent G3/G4/DCV review wave on the frozen candidate
   (reviewers read-only; delta-attestation pattern for any behavior-neutral rework);
   (b) orchestrator records gates and accepts/reworks; (c) present the owner canary package and
   STOP - the ten canaries are owner-typed from the frozen candidate after the owner-run
   controller update (CONTROLLER_UPDATE_RUNBOOK s3-s8) and a draft re-run; (d) any push/PR/merge
   of the candidate branch and everything beyond stays owner-gated; Tranche C NOT authorized
   (R522).
7. **Blockers/follow-ups (none stop review; full list `M0-T136-producer-report.md` s10):**
   doc-check DEFAULT_DOCS lacks the MRL runbook (CI covers via --doc only);
   `.claude/skills/loop-start/SKILL.md` + `.claude/hooks/loop_command_interceptor.py:202` still
   show the legacy launch shape (out of packet); ps_tests not in CI (workflows forbidden);
   CONTROLLER_UPDATE_RUNBOOK s9/s10 still name `wt-m0t063`; canary `--mode supervised` chosen
   (amendment silent - stated in package); live CLI permission shapes provable only by the
   owner canary (R579); root ruff F28 pre-existing.
8. **Standing restrictions:** R518 never run the rejected reapply line; R520-R522 no
   push/PR/merge/auto-accept/deploy/real loop/Tranche C; R523 no live canaries (present + stop);
   R524/R525 foreground in-scope subagents only, primary session sole integrator, no subagent
   git; never merge PR #241; supervisor commits cite `D-024-R###`; no `name:` on producer
   spawns; no bare `git stash`; thin client; Bootstrap Gate 0 (cwd = ctl24, `/mcp` empty)
   before any write; any code change after 1489879e invalidates the final verification (R594).
9. **Authoritative files:** `project-control/tasks/M0-T136.json`, `project-control/campaigns/*.json`,
   `project-control/directives/D-024-fable-codex-loop/source-040-amendment.md` + `requirements.json`,
   `project-control/reports/M0-T136-*`, `project-control/reports/M0-T136-gates/*.json`, git log of
   `candidate/D-024-mrl-option-b`.
10. **Stop conditions:** any push/remote/PR/merge need; legal/credential/payment; a contradiction
    between this file and the ledger (ledger wins); owner rows R603-R605 (never interpreted).

## COPY INTO THE NEW SESSION

Resume from durable evidence only. Confirm `git rev-parse --show-toplevel` =
`C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`, branch `candidate/D-024-mrl-option-b`, HEAD at or one
control-plane commit past 1489879e, Bootstrap Gate 0 (cwd is that root, `/mcp` empty). Read
`CLAUDE.md`, this file, `project-control/tasks/M0-T136.json`, and
`project-control/reports/M0-T136-producer-report.md`. Run `python tools/project_control.py status`
and `python -m tools.agent_supervisor.campaign_continuity --status`; the ledger wins over prose.
M0-T136 is submitted at frozen candidate 1489879e: run the independent review wave (G3
code-reviewer, G4 qa-engineer, directive-compliance-verifier - read-only, producer != reviewer)
against the frozen SHA and the `final-freeze-*` gate records, then record gates via the
orchestrator. Do NOT push, create/update/merge any PR, run live canaries, start Tranche C, or
change code (R594). Stop for owner-only items (R603-R605 never interpreted).
