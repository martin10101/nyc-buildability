# Session Handoff - NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume read it live -
`python tools/project_control.py status` - and reconcile; no SHA here is guaranteed current.
Orientation only; rules/gates live in `CLAUDE.md`. CURRENT-ONLY: `context-budget` CI fails > ~4000 tok.

## Handoff - seq 88: LOOP PIVOTED TO PRODUCT (D-038). Run persistent-local-19 / task M5-T003 on opus.

1. **Generated:** 2026-09-08 ~06:00Z, session_01WBbzN5Rx17CBSjky5uKmnY. Reason: owner directive
   "run the codex loop nonstop and build the software - no more building itself."
2. **Identity:** root `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`, branch `candidate/D-024-mrl-option-b`,
   HEAD `62aec042`, origin PUBLIC. Accepted tasks: **166** (unchanged; M5-T003 in flight).

3. **LOOP IS LIVE + DETACHED on a PRODUCT task (D-038):** run `persistent-local-19`, task **M5-T003**
   (scenario endpoint), supervisor **pid 12124** (lock at
   `%LOCALAPPDATA%\NYCBuildabilitySupervisor\9aca7075...\supervisor.lock`, token 01dd3f567d86697c),
   worker on **opus-4-8**. Launched via `Start-Process` from cwd `wt-controller-src`, repo `wt-m5t003`,
   branch `task/M5-T003-scenario-endpoint`, `--max-tasks 1 --max-cycles 10`. NONSTOP DUTY: a session-
   bound watcher polls the pid; on death **relaunch DETACHED run-id `persistent-local-20`** via the
   saved script `scratchpad/relaunch_m5t003.ps1` (or autostart-launch.ps1 pattern), NEVER ctl24-cwd.

4. **D-038 (owner 2026-09-08) - THE STEERING DIRECTIVE:** build the PRODUCT, no more supervisor self-
   infrastructure. Owner **declined credentials this session** (Supabase B-001 / Geoclient B-004 =
   deferred, NOT refused - they remain the real unlock for end-to-end product; surface first next
   session). Loop pivoted OFF the M0 self-tooling line. Records: `project-control/directives/D-038-*`,
   validate --check exit 0. `M0-T153` (accept-engine) + `M0-T155` (reviewer proportionality) are
   self-infra, now **DE-PRIORITIZED (preserved on wt-m0t153/wt-m0t155 branches, NOT deleted)**.

5. **CURRENT TASK M5-T003 (product):** `GET /api/v1/properties/{bbl}/scenario` exposing the already-
   built `app/scenario/build_scenario` (flag-gated INTERNAL_SCENARIO_ENABLED, contract-validated
   scenario@1.0.0, OFFLINE via injected PLUTO+substrate seams - NO Supabase/Geoclient). AS-1..AS-7.
   Claimed, wt-m5t003 @ 62aec042. When COMPLETE: standard T-B gate wave (G0/G3/G4/G5 + DCV), accept as
   DRAFT engineering (published/G6 deferred like the M4 chain). **NEXT product task = Compare (Step 3)
   UI** consuming this endpoint (the Confirm screen dead-ends at "steps 3-4 arrive later").

6. **MODEL - Fable weekly-exhausted; worker PINNED opus-4-8** (`C:\SupervisorController\model_selection.toml`).
   REVERT to `model="claude-fable-5"` when Fable returns (Thursday 9 PM local, D-036-R001). opus drops
   the checkpoint ~every 3rd cycle -> run may exit needing restart; work preserved on-branch, just relaunch.

7. **LOOP TASK-SWITCH DRILL (learned this session - a mid-unit kill trips 3 recovery gates in order):**
   after killing the old run to switch tasks: (a) `deny <req> <digest>` every stale pending ASK
   (pending-approvals) - clears `pending_requests`; (b) `git -C <new-worktree> reset --hard <candidate
   HEAD that CONTAINS the new task packet>` - the `task_authority` probe reads
   `<--repo>/project-control/tasks/<id>.json` and FAILS if the worktree base predates the packet;
   (c) reconcile the crashed-mid-unit dispatch intent via `recovery.reconcile_dispatch_intent(journal)`
   (no CLI verb; run scratchpad/reconcile_intent.py after read-only evidence) - clears `AMBIGUOUS_EFFECT`.
   Then `start` reaches SAFE_CHECKPOINT + run_budget_started. **LAUNCH BUG:** the `--config
   "C:\Program Files\SupervisorConfig\config.toml"` path has a SPACE - it MUST be quoted inside the
   Start-Process arg array or PowerShell splits it (autostart-launch.ps1 has the same latent bug - fix
   when installing autostart).

8. **Standing restrictions (unchanged):** no push/PR/merge (local-only; GitHub stale); NEVER merge
   PR #241; R595 / autostart-activation / continuous-mode owner-only; supervisor SHADOW; expansion
   hold; Bootstrap Gate 0 (cwd=root, `/mcp` empty); supervisor commits cite D-024-R###/AD-093; no bare
   git stash; thin client; R247 recert before NEW supervisor code to the running controller; launch
   ONLY from wt-controller-src cwd; NEVER audit-writing operator verbs against a LIVE run.

9. **Autostart:** owner elevated install still pending (D-036-R003); `autostart-launch.ps1` ACTIVE-TASK
   block updated to M5-T003. **Follow-ups (freeze-lane, gated):** wire live launch-probe seam (auto-
   fallback/return); fix install-autostart boot invalid-XML; the config-path quoting bug (item 7).

## COPY INTO THE NEW SESSION

Resume from durable evidence only. Bootstrap Gate 0 (root cwd, `/mcp` empty), branch
`candidate/D-024-mrl-option-b`. Read `CLAUDE.md`, this handoff, `python tools/project_control.py status`
(ledger wins). FIRST ACTION - KEEP THE LOOP NONSTOP: confirm supervisor pid alive (lock at
`...NYCBuildabilitySupervisor\9aca7075...`) and re-arm a read-only break watcher. On death, relaunch
DETACHED (run-id `persistent-local-20`) from `wt-controller-src` via `scratchpad/relaunch_m5t003.ps1`,
applying the task-switch drill (item 7) only if switching tasks. The loop builds PRODUCT now (D-038):
M5-T003 scenario endpoint -> then Compare (Step 3) UI. Worker on opus-4-8 (revert to Fable Thursday).
Do NOT: push/merge/PR #241, build supervisor self-infra as the loop target, run audit verbs against a
live run, launch from ctl24-cwd, install new supervisor code without R247 recert, bypass any gate.
Report READY TO RESUME or BLOCKED.
