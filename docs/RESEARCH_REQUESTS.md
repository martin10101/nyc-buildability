# Research requests — owner-assisted deep-research channel (D-050)

**What this is.** A running queue of research-shaped questions the build loop wants answered.
The owner runs them through external deep-research tooling (Astra) and brings back results —
making the campaign faster. Started 2026-09-13 (owner directive D-050).

**Read this from your phone (always current):**
https://github.com/martin10101/nyc-buildability/blob/candidate/D-024-mrl-option-b/docs/RESEARCH_REQUESTS.md
Every change to this file is committed AND pushed in the same step (D-050-R006), so that link
is never stale. From the phone you can also just ask the companion session to read out what's
open, or dictate results into the chat — it does the file work.

**The rules (D-050):**
- Results are **discovery aids, never sources of record.** Every load-bearing claim gets verified
  against the official text through the normal capture discipline (print/PDF-class completeness
  where applicable) before anything is encoded. Rule provenance always cites the captured official
  text — the research is credited only as a discovery note.
- **Non-blocking:** the loop never waits on this queue. An unanswered request just means the
  loop's own researcher does the work; an answered one saves that time.
- Questions about what a law **means** (interpretation) don't belong here — they go to
  `docs/ARCHITECT_REVIEW_QUESTIONS.md` (D-048) and come back as owner decisions or qualified
  rulings.
- Ask for **citations, section numbers, and exact quotes with URLs** in every answer — a claim
  without a pinpoint citation costs verification time instead of saving it.

**How a request is worked now (owner, 2026-10-06; D-090 R285 to R288).** Deep questions, such as a
starting floor height, are written here. For each one the orchestrator first runs its own research
helper, which searches widely online and reports an answer with its sources; the answer is written
into the entry. If the helper finds no well-supported answer, or its answer leaves the question less
clear, the entry stays OPEN and is marked **FOR THE OWNER'S OTHER AGENT**, and the owner is reminded
to hand it on. A request is never a blocker. Everything above still holds: an answer is a lead to be
checked, never a source of record.

**Entry format:** question · why it matters · what it unlocks · status (OPEN / ANSWERED
<date> / ROUTED-to-architect-doc).

**Lifecycle (D-050-R006):** results returned by the owner are stamped ANSWERED immediately
(date + named verification target) and pushed in the same step. Once a request is SATISFIED —
answer verified/consumed, everything checks out — its full entry is DELETED from the active
queue and collapsed to one line in the Closed register at the bottom (full text stays in git
history). The active queue never carries figured-out material.

---

## RQ-003 — The §12-10 "qualifying residential site" definition, verbatim — ANSWERED 2026-09-13

- **Question:** Quote the complete ZR §12-10 definition of "qualifying residential site"
  (City of Yes), enumerating every qualification route (transit proximity, community-facility
  floor space as of 2024-12-05, any others), each route's district inclusions/exclusions, and
  any cross-referenced sections. Full text, not a summary.
- **Why:** D-049-R004 encoded §23-424's 35/35 alternative as a fail-closed condition precisely
  because this definition wasn't captured; the FAR table also jumps R2/R2A to 1.00 on qualifying
  sites, so the definition moves floor-area numbers too.
- **Unlocks:** turning several "professional review required" flags into computed conditions.
- **Added 2026-09-13 (wave-3 finding):** while in §12-10, ALSO quote the current "street, wide"
  definition verbatim — the live text was AMENDED 3/26/2026 and is materially fuller than our
  accepted snapshot (an alternate-width clause + two named-street designations). The A2 build
  now requires a fresh §12-10 capture + architect ruling before the wide-street rules build.
- **ANSWERED 2026-09-13** (owner deep research, D-050;
  `docs/research/owner-research/NYC_Buildability_Research_2026-09-13.md` §RQ-003): complete
  route index (a)(1)–(c) + final affordability paragraph located, original §12-10 HTML in the
  owner's evidence archive; cross-refs §23-21 / §23-424 (35/35, 35/45, 45/55) / §27-111 /
  §66-11; **plus an express counterexample: §114-02 excludes certain >5-acre Special Bay Ridge
  lots from the definition** — a §12-10-only eligibility function is wrong. The research itself
  states print/PDF-class capture of the definition was NOT completed. Street-wide extension:
  amendment date 3/26/2026 corroborated (our own M4-T016 capture is already byte-verified).
  **Verification target:** the D-049-R004 conversion task must make its own recorded-official
  capture of §12-10 (qualifying residential site + street, wide) with print/PDF-class
  completeness, plus §23-21/§23-424/§27-111/§66-11 and the §114-02 exclusion; discovery aid is
  never cited as provenance.

