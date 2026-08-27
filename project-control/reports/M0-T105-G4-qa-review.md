# M0-T105 G4 QA review — round 1 (VERBATIM reviewer return; transport entity-decoding only)

Saved by the orchestrator per the report-preservation rule. Reviewer: qa-engineer (independent,
read-only, dispatched 2026-08-27). Verdict returned: **PASS — with 1 MEDIUM required correction
BLOCKING acceptance (+ LOW/ADVISORY items)**.

---

# GATE REPORT — M0-T105 (D-024 Amendment 3 unit D: native event integration)

**Gate:** G4 (independent QA)
**Reviewer:** qa-engineer (read-only; ADR-005)
**Task:** M0-T105 — durable hook-event bus + stream-JSON ingestion + catalog drift + command-hook recorder
**Frozen identity reviewed:** branch `control/D-024-fable-codex-loop`, live HEAD `70b38f87d5ded0988c84022b463d98ca35db1471`; deliverable commit `50abb346fc8637a374b1e5bae056d19d2792a827`; checkpoint content_manifest_sha256 `5f32cf98…4e812b17`
**Applicable requirements (QA-observable):** D-024-R154, D-024-R155, D-024-R173

## VERDICT: PASS — with 1 MEDIUM required correction BLOCKING acceptance (+ LOW/ADVISORY items)

