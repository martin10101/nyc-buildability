# Option 10 — parking and the transit zones (plus a parking / loading / bicycle line for every option)

**Unreviewed draft: discovery aid; each item links its source; nothing here is
professionally reviewed (ADR-007).** Readings here are drafts tied to the cited source text.
Where the producer is not sure, it says "not sure". Nothing here is labelled Verified; nothing
here calls a result compliant, buildable, feasible, optimal or preferred. No eligibility is
decided; no parking, loading, bicycle, floor area, height or unit count is computed for the
benchmark lot (a rule's own table percentage or threshold, cited to its section, is not such a
computation).

Second pass of `../options-sections.md` §10 and DB-180; built from helper HF plus the producer's
own checks of the snapshots and the settled R6B reference rows (`step-p5-worked.json#transit-zone-value`,
`#parking-loading-bicycle-sections`, `#parking-loading-bicycle-line-per-option`, the `option-*`
rows).

## Transit-zone membership of the benchmark lot (recorded value, unreviewed)

**215-16 Northern Boulevard (BBL 4073340070) is in the Outer Transit Zone.** This is a recorded
value, not a legal determination:
- **First source (settled reference):** `docs/reference-cases/R6B/cases/step-p5-worked.json#transit-zone-value`
  records the served transit-zone value as **Outer Transit Zone** (a recorded PLUTO attribute, a
  recorded value, not a rule). It notes the captured ZR 12-10 definitions do not independently
  settle the zone — they rest on DCP's ZoLa map, Appendix I and 66-11 — and the Outer Transit Zone
  lies within the Greater Transit Zone.
- **Agreeing dataset reading (HF):** the DCP "Transit Zones" dataset, NYC Open Data id
  `6ztr-wgff`, updated **2025-12-16**, by point-in-polygon on the lot point (lon -73.76681, lat
  40.76033): exactly one polygon, field `transtzone` = "Outer Transit Zone". This agrees with the
  recorded reference value.

The zone would be settled from the law only with Appendix I (image maps), the ZoLa boundary and
66-11 — none of which independently fixes it in text; the recorded value governs, labelled
unreviewed.

## Sections

| id | title | official URL | last amended (page) | capture | handled |
|---|---|---|---|---|---|
| 25-02 | Applicability (Chapter 5 parking/bicycle) | https://zoningresolution.planning.nyc.gov/article-ii/chapter-5/25-02 | 4/22/2009 | zr-25-02.snapshot.json | NOT HANDLED |
| 25-20 | Required Accessory Off-Street Parking Spaces for Residences | https://zoningresolution.planning.nyc.gov/article-ii/chapter-5/25-20 | 12/5/2024 | zr-25-20.snapshot.json | NOT HANDLED |
| 25-211 | General provisions (Inner Transit Zone) | https://zoningresolution.planning.nyc.gov/article-ii/chapter-5/25-211 | 12/5/2024 | zr-25-211.snapshot.json | NOT HANDLED |
| 25-212 | Existing parking requirements in the Inner Transit Zone | https://zoningresolution.planning.nyc.gov/article-ii/chapter-5/25-212 | 12/5/2024 | zr-25-212.snapshot.json | NOT HANDLED |
| 25-221 | General provisions (Outer Transit Zone) | https://zoningresolution.planning.nyc.gov/article-ii/chapter-5/25-221 | 12/5/2024 | zr-25-221.snapshot.json | NOT HANDLED |
| 25-222 | Requirements for developments/enlargements in the Outer Transit Zone | https://zoningresolution.planning.nyc.gov/article-ii/chapter-5/25-222 | 12/5/2024 | zr-25-222.snapshot.json | NOT HANDLED |
| 25-231 / 25-232 | Beyond the Greater Transit Zone — general / requirements | https://zoningresolution.planning.nyc.gov/article-ii/chapter-5/25-231 | 12/5/2024 | zr-25-231 / zr-25-232 | NOT HANDLED |
| 25-80 | Bicycle Parking (applicability / triggers) | https://zoningresolution.planning.nyc.gov/article-ii/chapter-5/25-80 | 12/5/2024 | zr-25-80.snapshot.json | NOT HANDLED |
| 25-81 / 25-811 | Required / Enclosed bicycle parking (residential-CF table) | https://zoningresolution.planning.nyc.gov/article-ii/chapter-5/25-811 | 12/5/2024 | zr-25-81 / zr-25-811 | NOT HANDLED |
| 12-10 | Definitions — "Transit Zone, Greater" / "Transit Zone, Outer" | https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10 | 12/5/2024 | zr-12-10-transit-zone-greater / zr-12-10-transit-zone-outer | NOT HANDLED |
| 12-10 | Definitions — "Transit Zone, Inner" | https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10 | not read | NOT CAPTURED | NOT HANDLED |
| 66-11 | Definitions (Article VI Ch 6 — TOD; defines "mass transit station") | https://zoningresolution.planning.nyc.gov/article-vi/chapter-6/66-11 | 8/14/2025 | zr-66-11.snapshot.json | NOT HANDLED |
| Appendix I | Transit Zones maps (Maps 1-15, image only) | https://zoningresolution.planning.nyc.gov/appendix-i | 11/21/2024 | zr-appendix-i.snapshot.json | NOT HANDLED |
| 36-21 | Commercial/CF parking schedule | https://zoningresolution.planning.nyc.gov/article-iii/chapter-6/36-21 | 12/5/2024 | zr-36-21.snapshot.json | NOT HANDLED |
| 36-231 / 36-232 / 36-25 / 36-24 | Small-number and small-lot parking waivers | https://zoningresolution.planning.nyc.gov/article-iii/chapter-6/36-231 | 6/6/2024 | zr-36-231 / zr-36-232 / zr-36-25 / zr-36-24 | NOT HANDLED |
| 36-31 | Residences in C-districts → surrounding residence district | https://zoningresolution.planning.nyc.gov/article-iii/chapter-6/36-31 | not read | zr-36-31.snapshot.json | NOT HANDLED |
| 36-62 | Required Accessory Off-street Loading Berths | https://zoningresolution.planning.nyc.gov/article-iii/chapter-6/36-62 | 12/5/2024 | zr-36-62.snapshot.json | NOT HANDLED |
| 36-70 / 36-71 / 36-711 | Commercial/CF/residential bicycle table | https://zoningresolution.planning.nyc.gov/article-iii/chapter-6/36-711 | 12/5/2024 | zr-36-70 / zr-36-71 / zr-36-711 | NOT HANDLED |
| 25-30 and following | Community-facility parking in the residence district | — | not read | NOT CAPTURED | NOT HANDLED |
| 73-432 / 73-433 / 74-52 / 75-31 | Special permits / authorizations to reduce or remove parking (cross-reference only; project-specific CPC/BSA) | https://zoningresolution.planning.nyc.gov/article-vii/chapter-3/73-432 | captured | zr-73-432 / zr-73-433 / zr-74-52 / zr-75-31 | NOT HANDLED |

