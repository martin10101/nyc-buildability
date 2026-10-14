# Option 8 — a split lot with two buildings (two readings, kept apart)

**Unreviewed draft: discovery aid; each item links its source; nothing here is
professionally reviewed (ADR-007).** Readings here are drafts tied to the cited source text.
Where the producer is not sure, it says "not sure". Nothing here is labelled Verified; nothing
here calls a result compliant, buildable, feasible, optimal or preferred. No eligibility is
decided; no floor area, height, unit count or parking count is computed for the benchmark lot.

Second pass of `../options-sections.md` §8; built from helpers HD and HX1 plus the producer's own
checks (snapshot of 36-64; the settled R6B reference reading of 23-342/23-344). **The meaning of
"split lot" is two legally different situations; they are kept apart below. Which one the owner's
sample / option 8 intends is an open owner/product question — see the end.**

## Reading A — one tax lot developed as two zoning-lot situations (no district boundary crossing the lot)

### A.1 Subdivide one tax lot into two independent zoning lots
Governing definition: ZR 12-10 "zoning lot" (captured `zr-12-10-zoning-lot.snapshot.json`; the
term's own stamp 2/2/2011). A zoning lot "may be subdivided into two or more zoning lots, provided
that all resulting zoning lots and all buildings thereon shall comply with all of the applicable
provisions of this Resolution" (per HD). After subdivision each resulting zoning lot is a full,
independent zoning lot: FAR, dwelling-unit count (23-52), lot coverage (23-362) and every yard are
measured **per resulting zoning lot**, and the new interior line becomes a lot line (R6B side-yard
treatment under 23-335). Subdivision is an ownership/recording act (recorded metes-and-bounds,
single-fee / party-in-interest conditions), not merely a drawing.

### A.2 Two buildings on one (undivided) zoning lot
Here nothing is divided: FAR, maximum dwelling units (23-52), lot coverage (23-362) and density
are taken for the **whole** zoning lot and shared — there is no per-building floor-area or unit
budget. Extra rules apply only because there are two buildings:

| id | title | official URL | last amended | capture | handled |
|---|---|---|---|---|---|
| 12-10 | Definitions — "zoning lot" (scope / subdivision clause) | https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10 | 2/2/2011 (term) | zr-12-10-zoning-lot.snapshot.json | NOT HANDLED |
| 23-371 | Standard minimum distance between buildings (40 ft under 125 ft) | https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-371 | 12/5/2024 | NOT CAPTURED | NOT HANDLED |
| 23-372 | Distance between legally required windows and lot lines (20 ft) | https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-372 | 12/5/2024 | NOT CAPTURED | NOT HANDLED |
| 23-35 / 23-351 / 23-352 / 23-353 | Court Regulations / obstructions / inner court (≥800 sq ft, ≥20 ft) / outer court | https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-35 | 12/5/2024 | NOT CAPTURED | NOT HANDLED |
| 35-01 | Applicability (multiple buildings on one zoning lot with residential + commercial/CF) | https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-01 | 12/5/2024 | zr-35-01.snapshot.json | NOT HANDLED |
| 23-52 | Maximum Number of Dwelling Units | https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-52 | 12/5/2024 | zr-23-52.snapshot.json | r6b_dwelling_units.rule.json |
| 23-362 | Maximum lot coverage in R6-R12 | https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-362 | 12/5/2024 | zr-23-362.snapshot.json | r6b_lot_coverage.rule.json |
| 23-335 | Side yard requirements R6-R12 | https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-335 | 12/5/2024 | zr-23-335.snapshot.json | NOT HANDLED |

HX1 read the uncaptured distance/court bodies live (23-371: 40 ft between unconnected buildings
below 125 ft; 23-372: 20-ft window-to-wall; 23-352: inner court ≥800 sq ft and ≥20 ft; 23-353:
outer court width ≥ its depth). 35-01 (captured) applies Chapter 5 bulk "where there are multiple
buildings on a single zoning lot and such zoning lot contains a residential use and either a
commercial use or a community facility use" — routing a two-building residential-plus-commercial
case to the 35-30/35-31 combination (the same greatest-single-use cap worked in
`docs/reference-cases/R6B/cases/step-p5-worked.json#mixed-use-floor-area-combination`).

**Note on the dwelling-unit-rounding gain.** The gain the sample claims arises only under A.1
(two independent zoning lots, two separate 23-52 budgets, two roundings); under A.2 the single
shared zoning-lot budget produces no extra rounding. Whether two zoning lots lawfully yield more
total units than one, or whether that double-counts density, is a legal reading — **not sure**;
no figure is computed here.

## Reading B — one zoning lot divided by a zoning-district boundary (Article VII, Chapter 7)

Governing family: ZR Article VII Chapter 7, "Special Provisions for Zoning Lots Divided by
District Boundaries" (none captured; bodies read live by HD/HX1):

| id | title | official URL | last amended | capture | handled |
|---|---|---|---|---|---|
| 77-01 | Applicability of This Chapter | https://zoningresolution.planning.nyc.gov/article-vii/chapter-7/77-01 | 12/15/1961 | NOT CAPTURED | NOT HANDLED |
| 77-11 | Conditions for Application of Use Regulations to Entire Zoning Lot (>50% / 25 ft) | https://zoningresolution.planning.nyc.gov/article-vii/chapter-7/77-11 | 6/29/1989 | NOT CAPTURED | NOT HANDLED |
| 77-12 | Application of Use Regulations Under All Other Conditions | https://zoningresolution.planning.nyc.gov/article-vii/chapter-7/77-12 | 6/25/1964 | NOT CAPTURED | NOT HANDLED |
| 77-21 / 77-211 | General Provisions (bulk) / Conditions for whole-lot bulk | https://zoningresolution.planning.nyc.gov/article-vii/chapter-7/77-21 | 9/27/1962 / 12/5/1990 | NOT CAPTURED | NOT HANDLED |
| 77-22 | Floor Area Ratio (apportion by area %, then sum) | https://zoningresolution.planning.nyc.gov/article-vii/chapter-7/77-22 | 12/5/2024 | NOT CAPTURED | NOT HANDLED |
| 77-24 | Lot Coverage (adjusted maximum) | https://zoningresolution.planning.nyc.gov/article-vii/chapter-7/77-24 | 12/5/2024 | NOT CAPTURED | NOT HANDLED |
| 77-25 | Density Requirements (sum of each portion's permitted units) | https://zoningresolution.planning.nyc.gov/article-vii/chapter-7/77-25 | 12/5/2024 | NOT CAPTURED | NOT HANDLED |
| 77-26 | Minimum Lot Area and Lot Width for Residences (more restrictive governs) | https://zoningresolution.planning.nyc.gov/article-vii/chapter-7/77-26 | 2/2/2011 | NOT CAPTURED | NOT HANDLED |
| 77-27 | Yard Regulations (each portion by its district) | https://zoningresolution.planning.nyc.gov/article-vii/chapter-7/77-27 | 2/2/2011 | NOT CAPTURED | NOT HANDLED |
| 77-28 | Height and Setback Regulations (apportioned by frontage %) | https://zoningresolution.planning.nyc.gov/article-vii/chapter-7/77-28 | 12/5/2024 | NOT CAPTURED | NOT HANDLED |
| 36-64 | Special Provisions for Zoning Lots Divided by District Boundaries (**loading-berth pointer only**) | https://zoningresolution.planning.nyc.gov/article-iii/chapter-6/36-64 | 6/6/2024 | zr-36-64.snapshot.json | NOT HANDLED |

Reading B keeps **one** zoning lot and **blends** the two districts' numbers: use by the district
holding >50% of the lot where the boundary is within 25 ft (77-11), else each portion keeps its
own (77-12); FAR apportioned by area percentage and summed to one adjusted FAR (77-22); yards per
portion (77-27); height/setback apportioned by frontage (77-28); density = sum of each portion's
permitted units (77-25). It does **not** create two independent budgets, so it does not produce
A.1's rounding gain.

**Correction carried from the first pass (checked by the producer).** The first pass treats
**36-64** as "the C-district counterpart" to Chapter 7. The producer checked the captured
snapshot body: 36-64 reads, in C1-C8, "whenever a #zoning lot# is divided by a boundary between
districts having different requirements for #accessory# off-street loading berths, the provisions
set forth in Article VII, Chapter 7, shall apply." So 36-64 is a **narrow loading-berth pointer
into Chapter 7**, not a general C-district apportionment rule; the apportionment rules are Chapter
7 itself. The non-editable first-pass files are addressed under "Findings outside my files".

## Is the C2-2 overlay inner boundary a "district boundary" for Chapter 7? — not sure (two readings)

HX2 worked this question and found the ZR text does **not** settle it; it gives both readings and
neither is a determination:
- **Reading A (plain text — Chapter 7 applies).** 77-01 applies "Whenever any zoning lot is
  located in two or more districts in which different uses are permitted, or in which different
  use, bulk, accessory off-street parking and loading, or other regulations apply" and names no
  overlay exception; 11-122 lists C2-2 as a "Local Commercial District", so its edge is a mapped
  district boundary. On the plain words a part-overlay lot would apportion use under 77-11/77-12
  and bulk under 77-21ff.
- **Reading B (structural / as administered — the overlay edge is not a Chapter-7 boundary).** The
  ZR/DCP treat a C1/C2 overlay as superimposed on a residence district: commercial use is confined
  to the overlay band (its mapped depth + 32-421), commercial FAR is keyed to the residence
  district (33-121), and residential use/bulk/density follow the residence district across the
  whole lot (34-11; DCP guidance). On this reading the lot is in one base district (R6B) for
  residential purposes, so Chapter 7 does not engage. Signals (not a ruling): DCP frames overlays
  as "superimposed"; MapPLUTO lot 70 has ZoneDist2 null and SplitZone "N"; the DCP glossary defines
  a split lot as a lot divided by a *zoning-district* boundary and describes overlays separately.

**Verdict: not sure** — no on-point official statement located. **Keep this input unresolved in
every dependent output.** 36-64 (captured) is only the narrow loading-berth pointer (see
correction), not a general reach of Chapter 7 to an overlay edge. Next step: look for a DCP
determination/FAQ or BSA/CPC text directly on an overlay-only split.

**How an overlay boundary is located, and whether the lot is even split (HX2).** A boundary
parallel to a street with no dimension is located by ZR 76-131(b): a C2-2 overlay defaults to
**150 ft from the nearest street** (76-11 reads the maps through these rules; 76-141 governs where
a figure is drawn, measured from the nearest street line). The **actual mapped overlay line at the
lot was not read** (zoning-map sheet / ZoLa / NYCO GIS not opened). Conditional observation only
(not a determination): MapPLUTO gives lot 70 a LotDepth of 100 ft, so a 150-ft default overlay
from Northern Boulevard would exceed the lot depth and could cover the whole lot, making the
overlay-edge question likely moot for this lot — but this depends on the actual mapped line and
the corner lot's geometry. **Nothing is assumed about how much of the lot the overlay covers**;
keep it unresolved. Next step: read the DCP Zoning Map sheet / ZoLa / NYCO geometry and 76-00 /
76-01.

## Measurement basis and zoning-lot scope
Lot area in sq ft; lot width/frontage in feet; FAR and the DU factor applied to zoning-lot area;
distances in feet between the closest points of buildings. Scope: per zoning lot throughout — the
whole A.1-vs-A.2-vs-B distinction is how many zoning lots exist and whether a district boundary
crosses one. A tax lot is not a zoning lot (NB-01). The benchmark's recorded-vs-tax-map lot-area
disagreement (NB-04) stays unresolved.

## Lot facts that decide which reading applies (each with a possible official source)
- Whether a zoning-district boundary actually crosses the lot (triggers Reading B) — the official
  NYC Zoning Map / City Map and DCP ZoLa; Admin Code §25-101 adopted City Map. The C2-2 overlay
  has a mapped depth from Northern Boulevard; whether that splits the lot, the % in each district,
  and the ≤25-ft minority-portion test (77-11) are computed from lot geometry (MapPLUTO / DCM /
  survey, EPSG:2263) intersected with the mapped boundary (DCP zoning GIS).
- Whether the applicant subdivides into two zoning lots (A.1) — ownership and recorded
  Declarations / single-fee status (ACRIS / title); resulting metes-and-bounds (survey). The
  program cannot assume a subdivision.
- Lot area, lot width, frontage, corner status — MapPLUTO / DOF tax map / survey (NB-04).
- For A.2 distance/court rules — building footprints, heights, whether buildings are connected or
  separated by a rear-yard equivalent — design inputs / DOB filings.

## What the owner's sample shows (pointer only)
The sample's "Split Lot (2 Buildings)" scenario is on **pp. 82-87**, listed in the table of
contents on **p. 2**; the site-at-a-glance table on **p. 5** carries a "Split Zone" field valued
"No". By HD's reading the sample is **Reading A.1** (one tax lot developed as two independent
zoning lots, each built separately), not Reading B (its own "Split Zone = No" says it is not
treating the lot as crossed by a district boundary). The sample's figures are reference-only and
several were flagged wrong; no number is copied here.

## The open question (stays open)
**Which reading does option 8 intend — A.1 (two independent zoning lots), A.2 (two buildings on
one shared-budget zoning lot), or B (a zoning lot crossed by a district boundary)?** The sample
suggests A.1, but which the program should offer is an owner/product decision, not settled here.
This question stays open (carried to README and the questionnaire). Next step for the law: capture
23-371 and the 23-35 court group (Reading A.2) and the 77-xx sections (Reading B) before any rule
cites them.
