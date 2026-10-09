# M5-T120 producer report — D-087 PDF-reading P4 (the M5-T118 riders DB-090 a/b/c/i)

Split the architect-sheet content interpreter BEFORE it can grow (748/750), then skip inline images
whose /DP value is a dictionary, fix the three ISO citation pointers, and give item 2's post-paint
lineto a disclosed rule that never draws from an undefined point — then re-run the six real architect
PDFs by sha256. Producer: backend-engineer (orchestrator-dispatched subagent). Worktree
`C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t120`, branch `task/M5-T120-pdf-p4-split-dp-orphan-lineto`,
from claim seam `0c638f88`.

Directives: D-087-R001/R002/R005/R009, D-066-R001. Unwired (no route/app/main change); zero new
dependencies (stdlib + already-admitted only; no lockfile/requirements touch). ISO 32000-1 cited next
to the code; anything unverified carries `[recalled - verify]`.

**HEADLINE (honest): 4 of the 6 real architect PDFs now READ FULLY** (was 3 of 6 after M5-T118). The
NEW read is item 2 — the 94-page VA HVAC vector set — unblocked by the orphan-lineto rule (STEP 4). I
verified by attribution diagnostic that STEP 4 is the load-bearing unblock and that the /DP-dictionary
feature (STEP 2) is NOT exercised by the real corpus (item 2's 8,154 inline images carry no /DP
dictionary). Items 1/3/4/5/6 reproduce M5-T118 byte-for-byte.

## Files changed (`git status --short` = 8 files, all inside allowed_paths)

- `services/api/app/drawings/sheet_path_state.py` (NEW, 248 lines) — the `_PathState` mixin that
  `_StreamRun` inherits; the path-construction group split out of the interpreter (DB-090 c).
- `services/api/app/drawings/sheet_interpreter.py` (749 -> 577 lines) — path group removed, `_StreamRun(_PathState)`,
  `_PATH_HANDLERS` re-imported so `_execute` still reads it as a module global (facade patch bites).
- `services/api/app/drawings/sheet_inline_image.py` (341 -> 444 lines) — /DP-dictionary + array-of-dicts/nulls
  parsing (DB-090 a); the three citation pointers fixed (DB-090 b).
- `services/api/app/drawings/sheet_reader.py` — `_SheetInterpreter` gains `orphan_subpaths`/`page_orphan_subpaths`
  (reset in `begin_page`, stamped by `_build_page`).
- `services/api/app/drawings/sheet_primitives.py` — `SheetPage.orphan_subpaths` (defaulted 0, byte-stable)
  + `SheetDocument.orphan_subpaths` aggregate.
- `services/api/tests/drawings/test_sheet_p4_features.py` (NEW) — 17 AS-2/AS-4 + split-facade tests with committed mutations.
- `services/api/tests/drawings/test_sheet_reader.py` — one docstring pointer updated (the `_PAINT_*` mutants now name `sheet_path_state`).
- `services/api/tests/drawings/test_sheet_reader_split_equivalence.py` — ONE deliberate golden revision (`refuse_l_no_current` -> `refuse_curve_no_current`; digest + `_OVERALL` recaptured).

Forbidden byte-UNCHANGED (`git diff --stat` empty): `sheet_objects.py`, `pdf_object_streams.py`,
`test_pdf_object_streams.py` (44 pass), `sheet_marked_content.py`, `app/documents/`.

## STEP 1 — split (DB-090 c; G3 A1). Split map + split-point proof

