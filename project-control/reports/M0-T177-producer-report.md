# M0-T177 producer report — Linux systemd control-group containment + POSIX self-kill fix

Qualifying evidence: B-027 (reproduced defect); D-091-R001, D-091-R007.
Commit: `4a75244ba87eea63bd9a62c7daec04233e9c64a3` on `task/M0-T177-linux-containment`
(contract head `35bc5149`). Worktree `/root/project/w-M0-T177`. Producer: backend-engineer.

## Safety property preserved (proved, not asserted)

When the supervisor dies by any external means (SIGKILL/OOM), the worker AND every descendant
(incl. `setsid`/double-fork) end WITHOUT the supervisor running, before any later `start` can
dispatch. On Linux this is delivered by systemd tearing down the service control group on stop.
The gate PROVES from inside the process (reading `/proc/self/cgroup` + `systemctl show`) that the
process actually IS the main process of such a unit, and REFUSES otherwise. No fail-closed check
was weakened; `process_group`/`taskkill` are still refused. On this host the proof correctly
refuses (euid 0, cgroup is a `.scope`), so nothing is newly enabled here.

## What changed per file

- `tools/agent_supervisor/linux_containment.py` (was a placeholder): the pure, injectable proof.
  `prove_systemd_containment(pid, euid, cgroup_reader, show_runner, timeout, max_timeout_stop_usec)`
  returns a typed `ContainmentProof(ok, kind, reason, cgroup_path, unit)`. Checks, each a refusal
  with a precise reason: single `0::`-prefixed cgroup-v2 line ending in `.service`; `systemctl show`
  (bounded `process.run`, no shell) reporting `KillMode in {control-group, mixed}`, `ExitType=main`,
  `MainPID==pid`, `ControlGroup==own path`, `SendSIGKILL=yes`, finite bounded `TimeoutStopUSec`, and
  — only when `euid==0` — `ProtectControlGroups=yes`. Parsers: `parse_cgroup_v2_path`,
  `parse_show_output`, `parse_systemd_usec` (handles raw us and human timespans; infinity/zero/junk
  are unbounded->refused). `pid_in_service_cgroup(pid, expected)` for worker membership (fail-closed).
  TimeoutStop cap = **60 s** (`MAX_TIMEOUT_STOP_USEC`): above the template's 15 s so it passes with
  margin, below systemd's 90 s default so a unit left at the default is refused, forcing an explicit
  short bound that guarantees the reap finishes before a later start.
- `process.py`: `CONTAINMENT_SYSTEMD_CGROUP` + the one shared `CONTAINMENT_ACCEPT_SET`
  = `{job_object, systemd_cgroup}`. `default_containment_kind()` returns `systemd_cgroup` on POSIX
  only when the cached, re-entrancy-guarded proof holds, else `process_group` (Windows unchanged).
  `ProcessContainer` POSIX branch sets kind from the proof, stores the service cgroup, and on
  `adopt()` VERIFIES worker membership via `pid_in_service_cgroup` -> `verified_in_job`. `close()`
  on POSIX terminates each adopted worker's own group (kill-on-close parity). `terminate_process_tree`
  REFUSES (typed `refuse_self_group_kill`) to `killpg` the caller's own group. New helper
  `posix_session_kwargs()` = `{start_new_session: True}` on POSIX, `{}` on Windows. Test seams
  `set_systemd_containment_proof_for_testing`/`reset_systemd_containment_cache`.
- `claude_runner.py` (worker launch ~:1213, probe ~:1694): POSIX launches add
  `**posix_session_kwargs()` so each leads its own session. Windows byte-for-byte unchanged.
- `mrl_one_shot.py` (~:492): same `**posix_session_kwargs()` on the one-shot worker launch.
- `cli.py`: `containment_precondition()` accepts exactly `CONTAINMENT_ACCEPT_SET`; refusal text names
  the Linux hardened-`.service` requirement; `doctor`'s POSIX `_check_containment_default` reports the
  proved kind (systemd_cgroup vs process_group) and passes; audit/refusal detail carries `accepted`.
