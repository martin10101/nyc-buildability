# M5-T097 producer report - D-087 CAD-3: DXF reader hardening + committed round trip

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
