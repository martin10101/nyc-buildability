# Architect-drawing corpus trial of the sheet reader (M5-T093, D-087 PDF-1b)

- **Task:** M5-T093 (research-only; D-087 wave 3). Producer: backend-engineer. Docs only; **no
  reader change** (the DB-055 (g)+(h) precondition).
- **Purpose:** discharge the F1/F2 riders that the M5-T083 DCV bound onto the next reader packet
  (`project-control/reports/M5-T083-DCV.md`, findings F1/F2; `docs/DISCOVERY_BACKLOG.md` DB-055
  (g)+(h)). The accepted sheet reader (`services/api/app/drawings/sheet_reader.py` `read_sheet`,
  M5-T083) was proven only on synthetic PDFs. Before anyone tells the owner that real architect
  PDFs can be read, the reader must be tried on the real public drawings recorded in
  `docs/research/architect-drawing-corpus-2026-09.md` (items 1-6).
- **Method:** each item downloaded by `curl` from its recorded URL into the session scratchpad
  only (never committed — licensing, corpus note §4); sha256 compared with the note; per-file
  facts established by an **independent byte scan that does not use the reader** (raw byte walk +
  stdlib-zlib inflation of every FlateDecode stream; page count and producer corroborated with
  PyMuPDF/`fitz`, which is independent of the sheet reader); then `read_sheet` run on each file
  from the **worktree's** `services/api` under the accepted bare-package 3.11 shim (so the
  3.12-only `app/documents/units.py` is never imported), **twice**, confirming identical output.
- **Headline result:** **the reader reads none of the six real files.** All six are refused at the
  cross-reference stage with the same typed refusal (`feature='cross-reference stream'`), before
  any page content is interpreted. DB-055 (g)'s cross-reference-stream limit is the single, real,
  blocking defect for real files; the `sh`-shading and inline-image limits are present in the
  corpus but **latent** (never reached, because the xref refusal fires first).
- **Scope honesty (binding):** these are 6 specific public files. Nothing here is generalised to
  "architect PDFs in general." What is notable is only that the blocker recurs across **both**
  drawing classes and **three independent producing toolchains** (see §4).

---

## 1. Provenance (AS-1) — all six fetched, all six sha256 MATCH

Downloaded 2026-09-24 UTC with `curl 8.11.0` (a browser-style User-Agent). HTTP status, byte
count, and sha256 recorded per file and compared against
`docs/research/architect-drawing-corpus-2026-09.md` §2. No fetch failed; no sha256 mismatched.

| # | File / record | Source URL | HTTP | Bytes (= note) | sha256 vs note | retrieved_at (UTC) |
|---|---|---|---|---|---|---|
| 1 | VA Standard Details Div 23 HVAC (1 of 2) | `https://www.cfm.va.gov/til/sDetail/sDetail-Div23-PDF-1.pdf` | 200 | 6,490,778 ✓ | `daf0fbb3…c7e6b7f4` **MATCH** | 2026-09-24T10:47:29Z |
| 2 | VA Standard Details Div 23 HVAC (2 of 2) | `https://www.cfm.va.gov/til/sDetail/sDetail-Div23-PDF-2.pdf` | 200 | 6,804,710 ✓ | `f8384c4d…f2f53c67c6de` **MATCH** | 2026-09-24T10:47:46Z |
| 3 | VA Drawing Deliverable Requirements | `https://www.cfm.va.gov/til/bim/DwgDelivRqmts.pdf` | 200 | 885,378 ✓ | `2288a94e…7bd3bb527` **MATCH** | 2026-09-24T10:48:17Z |
| 4 | Brooklyn Bridge — HAER NY-18 (data pages) | `https://tile.loc.gov/storage-services/master/pnp/habshaer/ny/ny1200/ny1234/data/ny1234data.pdf` | 200 | 148,470 ✓ | `8f80f6d2…9cc552c2` **MATCH** | 2026-09-24T10:48:56Z |
| 5 | Frantz-Dunn House — HABS OR-167 (data pages) | `https://tile.loc.gov/storage-services/master/pnp/habshaer/or/or0400/or0463/data/or0463data.pdf` | 200 | 15,158 ✓ | `d0355d6f…a9faf75b5` **MATCH** | 2026-09-24T10:49:13Z |
| 6 | Rothschild House — HABS WA-235 (data pages) | `https://tile.loc.gov/storage-services/master/pnp/habshaer/wa/wa0700/wa0717/data/wa0717data.pdf` | 200 | 11,800 ✓ | `8756f638…3785e5bfaeaf` **MATCH** | 2026-09-24T10:49:22Z |

Full 64-hex digests are in `docs/research/architect-drawing-corpus-2026-09.md` §2; each downloaded
byte stream reproduced its note digest exactly (`sha256sum` over the scratch copies). Corpus files
were deleted after the trial and **nothing from the corpus is committed**.

---

## 2. Per-file facts (AS-2) — independent byte scan (not the reader)