## RQ-004 — Special-district priority inventory (A4 planning input) — ANSWERED 2026-09-13

- **Question:** List NYC's special purpose districts (Article/chapter numbers + names), and for
  each: the boroughs/neighborhoods covered and whether it modifies residential height/setback or
  FAR. Flag the ~10 with the largest residential development activity (e.g. Special Hillsides
  Preservation, Special Ocean Parkway, Special Midtown, Hudson Yards…).
- **Why:** A4 is sequenced last and is the elastic part of the timeline; a priority order over
  the special districts lets the owner pick the waves that matter for real deals instead of
  encoding alphabetically.
- **Unlocks:** an informed owner triage for the final campaign waves.
- **ANSWERED 2026-09-13** (owner deep research, D-050;
  `docs/research/owner-research/NYC_Buildability_Research_2026-09-13.md` §RQ-004): 59 current
  chapter families inventoried (Articles VIII–XIV) with geography + H/F effect flags + section
  targets; measured activity ranking (DCP Housing Database 25Q4 × NYSP boundaries — Gowanus /
  MX / Lower Manhattan / LIC / Downtown Brooklyn top five) with its limitations stated;
  suggested implementation order incl. a separate small-house track (South Richmond, Ocean
  Parkway, Hillsides, Natural Area). **Two index inconsistencies flagged:** §11-122 still lists
  Garment Center at Art. XII Ch. 1 (now Midtown South Mixed Use) and omits Ch. 145
  (Eastchester–East Tremont). **Verification target:** A4 contracting verifies the inventory
  against official chapter text (never the DCP guide's numbers — e.g. §92-23 says 215 ft, not
  the guide's 210), resolves both index inconsistencies from the official text, and treats the
  activity ranking as a planning aid only.

## RQ-005 — DCM Street Center Line: official width-definition + bulk-product facts (B2 hardening) — ANSWERED IN PART 2026-09-13; residual (1) OPEN

- **Question:** (1) Find the official DCP/City Map documentation that defines exactly WHAT the
  DCM Street Center Line `Streetwidth` value records geometrically (mapped right-of-way /
  property-line-to-property-line vs roadbed) — the dataset metadata has NO field-level
  definition; cite the document, section, exact quote, URL. (2) The exact download URL + file
  name of the DCM street-centerline BYTES shapefile (nyc.gov returns 403 to non-browser
  clients; needs a browser). (3) The verbatim LION data-dictionary text defining `StreetWidth`
  ("narrowest width of the paved area…" is search-derived, not yet byte-read — it lives deep in
  lion_metadata.pdf). Exact quotes + URLs for all three.
- **Why:** these are the accepted M4-T013/M4-T015 open questions OQ-1, OQ-5, and E2/OQ-7 — the
  three pure fact-finding gaps left in the street-width connector's provenance. (OQ-3, the
  ambiguity-class policy, is interpretation and stays with the architect doc / G6.)
- **Unlocks:** closes the connector's remaining research caveats before the A2 wave consumes it;
  the width-definition citation also strengthens the wide-street rule's G6 package.
