# Session Handoff - NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live -
`python tools/project_control.py status` and `python -m tools.agent_supervisor.campaign_continuity
--status` - and reconcile against the remote: **origin may have advanced; do not trust any SHA here
as still-current.** Orientation only; rules/gates live in `CLAUDE.md`. CURRENT-ONLY:
`context-budget` CI fails > ~4000 tok.

## Handoff - seq 79: journey launcher corrected (Amendment 48); awaiting TWO owner acts - drafts disposition, then the one journey command

1. **Generated:** 2026-09-03 by the Amendment 46-48 session via `/session-handoff` (reason:
   none given). Session: the Fable-5 orchestrator that ran the M0-T143 repair -> commissioning
   -> M0-T140 closure -> journey preparation + path correction.
2. **Identity:** root/worktree `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`, branch
   `candidate/D-024-mrl-option-b` (LOCAL ONLY, no upstream), HEAD `a8aec2f4`, tree CLEAN
   (nothing uncommitted). **Frozen accepted CODE candidate `3f4cee86`** (subtree 209026fd) =
   controller install source; binding + runbook s4 + ps_test pin it; installed and
   byte-verified. Nothing pushed; PR #241 untouched.
3. **Completed this session (durable):** (a) canary-b5-02r2 `review_unavailable` root-caused
   (provider 400: `'uniqueItems' is not permitted`) and repaired as **M0-T143 ACCEPTED**
   (Amendment 46 R700-R713; schema flatten + controller-side bounds + pre-spawn strict-subset
   inspection in BOTH reviewers + failure observability; suite 3626/2/0 triple-reproduced).
   (b) Owner commissioning **canary-b5-02r3: ALL TEN R587 items PASS** - full loop live-proven
   incl. a schema-valid Codex REVISE decision (gpt-5.6-sol @ 0.146.0); owner deny close
   (`operator_declined` = clean settled stop, never a defect). (c) **M0-T140 ACCEPTED**
   (Amendment 47 R714-R724; G3+G4 PASS + DCV 41/41; live-proven-path record + honest GitHub
   boundary in `project-control/reports/M0-T140-canary-execution-evidence.md` s3/s4).
   (d) First-journey launcher prepared, then **path-corrected per Amendment 48 R725-R731**
   after a `cwd_mismatch` refusal (launch bound ctl24; packet declares wt-m0t107; guard
   untouched). All six independent reviewer agents returned and are reconciled; none running.
4. **Deployed journey script (atomically replaced):**
   `%LOCALAPPDATA%\NYCBuildabilitySupervisor\ctl24-activation\run_first_supervised_journey.ps1`
   **SHA-256 ab051334b01c8db59909049ef932431a539703b51eef1f238cccb4b4d3fec124** (PS 5.1 parse
   0 errors). ALL worker bindings (repo root/cwd/worktree/branch/HEAD/clean) come from
   **wt-m0t107**; ctl24 stays control-plane (binding, frozen identity, CURRENT packet);
   C:\SupervisorController stays the controller runtime. J5 asserts
   `manifest.expected.worktree == wt-m0t107`; Bash bare-denied; Explore 2/2; max-cycles 1;
   run id `journey-m0t107-01`; no push/PR/merge/deploy; model_selection never edited.
