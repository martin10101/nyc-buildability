"""Tests for the zero-dependency glTF 2.0 binary (GLB) writer (task M5-T092,
D-087 3D-3), scenarios AS-1..AS-5.

Offline and deterministic: no network, no I/O beyond reading repo source for the
scope checks, stdlib + pytest only. A minimal in-test GLB parser (``parse_glb``)
re-reads the emitted bytes against the Khronos glTF 2.0 Specification v2.0.1
(sections 4.4.2 header, 4.4.3 chunks/padding, 3.6.1-3.6.2 buffers/accessors,
3.7.2 meshes) WITHOUT using the writer's helpers, and the expected positions are
recomputed here from the input with an independent restatement of the declared
foot->metre factor and axis mapping.
"""

import ast
import hashlib
import json
import math
import struct
from collections.abc import Sequence
from pathlib import Path

import pytest

from app.cad import glb_writer as g
from app.cad.glb_writer import (
    PROPOSED_LABEL,
    REFUSAL_CODES,
    GlbLocalFrame,
    GlbMesh,
    GlbValidationError,
    write_glb,
)

# Independent restatement of the declared mapping (NIST: 1 US survey foot =
# 1200/3937 m exactly; EPSG:2263 unit "US survey foot").
FT_TO_M = 1200 / 3937
MAGIC, JSON_TYPE, BIN_TYPE = 0x46546C67, 0x4E4F534A, 0x004E4942

# --------------------------------------------------------------------------- #
# Fixture: a box "Tower" (8 vertices / 12 triangles, outward CCW) and a flat
# "Lot slab" quad, different colours, local US survey feet. Pins the golden.
# --------------------------------------------------------------------------- #

X0, Y0, Z0, X1, Y1, Z1 = -20.5, 10.25, 0.0, 20.25, 70.75, 145.3
TOWER_POSITIONS = [
    (X0, Y0, Z0), (X1, Y0, Z0), (X1, Y1, Z0), (X0, Y1, Z0),
    (X0, Y0, Z1), (X1, Y0, Z1), (X1, Y1, Z1), (X0, Y1, Z1),
]
TOWER_INDICES = [
    0, 2, 1, 0, 3, 2,  # bottom (faces down)
    4, 5, 6, 4, 6, 7,  # top (faces up)
    0, 1, 5, 0, 5, 4,  # south
    1, 2, 6, 1, 6, 5,  # east
    2, 3, 7, 2, 7, 6,  # north
    3, 0, 4, 3, 4, 7,  # west
]
SLAB_POSITIONS = [(-33.3, -12.7, 0.0), (41.9, -12.7, 0.0), (41.9, 88.1, 0.0), (-33.3, 88.1, 0.0)]
SLAB_INDICES = [0, 1, 2, 0, 2, 3]
TOWER_COLOR = (0.8, 0.35, 0.1)
SLAB_COLOR = (0.2, 0.6, 0.3, 1.0)
FRAME = GlbLocalFrame(origin_easting_ft=987654.5, origin_northing_ft=201234.25,
                      origin_elevation_ft=11.5)

# sha256 of write_glb(fixture_meshes(), FRAME). Regenerate ONLY on a deliberate
# format change (and re-run the in-test parser suite).
GOLDEN_SHA256 = "30d79d80587f138eb0c060be445be81ad5a590e20248eb2d4e203e68189563c5"


def fixture_meshes() -> list[GlbMesh]:
    return [
        GlbMesh("Tower", TOWER_POSITIONS, TOWER_INDICES, TOWER_COLOR),
        GlbMesh("Lot slab", SLAB_POSITIONS, SLAB_INDICES, SLAB_COLOR),
    ]


def f32(value: float) -> float:
    return struct.unpack("<f", struct.pack("<f", value))[0]


def expected_gltf_point(p: tuple[float, float, float]) -> tuple[float, float, float]:
    """(east, north, up) US survey ft -> glTF (x, y up, z = -north) metres, float32."""
    x, y, z = p
    return (f32(x * FT_TO_M), f32(z * FT_TO_M), f32(-y * FT_TO_M))


# --------------------------------------------------------------------------- #
# Minimal GLB parser (independent of the writer internals).
# --------------------------------------------------------------------------- #

