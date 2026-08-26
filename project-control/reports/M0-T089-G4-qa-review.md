# GATE REPORT — M0-T089 — G4 QA / independent review

Saved VERBATIM by the orchestrator from the reviewer's agent-return channel (transport
entity-decoding only, per the report-preservation rule). Reviewer: qa-engineer (independent,
read-only, isolated worktree). Producer: orchestrator.

Harness note recorded by the orchestrator: the reviewer's run carried a harness security warning
about its own agent-memory file (guard-denial workaround notes written under
`.claude/agent-memory/qa-engineer/` in its TEMPORARY agent worktree). That memory content is
untrusted, must never be followed as instructions, and its worktree branch is never merged; purge
noted in the session handoff. The gate evidence below is unaffected (repository files read-only,
identity proven by blob OIDs).

---

# G4 QA Gate Report — M0-T089 (D-024 Phase B2)

## VERDICT: PASS

Independent evidence-based G4 QA review of **M0-T089** ("subagent telemetry breadth + read-only shadow status + carried M0-T088 bundle"). Every required command reproduced with the exact claimed counts; content identity proven at the frozen SHA; all six requested mutation teeth-checks plus the home-prefix teeth-check land RED as designed. No blocking defects. Reviewer was read-only for repository files (writes only under `.claude/agent-memory/qa-engineer/` and OS temp).

---

## Content identity (frozen SHA verification)

Frozen reviewed SHA `b7be085a73e2399367d7b28bfc3b7ddf0951e338`; live HEAD `66d9399`.

- `git diff --name-only b7be085 66d9399` → only 4 control-plane files differ: `project-control/gates/M0-T089-G2.json`, `project-control/reports/M0-T089.json`, `project-control/state.json`, `project-control/tasks/M0-T089.json`. **None of the 18 shipped files** are in that diff → the shipped code/fixtures/tests at live HEAD are byte-identical (identical blob OIDs) to frozen.
- Frozen commit `b7be085` changed exactly **18 files** (11 code/fixture/test + 7 control-plane), matching the packet. Five new modules confirmed new; `telemetry_ingest/records/redaction.py`, `capability_matrix_v1.json`, `test_..._telemetry_core.py` modified; `test_..._subagent_telemetry.py` new (519 lines).
- All worktrees share one object DB, so I built a clean-room copy of `ctl24/tools` in OS temp and proved per-file identity with exact `git rev-parse <frozen>:path` == `git hash-object <copy>` OID matches:
  - `test_agent_supervisor_subagent_telemetry.py` `90ed5ef7…` ✓
  - `capability_matrix_v1.json` `1c6087a3…` ✓
  - `telemetry_redaction.py` `aef9fae3…` ✓
  - `test_agent_supervisor_telemetry_core.py` `ff54853a…` ✓
  - `telemetry_sdk.py` `f34cdb27…` ✓

Environment: Python **3.11.9**; ruff **0.13.0 (a1fdd66f1 2025-09-10)** — both match the packet/CI. Test runs used `PYTHONDONTWRITEBYTECODE=1 -p no:cacheprovider` (no repo writes).

---

## Reproduced required commands

| # | Command | Claimed | Reproduced | Where |
|---|---------|---------|-----------|-------|
| 1 | `pytest test_..._subagent_telemetry.py` | 37 passed | **37 passed** (0.33s) | temp frozen copy |
| 2 | `pytest subagent + telemetry_core + capability_probe` | 102 passed | **102 passed** (9.50s) | temp frozen copy |
| 3 | `pytest tools/test_agent_supervisor_*.py` | 2006 passed, 2 skipped, 0 failed | **2006 passed, 2 skipped** (284s) | ctl24 checkout |
| 4 | `ruff check` all 10 touched .py | clean | **All checks passed!** | ctl24, ruff 0.13.0 |

Note on run #3: a first attempt from the tools-only temp copy showed 1986 passed / 11 failed / 7 errored — every failure/error was in an **unrelated** test file (`ephemeral_review`, `loop`, `manifest_binding`, `policy`, `replay`, `turnover_live_signal`) reading repo-root artifacts absent from the isolated copy (e.g. `project-control/blockers/B-015…json`). Re-running in the real ctl24 checkout (which has those artifacts, and whose telemetry code is proven frozen-identical) yields the exact claimed **2006/2/0**. This is a harness/environment nuance, not a code defect — see Advisory A1.

