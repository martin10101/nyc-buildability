# M4-T023 producer report - zoning-rule review register REWORK (D-090 R362..R385 + R393/R394/R423/R425/R426/R441/R442/R443)

Producer: rules-engineer, isolated agent worktree
`/root/project/nyc-buildability/.claude/worktrees/agent-a38c5ad602668c836`
(reset to `52e3d8a461cf08577273c82f802b85433f6f1ec3` before work: the first build c55b7c47 plus the
orchestrator's project-control-only commits).

This is the rework after owner messages 94 (source-043) and 95 (source-044) and the first independent
review's five notes (F1-F5, project-control/reports/M4-T023-G3G4.md). No rule file, engine, registry,
evaluator, coverage, capture, CI, dependency or database file was touched. All 23 backfilled entries
keep no human decision ("Not reviewed"). Reviews by agents are called agent reviews everywhere
rendered.

## What changed this round

1. **Human review kept apart from applicability (S12, R425/R426).** `human_review` now stores the
   reviewer's ORIGINAL decision and never overwrites it: `decision` (Correct|Incorrect|null),
   reviewer_name, reviewer_role, review_date, comments, reviewed_revision, reviewed_conditions, and
   the identity of what was reviewed - `reviewed_rule_file_sha256` and `reviewed_law_digests`. Two
   fields are DERIVED by one function (`derive_human_review`): `applies_to_current` and the shown
   `verdict`. The checker recomputes both and refuses any stored value that differs, so updating or
   merely touching the register can never keep an old "Correct" on a changed rule file, law capture
   or revision. A decision is refused without a name, date, revision, conditions and both identities.
   The detail page shows the current verdict and, when a decision no longer applies, the line
   "Earlier decision: ...; it does not apply to the current version". Events `human_verdict_recorded`
   and `flagged_for_re_review` exist for this. Tests S12 (a)-(d) prove it, all on in-memory copies.
2. **The check enforces record-keeping only (S13, R394/R442).** Two tests render a mutated register
   to a temp folder and run the full build check: one for an updated entry with no decision, one for
   an entry whose decision no longer applies (verdict "Needs re-review"); both pass. Nothing requires
   a human decision; GUIDE.md says so in one sentence ("The check enforces record-keeping only").
3. **Planned / committed / tested told apart (S14, R393).** Each entry gained `behaviour`:
   {tested, committed_untested, planned}, built by reading each rule file and its test file. Every
   `tested` item names the test function(s) that exercise it (the checker enforces a `test_` name).
   Where a behaviour could not be shown as exercised it is under `committed_untested` and says "no
   test found that exercises this". Rendered under three plain headings on each detail page.
   Totals across 23 entries: **tested 104, committed_untested 6 (in 4 entries), planned 49**.
4. **Test RESULT, not an inventory count (S15, R441).** `automated_tests` is now
   {status, tested_commit, tested_on, command, counts, evidence, tested_rule_file_sha256,
   tested_test_file_sha256s, note}. I ran each rule's test file(s) at the reset head 52e3d8a4 (rule
   and test files unchanged by this task, so that is the commit tested), one command at a time, and
   committed each run log under `docs/zoning-rule-review/evidence/` (`.txt`; `*.log` is gitignored
   repo-wide and `.gitignore` is out of scope). The checker demands status "Not run" if the recorded
   rule-file or test-file digest differs from the current file. The table column shows status, short
   commit and an evidence link, never "N test files". Kept separate from the human-review block.
