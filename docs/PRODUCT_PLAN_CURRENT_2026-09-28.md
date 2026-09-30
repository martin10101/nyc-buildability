# NYC Buildability — Current Product Plan (consolidated 2026-09-28)

| | |
|---|---|
| **Status** | Planning only. This document authorizes no code change, deployment, settings change, merge or deletion. The orchestrator records it and authorizes work. |
| **Governs** | This is the single current plan. It consolidates, and for working purposes replaces, these documents, which are kept only as history:<br>• `WHOLE_PROGRAM_INTEGRATION_AUDIT_2026-09-27.md` (original audit)<br>• `WHOLE_PROGRAM_INTEGRATION_BRIEF_2026-09-27.md` (corrected brief)<br>• Amendments 1–4 to the brief<br>Where anything differs, this document wins. |
| **Basis** | The owner's product direction (2026-09-27/28) and the source-level findings of the audits. |
| **Suggested path** | `docs/PRODUCT_PLAN_CURRENT_2026-09-28.md` |

**Working rules for all derived work.**
- Follow `CLAUDE.md`, `AGENTS.md` (on the working branch) and path-scoped `.claude/rules/`, including owner holds such as `.claude/rules/expansion-agent-dispatch-hold.md`.
- Never run `npm`, `npx` or `node` locally; validate through remote CI.
- Producers do not read or write `project-control/`.
- The producer of a change never verifies it.
- UI work gets a human walkthrough.
- No rule is labeled reviewed or published without qualified-reviewer approval.
- **Set aside, never delete**, unless the owner explicitly approves a deletion.

---

## 1. What the product is

1. **One question.** The app answers one question for an architect: *how much can be built on this property, and what is the largest building the zoning rules allow, using every add-on that benefits the builder?* That means floor area, height, width and depth under the **New York City Zoning Resolution**, for **every residential (R) district in the city**, plus residential buildings in commercial zones: overlays and commercial districts that allow housing (§12a).
2. **Measurements come from the app.** The architect usually does not have them, and should not have to find or type them.
3. **Not an information-gathering tool.** Ownership, deeds and which lots are in play come from the client.
4. **Not a design tool.** The architect designs in AutoCAD or Revit. The app hands him numbers, diagrams and a DXF envelope.

## 2. Phases

| Phase | Scope |
|---|---|
| **Phase 1 (now)** | Zoning only, with every add-on. **No building-code deductions:** no percentage lost to stairs, elevators or walls. |
| **Phase 2 (later)** | Building-code feasibility: usable area after stairs, elevators and walls; high-rise flags above 75 ft; apartment light-and-air warnings. |

---

## 3. The architect's flow

**Layout (owner requirement).** Everything happens on the existing single-page dashboard. Search and key facts stay together on the page, and detailed tools (lot choice, add-ons, diagrams, report) open over it as floating tools. The flow below fits into that layout; it does not replace it.

1. **Find the property.** Search an address or BBL and confirm the property.
2. **Choose the lots.** "This property has N lots: use all (default), or pick." Each lot is listed with its approximate size.
   - Lots are tax lots, not condo apartments. For 298 Wallabout they are lots 32 and 33.
   - Lots can be combined only if they are on one block and touching. Otherwise the combination is not offered, and the reason is shown.
   - The choice is the architect's statement of the site. Results carry the label "Based on the lots you selected — the app does not verify the zoning lot".
3. **Site facts, pre-filled (§4).** Lot area, frontage on each street, depth, lot type (corner, interior, through), zoning district(s) and street widths. Each shows its source and can be edited.
4. **Existing building.** Keep or remove. If it is kept, the app needs its existing *zoning* floor area, from one of two sources:
   - a Buildings Department filing or certificate of occupancy;
   - a value the architect enters as a stated assumption.

   City-recorded building area may be shown for reference, but it is never subtracted, because it does not follow the zoning definition of floor area. Without a zoning value, remaining capacity shows "Not available — needs existing zoning floor area"; the full-site allowance still shows.
5. **Results (§5).** Three separate answers (floor-area allowance, permitted envelope, building option), optional add-ons, "Best combination" with a stated goal, and plan and section diagrams.
6. **Tweaks, numbers only.** Floor-to-floor heights, and program (market-rate, affordable, community facility) through the add-on switches.
7. **Export.** Three files.
   - **PDF report:**
     - a cover sheet (address, zone, lots, floor-area allowance, maximum height);
     - a dimensioned site plan with yards and street widths;
     - a section and a 3D view of the envelope;
     - the calculation table with Zoning Resolution sections;
     - the floor-by-floor area table (gross area, deductions, zoning floor area per floor);
     - the add-on comparison;
     - one assumptions page.
     
     It may also include a sheet styled like the Buildings Department zoning diagram, marked "Preliminary — not for filing".
   - **Excel file:** the calculation table, with values, units, sources and rule sections.
   - **DXF:** the lot outline and permitted envelope, in feet at 1:1, with the lot and envelope on separate layers. When measurements are not from a survey, the DXF carries a note on the drawing, for example "Approximate — city tax map, not a survey".

## 4. Measurements

**Source order** (highest available wins):

