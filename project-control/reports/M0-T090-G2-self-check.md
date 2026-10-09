# M0-T090 — G2 self-check (producer: orchestrator)

**Frozen content commit:** `e8b21d1` (5 modules + 53-test pack + report). 2026-08-26 UTC.

## 1. Deliverables present (packet outputs)

- assignment + supervision-envelope schemas and structural classifier under `tools/agent_supervisor` — `subagent_contracts.py`, `workload_classifier.py` (+ `spawn_decision.py`, decision layer);
- startup-overhead measurement + graph-based sizing/packet integration — `startup_overhead.py`, `workload_sizing.py`;
- `tools/test_agent_supervisor_bounded_contracts.py` — 53 tests incl. the s16.2 sizing cases and the no-quota-in-worker-prompt proof;
- `project-control/reports/M0-T090-bounded-contracts.md`.

## 2. Executable checks (foreground, at the frozen tree)

| Check | Result |
|---|---|
| `pytest tools/test_agent_supervisor_bounded_contracts.py -q` | **53 passed / 0 failed** |
| Adjacent supervisor packs (statusline, telemetry core, subagent telemetry, rotation, scheduler) | **290 passed / 0 failed** |
| **Full composite `tools/` suite (supervisor-freeze baseline duty)** | **2653 passed / 3 skipped / 0 failed** — chunk 1 `pytest tools/ --ignore=tools/test_directive_compliance.py` → 2533/3/0 (12:06); chunk A directive pack minus NegativeValidatorTests → 106 (7:48); chunk B `::NegativeValidatorTests` → 14 (18:34). Old baseline 2595 + 53 new bounded-contracts + 5 new M0-T101 shape tests = 2653 (arithmetic closes). The 3 skips are the same named env-conditional skips adjudicated in `M0-T099-G2-self-check.md` §2. |
| `ruff check` over all 6 new files | clean (1 auto-fix applied pre-freeze) |
| `python tools/modularity_check.py --check` | exit 0; largest new module 587 SLOC (< 600 warn) |
| `python tools/validate_directive_compliance.py --check` | EXIT=0 (run at the D-028/M0-T101 seam, post-capture) |
| gitleaks pre-commit | no leaks found (content commit e8b21d1) |

## 3. Mid-task discovery (transparency)

The first chunk-1 run (pre-M0-T101) failed 5 tests in `tools/test_mcp_policy.py` — a
post-acceptance defect from accepted M0-T100's settings key, repaired under the separate
bounded task **M0-T101** (accepted at `db8d333`). The composite above is at the frozen
M0-T090 tree, which contains that accepted fix beneath it. No M0-T090 file overlaps M0-T101.

## 4. Duties confirmed

- Supervisor-freeze: tree hash changes; baseline re-established above (≥1165/0 duty exceeded);
  D-024-R101 cited in packet + docstrings + commit.
- Carried advisories: G3-M1 discharged (two newer-completed vs older-active eviction tests,
  hosted in this pack — placement note in the producer report §3); G5-NIT-1 carried forward
  (target file outside allowed paths); G5-NIT-2 / G5-MIN-1 no action required.
- No dependency added; no forbidden path touched; shadow-only preserved (R595 untouched).

**G2 verdict: PASS — ready for independent G3 + G4 + G5 + DCV at frozen content `e8b21d1`.**
