# Producer report — M0-T165 (D-091 T1): Linux platform seam for the loop controller

Producer: backend-engineer. Worktree `/root/project/w-M0-T165`, branch
`task/M0-T165-linux-platform-seam`. Claim-seam HEAD `1d22a07a`. Directive refs
D-091-R001, D-091-R007.

## What changed and why

Three Windows-only controller seams were made to work on Linux WITHOUT weakening them,
Windows behavior byte-identical. New logic lives in the two new modules; the edits to
os_acl/config/process are thin, additive, platform-checked seams.

New modules:
- `tools/agent_supervisor/posix_acl.py` (180 lines) — the POSIX analogue of os_acl.
  Reuses os_acl's verdict dataclasses (`AclVerdict`, `ControllerConfigAclVerdict`) and
  states (PROTECTED/NOT_PROTECTED/UNKNOWN), so the verdict SHAPE is literally the same
  os_acl gives on Windows. OK (PROTECTED) only for a root-owned (uid 0), not group- or
  world-writable config, in a root-owned, not group/world-writable parent, no symlinks;
  otherwise NOT_PROTECTED or UNKNOWN, each with a named reason. Fail-closed: missing
  config, unreadable stat/owner, or a non-POSIX platform -> UNKNOWN, never read as
  protected. The stat/owner lookup (`lstat`) and the platform decision (`is_posix`) are
  injectable so every verdict is testable without root and on any host.
  - Why root-ownership = the Windows elevated-owner requirement: on POSIX the file owner
    can always chmod their own file, so a 0444 config owned by a non-root user is still
    effectively writable by that user — the POSIX analogue of a non-elevated Windows
    owner retaining implicit WRITE_DAC (os_acl G5 L-1). group/world-write = the DACL
    "no unprivileged write right" clause; owner(root) write is the expected elevated
    action. symlink = active bypass -> NOT_PROTECTED (safer direction, mirrors os_acl's
    "a writable probe beats a clean ACL"). Scope = file + immediate parent, same as os_acl.
