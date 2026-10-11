# Orchestrator's check of the owner's research on 215-16 Northern Boulevard (2026-10-10)

The owner brought this research back on 2026-10-10, answering the research brief of the same day. Under D-050 it is a discovery aid, not a source of record. This file records what the orchestrator re-checked against the official sources, and what is still unverified. Request entry: `docs/RESEARCH_REQUESTS.md`, RQ-009.

## What is kept here

- The research handoff, unchanged: `../2026-10-10-215-16-northern-research-handoff.md`.
- From the evidence pack, unchanged: `README.md`, `source-manifest.json`, `access-log.json`, `geometry-calculations.json`, `build_geometry.py`, `site-boundary-diagram.png`, and every file under `data/` except the two law pages.
- **Left out on purpose** (each can be fetched again from its URL in `source-manifest.json`; SHA-256 digests are listed there):
  - the official PDFs (four tax maps, City Map CP 4366, the DOB PW1 guide, four Zoning Resolution prints);
  - the rendered page images;
  - `data/law_12_10.html` and `data/law_23_22.html`.

  The Zoning Resolution text the program uses is captured separately under `services/api/app/_zr_snapshots/v1/`.

## Re-checked by the orchestrator on 2026-10-10 (re-fetched from the official source)

| Claim | Official source re-fetched | Result |
|---|---|---|
| Printed tax maps of 2014, 2017 and 2021 (current) | DOF map library, the three URLs in `source-manifest.json` | Byte-identical to the pack (SHA-256 equal). |
| MapPLUTO 26v2 outlines of lots 1, 70, 11 and 61; addresses; recorded areas and frontages | MapPLUTO feature service, block 7334 | Coordinates identical to `geometry-calculations.json` (largest difference 0.000000 ft). Lot 11 is 45-12 215 Place (2,842 sq ft, 28.42 ft front); lot 61 is 45-11 215 Street (2,858 sq ft, 28.58 ft front). |
| ACRIS index: the 2022 CERT, ZONE and DECL are indexed against both lots 1 and 70; the 2016 CERT and ZONE against lot 1; the 2018 deed against lot 70; types and dates | NYC Open Data, ACRIS Real Property Legals and Master | Confirmed. Index entries only; no instrument was read. |
| DOB jobs 421803891 (text "ONE (1) ZONING LOT AND (2) TAX LOTS (LOT #1 & #70)", 9,100 to 39,772 sq ft), 440608941 (39,934 sq ft, permit 04/23/2024), 421199072 (14,150 sq ft), 440655961 (text naming NB 121329641) | NYC Open Data, DOB Job Application Filings | Confirmed. |
| DOF change history: lot apportionment 2017-03-22, transaction 76338, "Survey by Christopher M. Buckley, 2/21/2017" | DOF Digital Tax Map change-history layer | Confirmed for lots 70 and 1. |
| ZR 12-10 "short dimension of a block": "a block frontage where the dimension between any two streets bounding the block measures less than 230 feet" (last amended 12/5/2024) | zoningresolution.planning.nyc.gov, 12-10 page | Confirmed. |
| ZR 23-344(b): "whenever a front lot line of a zoning lot coincides with the street line of the short dimension of a block, no rear yard shall be required within 100 feet of such street line" (last amended 12/5/2024) | zoningresolution.planning.nyc.gov, 23-344 page | Confirmed. The research brief of 2026-10-10 left this paragraph out; the program's rule `r6b_rear_yard_corner_waiver` records that 23-344(b) to (d) are not encoded. |

## Not re-checked yet (still leads)

- The DOB PW1 guide quote (page 14, section 12C). The page image in the pack shows it; the PDF was not re-fetched.
- City Map CP 4366 (1946) and the street-history reading.
- The BSA searches and DOB NOW filings.
- The ZR 23-342, 23-52 and 23-362 readings, and the 0.75 rounding rule of 23-52.
- The research's readings of the law: that 23-344(b) applies to this tract, and that lots 11 and 61 meet the subject along their side lot lines (23-344(c)(3)). These are interpretations, not facts. The program may encode them only as labelled drafts with a link to the law (ADR-007), once the short-block measure and the neighbouring-line classification are deterministic code.

## Not found by anyone yet

- The contents of the 2016 and 2022 CERT, ZONE and DECL instruments, and of the 2018 deed.
- The approved ZD1 and PW1 zoning section of NB 440608941.
- The Buckley survey of 2017-02-21.
- The legal status of the "ALLEY" label crossing lots 1 and 70 on the current tax map.
