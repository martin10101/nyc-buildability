# Option 5 — ground-floor shops with residences above (C2-2 overlay in R6B)

**Unreviewed draft: discovery aid; each item links its source; nothing here is
professionally reviewed (ADR-007).** Readings here are drafts tied to the cited source text.
Where the producer is not sure, it says "not sure". Nothing here is labelled Verified; nothing
here calls a result compliant, buildable, feasible, optimal or preferred. No eligibility is
decided; no floor area, height, unit count or parking count is computed for the benchmark lot.
Parking, loading and bicycle parking are in `option-10-parking-and-transit-zone.md`.

Second pass of `../options-sections.md` §5; built from research helpers HB and HX1 (saved
outside git) plus the producer's own checks of the snapshots and the first-pass benchmark JSON.

## Sections

Capture state read from a listing of `docs/research/zr-snapshots/v1/`; handled state from
`services/api/app/rules/rulesets/`.

| id | title | official URL | last amended (page) | capture | handled |
|---|---|---|---|---|---|
| 32-161 | Use Group VI — general use allowances (retail/service = the shops use) | https://zoningresolution.planning.nyc.gov/article-iii/chapter-2/32-161 | 6/6/2024 | zr-32-161.snapshot.json | NOT HANDLED |
| 32-131 | Use Group III — general use allowances (**community facilities, not shops**) | https://zoningresolution.planning.nyc.gov/article-iii/chapter-2/32-131 | 12/5/2024 | zr-32-131.snapshot.json | NOT HANDLED |
| 32-421 | Limitation on floors occupied by commercial uses | https://zoningresolution.planning.nyc.gov/article-iii/chapter-2/32-421 | 6/6/2024 | NOT CAPTURED | NOT HANDLED |
| 33-12 | Maximum Floor Area Ratio (commercial, parent) | https://zoningresolution.planning.nyc.gov/article-iii/chapter-3/33-12 | 12/5/2024 | zr-33-12.snapshot.json | NOT HANDLED |
| 33-121 | In districts with bulk governed by Residence District bulk regulations | https://zoningresolution.planning.nyc.gov/article-iii/chapter-3/33-121 | 12/5/2024 | zr-33-121.snapshot.json | NOT HANDLED |
| 33-26 | Minimum Required Rear Yards (commercial) | https://zoningresolution.planning.nyc.gov/article-iii/chapter-3/33-26 | 6/6/2024 | NOT CAPTURED | NOT HANDLED |
| 33-301 | Within one hundred feet of corners (commercial rear-yard waiver) | https://zoningresolution.planning.nyc.gov/article-iii/chapter-3/33-301 | 12/15/1961 | NOT CAPTURED | NOT HANDLED |
| 35-01 | Applicability of This Chapter (Ch. 5 mixed-building bulk) | https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-01 | 12/5/2024 | zr-35-01.snapshot.json | NOT HANDLED |
| 35-30 | Applicability of Floor Area and Open Space Regulations (heading) | https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-30 | 2/2/2011 | zr-35-30.snapshot.json (heading only) | NOT HANDLED |
| 35-31 | Maximum Floor Area Ratio (mixed building) | https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-31 | 12/5/2024 | zr-35-31.snapshot.json | NOT HANDLED |
| 35-32 | Maximum Floor Area for Mixed Buildings on Qualifying Residential Sites | https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-32 | 12/5/2024 | zr-35-32.snapshot.json | NOT HANDLED |
| 34-11 | General Provisions (residential bulk in C1/C2) | https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-11 | 12/5/2024 | zr-34-11.snapshot.json | NOT HANDLED |
| 34-111 | Residential bulk regulations in C1 or C2 Districts | https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-111 | 12/5/2024 | zr-34-111.snapshot.json | NOT HANDLED |
| 34-24 | Modification of Height and Setback Regulations | https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-24 | 12/5/2024 | zr-34-24.snapshot.json | NOT HANDLED |
| 34-231 | Modification of front yard requirements | https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-231 | 12/5/2024 | zr-34-231.snapshot.json | NOT HANDLED |
| 34-232 | Modification of side yard requirements | https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-232 | 12/5/2024 | zr-34-232.snapshot.json | NOT HANDLED |
| 35-63 | Height/Setback in Commercial Districts with R6-R12 Equivalency | https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-63 | 12/5/2024 | zr-35-63.snapshot.json | NOT HANDLED |
| 35-631 | Street wall location | https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-631 | 12/5/2024 | zr-35-631.snapshot.json | NOT HANDLED |
| 35-632 | Maximum height of buildings and setback regulations | https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-632 | 12/5/2024 | zr-35-632.snapshot.json | NOT HANDLED |