Structural facts from a raw byte walk; content-stream operators (`sh`, `BI`/`ID`/`EI`) and any
keys packed inside compressed object streams from inflating every FlateDecode stream with stdlib
`zlib`; page count / producer corroborated with `fitz` (agreed on all six). The **xref kind** is
decided the same way the strict reader decides it: the byte at the last `startxref` offset — a
literal `xref` keyword (classic table) vs an integer object header (a PDF 1.5+ cross-reference
stream).

| # | PDF ver | Producing app (`/Producer` → `/Creator`) | Pages | xref | Object streams (`/ObjStm`) | Shading | Inline image (BI·ID·EI) | Encryption |
|---|---|---|---|---|---|---|---|---|
| 1 | 1.7 | Acrobat PDFMaker 9.0 **for AutoCAD** | 88 | **STREAM** (`/Type /XRef`) | yes (10) | no | no | no |
| 2 | 1.7 | Acrobat PDFMaker 9.0 for AutoCAD | 94 | **STREAM** | yes (76) | no | **yes** | no |
| 3 | 1.5 | Adobe PDF Library 11.0 → Acrobat PDFMaker 11 for Word | 14 | **STREAM** | yes (32) | **yes** (`/Shading` + `sh` op) | no | no |
| 4 | 1.6 | Canon iR-ADV C5840 scan → Adobe Acrobat Pro 23 **Paper Capture** | 8 | **STREAM** | yes (13) | no | **yes** | no |
| 5 | 1.6 | Adobe Acrobat Pro 11.0.3 Paper Capture → I.R.I.S. | 1 | **STREAM** | yes (3) | no | no | no |
| 6 | 1.6 | Adobe Acrobat Pro 11.0.3 Paper Capture → I.R.I.S. | 1 | **STREAM** | yes (3) | no | no | no |

Notes:
- **Every file uses a cross-reference stream AND object streams.** The page-tree nodes
  (`/Type /Pages`, and hence the page objects) live **only inside compressed object streams** in
  every file sampled (item1: 0 in raw bytes / 19 inside `/ObjStm`; item3: 0 / 3; item5: 0 / 1).
  The catalog (`/Type /Catalog`) is a regular object, but resolving `/Root → /Pages → page →
  /Contents` is impossible without decoding object streams.
- Item 4's producer chain is richer than the note recorded: the page was first scanned on a **Canon
  iR-ADV C5840** (`Adobe PSL 1.3e for Canon`, a UTF-16 metadata string) and then re-produced through
  **Adobe Acrobat Pro (32-bit) 23 Paper Capture** (OCR). Both `/Producer` values are present; the
  note's "Acrobat 23 Paper Capture" is confirmed. No contradiction — the scan surfaced the origin
  device too.
- Item 2 (vector) and item 4 (scanned) each contain a genuine ordered `BI … ID … EI` inline-image
  sequence in a stream; item 3 uses `/Shading` + the `sh` operator. **None of these is reached by
  the reader** (see §3).
- Encryption is absent from all six.

---

## 3. Reader outcome (AS-3) — `read_sheet`, run twice, identical each time

Run from the worktree's `services/api` under the bare-package shim; `run1 == run2` was `True` for
every file (frozen dataclasses; deterministic). **All six returned the same typed refusal value**
(never raised):

| # | `read_sheet` result | origin | reject_code | feature | reproducible |
|---|---|---|---|---|---|
| 1 | REFUSAL | strict_reader | `unsupported_pdf_feature` | `cross-reference stream` | run1 == run2 ✓ |
| 2 | REFUSAL | strict_reader | `unsupported_pdf_feature` | `cross-reference stream` | ✓ |
| 3 | REFUSAL | strict_reader | `unsupported_pdf_feature` | `cross-reference stream` | ✓ |
| 4 | REFUSAL | strict_reader | `unsupported_pdf_feature` | `cross-reference stream` | ✓ |
| 5 | REFUSAL | strict_reader | `unsupported_pdf_feature` | `cross-reference stream` | ✓ |
| 6 | REFUSAL | strict_reader | `unsupported_pdf_feature` | `cross-reference stream` | ✓ |

The refusal `detail` (verbatim, item 1; the others differ only in the byte offset):

> `startxref offset 6488119 begins with an integer object header (a PDF 1.5+ cross-reference
> stream); only classic 'xref' tables are in the supported subset`

This is the strict reader's `read_object_table` refusing at the very first stage
(`app/documents/extraction/pdf_xref.py`), which the sheet profile reuses read-only and wraps via
`_wrap_strict`. Because the object table never materialises, **no catalog, page tree, page content,
`sh` operator, inline image, image XObject, or curve is ever examined** on any of these files.

---

## 4. Which DB-055 (g) limits actually block these real files

DB-055 (g) named two suspected blockers — cross-reference **streams** (PDF 1.5+) refused by the
reused strict reader, and the `sh` shading operator — and flagged the risk that the two positive
vector items (Acrobat PDFMaker 9.0 for AutoCAD) might use xref streams, "in which case the sheet
reader reads NEITHER."

