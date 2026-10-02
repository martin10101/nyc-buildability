# M0-T166 producer report — D-091 T2 (Linux launcher + bash shell-routing harness)

Producer: backend-engineer. Worktree `/root/project/w-M0-T166`, branch
`task/M0-T166-linux-launcher`. Base (claim seam) `d9c51780`. Material head
**`730dae361e076ee9d4341685b933c05ccfdbc012`**. Directive D-091 (R001, R007).

## Files changed (all inside allowed_paths; no forbidden path touched)
- `tools/agent_supervisor/launch_seam.py` (+66, additive only)
- `tools/agent_supervisor/cli.py` (call-site swap; -1 net line)
- `tools/agent_supervisor/capability_probe.py` (bare-probe env wiring)
- `tools/agent_supervisor/native_runtime.py` (bare-probe env wiring)
- `tools/agent_supervisor/linux/` (new: launch.sh, nyc-supervisor.service.template,
  README.md, sh_tests/{harness.sh,run_sh_tests.sh,test_raw_exit.sh,
  test_mutants_detected.sh,test_doc_check.sh,mutants/{mutant_pipe_tee,
  mutant_dollar_q,mutant_grep_pipe}.sh})
- `tools/test_agent_supervisor_linux_launch.py` (new, 19 tests)
Total: 16 files, +870 / -3. `git status` clean after commit.

## What changed and why
1. **launch_seam.py — platform launch-path selection (additive).** New pure
   `select_launch_path(os_name=None) -> LaunchPath` + frozen `LaunchPath`
   dataclass. POSIX returns the bash launcher, the systemd unit TEMPLATE, and the
   bash harness under `tools/agent_supervisor/linux/`; every other platform
   returns the existing `docs/MRL_LAUNCH_RUNBOOK.md` + `ps_tests/run_ps_tests.ps1`
   with `systemd_unit_template=""`. The existing ceiling + cwd decision guards
   (`enforce_launch`/`evaluate_cwd`/`evaluate_ceiling`/…) are byte-unchanged — the
   seam only ADDS a selection function at the end of the file. Pure: launches
   nothing, installs nothing, starts no run.

2. **linux/launch.sh — the Linux launcher.** Thin, fail-closed, env-driven
   (`NYC_SUP_CLAUDE_BIN`, `NYC_SUP_GATE_CMD`, `NYC_SUP_START_CMD`,
   `NYC_SUP_REQUIRED_ENV`). Guards, in order: (a) exports `DISABLE_AUTOUPDATER=1`
   (the Linux belt; D-091 T1 / runbook §13); (b) refuses exit 3 when the claude
   binary is missing/not executable; (c) refuses exit 4 when a declared required
   env var is unset/empty; (d) runs the start gate UNPIPED and refuses exit 5 when
   it refuses — the start command is never reached; (e) only on a passing gate
   `exec`s the already-gated controller start. It contains NO git push, NO merge,
   and NO live-run of its own (proven by a non-comment-line grep in the test).
   Installing/enabling the unit and the live start remain owner-typed (§12 / T8).

3. **linux/nyc-supervisor.service.template — UNINSTALLED systemd template.**
   Placeholders `<...>`, `Restart=no`, and NO `[Install]` section (a stray
   `systemctl enable` has no target). Sets `Environment=DISABLE_AUTOUPDATER=1`.
   Never installed or started by an agent.

