# M5-T118 producer report — D-087 PDF-reading P3 (the M5-T113 real-corpus next blockers)

Per-PAGE operator / path-point / decoded-byte budgets under a bounded per-DOCUMENT ceiling
(DB-055 c), the `sh` shading operator skipped as non-geometry (ISO 32000-1 §8.7.4.2), and inline
images `BI`/`ID`/`EI` skipped safely (§8.9.7, DB-055 d) — then the six real architect PDFs re-run
by sha256. Producer: backend-engineer (orchestrator-dispatched subagent). Worktree
`C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t118`, branch `task/M5-T118-pdf-p3-budgets-sh-inline-images`,
from claim seam `f2ada974`.

Directives: D-087-R001/R002/R005/R009, D-066-R001. Unwired (no route/app/main change); zero new
dependencies (stdlib `zlib`/`hashlib` only; no lockfile/requirements touch).

**HEADLINE (honest): 3 of the 6 real architect PDFs now READ FULLY** — the FIRST real architect
drawings the reader has ever read end to end (M5-T113 was 0/6). Item 1 (88-page vector CAD set)
reads on the per-page budget; item 3 reads and exercises the `sh` skip; item 4 (scanned+OCR) reads
with 3 inline images skipped. Item 2 refuses at a NEW, deeper blocker (a lineto with no current
point — a path-state content gap, distinct from the three P3 blockers); items 5-6 stay the correct
scan-only refusal. Details in the real-corpus table.

## Files changed (all inside allowed_paths; `git status` = 8 files)

- `services/api/app/drawings/sheet_reader.py` — facade: per-page + per-document budget constants
  (`MAX_CONTENT_OPERATORS`/`MAX_PATH_POINTS` kept as the PER-PAGE names, new
  `MAX_DOCUMENT_OPERATORS`/`MAX_DOCUMENT_PATH_POINTS`, re-exported `MAX_PAGE_DECODED_BYTES`,
  `MAX_INLINE_IMAGE_DICT_BYTES`/`_DATA_BYTES`); `_InterpreterLimits` split into per-page/per-doc
  fields; `_SheetInterpreter` gains page counters + `begin_page()`; `_build_page` calls
  `begin_page()` before decode and stamps the two skip counts onto each `SheetPage`.
- `services/api/app/drawings/sheet_inline_image.py` (NEW, ~230 SLOC) — the bounded inline-image
  skip: parse the abbreviated dictionary (Table 92/93) with the reused lexer; compute the data
  length when determinable (unfiltered `ceil(W*components*bpc/8)*H`, row-aligned) and REQUIRE a
  whitespace-delimited `EI` there; else scan for a whitespace-delimited `EI` under a byte cap; any
  ambiguity / over-cap / no-`ID` is a typed `SheetRefusal`. Never decodes a sample byte.
- `services/api/app/drawings/sheet_interpreter.py` (690 -> 748 SLOC; < 750) — per-page + per-doc
  operator counting; `_charge_points`/`_curveto` charge both budgets and thread the TIGHTER
  remaining point budget into flattening; `sh` skipped via the rebindable `_SKIP_SHADING` set;
  `BI` dispatched to the new `_op_bi` skip.
- `services/api/app/drawings/sheet_objects.py` — `_StreamDecoder` gains the per-page decoded-byte
  budget (`max_page_decoded_bytes`/`page_decoded_bytes`/`begin_page()`); `charge_decoded` checks
  the page budget then the document ceiling. (The 6 symbols `pdf_object_streams.py` imports are
  untouched.)
- `services/api/app/drawings/sheet_primitives.py` — `SheetPage` gains defaulted
  `shading_skips`/`inline_image_skips` (the disclosed P3 skip counts — the output surface for
  §8.7.4.2 / §8.9.7 non-geometry); `SheetDocument` gains summing properties. Defaults keep a
  no-skip page byte-identical to the pre-P3 type (the split-equivalence goldens are unperturbed).
- `services/api/tests/drawings/test_sheet_p3_features.py` (NEW) — 20 AS-1/AS-2/AS-3 tests with
  committed load-bearing mutations.
- `services/api/tests/drawings/test_sheet_reader.py` — DELIBERATE golden revision (the two `sh`
  "unsupported operator" probes -> `zz`, since `sh` is now skipped).
