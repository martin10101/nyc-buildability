# M5-T096 producer report (D-087 CAD-2) - backend-engineer

Owner-openable CAD sample files + plain-English AutoCAD opening checklist (closes DCV-F1 /
DB-057 a), DXF writer STYLE/VPORT tables (G1-A2 / DB-057 b), and a stdlib import allowlist
(DCV-F3 / DB-057 f). Producer subagent, task worktree `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t096`,
branch `task/M5-T096-cad-owner-samples`, reset to claim-seam `2e0b2351` before work.

Local Python 3.11.9 (CI is 3.12). Evidence status: [OBSERVED] unless marked otherwise.

## Files changed (exactly the allowed paths)

- `services/api/app/cad/dxf_writer.py` - STYLE (STANDARD) + VPORT (*ACTIVE) tables; TABLES
  order VPORT, LTYPE, LAYER, STYLE; golden re-pinned. New public constants `STYLE_*`, `VPORT_*`;
  new private helpers `_vport_frame`, `_write_vport_table`, `_write_ltype_table`,
  `_write_layer_table`, `_write_style_table`. No existing public name changed; CLAIM_CLASS_WORDS,
  AC1009, $INSUNITS 21, the layer set, every refusal and honesty text are byte-unchanged.
- `services/api/tests/cad/test_dxf_writer.py` - re-pinned golden (reason recorded inline), AS-1
  table-order / STYLE / VPORT-framing / every-text-resolves tests, AS-4 import-allowlist tests
  (replaces the former six-library `test_as5_module_imports_stdlib_only`).
- `services/api/tests/cad/test_cad_owner_samples.py` - replaces the placeholder; sample builders
  + AS-3 byte-identity, honesty-label, size and README-sha256 tests.
- `docs/samples/cad/README.md` - replaces the placeholder; owner-facing plain-English checklist.
- `docs/samples/cad/example-site-plan.dxf`, `example-site-plan.pdf`, `example-massing.glb` - the
  three samples (one synthetic lot + building).
