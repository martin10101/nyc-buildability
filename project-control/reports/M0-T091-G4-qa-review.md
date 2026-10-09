# M0-T091 — G4 Independent QA Review

> Saved VERBATIM by the orchestrator from the qa-engineer agent-return channel (transport
> entity-decoding only). Verdict: PASS (6/6 mutation teeth RED-on-mutant; 6/9 correction-bundle
> items proven RED by revert, remaining 3 verified by non-vacuous tests; 1 advisory ADV-1,
> non-blocking). Reviewer Limitation-1 (git byte-identity, sandbox worktree guard) DISCHARGED by
> the orchestrator below the report.

All evidence gathered. No repository file was modified (real modules were Read/imported only; all mutation edits were on scratch copies). Here is my gate report.

---

# GATE REPORT — G4 (Independent QA)

- **Gate ID:** G4
- **Task ID:** M0-T091 (D-024 Phase C2 — invisible runtime supervision)
- **Reviewer:** qa-engineer (independent; not the producer)
- **Producer:** orchestrator
- **Frozen content commit:** ee564dd · Live HEAD at dispatch: b4f7e40
- **Review target:** `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24` (branch `control/D-024-fable-codex-loop`)
- **Environment:** Python 3.11.9 · pytest 8.4.2 · ruff 0.13.0 (CI-matching)
- **Result: PASS** — no blocking defects. One advisory (ADV-1). Corrections not required for acceptance; ADV-1 recommended for follow-up.

---

## 1. Scope and method

Read the packet, producer report, and G2 self-check as claims to reproduce. Independently reproduced the test evidence, built an isolated mutation harness, ran negative/boundary/determinism probes against the real modules, audited s16.2 coverage against test bodies, and spot-proved the carried correction bundle by reverting fixes. Reviewer stayed read-only: no repository file was modified (real modules were only Read/imported; every mutation edit was applied to scratch copies under the session scratchpad).

---

## 2. Deliverables present and substantive (packet `outputs`)

| Named output | Present | Evidence |
|---|---|---|
| health-band / no-progress / extension-gate / landing enforcement under `tools/agent_supervisor` (accelerated-counter testable) | Yes | 5 focused modules: `runtime_health.py` (478), `runtime_detectors.py` (274), `extension_gate.py` (213), `child_handoff.py` (212), `lease_runtime.py` (163). Each has a typed error class, frozen records, closed vocabularies, injected clocks. |
| `tools/test_agent_supervisor_runtime_supervision.py` (s16.2 cases incl. forty-minute landing, high-usage-near-seam, observe-no-message) | Yes | 849 lines, 54 tests, all present and non-vacuous. |
| `project-control/reports/M0-T091-runtime-supervision.md` | Yes | Substantive; §2 correction-bundle table maps each item to code + regression test. |

All three named outputs exist and are substantive (not merely acceptance scenarios).

---

## 3. Reproduced test evidence

| Command (cwd `ctl24`) | Producer claim | Reproduced |
|---|---|---|
| `pytest tools/test_agent_supervisor_runtime_supervision.py -q` | 54/0 | **54 passed in 1.53s** ✓ |
| `pytest tools/test_agent_supervisor_bounded_contracts.py -q` (C1, untouched, under corrected guards) | 53/0 | **53 passed in 0.36s** ✓ |
| Adjacent packs: statusline_handler, telemetry_core, subagent_telemetry, rotation, scheduler, context_pack | 305/0 | **305 passed in 63.87s** ✓ |
| Spot-slice (composite corroboration): quota_classifier + c2_binding | — | **22 passed in 2.34s** ✓ (no regression from corrected guards) |
| `python tools/modularity_check.py --check` | exit 0; largest new module 478 raw < 600 warn | **EXIT=0**, 302 files, 0 failures; 5 warnings are all pre-existing files, **none the new modules** ✓ |
| `ruff check` (9 new/edited files) | clean | **All checks passed!** (ruff 0.13.0) ✓ |

**Composite 2707/3/0:** verified by arithmetic (accepted M0-T090 baseline **2653** + **54** new = **2707**, closes exactly) plus four live green slices totalling **434** reproduced passes (54+53+305+22). The full ~50-min composite was not re-run end-to-end (evidence-capture division of labor); CI/orchestrator holds the full run. No contradicting evidence found.

**C1 pack untouched:** `test_agent_supervisor_bounded_contracts.py` mtime `2026-08-26 02:38` predates every M0-T091 edit (`15:24`–`15:34`), it is outside the packet `allowed_paths`, and it passes 53/0 under the corrected guards. Byte-identity is git-confirmable by the orchestrator (git blocked in my sandbox by the worktree guard).

