# M5-T103 producer report — PDF 1.5+ xref-stream / object-stream resolver (D-087 PKT-K / C1)

Producer: backend-engineer. Worktree: `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t103`
(branch `task/M5-T103-pdf-object-streams`). Claim seam / parent:
`e9a268a52704a073a52ee0a34f4230394dbf9a49`.

## What shipped

A NEW profile-level resolver `services/api/app/drawings/pdf_object_streams.py` that builds a
`PdfObjectTable` for PDF 1.5+ files the shared strict reader
(`app/documents/extraction/pdf_xref.read_object_table`) refuses — WITHOUT widening that shared
reader (DB-055 (k)). It resolves cross-reference streams (`/Type /XRef`: `/W` field widths,
`/Index` subsections defaulting to `[0 /Size]`, entry types 0/1/2, bounded `/Prev` chains with a
cycle guard, and the PNG predictors of §7.4.4.4), object streams (`/Type /ObjStm`: `/N`,
`/First`), and hybrid-reference files (§7.5.8.4 `/XRefStm`). It is wired into the
`sheet_reader` facade as a fallback that fires ONLY when the strict reader refuses a
cross-reference-stream-family feature, so a classic-`xref` file takes the old path byte-for-byte.

ISO 32000-1 §7.5.7 / §7.5.8 / §7.5.8.4 / §7.4.4.4 are the authority; each structural constant
carries its section, and the PNG unfilter / Paeth math is marked `[recalled - verify]` (and was
corroborated by decoding the real corpus xref streams). Every unsupported construct (encryption,
non-Flate filter, TIFF predictor 2, unknown predictor, lying offset, `/Prev` cycle/over-depth,
bound overrun) is a typed refusal VALUE; the resolver never raises.

### Files changed (all inside allowed_paths)
- `app/drawings/pdf_object_streams.py` — the resolver (was a 1-line placeholder). 588 SLOC.
- `app/drawings/sheet_reader.py` — facade fallback + shared-budget seed + scan-only gate. 342 SLOC.
- `app/drawings/sheet_objects.py` — `decoded_bytes` budget seed; `_preview` on the unsupported
  `/Filter` detail (DB-064 (c)); NEW shared decode primitives `inflate_guarded` /
  `apply_predictor` / `_png_unfilter` (composed by the resolver; not on the classic path). 353 SLOC.
- `app/drawings/sheet_interpreter.py` — `_preview` truncation of the XObject `/name` echoes in
  the five refusal details (DB-055 (f)). 586 SLOC.
- `tests/drawings/test_pdf_object_streams.py` — 29 acceptance + mutation tests (was a placeholder).
- `project-control/reports/M5-T103-producer-report.md` — this report.

`app/documents/extraction/` is byte-untouched (`git diff --stat` empty). No route / main.py / web
change; zero new dependencies (stdlib `zlib` only). Imports acyclic (facade → resolver → objects;
resolver → objects; no back-edge).

## Mandatory decompression guard (M5-T099 G5 F2(a))

`inflate_guarded` inflates every xref/object stream by BOUNDED INCREMENTAL decompression
(`zlib.decompressobj().decompress(src, 65536)` in a loop — never an unbounded `zlib.decompress`),
charging each 64 KiB chunk against the shared document-wide budget and checking the absolute
inflated-bytes cap and the inflate-ratio guard BEFORE the chunk is retained (DB-064 (d): no
post-increment overshoot). The budget total is seeded into the content-stream `_StreamDecoder`
(`decoded_bytes=`) so the xref/objstm and content phases share ONE budget. `/Prev` depth, object
-stream count, and each `/N` are bounded.

## Acceptance scenarios