**Correction carried from the first pass (checked by the producer).** The first pass labels
**66-11** "transit-zone definitions". The producer checked the captured snapshot: 66-11 is
Article VI Chapter 6 **"Definitions"** (transit-oriented development; last amended 8/14/2025), and
defines "mass transit station" — it is **not** the parking-geography transit-zone definition. The
Transit Zone definitions are the **12-10** terms "Transit Zone, Greater / Outer / Inner", whose
membership routes to ZoLa's "Transit Zones Parking Geographies" layer with the Appendix I text
controlling on a conflict. 66-11 is relevant only because the Outer-Transit-Zone boundary text
borrows 66-11's "mass transit station". The non-editable first-pass files are addressed under
"Findings outside my files".

## Reading (unreviewed draft)

**Residential parking by geography (25-20 → 25-21 / 25-22 / 25-23).** 25-20 routes a residence's
required accessory off-street parking by transit geography. The settled reference
(`step-p5-worked.json#parking-loading-bicycle-sections`) reads the chain section by section:
- **Inner Transit Zone (25-211):** no parking required for dwelling units or rooming units created
  after 12/5/2024.
- **Outer Transit Zone (25-221) — the benchmark's zone:** parking is required for new dwelling
  units per 25-222; **no parking is required for rooming units created as part of a development or
  enlargement after 3/22/2016.** 25-222's R6 row (snapshot, read by HF): Column A 25% per standard
  dwelling unit; Column B 0% for ancillary / qualifying-senior / income-restricted-affordable
  units; Column C 15-space small-number waiver ("where the calculation results in a number … less
  than or equal to the number in Column C, no parking spaces shall be required"); footnote 3: a
  zoning lot existing on 12/5/2024 with lot width ≤25 ft requires none. (The ≤10,000 sq ft
  lot-area waiver covers R7-2/R8+, not R6.) These are section-cited table values; no count is
  computed for the benchmark.
- **Beyond the Greater Transit Zone (25-231/25-232):** same structure; R6 row 50% Column A — not
  the benchmark's zone.

**The "parking waiver" (what distinguishes option 10 from option 9).** For rooming units the
zero-parking result in the Outer Transit Zone is automatic (25-221, created after 3/22/2016); it
is the City-of-Yes transit-zone elimination, **not** a separate special permit (73-432 / 74-52
only reduce or remove existing/required spaces, and are project-specific CPC/BSA). So if shared
housing = rooming units, options 9 and 10 reach the same parking answer; option 10's label may
instead mean "shared housing shown with the transit-zone parking elimination applied". This is a
library/product reading, not a law question — not sure which the owner intends (carried to
README).

**Commercial / community-facility parking.** Set by Article III Chapter 6: 36-21 schedule (C2-2
row), small-number waiver 36-231 (C2-2 threshold 15 spaces), 36-25 small-use/small-lot, 36-24 no
conforming access. The C2-2 commercial tables carry no transit-zone reduction, so a C2-2 overlay
keeps its schedule regardless of the zone. Community-facility parking in the residence district
itself is 25-30+ (NOT CAPTURED); under the overlay it uses the 36-21 CF rows. **Open nuance (not
sure):** whether a C1/C2 overlay triggers the identical 36-21/36-231 numbers as a stand-alone
C2-2 district — no overlay-specific applicability clause was read.

**Loading berths (36-62).** Residences are not a Loading Requirement Category, so no accessory
loading berth is scheduled for residential use. For C2-2 commercial uses, 36-62 applies; the
"mapped within R1-R6" column's first band is "First 8,000 sq ft: None".

**Bicycle parking (residential 25-80/25-811; commercial-CF 36-70/36-711).** Applies to
developments, ≥50% enlargements, conversions to dwelling units, new dwelling units after
4/22/2009, large parking facilities. Residential rate (25-811): all residences other than
single-family = 1 per 2 dwelling units; affordable independent residences for seniors = 1 per
10,000 sq ft; 3 rooming units count as 1 dwelling unit; waived where a building/building segment
has 10 dwelling units or less. Computed per building/building segment (not per zoning lot).

**Measurement basis and scope.** Residential parking = dwelling-unit (and rooming-unit-equivalent)
count × percentage → spaces, per **zoning lot**; the Column-C/small-number waivers are per zoning
lot. Commercial parking = per sq ft of floor area / lot area / rated capacity. Loading = per sq ft
of floor area in bands → berths. Bicycle = per dwelling unit or per sq ft, per **building/building
segment**. A zoning lot is not the tax lot (NB-01).

**Facts the program needs (with a possible official source).**
- Transit-zone membership — **recorded: Outer Transit Zone** (reference `transit-zone-value`;
  dataset `6ztr-wgff` / ZoLa).
- Dwelling-unit / rooming-unit count and types (standard / ancillary / qualifying senior /
  income-restricted / rooming) — design/program input + a use/eligibility determination the
  program does not make + the 23-52 output.
- Lot width (ft) and whether the zoning lot existed on 12/5/2024 — survey / DOF Digital Tax Map /
  MapPLUTO (25-222 footnote 3; 25-212).
- Lot area (sq ft) — MapPLUTO / DOF / survey (commercial/CF thresholds).
- Commercial/CF floor area by use and Use Group — design input + use permission (32-131/32-161).
- Unit "created" date (TCO/CO) — DOB records (post-2016 / post-2024 cut-offs; 25-212).

## Parking / loading / bicycle — one line per option (options 1 to 11)

Each line names the sections that decide it; benchmark zone = Outer Transit Zone. No count is
computed. Rows 1-7, 9 cite the settled R6B reference rows where they exist; the rest follow HF.

1. **Standard residences** — parking 25-20 → 25-22/25-222 (Outer; R6 Column A 25%, Column C
   15-space waiver, lot-width ≤25 ft waiver, number not checked here); loading none (no residential
   category); bicycle 25-80/25-811 (1 per 2 DU, waived ≤10 DU).
2. **Qualifying affordable housing** — same 25-20 → 25-222; income-restricted units at Column B 0%
   (Outer); reduction only via special permit 73-432; loading none; bicycle 25-811.
3. **Qualifying senior housing** — 25-222 Column B 0% (Outer) for qualifying-senior units; reduction
   via 73-433; loading none; bicycle 25-811 (seniors 1 per 10,000 sq ft).
4. **More, smaller apartments** — 25-20 → 25-222 by DU count (Column A 25%, Column C 15); loading
   none; bicycle 25-811 (1 per 2 DU).
5. **Ground-floor shops with residences above** — residential 25-222 + 25-811; commercial 36-21
   (C2-2 row) + waivers 36-231(<15)/36-25/36-24; loading 36-62 (C2-mapped-within-R6 column; shop
   below 8,000 sq ft = none); commercial bicycle 36-70/36-711 (a ~small shop computes below one,
   waived ≤3). (Reference `option-shops-below-residences`.)
6. **Residences with a community facility** — residential 25-222 + 25-811; CF parking 25-30+ (NOT
   CAPTURED) in the residence district, or 36-21 CF rows + 36-231/36-232 under the overlay; loading
   36-62; CF bicycle 25-811 / 36-711. CF number turns on the use group and size (not given).
   (Reference `option-residences-with-community-facility`.)
7. **A community facility alone** — CF parking 25-30+ (NOT CAPTURED) or 36-21 CF rows + waivers;
   loading 36-62; bicycle 25-811 (CF rows) or 36-711 — each not checked because the CF use group
   and size are not given. (Reference `option-community-facility-alone`.)
8. **A split lot with two buildings** — per each building's use (residential 25-xx / commercial
   36-xx); parking and the Column-C/small-number waivers are per zoning lot and residential bicycle
   per building, so the split-lot scope (one zoning lot vs two vs a district boundary — option 8)
   changes the answer.
