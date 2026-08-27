# M0-T106 G5 security review — round 1 (VERBATIM reviewer return; transport entity-decoding only)

Saved by the orchestrator per the report-preservation rule. Reviewer: security-reviewer
(independent, read-only, dispatched 2026-08-27). Verdict returned: **PASS** (no blocking
corrections; 3 non-blocking advisories).

---

# G5 Security Gate Report — M0-T106 (D-024 Amendment 3 unit E: bounded /goal integration)

**Gate:** G5 (independent security review)
**Reviewer:** security-reviewer (read-only)
**Verdict: PASS** (no blocking corrections; 3 non-blocking advisories)

## Frozen identity verified
- Live HEAD: `ff2e2a808ed04fa94e0fb58caae88e0a0c33d8a3`
- Deliverable commit: `c3f376882690a0460222f26612e03fcbf02608bd` (confirmed via `git log --oneline -1`)
- Working-tree copies of all six subject files are **byte-identical** to the frozen commit (`git diff --quiet c3f3768 -- <file>` clean for each).
- Applicable directive requirements: D-024-R152, D-024-R162, D-024-R174 (carried: R045, R154).
- Repo is PUBLIC.

## Subject files reviewed at the frozen SHA
- NEW `tools/agent_supervisor/goal_contract.py` (153 lines)
- NEW `tools/agent_supervisor/goal_outcomes.py` (240)
- NEW `tools/agent_supervisor/goal_checkins.py` (170)
- NEW `tools/agent_supervisor/fixtures/goal_semantics_2_1_247.json` (78)
- NEW `tools/test_agent_supervisor_goal_integration.py` (346)
- MODIFIED `tools/agent_supervisor/event_bus.py` (+19, one additive `publish_typed`)

`git diff 8bc13fa..c3f3768 -- tools/agent_supervisor/event_bus.py` shows a **purely additive** `publish_typed` method inserted after `publish_stream_line`; every existing method body is byte-unchanged. Unit-D pack re-run confirms non-regression: **38/38 pass**.

## Reproduction commands run (all read-only)
```
git show c3f3768:<subject file>                     # read every subject file
git diff 8bc13fa..c3f3768 -- .../event_bus.py       # additive-only proof
git diff --name-only 8bc13fa..c3f3768 | grep .claude/settings/hooks  -> NONE
python -m pytest tools/test_agent_supervisor_goal_integration.py -q   -> 31 passed
python -m pytest tools/test_agent_supervisor_event_bus.py -q          -> 38 passed
python -m pytest tools/test_agent_supervisor_bounded_contracts.py \
                tools/test_agent_supervisor_subagent_telemetry.py \
                tools/test_agent_supervisor_telemetry_core.py -q      -> 151 passed
python - <probe>                                     # 5 live security probes (below)
```

## Findings by required security dimension

### 1. R045 worker-protection integrity — PASS
The only worker-facing string produced anywhere in the three modules is the `/goal` condition text. `GoalCondition.__post_init__` runs the reused `subagent_contracts.assert_worker_text_clean("goal_condition", self.text)` as the **final** validation on `self.text`, so it fires on **every** construction path:
- `compose_goal_condition(...)` builds `text` (end_state + stated_check + each constraint + explicit turn bound) then constructs `GoalCondition(text=text)`, so `__post_init__` validates the fully-composed text including constraints.
- Direct `GoalCondition(...)` construction validates the caller-supplied `text` identically (test `test_s1_direct_construction_cannot_drop_the_bound`).

Composition order cannot bypass the guard: the validator sees the concatenated final string, not the parts. **Live probe** — a quota phrase embedded inside a `constraint` (`"finish within 5000 tokens remaining"`) is caught: `ContractError: quota_language ... (D-024-R045)`. `goal_outcomes.py` and `goal_checkins.py` build **no** worker-facing text (they classify/ingest/schedule only). `assert_worker_text_clean` is reused verbatim and unchanged.

