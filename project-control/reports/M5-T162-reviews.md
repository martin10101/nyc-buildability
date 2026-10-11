# M5-T162 reviews (every return kept unchanged)
- G3 code-reviewer at cc794c74: PASS (two advisories, no action: a pre-existing lint gap outside this task, verified and logged as backlog DB-240; a malformed limit label is not named, the documented direction)
- G4 qa-engineer at cc794c74: PASS (two advisories, no action: S6 is proven by the full suites and the HTML line diff; the PDF and the CI suites are the orchestrator's); 1658 passed; its own three mutations fail

Both reviewers are AI agents; neither is a human or professional review.

## G3

<!-- saved unchanged by save_return.py from agent-a566bffaaf2f6c1f9.jsonl, entry 2026-10-11T10:16:38.287Z, sha256 ba606b49a587566cdd917da197d3ac0c44e0fd58a3a7f8fb879c8c1e2029450b -->
G3 CODE-REVIEW GATE — M5-T162 (report wording after M5-T157)
Reviewer: code-reviewer (independent, read-only). I am an AI agent; this is not a human or professional review.
Frozen head: cc794c74979d0fa42a3aec35906bedf23a77ef7a (task/wave23-density-zoning-lot, worktree /root/project/w-wave20). Base: 4b791266.

VERDICT: PASS (two ADVISORY notes, no REQUIRED defects)

=== WHAT I CHECKED (reproducible) ===
1. SCOPE — `git diff --name-only 4b791266..cc794c74`: exactly the 5 allowed code/test files + project-control/reports/M5-T162-producer-report.md (allowed) + 4 ledger files (gates/M5-T162-G0.json, reports/M5-T162-G0.md, state.json, tasks/M5-T162.json) from orchestrator commits. Grep for any path outside allowed+project-control returned none. CLEAN.

2. IMPORT CYCLE — none. readers.py imports unit_limit_text at module load; coverage.py imports both at load; unit_limit_text.py imports readers only at call time inside functions (shown_legal_unit_limits, _withheld_legal_unit_limits). unit_limit_text top-level imports only collections.abc.Mapping. Confirmed live: all 101 report tests import and the full report renders with no ImportError.

3. PRIVATE-NAME ACCESS ACROSS MODULES — none in production. readers→unit_limit_text.legal_unit_limit_item (public, __all__); coverage→unit_limit_text.shown_legal_unit_limits (public, __all__); unit_limit_text→readers.ANSWER_NAMES/answer_block/present_values/withheld_values (all public in readers.__all__). The only _private cross-access is in the test file (unit_limit_text._limit_program), which is acceptable.

4. CORRECTNESS FOR EVERY INPUT STATE — verified by the passing suite PLUS my own independent probes against the head code and the full before/after HTML diff of the benchmark:
   - benchmark (standard shown Conditional=29, affordable+senior withheld): effect = "The legal apartment limit is shown as a conditional ceiling for standard residences; it is not known for qualifying affordable housing or qualifying senior housing." I re-derived the two withheld reasons/resolvers from the fixture value_states and confirmed each is kept, labelled by program (fixes the old "only first reason survived" bug). "29" absent from the effect (number stays on the derivation table).
   - all three withheld: effect = "No legal apartment limit is shown."; coverage F = Not yet.
   - none withheld (standard shown only): no "Legal apartment limit" open item; coverage F = Partly.
   - one withheld: effect names only that one program; reason/resolves single-program.
   - absent OR malformed (non-mapping) allowance block: shown programs == [], no open item, coverage Not yet — driven by actual-present values, no truthiness shortcut.
   - shown limit's own state conditional / non-conditional ("settled") / no value_states entry: "conditional ceiling" said ONLY when value_states[key].way=="conditional"; otherwise "shown for …". Probe P5 (state deleted) → conditional False. The scope-correction fix (read the state, don't default) is correct and directly tested.

5. PAGE-1 vs OPEN-ITEMS AGREEMENT — decision_open_items picks the legal_unit_limit item carrying the new effect (probe P2); S5 guard slices both the decision-summary and open-items regions and asserts neither denies a shown limit. The old _EFFECTS["legal_unit_limit"] entry was removed safely (that category is no longer routed through put(); _ORDER still carries it and by_category is set directly).

6. FULL REPORT HTML before/after (build_report_html on the benchmark, 4b791266 vs cc794c74, tag-split diff) — EXACTLY 5 changed regions, nothing else moved:
   - decision-summary "Legal apartment limit:" effect (old→new); status chip "Pending verification" UNCHANGED.
   - coverage "Partly" gains "Legal unit limits (the limit for standard residences is shown as a conditional ceiling)".
   - coverage "Not yet" loses "Legal unit limits".
   - open-items table: effect cell + resolver cell (now both programs labelled).
   - open-items reason-row: now both withheld reasons labelled by program.
   No figure, no status label, no other text changed. status_label stays "Pending verification" (probe P4).

