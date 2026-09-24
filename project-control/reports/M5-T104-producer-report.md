# M5-T104 producer report — architect-sheet reader test debt (D-087 PKT-K2)

Producer: backend-engineer. Worktree: `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t104`
(branch `task/M5-T104-sheet-reader-test-debt`). Claim seam / parent:
`e9a268a52704a073a52ee0a34f4230394dbf9a49`.

Scope: close the recorded test gaps for the architect drawing-sheet reader (DB-055 a, e, i;
DB-064 a, b) WITHOUT changing production behaviour, plus the one-line §8.3.3→§8.3.4 citation fix.
No route, endpoint, or wiring touched. Zero new dependencies. Files written are exactly the three
allowed paths.

## Files changed

- `services/api/app/drawings/sheet_primitives.py` — one line only: the `apply_matrix` docstring
  citation `§8.3.3` → `§8.3.4` (DB-055 e). No code/behaviour change. (Note: the separate `§8.3.3`
  on the `Matrix` type-alias comment at the top of the file is a different citation and was left
  untouched, per "fix ONLY the apply_matrix citation".)
- `services/api/tests/drawings/test_sheet_reader.py` — strengthened the existing
  `test_mid_path_cm_does_not_corrupt_curve_start` (DB-055 a) and added 9 new tests (DB-055 i,
  DB-064 a/b). No existing test edited except the DB-055 (a) strengthening. 37 → 46 tests.
- `project-control/reports/M5-T104-producer-report.md` — this report.

## Acceptance-scenario evidence

