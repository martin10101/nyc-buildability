# M0-T105 — Unit D: native event integration (D-024 Amendment 3; R154/R155/R173)

Producer: fable-orchestrator-session (orchestrator). Supervisor-freeze qualifying evidence:
**D-024-R155 + D-024-R173** (packet; `.claude/rules/supervisor-freeze.md` §2 D-024 recognition).
Status: IN PROGRESS — scenario pack recorded before implementation (task routine).

## 0. Reuse boundary (what already exists vs. what unit D adds)

Accepted and REUSED (not duplicated): `telemetry_hooks.py` (M0-T089) — `KNOWN_HOOK_EVENTS`
(31-event catalog documented at 2.1.220), `ingest_hook_event()` (one typed `TelemetryRecord` per
hook, identity-only, `known: false` for unknown events), `SubagentRegistry` (bounded open/close
identity tracker); `telemetry_journal.py` (`TelemetrySidecar`/`TelemetryJournal`, atomic writes);
`telemetry_redaction.py` (`sanitize_structure`, `redact_user_paths`, `withhold_prompt`);
`telemetry_records.py` (`TelemetryRecord`); `telemetry_subagent.py` (subagent status ingestion);
the accepted live statusLine/subagentStatusLine fixtures (2.1.247, R162 discharge).

Unit D ADDS (the new bounded seam):
1. **Durable event bus** — event records with **deduplication** (idempotency key so a replayed or
   double-fired hook is recorded once) + **restart-safe replay** (a supervisor restart rebuilds
   state from the durable store without re-emitting effects or double-counting) + **ordering**.
2. **stream-JSON subagent-event ingestion** — parse `--output-format stream-json` /
   `--forward-subagent-text` events (distinct from `agents --json` status polling, which is unit C)
   into the same typed records, dedup-keyed, outside Fable context (R154).
3. **2.1.247 event-set drift** — probe/fixture the installed event catalog vs the 2.1.220-documented
   `KNOWN_HOOK_EVENTS`; unknown/new events handled honestly (recorded, never guessed, never crash).
4. **Hook recorder scripts** under `.claude/hooks` — thin, fast, deterministic, sanitized, bounded,
   fail-closed recorders that append a hook payload to the durable store. NO `.claude/settings.json`
   registration here (separate reviewed change; settings.json is forbidden_paths). MUST NOT touch
   `readonly_agent_guard.py` (M0-T108/T109 scope).

## 1. Acceptance-scenario pack (recorded pre-implementation)

| ID | Scenario (Given / When / Then) | Kind |
|---|---|---|
| S1 firing-order | Given a sequence of lifecycle hook payloads (SessionStart → SubagentStart → PostToolBatch → SubagentStop → SessionEnd), when ingested, then durable records preserve arrival order and each is one typed record. | deterministic |
| S2 dedup | Given the SAME hook event delivered twice (same idempotency key: event+session+task+sequence/content hash), when ingested, then exactly ONE durable record exists; the second is a no-op. | deterministic |
| S3 stream-JSON ingestion | Given a captured `--output-format stream-json` subagent event stream, when ingested, then each event becomes a typed record consumed OUTSIDE Fable context (R154); usage numbers carry source+confidence labels (R042); malformed lines raise typed errors and the statusLine sidecar stays primary (R154). | deterministic + fixture |
| S4 redaction | Given a hook/stream payload carrying a home path, session UUID, prompt text, or secret-shaped token, when recorded, then the durable record is sanitized (`sanitize_structure`): paths `[HOME]`-masked, prompts withheld, no secret/token/raw-UUID survives. | deterministic |
| S5 atomic persistence | Given a write interrupted mid-record, when the store is re-read, then no partial/corrupt record is visible (atomic temp-rename; reuse journal atomic write). | deterministic |
| S6 restart-safe replay | Given a durable event store and a supervisor restart, when state is rebuilt by replay, then the reconstructed subagent/session state equals the pre-restart state, no effect is re-emitted, and no dedup-keyed event is double-counted. | deterministic |
| S7 unknown-event | Given an event name NOT in the installed catalog, when ingested, then it is recorded honestly (`known: false`) — never dropped, never guessed, never crashes. | deterministic |
| S8 version-drift | Given the installed 2.1.247 event catalog differs from the committed 2.1.220 fixture, when the drift tooth runs, then the difference is surfaced (RED-on-drift locally; clean skip when claude absent) and reconciled — mirrors the M0-T104 capability drift-tooth model. | fixture + live (skips when absent) |
| S9 blocking semantics | Given a recorder hook, when it runs, then it writes EXTERNAL state only, never blocks/delays the hook, never injects context, never messages a worker (R155/s5.1-item-5); a recorder failure fails closed (records nothing) without breaking the session. | deterministic |
| S10 bounded store | Given an unattended controller and unbounded event volume, when events accumulate, then the store/registry is bounded (oldest-closed-first eviction; size cap) — no unbounded growth. | deterministic |
| S11 hook-script security | Given the recorder hook scripts, then they are command hooks (not HTTP), read the payload from stdin, write only under the bounded store path, embed no tokens, and are read-only w.r.t. the repo. | deterministic + inspection |
| C1 live event canary (OWNER-GATED) | Fire a real bounded set of lifecycle hooks on 2.1.247 via an owner-approved exact-command canary (R192/R197 pattern, as the R162 discharge did), capture masked per-event fixtures, prove the recorder path end-to-end. | live canary (owner exact-command approval required) |

