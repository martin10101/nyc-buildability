# M0-T105 independent directive-compliance verification (VERBATIM verifier return; transport entity-decoding only)

Saved by the orchestrator per the report-preservation rule. Verifier: directive-compliance-verifier
(independent, read-only, dispatched 2026-08-27; producer = fable-orchestrator-session ≠ verifier).
Overall verdict returned: **PASS**. Rows transcribed verbatim into
`project-control/directives/D-024-fable-codex-loop/verification.json` (M0-T105 entry).

---

# Independent Directive-Compliance Verification — M0-T105 (D-024 Amendment 3 unit D: native event integration)

**Verifier:** directive-compliance-verifier (independent; producer = fable-orchestrator-session, producer ≠ verifier)
**Frozen identity verified:** branch `control/D-024-fable-codex-loop`, HEAD `487a020` (confirmed via `git rev-parse`), deliverable `bfdf4ef` (confirmed), checkpoint `content_manifest_sha256 = 4bd0e18256d538b254a24a931b341c4b57b2851db15879dbcb4f86e336fe15d3` (confirmed in `project-control/reports/M0-T105.json`).
**Applicable set (independently re-derived, not taken on trust):** `DirectiveRegistry.evaluate_task_refs(M0-T105)` returns `applicable_ids = ['D-024-R154','D-024-R155','D-024-R173']`, `cited_ids` identical, `missing_ids = []`, `invalid_refs = []`, `unresolved = []`, `ok = True`.

## OVERALL VERDICT: PASS

---

## Frozen-identity discipline (verified, all clean)

- `git diff --stat bfdf4ef..HEAD -- tools/agent_supervisor/ .claude/hooks/supervisor_event_recorder.py tools/test_agent_supervisor_event_bus.py` is **empty** — the reviewed deliverable source is byte-stable since `bfdf4ef`; only control-plane/report/`.gitleaksignore` files moved after it (manifest `4bd0e182` stable).
- `git diff --stat 44a4c6c..HEAD -- .claude/hooks/readonly_agent_guard.py .claude/hooks/agent_dispatch_guard.py tools/agent_supervisor/native_runtime.py tools/agent_supervisor/runtime_backend.py .claude/settings.json` is **empty** — guards, native runtime backend, and settings.json all untouched across the unit.
- `python -m pytest tools/test_agent_supervisor_event_bus.py -q` → **38 passed** (reproduced personally, 1.65s).
- `python tools/validate_directive_compliance.py --check` → **EXIT=0**.

---

## D-024-R154 — Structured passive observation, consumed OUTSIDE Fable's context — **PASS**

- `tools/agent_supervisor/event_stream.py` is pure passive parsing: `parse_stream_json_line` / `ingest_stream_event` convert `--output-format stream-json` / `--forward-subagent-text` events into typed `TelemetryRecord`s. Reading the full 234-line module, there is **no model message, no prompt composition, no `SendMessage`, and no sidecar write anywhere** — it only produces records for the journal.
- statusLine sidecar stays PRIMARY: `test_s3_statusline_sidecar_stays_primary` asserts `"TelemetrySidecar" not in source` and that ingesting the full stream fixture creates only `{"hook_events.jsonl"}` in the temp dir — no sidecar surface exists in the module. Reproduced in the 38-pass run.
- R042 provider-exact labelling verified against code: `_step_measurements` stamps `label="provider-exact"`, `_result_measurements` stamps `label="sdk-cumulative"`, and absent usage yields `Measurement.unknown(...)` (never zero). `test_s3_usage_carries_source_confidence_labels` confirms `step_input_tokens.value==120 / label=="provider-exact"`, absent step `is_unknown` with `value is None`.
- R043 final_request caveat present in code: `_result_measurements` writes usage under `final_request_*` names with detail string `"...may describe only the final API request...never asserted as the whole subagent run (D-024 R043)"`; `test_s3_usage_carries_source_confidence_labels` asserts `"R043" in final.detail`.
- Forwarded subagent text is a digest reference, never a transcript: `ingest_stream_event` stores only `text_chars` + `text_sha256`; `test_s3_forwarded_text_is_reference_never_content` asserts the raw `text` is absent from the replayed store.
- "Never place token quotas/context numbers in worker assignments" and "never ask Fable for routine reports": these modules create no worker-facing text at all (passive observation only); the source obligation at `source-003-amendment.md:150` is mirrored faithfully by the requirement text (no weakening).

