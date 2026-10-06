# M4-T023 producer report - zoning-rule review register (D-090-R362..R385)

Producer: rules-engineer, isolated worktree
`/root/project/nyc-buildability/.claude/worktrees/agent-a8478e1d81b60aeaf`
(reset to the claim-seam head `10ce8cadcdb4403eeb823ccaed293c90d14c8075` before work).

## What was built

A permanent, structured zoning-rule review register the owner can hand to a New York City architect
or examiner. One authored data file is the source of truth; a deterministic stdlib renderer produces
the plain-English Markdown; a checker and a pytest suite enforce that the register stays honest and
current.

- `services/api/app/rules/review_register/register.json` - the authored source: schema name/version,
  a field guide (field names + value sets), 23 entries (one per rule file, stable `entry_id` = the
  rule id), and the append-only history (23 `created` events).
- `services/api/app/rules/review_register/render_review_register.py` - stdlib renderer + CLI;
  `--write` renders the Markdown, `--check` validates and exits non-zero on any inconsistency.
- `services/api/app/rules/review_register/check_review_register.py` - stdlib validator (S2, S3, S4,
  S6, S7, S8); the per-entry checkers are separate functions so the tests can drive the negative
  cases.
- `services/api/app/rules/review_register/__init__.py` - package doc.
- `docs/zoning-rule-review/REGISTER.md` - the short current table (one row per rule), rendered.
- `docs/zoning-rule-review/rules/<rule_id>.md` - 23 detail pages, rendered.
- `docs/zoning-rule-review/HISTORY.md` - the append-only history, rendered, oldest first.
- `docs/zoning-rule-review/GUIDE.md` - handwritten: what the register is/is not, every field and its
  values, how a session updates it, how a human verdict is recorded, the code-only zoning behaviour
  list, and the note on moving to a database later. Links (not copies) to the coverage matrix, the
  law-text captures and `docs/ARCHITECT_REVIEW_QUESTIONS.md`.
- `services/api/tests/rules/test_zoning_rule_review_register.py` - 29 build-time checks (S3-S8),
  including re-deriving every example's `actual` through the real rule engine.

Design decisions honoured: the register's source is one structured JSON file with fixed field names
(table-ready for Supabase later, no DB work now); `entry_id` = the existing rule id; automated-test
status is a field apart from the human verdict and never records "passing"; every example's `actual`
is recomputed by the test through the program's own registry/evaluator while the `expected` is
worked independently from the captured law text or a named reference case; a rule-file change without
a register update fails the build; all 23 human verdicts read "Not reviewed"; this is a review
record, not a gate. No rule file, engine, registry, coverage, capture, CI, dependency or database
file was touched. The standing CLAUDE.md instruction (R379/R380) is the orchestrator's edit, out of
producer scope.

## Examples: basis and agreement

- 23 entries, one example each. Basis: **law_text 18, reference_case 4, gap 1**.
- Agreement: **agree 22, differ 0, unknown 1** (the one "unknown" is the gap example; its `agrees` is
  `null`).
- reference_case examples (worked by the sealed-folder agent in the R6B work order, section 9):
  `r6b-dwelling-units`, `r6b-height`, `r6b-lot-coverage`, `r6b-rear-yard-corner-waiver`.
- gap example: `r6-r7-r8-wide-street-conditional-far` - R6 with no wide-street determination. ZR
  23-22 gives 2.20 (not within 100 ft of a wide street) or 3.00 (within); the single correct FAR
  cannot be worked from the captured text without the geometry, so `expected` is a gap, `agrees` is
  null, and the program's own answer (2.20, conditional) is still recorded in `actual`.
- No rule's expected and actual DIFFER. (If one had, it would be `agrees: false` with a gap sentence
  and reported here; none did. No rule was changed.)

## Gaps that matter most (per the register's gaps lists)

1. R6/R7-1/R7-2/R8 FAR cannot be settled without a wide-street determination; the program returns the
   non-wide-street base value and marks it conditional.
2. The wide-street footnote allows one lot to be split between two FAR values ("or portions thereof");
   the split is not computed.
3. The pitched-roof rules (R1/R2/R3/R4/R5A) report only the 25 ft wall and 35 ft ridge anchor heights;
   the sloping-plane geometry between them is not computed (professional review).
4. Heights are measured above the base plane, which the program does not itself determine.
5. The ZR 23-433 setback above the base height is not encoded in the R6B height rule.
6. R6B corner lot coverage returns a single 100 percent; the "within 100 ft of each street line"
   corner reach is not computed.
7. The R6B rear-yard waiver covers only the area within 100 ft of the corner; the ordinary rear-yard
   depth beyond that (ZR 23-342, not captured) is not computed.
8. Dwelling-unit rules do not compute qualifying-affordable dividends, qualifying senior housing or
   conversions (no factor applies).
9. Whether a site is a "qualifying residential site" or qualifies for qualifying-housing FAR is a
   separate legal determination the program does not make.
10. Special Purpose District / overlay modifications are not applied by any rule; they send the result
    to professional review or are surfaced as alternatives.
