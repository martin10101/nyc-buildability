# M0-T091 — D-024 C2: invisible runtime supervision

**Producer:** orchestrator · 2026-08-26 UTC · branch `control/D-024-fable-codex-loop`
**Authority:** campaign `D-024-fable-codex-loop` seq 6 NEXT (owner directive D-024 v4); completion,
review, acceptance, and the post-seam HOLD explicitly ordered by owner directive **D-029**
(captured mid-production). Supervisor-freeze qualifying evidence: **D-024-R101** (Phase C), cited
in the packet, every new module docstring, and the content commit message.

## 1. What was built (five focused runtime modules + one test pack + corrections)

All inside `tools/agent_supervisor/` (leaf package preserved — no graph/index import; the only
cross-module dependencies are the accepted C1 contract schemas and `telemetry_records`
vocabularies), each with its own typed error class, frozen records, closed vocabularies, and the
D-024 docstring convention:

| Module | Lines (raw `wc -l`) | Responsibility (D-024 anchor) |
|---|---|---|
| `lease_runtime.py` | 163 | the SERIALIZED grant ledger the G5 M4 correction demanded: every grant (parent or nested child) passes through ONE `LeaseLedger` that validates against the LIVE active set and folds each grant in before the next candidate; producer cap and overlap refusal therefore cannot be raced through a stale snapshot; child grants name a live parent; release refuses while children hold grants (exact-once, s6.3); `assert_write_within_scope` fails closed on any write outside the lease (Phase C item 4) |
| `runtime_health.py` | 478 | `TelemetrySnapshot` (by-value Phase B telemetry; unknown=None never zero; closed source/confidence vocabularies), `evaluate_band` (s5.4/s5.5: occupancy→band; unknown occupancy conservative; model-says-losing-thread = immediate LAND signal; no-progress/scope-drift force review regardless of tokens; near-complete+coherent at high usage → ALLOW-REACH-SEAM; emergency ONLY under the s5.5 closed condition set), `SupervisionState` (one-message landing discipline: the single concise `LANDING_DIRECTION_TEXT` proven through BOTH contract guards at send time; observe/prepare produce NO message; prepare holds scope), `bands_for_model` (per-resolved-model calibration, fail-closed config), `CatastrophicCeiling`/`validate_platform_caps` (maxTurns/spend caps refused as routine sizing; ceiling must sit ≥5× outside the normal range) + `ceiling_fired` → `PartialStateRecovery` (quarantine+reconcile, never false completion) (Phase C items 4, 6) |
| `runtime_detectors.py` | 274 | `ActivityEvent` on an INJECTED accelerated clock; durable-evidence closed set (s6.2) — only `evidence` events reset the window; repeated command/hypothesis signatures, cycling test failures, unbounded searches, stalled summaries, bare-clock no-progress `check()`, and file-writes outside the lease → typed `DetectorFinding`s routed to landing/extension review; findings carry NO worker-visible surface (Phase C item 4) |
| `extension_gate.py` | 213 | the s6.1 runtime: `ExtensionRequest` validates ALL s6.1 return items fail-closed (incl. the R063 likely-evidence-sources clause), `decide_extension` defaults to DENY→backlog unless the discovery blocks correctness/security/data-integrity/the current acceptance criterion, approvals grant exactly the least costly bounded experiment with its completion point, `ExtensionDecision` is a RECORD with no apply surface (Codex approves/denies without editing code), `BacklogEntry` for unrelated/denied discoveries (Phase C item 4) |
| `child_handoff.py` | 212 | `ChildHandoff` (durable partial handoffs; `failed-api` requires an EXPLICIT error; `bounded_summary` capped at 4000 chars so a transcript can never ride back into the primary context) + `TurnoverCoordinator` (s6.3 draining: no new children once landing begins; healthy children finish their bounded contracts; ONE landing instruction per child; successor orients read-only anytime but gains write authority only after children reconciled + external effects reconciled + zero live writer grants) (Phase C item 6) |

Test pack `tools/test_agent_supervisor_runtime_supervision.py` (849 raw lines, **54 tests**,
pytest style, deterministic, no network, accelerated clocks — no sleeps).

**Supervision stays INVISIBLE and SHADOW-ONLY:** workers never see counters, band names,
thresholds, or countdowns (R045/R050 unchanged; the only worker-visible artifact any module can
produce is the single guard-proven landing sentence). Nothing spawns, resumes, stops, or messages
a live agent; every output is a record/refusal. R595 and the D-024 §18 activation gate untouched.

## 2. Carried pre-activation correction bundle — disposition (all APPLIED here)

