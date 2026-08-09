---
name: m0-t017-g3-carryforward
description: M0-T017 S7 ledger-decoupling G3+G4 PASS @2aeb3db; stable-invariant policy for live-ledger tests; M9 = synthetic-ID namespace
metadata:
  type: project
---

M0-T017 (S7 test decoupled from live ledger composition) G3+G4 PASS at 2aeb3db, 2026-07-17. Test-only change; `tools/project_control.py` byte-identical to main.

Facts worth carrying forward:
- **Stable-invariant policy** now documented in the suite docstring: live-ledger tests may only assert monotone floors (`parsed >= 60` files, `accepted >= 21` — accepted is terminal per S6) and must SYNTHESIZE any exemplar records they need (backlog probe target) into the temp copy. If the orchestrator ever prunes ledger files (tasks/gates/blockers deletions), those floors break — producer documented this assumption in the M0-T017 producer report §6.
- **M9-T7xx is the synthetic-ID namespace** (M9-T700 exemplar, M9-T701 legacy, M9-T699 producer harness). Real ledger uses M0–M7 only. Flag any real task created under M9 as a defect.
- The permanent zero-backlog sub-check drains the temp copy and re-proves the synthesis path on EVERY run, so both compositions are always exercised; the backlog-present branch additionally verified via a disposable augmented-ledger copy (my independent method: full tree copy + injected M9-T900; producer's: REAL_PC monkeypatch).
- Live composition at review time: {accepted: 27, blocked: 2, claimed: 2}, zero backlog — the exact CI-breaking composition (job 87990690868).

**Why:** the defect class (test coupled to mutable live data) can recur in any future test that copies the real ledger; the policy + floors are the guard.
**How to apply:** when reviewing any new control-plane test that touches `REAL_PC`, check it obeys the stable-invariant policy; recheck the two floors if ledger pruning is ever proposed. See [[m0-t016-g3-carryforward]] for message-only progress semantics the probe relies on.
