# M0-T105 G3 code review — round 1 (VERBATIM reviewer return; transport entity-decoding only)

Saved by the orchestrator per the report-preservation rule. Reviewer: code-reviewer (independent,
read-only, dispatched 2026-08-27). Verdict returned: **PASS** (no blocking corrections; 5 advisory
findings, all non-blocking).

---

# Gate Report

- **Gate ID:** G3 (independent code review)
- **Task ID:** M0-T105 (D-024 Amendment 3 unit D: native event integration)
- **Reviewer:** code-reviewer (independent; read-only)
- **Producer:** fable-orchestrator-session
- **Result:** **PASS** (no blocking corrections; 5 advisory findings, all non-blocking)
- **Clean environment/worktree used:** Reviewed at frozen deliverable commit `50abb346fc8637a374b1e5bae056d19d2792a827`; live HEAD `70b38f87d5ded0988c84022b463d98ca35db1471` (the two commits after the deliverable are control-plane only: `37a1bd3` submit, `70b38f8` G2-self-check record — git-verified, no source change). Content manifest `5f32cf9…812b17`. Working tree clean (`git status --porcelain` empty).

## Acceptance criteria reviewed

Scenario pack S1–S11 (`M0-T105-event-integration.md` §1) plus the packet objective (durable hook records, stream-JSON subagent ingestion, dedup, redaction, atomic persistence, restart-safe replay, unknown-event/version-drift, fail-closed recorder, no `.claude/settings.json` registration). Reviewed all NEW files: `event_bus.py`, `event_stream.py`, `event_drift.py`, `.claude/hooks/supervisor_event_recorder.py`, three fixtures, and the 32-test pack, against the four reused telemetry modules for boundary discipline.

## Directive/requirement verification

Applicable set resolved for this packet's `allowed_paths` = **D-024-R154, D-024-R155, D-024-R173** (matches the packet, report, and evidence-map). Each re-derived from source at the frozen identity; the independent `directive-compliance-verifier` records the authoritative verdict in `verification.json` — the below is the code dimension.

| Requirement ID | Reviewed SHA / content identity | Verdict | Reproduced evidence |
|---|---|---|---|
| D-024-R154 (consume structured feeds outside Fable context; statusLine sidecar stays primary) | 50abb34 / 5f32cf9…812b17 | PASS | `event_stream.py` is passive parse only — no sidecar write, no model message, no prompt composition; `test_s3_statusline_sidecar_stays_primary` proves the module has no `TelemetrySidecar` surface and ingestion creates only the journal file. Subagent attribution via `parent_tool_use_id`/`agent_id` → no transcript polling. |
| D-024-R155 (hooks fast, deterministic, sanitized, bounded, fail-closed; external state only, never block/inject/message) | 50abb34 / 5f32cf9…812b17 | PASS | Recorder always exits 0, stdout-silent, bounded stdin (`MAX_STDIN_BYTES`), no HTTP/tokens; `_store` remembers dedup key only after successful append (fail-closed durability). Tests S9/S11 bite (subprocess fail-closed on malformed JSON / missing event name / unwritable store; source scan rejects `urllib/requests/socket/subprocess`, `permissionDecision`, `additionalContext`, `settings.json`). No `.claude/settings.json` registration present (git-verified). |
| D-024-R173 (unknown-event / version-drift handling) | 50abb34 / 5f32cf9…812b17 | PASS | Unknown hook names recorded `known:false` (S7); unknown stream `type` recorded `known_type:false` (S3); `event_drift.catalog_drift` + schema-checked fixture loader + recorded-vs-computed drift reconciliation + live version tooth (S8). 2.1.247 catalog = 31 events, drift vs 2.1.220 = NONE, verified against `telemetry_hooks.KNOWN_HOOK_EVENTS`. |

## Steps independently executed