- `services/api/tests/drawings/test_sheet_reader_split_equivalence.py` — DELIBERATE golden revision
  (the `refuse_unsupported_op` corpus case `sh` -> `zz`; digest + `_OVERALL` recaptured).

`pdf_object_streams.py`, `test_pdf_object_streams.py`, `sheet_marked_content.py`, `app/documents/`
UNCHANGED (`git diff --stat` empty). ISO 32000-1 cited next to the code; unverifiable
sub-citations carry `[recalled - verify]`.

## AS-1 (budgets, DB-055 c) — per-page budgets under a bounded document ceiling

Declared bounds (every number; all threaded from the facade so a monkeypatch still bites):

| bound | value | scope | reset |
|---|---|---|---|
| `MAX_CONTENT_OPERATORS` | 200,000 | operators on ONE page (incl. its forms) | per page |
| `MAX_PATH_POINTS` | 500,000 | flattened points on ONE page | per page |
| `MAX_PAGE_DECODED_BYTES` | 33,554,432 (32 MiB) | decoded bytes while building ONE page | per page |
| `MAX_DOCUMENT_OPERATORS` | 20,000,000 | operators summed across the document | never |
| `MAX_DOCUMENT_PATH_POINTS` | 50,000,000 | flattened points summed across the document | never |
| `MAX_TOTAL_DECODED_BYTES` | 134,217,728 (128 MiB) | decoded bytes across the document | never |
| `MAX_DECODED_STREAM_BYTES` | 8,388,608 (8 MiB) | one stream (unchanged) | per stream |
| leaf-page count | 512 | pages in the document (unchanged) | — |

The per-page pair keeps the public names `MAX_CONTENT_OPERATORS`/`MAX_PATH_POINTS` (semantics now
per-page); the document ceilings are new and set to 100x the per-page cap. A page over its budget
is `operator count` / `path points` / `page decoded bytes`; a document over its ceiling is the
DISTINCT `operator ceiling` / `path point ceiling` / `decoded bytes budget` (the last wording is
pinned by the M5-T104 per-document accounting test, so it is kept exactly).

**Worst-case arithmetic (nothing unbounded):**
- CPU: total operators executed <= 20,000,000 (each an O(1) dispatch + bounded per-op work); total
  flattened points <= 50,000,000 (each an O(1) append; a single degenerate Bezier stops at the
  remaining point budget threaded into `flatten_cubic`, never `2**MAX_FLATTEN_DEPTH` = 16.7M
  points); total decoded bytes <= 128 MiB (PNG unfilter is O(decoded bytes)); inline-image `EI`
  scanning is over already-decoded content bytes (bounded by the decoded budget) and capped at 8
  MiB per image.
