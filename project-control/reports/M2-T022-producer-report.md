# M2-T022 producer report — address-resolution API endpoint

Producer: backend-engineer/orchestrator. ENGINEERING_RELIABILITY_STANDARD §2 (owning boundary:
HTTP transport of the connector outcome, one new route module per the M5-T013 template), §3
(observations below), §7 (typed states = connector error_type verbatim; two-audience payloads;
correlation ids on both sides; no leak).

## What was authored

1. `services/api/app/api/v1/address_resolution.py` (~460 lines incl. the design docstring):
   GET /api/v1/address-resolution, flag-gated by the EXISTING INTERNAL_RULE_EVAL_ENABLED
   (app.config out of scope; evidence-route precedent, rationale in the docstring), generic
   404 when off, include_in_schema=False. Transports the connector's typed outcome verbatim:
   every geocoding outcome is a VISIBLE 200 (resolved / resolved_with_warnings / ambiguous
   with verbatim suggestions + selection_policy "caller_selects" / not_found / rejected /
   unrecognized_status); connector failures map to the documented STATUS_STATE_MATRIX with
   states equal to the taxonomy's error_type strings. C4 duties discharged: success-class
   outcomes emit source_facts[] shaped by packages/contracts/schemas/v1/source_fact.schema.json
   (READ-ONLY consumption; 12 required keys + fact_key/observation_id/value_digest/
   response_digest lineage; dataset_version is the honest self-describing string since the
   /address response exposes no Geosupport release id; facts withheld WITH A STATED REASON when
   the resolved BBL fails canonical validation - fail-safe, never a malformed-looking fact);
   the machine-readable unsanitized_reflected_input warning names every reflected surface; NO
   AnalysisBudget is ever constructed or passed (request_budget_exceeded structurally cannot
   arise). Local Retry-After guard: fullmatch charset + 32-char cap, DROPPED on failure (the
   shared sanitize_retry_after's C4 defect stays quarantined off this surface). Fail-closed
   assembly + dual-form JSON-safety check before send; the generic guard logs the type-free
   one-liner only (no exception text - it could echo reflected content).
2. `services/api/app/main.py`: router registration + the posture comment (only change).
3. `services/api/tests/api/test_address_resolution_api.py` (25 collected): S1-S8 per the
   packet - fixture-anchored values (never literals), jsonschema validation of every emitted
   fact against the REAL source_fact schema via a referencing.Registry (the C4 consumability
   proof), the failure matrix parametrized with positive controls, hostile Retry-After cases,
   the sentinel leak harvest across success + real-401 paths (upstream body text proven not to
   pass through), flag gating both ways, hostile reflected text byte-exact in JSON and absent
   from logs/headers, statelessness (two calls = two connector calls, distinct correlation
   ids), the S8 seam + source pin, and matrix exhaustiveness. Offline guard at the EGRESS
   SEAMS (http.client connect + socket.create_connection - the evidence-pack pattern; blocking
   socket construction deadlocks the TestClient portal).

## Behavior-proof observations (§3.1, recorded as they happened)

- The pack was written against the packet scenarios and run before the route was correct; two
  genuine defects were caught RED and fixed:
  (a) REAL production defect: the fact builder shipped `normalize_bbl(...)`'s NormalizedBBL
  RECORD as the fact's bbl -> the JSON-safety check refused it and the route emitted the typed
  (500, internal_error) instead of an untyped escape. The failing S1/S5 runs are the recorded
  red; the fix (.canonical) the green. This simultaneously PROVED the fail-closed assembly
  guard end-to-end on a real defect, not a synthetic one.
  (b) Test-side: the S2 expected-suggestion reconstruction invented a `slot` key the connector
  contract does not carry; corrected to the connector's documented shape (fixture-derived,
  still never self-referential).
- The (500, internal_error) pair is additionally pinned by test_matrix_internal_error_pair_
  via_unexpected_exception (a non-connector RuntimeError never leaks its text).

## Self-checks (producer-run; CI remains the authority)

`pytest services/api/tests/api -q` -> **396 passed** (371 + 25 new);
`pytest services/api/tests -q --ignore=tests/documents` -> **1856 passed, 1 failed** - the one
failure is the KNOWN local-3.11 PEP-695 ast-parse artifact in test_contract_serializers (passes
on CI 3.12; unchanged by this diff; tests/documents excluded locally for the same recorded
3.12-only reason); `ruff check services/api/app/api services/api/tests/api` -> All checks
passed; `python tools/modularity_check.py --check` -> exit 0.

## Deliberate choices (for the reviewers)

- Single validation authority: the route accepts plain strings and lets the CONNECTOR's typed,
  value-free InvalidInputError drive the 422 - no second validator to drift.
