# M0-T105 G4 QA review — DELTA round 2 (VERBATIM reviewer return; transport entity-decoding only)

Saved by the orchestrator per the report-preservation rule. Reviewer: qa-engineer (same agent
resumed with round-1 context, 2026-08-27). Verdict returned: **PASS — no blocking corrections
remain**.

Orchestrator note on §5's advisory (recorded, not a report edit): the +5-vs-+6 question
reconciles exactly — the post-correction suite (2,685) ran BEFORE the C1 fixture tooth was
added (32→37 tests, +5), and the final confirmation run at the re-frozen identity, including
the tooth (38 tests), is **2,686 passed / 3 skipped / 0 failed** (651.1s). No
environment-conditional variance.

---

# GATE REPORT (DELTA / round 2) — M0-T105 (D-024 Amendment 3 unit D: native event integration)

**Gate:** G4 (independent QA), delta re-review of the consolidated correction round
**Reviewer:** qa-engineer (read-only; ADR-005)
**Frozen identity:** branch `control/D-024-fable-codex-loop`, live HEAD `9f816477c1c78d45599d54637ccedcc88f401d80`; deliverable commit `bfdf4ef5e4682d64a7e1c8f0a330b86fc04d1963`; content_manifest_sha256 `4bd0e18256d538b254a24a931b341c4b57b2851db15879dbcb4f86e336fe15d3`
**Round-1 verdict:** PASS with M1 (MEDIUM) blocking + L1/L2/L3 + A1/A2.

## VERDICT: PASS — no blocking corrections remain

All round-1 findings are closed with non-cosmetic fixes and regression-sensitive tests, independently reproduced at the new frozen identity. The pack grew 32→38 (all pass, S8 live tooth ran not-skipped). The new C1 live fixture, its tooth, and the `.gitleaksignore` audit are honest and sound. One minor, non-blocking numeric observation (freeze delta) is noted.

## 1. Reproduction

Exported the new frozen HEAD read-only: `git archive 9f816477… | tar -x -C <temp2>` (worktree still lagged). The three changed code files are byte-identical to the frozen blobs after CRLF-normalization — and my reverse-mutants were fully reverted:
- recorder sha256 `9042fa6d…` (frozen == restored)
- event_bus sha256 `4d961868…` (frozen == restored)
- test pack sha256 `f7ab960c…` (frozen == restored)

Correction round touched only in-scope files (`supervisor_event_recorder.py` M, `event_bus.py` M, test pack M, `hook_events_live_…_c1.json` A, `.gitleaksignore` A) + control-plane. `event_stream.py`, `event_drift.py`, the three round-1 fixtures, and both guard packs are **unchanged**; `.claude/settings.json` is **not** touched. Line counts: recorder 87, event_bus 292, test 560 — all production files ≪ 600 warn.

## 2. Commands + outputs

| Command | Result |
|---|---|
| `pytest tools/test_agent_supervisor_event_bus.py -v -rs` | **38 passed, 0 skipped** (S8 live drift tooth ran & passed — claude 2.1.247 present) |
| `ruff check` (recorder, event_bus, test) | **All checks passed!** |
| `gitleaks detect --no-git` on isolated C1 fixture | **9 findings, all `generic-api-key`, lines 17-25**, each an `idempotency_key` sha256 digest (entropy 3.7-3.9); no other findings |
| Grep leak-scan C1 fixture (MLFLL/paths/tokens/email/raw-UUID) | **No matches** (cleanly masked) |
| Reverse-mutant `decode-reverts-to-locale` | `test_s9_recorder_non_ascii_payload_fidelity` **FAILED** (event dropped, 0 records) — KILLED |
| Reverse-mutant `mask-not-recursive` | `test_s4_nested_uuid_masked_at_any_depth` **FAILED** (nested/keyed/list UUIDs survive raw) — KILLED |

## 3. Round-1 findings — closure verification

**M1 (MEDIUM, was blocking) — CLOSED.** Recorder now `sys.stdin.buffer.read(MAX_STDIN_BYTES+1)` (byte-level cap) + `.decode("utf-8-sig","replace")`. I re-ran my round-1 probe (f) against the corrected recorder:
- emoji payload → recorded; on-disk `agent_type` == the true `\U0001F680` string, `model` == `café`; raw store bytes are **strict-valid UTF-8** (no mojibake).
- accented `cwd` (`Ísafjörður`, whose UTF-8 hits a cp1252-undefined byte — the round-1 silent-drop case) → **recorded, not dropped**; value preserved AND `[HOME]`-sanitized.
New test `test_s9_recorder_non_ascii_payload_fidelity` asserts exactly this; the reverse-mutant (revert to locale `sys.stdin.read()`) is caught (drops to 0 records). Non-cosmetic, regression-guarded.

**L2 (LOW) — CLOSED.** `_mask_if_uuid` → recursive `_mask_uuids` over strings, list/tuple items, and dict values **and keys**. Re-ran my round-1 probe (g): UUID nested in a dict value, used as a dict key, and inside a list — plus top-level `session_id`/`cwd` — all masked; **raw UUID absent from disk** (6× `[SESSION sha256=]`). idempotency key is computed pre-mask, so dedup is unaffected. New test `test_s4_nested_uuid_masked_at_any_depth` + reverse-mutant (shallow) killed.

**L1 (LOW) — CLOSED.** Dedup-window degradation disclosed inline at the recorder's `warm_rotated=False` (lines 72-76: re-record after a rotation boundary is the safe direction, surfaced by `store_duplicates`) and in report §3a (F3).

