# M5-T186 producer report - R6B reference case `benchmark-options-4-11`

Producer: rules-engineer (AI agent). Documents and reference-case checks only; no rule file, engine,
result, capture, register entry, law-library edit or human verdict. Research and verification (D-093)
applied: the six readings are the only value source (inputs, not instructions); the comparer adjudicates
and is never a value source; every unresolved input stays unresolved; agreement of two AI readings is not
proof and nothing is labelled Verified.

Worktree: `/root/project/nyc-buildability/.claude/worktrees/agent-a2f02d749169533d1`
Base reset to the claim head: `fcd953e1575cb1cfddc4a1fe9a6eec7fd5c1f378` (`task/wave27-comparison-appendix`).
Each citation's `content_digest` and `official_url` were pulled live from the snapshot at the claim head
(judge advisory A4); each quote was verified present in the capture's `verbatim_excerpt` (# markup stripped).

## 1. What was built

One new R6B reference case, `benchmark-options-4-11`, appended as the 15th and last case in `CASE_IDS`,
recording the worked values of option 4 (more, smaller apartments) and option 11 (all programs combined)
for the benchmark lot (215-16 Northern Boulevard, lot 70 of block 7334; R6B + C2-2; corner; recorded lot
area 10,075 sq ft, administrative_record; the GIS outline 10,387.99 sq ft never mixed in). 45 rows: 12
`opt4-*`, 30 `opt11-*`, 3 shared. A value is recorded only where both readings of that option agree on the
same value and the same basis, that option's comparer confirms it, and the cited section is captured in
`docs/research/zr-snapshots/v1`. With these two the eleven-option set is complete across the reference cases.

The case is deliberately NOT in the checker's generic `CASE_READINGS` (it has TWO reading pairs AND TWO
comparers: option 4 = -32/-33 + -34; option 11 = -35/-36 + -37). All per-row pair-and-comparer enforcement,
the must-stay-not-known guards, the street-wall 8-ft guard, the quantity-basis/no-mixed-basis guards, the
eligibility/owner-question caveats and the forbidden-wording guard live in the new step-P11 module, with
negative tests for each.

## 2. The rows

### Option 4 (opt4-*) - 12 rows

RECORD (both readings agree on value and basis; comparer -34 confirms; section captured):
- `opt4-recorded-lot-area` = 10,075 sq ft (administrative_record), conditional Z1. 12-10 lot-area.
- `opt4-residential-far-standard` = 2.00 FAR. 23-22 R6B standard (singular `table` -> table_assertion).
- `opt4-max-residential-fa` = 20,150 sq ft = 2.00 x 10,075. 23-22 + 23-52 opening.
- `opt4-du-factor` = 680 sq ft/unit. 23-52(b) (reaches R6B via 11-25, flagged as a reading).
- `opt4-max-dwelling-units` = 29 (20,150 / 680 = 29.63, 0.63 < 0.75 dropped). 23-52 opening + (b).
- `opt4-smaller-cannot-exceed-29` = finding: No; the 680 factor caps the count regardless of unit size, so
  option 4 yields the same 29 units as option 1. 23-52 opening + (b).
- `opt4-nofactor-special-density` = not applicable (bounded negative: Queens lot, not Manhattan Core / Special
  Downtown Brooklyn; NB-05). 23-52(a)(1) + 12-10 special-density-areas.

NOT SETTLED (stay not known, each with KIND OF GAP):
- `opt4-nofactor-senior` - agency determination (HPD / NYS DOH eligibility; an applicant fact).
- `opt4-nofactor-conversions` - unresolved reading (reader A not_applicable / reader B not_known; same
  practical result; labels differ, so not jointly settled; comparer prefers not_applicable but is an
  adjudicator, not a value source).
- `opt4-min-unit-size` - unresolved law (MDL / HMC / Building Code sit outside the captured ZR; named in prose
  only, never a value basis or a formal citation).
- `opt4-affordable-2.40-not-opt4` - unresolved reading (2.40/24,180/35 is option 2's path, not an option-4
  count; reader A in prose, reader B tabled not_known; the figure itself is settled for option 2, cross-cited).
- `opt4-vs-option-1` = finding: option 4 equals option 1 on the legal unit count (29 at 20,150 sq ft); the
  settled option-1 figures stand in real-lot.json rows L1 and L6 (cross-cited, not re-recorded).

