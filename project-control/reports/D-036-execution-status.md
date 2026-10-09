# D-036 execution status — 2026-09-07

Owner directive D-036: arm model fallback + install autostart, with three conditions. What was
done, what is blocked, and the honest gaps.

## The live fallback test (owner: "check how the loop did on this switch")

Fable's weekly quota was reached mid-run. The loop's behavior across two runs, from the journal:

- **run-12 (fallback config only, no actuation flag):** detected Fable exhaustion correctly
  (seq 356, `fable_exhaustion_turnover_recorded`), but the recorded note was *"the mode did not
  authorize an automatic redispatch, so the owner-approved chain was never consulted."* It did
  the safe thing and paused. No switch.
- **run-14 (with `--authorize-turnover-actuation`):** detected exhaustion AND attempted the
  turnover — real progress. It walked the owner-approved chain `[claude-fable-5,
  claude-opus-4-8]` (from `config.toml [approved_models]`, which is correct), but the verdict
  was `no_approved_successor`, detail verbatim: *"NOTHING was probed: … no live probe seam is
  wired, so their availability is UNKNOWN … Exhaustion of the approved chain is a safe stop,
  not a fallback"* (D-023-R013 fail-closed: never continue on an unprobed model).

**Conclusion / correction of my earlier claim.** Automatic fallback needs THREE things, not
"one config line": (1) the approved chain [done — already correct in config.toml]; (2) the
`--authorize-turnover-actuation` R595 flag [done — now on every launch]; (3) the **live
launch-probe seam wired into the production start path** [NOT done — this is controller code,
the M0-T054/R595 family]. Without (3), the controller safe-stops rather than switch to a model
it has not test-launched. This is a genuine gap in the built machinery, and it is why the Aug-9
test also did not auto-switch.

## What I did keep running (D-036-R002 manual actuation)

Since Fable is exhausted and auto-actuation can't fire yet, I did what the owner did manually on
Aug 9: **pinned the worker directly to `claude-opus-4-8`** in `model_selection.toml`
(`model = "claude-opus-4-8"`, `fallback_models = []`; the validator rejects opus in both slots).
run-15 launched on opus (supervisor pid 10592, 16:09Z). This is the owner-authorized
opus-on-weekly-exhaustion (D-036-R002). **REVERT to `claude-fable-5` when Fable returns
(normally Thursday 9 PM, D-036-R001).** Note: the `xhigh` effort in R002 cannot be written into
supervisor config (D-004-R159 permanent bar); it binds at the account/CLI settings layer, which
is outside the controller — carried as invocation metadata, not a CLI flag.

## Autostart (D-036-R003) — needs your elevated run

The controller's own `install-autostart` generates INVALID boot XML (a `DeleteExpiredTaskAfter`
with no `EndBoundary` on a logon trigger — a controller bug, freeze-lane follow-up) and requires
admin, which I cannot self-elevate to. So I prepared a clean install you run as admin:

- Pinned launcher wrapper: `C:\SupervisorController\autostart-launch.ps1` — relaunches the loop
  detached ONLY if it is not already holding its lock, and reports failure so the retry fires.
- Elevated installer: `project-control/reports/D-036-install-autostart-ADMIN.ps1` — registers
  **NYCBuildabilitySupervisorBoot** (logon) and **NYCBuildabilitySupervisorWeeklyThursday**
  (Thu 9 PM local), both with **RestartInterval 4 min, RestartCount 50, StartWhenAvailable,
  HighestAvailable** — exactly R003's "try every 4 min up to 50x until running" and R001's
  "know when it's back."

Run it elevated:
`powershell -ExecutionPolicy Bypass -File "C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\reports\D-036-install-autostart-ADMIN.ps1"`

The ACTIVE-TASK block in the wrapper targets the loop's current task (M0-T153) and the
orchestrator updates it as the loop advances.

## Incident during execution (owned)

Running `install-autostart` (an audit-writing verb) while run-12 was still live forked the audit
hash chain at seq 560 (the exact "never run audit-writing verbs against a live run" rule).
Repaired with the sanctioned `tools/controller_update/repair_forked_audit_chain.py`
(evidence-preserving; forked files archived as `audit.jsonl.forked-evidence-20260907-160141`).

## Follow-up to contract (freeze lane / R595)

1. Wire the live launch-probe seam into the production start path so auto-fallback AND
   auto-return actually actuate (the real fix for D-036-R001/R002 unattended).
2. Fix the `install-autostart --kind boot` invalid-XML bug (DeleteExpiredTaskAfter/EndBoundary).
Both are supervisor-code tasks under the freeze rule; until (1) lands, the model switch is manual.
