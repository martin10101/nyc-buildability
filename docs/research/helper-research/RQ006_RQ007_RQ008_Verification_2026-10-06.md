# RQ-006, RQ-007, RQ-008 - the second research helper's check at the official sources, 2026-10-06 (its notes, unchanged)

**A lead, not a source of record (D-050-R002).** After the owner's message of 2026-10-06 asked for the research assessment to be updated, a research helper (an AI agent) read six sources at their official origin: HPD's "Laying the Groundwork" section 3.1; the New York State HCR Design Guidelines (2025) section 3.4.1a and Exhibit A; the HCR 2026 Project Detail Application, Exhibit D-2; HPD's definition of a dwelling unit's area; the RentCafe (Yardi Matrix) apartment-size figures; and the definition of "floor area" in Zoning Resolution Section 12-10. No rule, number or fact may cite this file as its origin, and law text it quotes must be captured from the official source before it is used.

The owner's reviewer audited these notes twice on the same day; the corrections that followed are recorded in `docs/RESEARCH_REQUESTS.md` (RQ-006 to RQ-008). A third reading at the official pages, made after those audits, is in `RQ006_RQ007_RQ008_Official_Readings_2026-10-06.md` beside this file; where the two differ, the later reading and the research file say which statement stands.

The notes were written outside the repository (their own first paragraph says so) and are copied here unchanged below the line.

---

# Official-source verification — RQ-006 / RQ-007 / RQ-008 leads

Date of work: 2026-10-06. Researcher: official-source-researcher (verification, not new numbers).
Purpose: read five named sources + the ZR floor-area definition at their official origin and
record exactly what each says. Findings are leads for the owner's research file, not legal
conclusions. Nothing here was written inside a git repository (this file lives under
`/root/project/lanes-runtime/owner-docs/...`, which is not a git repo — confirmed with
`git rev-parse` returning "not a git repository").

Fetch notes: www.nyc.gov PDFs downloaded with a browser User-Agent via curl (HTTP 200).
hcr.ny.gov and rentcafe.com return HTTP 403 to curl at the TLS layer regardless of headers; they
were reached through the WebFetch tool (which saved the raw PDF/XLSX locally). PDFs read with
poppler `pdftotext -layout`; the HCR Project Detail Application .xlsx read by parsing the
OpenXML parts (sharedStrings + sheet18) with Python.

---

## ITEM 1 — HPD, "Laying the Groundwork" (ground-floor design guidelines), §3.1, printed p.37

- Document: **"Laying the Groundwork: Design Guidelines for Retail and Other Ground-Floor Uses in
  Mixed-Use Affordable Housing Developments."** A project of the Design Trust for Public Space in
  partnership with NYC Department of Housing Preservation and Development (HPD).
- Edition/date: **© 2015** ("© 2015 by the Design Trust for Public Space and NYC Department of
  Housing Preservation and Development"). PDF producer metadata: `DESIGN_121815.indd` (18 Dec
  2015). No numbered edition; this is the 2015 publication.
- Official URL: https://www.nyc.gov/assets/hpd/downloads/pdfs/services/laying-the-groundwork-retail-design-guidelines.pdf
  (HTTP 200, 14,873,889 bytes, 86 pp). Section 3 ELEMENTS lists "3.1 | Ceiling Height".
- Location of the three figures: **Section 3.1 "Ceiling Height", printed page 37** (PDF page 39).
  The printed folio reads "37   37   Section 3 : Interior Architecture". A caption on the facing
  page (printed p.35) also states "MINIMUM 15' FLOOR-TO-FLOOR HEIGHT AND A CLEAR SPAN OF 12'
  ABOVE THE FINISH FLOOR LEVEL".

Verbatim (printed p.37, §3.1, items .1 and .2):
> ".1 Provide a minimum of 15 feet floor-to-floor height and a minimum 14 feet, 4 inches
>  clear floor-to-underside of slab height in the retail areas."
> ".2 Maintain a clear span of 12 feet above the finish floor level (AFFL). No pipe, conduit,
>  or other utility running horizontally in the ceiling should be lower than 12 feet above
>  the retail floor slab."

