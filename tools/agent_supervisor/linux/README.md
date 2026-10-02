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
