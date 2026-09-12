<!-- Reviewer return preserved VERBATIM by the orchestrator (report-preservation rule,
.claude/rules/project-control.md; transport entity-decoding applied: &lt; -> <, &gt; -> >, &amp; -> &).
Reviewer: independent code-reviewer subagent (G1 delta), returned 2026-09-12,
reviewed HEAD e40c87c4. -->

All checks are complete and independently reproduced. Here is my delta gate report.

---

VERDICT: PASS

# G1 Code Review Gate Report (DELTA) — M2-T022 (address-resolution API endpoint)

- Task: M2-T022 — "Address-resolution API endpoint" (backend, milestone M2, in-regime `directive_refs` D-038:ALL)
- Reviewed HEAD: `e40c87c43e72a4f7e25611e7f83ffca562009259`
- Delta commit under review: `803d5606` (route + test + producer-report addendum); resubmit `e40c87c4` (control-plane only)
- Prior G1 wave: FAIL at `ec4b75dc` (report `project-control/reports/M2-T022-G1.md`; HIGH-1, LOW-1, LOW-2 — treated as my own prior round)
- Reviewer: code-reviewer (independent; did not author). Read-only per ADR-005. `PYTHONDONTWRITEBYTECODE=1`; in-process `TestClient`/`python -c` probes only; no pytest/ruff; nothing written; no `project_control.py`.
- Gate: DELTA — verified the three prior findings' corrections and the full `803d5606` diff for new defects.

## Verdict rationale

Every prior-round finding is fixed and independently reproduced at HEAD. HIGH-1 (the production-breaking resolver-signature mismatch) is corrected at the production seam and now covered by a test that genuinely exercises the real `get_address_resolver()` path; my own production-wiring probe returns 200 end to end, and the old signature still 500s (revert-proof coheres). LOW-1/LOW-2 corrected. The G3- and G4-driven changes are additive/behavior-neutral and introduce no new defect. The delta is in scope. No MEDIUM+ defect remains.

## Findings from the prior round — verified corrected

### HIGH-1 (production resolver signature) — FIXED, reproduced
`address_resolution.py:241-256` — `_default_resolver(house_number, street, *, borough=None, zip_code=None)` forwards positionally + keyword to `resolve_address(house_number, street, borough=borough, zip_code=zip_code)` with **no** `budget=` and **no** `transport=` (C4 duty 3 preserved). The route's call (`address_resolution.py:426-431`, unchanged, positional `house_number`/`street`) now matches.

Independently reproduced at HEAD (`INTERNAL_RULE_EVAL_ENABLED=1`, `dependency_overrides` cleared, module-global `resolve_address` monkeypatched, egress seams neutralized):
```
default resolver is _default_resolver: True
DIRECT CALL OK status: resolved forwarded: {'house_number':'314','street':'w 100 st','borough':'manhattan','zip_code':None,'extra':{}}
ROUTE (prod wiring) code: 200 status: resolved forwarded: {...same...} calls: 1
ROUTE (OLD **kwargs sig) code: 500 state: internal_error
```
- The new test `test_s1_production_wiring_default_resolver_reaches_the_connector` (test file lines 261-308) genuinely exercises the REAL dependency: it calls `app.dependency_overrides.clear()` and monkeypatches `address_resolution_module.resolve_address` — it does **not** override `get_address_resolver`, so the real `_default_resolver` is invoked. It asserts faithful forwarding (`zip_code is None`, `extra == {}`) and exactly one transport call. Confirmed by read + reproduced above.
- Revert-proof coherence: my probe injecting the old `**kwargs`-only signature yields HTTP 500, so the new test's `assert status_code == 200` fails under revert. The pack is now 27 tests (19 `def test_` functions; two parametrized ×6/×4; 17 non-param + 6 + 4 = 27), so running only the one production-wiring test gives "1 failed, 26 deselected" — the producer's recorded revert-proof coheres. Minor wording nit (advisory, non-blocking): the addendum says "the route reverted to the ec4b75dc form", but the route was already positional at `ec4b75dc`; it is the **resolver signature** (in the route module) that is reverted. Mechanism and numbers are correct.

