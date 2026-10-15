# M5-T184 producer report - benchmark-options-2-3-6-7 reference case

I am an AI agent (producer, role rules-engineer). I wrote files in an isolated worktree
and made one commit. I did not review, accept, push or touch the ledger.

Worktree: `/root/project/nyc-buildability/.claude/worktrees/wf_4772a445-caa-2`
Branch/claim head reset to: `b2bb6991e7c14a022eeb1e52f47130674cd992f6`.

## What this case is

One new R6B reference case, `benchmark-options-2-3-6-7`: the agreed worked values of
option 2 (qualifying affordable housing, incl. UAP), option 3 (qualifying senior
housing), option 6 (residences with a community facility) and option 7 (a community
facility alone) for the benchmark lot (215-16 Northern Boulevard, lot 70 of block 7334;
R6B + C2-2; corner; recorded lot area 10,075 sq ft, administrative_record). Two
independent readings per option (-19/-20, -21/-22, -23/-24) and one independent comparer
(-25). A value is recorded only where both readings of that option agree on the same
value and the same basis, confirmed by the comparer, and the cited section is captured in
`docs/research/zr-snapshots/v1`. 44 rows: 35 value rows, 9 not-known rows (after the
round-2 correction below moved opt67-cf-max-footprint to not known).

## The readers' method, stated truthfully

Each reader had READ access to a detached read-only checkout of the repo at `bb5c02b9`
(the law captures, the settled reference cases, the evidence records, the law library),
read no program output (no test run, API call, report print or benchmark fixture), and
some read official ZR pages live; each reader B was also told not to read any `return-`
file; the comparer read both readings and opened captures and official pages. The
provenance headers say exactly this and never call the set a "sealed folder" in the
P7/P8 sense and never claim "no outside access". The checker's literal phrase "sealed
folder" is supplied in each header as a name for that pinned read-only capture set.

## Rows (44) and which stay NOT SETTLED (9 not_known after round 2)

Option 2 (-19/-20): opt2-max-residential-fa 24,180 sq ft (2.40x10,075, 23-22);
opt2-uap-affordable-fa 4,030 sq ft (0.40x10,075, 27-111); opt2-heights 30/45/65 (23-432);
opt2-max-dwelling-units 35 (24,180/680=35.56->35, 23-52(b), matches settled real-lot L7);
opt2-setback-above-base 10/15 (23-433); opt2-rear-yard none within 100 ft of corner,
beyond not known (23-344(a)); **opt2-lot-coverage NK**; **opt2-affordable-share NK**;
**opt2-mih-area-membership NK**; opt2-vs-option-1 (+4,030 FA / +10 ft / +6 DU).

Option 3 (-21/-22): opt3-max-residential-fa 24,180 (23-22); opt3-heights 30/45/65
(23-432); opt3-dwelling-unit-factor none (23-52(a)(2)); **opt3-max-dwelling-units NK**;
opt3-airs-accessory-space >=4% of total FA (12-10 AIRS); opt3-senior-definitions AIRS/LTCF
(12-10); opt3-setback-above-base 10/15 (23-433); opt3-side-yard none/>=5 ft (23-335);
opt3-vs-option-1 (+4,030 FA / +10 ft / 680 factor removed).

Options 6/7 (-23/-24): opt6-cf-far 2.00 (24-11); opt6-cf-max-fa 20,150 (2.00x10,075,
24-11); opt6-combined-cap 2.00 greatest single use, ->2.40 if residential qualifies
(24-161); opt6-combined-max-fa 20,150 (24-161); **opt6-dwelling-units NK (bounded <=29)**;
opt7-dwelling-units 0; opt67-cf-lot-coverage corner 80 agreed, interior/through rate NOT
SETTLED (24-11); **opt67-cf-max-footprint NK** (whole-lot footprint not settled; the corner
and beyond-100-ft portion areas are a missing property fact; round 2); opt67-mixed-level-coverage
higher-use (24-163); opt67-heights
30/45/55 (24-04(b)(1)->23-432); opt67-setback-above-base 10/15 (23-433); opt67-cf-front-yard
none (24-34); opt67-cf-side-yard none/>=8 ft (24-35(b)); opt67-cf-rear-yard 30 ft (24-36);
opt67-corner-rear-yard-waiver no rear yard within 100 ft of a <=135-degree corner (24-391);
opt67-cf-rear-yard-obstruction 1-storey <=23 ft (24-33(b)(2)); opt67-no-fa-gain (24-162
excepts R6B; 35-33 un-suffixed only); opt67-24-162-not-applicable; opt67-35-33-not-applicable;
opt67-use-group-iii (22-13/32-131); **opt67-which-uses-not-known NK**; **opt67-street-wall NK**.

