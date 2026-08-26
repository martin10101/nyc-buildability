# GATE REPORT — M0-T089 — G3 Independent Code Review

Saved VERBATIM by the orchestrator from the reviewer's agent-return channel (transport
entity-decoding only, per the report-preservation rule). Reviewer: code-reviewer
(independent, read-only). Producer: orchestrator.

---

# G3 CODE REVIEW GATE REPORT — M0-T089 (D-024 Phase B2)

## VERDICT: PASS (with minor/nit findings; none blocking)

Reviewer: code-reviewer (independent, read-only). Date: 2026-08-25.
Task: M0-T089 — "D-024 B2: subagent telemetry breadth + read-only shadow status."
Reviewed content identity: **b7be085a73e2399367d7b28bfc3b7ddf0951e338** (18-file content commit).

---

## 1. Identity verification (done first)

- Frozen content commit `b7be085` = the 18-file diff (`git show --stat` matches the packet SCOPE exactly: 5 new production modules, 5 carried-bundle modifications, 1 new test file, 5 report/control records; 1624 insertions / 96 deletions).
- Live HEAD `66d9399` adds **only control-plane records** over `b7be085`: `gates/M0-T089-G2.json`, `reports/M0-T089.json`, `state.json`, `tasks/M0-T089.json` (4 files, 63/4). No production or test byte differs between the frozen SHA and HEAD.
- Working tree clean. Review performed at the frozen identity.

Scope compliance: every production change is confined to `tools/agent_supervisor/**` plus the two named test files and the report. No forbidden production path (`apps`, `services`, `supabase`, `tools/project_control.py`, `.claude/hooks`, …) is touched. The `tasks/`/`gates/`/`state.json` edits are orchestrator control-plane lifecycle writes (producer_agent = orchestrator), consistent with ADR-005 — not a producer file-scope breach.

---

## 2. Reproduction (commands re-run at frozen identity, Python 3.11.9)

| Check | Claim | Reproduced result |
|---|---|---|
| Targeted packs (`test_agent_supervisor_subagent_telemetry` + `_telemetry_core` + `_capability_probe -q`) | 102 passed | **102 passed in 20.84s** ✓ |
| Full supervisor suite (`tools/test_agent_supervisor_*.py -q`) | 2006 passed / 2 skipped / 0 failed | **2006 passed, 2 skipped in 245s** ✓ |
| New tests in `test_agent_supervisor_subagent_telemetry.py` | 37 | **37** (`grep -c '^def test_'`) ✓ |
| `python tools/modularity_check.py --check` | failures 0 | **selected 291 files; failures 0** (no new module flagged) ✓ |
| `ruff check` (CI-matched) on all 8 touched modules + 2 test files | clean | **All checks passed! (ruff 0.13.0)** ✓ |
| 31-event hook roster | 31 | `len(KNOWN_HOOK_EVENTS) == 31` ✓ |
| No control-flow module / consumer touched | cli.py unchanged | cli.py absent from diff; grep shows **no module imports the 5 new modules** except the test file ✓ |

Baseline arithmetic confirmed: 1969 (M0-T088) + 37 = 2006.

---

## 3. Requirement / dimension coverage (independently re-derived)

**Correctness — line-by-line, all 5 new modules + 3 modified.** Verified edge cases behave as required:

- `telemetry_subagent.py` — one record per task row; `_count_measurement` (l.42) rejects bool / non-numeric / negative → `unknown` occupancy; present `tokenCount==0` legitimately records as `0` (present, not missing); `model`/`contextWindowSize` omitted-until-resolution handled (absence = normal, l.85-88); `tokenSamples` preserved raw and never turned into a Measurement (l.89-95); malformed payload/row → single all-unknown record; empty tick honest (`{"tasks": 0}`). Correct.
- `telemetry_sdk.py` — `sdk_available()` is `find_spec`-only, no import/install (l.40-49, R040 satisfied); `_clean` guards bool/negative; high-water dedup (equal→dup, lower→regression keeps high-water, l.94-101); completion records `final_request_*` separately from `sdk_task_total_tokens` high-water (R043); out-of-order completion tolerated (late progress still lifts high-water); unknown event type → `known: False` + unknown. Correct.
- `telemetry_hooks.py` — identity-only records, no invented usage; unknown event names → `known: False`; `SubagentRegistry` open/close + bounded eviction (closed-first, then FIFO) verified against the eviction test's exact ordering. Correct.
- `telemetry_transcript.py` — read-only; reuses `UsageAccumulator(step_label="transcript-derived")` (good reuse); torn/non-dict/assistant-with-non-dict-message → `torn` counted; message-id dedup; `compact_boundary.preTokens` validated (int/float, non-bool, ≥0); multi-compaction sum + resumption via distinct `sessionId`s; empty → unknown but `compaction_count==0` as an observed fact. Correct. The G4-Adv1 observed-field logic flows through correctly (an all-absent field → transcript-derived unknown).
- `telemetry_status.py` — `read_only_status` and `main()` create/remove no files (proven by the before==after file-set test); missing artifacts → `null`, never zero; `compare_with_manual` reports disagreement, never raises. Actuation is genuinely off — **nothing consumes any of these records anywhere in the tree** (grep-confirmed), so there is no control-behavior change.

**Test adequacy / teeth.** The 37 tests have real teeth: they assert exact values, labels, categories, `is_unknown`, attribute contents, file-set equality (read-only proof), red/green on all five carried items, and negative paths (`pytest.raises(ValueError)` on bad `step_label`). No never-failing tautologies of concern. One cosmetic line (`test_transcript_derivation_sums_and_labels` l.306 `assert ... or True`) is a dead assertion, but the surrounding value assertions on the same record are strong, so it's a nit, not a hole.

