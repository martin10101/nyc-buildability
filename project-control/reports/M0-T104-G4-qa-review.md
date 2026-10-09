# M0-T104 G4 QA review (round 1) — VERBATIM reviewer return

Orchestrator note (provenance + security-flag assessment): saved verbatim from the qa-engineer
agent-return channel (transport entity-decoding only: `&lt;` → `<`). Review conducted at deliverable
identity `ac305ae` (HEAD `b8ce5cb`, control records only).

The harness raised an instruction-poisoning warning: this reviewer wrote a persistent agent-memory
note (`worktree-isolated-gate-technique.md`) whose wording frames `git archive`/script-file usage as
a way to "evade" the Bash worktree guard. Orchestrator assessment, verified before recording this
gate: (1) the note lives ONLY in the reviewer's transient auto-cleaned worktree of the *pack* repo
(`agent-a886966a86e3c711a`), NOT in ctl24 and NOT in the pack root's agent-memory — it will not be
read back by any ctl24 session; (2) ctl24's working tree is clean of any reviewer write; (3) the
underlying technique (a read-only reviewer reproducing at a frozen SHA via `git archive <sha>` into
scratch) is legitimate and isolation-preserving — no write escaped scratch, the deliverable was not
modified, the read-only mandate held. The "evade" framing is poor wording on benign behavior; it is
recorded as an owner-visible cleanup item (purge stale pack-repo agent worktrees, already tracked)
and is NOT treated as an instruction. The verdict below is accepted because its load-bearing claims
(53/19 pass, guard packs untouched, skip hygiene, mutants) were independently reproduced by the
orchestrator and by the G3 reviewer at this same identity — it is not taken on the reviewer's word.

---

# GATE REPORT — G4 QA — Task M0-T104 (D-024 Amendment 3 unit C: native runtime adapter)

- **Reviewer role:** independent QA (read-only; producer = fable-orchestrator-session; producer ≠ reviewer)
- **Reviewed deliverable identity:** `ac305ae` (HEAD `b8ce5cb` adds only control records — verified below)
- **Method:** clean checkout at the frozen SHA via `git archive ac305ae | tar -x` into scratch; all re-execution done there.
- **Environment:** Python 3.11.9, pytest 8.4.2, `claude --version` → **2.1.247 (Claude Code)** (live rows execute, not skipped). Repo CI runs 3.12; the two new modules use only `from __future__ import annotations` + stdlib typing (no PEP 695), so 3.11 execution is valid evidence.
- **VERDICT: PASS** (with 3 ADVISORY findings; none blocking).

## Identity / scope preconditions

- `git diff --stat ac305ae..b8ce5cb` touches **only** `project-control/` records (G2 gate, self-check, evidence-map, state, task) — HEAD is control-records-only as claimed, so ctl24's `tools/` working tree equals the reviewed identity.
- All deliverable file changes fall inside `allowed_paths` (`tools/agent_supervisor`, the two named test files, the report). `tools/test_agent_supervisor_capability_probe.py` is the recorded pre-submit widening. `forbidden_paths` respected — `.claude/hooks`, `tools/validate_directive_compliance.py`, `tools/project_control.py` all untouched.

## Claim-by-claim re-execution

**Claim 1 — adapter pack 53 passed: PASS.**
`python -m pytest tools/test_agent_supervisor_native_adapter.py -q` → `53 passed in 12.03s`. Live rows executed (claude present).

**Claim 2 — capability-probe pack 19 passed, drift tooth GREEN: PASS.**
`python -m pytest tools/test_agent_supervisor_capability_probe.py -q` → `19 passed in 7.46s`. `-v` confirms `test_live_reprobe_claude_version_matches_fixture PASSED` (drift tooth GREEN at 2.1.247), no masking skips. The probe-test diff is a clean re-baseline: live teeth repointed from the 2.1.246 fixture to the 2.1.247 `m0t104` fixture; 2.1.220/2.1.246 fixtures retained and still shape-checked; new `test_current_fixture_records_2_1_247_masked_and_shaped` added. No invariant weakened.