Per the three sub-questions:
- (a) 15 ft: "Provide a minimum of **15 feet floor-to-floor height** … in the retail areas."
  Measures **floor-to-floor height**. Framed as a recommended **minimum** ("Provide a minimum of").
- (b) 14 ft 4 in: "a minimum **14 feet, 4 inches clear floor-to-underside of slab height** in the
  retail areas." Measures **clear height from the finished floor to the underside of the slab**
  (i.e. the structural clear height, not floor-to-floor). A recommended **minimum**. The report's
  shorthand "structural clearance" is a fair paraphrase of "clear floor-to-underside of slab".
- (c) 12 ft: "Maintain a **clear span of 12 feet above the finish floor level (AFFL)**. No pipe,
  conduit, or other utility … should be lower than 12 feet above the retail floor slab." Measures
  the **unobstructed vertical clearance** above the finished floor (nothing may hang below 12 ft).
  Phrased as a directive ("Maintain"); effectively a minimum clear zone.

Scope (who it applies to) — "How to Use the Guidelines", printed p.10:
> "Developers and design professionals working in the affordable housing industry may use this
>  publication as a tool to achieve best practices in the design of retail and other ground-floor
>  spaces in mixed-use developments. These guidelines are based on projects typical to HPD and the
>  New York City context but are relevant to other cities as well. These best practices may also be
>  useful for developers undertaking mixed-use market-rate housing."
> "The guidelines address new construction projects only…"
> "For the purpose of this publication, the term 'retail' refers to any ground-floor use that
>  generates commercial activity or fills a community need and activates the streetscape."
Community uses in scope (p.11): "Childcare/Pre-K Center, Health Facility, Cultural Space" (plus the
retail types). HPD foreword (p.6): "These guidelines will be used as a resource by our development
and technical staff, and by other city agencies, developers, and community organizations…"

Guidance vs. law: the document presents itself as **best-practice design guidelines / "a tool" /
"a resource"**, co-produced with a nonprofit (Design Trust for Public Space). It uses
recommendation language ("Provide a minimum", "should"). It notes (p.~12, Mechanical): "Systems
must be designed to current codes by registered professionals and submitted for permitting to the
appropriate agencies." **No explicit sentence stating "this is guidance and not law" was found.**
It is not styled or labelled as a code or regulation.

Different figure for community-facility ground floors? **No different figure.** In §3.1 the
15 ft / 14'-4" / 12 ft numbers are stated for "the retail areas". In the back-of-book
**Applications** matrix (printed "Applications" section, PDF page 67), the "Ceiling height: floor
to slab" column shows **14'-4" for every use**, including the three Community Use rows
(Childcare/Pre-K Center, Health Facility, Cultural Space) and the cultural sub-uses (Art Center,
Community Center, Dance Studio, Gallery, Performance Space, Religious Facility). So community
facilities are assigned the **same 14'-4" ceiling (floor-to-slab) value as retail**, with no
separate floor-to-floor figure.

VERDICT ITEM 1: **VERIFIED AS STATED.** All three figures appear in §3.1 on printed p.37 with the
exact words above. Minor wording precision to carry forward: 14'-4" is "clear floor-to-underside
of slab height" (clear/structural height), and 12 ft is a "clear span above the finish floor
level" (unobstructed clearance); 15 ft is floor-to-floor. All three are recommended minimums in a
guidance document, not legal requirements. Community-facility ground floors get the same 14'-4"
ceiling value (no distinct number).

---

## ITEM 2 — NYS HCR Design Guidelines, 2025 edition, §3.4.1a + Exhibit A: common-space calculation

- Document: **"HCR Design Guidelines 2025"**, New York State Homes and Community Renewal.
  Footer on every page: "2025 HCR Design Guidelines | www.hcr.ny.gov". 94 pp.
- Official URL: https://hcr.ny.gov/system/files/documents/2025/06/hcr-design-guidelines-2025-full-final6.pdf
  (reached via WebFetch; curl 403). Stored locally; read with pdftotext.
