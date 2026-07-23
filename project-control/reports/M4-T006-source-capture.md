# M4-T006 Source-Capture Report — R5 Series Height & Setback (post-City of Yes)

Role: official-source-researcher. Purpose: capture CURRENT-effective ZR height & setback
regulations for R5, R5A, R5B, R5D so the rules-engineer can build byte-stable snapshots and
`needs_review` candidate rules; explicit ambiguity assessment. This file is append-only source
capture, not an encoded rule. AI captures/classifies; deterministic code calculates; a qualified
human approves at G6.

Access date: 2026-07-22. Portal: `zr.planning.nyc.gov` (alias `zoningresolution.planning.nyc.gov`),
server-rendered Drupal, bot-friendly (raw `curl` + HTML parse used; NOT summarizer paraphrase for any
value below). Every section cited below carries a machine-readable `<time datetime="2024-12-05...">`
Last-Amended stamp = the City of Yes for Housing Opportunity amendment (effective 2024-12-05).

## Structure discovered (City of Yes renumbering)

City of Yes replaced the legacy §23-66 Quality-Housing / §23-45 non-QH split for LOW-DENSITY
districts with a single building-envelope regime in §23-42 (Height and Setback Requirements in R1
Through R5 Districts). The legacy §23-661/§23-662 numbers still surfaced by third-party summaries
(UpCodes etc.) are STALE for R1–R5 and were NOT used. Governing sections:

- §23-42  overview / measurement (base plane). Last Amended 2024-12-05.
- §23-421 Basic pitched-roof envelopes for certain districts. Last Amended 2024-12-05.
- §23-422 Basic flat-roof envelopes for certain districts. Last Amended 2024-12-05.
- §23-423 Standard setback regulations. Last Amended 2024-12-05.
- §23-424 Height and setback requirements for qualifying residential sites. Last Amended 2024-12-05.
- §23-425 Height and setback modifications for large sites (referenced, not primary here).
- §23-426 Additional height and setback provisions. Last Amended 2024-12-05.
- §23-44  Special Provisions for Certain Areas (23-441/442/443) — special-district/geography overrides.

Envelope selection is by BUILDING TYPE, not just district:
- §23-421 (pitched-roof) applies to: R1 R2 R3A R3X R3-1 R3-2 R4 R4-1 R4A **R5A**, for
  "single- or two-family detached, semi-detached, or zero lot line buildings or other structures,
  where permitted." (verbatim applicability line)
- §23-422 (flat-roof) applies to: R3-2 R4 R4B **R5 R5B R5D** — "the height and setback regulations
  for buildings or other structures shall be set forth in this Section."