- `python -m pytest tools/test_agent_supervisor_event_bus.py -q` → **32 passed in 1.41s** (reproduced the producer's core claim).
- `python -m pytest tools/ --collect-only -q` → **2803 tests collected in 18.67s**, zero collection/import errors (the new modules import cleanly across the whole tree).
- `python -m pytest <telemetry*> test_agent_supervisor_native_adapter.py -q` → **111 passed** (reuse boundary intact; accepted M0-T104 adapter still green).
- `python -m ruff check` on all 5 new Python files → **All checks passed!** (ruff 0.13.0, the CI version).
- `python tools/modularity_check.py --check` → **0 failures, 5 warnings**, all in files this task does not touch (`surveyReview/types.ts`, `mappluto_geometry_arcgis.py`, `cli.py`, `policy.py`, `context_benchmark.py`); no new file flagged.
- Git byte-identity checks: `native_runtime.py`, `runtime_backend.py`, `readonly_agent_guard.py` — **byte-identical** to the M0-T104-accepted commit `44a4c6c` and **never touched** in `44a4c6c..HEAD`.
- `git show --stat 50abb34` — deliverable is all-NEW source/fixtures/tests + control-plane (`state.json`, `tasks/M0-T105.json` written by the CLI, not producer edits); no accepted file modified.
- `git check-ignore .claude/telemetry/hook_events.jsonl` → gitignored at `.gitignore:89` (recorder default store cannot pollute the tracked tree).

## Expected versus actual

| Claim | Expected | Actual |
|---|---|---|
| Event-bus pack | 32 pass | 32 passed ✓ |
| Report line counts (`event_bus 284 / event_stream 234 / event_drift 106 / recorder 77 / test 463`) | match git | match `git show --stat` exactly ✓ (no M0-T104-style count typo) |
| Catalog = 31 events, drift NONE | identical to KNOWN_HOOK_EVENTS | verified by count and by `test_s8_recorded_drift_matches_computed_drift` ✓ |
| Adapter/guard untouched | byte-identical | confirmed ✓ |
| ruff / modularity clean | clean | clean ✓ |

## Evidence paths

- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\event_bus.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\event_stream.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\event_drift.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\.claude\hooks\supervisor_event_recorder.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\fixtures\hook_event_catalog_2_1_247.json`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\fixtures\hook_event_payloads_v1.json`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\fixtures\stream_json_subagent_events_v1.json`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\test_agent_supervisor_event_bus.py`

## Human-style walkthrough findings

Not a UI task; N/A. Behavioral walkthrough of the event path (publish → mask → sanitize-first journal append → replay rebuild) traced by reading and confirmed by the biting tests below.

## Regression/security/provenance findings

**Correctness — verified sound (read + test-confirmed):**
- **Dedup key**: `idempotency_key` = event name + selected identity fields + full-payload content SHA-256. Two identical deliveries share a key (collapse); any payload difference yields a distinct key. No false-dedup path exists (collision requires byte-identical payload + same event name = a true duplicate). Key is computed from the RAW pre-mask payload and stored on the record, so dedup survives restart and the UUID-masking of `session_id`/`task_id` does not perturb it. `test_s2_*` bite.
- **Fail-closed durability**: `_store` appends first; on any append exception it rolls back `self._sequence` and re-raises WITHOUT remembering the key — the event stays unrecorded and re-publishable. `test_s10_failed_append_leaves_event_republishable` monkeypatches `journal.append` to raise and proves re-publish succeeds at `bus_sequence == 1`. This is the key fail-closed invariant and it genuinely bites.
- **Sequence monotonicity across restart**: `replay_store` sets `last_sequence = max(bus_sequence)`; the newest journal generation always holds the highest sequence, so it is recovered even when the active-only window is read. `test_s6_*` proves continuation to `last_sequence + 1` after a simulated restart.
- **Replay purity**: reading only; no re-append, no effect re-emission. `test_s6_replay_is_pure_reading` asserts store size unchanged across repeated replays.
- **Registry rebuild equivalence**: masking is deterministic, so open/close correlation keys are stable; live-observe and replay-observe both consume the masked stored record. `test_s6` asserts `registry.active()` equality across restart.
- **Redaction depth**: `ingest_hook_event` uses a scalar allowlist (`_EVENT_ATTRIBUTES`), so `prompt`, `api_key`, `transcript_path` never even enter the record; `cwd` survives and is `[HOME]`-masked; bare-UUID identity fields are digest-masked by the bus; then the reused sanitize-first journal runs. `test_s4_*` proves no `realname`/prompt/secret/raw-UUID survives. Strong defense-in-depth.

**Reuse discipline — clean**: `event_bus` imports `SubagentRegistry`/`ingest_hook_event`, `TelemetryJournal`, `TelemetryRecord`; `event_stream` imports `Measurement`/`TelemetryRecord`/`to_utc_iso`; `event_drift` imports `KNOWN_HOOK_EVENTS`. No re-implementation of sanitization, atomic write, or ingest. `claude_runner.ClaudeStreamParser` (existing) verifies model identity on a supervised `claude -p` stream for a different purpose; `event_stream` adds typed-record ingestion for the durable bus — genuinely additive, not a duplicate of the buffering parser.

**Security**: recorder is command-only, stdin payload, no network imports, no embedded tokens, gitignored default store, unregistered. `readonly_agent_guard.py` byte-untouched. No prompt/transcript content persisted (s5.3). No provenance loss — every fixture payload/usage number carries an honest confidence label; unknown remains `unknown`, never zero.

## Defects

None (no HIGH/MEDIUM). Advisory-only findings, all non-blocking:

1. **A1 — LOW/ADVISORY (modularity):** `_event_usage()` in `event_stream.py` (lines 129–138) is near-identical to `_event_usage()` in `claude_runner.py` (lines 638–649), and `MAX_LINE_BYTES = 4_194_304` is duplicated as a literal in both. Small (~8 lines) and the two consumers differ, so extraction now would couple modules for marginal gain — but flag as an extraction candidate if a third stream consumer appears.
2. **A2 — LOW/ADVISORY (concurrency/ordering):** `bus_sequence` is not collision-free under concurrent cross-process recorders (each recorder is a fresh process that reads the store and computes `sequence+1` independently). Arrival order is still preserved by file-append order, and `ReplayResult.store_duplicates` surfaces same-key races honestly rather than silently collapsing them. No live impact (recorder unregistered; supervisor shadow-only). The bus docstring's ordering claim is accurate for single-writer/restart; consider a one-line note that total ordering is not guaranteed under concurrent multi-process writers.
3. **A3 — LOW/ADVISORY (hidden default / dedup window):** the recorder passes `warm_rotated=False` with no INLINE rationale (the inline comment only justifies `fsync=False`; the `warm_rotated` rationale lives only in the G2 self-check §3). This narrows dedup to the ACTIVE journal generation, so a duplicate delivered after a `>max_bytes` rotation boundary would be re-recorded. The over-record direction is safe (never data loss / never false-dedup), and the bus's "recorded exactly once" is anyway scoped to the bounded `max_seen_keys`/retained-generations window. Recommend adding a one-line inline comment documenting the narrowed-window tradeoff.
4. **A4 — ADVISORY (defense-in-depth):** bus UUID masking (`_mask_if_uuid`) covers `session_id`/`task_id` and top-level attribute VALUES only; a bare UUID nested inside a sub-dict attribute would not be masked (and `sanitize_structure` has no UUID rule). Not exploitable today — `ingest_hook_event`/`ingest_stream_event` produce only flat scalar attributes — but a future ingest path adding nested attributes would surface this gap.
5. **A5 — LOW/ADVISORY (test coverage):** two simple branches lack a direct test — the recorder oversized-stdin path (`len(raw) > MAX_STDIN_BYTES → return 0`) and the `stream_idempotency_key` content-digest fallback for events with no `uuid`/`message.id`. Logic is straightforward; add cheap coverage when convenient.

## Required rework

None. Advisories A1–A5 are documentation/coverage/hardening suggestions and are NOT blocking for acceptance.

## Reviewer conclusion

**PASS.** The unit-D deliverable is correct for its documented semantics, well and honestly tested (32 biting scenario tests reproduced green; whole `tools/` tree collects with zero import errors; telemetry + native-adapter suites green at 111), reuses the accepted telemetry subsystem by import without re-implementation, and modifies no accepted file — `native_runtime.py`, `runtime_backend.py`, and `readonly_agent_guard.py` are git-verified byte-identical. Redaction/fail-closed/dedup/replay/ordering invariants hold and are exercised by tests that genuinely bite. Directive requirements R154/R155/R173 are satisfied at the code level (authoritative verdict to be recorded by the independent `directive-compliance-verifier`). ruff and modularity are clean; report line counts match git (no M0-T104-style count typo); the C1 live canary is honestly flagged as owner-gated (R192/R197) and does not gate the deterministic core. No blocking corrections; the five advisories are non-blocking. The orchestrator should record G3 = PASS.