5. **Wording and the five notes (S16, R423).** REGISTER.md and GUIDE.md now say the register covers
   the 23 rule-definition files the program has today and that this is NOT complete coverage of the
   law; agent reviews are named agent reviews and nothing reads as a human/professional review.
   F1: r5a-height basis softened (the quoted excerpt states 25/35; the R5A enumeration lives in the
   capture's notes and sibling captures). F2: r5b-height and r5d-height gained a gap line that the
   statement-to-district mapping in the ZR 23-422 capture is researcher-assigned and unconfirmed.
   F3: the misnamed S8 test now renders to a temp folder, tampers a detail page and runs the
   checker's `rendered_errors` on it. F4: GUIDE.md states append-only as a standing duty of each
   reviewer. F5: r2x-r4-residential-far exception reads "(R4 1.50; R2X unchanged at 1.00)".
6. **Revision policy (point 6).** GUIDE.md states which changes move an entry's revision (a change of
   interpretation, applicability, implementation or evidence) and which do not (a change of the
   register's own layout - like this rework). Because nothing has been merged or reviewed by a human,
   the whole backfill stays revision 1 with one `created` event dated 2026-10-06; HISTORY.md is
   unchanged (23 created events).
7. Files changed (allowed paths only): `register.json`, `render_review_register.py`,
   `check_review_register.py`, the one test file, all of `docs/zoning-rule-review/` (GUIDE, REGISTER,
   HISTORY, 23 detail pages, 7 evidence logs), and this report.

## Test results recorded in the register

All 23 entries: status **Passed**, tested at commit `52e3d8a461cf08577273c82f802b85433f6f1ec3`
(0 Failed, 0 Not run). Per test file (one evidence log each): test_r1_r2_height_setback 110 passed;
test_r1_r12_residential_far 15 passed; test_r3_r4_height 90 passed; test_r5_height_setback 47 passed;
test_rules_engine 36 passed; test_r6b_coverage_yard_units 88 passed; test_r6b_far_heights 32 passed.

## Checks (each run on its own; python = /root/project/lanes-runtime/venv/bin/python)

| # | Command (from the stated cwd) | Exit | Result |
|---|---|---|---|
| 1 | `cd services/api && python -m ruff check .` | 0 | All checks passed! |
| 2 | `cd services/api && python -m pytest -q -p no:cacheprovider tests/rules/test_zoning_rule_review_register.py tests/rules/test_coverage_matrix.py` | 0 | 55 passed |
| 3 | `python services/api/app/rules/review_register/render_review_register.py --check` (repo root) | 0 | register check PASSED (no issues) |
| 4 | `python3 tools/modularity_check.py --check` | 0 | selected 715 files; failures 0 (render 420, check 468, test 501 lines; all under the 600 warn line) |
| 5 | `cd services/api && python -m pytest -q -p no:cacheprovider` (FULL api suite, final candidate, alone) | 0 | 8040 passed, 8 skipped (the 8 skips are pre-existing and unrelated) |

## Mutation proofs (each in memory or a temp folder; no committed rule/test file touched)

- **S4** - set a copy's recorded `rule_file_sha256` to zeros -> `rule_file_errors` RED: "rule file ...
  content changed (sha256 ... != recorded 0000...); the register must be updated in the same change".
- **S6** - set a copy's `human_review.decision="Correct"` with no reviewer/identity ->
  `human_review_errors` RED: "a human decision of 'Correct' is refused - it needs a reviewer name, a
  review date, the revision reviewed, the conditions reviewed and the identity of what was reviewed".
- **S8** - rendered a copy to a temp folder, hand-edited `r6b-height.md` -> `rendered_errors` RED:
  "rendered file is stale: r6b-height.md (run --write)".
- **S12 (new)** - recorded a "Correct" decision for revision 1, then changed the rule file (new digest
  + revision 2 in the same change): `derive_human_review` -> applies_to_current=False,
  verdict="Needs re-review", original decision still "Correct"; storing "Correct" is refused RED.
- **S15 (new)** - set a copy's `tested_test_file_sha256s[...]` to zeros with status "Passed" ->
  `automated_tests_errors` RED: "a test file changed ... status must read 'Not run'"; setting status
  to "Not run" turns it GREEN.

## Two sample rows of REGISTER.md (exactly as rendered now)

```
| R2X and R4 residence districts (ZR 23-21 rows 2-3) - maximum residential floor area ratio (standard zoning lots) (`r2x-r4-residential-far`) | [23-21](https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-21), applies from 2024-12-05 | 1 (2026-10-06) | Passed (52e3d8a4) [log](evidence/test_r1_r12_residential_far.txt) | Not reviewed | - | [open](rules/r2x-r4-residential-far.md) |
| R6B district - minimum base height, maximum base height and maximum building height, standard residences and qualifying affordable or senior housing (ZR 23-432) (`r6b-height`) | [23-432](https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-432), applies from 2024-12-05 | 1 (2026-10-06) | Passed (52e3d8a4) [log](evidence/test_r6b_far_heights.txt) | Not reviewed | - | [open](rules/r6b-height.md) |
```

## Assumptions, limitations, doubts

- Evidence logs use `.txt` because a repo-wide `*.log` ignore in `.gitignore` would silence them and
  `.gitignore` is outside this task's allowed paths; the checker verifies each evidence file exists.
- The `committed_untested` lists are honest about the FAR family: for r1-r2-r3, r2x-r4, r5-residential-
  far and r5-qrs-height the emitted floor-area value or the qualifying-alternative evaluation is not
  asserted by a dedicated test (the same multiply/alternative mechanism is asserted elsewhere, e.g.
  R5 and the R6B benchmark); each such item says "no test found that exercises this".
- register.json was re-authored by a scratch generator kept OUTSIDE the worktree; the committed JSON
  is the single source the renderer, checker and test read. No scratch or untracked file remains in
  the worktree besides the committed evidence logs.
- Behaviour "tested" claims were written by reading each rule file and its test file(s); an
  independent reviewer should re-check them against those files.

## Round 3 - the three review corrections (F1, F2, F3)

The second independent review passed the rework (G3 PASS, G4 PASS) with three corrections. All build
only; no engine/rule/registry/coverage/capture/CI/dependency/database file touched; all 23 entries
stay revision 1 with their one `created` event; no change to any other first-reviewed field
(law, applies_where, interpretation, example, code_links), and NO change to any `exceptions` or `gaps`
text.

### F1 - every cited test is in a linked, bound file
- Checker: `behaviour_errors` now reads the entry's linked test files and refuses any `tested` item
  whose named `test_` function is not `def`-defined in one of them (a bare "test_" substring is no
  longer enough); `automated_tests_errors` now requires `tested_test_file_sha256s` keys to equal the
  entry's `test_links` (binding and the reverse).
- Data: the three flagged entries now link AND bind the second file that holds their cited test -
  r5-residential-far adds `test_r1_r12_residential_far.py` (holds test_as9_r5_*); r6-r12-residential-far
  and r6-r7-r8-wide-street-conditional-far add `test_r6b_far_heights.py` (holds
  test_c2_benchmark_standard_and_qualifying_allowances / test_r6b_has_no_wide_street_increase).
- Uniform form (described in GUIDE.md): every entry's `automated_tests` is one pytest command over all
  its linked test file(s), one combined count, and one run log named `evidence/<rule id>.txt`. The 7
  per-file logs were replaced by 23 per-entry logs, each produced by running the entry's command
  against an exported copy of commit 52e3d8a4 (`git archive 52e3d8a4 | tar -x`; run from that copy's
  services/api with the lanes venv). `tested_commit` stays 52e3d8a4.
- Tests: `test_tested_item_naming_a_function_not_in_a_linked_file_is_refused`;
  `test_every_committed_tested_citation_is_defined_in_a_linked_file` (all 23);
  `test_changed_second_linked_test_file_digest_demands_not_run` (r5-residential-far, 2 files);
  `test_a_linked_test_file_not_bound_by_a_digest_is_caught`.

### F2 - GUIDE.md evidence extension
`GUIDE.md` now says `evidence/<rule id>.txt` (was `.log`) and documents the one-log-per-entry form.

### F3 - "Planned, not built" holds only missing behaviour
Went through all 49 original planned items. Result: **kept 18; reworded to missing-only 27** (6 of
these are the kept half of a split); **moved to tested 4; moved to committed_untested 4; removed 2**
(already stated elsewhere); 0 moved to exceptions/gaps. New totals across 23 entries:
**tested 108, committed_untested 10, planned 45.** Disposition of every item:

| Entry | Old planned item (short) | What I did |
|---|---|---|
| r1-r2-bare | sloping envelope not computed | kept |
| r1-r2-bare | base plane not determined | kept |
| r1-r2-bare | overlay/etc not computed; sent to PR | reworded (dropped "sent to PR"; already tested) |
| r1-r2-qrs | qualifying-site determination not made | kept |
| r1-r2-qrs | 23-423 setback recorded as limitation, not computed | reworded (missing-only) |
| r1-r2-qrs | overlay/special not computed; sent to PR | reworded (dropped "sent to PR") |
| r1-r2-r3 | qualifying FAR determination not made | kept |
| r1-r2-r3 | SPD/overlay FAR not applied | kept |
| r1-r2-ref-plane | reference plane feeds sloping geometry, not computed | reworded (missing-only) |
| r1-r2-ref-plane | site-specific modifiers not modelled | kept |
| r1-r2-suffix | 11-25 suffix inheritance documented limitation | removed (already in exceptions + gaps) |
| r1-r2-suffix | sloping setback geometry not computed | kept |
| r1-r2-suffix | overlay/etc sent to PR | reworded to missing "not computed" (escalation already tested) |
| r2x-r4 | qualifying FAR determination not made | kept |
| r2x-r4 | SPD/overlay FAR not applied | kept |
| r3-2-r4-flat | overlay/etc not computed; sent to PR | reworded (dropped "sent to PR") |
| r3-r4-pitched | sloping envelope not computed | kept |
| r3-r4-pitched | overlay/etc sent to PR | reworded to missing "not computed" |
| r4b | overlay/etc not computed; sent to PR | reworded (dropped "sent to PR") |
| r5-height | no min base height; recorded as documented limitation | reworded (missing-only) |
| r5-height | overlay/etc sent to PR | reworded to missing "not computed" |
| r5-qrs | qualifying-site determination not made | kept |
| r5-qrs | 23-423 setback recorded as limitation, not computed | reworded (missing-only) |
| r5-qrs | overlay/special sent to PR | split: reworded missing "not computed" (kept) + moved escalation to committed_untested |
| r5-residential-far | qualifying FAR determination not made | kept |
| r5-residential-far | SPD/overlay FAR not applied | kept |
| r5-setback | 23-423 modifications not computed; final unresolved | reworded (missing-only; "unresolved" flag already tested) |
| r5-setback | overlay/special sent to PR | reworded to missing "not computed" |
| r5a | sloping setback geometry not computed | kept |
| r5a | overlay/etc sent to PR | split: reworded missing "not computed" (kept) + moved escalation to committed_untested |
| r5b | no base/setback split; single flat cap reported | reworded (missing-only) |
| r5b | overlay/etc sent to PR | split: reworded missing "not computed" (kept) + moved escalation to committed_untested |
| r5d | no base/setback split; single flat cap reported | reworded (missing-only) |
| r5d | overlay/etc sent to PR | split: reworded missing "not computed" (kept) + moved escalation to committed_untested |
| r6-r12 | qualifying-housing FAR determination not made | kept |
| r6-r12 | SPD/overlay FAR not applied | kept |
| r6-r7-r8 | wide-street determination not made; returns conservative, conditional | reworded (missing-only; "returns conservative/conditional" already tested) |
| r6-r7-r8 | 23-22 lot split not computed | kept |
| r6b-dwelling-units | conversions/mixed-factor not computed; documented limitations | reworded (missing-only) |
| r6b-dwelling-units | qualifying-affordable dividend sent to PR | removed (already built + in tested) |
| r6b-dwelling-units | reached through 11-25 documented limitation | moved to tested (test_r6b_is_reached_through_zr_11_25_and_every_rule_says_so) |
| r6b-height | 23-433 setback not encoded | kept |
| r6b-height | R6B heights do not depend on street width | moved to tested (test_c1_benchmark_heights_from_the_one_lookup) |
| r6b-height | commercial overlays not captured; special districts sent to PR | reworded to missing "overlays not captured" (special-district already tested) |
| r6b-lot-coverage | only standard lots; special interior/through rules documented limitation | reworded (missing-only; eligible-site % and special rules not computed) |
| r6b-lot-coverage | commercial overlays not captured; special districts sent to PR | split: reworded missing "overlays not captured" (kept) + moved special-district fail-closed to tested (test_special_district_or_unattested_special_district_fails_closed) |
| r6b-qualifying-housing | qualifying determination not made; FAR surfaced as alternative | reworded (missing-only) |
| r6b-rear-yard | only waiver within 100 ft computed; ordinary depth beyond not computed | reworded (missing-only: ordinary depth beyond not computed) |
| r6b-rear-yard | commercial overlays not captured; special districts sent to PR | split: reworded missing "overlays not captured" (kept) + moved special-district fail-closed to tested (test_special_district_or_unattested_special_district_fails_closed) |

Entries that now bind two test files: r5-residential-far (51 passed), r6-r12-residential-far (47 passed),
r6-r7-r8-wide-street-conditional-far (47 passed). All 23 statuses remain Passed at 52e3d8a4.

### Round 3 checks (each run on its own)

| # | Command | Exit | Result |
|---|---|---|---|
| 1 | `cd services/api && python -m ruff check .` | 0 | All checks passed! |
| 2 | `cd services/api && python -m pytest -q -p no:cacheprovider tests/rules/test_zoning_rule_review_register.py tests/rules/test_coverage_matrix.py` | 0 | 59 passed |
| 3 | `python services/api/app/rules/review_register/render_review_register.py --check` | 0 | register check PASSED (no issues) |
| 4 | `python3 tools/modularity_check.py --check` | 0 | failures 0 (render 423, check 498, test 538; all < 600) |
| 5 | `cd services/api && python -m pytest -q -p no:cacheprovider` (FULL api suite, once, last) | 1 | 8043 passed, 8 skipped, 1 FAILED - the one failure is OUT OF SCOPE: `tests/drawings/test_dxf_reader.py::test_t097_b1_mutation_double_find_reddens_time_guard`, a timing-threshold guard asserting a measured quadratic ratio >= 8.0x; it measured 7.95x. It fails the same way in isolation and does not touch the review register (I changed only review_register, docs/zoning-rule-review and the register test). Reported, not edited. |

Out-of-scope failure detail: `AssertionError: the double-find should scale quadratically (>= 8.0x);
measured 7.9x - the guard did not redden` (`7.948... >= 8.0`), at tests/drawings/test_dxf_reader.py:912.
This is a machine-timing-sensitive performance guard, not a review-register regression.
