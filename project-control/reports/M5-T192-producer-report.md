# M5-T192 (part B2 of M5-T173) producer report — section height-limit lines

Builder: backend-engineer. Worktree: `/root/project/nyc-buildability/.claude/worktrees/agent-a8940a6a78e64038a`.
Base head reset to `b9e9d563a8b9e869bcaf4af8862c9f3d411de645` (head of `task/wave29-scenario-drawings` at dispatch).

## What changed and why

Audit 2026-10-15c section 4 asks for a compact section carrying the relevant height limits, drawn
only where the document supports them. The draft (pre-split) read heights from `envelope_rows`, which
carry no heights; the benchmark carries them in `answers.permitted_envelope` (30/45/55 ft, ZR 23-432).
Opt-in only; without the new keyword every output is byte-identical.

1. **NEW `services/api/app/drawings/kit/section_legal_lines.py`** — a pure reader
   `section_legal_lines(results)` returning the STANDARD-case height lines from
   `results.answers.permitted_envelope` (status `available`; keys `min_base_height`,
   `max_base_height`, `max_building_height`). Each surviving entry must be a finite non-negative
   number in unit `feet` with a non-empty label; it carries the document's own label, `zr_sections`
   and the RFC 6901 pointer of its value (`/answers/permitted_envelope/values/<i>/value`) for
   provenance. Nothing computed, no building comparison, no qualifying-housing key, nothing from
   `envelope_rows`. A missing or malformed key drops only that line; `None` when none survive (never a
   default). `LegalLine` is a frozen dataclass.

2. **`services/api/app/drawings/kit/section.py`** — `draw_floor_stack(alternative, *, caption=True,
   legal_lines=None)`. With `legal_lines`, the height axis scales to the higher of the building top
   and the highest limit, in a compact layout (`_LEGAL_STACK_TOP=24`, `_LEGAL_STACK_H=200`) so the
   whole drawing is at most 260 pt tall; each limit is a dashed reference line (reused
   `_REFERENCE_STROKE`, dash `4.00 2.00`) labelled `"{document label} {value} ft"` at the existing
   8 pt label size, carrying the value's pointer as its `data-source` (role `floor_stack_legal_line`).
   Where a legal minimum-base line coincides with the `to_min_base` building top (both 30 ft here),
   the bare "Minimum base height" reference is suppressed so ONE line carries the document value.
   `legal_lines=None` leaves `axis_max/stack_top/stack_h/k/grade_y` and the min-base guard exactly as
   today → byte-identical.

3. **`services/api/app/drawings/kit/__init__.py`** — `render_floor_stack(alternative, *,
   frame='report', env=None, results=None)`. With `results` it reads (1) and passes the lines;
   omitted (the signature B3 checks by keyword) it is byte-identical to today's call.

No file outside the allowed paths was touched. No reference case, snapshot, benchmark fixture,
register or evidence record was edited: none of my files appears in any record's `code_paths`
(NB-04's `code_current=False` is pre-existing, DB-283, owned by part W). Renderer-only: every
displayed value comes from the results document; no law is evaluated.

## D-093 grounding (research and verification)

Expected heights are literals taken from reference case `docs/reference-cases/R6B/cases/real-lot.json`
row L3 and the ZR 23-432 capture `docs/research/zr-snapshots/v1/zr-23-432.snapshot.json`
(min base 30 ft, max base 45 ft, max building 55 ft; R6B row carries no footnote so wide/narrow does
not change them) — never a program run. Label PROSE is read from the fixture at test time (a later
wording pass may reword it; the numbers stay literal). NB-06 read only.

## Checks (direct exit codes)

- `cd services/api && python -m ruff check .` — **exit 0** ("All checks passed!").
- `cd services/api && flock …/heavy-run.lock python -m pytest -q tests/drawings/kit` — **exit 0**,
  **507 passed** (the 88 existing report-frame/rework tests pass unedited: default/K7 caption and the
  "Minimum base height" bare-label render are byte-identical).
- `tests/drawings/kit/test_section_legal_lines.py` alone — **exit 0**, **22 passed**.
- `python tools/modularity_check.py --check` — **exit 0** (B2 files not in any warn row;
  `section_legal_lines.py` ~110 SLOC, `section.py` grew to ~190, both well under thresholds).
- `python3 tools/research_record_check.py --check` — **exit 0**, PASS (7 records; NB-04 pre-existing).
- `python3 scripts/lanes/check_lane_paths.py --coverage` — **exit 0**, LANE COVERAGE PASS.

## Mutation proof (revert behaviour → test fails → restore)

- Reverting `render_floor_stack` to ignore `results` (`legal_lines=None`): the 3 S2 behaviour tests
  FAIL (`assert ['Minimum base height'] == []`), `test_s3_reader_returns…` still passes (reader
  untouched).
- Removing the coincidence suppression (`and not coincides_with_min_base_top`):
  `test_s2_one_line_where_the_minimum_base_coincides…` FAILS (bare "Minimum base height" reappears).
- Removing the reader `unit == 'feet'` guard: S3 case `[unit is not feet]` FAILS.
- Removing the reader finite/non-negative guard: S3 cases `[value is NaN]`, `[value is +inf]`,
  `[value is negative]`, `[value is a string]`, `[value is a boolean]` FAIL.
- All files restored; ruff and the 22 tests green again after restore.

## Picture (visual review)

`/tmp/claude-0/M5-T192/section_legal_lines_benchmark.svg` (+ `.png`) — benchmark Building B with
`results=doc`: three dashed limit lines "Maximum building height 55 ft", "Maximum base height 45 ft",
"Minimum base height 30 ft"; the 30 ft line coincides with the Storey 3 top as ONE line; storey tops
10/20/30 ft and the grade line kept; compact 360×238 pt. `section_no_results_benchmark.svg` is the
unchanged 360×358 pt baseline for comparison. No SVG→PNG converter in the api lane venv; PNG rendered
with the installed chromium (no server, no ports).

## Scenario evidence

- **S1** byte-identical without `results`/`legal_lines`: `test_s1_default_render_is_byte_identical_without_results`,
  `test_s1_legal_lines_none_is_byte_identical`, and the 88 forbidden report-frame tests pass unedited.
- **S2** three lines, storey tops kept, ≤260×515.9 pt, one line at 30 ft, every number a document
  number, provenance per source: `test_s2_*` (4 tests).
- **S3** per-state drop table (12 parametrized states + single-bad-key + reader-returns): `test_s3_*`.
- **S4** `envelope_rows` never become a line: `test_s4_envelope_rows_never_become_a_line`,
  `test_s4_envelope_rows_alone_draw_no_line`.
- **S5** a 1.4.0 document (`synthetic_building_alternatives_contract_1_4_0.json`, permitted_envelope
  not available) renders identically: `test_s5_a_1_4_0_document_renders_identically`.

## Assumptions / limitations

- Label wording "Minimum/Maximum base height", "Maximum building height" is the document's own prose
  (fixture), appended with the reference-case number; a later M5-T180 reword would not need to touch
  these tests (numbers stay literal; prose read at test time).
- Compact constants give 238 pt (caption off, the report frame) / 256 pt (caption on): both under the
  260 pt cap by construction; no explicit clamp added so the drawing is never clipped.
- Interface with B3 is `render_floor_stack(..., results=None)`, checked by signature, so the two land
  in either order. No cross-part import.
- Full api pytest, vitest/e2e and the real report print are not part of B2 (renderer/page level); they
  are part W's and CI's at the integrated head.
