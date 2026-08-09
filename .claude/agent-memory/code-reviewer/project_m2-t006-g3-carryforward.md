---
name: m2-t006-g3-carryforward
description: M2-T006 contract 1.3.0 G3+G4 PASS at cd0b385; residuals - contract.py module docstring still says builder declares 1.2.0 (LOW D1), one-directional staleness conditionals, client version-array generation follow-up (R-NEW-1)
metadata:
  type: project
---

M2-T006 (property-profile contract 1.3.0, typed reproducibility.staleness) reviewed 2026-07-17: G3 PASS and G4 PASS at cd0b385 (impl e500ea5), PR #34 all 8 CI jobs green both events. Independently reproduced: 276 api tests, validate_contracts.py 0 failures, typegen --check OK, vendored schema sha256-identical (f4d6a156...), ruff clean.

**Why:** carry-forwards for later gates/tasks.

**How to apply:**
- D1 (LOW, non-blocking): `services/api/app/profile/contract.py` module docstring lines 16-20 still states "the builder declares 1.2.0" — stale after the 1.3.0 advance. Recheck fixed at next touch of that module.
- OBS-1: staleness schema conditionals are ONE-DIRECTIONAL (served_from_cache:false + age/error fields present would still validate). Builder tests pin exact fresh marker, so production can't emit it; if a future producer emits invented values on fresh serves the schema will NOT catch it — tests must.
- OBS-2: client `SUPPORTED_CONTRACT_VERSIONS` completeness is proven only by vitest loop + web-e2e, not by `satisfies`. R-NEW-1 follow-up (generate the array from the schema enum) recommended in README + producer report §13 — check it got a task before the next version bump (1.4.0).
- Pattern confirmed: every contract version publication = atomic schema+backend+client change while the client pins a closed set (amendment-A1 precedent).
- upstream_error_type taxonomy is exactly the connector's retryable classifiers (source_unavailable, timeout, rate_limited); schema_drift can never reach LKG. [[m2-t003-g3-carryforward]] [[m2-t004-g3-carryforward]]
