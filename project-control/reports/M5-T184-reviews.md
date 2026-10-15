# M5-T184 reviews (every return kept unchanged)

- Two producer rounds (rules-engineer, worktrees): round 1 bbfb189f integrated as 0f62e39f, round 2 a4b81e74 integrated as f566724a (inside the allowed paths; LF sha256 equal to the producer's return; integration record b8eba3a0). Documents and reference-case checks only.
- Independent pre-integration checks at each round (return-M5-T184-precheck.json and -precheck-r2.json, session 2026-10-15a): round 1 found the community-facility coverage overclaim, corrected in round 2; whole api suite 9893 passed, 8 skipped at a4b81e74.
- G2 orchestrator self-check at the submit head: the task's files equal the integrated rounds plus the one tagged correction 307c8af2; nothing outside the allowed paths; tests/rules/reference_cases 179 passed and render --check PASSED under the lock after 307c8af2; the CI run at the submit head read green before submission.
- G3 data-contract-verifier at b8eba3a0: PASS with one REQUIRED (F1: the case summary and its page said "coverage 80/60" among the settled values; only the corner 80 percent is settled) and two advisories (no change). F1 applied by the orchestrator as 307c8af2 [ORCH-CORRECTED per G3 F1] (summary and change log only; page re-rendered). G3 delta check (data-contract-verifier) at 307c8af2: below.
- G4 qa-engineer at b8eba3a0: PASS, no required correction; 179 passed; six mutation probes all red; every scenario S1-S9 pinned; one accept-time advisory (read CI green for the whole api suite at the accept head; done by the accept seam).

Every reviewer is an AI agent; none is a human or professional review.

## G3 (data-contract-verifier)

M5-T184 — G3 REVIEW (data & law), reviewer: data-contract-verifier (independent, READ-ONLY AI agent — this is not a human/professional review)

VERDICT: PASS WITH REQUIRED CORRECTIONS (G3)

SCOPE / REPRODUCTION
Pinned b8eba3a0 on task/wave26-envelope-constraints in /root/project/w-wave20. The working tree is byte-identical to b8eba3a0 for every task path (`git diff b8eba3a0 -- docs/reference-cases services/api/tests/rules/reference_cases project-control/reports/M5-T184-producer-report.md` = empty); commits 48d6587b+ touch none of them (confirmed). I re-derived every value row of cases/benchmark-options-2-3-6-7.json from the sealed/reader-B/comparer returns in owner-docs/session-2026-10-15a, the pinned captures in docs/research/zr-snapshots/v1, and recomputed all arithmetic myself. I ran (flock, one at a time): ruff (pass), `r6b_reference_cases_render.py --check` (PASS — .md is byte-identical to render(JSON)), and `pytest tests/rules/reference_cases` (179 passed).

MY SHARE (a)-(f) — results
(a) Both readings agree on value AND basis for every VALUE row — verified against the actual returns:
 opt2: 24,180 (sealed l.15/30, B l.14/28); 4,030 (l.16/31, l.16/28); 30/45/65 (l.17-19, l.17-19); 35 = 24,180/680=35.56 (l.20/32, l.21/28); setback 10/15; rear-yard/coverage/affordable-share handled as not-known in both. opt3: 24,180, 30/45/65, 23-52(a)(2) no-factor, AIRS ≥4%, side yard 5ft — all in both (sealed vs readerB). opt6/7: FAR 2.00, 20,150, combined 2.00/20,150, heights 30/45/55, front 0 / side 8 / rear 30 / corner-waiver / 23-ft obstruction / UG III / no-FA-gain / 24-162 & 35-33 not-applicable / opt7 DU 0 / opt6 DU ≤29 — all in both. No value rests on a single reading or program output (the one single-reading risk — interior 60% / 6,045 from reading A only — was caught at round-1 precheck and corrected in round 2; I independently confirmed reading B (-24) gives ONLY corner 80 / 8,060, no worked interior figure).
(b) Every cited section is captured (24 distinct snapshots, all present in zr-snapshots/v1). I confirmed the quoted clause appears verbatim in each (28 spot-checks, all OK) and content_digests match (8 checked by hand + harness checks all 43 citations → 0 mismatches). Table bodies support the values: zr-23-22 R6B = 2.00/2.40; zr-23-432 R6B = 30/45/55 std, 45/65 qual; zr-24-11 plural `tables` R6B contextual = ["R6B","2.00","80","60"]; zr-24-34 lists only R1–R5 (so "no CF front yard in R6B" is a sound bounded negative). Arithmetic recomputed on 10,075: 2.40×10,075=24,180; 0.40×=4,030; 24,180/680=35.56→35; 2.00×=20,150; 20,150/680=29.6→29; 0.80×=8,060; 0.60×=6,045; opt2-vs-1 +4,030/+10/+6 — all exact; nothing mixes the 10,387.99 display basis (that figure appears only as display-only/≈3.1% conflict).
(c) Disagreements/unresolved/eligibility/missing facts are each not_known with the exact gap and next step (opt3-max-dwelling-units records the real A/B disagreement — A "no numeric limit", B "not known"; opt67-street-wall records the 23-431 vs 35-631(b) citation split; plus opt2-lot-coverage, affordable-share, MIH, opt6-DU, opt67-max-footprint, which-uses, real-lot-missing-facts). Nothing from a single reading or program output, except the F1 straggler below.
(d) Provenance 19-25 are faithful: each ends with its return byte-for-byte (after LF/trailing-newline normalization) + an honest ~8-line header; reading B's header discloses it was told not to read return files; the comparer header discloses it is an adjudicator, not a value source. No value was added to reading B.
(e) .md == render(JSON) (render --check green). README summary row reflects round 2. EXCEPTION: F1.
(f) No forbidden claim-word ("Verified"/"compliant"/"feasible"/"optimal"/"preferred"/"buildable") is used as a positive claim — all occurrences are explicit negations. Options 5, 8 and 9-10 are named as owed in work_order_table, summary, what_it_does_not_establish, change_log, and a dedicated options-out-of-scope row.

FINDINGS
F1 — REQUIRED — docs/reference-cases/R6B/cases/benchmark-options-2-3-6-7.json `summary` field (line 5) and its render in docs/reference-cases/R6B/benchmark-options-2-3-6-7.md (line 7). Both read: "The settled values include … options 6 and 7's community-facility FAR 2.00 / 20,150 sq ft, coverage 80/60, heights 30/45/55 ft …". Listing "coverage 80/60" as a SETTLED value reintroduces exactly the overclaim round 2 removed: interior/through 60% is NOT settled (reading B gives only corner 80; 60% is reading-A-only + a capture quote). This contradicts (i) the authoritative row opt67-cf-lot-coverage (records only corner 80; interior "not settled on both readings' words"), (ii) the change-log entry "6,045 removed from every settled place", and (iii) the corrected README row ("the agreed corner-lot coverage of 80 percent (the interior/through rate and the whole-lot footprint stay not settled…)"). So the JSON `summary`/.md and the README now disagree, and the summary states a not-settled value as settled — failing my share (c) and (e). Correction (wording only, no recomputation): in the JSON `summary` field replace "coverage 80/60" with "the agreed corner-lot coverage of 80 percent (the interior/through rate and the whole-lot footprint stay not settled)", then re-render the .md (`r6b_reference_cases_render.py --check` must stay green). The machine-readable row values and the test harness are already correct, so no value changes.

F2 — ADVISORY (no change) — opt3-max-dwelling-units correctly records the genuine A/B disagreement as not_known; opt67-street-wall correctly records the 23-431 vs 35-631(b) citation split as not_known; the 8 not-known rows carry no value and state the kind of gap. Handling is correct.

F3 — ADVISORY (no change) — Disclosed in the provenance/producer report: reading B of option 3 (-22) read a repo source file (services/api/app/drawings/report/options.py). This is within the readers' detached-checkout read access (a source file, not program output) and fed no recorded value; disclosure is honest.

BOTTOM LINE: The data and law content is sound — every recorded value is twice-read, same-basis, captured, verbatim-quoted, digest-matched, and arithmetically exact on the 10,075 basis; every gap is a correctly-scoped not_known; provenance is faithful; no claim-word misuse; owed options named. One REQUIRED wording correction (F1) remains: the case `summary` field (and its .md render) must be brought into line with the round-2 correction and the README so interior 60% is not stated as a settled value. Recommend recording G3 as PASS-with-required-corrections; F1 blocks acceptance until applied (tagged [ORCH-CORRECTED], then re-render + re-record at the corrected head).

END-OF-REPORT

## G3 (data-contract-verifier, delta check of the correction)

G3 DATA-AND-LAW DELTA REVIEW — M5-T184 correction 307c8af2 (data-contract-verifier). I am an AI agent; this is an independent read-only review, not a professional/legal review.

VERDICT: PASS (G3 delta).

PINNED: `/root/project/w-wave20` HEAD was exactly 307c8af2 during review; reviewed-before head b8eba3a0; scoped disk clean vs HEAD.

F1 (part 1 — change is summary + one change_log only; all else byte-identical) — PASS.
- Scoped diff b8eba3a0..307c8af2 and commit-vs-parent (307c8af2~1) both touch ONLY `docs/reference-cases/R6B/benchmark-options-2-3-6-7.md` and `cases/benchmark-options-2-3-6-7.json` (+8/-2). Other files in the b8eba3a0..307c8af2 range belong to disjoint peer tasks (M3-T010, M5-T183, D-094 source-025) outside the three scoped paths.
- In-memory JSON compare: top-level keys equal; only `summary` and `change_log` differ; all 44 `rows` byte-identical (every facts_used, citation, value, arithmetic, expected, quantities unchanged). `change_log`: old 2 entries are an exact prefix of new 3 (one appended). Word-diff of summary: the SOLE change is "coverage 80/60," → "the agreed corner-lot coverage of 80 percent (the interior/through rate and the whole-lot footprint stay not settled),". Option-2/3 settled values in the summary unchanged.

F2 (part 2 — new wording true against rows/README/readings; no new overclaim) — PASS.
- opt67-cf-lot-coverage expected = "80 percent on the corner portion (the agreed figure); the interior/through rate is not settled on both readings' words"; quantities = corner 80% basis law. opt67-cf-max-footprint = not_known (per-portion products 8,060/6,045 are not a whole-lot maximum). Summary now matches both exactly.
- Readings corroborate: reader A (return-sealed-options67) works corner 80% AND interior/through 60% as applied values; reader B (return-readerB-option6-7) gives only corner 80%/8,060 in its worked table and quotes the 24-11 cell (2.00/80/60) as the law; comparer (return-compare-options) confirms the 24-11 capture but is not a value source. So corner 80% agreed on same basis; interior/through 60% is one worked reading only; whole-lot footprint not settled — as stated.
- Other named settled values verified unchanged: FAR 2.00 (opt6-cf-far), 20,150 = 2.00×10,075 (opt6-cf-max-fa), heights 30/45/55 (opt67-heights). README line 40 already carried the corrected wording at b8eba3a0; the JSON summary was the lagging overclaim F1 caught — now consistent.

F3 (part 3 — page = renderer output; tests pass) — PASS.
- `r6b_reference_cases_render.py --check` (lanes venv): "reference-case check PASSED (no issues)", exit 0 — the .md is a byte-exact pure function of the .json for all cases; renderer+lib byte-identical 307c8af2↔HEAD.
- Under heavy-run.lock, from services/api: `pytest -q -p no:cacheprovider tests/rules/reference_cases` → 179 passed, exit 0. Matches the commit claim.

F4 (part 4 — change_log claims nothing beyond the change) — PASS, with one ADVISORY.
- Appended entry (by "orchestrator (M5-T184, [ORCH-CORRECTED per G3 F1])") accurately states summary-only, the old "coverage 80/60", the round-2 basis, and "No row, value, citation or arithmetic changed" — all independently confirmed true.
- ADVISORY (not a defect): the entry says the corrected facts are "as the row opt67-cf-lot-coverage and the README already say"; the whole-lot-footprint not-settled status actually lives in row opt67-cf-max-footprint (the README does state both). Harmless imprecision; claims nothing beyond the change.

COULD NOT / OUT OF SCOPE: I did not re-open the round-2 "not settled" determination (row content byte-identical, prior-round scope) or re-verify ZR 24-11 capture presence (prior rounds). The delta solely confirms the summary now matches those rows, the README and the readings.

END-OF-REPORT

## G4 (qa-engineer)

# G4 QA GATE REPORT — M5-T184 (benchmark-options-2-3-6-7)

I am an AI agent (qa-engineer), independent and read-only. I did not produce this task. This is not a human or professional review. Reviewed at frozen SHA **b8eba3a0** on `task/wave26-envelope-constraints`, in a `git archive b8eba3a0` copy under /tmp/claude-0/t184-g4/. Later commits (48d6587b, 4d5a42d5) confirmed NOT to touch any task path.

## VERDICT: PASS

## Share (1) — my assigned checks (all run from my copy, lanes venv)
- `flock heavy-run.lock pytest -q -p no:cacheprovider tests/rules/reference_cases` → **179 passed, exit 0**.
- `ruff check tests/rules/reference_cases` → **All checks passed, exit 0**.
- `tools/modularity_check.py --check` → **exit 0** (33 pre-existing warnings in app/, apps/web, tools/; NONE in reference_cases/). Support .py line counts: check 594, step_p9 443, lib 403, render 369, all others <300 — every one <600 (S9).
- `scripts/lanes/check_lane_paths.py --coverage` → **LANE COVERAGE PASS, 10568 files, exit 0**.
- Also independently: `render.py --check` → **PASSED, exit 0** (page byte-identical, program_result_errors empty, other cases byte-stable).

## Share (2) — scenario → test map (every S pinned)
- S1 → test_the_seven_step_p9_readings_are_present_unchanged + test_a_changed_step_p9_reading_is_caught (step_p9.reading_digest_errors).
- S2 → test_step_p9_rows_name_their_readings + one-reading / wrong-pair / missing-comparer negatives (reading_pair_errors; case NOT in CASE_READINGS — Risk 3 met).
- S3 → test_every_step_p9_citation_matches_the_capture + test_uncaptured_sections_are_never_a_formal_citation + test_a_changed_law_quote_is_caught (check.citation_errors).
- S4 → test_...not_settled_rows_stay_not_known + test_a_value_where_readings_differ_is_refused + footprint tests (must_stay_not_known / portion_footprint).
- S5 → eligibility caveat + forbidden-wording positives and negatives.
- S6 → nine-bases-equal-authoritative-set + per-quantity-basis + no-mixed-basis positives and negatives.
- S7 → arithmetic recompute + 24-11 table_assertion null + 23-22/23-432 table_assertion present + changed-operand negative.
- S8 → rear_yard positive + corner-waiver-drops-condition negative.
- S9 → case_is_wired_in + page_byte_identical + prior_cases_byte_stable + support_files_under_600 + program_result_errors_empty.
No scenario is left unpinned.

## Share (3) — my own mutation probes (on-disk case, via check module, independent of the producer's tests)
Baseline validate_case = 0 errors (clean). All six turn a check RED:
1. value +1 (24180→24181) → recompute_row_errors RED, names opt2-max-residential-fa.
2. one-reading source_reference → reading_pair_errors RED ("must name BOTH its readings").
3. uncaptured section cited (23-154) → citation_errors RED ("capture file missing").
4. NOT KNOWN→value (opt3-max-dwelling-units) → must_stay_not_known RED.
5. drop owed-options row → coverage_errors RED ("row 'options-out-of-scope' not present").
6. broken row shape (drop citations key) → validate_case RED ("row keys differ from the fixed set").
None failed to go red.

## Share (4) — pin/list extensions consistent; nothing weakens an older check
- CASE_IDS extended in BOTH lib.py and the literal tuple in test_r6b_reference_cases.py (append only).
- REQUIRED_BASE_IDS: new 44-row-id entry for the case.
- test_step_p7 PRIOR_ROWS_DIGEST and test_step_p8 OTHER_CASES_DIGEST: only the digest constant + explanatory comments changed; assertion logic unchanged (verified by filtered diff — no non-comment/non-digest line changed).
- check.py grew exactly 3 lines (import step_p9 + reading_digest_errors() + case_errors()); distinct entry name avoids the existing provenance_errors (Risk 1).
- Forbidden MODULES r6b_reference_cases_step_p7.py / _step_p8.py: **0 diff** (only their test files, which are in allowed_paths, changed).
- No pre-existing case JSON or .md page changed (git diff of cases/ and pages excl. the new case = empty); step_p9 PRIOR_CASES_DIGEST pins all 12 prior cases byte-stable. render.py: 0 diff (allowed as safety only; the brief's mention of "_render.py changed" does not match the diff — correctly unchanged per packet path_notes).

## Share (5) — modularity + lane coverage: both PASS (above).

## Source verification (D-093)
- Headline arithmetic re-derived: 2.40×10075=24180; 0.40×10075=4030; 24180/680=35.56→35; 2.00×10075=20150; 0.80×10075=8060. All match.
- Round-2 rule-of-agreement correction verified at primary source: opt67-cf-max-footprint is kind=not_known, value None, quantities [], arithmetic []; opt67-cf-lot-coverage records only the agreed corner 80% ("interior/through rate not settled on both readings' words"); NO settled quantity equals 6,045 anywhere. Reading A (-23 lines 30/31/43) gives corner 80 + interior 60 + 6,045; reading B (-24 lines 28/29) gives ONLY corner 80/8,060 in its worked table — interior 60 appears in B solely at line 66 as a capture re-verification, never a worked value. Corner 80 therefore correctly SETTLED; interior correctly NOT SETTLED. The round-1 precheck's two REQUIRED findings are genuinely closed at b8eba3a0.
- 43 citations, all kind=captured, zero uncaptured-section citations (23-154/23-63/74-902/74-903/22-131..135 never a formal citation). Provenance header -19 confirmed honest: names the "sealed folder" phrase as the pinned read-only capture set, states it was NOT a sealed folder in the P7/P8 sense, discloses live ZR reads, does NOT claim "no outside access".

## Findings
- A1 (ADVISORY / accept-time, not a defect): I did not run the full api pytest suite (my share is tests/rules/reference_cases). The r2 precheck ran it green (9893 passed, 8 skipped) at producer head a4b81e74, and its patch-id matched the cherry-picked work; per R639 the orchestrator must still read CI green for the full api suite at the exact reviewed head b8eba3a0 before accept.
- No REQUIRED findings. No ADVISORY defects in the artifact.

END-OF-REPORT