def parse_glb(data: bytes) -> tuple[dict, bytes]:
    """Validate the container per spec section 4.4 and return (json, bin)."""
    assert len(data) >= 12 and data[:4] == b"glTF"
    magic, version, length = struct.unpack_from("<III", data, 0)
    assert magic == MAGIC, "header magic"
    assert version == 2, "GLB container version"
    assert length == len(data), "header length must equal the total byte length"
    chunks: list[tuple[int, bytes]] = []
    offset = 12
    while offset < length:
        chunk_length, chunk_type = struct.unpack_from("<II", data, offset)
        start, end = offset + 8, offset + 8 + chunk_length
        assert end <= length, "chunk overruns the file"
        assert start % 4 == 0 and end % 4 == 0, "chunk start/end must be 4-byte aligned"
        chunks.append((chunk_type, data[start:end]))
        offset = end
    assert offset == length
    assert [t for t, _ in chunks] == [JSON_TYPE, BIN_TYPE], "chunk order JSON then BIN"
    json_data, bin_data = chunks[0][1], chunks[1][1]
    assert not json_data.startswith(b"\xef\xbb\xbf"), "JSON must not carry a BOM"
    text_end = json_data.rindex(b"}") + 1
    padding = json_data[text_end:]
    assert padding == b" " * len(padding), "JSON chunk must be padded with 0x20"
    assert len(padding) < 4
    doc = json.loads(json_data.decode("utf-8"))  # padded chunk parses as-is
    byte_length = doc["buffers"][0]["byteLength"]
    assert byte_length <= len(bin_data) <= byte_length + 3
    assert bin_data[byte_length:] == b"\x00" * (len(bin_data) - byte_length)
    return doc, bin_data


def read_accessor(doc: dict, bin_data: bytes, index: int) -> list[tuple]:
    accessor = doc["accessors"][index]
    view = doc["bufferViews"][accessor["bufferView"]]
    assert view["buffer"] == 0 and "byteStride" not in view
    fmt = {5126: "f", 5125: "I"}[accessor["componentType"]]
    width = {"SCALAR": 1, "VEC3": 3}[accessor["type"]]
    start = view["byteOffset"] + accessor.get("byteOffset", 0)
    assert start % 4 == 0
    count = accessor["count"] * width
    assert accessor.get("byteOffset", 0) + 4 * count <= view["byteLength"]
    assert view["byteOffset"] + view["byteLength"] <= doc["buffers"][0]["byteLength"]
    values = struct.unpack_from(f"<{count}{fmt}", bin_data, start)
    return [tuple(values[i : i + width]) for i in range(0, count, width)]


def all_strings(node: object) -> list[str]:
    if isinstance(node, str):
        return [node]
    if isinstance(node, dict):
        return [s for k, v in node.items() for s in [k, *all_strings(v)]]
    if isinstance(node, list):
        return [s for v in node for s in all_strings(v)]
    return []


# --------------------------------------------------------------------------- #
# AS-1 structure + determinism.
# --------------------------------------------------------------------------- #

def test_as1_header_and_chunk_layout() -> None:
    data = write_glb(fixture_meshes(), FRAME)
    doc, bin_data = parse_glb(data)
    assert struct.unpack_from("<I", data, 8)[0] == len(data)
    assert len(bin_data) == doc["buffers"][0]["byteLength"]  # 4-byte data: no BIN pad


@pytest.mark.parametrize("easting", [1.0, 10.0, 100.0, 1000.0])
def test_as1_json_chunk_padded_with_spaces(easting: float) -> None:
    data = write_glb(fixture_meshes(), GlbLocalFrame(easting, 5.0))
    json_length = struct.unpack_from("<I", data, 12)[0]
    json_data = data[20 : 20 + json_length]
    padding = json_data[json_data.rindex(b"}") + 1 :]
    assert padding == b" " * len(padding)
    parse_glb(data)


def test_as1_json_padding_lengths_cover_all_residues() -> None:
    """Guards the padding test against vacuity: pads of 0..3 bytes all occur."""
    seen = set()
    for easting in (1.0, 10.0, 100.0, 1000.0):
        data = write_glb(fixture_meshes(), GlbLocalFrame(easting, 5.0))
        json_data = data[20 : 20 + struct.unpack_from("<I", data, 12)[0]]
        seen.add(len(json_data) - (json_data.rindex(b"}") + 1))
    assert seen == {0, 1, 2, 3}


