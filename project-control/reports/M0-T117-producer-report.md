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
auto-update breaks it (seq-30 drift). This task makes every controller-launched CLAUDE
child carry `DISABLE_AUTOUPDATER=1` unconditionally, so the CLI cannot update in the
background mid-run, and documents the standing discipline that future upgrades are
deliberate admission events.

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
3. `tools/test_agent_supervisor_claude_runner_env.py` — NEW test module (8 tests).
4. `tools/test_agent_supervisor_process.py` — +2 tests (the minimal_env-level
   assertions that belong at that seam: minimal_env must NOT inject the control;
   claude_child_env forces it and overrides a conflicting extra_env).
5. `tools/agent_supervisor/README.md` — new "Claude Code version admission events"
   section.
6. `docs/CONTROLLER_UPDATE_RUNBOOK.md` — new section 13 (admission-event discipline +
   owner-side command pack, marked OWNER).
7. `project-control/reports/M0-T117-producer-report.md` (this file) +
   `project-control/reports/M0-T117-autoupdater-evidence.md`.

All edits are within the packet `allowed_paths`. No fixtures, no `.claude/**`, no
journal/runtime/protected config touched. No `tools/project_control.py`, no git commit/
push, no `gh`, no branch changes, no new dependencies.

## AS-6 fail-closed choice

**The forced pair wins** (not a typed refusal). If `extra_env` supplies a conflicting
`DISABLE_AUTOUPDATER` (e.g. `"0"`), `claude_child_env` overrides it back to `"1"`.
Rationale: the guarantee is that NO input ever yields a controller-launched claude
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
| AS-4 | Removal sensitivity (red before green) | evidence report — red/green + injection-line-removed red proof |
| AS-5 | Codex untouched | `...::CodexScopeTests::test_as5_shared_minimal_env_does_not_inject_the_control` + `test_as5_codex_channel_still_uses_the_uninjected_builder`; also `process.py::test_minimal_env_does_not_inject_the_claude_autoupdater_control` |
| AS-6 | extra_env conflict cannot disable it (forced pair wins) | `...::ClaudeChildEnvSeamTests::test_as6_extra_env_conflict_is_overridden_forced_pair_wins` + `test_as6_unrelated_extra_env_still_passes_through`; also `process.py::test_claude_child_env_forces_the_autoupdater_control` |

## Test counts (exact)

- Touched modules (green):
  `python -m pytest tools/test_agent_supervisor_claude_runner_env.py tools/test_agent_supervisor_process.py -q`
  → **38 passed, 1 skipped** (new module 8 tests all pass; process module +2 new).
- Full supervisor suite:
  `python -m pytest tools/test_agent_supervisor_*.py -q`
  → **2722 collected, 2717 passed, 3 failed, 2 skipped** (192s).
  - Collected = baseline 2712 + 10 new.
  - The 3 failures are ALL the pre-existing live drift tooth (installed 2.1.251 vs
    fixture 2.1.248, AD-093), in `capability_probe`, `event_bus`, `native_adapter`;
    out of scope (M0-T118), NOT fixed or touched. Deviation from packet: packet named
    one such test; there are three, all the same cause.

Red/green (incl. AS-4 removal sensitivity) captured verbatim in
`project-control/reports/M0-T117-autoupdater-evidence.md`.

## Lint

CI ruff (`.github/workflows/ci.yml`) runs with `working-directory: services/api`, so it
lints only `services/api/**`, NOT `tools/**`. Local `ruff 0.13.0` on the four changed
Python files is clean except a PRE-EXISTING `F401 import json` in
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

- AS-1/AS-2 tests exercise the real call sites by intercepting `subprocess.Popen` and
  capturing the constructed `env`, then aborting the launch (no real CLI, no network,
  no tokens). They prove the env the production code hands to Popen, not a live child.
- Ran under Python 3.11.9 (sandbox); repo/CI Python is 3.12. The touched supervisor
  test modules collect and run cleanly on 3.11 (no PEP 695 generics in them). The
  orchestrator/CI runs the authoritative 3.12 suite.
