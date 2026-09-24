# M5-T092 producer report — zero-dependency glTF 2.0 binary (GLB) writer (D-087 3D-3)

Producer: backend-engineer (orchestrator-dispatched subagent). Worktree
`C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t092`, branch `task/M5-T092-glb-writer`, parent
`114e5e56e158d6f263e58a314c383ea62ee7eff4` (claim-seam head; checked at start: toplevel = wt-m5t092,
HEAD = 114e5e56, status clean). One commit containing only the three allowed paths. A commit cannot
record its own sha, so the orchestrator return carries the commit sha. Requested status: **awaiting_gate**.

## IMPLEMENTATION

- `services/api/app/cad/glb_writer.py` (replaces the placeholder; sha256 LF
  `77404465db9f3af4c882d1fa047d88ac413059c8a38bc4fc24ecf369e0ca37ed`). Public API:
  `write_glb(meshes: Sequence[GlbMesh], frame: GlbLocalFrame) -> bytes` (:578),
  `GlbMesh(name, positions, indices, base_color=None)`, `GlbLocalFrame(origin_easting_ft,
  origin_northing_ft, origin_elevation_ft=0.0)`, `GlbValidationError(code, field)` /
  `GlbWriterError`, `REFUSAL_CODES` (:181). Output: one node + one mesh (one indexed TRIANGLES
  primitive) per input mesh in input order, one material per distinct base colour (a mesh
  without a colour uses the default material), one float32 VEC3 POSITION accessor (exact
  min/max) and one uint32 SCALAR index accessor per mesh, one bufferView per accessor with a
  target, a single GLB-stored buffer, `asset.generator` + `asset.extras` provenance.
  Pure: stdlib only (`json`, `math`, `numbers`, `struct`, `dataclasses`, `collections.abc`),
  no I/O, no clock, no network, no module-level mutable state.
- `services/api/tests/cad/test_glb_writer.py` (replaces the placeholder; sha256 LF
  `9b7820d61507ab3b96d14be0385dc4c515346ebef93a0f7959d35743f999ae0c`), 58 tests. It contains
  an in-test GLB parser `parse_glb` (:89) and accessor decoder `read_accessor` (:120) that
  do not use the writer's helpers, and an independent restatement of the foot-to-metre factor
  and axis mapping (`FT_TO_M` :35, `expected_gltf_point` :79).
- Size: the module has 597 physical lines, about 450 SLOC by the policy heuristic, which is under the 600
  warning threshold. `modularity_check --check` has 0 failures and does not flag the new files.
  The module has one job: a GLB serializer with its input validation.

## Format authority (spec citations)

[OBSERVED] Khronos glTF 2.0 Specification **version 2.0.1, 2021-10-11, git commit 8e798b02**,
fetched read-only from https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html on 2026-09-24
(HTML sha256 `182088415705f5c66583a1095f8908ffcebd0fabc93b402d857ffcd63c1d7cdb`). Every constant
was **checked against the fetched text**, so none of the format constants is marked
`[recalled - verify]`:

| Constant (glb_writer.py) | Spec section | Checked text (abridged) |
|---|---|---|
| `GLB_MAGIC = 0x46546C67` :88 | 4.4.2 | "magic MUST be equal to equal 0x46546C67. It is ASCII string glTF" |
| `GLB_VERSION = 2` :90 | 4.4.2 | "This specification defines version 2." |
| header `length` = total bytes :597 | 4.4.2 | "total length of the Binary glTF, including header and all chunks" |
| `CHUNK_TYPE_JSON 0x4E4F534A` / `CHUNK_TYPE_BIN 0x004E4942` :92/:94 | 4.4.3.1 Table 1 | JSON first (1), BIN second (0 or 1) |
| `CHUNK_ALIGNMENT = 4` :101 | 4.4.3.1 | "start and the end of each chunk MUST be aligned to a 4-byte boundary" |
| `JSON_PAD_BYTE = 0x20` :96 | 4.4.3.2 | "MUST be padded with trailing Space chars (0x20)" |
| `BIN_PAD_BYTE = 0x00` :98 | 4.4.3.3 | "MUST be padded with trailing zeros (0x00)" |
| little-endian `struct` `<` | 4.4.1, 3.6.1.1 | "Binary glTF is little endian"; buffer data "MUST use little endian" |
| `COMPONENT_FLOAT 5126` / `COMPONENT_UNSIGNED_INT 5125` :103/:105 | 3.6.2.2, 5.1.3 | UNSIGNED_INT "MUST NOT be used for any accessor that is not referenced by mesh.primitive.indices" (honoured) |
| `TARGET_ARRAY_BUFFER 34962` / `TARGET_ELEMENT_ARRAY_BUFFER 34963` :107/:109 | 5.11.5 | allowed values |
| `MODE_TRIANGLES = 4` :111 | 5.24.4 | "4 TRIANGLES" |
| `GLTF_ASSET_VERSION = "2.0"` :113 | 3.2, 5.9.3 | asset.version required |
| POSITION min/max required and exact | 3.7.2.1, 3.6.2.5 | "POSITION accessor MUST have its min and max properties defined"; "MUST match actual minimum and maximum binary values stored in buffers" |
| buffers[0] has no uri; BIN chunk ≤ byteLength+3 :560 | 3.6.1.2 | GLB-stored buffer "MUST be the first element... buffer.uri property undefined" |
| index < POSITION count; no 4294967295; count % 3 == 0 | 3.7.2.1 | as quoted in code comment :423-425 |
| no NaN/Inf | 3.6.2.2 | "Values of NaN, +Infinity, and -Infinity MUST NOT be present." |
| metres, +Y up | 3.4 | "+Y as up... The units for all linear distances are meters." |
| winding preserved by det +1 | 3.7.4 | "If the determinant is a positive value, the winding order triangle faces is counterclockwise" |
| no NORMAL written | 3.7.2.1 | "When normals are not specified, client implementations MUST calculate flat normals" |
| `GLB_MEDIA_TYPE = "model/gltf-binary"` :115 | 4.3 | registered media type |
| JSON UTF-8 no BOM, ASCII unescaped | 2.7 | SHOULD-level; names limited to `[A-Za-z0-9 _-.]` so nothing is escaped |

