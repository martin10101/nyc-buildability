<!-- Saved VERBATIM by the orchestrator from the G3 code-reviewer agent-return channel
     (transport entity-decoding only). Review head d4a529d, material identity d1b05bb. -->

I have completed all verification steps. Every check reproduces cleanly against the frozen head. Here is my complete G3 gate report.

---

# G3 Gate Report — M0-T118 (D-024 Amendment 13 unit R: bounded fixture recapture at Claude Code 2.1.251)

**Reviewer:** independent read-only code-reviewer (G3)
**Reviewed identity:** control head `d4a529d`, material identity commit `d1b05bb` (byte-identical fixture/test/source delta), branch `control/D-024-fable-codex-loop`
**Checkout:** `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24`
**Packet:** `project-control/tasks/M0-T118.json` (AS-1..AS-4; gates G0/G2/G3/G4/G5)
**Environment:** Python 3.11.9; `claude` on PATH reporting `2.1.251 (Claude Code)` — so the three live drift teeth genuinely EXECUTED (not skipped) against the installed CLI.

## Verdict summary

All four review areas PASS. Two non-blocking observations (1 MINOR doc nit, 1 INFO). No BLOCKER, no MAJOR. The core risk of this unit — a silently weakened drift tooth — is not present: every tooth still exact-matches (`==`) and each was reproduced RED-at-drift / GREEN-at-2.1.251.

---

## 1. Drift-teeth integrity — PASS

**The three live teeth all use exact `==`, no loosening, no swallowing, no added skip:**

- `test_agent_supervisor_event_bus.py:354` — `assert installed == data["claude_version"]` where `installed = claude --version` (subprocess, resolved binary, no shell). Guard `@requires_claude` (line 343) is the pre-existing feature-detection skip (skips only when `claude` absent) — not newly added.
- `test_agent_supervisor_capability_probe.py:191` — `assert rec["first_line"] == current["body"]["probes"]["claude_version"]["first_line"]`. Pre-existing skipif at line 186.
- `test_agent_supervisor_native_adapter.py:727` — `assert caps.claude_version == detection["claude_version"]`. Pre-existing `@requires_claude` at line 722.

No `startswith`/`in`/`contains`/regex/`try/except`/`pytest.skip` was introduced in any of the three. Reproduced GREEN against the live 2.1.251 CLI:

```
python -m pytest tools/test_agent_supervisor_event_bus.py::test_s8_live_version_matches_catalog_fixture \
  tools/test_agent_supervisor_event_bus.py::test_s8_recorded_drift_matches_computed_drift \
  tools/test_agent_supervisor_capability_probe.py::test_live_reprobe_claude_version_matches_fixture \
  tools/test_agent_supervisor_native_adapter.py::test_live_detection_matches_committed_fixture -v
  → 4 passed in 8.24s (all PASSED, none skipped)
```

**Removal-sensitivity confirmed** (would go RED on the NEXT version). Read-only simulation reproduced:
- `'2.1.252 (Claude Code)' == '2.1.251 (Claude Code)' → False (RED)`; `'2.1.250 …' → False (RED)`. The producer also documented the pre-repoint RED verbatim in `M0-T118-recapture-evidence.md:26-38` (3 failed: `'2.1.251' != '2.1.248'`).

**Deterministic drift test** (`test_s8_recorded_drift_matches_computed_drift`, event_bus:307-318): asserts `catalog_drift(data["events"], KNOWN_HOOK_EVENTS)` equals the recorded reconciliation AND the exact real +2 delta: `drift.added == ("PostModelSwitch","PreModelSwitch")`, `drift.removed == ()`, `drift.has_drift`, `describe() == "added: PostModelSwitch, PreModelSwitch"`. Independently recomputed: `added=('PostModelSwitch','PreModelSwitch')`, `removed=()` — matches. A hypothetical event drop reproduces `removed=('SessionEnd',)`, which would fail the recorded-drift assertion (bite confirmed).

**KNOWN_HOOK_EVENTS NOT widened:** `telemetry_hooks.py` is absent from commit `d1b05bb` (13-file delta); `KNOWN_HOOK_EVENTS` measured at **31** events (telemetry_hooks.py:29-38), fixture events at **33**. The +2 is recorded as a reconciled fact, not absorbed into the baseline (as the fixture note at `hook_event_catalog_2_1_251.json:63` states and the code confirms).

## 2. Fixture honesty — PASS

Compared each new `*_2_1_251` fixture to its `2_1_248` predecessor (`git diff --no-index`):