- **ANSWERED IN PART 2026-09-13** (owner deep research, D-050;
  `docs/research/owner-research/NYC_Buildability_Research_2026-09-13.md` §RQ-005):
  **(2) CLOSED** — exact bulk product byte-verified: `dcm_20251031shp.zip` (October 2025
  release; internal `DCM_StreetCenterLine.shp/.dbf/.shp.xml`; 19,554,628 bytes; ZIP sha256
  `ad21afd2c7c6…`; download URL in the archived report). **(3) CLOSED** — LION 26C metadata
  PDF page 24 byte-read: `StreetWidth_Min` (alias `StreetWidth`), Double, verbatim "Formerly
  known as StreetWidth, this represents the narrowest width, in feet, of the paved area of the
  street." (PDF sha256 `b98255a2…`) — confirms M4-T013's paved-vs-mapped finding; Geoclient
  width stays KILLED for legal use. **(1) REMAINS OPEN — refined 2026-09-13 by the owner's
  independent-confirmation pass**
  (`docs/research/owner-research/RQ005_Independent_Confirmation_2026-09-13.md`, D-051-R004):
  what IS now supported by official evidence — DCM records **mapped** street widths ("Mapped
  street widths (usually includes sidewalks)" per DCP's own application text), intended display
  units are **feet**, and the field-definition absence is thorough (no `attrdef` in the PDF or
  embedded XML, and the width entry in DCP's metadata-authoring file is name+type only across
  14 historical versions). Observed data profile: 54,051 records, 6,908 (12.8%) non-plain-
  numeric (`n/a` 2,954; `Unknown` 1,401; `>80` 368; `>75` 364; `60-75`, `~75`,
  `Width Irregular`, `Unknown but >75` …), some on records marked Mapped_St/City_St. What
  remains open — stated precisely: measurement boundaries (which mapped lines), variable-width
  representation (min/max/nominal/where-measured), and the authoritative interpretation of the
  nonnumeric encodings. **This is "no field-level definition located in the examined official
  sources" — NOT "never documented anywhere" (D-051-R001).** **Closure evidence:** a written
  DCP specification — dataset contact `DCPOpendata@planning.nyc.gov`, inquiry text drafted in
  the archived report (owner-side outreach) — and/or, per specific frontage, the effective
  adopted Section/Alteration Map (Borough President topographical bureau per current City Map
  guidance). **Handling until closed (D-051-R002/R003):** unknown/ambiguous width keeps
  factual status UNKNOWN with its class + review flag; conservative fallbacks are validated
  PER CONSUMING RULE (narrow is validated-safe for the accepted wide-street FAR rule, but NOT
  universally — §23-431 street-wall placement is the counterexample). The researcher's
  proposed DRAFT classification table is routed as INPUT to the OQ-3 interpretation process
  (D-051-R005), never adopted in-task. The B2-hardening/G6-package task still makes its own
  recorded captures of the DCM metadata PDF + LION 26C PDF (shas above make that cheap).
- **THIRD PASS 2026-09-14** (owner deep research;
  `docs/research/owner-research/RQ005_Deep_Research_2026-09-14.md`): materially strengthens
  the record without closing (1). NEW: (a) **qualified labels are publisher-INTENTIONAL** —
  DCP's own 2018-04-18 Street Map PR handles `Unknown but <71.2 ft` deliberately (not a parser
  artifact); (b) **variable width is represented by centerline SEGMENTATION** — E 96 St
  Brooklyn runs `60` → `60-75` → `75-90` → `90` across four adjoining features with ranges on
  ~27-ft transition segments, so a named street never gets ONE width and frontage work must
  collect every touching feature; (c) **Admin Code §25-101** makes the duly-adopted City Map
  conclusive on street location/width/grades — the controlling legal record above any dataset
  field; (d) a worked map-reading example verifies "width between mapped street boundaries"
  (BSA 4-07-A Tiemann Ave 60 ft property-line-to-property-line + 1956 Bronx Plan 11474 + DCM
  `60` agreeing); (e) the 2026 **Allen Street mall demapping** (C 250306 MMM / N 250307 ZRM)
  is live proof that legal wide-street classification and measured width are SEPARATE facts —
  the §12-10 named-street exception (amended 3/26/2026) preserves wide treatment while the
  mapped configuration changes; (f) a demonstrated per-frontage resolution route: the Final
  Section Map index (in DCP's public app config) links retrievable Section/Alteration Map PDFs
  — sheets for all three sampled ambiguous records were actually retrieved. **Report's own
  conclusion, adopted here: RQ-005(1) cannot close as a universal automated interpretation on
  this evidence; the two honest closure forms are (i) documented publisher semantics (DCP) or
  (ii) an owner-approved DRAFT product policy for stated inference conditions (the OQ-3
  decision, which now has rich input). Per-frontage map evidence can close individual sites
  meanwhile.** Build-packet carries: frontage-level multi-feature collection; segmentation
  awareness; §25-101 as legal anchor; the Section-Map retrieval route as a candidate connector;
  representation per D-051-R002 (raw text + recognized form + qualifiers + version + geometry +
  coverage reason, legal classification recorded separately). No conflict with accepted work.
- **OQ-3 DECIDED 2026-09-14 (D-052):** the owner approved the DRAFT classification policy
  (75-ft threshold, one-sided-bound rule, UNKNOWN-to-map-resolution, full provenance, per-rule
  fallback justification, DRAFT until G6) — see
  `project-control/directives/D-052-street-width-draft-classification/` and the architect doc
  section D. **The RQ-005(1) publisher-convention residual above remains OPEN unchanged** —
  the decision is an owner-approved product policy, not an official DCM interpretation.

---

*Loop: append new requests below with the same format. Owner: paste results to the companion
session or the build session; the receiving session marks the entry ANSWERED and names the
verification target.*

## RQ-006 — A starting floor-to-floor height for the floor estimate (R6B first) — ANSWERED IN PART 2026-10-06; ground-floor candidate revised to 15 ft and put to the owner 2026-10-06, not yet answered; residual OPEN, FOR THE OWNER'S OTHER AGENT

- **Question:** What floor-to-floor height should a feasibility estimate start from for a new
  residential building of the size R6B allows in New York City, and for its ground floor? Wanted:
  (a) what the Zoning Resolution itself says that bears on it (any rule that ties the number of
  storeys to height, or a ground-floor height, with section numbers and exact quotes); (b) the
  minimum ceiling heights in the NYC Building Code and Housing Maintenance Code (section numbers,
  quotes); (c) what City design guidance says (for example HPD design guidelines, DCP's zoning
  handbook); (d) what architects and feasibility studies commonly assume, with the reasoning
  (structure depth, services, finished ceiling); (e) whether the common value differs for a
  ground floor with shops or a community facility.
- **Why it matters:** the estimated number of floors is the height limit divided by the
  floor-to-floor height. The program holds 10 ft as a stated, editable starting value
  (`services/api/app/scenario/three_answers/inputs.py`). The owner's rule is that a design choice
  may have a visible, editable starting value and no hidden default (D-090-R256), and the owner
  approves the starting values (section map, choice 4).
- **What it unlocks:** a proposed starting value with its basis for the owner's approval; the
  "estimated floors" part of the report. Until then the result is shown as conditional on the
  value on screen.
- **Not asked here:** what any law means for a particular lot.
- **First research helper, 2026-10-06 (a lead only; full return in `docs/research/helper-research/RQ006_RQ007_RQ008_Starting_Values_2026-10-06.md`):**
  - It found no law that fixes a floor-to-floor height. The Zoning Resolution limits building
    height and floor area; the Building Code sets a minimum ceiling height for habitable rooms
    (it quotes section 1208.2: 8 feet). Both are leads to be captured from the official text
    before use.
  - Practice sources it found put a typical residential floor at 9 to 10 ft floor-to-floor and
    a ground floor with shops or a community facility at 14 to 16 ft. These are professional
    conventions, not City figures.
  - Its confidence: PARTLY SUPPORTED.
- **Checked at the official source, 2026-10-06 (owner messages 93 and 94; a second helper run and
  a reading of the document; a lead only; notes in
  `docs/research/helper-research/RQ006_RQ007_RQ008_Verification_2026-10-06.md` and
  `docs/research/helper-research/RQ006_RQ007_RQ008_Official_Readings_2026-10-06.md`):**
  - The document is HPD with the Design Trust for Public Space, "Laying the Groundwork: Design
    Guidelines for Retail and Other Ground-Floor Uses in Mixed-Use Affordable Housing
    Developments," copyright 2015 (PDF December 2015; commonly cited as January 2016). Section
    3.1 "Ceiling Height", printed page 37, gives three figures and keeps them apart: ".1 Provide
    a minimum of 15 feet floor-to-floor height and a minimum 14 feet, 4 inches clear
    floor-to-underside of slab height in the retail areas." ".2 Maintain a clear span of 12 feet
    above the finish floor level (AFFL)." So 15 ft is floor-to-floor; 14 ft 4 in is the clear
    height from the finished floor to the underside of the slab; 12 ft is the clear height kept
    free of pipes and ducts. They measure different things, and choosing 15 ft floor-to-floor
    does not by itself show the 14 ft 4 in and 12 ft clearances are met.
  - How the document says it is used (quoted): developers and designers "may use this publication
    as a tool to achieve best practices"; HPD's foreword says the guidelines "will be used as a
    resource by our development and technical staff, and by other city agencies, developers, and
    community organizations"; and they inform "criteria for requests for proposals (RFPs), the
    evaluation of development proposals, and the review of architectural plans." Each figure is a
    recommended minimum. It is not a universal legal requirement for any building.
  - The owner's reviewer states: "HPD identifies critical success factors as requirements for
    mixed-use proposals on HPD-owned property disposed through its RFP process." Reading this
    document in full on 2026-10-06 did not find that sentence or its substance in it: the
    document calls the nine factors guidance and a "resource," and the words "requirement,"
    "HPD-owned" and "disposition" were not found in that sense (the only "disposal" is of trash).
    The requirement the reviewer describes may rest on another HPD source (an RFP term sheet or
    disposition rules) not read here. This is a bounded negative about this one document, not a
    statement that HPD never requires the factors.
  - Its definition of "retail": "the term 'retail' refers to any ground-floor use that generates
    commercial activity or fills a community need and activates the streetscape." It lists
    ground-floor childcare (Childcare/Pre-K Center), health (Health Facility) and cultural
    (Cultural Space) uses among the community uses it covers, which supports applying its general
    guidance, including these heights, to those uses. Its back-of-book table gives community uses
    the same 14 ft 4 in clear height as retail and no separate floor-to-floor figure, so it does
    not set one height for every community facility as zoning defines that term.
- **Candidates (design assumptions; the owner approves; none adopted; the program and its
  starting values are unchanged):** 10 ft for a residential floor (the value the program already
  holds; a design assumption — the actual number of floors also depends on setbacks, elevations,
  structure and roof treatment); 15 ft floor-to-floor for a ground floor with shops, revised from
  14 ft on the basis above and put to the owner for approval on 2026-10-06, not yet answered; the
  same 15 ft offered for a community-facility ground floor on the support above. All stay editable
  preliminary assumptions; this research approves none.
- **Still open, FOR THE OWNER'S OTHER AGENT:** (1) a second, independent source for the usual
  floor-to-floor height of new low-rise apartment buildings in New York City, ideally an
  architect's typical section for an R6B building; (2) a source that states a floor-to-floor
  height for a community-facility ground floor.
- **Status:** ANSWERED IN PART 2026-10-06; the revised 15 ft ground-floor candidate awaits the
  owner's approval. Research is never a blocker: results that use the value are shown as
  conditional on the value on screen.
- **Corrected 2026-10-06 after the owner's review (messages 93, 94 and 95):** first written as a
  14 ft ground-floor candidate with the guideline's figures not yet read; now 15 ft floor-to-floor
  put to the owner, kept apart from the document's 14 ft 4 in clear and 12 ft clear figures, with
  the document's standing and its "retail" definition recorded and the reviewer's "requirements
  ... RFP process" sentence marked as not found in this document.

## RQ-007 — A starting average apartment size for the realistic apartment-count estimate — ANSWERED IN PART 2026-10-06; figures corrected to historical benchmarks from one dataset with an unverified measurement basis, legal cap kept separate; residual OPEN, FOR THE OWNER'S OTHER AGENT

- **Question:** What average apartment size should a realistic apartment-count estimate start
  from for new multifamily housing in New York City (low-rise and mid-rise, outer boroughs)?
  Wanted: (a) what the Zoning Resolution says about the number of dwelling units allowed per
  floor area (the dwelling-unit factor: section number, current value, exact quote), kept apart
  because that is the LEGAL limit, not the realistic count; (b) minimum apartment or room sizes
  in City codes and HPD design guidelines by apartment type; (c) published figures for the
  average size of newly built apartments in New York City or Queens, with source and year;
  (d) how feasibility studies usually pick the figure, and whether they state net or gross area.
- **Why it matters:** the realistic count is the floor area available for apartments divided by
  an average apartment size. The owner wants legal maximums kept apart from practical estimates
  and every estimate to state its assumptions (D-090 source-035).
- **What it unlocks:** a proposed starting value with its basis for the owner's approval (section
  map, choices 3 and 4); the "realistic apartment-count estimates" part of the report.
