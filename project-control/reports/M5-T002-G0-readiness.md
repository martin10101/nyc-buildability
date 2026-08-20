# M5-T002 — G0 readiness review (administrative)

**Task:** Scenario endpoint + property-screen scenario surface (R5 pilot; D-021)
**Reviewer:** orchestrator (G0 is administrative packet-readiness, ADR-005)
**Baseline:** origin/main `d8b3899f61efa6620e18a26541ced96020f5bef9` (local main == origin/main; clean; all 20 CI check runs green)
**Date:** 2026-08-20

## Verdict: PASS — packet is ready for implementation

## Evidence checked (live, not narrated)

1. **Dependencies merged and importable at the baseline.**
   - `services/api/app/scenario/` (M5-T001 foundation: `builder.py` `build_scenario`, `contract.py`
     `validate_scenario_document` / `assert_scenario_not_verified`, `models.py`, `constants.py`) is on main.
   - `services/api/app/api/v1/rule_evaluation.py` (M4-T005 endpoint pattern with flag gate, injection
     seams, single-sourced error maps) is on main; `properties.py` exports `PlutoFetcher`,
     `get_pluto_fetcher`, `_ERROR_STATUS`, `_DEFAULT_ERROR_STATUS`.
   - Ledger statuses: M5-T001 and M4-T005 are `awaiting_gate` with all their risk-required gates PASS
     on file and code MERGED to main (draft/needs_review regime, owner 2026-07-21/22). Dependency-READY
     for engineering; their final acceptance still owes genuine G6 legal approval of the M4 chain and is
     not claimed or weakened by this task.
2. **Contract surfaces exist; no contract change needed.** `packages/contracts/schemas/v1/scenario.schema.json`,
   `packages/contracts/generated/scenario.ts`, and `packages/contracts/fixtures/{valid,invalid}/scenario/`
   are on main from M5-T001. The endpoint returns the existing scenario document contract.
3. **Frontend patterns exist.** `apps/web/src/lib/rule-evaluation.ts` (+ `rule-evaluation-contract.ts`),
   `apps/web/src/components/rule-evaluation/`, `apps/web/e2e/rule-evaluation.spec.ts` +
   `rule-evaluation-flag-off.spec.ts`, and the recorded-official-fixture harness under `apps/web/e2e/harness/`.
4. **Known future-hardening items are in scope on purpose.** FH-M5T001-S1 (endpoint must call
   `validate_scenario_document` before emit) and FH-M5T001-S2 (bounded-depth guard) from
   `project-control/reports/M5-T001-future-hardening.md` are closed at this endpoint boundary.
5. **No open blocker binds.** B-001/B-004 (credentials) are not needed: the endpoint uses the injected
   fetcher seam and tests use recorded fixtures, same as M4-T005. B-010/B-011 do not touch this scope.
6. **Directive regime.** D-021 captured (source digest `9320b9b1…`), 25 requirements decomposed,
   `evaluate_task_refs(M5-T002)` → ok:True with applicable set = R001, R005–R011, R019–R023, R025
   (no other directive binds this packet's ids/paths). `validate_directive_compliance.py --check` exit 0.
7. **Holds preserved by scope.** `forbidden_paths` explicitly excludes tools/agent_supervisor/**,
   controller/model-selection configuration, context pipeline, MCP policy; packet records the
   PR-stays-UNMERGED stop condition (D-021-R022) and no-test-weakening (R011).
8. **Thin-client check.** Implementation + tests run in worktree/CI; no local db, no bulk data; scope is
   a small endpoint module, one config helper, one web surface, tests.

## Notes for the producer
- The endpoint mirrors `rule_evaluation.py` exactly (flag OFF by default → generic 404; bbl path param
  only; server-side rebuild; no request body; correlation id; payload-only logging).
- The surfaced cap must be the canonical trace value VERBATIM — never recomputed, never relabeled,
  in both API and UI. `needs_review` + `not_verified_disclaimer` carried end-to-end; never `verified`.
- A no-scenario outcome is a NORMAL 200 scenario document; honest typed states in the UI.