| Rank | Source | Label shown |
|---|---|---|
| 1 | Survey numbers the architect enters | Survey (entered) |
| 2 | City-recorded dimensions and area (PLUTO, DOF) | City records |
| 3 | Computed from the city tax-map outline | Approximate — tax map |
| — | No data | Unknown — enter |

- **Multi-lot sites.**
  - The combined outline is built from the selected lots' outlines, with the lines between them removed.
  - Frontage is measured only along streets on the outside of that combined outline.
  - Lot type (corner, through, interior) is decided from the combined outline.
  - Combined area is the sum of the lot areas, checked against the combined outline.
  - All of it is labeled approximate unless it comes from a survey.
- **Condo base lots.** PLUTO has no separate records for them, so they use rank 3 unless DOF dimensions are found.
- **Street widths.** Pre-filled from city street data where available; the rule-coverage matrix (M1-03) confirms which source gives the mapped width that zoning uses. If a width is unknown, the app shows both the wide-street and narrow-street results side by side, marked "Needs street width".
- **How labels carry through.** Each result carries the label of its weakest input. Entering survey numbers updates every dependent result.
- **Coordinates.** They are never shown to or edited by the architect. Internally, geometry is kept in feet for diagrams and the DXF.

## 5. Results and add-ons

**Three separate answers.** These are different limits, and one building may not reach all three at once.
1. **Floor-area allowance.** The most zoning floor area the rules allow on the site (FAR × lot area, with any applicable add-ons), minus the existing zoning floor area if a building stays.
2. **Permitted envelope.** The three-dimensional limits: base and maximum heights, setbacks, yards and lot coverage.
3. **Building option.** A generated building that fits inside the envelope and within the allowance, showing its achieved floor area, floors, height and footprint. If the envelope cannot hold the full allowance, the option shows how much it reaches and why.

**Calculation behavior.** Each answer is shown only when all three of these hold:
- its applicable rules are implemented and reviewed;
- eligibility is resolved;
- the site geometry is supported.

Otherwise that answer shows "Not available" with the reason, for example "Envelope not available — height rules for this district are not built yet". Every supported answer still shows. A caution label never turns an unsupported number into a result.

**Add-ons.**
- **Automatic add-ons** that follow from the site, such as a wide-street portion or corner-lot coverage, are always included.
- **Optional add-ons** are switches that start **off**.
  - Each shows what it would add to the current selection (square feet, height, floors) and what it requires.
  - Turning one on recalculates everything together, because gains can overlap, conflict or change the building's use. Gains are never simply added up.
- **Best combination** has a stated goal: by default *most residential floor area*, or another goal the architect picks, such as most total floor area.
  - It uses only supported, quantified as-of-right and certification add-ons (§6, Groups A and B).
  - It shows why anything was left out.
  - The goal, program and assumptions are saved with the option.
- **Agreement or approval add-ons** (§6, Groups C and D1) can be switched on to explore. They are never part of Best combination. While any is on, the result is labeled "With approvals — not guaranteed".
- **Variances and rezonings** (§6, Group D2) never produce a number. They appear as an opportunity note in details: eligibility, relevant nearby precedents, and what relief could be sought.

**Also shown.**
- **Completeness line.** For example "Add-ons checked for this district: all 12", or "Not yet covered: X, Y".
- **Labels.** These follow §5a: one short strip at the top, with details on tap.
- **The building.** Floors, height, footprint width × depth, a plan, and a section where height rules exist.
- **Floor-by-floor area table.** Gross area, deductions and zoning floor area per floor, computed from the same data as the building. No apartment layouts in Phase 1: layouts are the architect's design work.
- **Floor stack.** How many floors fit under the height limits.
  - Floor-to-floor heights are editable, with stated defaults.
  - The allowable area of each floor, including where setbacks shrink upper floors.
  - The setback lines, yards and coverage for each level, in plan, section and DXF.

  This is the legal box the architect designs inside, in CAD.

## 5b. Existing buildings: keep, partly rebuild, or rebuild (owner decision)

When a building exists, the app compares three paths side by side, each with its floor area, height and the rule behind it.

| Path | Rule | What the app shows |
|---|---|---|
| **1. Keep and renovate** | A building larger than today's rules may stay. Changes must not make it more non-complying (Article V). | Existing zoning floor area kept; what can still be added, if anything |
| **2. Partial rebuild** | If less than 75% of the floor area is demolished, that part may be rebuilt without increasing the non-compliance (ZR 54-41). | The "rebuild budget": floor area and outer-wall length that may be removed, and what the result can be |
| **3. Full rebuild** | If 75% or more is demolished, the new building follows today's rules (ZR 54-41). | The three answers (§5) under today's rules |

**Traps the app flags on path 2:**
- **Walls:** removing more than 75% of the floor area *and* more than 25% of the perimeter walls, then replacing them, counts as a new development.
- **Unsafe conditions:** if partial demolition creates an unsafe condition and the Buildings Department orders more removal, the protection is lost once the total reaches 75%.

**Exceptions shown only when they apply:**
- one- and two-family houses;
- severe-disaster recovery rules.

**Inputs:**
- Existing zoning floor area, per floor where possible (§3, step 4; M2-07).
- Perimeter wall length, from filings or entered by the architect.
- Which floors or portions are kept.