- Applies to (intro, "Intent and Use of the HCR Design Guidelines", p.1):
> "The HCR Design Guidelines (the Guidelines) have been developed by New York State Homes &
>  Community Renewal (the Agency), to establish standards of quality, function, efficiency and
>  durability required for projects funded by the Agency."
> "The HCR Design Guidelines do not exclude compliance with other criteria that may be required by
>  the project funding source(s) or required by applicable codes, laws or regulations."
  Table 3.4.1 distinguishes "New Construction & Adaptive Reuse", "Historic Adaptive Reuse", and
  "Substantial & Moderate Rehabs".

§3.4.1 Residential Common Space (definition of the numerator category):
> "Residential common space is defined as all common areas in the residential project funded by HCR
>  that are not within or dedicated to dwelling units (i.e., corridors, lobbies, utility rooms,
>  manager's office, laundry rooms, community rooms, shared mechanical rooms, etc.). Residential
>  common spaces shall be designed efficiently to make best use of the built area of the building."

§3.4.1a Overall Building Efficiency:
> "Residential common space must comply with the maximum percentages noted in Table 3.4.1. See
>  Section 5.1.2a and Exhibit A for guidance on residential common space area calculations."

Table 3.4.1 – Allowable Residential Common Space Percentage (maximums, printed p.41):
- New Construction & Adaptive Reuse: **25%** ; Historic Adaptive Reuse: **35%** ; Substantial &
  Moderate Rehabs: **N/A**.
- Allowable increases: "Projects located in New York City **+5%**"; "Integrated Supportive Housing
  Projects with on-site Supportive Services **up to +5%**"; "Amenity space for a fitness center,
  computer lab/co-working spaces **up to +2%**."
- Parking: naturally-ventilated garages are excluded from the common-space area; mechanically-
  ventilated garages are included.
- Waivers above the maximum require justification; HCR may require an operational guarantee.

Measurement basis — "interior gross area" (Exhibit A — Area Calculation Diagram Reference, pp.91-93):
> "Diagrams Should Convey the Following Information: • Interior gross area for each dwelling unit
>  (including any remote bulk storage, as permitted). • All residential common space. • All
>  non-residential space. • Any spaces shared by residential and non-residential programs…"
> "Calculations for interior gross area shall be per the instructions in Section 5.1 of the HCR
>  Design Guidelines."
> "The area of chases that serve directly to dwelling units shall be included in the dwelling unit
>  area. The area of chases that serve residential common spaces shall be included in residential
>  common area. The area of chases that serve non-residential spaces shall be included in the
>  non-residential area."

Where walls are counted (Exhibit A, "Measurement Details; Interior Gross Area"):
> "AT DEMISING WALL BETWEEN DWELLING UNITS; MEASURE TO CENTERLINE OF COMMON WALL"
> "BETWEEN COMMON CORRIDOR AND DWELLING UNIT; MEASURE TO CENTERLINE OF COMMON WALL"
> "AT EXTERIOR WALL OF DWELLING UNIT; MEASURE TO THE INSIDE FACE OF THE INTERIOR WALL FINISH"
> "AT EXTERIOR WALL OF RESIDENTIAL COMMON AREA AND NON-RESIDENTIAL SPACE; MEASURE TO INTERIOR WALL FINISH"
> "AT DEMISING WALL BETWEEN RESIDENTIAL COMMON AREA AND NON-RESIDENTIAL SPACE; MEASURE TO CENTERLINE OF COMMON WALL"
> "INTERIOR GROSS AREA INCLUDES ALL WALLS AND SPACES WITHIN THE EXTENTS OF THE DWELLING UNIT
>  (I.E. CABINETS, SHOWERS/TUBS CLOSETS, APPLIANCES, ETC.)"
> "WHERE PERMITTED REMOTE BULK STORAGE SPACE SHALL BE CALCULATED AS PART OF THE DWELLING UNIT AREA.
>  (ACTUAL DWELLING UNIT AREA + REMOTE BULK STORAGE AREA = TOTAL DWELLING UNIT AREA)"

The explicit fraction (numerator ÷ denominator) is **not written as a prose formula in the
guidelines**; §3.4.1a sets the maximum percentage and points to Section 5.1.2a + Exhibit A, and the
actual division is carried in the application's Area Calculation tables (see ITEM 3, which spells
it out: Residential Common Space ÷ (Residential Dwelling Unit Space + Residential Common Space), on
Total Interior Gross Area — non-residential space excluded).