### Option 11 (opt11-*) - 30 rows

RECORD:
- `opt11-single-use-far-res` = 2.00 standard / 2.40 qualifying. 23-22 (table_assertion).
- `opt11-single-use-far-commercial` = 2.00. 33-121 (PLURAL `tables` -> table_assertion null, operand + quote).
- `opt11-single-use-far-cf` = 2.00. 24-11 (PLURAL `tables` -> table_assertion null, operand + quote).
- `opt11-combination-ceiling-standard` = 2.00 (greatest single-use; uses share one envelope). 35-31 + 23-20.
- `opt11-combination-ceiling-qualifying` = 2.40 (qualifying residential raises the one ceiling; eligibility
  caveat). 35-31 + 23-22.
- `opt11-max-total-fa-standard` = 20,150 sq ft = 2.00 x 10,075 (= option 1, cross-cites real-lot L1). 35-31.
- `opt11-max-total-fa-qualifying` = 24,180 sq ft (2.40 x 10,075) and +4,030 sq ft bonus (24,180 - 20,150);
  prose expected so both arithmetic steps are kept; cross-cites benchmark-options-2-3-6-7#opt2-max-residential-fa.
- `opt11-shared-fa-attribution` = pro-rata on total floor area less the shared portion. 35-31 + 23-20.
- `opt11-shops-cf-add-no-fa` = finding: all single-use FARs are 2.00, so shops/CF add no total FA; only
  qualifying housing raises the ceiling. 35-31.
- `opt11-du-standard` = 29 (20,150 / 680) (cross-cites real-lot L6). 23-52(b).
- `opt11-du-qualifying-affordable` = 35 (24,180 / 680) (cross-cites opt2-max-dwelling-units; eligibility
  caveat). 23-52(b).
- `opt11-du-qualifying-senior` = finding: 23-52(a)(2) removes the 680 factor for qualifying senior housing;
  whether any other provision caps the count is the separate open point `opt11-senior-nofactor-cap`
  (eligibility caveat). 23-52(a) + (a)(2).
- `opt11-height-standard` = 30 / 45 / 55 ft. 23-432 standard (table_assertion) + 35-63 + 35-632; the
  mixed-building derivation path 35-63 -> 35-632 -> 23-432 recorded as an NB-06 draft reading (condition on the
  path, not on the numbers; advisory A1).
- `opt11-height-qualifying` = 30 / 45 / 65 ft. 23-432 qualifying (table_assertion) + 35-632 + NB-06 condition.
- `opt11-setback` = 10 ft wide / 15 ft narrow above the max base. 23-433.
- `opt11-combine-shops` = may combine, conditional on the mapped overlay reaching the footprint (eligibility
  caveat). 35-31 + 32-161.
- `opt11-combine-cf` = may combine. 35-31 + 24-11.
- `opt11-combine-two-buildings` = may (35-01 extends the Chapter-5 bulk across the zoning lot); split-lot
  meaning is owner N1, not decided. 35-01.
- `opt11-combine-parking` = may combine with any (orthogonal to the FAR cap; Outer Transit Zone a recorded
  dataset value, a sourced fact; no formal ZR citation).
- `opt11-carveouts-dont-tighten-R6B` = finding: the three checked carve-outs (35-32 qualifying residential
  sites, 35-33 R6-no-suffix + R7-1, 24-162 excludes R6B by name) do not reach R6B; the full sweep is separate
  and open. 35-31 + 35-32 + 35-33 + 24-162.
- `opt11-vs-option-1` = finding: adds a use mix in option 1's 20,150 sq ft envelope and, where residential
  qualifies, +4,030 sq ft, +10 ft height (55->65), +6 units (29->35); opens no second floor-area pool. 35-31.

NOT SETTLED (stay not known, each with KIND OF GAP):
- `opt11-street-wall-line` - unresolved reading (reader A "70% within 8 ft (wide) / within 10 ft (narrow)" is
  partly wrong; 35-631(b) is 70% within 8 ft for BOTH classes and the 10/15 ft are recess depths; reader B no
  numeric row; the comparer's 8-ft correction is noted in prose, NEVER recorded as a value; the row carries no
  quantity). 35-631.
