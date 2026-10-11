# M5-T162 producer report

Builder: backend-engineer. Worktree: `/root/project/nyc-buildability/.claude/worktrees/agent-a187b8d68e5d91da7`.
Claim head: `4b79126618f449bb720397d9147d8df7c9dd6906`.

## What changed and why

Since M5-T157 the city's record decides the special density area, so the standard-residence legal
dwelling-unit limit is shown on page 8 as a Conditional ceiling (29), while the qualifying-affordable
and qualifying-senior limits are still withheld. Two report texts were fixed sentences written before
that change and denied the shown figure:

1. `services/api/app/drawings/report/readers.py` — the "Legal apartment limit" open item's effect was
   the hard-coded `_EFFECTS["legal_unit_limit"]` = "No legal apartment limit is shown.", and the item
   kept only the FIRST withheld limit's reason (the `put` de-duplication dropped qualifying senior).
   The open item is now built from the document (`_legal_unit_limit_item`): each withheld limit is named
   by its program as not known; where a limit is shown, the effect says it is shown as a conditional
   ceiling for that program (the number stays on the derivation table); "No legal apartment limit is
   shown." is used only when none is shown. The reason row keeps EACH withheld limit's own reason and
   the resolver names EACH, both labelled by program (title, number 6, order, status label "Pending
   verification" unchanged).
2. `services/api/app/drawings/report/coverage.py` — entry "F" (Legal unit limits) was hard-coded
   `(NOT_YET, "the legal unit limit is withheld")`. It now reads `Partly` with a note naming the shown
   limit's program as conditional when at least one legal dwelling-unit limit is shown, and `Not yet`
   ("no legal unit limit is shown") only when none is shown.

"Shown" is decided only from values actually present in an answer's shown values
(`present_values`, which already excludes `way == "withheld"` and non-mapping values); an absent or
malformed answer block yields no shown value and no open item. **No truthiness test on an optional
fact is used** — the only boolean test is on the non-empty program list derived from present values,
and `if limit_item is not None`.

**Resolver choice (packet left it to me):** the two withheld limits' resolvers DIFFER, so I name BOTH,
labelled by program, instead of keeping only the first — this keeps every unresolved input visible
(D-093) and restores the qualifying-senior resolver the old de-duplication lost.

Returned texts are plain user texts: no keys, gap numbers, task ids or "the caller", and no statement
about what law text is captured.

## Exact new benchmark texts (215-16 Northern Boulevard)

- **Effect** (page 1 "Most important open items" and open item 6):
  "The legal apartment limit is shown as a conditional ceiling for standard residences; it is not known
  for qualifying affordable housing or qualifying senior housing."
- **Reason row** (open-items page):
  "Qualifying affordable housing: The program does not work out the legal dwelling-unit limit for
  qualifying affordable housing yet, so it is not known. Qualifying senior housing: The dwelling-unit
  formula sets no factor for qualifying senior housing (ZR 23-52(a)(2)), so this formula gives no unit
  limit for it; whether any other provision limits the number of units has not been checked, so the
  legal dwelling-unit limit for it is not known: it is not set by this formula."
- **Resolver cell** (open-items page):
  "Qualifying affordable housing: Connecting the rule for qualifying affordable housing and checking it
  against an independently worked example. Qualifying senior housing: Checking whether any other
  provision limits the number of units for qualifying senior housing and checking the result against an
  independently worked example."
- **Coverage note** ("Legal unit limits", now `Partly`):
  "the limit for standard residences is shown as a conditional ceiling".

The withheld reasons and resolvers above are read verbatim from the document; only the program label
prefixes and the composed effect/coverage sentences are mine (and carry no number).

## State table (state, outcome, test)

| State | Outcome | Test |
|---|---|---|
| benchmark: standard shown, affordable + senior withheld | effect names standard as a conditional ceiling and affordable+senior as not known; reason+resolver keep both, labelled by program; number 6, status "Pending verification" | `test_s1_benchmark_standard_shown_affordable_and_senior_withheld` |
| every legal limit withheld (standard forced withheld) | effect = "No legal apartment limit is shown."; coverage F = Not yet | `test_s2_every_limit_withheld_says_none_shown` |
| no legal limit withheld (standard shown only) | no "Legal apartment limit" open item; coverage F stays Partly | `test_s3_no_withheld_means_no_open_item` |
| only one withheld (affordable; senior removed) | effect names the single program; reason+resolver are affordable's alone | `test_only_one_withheld_names_the_single_program` |
| malformed block (string) and absent block | not shown; no open item; coverage F = Not yet | `test_malformed_or_absent_allowance_block_is_not_shown` |
| coverage line for the benchmark | `Partly` with note naming standard residences as conditional; never Not yet while a limit is shown | `test_s4_coverage_partly_names_the_shown_limit_as_conditional` |
| any report where a limit is shown (S5 guard) | report HTML, decision-summary slice and open-items slice contain neither "No legal apartment limit is shown" nor "the legal unit limit is withheld" | `test_s5_guard_no_denial_while_a_limit_is_shown` |

Expected texts are taken from the packet's scenarios and read from the document (withheld reason/resolver
strings loaded from the fixture's own `value_states`), never from a program run.

## Checks (direct exit codes)

Run with `/root/project/lanes-runtime/venv/bin/python`, `PYTHONDONTWRITEBYTECODE=1`, `-p no:cacheprovider`.

- `cd services/api && python -m ruff check .` -> `All checks passed!`, RUFF_EXIT=0
- `cd services/api && python -m pytest -q tests/drawings tests/cad tests/journey` ->
  `1655 passed, 6 skipped, 1 warning in 109.36s`, SUITE_EXIT=0
- `python -m pytest -q tests/drawings/report/test_report_unit_limit_text.py -v` -> `7 passed`, NEWTEST_EXIT=0
- `python3 tools/modularity_check.py --check` (worktree root) -> MOD_EXIT=0. readers.py `source_lines`
  moved 502 -> 602, which crossed the 600 warning threshold by 2, so I trimmed one docstring to land at
  599 (below warn); readers.py no longer appears in the warn list. Below justify (750) and hard (1000);
  allowed_paths are fixed so a split into a new module was not available.

## Mutation proof (restored afterward; green rerun above)

- **A (readers.py effect):** forced the fixed `_EFFECTS["legal_unit_limit"]` sentence by flipping
  `if shown:` to `if False:`. S1 and the S5 guard FAILED:
  - S1: `AssertionError: assert 'No legal apartment limit is shown.' == 'The legal apartment limit is
    shown as a conditional ceiling for standard residences; it is not known for qualifying affordable
    housing or qualifying senior housing.'`
  - S5: `AssertionError: assert 'No legal apartment limit is shown.' not in ...` — caught on the decision
    summary ("...t limit:  No legal apartment limit is shown.  Pending verification   (see item 6)...").
  Restored to `if shown:`.
- **B (coverage.py F):** restored the hard-coded `(NOT_YET, "the legal unit limit is withheld")`. S4
  FAILED: `AssertionError: assert 'Not yet in the program' == 'Partly in this report'`. Restored to
  `"F": f_state`.

## Research and verification (D-093)

Read evidence record `docs/research/evidence-records/NB-05-special-density-area.json` and opened the
primary-source snapshots it cites: `zr-23-52.snapshot.json` (23-52(a)(2): qualifying senior housing has
no applicable dwelling-unit factor; 23-52(b): factor 680, fractions >= 0.75 count as one unit) and
`zr-12-10-special-density-areas.snapshot.json` (special density areas = Manhattan Core + Special
Downtown Brooklyn District). These confirm the document's shown/withheld structure is faithful: the
Queens lot is outside both special density areas, so the standard limit is a conditional ceiling; the
senior limit is not set by this formula; the affordable limit is sent to review. Every unresolved input
stays unresolved: affordable and senior remain not known; the standard limit stays Conditional.

## What I could not check

- Did not render the PDF/browser or start any server (forbidden); the report HTML is exercised by the
  test suites and the S5 guard instead.
- Did not run the api CI job, the full `pytest -q` of services/api, or the web/security suites — those
  run in CI on the accepted head (R639).
- Qualifying affordable and qualifying senior dwelling-unit limits remain not-worked program gaps; this
  task only fixes wording and does not compute them.

## Rework 1 (scope correction 1; base df174f25)

Correction: say "conditional" only for a limit whose OWN state is conditional, not by default; and
move the legal-limit helpers out of readers.py into a new module.

What changed:
- New module `services/api/app/drawings/report/unit_limit_text.py` holds `_limit_program`,
  `_join_programs`, `_as_label`, `shown_legal_unit_limits` (new), `shown_legal_unit_limit_programs`,
  `_withheld_legal_unit_limits`, `legal_unit_limit_item`, and the `NO_LIMIT_SENTENCE` constant.
- `shown_legal_unit_limits(results)` returns `{"program", "conditional"}` per shown limit, reading
  `conditional` only from the value's own `value_states[<key>].way == "conditional"` (the same check
  the web journey test uses). An absent, malformed or other state is not conditional - no default.
  No truthiness test on an optional fact; the only booleans are `if shown`, `if conditional`,
  `if plain`, `if limit_item is not None`, `isinstance(...)` guards.
