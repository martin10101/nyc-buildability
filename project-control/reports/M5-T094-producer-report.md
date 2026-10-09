# M5-T094 producer report — D-087 PDF-1c: split the architect-sheet reader before any growth

Producer: backend-engineer (orchestrator-dispatched subagent).
Worktree: `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t094` (branch `task/M5-T094-sheet-reader-split`).
Claim-seam / parent: `a749d995`. Task: split `services/api/app/drawings/sheet_reader.py`
(962 SLOC, at the modularity justification ceiling) along its natural seam BEFORE the C1
reader packet must grow it — object-graph/stream-decode vs the operator interpreter behind a
compatibility facade — with **byte-identical behaviour (no feature change)**.

Evidence-status legend: `[OBSERVED]` = I ran it and pasted the real result; `[BLOCKED]` = I
could not run it here, with the exact command + reason, routed to CI.

## What changed (exactly the allowed paths)

Production:
- `services/api/app/drawings/sheet_objects.py` (NEW, 245 SLOC) — refusal helpers
  (`_wrap_strict`/`_refuse`/`_preview`/`sheet_refusal`), object-graph resolution
  (`_resolve`/`_resolved_int`/`_media_box`/`_catalog_pages_root`), single-stream decode
  (`_decode_stream`), and the `_StreamDecoder` class that owns the **document-wide
  decoded-bytes budget (`charge_decoded`), the Form-decode memo (`decode_form`/`form_cache`)
  and `/Contents` joining (`decode_contents`)** — DB-055 (b) "decode budgets, form memo,
  contents joining". Imports only downward (strict-reader leaf modules + `sheet_primitives`).
- `services/api/app/drawings/sheet_interpreter.py` (NEW, 584 SLOC) — the per-content-stream
  operator executor `_StreamRun` (graphics/text state, path construction with Bezier
  flattening, form placement), `_matches`, the operator vocabulary frozensets and
  `_PATH_HANDLERS` dispatch, and `_IDENTITY`. Imports `sheet_objects` + `sheet_primitives`.
- `services/api/app/drawings/sheet_reader.py` (REWRITTEN facade, 314 SLOC) — the public entry
  `read_sheet`/`sheet_refusal`, the profile bound constants (the patch surface), the
  `_flatten_cubic`/`_concat_matrix`/`_decode_stream`/`_catalog_pages_root` re-export aliases,
  the top-level backstop, the page-tree driver (`_read_sheet`/`_build_page`), and the
  per-document coordinator `_SheetInterpreter`/`_InterpreterLimits`. `__all__` unchanged.

Test:
- `services/api/tests/drawings/test_sheet_reader_split_equivalence.py` (NEW) — the AS-2
  byte-identical corpus + the AS-4 guard mutations (see below).

Report: this file.

`git diff --stat a749d995` = exactly these 4 code/test paths (+ this report). `app/documents/`
and `sheet_primitives.py` are **byte-untouched** (`git diff a749d995 -- <path>` empty for both).
No production module outside `app/drawings/` imports the reader (grep clean) — **not wired**.

## Architecture / import DAG (AS-3)

Runtime import edges are acyclic, top-down:
`sheet_reader (facade) -> sheet_interpreter -> sheet_objects -> {sheet_primitives, documents.extraction}`,
plus the facade's direct `-> sheet_objects` / `-> sheet_primitives` (still acyclic — the facade
is above both). The only back-reference is a **`TYPE_CHECKING`-only** import of `_SheetInterpreter`
into `sheet_interpreter` for one parameter annotation; it is never imported at runtime, so the
runtime DAG has no cycle. Verified by import + full test run under the bare-package shim.

The shared `app/documents/extraction/pdf_xref.read_object_table` (forbidden) is untouched; the
C1 packet's PDF 1.5+ xref/object-stream resolver has a clean seam as a NEW profile-level module
that `sheet_objects` can delegate to.

## Behaviour preservation — the golden (AS-2)

