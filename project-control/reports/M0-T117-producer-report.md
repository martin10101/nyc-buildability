# M0-T117 — Producer report

Task: M0-T117 — D-024 Amendment 13 unit Q: `DISABLE_AUTOUPDATER=1` control for
controller-launched Claude workers + standing admission-event discipline.
Producer: backend-engineer. Requested status: **awaiting_gate**.
Qualifying evidence (supervisor-freeze §2/§3): **D-024-R278** (also AD-093 provider CLI
drift, reproduced live at seq-30: installed 2.1.251 vs certified 2.1.248).

Worktree verified: `git -C C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t117 rev-parse
--show-toplevel` → `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t117` (exact). All edits
and commands targeted that worktree.

## What changed and why

The controller is certified against one exact Claude CLI identity; a silent CLI
auto-update breaks it (seq-30 drift). This task makes every claude child the supervisor
launches **with a constructed environment** carry `DISABLE_AUTOUPDATER=1` unconditionally,
so the CLI cannot update in the background mid-run, and documents the standing discipline
that future upgrades are deliberate admission events.

### Covered / uncovered set (precise, after the G3-8 correction)

Injection-forced (every claude launch that builds its env via `claude_child_env`):
worker launch (`claude_runner.ClaudeRunner.run_unit`), model-availability probe
(`claude_runner.probe_model_launch`), the `doctor --live` control-response probe run
inside the certification window (`preflight.control_response_round_trip`), and the
turnover successor launch — worker redispatch AND orchestrator/handoff start alike
(`turnover_adapters.SupervisorLauncher._build_invocation`).

NOT injection-forced (inherit the FULL parent env; covered by the owner machine-scope
belt): the two bare `claude --version`/`--help` capability probes —
`capability_probe.py::_run` (~line 99, no `env=`) and `native_runtime.py::_run`
(~line 101, `env=None`). These are outside allowed_paths and are the documented
exclusion; a version/help check needs the real PATH, so they are deliberately not
env-stripped. G3 Finding-4 fact: `minimal_env`'s allowlist STRIPS `DISABLE_AUTOUPDATER`
(not on `DEFAULT_ENV_ALLOWLIST`), which is exactly why the code-side forced injection
must exist for the constructed-env launches — the two belts are complementary.

### Files changed (exact paths)

1. `tools/agent_supervisor/process.py` — new claude-scoped seam:
   - `FORCED_CLAUDE_CHILD_ENV = {"DISABLE_AUTOUPDATER": "1"}` constant.
   - `claude_child_env(extra, allowlist)` — `minimal_env(...)` then
     `env.update(FORCED_CLAUDE_CHILD_ENV)` applied LAST (after allowlist + extra), so
     neither the allowlist nor a config `extra_env` can drop or override it.
   - `minimal_env` itself is UNCHANGED, so codex children (which call `minimal_env`)
     are untouched (claude-scoped only).
2. `tools/agent_supervisor/claude_runner.py` — both claude Popen sites now build the
   child env with `claude_child_env(...)` instead of `minimal_env(...)`:
   - worker launch in `ClaudeRunner.run_unit` (was ~1102);
   - probe launch in `probe_model_launch` (was ~1547).
   - import updated: `minimal_env` → `claude_child_env` (minimal_env no longer used in
     this module). One small shared helper, no duplicated logic (modularity policy;
     claude_runner is already ~1766 lines).
3. `tools/agent_supervisor/preflight.py` — G3-2 rework: `control_response_round_trip`
   (the `doctor --live` control-response probe) now builds its Popen env with
   `claude_child_env()` instead of `minimal_env()`; import updated. This probe runs
   the real claude executable inside the certification window.
4. `tools/agent_supervisor/turnover_adapters.py` — G3-3 rework:
   `SupervisorLauncher._build_invocation` builds the successor env with
   `claude_child_env({...})` instead of `minimal_env({...})` (import updated). The
   existing `SUPERVISOR_SUCCESSOR_EFFORT` / `SUPERVISOR_SESSION_ROLE` pairs are
   preserved; the forced control pair is applied last. Covers both WORKER and
   ORCHESTRATOR successor layers.
5. `tools/test_agent_supervisor_claude_runner_env.py` — NEW test module, now 12 tests
   (round 1: 8 = 2 injection-path + 4 seam + 2 codex-scope; this rework: 4 = G4-F6
   allowlist re-enable vector + 1 preflight seam + 2 turnover seam [worker+orchestrator]).
6. `tools/test_agent_supervisor_process.py` — +2 tests (the minimal_env-level
   assertions that belong at that seam: minimal_env must NOT inject the control;
   claude_child_env forces it and overrides a conflicting extra_env).
7. `tools/agent_supervisor/README.md` — "Claude Code version admission events" section
   (now states the exact covered/uncovered set + the G3-4 allowlist-strip fact).
8. `docs/CONTROLLER_UPDATE_RUNBOOK.md` — section 13 (admission-event discipline + owner
   command pack; now states the exact covered/uncovered set + the G3-4 fact).
9. `project-control/reports/M0-T117-producer-report.md` (this file) +
   `project-control/reports/M0-T117-autoupdater-evidence.md`.

