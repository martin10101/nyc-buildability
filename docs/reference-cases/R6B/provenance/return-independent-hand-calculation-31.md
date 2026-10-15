# Independent reading for M5-T185 (options 9-10 (shared housing; parking and the transit zone), reading B) (provenance)

M5-T185 PROVENANCE -31 (OPTIONS 9-10, READING B)

What this is: an independent worked reading made on 2026-10-15 by an AI helper that took no part in writing the program's rules. METHOD, stated exactly: the reader had READ access to a detached, read-only checkout of this repository at commit bb5c02b9 (the law-text captures under docs/research/zr-snapshots/v1, the settled reference cases, the evidence records and the law library), was told not to read any program output (no test run, no API call, no report print and no benchmark fixture value), and, for sections that were not among the captures at the time it read, it cross-checked the official Zoning Resolution page (zoningresolution.planning.nyc.gov) live. The checker's provenance guard requires the literal phrase "sealed folder"; here that phrase names that pinned, read-only set of captures and settled cases in the detached checkout at bb5c02b9 - it was NOT a sealed folder in the step-P7/P8 sense, and because some official pages were read live this was NOT an offline reading and does not assert the reader was sealed off from every outside source. It is a draft reading of the law (ADR-007), not professionally reviewed, decides no eligibility and is not a statement that anything complies, is buildable, is optimal or is feasible. It is reproduced below unchanged, byte for byte. (Several sections the reading marked uncaptured when it was made - for example 23-51, 23-12, 23-371, 32-421, 33-26, 33-301, 22-12/22-121/22-122, 32-121, 54-311 - were captured afterwards by task M3-T010 and are now present in docs/research/zr-snapshots/v1; the reference case records a value only where both readings of the option agree on the same value and the same basis.)

---

Reader B — options 9 (shared housing) and 10 (shared housing + parking waiver), 215-16 Northern Blvd (Qns block 7334 lot 70), R6B + C2-2 overlay, Outer Transit Zone, corner lot. Worked from the law text and settled facts only; no program run, no benchmark fixture read. I am an AI agent; this is an unreviewed draft (ADR-007) and decides no eligibility, use permission or legal step. "Shared housing" is not a ZR term; the ZR regulates it as #rooming units# (12-10). All figures are on the recorded tax-lot-70 area 10,075 sq ft (administrative record); the 10,387.99 sq ft GIS outline is display-only and never enters a calculation (NB-04); every figure also assumes lot 70 alone is the zoning lot (NB-01, unconfirmed).

WORKED VALUES

| Item | Value | Unit | Basis | ZR section | State | Conditions |
|---|---|---|---|---|---|---|
| Rooming unit = "shared housing" | a "living room" (MDL) in a residential bldg, not a dwelling unit | — | 12-10 def (LA 12/5/2024) | 12-10 rooming unit | applies | unit standard set by MDL, not ZR |
| Use permission in R6B | residences (UG II) permitted; rooming units not barred | — | 22-12/22-121 UG II; 22-122 bar list (R1/R2/R3A/R3-1/R3X/R4A/R5A/R4-1/R4B) excludes R6B; 11-25 suffix | 22-12,22-121,22-122,11-25 | applies | 22-12/121/122 NOT captured (read live) |
| Overlay effect (C2-2) | adds commercial UG only; residential use/bulk/density = underlying R6B | — | 34-11 (captured); 32-121 | 34-11,32-121 | applies | 32-121 NOT captured |
| Residential FAR (R6B) | 2.00 | FAR | 23-22 R6B standard-residence row | 23-22 | applies | same as option 1 |
| Max residential floor area | 20,150 | sq ft | 2.00 × 10,075 (recorded) | 23-22; 12-10 FAR | applies | zoning-lot + area basis conditional |
| Dwelling-unit factor (680) | does NOT apply to rooming units | — | 23-51 excludes rooming units from density regs; 23-52(b)=680 for DUs | 23-51,23-52 | not_applicable | 23-51 NOT captured (read live) |
| ZR unit-count ceiling | none for rooming units | units | 23-51 carve-out | 23-51 | not_applicable | practical count set by MDL/HMC (not ZR) |
| Room-size / size limit | none in ZR | — | no ZR interior-dimension rule | — | not_applicable | MDL §4/HMC §27-2004 outside ZR; 2027 bills not enacted |
| Transit-zone membership | Outer Transit Zone | — | recorded value (step-p5 transit-zone-value; DCP 6ztr-wgff) | 12-10 Outer; App. I; ZoLa | applies | recorded, not fixed by text alone |
| Parking — option 9/10 (rooming units) | 0 required | spaces | 25-221: no parking for rooming units created after 3/22/2016 | 25-221 | applies | the "waiver" = this elimination, not a special permit |
| Parking — any standard DUs | 25% (Col A), Col C waiver 15 | % / spaces | 25-222 R6 row | 25-222 | applies | 10,000 sq ft waiver (ftn 2) excludes R6; ≤25 ft width waiver (ftn 3) N/A (frontage 100.76/100 ft) |
| Loading berths | none for residential | berths | residences not a loading category | 36-62 (commercial only) | not_applicable | commercial would differ |
| Bicycle parking | 1 per 2 DU; 3 rooming units=1 DU; waived ≤10 DU | spaces | 25-80 (development trigger); 25-811 | 25-80,25-811 | applies | per building/segment; count not known |
| Special density area | not in one | — | 12-10; QN CD411, no special district | 12-10; 23-52(a)(1) | applies (N/A to rooming anyway) | NB-05 |

