# M5-T097 producer report - D-087 CAD-3: DXF reader hardening + committed round trip

## ROUND 2 (rework) - fix the O(n^2) splitter (G3-B1 = G5-Finding-1) + close G4 ADVISORY-1 + G3-A1 wording

Round 1 was reviewed: G4 PASS (advisories), G3 FAIL and G5 FAIL on ONE shared root cause -
the round-1 streaming splitter `_iter_dxf_lines` called BOTH `text.find("\n", pos)` and
`text.find("\r", pos)` every line, so when one terminator was absent (pure-LF - our own
writer's output - or pure-CR) the other `find` rescanned to EOF each line: O(n^2). This
rework is ONE bounded change on top of integration head `481e51ff` (worktree verified
`rev-parse --show-toplevel` == the wt-m5t097 path; HEAD == 481e51ff before any edit; no reset).

### What changed (only the two files this fix touches)
- `services/api/app/drawings/dxf_reader.py`: replaced the per-line double-`find` with a SINGLE
  precompiled `_LINE_TERMINATOR = re.compile(r"\r\n|\r|\n")` and `.search(text, pos)` - one
  C-level pass that finds the next terminator of any of the three kinds and NEVER rescans for an
  absent one (O(n) total). Added `import re` (stdlib; zero new deps). Semantics are BYTE-IDENTICAL
  to round 1: CR/LF/CRLF are the only terminators (CRLF alternative first so `match.end()` absorbs
  a full CRLF as one break); `\x0b \x0c \x1c-\x1e` stay in the value; streaming generator;
  `max_lines`/`max_line_chars` still enforced during the scan. Parity proven on 22 edge cases
  (old-vs-new identical, 0 mismatch). Also fixed the docstrings per G3-A1 (see finding closure).
- `services/api/tests/drawings/test_dxf_reader.py`: +5 tests (added `import time`). No existing
  test edited; the 49 prior reader + 7 round-trip tests pass unchanged. `test_dxf_roundtrip.py`
  was NOT touched (no change needed).

### Round-2 self-checks [all OBSERVED], explicit cwd
- cwd `services/api` - `python -m ruff check .` -> `All checks passed!`
- cwd `services/api` - `python -m pytest tests/drawings/test_dxf_reader.py tests/drawings/test_dxf_roundtrip.py -q`
  -> `61 passed in 6.68s` (56 round-1 + 5 new; the ~6s is the two deterministic time-guard tests).
- cwd repo root - `python tools/modularity_check.py --check` -> `failures 0`, EXIT=0
  (dxf_reader.py 613 SLOC via `--report --json`; still the WARN band, 600<613<750, unchanged
  disposition from round 1's 603; DISC-1 lexer/model split still routed, not in this packet's
  allowed_paths).
- Zero new dependencies (`re` is stdlib); unwired (only its own test imports the module); public
  API and the `DxfRefusalReason` refusal vocabulary unchanged.

### Before/after timings (scratch `parity_timing.py`, cwd `services/api`, PYTHONPATH=services/api) [OBSERVED]
Fully consuming the splitter (min-of-3, seconds); "old" = the round-1 double-`find`, "new" = this fix.

| input   | lines | old (s) | new (s) | speedup |
|---------|-------|---------|---------|---------|
| pure-LF | 50k   | 0.4053  | 0.1190  | 3.4x    |
| pure-LF | 100k  | 1.4420  | 0.1797  | 8.0x    |
| pure-LF | 200k  | 5.5547  | 0.4840  | 11.5x   |
| pure-CR | 50k   | 0.4378  | 0.1135  | 3.9x    |
| pure-CR | 100k  | 1.5075  | 0.2162  | 7.0x    |
| pure-CR | 200k  | 5.3195  | 0.4438  | 12.0x   |

Old scales ~4x per doubling (quadratic); new scales ~2x per doubling (linear). CRLF was already
linear under both (the `\r` is present, so `find` never rescans to EOF) - control, unchanged.

### Round-2 mutation table (all in-process, rebind the CONSUMED module global, then restore) [OBSERVED via the committed suite]

| Guard (new/edge) | Mutation | Result |
|---|---|---|
| sub-quadratic splitter time | rebind `_iter_dxf_lines` to the round-1 double-`find` | 4x-input ratio at N=30k rises to ~11.8x (>= 8 ceiling) -> `test_t097_b1_splitter_time_subquadratic_*` would redden; the mutation test asserts `mutant_ratio >= 8` and the real splitter stays `< 8` [KILLED] |
| `max_lines` exact edge (B6) | `count > max` -> `count > max + 1` | a 20-line file at `max_lines=19` no longer refused (parses) -> `test_t097_as2_max_lines_exact_edge_*` reddens [KILLED] |
| `max_line_chars` exact edge (B7) | `len(line) > max` -> `len(line) > max + 1` | a 30-char line at `max_line_chars=29` no longer refused (parses) -> `test_t097_as2_max_line_chars_exact_edge_*` reddens [KILLED] |

The scaling ratio is machine-speed-independent (linear ~4x, quadratic ~16x, ceiling 8x with 2x
margin) and uses min-over-reps, so no tight absolute wall-clock is asserted - robust on a loaded
CI runner. Every round-1 mutation (below) still holds; nothing else changed.

### Per-finding closure
- G3-B1 / G5-Finding-1 (BLOCKING, one root cause): CLOSED. Single-pass regex scan; O(n) proven by
  the timing table and the two committed time-guard tests (one reddens under the exact round-1
  double-`find`). Parity: 22 edge cases identical old-vs-new.
- G4 ADVISORY-1 (exact-edge B6/B7): CLOSED. Added exact-edge refusal probes at `max_lines+1` lines
  and `max_line_chars+1` chars (both off-by-one mutants now die), and kept exactly-at-the-limit
  passing (`max_lines=20`, `max_line_chars=30` both parse to a DxfDocument).
- G3-A1 (wording only): CLOSED. The module docstring and `_iter_dxf_lines` docstring no longer
  claim the control char is kept "VERBATIM"; they now state it is never a terminator (no pairing
  shift), survives when flanked by non-whitespace, and that the pre-existing per-value `.strip()`
  trims it when leading/trailing (a value of ONLY such chars strips to `''`). The `.strip()`
  behaviour is UNCHANGED (no code change).
- Out of scope, NOT done (declared): G5 A3 digit cap, G5 A1/A2/A4 import-route items, and the
  lexer/model split are for later gated packets (DISC-1). G3 A2 (round-1 doc-sync note) needs no
  action. No new discoveries in round 2.

---

## ROUND 1 (baseline record, unchanged below)

Producer: backend-engineer (orchestrator-dispatched subagent). Worktree
`C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t097`, branch `task/M5-T097-dxf-reader-hardening`,
based at claim-seam `2e0b2351` (verified `git -C wt-m5t097 rev-parse --show-toplevel` ==
the wt-m5t097 path; `git reset --hard 2e0b2351` done before any edit).

## Scope / isolation

Changed exactly the four allowed paths:
- `services/api/app/drawings/dxf_reader.py` (hardening; +139/-25 lines)
- `services/api/tests/drawings/test_dxf_reader.py` (21 new cases; existing 28 unchanged)
- `services/api/tests/drawings/test_dxf_roundtrip.py` (placeholder replaced; 7 cases)
- `project-control/reports/M5-T097-producer-report.md` (this file)

`git status --short` shows only the three source/test files (plus this report). No forbidden
path touched: `app/cad/` (writer, M5-T096) used READ-ONLY by the round trip; `app/documents/`,
`app/api/`, `app/main.py`, `requirements*.txt/.in`, the `sheet_*` split, `app/drawings/__init__.py`
all untouched. Zero new dependencies (added only the stdlib `collections.abc.Iterator` import;
tests add stdlib `tracemalloc` + already-admitted `pytest`). Unwired: nothing imports
`dxf_reader` except its own test; the max-envelope route stays unmounted.

Public API kept source-compatible: `read_dxf(data, *, limits=DEFAULT_LIMITS)`, `DxfLimits`,
`DxfDocument`, `DxfRefusal`, and the `DxfRefusalReason` closed vocabulary are all unchanged (no
new enum member; the new refusals reuse `MALFORMED_STRUCTURE` / `BINARY_DXF` / `NON_ASCII`).
Every refusal remains a typed RETURNED value; no exception escapes `read_dxf`. No behaviour
change for a VALID ASCII DXF (bytes or str) - all 28 pre-existing tests pass byte-unchanged.

## Declared design choices (packet open points)

1. Control character in a value (`\x0b \x0c \x1c-\x1e`, which `str.splitlines` would split on):
   KEPT VERBATIM in the value. Rationale: the only defect is the pairing shift; keeping the
   char verbatim is the minimal fix, adds no new refusal path (so it can never reject a file a
   lenient reader would accept), and a control char landing in a coordinate still fails closed
   at `_to_float` (BAD_COORDINATE). Valid DXF never carries raw control chars in values.
2. `DxfLimits` above the ceiling: CLAMPED DOWN (fail-safe), never raised. Rationale: clamping
   guarantees the size/line/entity/vertex protections can never be disabled by a permissive
   caller (G5-A1) WITHOUT breaking any caller who passes a reasonable limit, and without a
   raise. Ceilings (`_LIMIT_CEILINGS`) sit well above the reviewed `DEFAULT_LIMITS`, so every
   legitimate limit passes through unchanged; only an attempt to effectively disable a bound is
   reduced. The pre-existing `< 1` lower-bound guard still RAISES (unchanged) - a `< 1` limit
   is a caller bug, not an over-permission.
3. `str` input: CHECKED (not refused, not passed through leniently). Rationale: refusing `str`
   outright would break source compatibility and the entire existing suite (which drives the
   reader with `str` fixtures throughout). Instead the `str` path now applies the SAME
   binary-sentinel and non-ASCII (`str.isascii()`) checks as the `bytes` path, closing G5-A3;
   any non-bytes/non-str input is a typed `MALFORMED_STRUCTURE` refusal, never a raised TypeError.

## $INSUNITS 22/23/24 citation

Added `22 -> us_survey_inches`, `23 -> us_survey_yards`, `24 -> us_survey_miles` to
`_INSUNITS_NAMES` (lowercase-plural to match the existing `21 -> us_survey_feet`). Autodesk DXF
Reference, INSUNITS values 0-24 (US Survey Inch/Yard/Mile) - marked **[recalled - verify]** in
source because this producer could not re-open the live page; the same range was already
verified against the LIVE reference in `M5-T081-G1.md` (GUID-A58A87BB-482B-4042-A00A-EEF55A2B4FD8,
cloudhelp/2025), which named "codes 22-24 = US Survey Inch/Yard/Mile". G1 also flagged the
omission as the advisory this closes (DB-057 (n)).

## Commands (verbatim; explicit cwd)

CMD1 - cwd `services/api` - `python -m ruff check .`  [OBSERVED]
```
All checks passed!
```

CMD2 - cwd `services/api` - `python -m pytest tests/drawings/test_dxf_reader.py tests/drawings/test_dxf_roundtrip.py -q`  [OBSERVED]
```
........................................................                 [100%]
56 passed in 0.57s
```
(28 pre-existing reader tests + 21 new reader tests + 7 round-trip tests = 56.)

CMD3 - cwd repo root - `python tools/modularity_check.py --check`  [OBSERVED] EXIT=0
```
selected 488 files; failures 0; warnings 27
  warn review_signal: services/api/app/drawings/dxf_reader.py - above the warning threshold; consider the module boundary before growing it further
```

Environment: local Python 3.11.9, ruff 0.13.0. CI is 3.12 (authority on the pushed head).

### Known local-only collection artifact (NOT introduced here)
`python -m pytest tests/drawings tests/cad` fails COLLECTION on `tests/drawings/test_sheet_reader.py`
(a FORBIDDEN file) because `app/documents/units.py:276` uses PEP-695 generic syntax
(`def _match_unit[UnitT: enum.Enum]`) that Python 3.11 cannot parse. This is the pre-existing
3.11-vs-3.12 artifact documented in M5-T086-G3/G4 ("Local 3.11 collection blocked by
app/documents/units.py PEP-695"); it does not touch my files (which import only stdlib +
`app.cad.dxf_writer`) and clears under CI 3.12. `tests/cad/test_dxf_writer.py` alone: 24 passed
on 3.11 (the writer used by the round trip is intact).

## Per-scenario evidence  [all OBSERVED]

AS-1 (line splitting):
- `test_t097_as1_cr_lf_crlf_parse_identically` - CR, LF and CRLF files yield byte-identical
  primitives (splitter recognises those three terminators, and only those).
- `test_t097_as1_control_char_in_value_kept_verbatim` - a TEXT value with each of
  `\x0b \x0c \x1c \x1d \x1e` parses and the char survives verbatim (no pairing shift).
- `test_t097_as1_mutation_restoring_splitlines_reddens` - NAMED mutation: rebinding the
  consumed `_iter_dxf_lines` to a `str.splitlines()` version splits the form-feed value and
  breaks the clean parse (ODD_PAIR_COUNT), proving the CR/LF-only splitter is load-bearing.

AS-2 (bounds):
- `test_t097_as2_max_lines_refused` - over-`max_lines` -> TOO_MANY_LINES (no existing test
  pinned this).
- `test_t097_as2_max_lines_enforced_before_full_list_allocation_probe` - WORK/ALLOCATION PROBE:
  on a ~2 MB / one-million-line input capped at 1000, the streaming splitter's tracemalloc peak
  stays < 2 MB and is > 3x smaller than a `splitlines`-materialising mutant that builds the whole
  list up front. This is the AS-2 "enforced before the full line list exists" mutation.
- `test_t097_as2_limits_clamped_above_ceiling` + `test_t097_as2_limit_ceilings_are_reviewed_constants`
  - a permissive `DxfLimits` (each field 1e12-1e18) clamps to the hard ceilings; ceilings pinned
  (drift guard).
- `test_t097_as2_below_one_limit_still_raises` - the pre-existing `< 1` guard still raises for
  every field.
- `test_t097_as2_mutation_clamp_reddens` - mutation: raising the ceiling in-process defeats the
  clamp (raw 1e18 passes through), proving the clamp is load-bearing.
- `test_t097_as2_str_non_ascii_refused` / `test_t097_as2_str_binary_sentinel_refused` /
  `test_t097_as2_unsupported_input_type_refused` - the `str` path now refuses non-ASCII and the
  binary sentinel; a non-bytes/str input -> MALFORMED_STRUCTURE (typed value).
- `test_t097_as2_mutation_str_check_reddens` - mutation: a lenient `_decode` (old behaviour)
  passes a non-ASCII str through, so the NON_ASCII refusal disappears.

AS-3 (probe gaps + INSUNITS):
- `test_t097_as3_nan_coordinate_refused` (+ `_nan_probe_kills_finiteness_half_guard`) - nan
  refused; the in-process `isinf`-only mutant (G4 M3) lets nan through -> reddens.
- `test_t097_as3_negative_lwpolyline_bulge_refused` / `_negative_vertex_bulge_refused` - negative
  bulge on both the LWPOLYLINE and old-style VERTEX paths refused (the VERTEX-bulge path had no
  test at all).
- `test_t097_as3_closed_flag_128_is_open` / `_closed_flag_129_is_closed` - flag 128 -> open, 129
  -> closed (only bit 1 = closed).
- `test_t097_as3_insunits_survey_inch_yard_mile_reported` (+ `_mutation_insunits_codes_reddens`)
  - 22/23/24 report named survey units; removing them returns `unknown_insunits_22` -> reddens.

AS-4 (round trip - `test_dxf_roundtrip.py`, writer used READ-ONLY via
`render_site_plan_dxf`):
- `test_roundtrip_header_units_read_from_writer_output` - ok=True, units code 21 /
  `us_survey_feet` / `header:$INSUNITS`, acad `AC1009`.
- `test_roundtrip_tables_section_is_skipped_not_pinned` - `"TABLES"` in `skipped_sections`,
  `disclosed_unknown == ()`; the test does NOT pin TABLES contents or any writer golden digest,
  so M5-T096 adding STYLE/VPORT tables cannot break it.
- `test_roundtrip_lot_ring_exact_and_closed` / `_building_ring_exact_and_closed` - each footprint
  reads back as exactly one CLOSED polyline whose vertices equal the written open ring in order.
- `test_roundtrip_layers_and_entity_counts_as_written` - LOT + BUILDING_OUTLINE (1 polyline
  each), MASSING_3D band polylines = floors+1, 3DFACE walls = edges*floors, vertical LINEs =
  edges, ANNOTATION texts; `entity_count` equals the derived total.
- `test_roundtrip_honesty_texts_present` - the three fixed provenance labels survive verbatim on
  the ANNOTATION layer.
- `test_mutation_roundtrip_perturbed_lot_vertex_reddens` - NAMED mutation: bumping the lot
  polyline's first vertex X by one foot in the serialized output changes the read-back ring
  (only that vertex moves), so the exact-ring assertion has teeth.

AS-5 (compatibility + scope): 28 pre-existing reader tests pass unchanged; edits only ADD cases;
zero new deps; unwired; exactly the allowed paths (see Scope / isolation).

## Mutation table

| # | Guard (new) | Mutation | Result |
|---|---|---|---|
| 1 | CR/LF-only split | restore `str.splitlines()` (rebind `_iter_dxf_lines`) | form-feed value splits -> not the clean doc; committed test reddens [OBSERVED] |
| 2 | streaming `max_lines` | `splitlines()`-materialise before the count check | tracemalloc peak balloons > 3x; committed allocation probe distinguishes [OBSERVED] |
| 3 | `DxfLimits` clamp | raise the ceiling so clamp no longer bites | raw 1e18 passes through; committed test reddens [OBSERVED] |
| 4 | `str` checks | lenient `_decode` (old str pass-through) | non-ASCII str no longer NON_ASCII; committed test reddens [OBSERVED] |
| 5 | INSUNITS 22/23/24 | pop 22/23/24 from `_INSUNITS_NAMES` | `unknown_insunits_22`; committed test reddens [OBSERVED] |
| M3 | (existing) finiteness | `not isfinite` -> `isinf` (rebind `_to_float`) | nan reaches primitive; nan probe reddens [OBSERVED] |
| M4a | (existing) LWPOLYLINE bulge | `!= 0` -> `> 0` (rebind `_parse_lwpolyline`) | neg-bulge parses; neg-lwpoly probe reddens [OBSERVED, scratch] |
| M4b | (existing) VERTEX bulge | `!= 0` -> `> 0` (rebind `_parse_polyline`) | neg-bulge parses; neg-vertex probe reddens [OBSERVED, scratch] |
| M5 | (existing) closed flag | `& 1` -> `bool(flags)` (rebind `_closed_from_flags`) | flag 128 reported closed=True; flag128 probe reddens [OBSERVED, scratch] |
| AS-4 | round-trip ring exactness | perturb one lot vertex in writer output | read-back ring changes; committed test reddens [OBSERVED] |

Mutations 1-5 and AS-4 are committed as in-process mutation tests (rebind the CONSUMED module
global, then restore) and run green. M3/M4a/M4b/M5 confirm the AS-3 behaviour probes kill the G4
survivors; the in-process rebind runs are recorded here from a scratch verification (baseline
refused/open; each mutant flips the behaviour, so the committed behaviour test would FAIL under
the mutant). No production code was left mutated.

## Deviations

- Modularity: `dxf_reader.py` is 603 SLOC after the required hardening - 3 over the soft WARNING
  threshold (600), well below the JUSTIFY (750) and HARD (1000) thresholds. `--check` PASSES
  (failures 0, exit 0). JUSTIFICATION: the module is one cohesive strict-subset DXF parser
  (decode -> stream/split -> pair -> walk/parse -> typed model); the growth is entirely
  in-responsibility hardening. This packet's `allowed_paths` grant ONLY `dxf_reader.py`, so a
  lexer/model split into a new module is out of scope here (there is no path to write it). I
  trimmed docstring prose to keep the overshoot minimal. Precedent: sibling `sheet_reader.py`
  (818 SLOC) passed G3 with a recorded cohesion justification.

## Discoveries (routed, not fixed in-packet)

- DISC-1: `dxf_reader.py` crossed the modularity WARNING band. When a future gated packet wires
  the reader (or hardens it further), it should grant an additional module path so the line
  splitter/limits (lexer) can be split from the entity parser behind a compatibility facade.
- DISC-2 (pre-existing, informational): local Python 3.11 cannot collect `tests/drawings/`
  as a directory because `app/documents/units.py` uses PEP-695 syntax; CI 3.12 is unaffected.
  Already known (M5-T086-G3/G4); no action needed here.
- DB-057 residuals NOT in this packet's scope remain open: (a)+(b) AutoCAD-open check and
  STYLE/VPORT belong to M5-T096 / the export packet; (d)+(k residual) raw-length caps belong to
  the user-geometry / user-DXF wiring seam; (f) the T081 evidence-map allowlist widening belongs
  to the next `test_dxf_writer.py` touch.

END-OF-REPORT