- **hook_event_catalog_2_1_251.json** — `confidence: official-docs`; 33 events = the 31-event 2.1.248 set + exactly `PreModelSwitch`/`PostModelSwitch` (lines 38-39), none removed. Honest; per-event payload fields for the two additions explicitly NOT invented (`field_note`, line 54).
- **loop_interception_detection_2_1_251.json** — payload is **inherited**; new `payload_lineage` block (lines 7-10) explicitly states the measurement was NOT re-run at 2.1.251, only event-set membership re-verified. `zero_context_proof` stays `pending-owner-C1` (line 25); `queued_input_behavior` stays `pending-owner-C1` (line 30). No confidence label upgraded — this fixture is MORE honest than its predecessor.
- **guardrail_refusal_shapes_2_1_251.json** — `confidence: documented` unchanged; the one recognized shape stays `verified_live: false` (line 22); `cli_version` stays `"UNCAPTURED …"` (line 23). `recapture_lineage` (line 9) states corpus carried forward unchanged, no live refusal captured. Honest.
- **capability_probe_live_2026-08-29_m0t118_2_1_251.json** — **measured live**: `generated_at` moved to `2026-08-29T19:52:55+00:00`; `claude_version` sha changed vs predecessor (`40fd7dca…`→`1aaadbe0…`) and `claude_help` sha changed, while `codex_version`/`codex_help`/`codex_exec_help` shas are byte-identical (codex unchanged at 0.146.0) — the signature of a genuine re-probe, not a hand-edit. Paths masked `[HOME]`.
- **native_runtime_detection_2026-08-29_m0t118.json** — **measured live**: `claude_version: 2.1.251`; flag/verb classification identical to 2.1.248; `background_gaps: []`.

No fixture entry was upgraded to a stronger confidence without a new measurement.

## 3. Pointer completeness — PASS

- Module pointers re-pointed: `event_drift.py` `CATALOG_FIXTURE_PATH` → `hook_event_catalog_2_1_251.json`; `guardrail_refusal.py` `SHAPES_FIXTURE_PATH` → `guardrail_refusal_shapes_2_1_251.json`.
- All four test files re-pointed to the new fixtures.
- Grep of `tools/**/*.py` for every old fixture name (`_2_1_248`, `native_runtime_detection_2026-08-27…`, `capability_probe_live_2026-08-27_m0t092…`): **no matches** — zero stale code/test consumers.
- `.claude/hooks/loop_command_interceptor.py` uses glob `loop_interception_detection_*.json` (line 71) and selects newest-first via `for path in reversed(sorted(fixtures))` (lines 170-172); `_2_1_251` sorts after `_2_1_248`, so the new fixture is chosen and returns `selected_event = UserPromptSubmit`. Verified read-only; correctly requires no hook edit.
- Remaining `_2_1_248` references are (a) the append-only history fixtures themselves and (b) `project-control/` historical records for M0-T092/T093/T094/T110 — correctly out of scope.

## 4. Scope + provenance — PASS

- Material commit `d1b05bb` touches exactly **13 files, all within `allowed_paths`**; control commit `d4a529d` adds only `project-control/` bookkeeping (gates/reports/state/task).
- **Append-only confirmed:** no `*_2_1_248` fixture is in the delta; predecessors untouched.
- **Provenance recorded:** `hook_event_catalog_2_1_251.json:8` cites `code.claude.com/docs/en/hooks.md`, re-fetched 2026-08-29 by the orchestrator.
- **AS-4 version stamps identical:** `M0-T118-recapture-evidence.md:13-14` — START `2.1.251` @19:49:31Z, END `2.1.251` @20:07:08Z (no mid-capture drift).
- **Modularity:** `python tools/modularity_check.py --check` → `failures 0`; neither touched module (`event_drift.py`, `guardrail_refusal.py`) appears in the 9 warnings (all pre-existing, untouched files). Changes to production source are pointer + comment edits only.
- **Supervisor-freeze duty:** qualifying evidence `D-024-R281 (AD-093 provider CLI drift)` cited in both the packet and the commit message.

## 5. Tests — PASS (reproduced)

```
python -m pytest tools/test_agent_supervisor_event_bus.py \
  tools/test_agent_supervisor_capability_probe.py \
  tools/test_agent_supervisor_native_adapter.py \
  tools/test_agent_supervisor_operator_channel.py -q
  → 169 passed in 63.30s
```

Exactly the expected 169 passed, 0 failed. Live teeth executed (Section 1). Nothing failing.

---

## Findings

1. **[MINOR] Stale docstring version reference** — `tools/test_agent_supervisor_native_adapter.py:724-725`: the `test_live_detection_matches_committed_fixture` docstring still reads "the live surface still matches the committed **2.1.247** record". The test correctly targets the re-pointed 2.1.251 fixture and passes; this is a documentation-only inaccuracy with no behavioral impact. Non-blocking.
2. **[INFO] capability-probe `body.task` = "M0-T086"** — `capability_probe_live_2026-08-29_m0t118_2_1_251.json:72` carries the probe-schema origin task, consistent with its predecessor's convention; the consuming-task id is carried in the filename, which `test_current_fixture_records_2_1_251_masked_and_shaped` asserts (`"m0t118" in CURRENT_FIXTURE.name`). Not a defect.

All AS-1..AS-4 independently reproduced. The three live drift teeth exact-match and execute GREEN against the installed 2.1.251; the deterministic drift test bites on the real +2 delta with `KNOWN_HOOK_EVENTS` unwidened; every fixture confidence label is truthful; pointers are complete; the delta is scope-confined and append-only.

**G3 VERDICT: PASS**
