# M5-T176 producer report (step P7: the two independent readings of ZR 23-344(b) and (c)(3))

I am an AI agent (role rules-engineer), the producer for M5-T176. I wrote files and made one
commit in my own worktree; I did not review, accept, push, or touch the ledger.

Worktree: `/root/project/nyc-buildability/.claude/worktrees/agent-aa482240a2dfbebfe`
Claim head reset to: `8f713e6a6312a1cdcb6ae5eb941c2bd4e3a887db` (task/wave24-report-v3).

## What was built

One new reference case `short-block-rear-yard` (35 rows) written from the two independent step-P7
readings (saved unchanged as provenance -15 and -16), with its rendered page, the README updates,
and the step-P7 support module + test. Every law quote is a verified exact substring of its capture
(`docs/research/zr-snapshots/v1/`), pinned by `content_digest_sha256`. No value comes from a program
run; no unconditional "no rear yard" is recorded for the real lot; no human verdict is entered.

### Rows added (35)

b-group (6): b-what-measured [value], b-measurement-basis [not known], b-less-than-230 [value],
b-within-100-feet [not known], b-exact-100-ft [not known], b-block-boundary [value].
c-group (4): c-which-lots [value], c-becomes-rear-lot-line [value], c-from-which-street-line [value],
c-1-vs-c-3 [value, with reading 2's R6B-suffix condition recorded].
fit-group (4): fit-sections [value], fit-multiple-apply [value], fit-b-on-corner-lot [value],
fit-b-c-overlap [not known].
Made-up (10): M1 [yes], M2 [no], M3 [no], M4 [not known], M5 [yes + exact-100 caveat], M6 [rear yard
required beyond the band], M7 [yes via P; (c) neighbour not known], M8 [yes; internal line not a lot
line; (c) neighbour not known], M9 [yes; park bounds block], M10 [not known].
Real lot (8): real-lot-bounding-streets [value], real-lot-alley [not known], real-lot-short-dimension
[not known], real-lot-front-lot-line [value, settled [S]], real-lot-reach [value, settled [S]],
real-lot-z1-rear-yard [not known], real-lot-z2-rear-yard [not known], real-lot-beyond-100-sliver
[not known].
Catalogue/map (3): real-lot-missing-facts [value], both-readers-did-not-have [value],
m5-t167-scenario-map [value].

## Point-by-point comparison of the two readings

Agree (recorded as value / yes-no): what 23-344(b) measures (the dimension between any two streets
bounding the block, itself a block frontage); "less than 230 feet" is strict (M1 229.99 yes, M2
230.00 no, M3 230.01 no); a public park can bound a block and a private way cannot; (c) scope, the
deemed rear lot line, the intersecting street line, and that (c)(1)/(c)(3) turn on the adjoining lot's
lot-line kind plus the subject's own district (not the neighbour's district); the sections fit as
modifications of 23-342/23-343; more than one modification can apply; (b) is not barred on a corner
lot; M5/M6/M7/M8/M9 (b)-applicability; lot 70 corner with two front lot lines and no rear lot line [S];
the GIS-outline reach (99.97 / 103.93 / 144.60 ft) [S].

Differ or one holds a condition (recorded NOT SETTLED / with the condition named):
- Centreline side-street separation: reading 1 = 260.02 ft, reading 2 = about 261.0 ft (differ ~1 ft,
  both > 230) -> real-lot-short-dimension stays NOT SETTLED (both figures kept; no single figure).
- R6B within "R6 through R12" for (c)(3): reading 2 holds this subject to a district-suffix text
  (such as ZR 11-25) it did not have and flags it; reading 1 reads R6B as within R6-R12 without the
  caveat. Recorded as a value with the condition named (c-1-vs-c-3; also in the real-lot rows and the
  scenario map), per the rule of agreement.
- Outside-folder texts named: reading 1 names a missing "block frontage"/"frontage" definition;
  reading 2 names a missing general "lot line" definition, ZR 23-38, ZR 23-72, the full ZR 34-23, and
  the R6B-suffix rule. The ZR 12-10 "street setback line" definition was in the folder: reading 2 read
  it, reading 1 did not read it (recorded as "not read by reading 1", never "not captured").
