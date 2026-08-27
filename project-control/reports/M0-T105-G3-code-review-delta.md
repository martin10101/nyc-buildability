# M0-T105 G3 code review — DELTA round 2 (VERBATIM reviewer return; transport entity-decoding only)

Saved by the orchestrator per the report-preservation rule. Reviewer: code-reviewer (same agent
resumed with round-1 context, 2026-08-27). Verdict returned: **PASS**.

---

# Gate Report (G3 delta re-review)

- **Gate ID:** G3 (independent code review — delta, round 2)
- **Task ID:** M0-T105 (D-024 Amendment 3 unit D: native event integration)
- **Reviewer:** code-reviewer (independent; read-only)
- **Producer:** fable-orchestrator-session
- **Result:** **PASS** (round-1 blocking item and my A3/A4/A5 genuinely closed; A1/A2 remain correctly-scoped non-blocking residuals; no new defects)
- **Clean environment/worktree used:** Re-frozen deliverable `bfdf4ef5e4682d64a7e1c8f0a330b86fc04d1963`, content manifest `4bd0e182…fe15d3`, live HEAD `9f816477c1c78d45599d54637ccedcc88f401d80`. The two commits after the deliverable are control-plane only (`9f81647` resubmit). Working tree clean (`git status --porcelain` empty — matches the frozen blob).

## Acceptance criteria reviewed

Delta since round-1 deliverable `50abb34`: corrections F1–F5 + C1 discharge. Round-1 verdict was PASS with advisories A1–A5; a G4 M1 MEDIUM (recorder cp1252 stdin) was the blocking driver of this correction round. Scope re-reviewed: F1/F2 code diffs, closure of A3/A4/A5, correct scoping of A1/A2, the C1 fixture tooth, and report/G2 line-count accuracy at the new identity.

## Directive/requirement verification

No requirement scope change; applicable set is still **D-024-R154, D-024-R155, D-024-R173**. Each re-confirmed at the new identity; the corrections strengthen R155 (recorder correctness/fidelity) and R173 (measured 2.1.247 facts) without altering the boundary. Authoritative verdict remains the `directive-compliance-verifier`'s in `verification.json`.

| Requirement ID | Reviewed identity | Verdict | Delta evidence |
|---|---|---|---|
| D-024-R154 | bfdf4ef / 4bd0e182 | PASS | `event_stream.py` unchanged; sidecar-primary + no-transcript-polling intact. C1 fixture confirms structured events (no model queries). |
| D-024-R155 | bfdf4ef / 4bd0e182 | PASS | F1 makes the recorder byte-faithful (UTF-8), preserving fail-closed + external-state-only; F3 documents the dedup-window default; C1 proves the fail-closed recorder end-to-end on a real owner-launched 2.1.247 run (9 sanitized records, prompt never persisted, session UUID digest-masked). |
| D-024-R173 | bfdf4ef / 4bd0e182 | PASS | Unknown/drift handling unchanged; C1 adds a *measured* drift-relevant fact (Agent-tool spawn fires SubagentStart/Stop, NOT TaskCreated/TaskCompleted on 2.1.247), recorded honestly. |

## Steps independently executed

- `python -m pytest tools/test_agent_supervisor_event_bus.py -q` → **38 passed in 2.11s** (was 32; +6).
- Targeted `-k "nested_uuid or non_ascii or oversized_stdin or registry_bounded_at_bus or content_digest_fallback or c1_live_fixture"` → **6 passed, 32 deselected**.
- `git diff 50abb34 bfdf4ef` on `event_bus.py`, `supervisor_event_recorder.py`, test file — read in full (below).
- Line counts from the frozen blob (`git show bfdf4ef:<f> | wc -l`): **event_bus 292 / event_stream 234 / event_drift 106 / recorder 87 / tests 560** — exact match to the reported numbers.
- `ruff check` on the three changed files → **All checks passed!**
- `python tools/modularity_check.py --check` → **0 failures**; only pre-existing warnings (`cli.py`, `policy.py`, `context_benchmark.py`, `types.ts`, `mappluto_geometry_arcgis.py`); no new file flagged (event_bus 284→292 stays far under warn 600).
- `python -m pytest tools/ --collect-only -q` → **2809 collected**, zero import/collection errors.
- Adapter/guard integrity: `native_runtime.py`, `runtime_backend.py`, `readonly_agent_guard.py` — **never touched** across the full task range `44a4c6c..HEAD` (git-verified).

## Expected versus actual — the diffs

**F1 (recorder cp1252 → UTF-8), CORRECT.** `sys.stdin.read()` (locale/cp1252 on Windows) replaced with `sys.stdin.buffer.read(MAX_STDIN_BYTES + 1)` then `.decode("utf-8-sig", "replace")`. This is the right fix and matches the carried M0-T104 UTF-8 lesson: the oversized check now bounds *bytes* (a correct byte cap, decoded only after the size gate), `utf-8-sig` tolerates a BOM, and `"replace"` keeps a damaged byte visible rather than dropping the whole event. `test_s9_recorder_non_ascii_payload_fidelity` bites for real — an emoji `agent_type` and an accented `cwd` round-trip through the recorder subprocess with no mojibake, are not dropped, and still get `[HOME]`-sanitized.