`_StreamRun` now `class _StreamRun(_PathState)`. Moved verbatim into `sheet_path_state._PathState`:
`_flush_open`, `_open_after_close`, `_moveto`, `_lineto`, `_curveto`, `_close`, `_charge_points`,
`_paint`, `_op_m/_op_l/_op_c/_op_v/_op_y/_op_h/_op_re`, and the constants they alone use
(`_PAINT_STROKE`, `_PAINT_FILL`, `_PAINT_CLOSE_FIRST`, `_PATH_HANDLERS`). KEPT in `sheet_interpreter`
(facade / importable, verified reached through it by the suite): `_StreamRun`, `_IDENTITY`,
`_SKIP_SHADING`, `_PAINT_ALL`, `_IGNORED`, `skip_inline_image`, `read_inline_dict`, `_apply_matrix`,
`_is_finite_point`, `_map`, `_map_via`, `_take`, `_read_array`, `_read_inline_dict`, `_execute`, the
text/XObject ops, and `_PATH_HANDLERS` (re-imported so `_execute` reads it as this module's global).
`sheet_reader.py` still imports `_IDENTITY, _StreamRun` from `sheet_interpreter`.

**Split-point result (pure move, BEFORE any feature change):** `[OBSERVED-via-shim]` cwd `services/api`,
`python <shim> tests/drawings -q` -> `272 passed`. The goldens AND `test_sheet_reader_split_equivalence`
passed UNCHANGED at the split point (no golden edited), proving the move is byte-identical. Then the
STEP 2-4 features were applied. (`sheet_interpreter.py` 749 -> 577; new module 248; modularity exit 0.)

### Monkeypatch audit (split-facade trap, seq-130 lesson)

Every committed `setattr` on `sheet_interpreter` was graded; NONE goes vacuous (each still reddens,
proven by the passing suite):

| patched name | stays / moved | exercised consumer | disposition |
|---|---|---|---|
| `sheet_interpreter._SKIP_SHADING` | stays | `_execute` (stays) | bites (test_sheet_p3 as2_sh) |
| `sheet_interpreter.skip_inline_image` | stays | `_op_bi` (stays) | bites (test_sheet_p3 as3) |
| `sheet_interpreter.read_inline_dict` | stays | `_read_inline_dict` (stays) | bites (test_sheet_content) |
| `sheet_interpreter._StreamRun._place_form` | stays | `_place_form` (stays) | bites (split_equivalence AS-4) |
| `sheet_interpreter._is_finite_point` | stays | `_map`/`_map_via` (stay) — the finiteness-gate test exercises the MOVETO via `_map` | bites (split_equivalence AS-4) |

`_apply_matrix` (test_sheet_reader:655 PROSE) stays in `sheet_interpreter`, so that documented mutant
recipe is still accurate. The moved constants had NO committed patch (only test_sheet_reader:708 PROSE):
I updated that prose to name `sheet_path_state._PAINT_*` and added COMMITTED positive controls
(`test_split_paint_flag_sets_bite_at_new_namespace`, `test_split_path_handlers_bite_at_new_namespace`)
that patch the NEW consuming namespace and prove the seam still reddens. Note: `_curveto`'s internal
flatten-finiteness moved with it and now reads `sheet_path_state._is_finite_point`; the committed
finiteness-gate test exercises `_map` (which stays), so it is not vacuous — verified by the passing suite.

## STEP 2 — /DP dictionaries (DB-090 a; G1 A). AS-2

`sheet_inline_image._parse_dictionary` now accepts a `<<...>>` value (or `[ <<...>> null ]` array)
ONLY for /DP // /DecodeParms (`_nested_dict_allowed`), consuming exactly ONE nested level (`_skip_dict`,
capped by `_MAX_INLINE_DP_DICT_DEPTH=1`) under the same 4096-byte dictionary cap; the value is stored as
the `_DICT_VALUE` sentinel (never a geometry key), so the length arithmetic is untouched and no sample
byte is decoded. A nested dictionary under any OTHER key, and a SECOND nesting level, stay typed
refusals. AS-2 tests: /DP dict skipped + line-after draws; /DecodeParms full-name; array-of-dicts/nulls;
non-/DP `<<>>` refuses; second level refuses — each with a committed mutation (see the mutation table).

## STEP 3 — citations (DB-090 b; G1 B). AS-3 (doc-only, verified by inspection)