---

## 4. Mutation teeth — RED-on-mutant / GREEN-on-actual

Isolated scratch copy of the package (`PYTHONPATH=<scratch> pytest -k <test>`); pristine baseline of the 6 target tests: **11 selected passed** (GREEN). Each mutant applied to a scratch copy, target test run, then reverted.

| # | Module · mutation | Target test | Mutant result |
|---|---|---|---|
| a | `runtime_health.evaluate_band` — drop the near_complete+coherent allow-reach-seam branch | `test_high_usage_near_seam_completion_reaches_safe_seam` | **RED (killed)** — 1 failed |
| b | `SupervisionState.apply` — allow a second landing message (`if self._landing is not None` → `if False and …`) | `test_land_sends_one_concise_direction_exactly_once` | **RED (killed)** — 1 failed |
| c | `LeaseLedger.grant` — validate empty snapshot instead of folded active set (`assert_grantable((), envelope)`) | `test_grant_ledger_serializes_where_snapshot_validation_cannot` | **RED (killed)** — 1 failed |
| d | `AssignmentMonitor.observe` — let every non-evidence event reset `_last_evidence_at` | `test_text_volume_and_tool_activity_are_not_progress` | **RED (killed)** — 1 failed |
| e | `decide_extension` — default approve instead of deny-to-backlog (`if False and blocking_kind == NON_BLOCKING`) | `test_unrelated_discovery_defaults_to_backlog` | **RED (killed)** — 1 failed |
| f | quota guard — neutralize both `percent_numeric` and `conserve_synonym` patterns | `test_quota_guard_catches_paraphrased_pressure` | **RED (killed)** — **6 of 6 params failed**; restore → 6 passed |

**6 of 6 teeth killed** (minimum was 4). Note on (f): dropping both patterns makes *all six* paraphrased phrasings survive the guard, proving no other pattern covers them — the teeth are load-bearing, not vacuous. Post-restore full-pack check: **53 passed** (isolated), confirming clean revert.

---

## 5. Correction-bundle regression proofs (carried pre-activation bundle)

Spot-proved by reverting the fix in a scratch copy and confirming the named regression test goes RED (minimum was 3):

| Bundle item | Regression test | Revert result |
|---|---|---|
| G3 MAJOR-2 / MINOR-3 / G5 M1 (paraphrased percent + conserve) | `test_quota_guard_catches_paraphrased_pressure` | **RED** (mutant f above) |
| G3 MAJOR-1 / G5 M2 (word-boundary band-leak guard) | `test_leak_guard_word_boundary_passes_common_english` | **RED** — naive substring revert fails common-English ("landing"/"island"/"England") while band-vocabulary test still passes |
| G5 M3 (dot-segment/traversal/absolute lease) | `test_lease_paths_normalize_dot_segments_and_reject_traversal` | **RED** — disabling the `..` check lets `pkg/../other` and `..` through |
| G5 M4 (LeaseLedger serializes where snapshot cannot) | `test_grant_ledger_serializes_where_snapshot_validation_cannot` | **RED** (mutant c above) |
| G5 N1 (worker_text_fields fail-closed on unscannable types) | `test_worker_text_fields_fail_closed_on_unscannable_types` | **RED** — skipping instead of raising lets a dict / None field through |
| DCV R063 (likely-evidence-sources clause) | `test_extension_protocol_carries_likely_evidence_sources` | **RED** — removing the phrase fails the assertion |

**6 of 9 items executably proven RED.** Remaining three verified by non-vacuous passing tests read directly: G3 MINOR-4 root-lease (`test_root_lease_rejected_not_dodged`), G3 MINOR-5 size-class registry (`test_size_class_error_codes_registered_consistently`, asserts `set(SIZE_CLASS_ERROR_CODES) == {"bad_declared_class","bad_size_class"}`), G4 ADV-1 non-omittable categories (`test_mandatory_packet_categories_cannot_be_omitted` — ran green in the full 54-pack; not runnable in my isolated harness because it needs sibling `tools.context_pack_budget`). G4 ADV-2/3 and G5 N2/N3 are recorded dispositions, not code changes — nothing to regress.

---

## 6. Negative / robustness / determinism probes (36/36 pass)

