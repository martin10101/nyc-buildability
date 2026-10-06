# Guide to the zoning-rule review register

This guide is written by hand (it is not generated). It explains what the register is, what every
field means, and how the register is kept correct.

## What the register is, and is not

The register covers the 23 rule-definition files the program applies today - one entry per rule. That
is **not** complete coverage of the New York City Zoning Resolution; it is the set of zoning rules the
program has implemented so far. For each rule it shows the law it rests on, where it applies, how the
program reads it in plain English, one worked example, what the program does today versus what is only
planned, the result of the rule's automated tests, and a place for a New York City architect or zoning
examiner to say whether the program's reading is correct.

It **is** a review record you can hand to a professional. It is **not** a sign-off stage: nothing in
the program waits for a verdict, and a rule is never marked "professionally reviewed" just because its
tests pass or another program agreed. Every rule here is the program's own unreviewed draft reading of
the law, with a direct link to the source text, and it is not legal advice (this follows the project's
standing rule, ADR-007).

Reviews of this register by an AI agent are **agent reviews**. An agent review is never a human review
and never a professional review, and nothing in the register reads as one. The human-verdict field is
filled only by a named human reviewer, and every rule reads "Not reviewed" today.

## The files

- `REGISTER.md` - the short current table, one row per rule, rendered from the data.
- `rules/<rule id>.md` - one detail page per rule, rendered from the data.
- `HISTORY.md` - the append-only history, oldest first, rendered from the data.
- `evidence/<rule id>.txt` - a committed log of each rule's automated test run (command, date,
  commit, exit code and the pytest summary). There is one log per entry, named for the rule, and it
  is the run of exactly that entry's linked test file(s). The test-result field links to it.
- `GUIDE.md` - this guide (hand-written).
- `../../services/api/app/rules/review_register/register.json` - the authored source. The Markdown
  is rendered from it; do not edit the Markdown by hand. Re-render with
  `python services/api/app/rules/review_register/render_review_register.py --write` and validate with
  `--check`.

## The fields, their meaning and their allowed values

Each entry in `register.json` has these fixed field names:

- **entry_id** - the stable id. It equals the rule id and never changes (so the register can move
  into a database table later).
- **rule_id**, **rule_file**, **rule_version** - which rule this is and where its definition lives.
- **rule_file_sha256** - a fingerprint of the rule file (line endings normalized). If the rule file
  changes and this is not updated, the build fails.
- **title**, **family** - a short name and the rule's group.
- **law** - a list of law references, each with: the section, the official link, the capture id, the
  capture file, the last-amended date, the capture date, and a content fingerprint (sha256) of the
  captured text.
- **applicable_from**, **applicable_to** - the dates between which the rule is in effect
  (`applicable_to` is empty when there is no end date).
- **applies_where** - in plain English, where the rule applies.
- **exceptions** - plain sentences: the exceptions, special-district interactions and limits.
- **interpretation** - in plain English, what the program does with the rule.
- **example** - one worked example:
  - **inputs** - a simple, made-up lot (always said to be made up).
  - **expected** - the answer worked out independently, with: **values**; **basis_kind**, one of
    `law_text`, `reference_case` or `gap`; **basis** (the quoted law text and the arithmetic, or the
    named reference case, or why it is a gap); and **prepared_by** (who worked it and that it is not
    professionally checked).
  - **actual** - the answer the program actually gives (its output values and the result label it
    attaches). The test recomputes this through the program's own engine.
  - **agrees** - `true`, `false`, or `null`. `null` means the expected answer is a gap. The expected
    answer is never taken from a program run; if expected and actual differ, the entry says so
    plainly and the rule is not changed to force a match.
- **code_links**, **test_links** - the code and the test file(s) behind the rule. An entry links one
  test file, or more when its behaviour is exercised across more than one (for example a rule whose
  benchmark assertion lives in the R6B suite as well as its own family suite). Every test function a
  `behaviour.tested` item names must be defined in one of the entry's linked test files, and
  `automated_tests.tested_test_file_sha256s` lists exactly those files (the checker enforces both).