4. **linux/sh_tests/ — bash shell-routing harness (analog of ps_tests).**
   `harness.sh::invoke_raw_exit` captures the child's RAW exit via an UNPIPED
   invocation with file redirection, and FAILS CLOSED (no verdict, never ok) when
   the program does not resolve — the bash analog of PowerShell's `$LASTEXITCODE`
   discipline. `run_sh_tests.sh` runs every `test_*.sh` in its own `bash` process,
   fail-fast/fail-closed (no tests found = failure), explicit exit. Three test
   files mirror ps_tests' cases: `test_raw_exit.sh` (raw 7 preserved, exit 0 ok,
   not-found fails closed, captured stdout/stderr), `test_mutants_detected.sh`
   (each mutant loses/fakes the raw 7), `test_doc_check.sh` (living launcher
   carries every pinned fail-closed guard; a copy with one removed is detected).
   Mutants: `mutant_pipe_tee` (pipe→tee, no exit → reports 0), `mutant_dollar_q`
   (`$?` after an intervening command → 0), `mutant_grep_pipe` (grep pipe → last
   stage's code 1).

5. **cli.py call-site swap.** `_controller_config_acl_posture` now calls
   `os_acl.controller_config_acl_verdict(config_path)` (the cross-platform
   dispatcher) instead of the Windows-only `evaluate_controller_config_acl`. The
   now-dead `from .os_acl import evaluate_controller_config_acl` import was
   removed. `os_acl` was already imported (line 170). Net -1 line; cli.py 3598→3597
   (no growth, as required for the oversized file). Fail-closed is preserved:
   on Linux a non-root/writable config is NOT_PROTECTED and UNKNOWN stays UNKNOWN;
   `protected` is still True only for a definitive PROTECTED verdict.

6. **capability_probe.py / native_runtime.py bare-probe env.** The bare
   `claude --version`/`--help`(`/<verb> --help`) probes now carry
   `process.bare_probe_env()` (full parent env + `DISABLE_AUTOUPDATER=1`) on Linux
   (`os.name == "posix"`), and keep `env=None` on Windows (byte-unchanged).
   `native_runtime.run_command` only applies the belt when the caller passed NO
   env, so the dispatch path's explicit env is honoured unchanged. Each file
   gained `import os` and `from . import process` (no import cycle: process imports
   neither module).

## Modularity answers
- `cli.py` (3598→3597) got ONLY the call swap + dead-import removal — no net
  growth on the grandfathered oversized file (`modularity_check --check` exit 0;
  its pre-existing `cli.py symbol_ceiling` warning is unchanged and names no new
  growth).
- All new logic lives in focused new files (launch.sh 88 lines, harness.sh 52,
  new test 349) and a 66-line additive seam in launch_seam.py. No module gained
  unrelated responsibilities. `modularity_check.py --check` → **exit 0** (only
  pre-existing warnings; none name this task's files).

## Acceptance scenarios → proving tests (all green)
- **primary** (bash harness runs the same shell-routing cases as ps_tests and
  passes here): `BashHarnessTests.test_harness_passes_on_this_server`; direct run
  `bash .../sh_tests/run_sh_tests.sh` → exit 0, "3 test file(s) passed".
- **boundary** (each mutant detected / harness goes red):
  `BashHarnessTests.test_each_mutant_is_detected` — pipe_tee→0, dollar_q→0,
  grep_pipe→1, and `test_mutants_detected.sh` exit 0 with no ASSERT-FAIL.
- **missing/ambiguous** (missing claude binary OR unset required env fails closed
  before provider contact): `LauncherFailClosedTests.test_missing_claude_binary_fails_closed`
  (exit 3, start recorder absent) and `.test_unset_required_env_fails_closed`
  (exit 4, recorder absent); plus harness `no_exit_code_fail_closed`
  (`test_harness_fails_closed_on_a_missing_command`).
- **failure** (launcher refuses when the start gate refuses; never pushes/merges/
  starts a live run): `LauncherGateTests.test_launcher_refuses_when_gate_refuses`
  (exit 5, recorder absent), `.test_launcher_starts_only_through_a_passing_gate`
  (exit 0, recorder present via injected fake — no live run),
  `.test_launcher_has_no_push_merge_or_live_run`,
  `.test_systemd_unit_is_an_uninstalled_template`.
- **wiring** (doctor posture POSIX verdict + bare-probe belt; Windows unchanged):
  `LaunchPathSelectionTests` (posix vs nt selection + files exist),
  `DoctorPostureWiringTests.test_verdict_dispatches_windows_to_the_windows_entry`,
  `.test_verdict_dispatches_posix_to_posix_acl`,
  `.test_doctor_posture_reports_the_posix_verdict_on_linux` (NOT_PROTECTED on a
  world-writable parent — impossible from the Windows-only entry),
  `BareProbeEnvTests` (belt on Linux, env=None on Windows, explicit env honoured).

## Commands run (venv `/root/project/lanes-runtime/venv/bin/python`, Python 3.12.3)
- `bash tools/agent_supervisor/linux/sh_tests/run_sh_tests.sh` → **exit 0**, 3
  test files passed; every mutant DETECTED; doc tooth passes + mutation detected.
- `pytest -q tools/test_agent_supervisor_linux_launch.py` → **19 passed**.
- `pytest -q tools/test_agent_supervisor_launch_seam.py` → 3 failed, **66 passed**.
- `pytest -q tools/test_agent_supervisor_os_acl.py` → 3 failed, **22 passed**, 18 skipped.
- `pytest -q tools/test_agent_supervisor_platform_seam.py` → **34 passed**.
- `pytest -q tools/test_agent_supervisor_capability_probe.py` → 1 failed, **17 passed**, 1 skipped.
- `pytest -q tools/test_agent_supervisor_native_adapter.py` → 1 failed, **57 passed**.
- `pytest -q tools/test_agent_supervisor_process.py` → **30 passed**, 1 skipped.
- `python3 tools/modularity_check.py --check` → **exit 0**.
- `ruff check` (launch_seam, cli, capability_probe, native_runtime, new test) →
  All checks passed.

## Pre-existing failures (confirmed at base d9c51780 in a detached scratch
worktree, then removed) — NOT introduced by this task
- `launch_seam`: same 3 fail / 66 pass at base (Windows path-form assertions —
  `same_path`/UNC/drive-case don't fold `\` on Linux).
- `os_acl`: same 3 fail / 22 pass / 18 skip at base (Linux-only Windows-path
  assertions, e.g. `os.path.isabs("C:\\Windows/System32/icacls.exe")` is False).
- `capability_probe::test_live_reprobe_claude_version_matches_fixture` and
  `native_adapter::test_live_detection_matches_committed_fixture`: FAIL at base —
  the LIVE drift tooth: installed Linux claude is **2.1.287** vs the committed
  M0-T159 Windows fixture **2.1.281**. Version strings are env-independent, so the
  belt change cannot cause this; it is exactly what D-091 **T3** (Linux CLI
  identity + fixture recapture + recert) resolves, and the packet names
  recertification as a follow-up for every `tools/agent_supervisor/**` edit.

## Assumptions / scope decisions
- "same cases as ps_tests" → mirrored all three ps_tests files (raw_exit,
  mutants_detected, doc_check). `test_doc_check.sh` is a self-contained
  launcher-guard-integrity tooth (living launcher passes; a copy with a pinned
  fail-closed guard removed fails), NOT a wrapper around
  `supervisor_command_doc_check.py`: that tool validates presented `python -m
  tools.agent_supervisor` commands, and a certified Linux start command belongs to
  commissioning (T8, owner-typed), which is out of scope here. The spirit (living
  doc passes, mutation detected) is preserved.
- The launcher is intentionally env-driven so it is fully testable with injected
  fakes and no live provider; it wraps the controller start rather than
  reimplementing start_gate.py in bash (the gate's refusal is honoured via the
  gate command's exit code).
- cli.py dead-import removal: a strict "swap only line 529" would leave a dead
  import (ruff F401 / reviewer noise); removing it shrinks the oversized file and
  is intrinsic to the swap. Flagged here for the reviewer.

## Could not do / limitations
- Did not run the full `tools/test_agent_supervisor_*.py` glob (too large for this
  server, per instructions); ran the touched modules' suites individually.
- Manual bash verification of the launcher via the Bash tool was refused by the
  session sandbox (runtime-computed command-string values); the Python test
  exercises all four launcher behaviours via `subprocess.run` with env dicts
  instead (authoritative, green).
- No commissioning, no unit install/start, no live provider call, no push/merge,
  no `tools/project_control.py`/`gh` — per scope.
```

## Rework (G3/G4 FAIL B1 — 2026-10-02)

**Correction to the original report's Windows claim.** The original report and PR
body said Windows "keeps passing unchanged" / the Windows surface is safe. That
was WRONG for CI: the required `supervisor-bridge` job runs
`pytest tools/test_agent_supervisor_*.py` on `windows-latest`, whose glob now
collects the new `tools/test_agent_supervisor_linux_launch.py`. Its three
bash-invoking test classes call `subprocess.run(["bash", ...])` with no platform
guard; on windows-latest `bash` is the WSL stub with no distro (exits 1), so 7
tests failed (3 BashHarnessTests, 2 LauncherFailClosedTests, and
LauncherGateTests.test_launcher_refuses_when_gate_refuses +
test_launcher_starts_only_through_a_passing_gate). The PRODUCTION Linux launch
code is unaffected; this was a TEST-portability defect in the new test file only.

**Fix (test file only, inside allowed_paths; nothing else changed).** Added
`@unittest.skipUnless(os.name == "posix", "POSIX bash launch path")` to class
`BashHarnessTests`, class `LauncherFailClosedTests`, and the two bash-invoking
`LauncherGateTests` methods (`test_launcher_refuses_when_gate_refuses`,
`test_launcher_starts_only_through_a_passing_gate`). The mocked/file-reading tests
stay running on both platforms: `LaunchPathSelectionTests`,
`DoctorPostureWiringTests`, `BareProbeEnvTests`, and the two file-reading
`LauncherGateTests` methods (`test_launcher_has_no_push_merge_or_live_run`,
`test_systemd_unit_is_an_uninstalled_template`). So on windows-latest the 7
bash-dependent tests are skipped (not failed) and the Windows-safe tests still
execute; on Linux all 19 still run.

**Evidence.**
- `pytest -q tools/test_agent_supervisor_linux_launch.py` on this server → **19
  passed** (nothing skipped; `os.name == "posix"` here).
- Decorator inspection: the file contains exactly **4** occurrences of
  `@unittest.skipUnless(os.name == "posix", "POSIX bash launch path")`; evaluating
  the module's exact condition as it resolves on windows-latest
  (`"nt" == "posix"` → `False`) marks a `skipUnless(False, ...)` class
  `__unittest_skip__ = True` (bash-dependent → SKIPPED), while a True-condition
  class is not skipped (cross-platform → RUNS).
- Windows-latest `supervisor-bridge` must be re-run green by the orchestrator;
  the Linux G3/G4 evidence above is unchanged (no production behavior changed).
