# M4-T030 producer report - the independent reading of the law text captured by M4-T029, written into the R6B reference cases

Producer: rules-engineer (builder). Worktree: `/root/project/nyc-buildability/.claude/worktrees/agent-a3e8a895a04451dfa`.
Contract head reset to `d952c612a4ff147146c05c66105a9e021928cc71`; worktree clean before work.
Source of all new values: the two independent readings saved as `return-reading-P3-1.txt` and
`return-reading-P3-2.txt`, read in full. No program run was read or executed.

## Files written

New:
- `docs/reference-cases/R6B/provenance/return-independent-hand-calculation-7.md` (reading P3-1, byte-for-byte below a short header; sha256 `c0f09e913f4d274f3082553be50ee05cd3f42fb7ce42978d4373a88b381ae1c3`).
- `docs/reference-cases/R6B/provenance/return-independent-hand-calculation-8.md` (reading P3-2; sha256 `9c2b3d263e49a4396af922d5e709b1e051a95373029f775002a2920e96e8d10d`).
- `docs/reference-cases/R6B/cases/step-p3-worked.json` (new case, 21 rows) and `docs/reference-cases/R6B/step-p3-worked.md` (rendered).
- `services/api/tests/rules/reference_cases/r6b_reference_cases_step_p3.py` (new focused module, 102 lines: step-P3 reading digests, the "both readings do not settle -> not known" guard, and the "corner-coverage pins must not move" guard).

Changed:
- `services/api/tests/rules/reference_cases/r6b_reference_cases_lib.py` (CASE_IDS + REQUIRED_BASE_IDS for the new case).
- `services/api/tests/rules/reference_cases/r6b_reference_cases_check.py` (wire the new module: CASE_READINGS, label, provenance digest check, the two guards; a truthful comment fix on NOT_CAPTURED_SECTIONS).
- `services/api/tests/rules/reference_cases/test_r6b_reference_cases.py` (CASE_IDS assertion, NOT_KNOWN set, step-P3 tests).
- `docs/reference-cases/R6B/README.md` (new case row in the table; provenance sentence; a step-P3 subsection: what the new readers had and what they still did not have).
- `docs/reference-cases/R6B/cases/{step-p1-worked,corner-reach,real-lot,overlay-reading}.json` (the point-4 candidate rows below, plus a dated change-log entry each) and their rendered pages.
- `docs/reference-cases/R6B/{step-p1-worked,corner-reach,real-lot,overlay-reading}.md` (re-rendered).
- (render.py was NOT changed; the new case renders through the generic renderer.)

## New rows (case `step-p3-worked`, 21 rows) - kind recorded

