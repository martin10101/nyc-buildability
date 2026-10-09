# M2-T021 — G0 contract readiness (administrative)

**Task:** Geoclient v2 address-resolution connector. **Recorded by:** orchestrator, 2026-09-11.

- **Packet complete:** objective, business reason, inputs, outputs, 8 executable acceptance
  scenarios (each an {input, expected} pair naming the fixture or seam it runs against),
  documented test commands, path notes.
- **Inputs verified present on disk:** the recorded G01 fixture
  (`services/api/tests/fixtures/geoclient/G01_address_documented_example.json`, both
  Geosupport sub-calls `00`, response sha256 recorded), the M0-T002 Geoclient research doc
  (endpoints/auth/GRC semantics), and the `pluto_soda.py` connector pattern this packet
  mirrors (typed errors, SOURCE_ID, provenance emission, injected seam).
- **Scope:** allowed_paths are the connector module, its tests, its fixtures, one
  source-registry draft record, and the producer report — each in BOTH matcher forms
  (glob + plain directory, per the measured M4-T009 dual-form finding). forbidden_paths
  exclude the API layer, main/config, rules, scenario, contracts, web, tools, control
  records and CI — this packet builds a library, wires nothing.
- **Preconditions:** the subscription key is live on the owner machine (verified 32-char,
  2026-09-11) for any additional polite KB-scale fixture captures; rate limits officially
  UNKNOWN, so captures stay single-request and hand-counted. The key exists nowhere in the
  repository and no scenario requires it at test time (S6 uses a sentinel).
- **Acceptance-criteria lesson applied (M5-T004):** S1 forbids tautological assertions
  (values must be loaded from the fixture, never restated as literals); S2/S8 encode the
  both-sub-calls and fail-closed-on-unknown-GRC rules from the research doc rather than
  leaving honesty to reviewer discretion.
- **Directive regime:** D-038:ALL stamped at creation; independent directive verification
  owed at acceptance as for every in-regime task.

**Result: PASS — contract is executable as written.**
