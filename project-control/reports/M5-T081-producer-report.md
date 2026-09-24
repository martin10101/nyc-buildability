# M5-T081 producer report — D-087 CAD-1: zero-dependency DXF writer core

Producer: backend-engineer (orchestrator-dispatched subagent). Worktree
`C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t081`, branch `task/M5-T081-dxf-writer`,
contract head `f9bfd54d37c981e938185e3ae09ea9ad85f415f3` (verified before work).

## Scope delivered

- `services/api/app/cad/dxf_writer.py` — typed DXF document model, single sanitizing
  serializer, deterministic ASCII R12 (AC1009) writer, and a pure site-plan builder.
  Stdlib only (`math`, `collections.abc`, `dataclasses`); no network, no I/O, no new
  dependency; no route/endpoint/main.py/web change.
- `services/api/tests/cad/test_dxf_writer.py` — 17 tests across AS-1..AS-5 with an
  independent in-test group-code reader and a pinned golden sha256.
- This report.

`app/cad/__init__.py`, `tests/cad/__init__.py`, and the sibling
`app/cad/pdf_sheet_writer.py` were NOT touched (orchestrator/sibling-owned).

## Format decisions (Autodesk DXF Reference — every citation marked `[recalled - verify]`; authored offline, G1 confirms)

- Version R12 / `$ACADVER = AC1009` (`dxf_writer.py:62`, header emit `:437-438`):
  most widely openable ASCII DXF; needs no entity handles, no OBJECTS/CLASSES sections
  (packet preference over R2000+). Section order HEADER → TABLES → ENTITIES → `0/EOF`
  (`serialize_document` `:547-556`).
- Drawing-units variable `$INSUNITS = 2` (Feet) in the header (`:72`, emit `:439-440`).
  EPSG:2263 is US survey feet, which `$INSUNITS` cannot distinguish from international
  feet (2 ppm, immaterial to opening); the exact CRS is ALSO stated on the ANNOTATION
  layer so no unit fact depends solely on a reader honouring `$INSUNITS`. Availability
  note recorded inline for G1 (`:66-72`).
- Extents `$EXTMIN`/`$EXTMAX` from all emitted coordinates incl. z (`:441-448`,
  `_compute_extents` `:609-637`).
- TABLES: one CONTINUOUS LTYPE (group 2/70/3/72=65/73=0/40) + LAYER table (group
  2/70/62/6) — `_write_tables` `:454-482`.
- Entities: LINE (`:512`), closed 2D POLYLINE/VERTEX/SEQEND at an elevation
  (`:484-501`), TEXT (`:523`), 3DFACE quad four-corner (`:503-510`). Layer=group 8,
  color=ACI group 62. Each constant carries its group-code citation inline.

## Per-acceptance-scenario evidence

