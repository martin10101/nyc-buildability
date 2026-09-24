# M5-T083 producer report — D-087 PDF-1: architect-sheet PDF reader profile

Producer: backend-engineer (orchestrator-dispatched subagent). Worktree
`C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t083`, branch `task/M5-T083-sheet-reader`,
contract head `f9bfd54d37c981e938185e3ae09ea9ad85f415f3`.

## What shipped (allowed_paths only)

- `services/api/app/drawings/sheet_primitives.py` — geometry value types (frozen dataclasses)
  + the pure 2-D affine / Bezier algebra (`concat_matrix`, `apply_matrix`, `flatten_cubic`,
  `cubic_flat`, `point_line_distance`, `MAX_FLATTEN_DEPTH`).
- `services/api/app/drawings/sheet_reader.py` — `read_sheet(data, *, flatten_tolerance)`: the
  architect-sheet interpretation profile. Reuses the strict reader READ-ONLY via
  `read_object_table` (which composes `pdf_lexer` + `pdf_objects` + `pdf_xref`); does NOT import
  `pdf_content` (it refuses the very features this profile supports — a separate interpretation
  by design). Returns `SheetDocument | SheetRefusal`; never raises.
- `services/api/tests/drawings/test_sheet_reader.py` — 23 tests: AS-1..AS-4 + mutation guards +
  text/units/paint coverage. Self-contained synthetic PDFs (real classic-xref offsets); nothing
  under `tests/documents/` is imported or edited.
- this report.

## IMPLEMENTATION summary

- Coordinates are page-scoped PDF **user space** (default user space after every `cm`), NOT world
  coordinates. Each `SheetPage` also carries `media_box`, `user_unit`, and the declared
  `flatten_tolerance` for a later C2 unit-confirmation packet.
- Full affine CTM via `cm` (rotation/shear allowed — the survey profile refuses these):
  `_execute` `cm` branch `sheet_reader.py:665` → `concat_matrix` `sheet_primitives.py:36`.
- Depth-bounded `q`/`Q` CTM stack: `sheet_reader.py:653` (`q`, `MAX_Q_DEPTH=128`), `:659` (`Q`,
  underflow refused).
- Path construction `m l c v y h re`; Bezier flatten under the DECLARED chord error:
  `_curveto` `sheet_reader.py:602` → `flatten_cubic` `sheet_primitives.py:81` (adaptive de
  Casteljau, conservative control-point-to-chord flatness `cubic_flat` `:72`, subdivision-depth
  safety cap `MAX_FLATTEN_DEPTH=24`; total-point budget `MAX_PATH_POINTS=500000` is the hard
  bound). Stroke vs. fill distinguished in `_paint` `sheet_reader.py:627`.
- Text runs under the full text+CTM matrix (rotation allowed): `_show` `sheet_reader.py:792`
  (origin = `apply_matrix(concat_matrix(Tm, CTM), 0, 0)`; nominal `Tf` size; latin-1 decode; no
  advance — documented simplification).
- Form XObjects re-interpreted under each placement CTM with recursion `<= MAX_XOBJECT_DEPTH=8`
  and cycle refusal: `_op_do` `:829`, `_place_form` `:877` (depth guard `:881`, cycle guard
  `:883` via the object-ref stack). Image XObjects counted + disclosed, NEVER decoded:
  `_place_image` `:858` (returns without touching `stream.raw_data`).
- Refusal is a VALUE, all-or-nothing per document: strict-reader refusals wrapped by
  `_wrap_strict` `:151`; profile bounds/cycles/unsupported constructs by `_refuse` `:168`.
  `read_sheet` `:305` returns the first refusal from the page walk with no partial document.
- Untrusted input bounded: stream size / flate output (`_decode_stream` `:209`,
  `MAX_DECODED_STREAM_BYTES`), operator count (`MAX_CONTENT_OPERATORS=200000`), path points,
  `q` depth, XObject recursion, Bezier subdivision depth. Zero new dependencies (stdlib `math` +
  `zlib` only). No route, no `app/main.py`, no web, no network.
- Operator semantics carry per-operator ISO 32000-1 section citations marked `[recalled - verify]`
  for the G1 data-contract review (module docstrings + inline `§...` comments).

## Per-AS evidence

- **AS-1 (curves + declared tolerance).** `test_as1_quarter_circle_flattened_within_declared_tolerance`
  — a quarter circle built from 4 cubic Beziers, flattened at declared `flatten_tolerance=0.5`
  (R=200); measured max deviation from the true circle (vertices + chord midpoints) `<= 0.5`; the
  tolerance is recorded on `page.flatten_tolerance` and `doc.flatten_tolerance`. Mutation:
  `test_as1_mutation_skipping_subdivision_reddens` installs a no-subdivision flattener and shows
  the measured deviation exceeds the tolerance.