**L3 (LOW) — CLOSED.** S5 scenario text corrected (report line 39): "append-mode write + read-side torn-line skip-and-count; temp-rename atomicity is the SIDECAR path." Accurate now (F4).

**A2 (ADVISORY) — CLOSED.** New `test_s10_registry_bounded_at_bus_level` proves the bound through the bus itself (5 distinct `agent_id`, `registry_max_entries=2` → `len(bus.registry) ≤ 2`). Verified non-vacuous: distinct keys, `_evict` popitem-fallback bounds even all-active entries; bound is wired via `DurableEventBus(registry_max_entries=…)`.

**A1 (ADVISORY) — adequately addressed by disclosure.** "Never delays" remains design-asserted; the recorder now documents the bounded-per-invocation-latency rationale (`fsync=False`, `warm_rotated=False`). Acceptable.

Also new (F5): `test_s9_recorder_oversized_stdin_fails_closed` (1.1 MB stdin → nothing recorded) and `test_s3_stream_key_content_digest_fallback` (no-id events dedup by content digest) — both substantive.

## 4. NEW artifacts review

**C1 live fixture (`hook_events_live_2026-08-27_m0t105_c1.json`) — HONEST & masked.** Owner-launched 2.1.247 capture; 9 records / 8 event types (incl. SessionStart, SubagentStart/Stop, PostToolBatch, Stop×2, SessionEnd). Independent leak-scan clean (no username/paths/tokens/email/raw-UUID). `session_id` digest-masked (`[SESSION sha256=…]`), `cwd` `[HOME]`-masked, prompts withheld as digests. Honest measured facts: an Agent-tool spawn fires SubagentStart/Stop but **not** TaskCreated/TaskCompleted on 2.1.247; a SessionEnd from a different scratch-dir session carries a different digest (recorded, not guessed). The tooth `test_c1_live_fixture_masked_and_replayable` freezes these, parses all 9 as `TelemetryRecord`, and asserts the live cross-process `bus_sequence` collision (`sequences.count(3)==2`). This lands squarely in my round-1 probe (b) territory — I reproduced the same collision independently (two concurrent bus instances stamp overlapping sequences). It is an **inherent, safe, and now-disclosed** property (report §3a: total order not guaranteed under concurrent writers; append order preserved; distinct dedup keys; surfaced via `store_duplicates`), not a defect.

**`.gitleaksignore` audit — SOUND.** gitleaks flags exactly 9 `generic-api-key` findings on the fixture, on lines 17-25 — each the `idempotency_key` 64-hex value, which is a sha256 content digest of already-sanitized event identity, not a credential. The 9 committed fingerprints match these precisely; the scope is file+rule+line (cannot mask a secret elsewhere), and there are no other findings. The fixture leak-scan is independently clean, so nothing real is suppressed. (Even a fingerprint-format mismatch would fail *closed* — block the commit — not leak.)

## 5. Regression / no-regression

No accepted production file outside M0-T105's own new set was modified; guards byte-untouched; settings.json untouched. Pack 38/38 green; reused base already verified round-1. Freeze suite `2,685/3/0` is producer-captured and structurally regression-safe (in-scope-only change).

**Minor observation (ADVISORY, non-blocking):** the freeze passed-count grew +5 (2680→2685) while the pack grew +6 tests; I could not independently reproduce the full-suite count (the temp export is not a git repo and several packs shell out to git). The most likely cause is one environment-conditional test differing between the producer's two separate full-suite runs. It does not affect this gate; recommend the orchestrator confirm the exact number via CI.

## 6. Directive-observable (formal pass = DCV)
- **R154** — `event_stream.py` unchanged; passive parsing, no sidecar surface. Satisfied.
- **R155** — recorder still external-state-only, fail-closed, silent; guards/settings untouched; freeze preserved. Satisfied (and now honest for non-ASCII input).
- **R173** — unknown (`known:false`/`known_type:false`) + drift tooth unchanged; C1 adds a measured 2.1.247 catalog-behavior fact (Agent≠TaskCreated). Satisfied.

---

## VERDICT: PASS — no blocking corrections.

Round-1 M1 (MEDIUM) is genuinely closed (independently reproduced: emoji + accented-path now recorded with UTF-8 fidelity, previously mojibake/dropped); L1/L2/L3/A2 closed with non-cosmetic, regression-sensitive fixes (both reverse-mutants killed); the C1 fixture, tooth, and `.gitleaksignore` audit are honest and sound. 38/38 pack, ruff clean, content identity byte-verified, guards untouched. Recommend acceptance.

Advisory (optional, non-blocking): the +5-vs-+6 freeze-count note in §5 — confirm the exact figure via CI.

Report-relevant absolute paths (frozen content I reviewed, temp export):
- `…\scratchpad\M0-T105-delta\.claude\hooks\supervisor_event_recorder.py` (F1/M1)
- `…\scratchpad\M0-T105-delta\tools\agent_supervisor\event_bus.py` (F2/L2)
- `…\scratchpad\M0-T105-delta\tools\test_agent_supervisor_event_bus.py` (6 new tests)
- `…\scratchpad\M0-T105-delta\tools\agent_supervisor\fixtures\hook_events_live_2026-08-27_m0t105_c1.json` (C1)
- `…\scratchpad\M0-T105-delta\.gitleaksignore`
- Canonical repo paths at frozen HEAD `9f816477`: same files under `.claude/hooks/`, `tools/agent_supervisor/`, `tools/`, repo root.

Note to orchestrator: I am read-only — I did not run `project_control.py`/git/gh mutations (git archive/show/diff are reads). Please record this G4 delta gate result verbatim. Temp artifacts live under the session scratchpad and can be discarded.
