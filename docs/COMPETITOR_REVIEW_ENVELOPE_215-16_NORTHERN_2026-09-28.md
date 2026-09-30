# Competitor Review — Envelope Sample Report, 215-16 Northern Blvd (Queens)

| | |
|---|---|
| **Report reviewed** | Envelope (runenvelope.com) public sample: "215-16 Northern Boulevard — Zoning Analysis and Massing Study", 88 pages, report ID ab549f86, compiled Sept 18, 2026 |
| **Report's own sources** | PLUTO 24v4; Zoning Resolution "current through Dec 2024 (incl. City of Yes)" |
| **Reviewed** | 2026-09-28 |
| **Method** | • Full text of all 88 pages.<br>• The labels inside the 3D pictures of five scenarios, read directly from the embedded images.<br>• Automatic cross-check of every scenario (claimed units vs. units drawn, floor areas, elevators, ground-floor use).<br>• Visual check of 19 pages covering every drawing type; the other pages repeat the same plan templates.<br>• Key values checked against the current Zoning Resolution. |
| **How it is produced** | • PDF made in code with ReportLab (a Python library), letter size.<br>• Fonts: Inter, Instrument Serif, IBM Plex Mono.<br>• Floor plans are vector drawings.<br>• Sections and 3D massing are embedded JPEG pictures. Their style suggests a standard Python charting library; not confirmed. |
| **Not checked** | The 485-x tax table (p. 13–14) and the comparable-sales list (p. 15) against outside sources |
| **Suggested path** | `docs/COMPETITOR_REVIEW_ENVELOPE_215-16_NORTHERN_2026-09-28.md` |

Purpose: a test lot and a checklist of mistakes our program must not make. **Severity:** High = changes the answer a buyer or architect would act on; Medium = visible contradiction; Low = cosmetic.

---

## A. Expected values for this lot (our benchmark)

| Item | Expected | Source |
|---|---|---|
| Lot | 10,075 sq ft, about 100.8 × 100 ft, corner lot (215 Place & Northern Blvd) | Public records; report p. 5 |
| Zoning | R6B with a C2-2 commercial overlay | Report p. 5–6 (verify in ZoLa) |
| Maximum residential FAR | 2.00 standard (20,150 sq ft); 2.40 with qualifying affordable or senior housing (24,180 sq ft). R6B has no wide-street increase. | ZR 23-22 |
| Heights | Minimum base 30 ft; maximum base 45 ft; maximum height 55 ft. With qualifying affordable or senior housing: maximum base 45 ft, maximum height 65 ft. | ZR 23-432 |
| Lot coverage | Corner lot: up to 100% | ZR 23-362 |
| Rear yard | Not required within 100 ft of the corner | ZR 23-344(a) |
| Dwelling units (standard) | 20,150 ÷ 680 = 29.63, rounds to 29 (rounds up only at .75 or more) | ZR 23-52 |
| Existing building | 5 stories, about 54,488 sq ft, 38 apartments plus 1 store (existing FAR about 5.4) | Report p. 5; public records |
| Zoning-lot records | A zoning lot description and a certificate recorded for the property (documents dated 2016, recorded 2022) | ACRIS entries via PropertyShark |
| **To verify** | • Parking / transit-zone status.<br>• Whether ground-floor commercial is really required here.<br>• Unit cap with the affordable bonus.<br>• FRESH-zone eligibility. | — |

---

## B. Page-by-page findings