| row_id | kind | summary of the recorded answer |
|---|---|---|
| real-lot-lot-lines | value | corner lot; two front lot lines (Northern Blvd, 215 Place), two side lot lines, no rear lot line |
| real-lot-lot-depth | value | about 103.9 ft (corner method: greater of ~99.98 and ~103.90) |
| real-lot-lot-width | not_known | side lot lines adjacent/~perpendicular; the lot-width method presupposes opposite lines |
| interior-40x100-lot-dimensions | value | lot width 40 ft; lot depth 100 ft |
| interior-40x100-rear-yard | value | 20 ft at/below 75 ft, 30 ft above; width 40 makes building type immaterial; not shallow |
| through-40x200-rear-yard-equivalent | value | rear yard equivalent 40 ft (<=75 ft)/60 ft (>75 ft), midway +/-10 ft; not exempt; standard lot; alt locations unavailable |
| real-lot-rear-yard-beyond-corner | not_known | within 100 ft no rear yard; beyond, a small deemed rear lot line; requirement needs neighbour/building facts |
| corner-150x100-rear-yard-beyond-corner | not_known | within 100 ft no rear yard; beyond, a 50-ft deemed rear lot line; requirement not settled |
| zr-23-436-paragraphs | value | only (c) binds (street wall along the wide Northern Blvd via 35-631); (a),(b),(d) do not apply; (e),(f),(g) conditional/not had |
| zr-35-633-paragraphs | value | (a) applies (23-431 superseded by 35-631); (b) not known (block-frontage extent not in the record) |
| zr-34-21-routing | value | 34-21 modifies nothing itself; routes to 34-22/34-23/34-24; readers did not have 34-22/34-23, so FAR and yards stay open |
| zr-34-111-governs | value | 34-111 governs C2-2 within R6B (bulk of surrounding R6B); 34-112 table does not reach C2-2 |
| manhattan-core | value | no: Queens is not within Manhattan Community Districts 1-8 |
| special-downtown-brooklyn-district | value | outside on the recorded facts; reading 8 holds this subject to Article X Ch 1 (not had), reading 7 treats it settled |
| height-measured-from-base-plane | value | from the base plane (ZR 23-43); the 23-432 table heights are measured from it |
| base-plane-real-lot | not_known | only planimetric inputs are in/derivable; every elevation/design input is not, so the elevation is not known |
| zr-23-434-eligible-sites | value | R6-R12 without a letter suffix meeting a paragraph-(a) criterion; does not reach suffixed R6B |
| zr-23-362b-eligible-sites | value | (b) applies only to lots utilizing 23-434, not every 30,000-sq-ft lot; does not reach the real lot |
| residence-residential-definition | value | residence = dwelling/rooming units + common spaces (excl. transient/hospital/dormitory); residential = pertaining to a residence |
| floor-area-share-bases | value | 23-232 base = the corridor's own floor space (settled); 23-231 base = "residential floor area" (named, not settled, term not had) |
| sections-and-facts-not-had | value | the agreed list both readings name (see below) |

## Point-4 candidate rows (examined row by row; decision + exactly what changed)

A value or kind changed in NONE of these rows: all stay exactly as they were. Each row I touched had its
"not captured"/"uncaptured" wording brought into "the readers did not have" form and a pointer to the
step-P3 reading added (both step-P3 readings support what was added), with a dated change-log entry
(reason: corrected evidence - the text is now captured and read).

- `step-p1-worked/interior-40x100-rear-yard` - stays not_known (readings 3 and 4 differed). does_not_establish reworded ("...definitions are not captured" -> "the step-P1 readers did not have..."), step-P3 result added (both P3 readings read 20 ft <=75 / 30 ft >75 at lot width 40). CHANGED: wording only.
- `step-p1-worked/through-40x200-rear-yard` - stays not_known (readings 3/4 lacked ZR 23-343). why_applies, reason, does_not_establish and source_reference reworded; step-P3 result added (both P3 readings read 40/60 ft midway +/-10 ft). CHANGED: wording only.
- `step-p1-worked/special-density-real-lot` - stays not_known (readings 3/4 lacked the boundary defs). reason + does_not_establish reworded to "the step-P1 readers did not have the geographic boundary definitions"; step-P3 result added (Manhattan Core not in it; SDBD outside on facts). CHANGED: wording only.
- `step-p1-worked/corner-150x100-rear-yard` - stays not_known. reason reworded ("...definitions are not captured" -> "the step-P1 readers also did not have..."); step-P3 150x100 corner reading added (50-ft deemed rear lot line, not known). CHANGED: wording only. (Edit scoped by the unique trailing source_reference, because this row's reason is byte-identical to corner-200x120-rear-yard's.)
- `corner-reach/real-lot-rear-yard` - stays not_known. reason + does_not_establish reworded; step-P3 result added. CHANGED: wording only.
- `real-lot/L12` - stays not_known. reason + does_not_establish reworded ("uncaptured ZR 12-10 lot-line definitions" -> "the ZR 12-10 lot-line definitions the earlier readers did not have"); step-P3 result added. CHANGED: wording only.
- `overlay-reading/section-35-633` - stays not_known (step-P2 readers 5/6 lacked 23-436 and differ on 35-633(b)). why_applies, reason, does_not_establish reworded ("Section 23-436 is not captured" -> "the step-P2 readers did not have Section 23-436"); step-P3 result added (both P3 readings: (c) binds, 35-633(a) applies, 35-633(b) not known). source_reference still names readings 5 and 6 (both-readings rule). CHANGED: wording only.

