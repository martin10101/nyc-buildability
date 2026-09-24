# M5-T084 producer report — D-087 research (DXF reference + drawing corpus + 3D deps pre-screen)

- **Task:** M5-T084 (research/docs-only). Producer: official-source-researcher.
- **Worktree:** `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t084` — branch `task/M5-T084-d087-research`,
  contract HEAD `f9bfd54d37c981e938185e3ae09ea9ad85f415f3` (verified before work).
- **Directive refs:** D-087 R001/R002/R004/R005/R006/R007; D-066-R001.
- **Deliverables (allowed_paths, all replaced):**
  `docs/research/dxf-format-reference-2026-09.md`,
  `docs/research/architect-drawing-corpus-2026-09.md`,
  `docs/research/3d-web-deps-prescreen-2026-09.md`, and this report.
- **Scratch (downloads only, never in repo):** `C:\Users\MLFLL\AppData\Local\Temp\d087-corpus\`
  (drawing PDFs + Autodesk DXF reference PDF) and `…\d087-npm\` (registry/advisory JSON + parse scripts).
- **Retrieval anchor:** 2026-09-24 UTC (npm 07:30:32Z; OSV 07:32:51Z; GitHub advisories ~07:33Z;
  Autodesk/LoC/VA fetches ~07:34–07:51Z).

---

## Per-acceptance-scenario evidence

### AS-1 (DXF facts) — [OBSERVED]
Every group code / version code / header variable in the DXF note cites an exact Autodesk source with
`retrieved_at`. Primary source downloaded and hashed: **AutoCAD 2005 DXF Reference**,
`https://images.autodesk.com/adsk/files/acad_dxf.pdf`, sha256
`6c56324c32a86aae409f718ae50d6687c84f5043469a26fc6a5278b6cd3cba9d` (1,756,239 bytes), text extracted
with PyMuPDF (`cwd=C:\Users\MLFLL\AppData\Local\Temp\d087-corpus`). Version-sensitive facts taken from
the **current (2026) Autodesk DXF HEADER page** and bracketed against the 2016/2017 pages.
- **Minimal R12 vs R2000:** stated. R12 (`$ACADVER=AC1009`) needs no handles, no CLASSES, no OBJECTS
  section — sourced to [A2005] p.184: handles "existed since AutoCAD Release 10, and **as of AutoCAD
  Release 13, handles are always enabled**." R2000/AC1015 (R13+) requires per-object group-5 handles
  (`$HANDSEED`), a CLASSES section ("All fields are required", [A2005] p.31–32), and an OBJECTS section.
  The exact minimal OBJECTS root-dictionary contents are flagged `[NEEDS G1 RE-VERIFICATION]` (not read
  verbatim; not blocking for the recommended R12 writer).
- **US survey foot unit code:** **YES — `$INSUNITS = 21` = "US Survey Feet"** (22/23/24 = survey
  inch/yard/mile), **introduced in the AutoCAD 2017 DXF reference** (verbatim present in the 2017 page,
  absent in 2016 which stops at 20 = Parsecs). Load-bearing for EPSG:2263 (US survey feet).
- Full group-code tables recorded for LINE, LWPOLYLINE, POLYLINE/VERTEX/SEQEND, 3DFACE, TEXT, LAYER,
  LTYPE, plus $ACADVER string→release map and $INSUNITS 0–24, each with page/URL anchors.

### AS-2 (corpus) — [OBSERVED]
**6 real public-domain files** downloaded to scratch, each with URL + publisher + reuse basis + size +
sheet types + vector/scanned + producing app + **sha256**; **nothing entered the repository**; total
≈ 14.3 MB drawings (16 MB incl. the DXF-reference PDF) < 50 MB cap. Balance = 3 **vector** (VA Standard
Details Div 23 HVAC parts 1&2, CAD-plotted, 88+94 sheets, `/Producer` "Acrobat PDFMaker … for AutoCAD",
24,595 / 13,795 vector paths, 0 images; + VA drawing-requirements) and 3 **scanned+OCR** (HABS/HAER data
pages: Brooklyn Bridge HAER NY-18, Frantz-Dunn House HABS OR-167, Rothschild House HABS WA-235;
`/Producer` "Paper Capture Plug-in"). Classification method + raw byte inspection are reproducible
(`inspect_pdfs.py`, `cwd=…\d087-corpus`). Copyrighted material **EXCLUDED explicitly** (private sealed
surveys, commercial CAD-block libraries, the NCS standard document itself). Channel fact recorded: LoC
HABS/HAER measured-drawing **sheets** are raster **TIFF**, not PDF — only the data pages are PDF.
sha256 table (verbatim in the corpus note):
```
va_div23.pdf         6490778  daf0fbb3ed5ec3e7f66eabd671255d9111ed80884ed0fb7d04c75d67c7e6b7f4
va_div23_2.pdf       6804710  f8384c4d874db25e09c6a2561971078d105b4462e2cfb417c343f2f53c67c6de
va_dwgreq.pdf         885378  2288a94ec31c3a0b48815d3d82d3030edee581d73a38aeeff1c23bc7bd3bb527
haer_ny1234_data.pdf  148470  8f80f6d203b9d4a9c77360b500f88afd027ae4224e4b7d3cedcf20799cc552c2
habs_or0463_data.pdf   15158  d0355d6f49a27fdaf8e463e82b67c1eac315d48a6c606d7c1089789a9faf75b5
habs_wa0717_data.pdf   11800  8756f638629efb971bc082bf0e5ba20fde8a0fe1d11aaa62ee2d3785e5bfaeaf
```

