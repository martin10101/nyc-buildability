# M5-T189 producer report — report/figure rendering hardening (DB-277, DB-278)

Builder: backend-engineer (producer). Worktree:
`/root/project/nyc-buildability/.claude/worktrees/agent-a0cb23aa36395365c`.
Claim head (reset target): `1cbc8ccfeef53ce6986d1ccc7d76acc290d2723a` on
`task/wave28-placement-wiring`. All source changes are in-scope; no forbidden file
was edited. This is an AI agent's producer report; independent gates follow.

Plan: PLAN A of `return-plan-hardening.md`, confirmed line-by-line against the source.
Scope correction 1 (orchestrator, mid-task): added guard S10 in `layout.py` (evidence
column line-break); addressed below. Research/verification (D-093): boundary only — this
task changes no fact, reading, calculation or label; `close_frame_dimensions.py` (NB-04
pinned) was NOT edited; the `format_number` fix covers `_fact_figure` via the call path.

## The four guards

**Guard 1 — `report/layout.py::_css_string` (DB-277, scenario S1/S2).** In addition to the
existing backslash/double-quote/newline escapes, `<`→`\3C ` and `>`→`\3E ` (CSS hex escapes)
are appended AFTER the backslash doubling (so their own backslash is not doubled). A
header/footer value containing `</style>` can no longer terminate the `<style>` element the
`@page` margin boxes live in; `\3C ` renders as `<` in the content string, so any value
without angle brackets (every run-identity value: address, "Results revision N", "computed
YYYY-MM-DD") produces byte-identical CSS.

**Guard 2 — `report/formatting.py::_as_float` (DB-278, scenario S3/S4/S5).** `import math`
added; when the float is not `math.isfinite`, `_as_float` returns `None`. This single guard
makes `format_int_commas` (no `int(inf)` OverflowError / `int(nan)` ValueError),
`format_ratio` (no `"inf.0"`/`"nan.0"`), `format_sqft`, `format_feet` and
`whole_percent_shares` (no `int(nan)` crash) all degrade a non-finite document value to
missing, never 0. Finite values are untouched.

**Guard 3 — `kit/labels.py::format_number` (DB-278, scenario S6/S7).** Guard
`if isinstance(value, bool) or not isinstance(value,(int,float)) or not math.isfinite(value):
raise ValueError(...)` (`math` already imported). A non-numeric value no longer raises the
cryptic "Unknown format code 'f'"; `inf`/`nan` no longer render as literal "inf"/"nan" label
text. This also covers `close_frame_dimensions._fact_figure` (it formats through
`format_number`) with NO edit to the NB-04-pinned maps module. Finite reals (incl. `-0.0`,
thousands) are byte-identical.

**Guard 4 — `report/layout.py` `.evidence-column li { overflow-wrap: anywhere; }` (scope
correction 1, S10).** The appendix run-identity column prints the 40-character deployed
commit as one unbroken token in a `ul` inside `div.evidence-column`. With the identity commit
set, the token overflows the narrow flex column and Chromium shrinks the whole document to fit
(8 pages instead of 10). The smallest rule — let an evidence-column list item break anywhere —
restores 10 pages. It has no effect on a value that already fits, so every other output is
byte-identical. `page_evidence.py` was NOT touched (out of scope).

## Input-state tables (one test per state)

`tests/drawings/report/test_report_css_escaping.py` (6 tests):
| state | assertion |
|---|---|
| `</style>` payload in HEADER | no `</style>`/`<script>`/`</script>`; `\3C ` and `\3E ` present |
| `</style>` payload in FOOTER | no `</style>`/`<script>` |
| `_css_string("</style>")` | == `\3C /style\3E ` |
| normal value, no angle brackets | returned verbatim; CSS byte-identical; no `\3C `/`\3E ` emitted |
| S10 rule present | `.evidence-column li { overflow-wrap: anywhere }` in report_css |
| backslash/quote/newline preserved | `a\b`→`a\\b`; `"`→`\"`; CR/LF→spaces; `\<`→`\\\3C ` |

`tests/drawings/report/test_report_formatting_hardening.py` (5 tests):
| state | assertion |
|---|---|
| finite int/fractional | 20150.0→"20,150"; 6716.666→"6,716.67"; 2.0→"2.0"; feet/sqft/measure identical |
| `inf`/`-inf` | format_int_commas/ratio/sqft/feet/measure all `None` |
| `nan` | all `None` |
| whole_percent_shares non-finite member | `None`; finite set [1,1]→[50,50], [2,1,1] sums 100 |
| non-numeric/None/bool | still `None` (unchanged) |

`tests/drawings/kit/test_labels_format_number.py` (4 tests):
| state | assertion |
|---|---|
| finite reals | 1234.5→"1,234.5"; -0.0→"0"; 20150.0→"20,150"; 2→"2"; -3.25→"-3.25" |
| `inf`/`-inf`/`nan` | each raises ValueError |
| "abc"/None/[1.0]/{} | each raises ValueError |
| True/False (bool) | each raises ValueError |

## Mutation proofs (revert the guard → asserted value moves → restore)

Each guard was reverted in place, the targeted test run, then restored from a backup
(`diff -q` against the backup printed RESTORED-OK each time).

- **Guard 1 (CSS).** Removed the `<`/`>` replaces → `test_report_css_escaping.py`: **4 failed,
  1 passed** (exit 1). The breakout test re-saw raw `</style>`; `\3C /style\3E ` collapsed back
  to `\\<`. The byte-identity no-op test (normal value) correctly STILL PASSED — proof the
  guard moves only angle-bracket inputs.
- **Guard 2 (formatting).** Replaced `return result if math.isfinite(result) else None` with
  `return result` → `test_report_formatting_hardening.py`: **3 failed, 2 passed** (exit 1).
  Direct probe at the reverted code: `format_int_commas(inf)` raises **OverflowError**;
  `format_ratio(inf)` == **'inf.0'**. The two byte-identity tests (finite, non-numeric) STILL
  PASSED.
- **Guard 3 (labels).** Removed the fail-closed `if` block → `test_labels_format_number.py`:
  **3 failed, 1 passed** (exit 1). Direct probe: `format_number(inf)` → **'inf'**;
  `format_number("abc")` → **ValueError: Unknown format code 'f' for object of type 'str'**
  (the cryptic error). The finite byte-identity test STILL PASSED.
- **Guard 4 (S10).** Removed the `.evidence-column li` block, regenerated the commit-set HTML,
  printed it → **8 pages** (the bug). With the rule in place the same print is **10 pages**.

## Checks (direct exit codes; lanes venv; PYTHONDONTWRITEBYTECODE=1; pytest -p no:cacheprovider)

| check | command | result | exit |
|---|---|---|---|
| ruff (api CI first step) | `cd services/api && python -m ruff check .` | All checks passed | 0 |
| three new test files | packet cmd 2 (flock) | 15 passed | 0 |
| byte-identity proof suite | `test_report_benchmark.py tests/drawings/kit tests/drawings/maps tests/cad` (flock) | 1341 passed, 4 skipped; **no snapshot file edited** (working tree = only my 6 files) | 0 |
| modularity | `python tools/modularity_check.py --check` | selected 812 files; **failures 0**; none of my 3 production files in the 33 warnings | 0 |
| lane paths | `python3 scripts/lanes/check_lane_paths.py --coverage` | LANE COVERAGE PASS: 10812 files, each one lane | 0 |
| whole api suite | `cd services/api && python -m pytest -q` (flock) | **4 failed, 10077 passed, 8 skipped** in 484s — the 4 failures are PRE-EXISTING and out-of-scope (see below) | 1 |

### The 4 whole-suite failures are pre-existing and outside this task's scope

All four are in the zoning-rule-review register suite and report the same cause —
orphan calculation pages with no register entry:

- `tests/rules/test_zoning_rule_review_register.py::test_committed_register_validates_clean`
- `tests/rules/test_zoning_rule_review_register_calculations.py::test_committed_register_validates_clean`
- `tests/rules/test_zoning_rule_review_register_calculations.py::test_committed_calculations_validate_clean`
- `tests/rules/test_zoning_rule_review_register_calculations.py::test_no_orphan_calculation_page`

Assertion (identical across all four): `orphan calculation page with no entry:
calc-area-allocation.md` and `calc-first-placement.md`.

Evidence they are NOT caused by M5-T189:
- `docs/zoning-rule-review/calculations/calc-area-allocation.md` and `calc-first-placement.md`
  are COMMITTED at the claim head `1cbc8ccf` (tracked) and are NOT among my 7 changed files.
- My change touches no register, no calculation page, no rule module (`git status` = only
  `report/layout.py`, `report/formatting.py`, `kit/labels.py`, the 3 new test files, this
  report).
- `review_register/register.json` does NOT cite `report/layout.py`, `report/formatting.py` or
  `kit/labels.py` (grep: 0 matches), and has 0 entries for area-allocation/first-placement — so
  the orphan errors cannot interact with this task's modules.
- The register suite loads the committed register and scans the committed calculation pages,
  none of which I modified, so the result is identical with or without my edits.

Interpretation: the `task/wave28-placement-wiring` branch added two calculation pages
(area-allocation, first-placement — placement work) whose register entries are not yet
present; a separate in-flight register/placement task owns `register.json` and
`docs/zoning-rule-review/`, both OUTSIDE this packet's allowed paths. Per the brief I STOPPED
rather than edit a forbidden/out-of-scope file and report it here. Every M5-T189-owned test
(the 3 new files, the byte-identity proof suite, modularity, lane paths, ruff) is GREEN.

## Print comparison (no server, no port)

Report HTML built in-process with `TestClient POST /api/v1/properties/4073340070/report`,
`benchmark_provider(with_zoning_lot=True, street_on=True)` +
`recorded_pack_provider(benchmark_215_16_northern_window)` (LANE_A/LANE_E on); PDF via
`apps/web/scripts/print-report-pdf.mjs` (Playwright Chromium; the installed node_modules live in
the main checkout / w-wave20, not this reset worktree — printed from the main checkout's
`apps/web` against the `/tmp` HTML; no git, no server, no port). All PDFs under
`/tmp/claude-0/M5-T189/print/`.

- Print A — commit UNKNOWN, my code: **10 pages**.
- Print B — commit SET (40-hex `0123…4567`), my code: **10 pages**.
- diff_pages (A vs B): pages 1–9 IDENTICAL; page 10 (appendix) differs in the Code-commit line
  (the S10-relevant content) and the Document fingerprint.
- S10 mutation — commit SET, rule removed: **8 pages** (bug reproduced).

**Document fingerprint is non-deterministic run-to-run.** Two identical generations (same
code, same providers, same args) produced different fingerprints (c481d753400c vs 22569ba8c9a7);
main's print, Print A and the no-S10 baseline each show a different value. This is pre-existing
(a CSS change cannot alter a results-document hash) and is the only page-10 difference besides
the intended commit line.

**Airtight byte-identity.** HTML diff of the claim-head baseline (my guards 1–3 present, S10
absent) vs my output (both commit-unknown): the ONLY differences are (a) the 472-byte S10 CSS
block and (b) the non-deterministic fingerprint. After removing the S10 block and normalizing
the fingerprint, the two HTML strings are **byte-identical** — the three guards change zero
bytes of valid-document output, and S10 adds exactly one CSS rule.

**vs main's print** (`print-main-86a450d4/report.pdf`): both 10 pages. The text differences are
NOT from this task: (1) the identity header line (main's preview threads the confirmed street
address "215-16 NORTHERN BOULEVARD, Queens"; the TestClient provider recipe shows "Queens ·
block 7334, lot 70") — produced by `readers.py`, not touched here; (2) the document fingerprint
(non-deterministic, above). `git status` shows only my 6 files changed; neither `readers.py`
nor any rule/register file is among them, so neither difference can originate in this task.

## What I could not check / limitations

- The whole api suite result is recorded above from the frozen run on this head; e2e/web
  (Playwright specs) and full security/dependency gates run in CI at the accepted head
  (thin-client rule) — not run here.
- The PDF was printed from the main checkout's installed Playwright (this reset worktree has no
  `apps/web/node_modules`); the HTML is generated entirely from this worktree's code and the
  print script is byte-identical across checkouts at this head.
- The document-fingerprint non-determinism is a pre-existing observation surfaced while proving
  S10; it is outside this task's scope (no fingerprint code changed) and is noted for the
  orchestrator's backlog sweep.