- The effect and the coverage "F" note split shown limits into conditional vs plain; "conditional
  ceiling" is said only for the conditional ones, others are named plainly ("is shown for <program>").
- `readers.py` keeps only thin wiring: `open_items` calls `unit_limit_text.legal_unit_limit_item`; the
  moved helpers and the `legal_unit_limit` entry of `_EFFECTS` are gone; readers stays a document reader.
- `coverage.py` reads `unit_limit_text.shown_legal_unit_limits` directly (switched off readers).

Import cycle: avoided. `readers` imports `unit_limit_text` at module load; `unit_limit_text` reaches
back into `readers` (`ANSWER_NAMES`, `answer_block`, `present_values`, `withheld_values`) only inside
its functions (deferred `from . import readers`), and reads `value_states` straight off the block, so
neither module imports the other at top in both directions. `coverage` and the tests import
`unit_limit_text` directly. No module reads another's private names across the boundary.

New texts (non-conditional way, and no `value_states` entry - both the same):
- Effect: "The legal apartment limit is shown for standard residences; it is not known for qualifying
  affordable housing or qualifying senior housing."
- Coverage note: "the limit for standard residences is shown".
Benchmark (standard way conditional) is byte-identical to rework 0: effect "...shown as a conditional
ceiling for standard residences; ..."; coverage note "the limit for standard residences is shown as a
conditional ceiling".