VERDICT ITEM 2: **VERIFIED AS STATED** (with one clarification). It is a program-specific
calculation (HCR-funded projects), measured on an **interior-gross** basis, with the numerator =
residential common area and the denominator = dwelling-unit area + residential common area (non-
residential excluded). The clarification: the guidelines state the **maximum % (25% new
construction / 35% historic adaptive reuse, +5% NYC, +5% supportive, +2% amenity)**, the category
definitions, and the interior-gross wall rules (centerline of demising/common walls; inside face
at exterior walls); the explicit ratio itself lives in the application (Exhibit D-2), not in the
guidelines prose. HCR's interior-gross basis counts half of demising/corridor walls into each space
and includes unit-serving chases.

---

## ITEM 3 — HCR 2026 Project Detail Application, Exhibit D-2: does it match ITEM 2?

- Document: **"2026 HCR Multifamily Finance 9% Project Detail Application"** (Excel workbook).
  The download URL serves the .xlsx directly: https://hcr.ny.gov/2026-hcr-multifamily-finance-9-project-detail-application
  (reached via WebFetch; 2.2 MB .xlsx; curl 403). Linked from the 2026 Multifamily Finance 9%
  LIHTC RFP page: https://hcr.ny.gov/2026-multifamily-finance-9-lihtc-rfp
- The workbook has 48 sheets; sheet named **"Exhibit D-2"** carries the title cell
  "EXHIBIT D-2: AREA CALCULATIONS".
- Instructions cell (verbatim):
> "INSTRUCTIONS: 1. Refer to Section 5.1 and Exhibit A in the HCR Design Guidelines for detailed
>  instructions on how to complete this form. 2. Complete Tables 1-4 for each building or building
>  type… 8. The area of all parking garages will be included in the Gross Area Including Exterior
>  Walls for cost assessment purposes. All mechanically ventilated parking garages will be included
>  in the Residential Common Space area. 9. Area Calculation Diagrams that correspond with the
>  tables below must be submitted in PDF format as part of Attachment D-1, Preliminary Plans."

Fields / columns captured for every space (both Table 1 and Table 2):
- "Number of Each Space", "Interior Gross Area Each Space", "Total Interior Gross Area",
  "Gross Area Including Exterior Walls Each Space", "Total Gross Area Including Exterior Walls".
- Table 1: "Dwelling Unit Space" — rows: SRO, 0/1/2/3/4/5 Bedroom.
- Table 2: "Residential Common Space" — rows: Lobby & Vestibules; Corridors & Stairs; Laundry(ies);
  Mechanical Room(s); Office Space(s); Community Room(s); Community Kitchen; Supportive Service
  Spaces; Co-Working Space; Computer/Business Room; Fitness Room.
- Table (labelled) "Non-Residential Space".

The formula (from the workbook's live cell formulas):
- **Table 5: "Total Residential Interior Gross Area Percentages"** — column header
  **"Percent of Total Interior Residential Gross Area"**:
  - Row "Residential Dwelling Unit Space": value = Table 1 Total Interior Gross Area (`=H72`);
    percent cell `=IF(G196>0, G194/G196, "")`.
  - Row "Residential Common Space": value = Table 2 residential-common totals (`=H127+H134`);
    percent cell `=IF(G196>0, G195/G196, "")`.
  - Row "Totals": `G196 = SUM(G194:G195)` = dwelling-unit area + residential common area.
  So the Residential-Common-Space percentage = **Residential Common Space ÷ (Residential Dwelling
  Unit Space + Residential Common Space)**, both measured as **Total Interior Gross Area**.
- **Table 6: "Total Building Gross Area"** separately lists Residential Dwelling Unit Space,
  Residential Common Space, and Non-Residential Space, in BOTH "Total Interior Gross Area" and
  "Total Gross Area Including Exterior Walls" — the exterior-walls basis is used for cost assessment,
  not for the common-space percentage.

VERDICT ITEM 3: **VERIFIED AS STATED; it MATCHES ITEM 2.** Exhibit D-2 computes exactly "residential
common area ÷ (dwelling-unit area + common area)" on an interior-gross basis, with non-residential
space excluded from that percentage. It is the operational form of the max-% rule in §3.4.1a /
Table 3.4.1, and both cross-reference "Section 5.1 and Exhibit A" of the 2025 Design Guidelines.
(It additionally captures a parallel "Gross Area Including Exterior Walls" figure for cost purposes.)

---

## ITEM 4 — HPD definition of net/dwelling unit area (current new-construction design guidelines)

- Document: **"HPD DESIGN GUIDELINES for NEW CONSTRUCTION, Version 2.0"** (cover reads
  "Version 2.0" with a footnote marker). This is the current HPD new-construction design-guidelines
  document (issued by HPD Office of Development / BLDS; publicly described as v2.0, September 2023).
  69 pp. PDF created 5 Dec 2024.
- Official URL: https://www.nyc.gov/assets/hpd/downloads/pdfs/services/hpd-design-guidelines-for-new-construction.pdf
  (HTTP 200, 4,245,109 bytes).
- Location: **Section 5 "Apartment Planning"** (section begins at printed p.39), "Unit Area
  Calculation" callout, PDF page 41 (printed folio in the low 40s; the folio digit did not OCR
  cleanly — PDF page 41 confirmed to contain the text).