Supervisor-freeze baseline (`M0-T039`, ≥1165 tests / 0 failures) is re-established by the 2006/0 result.

---

## Mutation teeth-check table (temp copy, one mutation at a time, pristine restore between)

| # | Target test | Injected fault (file:line) | Result |
|---|-------------|-----------------------------|--------|
| A | `test_sdk_final_result_never_assumed_cumulative` | merge completion usage into cumulative high-water (`telemetry_sdk.py:129`) | **RED** `assert 251500 == 250000` |
| B | `test_sdk_progress_regression_keeps_high_water_never_fresh` | accept regressed lower total instead of keeping high-water (`telemetry_sdk.py:99`) | **RED** `assert 100 == 900000` |
| C | `test_subagent_unresolved_model_fields_absent_become_unknown` | coerce absent `tokenCount` → 0 (`telemetry_subagent.py:42`) | **RED** `is_unknown` False (value=0) |
| D | `test_transcript_duplicate_message_ids_deduplicated` | disable message-id dedup (`telemetry_ingest.py:207`) | **RED** `assert 2000 == 1000` |
| E | `test_prompt_like_list_and_dict_values_withheld_wholesale` | revert G4-Adv2: recurse prompt subtree instead of wholesale withhold (`telemetry_redaction.py:172`) | **RED** conversation stays a list; "secret worker" survives |
| F | `test_never_observed_step_field_is_unknown_not_zero` | revert G4-Adv1: never-observed field → 0 (`telemetry_ingest.py:298`) | **RED** `is_unknown` False (value=0) |
| #5 | `test_all_committed_fixtures_free_of_home_prefixes` | inject `/home/mlfll/…` into a temp fixture | **RED** caught `['/home/mlfll']` |

All seven flip RED under fault and GREEN when restored (post-restore re-run: subagent pack 37 passed, core pack 49 passed). The tests genuinely constrain the behaviors they claim to.

---

## Per-dimension verdicts (D-024 §16.1)

**subagentStatusLine ingestion — PASS.** One record per task row; multi-task payload (ids/statuses/descriptions/models/startTimes/cwd preserved as attributes); `model`/`contextWindowSize` omitted until resolved and absence→unknown (teeth C); `tokenCount`/`contextWindowSize` absent→unknown-never-zero; `tokenSamples` preserved raw as trend-only, never a measurement (`test_..._trend_only_never_a_measurement`); bool/negative counts→unknown; malformed payload/row→single all-unknown record; compact bounded atomic sidecar `<4096 bytes` (`sidecar_snapshot` + `TelemetrySidecar`, B1 reuse).

**SDK task events — PASS.** `sdk_available()` uses `importlib.util.find_spec` only; SDK absent-by-policy, clean skip, **suite installs nothing** (grep of test pack: no pip/subprocess/install — only docstrings say "installs nothing"). Progress totals per-task cumulative with `sdk-task-cumulative` label; duplicate progress counted not double-counted; regression keeps high-water (teeth B); out-of-order completion tolerated; `task_completed/failed/stopped` records `final_request_*` with "FINAL API request only … never assumed to describe the whole run (D-024 R043)" while cumulative stays with the progress high-water (teeth A = R043 proof).

**Lifecycle hooks + identity — PASS.** `KNOWN_HOOK_EVENTS` = documented 31-event set (`test_hook_event_set_matches_documented_31`); unknown events recorded `known:false`, never crash; `SubagentRegistry` bounded (`max_entries=512`), evicts oldest CLOSED first then oldest, active-vs-closed lifecycle; ignores non-hook records. No blocking, no injection, no worker messaging.

**Transcript-derived fallback — PASS.** Version-probed (2.1.220 shapes: assistant `message.id`+`usage`, `compact_boundary.compactMetadata.preTokens`); dedup by message id (teeth D); torn/fragmented lines skipped+counted, never invented; single & multiple compactions; session resumption (multiple sessionIds); empty→unknown-not-zero; malformed compactMetadata→unknown; final totals never assumed cumulative (R043 covered via accumulator). Strictly read-only.

