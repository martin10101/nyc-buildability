# M0-T042 Producer Report — Codex ephemeral review integration + minimal root AGENTS.md

**Task:** M0-T042 — Codex ephemeral review integration (0A.8 item 4; AD-081..AD-088) + minimal root AGENTS.md
**Branch / worktree:** `task/M0-T042-codex-review` @ `C:/Users/MLFLL/Downloads/nyc-zoning/orch`
**Producer:** backend-engineer
**Requested status:** awaiting_gate
**Posture preserved:** the supervisor remains ACCEPTED / MERGED / SHADOW-ONLY. Nothing in this change activates
autonomy, forwards a prompt, launches a real `codex` binary, or touches the R595 activation path. Every new
entry point records and returns, exactly like the rest of the package. R595 rehearsal remains a mandatory
blocking prerequisite before any activation and is untouched here.

## AD-093 qualifying evidence (no speculative supervisor feature)

This work is NOT speculative. Qualifying evidence, as required by D-010-R093/AD-093:
- **D-010 Section 0A.8 item 4** names *fresh ephemeral Codex review* an explicit BLOCKING minimum-autonomy capability.
- **AD-081..AD-088** are explicit directive requirements describing exactly this loop, its budgets, its content
  guard, its cadence, its independence, and its role honesty.
- **AD-041/AD-042** explicitly require a concise root `AGENTS.md` that does not duplicate `CLAUDE.md`.
Every module here maps to a named directive requirement; nothing was added on speculation.

## Design provenance

A prior read-only backend-engineer run produced a complete, in-process-validated design (staged verbatim in the
session scratchpad under `t042-design/`). As accountable producer I did NOT blind-copy it: I verified every
interface each file assumes against the real worktree source before writing, and adapted where the design was
wrong. Deviations are listed at the end. Where the design was correct, the module bodies are the design's,
because they were already verified against the live interfaces.

## Files created / modified

Created:
- `tools/agent_supervisor/review_cadence.py` — 0A.3 meaningful-checkpoint cadence policy (AD-084).
- `tools/agent_supervisor/review_packet.py` — 0A.4 token budget + AD-083 prohibited-content guard (AD-083/085/086).
- `tools/agent_supervisor/ephemeral_review.py` — the operational fresh-ephemeral review loop + durable record
  (AD-027/081/087/088; 0A.1 item 7).
- `tools/test_agent_supervisor_ephemeral_review.py` — 23 executable acceptance tests (AS-1..AS-5 + strip/usage/role).
- `AGENTS.md` (worktree root) — concise Codex-facing brief (AD-041/042).

Modified:
- `tools/agent_supervisor/codex_reviewer.py` — 4 additive hunks: `USAGE_UNKNOWN` import; `parse_usage_telemetry`
  + `_event_usage_object` + `USAGE_CARRIER_KEYS`; a defaulted `usage_telemetry` field on `ReviewOutcome`; and
  four one-line additions inside `review()` populating that field on both the success and the exhausted paths.
  Nothing removed; the resolution-unusable early return keeps the default `USAGE_UNKNOWN` (no process ran).
- `tools/agent_supervisor/__init__.py` — added the three new modules to the module-map docstring (see optional item).
- `tools/agent_supervisor/README.md` — added three rows to the "What exists, module by module" table (optional item).

## Verification duties (each checked against live source)

1. **models.py** — `USAGE_UNKNOWN="unknown"`, `canonical_json` (sort_keys, no whitespace, non-ASCII kept),
   `digest_of` (SHA-256 over canonical JSON, deterministic over dicts via sort_keys), `to_utc_iso` all exist with
   the assumed semantics. Digest determinism over dicts confirmed — the record digest round-trip relies on it.
2. **redaction.py** — `redact_structure` exists and returns `RedactionResult` with `.value/.count/.labels`. Confirmed.
3. **evidence.py** — `build_packet(run_id=, task_id=, checkpoint_id=, checkpoint=)` signature matches; result is
   `PacketResult` with `.ok/.reason/.packet.to_dict()`; the packet dict carries `sections`, `size_bytes`,
   `packet_digest`, `failed_collections`, and `truncations` exactly as `review_packet.py` reads them. Confirmed.