Rows examined and LEFT unchanged, with the reason:
- `corner-reach/C1-rear-yard` - the step-P3 readers worked a 150x100 corner lot, not a 40x100 corner lot, so there was nothing both readings support to add, and the row carries no "not captured" wording. Unchanged.
- `corner-reach/C3-rear-yard` - C3 is 150x100 and the step-P3 150x100 reading matches it, but the row already states the verdict correctly and carries no "not captured" wording; per "do not rewrite rows you do not otherwise change" it is left unchanged. The new 150x100 reading is recorded in the new case.
- `real-lot/L14` - carries no "not captured" wording (ZR 23-342 was captured at M4-T025) and stays not_known; the step-P3 readings keep it not known and additionally find the real lot's lot width itself not known (recorded in the new case's real-lot-lot-width row). Unchanged.

## The one point that must not move (point 4) - honoured

Both step-P3 readings say in passing in Q7c that "the standard coverage of ZR 23-362(a) for this corner
lot is 100 percent" without working the corner-lot-portion rule. These passing sentences are recorded as
what they are in the new case (row `zr-23-362b-eligible-sites`, does_not_establish, naming both sentences
and stating they are not a reading of whole-lot coverage), and NOWHERE as a value. `real-lot/L5`,
`corner-reach/real-lot-coverage`, and `step-p1-worked/corner-150x100-coverage` and
`step-p1-worked/corner-200x120-coverage` keep their not-known kind and value text exactly. A machine guard
(`r6b_reference_cases_step_p3.pinned_coverage_errors`) pins these four rows and is exercised by a test and
by mutation proof 2's companion.

## Where the two readings differ, or one holds an answer subject to something

- Special Downtown Brooklyn District (new row `special-downtown-brooklyn-district`): both readings reach
  "outside" on the recorded facts, but reading 8 (P3-2) holds the exclusion subject to a text the readers
  did not have (Article X, Chapter 1, the "DB" boundary), while reading 7 (P3-1) treats it as settled
  (that boundary is not needed to exclude a Queens lot with no special-district designation). Recorded as
  a value that states the condition and names which reading raised it, per the rule - the difference is
  not smoothed.
- No other step-P3 row has a genuine disagreement. The rows below are "both say not known" (not a
  disagreement), and stay not known: real-lot-lot-width, real-lot-rear-yard-beyond-corner,
  corner-150x100-rear-yard-beyond-corner, base-plane-real-lot.
- Shared caveats recorded in does_not_establish (both readings raise, not a disagreement): the through-lot
  "large sites"/block-occupying exemptions (undefined/absent); ZR 23-436 (e)/(f)/(g) conditional on height,
  Historic-District fact (not had) and sidewalk-widening design choice; the ZR 34-22/34-23 absence leaving
  the overlay's floor-area and yard modifications open.

## What stays not known (and why)

real-lot lot width (side lot lines not opposite); real-lot and corner-150x100 rear yard beyond the corner
(neighbour lot-line type, building type/height, and overlay 34-23 not available); the base-plane
elevation (curb level, grade, etc. not had); ZR 35-633(b) (block-frontage extent not in the record);
and, carried from the existing cases, the step-p1/overlay/real-lot/corner-reach candidate rows above.

## Checks (direct exit codes; run from services/api with the lanes venv, PYTHONDONTWRITEBYTECODE=1, pytest -p no:cacheprovider)

