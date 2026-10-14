# M5-T177 (producer) - step P8: Building B's placement on lot 70 and its area allocation

I am an AI agent (role rules-engineer), the producer for M5-T177. I built the new R6B reference
case `placement-building-b` from the two independent step-P8 readings. This is a draft reading of
law by AI helpers, not professionally reviewed; agreement between two AI readings is not proof.

Worktree: `/root/project/nyc-buildability/.claude/worktrees/agent-a084c38dbebc70d69`
Contract base (reset to): `e27bc2a00fbb71d2741a6a161c40325403bba7de`

## Rows added (11, all in `cases/placement-building-b.json`)

`plate`, `physical-plate-not-checked`, `footprint-tax-map`, `placement-tax-map`,
`gis-conflict-check`, `lot-coverage-max`, `lot-coverage-whole-lot`, `rear-yard`, `area-allocation`,
`both-readers-did-not-have`, `real-lot-missing-facts`. Value rows: plate, footprint-tax-map,
placement-tax-map, lot-coverage-max, area-allocation, both-readers-did-not-have,
real-lot-missing-facts. Not-known rows: physical-plate-not-checked, gis-conflict-check,
lot-coverage-whole-lot, rear-yard.

## Files written (LF sha256, `tr -d '\r' < f | sha256sum`)

- `9c3e0ebbd8e1edf36b2d904e1aaf94c79e24769cf5b09a6e0730794c2e92ae81`  docs/reference-cases/R6B/cases/placement-building-b.json
- `9ea4306f825fab61cfcf3c5205a09fcc723d8e970fa73dd34498b08cab494af6`  docs/reference-cases/R6B/placement-building-b.md
- `22cdeea31cc1c51e0a232a663707e7d48bd2522e6c0a0b2e0f08aeb1536794d5`  docs/reference-cases/R6B/README.md
- `7d6b923da87cb8f53028463c6d6d40e03e3e495b6dd0e1bcd453b30b9db76617`  docs/reference-cases/R6B/provenance/return-independent-hand-calculation-17.md
- `0e166f96f4831c85c8cb68028366d0412a0bcb4b6b578325ab9739c1d8cf3743`  docs/reference-cases/R6B/provenance/return-independent-hand-calculation-18.md
- `3b931e1dd532b87fe232c609fd55e37685abb46190418d23ddc596bccc148de1`  services/api/tests/rules/reference_cases/r6b_reference_cases_lib.py
- `42c4782ff7ae32ff206f903fae580f246967510e26c29df6c40c9580955e044e`  services/api/tests/rules/reference_cases/r6b_reference_cases_check.py
- `b4714322a1e54d9c108d51a59de6dc5060e86cc66a0080294dd7264660c8b27e`  services/api/tests/rules/reference_cases/r6b_reference_cases_step_p8.py
- `54ee2a49ba6bc6a2c9bc8b84db6303d6f99588ab1eca1893527390a18ef7c3f8`  services/api/tests/rules/reference_cases/test_r6b_reference_cases_step_p8.py
- `a3d55442058c58ea317949438a4b6678c829b737dab1661cb604b0bef3ba2017`  services/api/tests/rules/reference_cases/test_r6b_reference_cases.py
- `fc5f3bb957cdd161bdf2b3ae7bc426db44948337f9ec84e94ad2da7362152bdb`  services/api/tests/rules/reference_cases/test_r6b_reference_cases_step_p7.py
- (this file)  project-control/reports/M5-T177-producer-report.md

The provenance -17/-18 LF sha256 equal the digests pinned in the step-P8 module (the files carry no
CR bytes).
`r6b_reference_cases_render.py` is in allowed_paths but was left byte-identical (no construct was
missing; the step-P6 numbers_block differ-figure was NOT reused - its "reading 13/14" labels are
hardcoded). Provenance digests pinned in the step-P8 module:
-17 `7d6b923da87cb8f53028463c6d6d40e03e3e495b6dd0e1bcd453b30b9db76617`,
-18 `0e166f96f4831c85c8cb68028366d0412a0bcb4b6b578325ab9739c1d8cf3743`.

## Provenance: the two readings saved unchanged

