# M5-T048 CI evidence (orchestrator-captured)

Corrected head: `149fab76` (material cherry-pick 93f194c0 + G0 re-record seam commits).

- Workflow **CI** run **35439235554** — completed **success**; **0 non-success jobs** (the
  full matrix: api ruff+pytest, contracts JSON-Schema validation, contracts-typegen
  byte-identity, modularity, web lint/typecheck/build, web-e2e, code-graph,
  dependency-security/lock-verify jobs, exact-production-install, product-map,
  context-pipeline). The contracts job — the one that failed at the harvested head —
  now passes: the semantic fixtures live outside invalid/, and the negative-height
  fixture is correctly schema-rejected.
- Workflows context-budget and secret-scan at the same push: completed success.

Prior round (root-caused, corrected): CI run **35437764489** at 0c7b17f1 — contracts job
FAILED 2/11: `invalid/scenario/proposed_massing_{open_ring,self_intersecting}.json`
"unexpectedly PASSED validation" — by design schema-valid (geometry invariants JSON Schema
cannot express); the CI convention requires schema-rejection under invalid/. Corrected as
tagged 607aab6b (relocation to fixtures/semantically_invalid/scenario/ + test updates +
packet amendment [ORCH-PACKET-FIX 2] + G0 re-record).