## D-024-R155 — Hooks as the event bus — **PASS**

- Required event set probed and fixtured: `tools/agent_supervisor/fixtures/hook_event_payloads_v1.json` holds exactly **17** payloads whose keys are precisely the R155 list — SessionStart, SessionEnd, UserPromptExpansion, UserPromptSubmit, SubagentStart, SubagentStop, TaskCreated, TaskCompleted, Stop, StopFailure, PreCompact, PostCompact, PostToolBatch, Notification, WorktreeCreate, WorktreeRemove, ConfigChange (verified by loading the JSON). `test_s1_every_required_event_ingests_one_record` publishes each and asserts `known is True`.
- Catalog fixture at official-docs confidence: `hook_event_catalog_2_1_247.json` records `claude_version "2.1.247 (Claude Code)"`, `confidence "official-docs"`, **31 events**, `drift_vs_2_1_220.added/removed == []`. `test_s8_recorded_drift_matches_computed_drift` asserts the recorded reconciliation equals `catalog_drift()` output (`no drift`).
- Measured-live C1 capture present: `hook_events_live_2026-08-27_m0t105_c1.json` = 9 records, `confidence "measured-live"`, version 2.1.247; `test_c1_live_fixture_masked_and_replayable` confirms 7 event types incl SessionStart/UserPromptSubmit/SubagentStart/SubagentStop/PostToolBatch/Stop/SessionEnd, all `session_id` `[SESSION sha256=`-masked, `TaskCreated` absent (measured fact: Agent spawn ≠ TaskCreated), and the live cross-process `bus_sequence==3` collision preserved.
- Recorder records without blocking/injecting/messaging: `.claude/hooks/supervisor_event_recorder.py` reads one JSON payload from stdin, publishes to `DurableEventBus`, and `_main` always `return 0` while printing nothing; top-level `except Exception: code=0`. `test_s9_recorder_records_and_stays_silent` asserts `returncode==0` and `stdout==""`; `test_s9_recorder_failure_fails_closed` and `test_s9_recorder_oversized_stdin_fails_closed` confirm fail-closed (malformed JSON / unwritable path / >1 MiB stdin all record nothing, exit 0).
- Command hook, not HTTP: `test_s11_recorder_is_command_hook_only` asserts none of `urllib/requests/http.client/socket/subprocess` appear in the recorder code, that `permissionDecision`/`additionalContext` are absent, and that stdin is the input. Verified against the actual source (reads `sys.stdin.buffer.read`).
- No committed tokens, sanitized fixtures: `test_s11_recorder_embeds_no_tokens` (no `sk-ant-`/`ghp_`/`Bearer ` shapes) and `test_s11_fixtures_are_masked` (no `Users\\`/`/Users/`/`MLFLL` in any fixture) both pass.
- Not self-registered: `grep -c` for the recorder in `.claude/settings.json` returns **0**; settings.json last changed in unrelated commit `4e238b5` (M0-T108), never in the M0-T105 range; recorder docstring documents that wiring is a separate reviewed change.
- Fast/deterministic/bounded/fail-closed: `MAX_STDIN_BYTES=1_048_576` cap; journal rotation bound (`test_s10_journal_rotation_bounds_disk`), dedup window bound (`test_s10_seen_keys_bounded`), registry bound (`test_s10_registry_bounded_at_bus_level`), broken-bounds rejection (`test_s10_rejects_broken_bounds`) all pass.

## D-024-R173 — Unit D native event integration (each element present + tested) — **PASS**

