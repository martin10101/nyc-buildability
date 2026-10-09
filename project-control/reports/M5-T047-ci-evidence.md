# M5-T047 — CI evidence (orchestrator-captured)

Branch `candidate/D-024-mrl-option-b`.

## Corrected head `d27a6a83` (the T047 surface's CI-proven identity)

| run | workflow | conclusion |
|---|---|---|
| 35431045720 | CI (incl. web-e2e: vitest + Playwright vs recorded-official-fixture API) | **success** |
| 35431045643 | secret-scan | success |
| 35431045611 | context-budget | success |

## Prior head `7ecdcbf4` (material as first pushed, for the record)

CI run 35430668528 FAILED with exactly THREE tests of 1064, ALL in
`address-resolution.test.tsx` — a consumer test OUTSIDE the packet's allowed_paths: the
confirm card's new sibling record-address fetch skewed that file's whole-seam fetch-call
counts (and could have stolen queued mock responses in its deferred-response tests).
Corrected as the tagged `[ORCH-CORRECTED]` commit `20bea414` (task branch) / `d27a6a83`
(candidate) following the file's OWN M5-T023 precedent: the record-address endpoint joins
the existing lot-geometry side stub (benign 404 = the client's first-class `route_absent`),
so the resolution spy's order, counts, and queued responses stay exactly as each test
scripted them. No production code and no in-scope file changed in the correction;
out-of-scope test update routed to the orchestrator per CODING_RULES.

The submission head contains only control-plane/evidence commits over `d27a6a83` for the
T047 surface (plus the DISJOINT M5-T045 material and M5-T048 contract seams — zero path
overlap with T047's allowed_paths); the T047 surface at the submission head is byte-identical
to `d27a6a83`.

Orchestrator-reproduced local checks at the material identity (wt-m5t047): ruff clean;
`pytest tests/api/test_lot_geometry_api.py -q` = 33 passed; `pytest tests/api -q` = 439
passed; `python tools/modularity_check.py --check` exit 0 (warnings pre-existing).