### 2. Prompt-injection posture — PASS
Classification is pure pattern-matching: `str.startswith`, `in`, and pre-compiled `re` searches. No `eval`/`exec`/`format`-into-command/`subprocess` anywhere (grep confirmed empty). Verdict/reason excerpts are bounded to **160 chars** (`excerpt = stripped[:160]`) at classification time. Everything persisted flows `publish_typed -> _store -> _mask_uuids -> TelemetryJournal.append -> _to_sanitized_dict -> sanitize_structure` (sanitize-first).

**Probe (the requested one):** a `/goal status` payload with `last_reason="failed: api_key=sk-ABCDEF... AKIAIOSFODNN7EXAMPLE"` and `condition=r"C:\Users\MLFLL\secrets\prod.env and /home/martin/id_rsa"` persisted via `ingest_goal_status -> publish_typed`. Durable-store bytes:
```
"condition": "look at [HOME]\\secrets\\prod.env and [HOME]/id_rsa",
"last_reason": "failed: [REDACTED:assigned_secret] and token [REDACTED:aws_access_key]"
```
On-disk leak checks: `sk-ABCDEF...` False, `AKIAIOSFODNN7EXAMPLE` False, `/home/martin` False, `MLFLL` False, `Users` False. Secrets and home paths are redacted before touching disk. `reason_excerpt` (GoalClearing) is never itself persisted by these modules; if a caller later journals it, the same sanitize pass applies.

### 3. publish_typed invariants on the accepted bus — PASS
`publish_typed` computes its own namespaced dedup key (`f"typed:{record_type}"` prefix, avoiding collision with hook/stream keys) then delegates to the shared `_store`, so it inherits every invariant:
- **UUID masking** — probe: raw `12345678-1234-1234-1234-1234567890ab` in a check-in `session_id` is absent on disk; `[SESSION sha256=...]` marker present.
- **Sequence rollback** — probe: a record exceeding `max_bytes=200` raises `TelemetryBoundsError`; `self._sequence` is restored (`== seq_before`) and the seen-set stays empty.
- **Remember-key-only-after-append** — `_store` calls `_remember(key)` only after a successful `journal.append`; the failed write above left the key un-remembered (re-publishable).

Typed records receive the **same** `_store` masking and the **same** journal sanitize pass as hook/stream records; the skipped `ingest_hook_event`/`ingest_stream_event` steps are typing/normalization only, not sanitization, so there is **no sanitization bypass**. `_store` overwrites `attributes["idempotency_key"]` and `["bus_sequence"]` with computed values, so a caller cannot poison dedup/ordering metadata. No new unbounded persisted surface — record size is capped by `TelemetryJournal` (`bound_text` 512 chars/string; whole-record `max_bytes`, else `TelemetryBoundsError`).

### 4. Denial/abuse — PASS (1 non-blocking advisory)
- Check-in math uses Python arbitrary-precision ints — no integer overflow. Probe: `env=10**9` yields offsets `(1000000000, 3000000000, 7000000000)` with no error.
- Malformed env fails visible (`GoalCheckinError`); `env=0` disables; negatives/floats rejected (test S7).
- `_count()` in `ingest_goal_status` rejects `bool`, non-numeric, and negatives → `Measurement.unknown` (test S9 covers `True, -3, "many"`), preventing type-confusion in stored numbers.
- Unbounded ingest strings are bounded by the journal on write (probe 1 / dimension 2).
- **ADV-2 (LOW, defense-in-depth):** `checkin_schedule(count=...)` is bounded below (`count >= 0`) but has no upper bound; `count=200000` builds a 200k-element tuple in 0.05s. Not attacker- or env-reachable — `count` is a controller-supplied parameter (default 6); the env var scales magnitude only, not list length. Recommend a documented sane cap for defense-in-depth. Non-blocking.

