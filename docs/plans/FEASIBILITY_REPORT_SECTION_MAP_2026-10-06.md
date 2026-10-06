# The sample report, section by section, against the report we intend to build

Written 2026-10-06 by the orchestrator. Asked for by the owner (D-090 source-035: R248 to R254,
R261). Documents only: nothing is built by it.

**The goal (R248, R249, R251).** A full feasibility report of the kind of the owner's sample, with
numbers that can be relied on. Not a zoning summary. It is built one piece at a time, and a finished
piece is a milestone, never completion.

**The sample.** The 88-page "Zoning Analysis and Massing Study" for 215-16 Northern Boulevard that
the owner supplied (dated September 18, 2026). It is the KIND of report (R142). None of its numbers is
copied or treated as true; the earlier review found it disagrees with itself in several places. It is
not committed to the repository. Its text was read page by page for this map.

**The line (R254).** No detailed apartment layouts and no permit-ready plans. Rows marked OUTSIDE
fall beyond that line. Rows marked NOT IN THE LIST are inside the line but are not among the nine
contents the owner named; they are open scope decisions (section 4).

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

"Built" means code exists on the integration branch (commit `e97bf405`) or in a reviewed change that
is waiting to merge (named). **Nothing in this table is on a screen a user can reach today:** no
results route, no report builder and no report PDF exist. "Built" is never "finished".

Paths start at `services/api/app/` unless they start with `apps/` or `packages/`.