## 2. Owner-gated item (flagged, not blocking the deterministic core)

Like the M0-T103 R162 statusLine discharge, capturing a LIVE hook-event stream on the installed
binary requires an owner-approved exact launch command (D-024-R192/R197). The deterministic core
(S1–S11: event bus, dedup, replay, redaction, drift, hook scripts, all tests) is built and verified
WITHOUT the owner — exactly as the deterministic `capability_probe` preceded its live canaries. C1
(live per-event fixture capture) is the one step that queues for an owner exact-command approval; it
strengthens the evidence but does not gate the deterministic seam. This is surfaced per the
escalation boundary (a live-canary launch is owner-exact-command, not routine dispatch).

## 2a. C1 canary — PREPARED, validated deterministically, awaiting owner exact-command approval

Mirrors the accepted R162 discharge procedure verbatim (isolated scratch project outside the
repo, `--strict-mcp-config`, `--tools Agent`, no permission flags, zero-quote prompt,
explicitly-controlled child env per the M0-T104 child-env lesson). The scratch project's OWN
`.claude/settings.json` registers command hooks for all 17 pack events, each wiring to
`.claude/hooks/supervisor_event_recorder.py` with `NYCB_EVENT_STORE_PATH` pointed INTO the
scratch directory (repo untouched; recorder→store path already proven by S9 subprocess tests).
Cleanup = stop-if-lingering + `claude agents --json` zero-canary check + scratch delete; the
repo is unchanged by the launch, so rollback is deletion. Masked fixtures commit only after the
M0-T103-style final-bytes leak scan. The exact launch command is queued for the owner (R192/R197).

## 3. Evidence (deterministic core S1–S11)

Deliverables (all new; no accepted file modified — `readonly_agent_guard.py`, guard packs,
`native_runtime.py`/`runtime_backend.py` (R180 fallback boundary), and the telemetry modules are
untouched; reuse is by import only):

| File | Lines | Role |
|---|---|---|
| `tools/agent_supervisor/event_bus.py` | 284 | durable bus: dedup idempotency key, ordering (`bus_sequence`), restart-safe replay, raw-UUID digest masking; persists via the REUSED `TelemetryJournal` (sanitize-first/atomic/bounded/rotated) |
| `tools/agent_supervisor/event_stream.py` | 234 | stream-JSON subagent-event ingestion → typed records; `step_*` provider-exact, `final_request_*` sdk-cumulative with the R043 caveat; text as digest reference; typed `StreamEventError`; no sidecar surface (R154) |
| `tools/agent_supervisor/event_drift.py` | 106 | catalog drift: `catalog_drift()` + schema-checked fixture loader |
| `.claude/hooks/supervisor_event_recorder.py` | 77 | thin command-hook recorder: stdin→bus, fail-closed exit 0, stdout-silent, bounded, NOT registered (settings.json is a separate reviewed change) |
| `fixtures/hook_event_catalog_2_1_247.json` | — | 2.1.247 catalog @ official-docs confidence (code.claude.com/docs/en/hooks fetched 2026-08-27; same method as the 2.1.220 capture); recorded drift vs 2.1.220 = NONE (31 events identical) |
| `fixtures/hook_event_payloads_v1.json` | — | masked per-event payloads for all 17 pack events; UserPromptSubmit is measured-live (masked copy of the R162 capture); the rest documentation-confidence, honestly labelled per payload |
| `fixtures/stream_json_subagent_events_v1.json` | — | masked stream-json lines (session-evidence confidence; shapes mirror `claude_runner` measured handling) incl. dedup-duplicate, usage-absent, and unknown-type lines |
| `tools/test_agent_supervisor_event_bus.py` | 463 | 32 tests mapping S1–S11 (IDs in test names) |

Self-check results (producer, local 3.11.9):

- **32/32** `tools/test_agent_supervisor_event_bus.py` (S1–S11 all covered; the one live row —
  the S8 version drift tooth — passes against the installed 2.1.247 and skips when claude absent).
- **Mutation self-check 9/9 KILLED**: dedup-check-removed, uuid-mask-identity,
  remember-before-append, sequence-rollback-removed, step-label-swap, text-stored-verbatim,
  drift-sets-swapped, recorder-prints-to-stdout, replay-seen-ignored.
- **ruff 0.13.0 clean** on every new file; whole-tree ruff shows only pre-existing findings in
  files this task does not touch (`project-control/reports/M0-T054-protected-config/doctor_proof.py`,
  `tools/agent_supervisor/cli.py` — pre-existing at bc77972).
- **modularity_check --check**: no new warnings (largest new file 284 lines, far under warn 600).
- **Supervisor freeze suite**: `python -m pytest tools/ -q --ignore=tools/test_directive_compliance.py`
  at the frozen deliverable — **2,680 passed, 3 skipped, 0 failed** (598.8s); the excluded pack's
  subject ran standalone (`validate_directive_compliance.py --check` EXIT=0; CI runs the pack).
- Drift-tooth honesty note: the S8 live tooth compares `claude --version` to the fixture's
  recorded version (the M0-T104 model) — catalog content itself is documentation-confidence until
  the C1 measured-live upgrade; the deterministic S8 rows pin fixture↔code reconciliation.
