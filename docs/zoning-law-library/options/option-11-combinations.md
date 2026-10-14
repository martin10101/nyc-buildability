# Option 11 — all programs combined (which add-ons may combine, and the combination ceilings)

**Unreviewed draft: discovery aid; each item links its source; nothing here is
professionally reviewed (ADR-007).** Readings here are drafts tied to the cited source text.
Where the producer is not sure, it says "not sure". Nothing here is labelled Verified; nothing
here calls a result compliant, buildable, feasible, optimal or preferred. No eligibility is
decided; no floor area, height, unit count or parking count is computed for the benchmark lot.

Second pass of `../options-sections.md` §11; built from helper HG plus the producer's own checks
and the settled R6B reference rows (`step-p5-worked.json#mixed-use-floor-area-combination`,
`#shared-floor-area-rule`; `step-p4-worked.json#qualifying-residential-site`,
`#dwelling-unit-factors`, `#mixed-building-definition`).

## Sections

There is no single ZR section for option 11; the combination ceilings are:

| id | title | official URL | last amended | capture | handled |
|---|---|---|---|---|---|
| 23-20 | Floor Area Regulations (R-district multi-use greatest-FAR cap) | https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-20 | 12/5/2024 | zr-23-20.snapshot.json | NOT HANDLED |
| 35-31 | Maximum Floor Area Ratio (mixed-building greatest-FAR cap + shared-area attribution) | https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-31 | 12/5/2024 | zr-35-31.snapshot.json | NOT HANDLED |
| 35-01 | Applicability (Chapter 5 across one zoning lot, incl. multiple buildings) | https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-01 | 12/5/2024 | zr-35-01.snapshot.json | NOT HANDLED |
| 35-32 | Max FA on Qualifying Residential Sites (**does not reach R6B**) | https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-32 | 12/5/2024 | zr-35-32.snapshot.json | NOT HANDLED |
| 35-33 | Max FA … CF use in certain districts (**excludes R6B**) | https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-33 | 12/5/2024 | zr-35-33.snapshot.json | NOT HANDLED |

Option 11 also inherits every captured/handled and NOT-CAPTURED/NOT-HANDLED section of options
2-10. The commercial FAR (33-121, captured) and CF FAR (24-11/24-111, not captured) feed the cap
but have no rule; the two qualifying-housing columns (23-22 2nd column; 23-432 qualifying) are the
only rule-backed add-on inputs today.

