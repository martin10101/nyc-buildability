# Option 9 — shared housing (rooming units under current law)

**Unreviewed draft: discovery aid; each item links its source; nothing here is
professionally reviewed (ADR-007).** Readings here are drafts tied to the cited source text.
Where the producer is not sure, it says "not sure". Nothing here is labelled Verified; nothing
here calls a result compliant, buildable, feasible, optimal or preferred. No eligibility is
decided; no floor area, height, unit count or parking count is computed for the benchmark lot.
Parking is in `option-10-parking-and-transit-zone.md`.

Second pass of `../options-sections.md` §9; built from helper HE plus the producer's own checks
(official page 23-51; the 12-10 rooming-unit and dwelling-unit snapshots; the settled R6B
reference row `step-p5-worked.json#option-rooming-units`).

## Sections

| id | title | official URL | last amended (page) | capture | handled |
|---|---|---|---|---|---|
| 12-10 | Definitions — "rooming unit" | https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10 | 12/5/2024 | zr-12-10-rooming-unit.snapshot.json | NOT HANDLED (definition only, inside r6b_dwelling_units) |
| 12-10 | Definitions — "dwelling unit" (the rooming-unit extension clause) | https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10 | 12/5/2024 | zr-12-10-dwelling-unit.snapshot.json | NOT HANDLED |
| 22-00 / 22-12 / 22-121 | Use Groups permitted in Residence Districts / Use Group II — Residences / general use allowances (UG II as-of-right in R6) | https://zoningresolution.planning.nyc.gov/article-ii/chapter-2/22-12 | 12/5/2024 (chapter) | NOT CAPTURED | NOT HANDLED |
| 22-122 | Use Group II — uses subject to additional conditions (rooming-unit bar) | https://zoningresolution.planning.nyc.gov/article-ii/chapter-2/22-122 | 12/5/2024 | NOT CAPTURED | NOT HANDLED |
| 32-121 | Use Group II — general use allowances (residences permitted in C1/C2) | https://zoningresolution.planning.nyc.gov/article-iii/chapter-2/32-121 | 6/6/2024 | NOT CAPTURED | NOT HANDLED |
| 34-11 | General Provisions (residential bulk in C1-C6 → underlying residence district) | https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-11 | 12/5/2024 | zr-34-11.snapshot.json | NOT HANDLED |
| 23-51 | Applicability (of the density regulations) | https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-51 | 12/5/2024 | NOT CAPTURED | NOT HANDLED |
| 23-52 | Maximum Number of Dwelling Units | https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-52 | 12/5/2024 | zr-23-52.snapshot.json | r6b_dwelling_units.rule.json |
| 54-311 | Buildings containing rooming units (conversion to dwelling units) | https://zoningresolution.planning.nyc.gov/article-v/chapter-4/54-311 | 12/5/2024 | NOT CAPTURED | NOT HANDLED |

Outside the Zoning Resolution (pointers only; these set lawful construction/occupancy, not
zoning): NY Multiple Dwelling Law §4 (Class A/B, "living room", "rooming house"); NYC Housing
Maintenance Code §27-2004 (rooming-unit definition — HE's official fetch was HTTP 403, wording not
confirmed); NYC Building/Fire Code; and the pending shared-housing legislation (NY State S10497 /
A11136, still in committee in 2026; NYC Council Intro 1475-2025), targeted to take effect
2027-01-01 — not enacted.

**Correction carried from the first pass (checked by the producer).** The first pass applies the
23-52 dwelling-unit factor to rooming units. The producer opened **23-51** officially (WebFetch,
HTTP 200, last amended 12/5/2024), full text: "The provisions of Section 23-50 (DENSITY
REGULATIONS), inclusive, shall apply to developments, enlargements or to existing buildings that
increase the number of dwelling units. However, **the provisions of this Section shall not apply
to rooming units.**" So the density regulations of 23-50 (the 23-52 680 factor) do **not** apply
to rooming units; 54-311 reinforces this (the factor attaches only on conversion to dwelling
units). "Shared housing" is not a ZR term (a portal search returns 0 results); the ZR regulates
it as "rooming unit".

## Reading (unreviewed draft)

**Use permission.** Rooming units are a Use Group II (residential) use. The positive as-of-right
citation (HX2): 22-00 lists Use Groups I-VIII as permitted in Residence Districts; 22-12 /
22-121 mark "all other types of residences" permitted (●) in R6, carried to R6B by 11-25 (suffix);
in the C2-2 overlay residences are independently permitted (●) by 32-121, the overlay only adding
commercial use groups. 22-122 (read by HE and HX2, 12/5/2024) bars rooming units only "on zoning
lots where residences are limited to single- or two-family residences" (R1, R2, R3A, R3-1, R3X,
R4A, R5A, R4-1, R4B); R6B is not in that list, so the draft reading is that rooming units are
permitted as-of-right in R6B, and the C2-2 overlay does not change that.

**Density.** 23-51 excludes rooming units from the density regulations (checked; see correction).
So the 23-52 680 dwelling-unit factor does **not** cap a rooming-unit building; the only ZR
quantity that limits it is floor area / FAR (residential FAR on the zoning lot, counted once per
23-51). There is no dwelling-unit-count ceiling for rooming units under this reading.

**Definitions relied on (12-10).** "rooming unit" = "any #living room#, as defined in the
Multiple Dwelling Law, in a #residential building# … which is not a #dwelling unit# or part of a
#dwelling unit#" — a direct hand-off to State law for the unit standard. The "dwelling unit"
definition carries the bridge clause extending dwelling-unit regulations to rooming units "unless
specifically stated"; 23-51 is the "specifically stated" density carve-out. "#multiple dwelling
residence#" (not captured) is a definitional input to 23-52.

