# Options 6 & 7 — residences with a community facility (6) and a community facility alone (7)

**Unreviewed draft: discovery aid; each item links its source; nothing here is
professionally reviewed (ADR-007).** Readings here are drafts tied to the cited source text.
Where the producer is not sure, it says "not sure". Nothing here is labelled Verified; nothing
here calls a result compliant, buildable, feasible, optimal or preferred. No eligibility is
decided; no floor area, height, unit count or parking count is computed for the benchmark lot (a
rule table value cited to its section is not such a computation). Parking/loading/bicycle are in
`option-10-parking-and-transit-zone.md`.

Second pass of `../options-sections.md` §6 and §7; built from helpers HC, HX1 and HG plus the
producer's own checks (two official pages: 24-11 and 24-162) and the settled R6B reference cases.

## Sections

Capture state read from a listing of `docs/research/zr-snapshots/v1/`; handled from
`services/api/app/rules/rulesets/`. No `zr-24-*` snapshot exists, so every Article II Chapter 4
section is NOT CAPTURED.

| id | title | official URL | last amended (page) | capture | handled |
|---|---|---|---|---|---|
| 22-13 / 22-131…22-135 | Use Group III — community facilities (use permission) | https://zoningresolution.planning.nyc.gov/article-ii/chapter-2/22-13 | not individually read | NOT CAPTURED | NOT HANDLED |
| 32-131 | Use Group III — general use allowances (CF use in the C2-2 overlay) | https://zoningresolution.planning.nyc.gov/article-iii/chapter-2/32-131 | 12/5/2024 | zr-32-131.snapshot.json | NOT HANDLED |
| 24-11 | Maximum Floor Area Ratio and Percentage of Lot Coverage (CF) | https://zoningresolution.planning.nyc.gov/article-ii/chapter-4/24-11 | 12/5/2024 | NOT CAPTURED | NOT HANDLED |
| 24-111 | Maximum floor area ratio for certain community facility uses | https://zoningresolution.planning.nyc.gov/article-ii/chapter-4/24-111 | 12/5/2024 | NOT CAPTURED | NOT HANDLED |
| 24-161 | Maximum FAR for zoning lots containing CF and residential uses | https://zoningresolution.planning.nyc.gov/article-ii/chapter-4/24-161 | 12/5/2024 | NOT CAPTURED | NOT HANDLED |
| 24-162 | Maximum FARs and special FA limitations … in certain districts | https://zoningresolution.planning.nyc.gov/article-ii/chapter-4/24-162 | 12/5/2024 | NOT CAPTURED | NOT HANDLED |
| 24-163 | Lot coverage for CF + residential zoning lots | https://zoningresolution.planning.nyc.gov/article-ii/chapter-4/24-163 | not read | NOT CAPTURED | NOT HANDLED |
| 24-04 | Applicability of Article II, Chapter 3 Regulations (CF height/setback routing) | https://zoningresolution.planning.nyc.gov/article-ii/chapter-4/24-04 | 12/5/2024 | NOT CAPTURED | NOT HANDLED |
| 24-52 | Maximum Height of Walls and Required Setbacks (routing) | https://zoningresolution.planning.nyc.gov/article-ii/chapter-4/24-52 | 12/5/2024 | NOT CAPTURED | NOT HANDLED |
| 24-522 | Front setbacks where front yards are not required | https://zoningresolution.planning.nyc.gov/article-ii/chapter-4/24-522 | 12/5/2024 | NOT CAPTURED | NOT HANDLED |
| 24-56 | Special Height and Setback Provisions for Certain Areas | https://zoningresolution.planning.nyc.gov/article-ii/chapter-4/24-56 | 12/5/2024 | NOT CAPTURED | NOT HANDLED |
| 23-43 (/431/432/433) | Height and Setback Requirements in R6-R12 Districts | https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-43 | 12/5/2024 | zr-23-43 / zr-23-431 / zr-23-432 / zr-23-433 | r6b_height.rule.json (residences); NOT HANDLED as a CF rule |
| 24-33 | Permitted Obstructions in Required Yards | https://zoningresolution.planning.nyc.gov/article-ii/chapter-4/24-33 | 12/5/2024 | NOT CAPTURED | NOT HANDLED |
| 24-34 | Minimum Required Front Yards (none in R6B) | https://zoningresolution.planning.nyc.gov/article-ii/chapter-4/24-34 | 12/5/2024 | NOT CAPTURED | NOT HANDLED |
| 24-35 | Minimum Required Side Yards (none; ≥8 ft if provided) | https://zoningresolution.planning.nyc.gov/article-ii/chapter-4/24-35 | 12/5/2024 | NOT CAPTURED | NOT HANDLED |
| 24-36 | Minimum Required Rear Yards (30 ft) | https://zoningresolution.planning.nyc.gov/article-ii/chapter-4/24-36 | 12/5/2024 | NOT CAPTURED | NOT HANDLED |
| 24-391 | Within one hundred feet of corners (CF rear-yard waiver) | https://zoningresolution.planning.nyc.gov/article-ii/chapter-4/24-391 | 12/5/2024 | NOT CAPTURED | NOT HANDLED |
| 35-01 | Applicability of This Chapter (mixed building) | https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-01 | 12/5/2024 | zr-35-01.snapshot.json | NOT HANDLED |
| 35-31 | Maximum Floor Area Ratio (mixed building) | https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-31 | 12/5/2024 | zr-35-31.snapshot.json | NOT HANDLED |
| 35-33 | Max FA … CF use in certain districts (**excludes R6B**) | https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-33 | 12/5/2024 | zr-35-33.snapshot.json | NOT HANDLED |
| 33-121 | Overlay FAR (Column B = CF, R6B = 2.00) | https://zoningresolution.planning.nyc.gov/article-iii/chapter-3/33-121 | 12/5/2024 | zr-33-121.snapshot.json | NOT HANDLED |
| 34-11 / 34-111 | Residential bulk in C1/C2 → underlying R6B | https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-111 | 12/5/2024 | zr-34-11 / zr-34-111 | NOT HANDLED |
| 23-20 | Floor Area Regulations (multi-use cap) | https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-20 | 12/5/2024 | zr-23-20.snapshot.json | NOT HANDLED |
| 23-22 | Floor Area Regulations R6-R12 (residential input) | https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-22 | 12/5/2024 | zr-23-22.snapshot.json | r6_r12_residential_far.rule.json |

