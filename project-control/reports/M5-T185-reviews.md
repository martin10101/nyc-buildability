# M5-T185 reviews (every return kept unchanged)

- One producer round (rules-engineer, worktree): commit 56b3bca7 integrated as the cherry-pick 2ab7c148 (inside the allowed paths; LF sha256 equal to the producer's return). Documents and reference-case checks only. The plan's judge (return-judge-case-5-8-9-10.md) required one correction before contract (opt8-B minimum lot area/width NOT KNOWN), carried in the packet and applied by the producer.
- G2 orchestrator self-check at the submit head: the task's files equal the producer's digests; nothing outside the allowed paths; the producer ran the whole api suite (9984 passed); the CI run at the submit head read green before submission.
- G3 data-contract-verifier at 2ab7c148: PASS, no required correction; advisories A1 (the 23-22 and 23-432 captures hold their tables as a placeholder: a capture-completion task is being sized), A2 and A3 (two source-fidelity notes; no value affected).
- G4 qa-engineer at 2ab7c148: PASS, no required correction; 212 passed; six mutation probes red; every scenario S1-S9 pinned; four advisories (read CI green for the whole api suite at the accept head: done by the accept seam).

Every reviewer is an AI agent; none is a human or professional review.

## G3 (data-contract-verifier)

G3 REVIEW — M5-T185 (benchmark-options-5-8-9-10), data-and-law share. VERDICT: PASS (no required corrections; 3 advisories).

I am an independent, read-only AI agent; this is not a human or professional review. Reviewed the pinned case `docs/reference-cases/R6B/cases/benchmark-options-5-8-9-10.json` at `2ab7c148` on `task/wave27-comparison-appendix` in /root/project/w-wave20, against the six sealed readings + comparer (session-2026-10-15a), the plan/judge, the captures in `docs/research/zr-snapshots/v1/`, and the sibling M5-T184.

WHAT I REPRODUCED (not the producer's conclusion)
1. Arithmetic (share b): recomputed all 9 steps myself on the recorded 10,075 sq ft only — 2.00×10,075=20,150; 20,150/680=29.63→29; 10,075/2=5,037.5; 2.00×5,037.5=10,075; 10,075/680=14.82→15; 15+15=30 (prose only, correctly NOT a recorded value); 29×0.25=7.25. 0 errors; the GIS 10,387.99 never enters any step (no_mixed_basis holds).
2. Citations (share b): all 33 unique cited sections are captured — snapshot file present, case `content_digest` == live `content_digest_sha256`, and the quoted words appear in `verbatim_excerpt`. 0 problems. No uncaptured section (76-131, 33-27/28/30, 23-154, 74-902/903, 22-131..135, 77-xx) is ever a formal citation; each is named in prose only on citation-less not_known rows (RISK 7 holds). Verified 33-121 plural `tables` R5D R6B = 2.00/2.00/2.00; 23-12 = 2,375/25 & 1,700/18; 25-222 R6 row = A 25 / C waiver 15; 25-241 names Queens CDs 3,4,14 — not this lot (CD 11).
3. Two-reading agreement (share a): read 26/27 (opt5), 28/29 (opt8), 30/31 (opt9-10) + comparer -25 in full. Every value row's two readings agree on value AND basis; each source_reference names both readings of its family plus -25. Reader B (opt8, -29) left 23-12 min lot area/width not_known — so the judge's REQUIRED correction (opt8-B → NOT KNOWN, recording only each half ≈5,037.5 sq ft/≈50 ft with 23-12 thresholds in prose) is correctly applied (row opt8b-min-lot-area). The comparer loosely called it "not binding"; the case correctly followed the judge, not the comparer.
4. Not-known discipline (share c): all 16 must-stay-not-known rows carry kind=not_known, no number, and a stated KIND OF GAP (storey limit one-reading; commercial rear yard; lot coverage; overlay line; select-commercial-overlay; street wall; opt8a windows/courts; opt8b aggregate +1 labelled draft; opt8b coverage-by-half; opt8b interior rear yard; opt8b min-lot-area; N1; rooming-vs-dwelling; N2; shared-housing framework; real-lot facts). Eligibility/use-permission rows (opt5 retail, opt9-10 use) record only the use-group reading and carry the "decides no eligibility and no use permission" caveat; no value from any program run.
5. Provenance fidelity (share d): the six files -26..-31 each hash to the step_p10-pinned digest, carry their marker, contain "sealed folder", end END-OF-REPORT, do NOT claim "no outside access" (the header truthfully states some sections were read live), and reproduce the reading body verbatim below a method header that adds no new value. Comparer -25 reused unchanged.
6. Summary/README/.md (share e,f): README row and case summary state only what the rows settle (incl. 23-12 "one reading only", N1/N2 open, options 4 and 11 owed); judge correction reflected. The rendered .md (125 KB) names Option 4 and option 11 as owed, keeps N1/N2 open. No positive use of Verified/compliant/complies/feasible/optimal/preferred/buildable anywhere in the JSON or .md (every occurrence is negated boilerplate; one "reduce buildable area" is descriptive, not a claim). Judge's four advisories (A1 opt5 yards cross-referenced; A2 digest; A3 opt8-A 125-ft condition; A4 opt8-B +1 as labelled draft) are all applied.

ADVISORIES (not blocking; no recorded value changes)
A1. Capture completeness (inherited, provenance): the 23-22 and 23-432 captures store their FAR/height tables as a "[table - see structured table field]" placeholder with `tables: null`, so the asserted R6B numbers (FAR 2.00/2.40; heights 30/45/55) are NOT present in the pinned capture text — they rest on the two readings' live reading of the ZR table plus `table_assertion`. The enabling clause is quoted and matches; the numeric values are not in the snapshot body. This is identical to the accepted sibling M5-T184 and to the settled real-lot/step-p6 cases, the captures are M3-T010's (forbidden to edit here), and judge A2 already flagged it. Values are correct and independently agreed. A later capture-completion task should backfill the 23-22/23-432 table payloads. (33-121, by contrast, does carry its 2.00 value in the plural `tables` payload.)
A2. Minor source-fidelity: opt910-heights source_reference says "both read 23-432 R6B standard row: 30/45/55"; reader B's 9-10 reading affirmed "residential use/bulk/density = underlying R6B" rather than writing 30/45/55 explicitly for options 9-10. Defensible (the unchanged settled R6B envelope, which reader B gives elsewhere), but consider the opt5-yards "unchanged vs option 1" framing for exact fidelity.
A3. Minor: opt910-transit-zone's "25-241 names CDs 3, 4 and 14, not this lot" sub-analysis is the producer's (correct) reading of the captured 25-241 text; reader B did not cite 25-241. The recorded value (Outer Transit Zone) and the governing-general-rule/zero-parking conclusion are jointly settled and the 25-241 citation is capture-accurate, so no value is affected.

COULD NOT CHECK: I did not run pytest/render --check (CI's job; S1/S9 digests I verified by hand match). I verified law against the pinned captures and the two readings; I did not independently re-fetch official ZR pages this session (the captures are digest-pinned and the readings already cross-checked live).

CONCLUSION: The case records a value only where both readings agree on value+basis and the section is captured; arithmetic is exact on 10,075; disagreements/eligibility/missing facts stay NOT KNOWN with their gap; provenance is faithful; the judge's correction holds; N1/N2 open; options 4 and 11 owed; no overclaiming. PASS.
END-OF-REPORT

## G4 (qa-engineer)

M5-T185 — G4 QA GATE REVIEW (qa-engineer). I am an INDEPENDENT, READ-ONLY AI agent; this is not a human or professional review. I did not produce this task.

VERDICT: PASS (G4). No required corrections from my share; four advisories (non-blocking).

SCOPE / REPRODUCTION
Reviewed 2ab7c148 (task/wave27-comparison-appendix), worked from a `git archive 2ab7c148` copy under /tmp/claude-0/t185-g4 (git-init'd so the file-enumeration tools run). lanes venv (python 3.12.3, pytest 9.0.3, ruff 0.13.0). Read packet M5-T185.json, G0, producer report, plan + judge, sibling M5-T184 review standard, step_p10 module+test, the shared check/lib/test diffs.

MY SHARE (1)-(5) — results

(1) Suite + ruff (under heavy-run.lock, from services/api of the copy):
- `pytest -q -p no:cacheprovider tests/rules/reference_cases` → 212 passed, exit 0.
- `ruff check tests/rules/reference_cases` → All checks passed, exit 0.

(2) Scenario→test map — every S1–S9 is pinned (none unpinned):
- S1 → test_the_six_step_p10_readings_are_present_unchanged + test_a_changed_step_p10_reading_is_caught
- S2 → test_step_p10_rows_name_their_readings + …naming_only_one_reading_is_refused + …wrong_pair_is_refused + …shared_row_without_the_comparer_is_refused
- S3 → test_every_step_p10_citation_matches_the_capture + …uncaptured_sections_are_never_a_formal_citation + …changed_law_quote…is_caught (check.citation_errors enforces snapshot existence + content_digest_sha256 match + official_url match + quote-in-verbatim_excerpt + table_assertion field match — verified by reading the function, not just existence)
- S4 → …not_settled_rows_stay_not_known_with_a_kind_of_gap + …value_where_the_readings_differ_is_refused + …program_result_errors_is_empty
- S5 → …eligibility_and_meaning_rows_carry_their_caveats + 2 negative tests + …no_forbidden_present_tense_wording + …not_captured_phrase_is_caught
- S6 → …nine_bases_equal_the_authoritative_set + …every_quantity_carries_one_of_the_nine_bases + 2 negatives + …recorded_and_gis_areas_are_never_combined
- S7 → …arithmetic_recomputes + …plural_tables_rows_carry_table_assertion_null + …23_22_and_23_432…use_the_table_assertion + …changed_operand_is_caught
- S8 → …rear_yard_rows_name_condition_and_scope + …corner_waiver…drops_its_condition_is_refused
- S9 → …case_is_wired_in + …page_is_byte_identical_to_the_renderer + …other_cases_rows_are_byte_stable + …support_files_stay_under_600_lines

(3) Mutation probes — ran in-process against the real checker (the heavy-run.lock was held ~8 min by another session's full-suite run, so I probed by calling check.validate_case/citation_errors/coverage_errors/lib.load_case directly; pristine file validated CLEAN before and after). ALL SIX turn a check red:
1. recorded value 20150→20151 → RED "recomputes to 20150.00 but the case records 20151".
2. opt5-commercial-far one reading (drop -27) → RED "an option row must name BOTH its readings".
3. opt910-residential-far cite uncaptured 76-131 → RED "capture file missing: …zr-76-131.snapshot.json".
4. opt8b-min-lot-area not_known→value → RED "must be 'not known', not 'value'".
5. drop options-out-of-scope row → RED coverage "the work order's row 'options-out-of-scope' is not present".
6. broken JSON shape → RED load_case raises JSONDecodeError.

(4) Pins extended consistently; nothing weakens an older case's check:
- CASE_IDS: lib (14th id) and the literal tuple in test_r6b_reference_cases.py both +1/-1.
- REQUIRED_BASE_IDS: new 49-id entry added.
- p7 PRIOR_ROWS_DIGEST, p8 OTHER_CASES_DIGEST, p9 PRIOR_CASES_DIGEST: each exactly 1 line changed (digest constant only; blob formula and excluded-case unchanged); new step_p10 carries its own OTHER_CASES_DIGEST. step_p6 REACH_ROWS_DIGEST untouched; no len-count pin exists. Only benchmark-options-5-8-9-10.json changed among the 14 case JSONs (git --stat), so the 13 existing cases are byte-identical to the pre-commit state and the recomputed digests reflect only the addition.

(5) `tools/modularity_check.py --check` → exit 0 (0 failures; no finding for any reference_cases file; check.py 597 lines, step_p10 400 — both <600). `scripts/lanes/check_lane_paths.py --coverage` → exit 0 (LANE COVERAGE PASS, 10646 files).

SUPPORTING CONFIRMATIONS
- Six provenance files -26..-31: sha256 match the pinned digests; each contains "sealed folder", ends END-OF-REPORT, and does NOT claim "no outside access". Comparer -25 untouched by the commit (forbidden to edit).
- Judge REQUIRED correction applied: opt8b-min-lot-area kind=not_known, value=None; "not binding" appears only as reader A's divergence, not a recorded value; records the agreed ~5,037.5 sq ft/~50 ft halves and the 23-12 thresholds (2,375/1,700) in prose.
- N1 (opt8-which-meaning) and N2 (opt10-distinct-meaning) kept not_known with "decides neither meaning" caveats; options 4 and 11 named as owed in options-out-of-scope.
- No positive overclaim: every "complies/buildable/optimal/feasible/Verified" occurrence is a negated disclaimer (the proven convention; matches the M5-T184 standard). The summary/README keep the one-reading 23-12 item as not-settled (the analogue of M5-T184 F1 is clean here).
- render.py not in the commit (byte-identical); page byte-identical to render_page (S9 test passes).

ADVISORIES (non-blocking)
A1. I did not run the full api suite (brief scoped me to reference_cases; lock contended). The producer's "9984 passed" is CI's responsibility — the orchestrator must read CI green for the whole api suite at the exact accept head (D-090 R639) before accepting.
A2. Deep per-row two-reading/law re-derivation and the D-094 R007/R075/R084/R102 requirement verification are the data-contract-verifier (G3) and directive-compliance-verifier passes, not mine; I verified the harness that enforces those rules is correctly wired and fails closed.
A3. Mutation probes were executed in-process rather than via full pytest reruns because the heavy-run lock was held by a peer full-suite run; the in-process checker is the same code the tests call. The scoped suite (212) was run under the lock.
A4. I git-init'd the archive copy so modularity/lane tools (which need `git ls-files`) run; this does not alter file content.

RECOMMENDATION: record G4 as PASS. Before acceptance, confirm CI green for the full api suite at the accept head (A1).

END-OF-REPORT