def test_as1_bin_chunk_pads_with_zeros() -> None:
    chunk = g._bin_chunk(b"\x01\x02\x03\x04\x05")
    length, chunk_type = struct.unpack_from("<II", chunk)
    assert (length, chunk_type) == (8, BIN_TYPE)
    assert chunk[8:] == b"\x01\x02\x03\x04\x05\x00\x00\x00"
    assert g._json_chunk(b"{}")[8:] == b"{}  "


def test_as1_golden_sha256_and_determinism() -> None:
    first = write_glb(fixture_meshes(), FRAME)
    second = write_glb(fixture_meshes(), FRAME)
    assert first == second
    assert hashlib.sha256(first).hexdigest() == GOLDEN_SHA256


def test_as1_json_essentials() -> None:
    doc, _ = parse_glb(write_glb(fixture_meshes(), FRAME))
    assert doc["asset"]["version"] == "2.0"
    assert "uri" not in doc["buffers"][0] and len(doc["buffers"]) == 1
    assert doc["scene"] == 0 and doc["scenes"][0]["nodes"] == [0, 1]
    for mesh in doc["meshes"]:
        (primitive,) = mesh["primitives"]
        assert primitive["mode"] == 4
        pos = doc["accessors"][primitive["attributes"]["POSITION"]]
        idx = doc["accessors"][primitive["indices"]]
        assert (pos["componentType"], pos["type"]) == (5126, "VEC3")
        assert len(pos["min"]) == len(pos["max"]) == 3
        assert (idx["componentType"], idx["type"]) == (5125, "SCALAR")
        assert idx["count"] % 3 == 0 and idx["count"] > 0
        assert doc["bufferViews"][pos["bufferView"]]["target"] == 34962
        assert doc["bufferViews"][idx["bufferView"]]["target"] == 34963
    for view in doc["bufferViews"]:
        assert view["byteOffset"] % 4 == 0


# --------------------------------------------------------------------------- #
# AS-2 content round trip.
# --------------------------------------------------------------------------- #

def test_as2_two_named_meshes_round_trip() -> None:
    doc, bin_data = parse_glb(write_glb(fixture_meshes(), FRAME))
    assert [n["name"] for n in doc["nodes"]] == ["Tower", "Lot slab"]
    assert [m["name"] for m in doc["meshes"]] == ["Tower", "Lot slab"]
    assert [n["mesh"] for n in doc["nodes"]] == [0, 1]
    colors = [m["pbrMetallicRoughness"]["baseColorFactor"] for m in doc["materials"]]
    assert colors == [[*TOWER_COLOR, 1.0], list(SLAB_COLOR)]
    for mesh, positions, indices in zip(
        doc["meshes"], (TOWER_POSITIONS, SLAB_POSITIONS), (TOWER_INDICES, SLAB_INDICES),
        strict=True,
    ):
        (primitive,) = mesh["primitives"]
        decoded = read_accessor(doc, bin_data, primitive["attributes"]["POSITION"])
        assert decoded == [expected_gltf_point(p) for p in positions]
        assert [i for (i,) in read_accessor(doc, bin_data, primitive["indices"])] == indices
        assert doc["accessors"][primitive["indices"]]["count"] == len(indices)
        assert doc["accessors"][primitive["attributes"]["POSITION"]]["count"] == len(positions)
    assert [m["primitives"][0]["material"] for m in doc["meshes"]] == [0, 1]


def test_as2_accessor_min_max_exact() -> None:
    doc, bin_data = parse_glb(write_glb(fixture_meshes(), FRAME))
    for mesh, positions in zip(doc["meshes"], (TOWER_POSITIONS, SLAB_POSITIONS), strict=True):
        index = mesh["primitives"][0]["attributes"]["POSITION"]
        accessor = doc["accessors"][index]
        decoded = read_accessor(doc, bin_data, index)
        expected = [expected_gltf_point(p) for p in positions]
        for axis in range(3):
            assert accessor["min"][axis] == min(v[axis] for v in decoded)
            assert accessor["max"][axis] == max(v[axis] for v in decoded)
            assert accessor["min"][axis] == min(v[axis] for v in expected)
            assert accessor["max"][axis] == max(v[axis] for v in expected)
            assert f32(accessor["min"][axis]) == accessor["min"][axis]  # float32-exact