- `loop.py`: the post-cycle gate accepts `CONTAINMENT_ACCEPT_SET` (was `== job_object`); the
  `verified_in_job` gate reason generalized to both kinds. `turnover_wiring.py`: delegates to the
  bound precondition (same accept-set); `accepted` detail + reworded refusal text (no widening).
- `linux/nyc-supervisor.service.template`: added `KillMode=control-group`, `ExitType=main`,
  `SendSIGKILL=yes`, `TimeoutStopSec=15s`, `ProtectControlGroups=yes`; kept `Restart=no`, no
  `[Install]`, `DISABLE_AUTOUPDATER=1`. Documented that `NYC_SUP_START_CMD` must exec python directly.
- `linux/README.md`: new subsection on the five load-bearing directives + the MainPID/exec chain.
- `.github/workflows/ci.yml`: ONE additive `supervisor-linux-containment` ubuntu job (existing jobs
  untouched; SHA-pinned actions + hash-pinned pytest copied from `supervisor-bridge`): runs the
  containment file (incl. R1/R2), POSIX process + launch tests, and an opt-in `NYC_SUP_R3_SYSTEMD=1`
  R3 step.
- `docs/D091_LINUX_COMMISSIONING.md`: steps 3-4 updated for the hardened unit, the `systemctl show`
  verification, and the direct-python-exec MainPID requirement (template/cli line refs resynced).
- Tests: `tools/test_agent_supervisor_linux_containment.py` (new suite), plus `_loop.py` (2 systemd
  cycle tests + mutation note), `_start_reentry.py` (accept-set assertion + a systemd dispatch test).

## MainPID chain confirmation (asked in the packet)

`ExecStart=/usr/bin/env bash .../launch.sh`; `launch.sh:88` ends with `exec $NYC_SUP_START_CMD`.
`exec` replaces the process image while keeping the PID, so the chain env->bash->launch.sh->(exec)->start
keeps ONE pid. If `NYC_SUP_START_CMD` is a direct `python -m tools.agent_supervisor start ...`, the
unit's MainPID IS that python controller and `MainPID==os.getpid()` holds. A wrapper shell
(`bash -c "python ..."`) would make the shell MainPID and the controller a child -> gate REFUSES.
The template and README now require the direct exec. Confirmed `launch.sh:88` uses `exec`.

## Acceptance scenarios -> tests -> result (all GREEN unless noted)

Test module `tools/test_agent_supervisor_linux_containment.py` unless prefixed otherwise.

- S1 proved / start dispatches / cycle proceeds:
  `PositiveProofTests::{test_a_valid_service_cgroup_and_show_prove_containment,
  test_root_with_protect_control_groups_proves, test_mixed_kill_mode_proves,
  test_raw_microsecond_timeout_proves, test_default_containment_kind_is_systemd_cgroup_when_proved,
  test_container_reports_systemd_cgroup_and_verifies_membership,
  test_start_gate_accepts_a_proved_systemd_host}`;
  `_start_reentry.py::ContainmentGateTests::test_a_proved_systemd_cgroup_host_permits_the_dispatch`
  (start dispatches, ends in honest `no_valid_checkpoint`);
  `_loop.py::AchievedContainmentTests::test_systemd_cgroup_containment_proceeds_normally`. -> PASS.
