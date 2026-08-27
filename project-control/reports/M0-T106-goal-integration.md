# M0-T106 — Unit E: bounded /goal integration (D-024 Amendment 3; R152/R162/R174)

Producer: fable-orchestrator-session (orchestrator). Supervisor-freeze qualifying evidence:
**D-024-R152 + D-024-R174** (packet; `.claude/rules/supervisor-freeze.md` §2 D-024 recognition).
Status: IN PROGRESS — scenario pack recorded before implementation (task routine).

## 0. Reuse boundary (what already exists vs. what unit E adds)

Accepted and REUSED (never duplicated): `subagent_contracts.py` (M0-T090) — `WorkerAssignment`,
`assert_worker_text_clean` (the R045 fail-closed quota/countdown/conserve pattern classes),
`SupervisionEnvelope`; `telemetry_records.py` (`TelemetryRecord`/`Measurement`, R042 labels);
`telemetry_journal.py` (sanitize-first atomic bounded journal); unit-D `event_bus.py`
(dedup + replay durable store) for check-in/verdict observation persistence; the official `/goal`
docs snapshot `project-control/reports/M0-T102-docs-snapshot/goal.md` (R147, official-docs
confidence, fetched 2026-08-26).

Unit E ADDS (the new bounded seam):
1. **Goal condition contract** — compose ONE bounded, measurable completion condition from a task
   packet (one cohesive assignment; never one goal for the campaign): one end state + a stated
   check + constraints + an explicit turn-bound clause; ≤4,000 chars; R045 enforced fail-closed
   on the full condition text via the REUSED validator.
2. **Verdict/outcome classification** — evaluator verdicts (not-yet-met / met / impossible) and
   goal lifecycle outcomes: the four documented unrecoverable clearing classes (auth failure with
   the host-managed-credentials nuance, credit exhaustion, context overflow that auto-compaction
   couldn't clear, model unavailable), transient-error-stays-active, no-progress-paused (goal
   STAYS SET), cleared-by-user, resume-with-counter-reset — classified from documented shapes,
   honest UNKNOWN otherwise.
3. **Check-in schedule + ingestion** — deterministic schedule math for background-work check-ins
   (default 30-min first interval, doubling backoff capped at 4×, `CLAUDE_CODE_GOAL_CHECKIN_MINUTES`
   scaling, 0 = off; idle check-ins capped at 3 per goal between prompts) with version gates
   (≥2.1.234 / ≥2.1.236 / ≥2.1.246); check-in and verdict observations ingest into the durable
   journal via the REUSED unit-D bus, outside Fable context (R154 carried).
4. **Context-pressure policy** — `/autocompact` is an EMERGENCY buffer only, never a seam
   substitute: a context-overflow clearing classifies as a turnover seam trigger.
5. **Docs drift tooth** — execution-time re-fetch of the official `/goal` page reconciled against
   the M0-T102 snapshot in a goal-semantics fixture (mirrors the unit-C/D drift-tooth model).

## 1. Acceptance-scenario pack (recorded pre-implementation)

| ID | Scenario (Given / When / Then) | Kind |
|---|---|---|
| S1 condition-composition | Given a task packet / WorkerAssignment, when a goal condition is composed, then it contains ONE measurable end state, a stated check, the constraints that matter, and an explicit turn-bound clause; is ≤4,000 chars; and binds exactly ONE task (a campaign-shaped ask is refused, typed). | deterministic |
| S2 no-token-pressure (R045) | Given a condition or goal prompt draft carrying quota/countdown/percentage/conserve-tokens language, when validated, then composition FAILS CLOSED via the reused `assert_worker_text_clean`; no worker-visible token pressure can reach a goal text. | deterministic |
| S3 verdict ingestion | Given evaluator verdicts (not-yet-met + reason, met, impossible + reason), when ingested, then each becomes a typed record (reason bounded/sanitized); an unrecognized verdict string is honest UNKNOWN, never guessed. | deterministic |
| S4 clearing classes | Given the four documented unrecoverable-error warning shapes, when classified, then each maps to its class (auth_failure incl. the host-managed-credentials stays-active nuance; credit_exhausted; context_overflow; model_unavailable); transient shapes (rate limit, overloaded) classify goal-still-active; unknown text → UNKNOWN. | deterministic |
| S5 no-progress | Given the documented stall (no tool use for several turns → loop stops, warning, control returns), when classified, then outcome is no_progress_paused with the GOAL STILL SET (never met/cleared), surfaced typed to the controller; nothing silently re-prompts a worker. | deterministic |
| S6 resume semantics | Given a resume of a session with an active goal, then the condition carries over while turn count, timer, and spend baseline RESET; an achieved or cleared goal is NOT restored; the ≥2.1.239 all-routes gate is encoded (below it, the picker route is honest UNKNOWN). | deterministic |
| S7 check-in schedule | Given the documented cadence, when due times are computed, then: first check-in at 30 min (or the env-scaled value), doubling backoff capped at 4× the first interval, env=0 disables, idle check-ins cap at 3 per goal between prompts (≥2.1.246); version gates ≥2.1.234/≥2.1.236 yield UNKNOWN-below-version, never invented behavior. | deterministic |
| S8 check-in ingestion | Given a background-work check-in observation, when ingested, then it lands in the durable journal via the REUSED unit-D bus (dedup-keyed, sanitized, outside Fable context — R154); a duplicate delivery is a counted no-op. | deterministic |
| S9 goal-status telemetry | Given a `/goal` status snapshot (condition, duration, turns evaluated, token spend, last reason), when ingested, then it becomes a TelemetryRecord whose numbers carry R042 source/confidence labels (spend labeled, absent → unknown never zero). | deterministic |
| S10 autocompact policy | Given a context-overflow clearing event, when policy evaluates it, then it is a TURNOVER SEAM trigger (emergency buffer consumed ≠ seam); the policy never treats auto-compaction as a substitute for safe-seam succession. | deterministic |
| S11 docs drift | Given the execution-time re-fetch of code.claude.com/docs/en/goal vs the M0-T102 snapshot, when compared, then differences are surfaced and reconciled in the committed goal-semantics fixture (official-docs confidence); the deterministic tooth pins fixture↔code reconciliation. | fixture + fetch-at-build |
| C1 live goal canary (OWNER-GATED) | Run one real low-risk bounded `/goal` on 2.1.247 via an owner-approved exact command (R192/R197 pattern): met-path verdict + (if cheap) one background check-in captured as masked fixtures, proving the contract end-to-end. | live canary (owner exact-command approval required) |

