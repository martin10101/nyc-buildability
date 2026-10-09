# Linux loop launch path (D-091 T2, M0-T166)

The Linux analog of the owner's Windows launch path (`docs/MRL_LAUNCH_RUNBOOK.md`
plus `tools/agent_supervisor/ps_tests`). Nothing here installs a unit, starts a
run, or contacts a provider. Commissioning and the live certified start are
owner-typed (runbook section 12 / D-091 T8) and are never run by an agent.

`launch_seam.select_launch_path("posix")` selects these artifacts on POSIX; on
Windows the same seam keeps the PowerShell path byte-unchanged.

## `launch.sh` - the launcher

A thin, fail-closed wrapper with five load-bearing guards (pinned by
`sh_tests/test_doc_check.sh`):

1. carries the Linux autoupdater belt `DISABLE_AUTOUPDATER=1` (D-091 T1);
2. fails closed (exit 3) when the claude binary is missing or not executable;
3. fails closed (exit 4) when a declared required env var is unset or empty;
4. runs the start gate and refuses (exit 5) to start when the gate refuses;
5. only on a passing gate hands the already-gated start to the controller.

It never pushes, never merges, and never starts a live run of its own. It is
environment-driven (`NYC_SUP_CLAUDE_BIN`, `NYC_SUP_GATE_CMD`, `NYC_SUP_START_CMD`,
`NYC_SUP_REQUIRED_ENV`) so the harness can drive it with fakes and no live
provider.

## `nyc-supervisor.service.template` - systemd unit TEMPLATE

A template with `<...>` placeholders, no `[Install]` section and `Restart=no`, so
a stray `systemctl enable` has no target. An owner substitutes the placeholders
and installs/enables it at commissioning; an agent never does.

### Control-group containment the start gate proves (M0-T177, B-027)

The unit is HARDENED so that systemd is the Linux kill-on-external-death
mechanism the M0-T052 G5 C1 safety property requires: when the main process dies
by any external means (SIGKILL/OOM), systemd stops the unit and tears down the
service control group, reaping the worker and every `setsid`/double-fork
descendant without anything inside the supervisor running, before any later
`start`. The in-process gate (`linux_containment.prove_systemd_containment`)
REFUSES dispatch unless `systemctl show` reports exactly these, so they are
load-bearing, not cosmetic:

- `KillMode=control-group` - stop kills the whole cgroup (`process`/`none` would
  leave descendants alive);
- `ExitType=main` - the unit's lifetime is tied to the main process dying;
- `SendSIGKILL=yes` - a member that ignores SIGTERM is still SIGKILLed;
- `TimeoutStopSec=15s` - a finite, short bound (the gate caps it at 60 s);
- `ProtectControlGroups=yes` - `/sys/fs/cgroup` read-only, so even a root member
  cannot rewrite its cgroup to escape the kill (the gate REQUIRES this when the
  unit runs as root).

**`NYC_SUP_START_CMD` must exec python directly.** `launch.sh` ends with
`exec $NYC_SUP_START_CMD` (line 88), and `exec` REPLACES the launcher's process
image while keeping the same PID. The chain is: systemd forks the unit, which
runs `/usr/bin/env bash launch.sh` - `env` execs `bash`, `bash` runs `launch.sh`,
and `launch.sh`'s final `exec` replaces that same PID with the start command. So
the unit's `MainPID` is whatever that final `exec` becomes. If
`NYC_SUP_START_CMD` is a DIRECT python invocation (e.g.
`.../python -m tools.agent_supervisor start ...`), `MainPID` is the python
controller and the gate's `MainPID == os.getpid()` check passes. If it were a
wrapper shell (`bash -c "python ..."`), `MainPID` would be that shell and the
real controller a child, so the gate would REFUSE. Confirmed: `launch.sh:88`
uses `exec`, so python is kept as `MainPID` provided the start command is a
direct python exec.

## `sh_tests/` - the bash shell-routing harness

The bash analog of `ps_tests`. The only honest carrier of a child's exit code is
`$?` read immediately after an UNPIPED invocation.

- `harness.sh` - `invoke_raw_exit <program> [args...]`, the raw-exit discipline;
- `run_sh_tests.sh` - runs every `test_*.sh` in its own `bash` process, fail-fast
  and fail-closed (no tests found is a failure);
- `test_raw_exit.sh` - the harness preserves the raw child exit code and fails
  closed when a command never launches;
- `test_mutants_detected.sh` - each mutant in `mutants/` loses or fakes the raw 7
  (pipe-through-tee and `$?`-after-an-intervening-command report 0; a grep pipe
  reports the last stage's code), proving the discipline is load-bearing;
- `test_doc_check.sh` - the living launcher carries every pinned fail-closed
  guard, and a copy with one removed is detected.

Run on this server with:

```
bash tools/agent_supervisor/linux/sh_tests/run_sh_tests.sh
```