- **behaviour** - three plain-sentence lists, told apart:
  - **tested** - what the committed rule computes AND a named test exercises; each item names the
    test function(s), and each named function is defined in one of the entry's linked test files.
  - **committed_untested** - what the committed rule contains that no test exercises; where it cannot
    be told, the item says "no test found that exercises this".
  - **planned** - ONLY missing behaviour: what the program does not compute today, worded as what is
    not built, with no clause about what the program does instead. Behaviour that exists goes under
    `tested` or `committed_untested`; a characteristic of the law or a documented limit goes under
    "Exceptions and limits" or the gaps, not here. An empty list is fine and reads "Nothing recorded
    as planned for this rule."
- **automated_tests** - the RESULT of one run of the rule's linked test file(s), kept apart from the
  human verdict and never derived from it. The form is the same for every entry: one command runs
  all of the entry's linked test file(s) in a single pytest invocation, and one run log named for the
  entry records it; an entry that links two test files still has one command, one log and one combined
  count.
  - **status** - `Passed`, `Failed` or `Not run`.
  - **tested_commit**, **tested_on**, **command**, **counts** - the commit the tests ran at, the date,
    the command (all linked files in one invocation), and the pass/fail counts of that run.
  - **evidence** - a path under `docs/zoning-rule-review/evidence/<rule id>.txt` to the committed run
    log of exactly that command.
  - **tested_rule_file_sha256**, **tested_test_file_sha256s** - the fingerprints of the rule file and
    test file(s) the result is bound to. If any of them differs from the current file, the checker
    requires the status to read `Not run`, so a result for an earlier version is never shown as
    current.
- **revision**, **last_changed** - the revision number (starts at 1) and the date it last changed.
- **human_review** - the human verdict block (see below).
- **gaps** - plain sentences: what is missing or not computed.
- **draft_note** - the standing statement that this is an unreviewed draft reading, not legal advice.

Allowed values:

- **human verdict** (shown, derived): `Not reviewed`, `Correct`, `Incorrect`, `Needs re-review`.
- **human decision** (the reviewer's own, stored): `Correct`, `Incorrect`, or no decision (null).
- **applies_to_current** (derived): `true`, `false`, `null`.
- **automated-test status**: `Passed`, `Failed`, `Not run`.
- **example basis_kind**: `law_text`, `reference_case`, `gap`.
- **history event**: `created`, `interpretation_changed`, `applicability_changed`,
  `implementation_changed`, `evidence_changed`, `human_verdict_recorded`, `flagged_for_re_review`.

## Which changes move an entry's revision

A change to a rule's **interpretation, applicability, implementation or evidence** moves the entry to
a new revision: increase `revision`, set `last_changed`, add a history event, and - if a human
decision had been recorded - the derived verdict becomes `Needs re-review` because the decision no
longer matches the current version. A change to the **register's own layout or wording** - like the
rework that added the behaviour lists, the test-result field and the kept-apart human decision - does
**not** move an entry's revision. Because nothing in the register has yet been merged or reviewed by a
human, the whole backfill is recorded as revision 1 with a single `created` event dated 2026-10-06.

## How a session updates the register when a rule changes

Every session that adds or changes zoning-rule behaviour updates this register in the same change:

1. Update the entry's `rule_version` and `rule_file_sha256` to match the changed rule file (the
   build fails if they drift), and refresh `interpretation`, `applies_where`, `exceptions`,
   `example`, `behaviour` and `gaps` as needed.
2. Re-run the rule's test file(s) and update the `automated_tests` result, including the
   `tested_commit`, the `tested_*_sha256` fingerprints and the committed run log under `evidence/`.
3. Add one revision: increase the entry's `revision` and set `last_changed`.
4. Add a history event (for example `interpretation_changed`, `applicability_changed`,
   `implementation_changed` or `evidence_changed`) describing what changed. The old detail stays in
   the history; nothing is removed or rewritten.
5. Any recorded human decision keeps its original wording; the derived verdict re-computes to
   `Needs re-review` on its own because a reviewed identity no longer matches.
