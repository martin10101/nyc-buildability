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

## RQ-006 — A starting floor-to-floor height for the floor estimate (R6B first) — ANSWERED IN PART 2026-10-06 (research helper); residual OPEN, FOR THE OWNER'S OTHER AGENT

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
- **Research helper, 2026-10-06 (a lead only; full return in `docs/research/helper-research/RQ006_RQ007_RQ008_Starting_Values_2026-10-06.md`):**
  - It found no law that fixes a floor-to-floor height. The Zoning Resolution limits building
    height and floor area; the Building Code sets a minimum ceiling height for habitable rooms
    (it quotes section 1208.2: 8 feet). Both are leads to be captured from the official text
    before use.
  - Practice sources it found put a typical residential floor at 9 to 10 ft floor-to-floor and
    a ground floor with shops or a community facility at 14 to 16 ft. These are professional
    conventions, not City figures.
  - Its confidence: PARTLY SUPPORTED.
- **Proposed starting values (design assumptions; the owner approves; not adopted):** 10 ft for a
  residential floor (the value the program already holds); 14 ft for a ground floor with shops
  or a community facility, kept as a separate editable value.
- **Still open, FOR THE OWNER'S OTHER AGENT:** (1) the ground-floor height that HPD's "Laying the
  Groundwork" design guideline states (the helper could not read that file); (2) a second,
  independent source for the usual floor-to-floor height of new low-rise apartment buildings in
  New York City, ideally an architect's typical section for an R6B building.
- **Status:** ANSWERED IN PART 2026-10-06. Not a blocker: results that use the value are shown as
  conditional on the value on screen.

## RQ-007 — A starting average apartment size for the realistic apartment-count estimate — ANSWERED IN PART 2026-10-06 (research helper); residual OPEN, FOR THE OWNER'S OTHER AGENT

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
- **Research helper, 2026-10-06 (a lead only; full return in `docs/research/helper-research/RQ006_RQ007_RQ008_Starting_Values_2026-10-06.md`):**
  - The legal limit: it quotes the Zoning Resolution's dwelling-unit factor (section 23-52, as
    amended 2024-12-05) as 680 for multiple dwellings. That is the LEGAL cap on the number of
    apartments and is kept apart from the realistic figure.
  - The realistic figure: one market dataset (RentCafe on Yardi data, 2024) gives the average
    size of apartments built 2014 to 2023 as 737 sq ft in Manhattan, 712 in Brooklyn and 692 in
    Queens, measured as the inside area of the apartment. It found no second dataset.
  - City guidance it read (HPD design guidelines, 2000 revision) sets minimum ROOM sizes, not
    whole-apartment sizes.
  - Its confidence: WELL SUPPORTED for the legal factor; PARTLY SUPPORTED for the realistic
    figure (one source).
- **Proposed starting value (a design assumption; the owner approves; not adopted):** 700 sq ft
  of apartment area per apartment, measured inside the apartment, editable.
- **Still open, FOR THE OWNER'S OTHER AGENT:** a second source for the average size of newly
  built apartments in New York City by borough (for example the City's housing database or
  building filings), and HPD's current target apartment sizes by type.
- **Status:** ANSWERED IN PART 2026-10-06. Not a blocker.

## RQ-008 — A starting shared-space allowance (the part of a residential building that is not inside apartments) — OPEN: the helper's answer leaves it less clear; FOR THE OWNER'S OTHER AGENT

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
- **Research helper, 2026-10-06 (a lead only; full return in `docs/research/helper-research/RQ006_RQ007_RQ008_Starting_Values_2026-10-06.md`):**
  - It found no official figure. Practice sources give apartment buildings as 70 to 85 percent
    efficient, none of them specific to New York City, and they do not agree on what is being
    divided by what.
  - It reports that the Zoning Resolution's "floor area" counts halls, stairs, lift shafts and
    lobbies and leaves out cellar space and most mechanical space, so the percentage depends on
    whether it is applied to gross floor area or to zoning floor area. It could not read the
    full definition (section 12-10) in one piece. A lead to be captured from the official text.
  - **Why it is less clear:** "loss factor" in leasing sources (rentable against usable area)
    is not the architect's ratio of apartment area to building area. A figure taken from a
    leasing source would mislead.
  - Its confidence: PARTLY SUPPORTED, and it flags the answer as confusing.
- **Proposed starting value (a design assumption; weakly supported; the owner approves; not
  adopted):** 15 percent of the residential zoning floor area taken as shared space, so 85
  percent inside apartments, editable, with the denominator printed beside it.
- **Still open, FOR THE OWNER'S OTHER AGENT:** a New York City source (an architect's
  gross-to-net study for a low-rise apartment building, or a City or developer template) that
  gives the share of floor area inside apartments and names its denominator.
- **Status:** OPEN 2026-10-06 (helper run; no well-supported answer). Not a blocker.

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
