---
name: m2-t007-g3-carryforward
description: M2-T007 zoning-features ArcGIS connector G3+G4 PASS @4468954; LOW residuals (untested drift signals, dead-code test); facts for M2-T008/import-worker reviews
metadata:
  type: project
---

M2-T007 (GIS Zoning Features connector, six DCP ArcGIS layers) G3+G4 both PASS at worktree commit 4468954 (branch task/M2-T007-zoning-features-connector, PR #39). Re-ran evidence myself: 80/80 connector tests, 356/356 full suite, ruff clean. Scope diff exactly matched allowed_paths; contracts 1.3.0, resilience, pluto_soda, profile all untouched.

**Why:** future gates (G1 data-contract, G5 security, M2-T008, and the follow-up PostGIS import worker) should not re-litigate closed items and should recheck the LOW residuals.

**How to apply:**
- LOW residuals carried forward (non-blocking, recheck when connector next touched): (D1) drift signals `missing_editing_info` and `page_missing_spatial_reference` are implemented but have no test asserting them; (D2) `test_s9_added_field_signal_propagates_into_extraction_result` asserts via query_features not extract_layer and contains dead page-load code; (D3) count==maxRecordCount (nylh 14=14) single-page extraction at DEFAULT page_size not directly tested (logic verified safe by inspection).
- Established facts to reuse: ArcGIS error-object-with-HTTP-200 is live-verified (ZF06, error.code 400); empty results omit spatialReference (ZF05); resultOffset paging live-verified, f=geojson still OPEN (OQ-11 residue); retry authority is consolidated in `_request_with_retry` (client adds cache/breaker/LKG only — deliberate deviation from the pluto fetcher split, disclosed and sound).
- Fixture pack is ~782 KB on disk (producer said ~700 KB — approximation, not a defect); 5 synthetic nyzd metadata negatives each carry the full ~106 KB body. If the pack grows at M2-T008+, consider trimming drawingInfo in synthetic derivations.
- pluto_soda private `_request_with_retry` pattern is now duplicated per-connector by convention; producer and I both recommend a future additive shared `connectors/_transport.py` refactor — do not flag the duplication as a defect again, it is tracked.
- Two-staleness rule test pattern (ZF95 old-source-fresh-retrieval + cache-hit + LKG both directions) is the reference implementation for future connectors; related: [[m2-t006-g3-carryforward]] staleness conditionals.
