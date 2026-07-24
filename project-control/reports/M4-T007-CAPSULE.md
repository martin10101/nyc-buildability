# Startup capsule — M4-T007 (producer tab)

**You are a producer, not the controller.** Do not merge, accept, replan the ledger, change another
task, operate another worktree, read/import an unmerged sibling branch, or modify a shared contract.
Commit and push only your assigned branch; open one PR against main when the complete packet is ready.

- **Task / title:** M4-T007 — Exact Decimal/legal-units arithmetic and rounding foundation (DF-2).
- **Branch:** `task/M4-T007-decimal-legal-arithmetic` · **Expected worktree:** the sibling folder the controller created for you (path in the owner return).
- **Frozen base SHA:** your worktree's initial `HEAD` (run `git rev-parse HEAD`) — the post-D-002-consolidation `main` SHA in the controller's owner return. Start from it.
- **Read before starting:** (1) root `CLAUDE.md`; (2) your packet `project-control/tasks/M4-T007.json` (source of truth); (3) `project-control/reports/FIRST-WAVE-INTEGRATION-CONTRACT.md`; (4) your applicable D-002 requirements (the 14 PROD ids); (5) `project-control/reports/WHOLE-SYSTEM-TRUST-REPLAN-2026-07-23.md` (Area D / DF-2) + `project-control/blockers/B-014-*.json` + current `services/api/app/rules/operations.py` and `evaluator.py`; (6) your latest `M4-T007-*` resume report if any.
- **Directive refs:** D-002 (regime v1.0; cite `D-002:ALL`).
- **Owned interfaces:** `services/api/app/rules/units.py` (NEW canonical-decimal + unit-enforcement helpers; frozen interface). No schema. **Consumed read-only from main:** rule DSL/model types, ZR snapshots.
- **Allowed paths:** `services/api/app/rules/operations.py`, `services/api/app/rules/evaluator.py`, `services/api/app/rules/units.py`, `services/api/tests/rules/`, `project-control/reports/M4-T007-producer-report.md`.
- **Forbidden paths:** `packages/contracts/**` (canonical contracts; M2-T017 owns source_fact/analysis_state_transition); `services/api/app/rules/rulesets/**` (published rule CONTENT — no legal-semantics change without G6); `dsl.py`/`lifecycle.py`/`registry.py`/`integration.py`; `services/api/app/profile/**` and `.../api/**` (production entrypoints); every reserved hotspot.
- **Dependencies proven accepted:** none (builds on already-merged M4 engine code on main). No first-wave sibling dependency.
- **Required tests / harnesses:** property-based; differential (native evaluator vs an independent Decimal recompute); adversarial exact-threshold + rounding tests; the existing `services/api/tests/rules/**` suite must still pass.
- **Permitted report path:** `project-control/reports/M4-T007-producer-report.md`.
- **Completion condition:** legal math on the value path uses Decimal/rational from canonical strings with explicit per-rule rounding mode/scale/order + unit enforcement; geometry floats stay isolated behind typed conversions; all tests green; G0/G2/G3/G4/G5 evidence in your report; one PR against main opened.
- **Stop conditions (return a ≤200-word blocker):** any need to change rule CONTENT/semantics (G6 territory) or a canonical/shared contract (submit an interface-change request — do not edit it); credential/payment/security-exception/destructive-op/impossible-acceptance.
- **Final return (≤500 words, ≤8 bullets):** task+outcome; PR link+head; what now works; contract/interface impact; tests+review result; blockers/limitations; exact next dependency unlocked (future M4 rule tasks consume the exact-math foundation); whether you are now idle.