- **AS-2 (transforms + state).** `test_as2_rotation_and_translation_compose_exactly` — a 30° `cm`
  rotation composed with a prior `cm` translate maps two points to 1e-9 of an independent
  reference. `test_as2_shear_is_supported_and_maps_exactly` — a `c!=0` shear (which the survey
  profile refuses) maps exactly and is NOT refused. `test_as2_nested_q_q_restores_the_ctm` — a
  `q..cm..Q` restores the CTM. Mutation: `test_as2_mutation_dropping_ctm_multiply_reddens`
  replaces `concat` with one that drops the prior CTM, and the composed point diverges from the
  exact rotation+translation.
- **AS-3 (XObjects + images).** `test_as3_form_xobject_used_twice_yields_primitives_twice` — one
  Form XObject placed twice yields its segment twice, each under its placement CTM
  `((0,0)-(100,0))` and `((200,50)-(201,50))`. `test_as3_form_self_reference_cycle_is_refused`
  (feature `xobject cycle`); `test_as3_form_recursion_depth_bound_is_refused` (feature
  `xobject recursion`). `test_as3_image_xobject_counted_and_never_decoded` — an image with
  `/DCTDecode` + non-flate garbage bytes is counted (`image_count==1`), its declared
  width/height/bits/colorspace disclosed, its placement CTM recorded, and NEVER decoded (a decode
  attempt would fail on the garbage — proving none is made); it places no vector geometry.
- **AS-4 (fail-closed + bounds).** Each returns a typed `SheetRefusal` VALUE (no exception):
  encryption (`test_as4_encrypted_document_is_refused_as_value`, origin `strict_reader`),
  unsupported content filter `/LZWDecode` (`stream filter`), over-limit operators / path points /
  `q` depth (monkeypatched bounds), an unsupported operator `sh` (`unsupported operator`),
  non-bytes input (`input`), invalid `flatten_tolerance` incl. 0/neg/inf/nan (`flatten tolerance`),
  malformed header (origin `strict_reader`). All-or-nothing:
  `test_as4_all_or_nothing_second_page_refusal_fails_whole_document` — a bad page-2 fails the whole
  read (no partial 1-page document).
- **AS-5 (isolation + scope).** Byte-untouched proof below; nothing imports the profile (the
  `app/drawings/__init__.py` is a docstring-only package seeded by the orchestrator and left
  untouched; no route/module imports `sheet_reader`); zero new dependencies; ruff + modularity
  clean (below). Composition/units also covered by `test_user_unit_and_media_box_are_disclosed`,
  `test_fill_and_stroke_painting_is_distinguished`, `test_rotated_text_run_is_placed_and_not_refused`.

## Self-check commands (verbatim, with cwd)