### AS-1 (non-vacuous mid-path cm) — DB-055 (a)
`test_mid_path_cm_does_not_corrupt_curve_start` now pins `points[1]` — the reopened curve's FIRST
INTERIOR flattened point — the field the bug displaces. `points[0]` (moveto point) and `points[-1]`
(`= map(*end)`) are invariant under the pre-fix revert, so the prior assertions were vacuous
(G4-rework F6 / DCV F3). Real `points[1] = (14.160156, 13.339844)`. Under the literal pre-fix revert
`p0 = _apply_matrix(self._ctm, *self._current)` in `_StreamRun._curveto`, `points[1]` jumps to
`(23.125, 20.3125)` (matches the DCV's measured (23.12, 20.31)); `points[0]`/`points[-1]` stay
(10,10)/(40,40). Mutant recorded below (M1). Production code is correct; only the guard was weak.

### AS-2 (operator coverage + true rotated rectangle) — DB-055 (i)
Every operator DB-055 (i) lists is now executed by a test with an asserted outcome:
- `re` + `S`: `test_rotated_rectangle_via_re_maps_each_vertex` — a GENUINE 4-corner rectangle under a
  30° rotation CTM, `poly.closed and poly.stroked and not poly.filled`, `len(points)==4`, each vertex
  asserted `== _rotate_then_translate(cx, cy, 0, 0)` (abs=1e-9). Replaces the old rotated-LINE test.
- `v`: `test_v_curve_first_control_is_the_current_point` — first control = current point; `points[1]`
  pinned (21.71875, 19.257812).
- `y`: `test_y_curve_last_control_is_the_endpoint` — last control = endpoint; `points[1]` pinned
  (4.194336, 7.041016).
- `s, f, F, f*, B*, b, b*, n` (+ `S`): `test_all_paint_operators_set_expected_flags` — asserts
  (stroked, filled, closed) for each and that the path geometry is surfaced.
- `W, W*`: `test_clip_operators_are_ignored_and_keep_the_path` — consumed, not refused, path kept and
  painted by the following `n`.
- `TL, Td, TD, T*, Tj`: `test_text_line_moves_place_runs_with_leading` — run origins A(100,700),
  B(100,680), C(100,660), D(100,646).
- `TJ, ', "`: `test_text_show_TJ_quote_and_dquote_operators` — XY(50,470), P(50,460), Q(50,450);
  TJ joins string pieces and skips the numeric kern.

### AS-3 (budget semantics) — DB-064 (a)/(b)
- (a) `test_two_distinct_form_xobjects_decode_and_place` — two DISTINCT Form XObjects (FmA →
  (0,0)-(5,0); FmB placed at +100 → (100,0)-(100,9)) both decode and place correctly. A wrong-key
  (constant) form memo makes FmB reuse FmA's bytes → second polyline becomes (100,0)-(105,0); mutant
  M9 reddens the test.
- (b) `test_multi_stream_document_decoded_bytes_budget_is_per_document` — a `/Contents` array of two
  13-byte streams with `MAX_TOTAL_DECODED_BYTES` patched to 20: each stream (13) is under the cap but
  the sum (26) exceeds it, so the SECOND charge refuses "decoded bytes budget". This input ONLY
  refuses under per-DOCUMENT accumulation; a per-stream charge (each 13 ≤ 20) never refuses (mutant
  M10). This is the accumulation the pre-existing single-stream cap=4 test could not exercise.

### AS-4 (no production change + scope)
`git diff --stat`: only `sheet_primitives.py` (2 lines: 1 changed) and `test_sheet_reader.py`.
The `sheet_primitives.py` diff is the citation text only. The forbidden
`test_sheet_reader_split_equivalence.py` golden file is untouched and stays green (9/9). Zero new
dependencies (stdlib + already-admitted only; no requirements/lockfile touched). Exactly the allowed
paths written.

## Mutation table (each mutates the CONSUMING namespace in-process; red-run values recorded)

| # | Test / AS | Consuming-namespace mutant | Real value | Mutant value (RED) |
|---|-----------|----------------------------|-----------|--------------------|
| M1 | mid_path_cm / AS-1 | `_StreamRun._curveto` pre-fix `p0=apply_matrix(ctm,current)` (method, dynamic lookup) | points[1]=(14.160156,13.339844) | (23.125,20.3125) |
| M2 | rotated_rect / AS-2 | `sheet_interpreter._apply_matrix` = identity | verts rotated | verts unrotated (10,20),(40,20),(40,35),(10,35) |
| M3 | v curve / AS-2 | `sheet_interpreter._PATH_HANDLERS["v"]` with ctrl1_is_current=False | points[1]=(21.71875,19.257812) | (17.15332,16.494141) |
| M4 | y curve / AS-2 | `sheet_interpreter._PATH_HANDLERS["y"]` p2≠endpoint | points[1]=(4.194336,7.041016) | (6.71875,13.203125) |
| M5a | paint / AS-2 | `sheet_interpreter._PAINT_STROKE` = ∅ | S stroked=True | False |
| M5b | paint / AS-2 | `sheet_interpreter._PAINT_FILL` = ∅ | f filled=True | False |
| M5c | paint / AS-2 | `sheet_interpreter._PAINT_CLOSE_FIRST` = ∅ | s closed=True | False |
| M6 | clip / AS-2 | `sheet_interpreter._IGNORED` − {W,W*} | DOC (poly kept) | REFUSAL "unsupported operator" |
| M7 | text moves / AS-2 | `sheet_reader._concat_matrix` = (λ m,ctm: m) | B@(100,680) | (0,-20) |
| M8 | text show / AS-2 | `sheet_reader._concat_matrix` = (λ m,ctm: m) | XY@(50,470) | (0,-30) |
| M9 | two forms / AS-3(a) | `_StreamDecoder.decode_form` constant key (0,0) | poly1=(100,0)-(100,9) | (100,0)-(105,0) |
| M10 | multi-stream budget / AS-3(b) | `_StreamDecoder.charge_decoded` per-stream (count>cap) | REFUSAL "decoded bytes budget" | DOC (no refusal) |

Key note (by-value trap avoided): the path operators dispatch through the module-level dict
`sheet_interpreter._PATH_HANDLERS`, which holds the ORIGINAL functions by value; patching
`_StreamRun._op_v/_op_y` is a FALSE survivor (verified — no change). The true consuming namespace is
`_PATH_HANDLERS[...]`. `_curveto` is called via `self._curveto(...)` (dynamic lookup), so patching the
class method there IS effective (M1). All mutants above use the effective consuming namespace.

The committed assertions are the durable regression guards (a returning bug fails them). Mutation
tests are NOT committed to avoid a committed dependency on M5-T103-owned internal names
(`_PATH_HANDLERS`, `_PAINT_*`, `_IGNORED`, `_StreamDecoder` methods); the red runs are recorded here
per "record each mutant and its red run" (the M5-T083 G4/DCV precedent).

## Commands (explicit cwd; verbatim tails) — all [OBSERVED]

- cwd `services/api`: `python -m ruff check .` → `All checks passed!`
- cwd `wt-m5t104` via the 3.11 bare-package shim (copy of `run_sheet_split_tests.py` pointed at this
  worktree) running `tests/drawings/test_sheet_reader.py` + `tests/drawings/test_sheet_reader_split_equivalence.py`
  → `55 passed in 2.57s` (baseline before this task: `46 passed`). Per-file collection: sheet_reader
  46, split-equivalence 9.
- cwd repo root: `python tools/modularity_check.py --check` → `EXIT=0` (warnings only; neither
  changed file is flagged).
- cwd `wt-m5t104`: `git diff --stat` → `sheet_primitives.py | 2 +-`, `test_sheet_reader.py | 178 ++`
  (before this report file was added).
- Mutant red runs: reproduced in-process against this worktree's production modules via the bare
  package shim; every mutant moved its targeted assertion to the "Mutant value (RED)" column above.

Environment: local Python 3.11.9 (PEP-695 behind `app/documents/extraction/__init__.py` requires the
bare-package shim to collect these suites); CI on 3.12 is the raw-`pytest` authority for
`python -m pytest tests/drawings/test_sheet_reader.py tests/drawings/test_sheet_reader_split_equivalence.py -q`.

## Deviations / assumptions
- Where the plan and a backlog row differ, the backlog wording governs; none observed to differ here.
- Mutation proofs are recorded (not committed) — see the mutation-table note above.
- `v`/`y` interior points are pinned literals; each is proven non-vacuous by its recorded dispatch-table
  mutant (M3/M4), i.e. the pinned field is one the operator's semantics displace.

## DISCOVERIES (D-069; route to the orchestrator — not fixed in-packet)
- D1 (LOW, testing infra): the path-operator dispatch dict `sheet_interpreter._PATH_HANDLERS` is
  populated by value at import, so an in-process mutant on `_StreamRun._op_m/_op_l/_op_c/_op_v/_op_y`
  is a silent false survivor; the consuming namespace for those operators is `_PATH_HANDLERS[...]`.
  Worth a one-line note near the dispatch table for future reader-packet mutation work.
- D2 (LOW, doc nit — NOT fixed, outside allowed_paths): `sheet_primitives.py` still cites `§8.3.3`
  on the `Matrix` type-alias comment (line ~28); DB-055 (e) named only the `apply_matrix` citation,
  so it was left as-is. If the intent is that ALL affine citations point at §8.3.4, a follow-on nit
  can align the type-alias comment too.
- D3 (INFO): DB-064 (c)/(d) and DB-055 (f) (untruncated `/Filter` and `/name` echoes; the
  after-increment total check that can overshoot by up to one per-stream cap) remain OPEN and are
  pre-existing, lexer-bounded; they are out of this packet's scope (test-debt only) and untouched.

END-OF-REPORT