- **First research helper, 2026-10-06 (a lead only; full return in `docs/research/helper-research/RQ006_RQ007_RQ008_Starting_Values_2026-10-06.md`):**
  - The legal limit: it quotes the Zoning Resolution's dwelling-unit factor (section 23-52, as
    amended 2024-12-05) as 680 for multiple dwellings. That is the LEGAL cap on the number of
    apartments and is kept apart from the realistic figure.
  - The realistic figure: one market dataset (RentCafe on Yardi data, 2024) gives the average
    size of apartments built 2014 to 2023 as 737 sq ft in Manhattan, 712 in Brooklyn and 692 in
    Queens, measured as the inside area of the apartment. **[Corrected 2026-10-06: the article
    does not say how an apartment's size is measured; "the inside area of the apartment" is
    unverified — see the check below.]** It found no second dataset.
  - City guidance it read (HPD design guidelines, 2000 revision) sets minimum ROOM sizes, not
    whole-apartment sizes.
  - Its confidence: WELL SUPPORTED for the legal factor; PARTLY SUPPORTED for the realistic
    figure (one source).
- **The legal cap, kept separate (Zoning Resolution 23-52, captured in the repository at
  `docs/research/zr-snapshots/v1/zr-23-52.snapshot.json`, last amended 2024-12-05):** the
  dwelling-unit factor is 680 for other multiple dwellings; it is a ceiling on the number of
  apartments (maximum residential floor area divided by 680, a fraction of 0.75 or more rounding
  up), not proof that that many apartments physically fit. Who is exempt, quoted: "(a) For the
  following types of multiple dwelling residences, there shall be no applicable dwelling unit
  factor: (1) developments or enlargements of residences in special density areas; (2) qualifying
  senior housing; or (3) conversions ..." — affordable housing alone is not on that list and does
  not by itself remove the factor. The two R6B scenarios do not share one floor area and one
  ceiling: a standard-residence case and a qualifying-affordable case have different residential
  floor areas (for example 2.00 vs 2.40 FAR) and so different caps, and the affordable case does
  not inherit the standard case's floor area or unit count. For a mixed-use proposal the estimate
  uses the residential floor area actually allocated to it; a shop floor is not simply added to an
  already-used residential allowance without checking the combined FAR and shared-space rules. The
  lot area in any worked example is unverified and the numbers establish no whole-site or remaining
  development capacity. The estimate of what fits stays separate from this legal cap and its
  rounding.
