# M5-T113 producer report — D-087 PDF-reading P2 (DB-076 a-c, e)

Content-stream `/DecodeParms` PNG predictors, marked-content `BDC`/`DP` inline `<< >>`
property-list dictionaries, and a reachable + honest scan-only refusal; the six real
architect PDFs re-run by sha256. Producer: backend-engineer (orchestrator-dispatched
subagent). Worktree: `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t113`, branch
`task/M5-T113-pdf-content-features`, from claim seam `275ef85f`.

Directives: D-087-R001/R002/R005/R009, D-066-R001. Unwired (no route/app change); zero new
dependencies.

## Files changed (all inside allowed_paths)

- `services/api/app/drawings/sheet_objects.py` — content/form `_decode_stream` now accepts a
  `/DecodeParms` §7.4.4.4 PNG predictor by REUSING the existing bounded `apply_predictor`; new
  helper `_content_decode_parms`. TIFF (2), filter arrays, other filters, corrupt/over-cap stay
  typed refusals; every existing bound preserved (byte cap; predictor geometry bounded before any
  buffer is sized — inherited unchanged via `apply_predictor`).
- `services/api/app/drawings/sheet_marked_content.py` (NEW, 171 SLOC) — bounded balanced inline
  `<< >>` property-list lexer (`read_inline_dict`), declared depth + byte caps, discarded sentinel
  (`MarkedContentDict`); reuses the strict `lex_primitive` for scalars.
- `services/api/app/drawings/sheet_interpreter.py` (665 → 690 SLOC; < 750) — minimal wiring: a
  `<<` branch in the scan loop calling `_read_inline_dict`; `BDC`/`DP` still clear it via `_IGNORED`.
- `services/api/app/drawings/sheet_reader.py` — threads the two marked-content bounds into the
  interpreter limits (patchable); extracts `_scan_only_refusal` as a module-level mutation seam and
  enriches the detail (feature kept `"scan only"`).
- `services/api/tests/drawings/test_sheet_content_features.py` (NEW) — AS-1/AS-2/AS-3 + committed
  load-bearing mutations (28 tests).
- `services/api/tests/drawings/test_sheet_reader_split_equivalence.py` — DELIBERATE golden revision
  (below). `test_sheet_reader.py` needed NO change (byte-identity preserved) and is unmodified.

ISO 32000-1 cited next to the code: §7.4.4.4 (predictors), §14.6 (marked content), §8.2
(content-stream operators). Sub-citations already marked `[recalled - verify]` where unverified.

## Acceptance-scenario evidence

- **AS-1 (predictor content streams)** — `test_as1_png_predictor_content_stream_draws[0-4]`: a
  `/FlateDecode` + PNG predictor content stream (each row filter 0-4) decodes through the reused
  `apply_predictor` and draws (0,0)->(10,0). `test_as1_tiff_predictor_content_stream_refuses` →
  `feature="predictor"` ("TIFF..."); `test_as1_out_of_range_predictor_refuses`;
  `test_as1_decode_parms_without_filter_refuses` / `_non_dictionary_refuses` →
  `feature="decode parameters"`; `test_as1_predictor_none_passthrough_draws` (Predictor 1);
  budget still charged pre-predictor (`test_as1_predictor_stream_shares_the_document_decoded_budget`).
- **AS-2 (marked content)** — `test_as2_bdc_inline_dict_draws_geometry_inside`,
  `test_as2_dp_inline_dict_draws_and_points_nothing`, `test_as2_nested_inline_dict_and_array_draws`
  (nested `<< >>` + `[ ]` + string/hex/bool within depth). `test_as2_bmc_and_name_property_list_still_work`
  (BMC/EMC + NAME operand). `test_as2_hex_string_operand_still_lexes` (single `<` unaffected).
  `test_as2_unbalanced_inline_dict_refuses` and `test_as2_inline_dict_wrong_position_is_refused`
  (dangling operands) → typed refusals.
- **AS-3 (scan-only reachable + honest)** — `test_as3_marked_content_with_geometry_draws_on_resolver_path`
  (marked content parses on the resolver path); `test_as3_scan_only_reachable_through_marked_content`
  and `test_as3_scan_only_reaches_a_real_raster_page` → `feature="scan only"`, origin sheet_profile.
  DB-076 (e) inconsistencies DISCLOSED by characterization tests
  `test_disclosed_scan_only_label_also_fires_on_text_only` and
  `test_disclosed_image_only_classic_succeeds_but_resolver_refuses` (rationale in OPEN QUESTIONS).
- **AS-4 (real corpus)** — table below. **AS-5 (scope)** — zero new deps; unwired; read-only
  `test_pdf_object_streams.py` passes UNCHANGED (44 passed); ruff clean; modularity exit 0
  (sheet_interpreter 690 < 750); exactly the allowed paths (`git status`: 6 files).

## Deliberate golden revision (`test_sheet_reader_split_equivalence.py`, DB-076 a)