Three new state tests in `test_report_unit_limit_text.py` (each asserts the effect AND the coverage
note): `test_way_conditional_says_conditional_ceiling`, `test_way_non_conditional_is_shown_plainly`
(way "settled"), `test_no_value_states_entry_is_shown_plainly`.

Checks (direct exit codes; lanes venv, PYTHONDONTWRITEBYTECODE=1, -p no:cacheprovider):
- `cd services/api && python -m ruff check .` -> All checks passed! RUFF_EXIT=0
- `python -m pytest -q tests/drawings/report/test_report_unit_limit_text.py -v` -> 10 passed, NEWTEST_EXIT=0
- `python -m pytest -q tests/drawings tests/cad tests/journey` -> 1658 passed, 6 skipped, SUITE_EXIT=0
- `python3 tools/modularity_check.py --check` -> MOD_EXIT=0. source_lines: readers.py 505,
  unit_limit_text.py 137, coverage.py 114 - all below the 600 warn line.

Mutation proof (restored; green rerun above): forced `"conditional": True` regardless of state in
`shown_legal_unit_limits`. `test_way_non_conditional_is_shown_plainly` and
`test_no_value_states_entry_is_shown_plainly` both FAILED - the effect gained "as a conditional
ceiling" ("The legal apartment limit is shown as a conditional ceiling for standard residences; ...").
Restored to `way == "conditional"`.
