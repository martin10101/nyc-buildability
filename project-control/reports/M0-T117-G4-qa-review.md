<!-- Saved VERBATIM by the orchestrator from the G4 qa-engineer agent-return channel
     (transport entity-decoding only). Review head 0324342, material identity fa16560. -->

Here is my complete independent G4 QA report.

---

# G4 QA Gate Report — M0-T117

**Task:** M0-T117 — D-024 Amendment 13 unit Q: forced `DISABLE_AUTOUPDATER=1` on controller-launched Claude workers + standing admission-event discipline.
**Reviewer:** qa-engineer (independent, read-only). Producer was backend-engineer — producer ≠ reviewer satisfied.
**Reviewed checkout:** `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24`, branch `control/D-024-fable-codex-loop`, frozen head `0324342` / material identity `fa16560` (as supplied by the orchestrator).
**Verification method note:** the worktree-isolation guard refuses git commands targeting the shared `ctl24` checkout, so I could not run `git rev-parse` there myself (see F10). I instead verified the reviewed state by reading the deliverable files directly at `ctl24/**` and by running pytest against those exact `ctl24` files. All commands and paths below are under `ctl24`.

## Commands run (exact) and result lines

| # | Command (run against `ctl24`) | Result |
|---|---|---|
| C1 | `python --version` | `Python 3.11.9` (sandbox; repo/CI is 3.12 — touched modules use no PEP 695 generics, so they collect and run on 3.11, matching the producer's environment) |
| C2 | `python -m pytest ctl24/tools/test_agent_supervisor_claude_runner_env.py ctl24/tools/test_agent_supervisor_process.py -q` | **`38 passed, 1 skipped in 9.45s`** |
| C3 | `python -m pytest ctl24/tools/test_agent_supervisor_*.py -q -p no:cacheprovider` | **`3 failed, 2717 passed, 2 skipped in 196.10s`** (2722 collected) |
| C4 | `python ctl24/tools/modularity_check.py --check` | `selected 327 files; failures 0; warnings 9` → `EXIT=0` |

The 3 failures in C3 are exactly the three named live-drift teeth, each asserting `'2.1.251 (Claude Code)' == '2.1.248 (Claude Code)'`:
`test_agent_supervisor_capability_probe.py::test_live_reprobe_claude_version_matches_fixture`, `test_agent_supervisor_event_bus.py::test_s8_live_version_matches_catalog_fixture`, `test_agent_supervisor_native_adapter.py::test_live_detection_matches_committed_fixture`.

## 1. Acceptance-scenario → test mapping

| AS | Scenario | Concrete test(s) | Genuine? |
|----|----------|------------------|----------|
| **AS-1** | Worker launch injects even when parent env + allowlist omit the var | `test_agent_supervisor_claude_runner_env.py::ClaudeChildEnvInjectionTests::test_as1_worker_launch_injects_even_when_parent_and_allowlist_omit_it` — pops `DISABLE_AUTOUPDATER` from `os.environ`, asserts the allowlist omits it, intercepts the **real** `subprocess.Popen` at the worker site via `cr.ClaudeRunner(...).run_unit(...)`, asserts captured `env["DISABLE_AUTOUPDATER"]=="1"` | Yes — exercises the production call site |
| **AS-2** | Probe launch injects identically | `...::ClaudeChildEnvInjectionTests::test_as2_probe_launch_injects_identically` — same Popen-intercept technique via `cr.probe_model_launch(...)` | Yes |
| **AS-3** | No collateral env change (byte-identical except the one key) | `...::ClaudeChildEnvSeamTests::test_as3_no_collateral_change_vs_minimal_env` (dict-equality vs `minimal_env` + forced key) **and** `test_as3_only_difference_is_the_single_forced_key` (added/removed/changed set diff = exactly `{DISABLE_AUTOUPDATER}`) | Yes — two angles |
| **AS-4** | Removal sensitivity (red before green) | Evidence-based per packet (`verification: producer red/green evidence`) — `M0-T117-autoupdater-evidence.md`; independently corroborated below (F4) | Yes — packet defines this as evidence, not a live test; I re-derived it |
| **AS-5** | Codex untouched | `...::CodexScopeTests::test_as5_shared_minimal_env_does_not_inject_the_control` + `test_as5_codex_channel_still_uses_the_uninjected_builder` (binding-identity: `codex_channel.minimal_env is pc.minimal_env`, no `claude_child_env` bound) **and** `test_agent_supervisor_process.py::test_minimal_env_does_not_inject_the_claude_autoupdater_control` | Yes — see F7 for a strength note |
| **AS-6** | extra_env conflict cannot disable it (forced pair wins) | `...::ClaudeChildEnvSeamTests::test_as6_extra_env_conflict_is_overridden_forced_pair_wins` (hostile values `"0","false","","off","1"`) + `test_as6_unrelated_extra_env_still_passes_through` + `test_agent_supervisor_process.py::test_claude_child_env_forces_the_autoupdater_control` | Yes |

Every AS-1..AS-6 maps to at least one genuine test; no scenario is stubbed or vacuous. The fail-closed choice for AS-6 ("forced pair wins," applied via `env.update(FORCED_CLAUDE_CHILD_ENV)` last) is documented in the `claude_child_env` docstring and both reports.

## 2/3/4/6 — findings

**F1 — INFO (positive):** Implementation verified at source. `process.py:221` defines `FORCED_CLAUDE_CHILD_ENV = {"DISABLE_AUTOUPDATER": "1"}`; `process.py:224-247` `claude_child_env(extra, allowlist)` calls `minimal_env(...)` then `env.update(FORCED_CLAUDE_CHILD_ENV)` **last** (so allowlist and `extra_env` cannot drop/override it). Both claude Popen sites now consume it: `claude_runner.py:1103` (worker) and `:1549` (probe). `minimal_env` is unchanged; `codex_channel.py` imports/uses `minimal_env` and has **zero** references to `claude_child_env` (grep confirmed) — the claude/codex scope boundary is real.

**F2 — INFO:** Touched-module re-run (C2) reproduced **38 passed, 1 skipped**, matching the packet-expected count and the producer/evidence reports exactly.

**F3 — INFO:** Full-suite re-run (C3) reconciles exactly: **2722 collected = 2712 M0-T116 baseline + 10 new**, **2717 passed, 2 skipped, 3 failed**. The 10 new = 8 (new module) + 2 (process module); the touched-module run's 39 items (38+1) = 8 new-module + 31 process-module confirms the split. The 3 failures are exclusively the pre-existing 2.1.251-vs-2.1.248 live-drift teeth (M0-T118 fixture-recapture scope); this change touches env construction, not version detection, so it neither fixes nor worsens them. I ran the full suite myself rather than relying on records.

**F4 — INFO (removal sensitivity verified by reading + arithmetic):** With the single line `env.update(FORCED_CLAUDE_CHILD_ENV)` removed, `claude_child_env` collapses to `minimal_env` output (which never carries the key — parent popped, allowlist omits it), so:
- AS-1/AS-2 → `env.get("DISABLE_AUTOUPDATER")` returns `None` → `None != '1'` (matches the recorded RED verbatim).
- AS-3 (both), AS-6 (both), and `process::test_claude_child_env_forces...` → mismatch/`KeyError` (matches the recorded `KeyError: 'DISABLE_AUTOUPDATER'` at `process.py:244`).
- Surviving green: `test_as5_shared_minimal_env...`, `test_as5_codex_channel...`, `process::test_minimal_env_does_not_inject...`.

My per-test derivation gives **7 failed / 31 passed / 1 skipped** for the injection-line-removed variant — byte-for-byte the producer's recorded AS-4 count. The two other recorded RED states (fully-unmodified `7 failed, 1 passed` with `None!='1'`+`AttributeError`; AS-1/AS-2-only `2 failed` with `None!='1'`) are likewise consistent with the test design. The RED evidence is genuine and load-bearing, not decorative.

**F8 — INFO (evidence integrity):** `M0-T117-producer-report.md` and `M0-T117-autoupdater-evidence.md` agree with each other and with my runs on every number I can check: touched modules 38/1; full suite 2722/2717/3/2; the three named teeth; the red/green counts. Producer/evidence timing (192s) vs my 196.10s is normal variance. The reports transparently disclose the packet's one-vs-three drift-tooth deviation (packet named only `test_s8_...`; there are three, all the same cause) — an honest disclosure, and item 4 of my brief already reflects it. No number in either report contradicts my independent runs.

## 5. Negative-space (coverage gaps)

**F5 — MAJOR (adjudicate; not a QA code-regression):** The claude binary is launched from **three additional seams** that this change does **not** route through `claude_child_env` and that depend on parent-environment inheritance — contrary to R278(1)'s "NOT dependent on parent-environment inheritance":
- `tools/agent_supervisor/preflight.py:126` `control_response_round_trip` (a **live** claude control-response child) launches with `env=minimal_env()`. This runs during the `--live` preflight step of the very R276/certification window this amendment protects.
- `tools/agent_supervisor/capability_probe.py:99` `_run` (`claude --version/--help`) uses `subprocess.run([exe, ...])` with **no `env`** → inherits the full parent environment.
- `tools/agent_supervisor/native_runtime.py:101` `run_command` uses `env=None` → inherits parent env.

None have a forced-injection test. **Mitigation delivered:** the R288 owner-side machine-scope variable (`[Environment]::SetEnvironmentVariable('DISABLE_AUTOUPDATER','1','Machine')`) covers every inheriting child when set for the certification window, and the producer delivered that command pack verbatim. So under the intended deployment (machine var set) all paths are covered; the gap is only for these paths if the machine var is absent. Because the packet **explicitly** scoped the code injection to "the two `minimal_env` call sites in `claude_runner`," this is not a defect in the delivered scope, but it is a substantive negative-space item. **Recommendation:** the directive-compliance-verifier should confirm R278's general "controller-launched Claude processes" is satisfied for these three seams via R288, and/or a follow-up routes them through `claude_child_env` for machine-var-independent defense in depth. Does **not** invalidate AS-1..AS-6.

**F6 — MINOR:** Env-composition combination untested: an allowlist that explicitly **contains** `DISABLE_AUTOUPDATER` with a parent value set (e.g. `"0"`) as the re-enable vector. AS-6 tests only the `extra_env` conflict vector. Both are neutralized by the same last-write injection line, so risk is low, but the allowlist-inheritance re-enable path has no dedicated removal-sensitive assertion. Recommend one added test.

**F7 — MINOR/INFO:** AS-5 proves codex scope by **import-binding identity** + `minimal_env`-level non-injection, not by a live codex Popen env-capture (as AS-1/AS-2 do for claude). It is logically complete by composition (codex uses `minimal_env` ∧ `minimal_env` never injects ⇒ codex never receives the key), but slightly weaker than a runtime capture. Optional hardening.

## Modularity / process notes

**F9 — INFO:** `modularity_check --check` → `failures 0` (C4). `process.py` (813 lines) surfaces a warning-level `review_signal`, but `claude_child_env` is correctly placed next to `minimal_env` (the module owns child-env construction) — cohesive placement, correct responsibility ownership, no dumping-ground growth. `claude_runner.py` (1768 lines) passes via its pre-existing exception; this task adds only 2 comment lines + 2 swapped call lines there and no new responsibility. Call-site safety confirmed: `RunnerConfig.extra_env` defaults to an empty dict and `env_allowlist` to the tuple, so `dict(self.config.extra_env)` has no `dict(None)` regression.

**F10 — INFO (limitation, not a blocker):** I could not run `git` against `ctl24` (worktree-isolation guard refuses git ops targeting the shared checkout). Per the read-only-reviewer rule I did not return BLOCKED for this; I verified the reviewed state via file-content reads at `ctl24/**` and by executing pytest directly against those `ctl24` files. The pre-existing `F401 import json` in `test_agent_supervisor_process.py:18` is pre-existing, out of scope, and outside the CI ruff working-dir (`services/api`); not gate-relevant.

## Summary

All six acceptance scenarios map to genuine, removal-sensitive tests that I independently reproduced (38 passed / 1 skipped touched-module; 2722-collected full suite reconciling exactly to the three pre-existing out-of-scope drift teeth). Red/green evidence is internally consistent to the test count, and both producer artifacts agree with each other and with my runs. The one MAJOR is a scope/negative-space observation (three additional claude launch seams) that is mitigated by the delivered R288 owner machine-scope control and belongs to the directive-compliance-verifier to adjudicate against R278's general wording — it is not a QA regression of the delivered, packet-scoped deliverable.

**G4 VERDICT: PASS** — every acceptance scenario AS-1..AS-6 is backed by a genuine, independently-reproduced, removal-sensitive test and consistent evidence; the sole MAJOR is a directive-scope coverage question about non-worker claude launch paths that is already mitigated by the delivered R288 owner machine-scope variable and should be confirmed by the directive-compliance-verifier rather than reworked here.