- **Checked at the original publication and the official guideline, 2026-10-06 (owner messages 93
  and 94; a lead only; notes in the two helper files named above):**
  - The 692, 712 and 737 sq ft figures are historical benchmarks from ONE RentCafe/Yardi dataset
    (one 2024 article), not independently confirmed borough averages. Their measuring method is
    not stated in the article, so the net-interior basis first recorded is unverified.
  - The article's linked national study states its coverage (multifamily properties of 50 or more
    units); only the shorter New York article omits it. "Market-rate only" is not established for
    the size figures (RentCafe applies that only to its rent data, not to the size study). The
    50-unit coverage makes the sample a poor match for a 29-unit R6B example; it does not mean
    R6B prohibits 50-unit buildings.
  - Articles that repeat the same study are not independent sources; the list of such articles
    (Fox5NY, NBC New York, QNS, BrickUnderground, 6sqft and one investor site) is the second
    helper's finding, not the owner's reviewer's count — the reviewer did not independently
    establish a six-article count. An average for newly leased apartments is never used in place
    of one for newly built apartments; these figures are for apartments built 2014 to 2023.
  - HPD's target net areas by apartment type (a target on a stated basis, not an average of what
    is built) come from HPD's Design Guidelines for New Construction; the edition read for this
    assessment is the 2026 edition (item 5 of the official readings). In the document's own words
    it applies to design-consultation submissions received on or after October 1, 2026, and
    "Projects participating in Housing incentive programs (either MIH or UAP) that are not
    subsidized through any HPD Loan Programs shall not be subject to the Guidelines." (The owner's
    reviewer summarised this as such projects being "not automatically subject"; the document's
    own words are the stronger "shall not be subject to the Guidelines" — both are recorded.) The
    target net areas by type are studio/0BR 350–400 sq ft; 1BR 500–550; 2BR 650–725; 3BR 850–950.
    A midpoint mix of these comes to about 575 sq ft, which is an illustrative mix, not HPD's
    prescribed or observed average.