- S2 refused, one each: `NegativeRefusalTests::{test_cgroup_v1_or_hybrid_is_refused,
  test_a_scope_or_user_session_path_is_refused, test_kill_mode_process_is_refused,
  test_kill_mode_none_is_refused, test_exit_type_cgroup_is_refused, test_main_pid_mismatch_is_refused,
  test_control_group_mismatch_is_refused, test_send_sigkill_no_is_refused,
  test_timeout_infinity_is_refused, test_timeout_above_cap_is_refused, test_timeout_garbled_is_refused,
  test_systemctl_missing_is_refused, test_systemctl_nonzero_is_refused,
  test_systemctl_timed_out_is_refused, test_systemctl_garbled_partial_output_is_refused,
  test_unreadable_cgroup_is_refused, test_root_without_protect_control_groups_is_refused,
  test_a_worker_in_a_foreign_cgroup_is_not_verified, test_process_group_host_refuses_at_the_start_gate,
  test_taskkill_host_refuses_at_the_start_gate}`; foreign-cgroup -> unverified also at the loop:
  `_loop.py::AchievedContainmentTests::test_systemd_cgroup_unverified_membership_stops_containment_unverified`;
  process_group/taskkill dispatch refusals also:
  `_start_reentry.py::ContainmentGateTests::{test_a_posix_process_group_host_refuses_to_dispatch,
  test_a_windows_taskkill_fallback_host_refuses_to_dispatch}`. -> PASS.
- S3 mutation: see "Mutation evidence" — all five demonstrated RED then restored GREEN.
- S4 self-kill R1: `LinuxContainmentRealProcessTests::test_R1_timeout_kill_spares_the_harness_and_worker_has_its_own_group`
  -> PASS (3.19 s; harness exited 0, worker pgid != harness pgid).
- S5 R2 why process_group refused:
  `LinuxContainmentRealProcessTests::test_R2_group_kill_of_harness_leaves_a_setsid_grandchild_alive`
  -> PASS (1.87 s; setsid grandchild survived the harness group-kill, then cleaned up).
- S6 R3 real unit: `R3RealSystemdUnitTests::test_R3_kill_of_main_pid_reaps_the_whole_control_group`
  -> SKIPPED here (env-gated `NYC_SUP_R3_SYSTEMD`; NEVER run by an agent on this host). Runs in the new
  ubuntu CI job's opt-in step. NOT executed locally.
- S7 regression / freeze baseline (>=1165, 0 failures, windows): see "Suite" — the full-suite
  windows baseline is a CI responsibility; it cannot run on this host.

## Mutation evidence (each guard reverted locally -> RED, then restored -> GREEN)

Performed against committed HEAD `4a75244b`; each guard reverted, the target test run RED, then
`git checkout -- <file>` restored. Tree is clean (0 changed) and all restored tests re-pass.

1. Gate accepting process_group — `cli.containment_precondition` widened to accept `process_group`:
   `_start_reentry.py::ContainmentGateTests::test_a_posix_process_group_host_refuses_to_dispatch` +
   `NegativeRefusalTests::test_process_group_host_refuses_at_the_start_gate` -> 2 FAILED. (Constant
   also pinned by `MutationGuardTests::test_accept_set_is_exactly_the_two_kill_on_death_kinds`.)
2. Loop accept-set widened — loop gate `and achieved != "process_group"`:
   `_loop.py::AchievedContainmentTests::test_process_group_containment_also_fails_closed` -> 1 FAILED.
3. MainPID check dropped — `if False and main_pid != this_pid`:
   `NegativeRefusalTests::test_main_pid_mismatch_is_refused` +
   `MutationGuardTests::test_main_pid_guard_is_load_bearing` -> 2 FAILED.
4. Own-process-group kill guard removed — `if False and target_group == os.getpgrp()`:
   `MutationGuardTests::test_terminate_process_tree_refuses_to_kill_our_own_group` -> 1 FAILED
   ("ProcessError not raised").
5. start_new_session removed from the worker launch — dropped `**posix_session_kwargs()`:
   `LinuxContainmentRealProcessTests::test_R1_...` -> FAILED (harness hung 30 s: the shared-group
   worker is refused by guard #4, so it never dies and the harness never finishes — proving both the
   session isolation and the self-group guard are load-bearing).

## Suite commands and counts