### 5. Leak analysis (PUBLIC repo) — PASS
Full-byte scan of the three production modules, `event_bus.py`, and the fixture found **no** usernames, absolute user paths, secrets, emails, or real UUIDs. The fixture (`goal_semantics_2_1_247.json`) contains only documented version constants and semantics text; `test_s11_fixture_valid_and_no_drift_recorded` asserts `"Users" not in whole and "MLFLL" not in whole` and passes. The only occurrences of the string `MLFLL` in the diff are in the **test file**, used as negative masking-assertion needles; that username is already pervasive across dozens of committed control-plane files (e.g. 21 hits in `docs/CONTROLLER_UPDATE_RUNBOOK.md`), so this introduces no new exposure.

### 6. Authority boundaries — PASS
- **No worker messaging / context injection / pings into Fable context** — grep for `__main__`, `argparse`, `subprocess`, `Popen`, `spawn`, `SendMessage`, `Agent(`, `Task(`, `inject` across all subject modules is empty (only hit is the event_bus docstring's *negative* clause "…nor messages a worker"). `goal_checkins` computes when the *native* runtime will check in (controller-side math) and ingests observed check-ins passively (R154 carried, satisfied).
- **No network imports / no new dependencies** — imports are stdlib (`dataclasses`, `re`, `hashlib`, `json`, `typing`) plus in-package modules only.
- **No settings.json / hooks changes** — `git diff --name-only 8bc13fa..c3f3768` touches no `.claude/settings.json`, `.claude/hooks`, or `.claude/ORCHESTRATION_POLICY.md` (all forbidden paths); confirmed empty.
- **C1 live goal canary not executed or enabled** — no entrypoint, no auto-run; the canary is documented as owner-gated (R192/R197) in the fixture/report and explicitly NOT exercised by the test pack (test module docstring).
- **Applicable-requirement security obligations** all met: R152 (one bounded task; campaign-scale + foreign-task + task-id-shape tripwires — probe/tests confirm refusal), R162 (`is_turnover_seam_trigger` encodes context-overflow = emergency-buffer turnover trigger; no statusLine/cache code altered), R174 (safe condition + no-progress structural handling + background check-ins + no worker token pressure). Full requirement-to-evidence verification remains the directive-compliance-verifier's `verification.json` pass (producer ≠ verifier).

## Non-blocking advisories (do NOT block acceptance)
- **ADV-1 (LOW / security-safe, functional):** the `goal_token_spend` measurement is **fully** redacted to `[REDACTED:sensitive_key]` on the durable store, because the key name's delimited `_token_` segment matches `SENSITIVE_KEY_PATTERN`. This is over-redaction (leak-safe direction — token-spend never leaks), but it renders R042 token-spend telemetry unreadable from the journal. This is a G3/G4/functional concern, **not** a G5 security defect. Flag for the functional gates; consider renaming the measurement key (e.g. `goal_spend_tokens_evaluated` avoided) if the controller needs to read it back.
- **ADV-2 (LOW):** unbounded `count` in `checkin_schedule` — see dimension 4.
- **ADV-3 (INFO):** `publish_typed`'s dedup key is computed over raw `record.attributes`, so a caller who injected reserved keys (`idempotency_key`/`bus_sequence`) into attributes could perturb dedup; the in-module builders never do, and `_store` overwrites those keys on store, so it is unreachable in practice. No action required.

## Modularity note (informational)
The three new modules are small and single-responsibility (contract composition / outcome classification / check-in schedule+ingestion); `event_bus.py` grew by one cohesive additive method. No threshold pressure, no dumping-ground mixing.

## Test evidence
- goal-integration pack: **31/31 pass** (0.18s)
- unit-D event-bus pack (regression from the additive method): **38/38 pass**
- reused security modules (contracts=R045 validator, telemetry redaction/journal): **151/151 pass**
- 5 independent security probes: all pass (leak-free store, R045 on constraints, UUID masking, sequence rollback, DoS bounds).

**Verdict: PASS.** No corrections block acceptance. Three advisories are informational/non-blocking; ADV-1 is recommended for the functional (G3/G4) gates' attention.