Before editing `sheet_reader.py`, I ran a 62-case equivalence corpus through the PRE-split module
and pinned sha256 digests of a total, order-preserving canonical serialization of each
`read_sheet` result (documents: every page's box/user_unit/tolerance and every
polyline/text-run/image field with round-trip float repr; refusals: reject_code/feature/detail/
origin). Corpus coverage: curves (`c`/`v`/`y`, quarter-circle, asymmetric), full-affine CTM
(rotate/shear), nested `q`/`Q`, mid-path `cm`, all text ops (`Tf`/`Td`/`TD`/`Tm`/`T*`/`Tj`/`TJ`/
`'`/`"`), forms (placed twice, `/Matrix`, text inheritance, flate, cycle, depth), images
(counted/never-decoded, missing dims), flate/contents-array/inherited-box content, multi-page,
and **every refusal class + every budget** (operator/path-point/q-depth/xobject-depth/
decoded-bytes/stream-size, the last six patched exactly as the existing suite does so they also
prove the split threads a patched bound). 32 documents + 30 refusals.

- Pinned overall golden (pre-split): `767766ebc3e1bf1edbba58558d612db06e1fec18fa1d0713dbe8e47fe5283106`
- Post-split re-capture: **identical** overall digest `[OBSERVED]`; all 62 per-case digests
  identical (pinned in the test as `_GOLDEN`).
- Sensitivity (not vacuous) `[OBSERVED]`: mutating the threaded `_concat_matrix` changes the
  overall digest; restoring returns it to the golden.

## Acceptance scenarios

- **AS-1 (API preserved) [OBSERVED]** — every `__all__` name and every internal name the frozen
  37-test file rebinds on `sheet_reader` (`_flatten_cubic`, `_concat_matrix`, `_decode_stream`,
  `_catalog_pages_root`, `_read_sheet`, all `MAX_*`, `DEFAULT_FLATTEN_TOLERANCE`) resolve from
  `app.drawings.sheet_reader`; `from …sheet_reader import *` exposes `read_sheet`+`sheet_refusal`.
  The 37 existing tests pass **unchanged** (not edited).
- **AS-2 (byte-identical) [OBSERVED]** — overall + all 62 per-case digests equal the pre-split
  golden; the two equivalence tests + the non-triviality guard pass.
- **AS-3 (modularity) [OBSERVED]** — each new module < 600 SLOC (objects 245, interpreter 584,
  facade 314); acyclic imports (above); `modularity_check --check` exit 0, failures 0, and **no
  app/drawings warning** (previously `sheet_reader.py` at 962 emitted a JUSTIFY-band warning —
  now gone).
- **AS-4 (security guards kept) [OBSERVED]** — one mutation per guard reddens (table below).
- **AS-5 (scope) [OBSERVED]** — zero new dependencies (imports: only `math`, `zlib`,
  `dataclasses`, `typing` + in-repo `app.*`); `app/documents` and `sheet_primitives.py`
  byte-untouched; not wired; exactly the allowed paths changed.

## AS-4 mutation table (each guard is load-bearing)

| Guard | Real (guard active) | Mutation | Result with mutant |
|---|---|---|---|
| flatten point budget | never-flat curve, `MAX_PATH_POINTS`=5000 → refusal `path points` | `_flatten_cubic` ignores budget (append p3, return True) | SheetDocument (no refusal) |
| decoded-bytes budget | page decode, `MAX_TOTAL_DECODED_BYTES`=4 → refusal `decoded bytes budget` | `_StreamDecoder.charge_decoded` → no-op | SheetDocument |
| form depth guard | A→B→line, `MAX_XOBJECT_DEPTH`=1 → refusal `xobject recursion` | `_place_form` resets `self._depth` | SheetDocument |
| form cycle guard | self-ref form → refusal `xobject cycle` | `_place_form` clears `self._stack` | refusal, feature ≠ `xobject cycle` (falls through to depth bound) |
| top-level backstop | `_catalog_pages_root` raises → refusal `unexpected error` (only the exception TYPE) | call `_read_sheet` directly (no backstop) | `RuntimeError` propagates (`pytest.raises`) |
| finiteness gate | CTM overflow to inf → refusal `non-finite coordinate` | `sheet_interpreter._is_finite_point` → always True | SheetDocument (inf coords admitted) |