The catalogue add-on `community_facility_floor_area` has `rule_ids=()` → NOT HANDLED.

**Corrections carried from the first pass (checked by the producer).**
- **35-33 excludes R6B.** The producer checked against the captured snapshot: 35-33 applies "In
  C1 and C2 Districts mapped within R6 Districts **without a letter suffix**, and in R7-1
  Districts." R6B carries the suffix "B", so 35-33 does not apply; the general 35-31 greatest-
  single-use-FAR cap governs CF + residential on this lot.
- **24-162 excludes R6B.** The producer opened 24-162 officially (WebFetch, HTTP 200, last
  amended 12/5/2024): its opening sentence reads "In the districts indicated, except R4-1, R4A,
  R4B, R5D, R6A, R6B and R6D Districts, the provisions of this Section shall apply…" — so the
  Column-A/B CF reduction of 24-162 does not reach R6B.

## Reading (unreviewed draft)

**CF use permission.** Community-facility uses are Use Group III (22-13…22-135; not captured).
In the C2-2 overlay, CF use permission is 32-131 (Use Group III, captured). Which specific Group
III uses are as-of-right vs size-limited (22-132) vs special-permit (22-134) in R6B was not read
item by item — **not sure** (next step: read 22-131…22-134).

**CF floor area + lot coverage (option 7, and the CF part of option 6).** 24-11 R6B row: CF FAR
**2.00**; lot coverage **80% corner / 60% interior-or-through** (producer-checked official page).
24-111 does **not** change the R6B figure: for "R6 through R12 Districts with a letter suffix"
24-111 defers to 24-11, so even the special philanthropic / long-term-care uses stay at 2.00 in
R6B (HX1; the elevated 2.43 figure is for non-suffixed R6 only). These are table values cited to
their section, not computations for the lot.

**CF + residential combination (option 6).** The settled R6B reference reading
(`docs/reference-cases/R6B/cases/step-p5-worked.json`, rows `mixed-use-floor-area-combination`
and `shared-floor-area-rule`) gives each use its own maximum FAR plus a single combined cap: "the
total of all such floor area ratios shall not exceed the greatest floor area ratio permitted for
any such use on the zoning lot" (35-31; 23-20 in the same words), with shared floor area
attributed proportionally on a base of total floor area **less** the shared portion. 24-161 states
the same ceiling in Article II Chapter 4 for a residence-district reading. 24-162 (which would
impose a Column-A/B CF reduction) and 35-33 (the mixed-building CF tightening) both **exclude**
R6B (see corrections), so the ceiling is the plain greatest-single-use FAR.

