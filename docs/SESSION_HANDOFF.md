# Session Handoff - NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume read it live -
`python tools/project_control.py status` - and reconcile; no SHA here is guaranteed current.
Orientation only; rules/gates live in `CLAUDE.md`. CURRENT-ONLY: `context-budget` CI fails > ~4000 tok.

## Handoff - seq 90: M5-T004 (Compare Step-3 UI) loop LIVE + building autonomously (run persistent-local-20).

1. **Generated:** 2026-09-08 ~16:31Z, session ctl24 (resume of seq-89), after relaunching the loop on the
   next product feature per D-038.
2. **Identity:** root `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`, branch `candidate/D-024-mrl-option-b`,
   HEAD `1c8945be` (control-plane only; local-only, GitHub intentionally stale, origin/main d8b3899f).
   **Accepted tasks: 167** (M5-T003 scenario endpoint, unchanged). M5-T004 is `claimed`, NOT accepted.
3. **LOOP IS UP (run persistent-local-20, limited-auto + bounded-auto, worker opus-4-8) building M5-T004**
   = Compare (Step 3) UI in `apps/web` consuming the accepted scenario endpoint, offline/fixtures, no creds.
   Contracted this session (G0+claim, `directive_refs D-038:ALL`, appended to D-038-R003/R004 applicability;
   validator EXIT=0). Worker worktree `wt-m5t004` (branch `task/M5-T004-compare-ui`); files are UNCOMMITTED
   there (producer is broker-blocked from git; the **orchestrator commits at checkpoint/gate**). Supervisor
   pid changes per relaunch - find it live: read the lock at
   `%LOCALAPPDATA%\NYCBuildabilitySupervisor\9aca707563cfe6e2...\supervisor.lock`.
4. **AUTONOMY MODEL (owner directive this session): "the loop does the full job; I monitor ONLY big breaks
   and stay silent."** Achieved by (a) correct `allowed_paths` `**`/`scenario-*` globs so worker Writes
   AUTO-APPROVE, and (b) packet TOOL-DISCIPLINE text telling the worker to orient with Read/Grep/Glob and
   NEVER use Bash/git (undocumented shell STALLS the worker on an operator ASK; the worker does NOT self-adapt
   in 0.4.0-phase4). Result: 0 pending asks, writes auto-approving. **Do NOT answer asks against a LIVE run**
   (forks the audit chain). A read-only big-breaks-only watcher is armed (loop-close/crash/freeze only).
5. **EXACT NEXT ACTION:** the loop runs `--max-tasks 1` -> it builds M5-T004 to UNIT_COMPLETE then STOPS
   (the watcher pings "LOOP CLOSED"). On that: (a) commit the worker's `wt-m5t004` output to the candidate
   line; (b) run the gate wave G1/G3/G4/G5 (code, qa, security, +visual-quality/human-journey for UI) as
   independent reviewers != producer; (c) accept (needs D-038-R003/R004 verified PASS for M5-T004 at reviewed
   identity + all gates PASS); (d) relaunch the loop on the NEXT product feature (Evidence/Step-4 UI, or a
   rule family). Full relaunch mechanics: memory **loop-relaunch-mechanics** (checkout_key, the 5 start
   blockers, the drill, the audit-fork repair).
6. **MODEL - worker PINNED `claude-opus-4-8`** (`C:\SupervisorController\model_selection.toml`); Fable weekly
   quota exhausted. **REVERT to `model="claude-fable-5"` Thursday 9 PM local (D-036-R001).** opus may drop the
   checkpoint intermittently -> if the run exits, work is preserved on `wt-m5t004`; just relaunch.
7. **RELAUNCH:** `scratchpad/relaunch_m5t004.ps1` pattern (individual-flag `start`, NOT MRL manifest; mirror
   `C:\SupervisorController\autostart-launch.ps1`; `--config` path double-quoted INSIDE the arg array;
   `--max-tasks 1`; run-id `persistent-local-20`; cwd `wt-controller-src`, NEVER ctl24). Down-run drill before
   relaunch: `deny` each stale ask + `reconcile_dispatch_intent.py` + `clear-recovery` if PAUSED_RECOVERY;
   tree-kill a live supervisor with `taskkill //F //T //PID <pid>` (never Stop-Process all claude.exe).
   All operator write-verbs ONLY when the run is DOWN.
8. **Standing restrictions (unchanged):** no push/PR/merge; NEVER merge PR #241; R595 / autostart-activation /
   continuous-mode owner-only; supervisor SHADOW; expansion hold; Bootstrap Gate 0 (cwd=root, `/mcp` empty);
   R247 recert before NEW supervisor code; launch ONLY from wt-controller-src; no bare git stash; thin client;
   owner-only = credentials/payment/production/legal (Supabase B-001 + Geoclient B-004 remain the deferred
   unlock for the FULL end-to-end product - surface next session, D-038-R005).

## COPY INTO THE NEW SESSION

Resume from durable evidence only. Bootstrap Gate 0 (root cwd, `/mcp` empty), branch
`candidate/D-024-mrl-option-b`. Read `CLAUDE.md`, this handoff, memory `loop-relaunch-mechanics` +
`d038-product-pivot`, then `python tools/project_control.py status` (ledger wins). Reconcile handoff vs live
git + ledger. M5-T003 ACCEPTED (167th); M5-T004 (Compare UI) is the loop's current build target. Check the
loop is alive (lock pid under checkout 9aca7075...); if DOWN, run the drill + relaunch DETACHED (persistent-
local-20) from wt-controller-src per item 7. If the loop finished M5-T004, gate + accept it (item 5) then
relaunch on the next product feature. Owner directive: the loop does the full job; monitor ONLY big breaks
and stay silent; never answer asks against a live run. Worker opus-4-8 (revert Fable Thu). Do NOT: push/merge/
PR #241, build supervisor self-infra as the loop target (D-038), run audit-writing verbs vs a live run, launch
from ctl24-cwd, install new supervisor code without R247 recert, bypass any gate, or require the deferred
credentials. Report READY TO RESUME or BLOCKED.