| Page(s) | What the report says | Problem | Type | Severity |
|---|---|---|---|---|
| 1 | "Maximum zoning floor area: 23,136 sq ft" | 1,044 sq ft below the 24,180 sq ft affordable-bonus allowance. It also ignores the larger existing building. | Judgment / omission | High |
| 3 | Maximum FAR 2.00, maximum height 60 ft; "two street frontages may qualify for wide-street bonus" | • The best scenario uses 2.30, contradicting the 2.00 maximum.<br>• 60 ft is not an R6B limit (55, or 65 with affordable housing).<br>• R6B has no wide-street bonus. | Error / contradiction | High |
| 4 | "Site Summary" box | The box is empty; the table appears on page 5 | Layout | Low |
| 5 | Existing building 54,488 sq ft, existing FAR 5.41 | Never used again. No scenario says a new building would be less than half the existing one. | Omission | **High** |
| 5 | "Largest property on block: 8,409 sq ft" | The subject property itself is 54,488 sq ft | Contradiction | Low |
| 6 | Maximum height 60 ft | Wrong for R6B (55, or 65 with affordable housing) | Error | High |
| 7 | Maximum base 50 ft, maximum height 60 ft | Wrong. Correct: base 45; height 55, or 65 with affordable housing. | Error | High |
| 7 | "FRESH zone" FAR bonus annotation | Eligibility for this location is unverified | Unverified | Low |
| 8 | Buildable area 8,032 sq ft; development footprint 10,075 sq ft | Two different footprints on the same page | Contradiction | Medium |
| 9 | Cites ZR 23-151/153/154/155, 23-662, 23-64, 23-153 | These are pre-2024 section numbers; 23-64 is now about recreation space. Heights shown as 50/60. "Coverage 100% (corner lot: 80%)" contradicts itself. | Outdated / error | Medium |
| 10 | "Quality Housing: base 30–45 ft, max 55 ft" | Correct, but contradicts pages 3, 6, 7 and 9 | Contradiction | High |
| 10 | Commercial overlay listed as "+2.00 FAR" | Reads as a bonus, but commercial floor area does not add on top of residential (the report itself says programs aren't additive) | Misleading | Medium |
| 10 | Flood zone X: "freeboard +2 ft … floodproofing required" | Page 5 says construction need not be elevated | Contradiction | Medium |
| 11–12 | Scenarios 1–3: identical numbers | Scenario 1 is 4 floors and 45 ft; scenarios 2–3 are 3 floors and 38 ft, for the same building | Contradiction | Medium |
| 15 | Comparable sales | Mostly one- and two-family houses and a 2017 sale, compared against a 54,488 sq ft mixed-use building | Weak method | Low |
| 16 | "705 sq ft can't be captured … another floor would exceed the 65 ft limit" | The real gap is 1,044 sq ft, and the building shown is 45 ft tall | Error | High |
| 16 | "65 ft includes 5 ft affordable bonus per ZQA" | Wrong explanation: 65 ft is the current City of Yes table value, not a 2016 ZQA bonus | Error | Low |
| 16 (and every scenario) | "Walk-up (no elevator)"; elevators = 0 | Every residential plan and roof drawing shows an elevator and elevator bulkhead | Contradiction | Medium |
| 17 (and every scenario) | "Active ground floor commercial use is required at this location" | Not verified for a C2-2 overlay | Unverified | Medium |
| 18–22 | Floor plans | • Plans are about 103'-10" wide on a 100.8 ft lot, with a 10,388 sq ft floor plate on a 10,075 sq ft lot.<br>• The typical floor is drawn at 8,633 sq ft vs. 8,061 in the schedule.<br>• The ground floor is drawn as shops, but the schedule says residential.<br>• 16 apartments drawn vs. 27 claimed. | Error / contradiction | High |
| 23–29 | Senior housing (100% affordable) | Same numbers as scenario 1. Ground floor drawn as shops. Narrative sentence cut off ("65 ft he…"). | Contradiction / layout | Medium |
| 30–36 | All programs combined | Same building as scenario 1, but the text says another floor would exceed a "60 ft" limit where scenario 1 says 65 | Contradiction | Medium |
| 37–44 | Commercial overlay | Floor 3 is 4,894 sq ft in the schedule but drawn as a full 8,633 sq ft floor. 12 apartments drawn vs. 18 claimed. | Contradiction | Medium |
| 45–51 | Residential + community facility | • Ground floor is community facility in the schedule but drawn as shops.<br>• Floor 3 is 4,840 sq ft in the schedule but drawn at 8,633.<br>• Units match (14 = 14). | Contradiction | Medium |
| 52–57 | Community facility | • "Community facility FAR typically higher than residential": false here (both 2.00).<br>• Uses 1.79 of 2.00 with no reason given.<br>• Ground floor drawn with shops and a "resident lobby" in a building with no residents. | Misleading / contradiction | Medium |
| 58–63 | Shared housing (SRO) | • 16 parking spaces required, while other scenarios claim a transit exemption (0 spaces).<br>• 62 rooms claimed vs. 12 apartments drawn.<br>• 2 stories at 45 ft. | Contradiction | High |
| 64–69 | Shared housing, parking waiver | "Parking waiver (60 DU ≤ 15 threshold)" is garbled. 60 claimed vs. 12 drawn. | Error | Medium |
| 70–75 | Max units | • "2,116 sq ft can't be captured" on a 2-story, 45 ft building.<br>• 29 claimed vs. 11 drawn. | Error | High |
| 76–81 | Max residential | • Identical building to "Max units," with 20 units instead of 29.<br>• "Another floor would exceed 60 ft" on a 45 ft building.<br>• 20 claimed vs. 8 drawn. | Error / duplicate | High |
| 82–87 | Split lot (2 buildings) | • Assumes identical buildings, but one half becomes an interior lot where different yard and coverage rules can apply (ZR 23-342, 23-344, 23-363).<br>• A formal subdivision is required and not mentioned.<br>• Plans reuse the 8,633 sq ft floor on a 5,038 sq ft half-lot.<br>• 18 claimed vs. 8 drawn. | Omission / error | High |
| 88 | PLUTO 24v4; ZR through Dec 2024 | Data two PLUTO releases old (our app already uses 26v2). Special permits, variances and landmarks are excluded, despite "every legal scenario" marketing. | Outdated | Medium |
| All | Zoning lot = tax lot (10,075 sq ft "per PLUTO / tax map") | Recorded zoning lot documents exist for this property; not mentioned | Omission | Medium |
| 3D massing pictures (every scenario checked: 1, 2, 4, 6, 7) | Labels inside the picture | • "Width: 116′" and "Depth: 99′" on a 100.8 × 100 ft lot.<br>• "Rear Yard: 20′" although the report says no rear yard is required.<br>• Every floor labeled "8,032 SF", even where the schedule says 8,061 or 9,270.<br>• The first floor above the cellar is labeled F0, although the schedule uses F0 for the cellar.<br>• The commercial-overlay picture colors the whole ground floor commercial, while its schedule splits it half commercial, half residential.<br>The labels are fixed, not taken from each scenario. | Contradiction | High |

**Summary of units, claimed vs. drawn:**

| Scenario | Claimed | Drawn |
|---|---|---|
| UAP | 27 | 16 |
| Senior housing | 27 | 16 |
| All programs | 27 | 16 |
| Commercial overlay | 18 | 12 |
| Residential + community facility | 14 | 14 ✓ |
| Shared housing (SRO) | 62 | 12 |
| Shared housing, parking waiver | 60 | 12 |
| Max units | 29 | 11 |
| Max residential | 20 | 8 |
| Split lot | 18 | 8 |

Only 1 of 10 residential scenarios matches.

---

## C. What the report gets right

- Base R6B FAR of 2.00 (20,150 sq ft) and the +0.40 affordable-housing bonus.
- The dwelling-unit calculation and its rounding rule.
- Rear yard waived within 100 ft of the corner, and 100% corner-lot coverage.
- The C2-2 overlay, flood zone X, and the E-designation check.
- Lot size and existing building data match public records.
- The floor-by-floor area table format: gross area, deductions, zoning floor area per floor.

---

## D. Test checklist for our program

Each check must pass on this lot before the result is shown to an architect.

| # | Check | Pass when |
|---|---|---|
| C-1 | One source for heights | Every height shown anywhere comes from the same ZR 23-432 lookup: 30 / 45 / 55, or 45 / 65 with affordable housing |
| C-2 | Allowance vs. building | Allowance = 24,180 sq ft (affordable) and 20,150 sq ft (standard). If the fitting building is smaller, the shortfall reason is computed from real constraints and is true. |
| C-3 | Existing building | The existing zoning floor area is shown. When it exceeds the new allowance, one flag says so: "Existing building is larger than today's zoning allows; demolition would reduce floor area." |
| C-4 | Drawings match numbers | Footprint ≤ lot; floors drawn = floors in the table; per-floor areas match; every label inside a picture (width, depth, yards, floor names and areas) is read from the results, never fixed text |
| C-5 | Consistency sweep | An automated check over the whole report finds no value that differs between pages (heights, floors, parking, flood, elevators, units) |
| C-6 | No duplicate options | Two options producing the same building are merged or explained |
| C-7 | Current sources | Data versions shown and current; every ZR citation exists in the current Resolution |
| C-8 | Same rule everywhere | Parking or transit status is applied identically across all options |
| C-9 | Zoning lot | The report states that the lots are the architect's selection and the zoning lot is not verified; recorded zoning lot documents, if known, are flagged |
| C-10 | Lot-split ideas | Each resulting lot is evaluated with its own lot type (corner or interior), and the subdivision requirement is stated |
| C-11 | No template sentences | Explanations such as "another floor would exceed the height limit" appear only when computed as true |
| C-12 | Units in one place | The unit estimate appears once, with its formula, and matches everywhere it is repeated |