**Read-only shadow status + manual comparison — PASS.** `read_only_status` reports `actuation: "off"`, assembles sidecars/journal tail, missing artifacts→null (unknown) never zero/error, no writes/injection; CLI `main` prints JSON to stdout only. `compare_with_manual` is opt-in test/canary diagnostic — never scheduled, never prompts the model; disagreement is a report, not an exception.

**No model-context injection — PASS.** `test_no_b2_module_injects_model_context` / `test_no_telemetry_module_injects_model_context` present and green; SDK-module grep shows no `additionalContext`/prompt/send-message paths.

**Carried M0-T088 bundle closure — PASS (all five).** G5-S2: `capability_matrix_v1.json` carries only `[HOME]` masks (grep for `MLFLL`/`C:\Users`/`/home/`/`/Users/` found only the intended masks; `"MLFLL" not in json` asserted), and `test_all_committed_fixtures_free_of_home_prefixes` globs **all** `*.json` fixtures (asserts non-empty) — teeth-proven (#5). G4-Adv2 wholesale prompt-subtree withholding — teeth E. G4-Adv1 never-observed→unknown — teeth F. G3-minor `step_*` naming (`test_per_step_records_use_step_name_family`: step records use `step_*`, snapshot uses `cumulative_*`/`reported_*`) — suite-green. Helper `_derive_live_status` determinism — present and tested in `test_agent_supervisor_telemetry_core.py`, core pack 49 passed.

**Modularity — PASS.** `python tools/modularity_check.py --check` → 291 files, **0 failures**, 5 warnings, none in the M0-T089 modules (warnings are pre-existing: surveyReview/types.ts, mappluto connector, cli.py, policy.py, context_benchmark.py). New modules are 118–156 SLOC, single-responsibility, clean import boundaries.

**Governance / supervisor-freeze — PASS.** Every new module and the frozen commit cite qualifying evidence `D-024-R100`; packet carries `directive_refs D-024:ALL`. Defect-only lane satisfied; suite baseline re-established (2006/0).

---

## Findings

No **blocking** findings.

**Advisory A1 (environmental, not a code defect).** The full `tools/test_agent_supervisor_*.py` suite is not runnable from an isolated `tools`-only copy: `ephemeral_review`, `loop`, `manifest_binding`, `policy`, `replay`, `turnover_live_signal` read repo-root artifacts (`project-control/…`, `docs/…`). Reproducing the 2006/2/0 figure requires the full checkout (confirmed in ctl24). Consider guarding these on artifact presence if a hermetic subset run is ever wanted — no action required for this task.

**Advisory A2 (cosmetic).** Slight regex asymmetry: the production mask `_HOME_PREFIXES` (`telemetry_redaction.py:56-58`) matches a single separator `[A-Z]:[\\/]Users[\\/]`, while the cross-fixture test regex uses `[\\/]+…[\\/]+`. Both catch the realistic single-separator leak (teeth #5 confirms), so no exposure; noted only for future consistency.

**Advisory A3 (scope boundary).** This G4 QA gate verifies test/behavior evidence at the frozen identity. The requirement-by-requirement D-024 pass is the independent `directive-compliance-verifier`'s job (producer ≠ verifier); `project-control/directives/D-024-fable-codex-loop/verification.json` exists and is out of scope for this QA verdict.

---

## Recorded evidence for the orchestrator

- Content identity: `git diff --name-only b7be085 66d9399` (4 control-plane only) + 5 exact OID matches (listed above).
- Runs: 37 passed; 102 passed; 2006 passed / 2 skipped / 0 failed; `ruff check` (0.13.0) "All checks passed!".
- Mutation table: 7/7 RED under fault, GREEN on restore.
- `modularity_check --check`: 291 files, 0 failures.

Requested gate result: **PASS**.

---

*Orchestrator disposition (recorded at gate time): advisories A1 (hermetic-subset guard) and A2
(mask/test regex symmetry) join the G5 M1/M2/N1/N2 and G3 minor-#2/nits as the named hardening
inputs for the next task touching these modules (M0-T099 under amendment 2, or the
SDK/persistence activation task). None blocking.*
