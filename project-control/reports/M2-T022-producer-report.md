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