`tools/test_agent_supervisor_recovery_probes.py` and
`tools/test_agent_supervisor_turnover_live_seam.py` were in the extended allowed_paths
but did not need changes — the new seam tests live in the single injection module (the
coordinator's preferred location) and both existing packs still pass unmodified.

All edits are within the packet `allowed_paths`. No fixtures, no `.claude/**`, no
journal/runtime/protected config touched. No `tools/project_control.py`, no git commit/
push, no `gh`, no branch changes, no new dependencies.

## AS-6 fail-closed choice

**The forced pair wins** (not a typed refusal). If `extra_env` supplies a conflicting
`DISABLE_AUTOUPDATER` (e.g. `"0"`), `claude_child_env` overrides it back to `"1"`.
Rationale: the guarantee is that NO input ever yields a supervisor-constructed claude
child without `DISABLE_AUTOUPDATER=1`. An unconditional forced value delivers that for
every input; a launch-time refusal is strictly weaker (fails the launch on a config
typo, and adds an error path that could itself regress to fail-open). Documented in the
`claude_child_env` docstring and the evidence report.

## Acceptance-scenario mapping

| AS | Scenario | Test |
|----|----------|------|
| AS-1 | Worker launch injects even when parent env + allowlist omit it | `...claude_runner_env.py::ClaudeChildEnvInjectionTests::test_as1_...` (intercepts real Popen at the worker site) |
| AS-2 | Probe launch injects identically | `...::ClaudeChildEnvInjectionTests::test_as2_probe_launch_injects_identically` (intercepts real Popen at the probe site) |
| AS-3 | No collateral env change (byte-identical except the one key) | `...::ClaudeChildEnvSeamTests::test_as3_no_collateral_change_vs_minimal_env` + `test_as3_only_difference_is_the_single_forced_key` |
| AS-4 | Removal sensitivity (red before green) | evidence report — red/green + injection-line-removed red proof (both original and new seams) |
| AS-5 | Codex untouched | `...::CodexScopeTests::test_as5_shared_minimal_env_does_not_inject_the_control` + `test_as5_codex_channel_still_uses_the_uninjected_builder`; also `process.py::test_minimal_env_does_not_inject_the_claude_autoupdater_control` |
| AS-6 | extra_env conflict cannot disable it (forced pair wins) | `...::ClaudeChildEnvSeamTests::test_as6_extra_env_conflict_is_overridden_forced_pair_wins` + `test_as6_unrelated_extra_env_still_passes_through`; also `process.py::test_claude_child_env_forces_the_autoupdater_control` |
| G3-2 (rework) | `doctor --live` control-response probe injects | `...::DoctorLiveProbeEnvTests::test_control_response_round_trip_injects_the_control` (intercepts real Popen in `preflight`) |
| G3-3 (rework) | Turnover successor launch injects for BOTH layers, preserving effort/role pairs | `...::TurnoverSuccessorEnvTests::test_worker_successor_env_injects_and_preserves_existing_pairs` + `test_orchestrator_successor_env_injects_the_control` |
| G4-F6 (rework) | Allowlist re-enable vector (allowlist contains the var + parent "0") still yields "1" | `...::ClaudeChildEnvSeamTests::test_g4f6_allowlist_reenable_vector_is_overridden` |

## Test counts (exact)

- Injection module + process + the two extended-scope packs (green):
  `python -m pytest tools/test_agent_supervisor_claude_runner_env.py tools/test_agent_supervisor_process.py tools/test_agent_supervisor_recovery_probes.py tools/test_agent_supervisor_turnover_live_seam.py -q`
  → **221 passed, 1 skipped**.
- Injection module alone: **12 passed** (8 from round 1 + G4-F6 + preflight seam + 2 turnover seams).
- `test_agent_supervisor_process.py`: 30 passed, 1 skipped (+2 new this task, round 1).
- Full supervisor suite:
  `python -m pytest tools/test_agent_supervisor_*.py -q`
  → **2726 collected, 2721 passed, 3 failed, 2 skipped** (188s).
  - Collected = baseline 2712 + 14 new (10 from round 1 + 4 from this rework:
    G4-F6, preflight seam, worker successor, orchestrator successor).
  - The 3 failures are ALL the pre-existing live drift tooth (installed 2.1.251 vs
    fixture 2.1.248, AD-093), in `capability_probe`, `event_bus`, `native_adapter`;
    out of scope (M0-T118), NOT fixed or touched. Deviation from packet: packet named
    one such test; there are three, all the same cause.

Red/green (incl. AS-4 removal sensitivity) captured verbatim in
`project-control/reports/M0-T117-autoupdater-evidence.md`.

## Lint

CI ruff (`.github/workflows/ci.yml`) runs with `working-directory: services/api`, so it
lints only `services/api/**`, NOT `tools/**`. Local `ruff 0.13.0` on the six changed
Python files (process, claude_runner, preflight, turnover_adapters, and the two test
modules) is clean except a PRE-EXISTING `F401 import json` in
`test_agent_supervisor_process.py` (line 18) that this task did not introduce and left
untouched to stay in scope; that import is used only inside fake-executable string
literals. It is not CI-gated (tools/ is outside the ruff working dir).

## Environment / owner boundary

- The forced per-child injection is code-side and needs no owner action.
- The machine-scope Windows env var (`DISABLE_AUTOUPDATER=1` at Machine scope) is
  OWNER-ONLY (R288) — the exact Administrator PowerShell command pair + verification is
  recorded verbatim in the evidence report, labeled owner-executed. This producer did
  NOT execute any of it.
- `DISABLE_UPDATES` is deliberately NOT used (R280): it would also block a manual
  intentional `claude update`, which is required for the admission-event flow.

## Limitations / assumptions

- AS-1/AS-2 and the preflight (G3-2) seam tests exercise the real call sites by
  intercepting `subprocess.Popen` and capturing the constructed `env`, then aborting the
  launch (no real CLI, no network, no tokens). They prove the env the production code
  hands to Popen, not a live child. The turnover (G3-3) tests inspect the
  `SuccessorInvocation.env` that `_build_invocation` hands the injected command-runner.
- Ran under Python 3.11.9 (sandbox); repo/CI Python is 3.12. The touched supervisor
  test modules collect and run cleanly on 3.11 (no PEP 695 generics in them). The
  orchestrator/CI runs the authoritative 3.12 suite.