**Capture-state correction carried.** HG reported 23-20, 33-12, 33-121, 35-30, 35-31, 35-32, 35-33
as NOT CAPTURED. The folder is authoritative on capture (PROGRAM_KNOWLEDGE): the producer listed
`docs/research/zr-snapshots/v1/` and confirmed **all seven ARE captured** (HG read capture state
off `benchmark-r6b-sections.json`'s `not_evaluated/missing` flags instead of listing the folder).
Only 24-11 and 24-111 are not captured. Capture state throughout this file is from the folder.

## Reading (unreviewed draft)

**The combination ceiling.** The settled R6B reference reading
(`step-p5-worked.json#mixed-use-floor-area-combination` and `#shared-floor-area-rule`, two
independent readers agreeing) gives: each use keeps its own maximum FAR (commercial/CF per Article
III Chapter 3; residential per Article II Chapter 3) and the **total of all FARs may not exceed
the greatest FAR permitted for any single use on the zoning lot** (35-31; 23-20 in the same
words), with shared floor area attributed proportionally on a base of total floor area **less**
the shared portion. So uses **share one envelope; they do not stack.** The higher qualifying
affordable/senior residential FAR (R6B 2.40 vs 2.00) combines with commercial/CF only by raising
that one shared ceiling, not by adding onto the 2.00 commercial (33-121) or 2.00 CF (24-11).

**What does not raise the R6B ceiling.** 35-32 (qualifying-residential-site path, flat 2.50 in the
Greater Transit Zone) does **not** reach R6B — the producer checked that 35-32's rows and the
12-10 "qualifying residential site" term list only R1-R5 (and `step-p4-worked.json#qualifying-
residential-site` settles that R6B is not one). 35-33 (the CF mixed-building tightening) **excludes**
R6B (suffix; producer-checked). So the R6B mixed-building ceiling is the plain 35-31 greatest-
single-use cap.

**Which add-ons may combine (unreviewed draft; "combine" = allowed on one zoning lot / mixed
building under the stated ceiling, not that the program computes it).**

| Add-on (option) | May combine? | Governing ceiling / section |
|---|---|---|
| Qualifying affordable housing (2) | with commercial (5) & CF (6): MAY, in one mixed building | 35-31 greatest-FAR cap; residential col 23-22 2nd (2.40) becomes the shared ceiling; height 35-632(a)→23-432 qualifying col (45/65) |
| Qualifying senior housing (3) | with commercial (5) & CF (6): MAY | same as (2); plus 23-52(a)(2) no DU factor |
| Affordable (2) vs Senior (3) | MAY NOT (alternatives) | Same 23-22/23-432 2nd column; a program conflict on `housing_program`. Whether one development may hold both: NOT SURE (no ZR text read) |
| Ground-floor commercial (5) | MAY combine with residential (mixed building) | Use 32-161; FAR 33-121 (R6B 2.00) shares the 35-31 cap; 32-421 floor limits |
| Community-facility floor area (6) | MAY combine with residential & commercial | 24-11 (R6B 2.00) under the 35-31 cap; 35-33 excluded (R6B suffix) |
| Community facility alone (7) | n/a as an add-on (standalone CF building) | 24-11 FAR 2.00 + Article II Chapter 4 bulk |
| Split lot / two buildings (8) | MAY (two buildings on one zoning lot) | 35-01 applies the Chapter 5 cap across the zoning lot; a district-boundary split (77-00) is NOT SURE |
| Shared housing (9) | NOT SURE | ZR use/density identified (22-122, 23-51, 54-311) but not captured; occupancy framework not yet enacted |
| Parking waiver (10) | MAY combine with any (orthogonal to FAR) | 25-xx transit-zone parking; sets no `housing_program`, so no FAR conflict |

**Where the program's combination logic lives (read-only context).** Per HG, option 11 reads the
`best_combination` / `addon_gains` results slots produced by the scenario add-on engine
(`services/api/app/scenario/addons/catalogue.py` conflict detection and `.../recalculation.py`
`best_combination`), surfaced through `drawings/report/options.py`. Today only
`qualifying_affordable_housing` and `qualifying_senior_housing` name Lane A rule ids;
`community_facility_floor_area`, `ground_floor_commercial`, `choice_of_bulk_rules`,
`certification_transfer` have `rule_ids=()`, so they are never "available". Because the two
rule-backed programs are mutually exclusive (both set `housing_program`), **option 11 currently
reduces to "choose the single best qualifying-housing column" — it does not yet combine multiple
floor-area pools.** This is a description of current program behavior, read-only; this task changes
no code.

**Legal combination limits the program has NO rule for (HG).** (1) the 35-31 / 23-20 greatest-FAR
cap itself; (2) commercial overlay FAR (33-121) and CF FAR (24-11/24-111); (3) proportional
attribution of shared floor area (35-31; 23-52); (4) the interaction of the 2.40 qualifying FAR
with commercial/CF under the shared cap; (5) the mixed-building height/setback path (35-632 →
23-432/23-433); (6) shared housing; (7) the conflict model is purely input-key-based, so a legal
incompatibility not expressed as a shared generator input is invisible.

**Measurement basis.** FAR = floor area / zoning-lot area; the greatest-FAR cap is a ratio ceiling
on total floor area; shared floor area apportioned by each use's percentage of total floor area
less shared area; coverage is a percentage of lot area. Heights in feet.

**Zoning-lot scope.** The cap is per **zoning lot** (not per building, not per tax lot); 35-01
extends it across multiple buildings on one zoning lot. The zoning lot must be confirmed (NB-01);
a tax lot is not a zoning lot.

**Lot facts the rules need (each with a possible official source).** As for the component options:
district + suffix R6B and overlay C2-2 (MapPLUTO / DCP zoning map); zoning-lot area (survey /
ACRIS; MapPLUTO LotArea a proxy); corner status and street widths (DCM / survey); special district
(MapPLUTO SPDist + ZR maps); which programs apply (scenario input + legal determinations the
program does not make); transit-zone membership (recorded: Outer, see option 10).

**What the owner's sample shows (pointer only).** Sample scenario 3 "all programs combined"
(pp.30-36): the sample's "combination" names only the UAP bonus — it does not stack senior / CF /
commercial — reproducing the UAP max-development sheet. The sample cites no combination section.
**The sample's premise differs from the law/program intent:** its single-program treatment is
narrower than a true multi-use combination; whether option 11 should genuinely stack multiple
compatible programs, and toward which objective, is listed under "Questions for the owner".

## What is not sure (each with its next step)
1. **Whether a single development may contain both qualifying affordable and qualifying senior
   housing** — the program treats them as mutually exclusive; no ZR text read on mixing them (they
   are alternate routes to the same 2nd column, so no stacking benefit either way). Next step: read
   23-22 / 12-10 for any combine/exclude language.
2. **35-31 "except where explicitly stated otherwise"** — the full carve-out sweep (which explicit
   provisions raise the greatest-FAR cap) was not done; for R6B/C2-2, 35-32 and 35-33 are
   inapplicable. Next step: read 35-31 in full plus its neighbours (e.g. 35-34+).
3. **24-11 / 24-111 are NOT CAPTURED** (CF FAR feeding the cap). Next step: capture them.
4. **Shared housing (9/10) and the UAP chapter (Article II Ch 7) remain not captured / not
   handled**, and 23-154 is access-blocked — option 11 cannot be fully worked until the component
   options are rule-backed. Next step: the dedicated captures named in options 2-3, 9 and 10.
5. **Split-lot meaning (option 8)** feeds option 11's multi-building case and stays open (reading
   A.1 / A.2 / B; the overlay-edge question unresolved).
6. **Owner question** (product, not law): should option 11 genuinely stack multiple compatible
   bonuses toward a stated objective (most residential floor area, most units, …), or follow the
   sample's narrower UAP-alone treatment? (Carried to README and the questionnaire.)