| Correction | Disposition |
|---|---|
| **G3 MAJOR-1 / G5 M2** (leak guard false-positives on `observe`/`land`) | `assert_no_envelope_leak` now matches `_BAND_LEAK_PATTERNS` — word-boundary vocabulary tokens (`prepare_to_land`, `emergency_stop`, spaced/hyphen variants) and band-context phrases (`band <name>` / `<name> band`). "landing page", "island", "England", "observe the failing test" pass; band vocabulary still fails closed. Tests: `test_leak_guard_word_boundary_passes_common_english`, `test_leak_guard_still_catches_band_vocabulary`. |
| **G3 MAJOR-2 + MINOR-3 + G5 M1** (paraphrased percent/conserve pressure) | `_QUOTA_PATTERNS` gains `percent_numeric` (any numeric percent, spaced or spelled) and `conserve_synonym` (save/spare/economize/economical/frugal aimed at tokens/context/budget/window/capacity); `HealthBands.numeric_strings()` adds the `70 %`/`70 percent` forms. All four G3 finding-B probes now rejected; plain engineering usages ("Save and test what is coherent") still pass. Tests: `test_quota_guard_catches_paraphrased_pressure` (6 phrasings), `test_quota_guard_still_accepts_plain_engineering_language`, `test_leak_guard_catches_spaced_and_spelled_percent_thresholds`. |
| **G3 MINOR-4** (root `/` lease normalizes to empty and dodges overlap) | `_normalize_lease_path` refuses a path that normalizes to the repository root; `validate_envelope` normalizes `write_lease_paths` so the bad lease dies at validation and at `LeaseLedger.grant`. Test: `test_root_lease_rejected_not_dodged`. |
| **G5 M3** (dot-segments/absolute/traversal) | same normalizer: `posixpath.normpath` canonicalization (`./pkg`→`pkg`, `pkg/./sub`→`pkg/sub` now overlap), absolute (POSIX root, drive letter, UNC) and `..` traversal refused with `bad_lease_path`. Test: `test_lease_paths_normalize_dot_segments_and_reject_traversal`. |
| **G3 MINOR-5** (size-class error-code inconsistency) | both code strings are PINNED by the accepted M0-T090 pack, so the fix is a single registered closed set `workload_classifier.SIZE_CLASS_ERROR_CODES = ("bad_declared_class", "bad_size_class")` with the mapping documented at the vocabulary owner; callers treat them as one condition. Test: `test_size_class_error_codes_registered_consistently`. |
| **G5 M4** (assert_grantable snapshot-vs-lock) | documented in the `assert_grantable` docstring (snapshot, not a lock; runtime must serialize) AND implemented: `lease_runtime.LeaseLedger` serializes grants and folds each grant into the active set. Test: `test_grant_ledger_serializes_where_snapshot_validation_cannot` (proves the snapshot hole first, then the ledger closing it). |
| **G5 N1** (worker_text_fields silently skips unscannable types) | `worker_text_fields` now raises `unscannable_field` on any non-str/tuple-of-str field (bool explicitly exempt as the one non-text flag). Test: `test_worker_text_fields_fail_closed_on_unscannable_types`. |
| **G4 ADV-1** (every s13 category omittable) | `workload_sizing.NON_OMITTABLE_CATEGORIES = (bounded_task_and_acceptance, authority_and_prohibitions, return_schema)`; `packet_plan` raises `non_omittable_category` regardless of justification; role-dependent categories stay omittable (existing reviewer-omission test unchanged). Test: `test_mandatory_packet_categories_cannot_be_omitted`. |
| **DCV R063** (likely-evidence-sources clause) | `DEFAULT_EXTENSION_PROTOCOL` now reads "…the additional scope with its likely evidence sources and its natural completion point…"; the runtime `ExtensionRequest` requires a non-empty `likely_evidence_sources` tuple. Tests: `test_extension_protocol_carries_likely_evidence_sources`, `test_extension_request_validation_fail_closed`. |
| G4 ADV-2/ADV-3, G5 N2/N3 (recorded, non-bundle) | ADV-2 (regex guards cannot catch all natural-language pressure) and N2 (noun-context percent trade) are narrowed by the new broad `percent_numeric`/`conserve_synonym` classes; the residual is the documented fail-closed trade. ADV-3 (short numeric substring false-positives) unchanged — fail-closed direction, explicitly "noted only for completeness". N3 (prompt-template fencing for untrusted values) remains forward-looking: assignment authors are the controller; no untrusted substitution exists in this unit. |

## 3. s16.2 coverage map (the packet's supervision cases)