Residential part of the mixed building uses the option-1 base envelope (23-22, 23-432, 23-52,
23-362, 23-344(a), etc. — handled where option 1 marks handled). The catalogue add-on
`ground_floor_commercial` has `rule_ids=()`, so nothing on the commercial / mixed side is
rule-backed.

**Correction carried from the first pass (checked by the producer).** The first pass and
`benchmark-r6b-sections.json` label **32-131** as the "C2-2 retail use permission". That is
wrong for option 5. The producer checked against the captured snapshots: **32-131 is Use Group
III — general use allowances (community facilities)**; the shops use is **32-161 Use Group VI —
general use allowances** (retail trade and general service establishments). `zr-32-161`'s C2
column permits most Use Group VI retail/service as-of-right (some cells carry size "S" or
special-permit "○" flags). So option 5 points at 32-161 (+ the floors rule 32-421), with 32-131
belonging to options 6/7. The non-editable `benchmark-r6b-sections.json` mislabel is listed under
"Findings outside my files" in the producer report.

## Reading (unreviewed draft)

**Use permission.** A C2-2 commercial overlay (a C-district mapped within R6B) permits local
retail / service — Use Group VI, 32-161 — at grade, subject to per-use flags and size notations
in the 32-161 table itself. 32-131 (Use Group III) is community facilities, relevant to
options 6/7.

**On which storeys shops may sit (32-421, not captured, read by HX1 live 6/6/2024).** In C1/C2,
"not more than two stories may be occupied by commercial uses listed in Use Groups VI through X,"
and "No commercial uses shall be located above any story containing dwelling units" — i.e. shops
sit at/near grade, below the residences. A story shared with dwelling units is allowed only where
"no access exists between such uses at any level containing dwelling units." If C2-2 is a "select
commercial overlay", Use Group VIII Amusement and Recreation Facilities are additionally barred
from a second story holding dwelling units — **not sure** C2-2 is a "select commercial overlay"
(HX1 could not read that 12-10 term verbatim; see open items).

**Commercial FAR of the overlay, keyed to R6B (33-12 → 33-121).** 33-121 lists C2-2 and keys the
maximum FAR to the underlying Residence District. The producer checked the captured table: the
row is **"R5D R6B"**, Column A (commercial only) **2.00**, Column B (community facility only)
**2.00**, Column C (both) **2.00**. Paragraph (a): on a both-uses lot the commercial floor area
"shall not exceed the amount permitted for #zoning lots# containing only #commercial# #uses# set
forth in Column A." So the commercial FAR for a C2-2 overlay in R6B is 2.00 (draft; a table value
cited to its section, not a computation for the lot).

**Combining commercial + residential floor area, and the ceiling (35-01 → 35-31).** A C2-2
overlay is a Commercial District, so 35-01 applies Article III Chapter 5 bulk to a mixed building.
35-31: "The total of all such #floor area ratios# shall not exceed the greatest #floor area
ratio# permitted for any such #use# on the #zoning lot#, except where explicitly stated
otherwise." So residential FAR (R6B 2.00, or 2.40 with qualifying housing) and commercial FAR
(2.00) **do not stack** — the building is capped at the single greatest permitted use FAR, with
shared floor area attributed proportionally. 35-32 (higher qualifying-residential-site path) does
**not** reach R6B: the producer checked that 35-32's rows and the 12-10 "qualifying residential
site" term list only R1-R5, not R6/R6B (resolves HB's "not sure" and HG's "likely low-density").

**Height, setback, street wall of the mixed building.** Two pathways both reach the overlay
height chain (evidence record NB-06): a mixed building via 35-01 directly; a residential-only
building via 34-11 "except as modified by … 34-24", and 34-24 applies the 35-63 modifications for
an R6-R12 equivalency. Both reach 35-631 (street-wall location — for R6B/Queens, paragraph (b):
at least 70% of the aggregate street-wall width within eight feet of the street line, to the
minimum base height) and 35-632(a) (heights from the 23-432 R6B row: min base 30, max base 45,
max building 55 std / 65 qualifying; setback above 45 ft per 23-433). 35-632(b) eligible-site
increases exclude lettered districts; 35-632(c) towers are R9-R12 only.