4. **codex_reviewer.py** — all HUNK D anchors exist verbatim (`last_returncode = 0`, `last_returncode =
   result.returncode`, the success and exhausted `ReviewOutcome(...)` constructions). `ReviewOutcome` field names
   match (`decision_digest`, `selection_digest`, `model_self_report_mismatch`, `attempts`, `returncode`,
   `error_code`, `error_message`, `notify_events`, `tier`). `CodexReviewer.__init__` accepts the test's kwargs
   (`repo=, schema_path=, config=, selection=, audit=, run_id=, max_attempts=, timeout_seconds=, runner=`) with
   `executable` positional. `review()` accepts `expected_task_id`/`expected_checkpoint_id`. Confirmed.
5. **ReviewRecord.finalize()/verify_record digest round-trip** — traced by hand and proven by the suite:
   `finalize` computes `digest_of(stored)` over the redacted body plus `redaction_count` and `redaction_labels`
   (as a LIST), before `record_digest` is inserted. `verify_record` strips `record_digest`, coerces any tuple
   `redaction_labels` to a list, and recomputes — identical bytes. The only tuple field (`redaction_labels`) is
   converted to a list by `to_dict()`, so there is no tuple/list divergence in the in-memory path, and JSON has no
   tuples so the on-disk path is identical too. Proven by `test_a_tampered_record_fails_verification` (in-memory
   tamper), `journal.verify()` and `journal.load()` (JSON round-trip), and the worker-fallback record's verify.
6. **_apply_strip double negative for `unrelated_task_packets`** — traced by hand: for a packet whose `task_id`
   equals `current_task_id` the membership test is False, so `not (Mapping and False)` = True → KEPT; for an
   unrelated `task_id` it is True → `not (Mapping and True)` = False → DROPPED; empty/None `task_id` and
   non-mappings are kept (defensive). Added two tests: one on a MIXED list `[M0-T042 (related), M0-T099
   (unrelated)]` proving the related packet is kept and the unrelated one dropped with a recorded `stripped`
   finding, and one proving an all-unrelated list drops the whole `task_packets` section rather than leaving `[]`.
7. **AS-2 refusal window** — DEVIATION (see below). The real `ev.build_packet` output measures **652 bytes → 163
   estimated tokens**. The staged test used `model_context_window=1000` → 200-token ceiling; 163 ≤ 200 means the
   packet would NOT be refused and the staged test would have FAILED. I lowered the window to **100** (20-token /
   80-byte ceiling); 163 > 20 refuses deterministically regardless of small packet-size drift. Assertion tokens
   updated to 20. No acceptance scenario weakened — the refusal is now genuinely exercised.
8. **AS-5 thresholds vs the REAL CLAUDE.md** — measured: `AGENTS.md` = 3893 bytes / 78 lines; `CLAUDE.md` = 8227
   bytes. `3893 < 8227` ✓; `78 < 120` ✓; shared lines ≥40 chars = **0** (≤ 2) ✓. AGENTS.md left as written; no
   threshold changed.
9. **AGENTS.md factual claims** — `tools/code_graph/query.py` exists (verified). The six decision values in the
   "Reporting a checkpoint" section match the `codex_decision.schema.json` `decision` enum EXACTLY (CONTINUE,
   REVISE, STOP_FOR_OWNER, ROTATE_SESSION, COMPLETE, HALT_UNSAFE). Every routed doc path exists: `PRD.md`,
   `docs/IMPLEMENTATION_SEQUENCE.md`, `docs/GATES_AND_CHECKPOINTS.md`, `docs/PROJECT_CONTROL_PROTOCOL.md`,
   `docs/ACCEPTANCE_SCENARIO_STANDARD.md`, `docs/SESSION_HANDOFF.md`, `tools/project_control.py`,
   `tools/current_state.py`, `tools/agent_supervisor/schemas/codex_decision.schema.json`.
10. **process.run** — accepts `cwd=, env=, timeout=, input_text=` (plus container kwargs); the test's `runner`
    pops `env`, prepends the fake-script argv, and forwards `cwd/timeout/input_text` via `**kwargs`. Confirmed.
11. **config loaders** — `load_controller_config`/`load_model_selection` accept the test's TOML fixtures;
    `resolve_model` finds `review_model="codex-primary"` and `advisory_model="codex-fallback"` both present in
    `[codex].allowed_models`, so selection validates and the review resolves to `codex-primary`. Confirmed by AS-1
    asserting `record.model_used == "codex-primary"`.

## Budget policy numbers (0A.4)