- Two correlation ids, both surfaced (HTTP-level minted here; connector's inside provenance /
  error payload) - distinct by design, documented.
- Facts for resolved_with_warnings ARE emitted (a 01-warning outcome is a success class per
  the connector contract; the warning text travels in grc_message beside the facts).
- No request_url on facts: recomposing the URL endpoint-side would re-derive rather than
  transport; endpoint + request_params travel verbatim inside provenance instead.

---

## Rework addendum (gate wave at ec4b75dc: G1 FAIL / G3 FAIL / G4 FAIL / G5 PASS; reports at project-control/reports/M2-T022-G{1,3,4,5}.md)

One bounded change covering every blocking finding plus the cheap LOWs:

1. **G1 HIGH-1 (production resolver signature) — FIXED with a revert-proof.** `_default_resolver`
   now takes `(house_number, street, *, borough=None, zip_code=None)` — the ROUTE's exact call
   contract — and forwards positionally+keyword to `resolve_address` (still NO budget, NO
   transport: C4 duty 3 preserved at the production seam). The prior `**kwargs`-only form
   rejected the route's positional call, 500ing every real request, masked because every test
   override accepted positionals — the masked-seam failure class the packet's own risks named,
   which the G1 reviewer caught by clearing the overrides. NEW TEST
   `test_s1_production_wiring_default_resolver_reaches_the_connector`: dependency_overrides
   CLEARED, the module-global `resolve_address` monkeypatched with a recorder driving the real
   connector — production wiring exercised end to end, forwarding fidelity + empty extra-kwargs
   asserted. **Revert-proof (§3.4):** with the route reverted to the ec4b75dc form the new test
   FAILS (1 failed, 26 deselected — recorded); restored, the pack passes. (The G1 report's own
   end-to-end reproduction at ec4b75dc is the independent red.)
2. **G3 BLOCKING (input_echo missing from the escape contract) — FIXED.**
   `_REFLECTED_INPUT_WARNING.fields` now leads with `input_echo` and additionally names the
   street/borough `source_facts[]` original/normalized values (the reviewer's secondary note).
   NEW TEST `test_s6_input_echo_is_a_named_reflected_surface`: hostile `<script>` street +
   `7<b>7` house number arrive byte-exact in `input_echo` AND `input_echo` +
   `source_facts[]`-prefixed entries are asserted present in the warning's field list.
   **CORRECTION OF THIS REPORT'S OWN FALSE CLAIM:** the original text above says the warning
   "names every reflected surface" — that was FALSE at review time (input_echo was omitted);
   the sentence is retracted, not rewritten, and the property is now enforced by test rather
   than claimed in prose.
3. **G4 B1 (E501) — line wrapped; the finding's ruff-outcome claim CORRECTED with captured
   executable evidence.** The 107-char line is now wrapped (raw-length conformance). However
   the orchestrator-captured evidence at project-control/reports/M2-T022-ruff-evidence.txt
   (ruff 0.13.0, CI cwd + config) shows ruff PASSED on that line all along: ruff's E501 exempts
   lines whose overflow past the limit contains no whitespace (the URL token). The documented
   ruff command never failed and this report's "ruff clean" self-check was TRUE; G4's B1
   inferred the failure statically under its no-execution discipline. Recorded per the
   evidence-capture division of labor; the wrap removes the ambiguity class entirely.
4. **G1 LOW-1/LOW-2 — matrix corrected.** `(503, "request_budget_exceeded")` added as a
   documented UNREACHABLE-BY-CONSTRUCTION pair (the connector-error handler would emit it at
   the default 503 if a budget were ever introduced — the prior comment wrongly credited the
   generic 500 guard); matrix prose now says "every TYPED pair" with the flag-off generic 404
   explicitly outside the typed space. Matrix set-equality test updated (10 pairs).

Self-checks after rework: pack **27 passed** (25 + 2 new); `pytest services/api/tests/api -q`
-> **398 passed**; whole suite `--ignore=tests/documents` -> **1858 passed, 1 failed** (the
recorded local-3.11 PEP-695 artifact, unchanged); CI-style whole-tree `ruff check .` from
services/api -> All checks passed; `modularity_check --check` -> exit 0; gitleaks staged scan
clean. G5's PASS surfaces re-touched by this rework: the warning-field list (extended, never
narrowed) and the resolver signature (no new key/branch surface) — flagged for the G5 delta.

NOT changed, deliberately: G4's non-blocking observations 1-3 (source-scan supplementarity,
the undriven unreachable pair, construction-tied digest assertions) and G5's O1/O2 accepted
observations stay as recorded reviewer judgments.