Verbatim definition (the "UNIT AREA CALCULATION" box):
> "Dwelling unit area calculation refers to the area within the perimeter walls, which includes all
>  area between the finished surfaces of all exterior walls and demising partitions."
> "Structural members that are integral components of exterior walls and demising partitions, as
>  well as all mechanical and plumbing chases will be excluded from area calculations for the
>  purpose of determining compliance with unit size requirements. Structural members (such as
>  freestanding columns) that are not integral components of exterior walls or demising partitions
>  will be included in the unit and room area calculations. PTACs or similar equipment protruding
>  less than 1'-0" into the space under a window will not be deducted from area calculations but
>  will be considered for maneuvering clearances."
> "Measurements are taken to the finished face of demising partitions and exterior walls."
> "Mechanical and plumbing chases are NOT included in the unit area."
> "Structural, mechanical, and plumbing elements embedded in or protruding from exterior walls or
>  demising partitions are NOT included in the unit area."
> "Freestanding structural elements are included in the unit area."

What it includes/excludes:
- Includes: all area within the unit perimeter between finished wall/partition surfaces, interior
  partitions inside the unit, closets, freestanding structural columns, PTACs protruding < 1 ft.
- Excludes: exterior-wall thickness and demising-partition thickness (measure to the unit-side
  finished face), mechanical and plumbing chases, and structural members integral to exterior/
  demising walls.
- Term used: HPD's term is "**dwelling unit area**" / "**target net area**" (per-type target
  ranges). It does **not** use the literal phrase "net unit area".
- Target net area ranges by type (Section 5): Efficiency 300–350 sf; 0-BR 350–400 sf; 1-BR
  500–550 sf; 2-BR 650–725 sf; 3-BR 850–950 sf; 4-BR 950–1075 sf. (HTF-funded projects may go up to
  the lower end of the HCR unit-area ranges.)
- Older HPD "Design Guidelines for New Construction" (Revised August 1, 2000, 6 pp,
  https://www.nyc.gov/assets/hpd/downloads/pdfs/services/new-constr-guidelines.pdf) defines only
  ROOM area, not unit area: "The room area shall be computed to the inside finished surfaces of the
  walls and partitions, and exclude columns, pipe chases, and closets." (Superseded by v2.0 for the
  net-unit-area question.)

How it differs from the HCR basis (ITEM 2):
- **Walls at demising partitions / corridors:** HPD measures to the **finished face** of the
  demising partition (wall thickness NOT counted into the unit). HCR measures to the **centerline**
  of the demising/corridor wall (half the wall counted into the unit). → HCR unit area is larger.
- **Chases:** HPD **excludes** mechanical/plumbing chases from unit area. HCR **includes** chases
  that serve the dwelling unit in the dwelling-unit area. → HCR unit area is larger.
- **Exterior walls:** both measure to the interior finished face (exterior-wall thickness excluded)
  — this part agrees.
