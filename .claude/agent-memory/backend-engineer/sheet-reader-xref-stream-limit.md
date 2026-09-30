---
name: sheet-reader-xref-stream-limit
description: The architect sheet reader refuses all real-world modern PDFs at the xref stage (cross-reference streams + object streams unsupported)
metadata:
  type: project
---

`app/drawings/sheet_reader.py` `read_sheet` reuses `app/documents/extraction/pdf_xref.py`
`read_object_table` READ-ONLY, which reads exactly ONE classic `xref` section and refuses PDF
1.5+ cross-reference **streams** (`/Type /XRef`), `/Prev` chains, and `/XRefStm`. So any file whose
last `startxref` points at an integer object header instead of the `xref` keyword refuses at the
object-table stage with `SheetRefusal(feature='cross-reference stream', origin=strict_reader,
reject_code=unsupported_pdf_feature)` — **before** any catalog / page tree / content / `sh` / inline
image is examined.

**Why it matters:** real modern architect PDFs (Acrobat / PDFMaker / Paper-Capture output) default
to xref streams AND pack the page tree into compressed object streams (`/ObjStm`) — the `/Type
/Pages` nodes exist ONLY inside `/ObjStm`, so xref-stream support alone is insufficient; object-
stream decoding is an inseparable co-requisite. Verified 2026-09-24 (M5-T093): 6/6 public corpus
files (VA CAD vector + LoC scanned, three toolchains) all refuse this way, deterministically.

**How to apply:** the sheet reader currently reads ZERO real files. The next reader packet (C1) must
add xref-stream + object-stream parsing to the object-table path FIRST (re-run the M5-T093 corpus by
sha256 as the harness). `sh` shading (corpus item 3) and inline images `BI/ID/EI` (items 2, 4) are
real reader gaps too but LATENT — unreachable until the xref blocker is removed. DB-055 (b) requires
the `sheet_reader.py` modularity split before that growth. See [[socrata-pluto-gotchas]] for the
connector-gotcha style; corpus provenance in `docs/research/architect-corpus-reader-trial-2026-09.md`.
