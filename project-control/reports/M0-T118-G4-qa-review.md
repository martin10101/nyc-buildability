<!-- Saved VERBATIM by the orchestrator from the G4 qa-engineer agent-return channel
     (transport entity-decoding only). Review head d4a529d, material identity d1b05bb.
     Per the report's INFO-1 request, the orchestrator confirms at record time:
     HEAD == d4a529d at review dispatch; material identity commit d1b05bb; production
     files byte-identical between d1b05bb and the gate-record head. -->

Verification complete. Here is my G4 QA report.

---

# G4 QA GATE REPORT — M0-T118

**Task:** M0-T118 — "D-024 Amendment 13 unit R: bounded fixture recapture at installed Claude Code 2.1.251"
**Reviewer:** qa-engineer (independent, read-only)
**Review target:** frozen control-branch head `d4a529d` / material identity `d1b05bb`, files at `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24`
**Type:** governance (supervisor defect-only lane); in-regime (`directive_refs` D-024:ALL)

## Review method / limitation (stated up front)

The worktree-isolation guard refused a cross-directory git op against the shared `ctl24` checkout (verbatim: *"a worktree-isolated agent's git operations must target its own worktree"*). Per the task authorization, I verified by **direct file reads + pytest executed against the `ctl24` checkout** (non-git `cd ctl24 && python -m pytest` is permitted by the guard and ran normally). I therefore could **not** cryptographically confirm `HEAD == d4a529d` / identity `d1b05bb` via git; I verified the **content** of the changed files at `ctl24` and reproduced the full suite there. This is the same method established on prior supervisor gates. Environment: Python 3.11.9; `claude` and `codex` are installed on this sandbox.

## AS ↔ evidence mapping (independently reproduced)

| AS | Scenario | Concrete backing | Verdict |
|---|---|---|---|
| **AS-1** | catalog re-captured at 2.1.251; deterministic drift test matches `catalog_drift()`; S8 live tooth GREEN at 2.1.251, RED at any other version | `hook_event_catalog_2_1_251.json` (33 events, +2 = PreModelSwitch/PostModelSwitch). `test_s8_catalog_fixture_valid_and_masked` (task M0-T118, version 2.1.251, events==33), `test_s8_recorded_drift_matches_computed_drift` (asserts `catalog_drift(events, KNOWN_HOOK_EVENTS) == added=(PostModelSwitch,PreModelSwitch), removed=()` and `describe()`), live tooth `test_s8_live_version_matches_catalog_fixture` — all PASS in my run. Deterministic tooth proves removed==() ⇒ the fixture's 33 events are a strict superset of the 31-event baseline by exactly the +2. | GENUINE / met |
| **AS-2** | capability probe re-run live at 2.1.251; new fixture; no FAILED rows for depended-on capabilities | `capability_probe_live_2026-08-29_m0t118_2_1_251.json` (measured-live, claude 2.1.251, codex 0.146.0, all probes exit 0/supported; only `--init-only` = not-detected-in-help, not a dependency). Live tooth `test_live_reprobe_claude_version_matches_fixture` + `test_current_fixture_records_2_1_251_masked_and_shaped` PASS. `native_runtime_detection` background_gaps `[]`, host_ready True. | GENUINE / met |
| **AS-3** | interception + guardrail-shape fixtures re-pointed/re-measured with honest confidence labels; unproven stays unproven | `loop_interception_detection_2_1_251.json` (payload INHERITED with explicit `payload_lineage`; zero_context_proof + queued_input_behavior stay `pending-owner-C1`), `guardrail_refusal_shapes_2_1_251.json` (`verified_live=false`, `cli_version` UNCAPTURED). `test_the_installed_version_fixture_selects_the_measured_path`, S9/S11 honesty tests, and guardrail_bridge consumer PASS. | GENUINE / met |
| **AS-4** | recapture ran only after M0-T117 control (R279); `claude --version` identical before/after | Version stamps START 19:49:31Z / END 20:07:08Z both `2.1.251 (Claude Code)`; probe `generated_at` 19:52:55Z falls inside the window. I independently confirmed the installed CLI is stably `2.1.251 (Claude Code)`; DISABLE_AUTOUPDATER (M0-T117) structurally prevents mid-session drift. | met (see INFO-3) |

