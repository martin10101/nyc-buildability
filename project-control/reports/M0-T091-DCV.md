# M0-T091 — Directive-Compliance Verification (DCV)

> Saved VERBATIM by the orchestrator from the directive-compliance-verifier agent-return
> channel (transport entity-decoding only). Verdict: PASS (46/46 SATISFIED; 4 non-blocking
> advisories). Reviewer preamble: "I have reproduced all required primary evidence."

I have reproduced all required primary evidence. Here is my complete DCV report.

---

# DCV REPORT — M0-T091 (D-024 C2: invisible runtime supervision)

**Verifier:** directive-compliance-verifier (independent; producer = orchestrator, producer ≠ verifier)
**Mode:** READ-ONLY. No repository/control-plane/git writes performed.
**Directive:** D-024, `directive_refs = D-024:ALL`
**Frozen content commit:** `ee564dd1c6352366deeee7b28f6d588d52ef0474`

**PRIMARY-EVIDENCE STATEMENT:** I reproduced ALL primary evidence myself — the deliverable blob SHAs (git objects), the applicable-set resolver, the material-identity computation, the module source (read line-by-line for every mechanism), the runtime + bounded-contracts test packs, a broad adjacent-pack regression run, the modularity checker, and the directive-compliance validator. The producer's evidence map and report were treated as claims and independently reproduced. No requirement below is listed as covered without cited reproduced evidence.

---

## 1. Content identity observed (reproduced)

