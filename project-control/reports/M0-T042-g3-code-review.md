# G3 Code Review Report — M0-T042 (Codex ephemeral review integration + root AGENTS.md)

## Verdict: **PASS**

Reviewed head `fa69f9e5600e390750fada345f33713261438de1` in worktree `C:/Users/MLFLL/Downloads/nyc-zoning/orch` (branch `task/M0-T042-codex-review`). `git rev-parse HEAD` == reviewed SHA at review time; `git status --short` clean (reviewed_sha == HEAD). Diff under review: `0ed2cdb..fa69f9e`. Reviewer: code-reviewer (independent; not the producer).

## Independently observed test results

| Command | Result |
|---|---|
| `python -m unittest tools.test_agent_supervisor_ephemeral_review -v` | **Ran 23 tests in 0.419s — OK** |
| `python -m unittest discover -s tools -p "test_agent_supervisor_*.py"` | **Ran 1212 tests in 71.389s — OK (skipped=2)** |

So: **1212 run / 1210 pass / 0 fail / 2 skip** — matches the producer's claim exactly. No existing test file was modified (only `codex_reviewer.py`, `__init__.py`, `README.md` among non-new code files), so the +23 delta is entirely the new module.

## Load-bearing logic — verified

- **`ReviewBudget.effective_ceiling`** (review_packet.py:113-135): lower-of semantics correct — window None → 64,000 (`ordinary_only`, relative honestly skipped, not fabricated); 400,000 → 64,000 (`ordinary`, 20%=80k loses); 200,000 → 40,000 (`relative_model_window`). Equality boundary (window 320,000, relative==ordinary==64,000) → tokens 64,000, basis `ordinary` — correct. `within_ceiling` uses inclusive `estimated <= ceiling.tokens`. **`estimate_tokens`** = `ceil(max(0,bytes)/4)` — 400,000→100,000, 1→1, negatives→0. Correct.
- **`guard_packet` + `_apply_strip`** (review_packet.py:380-433): hand-traced the `unrelated_task_packets` double-negative filter. For a related packet `task_id == current_task_id`: `not (Mapping and (task_id not in ("",None,current)))` → `not(True and False)` → KEPT. Unrelated → `not(True and True)` → DROPPED. Empty/None task_id and non-mappings are defensively KEPT. Symmetric with the scan detector. Confirmed no false positives on the real `evidence.build_packet` output (`test_a_clean_bounded_packet_passes`): real packet top-level keys and section keys (`task_packet`, `directive_refs`, `claude_checkpoint`, `git`, ...) never collide with the marker/completeness sets.
- **`ReviewRecord.finalize()` / `verify_record`** (ephemeral_review.py:97-120): digest round-trip is sound in both directions. The only tuple field (`redaction_labels`) is popped before redaction, re-added as a list, and normalized to list on both the finalize side and the verify side (and JSON has no tuples), so the digested bytes are identical on the in-memory path, after `to_dict()`, and after the JSONL journal round-trip. No false tamper alarm (verify True on untampered — AS-1 + `journal.verify()`); no tamper pass for a modification that doesn't also recompute the digest (`test_a_tampered_record_fails_verification`). It is an unkeyed content seal (see INFO-2).
- **`parse_usage_telemetry`** (codex_reviewer.py:337-386): never returns zero for *absent* usage (returns `USAGE_UNKNOWN`); peak-cumulative across events (keeps max total); prefers a provider `*total*token*` field to avoid double-count; excludes bools via `isinstance(int) and not isinstance(bool)`; scans multiple carrier keys + nested `info` for CLI-shape drift; crash-safe because `ProcessResult.stdout` is coerced to `str` at process.py:698 (`stdout or ""`), so `None.splitlines()` cannot occur.

## Contract fit — verified

- **`ReviewOutcome.usage_telemetry`** is a defaulted trailing field (`= USAGE_UNKNOWN`), so all existing constructions stay valid. All three `review()` exit paths are correct: success and schema-exhausted both call `parse_usage_telemetry(...)`; the resolution-unusable early return (codex_reviewer.py:499) keeps the default `USAGE_UNKNOWN` — honest, because no process ran. `ephemeral_review` reads it defensively via `getattr(outcome, "usage_telemetry", USAGE_UNKNOWN)`.
- Packet shape read by `review_packet` matches `EvidencePacket.to_dict()` exactly: `sections` (Mapping), `failed_collections` (list of Mappings → omissions), `truncations` (list), `size_bytes`, `packet_digest`. `CodexDecision.evidence_refs` is `list[dict]`, so `_reopened_sources` (Mapping-based) works. Redaction uses `redact_structure` returning `RedactionResult(.value/.count/.labels)`, matching evidence.py's proven pattern. Fail-closed idiom (`BudgetError`, `GuardError`, `EphemeralReviewError`, refusal records) is consistent with the package.