**F2 (recursive UUID masking), CORRECT and closes A4.** `_mask_if_uuid` (top-level only) replaced by `_mask_uuids`, which recurses over dict values AND keys and list/tuple items, digest-masking every UUID-shaped string at any depth. Applied to `dict(record.attributes)`, `session_id`, `task_id`. Verified non-regressions: (a) `idempotency_key`/`bus_sequence` are stamped *after* masking, so neither is masked and dedup keys stay stable; (b) the dedup key is still computed from the raw pre-ingest payload, so masking never perturbs dedup; (c) mask output for a plain string is identical to the old behavior. `test_s4_nested_uuid_masked_at_any_depth` bites (UUID nested in a dict value, as a dict key, and in a list — asserts `SESSION_UUID` absent and ≥4 mask markers).

**F3 (inline warm_rotated rationale), closes A3.** A clear comment now documents that only the active journal generation warms the dedup set, so a post-rotation duplicate is re-recorded in the safe direction (never data loss / never false-dedup) and surfaced later as `store_duplicates` — exactly the disclosure A3 asked for, cross-referenced to G3-A3/G4-L1.

## Advisory disposition

- **A3 — CLOSED** (F3 inline disclosure).
- **A4 — CLOSED** (F2 recursive mask + biting nested test).
- **A5 — CLOSED** (F5: `test_s9_recorder_oversized_stdin_fails_closed` exercises the 1.1 MB → nothing-recorded branch; `test_s3_stream_key_content_digest_fallback` exercises uuid-less content-digest dedup). Also gains `test_s10_registry_bounded_at_bus_level` (registry bound proven through the bus, closing G4's round-1 A2).
- **A1 — RESIDUAL, correctly scoped (LOW/ADVISORY).** `_event_usage`/`MAX_LINE_BYTES` still lightly duplicated with `claude_runner.py`; deliberately not extracted (extraction would couple two modules for marginal gain). Still accurate; non-blocking.
- **A2 — RESIDUAL, correctly scoped and now LIVE-CONFIRMED (LOW/ADVISORY).** `bus_sequence` is inherently not collision-free under concurrent fresh-process recorders. It is now (i) disclosed inline (F3 references G3-A2) and (ii) empirically confirmed by the C1 capture: two concurrent hook firings (PostToolBatch + SubagentStart, identical timestamp) are each stamped `bus_sequence 3`, append order preserved, dedup keys distinct, no record lost. This is the honest resolution — a documented, measured, non-harmful property surfaced via `store_duplicates`, not a defect to "fix."

## Regression / security / provenance findings

- **C1 fixture tooth — sound and honest.** `hook_events_live_2026-08-27_m0t105_c1.json`: 9 measured-live records, all parse as `TelemetryRecord` (schema `supervisor_telemetry/v1`), all `known:true`, every `session_id` digest-masked, prompt never persisted (withheld as `PROMPT-WITHHELD` digest, 29 chars — measured non-UUID `prompt_id` shape on 2.1.247), `[HOME]`-masked cwd. `test_c1_live_fixture_masked_and_replayable` asserts the required event set, `TaskCreated` absence (measured), and the `bus_sequence.count(3)==2` collision. Notable provenance discipline: the stray SessionEnd from a *different* session in the scratch directory is recorded with its own distinct digest `[SESSION sha256=f8304cf9a432]` rather than guessed into the capture session — this is exactly the "record honestly, never invent" posture the directive requires.
- **`.gitleaksignore` (9 entries) — legitimate.** The flagged 64-hex values are content-addressed `idempotency_key` dedup digests of already-sanitized payloads (sha256 of event identity + sanitized content), not credentials; the audit rationale is documented in-file and cross-referenced to the G5 report. Correct call. **New ADVISORY (LOW):** the ignore uses `file:rule:line` fingerprints, which are line-position-fragile — if the frozen fixture is ever edited, the pins silently drift. Acceptable for frozen evidence; G5 owns the definitive leak-scan verdict.
- Adapter/guard byte-untouched; recorder default store still gitignored; working tree clean; no new modularity or ruff findings.

## Defects

None (no HIGH/MEDIUM/LOW blocking). Residual advisories: A1, A2 (both non-blocking, correctly scoped), plus the new `.gitleaksignore` line-fragility ADVISORY (owned by G5).

## Required rework

None. F1–F5 land the corrections cleanly; A3/A4/A5 are genuinely closed; A1/A2 are correctly retained as disclosed residuals.

## Reviewer conclusion

**PASS.** The correction round resolves the round-1 blocking driver (recorder cp1252 → byte-faithful UTF-8) correctly and closes my A3/A4/A5 with biting tests; A1 and A2 remain accurate, correctly-scoped, non-blocking residuals (A2 now confirmed live rather than merely argued). The recursive UUID mask hardens redaction at all nesting depths without perturbing dedup or ordering semantics. The owner-launched C1 fixture is masked, replayable, and honestly labelled, and it independently validates the A2 collision analysis and a real 2.1.247 seam-detection fact. Line counts (292/234/106/87/560), test count (38), ruff, modularity, and collection all reproduce clean at the re-frozen identity; the M0-T104 adapter and `readonly_agent_guard.py` are byte-untouched. Record G3 delta = PASS.