The 6 pre-split budget/guard mutation tests inside the frozen 37-test suite (patching
`sheet_reader._flatten_cubic`/`_concat_matrix`/`MAX_*`/`_decode_stream`/`_catalog_pages_root`)
also still pass — proving the split preserved the in-process mutant seam (facade constant/hook
patch → threaded into the running interpreter/decoder).

## Commands (verbatim; explicit cwd)

- `[OBSERVED]` cwd `wt-m5t094/services/api`: `python -m ruff check .` → `All checks passed!`
  (ruff is the api CI job's first step; ran clean on the full api tree).
- `[BLOCKED]` cwd `wt-m5t094/services/api`:
  `python -m pytest tests/drawings/test_sheet_reader.py tests/drawings/test_sheet_reader_split_equivalence.py -q`
  → collection ERROR on **local Python 3.11**: `SyntaxError: expected '('` at
  `def _match_unit[UnitT: enum.Enum](` (PEP 695 generics, 3.12-only), reached transitively via
  `app/documents/extraction/__init__.py`. This is an environment limit, not a defect in this
  task's code. Routed to (a) CI on Python 3.12 for the raw command and (b) the local bare-package
  shim below, which registers `app`/`app.documents`/`app.documents.extraction`/`app.drawings` as
  bare packages so the 3.11-safe strict-reader leaves load without the 3.12 package `__init__`.
- `[OBSERVED]` cwd `wt-m5t094/services/api`, via the shim
  (`scratchpad/m5t094/run_sheet_tests_ctl24.py`): both test files, **46 passed** (37 unchanged +
  9 new: 3 equivalence/shape + 6 guard mutations), 0 failed, 0 skipped.
- `[OBSERVED]` cwd `wt-m5t094` (repo root): `python tools/modularity_check.py --check` →
  `selected 488 files; failures 0; warnings 25`, exit 0, no app/drawings line.

## SLOC per module (modularity_check source_lines)

- `sheet_objects.py` = 245 (symbols 10)
- `sheet_interpreter.py` = 584 (symbols 2)
- `sheet_reader.py` = 314 (symbols 5)

All < 600 (WARN); pre-split `sheet_reader.py` was 962 (JUSTIFY-band warning), now cleared.

## Deviations (disclosed)

1. The per-document **coordinator `_SheetInterpreter`** (with `_InterpreterLimits`) lives in the
   **facade**, not in `sheet_interpreter`, so the runtime import DAG stays acyclic
   (`interpret()` drives `_StreamRun`; the page walk drives `interpret()`) AND `sheet_interpreter`
   stays < 600 SLOC (it would be 657 with the coordinator). The bulk of DB-055 (b)'s "operator
   interpreter (graphics/text state, path construction, form placement)" — `_StreamRun` — is in
   `sheet_interpreter` as specified. The coordinator's document-wide op/point counters sit with
   the facade driver that owns document orchestration; the decoded-bytes budget and Form memo sit
   on `_StreamDecoder` in `sheet_objects` exactly as DB-055 (b) assigns. This is a literal-text
   deviation from "keep the operator interpreter in a second new module", disclosed here; the
   responsibility split is clean and the behaviour is byte-identical.
2. One **`TYPE_CHECKING`-only** back-reference (`sheet_interpreter` → facade `_SheetInterpreter`)
   for a parameter annotation; no runtime import, no runtime cycle.

## DISCOVERIES (out-of-scope; not fixed in-packet)

- D1: the dispatch said to copy `scratchpad\run_sheet_tests_ctl24.py` into the scratch folder, but
  no such shim exists in the repo or the primary checkout's `scratchpad/`. I authored an
  equivalent bare-package shim from scratch (kept in the session scratch dir only, not committed).
  A committed, reusable 3.11 shim for the drawings/extraction suites would remove this per-task
  re-authoring; candidate for a tools/dev-helper packet.
- D2 (env, pre-existing, already in program knowledge): `app/documents/extraction/__init__.py`
  eagerly imports `routing`/`survey_pipeline`/`vector_pdf_decoder`, whose chain uses PEP 695
  syntax (`def _match_unit[UnitT: enum.Enum]`), so ANY local (3.11) `pytest` that imports that
  package fails at collection. Only the shim or CI (3.12) can run these suites locally. Not a
  defect of this task; noted so reviewers use the shim, not a raw local pytest.

END-OF-REPORT
