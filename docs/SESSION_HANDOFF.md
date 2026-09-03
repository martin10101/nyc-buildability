# Session Handoff - NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live -
`python tools/project_control.py status` and `python -m tools.agent_supervisor.campaign_continuity
--status` - and reconcile against the remote: **origin may have advanced; do not trust any SHA here
as still-current.** Orientation only; rules/gates live in `CLAUDE.md`. CURRENT-ONLY:
`context-budget` CI fails > ~4000 tok.

## Handoff - seq 78: COMMISSIONING COMPLETE (canary-b5-02r3 all ten PASS); M0-T140 + M0-T143 ACCEPTED; first real supervised journey (M0-T107) prepared, awaiting the owner-typed run

1. **Generated:** 2026-09-03 by the Amendment 46/47 session (schema repair -> commissioning ->
   closure -> journey preparation).
2. **Identity:** root/worktree `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`, branch
   `candidate/D-024-mrl-option-b` (LOCAL ONLY, no upstream). **Frozen accepted CODE candidate:
   `3f4cee8680ba5c9a167327507af387d316f5dbc3`** (tree 04688351, subtree 209026fd) - the
   controller install source; binding + runbook s4 + ps_test pin it; installed live and
   byte-verified. Nothing pushed; PR #241 untouched.
3. **Commissioning (canary-b5-02r3, owner-typed 2026-09-03 00:43-00:46Z):** ALL TEN R587 items
   PASS. Full loop live-proven: Fable-5 worker COMPLETED (exact `claude-fable-5`, session
   44c7cce4, structured_output), **Codex review returned a schema-valid REVISE decision**
   (gpt-5.6-sol @ 0.146.0, git-bound), supervised hold answered deny by the owner
   (`operator_declined` = the clean settled close, NOT a defect - R715). Durable record:
   `project-control/reports/M0-T140-canary-execution-evidence.md` (s3 = the live-proven path;
   s4 = the honest GitHub boundary: the supervised loop's own push/PR/CI/merge surface has
   ZERO live evidence and stays unproven).
4. **Accepted this session:** M0-T143 (Amendment 46 codex --output-schema strict-subset repair;
   accept 37b2c3b6; suite 3626/2/0 triple-reproduced) and M0-T140 (Amendment 47 closure;
   accept commit after dc49c85f stamp; G3+G4 PASS + DCV 41/41 PASS). Amendments 46 (R700-R713)
   + 47 (R714-R724) captured; registry validator exit 0 throughout.