The deterministic core is genuinely strong: all 32 scenario tests pass (including the S8 live drift tooth, which actually *ran* — not skipped — on my runner because claude 2.1.247 is installed), the reused telemetry base and both guard self-runners are green, the deliverable adds only new files (no accepted source modified, guards byte-untouched, settings.json unregistered), content identity is byte-verified against the frozen blobs, mutation kills reproduce, ruff is clean, and the fixtures/report numbers are honest. One real defect (the recorder's cp1252 stdin decoding on Windows) must be corrected before acceptance; the remainder are disclosure/precision advisories.

---

## 1. Reproduction environment

- Reviewer worktree HEAD was `d8b3899` (stale — lagged the pinned SHA; deliverable files absent). Exported the frozen tree read-only: `git archive 70b38f87… | tar -x -C <temp>` (no repo mutation, no checkout). Verified `event_bus.py` and `supervisor_event_recorder.py` are byte-identical to `git show 70b38f87:<path>` after CRLF normalization (sha256 `4c53e6cd…` and `66012ac2…` respectively).
- Python 3.11.9 (== producer's), pytest 8.4.2, ruff 0.13.0 (CI version), claude `2.1.247 (Claude Code)` present; child `sys.stdin.encoding=cp1252`, PYTHONUTF8/PYTHONIOENCODING unset.

## 2. Commands run (independent) + outputs

| Command | Result |
|---|---|
| `pytest tools/test_agent_supervisor_event_bus.py -q` | **32 passed** in 1.34s (verbose: S8 live tooth `test_s8_live_version_matches_catalog_fixture` **PASSED**, not skipped) |
| `pytest tools/test_agent_supervisor_telemetry_core.py tools/test_agent_supervisor_subagent_telemetry.py -q` | **98 passed** (reused base intact) |
| `python tools/test_readonly_agent_guard.py` | **ALL CHECKS PASSED** |
| `python tools/test_agent_dispatch_guard.py` | **ALL CHECKS PASSED** (corroborates "guard packs x2") |
| `ruff check` (5 new files) | **All checks passed!** |
| `git diff --name-status 50abb34~1 70b38f87` | production/test/fixture/recorder files all **A**dded; only `state.json`, `tasks/M0-T105.json`, `event-integration.md` **M**odified (control-plane) |
| `wc -l` new files | bus **284**, stream **234**, drift **106**, recorder **77**, test **463** — all match report exactly |
| `modularity_check.py --check` | Not reproducible in temp export (`git ls-files` exit 128 — non-git dir). Underlying claim verified by inspection: all new files ≤284 lines ≪ 600 warn; each single-responsibility. |

Full 2,680-test freeze suite: NOT independently re-run (temp export is not a git repo; several existing packs shell out to git and would spuriously fail — unrelated to M0-T105). Regression risk is structurally near-zero because the deliverable **modifies no existing file** (name-status above); my representative slice (32 + 98 + 2 guard packs) is fully green. CI runs the full suite on push.

## 3. Scenario-to-test traceability (S1–S11)

Each scenario has a direct test exercising its Given/When/Then (not a weaker proxy). Partials flagged per the QA brief:

| ID | Coverage | Verdict |
|---|---|---|
| S1 firing-order | `test_s1_firing_order_preserved` (order + monotonic unique bus_sequence + one typed record) + `test_s1_every_required_event_ingests_one_record` (17/17, known=True) | FULL |
| S2 dedup | duplicate→1 record/no-op; distinct payload→distinct; key deterministic | FULL (bounded-window caveat — Finding L1) |
| S3 stream-JSON | typed records (6 lines→5, 1 dedup); R042 labels + absent→unknown; R043 caveat; text=digest-only; typed errors; **no sidecar surface (R154)** | FULL |
| S4 redaction | `[HOME]`/prompt/secret/raw-UUID all masked; mask stable | COVERED for top-level scalars; **nested-in-list UUID survives — Finding L2** |
| S5 atomic persistence | `test_s5_torn_final_line_never_a_record` proves the observable Then (no partial record visible, `skipped_lines=1`) | Observable property COVERED; the append is `"ab"` + read-side torn-line skip, **not** temp-rename as the scenario text says — Finding L3 |
| S6 restart-safe replay | reconstruct==pre-restart, registry equal, `store_duplicates=0`, re-delivery after restart=no-op, sequence continues; replay is pure read (file size invariant) | FULL |
| S7 unknown-event | `known:false`, name preserved, never dropped/crashed | FULL |
| S8 version-drift | fixture schema+mask; **recorded drift == computed `catalog_drift()`** (KNOWN_HOOK_EVENTS 31 == fixture 31, no drift); broken fixture refused; **live tooth ran & passed** here | FULL (version-string-only tooth — disclosed by producer) |
| S9 blocking semantics | exit 0 + stdout=="" (no decision/context/message); fail-closed; never guesses event name | COVERED; **"never delays" is design-asserted, not timing-tested — ADVISORY A1**; **cp1252 non-ASCII path untested — Finding M1** |
| S10 bounded store | seen-keys bounded (≤8); disk rotation bounded ({.jsonl,.1,.2}); broken bounds rejected; failed-append republishable + sequence rollback | Store + seen-keys FULL; **registry bounding only via reused pack, no dedicated in-pack test — ADVISORY A2** |
| S11 hook-script security | command-hook-not-HTTP (code-only scan), stdin payload, no settings.json/tokens/permissionDecision/additionalContext; fixtures masked; guards untouched | FULL |
| C1 live canary | Owner-gated (R192/R197); correctly NOT exercised, prepared only | N/A (non-blocking) |

## 4. Adversarial probes (read-only, ad hoc)

- **(a) dedup after rotation eviction** — with tight bounds, the original record's generation rotated out; on restart its key is no longer on disk and a re-delivery is **recorded again**. Dedup degrades gracefully (safe: a duplicate record, never data loss; surfaced later via `store_duplicates`), but the S2/S6 "exactly one" claims read as absolute → see L1.
- **(b) two buses racing one store** — both write; `replay_store` reports `store_duplicates=1`. The `ReplayResult.store_duplicates` claim holds (surfaced, never silently collapsed). PASS.
- **(c) non-dict payload** — list/str/None/int all recorded with `payload_error`, no crash; repeated non-dict deduped. Robust. PASS.
- **(d) usage booleans/negatives** — `input_tokens=True`→unknown, `output_tokens=-5`→unknown, `total_tokens=False`→unknown, `cache_read=3.5`→3.5. `_count` correctly rejects bool/negative/non-numeric (R042 "unknown, never zero"). PASS.
- **(e) recorder empty stdin** — exit 0, stdout empty, no store file (fail-closed). PASS.
- **(f) unicode/emoji through the recorder (cp1252 hazard)** — **DEFECT (M1).** The recorder's `sys.stdin.read()` uses the Windows locale (cp1252), not UTF-8. A UTF-8 emoji payload is stored as **mojibake** (`has_rocket:false`; disk bytes are the double-encoded form — my console showed the emoji only as a cp1252↔utf-8 round-trip display artifact). A payload containing a common accented char whose UTF-8 hits a cp1252-undefined byte (e.g. `Í` = `C3 8D`, or a `cwd` like `C:\...\Ísafjörður`) raises `UnicodeDecodeError` → caught → **event silently dropped** (no store file). Confirmed via subprocess against the frozen recorder.
- **(g) UUID nested in a LIST attribute** — top-level `session_id` masked, but `agent_id=[UUID,"other"]` leaves the **raw UUID on disk**. Bus masking is top-level-only; the docstring's "raw session/task UUIDs never reach the durable store" is absolute → see L2.

## 5. Mutation-proof re-check (2 of 9, actually applied to temp copies)

- **uuid-mask-identity** — made `_mask_if_uuid` return unchanged → `test_s4_durable_record_sanitized` **FAILED** (`SESSION_UUID` present). Killed. ✔
- **recorder-prints-to-stdout** — made recorder print JSON → `test_s9_recorder_records_and_stays_silent` **FAILED** (`stdout != ""`). Killed. ✔
Both restored; final clean run = 32 passed; content sha256 re-verified identical to frozen blobs. The remaining 7 named mutants each map to a discriminating assertion (plausible).

## 6. Fixture honesty

- `hook_event_payloads_v1.json`: 17 pack events; **only UserPromptSubmit labelled `measured-live`** and its cited source (`statusline_live_2026-08-27_2_1_247_r162_discharge.json` → `round2_2_1_247.hook_userpromptsubmit_full_prompt`) is present in-tree — substantiated. Others honestly `official-docs`/`documented-common-fields`. No invented fields presented as measured.
- `hook_event_catalog_2_1_247.json`: 31 events == `KNOWN_HOOK_EVENTS` (31) exactly → recorded `drift added:[] removed:[]` matches `catalog_drift()` (test asserts). Confidence honestly `official-docs`; masked (no `Users`/`MLFLL`).
- `stream_json_subagent_events_v1.json`: `session-evidence` confidence, honest source note; includes dedup-dup, usage-absent, and unknown-type lines.

## 7. Report / G2 self-check accuracy

Cross-checked and reproducible: 32/32 pack; line counts 284/234/106/77/463 exact; ruff 0.13.0 clean; new-files-only; guards byte-untouched; validator standalone excluded (control-plane). No numeric errors found (unlike the M0-T104 typo precedent). The 2,680/3-skip freeze figure is producer-captured (not independently reproducible in the temp export, see §2) but structurally consistent with new-files-only.

## 8. Directive-observable notes (formal pass belongs to the DCV)

- **R154** (structured stream consumed outside Fable; statusLine sidecar stays primary): S3 confirms passive parsing, no model call, `TelemetrySidecar` absent from `event_stream.py`. Observed satisfied.
- **R155** (hooks write external state only; supervisor-freeze): recorder/bus never block/inject/message; S9/S11 confirm; freeze baseline preserved (no existing file modified). Observed satisfied.
- **R173** (unknown + version-drift honesty): S7 (`known:false`), S3 (`known_type:false`), S8 (drift tooth + fixture↔code reconciliation). Observed satisfied.

## 9. Skip hygiene

The only live row (`test_s8_live_version_matches_catalog_fixture`) is gated by `pytest.mark.skipif(shutil.which("claude") is None)` — skips cleanly when claude is absent; ran and passed when present. S9 recorder tests use `sys.executable` (always present) — correctly not claude-gated.

---

## FINDINGS

**M1 — MEDIUM (blocking): recorder corrupts/drops non-ASCII hook payloads on Windows (cp1252 stdin).**
`supervisor_event_recorder.py` reads `sys.stdin.read()` with the OS locale encoding (cp1252 on the owner's win32 box), but Claude Code emits hook payloads as UTF-8. Result: non-ASCII content in whitelisted fields (`cwd` tail, `agent_type`, `model`, `tool_name`, …) is either stored as mojibake or, when a UTF-8 byte is undefined in cp1252 (e.g. `Í`), triggers `UnicodeDecodeError` → the event is **silently dropped** (fail-closed exit 0). This violates the recorder's own "honestly record" guarantee and the codebase's otherwise-consistent UTF-8 discipline (`encode("utf-8","replace")` in the bus/journal; `utf-8-sig` reads), and directly contradicts the documented M0-T104 UTF-8-vs-cp1252 lesson. Untested — S9 uses ASCII-only payloads.
*Mitigating:* recorder is unregistered (dormant until the separate settings.json wiring), the store is gitignored runtime state (no repo leak), and failure is fail-closed (no crash/session break) — hence MEDIUM not HIGH.
**Required correction:** read stdin as UTF-8 explicitly — e.g. `raw = sys.stdin.buffer.read(MAX_STDIN_BYTES + 1).decode("utf-8", "replace")` (apply the byte cap to bytes), or `sys.stdin.reconfigure(encoding="utf-8", errors="replace")` before reading — and add an S9 regression test with a non-ASCII payload (emoji + accented `cwd`) asserting the record is stored with fidelity.

**L1 — LOW: bounded dedup window not disclosed.** Dedup is guaranteed only within (a) the in-memory `max_seen_keys` window and (b) journal retention (`max_bytes × max_generations`); the recorder additionally uses `warm_rotated=False`, narrowing cross-invocation dedup to the current generation. Once a record rotates out, a re-delivery is recorded again (probe a). Behavior is safe and surfaced via `store_duplicates`, but S2/S6 read as absolute. *Suggested:* one sentence in Known Limitations stating dedup is exact within retention and degrades to a surfaced duplicate beyond it.

**L2 — LOW: UUID masking is top-level only.** `event_bus.py` docstring says raw session/task UUIDs "never reach the durable store," but `_mask_if_uuid` only masks top-level string attribute values + `session_id`/`task_id`; a UUID nested in a list/dict attribute value survives (probe g). Narrow reachability (a whitelisted field delivered as a non-scalar) and non-committed store. *Suggested:* soften the docstring to "top-level identity values," or recurse the mask.

**L3 — LOW: S5 scenario wording imprecise.** The JSONL `append` is append-mode (`"ab"`) with read-side torn-line skipping, not the "atomic temp-rename" the S5 scenario/report text implies (temp-rename is the sidecar path). The observable Then is proven; only the description is inaccurate.

**A1 — ADVISORY:** S9's "never delays the hook" is design-asserted (`fsync=False`, `warm_rotated=False`, bounded stdin), not timing-measured. Acceptable; note it.

**A2 — ADVISORY:** S10's registry bound (`SubagentRegistry(max_entries=512)`) is verified via the reused telemetry packs, not a dedicated in-pack test. Consider one bus-level registry-eviction assertion.

---

## Corrections required before acceptance
1. **[MEDIUM, BLOCKING]** Fix M1 — UTF-8 stdin decode in the recorder + non-ASCII regression test.
2. **[LOW, non-blocking]** Address L1/L2/L3 (disclosure + docstring precision) at the producer's discretion; A1/A2 optional.

**VERDICT: PASS with required correction M1 blocking acceptance.** Recommend a short correction round (one-line stdin fix + one test; the L/A items are documentation touch-ups) followed by a delta re-review of the recorder + S9, consistent with the M0-T104 accept-after-correction-round precedent.

---

Report-relevant absolute paths (frozen content, temp export I reviewed):
- `C:\Users\MLFLL\AppData\Local\Temp\claude\C--Users-MLFLL-Downloads-nyc-zoning-ctl24\222b52b0-fd56-47cf-87cb-d17c0a4220dd\scratchpad\M0-T105-review\.claude\hooks\supervisor_event_recorder.py` (M1 subject)
- `…\M0-T105-review\tools\agent_supervisor\event_bus.py` (L1/L2 subject)
- `…\M0-T105-review\tools\agent_supervisor\event_stream.py`, `event_drift.py`
- `…\M0-T105-review\tools\test_agent_supervisor_event_bus.py`
- Canonical (repo) paths at frozen HEAD: `tools/agent_supervisor/event_bus.py`, `event_stream.py`, `event_drift.py`, `.claude/hooks/supervisor_event_recorder.py`, `tools/agent_supervisor/fixtures/{hook_event_catalog_2_1_247,hook_event_payloads_v1,stream_json_subagent_events_v1}.json`, `tools/test_agent_supervisor_event_bus.py`, `project-control/reports/M0-T105-event-integration.md`, `project-control/reports/M0-T105-G2-self-check.md`

Note to orchestrator: I am read-only — I did not run `project_control.py`/git/gh. Please record this G4 gate result verbatim. Temp artifacts (export tree, probe scripts) live under the session scratchpad and can be discarded.