So R5A is governed by the pitched-roof envelope; R5 / R5B / R5D by the flat-roof envelope. The four
variants do NOT share dimensions (task's warning confirmed).

## Governing definitions (Article I, §12-10)

- **wide street** — "A 'wide street' is any street 75 feet or more in width." (§12-10, def "street,
  wide"; Last Amended 3/26/2026 — threshold unchanged).
- **narrow street** — "A 'narrow street' is any street less than 75 feet wide." (§12-10, def "street,
  narrow"; Last Amended 12/15/1961).
- **qualifying residential site** — §12-10, Last Amended 2024-12-05. Verbatim (R1–R5 prong): a zoning
  lot, or portion thereof, "in an R1 through R5 District, that: ... has a minimum lot area of at least
  5,000 square feet; is located within the Greater Transit Zone ... has frontage along a wide street
  or along the short dimension of a block; and is not located within an R1 or R2 District; or ..."
  (multiple alternative prongs including community-facility floor space existing on 12/5/2024, and an
  R3-2/R4 prong). This is a complex, geography-dependent applicability (Greater Transit Zone / Outer
  Transit Zone per §66-11, measured to mass-transit stations existing 12/5/2024).

## Per-variant / per-constraint findings (verbatim)

### R5 (no letter suffix) — flat-roof envelope, §23-422
Verbatim: "In the district indicated, except R5 Districts with a letter suffix, the maximum base
height shall be 35 feet, and the maximum building height shall be 45 feet. At a height not higher
than the maximum base height, a setback shall be provided in accordance with Section 23-423."
- Base height: MAX 35 ft. MIN base height: not stated (no minimum base height for R1–R5 basic
  envelope — minimum base height is an R6–R12 Quality-Housing concept, absent here). — CLEAR
- Building height: MAX 45 ft. — CLEAR (street-width independent)
- Setback (above base): §23-423 — "At a height not higher than the maximum base height specified for
  the applicable district, a setback with a depth of at least 10 feet shall be provided from any
  street wall fronting on a wide street, and a setback with a depth of at least 15 feet shall be
  provided from any street wall fronting on a narrow street." Reductions: −1 ft per ft the street
  wall sits beyond the minimum required front yard, floor of 7 ft; optional where the wall is >50 ft
  from a street line or oriented ≤65° to it; recesses/outer courts may count; dormers per 23-413 may
  penetrate. — Depth is CONDITIONAL-ON-UNAVAILABLE-INPUT (wide vs narrow street; and front-yard/lot
  geometry for the reductions).
- Street wall: no street-wall-LOCATION requirement exists for R1–R5 (unlike §23-431 for R6–R12); wall
  placement governed by front-yard regs. Only articulation rule (§23-426): multiple-dwelling street
  walls > 150 ft must recess/project ≥3 ft over ≥20% of surface. — CLEAR (and only bites > 150 ft).

### R5A — pitched-roof envelope, §23-421
Verbatim envelope (uniform for all listed R1–R5A districts, NO R5A-specific numeric override found in
the section): "Perimeter walls are subject to setback regulations at a maximum height above the base
plane of 25 feet." "These planes start at the maximum permitted height of the perimeter walls and
meet at a ridge line of 35 feet above the base plane."
- Base/perimeter-wall height: MAX 25 ft above base plane. — CLEAR
- Building height: ridge line MAX 35 ft above base plane. — CLEAR (street-width independent)
- Setback above base: governed by the sloping-plane / pitched-roof geometry of §23-421 (apex points,
  ≤80° from wall intersection, sloping planes down to the 25-ft perimeter-wall plane), NOT the flat
  10/15-ft §23-423 setback. — CLEAR but geometry-dependent (building-form input).
- Street wall: n/a for low-density detached/semi-detached/zero-lot-line forms.
- Applicability caveat: §23-421 predicated on "single- or two-family detached, semi-detached, or zero
  lot line buildings ... where permitted." Building-type is a condition. — CONDITIONAL on building type.

### R5B — flat-roof envelope, §23-422
Verbatim: "In the district indicated, the maximum building height shall be 35 feet."
- Base height: NOT stated — single flat cap, no base/setback split. — CLEAR (absence is intentional)
- Building height: MAX 35 ft. — CLEAR (street-width independent)
- Setback above base: none required (no maximum base height ⇒ no §23-423 setback trigger). — CLEAR
- Street wall: none / §23-426 articulation only (> 150 ft). — CLEAR

### R5D — flat-roof envelope, §23-422
Verbatim: "In the district indicated, the maximum building height shall be 45 feet."
- Base height: NOT stated — single flat cap. — CLEAR
- Building height: MAX 45 ft. — CLEAR (street-width independent)
- Setback above base: none stated for R5D (contrast R5: same 45-ft building cap but R5 mandates a
  setback above a 35-ft base, R5D does not). — CLEAR. NOTE: encode R5 and R5D SEPARATELY; do not
  reuse R5's base/setback for R5D.
- Street wall: none / §23-426 articulation only. — CLEAR

## Alternative envelope — Qualifying Residential Sites (§23-424), all R1–R5
Verbatim table (districts as grouped in the source): for qualifying residential sites and qualifying
senior housing, "R5 R5A R5B R5D | Maximum Base Height 45 | Maximum Height of Buildings or other
Structures 55" (feet). "At a height not higher than the maximum base height, a setback shall be
provided in accordance with Section 23-423."
- All four R5 variants, IF the lot is a qualifying residential site (or qualifying senior housing),
  may instead use max base height 45 ft / max building height 55 ft, with the §23-423 setback above
  45 ft. — Value CLEAR; applicability CONDITIONAL-ON-UNAVAILABLE-INPUT (the §12-10 "qualifying
  residential site" test: ≥5,000 sf lot, Greater Transit Zone geography, wide-street/short-block
  frontage, district exclusions, community-facility conditions). System likely cannot fully evaluate
  Greater Transit Zone geography ⇒ fail-closed.

## Overriding-context flags (do not encode citywide value as final where these apply)
- §23-426: Historic District (LPC-designated) lots may raise the maximum base height to match an
  adjacent building before setback. — CONDITIONAL overlay.
- §23-44 (23-441/442/443) and any Special Purpose District / zoning overlay may modify these heights
  and setbacks. — CONDITIONAL; encoded citywide rule must yield to special-district/overlay data.
- §23-425 large-site modifications (referenced by §23-42) — separate CONDITIONAL path, out of scope
  here.

## AMBIGUITY ASSESSMENT — bottom line
No GENUINELY AMBIGUOUS item was found. For every R5 variant the official text (§23-421 / §23-422 /
§23-423 / §23-424, all Last Amended 2024-12-05) states specific numeric values under textually clear
conditions. The values CAN be encoded as `needs_review` candidate rules now (qualified human still
approves at G6). Input-dependence, not legal ambiguity, is the only complication and must be handled
fail-closed → `professional_review_required` when the input is unavailable:
1. Wide vs narrow street (75-ft threshold) — affects R5 / QRS setback DEPTH (10 vs 15 ft) only, NOT
   the height caps. CONDITIONAL-ON-UNAVAILABLE-INPUT.
2. Building type (flat vs pitched; detached/semi-detached/zero-lot-line) — selects §23-421 vs §23-422
   and applies to R5A. CONDITIONAL on proposed building form.
3. Qualifying residential site / qualifying senior housing (§23-424 + §12-10 def) — unlocks 45/55.
   CONDITIONAL; complex Greater-Transit-Zone geography ⇒ fail-closed.
4. §23-423 setback reductions (front-yard depth, 7-ft floor, >50 ft / ≤65° optionality) and lot
   geometry — CONDITIONAL on lot/wall geometry.
5. Historic District (§23-426) and Special District / overlay (§23-44) — CONDITIONAL overrides.

## Source URLs (for byte-stable snapshot capture by rules-engineer)
- https://zr.planning.nyc.gov/article-ii/chapter-3/23-42
- https://zr.planning.nyc.gov/article-ii/chapter-3/23-421
- https://zr.planning.nyc.gov/article-ii/chapter-3/23-422
- https://zr.planning.nyc.gov/article-ii/chapter-3/23-423
- https://zr.planning.nyc.gov/article-ii/chapter-3/23-424
- https://zr.planning.nyc.gov/article-ii/chapter-3/23-426
- https://zr.planning.nyc.gov/article-i/chapter-2/12-10  (defs: street wide; street narrow;
  qualifying residential site)
Access notes: raw `curl -A "Mozilla/5.0"` returns HTTP 200 for all above; legal text lives in the
`field--name-body` container; Last-Amended is a `<time datetime=...>` stamp. Per-section amendment
history is also available via the portal AJAX channel
`GET /ajax/get/amendment/section/{sectionEntityId}?_wrapper_format=drupal_ajax` (X-Requested-With:
XMLHttpRequest). Prefer official ZR text over UpCodes/law-firm summaries (the latter still cite the
stale §23-66x numbering for R1–R5).

## Representative raw response excerpt (§23-422 body, tag-stripped)
"R3-2 R4 R4B R5 R5B R5D / In the districts indicated, the height and setback regulations for buildings
or other structures shall be set forth in this Section. / R5B In the district indicated, the maximum
building height shall be 35 feet. / R5 In the district indicated, except R5 Districts with a letter
suffix, the maximum base height shall be 35 feet, and the maximum building height shall be 45 feet.
At a height not higher than the maximum base height, a setback shall be provided in accordance with
Section 23-423. / R5D In the district indicated, the maximum building height shall be 45 feet."