Units and CRS [OBSERVED]: EPSG:2263 WKT from https://epsg.io/2263.wkt (sha256
`f2df9458…d9db429a6`): `UNIT["US survey foot",0.304800609601219]`, `AXIS["Easting",EAST]`,
`AXIS["Northing",NORTH]`. NIST https://www.nist.gov/pml/us-surveyfoot (sha256 `1d0bf6c7…a616579`):
"1 foot = 1200/3937 meter exactly". [DERIVED, not specified by glTF] The axis map
`(x east, y north, z up) -> glTF (x, z, -y)` is a -90° rotation about X (det +1). It is the
usual Z-up to Y-up convention. I believe common tools (for example Blender's glTF +Y-up
export) do the same, but that is `[recalled - verify]`. Correctness does not rest on it:
tests AS-3 and the winding test prove the mapping directly.

## Per-scenario evidence

- **AS-1 (structure)** [OBSERVED]: `test_as1_header_and_chunk_layout` (:149) checks the magic,
  version 2 and total length through `parse_glb`, which also checks 4-byte chunk start/end, chunk
  order and the BOM. `test_as1_json_chunk_padded_with_spaces` (:157, 4 params) checks that the
  JSON padding is 0x20. `test_as1_json_padding_lengths_cover_all_residues` (:166) proves the
  padding tests are not vacuous: pads of 0, 1, 2 and 3 bytes all occur.
  `test_as1_bin_chunk_pads_with_zeros` (:176) checks zero padding for BIN and space padding for
  JSON at the chunk helper. `test_as1_golden_sha256_and_determinism` (:184) pins golden
  `30d79d80587f138eb0c060be445be81ad5a590e20248eb2d4e203e68189563c5` (:65) and checks that two
  independent calls return the same bytes. `test_as1_json_essentials` (:191) checks
  asset.version "2.0", buffers[0] without a uri, scene/nodes, mode 4, componentType/type pairs,
  min/max length 3, the targets 34962/34963 and 4-aligned view offsets.
- **AS-2 (content)** [OBSERVED]: `test_as2_two_named_meshes_round_trip` (:215) round-trips the
  "Tower" box (8 vertices, 12 triangles) and the "Lot slab" quad, which have different colours.
  Node and mesh names, node→mesh links, material colours, index counts and values, and the
  decoded positions all match exactly `expected_gltf_point(input)` (independent factor and axis
  map, float32). `test_as2_accessor_min_max_exact` (:235) checks that min/max equal the per-axis
  extremes of the decoded BIN, equal the extremes of the independently mapped input, and are
  float32-exact. `test_as2_shared_colour_and_default_material` (:250) checks that the same
  colour (RGB vs RGBA with alpha 1) shares one material, that an uncoloured mesh has no
  material, and that alpha < 1 gives BLEND. `test_as2_winding_preserved_up_normal_maps_to_plus_y` (:265).
