# Session Handoff - NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume read it live -
`python tools/project_control.py status` - and reconcile; no SHA here is guaranteed current.
Orientation only; rules/gates live in `CLAUDE.md`. CURRENT-ONLY: `context-budget` CI fails > ~4000 tok.

## Handoff - seq 87: LOOP LIVE + DETACHED (run-18 / M0-T153 on opus); watcher is session-bound; M0-T152 ACCEPTED (166th)

1. **Generated:** 2026-09-08 ~04:56Z, session_01WBbzN5Rx17CBSjky5uKmnY, `/session-handoff`.
   Reason (verbatim): "" (owner invoked after "i am back online").
2. **Identity:** root `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`, branch
   `candidate/D-024-mrl-option-b`, HEAD `6fb3516b`, origin PUBLIC (never push secrets). Tree CLEAN
   except deliberate untracked `.claude/agent-memory/qa-engineer/*`. Accepted tasks: **166**.

3. **LOOP IS LIVE AND DETACHED (survives session end):** run `persistent-local-18` (task M0-T153),
   supervisor pid 4896, launched via PowerShell **`Start-Process`** (hidden, detached) - NOT a
   background bash child, so it outlives this session. **The restart-on-death WATCHER is
   session-bound** and dies with this session. NONSTOP DUTY (D-035-R002 / D-033-R009): successor's
   FIRST action = confirm loop liveness (lock pid at
   `%LOCALAPPDATA%\NYCBuildabilitySupervisor\9aca7075...\supervisor.lock`) and **re-arm a read-only
   break watcher** (pid + journal `current_state`). On any death, run the DRILL: read
   `run_budget/persistent-local-<n>` exit_reason; answer/deny asks
   (`... --checkout C:\SupervisorController`, in-packet only per D-035-R006); reconcile intent if
   AMBIGUOUS_EFFECT (`recovery.reconcile_dispatch_intent` - read-only evidence first, no CLI verb);
   `clear-recovery` if PAUSED; `resume-after-answer` (+ commit a digest-bound snapshot) if
   WAIT_FOR_OWNER; **fresh run-id if budget_exhausted**; relaunch **DETACHED via Start-Process**,
   cwd `wt-controller-src` (certified a5886dab), NEVER ctl24-cwd. NEVER run audit-writing operator
   verbs against a LIVE run (forked the audit chain today; repaired via
   `tools/controller_update/repair_forked_audit_chain.py`).

4. **MODEL - Fable weekly-exhausted; worker MANUALLY PINNED to opus-4-8:** Fable 5 hit its weekly
   cap today. Auto-fallback does NOT actuate (the live launch-probe seam is not wired - built-but-
   ungapped, D-036 gap; even with `--authorize-turnover-actuation` on every launch it safe-stops on
   an unprobed candidate). So `C:\SupervisorController\model_selection.toml` is set
   `model="claude-opus-4-8"`, `fallback_models=[]` (D-036-R002 manual actuation, same as 2026-08-09).
   **REVERT to `model="claude-fable-5"`, `fallback_models=["claude-opus-4-8"]` when Fable returns
   (normally Thursday 9 PM local, D-036-R001).** opus is choppy on the big task: it drops the
   checkpoint ~every 3rd cycle (`no_valid_checkpoint`), forcing restarts (runs 15/16/17) - work is
   preserved on-branch each time; just restart.

5. **CURRENT TASK M0-T153 (D-033 T-B acceptance engine)** - claimed, in progress at
   `wt-m0t153` (branch `task/M0-T153-accept-engine`, ~cc4972fd). ~1200 LOC engine + ~1500 LOC tests
   built; grinding through review polish - the astra reviewer has returned **~38 REVISE vs 2
   COMPLETE** (the over-revise problem the owner flagged). Seven orchestrator span artifacts
   (`M0-T153-span-*.md`, UNTRACKED on purpose so the collector carries them) close the packet
   evidence gap. When it reaches COMPLETE: standard T-B gate wave (G0/G2/G3/G5 + DCV), accept, then
   the loop's next task is the STAGED M0-T155.