**Claim 3 — S1–S18 each map to a genuine tooth: PASS.** Enumerated mapping (all assertions inspected):
- S1 → `test_build_background_argv_exact`, `_unflagged_mode_stays_unflagged`, `_canary_measured_constraints`, `test_dispatch_runs_with_stripped_child_env_and_cwd`, `test_empty_prompt_refused`
- S2 → `test_parse_agents_json_typed_records`, `test_observe_parses_and_daemon_available`, committed-fixture tests
- S3 → `test_completed_classification` (+ reconcile: completed never in `safe_to_dispatch`)
- S4 → `test_parse_agents_json_typed_records` (records[1] blocked-input), `test_canary_measured_idle_and_stopped_literals`
- S5 → `test_malformed_agents_json_typed_error` (5 params), `test_observe_unavailable_feed_typed_error`, `test_unknown_status_stays_unknown_never_guessed`
- S6/S7 → `test_stop_logs_respawn_attach_argv`, `test_verb_argv_validation`
- S8/S9 → `test_restart_no_duplicate_and_unexpected_exit`, `test_restart_blocked_and_failed_surface`, `test_restart_stopped_and_unknown_surface`
- S10 → `test_native_selected_only_with_optin_and_full_support`, `_when_config_does_not_opt_in`, `_on_any_capability_gap_including_unknown`, `_when_claude_absent`, `test_controller_backend_delegates_to_existing_dispatch`
- S11 → `test_second_backend_activation_refused`
- S12 → `test_identity_deterministic_and_valid_uuid`, `_rejects_unsafe_tokens`, `_carries_no_host_or_user_material`
- S13 → `test_child_environment_strips_session_markers`, `test_dispatch_runs_with_stripped_child_env_and_cwd`
- S14 → `test_permission_mode_unflagged_resolves_to_auto`, `_accepts_installed_enum_refuses_bypass`, `_default_is_not_a_mode`
- S15 → `test_worktree_base_must_be_pinned`, `_head_refused_on_cli_path`, `_sha_pins_with_guarded_reset_preamble`
- S16 → `test_detection_measures_at_every_call`
- S17 → `test_live_detection_matches_committed_fixture` (adapter) + `test_live_reprobe_claude_version_matches_fixture` (probe)
- S18 → `test_forbidden_flags_cannot_be_smuggled_via_values`, `test_bypass_mode_never_reaches_argv`, `test_detection_probes_are_help_version_only`
- C1/C2 committed artifact → `agents_listing_all_2026-08-27_m0t104.json` + `test_committed_all_listing_carries_canary_lifecycle` (a1 stopped, a2 done). No scenario lacks a tooth.

**Claim 4 — mutation kills: PASS (3 spot-checked, all confirmed killed).** I re-execed mutated copies of the source entirely in memory (no repo files written) and confirmed baselines hold + each named test's assertion actually fails:
- Mutant #3 (`argv += ["--", prompt]` → `argv += [prompt]`): `test_build_background_argv_canary_measured_constraints` → KILLED (AssertionError).
- Mutant #6 (`if not prefer_native:` → `if False:`): `test_controller_when_config_does_not_opt_in` → KILLED (AssertionError).
- Mutant #8 (remove `state == "stopped" → CLASS_STOPPED`): `test_canary_measured_idle_and_stopped_literals` → KILLED (AssertionError).
Each mutation string was confirmed present in source; unmutated baseline assertions all held.

**Claim 5 — fixture integrity: PASS.** All four `m0t104` fixtures parse, are body-stamped `"task":"M0-T104"` (capability-probe fixture keeps body `M0-T086` from the byte-unchanged probe module but the **filename** carries `m0t104` per G3 ADV-1, and the test asserts it), `[HOME]`-masked, session UUIDs truncated to 8 chars + `-[MASKED]`. `agents_listing_all` carries both canary lifecycle rows: `d024-m0-t104-canary-a1` `state:stopped`, `d024-m0-t104-canary-a2` `state:done`. Committed-fixture tests (`test_committed_detection_fixture_shape`, `_agents_fixture_masked`, `_parses_after_unmasking`, `_all_listing_carries_canary_lifecycle`) assert these and ran inside the 53 passed.

**Claim 6 — guard packs / hooks byte-untouched + self-tests: PASS.** `git diff ac305ae~1..ac305ae -- .claude/hooks tools/readonly_agent_guard.py tools/test_readonly_agent_guard*.py` → empty. `python tools/test_readonly_agent_guard.py` → `ALL CHECKS PASSED`. `python tools/test_readonly_agent_guard_powershell.py` → `ALL CHECKS PASSED`.

