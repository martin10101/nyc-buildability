# M4-T016 - A2 geometry-mechanics research (D-045-R002; consumes accepted M4-T015)

Producer: official-source-researcher. Date: 2026-09-13. Scope: RESEARCH ONLY - no connector
code, no fixtures, no dependency, no schema touched. This report is the research-first
deliverable the later A2 build packets pin. Pin read: `project-control/reports/M4-T013-street-width-research.md`
(OQ-3/OQ-4 verbatim, the 75-ft mathematical-entailment rule). RQ-001/RQ-005 in
`docs/RESEARCH_REQUESTS.md` are OPEN (non-blocking per D-050); this report does the work itself.

**Search method (honest, up front):** (1) `WebSearch` to locate section numbers and the current
Article II Chapter 3 structure (post-City-of-Yes-for-Housing-Opportunity renumbering, Last Amended
2024-12-05 on the touched sections); (2) `WebFetch` on individual section URLs for a first read;
(3) where `WebFetch`'s small summarizer model truncated a large page (12-10 is a single ~1.3 MB
page holding every ZR defined term A-Z) or where a verbatim byte-exact capture was load-bearing, a
**direct HTTPS GET** (`curl -A Mozilla/5.0`, no auth, no bot-wall - zoningresolution.planning.nyc.gov
is bot-friendly, confirmed) of the canonical page, hashed and parsed locally. The `entityprint/pdf/node/<id>`
print-render channel (the completeness channel proven in prior tasks, e.g. M4-T012) was **attempted
twice** for the 12-10 mega-page (`https://zoningresolution.planning.nyc.gov/entityprint/pdf/node/18523`)
and **failed both times with HTTP 504 Gateway Timeout** - recorded honestly rather than retried
indefinitely; the direct-HTML-GET channel substituted successfully and is itself the canonical
rendered legal text (byte-captured, sha256-pinned below). **Completeness posture:** Article II
Chapter 3 (Residential Bulk Regulations in Residence Districts) was traversed section-by-section
from its own table of contents and internal cross-references (23-40 -> 23-41/23-411 -> 23-42/23-43
-> 23-432/23-433 -> 23-73 -> 23-731/23-736/23-737/23-738/23-739); every section this report cites
was independently confirmed by at least one live fetch today. Sections explicitly **out of scope
and NOT walked to completion** are listed in Part 4 (limitations) - this is not a claim of total
citywide ZR coverage.

All raw capture files referenced below live only in the session scratchpad (thin client - not
committed; sha256 + byte count + URL + retrieval date constitute the provenance record, matching
the M4-T013/M2-T021 pattern of recording digests rather than shipping bulk captures).

## 0. Bottom line

- The R6-R12 geometry-dependent height/setback mechanic is **NOT one section** - it is a routed
  chain: **23-432** (the base/max-height TABLE, wide/narrow-independent numbers) -> **23-433**
  (the STANDARD setback, wide/narrow-DEPENDENT depth) -> **23-73 series** (an OPTIONAL alternative
  regime for un-suffixed R6-R10 lots only, wide/narrow-DEPENDENT sky-exposure-plane slopes) ->
  **23-411/23-41** (permitted obstructions, penetrate either regime, wide/narrow-INDEPENDENT).
  R11/R12 sit in the 23-432/23-433 table/setback regime only - the 23-73 sky-exposure-plane
  alternative is NOT available to them (23-731 applicability is scoped to "R6 through R10
  Districts without a letter suffix").
- **Central finding for OQ-4/the A2 build:** the §12-10 "wide street" definition is materially
  MORE COMPLEX than the flat 75-ft threshold the M4-T013 pin and the existing DCM connector
  (M4-T015) encode. A live capture today shows the "street, wide" defined-term entry was
  **Last Amended 3/26/2026** - a DIFFERENT (later) date than "street, narrow" (Last Amended
  12/15/1961, unchanged) - and its current verbatim text adds (a) a Commercial-district-scoped
  (C5-3/C6-4/C6-6) alternate-width/street-line-continuity clause and (b) two NAMED-STREET
  designations (a Broadway segment in Manhattan CD7, an Allen Street segment in Manhattan CD3)
  that are unconditionally "considered a wide street" regardless of measured width. This is a
  genuine discrepancy against the prior research pin's captured text (section 3, flagged as an
  open question, NOT resolved here).
