# M1-T003 — G3 Independent Walkthrough Gate Review

- Gate ID: G3 (independent human-style walkthrough)
- Task ID: M1-T003 — Official-source research: NYC GIS Zoning Features + Zoning Tax Lot Database
- Reviewer: code-reviewer (independent; did not produce the work; did not run G1)
- Producer: official-source-researcher
- Result: **PASS** (1 minor defect D1; none invalidates findings; no guessed claim found)
- Review date / all live re-runs: 2026-07-16
- Recording note: reviewer returned this report content to the orchestrator per ADR-005 (read-only reviewer); saved verbatim by the orchestrator.

## Steps independently executed (live, KB-scale only)

| # | Command (exact) | Expected | Actual | Match |
|---|---|---|---|---|
| 1 | `curl -s 'https://data.cityofnewyork.us/resource/fdkv-4t4z.json?$limit=1'` | verbatim split-lot record from doc §2.1/Z3 | byte-identical record (`bbl 1000010010`, R3-2 + C4-1, GI, 16A, Y); blank keys omitted; numbers as strings | YES |
| 2 | nyzd `.../0/query?where=1=1&returnCountOnly=true&f=pjson` | 5,416 | `{"count":5416}` | YES |
| 3 | nyzd `where=ZONEDIST='R3-2'&outFields=*&resultRecordCount=1` | OBJECTID 86, R3-2, Shape__Area 837150.68…, 1 ring | exact match, SR 102718/2263, units esriFeet | YES |
| 4 | nyzd `where=ZONEDIST='XX'` (no-match) | empty features array | `"features" : []` | YES |
| 5 | HTTP code of nyc.gov gis-zoning-features page | 403 | 403 | YES |
| 6 | `api/views/fdkv-4t4z.json` rowsUpdatedAt + column count | 1775414816 = 2026-04-05T18:46:56Z; 16 cols | exact; staleness still live 2026-07-16 | YES |
| 7 | `returnCountOnly=true` on nysp/nysp_sd/nylh/nyzma (C3 reproduction) | 95 / 336 / 14 / 1,414 | 95 / 336 / 14 / 1414 — cap-exceedance hazard independently reproduced | YES |

## Corrections C1–C7 verification

- C1 APPLIED (doc:30, doc:84; ztldb.json fallback_source + OQ-1; search-evidenced ZTLDB page URL correctly keeps its marker).
- **C2 PARTIALLY APPLIED → D1**: doc carries viewLastModified (doc:48/170/178) but `grep viewLastModified docs/research/source-registry-drafts/` → zero hits; zoning-features.json record 2 (:77, :83, :88, :97) still claims "Socrata timestamps unusable for freshness" — superseded by C2.
- C3 APPLIED (doc:61–66; zoning-features.json feature_counts + CAP-EXCEEDANCE HAZARD; counts re-reproduced live).
- C4 APPLIED (doc:126; ztldb.json:29,:60). C5 APPLIED (doc:144, typo preserved + third sentence). C6 APPLIED (doc:68, doc OQ-9 row; zoning-features.json:25). C7 APPLIED (doc:149, OQ-10 row; zoning-features.json accuracy).

## Coherence pass

All four remaining `[NEEDS G1 RE-VERIFICATION]` markers legitimate (discipline definition, legacy page URL, ZTLDB page URL with explicit marker-stands note, Z14 register row). No stale markers contradict resolved items — the M1-T001 D1–D3 defect class is absent. OQ ledger matches G1 adjudication exactly (OQ-9/OQ-10 RESOLVED; OQ-1/2/3/4/5/6/7/8/11 OPEN).

## Owner-directed invariants — all intact in doc AND registry drafts

1. Generic pagination mandatory on every ArcGIS layer (doc:66; zoning-features.json:45–46), hazard reproduced live.
2. zoning_district_1 not a closed enum (doc:126; ztldb.json:29,:60).
3. ZTLDB health_status degraded_suspected with full staleness evidence chain; rowsUpdatedAt re-verified live.
4. Not-for-lot-level warning verbatim in doc:20/98 and zoning-features.json:26.
5. All 403/browser-only and release-boundary unknowns OPEN and unguessed; odd `zoning-map-index` link target recorded as-is.

## Carry-forwards for the connector packets

1. Generic resultOffset paging on all six layers; exercise OQ-11 (f=geojson/paging) at build (ZF-F4).
2. ZTLDB staleness guard (rowsUpdatedAt age > ~45 days); monthly-boundary observation on/after 2026-07-27 (OQ-3; OQ-4 via viewLastModified).
3. ZD1 open-enum tolerance; "/"-joined special-district parser (OQ-8); PARK caveat flag; schema from columns array only; BBL/block/lot string normalization.
4. OQ-1/OQ-2 browser-capable capture required before any BYTES bulk import — bundle with M1-T001 OQ-4/OQ-10; REJECT any packet that guesses BYTES URLs/shapefile names.
5. OQ-5/OQ-7 (five unread metadata PDFs; nyzma STATUS/LUCATS/EFFECTIVE domains) before the pending_land_use_actions connector.
6. ±20 ft accuracy → near-boundary splits non-authoritative; conflict-engine three-way check (ZTLDB vs PLUTO vs live nyzd intersection).
7. OQ-6 version stamping (dataLastEditDate + retrieval timestamp; confirm YYYYMM lockstep at a release boundary). Socrata app token = human action at build.

## Defects

1. **D1 (minor)** — `zoning-features.json` record 2 (`nyc-dcp-zoning-features-blob`): C2 not propagated. known_limitations still says the only blob signals are the description string and content hash; update_frequency/connector_implementation/OQ-4 likewise lack `viewLastModified` (1779809507 = 2026-05-26T15:31:47Z, primary polling signal). Risk if unfixed: the blob snapshotter would be contracted polling only the stale description string. Fix: one-record editorial fixup at acceptance.

## Reviewer conclusion

**PASS.** 7/7 live re-runs identical to claims. Six of seven corrections fully applied; C2 missed only in registry record 2 (D1). No guessed schema, endpoint, unit, or legal value; deliverables sufficient to contract the M2 connector tasks without re-research, with the seven carry-forwards written into their packets. Hygiene clean (KB-scale text only). Carry-forwards persisted in reviewer memory (`project_m1-t003-g3-carryforward.md`).
