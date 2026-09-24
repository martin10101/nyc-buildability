# DXF format reference notes (M5-T084, D-087)

- **Task:** M5-T084 (research-only; D-087 wave 1). Producer: official-source-researcher.
- **Purpose:** de-risk the DXF *writer* (M5-T081 `app/cad/dxf_writer.py`, "AutoCAD-openable site
  plan + 3DFACE massing walls") and the vector-PDF site-plan writer (M5-T085) with official,
  never-guessed DXF format facts. Deterministic code emits these codes; nothing here is a legal rule.
- **Primary sources (official Autodesk only):**
  - **[A2005]** *AutoCAD DXF Reference, AutoCAD 2005* (© Autodesk 2004; DXF Reference version
    u19.1.01). PDF: `https://images.autodesk.com/adsk/files/acad_dxf.pdf` — retrieved **2026-09-24
    UTC**, HTTP 200, `application/pdf`, 1,756,239 bytes,
    sha256 `6c56324c32a86aae409f718ae50d6687c84f5043469a26fc6a5278b6cd3cba9d`. Page numbers below
    are the **printed** page numbers shown in the PDF. This is Autodesk's own published reference and
    is byte-stable for the *structural* group codes (LINE/LWPOLYLINE/POLYLINE/VERTEX/SEQEND/3DFACE/
    TEXT/LAYER/LTYPE), which have not changed across releases.
  - **[HDR2026]** *HEADER Section Group Codes (DXF)*, current AutoCAD 2026 DXF Reference:
    `https://help.autodesk.com/cloudhelp/2026/ENU/AutoCAD-DXF/files/GUID-A85E8E67-27CD-4C59-BE61-4DC9FADBE74A.htm`
    — retrieved 2026-09-24 UTC. Used for the version-sensitive facts ($ACADVER strings for 2007+ and
    the $INSUNITS survey-unit codes) that post-date [A2005].
  - **[HDR2016]/[HDR2017]** same GUID under `/cloudhelp/2016/` and `/cloudhelp/2017/` — retrieved
    2026-09-24 UTC — used only to bracket *when* the US-survey-foot code appeared.
  - **[VERART]** Autodesk support article "Drawing format version codes for AutoCAD"
    (`https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/drawing-version-codes-for-autocad.html`)
    — **HTTP 403 to non-browser fetch** on 2026-09-24 (curl + browser UA both blocked). Documented
    fallback: the $ACADVER mapping is taken from [A2005] p.14 and [HDR2026]; not from this article.

---

## 0. Headline facts (what the writer needs first)

1. **Target R12 (`$ACADVER = AC1009`) for a hand-written writer.** R12 is the simplest
   AutoCAD-openable DXF: **handles are optional** (they are not mandatory until R13 — see §2/§5), and
   there is **no OBJECTS section and no CLASSES section** (both were introduced at R13). A valid R12
   file is just `HEADER` + `TABLES` + `BLOCKS` + `ENTITIES` + `EOF`, and in practice most readers even
   accept an `ENTITIES`-only file. Every later AutoCAD opens an AC1009 file. ([A2005] p.184;
   [HDR2026] $ACADVER.)
2. **US survey foot IS a unit code: `$INSUNITS = 21` = "US Survey Feet"** (22 = US Survey Inch,
   23 = US Survey Yard, 24 = US Survey Mile). It was **added in the AutoCAD 2017 DXF reference** —
   absent in 2016 (which stops at 20 = Parsecs). This matters because NYC geometry is EPSG:2263
   (US survey feet); a writer that means survey feet should set `$INSUNITS 21`, not `2` (international
   feet). ([HDR2026], [HDR2017] present; [HDR2016] absent.)
3. **Coordinates are plain doubles; there is no georeferencing in base DXF.** Group codes 10–39 are
   double-precision 3D point values ([A2005] p.3). The writer must carry the CRS as provenance
   *outside* the DXF (the file itself does not assert EPSG:2263).
4. **3DFACE (group 0 = `3DFACE`) is the primitive for massing walls** — four corners (codes
   10/20/30, 11/21/31, 12/22/32, 13/23/33) plus a bit-coded invisible-edge flag (70). See §4.

---

## 1. Version codes ($ACADVER, group code 1) and what opens them

`$ACADVER` (HEADER, group code **1**) is the drawing-database version string. Verbatim mapping
([A2005] p.14 for AC1006–AC1018; [HDR2026] for the full current list):

| `$ACADVER` | AutoCAD release |
|---|---|
| AC1006 | R10 |
| AC1009 | R11 and R12 |
| AC1012 | R13 |
| AC1014 | R14 |
| AC1015 | AutoCAD 2000 (2000/2000i/2002 share it) |
| AC1018 | AutoCAD 2004 (2004/2005/2006 share it) |
| AC1021 | AutoCAD 2007 |
| AC1024 | AutoCAD 2010 |
| AC1027 | AutoCAD 2013 |
| AC1032 | AutoCAD 2018 |

Notes:
- The current (2026) DXF reference's **newest listed code is `AC1032 = AutoCAD 2018`**; no newer
  `$ACADVER` string is listed, consistent with AutoCAD 2018–2026 all sharing the AC1032 drawing
  format. ([HDR2026].)
- A newer AutoCAD writing to an older format tag still opens in the older AutoCAD; AC1009 (R12) is the
  broadest-compatibility target. ($ACADMAINTVER, group 70, is a maintenance counter and "should be
  ignored" — [A2005] p.14.)

---

## 2. HEADER variables the writer will set (group codes + meaning)

All from [A2005] Chapter 2 "HEADER Section", pp.14–21, unless marked [HDR2026].

| Variable | Group code | Meaning / values |
|---|---|---|
| `$ACADVER` | 1 | version string (see §1) |
| `$HANDSEED` | 5 | "Next available handle" ([A2005] p.20). Required once handles are enabled (R13+). |
| `$INSUNITS` | 70 | drawing units (see §3) |
| `$INSBASE` | 10,20,30 | insertion base point (WCS) |
| `$EXTMIN` / `$EXTMAX` | 10,20,30 | drawing extents lower-left / upper-right (WCS) |
| `$LIMMIN` / `$LIMMAX` | 10,20 | drawing limits |
| `$LUNITS` | 70 | units format for coordinates/distances |
| `$AUNITS` | 70 | units format for angles |
| `$CECOLOR` | 62 | current entity color (0 = BYBLOCK, 256 = BYLAYER) |
| `$CELTYPE` | 6 | current entity linetype, or BYBLOCK / BYLAYER |
| `$DWGCODEPAGE` | 3 | drawing code page (set at creation) |

Value-type ranges (so the writer formats each group correctly) — [A2005] p.3:
- **0–9** = string; **10–39** = double-precision 3D point value; **40–59** = double-precision float;
  **60–79** = 16-bit integer; **90–99** = 32-bit integer; **210–239** = extrusion direction (double);
  **320–369** = handle families (arbitrary / soft-pointer / hard-pointer / soft-owner / hard-owner —
  [A2005] p.8). With extended symbol names (AutoCAD 2000+) the old 255-char string limit was lifted.

---

## 3. Drawing-units codes ($INSUNITS, group code 70) — incl. US survey foot

`$INSUNITS` "Default drawing units for AutoCAD DesignCenter blocks". Values **0–20** are stable since
at least AutoCAD 2005 ([A2005] p.21, verbatim): 0 = Unitless; 1 = Inches; 2 = Feet; 3 = Miles;
4 = Millimeters; 5 = Centimeters; 6 = Meters; 7 = Kilometers; 8 = Microinches; 9 = Mils; 10 = Yards;
11 = Angstroms; 12 = Nanometers; 13 = Microns; 14 = Decimeters; 15 = Decameters; 16 = Hectometers;
17 = Gigameters; 18 = Astronomical units; 19 = Light years; 20 = Parsecs.

**Survey units — added in the AutoCAD 2017 DXF reference** (verbatim, [HDR2026]/[HDR2017]):
- **21 = US Survey Feet**
- **22 = US Survey Inch**
- **23 = US Survey Yard**
- **24 = US Survey Mile**

**Version bracket (primary-sourced):** [HDR2016] $INSUNITS stops at "20 = Parsecs" and lists **no**
21–24; [HDR2017] adds 21–24. So the US-survey-foot code first appears in the **AutoCAD 2017** DXF
reference. It is independent of the *format* version — a file can carry the AC1027 (2013) format tag
and still set `$INSUNITS 21` if written by AutoCAD 2017 or a modern library. **Recommendation for this
platform:** since parcels/measurements are EPSG:2263 (US survey feet — see PROGRAM_KNOWLEDGE domain
anchors), a survey-accurate writer should emit `$INSUNITS 21`; a reader must not assume `2` (Feet =
international foot) means survey feet.

---

## 4. Entity group codes (ENTITIES section)

Every entity also carries the **common entity codes** ([A2005] "Common Group Codes for Entities",
p.62): 0 = entity type, 5 = handle (R13+), 8 = layer name, 6 = linetype, 62 = color, 100 = subclass
marker, etc. The codes below are the entity-specific ones.

### 4.1 LINE (`0 = LINE`) — [A2005] p.91
| Code | Meaning |
|---|---|
| 100 | subclass marker `AcDbLine` |
| 39 | thickness (optional, default 0) |
| 10 / 20,30 | start point X / Y,Z (WCS) |
| 11 / 21,31 | endpoint X / Y,Z (WCS) |
| 210 / 220,230 | extrusion direction (optional, default 0,0,1) |

### 4.2 LWPOLYLINE (`0 = LWPOLYLINE`) — [A2005] p.92 (subclass `AcDbPolyline`)
| Code | Meaning |
|---|---|
| 100 | subclass marker `AcDbPolyline` |
| 90 | number of vertices |
| 70 | polyline flag (bit-coded): 1 = Closed; 128 = Plinegen |
| 43 | constant width (optional; omit if variable width 40/41 used) |
| 38 / 39 | elevation / thickness (optional) |
| 10 / 20 | vertex X / Y (OCS), **one pair per vertex** |
| 40 / 41 | start / end width per vertex (optional) |
| 42 | bulge per vertex (optional; arc segment) |
| 210 / 220,230 | extrusion direction |

LWPOLYLINE is the lightweight 2D polyline (all vertices at one elevation) and is the natural primitive
for a **closed lot outline / building footprint** (set flag 70 = 1 for closed).

### 4.3 POLYLINE / VERTEX / SEQEND (the "heavy" 2D/3D polyline) — [A2005] pp.100–104, 116
POLYLINE (`0 = POLYLINE`) is a header entity **followed by a sequence of VERTEX entities and
terminated by one SEQEND** ([A2005] p.100-101).
- **POLYLINE** header codes: 100 = `AcDb2dPolyline` or `AcDb3dPolyline`; 66 = obsolete "entities
  follow" flag (ignore if present); 10/20 = dummy (always 0), 30 = elevation; 70 = polyline flag
  (bit-coded: 1 = closed, 8 = 3D polyline, 16 = 3D polygon mesh, 64 = polyface mesh, 128 = continuous
  linetype); 40/41 = default start/end width; 71/72 = mesh M/N vertex counts; 75 = smooth-surface type.
- **VERTEX** (`0 = VERTEX`) codes: 100 = `AcDbVertex` then 100 = `AcDb2dVertex` or
  `AcDb3dPolylineVertex`; 10/20/30 = location (OCS when 2D, WCS when 3D); 40/41 = start/end width;
  42 = bulge; 70 = vertex flags; 71–74 = polyface-mesh vertex indices.
- **SEQEND** (`0 = SEQEND`) has no persisted entity-specific codes — it only carries the common entity
  codes and marks the end of the VERTEX (or ATTRIB) sequence ([A2005] p.104; the APP-only code −2 is
  "not saved in a DXF file").

For a hand-written writer, **LWPOLYLINE (§4.2) is simpler than POLYLINE/VERTEX/SEQEND** and is
preferred for flat outlines; use POLYLINE/VERTEX only if you need a true 3D polyline or a polyface mesh.

### 4.4 3DFACE (`0 = 3DFACE`) — [A2005] pp.64–65 (subclass `AcDbFace`)  ← massing walls
| Code | Meaning |
|---|---|
| 100 | subclass marker `AcDbFace` |
| 10 / 20,30 | first corner X / Y,Z (WCS) |
| 11 / 21,31 | second corner |
| 12 / 22,32 | third corner |
| 13 / 23,33 | fourth corner — **"If only three corners are entered, this is the same as the third corner"** |
| 70 | invisible-edge flags (bit-coded, default 0): 1 = 1st edge, 2 = 2nd, 4 = 3rd, 8 = 4th invisible |

A 3DFACE is a planar 3- or 4-sided face carrying real Z values — the standard primitive for turning a
footprint + height into wall/roof surfaces. A rectangular wall panel is one 3DFACE with four corners;
set edge-invisibility (70) to hide subdivision seams.

### 4.5 TEXT (`0 = TEXT`) — [A2005] pp.112–113 (subclass `AcDbText`)
| Code | Meaning |
|---|---|
| 100 | subclass marker `AcDbText` |
| 39 | thickness (optional) |
| 10 / 20,30 | first alignment point (OCS) |
| 40 | text height |
| 1 | the text string itself |
| 50 | rotation (optional, default 0) |
| 41 | relative X scale (optional, default 1) |
| 51 | oblique angle (optional) |
| 7 | text style name (optional, default STANDARD) |
| 71 | generation flags: 2 = backward, 4 = upside-down |
| 72 | horizontal justification: 0 Left, 1 Center, 2 Right, 3 Aligned, 4 Middle, 5 Fit |
| 11 / 21,31 | second alignment point (OCS) — meaningful only if 72/73 ≠ 0 |
| 73 | vertical justification: 0 Baseline, 1 Bottom, 2 Middle, 3 Top |

**Quirk to honor:** the TEXT record emits the subclass marker `100 AcDbText` **twice** — once at the
start and again just before the 73 (vertical-justification) group ([A2005] p.113). A writer that
mirrors AutoCAD output should reproduce both markers; a reader must tolerate the repeat.

---

## 5. Symbol-table records (TABLES section): LAYER and LTYPE

### 5.1 LAYER (subclass `AcDbLayerTableRecord`) — [A2005] pp.44–45
| Code | Meaning |
|---|---|
| 100 | `AcDbLayerTableRecord` |
| 2 | layer name |
| 70 | standard flags (bit-coded): 1 = frozen, 2 = frozen-by-default in new viewports, 4 = locked, 16 = xref-dependent, 64 = referenced |
| 62 | color number (**if negative, layer is off**) |
| 6 | linetype name |
| 290 | plot flag (0 = do not plot) |
| 370 | lineweight enum value |
| 390 | hard-pointer handle of the PlotStyleName object |

### 5.2 LTYPE (subclass `AcDbLinetypeTableRecord`) — [A2005] pp.45–46
| Code | Meaning |
|---|---|
| 100 | `AcDbLinetypeTableRecord` |
| 2 | linetype name |
| 70 | standard flags (same bit meanings as LAYER's 16/32/64) |
| 3 | descriptive text |
| 72 | alignment code — **always 65** (ASCII "A") |
| 73 | number of linetype elements |
| 40 | total pattern length |
| 49 | dash/dot/space length (one per element) |
| 74 / 75 | complex-element type / shape number (embedded shape/text) |

A minimal writer defines at least layer `0` and linetype `CONTINUOUS`.

---

## 6. Minimal valid file: R12 vs R2000 (structure + handles)

**Section order** (both): `HEADER`, `CLASSES` (R13+ only), `TABLES`, `BLOCKS`, `ENTITIES`,
`OBJECTS` (R13+ only), each wrapped `0/SECTION … 0/ENDSEC`, file terminated by `0/EOF`.

### R12 / AC1009 (recommended writer target)
- **Handles optional.** Per [A2005] p.184 (Appendix B, "Database Objects"): a handle "has existed
  since AutoCAD Release 10, and **as of AutoCAD Release 13, handles are always enabled**." So in R12
  the group-5 handle and `$HANDSEED` are **not required**.
- **No CLASSES section** (the CLASSES section holds application-defined classes — [A2005] p.31 — and
  did not exist before R13). **No OBJECTS section** (introduced at R13).
- **Minimal complete R12 file:** `HEADER` (at least `$ACADVER = AC1009`, plus `$INSUNITS`), `TABLES`
  (at least a LAYER table with layer `0`; AutoCAD also expects VPORT/LTYPE/STYLE), `ENTITIES`
  (your LINE / LWPOLYLINE / 3DFACE / TEXT), `EOF`. In practice many DXF readers (incl. ezdxf and
  AutoCAD's own importer) accept a file consisting of only an `ENTITIES` section + `EOF`, but the
  HEADER+TABLES form is the safe, self-describing choice.

### R2000 / AC1015 (and any R13+)
- **Handles mandatory** ([A2005] p.184): every entity/object carries a **group-5 handle unique to the
  file**, and `$HANDSEED` (HEADER group 5) must give the next free handle.
- Adds the **CLASSES section** (each CLASS record: 0 = CLASS, 1 = DXF record name, 2 = C++ class name,
  3 = app name, 90 = proxy flags, 280 = was-a-proxy, 281 = is-an-entity; "All fields are required" —
  [A2005] pp.31–32) and an **OBJECTS section** of non-graphical objects (dictionaries etc.).
- **Residual to verify at implementation ([NEEDS G1 RE-VERIFICATION]):** the exact *minimum required
  contents* of the R2000 OBJECTS section (the root named-object dictionary and its mandatory children
  such as ACAD_GROUP) were **not** quoted verbatim from an official page in this pass — [A2005]'s
  OBJECTS-section intro was not extracted. If the writer must emit R2000+, confirm the minimal
  root-dictionary requirement against the OBJECTS-section chapter of the current DXF reference (or rely
  on a spec-complete library such as `ezdxf`, which is the sandbox-testable path the survey format
  policy already contemplates). For an AutoCAD-openable site plan, **R12 avoids this entirely** and is
  the recommended target.

---

## 7. Consumer-facing summary (for M5-T081 / M5-T085)

- Write **R12 (AC1009)** to sidestep handles/CLASSES/OBJECTS; set `$INSUNITS 21` (US Survey Feet) so
  the file self-declares survey feet consistent with EPSG:2263; keep the CRS in provenance, not the DXF.
- Use **LWPOLYLINE (closed, flag 70=1)** for lot outline / footprint, **3DFACE** for extruded massing
  wall/roof panels (four WCS corners + invisible-edge flags), **TEXT** for labels, on named **LAYER**s
  with linetype `CONTINUOUS`.
- A **G1 "format check"** should assert: file parses (e.g. via `ezdxf.readfile` in the cloud sandbox),
  `$ACADVER == AC1009`, `$INSUNITS == 21`, expected layers exist, and entity counts/coordinate bounds
  match the source geometry. Round-tripping through the in-repo reader (M5-T085) is the acceptance signal.

## 8. What I could not verify in this pass
- The exact minimal OBJECTS-section root-dictionary contents for R2000+ (see §6; marked
  [NEEDS G1 RE-VERIFICATION]). Not blocking for an R12 writer.
- Post-2018 `$ACADVER` codes: none is listed by the current reference; the Autodesk support article
  [VERART] that tabulates all codes is browser-only (403) and was not read.
- Binary-DXF specifics (Appendix A, [A2005] p.176) — out of scope; the writer should emit ASCII DXF.
