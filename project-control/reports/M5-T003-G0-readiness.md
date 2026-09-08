# G0 — Definition-of-Ready — M5-T003 (scenario endpoint)

**Task:** M5-T003 — `GET /api/v1/properties/{bbl}/scenario` exposing the built deterministic
scenario builder (flag-gated, contract-validated, offline; no credentials).
**Directive:** D-038:ALL (build product, not self-infra; no-credentials constraint D-038-R004).
**Reviewer:** orchestrator (administrative G0). **Base:** candidate `ebe4eaf6`.

## Readiness checklist

- [x] **Scope bounded.** 5 `allowed_paths` (new `scenario.py`, `main.py` registration, `config.py`
  flag, new `test_scenario_api.py`, producer report); 6 `forbidden_paths` (builder/contract/other
  routes read-only; no Supabase/Geoclient; no `apps/web`; no control-plane).
- [x] **All consumed inputs already present in the branch** (verified read-only):
  `services/api/app/scenario/builder.py` (`build_scenario`) + `contract.py`
  (`validate_scenario_document`); `services/api/app/api/v1/rule_evaluation.py` (template + seams);
  `packages/contracts/schemas/v1/scenario.schema.json` (scenario@1.0.0);
  `tests/api/test_rule_evaluation_api.py` + committed fixtures. No unbuilt dependency.
- [x] **Acceptance pack executable.** AS-1..AS-7 defined; each maps to a FastAPI-TestClient test with
  a concrete fixture and assertion (verbatim-cap equality, no_scenario range preservation,
  not-found/error matrix, contract validation, flag-off 404 indistinguishability, offline proof).
- [x] **No-credentials constraint satisfiable** (D-038-R004): the accepted rule_evaluation endpoint
  already runs fully offline over the injected `get_pluto_fetcher` + `get_spatial_substrate_provider`
  seams; this task mirrors that path — no network, no Supabase, no Geoclient.
- [x] **Gates + reviewers assigned.** G0,G1,G3,G4,G5; reviewers data-contract-verifier, code-reviewer,
  qa-engineer, security-reviewer.
- [x] **Draft-engineering boundary explicit.** Values surfaced verbatim from the trace (never
  recomputed); needs_review; published/G6 acceptance deferred (mirrors the M4 chain).

**Verdict: PASS (ready).** No unresolved blocker; scope and acceptance are executable with no
credential dependency.