11. The qualifying-housing FAR/height values are surfaced as labelled alternatives, never decided.
12. Every rule is a draft extraction (version 0.1.0-draft, status needs_review) awaiting raw-source
    verification and a qualified-human legal check; nothing here is a Verified determination.

## Zoning behaviour found in code with no rule id (S10 - reported, not changed, no invented ids)

- `services/api/app/rules/wide_street_wiring.py` - the within-100-ft-of-a-wide-street determination
  (mapped widths + 100-ft buffer) that several FAR/height rules mark "conditional".
- `services/api/app/rules/named_street_override_table.py` (+ `named_street_override.py`,
  `named_street_override_matching.py`, `named_street_override_status.py`) - the ZR 12-10 named-street
  alternate-width override table (e.g. Broadway, Allen Street), encoded in code.
- `services/api/app/scenario/three_answers/` and `services/api/app/scenario/derivation.py`,
  `max_envelope.py` - the engine that turns rule outputs into floor-area, envelope, dwelling-unit and
  building-option figures; it applies zoning arithmetic combining several rules, with no rule id.
- `services/api/app/rules/proposal_checks.py` - checks a proposed massing against the existing rules.
- `services/api/app/rules/integration.py` - maps property facts into rule inputs (maps; does not
  decide law).

This list is also in `docs/zoning-rule-review/GUIDE.md`; turning it into follow-up rule work is the
orchestrator's call.

## Checks (each run on its own; python = /root/project/lanes-runtime/venv/bin/python)

| # | Command (from the stated cwd) | Exit | Result |
|---|---|---|---|
| 1 | `cd services/api && python -m ruff check .` | 0 | All checks passed! |
| 2 | `cd services/api && python -m pytest -q tests/rules/test_zoning_rule_review_register.py tests/rules/test_coverage_matrix.py` | 0 | 44 passed |
| 3 | `python services/api/app/rules/review_register/render_review_register.py --check` (repo root) | 0 | register check PASSED (no issues) |
| 4 | `python3 tools/modularity_check.py --check` | 0 | pass; no new file flagged (render 356, check 333, test 297 SLOC; all under the 600 warn line) |
| 5 | `cd services/api && python -m pytest -q` (FULL api suite, final candidate, alone) | 0 | 8029 passed, 8 skipped (the 8 skips are pre-existing and unrelated) |

### Mutation proofs (each reverted; repo left clean)

- **S4** - appended a newline to `services/api/app/rules/rulesets/r6b_lot_coverage.rule.json`, then
  `pytest tests/rules/test_zoning_rule_review_register.py::test_rule_version_and_sha256_match_live_files`:
  FAILED (exit 1) with
  `r6b-lot-coverage: rule file ... content changed (sha256 ...); the register must be updated in the
  same change (new revision, history event)`. Reverted with `git checkout --`.
- **S6** - set `r1-r2-bare-pitched-height` verdict to "Correct" with no reviewer in register.json, then
  `render_review_register.py --check`: FAILED (exit 1) with
  `verdict 'Correct' is refused - it needs a reviewer name, a review date, the revision reviewed and
  the conditions reviewed (... never from tests or an AI)`. Register regenerated/re-rendered; `--check`
  back to PASSED.
- **S8** - appended a line to `docs/zoning-rule-review/REGISTER.md` by hand, then
  `pytest ...::test_register_md_is_byte_identical`: FAILED (exit 1) on the byte diff. Re-rendered with
  `--write`; the 29 register tests pass again.

## Two sample rows of REGISTER.md (exactly as rendered)

```
| R6 through R12 residence districts (flat ZR 23-22 rows) - maximum residential floor area ratio (standard residences) (`r6-r12-residential-far`) | [23-22](https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-22), applies from 2024-12-05 | 1 (2026-10-06) | 1 test file | Not reviewed | - | [open](rules/r6-r12-residential-far.md) |
| R6B district - minimum base height, maximum base height and maximum building height, standard residences and qualifying affordable or senior housing (ZR 23-432) (`r6b-height`) | [23-432](https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-432), applies from 2024-12-05 | 1 (2026-10-06) | 1 test file | Not reviewed | - | [open](rules/r6b-height.md) |
```

One detail page: `docs/zoning-rule-review/rules/r6b-height.md`.

## Assumptions, limitations, deviations

- The 5 R6B rules carry `lane_flag: "A"` and are not indexed unless lane A is enabled; the test and
  the authoring step build the registry with `LANE_A_ENABLED=true` so all 23 examples evaluate. The
  rendered register makes no claim about lane gating (it is an engine-build detail).
- The `law` block's content digests, official URLs and capture dates are read from the capture files
  and the rule citations at authoring time, never typed; `--check` re-reads the capture files and
  fails if a digest or URL drifts.
- register.json was authored with a scratch generator (kept outside the repo tree); the committed
  JSON is the real source and is what the renderer, the checker and the test read.
- The rule file title for `r1-r2-suffix-variants-pitched-height` contains an internal tag
  ("OWNER DECISION D-049, 2026-09-13"); the register shows a plain-English title for that one row so
  the rendered table carries no internal task/directive numbers (the owner's constraint). All other
  titles are the rule files' own titles.
- No deviation from scope. Only allowed_paths changed; `git status` is clean apart from gitignored
  caches.
</content>
