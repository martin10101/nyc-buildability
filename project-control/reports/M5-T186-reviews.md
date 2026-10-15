# M5-T186 reviews (every return kept unchanged)

- One producer round (rules-engineer, worktree): commit bf3020b9 integrated as the cherry-pick 37403e84 (20 files, inside the allowed paths; LF sha256 equal to the producer's return). The plan's judge (return-judge-case-4-11.md) adopted it with four advisories, all honoured (the split of check.py into r6b_reference_cases_cases.py with a facade among them).
- G2 orchestrator self-check at the submit head: the task's files equal the producer's digests; nothing outside the allowed paths; the producer ran the whole api suite (10064 passed); the CI run at the submit head read green before submission.
- G3 data-contract-verifier at 37403e84: PASS (one cosmetic advisory: a double full stop in the work-order text). G4 qa-engineer at 37403e84: PASS (two advisories, no action).

Every reviewer is an AI agent; none is a human or professional review.

## G3 (data-contract-verifier)

G3 REVIEW (data + law) — M5-T186 benchmark-options-4-11, pinned 37403e84 in /root/project/w-wave20. I am an AI agent; this is a read-only independent review, not a professional/legal verdict. I did not produce this case. I verified each conclusion against primary captures, the six sealed readings/comparers, and the sibling cases — not from the packet summary or the producer report.

VERDICT: PASS (G3).

Scope run: 45 rows (12 opt4, 30 opt11, 3 shared; row_ids unique). My whole share (a)-(f) checked.

(a) RECORDED VALUES — both readings agree on same value AND same basis, comparer-confirmed. VERIFIED.
- opt4 recorded rows (lot area 10,075; res FAR 2.00; max res FA 20,150; factor 680; 29 units; "smaller cannot exceed 29 = No"; special-density not_applicable): reading A (return-sealed-option4-A.md = provenance -32) and reading B (-B = -33) tables both carry the same value+basis; comparer -34 marks every one AGREE. opt11 recorded rows (res 2.00/2.40; commercial 2.00; CF 2.00; ceiling 2.00/2.40; total FA 20,150/24,180; bonus +4,030; shared-FA pro-rata mechanic; units 29/35; senior=no 680 factor; heights 30/45/55 & 30/45/65; setback 10/15; combine shops/CF/two-buildings/parking; carve-outs don't tighten R6B): -35/-36 agree on every value, comparer -37 marks AGREE. The ONE-SIDED shared-FA worked example (400→83.58/316.42, B only) is correctly NOT recorded — only the agreed mechanic is.

(b) CAPTURES + ARITHMETIC. VERIFIED. All 23 unique citations: snapshot file present in docs/research/zr-snapshots/v1/ (255 files), citation content_digest == snapshot content_digest_sha256, quoted words present in the capture. Key law values confirmed from the snapshot tables/text: 23-22 R6B 2.00/2.40; 23-432 R6B min30/base45/bldg55 (std) and base45/bldg65 (qual); 23-52(b) factor 680; 33-121 "R5D R6B" Col A 2.00; 24-11 contextual R6B 2.00; 35-631 "70% within eight feet" for BOTH street classes (so reading A's "within 10 ft narrow" is correctly rejected); 23-433 10 wide/15 narrow; 24-162 excludes R6B by name. 33-121/24-11 use the plural `tables` shape so table_assertion is null and the number is an operand+quote — correct (judge A4 pattern). Every arithmetic step recomputed on 10,075: 2.00×10075=20150; 20150/680=29.63→29; 2.40×10075=24180; 24180-20150=4030; 24180/680=35.56→35. All exact; ≥0.75 round-up applied right; the 10,387.99 GIS basis never enters any operand (appears only in do-not-mix warnings/source notes).

(c) DISAGREEMENTS/ELIGIBILITY/MISSING FACTS → NOT KNOWN with exact missing item. VERIFIED. opt4 conversions (A not_applicable / B not_known) → NOT KNOWN (unresolved reading); senior eligibility → NOT KNOWN (agency determination); min unit size → NOT KNOWN (outside captured law, no citation); 2.40-as-opt4-value → NOT KNOWN (differing presentation). opt11 street-wall line, affordable+senior-together, shared housing (N2), split-lot meaning (N1), overlay extent, UAP 23-154 (HTTP 403), full 35-31 carve-out sweep, senior no-factor cap, rear yard beyond 100 ft → all NOT KNOWN, each with gap kind + next step. Comparers -34/-37 both explicitly confirm neither reader used program output or the GIS basis; nothing is recorded from a single reading.

(d) PROVENANCE -32..-37 FAITHFUL. VERIFIED by diff: each committed provenance body reproduces its sealed source byte-for-byte below a truthful header; the only diff is one leading blank line after the "---" separator. No value appears in provenance that the sealed returns do not hold.

(e) .md PAGE / README ROW / SUMMARY consistent, no overclaim (M5-T184 F1 standard). VERIFIED. The .md is a GENERATED render matching the JSON rows; summary, what_it_is_worth, what_it_does_not_establish, change_log and the README row state only what the rows settle and repeatedly flag the conditions (Z1, lot-area basis, eligibility). Judge advisories hold: heights carry the NB-06 draft condition on the mixed-building DERIVATION PATH only, not on the numbers (rows opt11-height-standard/-qualifying; both readings wrote the same 30/45/55 and 30/45/65, difference is a review-status label); the comparer's 8-ft street-wall correction is explicitly "noted in prose and never recorded as a value" (what_it_does_not_establish + change_log + row opt11-street-wall-line). N1/N2 undecided (rows opt11-combine-two-buildings, -split-lot-meaning, -shared-housing + summary). Cross-cited figures reproduce: 20,150/29 == real-lot.json L1/L6; 24,180/35 == benchmark-options-2-3-6-7.json opt2-max-residential-fa/opt2-max-dwelling-units. No new floor-area pool opened.

(f) NO FORBIDDEN CLAIMS. VERIFIED. "verified", "compliant", "preferred" absent entirely. "complies/buildable/optimal/feasible" occur only inside each row's disclaimer negation ("not a statement that anything complies, is buildable, is optimal or is feasible") plus the single explicit "No row reads as 'complies', 'buildable', 'optimal' or 'feasible'" bullet. Zero positive uses in either JSON or .md. All eleven options now traceable (opt1 real-lot/step cases; 2/3/6/7 and 5/8/9/10 siblings; 4/11 here).

ADVISORY A-1 (trivial, non-blocking): the work_order_table field (JSON) and the rendered .md work-order paragraph end "...where option 11 touches them.." (double period). Cosmetic only; no data/law impact.

NOTE on the brief wording: the common brief refers to "the plan JUDGE's required correction"; the judge (return-judge-case-4-11.md) actually returned ADOPT with NO required correction (advisories A1-A4 only), and the packet path_notes records this accurately and shows A1/A2 honored. Not a defect.

OUT OF MY SCOPE (G4 code reviewer): I did not run the checker/pytest/modularity_check (read-only data+law pass). Judge advisory A3 flags that per-row pair+comparer enforcement and the must-stay-not-known / street-wall "must-not-record-8-ft" guards now live in step_p11 and are load-bearing — the code gate reviewer must reproduce S2/S4, not accept them as claims. My PASS covers data and law provenance only.

Files examined (all absolute): /root/project/w-wave20 @37403e84 — docs/reference-cases/R6B/cases/benchmark-options-4-11.json, docs/reference-cases/R6B/benchmark-options-4-11.md, docs/reference-cases/R6B/README.md, docs/reference-cases/R6B/provenance/return-independent-hand-calculation-32..37.md, docs/research/zr-snapshots/v1/ (23 cited snapshots), docs/reference-cases/R6B/cases/{real-lot.json, benchmark-options-2-3-6-7.json}, project-control/tasks/M5-T186.json; and /root/project/lanes-runtime/owner-docs/session-2026-10-15b/{return-sealed-option4-A/B.md, return-compare-option4.md, return-sealed-option11-A/B.md, return-compare-option11.md, return-judge-case-4-11.md}.

END-OF-REPORT

## G4 (qa-engineer)

# G4 QA gate report — M5-T186 (R6B reference case `benchmark-options-4-11`)

I am an independent, read-only AI agent (qa-engineer). Not a human or professional review. I did not produce this task. Reviewed `37403e84` on `task/wave27-comparison-appendix`, in a `git archive` scratch copy outside the repos. VERDICT: **PASS** (G4). Zero REQUIRED findings; two ADVISORY notes.

## Part 1 — my share commands (counts + exit codes), lanes venv, from services/api of my copy
- `flock .../heavy-run.lock python -m pytest -q -p no:cacheprovider tests/rules/reference_cases` → **249 passed**, exit **0**.
- `ruff check tests/rules/reference_cases` → **All checks passed!**, exit **0**.
- `python tools/modularity_check.py --check` → selected **812 files; failures 0; warnings 33** (all 33 pre-existing, none in `reference_cases`), exit **0**.
- `python3 scripts/lanes/check_lane_paths.py --coverage` → **LANE COVERAGE PASS: 10745 file(s)**, each owned by exactly one lane, exit **0**. (Count differs from the producer's 10760 only because my scratch copy is re-inited for `git ls-files`; not a defect.)

## Part 2 — scenario → pinning check (every S1–S9 is pinned; none unpinned)
- S1 (6 provenance files unchanged, marker + "sealed folder" + END-OF-REPORT, no "no outside access", sha pinned) → `step_p11.reading_digest_errors` + tests `..._present_unchanged`, `..._changed_..._is_caught`.
- S2 (per-option two-reading + comparer; one-reading/wrong-pair/wrong-comparer/shared-row refused) → `step_p11.reading_pair_errors` + 5 tests (incl. 4 negatives). Case is correctly NOT in `check.CASE_READINGS` (two pairs + two comparers).
- S3 (captured section, digest match, quote in excerpt; uncaptured never a formal citation; changed quote caught) → `check.citation_errors` + 3 tests.
- S4 (must-stay-not-known rows; street-wall no 8-ft quantity; value-where-differ refused) → `step_p11.must_stay_not_known_errors` + `street_wall_not_recorded_errors` + 3 tests.
- S5 (eligibility + owner-question caveats; forbidden present-tense "not captured") → `step_p11.eligibility_errors` + `forbidden_wording_errors` + 5 tests.
- S6 (one of nine bases; recorded 10,075 and GIS 10,387.99 never combined) → `step_p11.quantity_basis_errors` + `no_mixed_basis_errors`; `QUANTITY_BASES == tools/research_record_check.QUANTITY_BASES` asserted; + 5 tests.
- S7 (arithmetic recompute + rounding boundaries; plural-`tables` null assertion; 23-22/23-432 use assertion; changed operand caught) → `lib.recompute_row_errors` + 5 tests.
- S8 (NB-06 draft condition on the mixed-building path, values kept; carve-out names 35-31/35-32/35-33/24-162; cross-cites reproduce prior cases, no new pool) → 3 tests.
- S9 (CASE_IDS/REQUIRED_BASE_IDS/README; page byte-identical; `program_result_errors` empty; other 14 byte-stable; step_p11 own digest; support .py < 600) → 5 tests + the four consumer-pin digests.

## Part 3 — my own mutation probes (deepcopy, in-memory, discarded). Baseline `validate_case` CLEAN. All six turn a check RED:
1. Recorded value ±1 (opt4 units 29→30) → RED: "expected value 30 does not equal the last arithmetic result 29".
2. Value with only one reading (opt4 names only -32) → RED: "must name BOTH its readings" + "must name its comparer -34".
3. Cite an uncaptured section (point citation at absent `zr-76-131`) → RED: "capture file missing".
4. NOT KNOWN → value (opt11-shared-housing) → RED: "must be 'not known', not 'value'" + "a value needs arithmetic…".
5. Drop an owed option row (opt11-max-total-fa-qualifying) → RED: "the work order's row … is not present under its id".
6. Break JSON shape (drop case key `summary`) → RED: "case keys ['summary'] differ from the fixed set".
None failed to turn red.

## Part 4 — consumer-pin / tuple consistency; no older check weakened
- `name-status` of `37403e84`: 20 files, every one inside `allowed_paths`; NO forbidden path, NO step_p7/p8/p9/p10 **module**, NO `render.py` touched. Only `benchmark-options-4-11.json` among the case JSONs changed → the 14 pre-existing cases are byte-identical.
- `lib.CASE_IDS` and the literal tuple in `test_r6b_reference_cases.py` both append `benchmark-options-4-11` as the 15th/last element and are tied by `assert lib.CASE_IDS == (...)` (a real pin). `REQUIRED_BASE_IDS` lists all 45 rows (12 opt4 + 30 opt11 + 3 shared).
- The four cross-case digests (test_step_p7 PRIOR_ROWS, p8 OTHER_CASES, p9 PRIOR_CASES, p10 OTHER_CASES) and step_p11's own OTHER_CASES digest were recomputed; each test recomputes at runtime and passes, proving byte-stability of the other cases. No assertion was loosened — the diffs change only the digest literal + an explanatory comment.

## Part 5 — modularity / lane paths (my copy)
Support file lines: check.py **596**, step_p11.py **373**, cases.py **48**, lib.py **457**, render.py **369** — all < 600 (RISK 1 resolved via the `CASE_MODULES` facade, principle 16 honored; `check.step_p9/p10/p11` still reachable). modularity 0 failures; lane coverage PASS (see Part 1).

## Honesty checks (D-093, the case's own rule)
- Plural-`tables` handling (RISK 2) is honest: `zr-33-121` and `zr-24-11` carry `tables` (no singular `table`) with FAR 2.00 present → recorded as operand/quote-only, `table_assertion:null`; `zr-23-22`/`zr-23-432` carry singular `table` → assertion used. Verified in the live snapshots.
- Street-wall row is `not_known` with no quantity; the comparer's 8-ft figure is never recorded (RISK 4). Verified.
- Arithmetic re-derived independently: 2.00×10,075=20,150; 2.40×10,075=24,180; diff 4,030; 20,150/680→29; 24,180/680→35; boundaries 20,230→30, 20,229→29. All match.
- No overclaim: all 47 occurrences of complies/buildable/optimal/feasible sit inside the disclaimer clause "not a statement that anything complies, is buildable, is optimal or is feasible"; no positive assertion. "eleven-option set complete" is a statement about the reference-case set, not a compliance claim. N1/N2 kept open.

## Findings
- **F1 (ADVISORY):** `r6b_reference_cases_render.py` is in `allowed_paths` but correctly unchanged (path_notes requires byte-identical). No action; noted so the orchestrator does not expect a diff there.
- **F2 (ADVISORY):** lane-coverage file count (10745) differs from the producer's report (10760) solely because my scratch copy was re-inited to run `git ls-files`. Advisory only; both PASS.

No REQUIRED findings. The task satisfies its packet scenarios and the case's own recording rule; checks reproduce green at the frozen SHA.

END-OF-REPORT