Shared: both-readers-did-not-have (names 23-154, 23-63, 74-902/74-903, 22-131..135 in prose
only, confirmed by comparer -25); **real-lot-missing-facts NK** (zoning lot NB-01, lot-area
basis NB-04, eligibility); options-out-of-scope (5, 8, 9-10 owed, await M3-T010).

Kind of each NK gap: opt2-lot-coverage / opt3-max-dwelling-units / opt67-which-uses /
opt67-street-wall = unresolved law; opt2-affordable-share / opt2-mih-area-membership /
opt6-dwelling-units = a missing fact about the property (pathway / Appendix F membership /
the design split); real-lot-missing-facts = missing property facts (zoning lot, lot-area
basis) and unresolved law / agency determination (eligibility).

## Per-option point-by-point comparison (where the readings differ)

- Option 2: -19 and -20 agree on every headline value (24,180; 4,030; 30/45/65; 35;
  10/15; rear yard) and both leave lot coverage / affordable share / MIH membership not a
  single figure. No material disagreement; comparer -25 confirmed each number. (-20 adds
  the MIH mandatory-share table 27-131 only-if-in-an-MIH-area; recorded as conditional and
  the MIH membership kept NK, since UAP is the assumed route.)
- Option 3: -21 and -22 agree on 24,180 / 30/45/65 / no-factor / 4% AIRS / definitions /
  setback / side yard. They DIFFER on the senior unit count: -21 "no numeric limit (no
  factor)"; -22 "not known - another rule may govern". Per the comparer, kept NOT SETTLED
  (opt3-max-dwelling-units): no captured provision caps no-factor senior units. No winner
  picked; no reading of my own added.
- Options 6/7: -23 and -24 agree on CF FAR 2.00 / 20,150, corner lot coverage 80 (the
  interior/through rate is NOT settled across both readings - see round 2 below - and the
  whole-lot footprint is NOT settled), combined 2.00,
  30/45/55, the yards, corner waiver, obstruction, no FA gain, UG III, opt7 DU 0, opt6 DU
  <=29. They DIFFER on (a) the "null table" claim - -24 said zr-24-11/33-121 are null; the
  comparer resolved the numbers ARE captured under the plural `tables` key (-24 read the
  singular `table` key and misread it); no number affected, recorded as operands with the
  enabling sentence quoted and table_assertion:null (Risk 2). (b) CF-only street-wall
  routing - -24 cites 23-431, the residential/overlay route is 35-631(b); kept NOT SETTLED
  (opt67-street-wall). (c) which specific UG III uses - both name 22-131..135 as a text
  they did not have; kept NOT SETTLED (opt67-which-uses-not-known). The comparer's Appendix-F
  / 24-11 / 24-161 resolutions are recorded as its check against the text, not as a third
  reading's value.

## Missing facts about the real lot

Zoning lot (NB-01; a 2022 ZONE/CERT/DECL indexed against lots 1 and 70, instruments
unread; every figure conditional on Z1 = lot 70 alone); lot-area basis (NB-04; recorded
10,075 vs GIS 10,387.99, ~3.1%, every figure on the recorded 10,075, the two bases never
mixed); eligibility (affordable / senior qualification, MIH-area membership, CF use
permission - legal / agency determinations not made here).

## Older rows this case answers (NOT edited; the packet forbids editing other case files)

- settled real-lot `L2` (24,180), `L4` (30/45/65) and `L7` (35 DU, reviewer-ruled
  M4-T024) are the option-2 qualifying figures; opt2-max-residential-fa / opt2-heights /
  opt2-max-dwelling-units MATCH them (agreement, not a supersession). No proposal to edit.
- settled real-lot `L1`/`L3`/`L6` (20,150 / 30-45-55 / 29) are the option-1 baseline this
  case cites for the opt2/opt3/opt67 comparisons. No proposal to edit.
- No older row is contradicted or superseded.

## Consumer pins moved and why

- `test_r6b_reference_cases.py` literal CASE_IDS tuple: appended `benchmark-options-2-3-6-7`.
- `test_r6b_reference_cases_step_p7.py` PRIOR_ROWS_DIGEST: `2b923207...` -> `89dabbf0...`
  (the new case joins the "all cases except short-block-rear-yard" blob; no existing case's
  rows changed).