## Shadow-only discipline — CONFIRMED

No hidden activation path found.
- No import of `ephemeral_review` / `review_packet` / `review_cadence` (nor `guard_packet` / `conduct_ephemeral_review`) in `loop.py` or `cli.py`. (`cli.py`'s `--ephemeral` matches are the pre-existing Codex CLI flags, not the new module; `cli.py` is unmodified.)
- `__init__.py` mentions the three modules only in the module-map **docstring** (no imports, no `__all__` change); `README.md` adds descriptive rows only.
- `conduct_ephemeral_review` refuses any non-reviewer role (`role_not_activatable`, ephemeral_review.py:248-253) — proven by `test_worker_role_is_never_activated_by_the_loop`.
- `record_worker_fallback` builds a durable role=worker record and launches nothing / grants no writes.
- The four `codex_reviewer.py` hunks are additive telemetry only.

## AGENTS.md factual accuracy — verified

- Decision enum in AGENTS.md (`CONTINUE, REVISE, STOP_FOR_OWNER, ROTATE_SESSION, COMPLETE, HALT_UNSAFE`) matches `schemas/codex_decision.schema.json` line 29 **exactly**.
- `tools/code_graph/query.py` exists; all routed docs exist (`PRD.md`, `docs/IMPLEMENTATION_SEQUENCE.md`, `docs/GATES_AND_CHECKPOINTS.md`, `docs/PROJECT_CONTROL_PROTOCOL.md`, `docs/ACCEPTANCE_SCENARIO_STANDARD.md`, `docs/SESSION_HANDOFF.md`, `tools/project_control.py`, `tools/current_state.py`).
- Covers **all 13** Section 11.1 topics (source-001.md:1154-1168): mission, authoritative state, session start, never-guess, deterministic boundary, five-borough scope, task/path discipline, evidence, autonomy authority, hard stops, on-demand routing, code graph + context packs, checkpoint reporting.
- Authority claims (read-only when reviewing; orchestrator-only mutations; worker never self-completes; hard-stop list; never-guess list; 32k/64k/20% budget) are consistent with CLAUDE.md and ADR-005. No wholesale duplication: `wc` shows AGENTS.md 3893 bytes / 78 lines vs CLAUDE.md 8339 bytes / 112 lines; explicitly defers to CLAUDE.md / project-control as canonical. No overreach into 11.2 path-scoped files (out of scope, forbidden paths respected).

## Per-scenario confirmation

- **AS-1 PASS** — Fresh ephemeral end-to-end: durable record holds decision (`CONTINUE`), 2 evidence refs, supervisor-recorded model identity (`codex-primary`), usage telemetry (`total_tokens=1500`), packet+record digests; second review provably shares no state (distinct packet digests, `shares_conversation_state=False`, `distinct_from_prior`); tamper detected; AD-087 reopened-sources correct (engine.py reopened, task json not). Also round-trips and re-verifies from the JSONL journal.
- **AS-2 PASS** — Over-ceiling packet refused with split/summarize guidance and an explicit durable record; reviewer provably never called (`RecordingReviewer.calls==0`); lower-of ceiling semantics and `estimate_tokens` proven; bad-budget config fails closed. The producer's window `1000→100` deviation is **sound and unweakened** (see INFO-4).
- **AS-3 PASS** — Each prohibited category named in the scenario (transcript, directive registry, historical reports, whole repository, unrelated task packets) rejected; clean packet passes; strip mode records every removal including the mixed-list double-negative case; `conduct_ephemeral_review` refuses a prohibited packet without running the reviewer.
- **AS-4 PASS** — All 7 meaningful 0A.3 triggers warrant a review; a passing deterministic check alone is a reasoned refusal (not silent); a trigger beats a coincident deterministic pass; no signal → no review.
- **AS-5 PASS** — Root AGENTS.md exists, covers all 13 Section-11.1 topics, and does not duplicate CLAUDE.md wholesale (test asserts ≤2 shared ≥40-char lines and it passes; smaller byte size; <120 lines).

## Directive rows (13) — code-verifiable status (advisory to the directive-compliance-verifier)

R027 ✓ (independence proof, fresh process, AS-1), R041 ✓ (AGENTS.md 11.1 coverage), R042 ✓ (no wholesale duplication), R081 ✓ (sole loop entry, fresh process per call), R082 ✓ (no persistent session/resume), R083 ✓ (content guard), R084 ✓ (cadence), R085 ✓ (lower-of ceilings), R086 ✓ (guidance + refusal record, reviewer never called), R087 ✓ (reopened_sources), R088 ✓ (role guard + recorded worker fallback), R093 ✓ (bounded additive diff, every module maps to a named row, no forbidden paths, shadow-only), R116 ✓ (delivered via controlled-task → gate flow). No forbidden path touched (`.claude/`, `apps/`, `services/`, `.github/`, `project-control/directives/`, manifests/lockfiles all clean). Extra `project-control/` files in the diff (state.json, gates/, evidence-map, g0-readiness, M0-T042.json report) are orchestrator lifecycle artifacts, not producer code-scope violations.

## Findings

**BLOCKING:** none.
**MAJOR:** none.

**MINOR**
- **M-1 (test coverage)** — `review_packet.py:282-285`: `all_logs` and `full_code_graph` marker keys are implemented in `PROHIBITED_MARKER_KEYS` and named in 0A.1/AD-083, but neither has a direct rejection fixture (the AS-3 test covers the 5 categories named in the scenario text). Same code path as the tested categories, so risk is low, but a two-line fixture would close the AD-083 category set.
- **M-2 (test coverage)** — `ephemeral_review.py:294-314`: the path where `reviewer.review()` returns a non-refusal outcome with `decision=None` (schema-retry-exhausted or unusable model) is not exercised at the ephemeral-review layer. The code handles it defensively (empty `evidence_refs`, stores the outcome's error fields, `ok=False`), so this is a coverage gap, not a defect.

**INFO**
- **I-1** — `review_packet.py:330-341`: the content guard is key-name/completeness-flag structural detection, not content-semantic. A whole transcript smuggled as a string *value* under an innocuous key would not be caught. The deterministic `evidence.build_packet` (which never includes transcripts) is the primary control; the guard is a secondary belt-and-suspenders check. Worth re-confirming at the R595 activation review.
- **I-2** — `ephemeral_review.py:97-120`: `record_digest` is an unkeyed SHA-256 content seal (same idiom as evidence.py `packet_digest`). It detects corruption / non-recomputed modification (as the tamper test proves) but is not an authenticated MAC. Acceptable for a shadow-only audit log; consistent with the package.
- **I-3** — `review_packet.py:352`: unrelated-task-packet detection is skipped when `reviewed_task_id` is empty (no current task to correlate); marker/completeness scans still run. Not reachable in practice (`conduct_ephemeral_review` always passes a task id).
- **I-4** — The AS-2 refusal fixture uses `model_context_window=100`, an artificial value. The producer's `1000→100` change is correct: with the real 652-byte packet (163 est. tokens), a 1000-token window (200-token ceiling) would **not** refuse (a broken test); 100 makes the relative ceiling (20 tokens) the binding constraint and the refusal genuine. This exercises exactly 0A.4's novel relative-ceiling mechanism; the scenario is strengthened, not weakened. I concur with the producer.
- **I-5** — Producer report cites CLAUDE.md = 8227 bytes; my `wc -c` shows 8339 bytes / 112 lines. Immaterial — the AS-5 assertion only requires AGENTS.md < CLAUDE.md, which holds (3893 < 8339).

## Could not independently execute

The read-only guard blocked inline `python -c` and scratchpad file writes, so the reviewer could not run custom edge-case print scripts for (a) the exact AGENTS/CLAUDE shared-line count, (b) `effective_ceiling(320000)`, (c) additional `parse_usage_telemetry` peak/bool/nested cases. These were verified by hand-tracing the source AND by the passing unittest suite, which asserts the ≤2 shared-line bound, the lower-of ceilings, the ceil estimate, and the usage-sum/unknown behavior. This limitation does not affect the verdict.

## Relevant paths

- `tools/agent_supervisor/review_packet.py`, `review_cadence.py`, `ephemeral_review.py`, `codex_reviewer.py`
- `tools/test_agent_supervisor_ephemeral_review.py`
- `AGENTS.md`

**Recommendation: PASS.** M-1 and M-2 are optional test-hardening follow-ups (not gate blockers); I-1 belongs on the R595 activation checklist.