5. **LAUNCH BLOCKER - owner disposition required (decision A):** `wt-m0t107`
   (task/M0-T107-plugin-portability @ c5c6ff77, identity matches the packet) is NOT clean:
   two UNTRACKED prior-journey drafts sit at exactly the deliverable paths
   (`docs/D024_PORTABILITY_PLAN.md` 250 lines + `project-control/reports/M0-T107-portability-plan.md`
   70 lines; authored 2026-08-31 by supervisor-loop-fable-producer, lineage run_m0t107_j4 -
   the task's 55% progress). The script and the draft's dirty-tree guard refuse until the
   owner picks: **commit to the task branch as starting state (recommended; the journey prompt
   is disposition-aware and has the worker revise/complete existing files)**, preserve
   elsewhere, or remove. Never overwrite silently.
6. **Next actions in order:** (A) owner disposes of the two drafts (one line to the session,
   or their own git act in wt-m0t107); (B) owner types the ONE command:
   `powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$env:LOCALAPPDATA\NYCBuildabilitySupervisor\ctl24-activation\run_first_supervised_journey.ps1"`;
   (C) after the journey: review produced files in wt-m0t107 against M0-T107 allowed_paths,
   then normal mechanics (commit to task branch, gates G0/G2/G3 per packet, accept). On a
   journey FAIL: evidence preserved under `mrl\journey-m0t107-01`; causal-trace first
   (failures carry the parsed provider error + bounded stdout/stderr tails); never loop reruns.
7. **Terminal visibility (recorded honestly, R730):** no per-event streaming exists during a
   run - the terminal shows script phase banners, the start preamble, any typed refusal line,
   the interactive supervised-approval `input()` prompt (on REVISE), then the final DISPATCHED
   summary + J7 status. Events land in real time in `…\9aca7075…\audit.jsonl` (second-window
   `Get-Content -Wait` = zero-code live view). Any richer live display needs owner approval -
   NOT implemented.
8. **Parked owner decisions:** (B above is routine;) the single GitHub decision - authorize
   the first live supervisor-driven GitHub interaction (task-branch push / R595-gated
   automation + Option-A anchor activation). Also R603-R605 remain owner-only. Local journeys
   need no GitHub authority.
9. **Standing restrictions:** R518, R520-R525 (no push/PR/merge/Tranche C; PR #241 never);
   supervisor commits cite `D-024-R###` + AD-093 evidence; no `name:` on producer spawns; no
   bare `git stash`; thin client; Bootstrap Gate 0 before any write; never execute owner-run
   scripts; exact `claude-fable-5` only (no `fable` alias, no claude-fable-5-1, fallback []);
   never weaken the cwd guard; expansion-planning hold in force.
10. **Validation at handoff:** registry validator exit 0 at HEAD; `project_control.py status`
    counts accepted=155 / claimed=2 (M0-T107, M0-T109) / rework=1 (M0-T133);
    campaign_continuity --status rc 0. Authoritative files:
    `project-control/tasks/M0-T107.json`, `project-control/reports/M0-T140-*` + `M0-T143-*`,
    `project-control/directives/D-024-fable-codex-loop/source-046/047/048-amendment.md`,
    `tools/controller_update/source_binding.json`. Stop conditions: push/remote/PR/merge
    needs; credentials/payment/legal; ledger-vs-prose contradiction (ledger wins); journey
    FAIL (trace, never loop).

## COPY INTO THE NEW SESSION

Resume from durable evidence only. Confirm `git rev-parse --show-toplevel` =
`C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`, branch `candidate/D-024-mrl-option-b`, Bootstrap
Gate 0 (cwd is that root, `/mcp` empty). Read `CLAUDE.md`, this file,
`project-control/tasks/M0-T107.json`, and
`project-control/reports/M0-T140-canary-execution-evidence.md`. Run
`python tools/project_control.py status`; the ledger wins. Commissioning is COMPLETE; M0-T140
+ M0-T143 are ACCEPTED at frozen accepted candidate 3f4cee86. The corrected journey script
(sha ab051334...) binds the worker to wt-m0t107 and is deployed. TWO owner acts remain, in
order: (A) disposition of wt-m0t107's two untracked prior drafts (recommend: commit to
task/M0-T107-plugin-portability as the starting state; the script refuses while the worker
tree is dirty); (B) the one journey command (handoff item 6). Do NOT push, create/update/merge
any PR, execute owner scripts, rerun canaries, edit model_selection, weaken the cwd guard, or
start Tranche C. After the journey: review wt-m0t107's produced files against M0-T107
allowed_paths, then normal gates/accept. On a FAIL row: preserve evidence, causal-trace first.
Stop for owner-only items (GitHub activation, R603-R605, credentials/payment/legal).