- Net effect: HPD "dwelling unit area / target net area" is a **tighter, finished-face-to-finished-
  face net** figure; HCR "interior gross area" for a dwelling unit is **systematically larger**
  because it adds half of demising/corridor walls and unit-serving chases.

VERDICT ITEM 4: **VERIFIED AS STATED** (with term note). HPD's current (v2.0) definition is the
"dwelling unit area / target net area": area within the unit perimeter measured to the finished
face of exterior walls and demising partitions; interior partitions, closets, and freestanding
columns included; exterior/demising wall thickness, integral structural members, and mechanical/
plumbing chases excluded. HPD does not use the literal term "net unit area" (it uses "dwelling unit
area" / "target net area"). It differs from HCR by measuring to the finished face (vs HCR's
centerline) at demising/corridor walls and by excluding unit-serving chases (which HCR includes).

---

## ITEM 5 — RentCafe (Yardi Matrix) average new-apartment size: 737 Manhattan / 712 Brooklyn / 692 Queens

- Original publication: RentCafe blog, **"Apartment Size in New York City: Manhattan Rentals Are
  Getting Roomier"** (byline Alexandra Both), **published June 10, 2024**.
  URLs (same article, two paths): https://www.rentcafe.com/blog/apartment-search-2/apartment-size-new-york-city-2024/
  and https://www.rentcafe.com/blog/local-resources/apartment-size-new-york-city-2024/
- Figures (verbatim from the article, via WebFetch):
> Manhattan: "the average size of new apartments (built between 2014 and 2023) here is 737 square feet"
> Brooklyn: "the average apartment size in Brooklyn is 712 square feet for new units"
> Queens: "the average size of a new apartment is 692 square feet"
> Citywide: "the typical rental here offers around 700 square feet."
  Construction language: the article uses "**built** between 2014 and 2023" → these are
  newly-BUILT apartments (not newly leased). Comparison figures the article gives for pre-2014
  stock: Manhattan ~721 (so +16 sf), Brooklyn ~733 (−21 sf), Queens 724 (−32 sf). These are also
  built-stock figures.

What the ARTICLE itself states about source, population, and measurement (checked twice via
WebFetch against the full text + any footnote):
- Data source "Yardi Matrix" / "Yardi": **NOT PRESENT in the article.**
- Building population / unit-count threshold (e.g. 50+ units): **NOT PRESENT in the article.**
- How apartment size is measured (inside the apartment / rentable / net): **NOT PRESENT in the
  article** (not stated).

RentCafe's general methodology (from RentCafe's own methodology/national pages — context, because
this NYC article does not restate it):
- Yardi Matrix is described by RentCafe as "a RentCafe sister company … providing up-to-date
  information on **large-scale multi-family properties of 50 units or more** in over 130 U.S.
  markets." Rankings are "based on … multi-family buildings of **50 units or more**", excluding
  cities with < 500 units completed in a year, and the data "focuses exclusively on large-scale,
  **market-rate** multifamily properties." Source pages:
  https://www.rentcafe.com/blog/rental-market/us-average-apartment-size-trends-downward/ and
  https://www.rentcafe.com/blog/rental-market/market-snapshots/decade-housing-trends-methodology/
- The methodology categorizes units by bedroom count but does **not explicitly state** whether the
  square footage is interior/net or rentable area → measurement basis remains unstated.

Other articles that repeat the SAME RentCafe June-2024 study (REPEATS, not independent sources):
- Fox5NY — "This NYC borough ranks third for smallest average apartment size: study"
  https://www.fox5ny.com/news/nyc-borough-ranks-third-smallest-average-apartment-size-study
- NBC New York — "This borough has the smallest average apartment sizes for all of NYC" (Queens)
  https://www.nbcnewyork.com/news/queens-smallest-apartments-nyc/5508153/
- QNS.com — "Queens apartments have the smallest average size among all boroughs, third-smallest in
  country: report" https://qns.com/2024/06/queens-apartments-smallest-average-size-boroughs-third-smallest-country-report/
- BrickUnderground — "At new developments in Queens and Brooklyn, the average one-bedroom rental is
  getting smaller" https://www.brickunderground.com/rent/rentcafe-report-average-apartment-size-new-development-rentals-nyc