No acceptance scenario lacks genuine backing.

## Commands run and result lines (verbatim)

```
$ python --version
Python 3.11.9

$ python -m pytest tools/test_agent_supervisor_event_bus.py tools/test_agent_supervisor_capability_probe.py \
    tools/test_agent_supervisor_native_adapter.py tools/test_agent_supervisor_operator_channel.py -q
169 passed in 64.77s (0:01:04)        # 0 skipped ⇒ all CLI-gated live teeth RAN and passed

$ claude --version
2.1.251 (Claude Code)                  # == fixture-recorded string, exact

$ codex --version
codex-cli 0.146.0                      # == fixture-recorded string, exact

$ python -m pytest tools/test_agent_supervisor_*.py --collect-only -q
2726 tests collected in 9.74s          # == expected

$ python -m pytest tools/test_agent_supervisor_*.py -q
2724 passed, 2 skipped in 550.88s (0:09:10)   # == expected 2726 collected / 2724 passed / 2 skipped / 0 failed
```

The full-suite run is a primary independent whole-suite check (the orchestrator's earlier local run was interrupted). It completed cleanly at 2724 passed, 2 skipped, 0 failed.

## Item-by-item findings

**Item 2 (four fixture-consuming modules):** 169 passed, 0 failed — matches expected exactly.

**Item 3 (full suite):** 2724 passed, 2 skipped, 0 failed; 2726 collected — matches expected exactly. Count reconciliation: collection = 2726 confirmed; M0-T118 added 0 net test functions (grep confirms it only re-pointed constants and renamed/rewrote existing test functions; the 2_1_248 tags remaining in `.py` are historical comments only). The 2 skips are pre-existing platform/environment conditional skips (POSIX-only guards / admin-state / capability probes in `test_agent_supervisor_process.py`, `os_acl.py`, etc.), **not** the drift teeth — proven because `claude` is installed at 2.1.251 and the four-module run showed those teeth passing with 0 skips.

**Item 4 (red/green integrity — the crux):** The three live teeth each compare **live CLI output to the fixture-recorded constant string** (`installed == data["claude_version"]` / `first_line == current[...]["first_line"]` / `caps.claude_version == detection["claude_version"]`), **not** live-to-live. This is genuine and removal-sensitive: I confirmed the installed CLI is a real `2.1.251 (Claude Code)` and the fixtures store `2.1.251` as a constant, so the next unrecorded version bump makes `installed != fixture` ⇒ RED. **Not a tautology — no MAJOR finding.** The recorded RED block (`'2.1.251 (Claude Code)' == '2.1.248 (Claude Code)'`, 3 failed) is consistent with the pre-re-point state (teeth pointed at 2_1_248 fixtures, live 2.1.251); the three assertion messages in the RED evidence match the test source verbatim; the GREEN (3 passed) is reproduced live-equivalently in my runs.

**Item 5 (evidence integrity):** Version stamps (19:49:31Z / 20:07:08Z, both 2.1.251), probe `generated_at` (19:52:55Z, in-window), provenance labels (official-docs catalog; measured-live probe/detection; inherited interception; UNCAPTURED guardrail), and the counts (169 / 2724+2 / 2726) all agree between the producer report, the recapture-evidence report, and my independent runs. Masking verified by the passing `..._masked_and_shaped` / `Users`/`MLFLL` leak-guard tests.

**Item 6 (negative space):** Grep of `tools/` confirms every **active** pointer (event_drift, guardrail_refusal, and all four test modules) resolves to the 2_1_251 pack; no live pointer left on 2_1_248. The out-of-scope consumer `test_agent_supervisor_guardrail_bridge.py` reads only `unrecognized_similar_examples` (preserved) and asserts no version string, so the re-point doesn't break it (it passed). Historical fixtures (2.1.220/2.1.246/2.1.248, statusline captures) legitimately remain as append-only records, still pinned by `test_upgrade_pair_records_expected_versions`. No unintended-pin defect found.

**Modularity / supervisor-freeze:** Only two production files changed (`event_drift.py` 113 SLOC, `guardrail_refusal.py` 484 SLOC), each a single-constant pointer re-point plus comment updates — no new/oversized file, no responsibility mixing. Qualifying evidence D-024-R281 (AD-093 provider CLI drift) is cited in the packet; suite baseline (≥1165) far exceeded at 2724 passed.

### Numbered findings

1. **INFO-1** — Identity could not be git-confirmed (worktree guard); verified by direct reads + pytest at `ctl24` per task authorization. Recommend the orchestrator confirm `HEAD==d4a529d`/`d1b05bb` at record time.
2. **INFO-2** — `capability_probe_live_..._2_1_251.json` body carries `"task": "M0-T086"` (the probe module stamps its own origin task); the **consuming** task is encoded in the filename (`m0t118`), which `test_current_fixture_records_2_1_251_masked_and_shaped` asserts (G3 ADV-1 convention). Consistent with the m0t103/m0t092 precedents — not a defect.
3. **INFO-3** — AS-4's before/after stamps are self-reported in the markdown report (not machine-captured), and the "only after M0-T117" ordering is a ledger fact outside G4 execution. Both are structurally corroborated: DISABLE_AUTOUPDATER (M0-T117) blocks mid-session drift and I confirmed the installed CLI is stably 2.1.251.
4. **INFO-4** — Full D-024 requirement-by-requirement compliance is the `directive-compliance-verifier` gate (verification.json, producer ≠ verifier), not re-derived in this QA/G4 pass; my verdict covers the AS/test/red-green/evidence dimension.

No BLOCKER, MAJOR, or MINOR findings.

## Conclusion

Every acceptance scenario has genuine, reproduced backing. The drift teeth are legitimate live-vs-fixture-constant comparisons (removal-sensitive, would go RED on the next version change), the +2 event-set drift is deterministically pinned, unproven surfaces stay honestly unproven, no stale pointer remains, and my independent counts match exactly: four-module 169/0, full suite 2724 passed / 2 skipped / 0 failed / 2726 collected.

**G4 VERDICT: PASS**

---

Files that were load-bearing to this review (all absolute, at the `ctl24` checkout):
- `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24/project-control/tasks/M0-T118.json`
- `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24/project-control/reports/M0-T118-producer-report.md`
- `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24/project-control/reports/M0-T118-recapture-evidence.md`
- `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24/tools/agent_supervisor/event_drift.py`
- `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24/tools/agent_supervisor/guardrail_refusal.py`
- `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24/tools/agent_supervisor/fixtures/hook_event_catalog_2_1_251.json`
- `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24/tools/agent_supervisor/fixtures/loop_interception_detection_2_1_251.json`
- `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24/tools/agent_supervisor/fixtures/guardrail_refusal_shapes_2_1_251.json`
- `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24/tools/agent_supervisor/fixtures/capability_probe_live_2026-08-29_m0t118_2_1_251.json`
- `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24/tools/agent_supervisor/fixtures/native_runtime_detection_2026-08-29_m0t118.json`
- `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24/tools/test_agent_supervisor_event_bus.py`, `..._capability_probe.py`, `..._native_adapter.py`, `..._operator_channel.py`

Note: this report is returned via the agent channel for the orchestrator to save verbatim and record the gate (I did not run `project_control.py`/git/gh, per read-only reviewer discipline). Requested status for the task: **awaiting_gate** — G4 PASS, no blocking corrections.
