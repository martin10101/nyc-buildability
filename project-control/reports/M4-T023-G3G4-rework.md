# M4-T023 G3/G4 - independent review of the reworked register (code-reviewer, read-only)

Reviewed head: `1cdad2c07e825fff3a3344850466cad7d8accf18` (branch `task/M4-T023-zoning-rule-review-register`, PR #452, review copy `/root/project/rv-T023`). The reviewer is an AI agent that did not produce the work; this is an agent review, not a human or professional review. The first build's review (at `c55b7c47`, a different reviewer agent) is `project-control/reports/M4-T023-G3G4.md`.

## Verdict: G3 PASS, G4 PASS at `1cdad2c0`. No must-fix finding. One optional note left open.

The review was made in two steps by the same reviewer:

1. **Full review at `326c8560`** (the rework for the owner's two audits): G3 PASS and G4 PASS, with two should-fix findings and two notes.
   - F1 (should fix): five cited tests in three entries lived in a test file the entry did not link or bind. **Applied in round 3** (commit `9cb147a3`): the checker now requires every cited test function to be defined in a linked test file and the bound digests to equal the linked files; the three entries link and bind the second file.
   - F2 (should fix): GUIDE.md named the run logs `.log`; they are `.txt`. **Applied.**
   - F3 (note): "Planned, not built" held items that were existing behaviour or facts about the law. **Applied**: all 49 items were sorted; 45 remain, missing behaviour only; 4 moved to "tested", 4 to "in the program but no test checks it", 2 removed as already stated.
   - F4 (note): the automatically loaded instructions stand at about 9,922 of 10,000 tokens after the one-line standing instruction. No change; recorded.
   - Its answer to the question whether a stored decision edited after the fact is detected: no check detects it; it relies on review of each change, which GUIDE.md states.
2. **Check of the corrections at `1cdad2c0`**: every point confirmed; G3 PASS and G4 PASS at that head.
   - Its one new note (optional): the first line of each run log reads "(M4-T023)", an internal task number, in a file linked from the table. The rendered table and pages hold no internal numbers. Left as it is; recorded here for the owner.

Read by the orchestrator, not by the reviewer: the full `services/api` suite, run alone at `9cb147a3` on this branch: 8044 passed, 8 skipped, exit 0. The producer's own full run had one failure in an unrelated timing test in its pre-fix form; the producer's worktree does not contain the integration branch's fix for that test (pull request 443), and this branch does.

Both returns follow unchanged (copied from the session transcript by script).

---

## Return 1: full review at `326c8560`

```
# GATE REPORT — M4-T023 zoning-rule review register (G3/G4), rework review

**Reviewer:** code-reviewer (independent; did not produce this work). Read-only.
**Pinned head:** 326c85603436aa0b367649fee71926485fa954e8, branch task/M4-T023-zoning-rule-review-register (PR #452), read at /root/project/rv-T023.
**VERDICT: PASS for G3 and PASS for G4** at the pinned head. No must-fix defect. Three should-fix/note findings (F1 should-fix; F2 should-fix; F3, F4 notes), none blocking. The per-requirement directive attestation for D-090-R362..R443 is the directive-compliance-verifier's pass; this report covers the build, the re-write diff, the human-review design, the behaviour/test evidence, wording, the standing instruction, scope and quality, and reproduces the producer's mutation proofs.

## Reproductions (all green, run at the pinned head)
- `pytest -q -p no:cacheprovider tests/rules/test_zoning_rule_review_register.py tests/rules/test_coverage_matrix.py` → **55 passed**.
- `ruff check .` (services/api) → **All checks passed!** (exit 0).
- `render_review_register.py --check` (repo root) → **register check PASSED (no issues)** (exit 0).
- `tools/modularity_check.py --check` → **exit 0** (only pre-existing warnings on unrelated files; the three register source files are listed under the warn line).
- `tools/context_budget_check.py` → **PASS**; eager total **9922 tok / 10000 cap** (see Part F / F4).
- Re-ran the 7 evidence test files one at a time; counts match the logs AND register.json exactly: test_r1_r12_residential_far 15, test_r1_r2_height_setback 110, test_r3_r4_height 90, test_r5_height_setback 47, test_r6b_coverage_yard_units 88, test_r6b_far_heights 32, test_rules_engine 36 — all passed.
- `git diff --stat 52e3d8a4 HEAD -- services/api/app/rules/rulesets services/api/tests/rules` → only test_zoning_rule_review_register.py changed; **all 23 rule files and all 7 bound rule-test files are byte-identical** between the tested commit 52e3d8a4 and HEAD, so "Passed (52e3d8a4)" is true of the current files. `git status` clean after every run (the test writes only to pytest tmp_path; nothing left in the repo).

## PART A — nothing lost or changed by the register.json re-write (c55b7c47 → HEAD)
Compared entry-by-entry on the first-reviewed fields (rule_id, rule_file, rule_file_sha256, rule_version, law, applicable_from/to, applies_where, exceptions, interpretation, example.inputs/expected.values/expected.basis_kind/expected.basis/actual/agrees, code_links, test_links, gaps, revision, last_changed, title, family, draft_note). Same 23 rule_ids; history unchanged (23 `created` events). The ONLY differences in first-reviewed fields are the three expected notes — no other change:
1. **r2x-r4-residential-far :: exceptions[0]** — F5 applied: "…(1.50 in R4, 1.00 in R2X)…" → "…(R4 1.50; R2X unchanged at 1.00)…". RIGHT: R4 qualifying 1.50 vs standard 1.00 is "higher"; R2X qualifying equals standard 1.00, so "unchanged" is correct.
2. **r5a-height :: example.expected.basis** — F1 applied: "ZR 23-421 lists R5A among the covered districts…" → softened to state the quoted excerpt shows the 25/35 values and that the R5A enumeration lives in this capture's notes and the sibling R1/R2 and R3/R4 captures. RIGHT against the capture (quoted text carries 25/35; enumeration is in notes).
3. **r5b-height :: gaps** and **r5d-height :: gaps** — F2 applied: a gap line added that the R5B→35 ft / R5D→45 ft statement-to-district mapping is researcher-assigned from the ZR 23-422 table row and the quoted sentence is a generic "in the district indicated" statement, so the mapping is unconfirmed. RIGHT against the capture.
All sha/version pins, law digests, revisions, and every other first-reviewed field are byte-identical. New entry key `behaviour` added (expected for S14); `human_review`/`automated_tests` internal shapes changed (expected for S12/S15). **No loss, no unexpected change.**

## PART B — the new human-review design (S12, S13)
Read `derive_human_review` and `human_review_errors`. Probed in memory:
1. "Correct" decision, rule file changes + entry digest updated same edit → **(False, 'Needs re-review')**, original decision kept. Detected.
2. only a cited law-capture digest changed → **(False, 'Needs re-review')**. Detected.
3. only the revision moved → **(False, 'Needs re-review')**. Detected.
4. hand-typed `applies_to_current`/`verdict` differing from derived → **refused** ("does not match the recomputed value"). Detected.
5. decision missing any one of reviewer_name / review_date / reviewed_revision / reviewed_conditions / reviewed_rule_file_sha256 / reviewed_law_digests → **refused** in every case. Detected. (reviewer_role and comments are optional — matches S6.)
6. a decision **edited after the fact** (original wording changed) → **NOT detected by any check.** The checker has no git/commit access (confirmed: no subprocess/git in check_review_register.py); it reads only the current file. An after-the-fact edit of a stored decision's wording that keeps a consistent reviewed identity would pass. This is the same class as the append-only history limit — it relies on the GUIDE "Append-only is a standing review duty" (F4 of the first review) plus code review, which GUIDE.md states. Stated plainly here as the honest answer.
- Confirmed the build check passes for an entry with **no decision** and for one reading **"Needs re-review"** (test_s13_* both green; --check green). Nothing in the program consumes the verdict: only the test imports review_register; no engine/registry/evaluator/scenario code references human_review or applies_to_current. **All 23 entries carry decision=null, verdict="Not reviewed", applies_to_current=null** (verified directly).

## PART C — planned / committed / tested (S14)
Mechanical check over all 23 entries: **104 tested items, 157 named-test references, 0 items without a test_ token.** 152/157 named functions exist in the entry's OWN test_links file. **5 references (3 entries) name functions that exist in the suite but NOT in the entry's own test_links/evidence file** — see F1. By reading (5 R6B entries + the 3 flagged FAR entries), opening each named test and the rule file:

| Entry | items | Faithful? |
|---|---|---|
| r6b-height | 5 tested / 0 untested / 3 planned | YES — test_c1_benchmark_heights_from_the_one_lookup etc. in test_r6b_far_heights.py genuinely assert the 5 heights, overlay note, fail-closed. Note (F3): "Planned, not built" lists "R6B heights do not depend on street width" (a correct characteristic, not missing behaviour) and "special districts are sent to professional review" (already built+tested). Rule-file deeper limitations 23-434/436/44 not individually surfaced (minor). |
| r6b-dwelling-units | 5 / 0 / 3 | YES — test_c12_benchmark_units_29_with_the_formula asserts /680 + .75 rounding → 29. Note (F3): planned item "qualifying-affordable dividend is sent to professional review" is built+tested (tested item 4). |
| r6b-lot-coverage | 4 / 0 / 2 | YES — test_benchmark_corner_lot_coverage_is_100_percent asserts 100% corner, 80% interior. Note (F3): planned "special districts sent to professional review" is built+tested. |
| r6b-qualifying-housing-far | 4 / 0 / 1 | YES — all named tests (test_c2_benchmark_standard_and_qualifying_allowances, test_r6b_has_no_wide_street_increase) are in-file (test_r6b_far_heights.py); assert 2.40 → 24,180 and no wide-street increase. |
| r6b-rear-yard-corner-waiver | 5 / 0 / 2 | YES — test_benchmark_rear_yard_is_not_required_within_100_ft_of_the_corner asserts 0 within 100 ft at ≤135°. |
| r5-residential-far | 4 / 1 / 2 | Behaviour YES, traceability NO (F1): item 4 cites test_as9_r5_* which live in test_r1_r12_residential_far.py, but the entry links/evidences only test_rules_engine.py. committed_untested item honest ("no test found"). |
| r6-r12-residential-far | 4 / 0 / 2 | Behaviour YES, traceability NO (F1): items 1–2 cite test_c2_benchmark_standard_and_qualifying_allowances (in test_r6b_far_heights.py); item 2's ONLY cited test is cross-file. Entry links/evidences test_r1_r12_residential_far.py. |
| r6-r7-r8-wide-street-conditional-far | 4 / 0 / 2 | Behaviour YES, traceability NO (F1): item 3's only cited test test_r6b_has_no_wide_street_increase is in test_r6b_far_heights.py, not the linked file. |

Nothing listed as `tested` is fabricated — every cited function exists and passes and exercises the stated behaviour; nothing under `planned` is already-missing that is actually absent (the F3 items are mislabelled, not false).

## PART D — the test result (S15)
All 7 evidence logs re-run (above); command/date/exit/counts match the logs and register.json for every entry. Rule files and the 7 bound test files are byte-identical at HEAD vs 52e3d8a4, so the recorded "Passed (52e3d8a4)" is true of the current files (confirmed by --check: tested_rule_file_sha256 and tested_test_file_sha256s all match live files). In-memory probes: setting a recorded test-file digest to zeros with status "Passed" → checker demands **"Not run"** (RED); same for a rule-file digest; setting status to "Not run" → GREEN. REGISTER.md table "Tests" column renders `<status> (<short8>) [log](evidence/…)` and **never a count of test files**. The result is a separate top-level field and a separate column from the human-review block; nothing derives one from the other. **S15 binding is complete for each entry's own linked test file; the cross-file behaviour citations in F1 are NOT covered by the entry's digest binding** (a break in test_r6b_far_heights.py would not flip r6-r12-residential-far's status to "Not run").

## PART E — wording (S16) and the reader
REGISTER.md intro: "covers the 23 rule-definition files the program has today … **not** complete coverage of the New York City Zoning Resolution." Agent reviews are called agent reviews ("Agent reviews of this register are agent reviews, not human or professional reviews"); every row reads "Not reviewed"; the unreviewed-draft note is on every detail page. **No internal task/directive/scenario IDs** appear in REGISTER.md, HISTORY.md or any rules/*.md (grepped M#-T#, D-0##, R3##/R4##, G5, S1# → none). "professional review" appears only describing the rule engine's fail-closed escalation ("special districts send the result for professional review"), consistent with ADR-007 — not a claim the register was reviewed; nothing reads as a human review or as "legally correct." Three detail pages (r6b-height, r6b-dwelling-units, r2x-r4-residential-far) read in plain English end-to-end for a non-coder. GUIDE.md documents the revision policy (interpretation/applicability/implementation/evidence move a revision; layout/wording does not), the append-only duty (F4), the 6-step session update, and how a human verdict is recorded. **F3 of the first review is applied and real**: test_editing_a_rendered_file_is_caught_by_the_checker now renders to a temp folder, tampers r6b-height.md on disk, and runs checker.rendered_errors, asserting a "stale" error (green here). **F2/F4 notes also applied** (r5b/r5d gap line; append-only standing duty).

## PART F — the standing instruction
CLAUDE.md principle 20 (added by the orchestrator in 4cd2fc4a): "20. Zoning-rule review register (D-090-R379): every session that adds or changes zoning-rule behavior must update the register (`docs/zoning-rule-review/`; how: its `GUIDE.md`) as part of the same change. No session enters a human verdict." — one short line, matches source-042 R379, does not copy the register (R380). `context_budget_check.py` → **PASS**, eager total **9922 tok / 10000 cap** (see F4 — passes but slim).

## PART G — scope and quality
- Rework commit 8ac78417 `--stat`: touches ONLY allowed_paths (docs/zoning-rule-review/**, services/api/app/rules/review_register/**, test_zoning_rule_review_register.py, the producer report). ✓
- PR diff `9c90ffbf..HEAD`: allowed_paths + CLAUDE.md (orchestrator standing instruction, per path_notes) + project-control records (gates/reports/directives/state/task, orchestrator-owned). **No rule file, rule engine, registry, evaluator, coverage, capture (research/_zr_snapshots), workflow/.github, dependency manifest or database/supabase file.** ✓
- Source sizes: render 420, check 468, test 501 lines (register.json 2864 = data). All under 600; modularity --check exit 0. Each module keeps one responsibility (render / validate / test); the checker/renderer import nothing from the rule engine — the only engine coupling is in the test via the public RuleRegistry().load().evaluate() path. ✓
- Test file: no network, no order dependence, no globals/sleep; mutation cases use copy.deepcopy + monkeypatch + tmp_path; tree clean after runs. ✓
- **Five producer mutation proofs reproduced** (in memory / via the passing on-disk tamper test): S4 rule_file_errors RED; S6 human_review_errors "refused" RED; S8 rendered_errors "stale" RED on a tampered temp copy (test green); S12 derive→(False,'Needs re-review'), stored "Correct" refused, original decision kept; S15 RED with "Passed" → GREEN with "Not run". All confirmed.

## Scenario results
- **S12 — met.** Original decision stored and never overwritten; applies_to_current + verdict derived; (a)–(d) proven (tests + my probes); touching the register cannot keep an old "Correct"; history events human_verdict_recorded/flagged_for_re_review exist. (S6 read with S12; S12 governs — stored original not overwritten.)
- **S13 — met.** Build check passes for an updated entry with no decision and for one reading "Needs re-review"; nothing requires a human decision; GUIDE says it in one sentence ("The check enforces record-keeping only").
- **S14 — met with a should-fix.** Three lists told apart on every page and enforced by behaviour_errors; behaviour is genuinely tested where claimed. Should-fix F1: 3 entries cite tests outside their own test_links/evidence (checker only requires a "test_" substring). Note F3: a few "Planned, not built" items are actually characteristics or already-built escalation.
- **S15 — met.** Result (status/commit/date/command/counts/evidence) bound to rule+test digests; checker demands "Not run" on drift; table shows status + short commit + log, never a count; kept apart from the human block. (Cross-file gap under F1 noted.)
- **S16 — met.** Coverage wording, agent-reviews-as-agent-reviews, F1–F5 all applied; no internal IDs rendered; nothing reads as a human/professional review or "legally correct."
- **S1–S11 — all still hold after the rework.** S1 reads-alone ✓, S2 fixed structured fields ✓, S3 one-per-rule + links exist ✓ (23==23, --check green), S4 rule-change fails build ✓, S5 actual computed through the engine ✓ (23-entry re-derivation test green), S6 verdict rules ✓ (all 23 "Not reviewed"), S7 append-only enforced-where-possible + honestly disclosed ✓, S8 rendered byte-identical + no orphan ✓, S9 gaps honest ✓, S10 code-only behaviour reported in GUIDE + report (modules exist) ✓, S11 no gate/db/engine change ✓. None broken.

## Findings
- **F1 (should fix) — cross-file test citations break per-entry traceability and the S15 digest binding.** Files: services/api/app/rules/review_register/register.json (entries r5-residential-far, r6-r12-residential-far, r6-r7-r8-wide-street-conditional-far) and check_review_register.py (behaviour_errors). Five `behaviour.tested` references name functions that exist and pass but live in a test file NOT in the entry's `test_links` / `automated_tests.evidence` / `tested_test_file_sha256s`: r5-residential-far cites test_as9_r5_no_longer_carries_footnote_cap_r1r2r3_does and test_as9_r5_far_values_unchanged_and_match_snapshot (in test_r1_r12_residential_far.py, but the entry links test_rules_engine.py); r6-r12-residential-far cites test_c2_benchmark_standard_and_qualifying_allowances (in test_r6b_far_heights.py; it is item 2's ONLY cited test); r6-r7-r8-wide-street-conditional-far cites test_r6b_has_no_wide_street_increase (in test_r6b_far_heights.py). The checker's behaviour_errors only requires the substring "test_", so the build does not catch this, and a change to the file actually containing the cited test would not flip that entry's status to "Not run." The behaviour is genuinely tested (the functions pass, and are logged under other entries' evidence), so this is a traceability / evidence-binding weakness, not a false claim. Repro: `grep -rn "def test_c2_benchmark_standard_and_qualifying_allowances\|def test_r6b_has_no_wide_street_increase\|def test_as9_r5_" services/api/tests/rules` shows them only in test_r6b_far_heights.py and test_r1_r12_residential_far.py; compare with those three entries' `test_links`. Fix: add the second test file to the entry's test_links + automated_tests (digest + a run log), or cite in-file tests; optionally have behaviour_errors verify each named function exists in a linked test file.
- **F2 (should fix) — GUIDE.md evidence-file extension is wrong.** File: docs/zoning-rule-review/GUIDE.md line 30 — "`evidence/<test file>.log` - a committed log …". The committed evidence files are `.txt` (the producer deliberately used `.txt` because `*.log` is gitignored) and REGISTER.md / detail pages link `.txt`. The GUIDE should say `.txt`. Repro: `ls docs/zoning-rule-review/evidence/` (all `.txt`) vs `grep -n "\.log" docs/zoning-rule-review/GUIDE.md`.
- **F3 (note) — "Planned, not built" blends characteristics and already-built behaviour.** File: register.json behaviour.planned (r6b-height, r6b-lot-coverage, r6b-dwelling-units, r6b-rear-yard-corner-waiver and peers). Items such as "R6B heights do not depend on street width (recorded as a documented limitation)" (a correct characteristic, not missing behaviour) and "special districts are sent to professional review" (already built and in the `tested` list) appear under the heading "Planned, not built." Each is annotated as a documented limitation, so a reader is not misled, but the planned/committed separation S14 asks for is blurred. Consider moving characteristics/limitations out of the planned list or renaming the section.
- **F4 (note) — context budget headroom is thin.** `tools/context_budget_check.py` passes at 9922 / 10000 tok after principle 20; ~78 tok of headroom. Not a defect (passes), but a flag: the next eager-instruction addition will need compression first (the cap is owner-fixed at 10000).

Nothing in F1–F4 is must-fix; the core S4/S6/S8/S12/S13/S15 guarantees, the engine-computed examples, the honesty of gaps, the scope, and the all-"Not reviewed" backfill are solid and reproduced. Recommend recording **G3 PASS and G4 PASS**, with F1 and F2 addressed in a short follow-up (or accepted as recorded known limitations with a QUEUED follow-up for F1).

END-OF-REPORT
```

---

## Return 2: check of the corrections at `1cdad2c0`

```
# GATE RE-REVIEW — M4-T023 round 3 (correction of F1/F2/F3)

**Head checked:** 1cdad2c07e825fff3a3344850466cad7d8accf18 (`git rev-parse HEAD` in /root/project/rv-T023 = that sha; correction commit 9cb147a3). Read-only; tree clean after all runs (`git status --short` empty).

## 1. F1 — every cited test in a linked, bound file
- (a) **CONFIRMED.** Read the delta: `behaviour_errors` now regex-extracts every `test_*` name and requires `def <name>(` in one of the entry's OWN linked test files; `automated_tests_errors` requires `set(tested_test_file_sha256s) == set(test_links)`. In-memory probes: a `tested` item naming a function from an unlinked file → refused ("not defined"); same name in a linked file → passes; a linked test file with its digest removed → caught; a digest for an unlinked file → caught. All True.
- (b) **CONFIRMED.** All 23 `behaviour_errors == []`; 163 named-test references, **0 undefined in a linked file**; `tested_test_file_sha256s` keys equal `test_links` for all 23.
- (c) **CONFIRMED.** The three entries now link AND bind a second file (r5-residential-far += test_r1_r12_residential_far.py; r6-r12-residential-far and r6-r7-r8-wide-street-conditional-far += test_r6b_far_heights.py). Setting the SECOND file's recorded digest to zeros with status "Passed" → demands "Not run" for all three; status "Not run" → green.
- (d) **CONFIRMED.** 23 one-per-entry logs, each with command/date/exit 0/counts; each entry's command (file selection), counts and evidence path agree with its log. Re-ran 6 commands from services/api — r5-residential-far 51, r6-r12-residential-far 47, r6-r7-r8 47, r1-r2-bare-pitched-height 110, r6b-height 32, r6b-lot-coverage 88 — all match the logs and register.json. `git diff --stat 52e3d8a4 HEAD -- services/api/app/rules/rulesets services/api/tests/rules` shows only test_zoning_rule_review_register.py changed; all 23 rule files and all 7 linked test files are byte-identical, so "Passed (52e3d8a4)" is true of the current files. (Minor, not a finding: each log's command line carries `-p no:cacheprovider` while the register `command` field omits that cache flag — same file selection and counts; identical to round 1.)

## 2. F2 — GUIDE evidence extension
**CONFIRMED.** GUIDE.md now says `evidence/<rule id>.txt` (lines 30, 91) and documents the one-log-per-entry form ("one log per entry, named for the rule, … the run of exactly that entry's linked test file(s)"). No `.log` remains.

## 3. F3 — "Planned, not built" holds only missing behaviour
**CONFIRMED.** New totals verified against register.json: **tested 108, committed_untested 10, planned 45**. `planned` has **0 items** with escalation/limitation/"sent to professional review"/"documented limitation" wording (missing-behaviour only; the renderer emits "Nothing recorded as planned for this rule." when empty). Round-3 table accounts for all 49 old planned items.
- 4 moved to tested assert the statement: r6b-height "no street-width dependence" ← test_c1_benchmark_heights_from_the_one_lookup (asserts `no_street_width_dependence` applied); r6b-dwelling-units/r6b-lot-coverage/r6b-rear-yard "reached through 11-25" ← test_r6b_is_reached_through_zr_11_25_and_every_rule_says_so (asserts no section names R6B, the 11-25 text, and the suffix exception); r6b-lot-coverage & r6b-rear-yard special-district fail-closed ← test_special_district_or_unattested_special_district_fails_closed + test_unattested_overlay_fails_closed (both assert COVERAGE_PROFESSIONAL_REVIEW_REQUIRED).
- 4 moved to committed_untested (r5-qrs/r5a/r5b/r5d overlay/special-district escalation) are true: the only r5 escalation test (test_nc3_overlay_or_special_district_downgrades_never_silent_base) evaluates **only r5-height**, so no test exercises that escalation for the variant rules — the "no test found that exercises this escalation for this rule" wording is accurate.
- 2 removed are stated where claimed: r1-r2-suffix 11-25 inheritance is in its `exceptions` and `gaps`; r6b-dwelling-units qualifying-affordable dividend is in its `tested` list (test_qualifying_affordable_is_computed_but_sent_to_review).
- Nothing a reader needs is lost (gaps/exceptions retain the escalation facts).

## 4. Nothing else moved
**CONFIRMED.** register.json 326c8560 vs HEAD: **no diff** in law, applicable_from/to, applies_where, exceptions, interpretation, example, code_links, gaps, revision, last_changed, human_review, rule_file, rule_file_sha256, rule_version, title, family, draft_note. `test_links` changed **only** in the three entries. All 23 read "Not reviewed" with decision=null. HISTORY identical (23 events). (Expected changes outside the preserved set: `behaviour` and `automated_tests` — the F1/F3 rework.)

## 5. Checks (one at a time)
**CONFIRMED.** `pytest … test_zoning_rule_review_register.py test_coverage_matrix.py` → **59 passed**; `render_review_register.py --check` → **PASSED** (exit 0); `ruff check .` → exit 0; `tools/modularity_check.py --check` → exit 0 (render 423, check 498, test 538 lines — all < 600; the checker is still only validation functions and the test file is still only tests — one responsibility each). Did not run the full api suite (orchestrator ran it at 9cb147a3: 8044 passed, 8 skipped, exit 0).

## 6. Judgement — the log header "(M4-T023)"
The rendered table and pages (REGISTER.md, rules/*.md, HISTORY.md) contain **no** internal task/directive IDs (S16's letter is met). The evidence logs are committed run-provenance artifacts linked from the table; their first line reads "# Test-run evidence for the zoning-rule review register (M4-T023)". An examiner clicking "[log]" reaches a file bearing the task id. This is a **NOTE (optional)**: the logs are run-provenance (like a CI log), not rendered register content, and the same header was present and unflagged in round 1; if the owner wants the whole linked doc set free of internal IDs, drop "(M4-T023)" from the log header. Not blocking.

## VERDICTS at 1cdad2c0
- **G3: PASS.**
- **G4: PASS.**

All three prior findings (F1 should-fix, F2 should-fix, F3 note) are resolved and independently reproduced. The core guarantees (engine-computed examples, S4/S6/S8/S12/S13/S15 checks, both-direction test-file binding, all-"Not reviewed" backfill, clean scope, modularity, budget) hold at this head.

## Findings
- **F-new-1 (note, optional)** — evidence logs linked from the rendered table carry "(M4-T023)" in their header (docs/zoning-rule-review/evidence/*.txt, line 1). Rendered table/pages themselves are clean. Drop the task id from the log header only if the owner wants no internal IDs anywhere in the linked doc set.

Context (not a finding): the producer's own full-suite run recorded 1 unrelated flaky failure (tests/drawings/test_dxf_reader.py quadratic-timing guard, measured 7.95x vs a 8.0x threshold) — out of scope, no register file touched; the orchestrator's authoritative run at this head is green (8044 passed, 8 skipped).

END-OF-REPORT
```
