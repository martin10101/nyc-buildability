# The eleven options and the ZR sections each needs

**Unreviewed draft (ADR-007).** The eleven options and their order are defined in code at
`services/api/app/drawings/report/options.py` (`ELEVEN_OPTIONS`, lines 21-33), matching
`docs/plans/FEASIBILITY_REPORT_SECTION_MAP_2026-10-06.md` line 168 and
`docs/design/ARCHITECT_PRESENTATION_CONTRACT.md` row 3. "captured" and "handled" states are from
`benchmark-r6b-sections.json`. Nothing here is Verified; no option is called compliant, buildable, or
feasible. Eligibility determinations (affordable / senior / UAP / shared housing) are legal
determinations the program does not make.

Legend: **[C]** captured · **[NC]** NOT CAPTURED · **[H]** handled by a rule file · **[nH]** not handled.

### 1 — Standard residences
The as-of-right standard-residence floor area and envelope on the R6B lot.
- 23-22 FAR [C][H] · 23-432 height table [C][H] · 23-362 lot coverage [C][H] · 23-344(a) rear-yard corner
  waiver [C][H] · 23-52 dwelling units [C][H] · 11-25 suffix [C][H]
- 23-431 street wall [C][nH] · 23-433 setback [C][nH] · 23-342/23-343 rear-yard baseline/equivalent
  [C][nH] · 23-335 side yard [C][nH]