- **Candidate (a design assumption; the owner approves; not adopted; the program and its starting
  values are unchanged):** 700 sq ft per apartment for standard residences, as a rounded,
  explicitly chosen historical reference from the one dataset above — not a validated average for
  R6B and not shown to be measured the way HPD measures (if used in the program it would be stated
  as an adopted assumption on HPD's basis, not as a verified research result). It stays an editable
  preliminary assumption, put to the owner on 2026-10-06 with its evidence, its uncertainty, HPD's
  target areas as a second anchor, and a table of how the estimated count moves; this research
  approves no default.
- **Still open, FOR THE OWNER'S OTHER AGENT:** a second, independent dataset for the size of newly
  built apartments in New York City by borough that states how size is measured (for example the
  City's housing database or building filings).
- **Status:** ANSWERED IN PART 2026-10-06; the candidate awaits the owner's answer. Research is
  never a blocker.
- **Corrected 2026-10-06 after the owner's review (messages 93, 94 and 95):** first written as
  737/712/692 sq ft "measured as the inside area of the apartment" and a 700 sq ft value "measured
  inside the apartment"; the measurement basis is now recorded as unverified, the figures as
  historical benchmarks from one dataset, and the dwelling-unit factor as a legal ceiling kept
  separate from the realistic estimate.

## RQ-008 — A starting shared-space allowance (the part of a residential building that is not inside apartments) — OPEN; corrected 2026-10-06 (no percentage is established; the measurement basis is set out and must be resolved before any estimator); FOR THE OWNER'S OTHER AGENT

- **Question:** What share of a new New York City apartment building's floor area is commonly
  taken by halls, stairs, lifts, lobby, refuse and service rooms, so that a feasibility estimate
  can turn floor area into apartment area? Wanted: (a) published efficiency or loss-factor figures
  for low-rise and mid-rise multifamily buildings, with source, year, and whether the base is
  gross floor area or zoning floor area; (b) which spaces the Zoning Resolution leaves out of
  "floor area" for a residential building (section numbers and exact quotes), because that changes
  the base the percentage applies to; (c) how the figure changes with building size and with the
  number of stairs and lifts the Building Code requires.
- **Why it matters:** the owner's accuracy rules require gross, net and zoning floor area to stay
  distinct and every efficiency percentage to state its denominator (D-090 source-030, item 4).
- **What it unlocks:** a proposed starting value with its basis for the owner's approval (section
  map, choices 3 and 4); the realistic apartment-count estimate.
- **First research helper, 2026-10-06 (a lead only; full return in `docs/research/helper-research/RQ006_RQ007_RQ008_Starting_Values_2026-10-06.md`):** it found no official figure; practice sources
  give apartment buildings 70 to 85 percent efficient, none specific to New York City and with no
  agreed denominator. It noted ZR "floor area" counts halls, stairs, shafts and lobbies but leaves
  out cellar and most mechanical space (so a percentage depends on gross vs zoning floor area), and
  warns a leasing "loss factor" is not the architect's apartment-to-building ratio. PARTLY SUPPORTED.
- **What each area includes and excludes, with its source and status (checked 2026-10-06; owner
  messages 93, 94 and 95; a lead only; notes in the two helper files named in RQ-006 and RQ-007):**
  - **(a) Zoning floor area — ZR 12-10 "floor area" and the Section 23-23 allowances (read at the
    official page 2026-10-06; NOT captured — the repository's 12-10 capture holds only the
    street-width definitions, row DB-156 — to be captured before any rule or result relies on
    them).** Floor area is "the sum of the gross areas of the several floors ... measured from the
    exterior faces of exterior walls or from the center lines of walls separating two buildings";
    it already counts stairwells and elevator shafts and already leaves out cellar space (unless
    used for dwelling), accessory mechanical-equipment space and accessory parking within limits.
    Section 23-23 then lets a multiple dwelling leave out, each on conditions and none
    automatically: residential amenities up to 5 percent of residential floor area, accessible to
    the residents (the text lists "laundry facilities" as one example amenity inside that 5 percent
    allowance, so "laundry rooms count" holds only with that qualification — the reviewer wrote
    "qualifying laundry facilities," the Section 23-231 text says "laundry facilities"; both are
    recorded); corridors 50 percent under the termination/daylighting/outdoor-access provisions and
    another 50 percent where the corridor is no more than 100 linear feet, combinable; refuse
    storage or disposal up to 3 sq ft per dwelling unit; access to elevated ground-floor apartments
    up to 100 sq ft per foot of elevation difference, capped at 500 sq ft per building. Section
    12-10 also carries qualifying exterior-wall-thickness and energy exclusions; these and the
    parking, balcony and mechanical-space conditions are checked where they bear on a result, not
    treated as a complete short list.
  - **(b) HPD dwelling-unit area — HPD Design Guidelines for New Construction, 2026 edition (item 5
    of the official readings; applicability recorded in RQ-007).** In its own words: "measured
    within the perimeter walls, from the finished face of all exterior walls and demising
    partitions"; "Structural members that are integral components of exterior walls or demising
    partitions, as well as all mechanical and plumbing chases, are excluded ... All other structural
    members — including freestanding columns and columns attached to interior partitions — are
    included." So the apartment's own partitions and free-standing structure are included and the
    model must not subtract all apartment walls; the excluded shafts are the "mechanical and
    plumbing chases" precisely, not every kind of shaft. (The reviewer summarised the exclusion as
    "exterior/demising-wall thickness and mechanical/plumbing chases"; the document excludes the
    structural members integral to those walls and the chases and measures from the finished face;
    both are recorded.)
  - **(c) HCR common space — NYS HCR Design Guidelines 2025, section 3.4.1a and Exhibit A, and the
    2026 Project Detail Application, Exhibit D-2 (a program-specific calculation for HCR-funded
    projects).** The second helper read the application workbook and found Exhibit D-2 computes
    residential common space divided by (dwelling-unit area plus residential common space) on an
    interior-gross basis, non-residential space left out; the owner's reviewer could not open the
    spreadsheet and so could not certify the exact Exhibit D-2 cells or that the division appears
    only there. HCR measures to the centre line of demising and corridor walls and includes the
    apartment's own chases, so the same apartment measures larger on HCR's basis than on HPD's. The
    two bases differ, are never mixed, and nothing is subtracted twice. HCR's maximum is 25 percent
    for new construction plus 5 percent for New York City — a program ceiling, not an average — and
    HCR's percentage stays out of this estimate's formula.
