---
name: architect-pdf-reader-layers
description: Real architect PDF (drawings) reader — how the app/drawings sheet profile layers work, what the strict reader refuses, and the content-level limits real files hit after PDF 1.5+ xref/objstm support
metadata:
  type: project
---

The architect drawing-sheet reader lives in `services/api/app/drawings/` and REUSES the
strict PDF reader `app/documents/extraction/` READ-ONLY (its second consumer is the survey
pipeline — never widen it).

**Why:** the strict `read_object_table` implements exactly one classic `xref` section and
refuses PDF 1.5+ cross-reference STREAMS, `/Prev`, `/XRefStm`, `/Encrypt` by name. Every real
architect PDF (Acrobat PDFMaker / Adobe) uses an xref STREAM + object streams, so the strict
reader reads none of them.

**How to apply (module map, verified 2026-09-24 at M5-T103):**
- `sheet_reader.py` = facade (`read_sheet`, page-tree walk, profile bounds, backstop).
- `sheet_objects.py` = object graph + stream decode + decoded-bytes budget + shared decode
  primitives `inflate_guarded` / `apply_predictor` / `_png_unfilter` (M5-T103 added these here,
  not in the resolver, to keep every module < 600 SLOC).
- `sheet_interpreter.py` = content-operator interpreter (`_StreamRun`).
- `pdf_object_streams.py` = the PDF 1.5+ resolver (M5-T103): `/Type /XRef` (`/W`,`/Index`,
  types 0/1/2, `/Prev`+cycle guard), `/Type /ObjStm` (`/N`,`/First`), hybrid `/XRefStm`. Wired
  as a `sheet_reader` FALLBACK that fires only when the strict reader refuses a
  cross-reference-stream-family feature, so classic files take the old path byte-for-byte.

**Hard constraints that bit at M5-T103 (still true):**
- The 62-case split-equivalence golden (`test_sheet_reader_split_equivalence.py`, READ-ONLY)
  freezes content behavior: `refuse_decode_parms` freezes a content stream with `/FlateDecode`
  + PNG predictor (`/DecodeParms`) as a REFUSAL. So content-stream predictors CANNOT be
  decoded without a packet that grants the golden path. `_preview` is a no-op ≤ 64 chars, so
  wrapping short names/filters with it keeps every golden byte-identical.
- Real content limits that block full reads AFTER xref/objstm support: (1) content-stream
  `/FlateDecode`+predictor (`/DecodeParms`) — blocks the VA vector fixtures; (2) marked-content
  `BDC`/`DP` with an inline `<<…>>` property-list dict — the content scanner refuses at `<<`
  (blocks the scanned HABS/HAER files, masking the scan-only classification). `sh` shading and
  inline images sit behind these. See DISCOVERY_BACKLOG D-riders on M5-T103.
- `/Extends` object-stream chains can be IGNORED safely (the xref type-2 entry names the direct
  container objstm; each objstm header self-describes its objects; the header-number identity
  check guards correctness).
- Local Python 3.11 cannot import the sheet suites (PEP 695 in `app/documents/units.py`); use
  the outside-repo bare-package 3.11 shim (see [[env-producer-sandbox-no-exec]]) or CI on 3.12.