### LOW-1 (matrix omission / inaccurate comment) — FIXED, reproduced
`STATUS_STATE_MATRIX` now contains `(503, "request_budget_exceeded")` (`address_resolution.py:174`), and the docstring/matrix comment (lines 73-79, 155-162) no longer claim the generic 500 guard would type it — they now correctly state the connector-error handler would emit it at the default 503. Reproduced: `RequestBudgetExceededError` is a `GeoclientConnectorError` subclass with `error_type == "request_budget_exceeded"`; `_ERROR_STATUS.get(...) → _DEFAULT_ERROR_STATUS == 503`; pair is in the matrix. It remains unreachable on this route (no budget passed — S8), documented as such; this closes the latent gap G4 observation #2 raised. Not a false claim.

### LOW-2 (matrix wording) — FIXED, reproduced
Docstring/comment now say "every TYPED pair" with the flag-off generic 404 explicitly outside the typed space (lines 103-105, 152-155). Reproduced flag-off: `404 {"detail":"Not Found"}`, no `X-Correlation-ID` header — indistinguishable from an unmounted path (fail-safe disable).

## G3-driven change (substance is G3's delta) — no new defect
`_REFLECTED_INPUT_WARNING.fields` extended to lead with `input_echo` and name the street/borough `source_facts[]` original/normalized values (additive to a static contract list; no behavior branch). New `test_s6_input_echo_is_a_named_reflected_surface` added. Reproduced: hostile `<script>...`/`7<b>7` inputs arrive byte-exact in `input_echo`, absent from headers; the escape-contract `fields` now contains `input_echo` and `source_facts[]` entries. The addendum also retracts (not rewrites) the report's earlier false "names every reflected surface" universal. No new defect.

## G4-driven change — no logic change
G4 B1 was the E501 at `test_...:361` (the `AuthFailedError` `detail={...}` dict, 107 chars). The delta wraps that dict across lines (test file lines 412-416) — pure reformatting, no assertion/logic change. Scan of both delta files at HEAD: zero lines >100 chars, so no new E501 introduced. (The addendum's claim that ruff passed all along via the no-whitespace-overflow exemption is a producer/G4 evidence matter, not a code defect; the wrap moots it.)

## Scope & new-defect check
- `git diff --stat ec4b75dc..e40c87c4 -- services/api` → exactly `address_resolution.py` and `test_address_resolution_api.py`; nothing else under `services/api`.
- `803d5606` touches only the route module, the test module, and the producer report; resubmit `e40c87c4` touches only control-plane JSON (`M2-T022.json`, `state.json`, `tasks/M2-T022.json`).
- Full read of `git show 803d5606`: route changes are (1-3) docstring/matrix comments, (4) additive matrix pair, (5) additive warning-field list, (6) the `_default_resolver` signature fix — no hidden logic change; test changes are additive tests + the E501 wrap + import of the module alias. No forbidden path touched. Working tree clean vs HEAD (only untracked `scratchpad/` and this reviewer's `.claude/agent-memory/qa-engineer/**`, both out of scope).
- Matrix set-equality test (`test_matrix_documented_pairs_are_exactly_the_emitted_set`) expected set = 10 pairs = `STATUS_STATE_MATRIX` (10); genuine equality, not vacuous.

## Notes for the orchestrator
- Directive compliance (D-038:ALL, empty-applicable-set form) is the `directive-compliance-verifier`'s gate — not adjudicated here.
- I did not run pytest/ruff/modularity_check per discipline; the addendum reports pack 27 passed, `tests/api` 398, whole suite 1858 (+1 known local-3.11 PEP-695 artifact), whole-tree ruff clean, modularity exit 0 — CI at the pushed head is the execution authority.
- One advisory-only nit (revert-proof wording, above); nothing blocking. Recommend PASS and proceed to acceptance pending the directive-compliance verification.

Files reviewed (absolute): `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24/services/api/app/api/v1/address_resolution.py`, `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24/services/api/tests/api/test_address_resolution_api.py`, `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24/project-control/reports/M2-T022-G1.md`, `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24/project-control/reports/M2-T022-G4.md`, `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24/project-control/reports/M2-T022-producer-report.md`.

VERDICT: PASS (reviewed HEAD `e40c87c4`)
