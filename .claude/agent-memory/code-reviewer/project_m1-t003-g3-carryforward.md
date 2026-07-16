---
name: m1-t003-g3-carryforward
description: M1-T003 zoning-features/ZTLDB research G3 PASS (2026-07-16); D1 = C2 (viewLastModified) not propagated into zoning-features.json record 2; carry-forwards for zoning-features importer, ztldb-soda connector, nyzma/pending-actions work
metadata:
  type: project
---

M1-T003 (NYC GIS Zoning Features + ZTLDB official-source research) G3 reviewed 2026-07-16: **PASS** with one minor defect. All live re-runs reproduced by this reviewer (sandbox HAS network): ZTLDB `$limit=1` identical split-lot record (bbl 1000010010, R3-2+C4-1, GI); nyzd count 5,416; R3-2 sample OBJECTID 86 / Shape__Area 837150.6837310791; `ZONEDIST='XX'` → empty features; nyc.gov 403; rowsUpdatedAt still 1775414816 (staleness real); C3 counts re-reproduced live (nysp 95, nysp_sd 336, nylh 14, nyzma 1414 — all ≥ their maxRecordCount caps).

**D1 (minor, left at PASS — verify fixed at acceptance or in connector packet):** G1 correction C2 was applied to the research doc (lines 48/170/178) but NOT to `source-registry-drafts/zoning-features.json` record 2 (`nyc-dcp-zoning-features-blob`): its known_limitations still claim "Socrata timestamps unusable for freshness; only signals are the description version string and blob content hash" — factually superseded by C2 (`viewLastModified` = 1779809507 = 2026-05-26T15:31:47Z is live and is the PRIMARY blob-change polling signal). Grep `viewLastModified` in docs/research/source-registry-drafts/ → zero hits = still unfixed.

Carry-forwards for the connector task packets (zoning-features-arcgis importer, ztldb-soda connector, nyzma/pending_land_use_actions):
1. Generic resultOffset paging MANDATORY on ALL six ArcGIS layers — live counts exceed maxRecordCount on nysp/nysp_sd/nyzma and equal it on nylh; unpaged requests silently truncate (C3). OQ-11 (f=geojson, paging behavior) must be exercised at build (fixture ZF-F4).
2. ZTLDB: staleness guard on rowsUpdatedAt (>45-day alert); health `degraded_suspected` until OQ-3 resolves; monthly-boundary observation due on/after 2026-07-27 (does rowsUpdatedAt move? does mm69-vrje description advance past 202604 / viewLastModified move?).
3. ZD1 (`zoning_district_1`) is NOT a closed Appendix-B enum — Queens ZR-section-number values possible (C4); "/"-joined special-district values need a parser (OQ-8); PARK caveat (not usable for open-space calcs); SODA omits blank keys — schema from columns array only; number-typed bbl/block/lot serialize as strings → normalize to 10-digit BBL (same class as [[m1-t001-g3-carryforward]] item 1).
4. OQ-1/OQ-2 (BYTES URLs, shapefile variant) are nyc.gov-403-bound — browser-capable session required BEFORE any BYTES bulk import; bundle with M1-T001 OQ-4/OQ-10 residuals; fail any task that guesses them. The fdkv-4t4z description's archive link target is the odd `.../datasets/zoning-map-index` (also 403) — recorded as-is, intent not guessed.
5. OQ-5/OQ-7: five layer metadata PDFs unread; nyzma STATUS/LUCATS domains + EFFECTIVE null semantics unverified — extract before the pending_land_use_actions connector.
6. ±20 ft horizontal accuracy → split-lot boundary intersections near tolerance are NOT authoritative; rules/conflict engine must treat near-boundary as uncertain. Official warning: zoning features "not intended for determining zoning at the individual tax lot level" — lot-level lists come from ZTLDB/PLUTO; conflict engine compares all three vintages.
7. OQ-6: ArcGIS provenance version = dataLastEditDate + retrieval timestamp; confirm lockstep with the YYYYMM BYTES release at the next boundary.

**Why:** single defect is a partial correction application in a machine-consumable registry draft (the corrected fact exists 3x in the companion doc, same commit); PASS-with-recorded-residual per M0-T005/T009/M1-T001 precedent.
**How to apply:** first checks when reviewing the zoning-features importer, ztldb connector, blob snapshotter, or anything consuming `docs/research/zoning-features-ztldb-2026-07-16.md` / `source-registry-drafts/zoning-features.json` / `ztldb.json`.