- **AS-1 (resolver).** `test_reads_uncompressed_xref_stream`, `test_reads_object_stream_entry_types_0_1_2`
  (type 0/1/2 through one file), `test_reads_partial_object_stream`, `test_multiple_index_subsections`,
  `test_each_png_predictor_row_filter[0..4]` (each PNG filter), `test_narrow_field_widths_default_generation`
  (`/W [1 2 1]`), `test_prev_chain_newer_entry_wins`, `test_prev_cycle_is_refused`,
  `test_hybrid_xrefstm_file_reads`, `test_classic_xref_still_takes_old_path` (resolver patched to
  explode — a classic file must not call it), and typed-refusal tests for encryption, TIFF
  predictor 2, and a lying type-1 offset. All pass.
- **AS-2 (guard + mutations).** Mutation table below; plus `test_zip_bomb_refuses_with_bounded_memory`
  (a 50 MB-inflating xref stream refuses `inflated bytes cap` with `tracemalloc` peak < 5 MB).
- **AS-3 (hygiene).** `test_xobject_name_echo_is_preview_truncated` (90-char `/name` → detail carries
  `...(truncated)`, full name absent), `test_unsupported_filter_name_is_preview_truncated` (DB-064 (c)),
  `test_scan_only_page_is_typed_refusal` (resolved page, zero vector geometry → `scan only`),
  `test_vector_page_is_not_scan_only`. The scan-only gate is scoped to the NEW resolver path so the
  classic image-only success (`test_as3_image...` / `image_counted` golden) is unchanged.
- **AS-4 (no regression).** The 62-case split-equivalence golden overall digest and the existing
  sheet-reader suites pass UNCHANGED (see below); `app/documents/extraction` byte-untouched; every
  production module < 600 SLOC; `modularity_check --check` exit 0.
- **AS-5 (real corpus, honest).** Corpus table below.
- **AS-6 (scope).** Only the 6 allowed paths changed; zero new deps; unwired.

### Mutation table (each guard reddens under an in-process rebind)
| Guard | Constant rebound | Observed refusal `feature` |
|---|---|---|
| absolute inflated-bytes cap | `pdf_object_streams.MAX_INFLATED_STREAM_BYTES=4` | `inflated bytes cap` |
| inflate-ratio | `MAX_INFLATE_RATIO=0` | `inflate ratio` |
| `/Prev` depth | `MAX_PREV_DEPTH=0` | `xref /Prev depth` |
| object-stream count | `MAX_OBJECT_STREAMS=0` | `object stream count` |
| `/N` per object stream | `MAX_OBJSTM_OBJECTS=1` | `object stream` (`/N over ...`) |
| shared document budget | `sheet_reader.MAX_TOTAL_DECODED_BYTES=4` | `decoded bytes budget` |

## Self-checks (explicit cwd)

- **[OBSERVED] `cd services/api && python -m ruff check .`** → `All checks passed!` (exit 0).
- **[OBSERVED] sheet suites via my 3.11 shim copy** (API_ROOT = this worktree's `services/api`;
  runs `test_pdf_object_streams.py` + `test_sheet_reader.py` + `test_sheet_reader_split_equivalence.py`)
  → `75 passed`. The new file alone → `29 passed`. The split-equivalence overall-digest golden is
  among the 75 (byte-identical: `_preview` is a no-op ≤ 64 chars; classic path + `charge_decoded`
  signature unchanged; `decoded_bytes=` defaults to 0).
- **[BLOCKED, CI-authoritative] `cd services/api && python -m pytest tests/drawings/... -q`** →
  `SyntaxError` collecting `app/documents/units.py:276` (PEP 695 `def _match_unit[UnitT: enum.Enum]`
  under local Python 3.11). Documented harness; CI on 3.12 runs it. Recipe for harvest: run the
  three-file pytest from `services/api` on Python 3.12, or the shim copy on 3.11.
- **[OBSERVED] `cd <repo root> && python tools/modularity_check.py --check`** → exit 0; no warning
  for any drawings module (SLOC: pdf_object_streams 588, sheet_reader 342, sheet_objects 353,
  sheet_interpreter 586 — all < 600).

## Real corpus (AS-5) — fetched to scratch, sha256-verified, run, deleted