**Yards.** Front: 34-231 — no front yard required for a residential building in the overlay.
Side: 34-232 — no side yard required for a residential building; any side open area ≥5 ft.
Commercial rear yard: 33-26 — 20-ft rear yard at every rear lot line (except 33-27 shallow
interior lots / 33-28 through lots / 33-30), **waived within 100 ft of a corner by 33-301** (two
street lines meeting at ≤135°). The residential/mixed rear yard is the residence-district rear
yard (23-34x, handled by `r6b_rear_yard_corner_waiver`). The corner waiver exists on both sides
but under different sections (commercial 33-301; residential 23-344 path) — not conflated.

**Overlay depth / partial coverage (HX2).** Where a boundary parallel to a street carries no
dimension, its location is fixed by ZR 76-131(b): a C2-2 overlay defaults to **150 feet from the
nearest street**; a figure drawn on the zoning map overrides the default and is measured from the
nearest street line (76-141); 76-11 says the maps are read through these rules. The **actual
mapped overlay line at the lot was not read** this pass (zoning-map sheet / ZoLa / the DCP
Commercial Overlay (NYCO) GIS not opened). Conditional observation only (not a determination):
MapPLUTO gives lot 70 a LotDepth of 100 ft, so a 150-ft default overlay from Northern Boulevard
would exceed the lot depth and could cover the whole lot — but this depends on the actual mapped
line and the corner lot's geometry, so **nothing is assumed about how much of the lot the overlay
covers**; keep it unresolved. Where the overlay covers only part of the zoning lot, whether that
makes the lot a Chapter-7 split lot is itself unresolved — see `option-08-split-lot.md` reading B.

**Measurement basis.** FAR = floor area / zoning-lot area (dimensionless); floor area in sq ft;
heights in feet; stories counted for 32-421; rear yard in feet from the rear lot line.

**Zoning-lot scope.** FAR, the 35-31 ceiling and the 32-421 story limit are per **zoning lot /
building**; a tax lot is not a zoning lot (NB-01 unresolved).

**Lot facts the program would need (with a possible official source).**
- Overlay present + designation (C2-2) and its mapped depth — DCP Zoning Map / ZoLa; MapPLUTO
  Overlay1 (presence only; have: C2-2).
- Underlying residence district R6B — MapPLUTO ZoneDist1; DCP Zoning Map.
- Whether the overlay covers the whole lot or splits it, and the % each side — DCP Zoning Map +
  lot geometry.
- Street frontages and mapped widths (wide/narrow per frontage) — DCM Street Center Line (NB-06).
- Corner-lot status + the 100-ft corner portion — 12-10 "corner lot"; lot geometry.
- Lot area / dimensions — MapPLUTO LotArea; survey (NB-04).
- Use program (which Use Group VI uses; floor area by use) — a scenario input + use permission.

## What is not sure (each with its next step)

1. **Whether C2-2 is a "select commercial overlay"** (32-421 Amusement/Recreation second-story
   bar). Next step: verbatim read of the 12-10 "select commercial overlays" definition via the
   print/PDF node channel, then capture. Affects only the narrow UG VIII bar, not shops-below-
   residences.
2. **The single ZR rule governing the mixed-building rear yard** — HX1 gives a draft (33-26 for
   the commercial portion; 23-34x for the residential; residence-district rear yard may apply to
   the whole building where bulk is residence-governed) but could not verbatim-confirm one
   governing cross-reference. Next step: verbatim-read 33-26 + sub-sections and the
   residential-equivalency rear-yard provision.
3. **The exact combined-FAR ceiling for the lot** depends on the R6B residential FAR figure and
   whether qualifying housing applies — a computation left to the engine, not decided here.
4. **Whether 35-632 changes the R6B envelope numbers for a mixed building** — the modification is
   captured but not handled (NB-06). Next step: a rules task reads 35-632's numeric effect.
5. **Capture owed:** 32-421, 33-26, 33-27, 33-28, 33-30, 33-301 are NOT CAPTURED (read live by
   HX1/HB). Next step: capture these before a rule cites them.
6. **Actual mapped overlay line at the lot is NOT KNOWN** (76-131 default 150 ft recorded; the
   zoning-map sheet / ZoLa / NYCO GIS not read). Next step: read the DCP Zoning Map sheet (or ZoLa,
   or query the NYCO geometry) and check for a dimensioned line vs the 150-ft default. Also 76-00 /
   76-01 scaled-measurement bodies not extracted — read them. Nothing is assumed about overlay
   coverage until then.
7. **Owner question** (product, not law): should option 5 assume the C2-2 overlay covers the whole
   lot (its 150-ft default depth exceeds the 100-ft lot depth), or must the program read the actual
   overlay line and handle partial (split-lot) coverage? (Carried to README and the questionnaire.)
