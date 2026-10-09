# Architect-drawing PDF corpus shortlist (M5-T084, D-087)

- **Task:** M5-T084 (research-only; D-087 wave 1). Producer: official-source-researcher.
- **Purpose:** feed the PROPOSAL_EDITOR phase-C PDF reader (M5-T083 `app/drawings/sheet_reader.py`
  and the strict PDF reader in `app/documents/extraction/*`). The phased plan requires **real
  architect files to define the supported-drawing classes BEFORE the reader is widened** ("supported
  drawing classes are defined from real files, not invented" — `docs/PROPOSAL_EDITOR_PHASED_PLAN.md`
  phase C). Class assignment / evidentiary weight stays with a human; format ≠ class
  (`docs/SURVEY_DOCUMENT_FORMAT_POLICY.md`).
- **Retrieval anchor:** all downloads **2026-09-24 UTC**.
- **Thin-client rule honored:** every file below was downloaded to a scratch temp directory
  (`C:\Users\MLFLL\AppData\Local\Temp\d087-corpus\`), **never into the repository**. Total corpus
  ≈ 14.3 MB of drawings (16 MB incl. the DXF-reference PDF), well under the 50 MB cap. This note
  records the URL + sha256 + size so a later capture task can re-fetch identical bytes into cloud
  storage; the repo carries only this note.
- **Licensing rule honored:** every candidate is a **U.S. federal government work → public domain
  under 17 U.S.C. §105** (no copyright classification needed). No copyrighted drawing is proposed as a
  fixture; see §4 for what is explicitly EXCLUDED.

---

## 0. What "real architect drawings" look like in public sources (the class split)

Two genuinely different PDF classes exist in public federal sources, and the reader must handle both:

- **Born-digital vector PDFs** — CAD plotted straight to PDF; the page carries **vector path operators
  and no page-image** (`/Producer` reveals the CAD toolchain). These yield extractable linework. The
  best public example is the **VA Standard Details** (produced by "Acrobat PDFMaker … for AutoCAD").
- **Scanned PDFs** — a raster page image (one image XObject per page) usually with an **OCR text
  layer** (`/Producer` contains "Paper Capture Plug-in"). No vector geometry exists; text is OCR and
  advisory only. The **HABS/HAER "data pages"** are this class. (This is exactly the survey policy's
  "scanned PDF → raster-only, OCR-advisory" verdict.)

**Important channel fact:** the Library of Congress HABS/HAER/HALS **measured-drawing sheets**
themselves (the plans/elevations/sections) are delivered as **raster TIFF**, *not* PDF (verified in
the item JSON — see §3). Only the written data pages are PDF. So for a *PDF* reader, HABS/HAER
supplies the **scanned class**; the **vector class** comes from CAD-plotted agency sets like the VA
standard details.

---

## 1. Classification method (reproducible)

Each downloaded PDF was inspected with PyMuPDF (`fitz`) in the scratch dir:
`page_count`; `/Producer` + `/Creator` from `doc.metadata`; per-page **vector path count**
(`len(page.get_drawings())`) vs **image XObject count** (`len(page.get_images())`) vs OCR/text-layer
character count (`page.get_text()`), sampled over the first up-to-8 pages; sha256 over the whole file.
Rule: many paths + no images ⇒ vector; image-per-page + little/no path geometry ⇒ scanned (OCR text
layer noted). Script + raw output are in the scratch dir (`inspect_pdfs.py`).

---

## 2. Starter corpus (6 files — all public domain, downloaded to scratch only)

| # | Name / record | Source URL (retrieved 2026-09-24) | Publisher | Reuse basis | Bytes | Pages | Sheet types | Vector vs scanned | Producing app (`/Producer`,`/Creator`) | sha256 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **VA Standard Details, Div 23 HVAC (1 of 2)** | `https://www.cfm.va.gov/til/sDetail/sDetail-Div23-PDF-1.pdf` | U.S. Dept. of Veterans Affairs, Office of Construction & Facilities Mgmt (TIL, PG-18-4) | Federal work, PD (17 USC §105); format follows U.S. National CAD Standard — see §4 caveat | 6,490,778 | 88 | mechanical/HVAC detail sheets w/ title blocks, notes, dimensioned sections | **VECTOR** (24,595 paths / 0 images in first 8 pp) | Acrobat PDFMaker 9.0 **for AutoCAD** | `daf0fbb3ed5ec3e7f66eabd671255d9111ed80884ed0fb7d04c75d67c7e6b7f4` |
| 2 | **VA Standard Details, Div 23 HVAC (2 of 2)** | `https://www.cfm.va.gov/til/sDetail/sDetail-Div23-PDF-2.pdf` | VA CFM (TIL, PG-18-4) | Federal work, PD (17 USC §105) | 6,804,710 | 94 | more HVAC detail sheets | **VECTOR** (13,795 paths / 2 images in first 8 pp) | Acrobat PDFMaker 9.0 for AutoCAD | `f8384c4d874db25e09c6a2561971078d105b4462e2cfb417c343f2f53c67c6de` |
| 3 | **VA Drawing Deliverable Requirements** | `https://www.cfm.va.gov/til/bim/DwgDelivRqmts.pdf` | VA CFM (TIL, BIM) | Federal work, PD (17 USC §105) | 885,378 | 14 | spec text + sample title-block / sheet-layout figures | **VECTOR+text** (653 paths + 8 images + text layer) | Adobe PDF Library 11.0 / Acrobat PDFMaker 11 for Word | `2288a94ec31c3a0b48815d3d82d3030edee581d73a38aeeff1c23bc7bd3bb527` |
| 4 | **Brooklyn Bridge — HAER NY-18 (data pages)** | `https://tile.loc.gov/storage-services/master/pnp/habshaer/ny/ny1200/ny1234/data/ny1234data.pdf` (item `loc.gov/item/ny1234/`) | National Park Service HAER, via Library of Congress | PD — LoC: "No known restrictions on images made by the U.S. Government" (§4) | 148,470 | 8 | written historical/engineering data (the measured-drawing sheet is separate raster TIFF — §3) | **SCANNED** (8 image XObjects, 3 stray paths) + **OCR text layer** | Adobe Acrobat Pro (32-bit) 23 **Paper Capture Plug-in** | `8f80f6d203b9d4a9c77360b500f88afd027ae4224e4b7d3cedcf20799cc552c2` |
| 5 | **Frantz-Dunn House — HABS OR-167 (data pages)** | `https://tile.loc.gov/storage-services/master/pnp/habshaer/or/or0400/or0463/data/or0463data.pdf` (item `loc.gov/item/or0463/`) | NPS HABS, via LoC | PD — U.S. Government (§4) | 15,158 | 1 | written data page (this record has **12** measured-drawing TIFF sheets — §3) | **SCANNED** (1 image + OCR) | Adobe Acrobat Pro 11.0.3 Paper Capture Plug-in / I.R.I.S. | `d0355d6f49a27fdaf8e463e82b67c1eac315d48a6c606d7c1089789a9faf75b5` |
| 6 | **Rothschild House — HABS WA-235 (data pages)** | `https://tile.loc.gov/storage-services/master/pnp/habshaer/wa/wa0700/wa0717/data/wa0717data.pdf` (item `loc.gov/item/wa0717/`) | NPS HABS, via LoC | PD — U.S. Government (§4) | 11,800 | 1 | written data page (this record has **11** measured-drawing TIFF sheets — §3) | **SCANNED** (1 image + OCR) | Adobe Acrobat Pro 11.0.3 Paper Capture Plug-in / I.R.I.S. | `8756f638629efb971bc082bf0e5ba20fde8a0fe1d11aaa62ee2d3785e5bfaeaf` |

Balance: **3 vector** (items 1–3, the linework-extraction class) and **3 scanned+OCR** (items 4–6, the
typed-refusal / OCR-advisory class). Both classes the phase-C reader must distinguish are represented.

Reference file also downloaded (not a drawing; the DXF spec source for the sibling note):
`autocad_dxf.pdf` — AutoCAD 2005 DXF Reference, 1,756,239 bytes,
sha256 `6c56324c32a86aae409f718ae50d6687c84f5043469a26fc6a5278b6cd3cba9d`, from
`https://images.autodesk.com/adsk/files/acad_dxf.pdf`.

---

## 3. HABS/HAER measured-drawing SHEETS (the actual plans/elevations) — raster TIFF, not PDF

Verified from each item's `?fo=json` resources on 2026-09-24: the "Drawings from Survey" resource
lists each sheet only as `image/tiff` (+ derivative JPEGs), never `application/pdf`. Examples:
- `ny1234` (Brooklyn Bridge): 1 drawing sheet, master `…/ny1234/sheet/00001a.tif` = 1,800,256 bytes.
- `or0463` (Frantz-Dunn House): **12** drawing sheets (TIFF).
- `wa0717` (Rothschild House): **11** drawing sheets (TIFF).

These were **not downloaded** (multi-MB TIFF masters; budget/thin-client) — they are recorded here as
the **raster measured-drawing class**. If wrapped into a PDF for the reader they would behave as
**scan-only** (no vector geometry; any text via OCR only). If a real scanned-*drawing* PDF fixture is
wanted (vs the text data pages), a cloud capture task can pull one sheet's TIFF and wrap it — do that
in the cloud, not on the owner PC.

---

## 4. Licensing classification (per the LICENSING binding)

- **VA Standard Details / VA deliverable requirements (items 1–3):** authored by the U.S. Department
  of Veterans Affairs → **public domain, 17 U.S.C. §105**. **Caveat (record, do not block):** VA has
  adopted the **U.S. National CAD Standard (NCS)**, published by the National Institute of Building
  Sciences, for sheet organization/title blocks; the NCS *standard document* itself is copyrighted,
  but the VA-authored detail content is a federal work. Before any *production* reuse, confirm no
  third-party copyrighted block/detail is embedded. Reuse basis for fixtures = federal PD.
- **HABS/HAER/HALS (items 4–6):** National Park Service documentation on permanent deposit at the
  Library of Congress. LoC rights (captured verbatim from `loc.gov/item/ny1234/?fo=json`):
  *"No known restrictions on images made by the U.S. Government; images copied from other sources may
  be restricted."* → **public domain** for the federally-produced measured drawings and data pages.
  Detail: `https://www.loc.gov/rr/print/res/114_habs.html`.
- **EXCLUDED (copyrighted — never a fixture):** privately-produced architect/engineer sealed drawing
  sets (the survey policy's authoritative "licensed survey" class), commercial CAD-block libraries,
  the NCS standard document itself, and any drawing whose LoC/agency rights statement is not an
  affirmative "no known restrictions / U.S. Government work." None of these were downloaded.

---

## 5. Reader-corpus recommendations (for M5-T083 / phase C)

1. Adopt the two-class split as the reader's first contract: **vector PDF → extract linework**;
   **scanned PDF → typed refusal + OCR-advisory** (C1 refuses scan-only at first, per the phased plan).
   Detect the class the way §1 does: page vector-path count vs image-XObject-per-page, corroborated by
   `/Producer` ("… for AutoCAD" ⇒ vector; "Paper Capture" ⇒ scanned).
2. Use items 1–2 (VA HVAC, real multi-sheet CAD-plotted vector) as the **positive vector fixtures**
   and items 4–6 (HABS/HAER scanned+OCR) as the **scan-only refusal fixtures**. Item 3 is a useful
   mixed born-digital text+figure case.
3. Do **not** treat any extracted geometry as georeferenced — DXF/PDF vector coordinates are page/model
   units with no CRS; alignment to the mapped lot is user-confirmed, never auto-reconciled (phase C2).
4. Keep the real bytes in cloud storage keyed by the sha256 above; the repo test suite should reference
   fixtures by digest, not carry the PDFs (thin-client).

## 6. What I could not verify in this pass
- Per-sheet TIFF byte sizes for or0463/wa0717 (only sheet *counts* read from the item JSON; masters not
  downloaded to respect the budget).
- The VA TIL index now redirects to a JS portal (`vatilms.va.gov/vatilms/reports/PG-18-4`) that exposes
  no static links to a non-browser fetch; only the **legacy** direct paths for Division 23 resolved
  (`sDetail-Div23-PDF-1/2.pdf`). Other divisions' current filenames were not enumerable here — a
  browser-capable capture can broaden the vector corpus (architectural / site / structural divisions)
  later. This does not block: items 1–2 already give real multi-sheet vector CAD drawings.