All six fetched by their recorded URLs into scratch only, each sha256 MATCHED the note, run through
`read_sheet` TWICE (run1 == run2 for all). Corpus copies deleted after the run; nothing committed.

| # | file (sha256 prefix) | M5-T093 outcome (old) | M5-T103 outcome (new) |
|---|---|---|---|
| 1 | VA HVAC 1 `daf0fbb3…` | REFUSAL `cross-reference stream` (strict, at xref) | xref+objstm RESOLVED (1352 objects); refuses at content `decode parameters` |
| 2 | VA HVAC 2 `f8384c4d…` | REFUSAL `cross-reference stream` | RESOLVED; refuses at content `decode parameters` |
| 3 | VA Dwg Rqmts `2288a94e…` | REFUSAL `cross-reference stream` | RESOLVED (incl. `/Prev` + multi-`/Index`); refuses at content `<<` (marked-content dict) |
| 4 | HAER NY-18 `8f80f6d2…` | REFUSAL `cross-reference stream` | RESOLVED (incl. `/Prev`); refuses at content `<<` (marked-content dict) |
| 5 | HABS OR-167 `d0355d6f…` | REFUSAL `cross-reference stream` | RESOLVED; refuses at content `<<` (marked-content dict) |
| 6 | HABS WA-235 `8756f638…` | REFUSAL `cross-reference stream` | RESOLVED; refuses at content `<<` (marked-content dict) |

**Headline (honest, no claim beyond observed):** P1 works — the cross-reference-stream +
object-stream blocker (M5-T093, DB-055 (g)/(h)) is removed on ALL SIX real files; each now
resolves its full object graph and page tree and advances to a subsequent, correctly-typed
content-level limit. No corpus file yet FULLY reads (produces linework): items 1-2 hit a content
stream with `/FlateDecode` + a PNG predictor (`/DecodeParms`), which the profile's content decoder
deliberately still refuses — the exact case the read-only 62-case golden `refuse_decode_parms`
freezes as a refusal, so widening it is out of PKT-K scope; items 3-6 hit a marked-content operator
with an inline `<<…>>` property-list dict in the page content, which the existing content-stream
scanner does not handle. `sh` shading and inline images (DB-055 (g)) stay declared typed refusals
(unimplemented) and sit BEHIND these limits. No one may tell the owner that real architect PDFs can
be fully read yet.

## Deviations
- `/Extends` object-stream chains are IGNORED (not refused): the xref type-2 entry names the direct
  container objstm and each objstm header self-describes its own objects (guarded by the
  header-number == requested-number identity check), so `/Extends` never affects random-access
  resolution. This lets item 3 advance past its `/Extends` objstm.
- The mandatory-guard decode primitives (`inflate_guarded` / `apply_predictor` / PNG unfilter) live
  in `sheet_objects` (the profile's decode module), composed by the resolver, to keep every
  production module < 600 SLOC (AS-4) while preserving the resolver's patchable mutation surface.

## DISCOVERIES (route to backlog; not fixed in-packet)
- **D1 (content P2, HIGH):** real architect content streams use `/FlateDecode` + PNG predictor on
  page/form CONTENT (`/DecodeParms`), which the profile content decoder refuses (frozen by the
  `refuse_decode_parms` golden). Blocks items 1-2 (the positive vector fixtures) after P1. A P2
  packet that grants the golden path should decode content-stream predictors (the shared
  `apply_predictor` already exists).
- **D2 (content P2, HIGH):** marked-content operators (`BDC`/`DP`) with an inline `<<…>>`
  property-list dict appear in page content of items 3-6 (e.g. `/Suspect <</Conf 0>>BDC`); the
  content-stream scanner refuses at `<<`. This masks the scan-only classification (DB-055 (l)/P3) on
  real scanned files. A P2 packet should skip a balanced inline dict operand.
- **D3 (P3 refinement):** because of D2, real scanned files (items 4-6) refuse structurally, not as
  `scan only`; DB-055 (l) scan-only is implemented and tested synthetically but is reached on real
  files only once D2 lands.

END-OF-REPORT