7. PLAIN USER TEXT — all strings are plain English; program names come from the human label portion via _limit_program; no keys, no "legal_unit_limit", no value_states, no task ids leak into any user-facing text.

8. MODULE BOUNDARIES — `python tools/modularity_check.py --check` in the worktree (HEAD=cc794c74, the three modules clean on disk vs commit): exit 0, failures 0, 32 pre-existing warnings, NONE naming readers.py/coverage.py/unit_limit_text.py. readers.py stayed a reader with thin wiring (606 lines, not flagged); unit_limit_text.py 163; coverage.py 133. The extraction kept readers.py off the 600 warn line as the scope correction intended. (Note: modularity_check needs a git tree — it errors in a `git archive` export; I ran it in the worktree after confirming the three files on disk byte-match cc794c74 and HEAD==cc794c74.)

=== REQUIRED CHECKS (git-archive export of cc794c74, from services/api, /root/project/lanes-runtime/venv/bin/python, PYTHONDONTWRITEBYTECODE=1) ===
- `python -m pytest -q -p no:cacheprovider tests/drawings/report` → 101 passed in 41.36s. EXIT 0.
- `python -m ruff check .` → EXIT 1: 2 errors, BOTH in app/rules/coverage/render_coverage_matrix.py (F841 unused `column_order` line 70; E501 line 94). Ruff on the three task modules + app/drawings/report/ + tests/drawings/report/ → "All checks passed!" EXIT 0.

=== FINDINGS ===
F1 (ADVISORY) — Pre-existing whole-tree ruff failure, NOT this task. `ruff check .` is red at the frozen head due to app/rules/coverage/render_coverage_matrix.py (F841 L70, E501 L94). I reproduced the identical two errors at the BASE 4b791266, so they predate M5-T162 and the file is a forbidden_path (services/api/app/rules/) the task cannot touch. M5-T162's own modules/tests are ruff-clean. This is not a defect in the task diff, but the packet's documented command `cd services/api && python -m ruff check .` is the api CI first step and will stay red until a separate task fixes render_coverage_matrix.py. ORCHESTRATOR ACTION: ensure the merged head is CI-green (R639) by resolving this unrelated red before/at merge — it is outside M5-T162's scope.

F2 (ADVISORY, low severity) — unit_limit_text._limit_program returns None for a label not matching "Legal dwelling-unit limit, ", so a *shown* legal-unit-limit value carrying a malformed label is dropped from the shown set (probe P1 → []). In that corrupt-data corner the coverage/open-item could read "no/No legal apartment limit is shown" while the derivation table still prints the (malformed-label) figure — the same class of contradiction this task fixes. It cannot arise from the contract fixtures (labels are well-formed), and the requirement explicitly endorses inventing no program for a malformed value, so this is the documented conservative direction, not a bug. Noting for awareness only; no change required.