- `tools/agent_supervisor/platform_paths.py` (114 lines) — one resolver for the
  config/activation/runtime default locations. POSIX: config `/etc/nyc-supervisor/config.toml`,
  activation `($XDG_CONFIG_HOME or ~/.config)/nyc-supervisor/ctl24-activation/`, manifest
  `controller_manifest.json` inside it (filename from manifest.MANIFEST_FILENAME, no drift).
  Windows branch byte-matches the runbook locations (%ProgramFiles%\SupervisorConfig,
  %LOCALAPPDATA%\NYCBuildabilitySupervisor\ctl24-activation). No Windows path (`C:\`,
  `%LOCALAPPDATA%`) is ever returned on POSIX. runtime_base_dir() DELEGATES to
  durable_state.runtime_base_dir (already cross-platform, keyed by checkout-path hash) —
  not reimplemented, so it cannot drift. `os_name`/`environ` injectable.

Edits (additive, behind a platform check, no existing behavior changed):
- `os_acl.py` — added `controller_config_acl_verdict(config_path)`: on POSIX delegates to
  posix_acl (lazy import, no import cycle), else the existing Windows `evaluate_controller_config_acl`.
  The existing `evaluate_controller_config_acl`/`evaluate_file`/`evaluate_directory`
  functions are UNCHANGED (only the docstring of the Windows entry clarified), so every
  existing os_acl test keeps its exact behavior. Design choice: I deliberately did NOT make
  the existing single entry point dispatch, because the existing Linux tests
  (`test_combined_verdict_protected_requires_both`, the three FailClosedTests) pin the
  Windows combine/platform-guard behavior via monkeypatch and temp files; dispatching inside
  those functions would flip currently-passing Linux tests. The additive entry is the
  cross-platform seam a caller (e.g. cli `_controller_config_acl_posture`) adopts. See
  Limitations.
- `config.py` — added `default_config_path(os_name=None)` delegating to
  platform_paths.default_config_path (lazy import). A Linux launcher/runbook resolves the
  config default here instead of hardcoding a Windows path; callers still pass explicit --config.
- `process.py` — added `AUTOUPDATER_DISABLE_ENV` constant (now the single source of the
  name, referenced by the existing `FORCED_CLAUDE_CHILD_ENV`, value byte-identical), plus
  `posix_autoupdater_belt(os_name=None)` -> {DISABLE_AUTOUPDATER:'1'} on POSIX / {} on Windows,
  `bare_probe_env(parent_env, os_name=None)` (full parent env + belt on POSIX, the explicit
  env a bare version/help probe uses instead of env=None), and
  `apply_posix_autoupdater_belt(environ=os.environ, os_name=None)` (forces the belt into the
  controller's own process env on POSIX so the two bare probes, which launch with env=None
  and inherit the parent env, pick it up — the Linux analogue of the Windows machine-scope
  belt in runbook §13). Forced value WINS over a conflicting prior value, mirroring
  claude_child_env's "the forced pair wins". No-op on Windows (Windows keeps claude_child_env
  + the machine-scope variable unchanged). Nothing mutates os.environ at import.

## Modularity (docs/CODE_MODULARITY_POLICY.md)

`python3 tools/modularity_check.py --check` -> exit 0 (warnings pre-existing, none name my
files). New logic is in the two new modules (posix_acl 180, platform_paths 114 — well under
WARN 600). Edited files: os_acl 473->496, config 679->690, process 813->871 raw lines; SLOC
stays under the 600 warn threshold and none is flagged. Public imports preserved (purely
additive; existing symbols unchanged). No file split needed.

## Acceptance scenarios and the test that proves each
Test file: `tools/test_agent_supervisor_platform_seam.py` (34 tests; injection-based so it
also passes on the windows-latest CI runner — no root, no real OS dependence).

- primary ("root-owned 0444 config in root-owned 0755 dir gives the same OK verdict shape"):
  PosixAclOkTests.test_root_owned_0444_in_root_owned_0755_is_protected (PROTECTED, both file
  and parent) + VerdictShapeParityTests.test_posix_verdict_reuses_the_os_acl_dataclasses /
  test_to_dict_shape_matches_os_acl (same dataclasses + same to_dict keys as os_acl).
- boundary ("group/world-writable config, or writable parent, fails closed with a named
  reason"): PosixAclBoundaryTests — group-writable, world-writable, non-root-owned config,
  writable parent, non-root-owned parent. Each flips ONE field of the OK baseline so each
  clause is proven load-bearing; each asserts NOT_PROTECTED, the named reason, and
  not is_protected().
- missing/ambiguous ("missing config, unreadable owner, or unknown platform -> UNKNOWN, fail
  closed"): PosixAclUnknownTests — missing config (lstat FileNotFoundError), unreadable owner
  (lstat PermissionError), unknown platform (is_posix=False). All UNKNOWN, not is_protected().
- failure ("symlinked config or parent fails closed"): PosixAclSymlinkTests — symlinked
  config and symlinked parent, both NOT_PROTECTED with "symlink" reason, not is_protected().
- regression ("existing tests still pass; Windows code paths unchanged"): existing os_acl
  behavior preserved (see counts); VerdictShapeParityTests.test_every_non_protected_verdict_reads_not_protected
  pins the safety invariant; ControllerConfigAclDispatchTests proves the additive dispatcher
  routes POSIX->posix_acl and non-POSIX->the Windows entry without touching the existing
  functions.

Extra (objective items beyond the 5 packet scenarios):
- platform paths: PlatformPathsTests (8) — POSIX config = /etc, no Windows marker; Windows
  config uses %ProgramFiles%; activation prefers XDG_CONFIG_HOME, falls back to ~/.config;
  Windows uses %LOCALAPPDATA% and fails closed (ValueError) when unset; manifest inside
  activation dir; runtime_base_dir delegates to durable_state.
- autoupdater belt: AutoupdaterBeltTests (8) — belt set on POSIX / empty on Windows;
  bare_probe_env keeps parent env + adds belt on POSIX, none on Windows, forced value wins;
  apply_posix_autoupdater_belt mutates POSIX env (returns True), no-op on Windows (returns
  False), forces over a conflicting existing value.

## Commands and counts (venv /root/project/lanes-runtime/venv/bin/python, Python 3.12.3)

- New tests: `pytest -q tools/test_agent_supervisor_platform_seam.py` -> **34 passed** (0.16s).
- Regression, run as CI's glob but BATCHED (the full `tools/test_agent_supervisor_*.py` glob
  OOM-kills on this 8 GB box — exit 137 — exactly why CI pins the suite to windows-latest;
  design doc §(CI note): the ubuntu run "starved the hosted runner to death"):
  - os_acl + process: 3 failed, 52 passed, 19 skipped. The 3 failures are PRE-EXISTING
    Linux-only Windows-path assertions, identical to the pre-change baseline (captured before
    editing: os_acl alone = 3 failed / 64 passed / 19 skipped; the same three:
    FailClosedTests.test_clean_acl_but_writable_probe_is_not_protected,
    AbsoluteToolPathTests.test_query_owner_uses_absolute_system32_powershell,
    AbsoluteToolPathTests.test_run_icacls_uses_absolute_system32_path). No NEW failure.
  - process + claude_runner_env + phase1: 122 passed, 1 skipped.
  - codex_channel: 56 passed. manifest_binding: 32 passed, 1 skipped.
  - model_chain: OOM-killed (exit 137) at RUNTIME even isolated — a pre-existing environment
    memory limit, NOT a regression: it collects cleanly (25 tests, imports fine) and does not
    reference any of my new/changed functions (grep count 0). `python -c import` of all five
    changed/new modules => "all 5 import clean, no cycle".
- `python3 tools/modularity_check.py --check` -> exit 0 (pre-existing warnings only; none name
  my files). `py_compile` of all six files -> OK.

## Assumptions
- OK/FAIL/UNKNOWN in the objective map to os_acl's PROTECTED/NOT_PROTECTED/UNKNOWN; I reuse
  os_acl's dataclasses so the shape is identical rather than a parallel copy.
- POSIX config default `/etc/nyc-supervisor/config.toml` and activation under
  `~/.config/nyc-supervisor/ctl24-activation/` per design doc §1 row 2 (it gives these as
  examples); the Windows locations match the runbook exactly.
- Root-ownership (uid 0) is the POSIX requirement corresponding to the Windows elevated-owner
  requirement (owner can chmod regardless of mode).

## Limitations / what I could not do (in scope honesty)
- The additive `os_acl.controller_config_acl_verdict` is the cross-platform entry; wiring the
  consumer `cli.py::_controller_config_acl_posture` to call it on Linux is NOT done here —
  cli.py is outside this task's allowed_paths. Until that one-line consumer change (a task
  that owns cli.py), the Linux doctor posture still reports UNKNOWN via the Windows-only
  entry. I chose the additive seam specifically to keep every existing os_acl test green
  (dispatching inside the existing functions would flip currently-passing Linux tests I may
  not edit).
- DISABLE_AUTOUPDATER on Linux: process.py provides the belt + bare_probe_env +
  apply_posix_autoupdater_belt, but the bare probes `capability_probe._run` and
  `native_runtime.run_command` (which launch with env=None) and the systemd/launch unit are
  outside this task's allowed_paths (T2 launch-seam scope). The in-process belt makes those
  env=None-inheriting probes pick up DISABLE_AUTOUPDATER=1 once the Linux controller
  bootstrap/launcher calls apply_posix_autoupdater_belt(); that call site is T2.
- No live loop started, no provider call, no real config outside the repo touched, no
  dependency added, no fail-closed check weakened, no push/merge/gh/project_control.py.
- Full-suite regression could not run in one process on this box (OOM); evidence is batched +
  import-clean + the os_acl/process baseline diff. The authoritative full-suite run is CI's
  windows-latest job.

Requested status: awaiting_gate.
END-OF-REPORT
