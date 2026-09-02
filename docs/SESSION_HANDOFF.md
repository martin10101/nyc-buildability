# Session Handoff - NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live -
`python tools/project_control.py status` and `python -m tools.agent_supervisor.campaign_continuity
--status` - and reconcile against the remote: **origin may have advanced; do not trust any SHA here
as still-current.** Orientation only; rules/gates live in `CLAUDE.md`. CURRENT-ONLY:
`context-budget` CI fails > ~4000 tok.

## Handoff - seq 73: M0-T136 ACCEPTED; controller-update source binding repaired (M0-T138 submitted, awaiting independent review)

1. **Generated:** 2026-09-02 by the M0-T138 producer session (D-024 Amendment 41: owner rejected
   the manual command-substitution shortcut; canonical controller-update source binding repaired
   before any controller update or canary).
2. **Identity:** root/worktree `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`, branch
   `candidate/D-024-mrl-option-b` (LOCAL ONLY - no upstream, no remote head). **Frozen Tranche-B
   CODE candidate: `1489879e1f6787a9d53ed74db4524b24039e03a2`** (chain: 895cfbe5 B0 freeze ->
   2bcd9aa8 survey -> 0e37e115 B1 -> 9c8be98d B2 -> 0e0c4bcc+5319c50a B3 -> 4bf845cd B4 ->
   a57802cc/472ae045 packet scope -> d39c49bb C-B5 part 1 -> aa63a50f seq-71 handoff -> 1489879e
   C-B5 part 2). M0-T136 ACCEPTED at e60192ed (G3/G4/DCV 82 rows PASS at the frozen candidate);
   later commits are the M0-T138 capture/implementation/evidence sequence (docs + new
   `tools/controller_update/` + control plane; the accepted 1489879e supervisor code surface is
   untouched). Remote `control/D-024-fable-codex-loop` = 6f5d12a6 (untouched base); PR #241 head
   4174a3b2 untouched; nothing pushed (R520/R521).
3. **Status:** Tranche B accepted. Owner directive 2026-09-02 (Amendment 41, R607-R621) repaired
   the controller-update source binding: CONTROLLER_UPDATE_RUNBOOK s4 no longer resolves mutable
   `origin/main` (which lacks Tranche B and `mrl_launch_draft.py`); the sole checked-in
   procedure now installs from the immutable accepted candidate SHA via
   `tools/controller_update/update_controller_from_candidate.ps1` + `source_binding.json`
   (pre-copy repo/origin/commit/tree/subtree/module/detached-worktree verification, /MIR copy,
   complete bidirectional SHA-256 proof, `controller_update_evidence.json`, s5a recorded-manifest
   cross-check against the ACCEPTED source), with positive + six typed rejection classes + 4
   killed mutants + PS 5.1 parse tooth in `tools/controller_update/ps_tests/`.
4. **Ledger:** M0-T138 submitted awaiting independent review (G3 code-reviewer, G4 qa-engineer,
   directive-compliance-verifier; reviewers read-only, orchestrator records gates and decides;
   NO self-acceptance, R619). M0-T137 (model-selection addendum) BACKLOG until owner decides
   R603/R604/R605 - never interpreted. M0-T133 REWORK/unaccepted (R480); M0-T135 backlog.
5. **Deliverables (all committed):** M0-T136 set unchanged (MRL runbook, s11 obsolete, supervisor
   ps_tests, canary package, evidence). NEW under M0-T138: repaired CONTROLLER_UPDATE_RUNBOOK
   s4 + s5a + s1/s10 rows, `tools/controller_update/` (operator script, binding contract,
   ps_tests runner + 3 tests incl. mutation + parse teeth), `M0-T138-*` reports/gate records,
   Amendment 41 capture (source-041, R607-R621).
6. **Next steps (in order):** (a) independent G3/G4/DCV review wave for M0-T138 at its submitted
   head (reviewers read-only; producer != reviewer); (b) orchestrator records gates and
   accepts/reworks; (c) ONLY then the owner-typed controller update via the repaired
   CONTROLLER_UPDATE_RUNBOOK s3-s8 (ONE s4 install command sourcing immutable 1489879e, s5
   record-manifest, s5a verify-manifest cross-check, s6-s8) followed by the untouched
   `M0-T136-canary-package.md` steps - exactly one consistent owner command chain (R614/R615);
   (d) any push/PR/merge of the candidate branch and everything beyond stays owner-gated;
   Tranche C NOT authorized (R522).
7. **Blockers/follow-ups (none stop review; M0-T136 list in its producer report s10, M0-T138
   list in `M0-T138-producer-report.md`):** doc-check DEFAULT_DOCS lacks the MRL runbook;
   `.claude/skills/loop-start/SKILL.md` + `.claude/hooks/loop_command_interceptor.py:202` legacy
   shape (out of packet); ps_tests (both suites) not in CI (workflows forbidden);
   CONTROLLER_UPDATE_RUNBOOK s2/s7-s10 still name `wt-m0t063`; live CLI permission shapes
   provable only by the owner canary (R579); root ruff F28 pre-existing; a fully re-computed
   tampered binding contract is bounded by reviewed commits + the printed-identity comparison,
   not by the script alone (disclosed).
8. **Standing restrictions:** R518 never run the rejected reapply line; R520-R522 no
   push/PR/merge/auto-accept/deploy/real loop/Tranche C; R523 no live canaries (present + stop);
   R524/R525 foreground in-scope subagents only, primary session sole integrator, no subagent
   git; never merge PR #241; supervisor commits cite `D-024-R###`; no `name:` on producer
   spawns; no bare `git stash`; thin client; Bootstrap Gate 0 (cwd = ctl24, `/mcp` empty)
   before any write; any code change after 1489879e invalidates the final verification (R594).
9. **Authoritative files:** `project-control/tasks/M0-T138.json` (+ accepted `M0-T136.json`),
   `project-control/directives/D-024-fable-codex-loop/source-041-amendment.md` + `requirements.json`,
   `project-control/reports/M0-T138-*` (+ `M0-T136-*`), `tools/controller_update/`, git log of
   `candidate/D-024-mrl-option-b`.
10. **Stop conditions:** any push/remote/PR/merge need; legal/credential/payment; a contradiction
    between this file and the ledger (ledger wins); owner rows R603-R605 (never interpreted).

## COPY INTO THE NEW SESSION

Resume from durable evidence only. Confirm `git rev-parse --show-toplevel` =
`C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`, branch `candidate/D-024-mrl-option-b`, Bootstrap
Gate 0 (cwd is that root, `/mcp` empty). Read `CLAUDE.md`, this file,
`project-control/tasks/M0-T138.json`, and `project-control/reports/M0-T138-producer-report.md`.
Run `python tools/project_control.py status` and
`python -m tools.agent_supervisor.campaign_continuity --status`; the ledger wins over prose.
M0-T136 is ACCEPTED at the frozen candidate 1489879e; M0-T138 (Amendment 41 controller-update
source binding) is submitted: run its independent review wave (G3 code-reviewer, G4 qa-engineer,
directive-compliance-verifier - read-only, producer != reviewer) at the submitted head with the
`M0-T138-gates/*.json` raw records, then record gates via the orchestrator. Do NOT push,
create/update/merge any PR, update C:\SupervisorController, run live canaries, or start
Tranche C. Stop for owner-only items (R603-R605 never interpreted).