Where an input is missing, path 2 shows "Not available — needs existing floor-by-floor areas".

**Flags:** rent-regulated apartments (demolition needs state approval and tenant relocation); recorded zoning-lot documents; a large gap between recorded building area and zoning floor area (cellars and exempt space).

**Headline:** when path 1 or 2 keeps more floor area than path 3, the app says so plainly: "Keeping the building preserves N sq ft that a new building could not have."

---

## 5c. Professional drawings and report (how they are produced)

**Goal.** Report and drawings at least as polished as the leading competitor's, but always matching the numbers.

**How the competitor does it (from its sample PDF's file data).**
- Pages are composed in code with a Python PDF library (ReportLab), with three open-source fonts: Inter, Instrument Serif and IBM Plex Mono.
- Floor plans are drawn as vector lines.
- Sections and 3D massing are pasted in as JPEG pictures.
- The drawings come from templates, which is why they contradict the numbers.

**Our approach: one geometry, one drawing kit, three outputs.**
1. **One geometry source.** Lane A's results include the geometry: lot outline, yards, setback lines per level, the envelope, and the building option's floor plates per level.
2. **Drawing kit.** The server draws everything as **vector SVG** from that geometry. SVG stays sharp at any zoom and prints cleanly, unlike the competitor's JPEGs.
   - **Site plan:** lot lines, dimensions, street names and widths, yards (hatched), coverage, north arrow, scale bar.
   - **Section:** ground line, floor lines with heights, base height, setback, maximum height, labeled limits.
   - **3D axonometric massing:** floor plates stacked into volumes by floor height, colored by use (the same colors everywhere), with height labels.
   - **Location and zoning maps:** built from city open data (lot outlines, zoning districts, building footprints). Aerial or street imagery only from sources whose license allows use in reports.
3. **Three outputs, one source.** These can never disagree.
   - **Screen:** shows the same server-made SVGs.
   - **PDF:** embeds them.
   - **DXF:** is written from the same geometry.
4. **PDF composition.** HTML templates with print styling (page headers, footers, page numbers, a cover sheet, a table style) are converted to PDF on the server. Lane E picks the converter after a one-day trial on the benchmark lots, for example WeasyPrint, or headless Chromium, which the repo already uses for tests.
5. **Design system.** One set of fonts (open-source), colors per use, line weights, dimension style and page templates. A one-time review of the templates by a graphic designer or the architect is recommended.
   - **Drawing style table.** One table maps each kind of shape to its look:
     - kinds of shape: residential, commercial, community facility, cellar, bulkhead or mechanical, yard, court, setback zone;
     - its look: fill color, outline, line weight, hatch pattern, and CAD layer name.

     Screen, PDF and DXF all read this same table, so the legend is identical everywhere and is generated from what is actually drawn.
   - **Readable in any print.** The palette is colorblind-safe, and hatch patterns (for example diagonal lines for yards) keep drawings readable in black-and-white print.
   - **3D massing.** Each floor is drawn as a box made from its real footprint and floor height, shown at an angle. The faces facing the viewer are drawn last, and each face is shaded by its direction (top lightest, sides darker) to give depth. The output is vector, not a picture.
   - **Labels.** Every label (widths, depths, heights, yards, floor names and areas) is read from the results, never typed text. Labels are placed so they do not overlap.
6. **Quality checks.**
   - Every figure printed on a drawing (dimensions, heights, areas) is read from the same results the tables use (checks C-4 and C-5).
   - The benchmark lots' PDFs are compared page by page against approved snapshots on every change, so a layout break is caught automatically.

**Later (Phase 2).** An interactive 3D view in the app (subject to the Q8 hold), and test-fit floor layouts generated from the same geometry.

---

## 5a. "Label on the box" — no clutter (owner requirement)

The earlier program showed too much, too small and too often. Every screen and report follows these rules:

1. **One status strip.** A single line at the top of the results shows at most three short items, for example "Zoning maximum · approximate measurements · lots you selected". Tapping it opens the details.
2. **Standing notices live behind the strip.** These include:
   - not a Buildings Department approval;
   - the floor-area reminder, worded exactly: *"Make sure this floor area is available for use. Confirm with the owner or developer that none of it was sold or merged with another lot."* No records lookup is made;
   - the zoning lot is not verified;
   - the district is incomplete.
   They appear there and on one page of the report, never repeated beside numbers.
3. **Beside a number, only an exception that changes how to read it.** Examples: "Needs street width", "With approvals", "Out of date". At most one per row. An answer that cannot be calculated reliably shows "Not available" and the reason in place of the number, never a number with a caution label.
4. **Everything else goes in details.** Rule sections, sources, dataset versions and IDs go in details and the report appendix.
5. **Readable by default.** Comfortable text size; no small grey print. Headline numbers are large. Plain English, with no internal codes.
6. **At most three notices on screen at once.** Any more are grouped under one "Notes (N)" item.
7. **Acceptance test.** In the mockup review and the architect session, the architect:
   - finds the maximum within a few seconds;
   - can say what the strip means;
   - never sees more than three notices at once.

---

## 6. Add-on catalog

**How the catalog is built.**
- AI reads the full Zoning Resolution and drafts a list of every provision that can increase floor area, height, coverage or the usable envelope. That includes bonuses, exceptions, exclusions, permitted obstructions, special-district rules, transfers, certifications, authorizations and special permits.
- The qualified reviewer confirms each provision before it is implemented and tested.
- Interpretations the Buildings Department may reject are marked "Aggressive — confirm with examiner". They stay off by default and never enter "Best combination".
- When the Zoning Resolution changes, the same process updates the catalog.

**Starting catalog.** Examples only; the full list comes from the review above.

| Group | Add-on | Type |
|---|---|---|
| **A. As-of-right** | Wide-street portion | Automatic |
| A | Corner-lot coverage | Automatic |
| A | Split-district averaging | Automatic where the rule applies |
| A | Zoning floor-area exclusions and permitted obstructions | Automatic where the rule applies |
| A | Qualifying affordable or senior housing (City of Yes) | Optional |
| A | Community facility floor area | Optional |
| A | Choice of bulk rules (for example Quality Housing versus height factor) | Optional |
| A | Ground-floor commercial space (where a commercial overlay or commercial district allows it): shows the trade-off against residential floor area | Optional |
| **B. Certification** | Transfers the rules allow by certification (for example from a nearby landmark) | Optional |
| **C. Neighbor** | A neighbor's unused floor area (estimate; depends on an agreement) | Optional; never in Best combination |
| **D1. Approval with a text maximum** | City Planning special permits and authorizations whose text sets a maximum, shown as "up to X with approval" | Optional; never in Best combination |
| **D2. Variances and rezonings** | Board of Standards and Appeals variances and rezonings: eligibility, nearby precedents and possible relief, with no number. A variance depends on case-specific findings and the minimum relief necessary. | Opportunity note only |

**Build order.** Group A comes first and completes the core answer. Groups B, C and D follow. Best combination uses Groups A and B only.

## 7. What the app does not do

- Check deeds, ownership, mortgages, or sold or merged development rights. The floor-area reminder in §5a covers this instead.
- Draw or edit buildings with coordinates or vertices.
- Import AutoCAD files. A survey-outline import for irregular lots is a possible later feature.
- Apply building-code rules. That is Phase 2.

## 8. Checks and warnings

Warnings follow §5a. Separately, the §5 calculation behavior applies. An answer that cannot be calculated reliably shows "Not available" with the reason, whatever caused it: a missing number, a missing rule, unresolved eligibility, or unsupported geometry. Supported answers still show.

- Lots not on one block, or not touching: the combination is not offered, with the reason.
- Condo property: one line saying that combining or selling rights needs the condo board and others.
- Existing building kept: its existing zoning floor area is subtracted when it is established or entered as a stated assumption (§3, step 4). Recorded building area is never used.
- Existing building larger than today's allowance: one flag, "The existing building is larger than today's zoning allows; demolition would reduce floor area." This was missed by a competitor on its own sample lot (see competitor review).
- Split district, missing street width, or unpermitted work on record: a short flag beside the affected results.

---

## 8a. Hidden issues and opportunities (checked on every property)

Things that change what can be built but are easy to miss. Each is shown as a flag, an opportunity, or "Check needed" when the data is not available. Checks are added lane by lane (Lane B data, Lane A rules).

| Group | Items | Typical source | Phase |
|---|---|---|---|
| **Existing building** | • Larger than today's rules (§5b).<br>• Non-conforming use (loses its protection after major damage).<br>• Legal use and occupancy on the certificate of occupancy.<br>• Rent-regulated apartments.<br>• Harassment-certification requirements where they apply. | DOB filings/CO, DHCR and HPD data | 1 |
| **Zoning-lot history** | • Recorded zoning-lot descriptions or mergers.<br>• Floor area already transferred.<br>• (D) and other restrictive declarations.<br>• E-designations (environmental testing). | ACRIS (flag only, per P-2), ZR Appendices C and D | 1 |
| **Map-based rules** | • Special districts and overlays.<br>• Inclusionary-housing areas.<br>• Lots split by a district line.<br>• Lots within about 20 ft of a district line (the city's zoning map is not lot-precise).<br>• Flood zones and flood-resilience height rules.<br>• Waterfront and coastal-zone rules.<br>• Transit easements near stations.<br>• Airport height limits.<br>• Landmarks and historic districts. | DCP and LPC data, FEMA maps | 1 |
| **Site shape and street** | • Mapped-but-unbuilt streets or widening lines crossing the lot.<br>• Shallow or irregular lots (yard relief).<br>• Through lots.<br>• Line-up rules with neighboring street walls (R6B, R7B, R8B).<br>• Sloping sites.<br>• Neighbors' lot-line windows. | City Map, tax map, survey | 1 (flags) / 2 |
| **Opportunities** | • Floor-area exemptions: corridors, amenities, refuse rooms.<br>• Affordable and senior housing bonuses.<br>• Height increases for eligible sites.<br>• Underbuilt neighbors (air rights to buy) and assemblage.<br>• Lot splits evaluated correctly.<br>• Conversion rules for older non-residential buildings.<br>• FRESH and similar programs where mapped. | Rule catalog (§6) plus PLUTO for neighbors | 1 |
| **Approvals and process** | • Special permits and variances (opportunity notes only).<br>• Environmental review for discretionary actions.<br>• Demolition prerequisites. | Catalog Group D | 2 |

Each item follows §5a: one line in the status strip or details, never a wall of warnings.

---

## 9. Foundations that stay

- **No example data in real work.** Real-property workflows never show or use example values; the example site lives only in an explicit Example project.
- **Unknowns stay unknown.** Unknown inputs show "Unknown" and name what they block. Pre-filled city values are *sourced*, not guesses.
- **Explicit assumptions.** Any assumption is shown as an assumption.
- **One shared study per property.**
  - The **site** is shared by all options: facts and site inputs such as street widths and measurements.
  - Each **option** (an add-on selection, plus option inputs such as program and floor heights) is independent.
  - The selected option drives the report.
- **Dependency-based invalidation.**
  - Changing a site input marks dependent results in every option as out of date.
  - Changing an option affects only that option.
  - A new rule version marks every result that uses it.
  - Late responses never overwrite newer ones.
- **Historical exports.**
  - An export records its inputs, sources, rule versions and results.
  - Reopening an export shows it read-only, as history.
  - "Start a new study from this" copies inputs only; facts are re-fetched and results recalculated, with the differences listed.
  - Nothing imported becomes a current fact or result.
- **Communication.**
  - The main screen shows the property, lots, option, dimensions and values.
  - Each group has one status, with specific exceptions beside the affected results.
  - IDs, hashes, rule versions, full evidence and diagnostics go in details or an appendix.
  - The report has one identification line, such as "Option B · revision 7 · date".
- **Role of AI.** AI drafts rules and tests for review, and powers "Explain this" and "Likely examiner questions". It never changes the numbers.

## 9a. Validation — how we know the numbers are right

Official sources give the law and the data. The program's job is translating them correctly, and that translation is what gets tested.

**Test sources, used together:**
1. **City Planning's published examples.** District diagrams and handbook examples list permitted FAR, heights and achieved floor area for sample buildings. They are free, official test cases.
2. **Real Buildings Department filings.** NYC Open Data job filings list filed zoning floor area and unit counts for real buildings. The engine's answers are compared against filings on lots in the same district family. Differences are investigated one by one, never averaged away. (One competitor validates this way against thousands of filings.)
3. **Hand-checked lots.** For the first district family, the reviewer checks 10–20 real lots by hand, including the pilot lot.
4. **Competitor reports.** Reports bought for the same lots (§11a) are a cross-check. A difference is a question to resolve, not proof either side is right.
5. **Traceability.** Every number shows its Zoning Resolution section, so anyone can check it quickly.
6. **Benchmark lot and checklist.** 215-16 Northern Blvd, Queens (R6B / C2-2, corner). Expected values and checks C-1 to C-12 are in `COMPETITOR_REVIEW_ENVELOPE_215-16_NORTHERN_2026-09-28.md`. Every check must pass on this lot before results are shown to an architect.

**Reviewer (Q12).** Until an independent reviewer is appointed, the owner's architect acts as reviewer for the first district family. He reviews the rule tables and the test lots, not only the screens.

**Honesty.** No one can promise 100%. The standard is that every number is traceable, tested against the sources above, and "Not available" when it cannot be.

## 10. Where the program stands (to be re-verified)

The branch was at `574432f` on 2026-09-27.

| State | Items |
|---|---|
| **Working** | • Address search and confirmation<br>• PLUTO property facts<br>• Condo billing-to-base lot resolution<br>• Per-lot DOF tax-map outlines<br>• Parcel picker (each lot or all)<br>• Together/Separately/Compare study state and JSON export/restore<br>• Floating tools<br>• Honest withholding of unsupported results<br>• Stale-response handling<br>• Server gate and kill switch<br>• Recorded-official-data test harness |
| **Disconnected** | • Study choices never reach calculations or the report ("Not calculated")<br>• The proposal editor starts from an example site (R5, 8,000 sq ft, wide street)<br>• The envelope request is sent without lot or street lines<br>• Site-definition records are not connected to combined calculations<br>• Two property screens host the study (`/property?…&view=overview` and `/property/workspace`) |
| **Disabled or awaiting review** | • Draft rule evaluation, behind an internal flag (draft R7 FAR with wide-street branches; R5 path)<br>• Scenario endpoint, default-off<br>• Site-definition confirmation lifecycle, which needs authentication and storage<br>• 3D/expanded UI, under an owner hold |
| **Missing** | • R7 height, setback, yard and coverage rules<br>• The add-on catalog and toggles<br>• Maximum-building generator<br>• Lot-choice step with the measurement source order<br>• DXF export<br>• Study revisions and invalidation<br>• Report bound to a revision<br>• Authentication<br>• Durable storage |
| **Set-aside candidates** | • Coordinate/vertex proposal drawing in real-property workflows<br>• Example-site defaults<br>• Scenario endpoint (review or retire, Q5)<br>• One of the two property screens (Q4)<br>• Any zoning-lot evidence features beyond §8 |

## 11. Pilots

- **Pilot A — one real single lot, independently verified.**
  - CC researches two or three candidates. Preferred: a district with implemented height rules and at least two supported add-ons, preferably in R6–R10 where the affordable-housing bonus (UAP) applies, and no multi-lot zoning-lot history.
  - The owner confirms the lot and chooses a qualified professional who signs a golden record covering measurements, the three answers (§5), each add-on's gain and the best combination.
- **Pilot B — 298 Wallabout Street**, for multi-lot and condo behavior.
  - **Known:** base lot 32 sits under condo billing lot 3022647515 (Condominium No. 1313). Block 2264 was rezoned from M1-2 to R7-1 in 2001 (C 000109 ZMK).
  - **Reported by secondary sources:** a 7-story, 20-unit building from 2005; a 2023 stop-work order for an unpermitted extra floor.
  - **Unconfirmed:** lot 33 as a base lot, and the street widths.
  - **Limit:** until R7 height rules exist, Wallabout shows floor-area results only, with the height gap named once.

---

## 11a. Competitive landscape (researched 2026-09-28; prices change, so re-check)

| Competitor | What it offers (from its own site or directory listing) | Price per report |
|---|---|---|
| **Envelope** (runenvelope.com; also massingreport.com) | • Every legal scenario: as-of-right, UAP, Inclusionary Housing, community facility, tower-on-base<br>• Per-floor plans, sections, 3D massing<br>• DXF/IFC/OBJ/GLB exports for AutoCAD, Revit, Rhino and SketchUp<br>• Full ZR citations; special districts, split zones and assemblages<br>• Tax programs and pro forma<br>• Validated against thousands of real DOB filings | Free check (envelope, FAR, buildable SF); **$149–499 per report** by buildable SF; unlimited $4,990/yr or $649/month; enterprise $6,990/yr |
| **Tectmind** | • Automated report with incentive toggles, live massing and financial projections<br>• Human-assisted custom analysis in 2–3 business days, with a 60-minute expert call | Custom report/service **$499+**; hire an expert **$1,500+**; automated-report price not published |
| **NYC Zoning AI** (nyczoning.ai) | • FAR and bulk, bonus scenarios, air rights, ADU eligibility, 3D massing, special districts<br>• Revit integration listed<br>• Co-founder is a licensed architect and former DOB assistant chief plan examiner | Not published; free trial listed |
| Traditional zoning consultant or architect | Custom analysis | Often cited as $5,000+ per property |

**What this means.** At least one competitor (Envelope) already sells most of this plan, including CAD export, at $149–499 per report. Speed and export alone are not an edge. **Owner decision (Q13):** match everything they offer, done accurately and consistently (§11b).

---

## 11b. Competitive parity — everything they offer, done accurately (owner decision)

The program will offer everything the leading competitor offers, but correct and consistent. Every parity feature must pass the same rules: sourced values, "Not available" instead of guesses, drawings from the same data as the numbers, and checks C-1 to C-12.

| Feature | Phase |
|---|---|
| Scenario comparison, floor-by-floor area table, unit estimate with its formula | 1 (Milestone 1) |
| Existing building: keep, partial rebuild or full rebuild (§5b) | 1 (Milestone 2, M2-07 and M2-08) |
| Unused floor area on the lot ("air rights" remaining) | 1 |
| Data flags: flood zone, E-designation, landmark, transit/parking zone | 1 |
| Other programs as options: senior housing, community facility, shared housing, commercial overlay, lot split | 1 (catalog, L-1 to L-3) |
| Neighbors' unused floor area estimates (Group C) | 1 (after Milestone 1) |
| Tax-program eligibility (485-x and successors) | 1b (after Milestone 1) |
| Comparable sales | 1b |
| Financials (L-10) | 1b |
| Building-code checks; test-fit floor layouts generated only from engine numbers, never templates | 2 |

**Execution.** Parity work runs in the parallel lanes (`PARALLEL_BUILD_PLAN_LANES_2026-09-28.md`, Wave 3). It never delays Milestone 1.

---

## 12. Tasks, dependency-ordered

**First delivery (the smallest complete slice) is Milestone 1.** It delivers one real property with:
- sourced measurements;
- the three answers where supported;
- meaningful add-on alternatives;
- a matching plan and section;
- reliable PDF and DXF exports.

Catalog and district coverage (L-1) expands in parallel from M1-03 onward.

**Execution:** parallel Codex loops, one lane each, as set out in `PARALLEL_BUILD_PLAN_LANES_2026-09-28.md`. M1-06 is split into M1-06a (server side, Lane C) and M1-06b (interface, Lane D).

### Milestone 1 — verified single-lot pilot

| ID | Task | Depends on | Done when |
|---|---|---|---|
| M1-00 | Architect mockup review *(pending Q10)* | — | Two or three architects have reviewed the §3 flow; findings recorded |
| M1-00b | Competitor benchmark (owner, not code): run the free Envelope check and buy one report each from Envelope and Tectmind for the pilot candidates and 2–3 test lots | — | Features, formats and numbers recorded for comparison (§9a, §11a) |
| M1-01 | Confirm sources on the working branch, including `AGENTS.md` | — | Every §10 claim has a file:line reference or is corrected |
| M1-02 | Runtime configuration record, read-only | — | Deployed SHAs and flags recorded |
| M1-03 | Rule-coverage matrix for every residential district (district × output × add-on) and street-width source | M1-01 | Every R district in the current Zoning Resolution is listed; every cell has a status, inputs and tests |
| M1-04 | Pilot A candidates | M1-03 | Two or three ranked candidates with evidence |
| M1-05 | Verification by the reviewer (Q12), producing the golden record, cross-checked against City Planning examples and competitor numbers | M1-04, M1-00b | Signed record and recorded fixtures |
| M1-06 | Remove example-site defaults from real-property workflows | M1-01 | No example values in any real-property state, request or report |
| M1-07 | Input statuses: survey, city records, approximate, entered, assumed, unknown | M1-06 | Every input shows its status and source |
| M1-08 | Labeled input channel to the evaluator | M1-03, M1-07 | Reviewed contract keeps entered values distinct from facts |
| M1-09 | Study contract: lots, site facts, options as add-on selections | M1-07 | Valid and invalid fixtures pass and fail |
| M1-10 | One study store for every surface | M1-09 | All surfaces agree; editing one option leaves the others unchanged |
| M1-11 | Revisions and dependency-based invalidation | M1-10 | §9 invalidation rules pass their tests |
| M1-13 | Site setup: lot choice and pre-filled measurements with sources | M1-00, M1-03, M1-11 | No measurement has to be typed for Pilot A |
| M1-12 | Connect the evaluator for Pilot A | M1-05, M1-08, M1-13 | Outputs equal the golden record |
| M1-14 | Generator for the three answers: floor-area allowance, permitted envelope, building option | M1-00, M1-12 | All three equal the golden record; any shortfall between the option and the allowance is explained |
| M1-25 | Add-on switches (recalculated together), "Best combination" with a stated goal, and the completeness line | M1-14 | Gains relative to the current selection, and the best combination, equal the golden record; the goal and assumptions are saved with the option |
| M1-15 | Plan diagram per option, using the drawing kit (§5c) | M1-00, M1-14, M1-27 | Dimensions match the numbers |
| M1-16 | Section and 3D massing where height rules exist, using the drawing kit *(Q8 applies to interactive 3D only)* | M1-15, M1-27 | Section and massing match the numbers, or one line names what is missing |
| M1-17 | Communication pass (§9 and §5a) | M1-11 | Passes UI review, including the §5a acceptance test |
| M1-24 | Floor-area availability reminder (§5a) | M1-17 | Available from the status strip and shown once in the report |
| M1-18 | Compare options side by side | M1-15, M1-17 | Identical rows; plans at a common scale |
| M1-19 | Report and historical export | M1-11, M1-15, M1-17 | Report matches the screen and revision |
| M1-22 | PDF, Excel and DXF export (§3, step 7) | M1-15, M1-27 | The PDF contains every listed sheet; the Excel file matches the screen; the DXF opens correctly in AutoCAD and carries the measurement-status note when measurements are not from a survey |
| M1-26 | Validation suite (§9a): City Planning examples, a comparison against filed DOB jobs for the pilot district family, and hand-checked lots, run on every change | M1-12, M1-14 | The suite runs in CI; every difference from a filing or example is investigated and logged |
| M1-27 | Drawing kit and design system (§5c): server-made SVG site plan, section and 3D massing from the results geometry; PDF templates; snapshot tests | M1-14 | Every figure on a drawing matches the tables; benchmark PDFs match approved snapshots; the same SVGs appear on screen |
| M1-20 | Pilot A regression journey | M1-12 to M1-19, M1-22, M1-24, M1-25, M1-26 | Recorded-fixture CI journey from address to export passes |
| M1-21 | Observed architect session | M1-20, M1-02 | Completed without help and without typing any measurement |

### Milestone 2 — 298 Wallabout Street

| ID | Task | Depends on | Done when |
|---|---|---|---|
| M2-00 | Optional research: pull the permit, ACRIS and DTM records | — | Findings recorded with sources |
| M2-05 | Multi-lot site math: combined outline, outside street frontage and lot type; condo base lots in the lot choice | M1-13 | Selecting 1, 2 or all lots updates the outline, frontage, lot type and area correctly on test fixtures |
| M2-06 | §8 warnings | M1-17, M2-05 | Each warning appears once, beside the affected results |
| M2-07 | Existing floor area input, with source | M1-07 | Existing floor area is never taken from DOF building area |
| M2-08 | Keep / partial rebuild / full rebuild comparison (§5b), with the rebuild budget and its traps | M2-07, M1-14 | On the 215-16 Northern Blvd benchmark, path 1 keeps more floor area than path 3, and the app says so |
| M2-01 | Wallabout options (floor area only until R7 height rules exist) | M2-05, M2-06, M2-07, M1-12, M1-14 | Options shown; the height gap is named once |
| M2-02 | Wallabout comparison and report | M2-01, M1-18, M1-19 | Report matches the screen |
| M2-03 | Two-pilot regression | M1-20, M2-02 | Both pilots pass in CI |

### Rest of Phase 1

| ID | Work | Depends on |
|---|---|---|
| L-1 | Every residential (R) district: full add-on catalog and complete rule coverage, built in waves (§12a) | M1-03 |
| L-2 | Group B certifications and the Group C neighbor estimate | L-1 |
| L-3 | Group D: D1 approvals with a text maximum as switches; D2 variances and rezonings as opportunity notes with no number | L-2 |
| L-5 | "Explain this" and "Likely examiner questions" | M1-19 |
| L-6 | Compare several properties *(pending Q10)* | M1-21, L-1 |
| L-7 | Keep the catalog current as the Zoning Resolution changes | L-1 |
| L-8 | Commercial districts that allow housing: a reviewed table pairing each with its residential rules, mixed-building rules, golden cases per district family, and the §12a safeguards | L-1 (wave 2 at minimum) |
| L-9 | Manufacturing zones: check the residential pathways first, such as M1-D districts (where housing may be allowed by City Planning authorization) and special mixed-use districts. Answer "New housing isn't allowed here" only when none applies. | M1-03 |
| L-10 | Simple financials, such as cost and revenue per option *(Phase 1b, §11b)* | M1-21 |
| L-11 | Hidden-issues checks (§8a), added group by group | M1-03 |


### 12a. Covering every residential district

**Scope (owner direction):** every residential (R) district in the current Zoning Resolution, plus residential buildings in commercial zones (below). The M1-03 matrix lists them from the current text, including districts added or changed by City of Yes.

**How.** Build by rule family, not one district at a time: one shared calculation engine, with each district's values kept as reviewed data tables.

**Waves:**
1. The Pilot A district and its family.
2. Medium- and high-density districts (R6–R10), including Quality Housing, height factor and the affordable-housing add-ons. This covers Wallabout's R7-1.
3. Lower-density districts (R1–R5), including their building-type rules and the City of Yes lower-density add-ons, such as accessory dwelling units and transit-oriented development, subject to review.
4. Special purpose districts and special overlays that change R-district rules, including special mixed-use districts. Commercial overlays are not in this wave; they are handled inside the R waves (below).
5. Commercial districts that allow housing (for example C4 or C6), using the residential rules the Zoning Resolution pairs with each, plus the rules for buildings mixing shops and apartments. This wave starts right after the R waves, and may overlap wave 2 where the pairs line up.

**Commercial overlays** (for example "R7A/C2-4") are handled inside the R waves: the R district's rules apply, and ground-floor commercial space is one more optional add-on.

**Manufacturing zones.** Before declaring housing prohibited, the app checks the known residential pathways: M1-D districts (housing by City Planning authorization), special mixed-use districts (wave 4), and any others the catalog review finds. Pathways that need approval are shown as opportunities, not numbers. Only when none applies does the app answer "New housing isn't allowed here", with the reason.

**Honesty rule.** A district is marked complete only when every output and add-on is implemented, tested and reviewed. Until then, supported answers still show, unsupported answers show "Not available" (§5), and the status strip says the district is incomplete.

**Pace.** The qualified reviewer's time sets the speed, so reviews are batched by rule family.

**No-mix-up safeguards for commercial zones (owner requirement).** Adding commercial zones must never make an architect's numbers wrong or confusing.
1. **Exact zone identification.** The district, any overlay and any split are read from official zoning map data. Lots split between zones, or with an unrecognized district, are flagged and never guessed.
2. **All-residential headline.** The headline stays an all-residential building, computed with the paired R rules. Ground-floor stores are an optional switch that shows what they add and what they take away. They never silently change the headline.
3. **Visible rule basis.** Every result has its rule basis one tap away, for example "C4 district — residential rules of its paired R district", and the report states it. It is not repeated beside every number (§5a).
4. **Differences captured.** Where a commercial district's rules differ from its paired R district, the difference is implemented and tested, never assumed away.
5. **Reviewed before live.** A commercial district goes live only after the reviewer checks it against hand-calculated examples. Until then its answers show "Not available" (§5), and the status strip says the district is incomplete.
6. **R answers locked.** Automated tests confirm that adding commercial zones changes no R-district golden result.

### Phase 2

| ID | Work | Depends on |
|---|---|---|
| P2-1 | Building-code feasibility (§2) | Phase 1 complete for the residential districts it will cover (owner may start it before every wave finishes) |

## 13. Decisions

| # | Decision | Status |
|---|---|---|
| Q1 | Pilot A lot and verifier | CC recommends the lot; the owner confirms it and chooses the verifier |
| Q2 | Combined results for selected lots | **Decided:** calculated for the lots the architect selects, labeled as his choice |
| P-2 | Sold or merged development rights | **Decided:** a reminder only; no records check |
| Q4 | Which property screen is the base; what happens to the other | Open — owner |
| Q5 | Scenario endpoint: review or retire | Open — owner |
| Q7 | Authentication and exposure timing | Open — owner |
| Q8 | Whether the section view falls under the expansion hold | Open — owner |
| Q9 | District scope | **Decided:** every residential (R) district, built in waves (§12a) |
| Q10 | Confirm or reject the mockup review (M1-00) and property comparison (L-6) | Open — owner |
| Q11 | Cover residential buildings in commercial zones | **Decided:** yes, with the §12a no-mix-up safeguards. Overlays go inside the R waves; commercial districts follow the R waves (L-8); manufacturing zones get a clear answer (L-9). |
| Q12 | Reviewer | **Interim:** the owner's architect reviews rule tables and test lots for the first district family (§9a). Confirm his licensing and available time. |
| Q13 | Competitive edge | **Decided:** full parity with the leading competitor, done accurately (§11b). **Still open:** pricing. |