The packet's suite command `python3 -m pytest -q -p no:cacheprovider tools/test_agent_supervisor_*.py
-k "not RealProcess"` **cannot run on this host**: it is KILLED with exit 137 (OOM) partway through
(the documented exit-137 history; `tools/test_agent_supervisor_model_chain.py` alone OOMed here even
with `-k "not RealProcess"`). I therefore ran the affected/consumer files individually with the venv
python `/root/project/lanes-runtime/venv/bin/python -m pytest -q -p no:cacheprovider <file> -k "not RealProcess"`:

| file | result |
|---|---|
| test_agent_supervisor_linux_containment.py (`-k "not RealProcess"`) | 38 passed, 1 skipped (R3), 2 deselected (R1/R2) |
| test_agent_supervisor_linux_containment.py R1 (single id) | 1 passed (3.19 s) |
| test_agent_supervisor_linux_containment.py R2 (single id) | 1 passed (1.87 s) |
| test_agent_supervisor_process.py | 30 passed, 1 skipped |
| test_agent_supervisor_start_reentry.py | 17 passed |
| test_agent_supervisor_runner.py | 78 passed (25 subtests) |
| test_agent_supervisor_loop.py | 126 passed, **3 pre-existing failed** |
| test_agent_supervisor_model_chain.py (`-k "not RealProcess"`) | 14 passed, **8 pre-existing failed** |
| test_agent_supervisor_r595_actuation.py | 19 passed |
| test_agent_supervisor_mrl_launch_path.py | 52 passed |
| test_agent_supervisor_recovery_probes.py | 88 passed (26 subtests) |
| test_agent_supervisor_linux_launch.py | 19 passed |
| test_agent_supervisor_mrl_one_shot.py | 64 passed |

Ruff: `ruff check` on all edited supervisor + new test files -> All checks passed (ruff is NOT
configured for `tools/` — only `services/api` has a config — so this is advisory, run with the venv
ruff at default settings). Modularity: `python tools/modularity_check.py --check` -> exit 0 (only
pre-existing warnings; cli.py symbol_ceiling is a pre-existing signal; the new `linux_containment.py`
is not flagged; cli.py/loop.py were not grown unjustifiably — logic lives in
linux_containment.py/process.py). YAML: ci.yml parses; new job has 6 steps on ubuntu-latest.

## The 11 pre-existing failures are NOT mine (proved at the base)

The 3 loop + 8 model_chain failures are the documented pre-existing Linux-only containment class:
on an unhardened `process_group` host the start gate refuses (exit 12 UNSUPPORTED_PLATFORM) or the
post-cycle gate stops `containment_degraded`, so no real worker dispatches. None of them patches the
host to a contained kind; they pass only on windows-latest (job_object). I restored the base source
(`git checkout 35bc5149 -- <6 .py>`) and ran the exact 11 ids: **all 11 FAILED identically at the
base**, then restored HEAD (tree clean). `git show 35bc5149:tools/agent_supervisor/cli.py` confirms
the base refusal path (`kind == CONTAINMENT_JOB_OBJECT`, `UNSUPPORTED_PLATFORM`) is byte-identical in
effect for `process_group`. My change does not alter their outcome (an unhardened host is correctly
still refused). The new ubuntu CI job deliberately does NOT run loop/model_chain for this reason.

## Deviations from the trace / not done

- No design point in the trace was found wrong; the property was preserved exactly. One addition
  beyond a literal reading: `ProcessContainer.close()` on POSIX now also terminates the worker's own
  group (kill-on-close parity, as the packet's `terminate_all/close` bullet requires), guarded by the
  self-group refusal so it can never touch the supervisor's group.
- The full-suite windows freeze baseline (>=1165, 0 failures) is NOT established here — the suite
  OOMs on this Linux host and the Windows path cannot run here. It is a CI responsibility
  (windows-latest `supervisor-bridge` + the new ubuntu `supervisor-linux-containment` job). My changes
  keep Windows byte-for-byte unchanged (Job Object path, terminate_process_tree Windows branch,
  doctor Windows branch, `posix_session_kwargs()` empty on nt); all new POSIX/real-process tests are
  POSIX-gated or env-gated so they add skips (not failures) on windows-latest.
- R3 was NOT run on this host (host-safety; env-gated). It runs in the new CI job.
- No push, no `tools/project_control.py`, no dependency change. Only project-control write is this
  report.

END-OF-REPORT
