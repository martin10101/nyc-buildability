# M5-T086 producer report - D-087 CAD-3 strict-subset DXF reader

Producer: backend-engineer (orchestrator-dispatched subagent).
Worktree: `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t086`; branch `task/M5-T086-dxf-reader`.
Contract-seam HEAD verified `46cc1e6a258024ae8ce023ce17af97538d85b398` before work.

Deliverable: a dependency-free, stdlib-only, no-network strict-subset ASCII DXF reader that
turns the group-code stream into typed, layer-tagged primitives with declared units and
typed all-or-nothing refusal VALUES (never an exception). Not wired to any route / main.py /
worker. Three allowed files only.

- `services/api/app/drawings/dxf_reader.py` - the reader.
- `services/api/tests/drawings/test_dxf_reader.py` - 28 tests incl. the two named mutation probes.
- `project-control/reports/M5-T086-producer-report.md` - this report.

## Format authority (never guessed)

Group codes and header variables are cited per-constant to the Autodesk DXF Reference and
marked `[recalled - verify]` for the G1 reviewer (`dxf_reader.py:80-97`). The sibling
`docs/research/dxf-format-reference-2026-09.md` (M5-T084) was still a placeholder at this
seam, so recall + `[recalled - verify]` is the honest channel; the G1 reviewer verifies each
against the official reference. Constants to verify: entity/structural=0, text/string-var=1,
name=2, header-var=9, layer=8, points 10/20/30 .. 13/23/33, text-height=40, bulge=42,
flags=70 (closed = bit 1); `$INSUNITS` value on a group-70 pair, `$ACADVER` on a group-1
pair; `$INSUNITS` code->name map (`dxf_reader.py:113-135`); binary sentinel
`b"AutoCAD Binary DXF"` (`dxf_reader.py:109`).

## Written subset / disclose-or-refuse rule

Stated verbatim in the module docstring (`dxf_reader.py:24-55`). Summary: LINE, LWPOLYLINE,
POLYLINE/VERTEX/SEQEND, 3DFACE, TEXT are PARSED; any other ENTITIES-section type is
DISCLOSED (counted in `disclosed_unknown`, read still succeeds); whole non-HEADER/ENTITIES
sections are skipped and recorded in `skipped_sections` (so a BLOCKS *definition* is skipped
while an ENTITIES `INSERT` is disclosed-as-unknown); structural corruption / over-limit
input / a non-zero bulge is REFUSED all-or-nothing as a typed VALUE.

## Per-AS evidence (file:line)

### AS-1 subset -> typed primitives
- `test_as1_full_drawing_yields_typed_primitives` (`test_dxf_reader.py:106`) - one fixture
  with a closed LWPOLYLINE lot, a POLYLINE building (VERTEX/SEQEND), 3DFACE walls, TEXT and
  an unknown CIRCLE yields exactly `[Polyline, Polyline, Face, Text]` with exact coordinates,
  layer names (`LOT`/`BLDG`/`WALLS`/`NOTES`) and `closed=True` flags.
- LINE start/end typed: `test_as1_line_entity_start_and_end` (`:145`). DXF default layer `"0"`
  when group 8 is absent: `test_as1_missing_layer_defaults_to_zero` (`:162`).
- Implementation: entity dispatch `_handle_entity` (`dxf_reader.py:532-567`); per-entity
  parsers `_parse_line/_parse_lwpolyline/_parse_face/_parse_text` (`:330-401`); compound
  `_parse_polyline` consumes VERTEX* then SEQEND incl. SEQEND's own body (`:403-455`).

### AS-2 units honesty (never assume feet)
- Feet reported with code + provenance: `test_as2_feet_units_reported_with_code` (`:176`)
  -> `code=2`, `name="feet"`, `source="header:$INSUNITS"`, `acad_version="AC1027"`.
- No `$INSUNITS` header -> unitless, never feet: `test_as2_no_units_header_is_unitless_never_feet`
  (`:185`) -> `code=None`, `name="unitless"`, `source="absent"`.
- Declared-unitless (`$INSUNITS=0`) is distinguished from absent by `source`:
  `test_as2_explicit_unitless_distinguished_from_absent` (`:198`).
- Unknown units code reported verbatim, never coerced:
  `test_as2_unknown_units_code_reported_verbatim_never_coerced` (`:212`) -> `unknown_insunits_99`.
- Implementation: `_handle_header` (`dxf_reader.py:517-529`), `_resolve_units` (`:615-619`).

### AS-3 outside the subset (disclose-or-refuse)
- Unknown entity counted + disclosed, not refused:
  `test_as3_unknown_entity_counted_and_disclosed_not_refused` (`:228`) ->
  `disclosed_unknown == (("CIRCLE", 1),)`, `entity_count == 5` (4 parsed + 1 disclosed).
- INSERT reference disclosed-as-unknown: `test_as3_insert_reference_disclosed_as_unknown` (`:235`).
- Non-data section skipped + disclosed: `test_as3_non_data_section_skipped_and_disclosed` (`:248`)
  -> `skipped_sections == ("BLOCKS",)`; the LINE inside BLOCKS is skipped with the section.