- `docs/samples/cad/.gitattributes` - marks *.dxf/*.pdf/*.glb `binary` (see Deviation D2).
- `project-control/reports/M5-T096-producer-report.md` - this report.

No forbidden path touched (pdf_sheet_writer.py, glb_writer.py, cad/__init__.py, the sibling test
files, app/drawings, app/scenario, app/api, main.py, requirements*, apps/, packages/ all untouched).
Zero new dependencies; no route/main.py/web change; native DWG untouched (R007).

## Commands (verbatim results)

cwd `services/api`:
- `python -m ruff check .` -> `All checks passed!` (exit 0). [OBSERVED]
- `python -m pytest tests/cad/test_dxf_writer.py tests/cad/test_cad_owner_samples.py tests/cad/test_pdf_sheet_writer.py tests/cad/test_glb_writer.py -q` -> `277 passed in 0.78s`. [OBSERVED]

cwd repo root `wt-m5t096`:
- `python tools/modularity_check.py --check` -> `selected 488 files; failures 0; warnings 27`,
  exit 0. dxf_writer.py appears once as a WARN-band `review_signal` (see Deviation D5). [OBSERVED]

Openability signal (read-only round-trip through the ACCEPTED M5-T086 reader `app.drawings.dxf_reader`):
`read_dxf(example-site-plan.dxf)` -> `ok=True`, `acad_version=AC1009`,
`units=DxfUnits(code=21, name='us_survey_feet', source='header:$INSUNITS')`, 31 primitives
(16 FacePrimitive, 7 PolylinePrimitive, 4 LinePrimitive, 4 TextPrimitive) - the 4 texts are the
three fixed annotations plus `Example lot - not a real property`. The new STYLE/VPORT tables do not
disturb parsing. [OBSERVED] (I cannot run AutoCAD here - AutoCAD-open is [BLOCKED]; that is exactly
why the owner-openable sample + README checklist is the deliverable.)

## STYLE / VPORT format authority (for the G1 verifier)

- STYLE record group codes are CHECKED against the LIVE Autodesk DXF Reference "STYLE (DXF)" page
  (help.autodesk.com/cloudhelp/2024/ENU/AutoCAD-DXF, GUID-EF68AF7C-13EF-45A1-8175-ED6CE66C8FC9,
  retrieved 2026-09-24 UTC): 2 name, 70 flags (1=shape, 4=vertical), 40 fixed height (0=not fixed),
  41 width factor, 50 oblique, 71 gen-flags, 42 last height, 3 primary font, 4 bigfont (blank). The
  record is stable across releases. STANDARD is written with font `txt`, blank bigfont, height 0 (so
  each TEXT keeps its own group-40 height). TEXT entities omit group 7, so they resolve to STANDARD,
  which the table now defines.
- VPORT uses the R12/AC1009 layout, marked `[recalled - verify]` in the source for the group codes
  that DIFFER from the live modern page. I fetched the LIVE 2024 "VPORT (DXF)" page
  (GUID-8CE7CC87-27BD-4490-89DA-C21F516415A9): it is the R2000+ subclass form and relocates VIEW
  HEIGHT to group 45, with no group 41. In an R12 file AutoCAD reads the VPORT with the R12 schema
  (VIEW HEIGHT = group 40, VIEWPORT ASPECT RATIO = group 41, lens length 42, clipping 43/44); the
  *ACTIVE record therefore uses the R12 codes. Codes shared with the live page (2 name, 10/20+11/21
  corners, 12/22 view centre DCS, 13-15/23-25 snap/grid, 16/26/36 view direction, 17/27/37 target,
  42 lens length, 50/51, 71, 72 circle sides, 74 UCSICON) are CHECKED against it.
- TABLES order VPORT, LTYPE, LAYER, STYLE is `[recalled - verify]` (the "About the DXF TABLES
  Section" overview GUIDs I tried returned 404; the live STYLE and VPORT record pages loaded). LTYPE
  precedes LAYER because a layer's group 6 references the CONTINUOUS linetype.

## Golden re-pin

- Old: `2d8988d6d7338ed606a9a253cb0d3af2fe1c8f5d526cd8750dac769a9025d809`
- New: `6a8dbd94fd3f5a6e9ddc22bb5712dd10133a1b7701301c59fc7023f495ba127b`
- Reason: the TABLES section now emits a VPORT (*ACTIVE) table framing the extents and a STYLE
  (STANDARD) table, in R12 order (VPORT, LTYPE, LAYER, STYLE), in addition to the prior LTYPE +
  LAYER tables. No HEADER variable, layer, entity, refusal or honesty text changed; only the two
  added tables move the bytes. The fixture (LOT/BUILDING/FLOOR_HEIGHTS) is unchanged; the rendered
  VPORT for it is *ACTIVE, view centre (1050.0, 2035.0) = extents midpoint, view height 110.0
  covering the 100 x 90 ft extents at aspect 1.0.

## Sample files (each well under 200 KB)

| File | Size (bytes) | sha256 |
|---|---|---|
| example-site-plan.dxf | 7936 | 4e19c669ca00d8e71b529e81921f0d203ecfa3c6d4bb57988f9b78d70465c03e |
| example-site-plan.pdf | 1839 | 8f28f12d9b244c8d17876951dc11e73963f703110cc3ad5697a8b85a7fb0c726 |
| example-massing.glb | 2460 | 0bc7a37d0f78feafe6440bf8636cd5b43b3d25259e76f36d3f9f3fc4fd5816bf |

One synthetic lot (100x80 ft) + centred building (60x40 ft, 4 floors / 42 ft), EPSG:2263 US survey
feet (easting ~9.88e5, northing ~2.10e5 - inside the NYC range). Built through the accepted writers'
public functions: DXF via `build_site_plan_document`+`serialize_document` (with one appended public
`TextLabel` for the synthetic label - Deviation D3), PDF via `render_site_plan_pdf`, GLB via
`write_glb` on a box+slab mesh assembled in the test module (no production code). Each file carries
`Example lot - not a real property` and its writer's proposed / not-a-city-record stamp (Deviation
D1). README lists every file's true sha256 (asserted by `test_as3_readme_lists_correct_sha256_of_each_file`).

## Per-acceptance-scenario evidence

- AS-1 (tables) [OBSERVED]: `test_as1_tables_in_r12_reference_order`, `test_as1_style_table_defines_standard`,
  `test_as1_every_text_resolves_to_a_defined_style`, `test_as1_vport_active_frames_the_extents` pass;
  the in-repo group-code parser confirms LTYPE, LAYER, STYLE(STANDARD), VPORT(*ACTIVE) in order, every
  TEXT resolves to the defined STANDARD style, and the *ACTIVE view centre = extents midpoint with the
  framed view (height x aspect) covering the extents. Mutation M1 (drop STYLE) reddens.
- AS-2 (compatibility kept) [OBSERVED]: AC1009, $INSUNITS 21, the four layers, refusals, honesty
  texts and CLAIM_CLASS_WORDS unchanged (existing `test_as2_*`, `test_as4_*` still green); the golden
  is re-pinned with the reason above; `test_pdf_sheet_writer.py` passes unchanged (inside the 277).
- AS-3 (samples) [OBSERVED]: three files under `docs/samples/cad/`, each labelled synthetic +
  proposed, each regenerated byte-identically by `test_as3_sample_regenerates_byte_identically`; the
  README gives a per-file plain-English opening checklist with expected layers/units and each file's
  sha256. Mutation M5 (writer-output change) reddens the sample test.
- AS-4 (import allowlist) [OBSERVED]: `test_as4_module_import_allowlist` asserts the AST-parsed import
  set is a subset of `{__future__, math, collections.abc, dataclasses}` (and non-vacuously that each is
  present); `test_as4_allowlist_is_load_bearing` shows `import json` is rejected. Mutation M6 reddens.
- AS-5 (scope + boundaries) [OBSERVED]: zero new dependencies, no route/main.py/web change, native DWG
  untouched, exactly the allowed paths (git status confirms only the allowed paths changed).

## Mutation table (in-process, actual test assertions run against a mutated writer)

| # | Mutation | Test exercised | Result |
|---|---|---|---|
| M1 | `_write_style_table` -> no-op (drop STYLE) | test_as1_style_table_defines_standard / _every_text_resolves | RED |
| M2 | `_vport_frame` -> return (0,0,110) (centre ignores extents) | test_as1_vport_active_frames_the_extents | RED |
| M3 | emit STYLE before VPORT (wrong order) | test_as1_tables_in_r12_reference_order | RED |
| M4 | STYLE font `txt`->`arial` | test_as1_golden_digest_is_byte_stable | RED |
| M5 | STYLE font change (writer output drift) | test_as3_sample_regenerates_byte_identically(dxf) | RED |
| M6 | `import json` prepended to source | test_as4_allowlist_is_load_bearing | RED |

## Deviations

- D1 (honesty-stamp casing): the DXF and PDF carry the upper-case `PROPOSED - NOT A CITY RECORD`; the
  accepted GLB writer stamps its own title-case `Proposed - not a city record` (asset + scene), which
  I must not change (glb_writer.py is forbidden). Each file "keeps" a proposed/not-a-city-record
  stamp; only the casing differs by writer. Asserted per-file in `test_as3_every_file_carries_a_proposed_not_a_city_record_stamp`.
- D2 (`docs/samples/cad/.gitattributes`): the repo has `core.autocrlf=true`. Without a binary
  attribute git would corrupt the PDF (it carries CR/LF in its xref and has no NUL byte, so git would
  strip the CR on add) and smudge the DXF (ASCII+LF -> CRLF on Windows checkout), breaking
  byte-identity and the README digests. I added `docs/samples/cad/.gitattributes` (`*.dxf/*.pdf/*.glb
  binary`) - inside the allowed `docs/samples/cad/**`. `git check-attr -a` confirms `binary: set,
  text: unset` for all three. It is a dotfile; flagging in case the allowed_paths matcher treats
  dotfiles specially (the file is required for the byte-identity guarantee).
- D3 (DXF synthetic label): the DXF writer's annotation is fixed (PROPOSED / CRS / generator). To put
  `Example lot - not a real property` in the DXF, the sample builder appends one ANNOTATION `TextLabel`
  through the writer's public API and extends the public `DxfDocument.extents_min/max` to include it,
  then calls `serialize_document`. All geometry and the fixed stamp still come from
  `build_site_plan_document`; no private helper is used.
- D4 (VPORT R12 codes vs the live modern page): see "STYLE / VPORT format authority". VPORT view
  height/aspect use the R12 codes 40/41, marked `[recalled - verify]`; the modern page (group 45) is
  the R2000+ form and does not apply to an AC1009 file. A worst-case misread affects only the initial
  zoom, never geometry or openability.
- D5 (modularity WARN): dxf_writer.py grew to ~671 SLOC (932 physical lines), tripping the WARN-band
  `review_signal` (WARN_SLOC 600, JUSTIFY_SLOC 750, HARD_SLOC 1000). The check still passes (failures
  0, exit 0; WARN band is reported-but-never-fails and below the justification threshold). The growth
  is scope-forced - the packet's allowed_paths permit only dxf_writer.py, so STYLE/VPORT cannot go in a
  new module - and cohesive: STYLE and VPORT are part of the same DXF TABLES-serialization
  responsibility. A future non-scope-limited touch could split the writer (HEADER/TABLES/ENTITIES) with
  a compatibility facade.

## DISCOVERIES (out-of-scope; not fixed in-packet - for the orchestrator to route)

- DSC-1: cross-writer honesty-vocabulary casing is inconsistent - the DXF/PDF use `PROPOSED - NOT A
  CITY RECORD` while the accepted GLB writer uses title-case `Proposed - not a city record`. Harmless
  today; a future touch could normalize the honesty vocabulary across app/cad writers.
- DSC-2: D-087-R004's owner-runnable AutoCAD-open check is now DELIVERED (committed sample DXF + PDF +
  GLB and the plain-English README checklist). Two directive-level items remain and are NOT closed by
  this packet: the R008 owner "DXF = the middleman" confirmation still awaits the owner, and any actual
  route/wiring that exposes these exports is a later gated packet (this packet ships a tested module +
  static samples only).
- DSC-3: the Autodesk "About the DXF TABLES Section" overview page (canonical inter-table order) was
  not fetched (the GUIDs I tried 404'd); table order is `[recalled - verify]` for the G1 verifier with
  network. The STYLE and VPORT record pages themselves loaded and are cited above.

## Requested status

awaiting_gate. One commit will contain exactly the allowed paths above.