| Sample section (pages) | Goes to | Built today | Remains | Line |
|---|---|---|---|---|
| Cover (1): title, headline floor area, unit range, lot identity | I | nothing rendered; the report contract names a cover (`packages/contracts/schemas/v1/report_model.schema.json`) | the report builder and the cover page. No "best-in-class" headline: a headline figure needs its criterion (R260). | inside |
| Contents (2) | I | nothing | made by the report builder | inside |
| Executive summary (3): headline floor area, unit range across options, maximum floor-area ratio and height, key constraints, programs, site at a glance | A, B, C, H | the engine computes the floor-area figures, the height limits and the legal unit limit for R6B (`scenario/three_answers/`); no summary page | the summary page; a unit RANGE needs options (C) and estimates (G), which are not built | inside |
| Property location (4): city map, neighbourhood map, close-up with the lot line | A | vector location and zoning map drawings and their input contract (`drawings/maps/`, `packages/contracts/schemas/v1/map_context.schema.json`); not connected to any result | connect the maps to the result and the report | inside |
| Property location (4): aerial and street photographs | A | none | an imagery licence | NOT IN THE LIST (owner decision) |
| Site summary (4-5): address, borough, block and lot, lot area, frontage, depth, lot type, community district, existing floor-area ratio, floors, building area, land use, street width, split zone | A | the official-record connector (`connectors/pluto_soda.py`), the facts read with source labels (`api/v1/study_read.py`), lot outline and frontages (`spatial/site_geometry`), street widths (`spatial/frontage_street_width`), existing floor area read or honestly unknown (`profile/existing_floor_area/`), address lookup (`connectors/geoclient_address.py`) | a facts page; the address of this lot has no recorded lookup (the key is the owner's); street width is not yet shown with the facts; the two lot-area figures (work order, section 6) | inside |
| Site summary (5): block character, largest property on the block | A | partly: comparable-property data (`profile/parity/`) | a written block description is not built | NOT IN THE LIST |
| Applicable development characteristics (5): district in words, street class, lot type, parking, overlay, flood zone | A, B | recorded flags for overlay, special district, flood, landmark, inclusionary housing, split lot (`profile/hidden_issue_flags/`); transit and parking zone status (`profile/transit_parking.py`) | wire each flag into the result as evidence (work order K10, K18, K19); conditions with no data source (K20) | inside |
| Zoning overview (6-7): zoning map, district, floor-area ratio, height, unit limit, base rules table (base heights, building height, rear yard, side yards, coverage, unit factor), floor-area ratio by use | B, F | six R6B rule files with their law sections (floor area, qualifying floor area, height, coverage, rear-yard waiver at a corner, unit limit) in `rules/rulesets/`; the engine; an independent hand calculation agrees wherever the engine gives a number | the gaps of the work order (K1 to K20): coverage and rear yard for part of a lot, setback, overlay rules, side yards, community-facility floor area; the page itself | inside |
| Calculation detail (8): plan of the lot with the buildable footprint and yards; footprint numbers; the unit-limit arithmetic | E, F | a simplified lot rectangle, envelope and floor plates in the result (`scenario/three_answers/geometry.py`); a site-plan drawing (`drawings/kit/`); an AutoCAD file (`cad/results_dxf.py`); the unit-limit arithmetic (`scenario/three_answers/dwelling_units.py`) | drawing from the recorded outline, labelled approximate; yards and setbacks that are known (K1, K4, K8); nothing drawn where the result is withheld | inside |
| Zoning analysis (9-10): the full parameter table with law references: district, site area, floor area, overlay detail and permitted uses, yards, courts, street wall, units, parking, loading, bicycle parking | B | the R6B rows above; street-wall text is captured with no rule; parking is a zone status only | a parameter-table page; overlay uses and commercial floor area; courts; street wall; parking, loading and bicycle parking are not computed | inside; parking, loading and courts are NOT IN THE LIST as computed items |
| Applicable zoning programs (10): programs screened, which apply, bonus, affordable share | C | a catalogue of add-ons as data with one live entry (qualifying housing) and the rest marked not available (`scenario/addons/`, waiting as #439) | rules for each program that version one promises (section 4, decision 1) | inside |
| Scenario comparison (11-12): a card per option and one numeric table (floor area, height, floors, units, gross area, floor-area ratio, residential area, other uses, loss, parking) | H | a comparison contract and a builder that gives identical rows for any two options (`contracts/compare_rows.py`); an older comparison in `scenario/comparison.py` | options to compare (C, D, G); stated criteria; no "BEST" tag without its criterion (R260); the page | inside |
| Tax abatement eligibility (13-14) | none | none; the code says it computes none | everything | NOT IN THE LIST (owner decision) |
| Comparable sales nearby (15) | none | comparable sales from city sales records and a read route (`profile/parity/comparable_sales.py`, `api/v1/parity_read.py`); no averages by product choice | a page, if wanted | NOT IN THE LIST (owner decision) |
| Each of the 11 scenario chapters (16-87): header and narrative (program, floor-area ratio, height, why floor area is left unused) | C | one option for R6B (standard residences) with a qualifying-housing alternative; the reason for unused floor area exists as a "shortfall" field | the other options that version one promises; the narrative page | inside |
| Scenario chapter: summary (floor area, gross area, net area, floors, height, units, parking) | D, F, G | floors, height and floor area of the one option (`scenario/three_answers/building_option.py`), currently withheld by gaps K4, K6, K8; the legal unit limit | gross and net area and the realistic unit estimate are not built (G) | inside |
| Scenario chapter: building core (stairs, elevators, shafts, corridor, core per floor) | G | none | at most ONE shared-space allowance as a visible, editable assumption of the estimate | the allowance is inside; a designed core is OUTSIDE |
| Scenario chapter: proposed floor area schedule (per floor: use, gross area, deductions, zoning floor area, efficiency) | D | a floor-by-floor table and floor stack in the result contract and the engine (`floor_by_floor`, `floor_stack`) | per-floor use for options with more than one use; every percentage states what is divided by what; kept simple | inside, simplified |
| Scenario chapter: financial analysis inputs | none | none | everything | NOT IN THE LIST; financial analysis is under an owner hold |
| Scenario chapter: synthesized floor plans (cellar, ground, typical, top, roof, with rooms and apartments) | none | none | nothing: not built on purpose | **OUTSIDE** (detailed apartment layouts) |
| Scenario 11: split lot, two buildings | C | a recorded flag for split lots; a multi-lot site write route, off by default | an option of its own, with building and site figures kept apart | inside if promised (section 4, decision 1) |
| Colophon and disclaimers (88): report id, date, data versions, law currency, sources, limits | I | data-version checks (`profile/data_versions.py`); the standing label (waiting as #433); a reproducibility reference in the report contract | the page | inside |
| The PDF itself | I | a single-sheet site-plan PDF writer (`cad/pdf_sheet_writer.py`) behind an export route that is not mounted (`api/v1/export_api.py`); the report contract; a converter trial folder (`docs/samples/pdf-converter-trial`) | the report builder, a report route, the multi-page PDF; the converter choice and saved-report storage are owner decisions already on the list | inside |

## 3. Where each of the nine contents stands

| # | Content | State today | What is owed |
|---|---|---|---|
| A | Property facts | read from official records with sources; not on a results screen | the facts page; the two-area rule; street width with the facts |
| B | Applicable zoning | six R6B rules; independent values agree where a number exists | the gaps K1 to K20; side yards, courts, street wall, overlay rules; the remaining R6B checklist rows |
| C | Development options | one option and one alternative | every other option version one promises |
| D | Estimated floors | exists in the engine; withheld by known gaps | close K4, K6, K8; an independent reference case for a building option |
| E | Simple building shapes | a simplified rectangle and envelope; a site-plan drawing; an AutoCAD file | shapes from the recorded outline, the known yards and setbacks; agreement with the numbers |
| F | Legal unit limits | built for standard residences | the density-area fact from evidence (K11); the qualifying-housing case (K13) |
| G | Realistic apartment-count estimates | **not built** | the whole estimate: shared-space allowance and average apartment size as visible, editable starting values the owner approves |
| H | Option comparisons | a row builder only | options, criteria, the page |
| I | Downloadable report | **not built** | report builder, route, PDF |

## 4. Scope decisions that are still open (R264)

None of these blocks the work order's first milestone. Each is needed before the piece it names.

1. **Which development options version one promises for R6B.** The sample shows eleven. Suggested
   first set: standard residences; qualifying affordable housing; qualifying senior housing;
   ground-floor commercial with residences above, on an overlay lot. Suggested later: community
   facility, residences with a community facility, shared housing, a split lot with two buildings,
   all programs combined. "Maximum units with smaller apartments" is not a separate legal option; it
   is the same option with a different average apartment size (G).
2. **Sample sections outside the nine contents:** tax abatement eligibility, comparable sales,
   aerial and street photographs, parking and loading counts, block description. In or out of
   version one? Financial inputs stay out while the owner's hold stands.
3. **Conditions the program has no data for** (waterfront rules, airport height limits, transit
   easements, a lot close to a district line). Either the results they could change are withheld for
   every lot until a data source exists, or the results are shown with a fixed, visible list of what
   was not checked. Recommended: the visible list, because withholding would blank every lot.
4. **The starting values for the realistic estimate** (average apartment size, shared-space
   allowance) and for the floor-to-floor height. The owner approves them; the program does not
   invent them.
5. Already on the owner's list and unchanged: the PDF converter, saved-report storage, the imagery
   licence, turning any switch on in production.

## 5. What this document does not establish

- It builds nothing. No row means a user can see the item today.
- "Built" rows were checked for the existence of the named files at the named commits, not re-tested
  for this document.
- It does not decide the open scope questions of section 4.