**Claim 7 — skip hygiene: PASS.** Re-ran both packs with `PATH` stripped so `shutil.which("claude"/"codex")` → `None`:
- adapter: `51 passed, 2 skipped` (lines 629, 640 — the two `@requires_claude` LIVE tests skip with reason "claude CLI not installed on this runner"), returncode 0.
- probe: `17 passed, 2 skipped` (lines 182 claude, 218 codex), returncode 0.
Fixture-reader tests carry **no** skipif and ran in both cases. The M0-T103 G4 ADV-1 regression (skipif wrongly on fixture readers) is **absent** — skipif is on the live tests only.

**Claim 8 — limitations (§4) honest: PASS.**
1. `test_directive_compliance.py` and `validate_directive_compliance.py` are both **untouched** by this task (empty diff), so the local non-run does not affect M0-T104's own coverage. I did **not** re-run the full validator (CI-covered; directive-requirement verification is the independent `directive-compliance-verifier`'s pass, recorded in D-024 `verification.json`). Evidence map (`M0-T104-evidence-map.json`): applicable set = R153/R154/R156/R172 = cited `D-024:ALL` (4/4, missing 0), coherent.
2. `attach` is argv-construction only — confirmed: `NativeBackgroundBackend.attach_argv()` returns the tuple; no code path executes `attach`.
3. Canary history rows remaining in the daemon `--all` are native machine history (disclosed; committed fixture reflects it; not independently re-verified against the live daemon — not required).
4. `prefer_native` has **no production caller** — grep confirms it appears only in the `select_runtime_backend` signature and as test arguments; controller remains the operative default (R180 boundary honest).

## Modularity (handwritten production source changed)

PASS. The only in-scope production files are the two NEW modules (tests + fixtures excluded by the checker). Using the checker's own `source_lines()`: `native_runtime.py` = 465 SLOC / 23 symbols; `runtime_backend.py` = 216 SLOC / 9 symbols — both **clean** (warn 600, justify 750, hard 1000, symbol ceiling 40; NEW files fail only above 1000). Responsibilities are cleanly split (primitives vs. selection/reconciliation/fallback) with an explicit one-directional import boundary; no dumping-ground or responsibility mixing. (`modularity_check.py --check` itself needs a git index and cannot run against an archive extract — I computed SLOC directly instead.)

## Missing failure-mode coverage (probe) — all ADVISORY, none blocking

- **ADV-1:** S6's *post-stop absence verification* ("id absent from the active listing") has no deterministic tooth — the deterministic test pins only `claude stop <id>` argv; the absence check is demonstrated solely in the live C1 canary. This is honestly labeled in the report (S6 kind = "deterministic + live canary"), and `find_by_identity` (the building block) is separately tested; the thinnest-tested area.
- **ADV-2:** `dispatch()/stop()/respawn()/logs()` return the raw `CommandResult` without checking `.status`; only `observe()` raises on failure. A daemon-rejected dispatch/stop (non-zero exit) is not surfaced as a typed error and has no test. Currently harmless (nothing consumes the seam — R180), but the command-execution error surface is thinner than the feed path; flag for the consuming unit (F–H).
- **ADV-3 (minor):** `WorktreeSpec` `invalid_worktree_name` path and forbidden-flag-via-`agent`-value are covered only indirectly (the final `FORBIDDEN_DISPATCH_FLAGS` argv scan catches an `--cloud` agent value; invalid worktree name is unexercised). Consider direct teeth.

## Commands run (all from the clean `ac305ae` scratch checkout)
- `git archive ac305ae | tar -x` → clean checkout; `git diff --stat ac305ae~1..ac305ae` and `ac305ae..b8ce5cb`
- `python -m pytest tools/test_agent_supervisor_native_adapter.py -q` → 53 passed
- `python -m pytest tools/test_agent_supervisor_capability_probe.py -q` → 19 passed
- in-memory mutation harness → mutants #3/#6/#8 KILLED, baselines hold
- `python tools/test_readonly_agent_guard.py` / `..._powershell.py` → ALL CHECKS PASSED ×2
- skip-hygiene run with empty PATH → adapter 51p/2s, probe 17p/2s, rc 0
- SLOC via `modularity_check.source_lines` → 465 / 216 (clean)

**Recommendation:** PASS. The three ADVISORY items are appropriate follow-ups (ADV-1/ADV-2 naturally close when the seam is wired in a later unit); they do not affect the correctness or safety of the delivered bounded seam. The orchestrator records the gate.