- 6sqft — "Manhattan apartments are bigger now than a decade ago"
  https://www.6sqft.com/manhattan-apartments-are-bigger-now-than-a-decade-ago/
- unitedstatesrealestateinvestor.com — "New York Apartments Grow Larger in One Borough"
All of the above attribute the numbers to the RentCafe/Yardi report → treat as repeats of one
study, not as corroborating independent datasets.

Leasing vs built: no leasing figure was used here; the 737/712/692 are for apartments "built
2014–2023." (If any downstream source substitutes a "newly leased" average, it must be relabelled.)

VERDICT ITEM 5: **VERIFIED WITH A DIFFERENCE.** The three numbers (737 / 712 / 692) and the "built
2014–2023" framing are confirmed in the original RentCafe article (June 10, 2024). The DIFFERENCE:
the article itself does NOT name Yardi Matrix, does NOT state the building population (no "50-unit"
threshold), and does NOT state how size is measured. Those details come only from RentCafe's
general methodology pages (Yardi Matrix sister data, 50+-unit market-rate buildings; measurement
basis still not explicitly defined). The figures rest on this single study; the other outlets are
repeats of it.

---

## ITEM 6 — NYC Zoning Resolution §12-10 "floor area" definition

- Official site: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10 (HTTP 200,
  1,312,389 bytes). The "floor area" definition is at anchor `id="term-floor area"` (distinct from
  "affordable floor area" and "floor area ratio"). The whole §12-10 definitions page loaded; this
  entry was read in full.
- **Last Amended: 12/5/2024** (the page shows "General Definition — Last Amended 12/5/2024" within
  the floor-area entry; `<time datetime="2024-12-05T12:00:00Z">`). This 12/5/2024 amendment is the
  "City of Yes for Housing Opportunity" change.
- The definition is rendered as bulleted items (not visibly lettered (a)/(b) in the HTML; the
  official print/PDF uses lettered paragraphs).

Opening sentence (verbatim):
> "'Floor area' is the sum of the gross areas of the several floors of a building or buildings,
>  measured from the exterior faces of exterior walls or from the center lines of walls separating
>  two buildings."

INCLUDES (verbatim items; relevant to a residential building):
> "basement space, except as specifically excluded in this definition;"
> "elevator shafts or stairwells at each floor, except as specifically excluded in this definition;"
> "floor space in penthouses;"
> "attic space … providing structural headroom of eight feet or more;"
> "floor space in gallerias, interior balconies, mezzanines or bridges;"
> "floor space in open or roofed bridges, breeze ways or porches, if more than 50 percent of the
>  perimeter … is enclosed …;"
> "any other floor space used for dwelling purposes, no matter where located within a building,
>  when not specifically excluded;"
> "floor space in accessory buildings, except for floor space used for accessory mechanical equipment;"
> "floor space used for accessory off-street loading berths in excess of 200 percent of the amount
>  required …;"
> "floor space that is not otherwise exempt pursuant to this Section and is, or is made,
>  inaccessible within a building;"
> "floor space in exterior balconies or in open or roofed terraces if more than 67 percent of the
>  perimeter … is enclosed …;"
> "any other floor space not specifically excluded."