- **AS-3 (units + honesty)** [OBSERVED]: `test_as3_unit_factor_is_us_survey_foot` (:279) checks
  that the constant equals 1200/3937 and not 0.3048, and that 3937 ft decodes to exactly
  1200.0 m. `test_as3_axis_mapping_east_up_north` (:290) checks east→+X, up→+Y, north→−Z.
  `test_as3_provenance_recorded_in_asset` (:299) checks the label "Proposed - not a city record" in
  `asset.generator`, `asset.extras.label` and the scene name, plus sourceCrs EPSG:2263,
  sourceUnit, "1200/3937" + decimal, axisMapping, and localOrigin (crs, easting, northing,
  elevation) with the reconstruction note. `test_as3_no_claim_class_words_anywhere` (:321).
  The skipped-conversion mutation reddens (M5 below).
- **AS-4 (fail-closed)** [OBSERVED]: `test_as4_typed_refusals` (:380, 27 cases, :340) covers
  NaN/±Inf positions and colours, colours out of range or with the wrong arity, an index equal
  to the vertex count, a negative index, float/bool indices, an index count that is not a
  multiple of 3, empty positions or indices, a repeated index, collinear or coincident
  triangles, a malformed triple, a string coordinate, un-localized world coordinates, no
  meshes, a non-mesh, bad/empty/quoted names, claim-class names and duplicate names.
  `test_as4_frame_refusals` (:394) covers the frame refusals. The caps are enforced before any
  vertex or index is read: `test_as4_vertex_cap_refused_before_reading` (:413) and
  `..._index_cap_...` (:420) use a sequence that raises if any element is read;
  `test_as4_iteration_bounded_by_declared_length` (:440) covers a sequence that iterates past
  its declared length; `..._vertex_cap_is_a_total_across_meshes` (:451); `test_as4_mesh_cap`
  (:458). `test_as4_refusal_yields_no_partial_output` (:465) spies `_assemble`: a defect in the
  LAST mesh refuses before assembly starts, and the next valid call still matches the golden.
  `test_as4_error_codes_are_registered` (:483). Refusals are typed only: `GlbValidationError.code`
  must be in `REFUSAL_CODES`.
- **AS-5 (scope)** [OBSERVED]: `test_as5_stdlib_imports_only` (:496) is an AST import check: the
  imports are exactly {__future__, collections, dataclasses, json, math, numbers, struct}.
  `test_as5_not_wired_into_the_app` (:508): no file under `app/` other than the module itself
  mentions `glb_writer`. There are no route, main.py, web, requirements or lockfile changes, and
  the diff touches only the three allowed paths (`git status` below). ruff and modularity are
  clean (self-checks below).

## Mutation table [OBSERVED]

Harness: scratchpad script (outside the repo). For each mutant it replaces one pattern that
occurs exactly once in `glb_writer.py`, runs `python -m pytest tests/cad/test_glb_writer.py -q -rf
-p no:cacheprovider` from `services/api`, restores the original bytes and re-checks the sha256.
Baseline was 58 passed. After the restore run there were 58 passed, and the module sha256 was
`77404465…ca37ed` before and after. Harness exit 0.

| # | Mutation | Result | Named reddened tests (subset) |
|---|---|---|---|
| M1 | JSON pad 0x20→0x00 (**wrong padding char**) | RED 15 failed | `test_as1_json_chunk_padded_with_spaces[1.0/10.0/100.0]`, `test_as1_bin_chunk_pads_with_zeros`, `test_as1_header_and_chunk_layout`, golden ([1000.0] has pad 0, correctly green) |
| M2 | BIN pad 0x00→0x20 (**wrong padding char**) | RED 1 failed | `test_as1_bin_chunk_pads_with_zeros` |
| M3 | max[Y] computed with `min` (**accessor min/max off**) | RED 3 failed | `test_as2_accessor_min_max_exact`, golden |
| M4 | min − 1e-6 (**accessor min/max off**) | RED 3 failed | `test_as2_accessor_min_max_exact`, golden |
| M5 | **unit conversion skipped** | RED 6 failed | `test_as2_two_named_meshes_round_trip`, `test_as3_unit_factor_is_us_survey_foot`, `test_as3_axis_mapping_east_up_north`, `test_as2_accessor_min_max_exact`, golden |
| M6 | international foot 0.3048 | RED 7 failed | `test_as3_unit_factor_is_us_survey_foot`, `test_as3_provenance_recorded_in_asset`, round trip, golden |
| M7 | axis mapping skipped | RED 7 failed | `test_as3_axis_mapping_east_up_north`, `test_as2_winding_preserved_up_normal_maps_to_plus_y`, round trip, golden |
| M8 | header length omits the 12-byte header | RED 16 failed | `test_as1_header_and_chunk_layout` + every parse_glb user |
| M9 | index bound `<=` count accepted | RED 1 failed | `test_as4_typed_refusals[index_eq_count]` |
| M10 | degenerate check disabled | RED 3 failed | `test_as4_typed_refusals[repeated_index/collinear/coincident]` |
| M11 | vertex cap skipped | RED 2 failed | `test_as4_vertex_cap_refused_before_reading`, `..._total_across_meshes` |
| M12 | non-finite check removed | RED 6 failed | `test_as4_typed_refusals[nan/inf/neg_inf_position, nan_color]`, `test_as4_frame_refusals[frame0/frame1]` |
| M13 | claim-class name check disabled | RED 2 failed | `test_as4_typed_refusals[claim_word, claim_word_2]` |