- Binary DXF sentinel refused: `test_as3_binary_dxf_sentinel_refused` (`:266`) -> `BINARY_DXF`.
- Implementation: unknown counting + skipped-section tracking in `_walk` (`dxf_reader.py:570-613`),
  binary sentinel in `_decode` (`:457-461`).

### AS-4 fail-closed + bounds (every refusal a VALUE, no exception escapes)
- `test_as4_odd_pair_count_refused` (`:275`) -> `ODD_PAIR_COUNT` (pair-parity, `dxf_reader.py:483-487`).
- `test_as4_non_numeric_coordinate_refused` (`:282`) / `test_as4_non_finite_coordinate_refused`
  (`:293`) -> `BAD_COORDINATE` (`_to_float`, `:283-295`; rejects Inf/NaN via `math.isfinite`).
- `test_as4_bad_group_code_refused` (`:304`) -> `BAD_GROUP_CODE`.
- `test_as4_non_zero_bulge_refused` (`:310`) -> `UNSUPPORTED_BULGE` (curved segment refused,
  never silently flattened).
- `test_as4_file_too_large_refused` (`:323`) -> `FILE_TOO_LARGE`;
  `test_as4_line_too_long_refused` (`:329`) -> `LINE_TOO_LONG`;
  `test_as4_too_many_vertices_refused` (`:340`) -> `TOO_MANY_VERTICES`.
- `test_as4_stray_vertex_outside_polyline_refused` (`:354`) /
  `test_as4_unterminated_polyline_refused` (`:365`) /
  `test_as4_no_section_markers_refused` (`:377`) -> `MALFORMED_STRUCTURE`.
- `test_as4_never_raises_on_garbage` (`:383`) - empty/binary/high-byte/ASCII-garbage blobs all
  return a value (no exception escapes); `test_as4_non_ascii_bytes_refused` (`:391`) -> `NON_ASCII`.
- Implementation: private `_Refuse` marker (`dxf_reader.py:275-280`) raised internally and
  converted to a `DxfRefusal` VALUE at the public boundary, with a final defensive
  `except Exception` guard so ANY unexpected error becomes a refusal value (`:630-640`).

### AS-5 scope
- `test_as5_default_limits_are_the_reviewed_constants` (`:400`) guards against silent bound
  drift; `test_as5_result_is_frozen_value` (`:409`) proves results are frozen (immutable)
  value objects. No route/main.py/web touched; zero new dependencies; stdlib only
  (`import enum`, `math`, `dataclasses`); ruff + modularity clean (below); exactly the three
  allowed files changed.

## Self-check lines (verbatim, with cwd)

cwd `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t086\services\api`:
```
$ python -m ruff check .
All checks passed!
```
```
$ python -m pytest tests/drawings/test_dxf_reader.py -q
............................                                             [100%]
28 passed in 0.10s
```
cwd `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t086`:
```
$ python tools/modularity_check.py --check   # EXIT=0
selected 484 files; failures 0; warnings 22
```
All 22 warnings are pre-existing signals on OTHER files; `dxf_reader.py` is not flagged
(grep for `dxf`/`drawings` in the output: none). `dxf_reader.py` is well under the 600 SLOC
warning threshold (single-responsibility module: read strict-subset DXF).

## Mutation record (red/green, named in the packet)

Both mutations applied to the real module, the single target test run, then reverted; the
full suite is green again after revert (28 passed, shown above).

- MUTATION #1 - drop the entity-count bound (`_handle_entity`, `dxf_reader.py:562-566`):
  `test_mutation_entity_count_bound_reddens` (`:423`) FAILED red -
  `AssertionError: isinstance(DxfDocument(... entity_count=3), DxfRefusal)` (the 3-entity
  file parsed instead of refusing under `max_entities=2`). Restored -> green.
- MUTATION #2 - drop the pair-parity check (`_to_pairs`, `dxf_reader.py:483-487`):
  `test_mutation_pair_parity_check_reddens` (`:438`) FAILED red - reason became
  `MALFORMED_STRUCTURE` (`detail='unexpected IndexError: list index out of range'`, the
  pairing loop reads past the final line and the defensive guard catches it) instead of
  `ODD_PAIR_COUNT`. Restored -> green.

## Deviations

None. Stayed within the three allowed_paths; did not touch `app/drawings/__init__.py`,
`sheet_reader.py`, `sheet_primitives.py`, or `app/cad/`; did not import the M5-T081 writer.

## Discoveries (D-069; orchestrator records at the seam)

- WATCH: bulge (group 42) arcs on LWPOLYLINE/POLYLINE are currently REFUSED (no assumed arc
  tolerance in phase C). A later gated packet could add opt-in flattening under a declared,
  reviewed tessellation tolerance if real architect DXFs carry arc boundaries frequently -
  needs the M5-T084 architect-drawing-corpus finding to decide.
- WATCH: this reader decodes strictly as ASCII; real TEXT with non-ASCII glyphs (accents,
  degree signs) refuses as `NON_ASCII`. If the corpus shows non-ASCII TEXT is common, a
  future packet may widen to a declared single-byte or UTF-8 decode - deferred deliberately
  so the strict-subset boundary stays honest for now.
- NOTE: `read_dxf` accepts `str` for test convenience but only `bytes` input exercises the
  binary-sentinel and byte-size paths; the future route/worker wiring must pass raw bytes.

END-OF-REPORT