def test_as2_shared_colour_and_default_material() -> None:
    meshes = [
        *fixture_meshes(),
        GlbMesh("Tower copy", TOWER_POSITIONS, TOWER_INDICES, (*TOWER_COLOR, 1.0)),
        GlbMesh("Context", SLAB_POSITIONS, SLAB_INDICES),
        GlbMesh("Glass", SLAB_POSITIONS, SLAB_INDICES, (0.5, 0.5, 0.9, 0.4)),
    ]
    doc, _ = parse_glb(write_glb(meshes, FRAME))
    materials = [m["primitives"][0].get("material") for m in doc["meshes"]]
    assert materials == [0, 1, 0, None, 2]
    assert len(doc["materials"]) == 3
    assert doc["materials"][2]["alphaMode"] == "BLEND"
    assert "alphaMode" not in doc["materials"][0]


def test_as2_winding_preserved_up_normal_maps_to_plus_y() -> None:
    mesh = GlbMesh("Pad", [(0.0, 0.0, 0.0), (10.0, 0.0, 0.0), (0.0, 10.0, 0.0)], [0, 1, 2])
    doc, bin_data = parse_glb(write_glb([mesh], FRAME))
    a, b, c = read_accessor(doc, bin_data, 0)
    u = [b[k] - a[k] for k in range(3)]
    v = [c[k] - a[k] for k in range(3)]
    normal = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
    assert normal[0] == 0 and normal[2] == 0 and normal[1] > 0  # source +z (up) -> glTF +Y


# --------------------------------------------------------------------------- #
# AS-3 units + honesty.
# --------------------------------------------------------------------------- #

def test_as3_unit_factor_is_us_survey_foot() -> None:
    assert g.US_SURVEY_FOOT_TO_METRE == 1200 / 3937
    assert g.US_SURVEY_FOOT_TO_METRE != 0.3048
    mesh = GlbMesh("Survey", [(0.0, 0.0, 0.0), (3937.0, 0.0, 0.0), (0.0, 3937.0, 3937.0)],
                   [0, 1, 2])
    doc, bin_data = parse_glb(write_glb([mesh], FRAME))
    assert read_accessor(doc, bin_data, 0) == [
        (0.0, 0.0, 0.0), (1200.0, 0.0, 0.0), (0.0, 1200.0, -1200.0),
    ]


def test_as3_axis_mapping_east_up_north() -> None:
    mesh = GlbMesh("Axes", [(1.0, 0.0, 0.0), (0.0, 2.0, 0.0), (0.0, 0.0, 3.0)], [0, 1, 2])
    doc, bin_data = parse_glb(write_glb([mesh], FRAME))
    east, north, up = read_accessor(doc, bin_data, 0)
    assert east == (f32(FT_TO_M), 0.0, 0.0)
    assert north == (0.0, 0.0, f32(-2.0 * FT_TO_M))
    assert up == (0.0, f32(3.0 * FT_TO_M), 0.0)


def test_as3_provenance_recorded_in_asset() -> None:
    doc, _ = parse_glb(write_glb(fixture_meshes(), FRAME))
    asset = doc["asset"]
    assert PROPOSED_LABEL == "Proposed - not a city record"
    assert PROPOSED_LABEL in asset["generator"]
    extras = asset["extras"]
    assert extras["label"] == PROPOSED_LABEL
    assert doc["scenes"][0]["name"] == PROPOSED_LABEL
    assert extras["sourceCrs"] == "EPSG:2263"
    assert extras["sourceUnit"] == "US survey foot"
    assert extras["metresPerSourceUnit"] == "1200/3937"
    assert extras["metresPerSourceUnitDecimal"] == FT_TO_M
    assert extras["axisMapping"] == {
        "gltfX": "+source x (east)", "gltfY": "+source z (up)", "gltfZ": "-source y (north)",
    }
    origin = extras["localOrigin"]
    assert (origin["crs"], origin["eastingFt"], origin["northingFt"], origin["elevationFt"]) == (
        "EPSG:2263", 987654.5, 201234.25, 11.5,
    )
    assert "3937/1200" in origin["note"]


def test_as3_no_claim_class_words_anywhere() -> None:
    doc, _ = parse_glb(write_glb(fixture_meshes(), FRAME))
    text = " ".join(all_strings(doc)).upper()
    for word in ("PERMITTED", "APPROVED", "CERTIFIED", "COMPLIANT", "LEGAL", "MAXIMUM ALLOWED",
                 "AS OF RIGHT", "GUARANTEED"):
        assert word not in text