The pre-M5-T113 corpus froze `/DecodeParms` as an unconditional refusal. Revised deliberately:

| | case | result | per-case sha256 |
|---|---|---|---|
| BEFORE | `refuse_decode_parms` | REFUSAL `feature="decode parameters"` | `9530c4e65ca0acc0f986c1f9ce72255a09c99e72f4600f54aa302e6f5f96c023` |
| AFTER (new expected) | `decode_parms_png_predictor` | DOCUMENT draws (5,7)->(9,3) | `f1b2f8353122b7680f3c43eaa03773396eab071dd39143456846e65e945da6e0` |
| AFTER (stays unsupported) | `refuse_decode_parms_tiff` | REFUSAL `feature="predictor"` (TIFF) | `f0c87de8e7d60cfc42304a901dadd438661664811f570926778b6d4788a2b479` |

`_OVERALL` `767766eb…` → `887a0a68…`; corpus 62 → 63 cases. The `decode_parms_png_predictor`
digest equals the plain `line` case's (identical drawn output — the predictor round-trips). The
predictor is load-bearing (row filter tag 2, not 0). **All other 61 per-case digests are UNCHANGED**
(verified: `CHANGED digests among shared cases: {}`), so the M5-T094 split-equivalence proof holds
for everything the split touched.

## Real corpus (AS-4, honesty) — six files by sha256, two runs each, then deleted

Downloaded to a scratch folder OUTSIDE the worktree, sha256-verified against
`docs/research/architect-drawing-corpus-2026-09.md` §2, run through `read_sheet` TWICE, then the
copies were deleted (`rm` exit 0; nothing from the corpus committed). Observed under the 3.11 stub
shim (see Deviations).

| # | file (producer) | sha256 | run1==run2 | result NOW | next blocker |
|---|---|---|---|---|---|
| 1 | VA HVAC Div23 (1/2), 88pp vector (PDFMaker 9 for AutoCAD) | MATCH | True | REFUSED `operator count` (over 200000 operators) | per-DOCUMENT 200k operator budget (DB-055 c) — a real 88-page vector set exceeds it |
| 2 | VA HVAC Div23 (2/2), 94pp vector | MATCH | True | REFUSED `operator count` (over 200000 operators) | same (94-page) |
| 3 | VA Dwg Deliv Rqmts, 14pp (PDFMaker 11 for Word) | MATCH | True | REFUSED `unsupported operator` `sh` @21738 | `sh` shading operator unsupported (M5-T093 §5 P2; now REACHED) |
| 4 | Brooklyn Bridge HAER, 8pp scanned+OCR | MATCH | True | REFUSED `unsupported operator` `BI` @130 | inline image BI/ID/EI — intentionally refused (DB-055 d) |
| 5 | Frantz-Dunn HABS, 1pp scanned | MATCH | True | REFUSED `scan only` | none to "read" — a scan has no vector linework (correct terminal) |
| 6 | Rothschild HABS, 1pp scanned | MATCH | True | REFUSED `scan only` | none to "read" — correct terminal |

**Headline (honest): 0 of 6 read fully — nobody may tell the owner that real architect PDFs can be
read.** But this packet's two features are load-bearing on the REAL files and advance all six from a
single uniform xref-stage refusal (M5-T103 baseline) to six DISTINCT, correct content-level
outcomes. Attribution probe (features disabled in-process, approximating the M5-T103 baseline):
items 1-2 → `decode parameters` (need (a) predictor); items 3-6 → `marked-content dictionary` (need
(b) inline dicts). So:
- (a) is what lets items 1-2 get past content decode (they then hit the operator budget).
- (b) is what lets items 3-6 parse; item 3 then hits `sh`, item 4 hits `BI`, and **items 5-6 reach
  the scan-only refusal — DB-076 (c) achieved on REAL scanned files, directly attributable to (b).**

## Mutation table (consuming-namespace; committed load-bearing tests + explicit red runs)

| guard | mutant (consuming namespace) | REAL | MUTANT (RED) | committed test |
|---|---|---|---|---|
| predictor acceptance (a) | `sheet_objects.apply_predictor` → refuse | draws | refuses `decode parameters` | `test_as1_predictor_acceptance_is_load_bearing` |
| inline-dict acceptance (b) | `sheet_interpreter.read_inline_dict` → refuse | draws | refuses `marked-content dictionary` | `test_as2_inline_dict_acceptance_is_load_bearing` |
| marked-content depth cap | `sheet_reader.MAX_MARKED_CONTENT_DEPTH`=1 | draws | refuses (`...depth...`) | `test_as2_depth_cap_is_load_bearing` |
| marked-content byte cap | `sheet_reader.MAX_MARKED_CONTENT_BYTES`=4 | draws | refuses (`...bytes...`) | `test_as2_byte_cap_is_load_bearing` |
| scan-only gate (c) | `sheet_reader._scan_only_refusal` → None | refuses `scan only` | empty-page DOCUMENT | `test_as3_scan_only_gate_is_load_bearing` |