Target 32,000 tokens; ordinary hard ceiling 64,000 tokens; relative hard ceiling 20% of the reported model
context window; effective ceiling = the LOWER of ordinary and relative; deterministic estimate = ceil(bytes / 4).
Verified: window None → 64,000 (ordinary_only); 400,000 → 64,000 (20% = 80k, ordinary wins); 200,000 → 40,000
(relative_model_window); estimate_tokens(400,000 bytes) = 100,000. When the window is unknown the relative
ceiling is honestly recorded as skipped, never fabricated. Overflow yields `within_ceiling=False`, six-item
split/summarize guidance, and a durable refusal — never a silent trim (0A.4 rule 5).

## Durable review record fields (0A.1 item 7)

`ephemeral_review.ReviewRecord` records: `decision` (+ `decision_value`, `decision_digest`), `evidence_refs`,
`model_used` + `model_selection_digest` + `model_self_report_mismatch` (supervisor-recorded identity, never the
model's self-claim), `usage_telemetry` (peak `total_tokens`, or `USAGE_UNKNOWN` — never zeroed), `packet_digest`,
the full `budget` assessment, `guard_findings`, `reopened_sources` (AD-087), an `independence` proof (AD-027),
`attempts`/`returncode`/`error_code`/`error_message`/`notify_events`, `redaction_count`/`redaction_labels`, and a
content `record_digest` sealing the stored bytes. `ReviewJournal` is append-only JSONL with fsync and a
`verify()` that re-checks every row's digest.

## AGENTS.md rationale (AD-041/042)

A concise (78-line) Codex-facing brief covering the Section 11.1 topics — mission, authoritative state, session
start, never-guess, deterministic boundary, full five-borough scope, task/path discipline, evidence, autonomy
authority (read-only when reviewing), hard stops, on-demand routing, code graph + bounded context packs, and how
to report a checkpoint. It explicitly defers to `CLAUDE.md` and `project-control/` as canonical on any conflict
and shares ZERO ≥40-char lines with `CLAUDE.md`, so it adds a Codex orientation without duplicating the operating
rules.

## Optional package-doc coherence item (owner's-call, recorded)

I ADDED the three new modules to the `__init__.py` module-map docstring and the README "What exists, module by
module" table. Decision rationale: both paths are in allowed scope; the controller manifest is generated
dynamically via `rglob("*")` over covered patterns (`*.py`, `README.md`, ...) and verified against a recorded
manifest generated in the same run — there is no frozen file-list fixture, so new files and edited docs are
manifest-safe. Confirmed: the full suite (including the manifest matrices) stays green after the edits.

## Commands run + results

```
$ python -m unittest tools.test_agent_supervisor_ephemeral_review -v
Ran 23 tests in 0.472s
OK
```
(23 test methods total in the new module — the design's 21 plus the two added strip-mode tests, duty 6.)

```
$ python -m unittest discover -s tools -p "test_agent_supervisor_*.py"
Ran 1212 tests in 73.793s
OK (skipped=2)
```

Baseline before this task: 1189 run / 1187 pass / 0 fail / 2 skip. After: **1212 run / 1210 pass / 0 fail / 2
skip**, i.e. **+23 net new tests** (the discover delta 1212 − 1189 = 23, all contributed by the new module). All
new tests pass; zero failures/errors introduced. Duration 73.8s.

## Per-requirement evidence mapping (all 13 bound rows)

- **D-010-R027 (AD-027, fresh & ephemeral):** every review is a brand-new read-only process; `ReviewRecord.independence`
  proves `fresh_process_per_review=True`, `shares_conversation_state=False`, and `distinct_from_prior`. Evidence:
  `ephemeral_review._independence_proof`; test `test_a_second_review_shares_no_state_with_the_first`.
- **D-010-R041 (AD-041, root AGENTS.md):** concise root `AGENTS.md` created. Evidence: `AGENTS.md`; test
  `test_agents_md_exists_and_covers_the_11_1_topics`.
- **D-010-R042 (AD-042, no CLAUDE.md duplication):** 0 shared ≥40-char lines, smaller byte size, <120 lines. Evidence:
  `test_agents_md_does_not_duplicate_claude_md_wholesale`.
- **D-010-R081 (AD-081, ephemeral review is the default):** `conduct_ephemeral_review` runs only the fresh read-only
  reviewer; there is no persistent-controller path. Evidence: `ephemeral_review.py`; AS-1 tests.
- **D-010-R082 (AD-082, no persistent Codex controller):** no long-lived session is created or resumed; each review is a
  single fresh process discarded on completion. Evidence: `codex_reviewer.review` (fresh process per attempt) + loop.
- **D-010-R083 (AD-083, no full transcript / unrelated history):** `guard_packet` rejects/strips full transcript, full
  directive registry, all historical reports, unrelated task packets, whole repository, all logs, full code-graph.
  Evidence: `review_packet.guard_packet`; AS-3 tests incl. mixed-list strip.
- **D-010-R084 (AD-084, meaningful-checkpoint cadence):** `decide_review` reviews the 0A.3 triggers and refuses to spend
  a review on a deterministic pass alone. Evidence: `review_cadence.py`; AS-4 tests.
- **D-010-R085 (AD-085, packet token & relative-context ceilings):** `ReviewBudget.effective_ceiling` enforces the lower
  of the 64k ordinary and 20%-of-window relative ceilings. Evidence: `review_packet.py`; AS-2 tests.
- **D-010-R086 (AD-086, split oversized reviews, no giant session):** over-ceiling packets are refused with
  split/summarize guidance (incl. "never open a giant persistent Codex conversation"). Evidence:
  `SPLIT_SUMMARIZE_GUIDANCE`; `test_an_oversized_packet_is_refused_with_guidance_and_no_review`.
- **D-010-R087 (AD-087, no duplicate investigation):** the bounded packet lets Codex challenge the worker without
  inheriting its context; `reopened_sources` records paths Codex cited beyond the packet. Evidence:
  `ephemeral_review._reopened_sources`; AS-1 reopened-sources assertions.
- **D-010-R088 (AD-088, writable worker is a bounded fallback role):** the loop refuses any non-reviewer role;
  `record_worker_fallback` builds (never activates) a recorded worker-role exception. Evidence:
  `conduct_ephemeral_review` role guard + `record_worker_fallback`; `RolesAndUsage` tests.
- **D-010-R093 (AD-093, no speculative feature):** every module maps to a named directive requirement; qualifying
  evidence cited above (0A.8 item 4 blocking capability + AD-081..088). Evidence: this report's AD-093 section.
- **D-010-R116 (session-2 re-dispatch / resume wave-1 minimum-autonomy):** this task is one of the resumed wave-1
  minimum-autonomy work items; it is delivered through the standard controlled-task → independent-gate flow with
  executable acceptance evidence, consistent with the re-dispatch requirement. Evidence: this producer submission.

## Deviations from the staged design (I own these)

1. **AS-2 refusal window 1000 → 100.** The real packet is 652 bytes (163 est. tokens); the staged window of 1000
   gave a 200-token ceiling, so the packet would have been WITHIN budget and the refusal test would have failed. I
   lowered the window to 100 (20-token / 80-byte ceiling) and updated the asserted ceiling to 20. This makes the
   refusal genuine and robust to small packet drift; no assertion was weakened.
2. **Added two strip-mode tests (duty 6).** The staged test file only exercised the transcript strip. I added
   `test_strip_mode_keeps_the_related_packet_and_drops_the_unrelated_one` (mixed list, proves the double-negative
   `kept` filter keeps the related packet and drops the unrelated one with a recorded `stripped` finding) and
   `test_strip_mode_drops_task_packets_when_none_are_related` (all-unrelated → whole section removed).
3. **Optional package-doc edits (owner's-call, taken).** Added the three modules to `__init__.py` module-map and
   the README table for coherence; verified manifest-safe (dynamic rglob manifest) and suite-green.

No other changes: the three module bodies and `AGENTS.md` are the design's, because their interfaces were all
verified correct against the live worktree. The four `codex_reviewer.py` hunks were applied exactly as specified
and their anchors verified present.

## Anomalies / open concerns

- None blocking. The suite is fully green (0 failures/0 errors) on Python 3.11.9, Windows.
- The loop is deliberately NOT wired into `loop.py` / `cli.py`; it records and returns only. Wiring it into an
  active supervised cycle is a separate, activation-gated step behind R595 and is out of scope here.
- `parse_usage_telemetry` scans multiple carrier keys (`usage`/`token_usage`/`token_count`, incl. nested `info`)
  to tolerate Codex `--json` event-shape drift (the AD-022 risk note); a live-CLI fixture should re-confirm the
  real event shape before any activation.