`sheet_inline_image.py`: the row-byte-alignment rule now cites **§8.9.3 "Sample Representation"** (was
§8.9.5.2) at the module docstring and `_determinable_length`; the permitted /BitsPerComponent set now
cites **§8.9.5.1 / Table 89** (was §8.9.5.2) at `_VALID_BPC`; the colour-space abbreviations now cite
**Table 93** (was Table 92) at `_COMPONENTS` AND at the module-docstring "colour space (Table 93
abbreviations)" line (the same claim as the flagged `:84` — fixed for internal consistency). Table 92
stays where it is correct (KEY abbreviations). These match the packet's binding FORMAT AUTHORITY and
G1's web-verification, so the two former `[recalled - verify]` markers on the row-alignment citation
were removed (now verified).

## STEP 4 — orphan lineto (DB-090 i). AS-4

`sheet_path_state._lineto`: when `self._current is None` it now calls `_orphan_lineto`, which starts a
NEW subpath AT ITS OWN mapped end point (`_cur_points=[point]`, `_current=point`, `_subpath_start=point`),
draws NO segment to it (later `l` draw FROM it), and increments the per-page + document orphan count.
This fires ONLY when the current point is undefined — after a painting operator (ISO 32000-1 §8.5.3) or
at stream start — so no existing golden path (which always has an `m`/`re`/`h`-retained current point)
is perturbed; the count defaults to 0 and is not serialized by the equivalence corpus, so goldens are
byte-identical. Reader-of-record match [ORCH-CORRECTED per M5-T120 G1]: the WHATWG HTML Canvas 2D
`lineTo` "ensure there is a subpath" rule (a new subpath at the point, no segment), which pdf.js
inherits by drawing to a canvas - verified by the G1 reviewer from the primary source; MuPDF is
STRICTER (its `fz_lineto` with no current point warns and ignores the operator), so it is NOT a match.
ISO 32000-1 §8.5.2/§8.5.3 ("current point undefined after painting") IS verified via the packet's
FORMAT AUTHORITY. PROHIBITED reopening-at-the-last-point is NOT done (the mutation proves it). Curves
(`c`/`v`/`y`) with no current point STAY typed refusals (`_curveto` / `_op_v`); **no real file hits an
orphan curve** (item 2 reads fully).

## AS-5 — real corpus (honest). Six files by sha256, two runs each, then deleted

Fetched to a scratch folder OUTSIDE the worktree, sha256-verified against
`docs/research/architect-drawing-corpus-2026-09.md` §2, run through `read_sheet` TWICE, then deleted
(`REMAINING corpus files: []`; nothing committed). Observed under the 3.11 shim (Deviations). Tuple =
(pages, polylines, segment-points, text-runs, images, sh-skips, inline-skips, orphan-subpaths).

| # | file | sha256 | run1==run2 | result NOW | next blocker |
|---|---|---|---|---|---|
| 1 | VA Div23 1/2 88pp | MATCH | True | **READS** 88pp, 332,057 pl, 1,687,113 segpts, 1,567 text, 5 img, 0 sh, 0 inline, 0 orphan | none (identical to M5-T118) |
| 2 | VA Div23 2/2 94pp | MATCH | True | **NOW READS** 94pp, 299,548 pl, 1,558,683 segpts, 2,710 text, 8 img, 0 sh, **8,154 inline**, **1 orphan** | none — the orphan-lineto (STEP 4) unblocked the M5-T118 blocker |
| 3 | VA DwgDelivRqmts 14pp | MATCH | True | **READS** 14pp, 1,611 pl, 6,444 segpts, 2,898 text, 19 img, 4 sh, 0 inline, 0 orphan | none (identical to M5-T118) |
| 4 | Brooklyn Bridge HAER 8pp | MATCH | True | **READS** 8pp, 11 pl, 38 segpts, 990 text, 8 img, 0 sh, 3 inline, 0 orphan | none — scan+OCR (identical to M5-T118) |
| 5 | Frantz-Dunn HABS 1pp | MATCH | True | REFUSED `scan only` | none — correct scan-only terminal |
| 6 | Rothschild HABS 1pp | MATCH | True | REFUSED `scan only` | none — correct terminal |