Independent probes against the real modules (not the producer's tests):

- **Boundary occupancies at exact thresholds:** 0.50→observe, 0.4999→normal, 0.70→prepare, 0.85→land, 0.95→emergency-stop, 1.0→emergency, 0.0→normal (`>=` semantics correct on every band edge).
- **near_complete requires coherent:** near_complete+`coherent=False`→SEND_LANDING (not allow-seam); near_complete+coherent→ALLOW_SEAM.
- **Catastrophic ceiling boundary:** `ceiling_tokens == normal_range * min_multiple` passes; one below raises `bad_ceiling`; fires exactly at `ceiling_tokens`, not one below.
- **HealthBands fail-closed:** band-order violation → `band_order`; value ≥1 → `bad_band`; value ≤0 → `bad_band`; `bands_for_model` unknown key → `unknown_band_key`, non-mapping → `bad_section`, empty model → `missing_model`.
- **Emergency condition** unknown → `bad_emergency_condition`.
- **Empty lease tuple:** reader consumes no writer slot; reader write attempt → `scope_violation`; unknown grant write → `unknown_grant`.
- **Duplicate/unknown children:** duplicate register → `duplicate_child`; unknown land/continue → `unknown_child`.
- **Ledger drain:** duplicate grant → `duplicate_grant`; releasing a parent with a live child → `children_not_drained`.
- **at_minutes ties + determinism:** `decide_extension` identical on repeat with equal `at_minutes`; `evaluate_band` identical on repeat (dataclass equality); no-progress window fires at exactly 20 min, silent at 19.999; repeated-attempt limit fires on the 3rd, quiet on the first two.
- **No wall-clock / randomness:** grep of the 5 new modules found **no** `time`/`random`/`datetime`/`sleep`/`perf_counter`/`threading` imports or calls (only two English comment lines). The accelerated-clock claim holds: all clocks are injected `at_minutes` floats.
- **Shadow-only / no actuation:** grep found **no** `subprocess`/`Popen`/`os.system`/`spawn`/`kill`/`socket`/`open(`/`.write(`/`send_message`/`resume`/`threading` in any new module. Every output is a frozen record or typed refusal; R595/§18 activation gate untouched.

---

## 7. s16.2 coverage audit (named cases → non-vacuous tests)

Every packet-named supervision case maps to a real test whose body asserts the behavior (all test bodies read):

| s16.2 case | Test | Assertion substance |
|---|---|---|
| observe → no worker message | `test_observe_band_produces_no_worker_message` | band OBSERVE, action EXTERNAL_CHECK, `worker_message is None`, `apply()` returns None |
| forty-minute-equivalent landing (accelerated) | `test_forty_minute_equivalent_investigation_landed_in_accelerated_time` | UNBOUNDED_SEARCH + NO_PROGRESS raised; extension DENY_BACKLOG; action ≠ EMERGENCY_STOP |
| high-usage near-seam completion | `test_high_usage_near_seam_completion_reaches_safe_seam` | band LAND, action ALLOW_SEAM, no message (teeth: mutant a) |
| TaskStop reserved for emergencies | `test_taskstop_reserved_for_emergency_conditions` | ordinary landing ≠ EMERGENCY_STOP; emergency occupancy & owner-stop → EMERGENCY_STOP; bad condition raises |
| catastrophic ceiling + partial-state recovery | `test_catastrophic_ceiling_must_sit_far_outside_normal_range`, `test_ceiling_fire_produces_partial_state_recovery`, `test_platform_caps_rejected_as_routine_sizing` | bad_ceiling; quarantined & not completed; false_completion raise; routine_cap raise |
| child turnover rows | `test_active_child_finishes_bounded_contract_during_parent_landing`, `test_child_landing_returns_one_instruction_and_partial_handoff`, `test_child_api_failure_is_an_explicit_state` | healthy child continues, no new children once landing; one instruction then None; failed-api requires explicit error |
| nested-cap evasion | `test_nested_children_cannot_evade_producer_cap_or_leases`, `test_ledger_exactness_...` | nested 4th writer → producer_cap; nested overlap → lease_overlap |
| transcript out of context | `test_verbose_child_transcript_stays_out_of_primary_context` | MAX_SUMMARY_CHARS boundary ok; +1 char → transcript_not_summary |
| one-message landing / sparse | `test_land_sends_one_concise_direction_exactly_once` | exactly one record, second apply None (teeth: mutant b) |
| scope drift → extension, never silent | `test_scope_drift_produces_extension_request_not_silent_continuation` | out-of-lease write → SCOPE_DRIFT / extension-review; in-lease → none |
| unrelated → backlog; blocking → least-costly | `test_unrelated_discovery_defaults_to_backlog` (teeth: mutant e), `test_blocking_discovery_gets_least_costly_bounded_extension` | DENY_BACKLOG vs APPROVE with bounded_addition = least-costly experiment |
| Codex approves/denies without editing code | `test_extension_decision_is_a_record_not_a_code_edit` | no apply/execute/run/edit/write attribute; unbounded approval raises |
| findings carry no worker surface | `test_repeated_corrections_get_outside_decision_without_countdown` | DetectorFinding field set is exactly {assignment_id, kind, detail, at_minutes, requires}; no worker_message |
| per-model band calibration / conservative unknown | `test_bands_calibrated_per_resolved_model_fail_closed`, `test_unknown_occupancy_is_conservative_never_normal` | override honored, fallback to global, unknown key raises; None occupancy → OBSERVE |

No vacuous assertions found.

---

## 8. Defects

- **MAJOR:** none.
- **MINOR:** none.
- **ADV-1 (advisory, non-blocking):** In `runtime_health.evaluate_band`, the combination `model_reports_losing_thread=True` with `near_complete=True` + `coherent=True` yields `action=allow-reach-seam`, `worker_message=None`, `requires_review=False` — the "immediate quality signal regardless of counters" intent of `model_reports_losing_thread` is silently overridden by the allow-seam branch, and no test asserts behavior for this combination. This is benign in practice (allow-seam requires `coherent=True`, which contradicts a model that is losing the thread, so a controller would not set both), but the interaction is undocumented and untested. Suggest either (a) an inline note that losing-thread is intentionally subordinate to a coherent near-complete seam, or (b) a test pinning the chosen behavior. Verified live: `EDGE losing-thread+near_complete+coherent -> band LAND, action=allow-reach-seam, worker_msg=False, requires_review=False`.

---

## 9. Required rework

None blocking. Recommended (not required for acceptance): address ADV-1 with a documenting note or a pinning test in a future defect-lane increment.

---

## 10. Limitations (evidence-capture division of labor — not BLOCKED)

1. **Git byte-identity `ee564dd..HEAD`** could not be reproduced in my sandbox (the worktree guard refuses git against the `ctl24` shared checkout). I reviewed the on-disk working tree at `ctl24` and reproduced all tests against it. **Requires orchestrator confirmation** that the `ctl24` working tree equals frozen content `ee564dd` and that post-freeze commits are control-plane only.
2. **Full ~50-min composite (2707/3/0)** was verified by arithmetic + four live slices (434 green), not re-run end-to-end; CI/orchestrator holds the full-run artifact.
3. **G4 ADV-1 bundle test** (`test_mandatory_packet_categories_cannot_be_omitted`) ran green only in the full 54-pack (needs sibling `tools.context_pack_budget`), not in my isolated mutation harness — a harness artifact, not a product failure.

---

## 11. Conclusion

**G4 verdict: PASS.** The five runtime modules and the 54-test pack are present, substantive, deterministic, and shadow-only (no actuation surface, no wall-clock/randomness, injected accelerated clocks). All required test evidence reproduced (54/0, 53/0, 305/0, plus 22/0 spot); composite 2707/3/0 confirmed by arithmetic and live slices. Mutation teeth are strong: **6/6 killed** (RED-on-mutant, GREEN-on-actual). The carried correction bundle is real: **6/9 items proven RED by revert/mutation**, the remaining 3 verified by non-vacuous passing tests. All s16.2 named cases map to non-vacuous tests; 36/36 independent boundary/negative/determinism probes pass; modularity EXIT=0 (no new warning) and ruff clean. Only one advisory (ADV-1), non-blocking. No corrections are required for acceptance.

---

**Requested status to orchestrator:** record G4 = **PASS** for M0-T091 at frozen content `ee564dd`, subject to the orchestrator's own confirmation of Limitation-1 (working-tree byte-identity to `ee564dd`). Files reviewed (all absolute): `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\{lease_runtime,runtime_health,runtime_detectors,extension_gate,child_handoff,subagent_contracts}.py` and `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\test_agent_supervisor_runtime_supervision.py`.

---

## Orchestrator discharge of Limitation-1 (recorded at gate time, not reviewer text)

`git diff --stat ee564dd..HEAD -- tools/agent_supervisor tools/test_agent_supervisor_runtime_supervision.py project-control/reports/M0-T091-runtime-supervision.md` → **empty** at gate-recording HEAD (post-freeze commits are control-plane only: G2/submit, D-029 capture, G5/G3 review records). Working tree clean at recording. Independently, both G3 and G5 (git-capable sandboxes) verified the same byte-identity in their own reports. Limitation-2 (composite 2707/3/0) is held as the orchestrator-captured foreground run recorded in `M0-T091-G2-self-check.md` §2.