- Hook records: `DurableEventBus.publish` → reused `telemetry_hooks.ingest_hook_event`; `test_s1_firing_order_preserved` confirms 5 lifecycle events stored as `record_type=="lifecycle_hook"` in monotonic `bus_sequence` order.
- Stream-JSON subagent events: `publish_stream_line`/`publish_stream_event` → `ingest_stream_event`; `test_s3_stream_events_become_typed_records` confirms 6 fixture lines → 5 records (`record_type=="subagent_stream_event"`), 1 dedup.
- Deduplication: `idempotency_key` (event+session+task+event-id+content digest) with bounded `_seen` OrderedDict; `test_s2_duplicate_delivery_is_single_record` (duplicate → `None`, `duplicates_ignored==1`), `test_s2_idempotency_key_deterministic`, and `test_s3_stream_key_content_digest_fallback` (content-digest fallback when no uuid) all pass.
- Redaction: reused sanitize-first journal PLUS `_mask_uuids` recursive digest-masking of raw session/task UUIDs at any depth (values, list items, dict keys). `test_s4_durable_record_sanitized` asserts `realname`, `SECRET business plan`, `sk-ant-fake12345678`, and the raw UUID are all absent from the store while `[HOME]` and `[SESSION sha256=` are present; `test_s4_nested_uuid_masked_at_any_depth` (the round-1 converged G4-L2/G5-LOW-1/G3-A4 finding) confirms ≥4 masked references and no raw UUID.
- Atomic persistence: reused `TelemetryJournal` atomic temp-rename append; `test_s5_torn_final_line_never_a_record` appends a torn line and confirms `stored_records==1`, `skipped_lines==1` (counted, never guessed into a record). `_store` rolls back `self._sequence` on append failure (`test_s10_failed_append_leaves_event_republishable`).
- Restart-safe replay: `replay_store`/`DurableEventBus` warm-start rebuilds dedup set + sequence + registry by pure reading. `test_s6_restart_rebuilds_state_without_double_count` confirms a simulated restart reproduces records, re-delivered event is a no-op (`duplicates_ignored==1`), and `bus_sequence` continues at `last_sequence+1`; `test_s6_replay_is_pure_reading` confirms store size is unchanged after repeated replays (no effect re-emission).
- Unknown-event handling: `publish` records unknown names with `known:false`, never dropped/crashed; `test_s7_unknown_event_recorded_honestly` confirms.
- Version-drift handling: `tools/agent_supervisor/event_drift.py` `catalog_drift` + schema-checked `load_catalog_fixture`; `test_s8_recorded_drift_matches_computed_drift`, `test_s8_drift_computation_surfaces_differences`, `test_s8_broken_fixture_refused` (empty/missing fixture → `CatalogFixtureError`) all pass; `test_s8_live_version_matches_catalog_fixture` is the live RED-on-drift tooth (skips cleanly, `claude` absent on this runner).

---

## Selective-citation cross-check — CLEAN

Read `project-control/directives/index.json` (28 active directives). Scanned every directive's `requirements.json` for path applicability intersecting the task's `allowed_paths` (`tools/agent_supervisor`, `.claude/hooks`, `tools/test_agent_supervisor_event_bus.py`, `project-control/reports/M0-T105-event-integration.md`). D-004 (R746/R751/R754…) and D-007 (R597/R603/R615…) do carry path scopes on `tools/agent_supervisor/` and `.claude/hooks/`, **but each also carries a non-empty `task_ids` dimension that excludes M0-T105** (e.g. `M0-T034`, `D-004-MODELGOV`, `D-007-BUILD`, `M0-T036`). Under the conjunction semantics in `DirectiveRegistry._applicability_matches` (line 544: "for every NON-EMPTY dimension the task must match"; line 558: `if tids and task.get("task_id") not in tids: return False`), those requirements are **not applicable** to M0-T105. The authoritative `evaluate_task_refs(M0-T105)` run confirms `missing_ids=[]` and `unresolved=[]` — no un-cited active directive requirement is made applicable by these paths. Mechanical enforcement at accept will not fire.

## Advisory (non-blocking, no verdict impact)