- Both agree on the per-basis short-dimension result but the governing basis is unresolved law; both
  agree the exact-100-ft edge, the "within 100 feet" method and the non-parallel-block method are not
  fixed; both agree the (b)/(c) overlap has no priority rule. All kept NOT SETTLED.

## What stays NOT SETTLED, with its kind of gap

- b-measurement-basis, b-within-100-feet, b-exact-100-ft, fit-b-c-overlap, M10 - unresolved law
  (the captured text does not fix the basis / method / exact-100 edge / overlap priority / the method
  for non-parallel streets).
- M4 - a missing fact about the property (an authoritative survey dimension) AND unresolved law (a
  source-fixing rule).
- real-lot-short-dimension - unresolved law (the basis) AND a missing fact (an authoritative
  side-street separation: a survey / certified street-line record); the two readings' centreline
  figures also differ.
- real-lot-alley - a missing fact about the property (the ALLEY's status and the SW-end feature, from
  the City Map).
- real-lot-z1-rear-yard, real-lot-z2-rear-yard - unresolved law (the basis) AND missing facts (the
  adjoining zoning lot's lot-line kind; whether lots 70 and 1 are one zoning lot).
- real-lot-beyond-100-sliver - a missing fact (the adjoining lot's lot-line kind) AND unresolved law
  (the (b)/(c) overlap).

## Missing facts about the real lot, with the variant each selects

1. Authoritative measurement basis (survey / certified street-line record) -> selects whether the
   Northern Boulevard frontage is a short dimension (so whether 23-344(b) applies).
2. Whether lots 70 and 1 are one zoning lot (Z1 vs Z2; zoning-lot description / deed / Declaration) ->
   selects which zoning lot 23-344(b) reads.
3. The zoning and lot-line kind of the other lots on the block (neighbouring lots' records) ->
   selects 23-344(c)(1) against (c)(3) on the beyond-100-ft strip.
4. The ALLEY's status and the SW-end bounding feature (the City Map) -> selects the far-end block
   boundary.

## Texts the readings name as not had (section; pointing words; the answer that waits on it)

- "block frontage"/"frontage" (reading 1) - used in the short-dimension definition - leaves exactly
  what a frontage is partly open.
- General "lot line" definition (reading 2) - the front/rear/side definitions build on it - the base
  lot-line test is under-sourced (the readers used the front/rear/side captures directly).
- ZR 23-38, ZR 23-72 (reading 2) - the 23-344 note points to further interactions - could add further
  modifications.
- Full ZR 34-23 (reading 2) - the C2-2 overlay rear-yard conclusion stays conditional.
- District-suffix rule (such as ZR 11-25) (reading 2) - "R6 through R12 Districts" - whether R6B counts
  within R6-R12 for (c)(3).
- The ZR 12-10 "street setback line" was in the folder and read by reading 2 (supersedes the street
  line for yards, but only in Staten Island or Queens Community District 10); not read by reading 1.

## M5-T167 S1-S12 map (also in the case row m5-t167-scenario-map)

- S1 -> b-less-than-230, M1, M2, M3.
- S2 -> b-measurement-basis, M4, real-lot-short-dimension.
- S3 -> b-within-100-feet, b-exact-100-ft, M5, M6, real-lot-beyond-100-sliver.
- S4 -> real-lot-reach, real-lot-z1-rear-yard (step-P7 carries 99.97 ft GIS and 100 ft tax-map; the
  ~101.06 ft derived value is an earlier reading's, not a step-P7 value, so the within/beyond-100 edge
  stays not settled).
- S5 -> c-which-lots, M7, M8 (long frontage not short), the real lot's long direction (~545 ft).
- S6 -> fit-b-on-corner-lot, M7, M8, real-lot-short-dimension.
- S7 -> M8, real-lot-z2-rear-yard.
- S8 -> b-block-boundary, M9, real-lot-alley, real-lot-bounding-streets.
- S9 -> M10, b-measurement-basis.
- S10 -> c-1-vs-c-3 and the R6B-within-"R6 through R12" condition (ZR 11-25 not had).
- S11 -> fit-multiple-apply, fit-b-c-overlap, c-1-vs-c-3.
- S12 -> the quantity-basis rule and real-lot-short-dimension (no two bases mixed).

## Older rows this case touches (point 7; NO edit made - for the orchestrator)

These existing rows hold the rear-yard question this case now reads more fully. The packet forbids
editing them; I propose NO edit and flag them for the orchestrator's judgment. All remain not-settled,
so this case does not contradict them; the orchestrator may decide whether any `superseded_by`
cross-reference is warranted (I do not add one).

- `step-p3-worked#real-lot-rear-yard-beyond-corner` (old: not known, from the P3 readings) - new rows:
  real-lot-beyond-100-sliver, real-lot-z1/z2-rear-yard. Proposal: leave as-is (both not settled; same
  missing fact).
- `step-p5-worked#benchmark-rear-yard-23-342-23-344` (old: not known; P5 readings differed on the
  far-edge reach) - new rows: real-lot-z1/z2-rear-yard, real-lot-beyond-100-sliver. Proposal: leave as-is.
- `step-p6-worked#real-lot-rear-yard-variants` (old: not known; missing adjoining lot-line types) -
  new rows: real-lot-beyond-100-sliver, real-lot-z1/z2-rear-yard. Proposal: leave as-is.
- `real-lot#L12` and `corner-reach#real-lot-rear-yard` are already superseded (step P3); untouched.

## REQUIRED out-of-scope seam for the orchestrator (one line, forbidden path)

Adding the case id to `CASE_IDS` (required by the packet) reddens the brittle hardcoded tuple at
`services/api/tests/rules/reference_cases/test_r6b_reference_cases.py:45`
(`assert lib.CASE_IDS == (...10-tuple...)`). That file is outside this packet's allowed paths. The fix
is to append `"short-block-rear-yard"` as the 11th element. This is the ONLY reference-case test
failure caused by this change; all 136 other tests in the focused suite pass. Routed to the
orchestrator per the consumer-sweep rule; I did not edit the file.

## Checks (direct exit codes)

- a. `python -m ruff check .` (from services/api): PASS, exit 0.
- b. `python -m pytest -q -p no:cacheprovider tests/rules/reference_cases tests/spatial/test_lot_reach.py tests/scenario/three_answers/test_result_way_bridge_overlay.py`:
  1 failed, 136 passed, exit 1. The single failure is `test_r6b_reference_cases.py::test_each_case_has_a_data_file_and_a_page` (line 45 brittle tuple; see the seam above). The two loader-consuming tests (test_lot_reach.py, test_result_way_bridge_overlay.py) PASS unchanged; all 19 step-P7 tests PASS.
- b'. `python -m pytest -q -p no:cacheprovider tests/rules/reference_cases/test_r6b_reference_cases_step_p7.py`: 19 passed, exit 0.
- c. `python tests/rules/reference_cases/r6b_reference_cases_render.py --check`: PASSED (no issues), exit 0.
- d. `python3 tools/modularity_check.py --check`: failures 0 (warnings pre-existing, none mine), exit 0.
     `python3 scripts/lanes/check_lane_paths.py --coverage`: LANE COVERAGE PASS, exit 0.
- e. Mutation proofs on temp copies outside the repo (/tmp/claude-0/M5-T176/mutation_proofs.py): all
     four FAIL-AS-EXPECTED and name the row - (1) a changed law quote fails the citation check naming
     b-less-than-230; (2) a value where the readings differ fails naming real-lot-short-dimension; (3) a
     quantity's basis removed fails naming real-lot-reach; (4) an unconditional "no rear yard" in a
     real-lot row fails naming real-lot-z2-rear-yard. The committed file is clean through every guard.

## Research and verification (D-093)

Read NB-03 and NB-04 (read only; not edited) and the primary captures the readings quote. The real lot's
reach-vs-100-ft is kept basis-dependent and not settled (NB-03 gap (a): 100 ft printed_tax_map / 99.97 ft
gis straddle the line); the short-dimension basis is kept unresolved (NB-03 gap (b)/(d)); the ALLEY is
kept not settled (NB-03 gap (c)); the neighbour lot-line kinds are kept missing (NB-03 gap (e)). No
value is sourced from NB-03/NB-04's own figures beyond what the two step-P7 readings give; the ~101.06 ft
derived figure (an earlier reading) is explicitly noted as outside the step-P7 readings.

## Files written (LF sha256; `tr -d '\r' < f | sha256sum`)

(computed and listed in the return to the orchestrator)