**Attribution diagnostic on item 2 (fetched once, three in-process variants, deleted):** baseline READS
(8,154 inline, 1 orphan); with /DP-dict acceptance DISABLED it STILL READS identically (so STEP 2 is NOT
load-bearing on the real corpus — item 2's inline images carry no /DP dictionary); with the orphan
lineto reverted to the pre-P4 refusal it REFUSES `path` "'l' with no current point" (so STEP 4 is THE
unblock). Items 1/3/4/5/6 reproduce M5-T118 exactly, confirming the split + features are behaviour-
preserving on real files. No overclaim: 4 of 6 read; STEP 2 is proven by synthetic tests only.

## Mutation table (committed; each REAL != MUTANT proven by a passing test)

| guard | mutant (consuming namespace) | REAL | MUTANT | committed test |
|---|---|---|---|---|
| orphan starts at its OWN point | reopen-at-last-point: `_StreamRun._paint` keeps current (violates §8.5.3) | polyline = (10,10)->(20,20) | (5,5)->(10,10)->(20,20) invented segment | `test_as4_orphan_lineto_no_segment_from_pre_paint_point_mutant` |
| orphan count disclosed | drop-the-count: `_StreamRun._orphan_lineto` omits the increment | orphan==1 | orphan==0 (geometry unchanged) | `test_as4_orphan_subpath_count_is_load_bearing` |
| /DP dict accepted (not refused) | disallow-dp-dict: `sheet_inline_image._nested_dict_allowed`->False | reads | refuses `inline image` | `test_as2_dp_dictionary_skip_is_load_bearing` |
| /DP-only restriction | allow-any-nested-dict: `_nested_dict_allowed`->True | `/CS <<>>` refuses | reads | `test_as2_non_dp_nested_dictionary_restriction_is_load_bearing` |
| exactly one nested level | raise-the-depth-cap: `_MAX_INLINE_DP_DICT_DEPTH`=2 | 2nd level refuses | reads | `test_as2_one_level_depth_cap_is_load_bearing` |
| moved paint sets bite at new home | empty `sheet_path_state._PAINT_STROKE`/`_FILL`/`_CLOSE_FIRST` | stroked/filled/closed | not | `test_split_paint_flag_sets_bite_at_new_namespace` |
| moved dispatch bites through facade | empty `sheet_interpreter._PATH_HANDLERS` | reads | `unsupported operator` | `test_split_path_handlers_bite_at_new_namespace` |
| orphan CURVE still refuses | (positive control, c/v/y) | refuses `path`/`v` | — | `test_as4_orphan_curve_still_refuses` |

The pre-existing p3 + split-equivalence mutations (sh skip, inline skip/desync, per-page resets,
finiteness gate, form depth/cycle, backstop) all still bite (part of the 289-pass).

## Golden revision (deliberate; before -> after)

`refuse_l_no_current` (`5 5 l S`) refused pre-P4; the orphan-lineto rule makes it a READ, so the
split-equivalence corpus case is replaced by `refuse_curve_no_current` (`5 5 10 10 20 20 c S`), which
STAYS a "curve with no current point" refusal. Recomputed from the CURRENT module: the ONLY changed
case is this substitution (`changed-vs-golden: []`; added `refuse_curve_no_current`, removed
`refuse_l_no_current`) — every OTHER of the 62 per-case digests is byte-identical, proving the split +
/DP + citations + orphan changes perturb nothing else. New `refuse_curve_no_current` digest
`53a90aae…df40b965`; new `_OVERALL` `264b5416…c3b00efd`. The orphan-lineto READ behaviour lives in
`test_sheet_p4_features.py`.

## Self-checks (explicit cwd; verbatim tails)

1. `[OBSERVED]` cwd `services/api`: `python -m ruff check .` -> `All checks passed!`
2. `[OBSERVED-via-shim]` cwd `services/api`: documented `python -m pytest tests/drawings -q` cannot
   collect under the sandbox Python 3.11 (`app/documents/units.py` PEP-695). Ran via the worktree-pointed
   shim `python <scratch>/m5t120/shim311/runtests.py tests/drawings -q -p no:cacheprovider` ->
   `289 passed` (272 pre-P4 + 17 new p4). At the SPLIT POINT (pure move) the same command -> `272 passed`
   (goldens + split-equivalence UNCHANGED). `test_pdf_object_streams.py` -> `44 passed` (forbidden,
   unchanged). CI (3.12) is the authority — HARVEST there.
3. `[OBSERVED]` cwd repo root: `python tools/modularity_check.py --check` -> exit `0`. Line counts:
   `sheet_interpreter.py` 577 (was 749; comfortably under the 750 ceiling AND under the warn line),
   `sheet_path_state.py` 248, `sheet_inline_image.py` 444.
4. `[OBSERVED]` cwd `wt-m5t120`: `git status --short` -> exactly the 8 allowed paths; `git diff --stat`
   on `sheet_objects.py` / `pdf_object_streams.py` / `test_pdf_object_streams.py` /
   `sheet_marked_content.py` / `app/documents/` -> empty (byte-unchanged).

## Deviations

- **Documented pytest blocked on sandbox Python 3.11; observed via a worktree-pointed shim.** The
  packet's named shim points `API_ROOT` at the PRIMARY checkout, which lacks my edits, so I copied the
  shim mechanism into `<scratch>/m5t120/shim311/` with `API_ROOT` re-pointed at
  `wt-m5t120\services\api` (it stubs only package `__init__` bodies; drawings behaviour is unmodified).
  CI (3.12) is the authority.
- **`test_sheet_reader.py` touched (allowed).** One docstring pointer only (the report-documented
  `_PAINT_*` mutants now name their new home `sheet_path_state`); no test logic changed, suite green.

## OPEN QUESTIONS (owner asleep — recommended answers)

1. **STEP 2 (/DP dictionaries) is not exercised by the real corpus.** The attribution diagnostic shows
   item 2's 8,154 inline images carry no /DP dictionary, so /DP-dict handling is proven by synthetic
   tests only. RECOMMEND accept — it is a real, common class in SCANNED CCITTFax sheets (G1 A named it),
   it is fully bounded and mutation-covered, and a future scanned-CAD file will exercise it. Not a gap.
2. **Orphan-lineto reader-of-record citation** [ORCH-CORRECTED per M5-T120 G1: resolved]. The "start a
   subpath at the lineto's own point when there is no current point" leniency matches the WHATWG Canvas
   2D `lineTo` rule that pdf.js inherits (G1-verified from the primary source); MuPDF does NOT match -
   it warns and ignores the orphan lineto (stricter). Originally: RECOMMEND the G1 verifier confirm; the
   ISO §8.5.2/§8.5.3 "current point undefined after painting" basis IS verified, and the rule provably
   never invents a segment (the reopen-at-last-point mutant reddens).
3. **Should orphan curves also lenient-reopen?** No real file hits one (item 2 reads fully). RECOMMEND
   keep the strict refusal for `c`/`v`/`y` (a curve needs a defined start tangent; lenient-reopening it
   would invent geometry) until a real file requires otherwise — then a dedicated packet decides.

## DISCOVERIES (D-069 — for the orchestrator to record)

- **4 of 6 real architect PDFs now READ** (items 1, 2, 3, 4); item 2 (94pp VA HVAC vector set) is the
  new read, unblocked by the orphan-lineto rule. It surfaces 299,548 polylines, 8,154 skipped inline
  images and exactly 1 orphan subpath. [product milestone — D-087-R005 further advanced]
- **The /DP-dictionary handling (DB-090 a) is proven by synthetic tests only** — absent from the real
  corpus (item 2's inline images have no /DP dict). [reader-subset note; real CCITTFax scanned-CAD file
  would exercise it]
- **No real corpus file hits an orphan CURVE** (post-paint `c`/`v`/`y` with no current point); the
  strict curve refusal is untriggered on the corpus. [reader-subset note]
- **`sheet_interpreter.py` split to 577 lines** (path group -> `sheet_path_state.py`, 248 lines); both
  well under the 750 ceiling, so the next PDF feature has headroom. [modularity note]

END-OF-REPORT