**AS-1 (structure / determinism).** Output is pure ASCII with strictly alternating
group-code/value lines, sections in reference order, terminated by `0/EOF`. The in-test
reader `parse_pairs`/`split_sections` (`test:58,72`) parses it back and asserts alternation
+ order + `$ACADVER=AC1009` + `$INSUNITS` present (`test_as1_structure...` `test:154`).
Byte-identical output on repeat and the pinned golden sha256
`dbef79e1fd68508541a874ad5948a0384d08b8124f7c57122422706466d2ff11`
(`GOLDEN_SHA256` `test:47`, `test_as1_golden_digest_is_byte_stable` `test:167`). LF EOL and
`{:.6f}` real formatting make the digest platform-stable (the `"\n"` literal is one LF byte
regardless of the .py file's own CRLF-on-Windows line endings).

**AS-2 (site-plan content).** Fixture = rectangular lot + L-shaped building (6 vertices) +
3 floors (`test:34-45`). Emits exactly layers LOT, BUILDING_OUTLINE, MASSING_3D, ANNOTATION
(`test_as2_layers_present_exactly` `test:178`). 3DFACE count = 18 = 6 edges × 3 floors;
POLYLINE = 6 = lot + building + (floors+1) massing rings; LINE = 6 vertical corner lines;
TEXT = 3 (`test_as2_face_count...` `test:189`; builder `:672-711`). Every outline polyline
closed (flag 70 bit 1) and every written building/lot coordinate round-trips exactly through
the reader (`test_as2_outlines_closed_and_coordinates_round_trip` `test:199`). Header declares
the drawing unit `$INSUNITS=2` (`test_as2_header_declares_drawing_unit` `test:211`).

**AS-3 (fail-closed + injection).** Typed `DxfValidationError` with machine `code` for:
non-finite coordinate (`test:221`, `_format_real` `:191`/`Ring.validate` `:289`),
degenerate ring — <3 vertices (`test:229`) and zero-area/collinear (`test:237`, shoelace
`_signed_area` `:264`), invalid layer name (`test:245`, `_validate_layer_name` `:250`),
over-cap entity count (`test:252`, `DxfDocument.validate` `:405`/`MAX_ENTITIES` `:137`).
Validation runs before serialization and the document is assembled fully in memory, so a
refusal yields NO partial output (`test_as3_no_partial_output_on_refusal` `test:280`).
Injection: the single choke point `_GroupCodeStream.pair → _sanitize_value` (`:233,203`)
rejects any CR/LF/control/non-ASCII byte, so a text value cannot forge a group-code line
(`test_as3_newline_injection_refused` `test:274`; guard-necessity monkeypatch
`test_as3_sanitizer_guard_is_necessary` `test:289`).

- Sanitizer MUTATION record (ran both directions):
  - MUTANT (inserted `return value` at top of `_sanitize_value`, bypassing the guard):
    `python -m pytest tests/cad/test_dxf_writer.py::test_as3_newline_injection_refused -q`
    → **1 failed** — `Failed: DID NOT RAISE DxfSanitizationError` (injection accepted).
  - REVERTED (guard restored): same command → **1 passed**. No `MUTANT` residue remains
    (grep clean); the module is byte-identical to its pre-mutation state.

**AS-4 (honesty).** ANNOTATION layer always carries `PROPOSED - NOT A CITY RECORD`
(`:110`), the CRS/units note `COORDINATES: EPSG:2263 NAD83 NY LONG ISLAND - US SURVEY FEET`
(`:111`), and the generator identity (`:112`) — `_build_annotation` `:588-607`. No
claim-class word appears anywhere in the output: the test greps the full uppercased DXF
against `CLAIM_CLASS_WORDS` (`:117`; `test_as4_no_claim_class_words_anywhere` `test:310`)
and spot-checks PERMITTED / APPROVED / MAXIMUM ALLOWED. The forbidden list deliberately
excludes the honest negation "NOT A CITY RECORD"; `_assert_no_claim_words` (`:579`) also
guards the annotation strings at build time.

**AS-5 (scope).** Zero new dependencies; ruff clean; modularity exit 0; only the three
allowed files changed; no route/web change. `test_as5_module_imports_stdlib_only`
(`test:323`) asserts the module imports no shapely/numpy/pydantic/fastapi/requests/httpx.

## Self-checks (verbatim)

```
### CWD: services/api
$ python -m ruff check .
All checks passed!

$ python -m pytest tests/cad/test_dxf_writer.py -q
.................                                                        [100%]
17 passed in 0.07s

### CWD: worktree root (C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t081)
$ python tools/modularity_check.py --check
exit=0   (dxf_writer.py and test_dxf_writer.py absent from the warn/fail list)
```

Environment note: sandbox Python is 3.11.9; CI targets 3.12 (`requires-python >=3.12`,
ruff `target-version = py312`). `from __future__ import annotations` keeps all annotations
as strings, so the 3.11 local run and the 3.12 CI run are behaviourally identical for this
module. ruff 0.13.0, pytest 8.4.2 locally.

## Deviations

- None from the packet's substance. The objective lists `$ACADVER + the drawing-units
  variable + extents`; I emit exactly `$ACADVER`, `$INSUNITS`, `$EXTMIN`, `$EXTMAX` (no
  extra header vars) to keep the R12 header minimal and maximally openable.
- Interpretation recorded for the reviewer: "outline polylines at each elevation" is
  implemented as one closed ring at every band boundary INCLUDING the base (floors+1 rings)
  so the MASSING_3D layer is a self-contained wireframe independent of the BUILDING_OUTLINE
  footprint layer. This duplicates the footprint ring across two layers by design.

## DISCOVERIES (out of scope — for the orchestrator's D-069 backlog sweep)

- D1 (verify): `$INSUNITS` entered wide use at R2000 (AC1015); it is emitted here as an
  ordinary group-9 header variable and AutoCAD reads it in an AC1009 file, but a strict
  minimal R12 reader could ignore it. G1 should confirm against the live DXF Reference; the
  fallback (already in place) is that the CRS/units fact is ALSO carried in ANNOTATION text.
- D2 (verify): the writer omits a STYLE table and relies on TEXT defaulting to the implicit
  STANDARD text style (group 7 absent). This is common minimal-DXF practice and AutoCAD
  auto-provides STANDARD; flagged for G1 to confirm no reader requires an explicit STYLE
  table for TEXT.
- D3 (product, future wiring): this packet ships a tested module only; a later gated packet
  must wire it to the scenario/max-envelope geometry (EPSG:2263 rings from
  `app.connectors.mappluto_geometry_arcgis` and the massing engine) and decide the export
  route surface. No route is mounted here.