- **The rule for the estimate (owed before any estimator is built; the estimator is not built until
  this basis is resolved):** its ratio means total HPD-measured dwelling-unit area divided by
  residential zoning floor area and nothing else. No general gross-to-net percentage is applied to
  zoning floor area and no allowance is taken for space zoning already leaves out (that would deduct
  the same space twice; a subtract-walls-and-shafts conversion is not universally valid). Zoning
  floor area and HPD dwelling-unit area are each worked out separately from ONE schedule of measured
  areas taken from a proposed building layout — the maximum floor area a lot allows does not
  establish that physical space — with every component (apartments, corridors, walls, chases,
  mechanical rooms) shown with its treatment under both systems, then reconciled. Two or three
  worked examples can check the calculations reconcile with nothing deducted twice and show that no
  single percentage is general; their ratios stay specific to those examples. For a mixed-use
  building the input is the residential portion's zoning floor area, including any residential
  circulation and support space counted as floor area, not "the area given to apartments." Correct
  arithmetic in a sensitivity table is not support for an assumption.
- **Candidate (a design judgment; the owner approves; not adopted; the program and its starting
  values are unchanged):** no percentage is offered as established. 15 percent is withdrawn as a
  description of anything established — it is not a New York City average. 25 percent shared (a 75
  percent ratio of apartment area to residential zoning floor area) is a design judgment that
  neither HPD's material nor HCR's ceiling supports; it stays an editable, explicitly unvalidated
  preliminary assumption. Neither "25 percent is appropriate" nor "15 percent is too low" is
  established by the research; both are design judgments.