- `opt11-affordable-senior-together` - unresolved law (no captured text; no benefit either way).
- `opt11-shared-housing` - pending legislation and an open owner question (N2; framework pending 2027).
- `opt11-split-lot-meaning` - an open owner question (N1; 77-00 not among the captures).
- `opt11-overlay-extent` - a missing fact about the property (mapped overlay line; 76-131 not among captures).
- `opt11-uap-text` - unresolved law (23-154 not among the captures; HTTP 403).
- `opt11-35-31-full-carveout-sweep` - unresolved law (35-34+ neighbours not swept).
- `opt11-senior-nofactor-cap` - unresolved law (no captured provision found that caps the no-factor count).
- `opt11-rear-yard-beyond-100ft` - a missing fact about the property (geometry; 23-344(c), NB-03 draft).

### Shared rows - 3
- `both-readers-did-not-have` (value, prose only): 76-131, 23-154, 77-00/Art VII Ch 7, 35-34+ neighbours, and
  the MDL/HMC/Building Code room standards - named in prose, never a value basis or a formal citation.
- `real-lot-missing-facts` (not known): the zoning lot (NB-01), the lot-area basis (NB-04), the overlay line,
  the street-wall facts, the rear-yard geometry, use classification and eligibility.
- `options-out-of-scope` (value): with options 4 and 11 recorded the eleven-option set is complete; asserts no
  eligibility or compliance; N1 and N2 stay open.

## 3. Where the two readings differ (per option)

