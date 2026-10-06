# The sample report, section by section, against the report we intend to build

Written 2026-10-06 by the orchestrator. Asked for by the owner (D-090 source-035: R248 to R254,
R261). Corrected the same day after the owner's check (source-036: R266 to R273): it now says what a
user can already see on the existing property screens, apart from the new results and the PDF that
are not connected; and it drops nothing. Documents only: nothing is built by it.

**The goal (R248, R249, R251).** A full feasibility report of the kind of the owner's sample, with
numbers that can be relied on. Not a zoning summary. It is built one piece at a time, and a finished
piece is a milestone, never completion.

**The sample.** The 88-page "Zoning Analysis and Massing Study" for 215-16 Northern Boulevard that
the owner supplied (dated September 18, 2026). It is the KIND of report (R142). None of its numbers is
copied or treated as true; the earlier review found it disagrees with itself in several places. It is
not committed to the repository. Its text was read page by page for this map.

**The line (R254).** No detailed apartment layouts and no permit-ready plans. Rows marked OUTSIDE
fall beyond that line. Rows marked BEYOND THE NINE are inside the line but are not among the nine
contents the owner named.

**Nothing is dropped (R272).** Every section of the sample inside the line, and all eleven of its
options, stay in the goal unless the owner agrees to drop one. What this document proposes is an
order of building. Where it asks whether something should be dropped, that is a question, and the
answer until the owner gives one is "it stays".

## 1. The nine contents of the intended report (R252, R253)

| # | Content | What it means here |
|---|---|---|
| A | Property facts | what the official records say about the lot, each with its source and date |
| B | Applicable zoning | the limits that apply, each with its law section; what is not checked is named |
| C | Development options | the ways the lot could be developed that the program supports |
| D | Estimated floors | for each option, how many floors and a simple floor-by-floor table |
| E | Simple building shapes | the lot, the yards, the allowed envelope and the option's shape, as labelled diagrams |
| F | Legal unit limits | the maximum number of dwelling units the law allows, where a limit applies |
| G | Realistic apartment-count estimates | a practical estimate from stated, editable assumptions; always apart from F |
| H | Option comparisons | the options side by side on stated criteria; no "best" without the criterion |
| I | The downloadable report | one PDF that says the same as the screen |

A legal maximum (B, F) and a practical estimate (D, G) are never shown as one figure or under one
label, and every estimate prints its assumptions (R253).

## 2. The map

"Exists as code" means code is on the integration branch (commit `e97bf405`) or in a reviewed change
that is waiting to merge (named). It is never "finished". Paths start at `services/api/app/` unless
they start with `apps/` or `packages/`.

"On a screen today" is one of three things, read from the website's code at `e97bf405`:

- **yes** = on an existing property screen that needs no switch;
- **switch off** = on an existing screen that only appears when an internal switch is on, and no
  committed setting turns any of them on;
- **no** = on no screen.

Section 2a describes those screens. The new results (the R6B floor-area figures, heights, coverage,
unit limit, building option, floors and shapes of the newer engine), any comparison of options, the
report builder and any downloadable file are on no screen and are not connected to one.