- **Still open, FOR THE OWNER'S OTHER AGENT:** a New York City source (an architect's gross-to-net
  study for a low-rise apartment building, or a City or developer template) that gives the share of
  floor area inside apartments and names what it is a share of; and how much floor space Section
  23-23 lets a multiple dwelling leave out, once 12-10 and 23-23 are captured.
- **Status:** OPEN 2026-10-06 (two helper runs; no well-supported New York figure; the measurement
  basis set out above must be resolved before any apartment estimator). Research is never a blocker.
- **Corrected 2026-10-06 after the owner's review (messages 93, 94 and 95):** first written as a 15
  percent shared-space allowance (85 percent inside apartments) offered as a proposed value; now no
  percentage is offered as established, the three measurement bases are set out, and the estimate's
  rule (HPD dwelling-unit area divided by residential zoning floor area, both from one measured
  schedule) replaces the earlier subtract-walls-and-shafts outline.

---

## Closed register (one line per satisfied request; full text in git history)

- **RQ-001** — satisfied by the loop's own accepted research (M4-T016, A2 geometry-mechanics
  section map, 201st accepted) — closed 2026-09-13 — answer lives in the M4-T016 report.
  Owner research (same day) additionally returned a broader discovery map (23-431/434/435/436,
  23-44x, 23-732–739, 35-81, waterfront/flood/transit/split-lot dispatch boundary) — see
  `docs/research/owner-research/NYC_Buildability_Research_2026-09-13.md` §RQ-001 (aid only).
- **RQ-002** — satisfied by the loop's own accepted research (M4-T017, C-district survey,
  202nd accepted; corrected the C4-6 example: residential equivalent is R10, not R7) — closed
  2026-09-13 — answer lives in the M4-T017 report. Owner research (same day) corroborated
  C4-6→R10 and additionally returned the §33-122 standalone values our report deferred
  (C4-6=3.4, C4-7=10.0, C6-11=12.0, C6-12=15.0 — non-monotonic!), §35-31/35-32 mixed-building
  caps, and §32-121/122 C7/C8/C3A use gates — see the same archived report §RQ-002 (aid only;
  family-2 build still captures its own values).