**CF height/setback (options 6 and 7).** Per HC, 24-04 routes R6B CF buildings to the residence
contextual chain: "In R6 through R12 Districts with a letter suffix, the height and setback
regulations of Section 23-43 … inclusive, shall be applied." So a CF building in R6B follows the
same 23-431 / 23-432 (R6B min base 30, max base 45, max building 55) / 23-433 chain that
`r6b_height` handles for residences; 24-522's generic table carries no R6B row and is superseded;
24-56 is special geographies only (not R6B). 24-04's own exception: the 23-431(b) street-wall
rules "need not apply to houses of worship listed under Use Group III(B)." These 24-xx sections
are NOT CAPTURED (next step: capture them).

**CF yards.** Front: 24-34 — none required for CF in R6B. Side: 24-35 — none required; any side
open area ≥8 ft (vs 5 ft for a residence, 23-335/34-232). Rear: 24-36 — 30 ft at every rear lot
line (subject to 24-37/38/39). Corner waiver: 24-391 — no rear yard within 100 ft of two street
lines meeting at ≤135°; it sits inside Chapter 4, so it reaches CF (the benchmark is a corner).
24-33 permits listed obstructions. All NOT CAPTURED.

**Overlay / special-district effects (C2-2 on R6B).** 33-121 lists C2-2; the R5D/R6B row Column
B (CF only) = **2.00** and Column C (both) = 2.00, so the overlay does **not** raise the CF FAR
above the underlying R6B 2.00 (producer-checked table). 34-11 / 34-111 route residential bulk in
the overlay to the underlying R6B; the settled reference reading
(`step-p4-worked.json#zr-34-111-exceptions`) confirms neither 34-111 exception reaches an R6B
lot, so the general rule governs. 35-01 applies Chapter 5 to a mixed building; 23-20 is the
general multi-use cap.

**Measurement basis.** FAR = CF floor area / zoning-lot area (CF FAR 2.00 → CF floor area ≤ 2.00
× zoning-lot area). Lot coverage = percent of zoning-lot area (80/60). Heights in feet above curb
level / base plane. Yards in feet from the relevant lot line (rear 30 ft; side open area ≥8 ft;
front none).

**Zoning-lot scope.** FAR, the combination ceiling, lot coverage and 23-20 are per **zoning
lot**; heights/setbacks per building; yards per lot line. A tax lot is not a zoning lot (NB-01).

**Lot facts the program would need (with a possible official source).**
- District + suffix R6B — MapPLUTO ZoneDist1 (NB-05) / DCP zoning map.
- Commercial overlay C2-2 — MapPLUTO Overlay1 (NB-05).
- Zoning-lot scope and lot area — DOF / zoning-lot records; MapPLUTO LotArea is a proxy (NB-01,
  NB-04).
- Street widths wide/narrow (drives the 23-43 chain for CF) — DCM Street Center Line (NB-06).
- Corner geometry + intersection angle (≤135°, for 24-391) — DCM / survey / MapPLUTO.
- The CF use type, whether it has sleeping accommodations, whether it is a Use Group III(B) house
  of worship — a scenario/use-program input, not a lot fact.

**What the owner's sample shows.** Sample scenario 5 "residential + CF" (pp.45-51): one mixed
building combining residential and a community-facility use, the total held to the highest
single-use FAR rather than summed. Sample scenario 6 "community facility" (pp.52-57): a pure
institutional building with no dwelling units, the CF FAR driving the envelope. The sample cites
no CF-FAR or combination section. Its premise (a CF-equivalent FAR and a highest-single-use cap)
matches the law as read; the CF FAR source (24-11, not captured) and use permission stay inputs.

## What is not sure (each with its next step)

1. **Which section is the operative combination citation for option 6** — 24-161 (residence
   district) vs 35-31 (mixed building, reached via 35-01 because a C2-2 overlay is a Commercial
   District). Both reach the same greatest-single-use ceiling and 35-33 is excluded, so the number
   is the same, but the citation differs. Next step: read 34-11 / 35-00 / 35-01 / 24-17
   applicability precedence for a residential+CF building in a C1/C2 overlay. Keep unresolved.
2. **24-11, 24-111, 24-161, 24-163 and the Chapter-4 height/yard sections are NOT CAPTURED.** Next
   step: capture the Article II Chapter 4 sections options 6/7 rely on before a rule cites them.
3. **Use-permission precision** — which Use Group III uses are as-of-right vs 22-132/22-133/22-134
   in R6B. Next step: read 22-131…22-134.
4. **24-163 lot coverage for a combined CF + residential lot** — read from the index only. Next
   step: read 24-163.
5. **Owner question** (product, not law): does "residences with a community facility" (option 6)
   mean one mixed building or separate residential and CF buildings on one lot? The combination
   ceiling is cited differently for a single mixed building versus a multi-building zoning lot.
   (Carried to README and the questionnaire.)