- (a) `python -m ruff check .` -> `All checks passed!`; exit 0.
- (b) `python -m pytest -q -p no:cacheprovider tests/rules/reference_cases` -> `49 passed`; exit 0.
- (c) renderer check mode (`r6b_reference_cases_render.py --check`) -> `reference-case check PASSED (no issues)`; exit 0.
- (d) `python3 tools/modularity_check.py --check` -> `selected 716 files; failures 0; warnings 29` (all 29 warnings are pre-existing files, none mine); exit 0. `python3 scripts/lanes/check_lane_paths.py --coverage` -> `LANE COVERAGE PASS: 9013 file(s)`; exit 0.
- (e) Two mutation proofs on in-memory copies (scratchpad script, outside the repo), exit 0:
  - MUT1: changed one quoted law phrase in `step-p3-worked/manhattan-core` -> citation check fails:
    `step-p3-worked/manhattan-core: the quoted words for 12-10 are not found in the capture zr-12-10-manhattan-core` (row named). PASS.
  - MUT2: forced a value on `step-p3-worked/real-lot-lot-width` (a row the two readings do not jointly settle) -> refused:
    `step-p3-worked/real-lot-lot-width: the two step-P3 readings do not jointly settle this, so it must be 'not known', not 'value'`. PASS.
  - BONUS (literal "two readings differ"): forced a value on the existing differ row `overlay-reading/section-35-633` -> refused by `readings_differ_errors` (already covered by `test_an_overlay_value_where_the_readings_differ_is_refused`). PASS.
  - (The orchestrator runs the FULL `services/api` pytest once at the wave's final candidate; I did not.)

## Scope

`git status --porcelain` lists only allowed paths: `docs/reference-cases/R6B/**` (README, cases/*.json,
*.md pages, provenance/*.md) and `services/api/tests/rules/reference_cases/**` (lib, check, test, new
module), plus this report. No forbidden path touched. No capture, rule file, engine, register, plan,
helper file, other test or dependency file changed.

## Disclosed residual (DB-170 wording in NON-candidate rows - OUT OF MY SCOPE per point 5)

Task M4-T029 captured text that makes several PRE-EXISTING "not captured"/"uncaptured"/"repository does
not hold" statements stale. Point 4 scoped my candidate rows, and point 5 says "do not rewrite rows you
do not otherwise change", so I left these untouched and disclose them for the orchestrator to route a
follow-up if wanted. Verified against the repo: of the sections these rows call "not captured", only
34-22 and 34-23 are still genuinely uncaptured; 23-343, 23-434, 23-435, 23-436, 23-41, 34-21, 35-64,
35-71 and 36-64 are now captured.
- `overlay-reading.json` case-level `what_it_is_worth` says "a section the repository does not hold" (the
  single most-forbidden phrasing) and `what_it_does_not_establish` names 23-436 as an "uncaptured section".
- `overlay-reading.json` non-candidate rows (floor-area-ratio, lot-coverage, base-and-building-height,
  street-wall-location, rear-yard, paragraphs-applicable, and the `not-captured` row) repeatedly say
  "uncaptured ZR 34-21 through 34-23" (34-21 is now captured), "the uncaptured Section 36-64", "Section
  23-434/23-435/23-436 ... not captured", etc.
- `step-p1-worked.json` non-candidate rows `corner-200x120-rear-yard` (reason) and `through-40x200-coverage`
  (does_not_establish) still say "...definitions are not captured" and "...ZR 23-343, not captured".
- Pre-existing change-log entries (M4-T027/M4-T028) that historically describe a "not-captured -> captured"
  citation transition are left as-is (they are immutable history, not row content).

## Assumptions / limitations

- The step-P3 made-up lots (interior 40x100, through 40x200, corner 150x100) match the existing cases'
  examples; the real lot's geometry uses the approximate tax-map outline, as the readings state.
- I resolved no disagreement and added no reading of my own; every new value rests on both readings
  agreeing on the same basis, and every "not known" names both readings.

Requested status: awaiting_gate.

END-OF-REPORT
