---
name: m2-t008-g3-carryforward
description: M2-T008 ZTLDB connector G3+G4 PASS @afacff2; LOW TypeError edge in check_columns_for_drift; env-token hermeticity nit; ZT96 dual lineage; route-wiring next
metadata:
  type: project
---

M2-T008 (ZTLDB lot-level zoning connector, SODA fdkv-4t4z) G3+G4 both PASS at afacff2 (producer 7e40e81 + comment-only secretscan pragma fix, verified exactly two comment-string edits). Locally re-executed: 72 connector + 14 crosscheck, full suite 442 passed (356 baseline intact), ruff clean. Scope exact vs packet; pluto_soda.py/bbl.py/zoning_features_arcgis.py/contracts/resilience untouched.

**Why:** carry residual findings to the tasks that consume this connector (API route wiring, monthly sync, persistence).

**How to apply:**
- D1 (LOW, open unless orchestrator ordered a fix): `check_columns_for_drift` in ztldb_soda.py raises an UNTYPED TypeError when metadata mixes a columns entry lacking `fieldName` (None key) with an unknown string column — `sorted()` on mixed None/str. Repro: `check_columns_for_drift({'columns':[{'dataTypeName':'text'},{'fieldName':'brand_new','dataTypeName':'text'}]})`. Recheck at route-wiring/G5 or any drift-check refactor; same pattern may exist in sibling connectors.
- Hermeticity nit: tests pass `app_token=None`, which triggers the `SOCRATA_APP_TOKEN` env fallback inside fetch functions — a dev machine with that var set would fail header-assertion tests. Same pattern as accepted PLUTO suite; flag if a hermetic-test policy lands.
- ZT96 duplicate-page synthetic: manifest `derived_from` = ZT07b (request slot) but body bytes = ZT07a (deliberate, documented in build_fixture_pack.py derive entry). Not a defect; don't re-flag.
- Builder integration: `build_property_profile` gained three optional kwargs (additional_provenance/conflicts/notes, default None); default-path equality proven by omitted-vs-None test + untouched 356 baseline (not a direct main-vs-branch byte diff). Combined conflicts feed `_status_dimensions` so crosscheck zonedist1 conflict -> blocked_data_conflict via existing M2-T004 machinery.
- Error taxonomy identical to M2-T007 zoning_features (incl. paging_pathology); no_record is a RESULT status. dataset_version label = `socrata-rows-<rowsUpdatedAt RFC3339>` (no version column exists — research-grounded, not guessed).
- OQ-3: Socrata rows STILL at 2026-04-05 on 2026-07-20 (second missed monthly cycle); producer recommends DCP escalation (human action) — check a blocker/task exists.
- Fixture pack: 24 fixtures = 104,456 bytes; +MANIFEST+build script = 144,115 bytes total (report's "~104 KB" = fixtures only). All KB-scale.
- CI attestation deferred (B-009 GitHub Actions billing outage); orchestrator post-restore duty — cross-platform digest anchor ZT01 needs a Linux CI confirmation.

Related: [[m2-t007-g3-carryforward]], [[m2-t004-g3-carryforward]], [[m1-t002-g3-carryforward]].
