# Coverage — what the program handles and does not

**Unreviewed draft (ADR-007).** Coverage statuses use the one project vocabulary
(`docs/LEGAL_CORPUS_COVERAGE_MATRIX.md` §2): `missing`, `not_evaluated`, `unsupported`, `conflicting`,
`professional_review_required`, `not_applicable` (per-evaluation) and `implemented` / `partial`
(domain roll-up). This library applies them per section as described in `benchmark-r6b-sections.json`
(`coverage_status_vocabulary`). Nothing here is Verified; no result is called compliant, buildable, or
feasible.

## Handled today (6 sections, computed by a rule file)

A section is "handled" only when a rule file **formally cites** it (in `citations[]`) and computes a
value from it. These are unreviewed drafts, not professional verifications.

| Section | Title | Handled by | What it computes |
|---|---|---|---|
| 11-25 | District Designations Appended with Suffixes | `r6b_dwelling_units`, `r6b_lot_coverage`, `r6b_rear_yard_corner_waiver` | suffix inheritance (R6 … lists reach R6B) |
| 23-22 | Floor Area Regulations for R6 Through R12 | `r6_r12_residential_far`, `r6b_qualifying_housing_far` | residential FAR (standard + qualifying columns) |
| 23-52 (+ 23-52(b)) | Maximum Number of Dwelling Units | `r6b_dwelling_units` | dwelling-unit count (680 factor) |
| 23-362 | Maximum lot coverage in R6-R12 | `r6b_lot_coverage` | maximum lot coverage |
| 23-432 | Height and setback requirements | `r6b_height` | the height table (min/max base height, max building height) |
| 23-344(a) | Additional rear yard modifications | `r6b_rear_yard_corner_waiver` | the within-100-ft-of-corner rear-yard waiver |

## Not handled but needed for the BASE R6B envelope (core gaps)

These apply to the plain standard-residence case and have **no** rule file:

- **23-431 Street wall location** — no rule computes street-wall placement. Referenced in r6b_height prose
  only. (`not_evaluated`.)
- **23-433 Standard setback** — no rule computes the setback depth (10 ft wide / 15 ft narrow above the
  max base height). Not triggered by the 3-storey benchmark, but not computed. (`not_evaluated`.)
- **23-335 Side yard** — no rule; every residential option needs it. (`not_evaluated`.)
- **23-342 / 23-343 rear-yard baseline / equivalent** — the corner *waiver* is handled, but the baseline
  rear-yard depth and the through/corner-lot equivalent are not computed (referenced as context by the
  waiver rule, not in its `citations[]`). (`not_evaluated`.)
- **23-363 interior/through-lot coverage increases** — referenced in r6b_lot_coverage prose, not computed.
- **23-434 eligible/affordable-site H&S modifications** — captured, in scope, no rule.

## Not handled — the families the remaining options need

Grouped plainly (sections captured unless marked NOT CAPTURED):

- **Side yards** — 23-335 (every residential option).
- **Mixed buildings and overlay FAR** — 32-131 / 32-161 (commercial use permission); 33-12 / 33-121
  (overlay commercial/CF FAR, keyed to the underlying R6B); 35-30 / 35-31 / 35-32 / 35-33 (mixed-building
  floor-area combination = per-use caps summed to the greatest single-use FAR); 34-11 / 34-24 / 34-232
  (residential-bulk-in-commercial modifications); 35-63 / 35-631 / 35-632 / 35-633 (overlay
  street-wall/height). Options 5, 6, 11.
- **Community facility** — 24-11 (captured, M3-T009; R6B FAR 2.00, coverage 80/60, last amended
  12/5/2024) and 24-111 (captured, M3-T009); the Article II Chapter 4 height/yard sections
  (24-161/162/163, 24-33 to 24-56) are captured. Options 6, 7, 11.
- **Parking and transit zones** — 25-20 / 25-211 / 25-212 / 25-22 / 25-221 / 25-222 / 25-23 / 25-231 /
  25-232; 66-11 (Article VI Chapter 6 "Definitions" — defines the "mass transit station" terms, not the
  transit zones; the transit-zone definitions themselves are the 12-10 defined terms Transit Zone,
  Greater / Inner / Outer plus Appendix I); Appendix I (transit-zone maps — a lot's transit zone stays a
  recorded value, DB-194(b)). Options 10, 11.
- **Universal Affordability Preference (UAP)** — 23-154 (**NOT CAPTURED**; HTTP 403 when H6 tried; the FAR
  consequence flows through 23-22's second column, but UAP eligibility is a legal determination, not a
  computed rule). Options 2, 11.
- **Shared housing** — the City-of-Yes shared-housing use/density/standards sections are **not identified
  in the snapshot set** (numbers unresolved). 12-10 "rooming unit" (captured) + 23-52 extend
  dwelling-unit regs to rooming units, but the dedicated shared-housing use/standards are not handled.
  Options 9, 10, 11.
- **Two buildings on one lot / split lot** — 12-10 "zoning lot" (captured) is used for scope; no rule
  models subdivision/aggregation or two buildings on one zoning lot. If "split lot" instead means a lot
  divided by a district boundary, the family is 77-00 (**captured, M3-T015**); 36-64 (captured) is only a
  loading-berth pointer into Article VII, Chapter 7 (accessory off-street loading berths), not a general
  C-district counterpart. The meaning is an **open question** (see `options-sections.md`). Options 8, 11.
- **Multi-use FAR combination** — 23-20 (captured) and 35-31; no rule computes the combined ceiling.
  Option 11 inherits every not-handled family above and cannot be fully worked until they are rule-backed.

## 12-10 defined terms that are NOT captured (block clean handling)

These terms are relied on by captured sections but have no snapshot (see `benchmark-r6b-sections.json`
`defined_terms`): Mandatory Inclusionary Housing areas, UAP developments (23-22 footnotes); outer court
(35-631(b)); bulk (34-11/34-21/34-111/35-01); Commercial District / commercial use / community facility
use / residential use (34-11/34-232/35-01/23-52); development / enlargement / conversion (23-52); detached
/ semi-detached / attached / zero lot line building (23-335/23-342); required yard (23-342/23-343).

## Roll-up

The Zoning-Resolution-text domain in the coverage matrix is `partial`: a handful of R6B sections are
captured and computed as unreviewed drafts, while street-wall placement, setback depth, side yards, the
rear-yard baseline, and every overlay / community-facility / parking / shared-housing / split-lot family
remain not handled. No deliverable may emit a single "complete", "compliant", or "buildable" label while
any of these is unresolved.