**Exceptions / carve-outs.** 22-122 bars rooming units in single-/two-family-only districts (not
R6B); 23-51 excludes them from density; 23-52(a) no-factor branches (special density areas,
qualifying senior housing, certain conversions) are separate — per NB-05 the lot is not in a
special density area.

**Overlay / special-district effects.** The C2-2 overlay adds commercial use groups but
residential use and density stay governed by the underlying R6B. HX2 identified the governing
sections: residential **bulk** in the overlay follows the residence district via 34-11 (captured);
residential **use** is the residence-district Use Group II permission (22-12/22-121), with 32-121
permitting residences in C1/C2; residential **density** has no overlay version — it is the
residence district's 23-50/23-52 (and, for rooming units, the 23-51 exclusion). So the overlay
does not change whether rooming units are permitted or how their density is controlled. No special
purpose district is mapped (NB-05 SPDist1 null).

**Measurement basis.** The ZR imposes no interior-dimension measurement on rooming units (no
minimum room area, no kitchen/bath ratio) — those live outside the ZR (MDL / HMC / Building Code;
the pending bills propose 100 sq ft for one occupant / 150 for two). Within the ZR, only floor
area / FAR limits a rooming-unit building, counted once (23-51).

**Zoning-lot scope.** FAR (and the inapplicable DU factor) are per **zoning lot**; the benchmark
zoning lot is unconfirmed (NB-05 lot_scope = zoning_lot_unconfirmed; a tax lot is not a zoning
lot). Use permission (22-122) is also per zoning lot.

**Facts the program would need (each with a possible official source).**
- Zoning district + overlay — MapPLUTO (ZoneDist1 R6B, Overlay1 C2-2) / DCP zoning maps (NB-05).
- Whether the proposal's units are "rooming units" vs "dwelling units" — an applicant/program
  fact; the program cannot infer it; it picks the density branch.
- Whether the building "contains #multiple dwelling residences#" and its MDL Class A/B
  classification — a proposal fact + MDL §4.
- Zoning-lot extent — DOF/DCP zoning-lot records; tax lot ≠ zoning lot (keep unresolved).
- Maximum residential floor area on the zoning lot — the R6B FAR rule output (not recomputed).
- Special density area status — ZR 12-10 (NB-05: not in one).

**What lies outside the ZR (draft).** The zoning barrier to rooming units was removed effective
12/5/2024, but whether a shared-housing building can lawfully be built or occupied today still
depends on the MDL (Class A/B), the HMC (rooming-unit standards, registration, certificate of
occupancy) and the Building/Fire Code; the modern "shared-housing-suite" framework is **not yet
enacted** (State bills in committee; city bill introduced 2025-11-25) and is targeted for
2027-01-01. So as of 2026-10-14 the program should not treat a new shared-housing suite as
lawfully occupiable as-of-right.

**What the owner's sample shows (pointer only).** Sample scenario 7 "shared housing / SRO"
(pp.58-63): individual rooms (about 150 sq ft) with shared kitchen/bath, counted as units, and a
positive parking requirement. **The sample's premise differs from the law as read:** it counts SRO
rooms as dwelling units for density and shows required parking, whereas the ZR excludes rooming
units from density (23-51) and requires no parking for rooming units in the transit zone (see
option 10). Listed under "Questions for the owner" in the README.

## What is not sure (each with its next step)
1. **Exact referent of "this Section" in 23-51's rooming-unit sentence** — HX2 confirmed the
   literal word is "this Section" (singular), whose literal referent is Section 23-51; two
   interpretive readings (23-51 the applicability trigger, or shorthand for 23-50) both reach "no
   dwelling-unit factor for rooming units", reinforced by 54-311. Interpretation left as a labelled
   draft. 23-51 still NOT CAPTURED — next step: capture the verbatim node (print/PDF channel).
2. **The positive Use Group II as-of-right citation for R6** — RESOLVED by reading to 22-12/22-121
   (+ 22-00; 11-25 for the suffix); 32-121 permits residences in C1/C2. All NOT CAPTURED — next
   step: capture before a rule cites them.
3. **The sections governing residential use/bulk in a C1/C2 overlay** — RESOLVED by reading: bulk =
   34-11 (captured) + the 34-21…34-24/35-63 modifications; use = residence-district Use Group II
   (22-12/22-121) with 32-121; density = the residence district's 23-50/23-52. The overlay adds
   commercial only. (34-11 captured; 22-1xx / 32-121 not captured.)
4. **The r6b_dwelling_units rule does not encode the 23-51 rooming-unit exclusion** (HE). Applying
   it to a rooming-unit scenario would impose a unit cap the law does not. This is a rule-behavior
   note for the rule owner (that file is outside this task's scope); recorded in the producer
   report, no change made here.
5. **22-122, 23-51, 54-311 are NOT CAPTURED.** Next step: capture them before a rule cites them.
6. **Owner question** (product, not law): should option 9 be modeled as ZR rooming units under
   current law (zoning-permitted, no unit factor, but the modern shared-housing-suite operating
   framework not yet enacted), or presented as conditional on the pending 2027 legislation? And
   should the program show the zoning envelope only and mark buildability/occupancy as conditional
   on the MDL/HMC/Building Code rather than report a rooming-unit count? (Carried to README and the
   questionnaire.)
