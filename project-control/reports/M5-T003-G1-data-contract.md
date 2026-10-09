# GATE REPORT — G1 (data-contract fidelity) — M5-T003

**Reviewer:** data-contract-verifier (independent, read-only). **Reviewed SHA:** `30d6e3b4`.
**Verdict: PASS.** (Verbatim reviewer return preserved below; transport decoding only.)

---

**Task:** M5-T003 — Scenario endpoint `GET /api/v1/properties/{bbl}/scenario`
**Reviewed SHA:** `30d6e3b4a9e9fa4e90740b58a57af883c5145b66` (branch `candidate/D-024-mrl-option-b`, HEAD confirmed)
**Reviewer role:** independent, read-only (data-contract-verifier)
**Regime:** in-regime (`directive_refs: D-038 ALL`); DRAFT engineering — G6/legal acceptance deferred
**Verdict: PASS**

## Scope / provenance integrity
- Production + test files on disk are byte-identical to HEAD (`git diff HEAD --stat` empty for all four files). No uncommitted production edits.
- The M5-T003 integration commit `30d6e3b4` touched **exactly** the four allowed paths: `services/api/app/api/v1/scenario.py` (new), `config.py`, `main.py`, `tests/api/test_scenario_api.py`. Forbidden paths (`app/scenario/`, `rule_evaluation.py`, `properties.py`, `packages/contracts/`) were **not** modified by this task. (The `rule_evaluation.py` "M" in the branch-vs-main range is a different task, M2-T020 / commit `f12e828c`, not M5-T003.)
- Bundled runtime schemas `services/api/app/_contract_schemas/v1/{scenario,coverage_status,common}.schema.json` are **IDENTICAL** to the canonical `packages/contracts/schemas/v1/` counterparts (`diff` empty for all three). No forked/competing schema. `validate_scenario_document` loads from the bundled package via `importlib.resources` (contract.py:29,51-53), so it validates against the canonical contract.

## Review criteria — findings (file:line)

1. **Every 200 validates against scenario@1.0.0 before send — CONFIRMED.** `scenario.py:294` calls `validate_scenario_document(scenario)` and only on success reaches `return _json(200, scenario, …)` at `scenario.py:302`. On `ScenarioContractError` it returns `(500, internal_contract_error)` (`:295-300`), so an invalid 200 is impossible. Rebuilt profile and rebuilt rule_evaluation are likewise validated first (`:259`, `:277`). The scenario schema `coverage_status` field is narrowed to exclude `verified` via `$defs/coverage_status_draft` (allOf + subset enum: `conditional, professional_review_required, data_conflict, unsupported, not_applicable`) — schema-level enforcement, plus a belt-and-suspenders `assert_scenario_not_verified` fail-closed in `contract.py:93-102,121`.

2. **Cap is VERBATIM from the trace — CONFIRMED.** The endpoint performs no arithmetic; it passes `rule_evaluation` to `build_scenario` (`scenario.py:289`). The builder reads the cap from `trace_outputs.get(C.CAP_OUTPUT_NAME)` (`builder.py:382`), surfaces it unchanged as `draft_zoning_floor_area_cap_sq_ft` (`builder.py:321`, via `cap_value` at `:390`), unit `square_feet` unchanged. The `far*lot_area` recompute (`builder.py:476-485`) is **verification-only**, fails closed to `no_scenario/data_conflict` on disagreement, and never replaces the value. Test `test_as1_…verbatim` asserts `doc[...cap] == trace_cap == 15000.0`, reading `trace_cap` back from the sibling rule-evaluation route over identical inputs (`test:308-312`). No local recomputation, no unit change.

3. **(HTTP status, state) matrix = documented set = rule-evaluation route's matrix minus the version pair — CONFIRMED.** `STATUS_STATE_MATRIX` (`scenario.py:96-108`) equals `properties.STATUS_STATE_MATRIX` minus `(500, unsupported_contract_version)`, which the rebuild path collapses into the shared `(500, internal_contract_error)` — so no new pair is introduced. `test_as5_matrix_is_the_existing_property_route_matrix_minus_version_pair` proves the set relation; `test_as5_matrix_equals_rule_evaluation_route_emitted_set` **drives the actual sibling route** over the offline harness and asserts its emitted set equals the scenario matrix; `test_as5_every_emitted_pair_is_in_the_matrix` drives the scenario route through every pair. All pass.

4. **coverage_status vocabulary never up-labelled — CONFIRMED.** `verified` is unreachable (schema subset enum + fail-closed guard). `no_scenario / professional_review_required / unsupported / data_conflict` outcomes are returned as **NORMAL 200 documents** (endpoint returns 200 for any validated build; `scenario.py:302`), not errors — proven by AS-2 (split-lot → 200, `professional_review_required`, share ranges preserved verbatim, no cap).

5. **No independent legal calculation in the endpoint layer — CONFIRMED.** `scenario.py` only orchestrates the trusted injected seams (`get_pluto_fetcher` → `build_property_profile` → `evaluate_property` → `serialize_rule_evaluation`) and the already-built `build_scenario`; it contains no cap/FAR math. Request accepts only the `bbl` path param (no body/profile injection).

## Failure-behavior scenarios
- **null/no-match:** valid BBL, no PLUTO record → `(404, no_match)` with correlation id, source_id/dataset_id, no invented scenario body (AS-3, pass).
- **ambiguous (split-lot):** → `(200, no_scenario/professional_review_required)`, district `value: null` never collapsed, R5/R6 share ranges `0.55–0.65` / `0.35–0.45` preserved, exact review reason propagated verbatim (AS-2, pass).
- **malformed BBL:** typed `(422, validation_error)` with **zero** connector call (AS-4 landmine, pass).
- **rate-limit:** three 429s exhaust the retry budget → `(503, rate_limited)` (AS-5 via `F07` fixture, pass).
- **schema-drift:** dataset contract breakage → `(502, schema_drift)` (AS-4/AS-5 via `F13` fixture, pass).
- **internal defect / contract defect:** generic `(500, internal_error)` and typed `(500, internal_contract_error)` — no traceback, path, secret, or partial scenario leaks (AS-4 asserts absence of injected hostile strings; pass).
- Connector failures reuse the accepted `PlutoConnectorError → _ERROR_STATUS` mapping shared with the property/rule-eval routes — same semantics, no drift.

## Independent reproduction
- Interpreter: `Python 3.11.9` (the only resolving interpreter; CI targets 3.12, push held).
- `python -m pytest tests/api/test_scenario_api.py -q` → **27 passed** in 2.03s (independently reproduced; matches orchestrator-captured Row 1).
- Verified the orchestrator-captured evidence for internal consistency: file digests correspond to the reviewed content, and its CMD3 non-zero exit is the pre-existing, out-of-scope `tests/documents/**` PEP-695 3.11 collection failure (deselected by `-k`), not an M5-T003 defect. Row 3b isolates it (111 pass, exit 0).

## Caveats (not defects)
- Adjacent-regression (107) and config/flag (111) suites were verified via orchestrator-captured evidence, not re-executed here; the packet authorized re-running only the scenario suite on 3.11, which I did. CI on 3.12 has not run (push held) — documented environment limitation, acceptable for DRAFT-engineering with G6/legal deferred.

**VERDICT: PASS** — data-contract fidelity confirmed at the frozen SHA; no defects. DRAFT engineering; published/G6 legal acceptance remains deferred.