- observe produces no worker message → `test_observe_band_produces_no_worker_message`; normal → `test_normal_band_takes_no_action`
- prepare-to-land prevents new scope/children outside the model context → `test_prepare_to_land_holds_scope_without_worker_message` (+ coordinator `test_active_child_finishes_bounded_contract_during_parent_landing`)
- land sends ONE concise direction → `test_land_sends_one_concise_direction_exactly_once`, `test_landing_direction_passes_both_guards_and_carries_no_numbers` (sparse/durable/within authority)
- high usage + coherent near-complete reaches its safe seam → `test_high_usage_near_seam_completion_reaches_safe_seam`
- low usage + repeated speculation triggers review → `test_low_usage_repeated_speculation_triggers_review`
- model losing the thread = immediate quality signal → `test_model_losing_thread_is_immediate_quality_signal`
- forty-minute-equivalent investigation landed/denied in ACCELERATED time → `test_forty_minute_equivalent_investigation_landed_in_accelerated_time`
- repeated searches/hypotheses/test failures → no-progress handling → `test_repeated_commands_hypotheses_test_failures_trigger_no_progress`, `test_text_volume_and_tool_activity_are_not_progress`, `test_successive_summaries_without_evidence_stall_out`, `test_durable_evidence_resets_counters_and_window`
- repeated corrections → OUTSIDE decision, no countdown exposed → `test_repeated_corrections_get_outside_decision_without_countdown`
- scope drift → extension request, never silent continuation → `test_scope_drift_produces_extension_request_not_silent_continuation`
- unrelated discoveries → backlog → `test_unrelated_discovery_defaults_to_backlog`; blocking discovery → least costly bounded extension → `test_blocking_discovery_gets_least_costly_bounded_extension`
- Codex approves/denies without editing code → `test_extension_decision_is_a_record_not_a_code_edit`
- TaskStop reserved for emergencies (never ordinary landing) → `test_taskstop_reserved_for_emergency_conditions`
- no routine maxTurns/spend caps; catastrophic-ceiling partial-state recovery → `test_platform_caps_rejected_as_routine_sizing`, `test_catastrophic_ceiling_must_sit_far_outside_normal_range`, `test_ceiling_fire_produces_partial_state_recovery`
- active child finishes bounded contract during parent landing → `test_active_child_finishes_bounded_contract_during_parent_landing`
- landing child returns coherent partial handoff → `test_child_landing_returns_one_instruction_and_partial_handoff`
- child API failure = EXPLICIT state → `test_child_api_failure_is_an_explicit_state`
- nested children cannot evade cap/leases → `test_nested_children_cannot_evade_producer_cap_or_leases` (+ ledger exactness tests)
- parent rotation never creates overlapping writers; read-only orientation allowed → `test_parent_rotation_never_creates_overlapping_writers`
- verbose child transcript stays out of primary context → `test_verbose_child_transcript_stays_out_of_primary_context`
- read-only agents run without write authority/cap impact → `test_read_only_agents_do_not_consume_the_producer_cap`
- per-model private band calibration fail-closed → `test_bands_calibrated_per_resolved_model_fail_closed`; conservative unknown occupancy → `test_unknown_occupancy_is_conservative_never_normal`; validation fail-closed packs for snapshots/events/requests/handoffs

## 4. Integration decisions a reviewer should check deliberately

- **Leaf discipline intact:** the runtime modules import only sibling C1 schemas and
  `telemetry_records` vocabularies; telemetry arrives BY VALUE in `TelemetrySnapshot` (callers
  adapt the accepted Phase B feeds); no graph/index import; no new dependency.
- **`evaluate_band` emergency fallback:** occupancy ≥ emergency always implies the
  `imminent-hard-limit` condition, so the post-condition `band == EMERGENCY` branch that demotes
  to LAND is deliberately defensive (documented in-line) — it exists so a future edit to the
  auto-condition line cannot silently create an uncondition​ed platform stop.
- **One-message discipline lives in `SupervisionState`, not `evaluate_band`:** evaluation stays a
  pure function (testable/replayable); the mutable per-assignment state enforces sparseness and
  re-proves the message through `assert_worker_text_clean` + `assert_no_envelope_leak` at send.
- **`LANDING_DIRECTION_TEXT` wording** deliberately contains "save and test what is coherent" —
  the broadened conserve-synonym guard requires a token/context/budget noun nearby, so honest
  engineering "save" survives while "save tokens" dies; this exact sentence is guard-proven in
  the pack.
- **Pinned error codes honored:** the G3 MINOR-5 fix adds a registry constant instead of renaming
  either pinned code (`bad_size_class` / `bad_declared_class` are asserted by the accepted
  M0-T090 pack, which this task may not edit).
- **`MAX_SUMMARY_CHARS = 4000`** is a policy choice: far above any honest bounded summary in this
  repo's agent returns, far below a transcript; the constant is public for future calibration.
- **False friend:** `worker_turnover.py` / `model_turnover.py` are the D-007 supervisor-loop
  turnover modules; the s6.3 CHILD draining rules live in the new `child_handoff.py` and do not
  touch them.

## 5. Self-checks (G2 doc completes the suite figures)

- New pack: **54 passed / 0 failed**. Combined with the C1 pack: **107 passed**. Adjacent
  supervisor/context packs (statusline handler, telemetry core, subagent telemetry, rotation,
  scheduler, context-pack): **305 passed / 0 failed**.
- **Full composite `tools/` suite (supervisor-freeze baseline duty): 2707 passed / 3 skipped /
  0 failed** = 2653 accepted baseline + 54 new (chunks: 2587/3/0 + 106 + 14; same 3 adjudicated
  env-conditional skips).
- `ruff check` over all 9 touched/new files: clean. `python tools/modularity_check.py --check`:
  exit 0 (largest new module `runtime_health.py` 478 raw lines, under the 600 warn line; no new
  warning).
- No dependency added; no forbidden path touched; PR #241 untouched; no actuation surface;
  existing C1 pack (outside this packet's write scope) untouched and green under the corrected
  guards.
- Mid-production owner directive **D-029** captured (finish-and-hold seam); registry validator
  run at the capture (exit recorded in the G2 doc).
