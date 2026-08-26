# M0-T091 — G2 self-check (producer: orchestrator)

**Frozen content commit:** `ee564dd` (5 new runtime modules + 3 corrected C1 modules + 54-test
pack + producer report). 2026-08-26 UTC.

## 1. Deliverables present (packet outputs)

- health-band / no-progress / extension-gate / landing enforcement under `tools/agent_supervisor`
  (accelerated-counter testable): `runtime_health.py`, `runtime_detectors.py`,
  `extension_gate.py`, `lease_runtime.py`, `child_handoff.py` — every clock/counter injected,
  nothing worker-visible, SHADOW-ONLY (records/refusals; no spawn/resume/stop/message surface);
- `tools/test_agent_supervisor_runtime_supervision.py` — 54 tests incl. the s16.2 supervision
  cases: forty-minute-equivalent landing (accelerated), high-usage-near-seam completion,
  observe-produces-no-message — plus the full carried correction-bundle regressions;
- `project-control/reports/M0-T091-runtime-supervision.md` (incl. §2 correction-bundle
  disposition table).

## 2. Executable checks (foreground, at the frozen tree)

| Check | Result |
|---|---|
| `pytest tools/test_agent_supervisor_runtime_supervision.py -q` | **54 passed / 0 failed** |
| `pytest tools/test_agent_supervisor_bounded_contracts.py -q` (accepted C1 pack, UNTOUCHED, under the corrected guards) | **53 passed / 0 failed** |
| Adjacent packs (statusline handler, telemetry core, subagent telemetry, rotation, scheduler, context-pack) | **305 passed / 0 failed** |
| **Full composite `tools/` suite (supervisor-freeze baseline duty)** | **2707 passed / 3 skipped / 0 failed** — chunk 1 `pytest tools/ --ignore=tools/test_directive_compliance.py` → 2587/3/0 (12:56); chunk A directive pack minus NegativeValidatorTests → 106 (10:53); chunk B `::NegativeValidatorTests` → 14 (27:36). Old baseline 2653 + 54 new = 2707 (arithmetic closes). The 3 skips are the same named env-conditional skips adjudicated in `M0-T099-G2-self-check.md` §2. |
| `ruff check` over all 9 new/edited files | clean |
| `python tools/modularity_check.py --check` | exit 0; largest new module 478 raw lines (< 600 warn); no new warning |
| `python tools/validate_directive_compliance.py --check` | **EXIT=0** (re-run after the D-029 capture correction; first run EXIT=1 on two classification names + affected_tasks, fixed pre-commit, recorded in the D-029 manifest audit_log) |
| gitleaks pre-commit | no leaks found (capture commit 9e47c27, content commit ee564dd) |

## 3. Mid-task events (transparency)

- Owner directive **D-029** (M0-T091 seam-hold) arrived mid-production (during composite chunk B);
  captured verbatim BEFORE proceeding (commit `9e47c27`); this task's completion and the
  post-acceptance HOLD are now owner-ordered. M0-T091's acceptance set is unchanged
  (D-024:ALL, 46 ids; D-029 is conduct-only on sentinel D-029-BOOTSTRAP).
- The composite suite ran BEFORE the report/G2 files existed; those are non-code control-plane
  files outside every pytest collection path, so the figures hold at the frozen tree.

## 4. Duties confirmed

- Supervisor-freeze: tree hash changes; baseline re-established above (≥1165/0 duty exceeded);
  D-024-R101 cited in packet + all five new module docstrings + test-pack docstring + content
  commit message.
- Carried correction bundle: ALL NINE items applied in this unit (report §2 table maps each to
  its code change and regression test); G4 ADV-2/3 + G5 N2/N3 dispositions recorded there too.
- No dependency added; no forbidden path touched; the C1 test pack (outside allowed paths) was
  NOT edited and stays green; shadow-only preserved (R595 untouched); PR #241 untouched;
  no worker-facing counter/quota/band vocabulary anywhere (R045/R056 guards extended, not
  weakened).

**G2 verdict: PASS — ready for independent G3 + G4 + G5 + DCV at frozen content `ee564dd`.**