- Memory (peak): the per-page output lists RESET each page, so retained geometry is ONE page's
  worth (<= 500,000 points ~ tens of MB of tuples + that page's text/images); one page's decoded
  content is transient (<= 32 MiB); the Form-decode memo caches decoded form bytes for the document
  (<= 128 MiB in the pathological many-distinct-forms case); the single-curve flatten transient is
  bounded to the remaining point budget. No allocation is sized by attacker geometry before it is
  bounded (inherited `apply_predictor` guard unchanged).

**Measured on the real 88-page vector set (item 1), validating the caps have headroom yet bound:**
peak page = 80,700 ops (40% of 200k) / 36,342 pts (7% of 500k); document = 2,302,175 ops (12% of
20M) / 1,355,056 pts (2.7% of 50M) / 25,580,637 decoded bytes (19% of 128 MiB). The largest real
file fits with 2.5x-37x headroom while every ceiling stays a hard bound.

AS-1 tests (test_sheet_p3_features.py): `test_as1_multipage_reads_under_per_page_budget` (a 2-page
doc whose op SUM exceeds the per-page cap now reads — the pre-M5-T118 single per-document budget
refused it), `test_as1_over_budget_page_operators_refuses`, `test_as1_document_operator_ceiling_refuses`
(distinct `operator ceiling`), `test_as1_over_budget_page_points_refuses`,
`test_as1_document_point_ceiling_refuses` (distinct `path point ceiling`),
`test_as1_over_budget_page_decoded_bytes_refuses`, plus the two reset-mutation tests below.

## AS-2 (`sh`, §8.7.4.2) — shading skipped as non-geometry with a disclosed count

`sh` paints a smooth colour shading, not linework, so it is skipped (operands cleared, count
incremented on the page and document), never refused. Tests: `test_as2_sh_skipped_with_count`
(the line before and after `sh` both draw; `page.shading_skips == 1`), `test_as2_two_sh_counted`,
`test_as2_sh_skip_is_load_bearing`.

## AS-3 (inline images, §8.9.7) — `BI`/`ID`/`EI` skipped without desync

Determinable (unfiltered, known geometry) => computed length + a REQUIRED whitespace-delimited
`EI`; not determinable (a filter present, or an unknown/array colour space) => a whitespace-
delimited `EI` scan under an 8 MiB cap; a length mismatch, an over-cap scan, or no `ID` is a typed
refusal (never a guess that desyncs). Tests: determinable-length skip + line-after draws;
image-mask determinable; scanned-length skip; array `/F` value scanned; length-mismatch refuses;
over-scan-cap refuses; no-`ID` refuses; skip is load-bearing; and the desync-guard mutation
(an under-consuming skip fails SAFE to a refusal, never a wrong drawing).

## Golden revisions (deliberate; before -> after)

`sh` was the stand-in "unsupported operator" in two suites; now that it is skipped, those probes use
a genuinely out-of-subset token `zz` (still `unsupported operator`), and the P3 skip is covered in
test_sheet_p3_features.py.

| location | case | before | after |
|---|---|---|---|
| test_sheet_reader.py | `test_as4_unsupported_operator_is_refused` | `0 0 1 sc 5 5 sh` | `0 0 1 sc 5 5 zz` (same assertion) |
| test_sheet_reader.py | `test_as4_all_or_nothing_...` | page-2 `5 5 sh` | page-2 `5 5 zz` (same assertion) |
| split_equivalence.py | `refuse_unsupported_op` content | `0 0 1 sc 5 5 sh` | `0 0 1 sc 5 5 zz` |
| split_equivalence.py | `refuse_unsupported_op` digest | `c0efa5e1c6a70962...c40c5baf75fd4c6` | `c4353d678cf4a7f9...c8a4ac75415cee0` |
| split_equivalence.py | `_OVERALL` | `887a0a680999ab46...8ba9c601840b5` | `137837884e15e8bf...a425c51cf29fe5b` |

Verified the per-page/document budget split and the `sh`/inline-image additions changed NO other
golden case: the recompute script reported `CHANGED vs golden: ['refuse_unsupported_op']` and the
corpus stays 63 cases (all 62 unrevised per-case digests unchanged).

## Real corpus (AS-4, honesty) — six files by sha256, two runs each, then deleted

Fetched to a scratch folder OUTSIDE the worktree, sha256-verified against
`docs/research/architect-drawing-corpus-2026-09.md` §2, run through `read_sheet` TWICE, then the
copies were deleted (`os.remove`; `REMAINING corpus files: []`; nothing from the corpus committed).
Observed under the 3.11 worktree shim (see Deviations). "result NOW" = DOCUMENT(pages, polylines,
segment-points, text-runs, images, sh-skips, inline-image-skips) or REFUSAL(feature).

| # | file | sha256 | run1==run2 | result NOW | next blocker |
|---|---|---|---|---|---|
| 1 | VA Div23 (1/2), 88pp vector | MATCH | True | **READS**: DOCUMENT 88pp, 332,057 polylines, 1,687,113 segpts, 1,567 text, 5 img, 0 sh, 0 inline | none — first real architect PDF read (per-page budget unblocked it; old 200k per-doc op budget refused it) |
| 2 | VA Div23 (2/2), 94pp vector | MATCH | True | REFUSED `path` ("'l' with no current point") | a lineto that begins a subpath after a paint with no `m` (path-state content gap; only reached now that the per-page budget cleared the old 200k op refusal — got to 604,687 ops) |
| 3 | VA DwgDelivRqmts, 14pp | MATCH | True | **READS**: DOCUMENT 14pp, 1,611 polylines, 6,444 segpts, 2,898 text, 19 img, **4 sh**, 0 inline | none — the `sh` skip unblocked it (was `sh @21738`) |
| 4 | Brooklyn Bridge HAER, 8pp scan+OCR | MATCH | True | **READS**: DOCUMENT 8pp, 11 polylines, 38 segpts, 990 text, 8 img, 0 sh, **3 inline** | none — inline-image skip unblocked it (was `BI @130`); reads as OCR text + page images + a few stray vector paths |
| 5 | Frantz-Dunn HABS, 1pp scan | MATCH | True | REFUSED `scan only` | none — a scan has no vector linework (correct terminal) |
| 6 | Rothschild HABS, 1pp scan | MATCH | True | REFUSED `scan only` | none — correct terminal |

All three P3 features are load-bearing on REAL files: (a) the per-page budget => item 1 (peak page
80,700 ops << 200k; doc 2.3M ops << 20M); (b) `sh` skip => item 3 (4 real `sh`); (c) inline-image
skip => item 4 (3 real `BI`). Nobody may claim item 2 reads or that ALL architect PDFs read — 3 of
6 do, and each honest outcome above is exactly what I observed.

## Mutation table (committed consuming-namespace mutations; each REAL != MUTANT proven by a passing test)

| guard | mutant (consuming namespace) | REAL | MUTANT | committed test |
|---|---|---|---|---|
| per-page operator RESET | `_SheetInterpreter.begin_page` -> no-op | 2-page doc reads | refuses `operator count` (ops accumulate) | `test_as1_per_page_operator_reset_is_load_bearing` |
| per-page operator cap | `MAX_CONTENT_OPERATORS` raised | page refuses `operator count` | page reads | `test_as1_over_budget_page_operators_refuses` |
| document operator ceiling | `MAX_DOCUMENT_OPERATORS` raised | refuses `operator ceiling` | doc reads | `test_as1_document_operator_ceiling_refuses` |
| per-page point cap | `MAX_PATH_POINTS` raised | refuses `path points` | reads | `test_as1_over_budget_page_points_refuses` |
| document point ceiling | (default vs low) | refuses `path point ceiling` | — | `test_as1_document_point_ceiling_refuses` |
| per-page decoded RESET | `_StreamDecoder.begin_page` -> no-op | 2-page doc reads | refuses `page decoded bytes` | `test_as1_page_decoded_bytes_reset_is_load_bearing` |
| per-page decoded cap | `MAX_PAGE_DECODED_BYTES` raised | refuses `page decoded bytes` | reads | `test_as1_over_budget_page_decoded_bytes_refuses` |
| `sh` skip | `sheet_interpreter._SKIP_SHADING` -> `frozenset()` | reads | refuses `unsupported operator` | `test_as2_sh_skip_is_load_bearing` |
| inline-image skip | `sheet_interpreter.skip_inline_image` -> refuse | reads | refuses `inline image` | `test_as3_inline_image_skip_is_load_bearing` |
| inline-image end-offset (no desync) | skip under-consumes (resumes at the dict) | line after draws | REFUSAL (fail-safe, never wrong geometry) | `test_as3_inline_image_end_offset_desync_fails_safe` |

Each test runs REAL then installs the mutant and asserts the flip in ONE test, so the passing suite
IS the recorded red/green (no throwaway harness committed).

## Self-checks (explicit cwd; verbatim tails)

1. `[OBSERVED]` cwd `services/api`: `python -m ruff check .` -> `All checks passed!`
2. `[BLOCKED -> OBSERVED-via-shim]` cwd `services/api`: `python -m pytest tests/drawings -q` cannot
   collect under the sandbox's Python 3.11 (`app/documents/units.py` PEP-695). Ran via the
   worktree-pointed shim `python <scratch>/m5t118/shim311/runtests.py tests/drawings -q
   -p no:cacheprovider` -> `272 passed in 14.92s` (was 252 pre-P3; +20 new). Per file:
   `test_pdf_object_streams` **44 passed (UNCHANGED, read-only)**, `test_sheet_p3_features` 20
   passed, `test_sheet_reader` / `test_sheet_reader_split_equivalence` / `test_sheet_content_features`
   all green. CI (3.12) is the authority.
3. `[OBSERVED]` cwd repo root: `python tools/modularity_check.py --check` -> exit `0`
   (sheet_interpreter.py 748 SLOC crosses the ADVISORY warn threshold but is < 750, non-blocking).
4. `[OBSERVED]` cwd `wt-m5t118`: `git status --short` -> exactly the 8 allowed paths;
   `git diff --stat` on the forbidden files -> empty (unchanged).

## Deviations

- **Documented pytest blocked on sandbox Python 3.11; observed via a worktree-pointed shim.** The
  packet's named shim (`...\ctl24\...\shim311`) points `API_ROOT` at the PRIMARY checkout, which does
  NOT carry my edits, so I copied the same shim mechanism into
  `<scratch>/m5t118/shim311/` with `API_ROOT` re-pointed at `wt-m5t118\services\api`, so the tests
  exercise THIS task's code. It stubs only package `__init__` bodies (units.py never compiles);
  drawings behaviour under test is unmodified. CI (3.12) `python -m pytest tests/drawings -q` is the
  authority — HARVEST it there.
- **`sheet_primitives.py` touched beyond "where a budget lives".** The two disclosed skip-count
  fields on `SheetPage`/`SheetDocument` are the observable OUTPUT surface of the §8.7.4.2 / §8.9.7
  non-geometry skips; the frozen output types are their natural home and the point budget already
  threads through this module's `flatten_cubic`. Defaults keep pre-P3 pages byte-identical. If a
  reviewer prefers the counts elsewhere it is a trivial relocation (see OPEN QUESTIONS 3).

## OPEN QUESTIONS (owner asleep — recommended answers)

1. **Item 2 (94pp vector) refuses at `path` "'l' with no current point".** This is a lineto that
   begins a subpath after a paint with no intervening `m` — per ISO 32000-1 §8.5.2 there is no
   current point after a painting operator, so the refusal is spec-correct for that byte sequence,
   but a real CAD producer emitting it means the reader cannot read this file. RECOMMEND a follow-up
   packet decide whether to (a) treat a post-paint `l`/`c` as implicitly reopening at the last
   current point (lenient, matches some viewers) or (b) keep the strict refusal and disclose it.
   Out of scope here (P3 = the three named blockers). Do NOT change path-state semantics blindly.
2. **Document ceilings 20M ops / 50M pts / 128 MiB.** Chosen as 100x the per-page cap; the largest
   real file uses 12% / 2.7% / 19%. RECOMMEND keep; the future import route still owns a per-request
   DEADLINE (DB-076 d) — a wall-clock bound is orthogonal to these work budgets and not this
   packet's job.
3. **Skip counts on the frozen output types.** RECOMMEND keep on `SheetPage`/`SheetDocument` (honest
   per-page disclosure, defaults preserve equivalence). Alternative: a document-level side channel.
4. **Inline-image `EI` scan false-positive.** A binary `<ws>EI<ws>` inside FILTERED sample data
   could end the scan early; because the reader never decodes samples, an early cut desyncs into a
   DOWNSTREAM typed refusal (fail-safe), never a wrong drawing. RECOMMEND accept (the standard inline-
   image heuristic); a length-bearing decoder is a future option if a real file trips it.

## DISCOVERIES (D-069 — for the orchestrator to record)

- **3 of 6 real architect PDFs now READ** (items 1, 3, 4) — the first end-to-end real reads; item 1
  is an 88-page vector CAD set (332k polylines). All three P3 features are load-bearing on real
  files. [product milestone — the owner-visible D-087-R005 goal is partially met]
- **Item 2 (94pp vector) next blocker: `path` "'l' with no current point"** — a post-paint lineto
  with no moveto; the per-page budget advanced it past the old 200k operator refusal to this deeper
  path-state gap. [reader content-subset gap; next PDF packet — see OPEN QUESTIONS 1]
- **Item 4 reads as scan+OCR** (8 page images + 990 OCR text runs + 3 skipped inline images + 11
  stray vector paths) — not scan-only, because it has stray linework. Honest: it "reads" but the
  content is OCR/raster, not drawing geometry a consumer should treat as linework. [product note —
  a class label (vector vs scan) belongs to a later human-confirmed stage]
- **Per-page budgets validated against a real file:** peak page 80,700 ops / 36,342 pts on the 88-
  page set; the 200k/500k per-page caps and 20M/50M/128MiB document ceilings have 2.5x-37x headroom.
  [reader tuning; by note]

END-OF-REPORT