- **Cross-reference streams — REAL, blocks 6 / 6.** This is the single, decisive blocker. Every
  file, in **both** classes and across **three independent toolchains** — Acrobat PDFMaker 9.0 *for
  AutoCAD* (items 1-2, born-digital CAD vector), Adobe PDF Library 11 / PDFMaker 11 for Word (item
  3, mixed), and Acrobat Paper Capture / Canon (items 4-6, scanned+OCR) — writes a PDF 1.5+
  cross-reference stream. Modern Acrobat/PDFMaker output defaults to it; it is not incidental to one
  producer. The DCV's worst case is confirmed: the reader reads **neither** positive vector fixture.
- **Object streams (`/ObjStm`) — REAL co-requisite, 6 / 6.** Not separately called out in (g), but
  inseparable from the above: the page tree lives only inside object streams here, so xref-stream
  support alone is insufficient — the reader must also decode object streams to resolve `/Pages`.
- **`sh` shading operator — present but LATENT (item 3 only).** Item 3 carries `/Shading` and a real
  `sh` operator; the reader has no `sh` handler (it is not in `_IGNORED`), so it *would* refuse
  "unsupported operator". But this is **never reached** — item 3 is refused at the xref stage first.
- **Inline images (`BI`/`ID`/`EI`) — present but LATENT (items 2 and 4).** The reader has no `BI`
  handler, so an inline image *would* refuse the whole document as "unsupported operator". Also
  never reached on these files.
- **Encryption — not a blocker for this corpus** (absent in all six).

So for the corpus as it stands, exactly **one** limit blocks — the cross-reference stream (with
object streams as its inseparable co-requisite). The shading and inline-image limits are real
reader gaps that these files *contain* but that only become reachable once the xref/object-stream
blocker is removed.

DB-055 (h) is discharged with a **negative** result: the corpus items (1-6, by sha256, with (g)
checked first) were run through `read_sheet`; the reader currently reads **zero** real files. **No
one may tell the owner that real architect PDFs can be read.**

---

## 5. Prioritised scope for the next reader packet (C1)

In priority order, derived only from these six files:

1. **P1 — PDF 1.5+ cross-reference streams AND object streams (blocking, 6/6).** Without both,
   `read_sheet` reads no real file in the corpus. This is a substantial extension to the reused
   strict `read_object_table`, which today reads exactly one classic `xref` section and never
   follows `/Prev` or `/XRefStm`. C1 must add: locate and parse an xref *stream* (`/Type /XRef`,
   the `/W` field widths, `/Index`, and `/Prev` chaining) and decode object streams (`/Type
   /ObjStm`, `/N`, `/First`) to resolve `/Root`, `/Pages`, the page nodes and `/Contents`. The same
   fail-closed bounds the profile already applies (stream-size, decoded-byte, hop caps) must extend
   to the new indirections. **Re-run this exact corpus by sha256 as the C1 acceptance harness.**
2. **P2 — the two content-level limits the corpus exposes, reachable only after P1.**
   - **Inline images (`BI`/`ID`/`EI`)** — items 2 (vector) and 4 (scanned) contain them; with P1 in
     place they would otherwise turn into an "unsupported operator" refusal of the whole document.
     C1 should decide: a typed inline-image refusal, or count-and-disclose (mirroring the existing
     image-XObject treatment: counted, never decoded).
   - **`sh` shading operator** — item 3 uses it; needs either a typed shading refusal or an explicit
     ignore. Vector items 1-2 use no shading, so this is second to inline images for the linework
     goal.
3. **P3 — make the scan-only class refuse for the RIGHT reason.** Items 4-6 are the intended
   scan-only / OCR-advisory class (the phased plan has C1 refuse scan-only). Today they refuse
   incidentally at the xref stage, which *masks* their true nature. After P1, C1 must classify them
   as scan-only (one image XObject per page, no vector geometry) and refuse with a **scan-only**
   typed reason, not a structural one — so the class split the corpus note §5 called for is real in
   the reader, not an accident of the xref format.
4. **Deprioritise encryption** — absent from this corpus; add only if a later corpus needs it.

**Sequencing note for C1:** DB-055 (b) requires `sheet_reader.py` to be split (it is in the
JUSTIFY modularity band) **before** any further growth, in a packet that grants the third module
path. P1 adds real code to the reader/object-table path, so the split precedes P1's implementation.

---

## 6. Evidence pointers (reproducible; artefacts were in scratch only, not committed)

- Independent byte scan: `scan.py` (stdlib byte walk + zlib inflation + `fitz` corroboration) over
  `item1.pdf … item6.pdf`; object-location check `where_objs.py`.
- Reader trial: `run_reader.py` (bare-package 3.11 shim; `API_ROOT` = the M5-T093 worktree's
  `services/api`; each file read twice). A copy of the accepted shim technique
  (`run_sheet_tests_ctl24.py`) was used unmodified in spirit; the original was not edited.
- All downloads, scripts, and outputs lived under
  `…/scratchpad/m5t093/` and the drawings were deleted at the end of the trial. The reader and every
  `app/**` file are byte-untouched (this task changed exactly the two allowed doc paths).
