# G4 INTEGRATION / REGRESSION GATE — M5-T006

**Result: PASS.** Reviewed identity `817815cc9f8205fba152d3e4b684b0b036ab56f0`. Evidence independently reproduced by the G1 (code-reviewer) and G3 (qa-engineer) reviewers; recorded by the orchestrator per ADR-005.

## Integration
- M5-T006's producer output committed at `817815cc` on `task/M5-T006-derive-hardening` (linear descendant of the contracting commit `b0d39ad6`); integrated into `candidate/D-024-mrl-option-b` by **fast-forward** (no merge commit, no conflict). Changes: `services/api/app/scenario/derive.py` (+112/−18), `services/api/tests/scenario/test_scenario_derive.py` (+22 tests), `project-control/reports/M5-T006-producer-report.md`.
- **Scope clean:** `git diff --name-only 817815cc^ 817815cc` = exactly those 3 files; no forbidden path (`builder.py`/`models.py`/`constants.py`/`contract.py`/`__init__.py`/`packages/contracts/**`/`tools/**`). Contract-free, additive defense-in-depth.

## Regression
- Full scenario suite reproduced green at the reviewed SHA: **`python -m pytest tests/scenario -q` → 124 passed, 0 failed** (both code-reviewer and qa-engineer independently; ~0.55s, Python 3.11.9). +22 new hardening tests; the pre-existing 102 (M5-T005 derive + contract + foundation) **unchanged and still green — no regression**.
- **DERIVED happy path proven byte-identical to the M5-T005 parent:** the code-reviewer byte-compared 9 positive-finite outcomes (json.dumps) against `817815cc^`, and the qa-engineer pinned two full-output golden baselines — the hardening changes only the fail-closed outcomes + input-copy/echo bounding, never the correct DERIVED arithmetic.
- **Modularity:** `python tools/modularity_check.py --check` → **0 failures** (derive.py 490 lines, cohesive same-domain helpers; not flagged).
- No canonical contract/schema/generated artifact changed → no downstream contract regression surface.

## Conclusion
Additive, scope-clean, contract-free hardening; full suite green with zero regression; the DERIVED path is byte-identical to the accepted M5-T005 baseline. **PASS.**