| Check | Reproduced value |
|---|---|
| Frozen content commit | `ee564dd` |
| Live HEAD at dispatch | `b4f7e40` |
| Live HEAD during my run | advanced `b4f7e40` → `50d09d0` (G5 PASS record) → `60485fd` (G3 PASS record) — the parallel review wave landing control-plane gate records under D-029 "agents finish naturally" |
| Material identity (G2 `content_manifest_sha256`) | `2880691790763d42346117f2a094b9ceb3cb6bdba12a5d97c2816ef6a9eefe1d` |
| Material identity recomputed by me at HEAD via `project_control._task_git_identity(reg, task)` | `2880691790763d42346117f2a094b9ceb3cb6bdba12a5d97c2816ef6a9eefe1d` — **EXACT MATCH** to G2 and to the G5 gate record |
| Deliverable blobs (8 modules + test pack) `ee564dd` vs live HEAD | **9/9 byte-identical** (verified at `b4f7e40`, `50d09d0`, and `60485fd`) |
| Post-freeze commits `ee564dd..HEAD` | project-control/** ONLY (gates, reports, state, tasks); `grep -v '^project-control/'` = empty |
| Content commit `ee564dd~1..ee564dd` scope | 8 modules under `tools/agent_supervisor/` + `tools/test_agent_supervisor_runtime_supervision.py` + `project-control/reports/M0-T091-runtime-supervision.md` — 100% within allowed_paths, zero forbidden paths |
| Blob SHAs (ee564dd=HEAD) | lease_runtime `adcf042`, runtime_health `c002dd5`, runtime_detectors `9368cc3`, extension_gate `3cd8a3c`, child_handoff `0be96ee`, subagent_contracts `a0db382`, workload_classifier `7e4791d`, workload_sizing `13ef920`, test pack `3d843a7` |

The material-identity function fails closed for a non-HEAD `reviewed_sha` but returns the identical digest at the moving HEAD because the allowed_paths blobs are unchanged — this is the expected "material identity stable across control-plane commits" property, independently reproduced.

## 2. Applicable-set reproduction (selective-citation check)

`load_registry().evaluate_task_refs(<M0-T091 task dict>)` → `ok=True`; **46 applicable ids**; `cited_ids`=46; `missing_ids`=[]; `invalid_refs`=[]; `unresolved`=[]. The applicable set is **exactly equal** to the 46 keys of `project-control/reports/M0-T091-evidence-map.json` (set-difference empty both directions). **No selective-citation failure.**

Amendment 2 (`source-002-amendment.md`, R129–R138 statusline capability) is correctly OUTSIDE this runtime-supervision task's applicable set. Source digests reproduced: `source-001.md` = `0611bb45…f754537` and `source-002-amendment.md` = `45f7726e…0cb078c`, both matching `manifest.json`. `requirements.json` holds 138 rows (R001–R138, no gaps). `validate_directive_compliance.py --check` → **EXIT=0** (fail-closed validator silent on success).

D-029 mid-task capture: verbatim owner text between `VERBATIM-BEGIN/END` markers; 6 requirements all bound to sentinel `D-029-BOOTSTRAP` (empty task_types) → inert for M0-T091; the clean `evaluate_task_refs` confirms D-029 raises no uncited-applicable obligation. Conduct-only; M0-T091's cited applicable set unchanged.

## 3. Per-requirement verdicts (ALL 46) — reproduced evidence

Reproduced test totals underpinning the table: runtime pack **54/54 PASSED, 0 skipped** (`-v`, 49 defs + 5 parametrized); bounded_contracts **53/53**; broad `agent_supervisor+adjacent` run **2183 passed / 2 skipped / 0 failed**; modularity `--check` **exit 0** (5 pre-existing warnings, none in the new modules); composite arithmetic 2653 accepted baseline + 54 reproduced = **2707** (consistent with the claimed 2707/3/0).

| ID | State | Reproduced primary evidence | Note |
|---|---|---|---|
| R002 | SATISFIED | content commit within allowed paths; no transport/loop/spawn surface; composite green | conduct |
| R003 | SATISFIED | no loop.py/cli.py edit in ee564dd; runtime modules import no graph/index | conduct |
| R004 | SATISFIED | `extension_gate.ExtensionDecision` has no apply surface; `test_extension_decision_is_a_record_not_a_code_edit` PASS | no-violation |
| R007 | SATISFIED | D-029 captured verbatim (marker-delimited), not paraphrased | conduct |
| R008 | SATISFIED | no owner questions; D-029 finish-and-hold honored (this review wave is the honored "finish/review/accept") | conduct |
| R010 | SATISFIED | `git branch --contains ee564dd` = control branch only; `main`=`d8b3899` untouched; no merge commits in range | prohibition |
| R017 | SATISFIED | `D-024-R101` in packet objective + all 8 touched module docstrings + commit `ee564dd` msg | conduct/freeze |
| R018 | SATISFIED | runtime modules reuse C1 schemas (`SupervisionEnvelope`,`HealthBands`,`assert_grantable`) + `telemetry_records`; report §4 false-friend check | reuse |
| R020 | SATISFIED | ee564dd scope = allowed paths only; control-branch commits only | conduct |
| R021 | SATISFIED | `TelemetrySnapshot.source` validated vs closed `TELEMETRY_SOURCES`; no Codex action surface added | no-violation |
| R022 | SATISFIED | all outputs are frozen records/refusals; no mutation surface | no-violation |
| R023 | SATISFIED (**discharge**) | `LeaseLedger.grant` serializes + folds active set; `assert_write_within_scope` raises `scope_violation`; `test_scope_enforcement_fails_closed`, ledger tests PASS | runtime enforcement DISCHARGED |
| R025 | SATISFIED | no dispatch/accept path; `decide_extension`/`evaluate_band` return records | no-violation |
| R026 | SATISFIED | R595/activation untouched; shadow-only; report §1 | no-violation |
| R042 | SATISFIED | `TelemetrySnapshot.__post_init__` validates source/confidence closed vocabs, unknown=None; `test_snapshot_validation_fail_closed` PASS | |
| R045 | SATISFIED | `_QUOTA_PATTERNS` adds `percent_numeric`+`conserve_synonym`; `worker_text_fields` raises `unscannable_field`; `test_quota_guard_catches_paraphrased_pressure`[×6], `_worker_text_fields_fail_closed_on_unscannable_types`, `_landing_direction_passes_both_guards` PASS | |
| R046 | SATISFIED (**discharge**) | `evaluate_band` occupancy→band; `AssignmentMonitor` no-progress/repeated/scope-drift; findings force `requires_review`; band+detector tests PASS | runtime bands DISCHARGED |
| R047 | SATISFIED | only worker-visible output is guard-proven `LANDING_DIRECTION_TEXT`; measurements never in worker text | |
| R048 | SATISFIED | `workload_classifier.SIZE_CLASS_ERROR_CODES=("bad_declared_class","bad_size_class")`; `test_size_class_error_codes_registered_consistently` PASS; C1 53/53 | |
| R049 | SATISFIED | `startup_overhead.py` not in ee564dd file list (untouched) | |
| R050 | SATISFIED | `bands_for_model` per-model fail-closed; `numeric_strings` adds `70%`/`70 %`/`70 percent`; `test_bands_calibrated_per_resolved_model_fail_closed`, leak-guard tests PASS | |
| R051 | SATISFIED (**discharge**) | `validate_platform_caps` raises `routine_cap`; `CatastrophicCeiling` requires ≥5×; `ceiling_fired`→`PartialStateRecovery` (`false_completion` impossible); 3 ceiling tests PASS | catastrophic-ceiling recovery test DISCHARGED |
| R052 | SATISFIED (**discharge**) | `bands_for_model(config,resolved_model)`; `BandEvaluation.reasons`/`ExtensionDecision.reasons` recorded for calibration | live calibration surface DISCHARGED |
| R053 | SATISFIED | `evaluate_band` promotes to LAND on `model_reports_losing_thread` at any level; `test_model_losing_thread_is_immediate_quality_signal` PASS | |
| R055 | SATISFIED | `DEFAULT_EXTENSION_PROTOCOL` carries "likely evidence sources … natural completion point"; C1 pack 53/53 (no field regression); `test_extension_protocol_carries_likely_evidence_sources` PASS | |
| R056 | SATISFIED (**discharge**) | `_BAND_LEAK_PATTERNS` word-boundary vocab/context (not substring); numeric leak set extended; `test_leak_guard_word_boundary_passes_common_english`, `_still_catches_band_vocabulary`, `_catches_spaced_and_spelled_percent_thresholds` PASS | leak-guard graduation DISCHARGED |
| R057 | SATISFIED | `spawn_decision.py` untouched; `SupervisionState.scope_held` + `TurnoverCoordinator.may_spawn_children`; `test_prepare_to_land_holds_scope_without_worker_message` PASS | |
| R058 | SATISFIED | startup-overhead measurement untouched; shadow-only resumes nothing | |
| R059 | SATISFIED | no model-routing change; `bands_for_model` conservative per-model | conduct |
| R060 | SATISFIED | `LeaseLedger.grant`→`assert_grantable` vs live active set; nested via `parent_assignment_id` fold; `test_nested_children_cannot_evade_producer_cap_or_leases`, `_read_only_agents_do_not_consume_the_producer_cap` PASS | |
| R061 | SATISFIED (**discharge**) | `ChildHandoff.bounded_summary` capped `MAX_SUMMARY_CHARS=4000` (`transcript_not_summary`); `test_verbose_child_transcript_stays_out_of_primary_context` PASS | bounded-summary construction DISCHARGED |
| R062 | SATISFIED (**discharge**) | `AssignmentMonitor` counts command/hypothesis signatures + cycling failures vs `repeated_attempt_limit`; findings carry no worker surface; `test_repeated_corrections_get_outside_decision_without_countdown` PASS | runtime repeated-attempt DISCHARGED |
| R063 | SATISFIED (**discharge**) | `ExtensionRequest` requires all s6.1 items incl. `likely_evidence_sources`; `decide_extension` deny→backlog default; `test_extension_request_validation_fail_closed`, `_blocking_discovery_gets_least_costly_bounded_extension`, `_unrelated_discovery_defaults_to_backlog` PASS | extension-gate runtime + M0-T090 likely-evidence advisory DISCHARGED |
| R064 | SATISFIED (**discharge**) | only `DURABLE_EVIDENCE_KINDS` reset the window; `test_text_volume_and_tool_activity_are_not_progress`, `_low_usage_repeated_speculation_triggers_review`, `_durable_evidence_resets_counters_and_window` PASS | runtime no-progress DISCHARGED |
| R079 | SATISFIED | modules import only sibling C1 + `telemetry_records`; no graph/index import | |
| R080 | SATISFIED | `_band_from_occupancy(None)`→OBSERVE; `test_unknown_occupancy_is_conservative_never_normal` PASS | |
| R081 | SATISFIED | `workload_sizing` additive `NON_OMITTABLE_CATEGORIES`; existing omission/sufficiency tests green | |
| R092 | SATISFIED | `packet_plan` raises `non_omittable_category` for the 3 mandatory categories; `test_mandatory_packet_categories_cannot_be_omitted` PASS | |
| R098 | SATISFIED | `LeaseGrant.parent_assignment_id`, `ChildHandoff.parent_task_id`, `unlinked_records` refusals; `test_ledger_exactness_…` PASS | |
| R101 | SATISFIED (**discharge**) | item 4 (lease enforcement, cap, bands, no-progress, extension) + item 6 (sparse landing, TaskStop reserved, child handoffs + turnover draining) all present in code + tests; C1 report §1 deferral discharged | Phase C 4+6 DISCHARGED |
| R108 | SATISFIED (**discharge**) | s16.2 rows executable: `test_forty_minute_equivalent_investigation_landed_in_accelerated_time`, `_high_usage_near_seam_completion_reaches_safe_seam`, `_observe_band_produces_no_worker_message`, `_taskstop_reserved_for_emergency_conditions`, ceiling+child-turnover rows; 54/54 PASS | s16.2 supervision rows DISCHARGED |
| R120 | SATISFIED | refusal guards `routine_cap`, `non_omittable_category`, `transcript_not_summary`, `unbounded_approval`, `children_not_drained`, `scope_violation` all present + tested | |
| R125 | SATISFIED | `M0-T091-G0-readiness.md` records primary cwd=worktree root, branch, HEAD `1d8d53f`=origin tip, clean tree, MCP-empty (committed `6968ed5`) | conduct |
| R126 | SATISFIED | G0-readiness records empty MCP roster (no `mcp__*` tools) | conduct |
| R127 | SATISFIED | no Gate-0 failure; no fallback root | conduct |
| R128 | SATISFIED | clean lineage `1d8d53f`→`6968ed5`→`9e47c27`→`ee564dd`→…; no failed-start adoption | conduct |

**Result: 46/46 SATISFIED. 0 VIOLATED, 0 BLOCKED, 0 UNVERIFIABLE.** All 10 named deferred-share discharges (R023, R046, R051, R052, R061, R062, R063, R064, R101 items 4+6, R108) are real and backed by executable tests I reproduced passing.

## 4. Advisories (non-blocking)

1. **Untracked working-tree file** `project-control/reports/M0-T091.json` (the submit record; its `content_manifest_sha256` = `2880691…` matches). It is under the control-plane material prefix, did not disturb the reproduced material identity (identity function returned clean), and is a routine submit artifact the orchestrator commits at acceptance. Note only — the D-029 "clean seam" verification is the orchestrator's post-DCV step. *(Orchestrator note: committed with the G4 review commit `c3f0558`.)*
2. **HEAD moved during this review** (`b4f7e40`→`50d09d0`→`60485fd`) as the parallel G5/G3 gate records landed. Deliverable blobs and material identity were unchanged at every point; expected under D-029.
3. Three M0-T090-accepted C1 modules (`subagent_contracts`, `workload_classifier`, `workload_sizing`) were modified here to carry the pre-activation correction bundle forward; the accepted M0-T090 pack still passes 53/53 under the corrected code — no regression to accepted behavior. Legitimate carry-forward, not a reopen.
4. Modularity: 5 new modules well under the 600-line warn threshold (largest `runtime_health.py` = 478); leaf discipline (only sibling C1 + `telemetry_records` imports) preserved; `modularity_check --check` exit 0 with no new warnings. Boundary answers hold against the actual diff.

## 5. Verdict

**PASS.**

At the frozen content identity `ee564dd` (material identity `2880691790763d42346117f2a094b9ceb3cb6bdba12a5d97c2816ef6a9eefe1d`, reproduced), every one of the 46 applicable D-024 requirements is independently verified SATISFIED from primary repository evidence. The applicable set reproduces exactly (46, no selective citation); source digests match and amendment 2 is reflected; the validator returns EXIT=0. Deliverable blobs are byte-identical from freeze through the current live HEAD and every post-freeze commit is control-plane only. Conduct rows hold: PR #241 and `main` untouched, no merge/deploy/dispatch, `D-024-R101` cited in packet + all 8 modules + the content commit, and D-029 captured verbatim, conduct-only, and inert for this task. No VIOLATED or UNVERIFIABLE result exists.

Recording of this verdict and any `verification.json` rows are for the orchestrator; I have performed no writes.

Relevant paths (absolute):
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\{lease_runtime,runtime_health,runtime_detectors,extension_gate,child_handoff,subagent_contracts,workload_classifier,workload_sizing}.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\test_agent_supervisor_runtime_supervision.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\gates\M0-T091-G2.json`, `…-G5.json`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\reports\M0-T091-{runtime-supervision.md,evidence-map.json,G0-readiness.md}`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\directives\D-024-fable-codex-loop\{source-001.md,source-002-amendment.md,requirements.json,manifest.json}`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\directives\D-029-m0t091-seam-hold\source-001.md`