- The `source_ref` fragment anchors on R154/R155/R173 (`...#native-capabilities-3-passive-observation`, `...#native-capabilities-4-hooks`, `...#implementation-campaign-unit-d`) are slugified pointers that do not literally appear as HTML anchors in `source-003-amendment.md`; the corresponding **section content** is present and faithful (`source-003-amendment.md:140` "3. Structured passive observation", `:150` the R154 prohibitions verbatim, `:152` "4. Hooks as the event bus", `:304`/`:307` "D. Native event integration" / "Stream-JSON subagent events", `:375` "No token quotas exposed in worker assignments"). This is a cosmetic provenance-anchor style, not a missing/weakened/invented requirement — obligations map 1:1 to the requirement texts. No action required.

---

## Recorded rows (for verbatim transcription into verification.json)

- **D-024-R154 — PASS.** Evidence bullets: (1) `tools/agent_supervisor/event_stream.py` is passive parse-to-`TelemetryRecord` only — no model message, prompt composition, or sidecar write in the full 234-line module. (2) `test_s3_statusline_sidecar_stays_primary` passes: `"TelemetrySidecar" not in source` and ingestion creates only `hook_events.jsonl`. (3) R042 labels verified in `_step_measurements`/`_result_measurements` (`provider-exact`/`sdk-cumulative`, absent→`Measurement.unknown`); `test_s3_usage_carries_source_confidence_labels` passes. (4) R043 caveat coded in `_result_measurements.caveat` and asserted (`"R043" in final.detail`). (5) forwarded text stored as `text_chars`+`text_sha256` only; `test_s3_forwarded_text_is_reference_never_content` passes. (6) 38/38 event-bus tests pass at frozen `bfdf4ef`.
- **D-024-R155 — PASS.** (1) `hook_event_payloads_v1.json` fixtures exactly the 17 required event types; `test_s1_every_required_event_ingests_one_record` passes. (2) `hook_event_catalog_2_1_247.json` = 31 events, official-docs, drift NONE; `test_s8_recorded_drift_matches_computed_drift` passes. (3) live C1 fixture 9 records/7 event types, all UUID-masked; `test_c1_live_fixture_masked_and_replayable` passes. (4) recorder exits 0 + stdout-silent + fail-closed; `test_s9_*` pass. (5) command hook not HTTP + no self-registration; `test_s11_recorder_is_command_hook_only` passes and `grep -c supervisor_event_recorder .claude/settings.json == 0`, settings.json untouched 44a4c6c..HEAD. (6) no committed tokens / masked fixtures; `test_s11_recorder_embeds_no_tokens` + `test_s11_fixtures_are_masked` pass.
- **D-024-R173 — PASS.** (1) hook records + stream events ingested (`test_s1_*`, `test_s3_stream_events_become_typed_records`). (2) dedup via `idempotency_key`+bounded `_seen` (`test_s2_*`, `test_s3_stream_key_content_digest_fallback`). (3) redaction via reused journal + recursive `_mask_uuids` (`test_s4_durable_record_sanitized`, `test_s4_nested_uuid_masked_at_any_depth`). (4) atomic persistence + torn-line skip counted (`test_s5_torn_final_line_never_a_record`). (5) restart-safe replay, no double-count, pure reading (`test_s6_restart_rebuilds_state_without_double_count`, `test_s6_replay_is_pure_reading`). (6) unknown-event (`test_s7`) + version-drift (`event_drift.py`, `test_s8_*`) handled. All in the 38/38 pass at frozen identity.

**Prohibited-action check:** I performed no writes — no `git`/`gh`/`project_control.py`/edits. Nothing was merged, accepted, dispatched, or installed by this verification.

**Relevant absolute paths:** `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\event_bus.py`, `event_stream.py`, `event_drift.py`; `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\.claude\hooks\supervisor_event_recorder.py`; `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\test_agent_supervisor_event_bus.py`; fixtures under `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\fixtures\`; `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\directives\D-024-fable-codex-loop\requirements.json` and `source-003-amendment.md`; `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\directive_registry.py`.