9. **Shared housing** — rooming units → 25-221 (Outer): **no parking required** (created after
   3/22/2016); loading none captured for residences; bicycle 25-811 (3 rooming units = 1 DU, 1 per
   2 DU-equivalent, waived ≤10). (Reference `option-rooming-units`.) Depends on the uncaptured
   shared-housing use classification.
10. **Shared housing with the parking waiver** — same as 9 for the benchmark: 25-20 → 25-221 (Outer)
    zero parking for rooming units; any standard dwelling units → 25-222 R6 (25%, Column C 15); the
    "waiver" is the transit-zone / post-2016 rooming-unit elimination, not a separate special permit;
    bicycle 25-811.
11. **All programs combined** — the union of the above: residential 25-20…25-23 + 25-80/25-811;
    commercial 36-21/36-231/36-232/36-25 + 36-62 + 36-70/36-711; CF 25-30+ (NOT CAPTURED) or 36-21;
    per-zoning-lot aggregation of required spaces and waivers (mixed-use parking 36-22, captured
    elsewhere, not read this pass).

**What the owner's sample shows (pointer only).** Sample scenario 8 "SRO, parking waiver"
(pp.64-69) is the same SRO building as scenario 7 but with the unit count trimmed so the project
falls under a parking-waiver threshold and shows zero spaces; scenario 7 keeps the higher room
count and shows required spaces. The sample cites no parking (25-xx) or transit-zone section.
**The sample's premise differs from the law as read:** the ZR requires **no** parking for rooming
units in the Outer Transit Zone regardless of count (25-221), so trimming rooms to claim a waiver
is not what the rooming-unit rule turns on; the 25-222 percentage/15-space waiver is the
dwelling-unit path. Listed under "Questions for the owner".