Option 4 (comparer -34): the readings AGREE on every recorded value (10,075; 2.00; 20,150; 680; 29; the
no-exceed-29 finding; special-density not_applicable). Divergences, all kept not known: (a) conversions label
(A not_applicable / B not_known - same practical result); (b) the affordable 2.40/35 figure (A prose "option
2's path" / B tabled not_known) - both agree it is not an option-4 count. Neither reader used the 10,387.99 GIS
basis or program output (comparer confirmed).

Option 11 (comparer -37): the readings AGREE on the single-use FARs (2.00/2.40, 2.00, 2.00), the ceilings
(2.00/2.40), the totals (20,150/24,180) and bonus (+4,030), the shared-FA attribution, the shops/CF-add-no-FA
finding, the units (29/35; senior no-factor), the setback (10/15), the height VALUES (30/45/55 and 30/45/65),
which programs may combine, and the checked carve-outs. Divergences: (a) street-wall line - reader A gave a
number that is partly wrong, reader B gave none, so NOT SETTLED and the comparer's 8-ft correction is never
recorded (RISK 4 / advisory A3); (b) height-applicability certainty - reader A "applies" vs reader B
"not_known (NB-06 draft)"; both wrote the SAME numbers, so the VALUES are recorded WITH the NB-06 draft
condition on the mixed-building derivation path (RISK 5 / advisory A1), not dropped. Neither reader used GIS or
program output (comparer confirmed).

## 4. Cross-citation without double-recording (RISK 10)

Option 11's figures that repeat recorded ones cite the prior case+row in prose and re-derive their own
arithmetic, opening no second floor-area pool. A test proves the numbers reproduce:
- `opt11-max-total-fa-standard` (20,150) == real-lot L1; `opt11-du-standard` (29) == real-lot L6.
- `opt11-max-total-fa-qualifying` (24,180) == benchmark-options-2-3-6-7#opt2-max-residential-fa;
  `opt11-du-qualifying-affordable` (35) == #opt2-max-dwelling-units.

## 5. Consumer pins moved and why

A new case joins every cross-case "prior/other" blob, so these four pins were recomputed (the blob grew by the
new case's rows; no existing case's rows changed):
- `test_r6b_reference_cases_step_p7.py` PRIOR_ROWS_DIGEST -> `579e95df1a72f9a680452cd89c0fcddbf940a9319cc7cc9b77c20ad7bb4bb020`
- `test_r6b_reference_cases_step_p8.py` OTHER_CASES_DIGEST -> `463b284be8608af92ea44f2b976f464798ffa750af84b437bb784416bd7c4868`
- `test_r6b_reference_cases_step_p9.py` PRIOR_CASES_DIGEST -> `76a70ec3ca6166201ec34fddf8133bf36012866b0959938fcc274a03523aedca`
- `test_r6b_reference_cases_step_p10.py` OTHER_CASES_DIGEST -> `042c62bdef6ad1935072cfed8a1bb1b7f7c0d9b54972f88675aea666df286c84`
The new `test_r6b_reference_cases_step_p11.py` carries its own OTHER_CASES_DIGEST
`2bfd30e3f3122f7507af463adb382a36b924a0b6a3311bb2a898cd1d5accce5e` (all 14 pre-existing cases). `step_p6`
REACH_ROWS_DIGEST (corner-reach only) does NOT move and was not touched. `test_r6b_reference_cases.py` pins the
literal CASE_IDS tuple - the new id appended as the 15th element. `r6b_reference_cases_lib.py` CASE_IDS and
REQUIRED_BASE_IDS updated; README lists the case.

## 6. The 600-line split (RISK 1 / advisory A2)

Plain step-P11 wiring would push `r6b_reference_cases_check.py` to >= 600 (fail). Per advisory A2 the case-module
dispatch and the reading-digest aggregation were extracted into the new `r6b_reference_cases_cases.py`
(`CASE_MODULES = (step_p9, step_p10, step_p11)`; one registry loop each for `case_errors` and
`reading_digest_errors`), with the step modules re-exported so the checker and its tests keep reaching
`check.step_p9/p10/p11` (a compatibility facade, CLAUDE.md principle 16). This is durable: a later case adds one
entry to `CASE_MODULES` and nothing in the checker. `check.py` is 596 lines; `step_p11.py` 373; `cases.py` 48;
all support .py < 600 (confirmed by modularity_check and the suite's `test_support_files_stay_under_600_lines`).

## 7. Provenance headers (RISK 6)

`-32..-37` were written as a truthful header (distinctive `M5-T186 PROVENANCE -NN (...)` marker + the literal
phrase "sealed folder" naming the pinned read-only captures and settled cases) followed by the reading
reproduced byte-for-byte, ending END-OF-REPORT. Each header states that file's actual method and none claims
"no outside access": option 4 reading A read only the snapshots/NB/cases/library; option 4 reading B needed no
ZR website fetch; option 11 reading A read no program run; the two comparers reopened the v1 snapshots. Digests
are pinned on the saved file AFTER the header.

## 8. Checks (each run one at a time; lanes venv; PYTHONDONTWRITEBYTECODE=1; pytest -p no:cacheprovider;
multi-file pytest under `flock /root/project/lanes-runtime/heavy-run.lock`)

| # | Check | Result | Exit |
|---|---|---|---|
| a | `python -m ruff check .` (services/api) | All checks passed | 0 |
| b | `pytest -q tests/rules/reference_cases` | 249 passed in 3.84s | 0 |
| c | `r6b_reference_cases_render.py --check` | reference-case check PASSED (no issues) | 0 |
| d | `tools/modularity_check.py --check` | 812 files, failures 0, 33 pre-existing warnings (none in my files) | 0 |
| e | `scripts/lanes/check_lane_paths.py --coverage` | LANE COVERAGE PASS: 10760 files, each owned by exactly one lane | 0 |
| f | whole api suite `pytest -q` (under the lock) | 10064 passed, 8 skipped, 1 warning in 519.49s | 0 |

## 9. Mutation proofs (each turns a check RED; baseline and restore green; disk untouched - deepcopy)

| Mutation | Check that went RED |
|---|---|
| 1 changed value (opt4 units 29 -> 30) | `lib.recompute_row_errors`: expected 30 != last arithmetic result 29 |
| 2 one-reading opt4 row (names only -32) | `step_p11.reading_pair_errors`: must name BOTH readings |
| 3 wrong-comparer opt4 row (-37 not -34) | `step_p11.reading_pair_errors`: must name its comparer -34 |
| 4 changed/uncaptured citation digest | `check.citation_errors`: law digest for 23-22 does not match the capture |
| 5 not-known opt4-nofactor-senior -> value | `step_p11.must_stay_not_known_errors`: must be 'not known' |
| 6 street-wall 8-ft value recorded as a quantity | `step_p11.street_wall_not_recorded_errors`: records no measured quantity |

These are also the negative unit tests in `test_r6b_reference_cases_step_p11.py` (one-reading, wrong-pair,
wrong-comparer, shared-row-without-comparers, value-where-differ, street-wall-8-ft, missing caveats, forbidden
wording, missing basis, basis-outside-nine, recorded/GIS combined, changed operand, changed quote, changed
reading digest), all passing in check b.

## 10. Assumptions and limitations

- Every figure stays conditional on Z1 (lot 70 alone is the zoning lot; NB-01 unconfirmed) and uses the
  recorded 10,075 sq ft; the GIS 10,387.99 never enters a figure (the GIS 30-unit figure is never recorded).
- Nothing is Verified: agreement of two AI readings is not proof; the case is a draft reading, not
  professionally reviewed (ADR-007). The owner questions N1 (option 8 meaning) and N2 (shared housing) stay
  open where option 11 touches them; no eligibility or use permission is decided.
- The 23-52 -> R6B reach rests on the 11-25 suffix inheritance (a reading flagged for the reviewer), not an
  express naming; recorded as such in `opt4-du-factor`.
- The mixed-building street-wall/height derivation path is an NB-06 draft reading; the height VALUES are
  settled (23-432 capture and the option-1 / option-2-3 cases) and recorded with that condition.
- AI-agent limits: I did not enter any human or professional verdict and recorded no register entry or
  law-library edit (forbidden). `r6b_reference_cases_render.py` was kept byte-identical (not modified).

## 11. Files written (FULL LF-normalized sha256)

| sha256 (`tr -d '\r' < f | sha256sum`) | file |
|---|---|
| 2f5d6a0763dbec7e0b4713d5936fc81a2c59763505bfa1e39e064673b7fb4f67 | docs/reference-cases/R6B/README.md |
| 6f6fdeb90c8862f4ad1e0fb02088dab46b692b13ae55c282ecbd193804da7686 | docs/reference-cases/R6B/benchmark-options-4-11.md |
| 102ea9bf41aed6518dac77769ecdf13479da1ae9234fcfb0b2ac84b9d828efe6 | docs/reference-cases/R6B/cases/benchmark-options-4-11.json |
| 87672565a1c78bcc49fd36c53174a1155584232cd336dabd5b3ec2cca6803835 | provenance/return-independent-hand-calculation-32.md |
| dfe4d9760bce6061feae8ecb714830f4a7377492b0c459ae26bcb83c18407400 | provenance/return-independent-hand-calculation-33.md |
| a9d3f6b5bec18e2ea389ee1dcb424097a2fea5ec5119155028a01216af3cdfec | provenance/return-independent-hand-calculation-34.md |
| b7dfde7abdce51c8fa4883fc333928f1d551bd70ac2eb55cd07b64d251dc5bd7 | provenance/return-independent-hand-calculation-35.md |
| c2b08bbbbe66491010d4beb61bb20db51020b928aad18bd82abb5e53b772b3e5 | provenance/return-independent-hand-calculation-36.md |
| fee1eb07d8acd563be68ed093c8663d584305e8a57f7c20616c2143acfe0ff0e | provenance/return-independent-hand-calculation-37.md |
| 241e0531dbebc76d7478b9ef0a40dbc8607e3bfe6e145e859cffa0f790b68135 | reference_cases/r6b_reference_cases_cases.py |
| 65ea584ce10be5f5f7149ad6644b657643c83b1a524833ce02519e8f44f90ad6 | reference_cases/r6b_reference_cases_check.py |
| 145f09d810c6a03e9717d5ad439eec6c1a03f367572a8aaf9326d45ecbcdada0 | reference_cases/r6b_reference_cases_lib.py |
| 851c2d651fd2f2b579b3d2faf2b6818087f47f5aebb3e270c09d6b2ca816e633 | reference_cases/r6b_reference_cases_step_p11.py |
| 4949b291e0ebff6122cd9f86643eaf16164485dd753e7088d37e23aa49f6a3ad | reference_cases/test_r6b_reference_cases.py |
| 112ed9c5e639376aea5a43b766f3c9c088534674d96bcb6383abd65d890bc2ee | reference_cases/test_r6b_reference_cases_step_p7.py |
| 686bb06607dea0689c158270017cc75b9e66eaf47a28b8212be2c1716af6f472 | reference_cases/test_r6b_reference_cases_step_p8.py |
| b631d8482f3fe434fc14cd96a6b1787b4e7d57c2dcb3a13c42dc4a5cb47adb8c | reference_cases/test_r6b_reference_cases_step_p9.py |
| cf4f0337e907a51f753901dc5560c6b8ee32925b74916167a33e220ab3689711 | reference_cases/test_r6b_reference_cases_step_p10.py |
| feaac8561f26c6336e957fc9f8fbd01c931a1b78c6a8e8028404799a13c46da4 | reference_cases/test_r6b_reference_cases_step_p11.py |

(The report file itself is not listed; it is written after these.)