Explicit throwaway red/green run (`mutation_demo.py`, not committed): each guard REAL draws=True,
MUTANT draws=False. Harnesses were NOT committed.

## Self-checks (explicit cwd; verbatim tails)

1. `[OBSERVED]` cwd `services/api`: `python -m ruff check .` → `All checks passed!`
2. `[BLOCKED]` cwd `services/api`: `python -m pytest tests/drawings -q` → collection error, the
   sandbox's only interpreter is Python 3.11.9 and the repo needs 3.12: `File "…/app/documents/units.py",
   line 276 … SyntaxError: expected '('` (PEP-695 generic, pulled in eagerly by
   `app/documents/extraction/__init__` → routing → checks → boundary → units); `4 errors during
   collection`. Routed to CI (authoritative on 3.12) + observed via the 3.11 stub shim →
2b. `[OBSERVED via shim]` `python runtests.py …/tests/drawings -q` → `245 passed`. Per file:
   `test_pdf_object_streams` **44 passed (UNCHANGED, read-only)**, `test_sheet_reader` 46 passed,
   `test_sheet_reader_split_equivalence` 9 passed, `test_sheet_content_features` 28 passed (the rest
   of the 245 are the sibling dxf/other drawings suites, all green).
3. `[OBSERVED]` cwd repo root: `python tools/modularity_check.py --check` → exit `0`
   (sheet_interpreter.py 690 SLOC crosses the ADVISORY warn threshold but is < 750 and non-blocking).

## Deviations

- **Documented pytest blocked on the sandbox's Python 3.11; observed via a stub shim.** Only
  Python 3.11.9 is usable (the registered 3.13/3.9 launchers point at missing executables). The
  drawings suites cannot import under 3.11 because `app/documents/extraction/__init__` eagerly
  imports a chain ending at `app/documents/units.py` (3.12 PEP-695 syntax). I ran the suites under a
  scratch bootstrap (`_boot.py`) that pre-seeds STUB parent packages (`app`, `app.documents`,
  `app.documents.extraction`, `app.drawings`) so the leaf `pdf_lexer`/`pdf_objects`/`pdf_xref` +
  `sheet_*` modules load and execute the REAL code without compiling `units.py`. The drawings
  behavior under test is unmodified; only unrelated side-effect `__init__` bodies are stubbed. The
  authoritative 3.12 `python -m pytest tests/drawings -q` run is CI's job — HARVEST it there.
- **DB-076 (e) inconsistencies DISCLOSED, not fixed** (see OPEN QUESTIONS 2-3).

## OPEN QUESTIONS (owner asleep — recommended answers)

1. **Items 1-2 (real vector CAD) now hit the per-DOCUMENT 200k operator budget.** These are the
   first real files past content decode. RECOMMEND: a follow-up packet make the operator/point/
   decoded-byte budgets per-PAGE (or raise them with a documented rationale) paired with the
   DB-076 (d) per-request work budget, so a legitimate large multi-page vector set is not refused
   on the sum. Out of scope here (P2 = content features). Do NOT raise budgets blindly.
2. **(e) #2 image-only classic-succeeds / resolver-refuses — DISCLOSED.** Fixing requires running
   the scan-only gate on the classic path too, which flips accepted classic image-only behavior and
   revises goldens beyond this packet's authorized revision; and every real corpus file is PDF 1.5+
   (resolver path), so the asymmetry never affects them. RECOMMEND: leave disclosed; unify in a
   dedicated packet if ever wanted.
3. **(e) #1 scan-only label also fires on text-only — DISCLOSED.** The read-only
   `test_pdf_object_streams.py::test_scan_only_page_is_typed_refusal` PINS `feature=="scan only"`
   for a text-only resolver doc, so the label cannot be relabeled without editing a must-pass-
   unchanged suite. I enriched the detail to name the text-only case honestly. RECOMMEND: introduce
   a distinct `"text only"` feature only in a packet also allowed to revise that read-only test.

## DISCOVERIES (D-069 — for the orchestrator to record)

- **Per-document budget vs real vector sheets:** items 1-2 refuse on `MAX_CONTENT_OPERATORS`
  (200000) — the first real files to clear content decode. The operator/point budgets should become
  per-page or be paired with a per-request work budget (DB-055 c + DB-076 d) so real large vector
  drawings can read. [reader/product gap; next content packet]
- **`sh` shading (item 3) and inline images `BI`/`ID`/`EI` (items 2, 4) are now REACHED** on real
  files (previously latent behind the xref refusal). `sh` needs a typed shading refusal or explicit
  ignore (M5-T093 §5 P2); inline images intentionally stay refused (DB-055 d). [next content packet]
- **3.11/3.12 sandbox split:** a committed reusable bare-package shim for the drawings/extraction
  suites (DB-064 g) would remove per-task re-authoring of the `_boot.py` bootstrap this task needed.
  [dev-tooling]

END-OF-REPORT