- The DCM connector's "geometry flip" (packet shorthand) is, precisely: the connector's ArcGIS
  query does **not** set `returnGeometry` at all, so the service's own default (`true`) means
  polyline geometry bytes ARE transported today (confirmed by the M4-T015 fixture manifest note
  on the `Margaret Corbin Drive` fixture's larger byte size); `parse_segment_page` simply never
  reads `feature["geometry"]` - only `feature["attributes"]`. The build item is "parse, validate,
  and expose the polyline geometry that is already arriving," not "flip a boolean to start
  receiving it" - a precise correction to the packet's own shorthand, not a guess.
- The MapPLUTO side of OQ-4 already has a fit-for-purpose measurement-grade connector
  (`mappluto_geometry_arcgis.py`: authoritative EPSG:2263, CRS-validated, geometry-validity-typed,
  canonical-digested, 20-ft boundary tolerance). The sibling `mappluto_lot_outline.py` is
  EXPLICITLY display-only (EPSG:4326, "no area, dimension, or any measurement is EVER computed
  from these degree coordinates") and must NOT be used for the buffer test.
- OQ-3 (the ZR-grounded fail-closed policy for ambiguous DCM width classes) is surfaced, never
  resolved, per the binding constraint.

## Part 1 - ZR section map: R6-R12 geometry-dependent height/setback mechanics

### 1.1 Section map table

| Section | Exact title (as rendered) | Districts named | Wide/narrow changes the numbers? | §12-10 defined terms leaned on |
|---|---|---|---|---|
| **23-432** | "Height and setback requirements" | R6, R7, R8, R9, R10, R11, R12 (table header row, verbatim) | NO for the base table itself (minimum base height / maximum base height / maximum building height are per-district-designation values only); the wide/narrow dependence enters downstream via 23-433 | *building*, *street wall*, *zoning lot*, *qualifying affordable housing*, *qualifying senior housing* |
| **23-433** | "Standard setback regulations" | R6, R7, R8, R9, R10, R11, R12 (same header) | **YES** - "a setback with a depth of at least 10 feet shall be provided from any street wall fronting on a wide street, and a setback with a depth of at least 15 feet shall be provided from any street wall fronting on a narrow street" (verbatim) | *wide street*, *narrow street*, *street wall*, *street line* |
| **23-731** | "Applicability" (of the 23-73 sky-exposure-plane-building alternative) | "R6 through R10 Districts without a letter suffix" ONLY, with named carve-outs excluded (R6-1, R6-2, R7-3, R9-1; part of Manhattan CD9 north of W 125th St for un-suffixed R8; Limited Height Districts) | N/A (applicability gate, not a numeric provision) | *zoning lot*, *Limited Height Districts* |
| **23-736** | "Special height and setback regulations for sky exposure plane buildings" | R6, R7, R8, R9, R10 (un-suffixed only, per 23-731) | **YES** - both the initial setback distance AND the sky-exposure-plane slope differ by street width (table, section 1.2 below) | *street line*, *sky exposure plane* (a.k.a. *front sky exposure plane*), *wide street*, *narrow street*, *building or other structure* |
| **23-737** | "Tower regulations" (cross-referenced by 23-736: "In R9 or R10 Districts, towers may penetrate a sky exposure plane pursuant to Section 23-737") | R9, R10 | Not independently verified this task (out of scope per Part 4; cross-reference only, confirmed to exist and to be the tower-penetration exception) | *sky exposure plane* |
| **23-738** | "Height limitations for narrow buildings or enlargements" (cross-referenced by 23-736: "for narrow buildings, the provisions of Section 23-738 shall apply") | Referenced from the 23-73 series (R6-R10 un-suffixed) | Not independently verified this task (title only, confirmed to exist) | not verified this task |
| **23-739** | "Limited Height Districts" (cross-referenced by 23-736 and 23-731) | Limited Height Districts (a mapped overlay, separate from R6-R12 base designations) | Not independently verified this task (title only, confirmed to exist) | *Limited Height Districts* |
| **23-411** | "General permitted obstructions" | "In all Residence Districts" (verbatim, so R6-R12 included) | NO - the obstruction list (awnings, building columns, chimneys/flues, decks, flagpoles, parapets/railings/safety guards, skylights, solar equipment, vegetated roofs, stormwater equipment, window-washing equipment, transparent fences) is wide/narrow-independent; the verbatim opening clause is "the following obstructions shall be permitted to penetrate a maximum height limit **or sky exposure plane**" - i.e. it explicitly penetrates BOTH the 23-432/23-433 regime and the 23-73 sky-exposure-plane regime | *Residence Districts*, *sky exposure plane*, *street wall*, *initial setback distance* |
| **23-41** | "Permitted Obstructions" (chapter head; 23-411 is its first numbered subsection) | "In all Residence Districts, the obstructions set forth in this Section, inclusive, shall be permitted to penetrate a maximum height limit set forth in Sections 23-42 ... 23-43 ... or 23-44" (verbatim opening, confirmed via WebFetch of the section head) | NO (routing/chapter-head section) | n/a |

Every row above except 23-737/23-738/23-739 (title-only, explicitly flagged not-independently-verified)
carries a verbatim quote captured today (below) plus a live URL and retrieval date.

### 1.2 23-736 numeric table (verbatim values, both capture channels agree)

Captured via `WebFetch` (paraphrase-summary) AND independently via direct HTTPS GET + local
regex extraction (byte-exact, both channels cross-checked and agree on every number):

| District group | Initial setback distance (narrow / wide, ft) | Max front-wall height within setback | Sky exposure plane slope (narrow / wide) |
|---|---|---|---|
| R6 or R7 | 20 / 15 | "60 feet or six stories, whichever is less" | 2.7 to 1 / 5.6 to 1 |
| R8, R9 or R10 | 20 / 15 | "85 feet or nine stories, whichever is less" | 2.7 to 1 / 5.6 to 1 |

Alternate front setback (paragraph (b), an open-area-along-the-entire-front-lot-line option):
open-area depth 15 ft (narrow) / 10 ft (wide); alternate slopes 3.7 to 1 (narrow) / 7.6 to 1
(wide), base heights unchanged (60 ft R6/R7, 85 ft R8-R10). All four slope strings (`2.7`, `5.6`,
`3.7`, `7.6`) were confirmed present verbatim in the raw captured HTML bytes (grep-verified against
the sha256-pinned file, section 1.4).

Verbatim opening text (23-736, direct capture): *"In the districts indicated without a letter
suffix, for sky exposure plane buildings, the height and setback regulations shall be as set forth
in this Section, inclusive. Buildings may elect to utilize the front setback provisions of
paragraph (a) of this Section, or the alternate front setback provisions of paragraph (b) of this
Section. Where elected, such provisions shall supersede the provisions of Section 23-43,
inclusive."* -- i.e. this is an OPTIONAL, elective alternative to the 23-432/23-433 table regime,
not an additional stacked requirement. This election point is itself an A2 build-scope decision
(does the platform model both regimes and let the two heights be compared, or only compute the
mandatory 23-432/23-433 regime and surface 23-73 as a conditional alternative, mirroring how the
existing `r6_r7_r8_wide_street_conditional_far.rule.json` already surfaces its own wide-street
alternative as `conditional_alternative` rather than applying it) - flagged as a build-packet
decision point in Part 4, not decided here.

23-433 verbatim (direct capture): *"At a height not lower than the minimum base height or higher
than the maximum base height specified for the applicable district, a setback with a depth of at
least 10 feet shall be provided from any street wall fronting on a wide street, and a setback with
a depth of at least 15 feet shall be provided from any street wall fronting on a narrow street.
... The depth of such required setback may be reduced by one foot for every foot that the street
wall is located beyond the street line, but in no event shall a setback of less than seven feet in
depth be provided, except as otherwise set forth in this Section. ... These setback provisions are
optional for any building wall that either is located beyond 50 feet of a street line, or oriented
so that lines drawn perpendicular to it, in plan, would intersect a street line at an angle of 65
degrees or less."* This "beyond 50 feet of a street line" / "65 degree" carve-out is itself a
geometry test distinct from (and narrower in scope than) the OQ-4 100-ft wide-street buffer test -
recorded as a related-but-separate mechanic, not conflated with OQ-4.

23-411 verbatim opening (direct capture): *"In all Residence Districts, the following obstructions
shall be permitted to penetrate a maximum height limit or sky exposure plane. These allowances are
generally common to Residence, Commercial and Manufacturing Districts."* Selected dimensioned
items (all verbatim numbers, direct capture): awnings/sun-control devices "maximum projection from
a building wall of 2 feet, 6 inches" above the first story; building columns "aggregate width equal
to not more than 20 percent of the aggregate width of street walls," depth "not exceeding 12
inches"; chimneys/flues "total width not exceeding 10 percent of the aggregate width of street
walls"; decks "not more than 3 feet, 6 inches in height."

### 1.3 §12-10 defined terms (verbatim, with the dates that matter)

All captured via direct HTTPS GET of `https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10`
today (2026-09-13; sha256 below), each term located by its own `id="term-<name>"` anchor in the raw
HTML and extracted from the `definition__definition` block:

| Term | Last Amended | Verbatim text |
|---|---|---|
| **Street line** | 10/25/1973 | "A 'street line' is a lot line separating a street from other land. A street setback line supersedes the street line in the application of yard, height and setback, and court regulations." |
| **Street wall** | 12/15/1961 | "A 'street wall' is a wall or portion of a wall of a building facing a street." |
| **Base plane** | 5/12/2021 | "The 'base plane' is a plane from which the height of a building or other structure is measured as specified in certain Sections. For buildings, portions of buildings with street walls at least 15 feet in width, or building segments within 100 feet of a street line, the level of the base plane is any level between curb level and street wall line level. Beyond 100 feet of a street line, the level of the base plane is the average elevation of the final grade adjoining the building or building segment, determined in the manner prescribed by the New York City Building Code for adjoining grade elevation." (subsections (a)-(c) continue with corner-lot/through-lot/sloping-site detail, captured in full in the raw file, not reproduced here for length) |
| **Sky exposure plane, or front sky exposure plane** | **4/18/1987** (unchanged since - the OLDEST of the terms captured here) | "A 'sky exposure plane' or 'front sky exposure plane' is an imaginary inclined plane: (a) beginning above the street line (or, where so indicated, above the front yard line) at a height set forth in the district regulations; and (b) rising over a zoning lot at a ratio of vertical distance to horizontal distance set forth in the district regulations." |
| **Narrow street** (canonical entry filed as "Street, narrow") | 12/15/1961 (unchanged) | "A 'narrow street' is any street less than 75 feet wide." |
| **Wide street** (canonical entry filed as "Street, wide") | **3/26/2026** (recently amended - see 1.4) | Full text in section 1.4 below (multi-paragraph, quoted in full - too long for this table cell). |

The site files "wide street"/"narrow street" alphabetically under **"street, wide"** /
**"street, narrow"**, not under "W"/"N" - a lookalike entry exists at the plain "wide street" /
"narrow street" alphabetical slot but its body is only a one-line cross-reference ("see street,
wide" / "see street, narrow"), confirmed live; the citable definitional text lives at the
"street, wide"/"street, narrow" entries.

### 1.4 The "wide street" discrepancy (central Part-1 finding, flagged not resolved)

Verbatim, captured today from the "street, wide" entry (Last Amended 3/26/2026):

> "A 'wide street' is any street 75 feet or more in width. In C5-3, C6-4 or C6-6 Districts, when a
> front lot line of a zoning lot adjoins a portion of a street whose average width is 75 feet or
> more and whose minimum width is 65 feet, such portion of a street may be considered a wide
> street; or when a front lot line adjoins a portion of a street 70 feet or more in width, which is
> between two portions of a street 75 feet or more in width, and which portion is less than 700
> feet in length, such portion may be considered a wide street, and in that case, for the purposes
> of the height and setback regulations and the measurement of any publicly accessible open area or
> arcade, the street line shall be considered to be a continuous line connecting the respective
> street lines of the nearest portions of the street which are 75 feet or more in width."
>
> "In Community District 7 in the Borough of Manhattan, the roadways of Broadway between West 94th
> and West 97th Streets and in Community District 3 in the Borough of Manhattan, the roadways of
> Allen Street between Rivington and Delancey Streets, which are separated by mapped public park
> shall each be considered a wide street."

**Why this is flagged, not resolved (never an interpretation call in this task):**

1. The **M4-T013 pin** (this task's own required-reading input) and the existing
   `docs/research/zr-snapshots/v1/zr-12-10.snapshot.json` (a DIFFERENT, R1-R5-scoped prior capture,
   retrieved 2026-07-22) both carry only the flat one-sentence form ("A wide street is a street that
   is 75 feet or more in width. A narrow street is a street that is less than 75 feet in width."),
   with NO mention of the C5-3/C6-4/C6-6 clause or the two named-street designations. Today's live
   "street, wide" Last-Amended stamp (3/26/2026) is LATER than both of those prior captures'
   retrieval dates, so this is not new law that appeared after the prior work - it means the prior
   captures' text was already incomplete/simplified relative to the live site at the time they were
   taken. This is an evidenced discrepancy between two official-source captures of the "same"
   definition at different times, not a guess.
2. The Commercial-district-scoped clause (C5-3/C6-4/C6-6) is facially outside R6-R12 pure Residence
   Districts, but ZR zoning lots frequently straddle a Commercial overlay or a Residence-equivalent
   Commercial District mapping (the existing `r6_r7_r8_wide_street_conditional_far.rule.json`
   consumer's own `special_district_interactions` stub already flags Special Purpose District /
   overlay modification as unhandled) - whether this clause can ever be reachable for an R6-R12
   applicability path is a genuine open question, not decided here.
3. The two named-street "considered a wide street" designations (Broadway W94-97 Manhattan CD7;
   Allen St Rivington-Delancey Manhattan CD3) are **unconditional legislative designations** that no
   width-measurement or DCM `Streetwidth` field value can ever produce - a geometry/attribute-driven
   OQ-4 computation will silently miss them unless a small, explicitly-sourced named-street override
   table is added as a build-packet requirement (Part 3/4).
4. **This is an OQ-3/OQ-4-adjacent research finding about the DEFINITION's own text, not a resolution
   of OQ-3 (the ambiguity-class fail-closed policy) or OQ-4 (the buffer geometry) themselves** - both
   stay open, per the binding constraint. The correct next step is a G6-class / architect-doc review
   of which prior capture is authoritative-as-of-effective-date and whether the M4-T013/M4-T015
   pipeline needs a corrective pass; this report does not make that call.

Provenance for this finding: direct HTTPS GET, `https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10`,
retrieved 2026-09-13, raw file sha256 `0c341a0b55eb7bc0bea817144c434b4d229de41c7f7ebc9c1b021e2f824dd977`
(1,316,667 bytes); term located at HTML anchor `id="term-street, wide"` and `id="term-street, narrow"`.

## Part 2 - OQ-4 geometry-mechanic design (within 100 ft of a wide street)

### 2.1 The governing text (quoted, not paraphrased)

ZR 23-22 footnote 1 (already pinned verbatim in `r6_r7_r8_wide_street_conditional_far.rule.json`
citations and in the M4-T013 report): *"For zoning lots, or portions thereof, located within 100
feet of a wide street."* Combined with the §12-10 "wide street" definition (Part 1.3/1.4), the full
test a zoning lot must pass, per portion, is: **is this portion of the lot within 100 horizontal
feet of a street segment that qualifies as a "wide street" under §12-10** (the 75-ft-or-more
default rule, OR one of the C5-3/C6-4/C6-6 alternate-width clauses, OR one of the two named-street
designations)?

### 2.2 Geometric operations (design, not implementation)

1. **Inputs.** (a) DCM Street Center Line polyline geometry for the street segment(s) fronting or
   near the lot, in **EPSG:2263** (the source's own native CRS - section 2.3); (b) the DCM
   `Streetwidth` free-text field, run through the ALREADY-ACCEPTED `dcm_street_width_classifier`
   (M4-T015) to get `effective_disposition` in `{wide, narrow_fail_closed}` per segment (never
   re-implemented here); (c) the MapPLUTO zoning-lot polygon for the subject BBL, in EPSG:2263, from
   the ALREADY-ACCEPTED `mappluto_geometry_arcgis` connector (M2-T009).
2. **Step A - classify segments.** For every DCM segment within a generous search radius of the lot
   (e.g. lot bounding-box buffered by 100+ ft, to bound the query - an implementation choice for the
   build packet, not decided here), apply the M4-T015 classifier's `effective_disposition`. Only
   segments disposed `wide` (mathematically-entailed >= 75 ft AND a currently-mapped, non-paper,
   non-record street per the M4-T015 override) participate in the buffer test. Everything else
   (including every `narrow_fail_closed` disposition, by construction) is excluded - this preserves
   the already-accepted fail-closed posture without re-deciding OQ-3.
3. **Step B - construct the 100-ft buffer.** For each `wide`-disposed segment's polyline geometry,
   compute a **planar buffer of 100.0 US survey feet** (a linear operation, valid only because the
   CRS is a projected, foot-unit CRS - EPSG:2263 - never performed in unprojected WGS84 degrees; see
   section 2.3). This mirrors the existing `mappluto_geometry_arcgis` module's own discipline of
   never computing measurement in a non-authoritative CRS.
4. **Step C - intersect with the lot polygon.** Compute `lot_polygon.intersects(segment_buffer)` (a
   boolean "any portion" test, matching footnote 1's "or portions thereof" language) and, for the
   rule layer's benefit, `lot_polygon.intersection(segment_buffer)` (the actual sub-area within 100
   ft, so a downstream rule can apportion FAR by area the way `r6_r7_r8_wide_street_conditional_far.rule.json`'s
   own limitations section anticipates: "a single lot can be split between the two values - a
   geometry computation, not a table lookup").
5. **Step D - the named-street/alternate-width override (2.4/Part 1.4).** Before Step A excludes a
   segment as `narrow_fail_closed`, a segment whose location matches one of the two named-street
   legislative designations (Broadway W94-97 Manhattan CD7; Allen St Rivington-Delancey Manhattan
   CD3) must be treated as `wide` regardless of its DCM `Streetwidth` reading - because no
   width-measurement can encode a legislative designation. **This override does not exist in any
   accepted connector today** - recorded as a build-packet requirement (Part 3/4), not built here.

### 2.3 Units/projection evidence (from the sources' own documentation, never assumed)

- DCM Street Center Line ArcGIS layer: `spatialReference` `wkid 102718` / `latestWkid 2263`
  (already live-verified in M4-T013/M4-T015, re-confirmed by this task's read of
  `dcm_street_centerline_arcgis.py`'s `EXPECTED_WKID`/`EXPECTED_LATEST_WKID` constants and their
  docstring citation of the DCP metadata PDF: "NAD_1983_StatePlane_New_York_Long_Island_FIPS_3104_Feet").
- MapPLUTO ArcGIS layer: the same EPSG:2263/wkid 102718 CRS, per `mappluto_geometry_arcgis.py`'s own
  design-commitments docstring (item 2: "the authoritative source CRS (EPSG:2263 / wkid 102718, NAD83
  New York Long Island, US survey feet) is validated from service metadata and from every query
  envelope BEFORE any coordinate is interpreted").
- **Independent, non-DCP confirmation that EPSG:2263's unit is specifically the US survey foot** (not
  the international foot - a real distinction with a ~2 ppm difference that matters for a 100-ft
  buffer over a long lot boundary): `https://epsg.io/2263` (an EPSG-registry mirror; the primary
  registry `epsg.org/crs_2263/...` returned HTTP 403 to this fetch, recorded honestly rather than
  substituted silently), retrieved 2026-09-13, quoting: "CRS Name: 'NAD83 / New York Long Island
  (ftUS)' ... Unit: US survey foot." The "(ftUS)" suffix in the CRS's own name is itself the
  authoritative signal DCP's ArcGIS `wkid`/`latestWkid` pair resolves to.
- **Both source geometries share the identical CRS** - no reprojection is required between the DCM
  polyline and the MapPLUTO polygon before the buffer/intersection operations, which removes an
  entire class of reprojection-introduced error from the OQ-4 computation. This is a positive,
  evidenced design simplification, not an assumption.

### 2.4 Edge cases (inventoried, not resolved)

1. **Corner lots / multiple frontages.** A corner or through lot can have two or more fronting
   street segments with DIFFERENT `effective_disposition` values (e.g. one wide, one narrow) - the
   buffer/intersection design in 2.2 already handles this correctly by construction (each qualifying
   segment contributes its own buffer, unioned before intersecting the lot), but the RESULT is a lot
   split into wide-eligible and non-wide-eligible sub-areas, which is exactly the "portions thereof"
   case the consumer rule's `limitations` already anticipates but does not compute.
2. **Irregular/ambiguous segments.** A DCM segment whose `Streetwidth` is one of the many
   ambiguity classes cataloged by the M4-T015 classifier (`range_straddles_cutoff`,
   `approximate_or_hedged_value_ambiguous`, `width_irregular`, etc.) is EXCLUDED from the buffer set
   entirely (Step A), because it never reaches `effective_disposition == wide`. This means a lot
   that is genuinely within 100 ft of what might be a real wide street, but whose DCM width value is
   messy, will be conservatively scored as NOT within 100 ft of a wide street - consistent with the
   project's fail-closed posture, but an honest under-claim the build packet must document exactly
   like the M4-T013 report's own tradeoff section does for the classifier alone.
3. **Segment self-intersection / non-simple polylines and multi-segment named streets.** The DCM
   product is per-block-face segmented (confirmed by the M4-T015 West-100th-Street fixture: one
   named street, two adjacent segments, two different widths); a street corridor near a lot may
   therefore be represented by several distinct segment records with DIFFERENT dispositions -
   handled by 2.2 Step A/B operating per-segment, but the build packet must NOT assume a named
   street has a single uniform width across its length (already false per the accepted M4-T015
   fixture, and reinforced by the "wide street" definition's own "portion of a street" language,
   Part 1.4).
4. **Lots touching the buffer boundary exactly at 100 ft.** A geometry `intersects` predicate at an
   exact tangency is a genuine floating-point-boundary case; no official source states a rounding
   or tolerance convention for this test. The existing `mappluto_geometry_arcgis` module's own
   `BOUNDARY_TOLERANCE_FT = 20.0` constant is sourced from the MapPLUTO product's own +/-20-ft
   *horizontal accuracy* disclosure (an entirely different concept: positional accuracy of the
   surveyed geometry, not a legal buffer-boundary allowance) and must NOT be silently reused as a
   100-ft-buffer tolerance without a fresh, explicitly-sourced justification - flagged as an open
   design question for the build packet, not resolved here.
5. **The C5-3/C6-4/C6-6 alternate-width clause and the two named-street designations (Part 1.4).**
   Recorded as edge cases the geometry design in 2.2 explicitly could NOT satisfy from DCM data
   alone (2.2 Step D); the named-street case requires a small, explicitly-sourced override table
   (two rows) as a build-packet input, and the C5-3/C6-4/C6-6 clause requires a scope decision
   (Part 1.4 item 2) before any implementation.
6. **Missing/no DCM segment for a mapped or paper street near the lot.** The M4-T015 connector
   already types this (an empty `features` page is a normal, not-erroneous outcome; `Feat_Type`
   values outside the documented domain are typed schema drift). The buffer/intersection design must
   propagate an honest "no wide-street segment found nearby" result rather than defaulting either
   way - an explicit design requirement for the build packet, not a numeric edge case.

## Part 3 - Data-input fit (against the accepted connectors, from the code as it exists)

### 3.1 DCM connector (`dcm_street_centerline_arcgis.py`, accepted M4-T015)

**What exists today:** a bounded, paginated, injection-proof ArcGIS query returning 17 typed
attribute fields per segment (`OUT_FIELDS`, explicitly excluding the geometry field by design - the
module's own docstring states "geometry buffer/within-100-ft computation (OQ-4)" is "NOT in scope"
for that packet) plus the pure free-text width classifier (`dcm_street_width_classifier.py`,
exhaustive ambiguity-class table) and the one additional mapped-street/paper-street/record-street
fail-closed override this connector owns on top of the classifier.

**What OQ-4 needs that is NOT there today:**
1. **Polyline geometry, parsed and typed.** The ArcGIS query today does not set `returnGeometry`
   (verified: the literal string does not appear anywhere in `build_segment_query_url` or the rest
   of the module), so the service's documented default (`true`) means geometry bytes are already
   arriving on the wire - confirmed independently via the M4-T015 fixture manifest's own note on the
   `unknown_hedged_below_75.json` fixture ("Larger byte size than sibling fixtures reflects this
   segment's own polyline vertex count (returnGeometry defaults true on this endpoint); no
   anomaly"). `parse_segment_page` (the only parsing function) reads `feature["attributes"]`
   exclusively and never touches `feature.get("geometry")` - so the geometry is fetched and then
   silently dropped. **Build requirement:** parse the polyline `geometry.paths` array into a typed,
   CRS-validated geometry object (mirroring the geometry-validity taxonomy discipline already proven
   in `mappluto_geometry_arcgis.py`), and expose it on `StreetSegment` (or a new sibling type) -
   this is an additive change to an already-accepted, byte-immutable-per-project-convention module,
   so the build packet must decide whether to extend `dcm_street_centerline_arcgis.py` in place or
   add a new sibling transport module (the `mappluto_lot_outline.py`-beside-`mappluto_geometry_arcgis.py`
   precedent for "new focused module, read-only reuse of the existing one's public discipline" is
   directly applicable and is the pattern this report recommends, Part 4).
2. **No buffer/intersection utility exists anywhere in the connectors reviewed for this task.**
   `mappluto_geometry_arcgis.py` computes area (`compute_area_sq_ft`) and geometry-validity
   assessments, and its `classify_spatial_relation` is explicitly named as "a TEST-LEVEL diagnostic
   ... NOT a production spatial-intersection engine (out of scope per packet)" - so a genuine new
   production geometry-operations module (buffer + intersect, CRS-guarded) is a clean gap, not an
   extension of an existing one.
3. **No named-street override table** for the two §12-10 legislative "considered a wide street"
   designations (Part 1.4/2.4 item 5) - genuinely new, tiny, and must cite the exact §12-10 text
   captured in this report rather than being re-derived.

### 3.2 MapPLUTO connectors (`mappluto_geometry_arcgis.py`, `mappluto_lot_outline.py`)

**What exists today (measurement-grade, fit for OQ-4's lot-polygon input):**
`mappluto_geometry_arcgis.py` - per-BBL polygon, EPSG:2263-validated before any coordinate is
interpreted, an explicit geometry-validity taxonomy (`valid`/`repaired`/`invalid_geometry`/
`review_required`), never-silent repair with original-vs-repaired digests kept separate, a
deterministic canonicalization spec (`MPG_CANONICALIZATION_SPEC`, 0.01-ft coordinate precision),
and the `BOUNDARY_TOLERANCE_FT = 20.0` constant (MapPLUTO's own +/-20-ft accuracy disclosure - a
DIFFERENT concept from a 100-ft legal buffer, per 2.4 item 4). This is the correct input for OQ-4's
lot-polygon side; no gap for the polygon geometry itself.

**What is explicitly NOT fit for OQ-4:** `mappluto_lot_outline.py` is display-only by design
("DISPLAY-ONLY DISCIPLINE ... No area, dimension, or any measurement is EVER computed from these
degree coordinates anywhere in this module") and transports EPSG:4326 (WGS84 degrees), not
EPSG:2263 - using it for a 100-ft buffer test would be a CRS violation of the exact kind
`mappluto_geometry_arcgis.py` itself refuses (`WrongCRSError`). The OQ-4 build packet must consume
`mappluto_geometry_arcgis.py`, never `mappluto_lot_outline.py`.

### 3.3 Summary gap table

| Input OQ-4 needs | Exists today? | Gap (build-packet requirement) |
|---|---|---|
| Street-segment polyline geometry, EPSG:2263, typed | Fetched (default `returnGeometry=true`) but discarded | Parse + type + CRS-validate the geometry already on the wire |
| Street-segment wide/narrow disposition | YES (M4-T015, accepted, reused as-is) | none |
| Mapped-street/paper-street override | YES (M4-T015, accepted, reused as-is) | none |
| Lot polygon, EPSG:2263, measurement-grade | YES (`mappluto_geometry_arcgis.py`, accepted) | none |
| Buffer + intersection geometry operation | NO | New module (production-grade, not the existing test-only diagnostic) |
| Named-street "considered wide" override | NO | New, small, explicitly-sourced (Part 1.4) lookup |
| Ambiguous/irregular segment handling policy | Classifier fails closed (M4-T015); the LEGAL fail-closed-per-class policy is OQ-3 | OQ-3 stays open (G6-class ruling), never built around by assumption |

## Part 4 - Limitations, open questions, build-packet decomposition

### 4.1 Honest limitations of this report

- **R11/R12 numeric detail** was confirmed present in the 23-432/23-433 table header row
  ("R6 R7 R8 R9 R10 R11 R12") and the 23-433 setback text, but the FULL 23-432 numeric table (every
  letter-suffix district row: R6A, R6B, R6D, R7A, R7B, R7D, R7X, R8A, R8B, R8X, R9A, R9D, R9X, R10A,
  R10X, R11A, R11B/R12 etc.) was captured in raw form (sha256-pinned) but not individually
  transcribed into this report for every row - the table exists and is byte-available in the pinned
  capture; a build packet extracting specific numeric values must re-read the pinned raw file (or
  refetch and re-verify) rather than trusting a partial transcription here.
- **23-737 (Tower regulations), 23-738 (narrow buildings/enlargements), and 23-739 (Limited Height
  Districts)** were confirmed to exist (table of contents + cross-references in 23-736/23-731) but
  their own numeric/operative text was NOT independently fetched and verified this task - explicitly
  flagged, not silently assumed, in the section-map table (1.1).
- **Qualifying-site / large-site height increases** (the R6-R12 analog of the R1-R5 23-424/23-425
  pointers seen in the read-only `zr-23-42.snapshot.json` reference) were not investigated for
  R6-R12 - out of scope for this pass, a gap for a future research task if the A2 build needs it.
- **Special Purpose District / overlay modification** of any of these mechanics is explicitly
  out of scope, consistent with the existing consumer rule's own `special_district_interactions`
  stub ("this general rule does not apply the modification").
- The **"wide street" discrepancy (Part 1.4)** is the single most consequential limitation: it
  means neither this report nor the accepted M4-T015/M4-T013 chain has a settled, single verbatim
  text for the term the entire OQ-4 computation turns on. This is surfaced prominently, not buried.
- Search coverage relied on `WebSearch` for discovery and either `WebFetch` or direct HTTPS GET for
  verification; no browser-rendered/JS-dependent capture was attempted (not needed - the site is
  server-rendered Drupal, confirmed working with a plain `curl`).

### 4.2 Open questions (carried forward, none resolved by assumption)

1. **OQ-3** (ambiguity-class fail-closed policy for DCM free-text widths) - stays fail-closed-to-narrow,
   routed to a G6-class ruling. NOT resolved in this task (binding constraint honored).
2. **OQ-4-a (new, this task):** which capture of the §12-10 "wide street" definition is authoritative
   as of which effective date - the flat 75-ft form (M4-T013 pin, `zr-12-10.snapshot.json`) or the
   fuller Last-Amended-3/26/2026 form captured live today (Part 1.4)? Whether the M4-T013 pin needs
   a corrective addendum. Routed for architect/G6 review; not decided here.
3. **OQ-4-b (new, this task):** are the two named-street "considered a wide street" designations
   (Broadway W94-97 Manhattan CD7; Allen St Rivington-Delancey Manhattan CD3) in scope for the A2
   build at all, given their real-world footprint is two short, specific segments? A scope decision,
   not a research finding to resolve unilaterally.
4. **OQ-4-c (new, this task):** is the C5-3/C6-4/C6-6 alternate-width/street-line-continuity clause
   (Part 1.4) ever reachable for a lot whose applicable district is R6-R12, given mixed-use/overlay
   mapping realities? A scope/legal question, not decided here.
5. **OQ-4-d (new, this task):** what tolerance/rounding convention, if any, applies to a lot boundary
   that is exactly tangent to the 100-ft buffer (2.4 item 4)? No official source located states one;
   the existing 20-ft `BOUNDARY_TOLERANCE_FT` is a DIFFERENT concept (positional accuracy, not legal
   buffer allowance) and must not be silently repurposed.
6. **OQ-4-e (new, this task):** does the platform need to model the OPTIONAL 23-73 sky-exposure-plane
   alternative regime at all for un-suffixed R6-R10 lots, or only the mandatory 23-432/23-433 table
   regime (mirroring the existing wide-street-FAR rule's own conditional-alternative-not-applied
   posture, section 1.2)? A build-packet product decision, not decided here.
7. Carried from M4-T013 (still open, relevant to OQ-4's Step A input): OQ-1 (exact geometric
   definition of DCM mapped width), OQ-2 (Feat_status/RoadwayType/Build_Status value domains), OQ-5
   (BYTES shapefile URL, browser-capture-only).

### 4.3 Recommended build-packet decomposition (for the later A2 build tasks to pin against)

This report recommends, but does not create or contract, the following split (consistent with the
D-046 wave-3 disjointness discipline already governing this task):

1. **B3 - DCM geometry parsing.** Extend the accepted `dcm_street_centerline_arcgis` family with a
   new sibling transport module (the `mappluto_lot_outline.py`-beside-`mappluto_geometry_arcgis.py`
   precedent) that parses, CRS-validates, and types the polyline geometry already arriving on the
   wire. Depends on: nothing new (data already flows); blocked by: nothing.
2. **B4 - buffer/intersection geometry engine.** A new production module computing the 100-ft
   EPSG:2263 buffer over `wide`-disposed DCM segments and its intersection with a
   `mappluto_geometry_arcgis` lot polygon, typed per the edge cases in Part 2.4. Depends on: B3 +
   the already-accepted MapPLUTO connector.
3. **B5 - OQ-3 G6 ruling.** A legal/architect-track item (not a coding task) resolving the
   ambiguity-class fail-closed policy. Blocks B4's "wide" disposition input at the ambiguous margin
   only (B4 can proceed today using the classifier's already-accepted conservative disposition; B5
   only changes which segments cross into `wide` at the margin).
4. **B6 - the §12-10 "wide street" text reconciliation.** A short, focused research/architect task
   resolving OQ-4-a/b/c (Part 4.2 items 2-4) BEFORE the named-street override table or the
   C5-3/C6-4/C6-6 clause are built, so B4 is not built against a text that later turns out
   incomplete or superseded.
5. **B7 - rule wiring.** Once B4 lands, wire its per-portion result into
   `r6_r7_r8_wide_street_conditional_far.rule.json` (replacing its current "a wide-street
   determination is not performed" limitation with an actual computed split), plus G6 qualified-human
   approval per the rule's own `release.qualified_human_approval: "pending"` status.

## Evidence index (all retrieved 2026-09-13 unless noted; sha256 over exact captured bytes)

- E1 - `https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-432` (direct HTTPS GET,
  182,102 bytes, sha256 `6ded75a4506a6e5ee3dbfe876a485bed6ff80a16eb51533262f4dac4878d927e`); Last
  Amended `2024-12-05T12:00:00Z` (`<time>` element).
- E2 - `https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-433` (direct HTTPS GET,
  113,717 bytes, sha256 `03ba408113c3afa959cd03066f63e44196d8c52bd32b55b99ab8511f6d161e5a`); Last
  Amended `2024-12-05T12:00:00Z`.
- E3 - `https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-731` (direct HTTPS GET,
  112,027 bytes, sha256 `402357171891ba0b288666f9e670054a5ec5a9a62e64a22a66a48d6b872f606e`); Last
  Amended `2024-12-05T12:00:00Z`.
- E4 - `https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-736` (direct HTTPS GET,
  336,287 bytes, sha256 `ddb0d5efd670ee3c02ea159bf251ec9b4837ec75a3cc4585a5386fb17390d2e1`); Last
  Amended `2024-12-05T12:00:00Z`.
- E5 - `https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-411` (direct HTTPS GET,
  116,343 bytes, sha256 `7b80969dd507945b773b4bd82cff812a725296f2da0018d166d5b109cd79c702`); Last
  Amended `2024-12-05T12:00:00Z`.
- E6 - `https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10` (direct HTTPS GET,
  1,316,667 bytes, sha256 `0c341a0b55eb7bc0bea817144c434b4d229de41c7f7ebc9c1b021e2f824dd977`); the
  single page holding every ZR defined term, including "street line" (amended 10/25/1973), "street
  wall" (12/15/1961), "base plane" (5/12/2021), "sky exposure plane or front sky exposure plane"
  (4/18/1987), "street, narrow" (12/15/1961), "street, wide" (**3/26/2026**).
- E7 - `https://zoningresolution.planning.nyc.gov/entityprint/pdf/node/18523` - attempted twice,
  **HTTP 504 Gateway Timeout both times** (recorded as a failed channel for this large page, not
  retried further).
- E8 - `https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-41` and `.../23-73` -
  `WebFetch` (chapter-head/table-of-contents reads only; used for routing and subsection
  enumeration, not for numeric verbatim claims).
- E9 - `https://epsg.io/2263` (`WebFetch`, retrieved 2026-09-13): "CRS Name: 'NAD83 / New York Long
  Island (ftUS)' ... Unit: US survey foot." Primary registry `https://epsg.org/crs_2263/NAD83-New-York-Long-Island-ftUS-.html`
  returned HTTP 403 to this fetch (recorded, not substituted silently).
- E10 (read-only repo inputs, not re-fetched by this task, cited for the connector-fit assessment):
  `services/api/app/connectors/dcm_street_centerline_arcgis.py`,
  `services/api/app/connectors/dcm_street_width_classifier.py`,
  `services/api/app/connectors/mappluto_geometry_arcgis.py`,
  `services/api/app/connectors/mappluto_lot_outline.py`,
  `services/api/tests/fixtures/dcm_street_centerline/MANIFEST.json`,
  `services/api/app/rules/rulesets/r6_r7_r8_wide_street_conditional_far.rule.json`.
- E11 (read-only pin) - `project-control/reports/M4-T013-street-width-research.md`.