6. Do **not** add a second entry for a rule that already has one, and do not add a history event
   when nothing changed.

**The check enforces record-keeping only.** No check, test, gate or script requires a human decision:
the build check requires only that the record is current (the recorded identities match the files and
each change adds a revision and a history event), and it never fails because an entry reads
"Not reviewed" or "Needs re-review". Development never waits for an examiner.

**Append-only is a standing review duty.** The build can read only the current file, not earlier
commits, so it cannot by itself prove the history was only appended. On every change a reviewer
confirms that the history was added to and never rewritten; this is a standing duty of each review,
not an optional check.

## How a human verdict is recorded

A verdict is recorded **only** from a named human reviewer's own answer; an agent review is never
recorded here. The reviewer's original decision is stored and never overwritten: the `decision`
(`Correct` or `Incorrect`), the reviewer's name and role, the review date, the comments, the revision
reviewed, the conditions reviewed, and the identity of what was reviewed - the rule file's digest
(`reviewed_rule_file_sha256`) and the cited law-capture digests (`reviewed_law_digests`). A decision
is refused unless all of these are present.

A separate field, `applies_to_current`, is **derived** (never typed) by comparing those recorded
identities with the current ones. The shown `verdict` follows from the two:

- no decision -> `Not reviewed`;
- a decision whose rule digest, law digests and revision all still match the current ones -> that
  decision (`Correct` or `Incorrect`);
- a decision where any of them differs -> `Needs re-review`, with the earlier decision still shown on
  the detail page ("Earlier decision: Correct, given by ... for revision N; it does not apply to the
  current version").

The checker recomputes `applies_to_current` and the shown `verdict` and refuses any stored value that
differs, so updating or merely touching the register file can never keep an old "Correct" on changed
logic. A verdict is **never** derived from the automated tests passing or from an agent review.

## Zoning behaviour in code that has no rule id yet

Some zoning logic lives in code without its own rule id, so it is **not yet** in this register. It is
listed here so it is not forgotten; it has not been given an invented id and has not been changed.
Turning this list into follow-up rule work is an orchestrator decision.

- **Wide-street determination** (`services/api/app/rules/wide_street_wiring.py`) - decides, from
  mapped street widths and a 100-foot buffer, whether a lot is within 100 feet of a wide street.
  This is the determination several FAR and height rules mark "conditional" and do not make
  themselves.
- **Named-street override table** (`services/api/app/rules/named_street_override_table.py` and
  `named_street_override.py`, `named_street_override_matching.py`, `named_street_override_status.py`)
  - the ZR 12-10 named-street alternate-width overrides (for example Broadway and Allen Street),
  encoded as a table in code.
- **Scenario "three answers" engine** (`services/api/app/scenario/three_answers/` and
  `services/api/app/scenario/derivation.py`, `max_envelope.py`) - turns the rule outputs into
  floor-area, envelope, dwelling-unit and building-option figures. It applies zoning arithmetic that
  combines several rules, without a rule id of its own.
- **Proposal checks** (`services/api/app/rules/proposal_checks.py`) - checks a proposed massing
  against the existing rules.
- **Rules / property integration** (`services/api/app/rules/integration.py`) - maps property facts
  into rule inputs; it maps, it does not decide law.

## Moving the register into a database later

The register is already structured so it can move into a Supabase (Postgres) table later with no
redesign: each entry is one row, the fixed field names map to columns (`entry_id` is the stable
primary key, `law`, `exceptions`, `gaps`, `code_links`, `test_links`, `behaviour` become related rows
or JSON columns, and the `history` list becomes an append-only history table). No database work is
done now; this is only a note so the shape stays table-ready.

## Related records (linked, not copied)

- The rule-coverage matrix: `../../services/api/app/rules/coverage/COVERAGE_MATRIX.md` - which
  outputs are built for which districts.
- The captured law texts: `../research/zr-snapshots/v1/` - the official source text each rule cites.
- The question list for a professional: `../ARCHITECT_REVIEW_QUESTIONS.md` and
  `../MVP_ARCHITECT_REVIEW_QA.md`.