## What is not sure (each with its next step)
1. **Rooming unit vs dwelling unit for shared housing** — a use classification the program does not
   make and whose ZR sections are uncaptured; it gates which parking line applies (25-221 zero vs
   25-222 percentage). Keep unresolved. Next step: capture the City-of-Yes shared-housing use
   sections (shared with option 9).
2. **"Transit Zone, Inner" definition and 25-24/25-241 special provisions are NOT CAPTURED** (not
   needed for the benchmark, which is Outer; owed for the general rule). Next step: capture the
   12-10 Inner term and 25-241.
3. **Whether a C1/C2 overlay triggers the identical 36-21/36-231 commercial numbers as a
   stand-alone C2-2 district** — no overlay-applicability clause read. And the overlay's **extent
   on the lot** is itself unresolved (HX2: 76-131(b) default 150 ft from the nearest street; the
   actual mapped line / ZoLa / NYCO GIS not read), so how much of the lot carries commercial
   parking at all is not known. Next step: read the overlay applicability for Article III Chapter 6
   and the actual overlay line.
4. **Community-facility parking 25-30+ is NOT CAPTURED.** Next step: capture it (options 6/7/11).
5. **Suffix (not sure):** the 25-222 table uses an unsuffixed "R6" row; the settled reference rows
   `suffix.json` confirm R6B reads the R6 row for FAR/height/coverage/units, but a parking-specific
   applicability clause was not read. Next step: confirm R6B is covered by the unsuffixed "R6"
   parking row.
6. **Byte-identity of dataset 6ztr-wgff vs the live ZoLa layer** — not cross-read. The recorded
   value (Outer) is authoritative; label unreviewed. Next step (if higher assurance wanted):
   cross-read ZoLa for BBL 4073340070.
7. **Owner question** (product, not law): does option 10 differ from option 9 only in showing the
   parking requirement eliminated, or in the housing programme itself? (Carried to README.)