Each reading was made on 2026-10-14 by a different AI helper (reading 1 a geospatial-engineer,
reading 2 a scenario-optimization-engineer) working alone from the sealed folder
`session-2026-10-14a/sealed-p8` (189 pinned law captures without their notes, 8 fact files; I
counted both: `ls law | wc -l` = 189, `INDEX.json` law=189 facts=8). The sealed settled sheet holds
**18** settled answers (I counted: `len(settled_by_earlier_readings.json.answers)` = 18); the earlier
footprint answer `step-p6-worked#real-building-b` is **not** among them (left out on purpose). Each
provenance file carries a short header in the words of files 15/16 saying truly "EIGHTEEN answers
settled by earlier readings" and "real-building-b was left out on purpose", then the reading
byte-for-byte below it, ending END-OF-REPORT.

## Point-by-point comparison of the two readings

Where both agree on the same words and basis I recorded a value; otherwise NOT SETTLED. The points:

AGREE (same basis): plate 6,716.67 (20,150/3); footprint on the printed-tax-map basis 100.76 x
66.66 = 6,716.66 (0.01 sq ft under the plate); the three touches at 0 ft (Northern Boulevard, 215
Place, the lot-1 side line) and the 33.34 ft back clearance on the tax-map basis; the lot-coverage
maximum 100% corner / 80% interior by portion (ZR 23-362(a), ZR 12-10 corner-lot); the area
allocation 12,090 / 4,030 apartment and 8,060 / 2,686.67 other; front yard 0 (ZR 23-322), side yard
0 with a 5 ft open-area minimum (ZR 23-335(b)), no setback at 30 ft (30<=45); the rear yard NOT
KNOWN under Z1 (both carry settled short-block-rear-yard#real-lot-z1-rear-yard); the whole-lot
coverage NOT KNOWN as a single figure.

DIFFERENCES the orchestrator flagged (checked; recorded per-basis or NOT SETTLED, never merged):
1. Footprint share of the lot. Reading 1: 66.66% of the 10,076 sq ft tax rectangle. Reading 2:
   66.67% of the recorded 10,075 (filing_attribute) AND 66.66% of the 10,076 tax rectangle. On the
   same basis (the 10,076 tax rectangle) both give 66.66%. Recorded in `lot-coverage-whole-lot`
   (NOT SETTLED as a single whole-lot figure; the per-basis shares and both readings named).
2. Basis label for the mapped street widths. Reading 1 labels the 100/60 ft widths "gis /
   administrative"; reading 2 labels them "administrative_record". I did not record a street-width
   row (not in the mandated groups); the mapped widths enter only through the settled street-wall
   and bounding-street readings. Flagged here for completeness.
3. The GIS Northern Boulevard frontage. Reading 1: 103.88 ft. Reading 2: 103.879 ft. Equal to the
   hundredth (103.88). Recorded at 2 dp in `gis-conflict-check`, with the source_reference naming
   both readers' figures; the row is NOT SETTLED (the tax-map/GIS conflict is not resolved).
4. Coverage worked by portion in figures (reading 1) vs in words (reading 2). Both reach the same
   per-portion maxima and the same "not known as a single figure"; recorded as `lot-coverage-max`
   (value) + `lot-coverage-whole-lot` (not known).

CONDITIONS one reading holds: none that changes a recorded value. Both readings note the rear-yard
answer is conditional (basis + adjoining lot-line kind) and the street-wall mandate on the narrow
215 Place is conditional on a whole-frontage-commercial question that is not known; these conditions
are carried in `rear-yard` and in the settled street-wall reading, not forced into a value.

## MATERIAL DISCREPANCY to disclose (the packet's anticipated "33.32" south offset)

The packet (M5-T172 S13 and workorder finding 15) anticipates offsets "south 33.34 (tax map) / 33.32
(map outline)". **Neither reading produced 33.32.** Both readers give the back-wall (south) clearance
as **33.34 ft on the tax-map basis** and **35.31 ft on the city-map (GIS) basis** (the GIS plan depth
is 64.66 ft because the GIS frontage is longer, so 99.97 - 64.66 = 35.31). The case records 33.34
(tax map) and 35.31 (GIS), difference +1.97 ft, in `placement-tax-map` and `gis-conflict-check`; it
never records 33.32. A later task that expects 33.32 on the map-outline basis would be taking a value
the readings do not support. Left visible for the orchestrator; I did not invent 33.32 or reconcile
it.

## Map of point 5 - the values M5-T172 / M5-T173 take from this case

M5-T172 (illustrative placement + area allocation):
- S1 (dimensions = step P8, area +/-0.5): `footprint-tax-map` (100.76 x 66.66 = 6,716.66) and
  `plate` (6,716.67); the +/-0.5 reconciliation is in `footprint-tax-map`.
- S2 (coverage bound on the stated measure): `lot-coverage-max` gives the 80%/100% per-portion
  maxima; the engine's 0.80 x 10,075 = 8,060 lower bound uses the recorded lot area recorded in
  `lot-coverage-whole-lot` facts. The withheld whole-lot figure stays in `lot-coverage-whole-lot`.
- S3 (66.66 ft depth in the (b) band): `placement-tax-map` (within 100 ft of Northern Boulevard) +
  `rear-yard` (the (b) band reading; overall NOT KNOWN - the task's G0 fixes the withheld fallback).
- S6 / S13 (map outline 3.12 ft longer; offsets by basis): `gis-conflict-check` (+3.12 frontage;
  GIS back clearance 35.31) + `placement-tax-map` (tax-map back 33.34; west/lot-1 touch 0 on both).
  See the discrepancy section: the case gives 35.31 for the GIS south offset, not 33.32.
- S7 (no fit -> withheld; allocation still emitted): `area-allocation` is independent of the
  placement; `placement-tax-map` is explicitly an illustration.
- S14 (allocation = step P8): `area-allocation` (share 60%, measure = zoning floor area, 0.60 x
  20,150 = 12,090; per-storey x 3 = totals).
- S4 (street wall within 8 ft Conditional) and S5 (no setback, 30<=45) are rule triggers, not
  placement/allocation values; this case does not add a standalone street-wall or setback row (both
  are outside the seven mandated row groups). Both P8 readings worked them (Q1a, Q1e) and they rest
  on settled step-p6-worked#real-lot-street-wall; M5-T172 takes them from there. GAP noted: no
  standalone row here.
- S11 not_checked "physical floor plate": `physical-plate-not-checked` + the label on `plate` and
  `footprint-tax-map`.

M5-T173 (scenario sheet):
- S1 (drawn numbers = results geometry): from M5-T172, which derives from `footprint-tax-map` and
  `placement-tax-map`.
- S4 (rows sum to total) / schedule 6,717+6,717+6,716 = 20,150: supported by `plate` and
  `area-allocation` (the largest-remainder schedule is M5-T173's own rounding).
- S9 / S10 (area illustration, both states, share): `area-allocation` (12,090 / 8,060; 4,030 /
  2,686.67; 60%).
- S12 (footprint label carries the G-14 measure statement): the label on `plate` and
  `footprint-tax-map`.

## What stays NOT SETTLED, with the kind of each gap

- `physical-plate-not-checked` - KIND: a missing fact about the property (the gross-up factor,
  excluded areas and wall thicknesses, from an architectural floor plan).
- `gis-conflict-check` - KIND: a missing fact about the property (no survey or deed resolves the
  ~3.1 ft frontage / ~313 sq ft area conflict: 10,075 recorded / 10,076 tax rectangle / 10,387.99
  GIS).
- `lot-coverage-whole-lot` - KIND: a missing fact about the property (a surveyed outline; the
  conflicting lot areas; the governing lot area not fixed).
- `rear-yard` - KIND: unresolved law (the governing measurement basis) AND a missing fact about the
  property (the adjoining zoning lot's lot-line kind). No unconditional "no rear yard" recorded.

## Missing facts about the real lot (both readings)

No survey, deed or zoning-lot description for lot 70 or any neighbour (so the ZR 23-344(c) adjoining
lot-line kind is not known and Z1 is a stated condition, not a fact); the ~313 sq ft area conflict
(10,075 / 10,076 / 10,387.99); no ground elevations, base plane or curb level. Reading 1 also: the
whole-frontage-commercial question on 215 Place. Reading 2 also: the surveyed corner angle and the
block's south-west / ALLEY edge.

## Texts the readings name as not had

There is no text both readings say they did not have, so the joint "both readers did not have" list
is empty (`both-readers-did-not-have` row). Per reading: reading 2 names the "outer court"
definition, the Mandatory Inclusionary Housing / UAP terms and the New York City Administrative Code
as not in its folder (each not load-bearing here); reading 1 names no text as outside the folder and
marks ZR 23-341 / 23-343 / 23-434 as in the folder but not read by reading 1, taking the
prevailing-street-wall-frontage definition from the settled sheet. Wording follows the brief: "the
readers did not have" / "not read by reading N"; no "not captured" / "uncaptured" / "does not hold"
outside change-log entries (proved by the round2 and step-P8 wording scans).

## Older rows this case touches (point 7 - NOT edited; the packet forbids it)

- `step-p6-worked#real-building-b` (value): the step-P6 footprint placed Building B's plan at about
  103.9 ft along Northern Boulevard x about 64.66 ft deep = 6,716.67, three storeys, on the
  GIS/lot-depth basis, kept within the corner-lot portion. The new step-P8 rows `footprint-tax-map`
  and `placement-tax-map` work the same footprint on the stated printed-tax-map basis (A1), 100.76 x
  66.66 = 6,716.66, with the GIS outline as a conflict check (`gis-conflict-check`, GIS 103.88 x
  64.66 - consistent with step-P6's ~103.9 x 64.66). These are the same building on two outline
  bases, not a correction. PROPOSAL: leave real-building-b unchanged; if the orchestrator wants a
  cross-reference it could add one later, but no supersede is warranted - the step-P8 case states its
  basis (A1) and the conflict check explicitly, and the figures are consistent per basis.
- `corner-reach#real-lot-coverage` and `short-block-rear-yard#real-lot-z1-rear-yard` (both NOT
  KNOWN): this case leaves both NOT KNOWN too (`lot-coverage-whole-lot`, `rear-yard`); consistent,
  no change proposed.

## Checks (each run one at a time; direct exit code)

a. `python -m ruff check .` (from services/api): "All checks passed!" exit **0**.
b. `python -m pytest -q -p no:cacheprovider tests/rules/reference_cases tests/spatial/test_lot_reach.py
   tests/scenario/three_answers/test_result_way_bridge_overlay.py`: **163 passed** exit **0** (the
   claim head gave 118 in the reference_cases folder alone; the step-P8 tests and the two consumer
   tests bring the total to 163; the two consumer tests pass unchanged).
c. `python tests/rules/reference_cases/r6b_reference_cases_render.py --check`: "reference-case check
   PASSED (no issues)" exit **0**.
d. `python3 tools/modularity_check.py --check`: "failures 0; warnings 32" (all warnings pre-existing;
   none is a reference_cases file) exit **0**. `python3 scripts/lanes/check_lane_paths.py
   --coverage`: "LANE COVERAGE PASS: 10344 file(s)" exit **0**.
e. Five mutation proofs (in memory / a temp copy outside the repo), all PASS: (1) a changed law
   phrase makes `citation_errors` fail and names `placement-building-b/lot-coverage-max`; (2) a value
   on `gis-conflict-check` where the readings differ makes `must_stay_not_known_errors` fail; (3) a
   removed quantity basis makes `quantity_basis_errors` fail; (4) one byte flipped in a temp copy of
   provenance -17 makes its sha256 differ from the pinned digest; (5) the allocation apartment total
   changed by 1 (12,090.00 -> 12,091.00) makes `recompute_row_errors` fail and names
   `placement-building-b/area-allocation`. The same five are permanent tests in
   `test_r6b_reference_cases_step_p8.py`.

Support-file sizes (under the 600-SLOC focus cap): check.py 591, step_p8.py 196,
test_r6b_reference_cases_step_p8.py 331, lib.py 379.

Byte-stability: the 10 pre-existing non-short-block cases still hash to the prior step-P7 pin
`4285ac72...`, proving no existing case row changed; the step-P7 PRIOR_ROWS_DIGEST moved to
`2b9232078c6f90a36fe87b55a4493b8fce71dd7b7decfe028f5aecc6a482b4ee` only because
placement-building-b is now a prior case; the step-P8 OTHER_CASES_DIGEST
`9a77545ad3ff53d0049a6c0679935b974ee7f1b70a06ac79b19af0bc999e6f9c` pins all cases except the new one.

## Per-input-state test table (state | expected | test name) - in test_r6b_reference_cases_step_p8.py

- S1 readings present unchanged | digests pinned, markers, sealed folder, END-OF-REPORT, EIGHTEEN
  settled, real-building-b left out | test_the_two_step_p8_readings_are_present_unchanged
- S1 changed reading caught | "digest changed" | test_a_changed_step_p8_reading_is_caught
- case validates clean | no errors | test_step_p8_case_validates_clean
- S2 both readings named | -17 and -18 in every source_reference | test_step_p8_rows_name_both_readings
- S2 captured words | every citation matches the capture | test_every_step_p8_citation_matches_the_capture
- S2 changed law quote caught | names the row | test_a_changed_law_quote_in_a_step_p8_row_is_caught
- S3 not-settled stay not known | kind of gap present | test_step_p8_not_settled_rows_stay_not_known_with_a_kind_of_gap
- S3 value where readings differ refused | names gis-conflict-check | test_a_step_p8_value_where_the_readings_differ_is_refused
- S4 plate/footprint pinned | 6,716.67 / 6,716.66, recompute | test_the_plate_and_the_footprint_are_each_pinned_to_their_recompute
- S4 label present | plate_label_errors == [] | test_the_plate_and_footprint_carry_the_stated_measure_label
- S4 dropped label refused | names footprint-tax-map | test_a_figure_that_drops_the_stated_measure_label_is_refused
- S4 physical plate not checked | not_known | test_the_physical_floor_plate_is_not_checked
- S4 nine bases authoritative | equals QUANTITY_BASES | test_module_nine_bases_equal_the_authoritative_set
- S4 every quantity one basis | all in the nine | test_every_quantity_carries_one_of_the_nine_bases
- S4 missing basis refused | "no measurement basis" | test_a_quantity_without_a_basis_is_refused
- S4 basis outside nine refused | "not one of the nine" | test_a_quantity_with_a_basis_outside_the_nine_is_refused
- S5 allocation sums and recomputes | 12,090+8,060=20,150; 4,030+2,686.67=6,716.67 | test_the_area_allocation_sums_and_recomputes
- S5 apartment figure +1 caught | names area-allocation | test_a_changed_allocation_apartment_figure_is_caught
- S6 placement/coverage name basis+Z1 | placement_basis_errors == [] | test_placement_and_coverage_rows_name_basis_and_z1
- S6 placement row w/o basis or Z1 refused | names placement-tax-map | test_a_placement_row_without_its_basis_or_z1_is_refused
- S4 no program result | program_result_errors == [] | test_step_p8_program_result_errors_is_empty
- S7 wired in | CASE_IDS, REQUIRED_BASE_IDS, coverage, README | test_step_p8_case_is_wired_in
- S7 page byte-identical | render_page == page | test_step_p8_page_is_byte_identical_to_the_renderer
- S7 other cases byte-stable | OTHER_CASES_DIGEST | test_other_cases_rows_are_byte_stable
- S7 support files < 600 | all under 600 | test_support_files_stay_under_600_lines
- wording | no forbidden present-tense phrases | test_no_forbidden_present_tense_wording_in_the_step_p8_case

## Limitations / doubt

- Legal readings are drafts by AI helpers, not professionally reviewed; nothing is labelled verified.
- The packet's anticipated "33.32" map-outline south offset is not supported by the readings (35.31
  is); disclosed above for the orchestrator.
- No standalone street-wall or setback row (outside the seven mandated groups); M5-T172 S4/S5 take
  those from both P8 readings' Q1 and settled step-p6-worked#real-lot-street-wall.
- I did not run the full api suite (CI runs it on the pushed head); I ran the folders the brief named.