6. **M0-T155 STAGED (D-037 reviewer proportionality = the fix for #5's churn):** G0 PASS + CLAIMED,
   worktree `wt-m0t155` (branch `task/M0-T155-reviewer-proportionality`), packet synced. Runs when
   M0-T153 parks (owner said bump ahead; done without interrupting near-done work). Adds an OBJECTIVE
   rule to `prompts/codex_review.md`: REVISE only when it NAMES a failing gate/acceptance criterion;
   minor nits -> advisory + COMPLETE; real gates unchanged. **Takes effect on the live reviewer only
   after a controller recert** - bundle that recert with the acceptance-engine's (one owner-gated step).

7. **Directives captured today (all committed, validate --check exit 0):** D-035 (8-hour overnight
   monitor-only + restart-on-death; sentinel D-035-BOOTSTRAP), D-036 (arm fallback + autostart;
   sentinel D-036-BOOTSTRAP), D-037 (reviewer proportionality -> M0-T155). Records under
   `project-control/directives/`.

8. **AUTOSTART - owner elevated run pending (D-036-R003):** `schtasks` needs admin (I can't
   self-elevate). Ready: wrapper `C:\SupervisorController\autostart-launch.ps1` (relaunches the loop
   detached only if not already up; update its ACTIVE-TASK block as the loop advances) + installer
   `project-control/reports/D-036-install-autostart-ADMIN.ps1` (owner runs elevated -> Boot/logon +
   Weekly-Thu-9PM tasks, RestartInterval 4 min x50 until running). Not installed yet.

9. **Follow-ups to contract (freeze-lane, gated):** (a) wire the live launch-probe seam so auto-
   fallback AND auto-return actually fire; (b) fix `install-autostart --kind boot` invalid-XML bug
   (DeleteExpiredTaskAfter/EndBoundary); (c) M0-T155 (staged); (d) consider an opus checkpoint-
   reliability fix if the ~3rd-cycle drops persist.

10. **Standing restrictions (unchanged):** no push/PR/merge (Am40 local-only; GitHub intentionally
    stale; push needs a directive); NEVER merge PR #241; R595 / autostart-activation / continuous-
    mode owner-only; supervisor SHADOW until owner activates; expansion hold; Bootstrap Gate 0 (cwd =
    root, `/mcp` empty); supervisor commits cite D-024-R###/AD-093; no bare git stash; thin client;
    R247 recert+reinstall before any NEW supervisor code is installed to the running controller;
    launch supervisor ONLY from wt-controller-src cwd.

11. **Authoritative files:** `project-control/tasks/{M0-T152,M0-T153,M0-T155}.json`;
    `project-control/directives/{D-035,D-036,D-037}-*/`; `reports/D-035-overnight-20260907.md`
    (E0-E11 event log), `reports/D-036-execution-status.md`, `reports/M0-T153-*` + span files.
    Ledger + campaign records win over this prose.

## COPY INTO THE NEW SESSION

Resume from durable evidence only. Confirm `git rev-parse --show-toplevel` =
`C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`, branch `candidate/D-024-mrl-option-b`, Bootstrap Gate 0
(cwd = root, `/mcp` empty). Read `CLAUDE.md`, `docs/SESSION_HANDOFF.md`, then run
`python tools/project_control.py status` (ledger wins). FIRST ACTION - KEEP THE LOOP NONSTOP: the
loop is DETACHED and likely still running (run `persistent-local-18`, supervisor lock at
`%LOCALAPPDATA%\NYCBuildabilitySupervisor\9aca7075...`); confirm the lock pid is alive and RE-ARM a
read-only break watcher (the prior watcher died with the old session). On any loop death run the
drill in handoff item 3 and relaunch DETACHED via PowerShell Start-Process from cwd
`wt-controller-src` (NEVER ctl24), run-id `persistent-local-19`. Worker is on opus-4-8 (Fable weekly-
exhausted; revert to Fable Thursday 9 PM, item 4). THEN: process M0-T153 through its T-B gate wave
when it reaches COMPLETE, then the loop advances to the STAGED M0-T155 (reviewer proportionality).
Autostart install is an owner elevated action (item 8). Do NOT: push/merge/PR #241, run audit-writing
verbs against a live run, launch the supervisor from ctl24 cwd, install new supervisor code without
R247 recert, or bypass any gate. Report READY TO RESUME or BLOCKED.