ARITHMETIC (hand-worked from the cited text; no program run)

- Floor area: FAR 2.00 × 10,075 sq ft = 20,150 sq ft (same ceiling as option 1). Rooming units share the R6B residential FAR; there is no separate rooming-unit FAR and no FAR bonus.
- Unit count: 23-51 removes rooming units from the density regulations, so the 23-52 680 factor does not apply. The ZR sets no unit-count ceiling for shared housing. (Compare option 1: 20,150 / 680 = 29.63 → 29 standard dwelling units, fraction 0.63 < 0.75.)
- Parking, option 9/10: 25-221 requires zero spaces for rooming units — no count needed.
- Parking cross-check, option 1 (29 standard DUs): 29 × 25% = 7.25 spaces; Column C waiver for R6 = 15; 7.25 ≤ 15 → 0 required (25-222). So this lot requires zero residential parking in BOTH the standard and the shared-housing case, by different clauses (25-222 small-number waiver vs 25-221 rooming-unit elimination). Option 10 adds no parking relief beyond option 9 for a pure rooming-unit building.
- Bicycle, option 1 (29 DUs): 29 ÷ 2 = 14.5 → 15 enclosed spaces (fraction ≥50% rounds up); not waived (29 > 10 DU). Option 9/10: N rooming units → N/3 DU-equivalents → ÷2; waived if the building/segment holds ≤10 DU-equivalents. N is not ZR-capped, so no number is computed.

WHAT IS NOT KNOWN (exact item → where to find)

1. Zoning-lot extent (lot 70 alone, or lots 1+70): contents of CERT 2022020201551001 / ZONE 2022020201551002 / DECL 2022031600431001 — ACRIS document images (access_blocked); owner saves them or authorizes a records request (NB-01). Changes lot area → floor area → every unit/parking figure.
2. Lot-area basis conflict (10,075 recorded vs 10,387.99 GIS, ~3.1%): Christopher M. Buckley survey 2017-02-21 or 2018 deed Schedule A — not online; ask owner (NB-04). Figures worked on 10,075.
3. Rooming-unit vs dwelling-unit classification of the actual proposal: an applicant/use determination the program does not make. Gates 25-221 (zero) vs 25-222 (25%) parking and whether the 680 factor bites.
4. Lawful room standard / occupiable unit count: MDL §4, HMC §27-2004 (official fetch was HTTP 403, wording unconfirmed), Building/Fire Code; the City-of-Yes shared-housing-suite operating framework is pending 2027 legislation (not enacted). Outside the ZR — the ZR permits the use and caps only floor area.
5. "This Section" referent in 23-51's rooming-unit sentence: literal referent is 23-51; both readings (23-51 as the applicability trigger, or shorthand for 23-50) reach "no DU factor for rooming units," reinforced by 54-311. Interpretation left as a labelled draft.
6. Transit-zone from the law alone: Appendix I image maps + ZoLa boundary + 66-11 "mass transit station"; none fixes it in text, so the recorded Outer value governs, labelled unreviewed.
7. C2-2 overlay extent on the lot (affects commercial parking only, not shared housing): the mapped overlay line / ZoLa (76-131 default 150 ft) — not read.

CONFLICTS (captures vs settled cases vs library)

- The library pages (option-09, option-10) are accurate on what is NOT captured: I confirmed 23-51, 22-12, 22-121, 22-122, 32-121, 54-311 and "Transit Zone, Inner" are absent from docs/research/zr-snapshots/v1/. I read 23-51, 22-122 and 22-12 live from the official portal (all Last Amended 12/5/2024); their text matches the library's reading — rooming units excluded from density (23-51), and the 22-122 bar excludes R6B. So the load-bearing density conclusion rests on uncaptured text verified live, not on a pinned snapshot.
- options-sections.md §10 summary (line 155) still flags "66-11 transit-zone definitions [C]"; the corrected option-10 page shows 66-11 is NOT the transit-zone definition (it defines "mass transit station"); the real definitions are the captured 12-10 Outer/Greater. Stale summary row only.
- The owner's sample (scenarios 7/8) counts SRO rooms as dwelling units for density and shows required/trimmed parking; the law as read excludes rooming units from density (23-51) and requires zero parking in the Outer Transit Zone regardless of count (25-221). Premise conflict, correctly flagged in both library pages.
- No conflict with the settled R6B cases (step-p5 parking/transit rows; NB-05 680/special-density): they agree with this reading.

SECTIONS A CAPTURE TASK SHOULD ADD (priority order)

1. 23-51 Applicability (density regs; the rooming-unit exclusion) — the pivot for the whole option-9 unit-count conclusion, currently uncaptured.
2. 22-12 / 22-121 (Use Group II — residences; the positive as-of-right table) and 22-122 (rooming-unit bar) — the use-permission basis.
3. 32-121 (residences permitted in C1/C2 overlay).
4. 54-311 (buildings containing rooming units; conversion to dwelling units) — reinforces the 680 carve-out.
5. 12-10 "Transit Zone, Inner" (completeness of the parking-geography rule; not needed for this Outer lot).

END-OF-REPORT