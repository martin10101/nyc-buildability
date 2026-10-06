# Guide to the zoning-rule review register

This guide is written by hand (it is not generated). It explains what the register is, what every
field means, and how the register is kept correct.

## What the register is, and is not

The register is a plain record of every zoning rule the program applies today. For each rule it
shows the law it rests on, where it applies, how the program reads it in plain English, one worked
example, the code and tests behind it, a revision, and a place for a New York City architect or
zoning examiner to say whether the program's reading is correct.

It **is** a review record you can hand to a professional. It is **not** a sign-off stage: nothing in
the program waits for a verdict, and a rule is never marked "professionally reviewed" just because
its tests pass or another program agreed. Every rule here is the program's own unreviewed draft
reading of the law, with a direct link to the source text, and it is not legal advice (this follows
the project's standing rule, ADR-007).

## The files

- `REGISTER.md` - the short current table, one row per rule, rendered from the data.
- `rules/<rule id>.md` - one detail page per rule, rendered from the data.
- `HISTORY.md` - the append-only history, oldest first, rendered from the data.
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
- **code_links**, **test_links** - the code and tests behind the rule.
- **automated_tests** - the test files and a note. This is kept apart from the human verdict. It
  never says "passing": if the tests fail, the build fails, so the register never ships with failing
  tests.
- **revision**, **last_changed** - the revision number (starts at 1) and the date it last changed.
- **human_review** - the human verdict block (see below).
- **gaps** - plain sentences: what is missing or not computed.
- **draft_note** - the standing statement that this is an unreviewed draft reading, not legal advice.

Allowed values:

- **human verdict**: `Not reviewed`, `Correct`, `Incorrect`, `Needs re-review`.
- **example basis_kind**: `law_text`, `reference_case`, `gap`.
- **history event**: `created`, `interpretation_changed`, `applicability_changed`,
  `implementation_changed`, `evidence_changed`, `human_verdict_recorded`, `flagged_for_re_review`.

## How a session updates the register when a rule changes

Every session that adds or changes zoning-rule behaviour updates this register in the same change:

1. Update the entry's `rule_version` and `rule_file_sha256` to match the changed rule file (the
   build fails if they drift), and refresh `interpretation`, `applies_where`, `exceptions`,
   `example` and `gaps` as needed.
2. Add one revision: increase the entry's `revision` and set `last_changed`.
3. Add a history event (for example `interpretation_changed`, `applicability_changed` or
   `implementation_changed`) describing what changed. The old detail stays in the history; nothing
   is removed or rewritten.
4. If the rule's interpretation, applicability or implementation changed, set the affected
   `human_review.verdict` to `Needs re-review` (a past verdict applies only to the version and
   conditions actually reviewed).
5. Do **not** add a second entry for a rule that already has one, and do not add a history event
   when nothing changed.

A limit to be honest about: the build can check the current file, but it cannot see earlier commits,
so it cannot by itself prove the history was only appended. A reviewer confirms, when a change lands,
that the history was added to and not rewritten.

## How a human verdict is recorded

A verdict is recorded **only** from a named human reviewer's own answer. To move a verdict off
`Not reviewed`, the entry must record the reviewer's name, the reviewer's role, the review date, the
revision that was reviewed, and the conditions that were reviewed. A verdict of `Correct` or
`Incorrect` must be against the rule's current revision; if the rule has since changed, the verdict
must read `Needs re-review`. A verdict is **never** derived from the automated tests passing or from
another program (AI) agreeing - the checker refuses any such entry.

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
primary key, `law`, `exceptions`, `gaps`, `code_links`, `test_links` become related rows or JSON
columns, and the `history` list becomes an append-only history table). No database work is done now;
this is only a note so the shape stays table-ready.

## Related records (linked, not copied)

- The rule-coverage matrix: `../../services/api/app/rules/coverage/COVERAGE_MATRIX.md` - which
  outputs are built for which districts.
- The captured law texts: `../research/zr-snapshots/v1/` - the official source text each rule cites.
- The question list for a professional: `../ARCHITECT_REVIEW_QUESTIONS.md` and
  `../MVP_ARCHITECT_REVIEW_QA.md`.