## 2. Owner-gated item (flagged, not blocking the deterministic core)

Like the unit-C/D canaries, the LIVE goal run needs an owner-approved exact launch command
(R192/R197). The deterministic core (S1–S11) is built and verified without it; C1 strengthens
evidence (measured-live verdict/check-in shapes) and upgrades the semantics fixture, exactly as
the unit-D C1 did for hook payloads.

## 3. Evidence (deterministic core S1–S11)

Deliverables (new files + ONE additive method on the just-accepted unit-D bus; no other accepted
file modified; `.claude/hooks` is forbidden to this task and untouched):

| File | Lines | Role |
|---|---|---|
| `tools/agent_supervisor/goal_contract.py` | 153 | bounded condition contract: one-task binding, end state + stated check + constraints + explicit turn bound, ≤4,000 chars, campaign-scale tripwires, R045 via the REUSED `assert_worker_text_clean`; shared version helpers + documented version-gate constants |
| `tools/agent_supervisor/goal_outcomes.py` | 240 | verdict normalization (3 documented verdicts + honest unknown); clearing classification (documented warning frame → four unrecoverable classes incl. the host-managed-credentials stays-active nuance; transient-stays-active; user-clear; no-goal; unknown); STRUCTURAL no-progress pause (goal stays set — the stall warning text is undocumented, so nothing parses it); resume semantics (all-routes ≥2.1.239, counter reset, achieved/cleared never restored); `/autocompact` policy (context-overflow clearing = turnover seam trigger); `/goal` status ingestion with R042 labels (spend detail: baseline resets on resume — never whole-session) |
| `tools/agent_supervisor/goal_checkins.py` | 170 | check-in schedule math (30-min default first interval, doubling capped at 4×, `CLAUDE_CODE_GOAL_CHECKIN_MINUTES` scaling, 0=off, malformed env fails visible); version gates (≥2.1.234 / ≥2.1.236 / cap 3 ≥2.1.246, unknown-version honest); check-in ingestion → `goal_checkin` records persisted via the REUSED unit-D bus |
| `tools/agent_supervisor/event_bus.py` (+19) | 311 | ADDITIVE `publish_typed(record)`: dedup-keyed publish for typed records from other modules — same store/dedup/replay semantics, no second persistence path; existing publish paths byte-unchanged |
| `fixtures/goal_semantics_2_1_247.json` | — | goal contract facts @ official-docs confidence (build-time re-fetch of code.claude.com/docs/en/goal, 2026-08-27) reconciled against the accepted M0-T102 snapshot: **drift = NONE**; the S11 tooth pins fixture↔code on every constant (verdicts, classes, warning frame, cadence, gates, caps, ceiling) |
| `tools/test_agent_supervisor_goal_integration.py` | 346 | 31 tests mapping S1–S11 (IDs in test names) |

Self-check results (producer, local 3.11.9; installed claude 2.1.247):

- **31/31** goal pack + **38/38** unit-D event-bus pack (69 combined — the `publish_typed` addition
  regresses nothing).
- **Mutation self-check 9/9 KILLED**: turn-bound-guard-removed, foreign-task-guard-removed,
  campaign-guard-removed, R045-validator-removed, host-managed-nuance-removed,
  transient-check-removed, backoff-cap-removed, seam-trigger-any-unrecoverable,
  publish-typed-dedup-removed.
- **ruff 0.13.0 clean** on all five changed Python files; `modularity_check --check` 0 failures
  (largest new file 240 lines).
- **Guard packs** `ALL CHECKS PASSED` ×2; `.claude/hooks/` diff empty (forbidden path respected).
- **No-leak scan** over every new path: CLEAN except the precedented benign class (the leak-needle
  assertion string inside the test pack itself).
- **S11 drift check executed at build time**: live page vs M0-T102 snapshot — no substantive drift;
  recorded in the fixture with the reconciliation note.
- **Freeze-suite evidence**: targeted regression slice **278 passed / 0 failed** + whole-tree
  collection **2,720 tests, zero errors**; the local full-suite runs were externally stopped
  twice mid-run (zero failures at the stops) and were not relaunched against the operator
  signal — full-suite proof rests on CI at the pushed head plus reviewer re-runs (disclosed in
  the G2 self-check; M0-T105 G4-accepted reasoning for a new-files-plus-additive change).
- Context discipline (D-031): occupancy measured at the claim seam ≈45%; measured again at submit
  (recorded in the progress log); handoff due at ~750k per D-031-R002.