- `test_r6b_reference_cases_step_p8.py` OTHER_CASES_DIGEST: `9a77545a...` -> `106d76df...`
  (the new case joins the "all cases except placement-building-b" blob).
- `step_p6` REACH_ROWS_DIGEST NOT moved (it hashes only corner-reach's reach rows).
- Byte-stability of the 12 pre-existing cases proved in `test_r6b_reference_cases_step_p9.py`
  (`PRIOR_CASES_DIGEST` = `f5e61b1a...`, "all cases except the new one"). Only the new
  `.md` page changed under `--write`; the other 12 pages stayed byte-identical.

## Thin wiring (Risk 1)

`r6b_reference_cases_check.py` grew by exactly 3 lines (1 import + 1 call in
`provenance_errors` + 1 call in `validate_case`) and is 594 lines (< 600). All step-P9
per-row/per-case guards sit behind `step_p9.case_errors` and the reading guard behind
`step_p9.reading_digest_errors` (distinct name; no collision with check.py's top-level
`provenance_errors`). `r6b_reference_cases_step_p9.py` is 387 lines (< 600);
`r6b_reference_cases_render.py` is byte-identical (unedited; in allowed_paths as safety only).

## Checks (one at a time, direct exit codes)

- a. `python -m ruff check .` (from services/api): **exit 0** - All checks passed.
- b. `flock .../heavy-run.lock python -m pytest -q -p no:cacheprovider tests/rules/reference_cases
  tests/spatial/test_lot_reach.py tests/scenario/three_answers/test_result_way_bridge_overlay.py`:
  **exit 0** - 195 passed.
- c. `python tests/rules/reference_cases/r6b_reference_cases_render.py --check`: **exit 0** -
  reference-case check PASSED (no issues).
- d. `python3 tools/modularity_check.py --check`: **exit 0** (only pre-existing warn signals,
  none in the files I touched). `python3 scripts/lanes/check_lane_paths.py --coverage`:
  **exit 0** - LANE COVERAGE PASS: 10544 files, each owned by exactly one lane.
- e. Mutation proofs in a throwaway copy outside the repo (`/tmp/claude-0/M5-T184/mut`):
  **exit 0** - baseline clean (0 issues); each of the five mutations caught and named its
  row, and the checker returned clean after every restore:
  (1) a quoted phrase changed -> "the quoted words for 24-11 are not found in the capture";
  (2) a value where the readings differ (opt67-street-wall) -> "must be 'not known', not 'value'";
  (3) a basis removed -> "carries no measurement basis";
  (4) one arithmetic figure +1 (24,180->24,181) -> "recomputes to 24180.00 but the case records 24181";
  (5) a provenance byte changed -> "digest changed".

Not run (the independent check after me runs them): the full api pytest suite. No server
started; ports 3000/3001/8000 untouched; no Playwright.

## Doubt / limitations I disclose

- The 24-11 R6B contextual row (2.00 / 80 / 60 for FAR / corner / interior-or-through)
  lives in the capture's plural `tables` key, which the checker's singular `table_assertion`
  cannot read; the FAR 2.00 and the corner coverage 80 are recorded (the FAR as arithmetic
  operands, the corner coverage as a settled quantity) plus a verbatim quote of the enabling
  sentence, with `table_assertion: null`, and need a reviewer to eyeball 2.00/80/60 against
  the snapshot's R6B contextual `tables` row (Risk 2). The interior/through 60 is NOT recorded
  as a settled rate (round 2: reading B gives only the corner in its worked reading); the
  capture cell may still be quoted as the law. 23-22 and 23-432 (options 2/3) use the singular
  `table`, so their R6B rows ARE pinned by `table_assertion` (verified in tests).
- `captured_on`/`last_amended`/`date_read`/`status_note` are left empty on the captured
  citations (the checker neither requires nor renders them for a captured citation); the
  load-bearing fields (snapshot_id, snapshot_file, content_digest, official_url, quote) are
  all pinned and verified against the live captures.
- One reading (-22, reader B of option 3) recorded that it read a repository source file
  (`services/api/app/drawings/report/options.py`) and no program output; reading a source
  file is within the detached-checkout read access the readers were given and is not program
  output, so it is disclosed here but did not feed any value (the reading states it needed no
  program output and no live ZR site).
- Agreement of two (or three) AI readings is not proof; this is an ADR-007 draft reading,
  not professionally reviewed, and decides no eligibility.

## Round 2 - correction to the two community-facility lot-coverage rows

Round 2 runs in a different isolated worktree
(`/root/project/nyc-buildability/.claude/worktrees/wf_a9df234b-e81-2`), on the rebased
round-1 commit (cherry-picked onto the current branch head) plus one new commit. It is one
small, exact correction from an independent pre-integration check (two REQUIRED findings).

The two findings (both on options 6/7 lot coverage):
- Rule-of-agreement / attribution: the case recorded the interior/through lot coverage
  (60 percent) and the interior footprint (6,045 sq ft) as settled and attributed both to
  reading B (-24). Checked against reading B directly: its worked table gives only the corner
  portion (coverage 80, footprint 8,060); 60 percent and 6,045 appear only in reading A (-23)
  and in reading B's conflicts note, where -24 quotes the 24-11 capture row "2.00 / 80 / 60"
  as the law, not as an interior worked value. The comparer (-25) confirms corner 80 /
  interior 60 against the 24-11 capture but is an adjudicator, not a value source. (The capture
  itself reads R6B = 2.00 / 80 / 60; verified in `zr-24-11.snapshot.json` `tables`.)
- Return claim: the round-1 hand-back said 6,045 agrees across both readings. It does not;
  only reading A gives it. Corrected here and in the row/README/page.

What changed:
- opt67-cf-lot-coverage now records only the agreed corner 80 percent (basis: law). The
  interior/through 60 percent is recorded as NOT SETTLED on both readings' words - reading A
  gives it, reading B gives only the corner and quotes the capture cell as the law, the
  comparer confirms the capture but is not a value source; the capture cell is quotable as the
  law, and what would settle the rate is reading B applying it. The interior quantity was
  removed.
- opt67-cf-max-footprint becomes NOT KNOWN. Neither 8,060 (0.80 x whole lot) nor 6,045
  (0.60 x whole lot) is a whole-lot maximum footprint: each multiplies the WHOLE recorded lot
  area by one portion's rate, while the lot spans a corner portion (within 100 ft of each
  street line) and a strip beyond the 100-ft corner reach (the settled residential reading
  real-lot.json records the 23-362 coverage on this lot by portion, the lot reaching about
  103.9 ft from the 215 Place line). KIND OF GAP: a missing fact about the property - the two
  portion areas. The arithmetic (8,060 / 6,045) and both derived footprint quantities were
  removed; 6,045 no longer appears as a settled value anywhere (rows, README, page, this
  report's headline list). It is added to `step_p9.MUST_STAY_NOT_KNOWN`.
- A new guard `step_p9.portion_footprint_errors` refuses a settled footprint of 6,045 or
  8,060 and an arithmetic step that multiplies the whole lot area by a portion coverage rate.
  Two new mutation proofs exercise it (a settled row giving 6,045; a whole-lot footprint from
  a portion rate). The P9 arithmetic-recompute test dropped the two footprint rows.
- Consumer digests: `test_r6b_reference_cases_step_p7.py` PRIOR_ROWS_DIGEST and
  `test_r6b_reference_cases_step_p8.py` OTHER_CASES_DIGEST both include the benchmark case in
  their "prior"/"other" blob, so changing its rows moved both; recomputed to
  `bc45ce90...` (P7) and `8af6b2d4...` (P8). P9 PRIOR_CASES_DIGEST (all cases except the
  benchmark) is UNCHANGED (`f5e61b1a...`), proving every other case stayed byte-identical.
  The benchmark page was re-rendered under `--write`; every other page byte-identical.

Round-2 checks (lanes venv, PYTHONDONTWRITEBYTECODE=1, pytest -p no:cacheprovider, from
services/api, multi-file pytest under flock; one at a time; direct exit codes):
- a. `python -m ruff check .` (from services/api): recorded in the return.
- b. `flock .../heavy-run.lock python -m pytest -q -p no:cacheprovider tests/rules/reference_cases
  tests/spatial/test_lot_reach.py tests/scenario/three_answers/test_result_way_bridge_overlay.py`:
  recorded in the return.
- c. `python tests/rules/reference_cases/r6b_reference_cases_render.py --check`: recorded.
- d. `python3 tools/modularity_check.py --check` and
  `python3 scripts/lanes/check_lane_paths.py --coverage`: recorded.
- e. the two new mutation proofs (above), plus the round-1 proofs: recorded.
The full api suite is left to the independent check.

END-OF-REPORT
