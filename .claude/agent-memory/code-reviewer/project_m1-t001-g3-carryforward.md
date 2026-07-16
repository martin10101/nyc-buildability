---
name: m1-t001-g3-carryforward
description: M1-T001 PLUTO/MapPLUTO research G3 PASS (2026-07-16); carry-forwards for PLUTO connector and M2 MapPLUTO bulk import reviews (BBL serialization, drift signature, OQ-4/OQ-10 residuals, 3 stale markers)
metadata:
  type: project
---

M1-T001 (PLUTO/MapPLUTO official-source research) G3 reviewed 2026-07-16: **PASS** at corrections commit `e178adb`. All G1 corrections C1-C6 verified applied; all four SODA spot-tests reproduced LIVE (this reviewer sandbox HAS network — curl to data.cityofnewyork.us works). Report: `project-control/reports/M1-T001-G3-review.md`.

Carry-forwards to check when reviewing the PLUTO connector task (M1/M2):
1. Connector MUST normalize Socrata number-typed BBL (`$select=bbl` returns `"1000010100.00000000"`) to 10-digit strings — reproduced live. Ties into [[m0-t009-g3-carryforward]] residuals (BBL pattern anchoring, normalization obligations).
2. Schema-drift failure signature: HTTP 400 + `errorCode: query.soql.no-such-column`; drift check against the 108-column `api/views/64uk-42ks.json` columns array; SODA omits null fields per record — never infer schema from records.
3. OQ-4 (bulk zip URLs/sizes) and OQ-10 (gdb/borough-shapefile file names) residuals are nyc.gov-403-bound; must close via a browser-capable session BEFORE the M2 MapPLUTO bulk import — fail any task that guesses them. Fetch-evidence E6 contains search-summary names (`Mappluto.gdb`/`Mapplutounclipped.gdb`) that were deliberately NOT promoted; do not let a later task cite them as verified.
4. OQ-6: observe minor-release (26v1.x) propagation to SODA across the next boundary; baseline 26v1 / rowsUpdatedAt 2026-05-28.
5. Three stale-marker minor defects (D1-D3) left at PASS: doc lines 42, 193 ([NEEDS G1 RE-VERIFICATION] markers post-G1) and registry record 2 authentication.notes line 80 — verify cleaned at acceptance or noted in the connector packet.
6. Socrata app token creation is a human-only action at connector build.

**Why:** defects were coherence-only (stale markers whose OQ pointers resolve correctly); all facts verified; PASS without rework per the M0-T005/T009 precedent of recording residuals in memory.
**How to apply:** first checks when reviewing `pluto-soda` connector, MapPLUTO bulk importer, or any task consuming `docs/research/pluto-mappluto-2026-07-16.md` / `source-registry-drafts/pluto-mappluto.json`.
