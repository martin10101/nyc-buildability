# M0-T118 recapture evidence — bounded fixture recapture at Claude Code 2.1.251

Task: M0-T118 (D-024 Amendment 13 unit R, R281). Producer: backend-engineer.
Worktree (verified `git rev-parse --show-toplevel`): `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t118`.
Method: bounded, no-write probes only (`--version` / `--help` / capability probe). No provider
session was started; no prompt was sent. CLI was neither downgraded nor updated. No
DISABLE_UPDATES anywhere. Only allowed_paths were touched.

## AS-4 — version stamps (identical before and after; no mid-capture drift)

| Stamp | `claude --version` (verbatim) | Timestamp (UTC) |
|---|---|---|
| START (before any capture) | `2.1.251 (Claude Code)` | 2026-08-29T19:49:31Z |
| END (after all captures + full suite) | `2.1.251 (Claude Code)` | 2026-08-29T20:07:08Z |

Both stamps read `2.1.251 (Claude Code)`; identical => no mid-capture drift (AS-4 satisfied).
codex re-probed live at `codex-cli 0.146.0` (unchanged from the 2.1.248 pack).

## Drift teeth — RED before re-point, GREEN after

Command (run from worktree root, both times):
`python -m pytest tools/test_agent_supervisor_event_bus.py::test_s8_live_version_matches_catalog_fixture tools/test_agent_supervisor_capability_probe.py::test_live_reprobe_claude_version_matches_fixture tools/test_agent_supervisor_native_adapter.py::test_live_detection_matches_committed_fixture -q`

### RED (before re-pointing — teeth still pointed at the 2_1_248 pack)

```
E       AssertionError: installed claude version drifted from the committed current fixture; re-run python -m tools.agent_supervisor.capability_probe and re-review
E       assert '2.1.251 (Claude Code)' == '2.1.248 (Claude Code)'
E         - 2.1.248 (Claude Code)
E         + 2.1.251 (Claude Code)
...
E       AssertionError: installed claude drifted from the committed detection fixture; re-run the unit-C detection capture and re-review
E       assert '2.1.251 (Claude Code)' == '2.1.248 (Claude Code)'
=========================== short test summary info ===========================
FAILED tools/test_agent_supervisor_event_bus.py::test_s8_live_version_matches_catalog_fixture
FAILED tools/test_agent_supervisor_capability_probe.py::test_live_reprobe_claude_version_matches_fixture
FAILED tools/test_agent_supervisor_native_adapter.py::test_live_detection_matches_committed_fixture
3 failed in 9.79s
```

All three assert installed `2.1.251` != committed `2.1.248` => teeth are genuinely
removal-sensitive (they bite on version drift).

### GREEN (after re-pointing consumers to the 2_1_251 pack)

```
...                                                                      [100%]
3 passed in 8.76s
```

Removal-sensitivity is preserved: each tooth still exact-matches installed `claude --version`
against its fixture's recorded `2.1.251` string, so it will go RED again on the NEXT installed
version drift without a re-capture. No tooth was weakened (the `==` exact-match comparisons are
unchanged; only the fixture pointers/recorded versions moved).

## Per-fixture provenance / method

1. **hook_event_catalog_2_1_251.json** — official-docs confidence. Provenance recorded verbatim
   in `source`: docs re-fetched 2026-08-29 by the orchestrator (code.claude.com/docs/en/hooks.md);
   producer recorded the delivered set. REAL +2 event-set drift vs the 31-event 2.1.248 catalog:
   **added PreModelSwitch and PostModelSwitch** (33 events total); no removals. `drift_vs_2_1_220`
   records added=`["PostModelSwitch","PreModelSwitch"]` (sorted, as `catalog_drift()` sorts),
   removed=`[]`. No per-event input fields were invented for the two added events (only the event
   NAME set was delivered). Live catalog tooth verified GREEN at 2.1.251.
2. **loop_interception_detection_2_1_251.json** — carried forward from the 2_1_248 structure.
   selected_event stays UserPromptSubmit. The measured payload is INHERITED (not re-measured; a
   `payload_lineage` block states this); event-set MEMBERSHIP of UserPromptSubmit/UserPromptExpansion
   was re-verified present in the 2.1.251 catalog. Every unproven surface stays
   pending-owner-C1/UNPROVEN — no label upgraded, no live measurement faked.
3. **guardrail_refusal_shapes_2_1_251.json** — base CLI updated to 2.1.251; recognized-shape corpus
   and confidence labels carried forward unchanged. The single recognized shape stays
   `verified_live=false`; `cli_version` reads "UNCAPTURED ... base CLI 2.1.251". No live refusal was
   captured (would require an owner-gated C1 canary + R595) — honestly UNCAPTURED at 2.1.251.
4. **capability_probe_live_2026-08-29_m0t118_2_1_251.json** — MEASURED LIVE by
   `python -m tools.agent_supervisor.capability_probe --out <path>` from the worktree root. Recorded
   claude_version first_line `2.1.251 (Claude Code)`, codex_version `codex-cli 0.146.0`. Binary paths
   masked `[HOME]`; no volatile data in the deterministic body.
5. **native_runtime_detection_2026-08-29_m0t118.json** — MEASURED LIVE via
   `native_runtime.detect_native_capabilities()` + `build_detection_fixture(task="M0-T118")` (bounded
   `--version`/`--help` probes only). claude_version `2.1.251 (Claude Code)`; every flag/verb
   classification identical to 2.1.248; background_gaps `[]`, background_host_ready True.

Leak scan (MLFLL / drive-rooted `\Users\` / `/Users/`) across all five new fixtures: **clean**.

## Self-check counts

- Four fixture-consuming modules (event_bus, capability_probe, native_adapter, operator_channel):
  `169 passed in 71.22s`, 0 failures.
- Full supervisor suite `python -m pytest tools/test_agent_supervisor_*.py -q`:
  `2724 passed, 2 skipped in 560.01s`, exit 0. Total collected 2726 (baseline; no new test
  functions were added — only existing assertions were updated and fixture pointers re-pointed).
  The 2 skips are pre-existing conditional skips, unchanged by this task.