**Carried M0-T088 bundle closure (verified against the prior-finding texts in the packet):**
- G5-S2 — `capability_matrix_v1.json` binary/dual-install notes `[HOME]`-masked (diff), plus a **cross-fixture** assertion scanning all `agent_supervisor/fixtures/*.json` (`test_all_committed_fixtures_free_of_home_prefixes`) — exposure class closed. ✓
- G4-Adv2 — `withhold_prompt_value` collapses list/dict prompt values to one digest; `sanitize_structure` l.169-172 rewired; red/green test confirms "secret worker"/"assignment" absent from output and empty containers preserved. ✓
- G4-Adv1 — `_observed_fields` tracking; snapshot returns `unknown` (not 0) for a never-observed field; red/green. ✓
- G3-minor — `_STEP_USAGE_FIELDS` 3-tuple; `provider_usage_step` uses `step_*`, only `snapshot()` uses `cumulative_*`; `MEASUREMENT_CATEGORY` additions; B1 core assertions updated. ✓
- Helper determinism — `_derive_live_status` mixed-set now `sorted(...)[0]`, not `pop()`. ✓

**Modularity.** 5 focused single-responsibility modules (117-155 SLOC each), all far under thresholds; `modularity_check --check` = 0 failures; strong reuse over duplication (`UsageAccumulator`, `TelemetrySidecar`, `TelemetryJournal`, `ingest_status_line` all reused). Sound.

**No model-context injection / no worker counters.** `test_no_b2_module_injects_model_context` AST-scans all 5 modules for `additionalContext`/`hookSpecificOutput` in non-docstring strings; passes. No numeric quota/countdown language in any worker-facing surface (there is no worker-facing surface — all modules are passive parsers).

**Report accuracy (≥6 claims spot-checked, all true):** 37 new tests; 102 passed; 2006/2/0; modularity 0 failures; ruff 0.13.0 clean; cli.py unchanged/no consumer; 31-event roster; G5-S2 masking; R043 final-request-only; Python 3.11.9. Every spot-checked claim reproduced.

---

## 4. Findings

**Blocking:** none.

**Minor:**
1. `tools/agent_supervisor/telemetry_hooks.py:29-38` — the 31-name `KNOWN_HOOK_EVENTS` roster is asserted at "official-docs confidence." I cannot independently confirm from this sandbox that all 31 names are genuine documented Claude Code 2.1.220 hook events (several — e.g. `Setup`, `MessageDisplay`, `TeammateIdle`, `InstructionsLoaded`, `ConfigChange`, `CwdChanged`, `DirectoryAdded`, `WorktreeCreate/Remove`, `Elicitation/ElicitationResult`, `PostToolBatch`, `PostToolUseFailure`, `StopFailure`, `PermissionDenied`, `UserPromptExpansion` — are outside the widely-documented core set). Mitigating: the roster only sets the `known` boolean, nothing consumes it, and unknown events fail safe (`known: False`, no crash). Recommend the producer retain a captured doc snapshot/URL as provenance for the roster.
2. `tools/agent_supervisor/telemetry_sdk.py:147` — `duplicates`/`regressions` counters increment **per field**, not per event (a fully-duplicated 3-field progress event increments `duplicates` by 3). Diagnostic-only and documented loosely; could mislead a later reader who treats it as an event count.

**Nit:**
3. `tools/agent_supervisor/telemetry_sdk.py:122` — `final_request_*` measurements carry label `sdk-cumulative` while describing only the final API request. The measurement *name* and the explicit detail ("FINAL API request only … R043") disambiguate, and `sdk-cumulative` is the closest source label in the fixed s5.2 vocabulary, so this is defensible; flagging only because a naive label-filter would sweep it in.
4. `tools/agent_supervisor/telemetry_subagent.py:48-51` — the "documented pairing with contextWindowSize" detail string is applied verbatim to the `contextWindowSize` measurement itself (a window "paired with itself"); cosmetic.
5. `tools/test_agent_supervisor_subagent_telemetry.py:306` — `assert "lower bound" not in ... or True` is a dead (always-true) assertion; harmless given the strong value assertions beside it.

---

## 5. Notes for the orchestrator / other gates

- The packet's `directive_refs = D-024:ALL` and the report's claim of "34 applicable ids, identical to M0-T088" are the **directive-compliance-verifier's** province, not this G3; I did not adjudicate the full requirement set — only the code, tests, modularity, and report accuracy.
- Supervisor-freeze compliance: D-024-R100 cited in packet objective, report, and commit message; freeze §4 suite-baseline (≥1165, 0 failures) re-established at 2006. Satisfied.
- A background `pytest tools/ -q` (superset) was still running when I finished; the authoritative `tools/test_agent_supervisor_*.py` run completed green (2006/2/0), which fully covers this task's surface.

**Recommended gate result: PASS.** The five minor/nit items are advisory and non-blocking; none affects correctness, the directive requirements, or the shadow-only guarantee. Finding #1 (roster provenance) is worth capturing but does not block given the safe failure mode.

---

*Orchestrator disposition (recorded at gate time): G3 minor #1 (hook-roster provenance) is
SATISFIED by owner amendment 2 (source-002-amendment.md, captured 2026-08-26): the official
statusline documentation URL is now adopted as primary capability evidence, and the amendment's
capture annex preserves the fetch-verified field/version facts; the hooks-page provenance for the
31-event roster remains the matrix's `claude.hooks.event_set_2_1_220` entry (official-docs,
fetched 2026-08-25). G3 minor #2 (per-field duplicate counters) and nits #3/#4/#5 join the G5
advisory items as named hardening inputs carried to the next task that touches these modules
(M0-T099 statusLine-handler work under amendment 2, or the SDK/persistence activation task).
None blocking.*