# --------------------------------------------------------------------------- #
# AS-4 fail-closed refusals.
# --------------------------------------------------------------------------- #

def _mesh(**overrides: object) -> GlbMesh:
    fields = {"name": "M", "positions": SLAB_POSITIONS, "indices": SLAB_INDICES,
              "base_color": None}
    fields.update(overrides)
    return GlbMesh(**fields)  # type: ignore[arg-type]


BAD_CASES = [
    ("nan_position", [_mesh(positions=[(math.nan, 0.0, 0.0), *SLAB_POSITIONS[1:]])],
     "non_finite_value"),
    ("inf_position", [_mesh(positions=[(0.0, math.inf, 0.0), *SLAB_POSITIONS[1:]])],
     "non_finite_value"),
    ("neg_inf_position", [_mesh(positions=[(0.0, 0.0, -math.inf), *SLAB_POSITIONS[1:]])],
     "non_finite_value"),
    ("nan_color", [_mesh(base_color=(0.1, math.nan, 0.1))], "non_finite_value"),
    ("color_range", [_mesh(base_color=(0.1, 1.5, 0.1))], "invalid_color"),
    ("color_arity", [_mesh(base_color=(0.1, 0.1))], "invalid_color"),
    ("index_eq_count", [_mesh(indices=[0, 1, 4])], "index_out_of_range"),
    ("index_negative", [_mesh(indices=[0, 1, -1])], "index_out_of_range"),
    ("index_float", [_mesh(indices=[0, 1, 2.0])], "invalid_index"),
    ("index_bool", [_mesh(indices=[0, 1, True])], "invalid_index"),
    ("not_triangles", [_mesh(indices=[0, 1, 2, 0])], "index_count_not_triangles"),
    ("empty_positions", [_mesh(positions=[], indices=[])], "empty_mesh"),
    ("empty_indices", [_mesh(indices=[])], "empty_mesh"),
    ("repeated_index", [_mesh(indices=[0, 0, 1])], "degenerate_triangle"),
    ("collinear", [_mesh(positions=[(0.0, 0.0, 0.0), (1.0, 1.0, 1.0), (2.0, 2.0, 2.0)],
                         indices=[0, 1, 2])], "degenerate_triangle"),
    ("coincident", [_mesh(positions=[(5.0, 5.0, 5.0)] * 3, indices=[0, 1, 2])],
     "degenerate_triangle"),
    ("bad_triple", [_mesh(positions=[(0.0, 0.0), *SLAB_POSITIONS[1:]])], "invalid_position"),
    ("string_coord", [_mesh(positions=[("0", 0.0, 0.0), *SLAB_POSITIONS[1:]])],
     "invalid_position"),
    ("world_coords", [_mesh(positions=[(987654.0, 201234.0, 0.0), *SLAB_POSITIONS[1:]])],
     "coordinate_out_of_range"),
    ("no_meshes", [], "no_meshes"),
    ("not_a_mesh", [("M", SLAB_POSITIONS, SLAB_INDICES)], "invalid_mesh"),
    ("bad_name", [_mesh(name="A\nB")], "invalid_mesh_name"),
    ("empty_name", [_mesh(name="")], "invalid_mesh_name"),
    ("quote_name", [_mesh(name='A"B')], "invalid_mesh_name"),
    ("claim_word", [_mesh(name="Maximum allowed building")], "claim_class_word"),
    ("claim_word_2", [_mesh(name="Approved massing")], "claim_class_word"),
    ("duplicate", [_mesh(), _mesh()], "duplicate_mesh_name"),
]


@pytest.mark.parametrize(("meshes", "code"), [c[1:] for c in BAD_CASES],
                         ids=[c[0] for c in BAD_CASES])
def test_as4_typed_refusals(meshes: list, code: str) -> None:
    assert code in REFUSAL_CODES
    with pytest.raises(GlbValidationError) as info:
        write_glb(meshes, FRAME)
    assert info.value.code == code


@pytest.mark.parametrize(("frame", "code"), [
    (GlbLocalFrame(math.nan, 0.0), "non_finite_value"),
    (GlbLocalFrame(0.0, 0.0, math.inf), "non_finite_value"),
    (GlbLocalFrame(1e9, 0.0), "coordinate_out_of_range"),
    (GlbLocalFrame("1", 0.0), "invalid_frame"),  # type: ignore[arg-type]
    (None, "invalid_frame"),
])
def test_as4_frame_refusals(frame: object, code: str) -> None:
    with pytest.raises(GlbValidationError) as info:
        write_glb(fixture_meshes(), frame)  # type: ignore[arg-type]
    assert info.value.code == code