| Sample section (pages) | Goes to | Exists as code | On a screen today | Remains | Line |
|---|---|---|---|---|---|
| Cover (1): title, headline floor area, unit range, lot identity | I | nothing rendered; the report contract names a cover (`packages/contracts/schemas/v1/report_model.schema.json`) | no | the report builder and the cover page. No "best-in-class" headline: a headline figure needs its criterion (R260). | inside |
| Contents (2) | I | nothing | no | made by the report builder | inside |
| Executive summary (3): headline floor area, unit range across options, maximum floor-area ratio and height, key constraints, programs, site at a glance | A, B, C, H | the engine computes the floor-area figures, the height limits and the legal unit limit for R6B (`scenario/three_answers/`); no summary page | no | the summary page; a unit RANGE needs options (C) and estimates (G), which are not built | inside |
| Property location (4): city map, neighbourhood map, close-up with the lot line | A | vector location and zoning map drawings and their input contract (`drawings/maps/`, `packages/contracts/schemas/v1/map_context.schema.json`); not connected to any result | switch off: a lot-outline map in the workspace; the location and zoning map drawings: no | connect the maps to the result and the report | inside |
| Property location (4): aerial and street photographs | A | none | no | an imagery licence | BEYOND THE NINE; stays unless the owner agrees to drop it |
| Site summary (4-5): address, borough, block and lot, lot area, frontage, depth, lot type, community district, existing floor-area ratio, floors, building area, land use, street width, split zone | A | the official-record connector (`connectors/pluto_soda.py`), the facts read with source labels (`api/v1/study_read.py`), lot outline and frontages (`spatial/site_geometry`), street widths (`spatial/frontage_street_width`), existing floor area read or honestly unknown (`profile/existing_floor_area/`), address lookup (`connectors/geoclient_address.py`) | **yes**: the property page shows the official lot and existing-building facts for any lot; the newer facts with source ranks, frontages and street widths: switch off | a facts page; the address of this lot has no recorded lookup (the key is the owner's); street width is not yet shown with the facts; the two lot-area figures (work order, section 6) | inside |
| Site summary (5): block character, largest property on the block | A | partly: comparable-property data (`profile/parity/`) | switch off: a comparable-sales tool in the workspace; no block description | a written block description is not built | BEYOND THE NINE; stays |
| Applicable development characteristics (5): district in words, street class, lot type, parking, overlay, flood zone | A, B | recorded flags for overlay, special district, flood, landmark, inclusionary housing, split lot (`profile/hidden_issue_flags/`); transit and parking zone status (`profile/transit_parking.py`) | **yes**: districts, overlays, special districts and the landmark and flood flags on the property and confirm pages; the fuller flag list: switch off | wire each flag into the result as evidence (work order K10, K18, K19); conditions with no data source (K20) | inside |
| Zoning overview (6-7): zoning map, district, floor-area ratio, height, unit limit, base rules table (base heights, building height, rear yard, side yards, coverage, unit factor), floor-area ratio by use | B, F | six R6B rule files with their law sections (floor area, qualifying floor area, height, coverage, rear-yard waiver at a corner, unit limit) in `rules/rulesets/`; the engine; an independent hand calculation agrees wherever the engine gives a number | switch off: an older calculation shows one draft floor-area cap and a draft rule evaluation, labelled draft and tax-lot-only; the R6B heights, coverage, rear yard and unit limit: no | the gaps of the work order (K1 to K20): coverage and rear yard for part of a lot, setback, overlay rules, side yards, community-facility floor area; the page itself | inside |
| Calculation detail (8): plan of the lot with the buildable footprint and yards; footprint numbers; the unit-limit arithmetic | E, F | a simplified lot rectangle, envelope and floor plates in the result (`scenario/three_answers/geometry.py`); a site-plan drawing (`drawings/kit/`); an AutoCAD file (`cad/results_dxf.py`); the unit-limit arithmetic (`scenario/three_answers/dwelling_units.py`) | no | drawing from the recorded outline, labelled approximate; yards and setbacks that are known (K1, K4, K8); nothing drawn where the result is withheld | inside |
| Zoning analysis (9-10): the full parameter table with law references: district, site area, floor area, overlay detail and permitted uses, yards, courts, street wall, units, parking, loading, bicycle parking | B | the R6B rows above; street-wall text is captured with no rule; parking is a zone status only | no (the workspace's zoning tool, switch off, shows district facts and the older draft evaluation) | a parameter-table page; overlay uses and commercial floor area; courts; street wall; parking, loading and bicycle parking are not computed | inside; parking, loading and bicycle counts are BEYOND THE NINE and stay |
| Applicable zoning programs (10): programs screened, which apply, bonus, affordable share | C | a catalogue of add-ons as data with one live entry (qualifying housing) and the rest marked not available (`scenario/addons/`, waiting as #439) | no | rules for each of the promised options (section 4, choice 1) | inside |
| Scenario comparison (11-12): a card per option and one numeric table (floor area, height, floors, units, gross area, floor-area ratio, residential area, other uses, loss, parking) | H | a comparison contract and a builder that gives identical rows for any two options (`contracts/compare_rows.py`); an older comparison in `scenario/comparison.py` | no: a compare page exists but its server route is off, and it shows one older scenario's constraints, not options side by side | options to compare (C, D, G); stated criteria; no "BEST" tag without its criterion (R260); the page | inside |
| Tax abatement eligibility (13-14) | none | none; the code says it computes none | no | everything | BEYOND THE NINE; stays unless the owner agrees to drop it |
| Comparable sales nearby (15) | none | comparable sales from city sales records and a read route (`profile/parity/comparable_sales.py`, `api/v1/parity_read.py`); no averages by product choice | switch off: the workspace's comparable-sales tool | a page, if wanted | BEYOND THE NINE; stays unless the owner agrees to drop it |
| Each of the 11 scenario chapters (16-87): header and narrative (program, floor-area ratio, height, why floor area is left unused) | C | one option for R6B (standard residences) with a qualifying-housing alternative; the reason for unused floor area exists as a "shortfall" field | switch off: the older engine's single scenario; the newer option: no | the other ten options; the narrative page | inside |
| Scenario chapter: summary (floor area, gross area, net area, floors, height, units, parking) | D, F, G | floors, height and floor area of the one option (`scenario/three_answers/building_option.py`), currently withheld by gaps K4, K6, K8; the legal unit limit | no | gross and net area and the realistic unit estimate are not built (G) | inside |
| Scenario chapter: building core (stairs, elevators, shafts, corridor, core per floor) | G | none | no | at most ONE shared-space allowance as a visible, editable assumption of the estimate | the allowance is inside; a designed core is OUTSIDE |
| Scenario chapter: proposed floor area schedule (per floor: use, gross area, deductions, zoning floor area, efficiency) | D | a floor-by-floor table and floor stack in the result contract and the engine (`floor_by_floor`, `floor_stack`) | no | per-floor use for options with more than one use; every percentage states what is divided by what; kept simple | inside, simplified |
| Scenario chapter: financial analysis inputs | none | none | no (a "Financials" tool is a planned placeholder) | everything | BEYOND THE NINE; held by the owner's earlier hold on financial analysis, not dropped by this document |
| Scenario chapter: synthesized floor plans (cellar, ground, typical, top, roof, with rooms and apartments) | none | none | no | nothing: not built on purpose | **OUTSIDE** (detailed apartment layouts) |
| Scenario 11: split lot, two buildings | C | a recorded flag for split lots; a multi-lot site write route, off by default | switch off: a parcel-study tool for multi-parcel records; no option | an option of its own, with building and site figures kept apart | inside; promised |
| Colophon and disclaimers (88): report id, date, data versions, law currency, sources, limits | I | data-version checks (`profile/data_versions.py`); the standing label (waiting as #433); a reproducibility reference in the report contract | no | the page | inside |
| The PDF itself | I | a single-sheet site-plan PDF writer (`cad/pdf_sheet_writer.py`) behind an export route that is not mounted (`api/v1/export_api.py`); the report contract; a converter trial folder (`docs/samples/pdf-converter-trial`) | no file anywhere; switch off: a browser print view ("Print property brief") that makes no file | the report builder, a report route, the multi-page PDF; the converter choice and saved-report storage are owner decisions already on the list | inside |

## 2a. What a user can see today, and what is not connected (R273)

Read from the website's code at `e97bf405` by a read-only helper. No evidence was found that the
website is deployed anywhere: the deployment file says nothing is provisioned, and no setting in it
turns a switch on.

**On the existing property screens, with no switch:**

- The property page: enter a tax-lot number and see the official profile for any lot. It shows the
  lot's identity, how complete the data is, conflicts between sources, the zoning facts (districts,
  overlays, special districts, flags), lot facts, existing-building facts, and what is missing.
- The confirm page: a property card with the lot summary, existing building, zoning and overlays,
  landmark and flood flags, conflicts, and the questions the data cannot answer.
- A compare page that loads and says the feature is not available, because its server route is off.

That is property facts (A) and the zoning facts of the lot (part of B). **Nothing computed is on
these screens.**

**On existing screens behind internal switches, all off:**

- An architect workspace with tools for the property map, facts, lot and site setup, zoning and
  development limits, scenarios, a proposal editor, evidence, items to review, hidden issues,
  comparable sales, a property report, condo and parcel records. "Unit estimate" and "Financials"
  are placeholders.
- What it computes comes from an **older calculation**, not the newer R6B one: a single draft
  floor-area cap and a draft rule evaluation. It prints "Draft zoning floor-area cap" and "Tax-lot-only
  estimate", says the buildable envelope is not assessed, and shows the remaining development
  capacity as "Not confirmed".
- Its "property report" is a browser print view ("Print property brief"). It makes no file.

**On no screen, and not connected to one:**

- **The new results.** The newer engine that computes the R6B floor-area figures, heights, coverage,
  rear yard, legal unit limit, building option, floors and simple shapes is called by no server
  route. This is what the work order's first milestone connects.
- **Any comparison of options**, the realistic apartment estimate (not built), and the remaining
  ten options.
- **The full PDF.** There is no report builder and no route that returns a file. The code that can
  write a drawing file or a one-sheet PDF exists and is not mounted.

## 3. Where each of the nine contents stands

| # | Content | On a property screen today | Exists as code, not connected | What is owed |
|---|---|---|---|---|
| A | Property facts | **yes**: official lot and building facts for any lot | newer facts with source ranks, frontages, street widths (switch off) | the facts page; the two-area rule; street width with the facts |
| B | Applicable zoning | **yes** for the zoning facts (district, overlays, flags); no limit is computed there | six R6B rules and the newer engine (no screen); an older draft floor-area cap (switch off) | the gaps K1 to K20; side yards, courts, street wall, overlay rules; the remaining R6B checklist rows |
| C | Development options | no | one option and one alternative in the newer engine; one scenario in the older one (switch off) | every other option version one promises |
| D | Estimated floors | no | in the newer engine; withheld by known gaps | close K4, K6, K8; an independent reference case for a building option |
| E | Simple building shapes | no (a flat lot outline only, switch off) | a simplified rectangle and envelope; a site-plan drawing; an AutoCAD file | shapes from the recorded outline, the known yards and setbacks; agreement with the numbers |
| F | Legal unit limits | no | the rule and its arithmetic for standard residences | the density-area fact from evidence (K11); the qualifying-housing case (K13) |
| G | Realistic apartment-count estimates | no (a placeholder tool) | **not built** | the whole estimate: shared-space allowance and average apartment size as visible, editable starting values the owner approves |
| H | Option comparisons | no | a row builder only | options, criteria, the page |
| I | Downloadable report | no file (a print view only, switch off) | **not built**; a one-sheet PDF writer and export route, not mounted | report builder, route, PDF |

## 4. The scope choices that remain (R264, R271, R272)

Nothing below removes a section of the sample or an option. Each choice says what is recommended
and what it adds to the work. "A piece" means: its law text captured and read, worked reference
cases, the rule or calculation, its place on the screen and in the PDF, and its tests.

**Settled by the owner, no longer a choice:** how conditions the program cannot check are treated
(R268). Answers they cannot change stay visible; answers that hold only if they do not apply are
conditional and name them; answers that cannot be supported are withheld. A district limit is not
the property's confirmed maximum (R269). What it adds: a data source for each of four conditions
(waterfront rules, airport height limits, transit easements, a lot close to a district line), four
research-and-connect pieces, before the affected results can be settled.

| # | Choice | Recommendation | What it adds to the work |
|---|---|---|---|
| 1 | **The order of the sample's eleven development options.** All eleven stay promised. | Standard residences first; then qualifying affordable housing; qualifying senior housing; the "more, smaller apartments" variant; ground-floor shops with residences above; residences with a community facility; community facility alone; a split lot with two buildings; shared housing and its parking-waiver variant; all programs combined last, because it needs the others. | One piece per option. The first four reuse rules that largely exist. Shops and community facility each need a rule family that is not captured. The split lot needs two-building modelling with building and site figures kept apart. Shared housing needs its own use and parking rules. |
| 2a | Comparable sales nearby | Keep. Build after the options. | Small: the data and a workspace tool exist; it needs a report page. Averages and price per square foot are a product choice not made yet. |
| 2b | Block description (neighbours, largest property) | Keep. | Small to medium: uses the same neighbour data; the wording must be generated from facts. |
| 2c | Parking, loading and bicycle-parking counts | Keep. Build after the first four options. | Medium: a rule family that is not captured; only the transit-zone status exists. |
| 2d | Aerial and street photographs | Keep, once the imagery licence is decided. The vector maps go in regardless. | Small after the licence. |
| 2e | Tax abatement eligibility | Keep in the goal and build it last. It is tax law, not zoning. If the owner would rather drop it, that is the owner's to say. | Large: new law text, eligibility rules for each option, its own reference cases. |
| 2f | Financial analysis inputs | Held by the owner's earlier hold on financial analysis. It stays held, not dropped, until the owner lifts the hold. | Medium once released; its gross, net and efficiency figures overlap with the realistic estimate, which is in. |
| 3 | How the realistic apartment estimate is made | Start with one average apartment size and one shared-space allowance, both visible and editable. Add a mix of apartment types afterwards. | Small to start: one calculation and its reference cases. The mix adds a table of types and more cases. |
| 4 | The starting values (floor-to-floor height, average apartment size, shared-space allowance) | The owner approves them. The orchestrator brings proposed values with the basis for each; none is taken from the sample. | No building work; one short proposal. |
| 5 | Already on the owner's list, unchanged: the PDF converter; where saved reports are stored; the imagery licence | As before. | The converter is one new package through the dependency-security check; storage needs the owner's credential. |

Outside the line by the owner's own rule, and so not a choice: the sample's floor plans with rooms
and apartments, and a designed building core.

## 5. What this document does not establish

- It builds nothing.
- "Exists as code" rows were checked for the existence of the named files at the named commits, not
  re-tested for this document. "On a screen today" was read from the website's code, not by running
  the website.
- It does not show that the website is deployed anywhere.
- It does not decide the scope choices of section 4, and it drops nothing.