Note on M2: the public path never emits BIN padding, because float32 and uint32 payloads are
always 4-byte multiples. The BIN padding rule is therefore proven at the `_bin_chunk` helper.
The parser still asserts that any BIN tail past `byteLength` is zero.

## Self-checks (verbatim)

```
$ (cwd services/api) python -m ruff check .
All checks passed!
exit=0
$ (cwd services/api) python -m pytest tests/cad/test_glb_writer.py -q
..........................................................               [100%]
58 passed in 0.81s
exit=0
$ (cwd worktree root) python tools/modularity_check.py --check
selected 486 files; failures 0; warnings 23
exit=0   (the 23 warnings are all pre-existing files; none mentions glb)
```

Extra check: `(cwd services/api) python -m pytest tests/cad -q` gave `101 passed` (the sibling
DXF/PDF suites are unaffected). Local interpreter: Python 3.11.9. CI runs 3.12, and the code uses
nothing that is specific to either version.

## Deviations / decisions (for reviewers)

1. Materials use `metallicFactor 0.0` and `roughnessFactor 1.0` (matte). The spec default,
   metallic 1, renders dark without an environment map. `doubleSided` is left at the spec
   default (false), so callers must supply outward CCW winding. The writer preserves winding.
2. Local coordinates are capped at ±100,000 ft. This limits float32 precision loss to about
   2 mm and refuses un-localized EPSG:2263 coordinates. Totals are capped at 1,000 meshes,
   500k vertices and 1.5M indices, so the output is at most about 12 MB of geometry.
3. A triangle is degenerate when the sine of the angle at its first vertex is ≤ 1e-6, measured
   on the float32 values actually written. This refuses repeated, coincident and collinear
   vertices.
4. The claim-class word list is duplicated from `dxf_writer.CLAIM_CLASS_WORDS`, not imported.
   The sibling is in rework and is a forbidden path, and importing it would couple the two
   writers. See DISCOVERIES.
5. Errors are raised as typed exceptions, the same as the DXF sibling. The PDF sibling returns
   refusal values instead. The packet asks for "typed refusals", and both styles satisfy it.

## Limitations / routed to harvest

- [BLOCKED → harvest] I did not run the official Khronos glTF-Validator. It is an npm/Dart
  tool, and this thin client allows no local npm. Recipe: from `services/api`, run
  `python -c "from tests.cad.test_glb_writer import fixture_meshes, FRAME; from app.cad.glb_writer import write_glb; open('golden.glb','wb').write(write_glb(fixture_meshes(), FRAME))"`,
  then drop `golden.glb` into https://github.khronos.org/glTF-Validator/ (validation runs in the
  browser). Expected: 0 errors. Delete the file afterwards. Structural conformance is proven
  here only by the in-test parser against the cited sections.
- The code-graph query returned `STALE (stale fingerprint): refusing to serve the cached graph`.
  I checked "nothing imports glb_writer" by grepping `services/api` instead, and the AS-5 test
  enforces it.

## DISCOVERIES (D-069; not fixed in-packet)

1. **Vertical datum is unowned.** EPSG:2263 is horizontal only. The writer records
   `origin_elevation_ft` as caller-declared and states "vertical datum not asserted". The wiring
   packet must decide what local z = 0 means (lot grade? NAVD88?) before any GLB is placed next
   to other 3D data.
2. **Winding contract for the massing wiring packet.** The default material culls back faces,
   so the massing-to-mesh adapter must emit outward CCW triangles or deliberately opt into
   double-sided materials. This belongs in the wiring packet's acceptance scenarios.
3. **Honesty vocabulary is duplicated** (the DXF writer, and now the GLB writer, each carry a
   CLAIM_CLASS_WORDS list). A shared cad-honesty vocabulary module could be extracted in a
   later packet, keeping compatibility facades.
4. The code-graph cache was stale at this worktree's head, even though the packet said it was
   regenerated at the contract seam.

END-OF-REPORT