EXCLUDES ("the floor area of a building shall not include", verbatim items):
> "cellar space, except where such space is used for dwelling purposes. Cellar space used for
>  retailing shall be included for the purpose of calculating requirements for accessory off-street
>  parking spaces, accessory bicycle parking spaces and accessory off-street loading berths;"
> "elevator or stair bulkheads, accessory water tanks, or cooling towers, except … in R2A Districts;"
> "uncovered steps;"
> "attic space … providing structural headroom of less than eight feet;"
> "floor space in open or roofed bridges, breeze ways or porches, provided that not more than 50
>  percent of the perimeter … is enclosed …;"
> "floor space used for accessory off-street parking spaces provided in any story: up to 300 square
>  feet per single- or two-family residence …; within group parking facilities located not more than
>  23 feet above curb level …; or within automated parking facilities located not more than 40 feet
>  above curb level …;"
> "floor space used for accessory off-street loading berths, up to 200 percent of the amount
>  required …;"
> "floor space used for accessory mechanical equipment. Such exclusion shall also include the
>  minimum necessary floor space to provide for necessary maintenance and access to such equipment …;"
> "floor space in exterior balconies or in open or roofed terraces provided that not more than 67
>  percent of the perimeter … is enclosed …;"
> "floor space within stairwells: at each floor of buildings containing residences developed or
>  enlarged after April 16, 2008, that are greater than 125 feet in height, provided that [44-inch
>  min width; capped at 8 inches of stair+landing width per floor; etc.]; at each floor of buildings
>  developed or enlarged after April 28, 2015, that are 420 feet or greater in height …;"
> "floor space used for the storage of equipment by the Fire Department … in buildings that are 420
>  feet or greater in height;"
> "qualifying exterior wall thickness;"
> "floor space in a qualifying rooftop greenhouse;"
> "floor space on a sun control device, where such space is inaccessible other than for maintenance;"
> "floor space within a fully electrified building or an ultra low energy building, of an amount
>  equivalent to five percent of the floor area located within such building …;"
> "floor space in buildings containing multiple dwelling residences allocated to building amenities,
>  corridors, refuse storage or disposal, or access to elevated ground floor dwelling units that is
>  provided in accordance with the provisions of Section 23-23, inclusive;"
> "floor space in Quality Housing buildings that was exempted pursuant the Quality Housing Program,
>  as such program existed prior to December 5, 2024."

Per the named spaces in the question (for a residential / multiple-dwelling building):
- **Corridors:** generally included as part of "the gross areas of the several floors"; the
  12/5/2024 amendment then EXCLUDES "floor space … allocated to building amenities, **corridors**,
  refuse storage or disposal … in accordance with … Section 23-23." (A capped, §23-23-governed
  exclusion — not a blanket one.)
- **Stairs / stairwells:** INCLUDED — "elevator shafts or **stairwells** at each floor" — except
  the specific tall-building stairwell exclusions (> 125 ft and ≥ 420 ft, with width caps).
- **Elevator shafts:** INCLUDED — "**elevator shafts** … at each floor" — except elevator/stair
  bulkheads (excluded).
- **Cellar space:** EXCLUDED, "except where such space is used for dwelling purposes."
- **Mechanical space:** EXCLUDED — "floor space used for accessory mechanical equipment" (+ minimum
  maintenance/access space).
- **Parking:** EXCLUDED — accessory off-street parking per the stated height/area conditions.
- **Balconies:** interior balconies INCLUDED; exterior balconies/terraces EXCLUDED if ≤ 67 percent
  of the perimeter is enclosed, INCLUDED if > 67 percent enclosed.
- **Refuse rooms:** EXCLUDED for multiple-dwelling residences via the §23-23 allowance ("refuse
  storage or disposal") added 12/5/2024.
- **Laundry rooms:** **NOT named** in the §12-10 floor-area definition; therefore not specifically
  excluded (counted as ordinary floor area). (Laundry rooms ARE named in the HCR definition in
  ITEM 2, but not in the ZR.)

VERDICT ITEM 6: **VERIFIED AS STATED.** The full "floor area" definition was read from the official
ZR site, opening sentence and all included/excluded items captured verbatim above; Last Amended
12/5/2024. Note that corridors and refuse storage are now excludable for multiple-dwelling
buildings only under the §23-23 allowance (not unconditionally), stairwells/elevator shafts are
included except the tall-building stairwell carve-outs, and laundry rooms are not named in the ZR
definition.

---

## Files captured locally (scratchpad; not in any repo)
- hpd_laying_groundwork.pdf (HPD "Laying the Groundwork", 2015, 86 pp)
- hcr_design_2025.pdf (HCR Design Guidelines 2025, 94 pp)
- hcr_pda_2026.xlsx (2026 HCR Multifamily Finance 9% Project Detail Application; sheet "Exhibit D-2")
- hpd_dg_nc_2023.pdf (HPD Design Guidelines for New Construction v2.0, 69 pp)
- hpd_newconstr.pdf (HPD Design Guidelines for New Construction, Rev. Aug 1 2000, 6 pp — superseded)
- zr1210.html / zr_floorarea.txt (ZR §12-10, floor-area entry)