### 2 — Qualifying affordable housing (incl. UAP)
A legal determination of qualifying affordable housing (the program does not make it), then the higher FAR
column and 65-ft height.
- 12-10 "qualifying affordable housing" [C] (eligibility, not computed) · 23-154 UAP [NC][nH] (HTTP 403;
  FAR consequence flows through 23-22's 2nd column; exact R6B wording not sure)
- 23-22 2nd column [C][H] · 23-432 qualifying column (R6B 45/65 ft) [C][H]
- plus the whole option 1 base envelope (same handled / not-handled split)
- **Second pass → `options/option-02-03-affordable-and-senior-housing.md`.** 23-154 UAP: still
  ACCESS BLOCKED (HTTP 403 on WebFetch and the browser-UA GET fallback, 2026-10-14); the
  substantive UAP/affordable rules are in Article II Chapter 7 (27-111 defines UAP/MIH/regulatory
  agreement, cites 23-22/23-432 for the on-site rate and 23-154 only for the Offsite Option) —
  27-111/27-131/27-133/27-14/27-151 + Appendix F are CAPTURED (M3-T008). 23-22 2nd column (R6B 2.40, no
  footnote) and 23-432 qualifying (R6B 45/65) CONFIRMED against the snapshots. Still open: §23-154
  text (print/PDF node); option 2's unit-count dividend; the UAP
  income-index band.

### 3 — Qualifying senior housing
A legal determination of qualifying senior housing, the higher FAR/height, and the no-dwelling-unit-factor
branch.
- 12-10 "qualifying senior housing" [C] (eligibility, not computed)
- 23-22 2nd column [C][H] · 23-432 qualifying column [C][H] · 23-52 senior no-factor branch [C][H]
- plus the option 1 base envelope
- **Second pass → `options/option-02-03-affordable-and-senior-housing.md`.** 23-52(a)(2) senior
  no-factor branch CONFIRMED against the snapshot; the senior sub-terms (affordable independent
  residences for seniors; long-term care facility) are §12-10 general definitions, CAPTURED (M3-T008).
  Still open: a long-term care facility needs NYS Department of Health
  licensure (an applicant fact, not decided).

### 4 — More, smaller apartments
The maximum unit count at the same floor area, then a preliminary small-unit estimate.
- 23-52 dwelling-unit factor 680 [C][H] · 12-10 "special density areas" [C] (NB-05: lot 70 is NOT in a
  special density area, so the 680 factor applies and the no-factor branch does not help this lot)
- the realistic small-unit estimate is
  `services/api/app/scenario/three_answers/preliminary_apartment_estimate.py` (an estimate, not a rule);
  the section map notes option 4 cannot be shown before that estimate is built

### 5 — Ground-floor shops with residences above
Confirm the C2-2 overlay permits the retail use, add commercial overlay FAR, and combine commercial +
residential floor area in one mixed building.
- 32-131 UG III / 32-161 UG VI use permission [C][nH]
- 33-12 / 33-121 overlay commercial FAR keyed to underlying R6B [C][nH]
- 35-30 / 35-31 mixed-building floor-area combination (= greatest single-use FAR) [C][nH] · 35-32 [C][nH]
- 35-63 / 35-631 / 35-632 overlay street-wall + height/setback [C][nH] · 34-11 / 34-24 / 34-232 [C][nH]
- residential part uses the option 1 base envelope · catalogue add-on `ground_floor_commercial`
  `rule_ids=()` → [nH]
- Reading (unreviewed draft; not sure on the exact combined-FAR ceiling for this lot): a C2-2 overlay in
  R6B permits local retail (UG III/VI) at grade with residences above; residential FAR stays the R6B
  23-22 figure, commercial overlay FAR is the 33-121 table value, and 35-31 caps the sum at the greatest
  single-use FAR. None of the commercial/mixed side is rule-backed.
- **Second pass → `options/option-05-shops-with-residences.md`.** CORRECTED: the shops use is
  **32-161 (Use Group VI)**, not 32-131 (which is Use Group III = community facilities) — checked
  against the snapshots; add the floors rule 32-421 (CAPTURED). 33-121 R6B row A/B/C all 2.00
  and the 35-31 greatest-single-use cap CONFIRMED against the snapshots; 35-32 does NOT reach R6B
  (R1-R5 only, checked). Still open: the actual mapped overlay line at the lot (76-131 default
  150 ft; not read — nothing assumed about coverage); whether C2-2 is a "select commercial
  overlay" (32-421); the single mixed-building rear-yard rule; 32-421/33-26/33-301 CAPTURED (M3-T010),
  33-27/33-28/33-30 CAPTURED (M3-T011).

### 6 — Residences with a community facility
Confirm the community-facility use is permitted, add community-facility FAR, and combine with residential
floor area.
- 24-11 community-facility FAR [C][nH] (H6's official read: R6B FAR 2.00, coverage 80/60, last amended
  12/5/2024) · 24-111 [C][nH] (not sure whether it changes the R6B figure)
- 35-31 / 35-33 mixed-building floor-area combination [C][nH]
- residential part uses the option 1 base envelope · catalogue add-on `community_facility_floor_area`
  `rule_ids=()` → [nH]
- **Second pass → `options/option-06-07-community-facility.md`.** 24-11 R6B CF FAR 2.00, coverage
  80/60 CONFIRMED on the official page (now CAPTURED, M3-T009); 24-111 does NOT change
  the R6B figure (suffixed R6-R12 defer to 24-11). CORRECTED: 24-162 and 35-33 both EXCLUDE R6B
  (checked: 24-162 opening excepts R6B; 35-33 scope is R6 without a letter suffix), so the
  combination ceiling is the plain greatest-single-use FAR (35-31 / 24-161). Still open: whether
  24-161 or 35-31 is the operative citation for option 6; the Article II Chapter 4
  sections (24-11/24-111/24-161/24-163, the height/yard sections) are now CAPTURED (M3-T009); Use Group III use detail.

### 7 — A community facility alone
The community-facility FAR and the community-facility bulk envelope on the R6B lot.
- 24-11 FAR 2.00 + coverage 80/60 [C][nH]
- community-facility height/setback/yard sections in Article II Chapter 4 [C][nH] — captured M3-T009
  (24-04/24-33/24-34/24-35/24-36/24-391/24-52/24-522/24-56); handling under the 2024-12-05 text still open
- **Second pass → `options/option-06-07-community-facility.md`.** RESOLVED by reading (now all
  CAPTURED, M3-T009): FAR/coverage 24-11 (R6B 2.00; 80/60) + 24-111; height/setback routed
  by 24-04 to the residence chain 23-43 inclusive for suffixed R6B (24-52 routing, 24-522 generic
  no-R6B-row, 24-56 special areas only); yards 24-34 (no front), 24-35 (no side; ≥8 ft if
  provided), 24-36 (30 ft rear), 24-391 (corner waiver), 24-33 (obstructions). These Chapter 4
  sections and 24-163 are now captured (M3-T009); handling for combined lots still open.

### 8 — A split lot with two buildings
Model two separate buildings with per-building and per-site figures kept apart.
- 12-10 "zoning lot" [C] (used for scope; no computed subdivision/aggregation rule)
- **OPEN QUESTION — what "split lot" means:**
  (a) **two buildings on one zoning lot** → 35-01 applies Chapter-5 bulk where a single zoning lot has
      multiple buildings with residential + commercial/CF use [C][nH]; the normal R6B bulk applies per
      building, but there is no two-building modelling rule; or
  (b) **a zoning lot divided by a zoning-district boundary** → the governing family is ZR Article VII
      Chapter 7, 77-00 [C][nH], with 36-64 [C][nH] as the C-district counterpart.
  The producer is **not sure** which reading the sample intends. Next step: read the sample "split lot"
  page and the official 77-00 vs multiple-buildings provisions. **This question stays open.**
- **Second pass → `options/option-08-split-lot.md`.** The two readings are kept apart: A.1 subdivide
  into two independent zoning lots (12-10 zoning-lot subdivision clause, captured) and A.2 two
  buildings on one zoning lot (23-371/23-372 and the 23-35 court group 23-351/23-352/23-353, all CAPTURED M3-T010; 35-01 captured);
  B a zoning lot crossed by a district boundary (Article VII Chapter 7 — 77-01/77-11/77-12/77-21/
  77-211/77-22/77-24/77-25/77-26/77-27/77-28, all CAPTURED M3-T015, bodies also read live). CORRECTED: 36-64
  is only a loading-berth pointer into Chapter 7 (checked), not a general C-district rule. The
  sample is Reading A.1 (pp. 2, 5, 82-87; "Split Zone = No"). Still open and UNRESOLVED: whether a
  C2-2 overlay edge is a Chapter-7 district boundary (not settled by the text — both readings
  given); the actual mapped overlay line at the lot (76-131 default 150 ft > 100 ft lot depth, but
  not read — nothing assumed about coverage); which reading option 8 intends (owner question).

### 9 — Shared housing
The shared-housing use (dwelling units with shared kitchens / rooming units re-legalized by City of Yes)
and its density.
- 12-10 "rooming unit" [C] (the 12-10 "dwelling unit" text extends dwelling-unit regs to rooming units
  unless specifically stated)
- 23-52 dwelling-unit factor applied to rooming units [C][H] (not sure it fully models the shared-housing
  case)
- the dedicated shared-housing **use permission and density/standards** sections are now identified and
  **captured** [C][nH] in the second pass below (23-51, 22-12/22-121/22-122, 32-121, 54-311); the first
  pass had not identified them. Section map: "Shared housing needs its own use and parking rules." Next
  step: the City-of-Yes shared-housing operating framework (pending 2027 legislation), then handling.
- **Second pass → `options/option-09-shared-housing.md`.** "Shared housing" is not a ZR term; the
  ZR regulates it as "rooming unit". CORRECTED: 23-51 takes rooming units OUT of the density
  regulations (checked on the official page: "the provisions of this Section shall not apply to
  #rooming units#"), so the 23-52 680 factor does not cap them; 54-311 attaches the factor only on
  conversion to dwelling units. Use permission: 22-12/22-121 (UG II in R6, via 11-25 for the
  suffix) and 32-121 (residences in C1/C2); 22-122 bars rooming units only in single-/two-family
  districts (not R6B); residential bulk follows the residence district via 34-11 (captured). 22-12 /
  22-121 / 22-122 / 23-51 / 32-121 / 54-311 CAPTURED (M3-T010); 22-131…22-135 CAPTURED (M3-T011). Still open: the modern
  shared-housing-suite framework is pending 2027 legislation; occupancy is set outside the ZR
  (MDL/HMC/Building Code); the r6b_dwelling_units rule does not yet encode the 23-51 exclusion.

### 10 — Shared housing with the parking waiver
Everything in option 9, plus the residential parking requirement and its elimination/waiver in the transit
zone.
- 25-20 required parking for residences [C][nH] · 25-211 / 25-212 (Inner Transit Zone) [C][nH]
- 25-22 Outer Transit Zone / 25-221 / 25-222 [C][nH] · 25-23 beyond the Greater Transit Zone / 25-231 /
  25-232 [C][nH]
- 66-11 'mass transit station' [C][nH] · 12-10 "Transit Zone, Greater" / "Transit Zone, Outer" [C]
  (membership is a recorded value) · Appendix I transit-zone maps [C][nH]
- the parking sections also reference the parking-removal special permits 73-432 / 73-433 (reduce existing
  parking) [C], 75-31 (authorization to remove) [C], 74-52 (special permit to remove) [C] — captured but
  project-specific (CPC/BSA); recorded in each section's `cross_references_out`, not followed as entries.
- Reading (unreviewed draft): the parking "waiver" is the City-of-Yes elimination/reduction of parking
  minimums inside the transit zones; parking and transit-zone geography are well captured but no rule
  computes them.
- **Second pass → `options/option-10-parking-and-transit-zone.md`** (and a parking/loading/bicycle
  line per option 1-11, DB-180). Transit-zone membership is a RECORDED value: **Outer Transit
  Zone** (reference `step-p5-worked.json#transit-zone-value`; DCP dataset `6ztr-wgff` 2025-12-16
  agrees), labelled unreviewed. In the Outer Transit Zone, 25-221 requires NO parking for rooming
  units created after 3/22/2016; dwelling units follow 25-222 (R6 row 25% Col A, 15-space Col C
  waiver, lot-width ≤25 ft waiver). CORRECTED: 66-11 is NOT the transit-zone definition (it is
  Article VI Ch 6 "Definitions", TOD; the 12-10 terms are the transit-zone definition). Still open:
  rooming-unit vs dwelling-unit classification; "Transit Zone, Inner", 25-24 and 25-241 CAPTURED
  (M3-T010), CF parking 25-30+ NOT CAPTURED; whether an overlay triggers the same commercial parking as a stand-alone
  district, and the overlay's extent on the lot.

### 11 — All programs combined
The best supported, compatible combination of add-ons toward a stated goal (default: most residential
floor area).
- no single ZR section; combination ceilings are 23-20 multi-use cap [C][nH] and 35-31 mixed-building cap
  [C][nH]
- best-combination logic lives in the scenario engine (`services/api/app/scenario/ranking.py`,
  `comparison.py`, the `best_combination` results key), **not** a rule file
- inherits every not-handled / not-captured family from options 2-10, so it cannot be fully worked until
  those are rule-backed
- **Second pass → `options/option-11-combinations.md`.** The combination ceiling is the greatest
  single-use FAR on the zoning lot (35-31; 23-20 in the same words — two independent reference
  readers agree; `step-p5-worked.json#mixed-use-floor-area-combination`), with shared floor area
  attributed proportionally on a base of total floor area less the shared portion. CORRECTED on
  capture: 23-20, 33-12, 33-121, 35-30, 35-31, 35-32, 35-33 are all CAPTURED (the folder decides;
  the first-pass `[C]`/`[NC]` flags from `benchmark-r6b-sections.json` were partly wrong). 35-32
  and 35-33 do not reach R6B. Still open: 24-11/24-111 now CAPTURED (M3-T009); whether a development may hold
  both affordable and senior; the full 35-31 carve-out sweep; option 11 currently reduces to the
  single best qualifying-housing program; inherits every open item of options 2-10.

## Summary — not-handled sections shared by several options

- 23-335 side yard — options 1, 2, 3, 4, 9, 10, 11
- 23-20 / 35-31 multi-use & mixed-building FAR cap — options 5, 6, 11
- 24-11 / 24-111 community-facility FAR (CAPTURED) — options 6, 7, 11
- 33-12 / 33-121 overlay commercial/CF FAR — options 5, 11
- 35-30 / 35-31 / 35-32 / 35-33 mixed-building floor area — options 5, 6, 11
- 35-63 / 35-631 / 35-632 mixed-building height/street-wall; 34-11 / 34-24 / 34-232 residential-bulk
  modifications — options 5, 6, 11
- 32-131 / 32-161 commercial use permission — options 5, 11
- 25-xx parking + 66-11 + Appendix I transit zone — options 10, 11
- 23-154 UAP (NOT CAPTURED) — options 2, 11
- shared-housing use/density/parking sections (unidentified) — options 9, 10, 11
- two-building / split-lot modelling (12-10 zoning lot captured; 77-00 captured, M3-T015, under reading (b)) —
  options 8, 11