5. **NEXT = first real supervised production journey (R720-R722):** task **M0-T107**
   (portability plan; claimed; dependency M0-T096 accepted; allowed_paths = ONLY
   `docs/D024_PORTABILITY_PLAN.md` + `project-control/reports/M0-T107-portability-plan.md`).
   ONE deployed script
   `%LOCALAPPDATA%\NYCBuildabilitySupervisor\ctl24-activation\run_first_supervised_journey.ps1`
   (**Amendment-48 path-wiring corrected**: SHA-256
   ab051334b01c8db59909049ef932431a539703b51eef1f238cccb4b4d3fec124; PS 5.1 parse 0 errors).
   Every WORKER binding (repo root/cwd/worktree/branch/HEAD/clean) now comes from
   **wt-m0t107** (the packet's isolated worktree - the first attempt was refused
   `cwd_mismatch` because it bound ctl24; the R335/R336 guard is untouched). It: J0
   preconditions (control-plane checks on ctl24 + worker checks on wt-m0t107) -> J1
   verify-manifest (NO install) -> J2 claude-fable-5 VERIFY-ONLY -> J3 doctor -> J4 canonical
   journal transition -> J5 draft `--worktree wt-m0t107` vs the CURRENT ctl24 packet (allow
   Read/Grep/Glob/Agent/Write/Edit, BARE DENY Bash, Explore 2/2, max-turns 40, 1800s; asserts
   manifest.expected.worktree == wt-m0t107) -> J6 ONE supervised one-shot
   `--run-id journey-m0t107-01` -> J7 status + evidence paths. No push/PR/merge/deploy;
   model_selection never edited; preserved canary evidence guarded.
   **LAUNCH BLOCKER (owner disposition required):** wt-m0t107 is NOT clean - two UNTRACKED
   prior-journey drafts sit at exactly the deliverable paths (`docs/D024_PORTABILITY_PLAN.md`
   250 lines + `project-control/reports/M0-T107-portability-plan.md` 70 lines, authored
   2026-08-31 by supervisor-loop-fable-producer, run lineage run_m0t107_j4, at
   task/M0-T107-plugin-portability @ c5c6ff77 - the task's recorded 55% progress). The script
   (and the draft's own dirty-tree guard) refuses until the owner disposes: commit them to the
   task branch as the starting state (the journey prompt then has the worker revise/complete
   them), preserve them elsewhere, or remove them. Never overwrite silently.
6. **After the journey:** worker-produced docs sit UNCOMMITTED in ctl24; the orchestrator
   reviews the diff against M0-T107's allowed_paths, then normal mechanics (commit, G2/G3 per
   the packet, accept). On a journey failure: evidence preserved under `mrl\journey-m0t107-01`;
   causal-trace first (failures now carry the parsed provider error + bounded stdout/stderr
   tails); never loop reruns.
7. **Single owner-only GitHub decision (R723, parked):** whether to authorize the first live
   supervisor-driven GitHub interaction (task-branch push and/or the R595-gated automation
   path + Option-A audit-anchor activation, which needs controller credentials AND explicit
   owner activation). Local journeys need no GitHub authority; nothing proceeds on that
   surface without this one decision.
8. **Standing restrictions:** R518; R520-R525; never merge PR #241; supervisor commits cite
   `D-024-R###` + AD-093 evidence; no `name:` on producer spawns; no bare `git stash`; thin
   client; Bootstrap Gate 0 before any write; never execute owner-run scripts; no Tranche C;
   exact `claude-fable-5` only (never the `fable` alias, never claude-fable-5-1, fallback []).
9. **Authoritative files:** `project-control/tasks/M0-T107.json` (+ accepted M0-T140/T143),
   `project-control/directives/D-024-fable-codex-loop/source-046/047-amendment.md`,
   `project-control/reports/M0-T140-*` + `M0-T143-*`,
   `tools/controller_update/source_binding.json`.
10. **Stop conditions:** any push/remote/PR/merge need (see item 7); legal/credential/payment;
    ledger-vs-prose contradiction (ledger wins); a journey FAIL (trace, never loop).

## COPY INTO THE NEW SESSION

Resume from durable evidence only. Confirm `git rev-parse --show-toplevel` =
`C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`, branch `candidate/D-024-mrl-option-b`, Bootstrap
Gate 0 (cwd is that root, `/mcp` empty). Read `CLAUDE.md`, this file,
`project-control/tasks/M0-T107.json`, and
`project-control/reports/M0-T140-canary-execution-evidence.md`. Run
`python tools/project_control.py status`; the ledger wins. Commissioning is COMPLETE
(canary-b5-02r3 all ten PASS); M0-T140 + M0-T143 are ACCEPTED at frozen accepted candidate
3f4cee86 (binding pins it). NEXT: the owner types ONE command -
`run_first_supervised_journey.ps1` (ctl24-activation; sha 1b636d59...; verify-only install
check, claude-fable-5 pin verify, canonical resume-after-answer, ONE supervised M0-T107
journey). Do NOT push, create/update/merge any PR, execute owner scripts, rerun canaries,
edit model_selection, or start Tranche C. After the journey: review the produced docs against
M0-T107 allowed_paths, then normal gates/accept. On a FAIL: preserve evidence, causal-trace
first (failures carry the parsed provider error + tails). The single parked owner decision:
authorizing the first live supervisor-driven GitHub interaction (item 7). Stop for owner-only
items; credentials/payment/legal always stop.