=== WHAT I COULD NOT CHECK ===
- tests/cad and tests/journey (S6's wider assertion) — out of my G3 brief (I ran tests/drawings/report per the review brief); these belong to the qa-engineer G4 pass. The before/after HTML diff shows only the intended lines move, so report-consumer regressions are unlikely.
- Directive-requirement-to-source re-derivation (D-090/D-093/D-094 requirement IDs) — that is the directive-compliance-verifier's pass, not G3.
- Primary legal sources behind NB-05-special-density-area.json — I confirmed the benchmark fixture's shown/withheld states and reasons match the report output, but did not re-verify the underlying ZR interpretation (research/verification scope).

END-OF-REPORT

## G4

<!-- saved unchanged by save_return.py from agent-a7fd299f5136e967b.jsonl, entry 2026-10-11T10:18:25.792Z, sha256 b1bd16be3ecda01b85154741db06aab4409981876508208470b2d34ab5052aae -->
G4 (qa-engineer) INDEPENDENT REVIEW — M5-T162 — VERDICT: PASS

I am an AI agent; this is an automated independent gate, not a human or professional review. Read-only: I edited no repository file (all work in a `git archive` export under my scratch folder). Frozen head cc794c74 on task/wave23-density-zoning-lot.

WHAT I DID
Worked the expected texts from the benchmark document (packages/.../recorded_215_16_northern_journey.json) BEFORE reading the change: legal_unit_limit_standard is a shown value (29.0) with value_states.way="conditional"; legal_unit_limit_qualifying_affordable and _qualifying_senior are way="withheld", each with its own distinct reason and resolved_by. So the correct effect names standard as a conditional ceiling and the two programs as not known; the reason row and resolver must keep BOTH withheld limits (not just the first); coverage "Legal unit limits" must read Partly, not Not yet. The implementation matches this independent derivation.

REQUIRED SUITES (lanes venv, PYTHONDONTWRITEBYTECODE=1, -p no:cacheprovider, from export services/api; DIRECT exit codes)
1. `pytest -q tests/drawings tests/cad tests/journey` -> 1658 passed, 6 skipped, 1 warning in 114.72s; SUITE_EXIT=0.
2. `pytest -q tests/drawings/report/test_report_unit_limit_text.py -v` -> 10 passed in 0.46s; NEWTEST_EXIT=0.

SCENARIO COVERAGE (each fails if broken; expected texts from scenarios + document, not from a program run)
- S1 test_s1_benchmark_standard_shown_affordable_and_senior_withheld: effect string asserted from scenario text; the two withheld reasons/resolvers read from the fixture (`affordable["reason"] in item["reason"]`, etc.), program labels asserted, "29" asserted absent from effect. OK.
- S2 test_s2_every_limit_withheld_says_none_shown: forces standard withheld; effect == "No legal apartment limit is shown.", coverage F == NOT_YET. OK.
- S3 test_s3_no_withheld_means_no_open_item: deletes both withheld; no item; coverage PARTLY. OK.
- S4 test_s4_coverage_partly_names_the_shown_limit_as_conditional: PARTLY + note "the limit for standard residences is shown as a conditional ceiling". OK.
- S5 test_s5_guard_no_denial_while_a_limit_is_shown: builds HTML, asserts neither denial phrase on the decision-summary slice nor the open-items slice. OK.
- S6 (regression-only, no single test): satisfied by the full suite (1658 passed) + the HTML line-diff below showing only allowed lines moved. Plus test_report_pages.py updated to assert the new effect and that "No legal apartment limit is shown." is absent.

THREE OWN MUTATIONS (each run once in the export, then restored; files restored to pre-mutation sha256)
- M1 dropped the "...it is not known for..." clause in legal_unit_limit_item -> 5 tests FAIL incl S1 ("...standard residences." != "...qualifying senior housing.").
- M2 coverage else-branch set to PARTLY when none shown -> test_s2 and the malformed/absent test FAIL ("Partly in this report" != "Not yet in the program").
- M3 treated a no-state shown limit as conditional (`way=="conditional" or state is None`) -> test_no_value_states_entry_is_shown_plainly FAILS (gained "as a conditional ceiling"). Confirms "conditional" is read from the value's own state, not defaulted.

BENCHMARK REPORT HTML DIFF — 4b791266 vs cc794c74 (both rendered via build_report_html on the byte-identical fixture; visible text, 381 lines each). Every differing visible line, and all are within the allowed set (the two texts + the item's reason row + resolver):
- Line 30 (decision summary "most important open items") and line 249 (open-items page): EFFECT text changed from "No legal apartment limit is shown." to "The legal apartment limit is shown as a conditional ceiling for standard residences; it is not known for qualifying affordable housing or qualifying senior housing." Title "Legal apartment limit" and status "Pending verification" unchanged; decision summary and open-items page agree.
- Lines 34-35 (coverage groups): "Legal unit limits" moved from the Not-yet group to the Partly group with note "(the limit for standard residences is shown as a conditional ceiling)" — the COVERAGE text change, inserted in correct letter order.
- Line 250 (resolver cell): was affordable's resolver only; now both, labelled by program.
- Line 252 (reason row): was affordable's reason only; now both, labelled by program (restores the senior reason the old de-dup dropped).
No figure moved: the derivation line "20,150 / 680 = 29.63 ... 29" (line 329) is byte-identical. "No legal apartment limit is shown" count base=2 -> frozen=0; "the legal unit limit is withheld" 0 in both.

OTHER CHECKS
- "Shown" decided only from present values: shown_legal_unit_limits reads readers.present_values (excludes way=="withheld") filtered to keys containing "legal_unit_limit" with a readable program label; absent/malformed answer block -> answer_block returns {} -> no shown (test_malformed_or_absent confirms). No truthiness test on an optional fact; booleans are explicit equality/None/isinstance. Conditional read from value_states[key].way.
- Plain text: grep of the rendered visible report for internal tokens (legal_unit_limit, value_states, M5-T162/T157, gap_kind, resolved_by, category) -> 0 hits.
- Provenance (D-093): opened the primary ZR 23-52 snapshot — 23-52(a)(2) gives qualifying senior housing no dwelling-unit factor and 23-52(b) sets factor 680 with >=0.75 rounding up; this makes the benchmark's senior withheld reason and the standard 29 faithful. T162 reads these from the document verbatim and invents no state. Unresolved inputs stay unresolved (affordable/senior remain not known; standard stays conditional).

FINDINGS
1. ADVISORY: S6 has no dedicated test; it is proven here only by the full-suite pass + the HTML line-diff. Acceptable (S6 is a regression guarantee), but a future reader relies on the suite, not a named assertion.
2. ADVISORY: I did not render the actual PDF/browser or run the api CI job, full services/api pytest, web, or security suites (forbidden / out of scope); those run in CI on the accepted head (R639). Not a blocker — the report HTML is the shared source both the PDF and web preview read, and it is exercised by the suites and the S5 guard.

No REQUIRED findings. The two report texts now follow the document, the reason row keeps each withheld limit's own reason, the decision summary and open-items page agree, and no figure/status label/other visible line changed.

END-OF-REPORT
