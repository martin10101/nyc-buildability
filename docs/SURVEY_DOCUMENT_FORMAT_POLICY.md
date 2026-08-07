# Survey / Official-Document UPLOAD Format Policy (canonical)

**Status:** Canonical decision matrix for the **initial** supported upload formats of the survey /
official-document ingestion pipeline (M2-T015 and downstream). Produced by task M2-T014 (owner directive
2026-07-20, Packet A).
**Companion research:** `docs/research/survey-document-sources-2026-07.md` (source inventory + the
seven-way document-class distinction). **Retrieval anchor for external facts:** 2026-08-05 UTC.

## Governing principles (apply to every verdict)

1. **No format is promised without a proven path.** A format is `supported` only when parsing/handling is
   demonstrably feasible with an admissible, sandboxable, testable toolchain. Anything unproven is
   `convert` (accept only after a proven server-side conversion) or `defer` (not accepted initially, with a
   safe alternative stated). (SR-S3; CLAUDE.md principle 3 — never guess.)
2. **AI does not calculate or decide legal weight.** Formats govern *ingestion/handling*; the document
   **class** (survey vs tax map vs proposed plan, etc.) and its evidentiary weight are governed by the
   research doc §9 and by qualified humans — never inferred from the file format. A DWG and a scanned PDF
   can both be a "licensed survey" or a "proposed plan"; format ≠ class.
3. **Thin-client / cloud-only.** All parsing/conversion/OCR runs on Render workers or another cloud
   sandbox, never on the owner PC (CLAUDE.md principle 14). No heavy local tooling is implied by any
   `supported` verdict here.
4. **Provenance preserved on ingest.** Every upload stores the original bytes immutably with: original
   filename, upload timestamp, declared class, uploader, MIME type (server-sniffed, not trusted from the
   client), and a content digest. Any conversion keeps the **original + converted** artifacts and records
   the tool + version (mirrors the MapPLUTO geometry-normalization no-silent-repair rule, registry §4).
5. **Untrusted-input handling.** All uploads are untrusted: type is verified by content sniffing;
   size/pixel/page bounds enforced; rendering/parsing sandboxed; no macro/script execution. (Security
   review is a required gate.)

## Decision matrix (all seven evaluated separately — SR-S3)

| # | Format | Nature | Initial verdict | Basis / proof or deferral reason |
|---|---|---|---|---|
| 1 | **Born-digital PDF** | PDF authored digitally; may carry a text layer + vector content | **SUPPORTED** | Ubiquitous, open ISO 32000 standard (LC FDD sustainable format). Store bytes + digest; render/inspect server-side; extract text/vector where present. Lowest-risk path; toolchain (e.g. PDF renderers) is standard and sandboxable. Class still assigned by a human. |
| 2 | **Vector PDF** | PDF whose graphics are vector (CAD "print/plot to PDF") | **SUPPORTED** | Same open PDF container as (1); vector geometry is preserved and inspectable. This is the **recommended CAD interchange target** — asking a user to "print to PDF" from DWG/DXF yields a supported artifact without touching the proprietary CAD parser. Geometry-to-CRS interpretation is NOT auto-trusted (no georeferencing implied). |
| 3 | **Scanned PDF** | Raster page(s) wrapped in PDF; image-only, no vector/text | **SUPPORTED (raster-only)** | Common for surveys/microfilm. Accepted and stored; handled as **raster** — no vector geometry exists to extract. Any text is via **OCR** (cloud, sandboxed) and is **advisory only**, never authoritative. Flagged `raster_only=true` so downstream never treats it as machine-readable geometry. |
| 4 | **TIFF** | Raster image (frequent scan/survey deliverable; may be multi-page) | **SUPPORTED (raster)** | Open, well-documented raster format (LC FDD). Accepted and stored; multi-page handled; large/tiled images bounded. Same raster-only, OCR-advisory posture as (3). Recommend normalizing to a PDF/lossless-derivative for display while keeping the original TIFF. |
| 5 | **PNG / JPEG** | Raster image (photos, exported plan images) | **SUPPORTED (raster)** | Open raster formats (LC FDD). Accepted and stored. **JPEG is lossy** — recorded as a data-quality caveat (compression artifacts can degrade fine survey linework/text); prefer PNG/TIFF/PDF for survey-grade scans. Raster-only, OCR-advisory. |
| 6 | **DXF** | Autodesk **Drawing Exchange Format** — ASCII/binary CAD interchange with a **published** Autodesk specification | **CONVERT / DEFER-initial** | DXF is an *interchange* format with a public Autodesk spec and mature open-source readers exist (candidate: `ezdxf`, Python) — so a proven server-side path is *plausible*, but the parser sandboxing + testability + coordinate/units semantics are **not yet proven in this repo**. Initial posture: **do NOT accept DXF as a parsed geometry source yet.** Accept only via a **validated conversion stage** (DXF→vector-PDF/normalized geometry) that passes its own G1, OR direct the user to upload a **vector PDF** (2) meanwhile. Never auto-derive georeferenced boundaries from DXF without proven CRS/units handling. |
| 7 | **Native DWG** | Autodesk proprietary drawing format | **DEFER (not supported initially)** | **Proprietary, no official public specification** (Library of Congress FDD `fdd000445`; Wikipedia `.dwg`, retrieved 2026-08-05). The only full read/write libraries are **licensed**: Autodesk **RealDWG** ("sold under selective licensing terms for use in non-competitive applications") and the **Open Design Alliance** library (commercial ODA membership; ODA's spec is **reverse-engineered**, covering AutoCAD R13→2018). Reverse-engineered open libs (e.g. LibreDWG, GPL) carry copyleft/licensing and maturity concerns. **Licensing + sandboxing + testability are NOT proven** → DWG is **not promised**. **Safe deferral:** require the user to export DWG to **vector PDF (2)** or **DXF via a future validated converter (6)**; DWG bytes MAY be accepted as **store-only** (immutable original, no parsing, class assigned by a human) but the platform derives **nothing** from them until a licensed, sandboxed, tested toolchain is approved (owner decision — licensing = a paid/legal STOP condition). |

## Summary posture

- **Accept + handle now (raster or open-container):** born-digital PDF, vector PDF, scanned PDF, TIFF,
  PNG/JPEG. Vector content is inspected where the open PDF container preserves it; raster is stored + OCR
  advisory only.
- **Do NOT parse yet:** DXF — accept only through a validated conversion stage or steer users to vector PDF.
- **Do NOT promise:** native DWG — proprietary, licensing/sandboxing/testability unproven; store-only at
  most; conversion to PDF/DXF is the safe path. Any DWG-parsing library adoption is a **licensing/legal +
  possible payment STOP condition** requiring owner approval.
- **Recommended universal interchange target:** **vector PDF** — it turns the CAD-format problem into the
  already-supported PDF path without adopting a proprietary parser.

## Cross-references
- Document **classes** & evidentiary weight (survey vs tax map vs proposed plan …):
  `docs/research/survey-document-sources-2026-07.md` §9.
- Where each class can be **retrieved** vs must be **uploaded**: same doc §10; registry rows below.
- Registry: `docs/SOURCE_ACCESS_REGISTRY.md` §11 (this task's additive rows) +
  `docs/research/source-registry-drafts/survey-document-sources.json`.