class _Unreadable(Sequence):
    """Sized sequence whose elements must never be read (cap-before-read proof)."""

    def __init__(self, length: int) -> None:
        self._length = length

    def __len__(self) -> int:
        return self._length

    def __getitem__(self, index):  # noqa: ANN001
        raise AssertionError("element read before the cap check")


def test_as4_vertex_cap_refused_before_reading() -> None:
    mesh = GlbMesh("Big", _Unreadable(g.MAX_TOTAL_VERTICES + 1), [0, 1, 2])
    with pytest.raises(GlbValidationError) as info:
        write_glb([mesh], FRAME)
    assert info.value.code == "vertex_cap_exceeded"


def test_as4_index_cap_refused_before_reading() -> None:
    mesh = GlbMesh("Big", SLAB_POSITIONS, _Unreadable(g.MAX_TOTAL_INDICES + 1))
    with pytest.raises(GlbValidationError) as info:
        write_glb([mesh], FRAME)
    assert info.value.code == "index_cap_exceeded"


class _Outrunning(Sequence):
    """Declares a small length but its iteration never ends."""

    def __init__(self, length: int, item: object) -> None:
        self._length, self._item = length, item

    def __len__(self) -> int:
        return self._length

    def __getitem__(self, index):  # noqa: ANN001
        return self._item  # never raises IndexError: iteration would run forever


def test_as4_iteration_bounded_by_declared_length() -> None:
    mesh = GlbMesh("Liar", _Outrunning(3, (1.0, 2.0, 3.0)), [0, 1, 2])
    with pytest.raises(GlbValidationError) as info:
        write_glb([mesh], FRAME)
    assert info.value.code == "invalid_position"
    liar_indices = GlbMesh("Liar", SLAB_POSITIONS, _Outrunning(3, 0))
    with pytest.raises(GlbValidationError) as info:
        write_glb([liar_indices], FRAME)
    assert info.value.code == "invalid_index"


def test_as4_vertex_cap_is_a_total_across_meshes(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(g, "MAX_TOTAL_VERTICES", 11)  # fixture has 8 + 4 = 12
    with pytest.raises(GlbValidationError) as info:
        write_glb(fixture_meshes(), FRAME)
    assert info.value.code == "vertex_cap_exceeded"


def test_as4_mesh_cap(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(g, "MAX_MESHES", 1)
    with pytest.raises(GlbValidationError) as info:
        write_glb(fixture_meshes(), FRAME)
    assert info.value.code == "mesh_cap_exceeded"


def test_as4_refusal_yields_no_partial_output(monkeypatch: pytest.MonkeyPatch) -> None:
    """A defect in the LAST mesh refuses before any assembly starts."""
    calls: list[int] = []
    real_assemble = g._assemble

    def spy(prepared, frame):  # noqa: ANN001
        calls.append(1)
        return real_assemble(prepared, frame)

    monkeypatch.setattr(g, "_assemble", spy)
    bad_last = [*fixture_meshes(), _mesh(indices=[0, 1, 9])]
    with pytest.raises(GlbValidationError):
        write_glb(bad_last, FRAME)
    assert calls == []
    assert hashlib.sha256(write_glb(fixture_meshes(), FRAME)).hexdigest() == GOLDEN_SHA256
    assert calls == [1]


def test_as4_error_codes_are_registered() -> None:
    with pytest.raises(ValueError):
        GlbValidationError("made_up_code", "x")


# --------------------------------------------------------------------------- #
# AS-5 scope: stdlib only, not wired.
# --------------------------------------------------------------------------- #

API_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = API_ROOT / "app" / "cad" / "glb_writer.py"


def test_as5_stdlib_imports_only() -> None:
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.add((node.module or "").split(".")[0])
    assert imported == {"__future__", "collections", "dataclasses", "json", "math", "numbers",
                        "struct"}


def test_as5_not_wired_into_the_app() -> None:
    importers = [
        path.relative_to(API_ROOT).as_posix()
        for path in (API_ROOT / "app").rglob("*.py")
        if path != MODULE_PATH and "glb_writer" in path.read_text(encoding="utf-8")
    ]
    assert importers == []
