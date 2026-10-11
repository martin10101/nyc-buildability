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

### 3 — Qualifying senior housing
A legal determination of qualifying senior housing, the higher FAR/height, and the no-dwelling-unit-factor
branch.
- 12-10 "qualifying senior housing" [C] (eligibility, not computed)
- 23-22 2nd column [C][H] · 23-432 qualifying column [C][H] · 23-52 senior no-factor branch [C][H]
- plus the option 1 base envelope

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

### 6 — Residences with a community facility
Confirm the community-facility use is permitted, add community-facility FAR, and combine with residential
floor area.
- 24-11 community-facility FAR [NC][nH] (H6's official read: R6B FAR 2.00, coverage 80/60, last amended
  12/5/2024) · 24-111 [NC][nH] (not sure whether it changes the R6B figure)
- 35-31 / 35-33 mixed-building floor-area combination [C][nH]
- residential part uses the option 1 base envelope · catalogue add-on `community_facility_floor_area`
  `rule_ids=()` → [nH]

### 7 — A community facility alone
The community-facility FAR and the community-facility bulk envelope on the R6B lot.
- 24-11 FAR 2.00 + coverage 80/60 [NC][nH]
- community-facility height/setback/yard sections in Article II Chapter 4 [NC][nH] — exact current
  section numbers under the 2024-12-05 text are **not sure**; next step: read them officially

### 8 — A split lot with two buildings
Model two separate buildings with per-building and per-site figures kept apart.
- 12-10 "zoning lot" [C] (used for scope; no computed subdivision/aggregation rule)
- **OPEN QUESTION — what "split lot" means:**
  (a) **two buildings on one zoning lot** → 35-01 applies Chapter-5 bulk where a single zoning lot has
      multiple buildings with residential + commercial/CF use [C][nH]; the normal R6B bulk applies per
      building, but there is no two-building modelling rule; or
  (b) **a zoning lot divided by a zoning-district boundary** → the governing family is ZR Article VII
      Chapter 7, 77-00 [NC][nH], with 36-64 [C][nH] as the C-district counterpart.
  The producer is **not sure** which reading the sample intends. Next step: read the sample "split lot"
  page and the official 77-00 vs multiple-buildings provisions. **This question stays open.**

### 9 — Shared housing
The shared-housing use (dwelling units with shared kitchens / rooming units re-legalized by City of Yes)
and its density.
- 12-10 "rooming unit" [C] (the 12-10 "dwelling unit" text extends dwelling-unit regs to rooming units
  unless specifically stated)
- 23-52 dwelling-unit factor applied to rooming units [C][H] (not sure it fully models the shared-housing
  case)
- the dedicated shared-housing **use permission and density/standards** sections are **not identified in
  the snapshot set** [NC][nH]; exact section numbers **not sure**. Section map: "Shared housing needs its
  own use and parking rules." Next step: resolve the City-of-Yes shared-housing ZR sections, then capture.

### 10 — Shared housing with the parking waiver
Everything in option 9, plus the residential parking requirement and its elimination/waiver in the transit
zone.
- 25-20 required parking for residences [C][nH] · 25-211 / 25-212 (Inner Transit Zone) [C][nH]
- 25-22 Outer Transit Zone / 25-221 / 25-222 [C][nH] · 25-23 beyond the Greater Transit Zone / 25-231 /
  25-232 [C][nH]
- 66-11 transit-zone definitions [C][nH] · 12-10 "Transit Zone, Greater" / "Transit Zone, Outer" [C]
  (membership is a recorded value) · Appendix I transit-zone maps [C][nH]
- the parking sections also reference the parking-removal special permits 73-432 / 73-433 (reduce existing
  parking) [C], 75-31 (authorization to remove) [C], 74-52 (special permit to remove) [C] — captured but
  project-specific (CPC/BSA); recorded in each section's `cross_references_out`, not followed as entries.
- Reading (unreviewed draft): the parking "waiver" is the City-of-Yes elimination/reduction of parking
  minimums inside the transit zones; parking and transit-zone geography are well captured but no rule
  computes them.

### 11 — All programs combined
The best supported, compatible combination of add-ons toward a stated goal (default: most residential
floor area).
- no single ZR section; combination ceilings are 23-20 multi-use cap [C][nH] and 35-31 mixed-building cap
  [C][nH]
- best-combination logic lives in the scenario engine (`services/api/app/scenario/ranking.py`,
  `comparison.py`, the `best_combination` results key), **not** a rule file
- inherits every not-handled / not-captured family from options 2-10, so it cannot be fully worked until
  those are rule-backed

## Summary — not-handled sections shared by several options

- 23-335 side yard — options 1, 2, 3, 4, 9, 10, 11
- 23-20 / 35-31 multi-use & mixed-building FAR cap — options 5, 6, 11
- 24-11 / 24-111 community-facility FAR (NOT CAPTURED) — options 6, 7, 11
- 33-12 / 33-121 overlay commercial/CF FAR — options 5, 11
- 35-30 / 35-31 / 35-32 / 35-33 mixed-building floor area — options 5, 6, 11
- 35-63 / 35-631 / 35-632 mixed-building height/street-wall; 34-11 / 34-24 / 34-232 residential-bulk
  modifications — options 5, 6, 11
- 32-131 / 32-161 commercial use permission — options 5, 11
- 25-xx parking + 66-11 + Appendix I transit zone — options 10, 11
- 23-154 UAP (NOT CAPTURED) — options 2, 11
- shared-housing use/density/parking sections (unidentified) — options 9, 10, 11
- two-building / split-lot modelling (12-10 zoning lot captured; 77-00 NOT CAPTURED under reading (b)) —
  options 8, 11