### AS-3 (deps pre-screen) — [OBSERVED]
For each package, the newest **≥ 7-day-old (604800 s)** stable version, license, install scripts,
direct-dep count, and advisory status with registry URL. Cutoff = publish ≤ 2026-09-17T07:30:32Z.
- **three → 0.186.0** (latest; 15.50 d) — MIT, **0 deps**, no install scripts, 2 maintainers,
  advisory-free (OSV empty; GitHub GHSAs affect < 0.137.0 / < 0.125.0 only; `affects=three@0.186.0` = 0).
- **@react-three/fiber → 9.7.0** (latest **9.8.0 is 1.49 d → FAILS gate**) — MIT, 10 direct deps, no
  install scripts, 8 maintainers, advisory-free.
- **@react-three/drei → 10.7.8** (latest; 49.69 d) — MIT, **21 direct deps** (largest fan-out), no
  install scripts, 6 maintainers, advisory-free.
Transitive counts deferred to the G5 admission packet (needs a committed lockfile; whole-tree age +
`npm audit` is the real gate). Positive control: OSV returned 7 GHSAs for `lodash@4.17.11` (endpoint
proven live). No package/lockfile/source change made.

### AS-4 (scope) — [OBSERVED]
Docs only — exactly the four allowed_paths changed (three research notes + this report). No package,
lockfile, source, or rule change. `git status` shows only the four files (below).

---

## Commands run (evidence, cwd noted)
- `cwd=C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t084`: `git rev-parse HEAD` → contract HEAD confirmed.
- `cwd=…\d087-npm`: `curl registry.npmjs.org/{three,@react-three/fiber,@react-three/drei}` (HTTP 200);
  `python parse.py` (versions/ages/licenses/scripts); `curl api.osv.dev/v1/querybatch` → `{}` ×3;
  OSV positive control (lodash → 7 vulns); `curl api.github.com/advisories?...` per package.
- `cwd=…\d087-corpus`: `curl images.autodesk.com/adsk/files/acad_dxf.pdf` (HTTP 200, hashed);
  PyMuPDF extraction scripts; LoC `?fo=json` item/search fetches; `curl cfm.va.gov/til/sDetail/...`
  + `bim/DwgDelivRqmts.pdf` (HTTP 200); `python inspect_pdfs.py` (classification + sha256).

## Source list (primary/official)
- Autodesk AutoCAD 2005 DXF Reference PDF (images.autodesk.com); current DXF HEADER pages
  (help.autodesk.com/cloudhelp/{2016,2017,2026}/ENU/AutoCAD-DXF/…GUID-A85E8E67…).
- npm registry JSON (registry.npmjs.org). OSV.dev querybatch. GitHub Advisory Database REST
  (api.github.com/advisories).
- Library of Congress HABS/HAER item + search JSON (loc.gov `?fo=json`; tile.loc.gov masters);
  VA CFM Technical Information Library (cfm.va.gov/til).

## Blocked / could-not-verify (honest)
- [BLOCKED] Autodesk support article "Drawing format version codes" (autodesk.com/support/technical/…)
  → **HTTP 403** to curl+browser-UA; $ACADVER map instead sourced from [A2005] + the 2026 DXF HEADER
  page (documented fallback).
- [BLOCKED] VA TIL index now redirects to a JS portal (`vatilms.va.gov/…/PG-18-4`) with no static links
  to a non-browser fetch; only the legacy Division-23 direct PDFs resolved. Vector corpus can be
  broadened (architectural/site divisions) by a browser-capable capture later — not blocking (items 1–2
  already give real multi-sheet vector CAD drawings).
- [NEEDS G1 RE-VERIFICATION] exact minimal R2000+ OBJECTS root-dictionary contents (see DXF note §6);
  not blocking for the recommended R12 writer.
- Transitive dep trees / whole-tree advisory audit deferred to the admission packet (§4 of deps note).

## Discoveries (D-069 — for the orchestrator to route; NOT fixed here)
- **$INSUNITS = 21 (US Survey Feet)** exists since the AutoCAD 2017 DXF reference — the DXF writer
  (M5-T081) and any CAD export should set it so files self-declare survey feet (EPSG:2263), and a
  future reader must not read `2` (international Feet) as survey feet. Candidate backlog note.
- LoC HABS/HAER measured-drawing **sheets are raster TIFF, not PDF** — the phase-C PDF reader gets its
  vector fixtures from CAD-plotted agency sets (VA), and its scan-only fixtures from HABS/HAER data
  pages; a scanned-*drawing* PDF fixture would need a cloud capture that wraps a sheet TIFF.

END-OF-REPORT