1. `cd services/api && python -m ruff check .` — [OBSERVED] `RUFF exit=0` / `All checks passed!`
   (the api CI job's first step).
2. `cd services/api && python -m pytest tests/drawings/test_sheet_reader.py -q` — [BLOCKED locally]
   `exit=2`, collection `SyntaxError: expected '('` at `app/documents/units.py:276`
   (`def _match_unit[UnitT: enum.Enum](` — Python-3.12 generic syntax). Root cause: the sandbox
   interpreter is Python **3.11.9** while the repo targets **3.12**; importing any
   `app.documents.extraction` submodule runs the package `__init__`, which eagerly imports
   `survey_pipeline` → `checks` → `units.py`. This is an ENVIRONMENT artifact unrelated to this
   packet's code — it reproduces on the untouched strict-reader modules too. It runs green in CI
   (Python 3.12). No Python 3.12/3.13 interpreter is launchable in this sandbox (3.13 is
   registered but its binary fails to start; 3.12 is absent). ROUTED TO HARVEST: run this exact
   command on the pushed head under CI's Python 3.12.
3. [OBSERVED — shimmed local run] To prove the test LOGIC locally under 3.11, a scratchpad shim
   pre-registers a bare `app.documents.extraction` package (real `__path__`, empty `__init__`) so
   the reused strict-reader submodules load WITHOUT the unrelated `units.py` import, then runs the
   real, unmodified test file via `pytest.main`:
   `....................... [100%]  23 passed in 0.36s`. The shim touches no repo file; it only
   bypasses the 3.12-syntax eager import that CI does not hit.
4. `cd <worktree root> && python tools/modularity_check.py --check` — [OBSERVED]
   `MODULARITY exit=0`; `selected 483 files; failures 0; warnings 23`. sheet_reader.py is a
   WARNING only (`review_signal ... record a cohesion justification`), not a failure — see the
   cohesion justification below. sheet_primitives.py is clean.

## Named mutation record (red/green) — [OBSERVED]

Applied each named mutation in-process to the PRIMARY AS test and reverted:

```
AS-1 baseline: GREEN (passed)
AS-2 baseline: GREEN (passed)
MUTATION drop tolerance subdivision -> AS-1: RED (AssertionError)
MUTATION drop CTM multiply        -> AS-2: RED (AssertionError)
AS-1 restored: GREEN (passed)
AS-2 restored: GREEN (passed)
```

The two guards therefore have teeth. Dedicated in-tree mutation tests
(`test_as1_mutation_skipping_subdivision_reddens`, `test_as2_mutation_dropping_ctm_multiply_reddens`)
encode the same detection and are part of the 23-test suite. Mutations rebind the CONSUMING
module's binding (`sheet_reader._flatten_cubic` / `sheet_reader._concat_matrix`), which are
resolved from `sheet_reader`'s globals at call time — valid even though the functions are defined
in `sheet_primitives` (a by-value import into the reader; per the mutate-the-consuming-namespace
rule the defining-module rebind would be a false survivor).

## Byte-untouched isolation proof (AS-5) — [OBSERVED]

- `git diff --stat f9bfd54d -- services/api/app/documents` → EMPTY (no output).
- Tree hash `services/api/app/documents` at contract head `f9bfd54d` = `c14c65ff…` = HEAD tree
  hash `c14c65ff…`; `git status --porcelain services/api/app/documents` → EMPTY. The strict-reader
  modules (`pdf_lexer/pdf_objects/pdf_xref/pdf_container/pdf_content/vector_pdf_decoder/routing/
  survey_pipeline`) and `isolation.py` are byte-identical.
- `git status --porcelain` shows ONLY the three allowed source/test files modified (plus this
  report). `app/drawings/__init__.py`, `tests/drawings/__init__.py`, and all forbidden paths are
  untouched. `sheet_primitives.py` was split from the placeholder (it is NOT left as the
  placeholder — it carries the geometry types + algebra).

## Cohesion justification for the modularity review (G3)

`sheet_reader.py` is 818 SLOC (WARN 600 / JUSTIFY 750 / HARD 1000 — passes CI; a JUSTIFY-band
warning). The packet grants exactly two production files, and the natural boundaries are already
used: `sheet_primitives.py` (geometry value types + pure affine/Bezier algebra, 155 SLOC) vs
`sheet_reader.py` (one cohesive responsibility: interpret a PDF content stream — object-graph
resolution, stream decode, page walk, and the single operator-dispatch interpreter). The interpreter
is one algorithm over the PDF content grammar; fragmenting it across the two allowed files would
split a single state machine, not create cleaner boundaries. A future third module (e.g. a separate
content-interpreter) is the right home if this grows, but requires a packet that grants that path.

## Deviations

- Documented `pytest` command not runnable locally (sandbox Python 3.11 vs repo 3.12); proven via
  a repo-touching-nothing shim (23 passed) and routed to CI harvest at the pushed head. This is the
  known sandbox-3.11-vs-3.12 gate condition.
- `pdf_content` is deliberately NOT reused (it refuses curves/XObjects/rotation by design). The
  profile re-implements interpretation for the wider architect subset while reusing
  lexer/objects/xref via `read_object_table`. This satisfies "compose the strict reader read-only":
  no strict-reader module is imported for a purpose that would relax its refusals.

## DISCOVERIES (route to docs/DISCOVERY_BACKLOG.md at the seam; not fixed in-packet)

- **Cross-reference streams (PDF 1.5+) are refused.** `read_object_table` supports only the classic
  `xref` table and refuses cross-reference streams / `/Prev` / hybrid-reference / `/Encrypt`. Many
  modern architect PDFs use xref streams, so this profile will fail-closed on them (feature
  `cross-reference stream`, origin `strict_reader`). Broadening coverage needs an xref-stream reader
  — a separate, larger effort outside D-087 PDF-1.
- **Clipping paths are recorded but not applied.** `W`/`W*` are consumed as no-ops (the path is kept
  and painted); geometry outside the clip region is still surfaced. A later consumer that needs true
  clipped extents would add clip-region tracking.
- **Text advance / glyph metrics not modelled.** Each `Tj`/`TJ`/`'`/`"` emits one `SheetTextRun`
  anchored at the line origin (no width/kerning advance; latin-1 decode). Sufficient to locate
  labels; a text-extraction consumer needing reading order/width would need font metrics + encodings.
- **Shading (`sh`) and inline images (`BI`) are refused** as unsupported operators (fail-closed).
  If real architect title blocks use them widely, a future packet may choose to count-and-disclose
  shadings/inline-images like image XObjects rather than refuse the whole document.

END-OF-REPORT
