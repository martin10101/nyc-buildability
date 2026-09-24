"""Zero-dependency glTF 2.0 binary (GLB) writer for proposed 3D geometry
(task M5-T092, D-087 3D-3).

Purpose: turn a GENERIC list of named triangle meshes (float positions in a
declared local frame + uint32 triangle indices + an optional base colour) into
one deterministic GLB file - the runtime format the 3D architecture names for
browser viewers and 3D downloads (D-087-R003/R006). The input is deliberately
independent of the massing model's shape; wiring to a route or the massing truth
object is a later gated packet. Nothing imports this module yet.

Commitments:

* STDLIB ONLY - ``json``, ``math``, ``numbers``, ``struct``, ``dataclasses``.
  No new dependency, no network, no I/O: :func:`write_glb` returns ``bytes`` and
  the caller decides where they go. Identical inputs give byte-identical output
  (a golden sha256 is pinned in the tests).
* FORMAT AUTHORITY - the Khronos glTF 2.0 Specification, version 2.0.1
  (2021-10-11, git commit 8e798b02), https://registry.khronos.org/glTF/specs/
  2.0/glTF-2.0.html, read on 2026-09-24. Every constant below cites the section
  it was CHECKED against; nothing here is recalled-only (see the axis-mapping
  note for the one convention that is derived rather than specified).
* UNITS + AXES - the input frame is EPSG:2263 (NAD83 / New York Long Island,
  ftUS: axes Easting EAST, Northing NORTH; unit "US survey foot"
  0.304800609601219 m, per the EPSG WKT) shifted to a declared local origin,
  with z = height up in the same US survey feet. glTF linear units are metres
  and +Y is up (spec section 3.4). The writer therefore (1) multiplies every
  coordinate by the US survey foot 1200/3937 m (exact; NIST "U.S. Survey Foot"
  page: "1 foot = 1200/3937 meter exactly") - NOT the international foot 0.3048
  - and (2) maps axes (east, north, up) -> glTF (+X, +Y, +Z) as
  (x, y, z) -> (x, z, -y): east -> +X, up -> +Y, north -> -Z. That map is a
  proper rotation (-90 degrees about X, determinant +1), so right-handedness
  and triangle winding are preserved (spec section 3.7.4: with a
  positive-determinant node transform - here identity - front faces are
  counter-clockwise). Both the factor and the mapping are recorded verbatim in
  ``asset.extras`` together with the local-origin note. No NORMAL attribute is
  written: "When normals are not specified, client implementations MUST
  calculate flat normals" (spec section 3.7.2.1) - the right shading for planar
  massing faces.
* FLOAT32 HONESTY - positions are stored as IEEE-754 single precision (spec
  section 3.6.2.2). The POSITION accessor ``min``/``max`` are computed from the
  float32 values actually written, so they "MUST match actual minimum and maximum
  binary values stored in buffers" (spec section 3.6.2.5) exactly. Local
  coordinates are capped at +/-100,000 US survey feet: that keeps the float32
  step at or below ~2 mm and refuses un-localized EPSG:2263 world coordinates
  (eastings are ~9e5-1.07e6 ft), which float32 would round to ~3 cm steps.
* FAIL CLOSED - non-finite values, index out of range, empty or degenerate
  meshes, over-cap mesh/vertex/index counts, invalid names/colours and claim-
  class words each raise :class:`GlbValidationError` with a machine-readable
  ``code``. Counts are capped BEFORE any vertex or index is read, and the file is
  assembled in memory and returned only on success, so a refusal never yields
  partial output.
* HONESTY (D-073-R006 / D-076-R002 / D-083) - ``asset.generator``,
  ``asset.extras.label`` and the scene name carry "Proposed - not a city
  record". Mesh names may not contain a claim-class word (permitted, approved,
  "maximum allowed", ...). This module writes geometry only and draws no legal
  conclusion.
"""

from __future__ import annotations

import json
import math
import numbers
import struct
from collections.abc import Iterator, Sequence
from dataclasses import dataclass

__all__ = [
    "AXIS_MAPPING",
    "GLB_MEDIA_TYPE",
    "GENERATOR",
    "PROPOSED_LABEL",
    "REFUSAL_CODES",
    "SOURCE_CRS",
    "US_SURVEY_FOOT_TO_METRE",
    "GlbLocalFrame",
    "GlbMesh",
    "GlbValidationError",
    "GlbWriterError",
    "write_glb",
]

# --------------------------------------------------------------------------- #
# Format constants - Khronos glTF 2.0 Specification v2.0.1 (checked 2026-09-24).
# --------------------------------------------------------------------------- #

#: Section 4.4.2: "magic MUST be equal to equal 0x46546C67. It is ASCII string glTF".
GLB_MAGIC = 0x46546C67
#: Section 4.4.2: "This specification defines version 2" (the container version).
GLB_VERSION = 2
#: Section 4.4.3.1, Table 1: chunk type JSON (must be first, exactly once).
CHUNK_TYPE_JSON = 0x4E4F534A
#: Section 4.4.3.1, Table 1: chunk type BIN (second, 0 or 1 occurrences).
CHUNK_TYPE_BIN = 0x004E4942
#: Section 4.4.3.2: the JSON chunk "MUST be padded with trailing Space chars (0x20)".
JSON_PAD_BYTE = b"\x20"
#: Section 4.4.3.3: the BIN chunk "MUST be padded with trailing zeros (0x00)".
BIN_PAD_BYTE = b"\x00"
#: Section 4.4.3.1: "The start and the end of each chunk MUST be aligned to a
#: 4-byte boundary."
CHUNK_ALIGNMENT = 4
#: Section 3.6.2.2 / 5.1.3: componentType 5126 = float (IEEE-754 single).
COMPONENT_FLOAT = 5126
#: Section 3.6.2.2 / 5.1.3: componentType 5125 = unsigned int (indices only).
COMPONENT_UNSIGNED_INT = 5125
#: Section 5.11.5: bufferView.target 34962 ARRAY_BUFFER (vertex attributes).
TARGET_ARRAY_BUFFER = 34962
#: Section 5.11.5: bufferView.target 34963 ELEMENT_ARRAY_BUFFER (indices).
TARGET_ELEMENT_ARRAY_BUFFER = 34963
#: Section 5.24.4: mesh.primitive.mode 4 = TRIANGLES.
MODE_TRIANGLES = 4
#: Section 3.2 / 5.9.3: asset.version (pattern ^[0-9]+\.[0-9]+$) is required.
GLTF_ASSET_VERSION = "2.0"
#: Section 4.3: the registered media type (for a later download route).
GLB_MEDIA_TYPE = "model/gltf-binary"
#: Section 3.6.1.1: a GLB-stored buffer has an implicit limit of 2^32-1 bytes;
#: section 4.4.2: the header length is a uint32.
_UINT32_MAX = 0xFFFFFFFF

_HEADER = struct.Struct("<III")  # section 4.4.1: "Binary glTF is little endian"
_CHUNK_HEADER = struct.Struct("<II")
_F32 = struct.Struct("<f")

# --------------------------------------------------------------------------- #
# Units, axes and provenance (recorded verbatim in asset.extras).
# --------------------------------------------------------------------------- #

SOURCE_CRS = "EPSG:2263"
SOURCE_UNIT = "US survey foot"
#: Metres per US survey foot - 1200/3937 exactly (NIST), NOT 0.3048.
US_SURVEY_FOOT_TO_METRE = 1200 / 3937
US_SURVEY_FOOT_TO_METRE_EXACT = "1200/3937"

#: Declared axis mapping from the local EPSG:2263-aligned frame to glTF.
AXIS_MAPPING: dict[str, str] = {
    "gltfX": "+source x (east)",
    "gltfY": "+source z (up)",
    "gltfZ": "-source y (north)",
}

PROPOSED_LABEL = "Proposed - not a city record"
GENERATOR = f"NYC Buildability GLB writer v1 (M5-T092) - {PROPOSED_LABEL}"

#: Claim-class words barred from caller-supplied names (upper-cased substring
#: match). Only affirmative legal/approval claims are barred.
CLAIM_CLASS_WORDS: tuple[str, ...] = (
    "PERMITTED",
    "APPROVED",
    "CERTIFIED",
    "COMPLIANT",
    "LAWFUL",
    "LEGAL",
    "ENTITLEMENT",
    "GUARANTEED",
    "MAXIMUM ALLOWED",
    "AS OF RIGHT",
    "AS-OF-RIGHT",
)

# --------------------------------------------------------------------------- #
# Bounds and caps (fail-closed).
# --------------------------------------------------------------------------- #

MAX_MESHES = 1_000
#: Total vertices across all meshes (12 bytes each -> <= 6 MB of positions).
MAX_TOTAL_VERTICES = 500_000
#: Total indices across all meshes (<= 500,000 triangles, <= 6 MB).
MAX_TOTAL_INDICES = 1_500_000
#: Local-coordinate magnitude bound (US survey feet); see the FLOAT32 note.
MAX_LOCAL_COORD_ABS_FT = 100_000.0
#: Local-origin magnitude bound (US survey feet); mirrors the sibling writers.
MAX_ORIGIN_ABS_FT = 1e8
#: A triangle whose sine at its first vertex is at or below this is degenerate
#: (coincident or collinear vertices after float32 quantization).
DEGENERATE_SINE_TOLERANCE = 1e-6
MESH_NAME_MAX = 64
_NAME_CHARS = frozenset(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 _-."
)

REFUSAL_CODES: frozenset[str] = frozenset({
    "claim_class_word",
    "coordinate_out_of_range",
    "degenerate_triangle",
    "duplicate_mesh_name",
    "empty_mesh",
    "index_count_not_triangles",
    "index_cap_exceeded",
    "index_out_of_range",
    "invalid_color",
    "invalid_frame",
    "invalid_index",
    "invalid_mesh",
    "invalid_mesh_name",
    "invalid_position",
    "mesh_cap_exceeded",
    "no_meshes",
    "non_finite_value",
    "output_size_exceeded",
    "vertex_cap_exceeded",
})


# --------------------------------------------------------------------------- #
# Typed errors and inputs.
# --------------------------------------------------------------------------- #

class GlbWriterError(Exception):
    """Base class for every GLB writer refusal."""


class GlbValidationError(GlbWriterError):
    """Input refusal; ``code`` is one of :data:`REFUSAL_CODES`."""

    def __init__(self, code: str, message: str, *, field: str | None = None) -> None:
        if code not in REFUSAL_CODES:  # programming error, never caller data
            raise ValueError(f"unregistered refusal code {code!r}")
        self.code = code
        self.field = field
        detail = f"{code}: {message}"
        if field is not None:
            detail = f"{detail} (field={field})"
        super().__init__(detail)


@dataclass(frozen=True)
class GlbLocalFrame:
    """The declared local frame: local (0, 0, 0) sits at this EPSG:2263 point.

    ``origin_elevation_ft`` is the elevation of local z = 0 as the caller
    declares it; this writer asserts no vertical datum.
    """

    origin_easting_ft: float
    origin_northing_ft: float
    origin_elevation_ft: float = 0.0


@dataclass(frozen=True)
class GlbMesh:
    """One named triangle mesh in the local frame (US survey feet).

    ``positions``: (x east, y north, z up) triples, offsets from the frame origin.
    ``indices``: uint32 vertex indices, three per triangle, counter-clockwise
    seen from the front face. ``base_color``: optional linear RGB or RGBA, each
    component in [0, 1]; meshes without one use the glTF default material.
    """

    name: str
    positions: Sequence[Sequence[float]]
    indices: Sequence[int]
    base_color: Sequence[float] | None = None


@dataclass(frozen=True)
class _PreparedMesh:
    name: str
    flat_positions: tuple[float, ...]  # glTF frame, metres, float32-exact
    indices: tuple[int, ...]
    color: tuple[float, float, float, float] | None
    minimum: tuple[float, float, float]
    maximum: tuple[float, float, float]


# --------------------------------------------------------------------------- #
# Validation + preparation (all refusals happen here, before assembly).
# --------------------------------------------------------------------------- #

def _real(value: object, field: str, *, code: str) -> float:
    """Return ``value`` as a finite float or refuse (bools are not numbers)."""
    if isinstance(value, bool) or not isinstance(value, numbers.Real):
        raise GlbValidationError(code, f"{value!r} is not a real number", field=field)
    try:
        result = float(value)
    except OverflowError:
        raise GlbValidationError(
            "coordinate_out_of_range", f"{value!r} overflows a float", field=field
        ) from None
    if not math.isfinite(result):
        raise GlbValidationError("non_finite_value", f"{result!r} is not finite", field=field)
    return result


def _f32(value: float) -> float:
    """Round to IEEE-754 single precision; ``-0.0`` is normalized to ``0.0``."""
    return _F32.unpack(_F32.pack(value))[0] + 0.0


def _sized(value: object, field: str, code: str) -> int:
    try:
        return len(value)  # type: ignore[arg-type]
    except TypeError:
        raise GlbValidationError(code, "must be a sized sequence", field=field) from None


def _bounded(items: object, field: str, code: str) -> Iterator[tuple[int, object]]:
    """Enumerate at most ``len(items)`` elements: a sequence whose iteration
    outruns its declared length cannot slip past the length-based caps."""
    limit = _sized(items, field, code)
    for k, item in enumerate(items):  # type: ignore[call-overload]
        if k >= limit:
            raise GlbValidationError(code, f"yields more than its {limit} items", field=field)
        yield k, item


def _check_caps(meshes: object) -> tuple[GlbMesh, ...]:
    """Refuse over-cap requests using lengths only - no vertex/index is read.

    Returns the meshes as a tuple so later passes see exactly what was capped."""
    if isinstance(meshes, (str, bytes)):
        raise GlbValidationError("invalid_mesh", "meshes must be a sequence of GlbMesh")
    count = _sized(meshes, "meshes", "invalid_mesh")
    if count == 0:
        raise GlbValidationError("no_meshes", "at least one mesh is required")
    if count > MAX_MESHES:
        raise GlbValidationError("mesh_cap_exceeded", f"{count} meshes exceed cap {MAX_MESHES}")
    vertices = indices = 0
    checked: list[GlbMesh] = []
    for i, mesh in _bounded(meshes, "meshes", "invalid_mesh"):
        if not isinstance(mesh, GlbMesh):
            raise GlbValidationError("invalid_mesh", "not a GlbMesh", field=f"meshes[{i}]")
        vertices += _sized(mesh.positions, f"meshes[{i}].positions", "invalid_position")
        indices += _sized(mesh.indices, f"meshes[{i}].indices", "invalid_index")
        checked.append(mesh)
    if vertices > MAX_TOTAL_VERTICES:
        raise GlbValidationError(
            "vertex_cap_exceeded", f"{vertices} vertices exceed cap {MAX_TOTAL_VERTICES}"
        )
    if indices > MAX_TOTAL_INDICES:
        raise GlbValidationError(
            "index_cap_exceeded", f"{indices} indices exceed cap {MAX_TOTAL_INDICES}"
        )
    return tuple(checked)


def _check_frame(frame: object) -> None:
    if not isinstance(frame, GlbLocalFrame):
        raise GlbValidationError("invalid_frame", "frame must be a GlbLocalFrame", field="frame")
    for attr in ("origin_easting_ft", "origin_northing_ft", "origin_elevation_ft"):
        value = _real(getattr(frame, attr), f"frame.{attr}", code="invalid_frame")
        if abs(value) > MAX_ORIGIN_ABS_FT:
            raise GlbValidationError(
                "coordinate_out_of_range",
                f"|{value!r}| exceeds bound {MAX_ORIGIN_ABS_FT:.0f}",
                field=f"frame.{attr}",
            )


def _check_name(name: object, field: str, seen: set[str]) -> str:
    if (
        not isinstance(name, str)
        or not 1 <= len(name) <= MESH_NAME_MAX
        or name != name.strip()
        or not set(name) <= _NAME_CHARS
    ):
        raise GlbValidationError(
            "invalid_mesh_name",
            f"{name!r} must be 1..{MESH_NAME_MAX} of [A-Za-z0-9 _-.], no edge spaces",
            field=field,
        )
    upper = name.upper()
    for word in CLAIM_CLASS_WORDS:
        if word in upper:
            raise GlbValidationError(
                "claim_class_word", f"{name!r} contains barred word {word!r}", field=field
            )
    if name in seen:
        raise GlbValidationError("duplicate_mesh_name", f"{name!r} is repeated", field=field)
    seen.add(name)
    return name


def _check_color(color: object, field: str) -> tuple[float, float, float, float] | None:
    if color is None:
        return None
    if isinstance(color, (str, bytes)) or _sized(color, field, "invalid_color") not in (3, 4):
        raise GlbValidationError("invalid_color", "must be RGB or RGBA", field=field)
    parts = [_real(c, field, code="invalid_color") for _, c in _bounded(color, field,
                                                                         "invalid_color")]
    if len(parts) not in (3, 4) or any(not 0.0 <= c <= 1.0 for c in parts):
        raise GlbValidationError("invalid_color", f"{parts!r} not RGB(A) in [0, 1]", field=field)
    if len(parts) == 3:
        parts.append(1.0)
    return (parts[0], parts[1], parts[2], parts[3])


def _map_positions(positions: Sequence[Sequence[float]], field: str) -> tuple[float, ...]:
    """Validate local-feet positions; return flat float32-exact glTF metres."""
    flat: list[float] = []
    for v, point in _bounded(positions, field, "invalid_position"):
        where = f"{field}[{v}]"
        if isinstance(point, (str, bytes)) or _sized(point, where, "invalid_position") != 3:
            raise GlbValidationError("invalid_position", "must be an (x, y, z) triple", field=where)
        coords = tuple(
            _real(c, where, code="invalid_position")
            for _, c in _bounded(point, where, "invalid_position")
        )
        if len(coords) != 3:  # iteration fell short of the declared length
            raise GlbValidationError("invalid_position", "must be an (x, y, z) triple", field=where)
        x, y, z = coords
        for c in (x, y, z):
            if abs(c) > MAX_LOCAL_COORD_ABS_FT:
                raise GlbValidationError(
                    "coordinate_out_of_range",
                    f"|{c!r}| ft exceeds local bound {MAX_LOCAL_COORD_ABS_FT:.0f}"
                    " (localize to the frame origin first)",
                    field=where,
                )
        # (east, north, up) ft -> glTF (+X, +Y up, +Z = -north) metres.
        flat.append(_f32(x * US_SURVEY_FOOT_TO_METRE))
        flat.append(_f32(z * US_SURVEY_FOOT_TO_METRE))
        flat.append(_f32(-(y * US_SURVEY_FOOT_TO_METRE)))
    return tuple(flat)


def _check_indices(indices: Sequence[int], vertex_count: int, field: str) -> tuple[int, ...]:
    out: list[int] = []
    for k, index in _bounded(indices, field, "invalid_index"):
        if isinstance(index, bool) or not isinstance(index, numbers.Integral):
            raise GlbValidationError("invalid_index", f"{index!r} is not an integer",
                                     field=f"{field}[{k}]")
        value = int(index)
        # < vertex_count <= MAX_TOTAL_VERTICES also excludes the uint32 restart
        # value 4294967295 (spec section 3.7.2.1).
        if not 0 <= value < vertex_count:
            raise GlbValidationError(
                "index_out_of_range", f"{value} not in [0, {vertex_count})", field=f"{field}[{k}]"
            )
        out.append(value)
    if not out:
        raise GlbValidationError("empty_mesh", "mesh has no indices", field=field)
    if len(out) % 3:
        raise GlbValidationError(
            "index_count_not_triangles", f"{len(out)} indices is not a multiple of 3", field=field
        )
    return tuple(out)


def _check_triangles(flat: tuple[float, ...], indices: tuple[int, ...], field: str) -> None:
    """Refuse coincident/collinear triangles on the float32 values written."""
    tol2 = DEGENERATE_SINE_TOLERANCE * DEGENERATE_SINE_TOLERANCE
    for t in range(0, len(indices), 3):
        a, b, c = (3 * i for i in indices[t : t + 3])
        ux, uy, uz = flat[b] - flat[a], flat[b + 1] - flat[a + 1], flat[b + 2] - flat[a + 2]
        vx, vy, vz = flat[c] - flat[a], flat[c + 1] - flat[a + 1], flat[c + 2] - flat[a + 2]
        cx, cy, cz = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
        cross2 = cx * cx + cy * cy + cz * cz
        if cross2 <= tol2 * (ux * ux + uy * uy + uz * uz) * (vx * vx + vy * vy + vz * vz):
            raise GlbValidationError(
                "degenerate_triangle",
                f"triangle {t // 3} {indices[t : t + 3]} has coincident or collinear vertices",
                field=field,
            )


def _prepare(mesh: GlbMesh, i: int, seen: set[str]) -> _PreparedMesh:
    field = f"meshes[{i}]"
    name = _check_name(mesh.name, f"{field}.name", seen)
    color = _check_color(mesh.base_color, f"{field}.base_color")
    flat = _map_positions(mesh.positions, f"{field}.positions")
    if not flat:
        raise GlbValidationError("empty_mesh", "mesh has no positions", field=f"{field}.positions")
    indices = _check_indices(mesh.indices, len(flat) // 3, f"{field}.indices")
    _check_triangles(flat, indices, f"{field}.indices")
    columns = (flat[0::3], flat[1::3], flat[2::3])
    minimum = (min(columns[0]), min(columns[1]), min(columns[2]))
    maximum = (max(columns[0]), max(columns[1]), max(columns[2]))
    return _PreparedMesh(name, flat, indices, color, minimum, maximum)


# --------------------------------------------------------------------------- #
# Assembly (pure; runs only after every refusal check has passed).
# --------------------------------------------------------------------------- #

def _asset(frame: GlbLocalFrame) -> dict[str, object]:
    return {
        "version": GLTF_ASSET_VERSION,
        "generator": GENERATOR,
        "extras": {
            "label": PROPOSED_LABEL,
            "sourceCrs": SOURCE_CRS,
            "sourceUnit": SOURCE_UNIT,
            "metresPerSourceUnit": US_SURVEY_FOOT_TO_METRE_EXACT,
            "metresPerSourceUnitDecimal": US_SURVEY_FOOT_TO_METRE,
            "axisMapping": dict(AXIS_MAPPING),
            "localOrigin": {
                "crs": SOURCE_CRS,
                "eastingFt": float(frame.origin_easting_ft),
                "northingFt": float(frame.origin_northing_ft),
                "elevationFt": float(frame.origin_elevation_ft),
                "note": (
                    "positions are float32 metre offsets from this origin; EPSG:2263 ft ="
                    " origin + (gltfX, -gltfZ, gltfY) * 3937/1200; vertical datum not"
                    " asserted by this writer"
                ),
            },
        },
    }


def _assemble(prepared: list[_PreparedMesh], frame: GlbLocalFrame) -> tuple[dict, bytes]:
    binary = bytearray()
    buffer_views: list[dict[str, int]] = []
    accessors: list[dict[str, object]] = []
    meshes: list[dict[str, object]] = []
    materials: list[dict[str, object]] = []
    material_index: dict[tuple[float, float, float, float], int] = {}
    for i, mesh in enumerate(prepared):
        # float32 (12 B/vertex) and uint32 (4 B/index) keep every view 4-aligned
        # (spec section 3.6.2.4).
        payloads = (
            (struct.pack(f"<{len(mesh.flat_positions)}f", *mesh.flat_positions),
             TARGET_ARRAY_BUFFER),
            (struct.pack(f"<{len(mesh.indices)}I", *mesh.indices), TARGET_ELEMENT_ARRAY_BUFFER),
        )
        for data, target in payloads:
            buffer_views.append({"buffer": 0, "byteOffset": len(binary),
                                 "byteLength": len(data), "target": target})
            binary += data
        accessors.append({
            "bufferView": 2 * i, "componentType": COMPONENT_FLOAT,
            "count": len(mesh.flat_positions) // 3, "type": "VEC3",
            "min": list(mesh.minimum), "max": list(mesh.maximum),
        })
        accessors.append({
            "bufferView": 2 * i + 1, "componentType": COMPONENT_UNSIGNED_INT,
            "count": len(mesh.indices), "type": "SCALAR",
        })
        primitive: dict[str, object] = {
            "attributes": {"POSITION": 2 * i}, "indices": 2 * i + 1, "mode": MODE_TRIANGLES,
        }
        if mesh.color is not None:
            if mesh.color not in material_index:
                material_index[mesh.color] = len(materials)
                material: dict[str, object] = {
                    "name": f"colour_{len(materials)}",
                    "pbrMetallicRoughness": {
                        "baseColorFactor": list(mesh.color),
                        "metallicFactor": 0.0,
                        "roughnessFactor": 1.0,
                    },
                }
                if mesh.color[3] < 1.0:
                    material["alphaMode"] = "BLEND"
                materials.append(material)
            primitive["material"] = material_index[mesh.color]
        meshes.append({"name": mesh.name, "primitives": [primitive]})
    document: dict[str, object] = {
        "asset": _asset(frame),
        "scene": 0,
        "scenes": [{"name": PROPOSED_LABEL, "nodes": list(range(len(prepared)))}],
        "nodes": [{"name": m.name, "mesh": i} for i, m in enumerate(prepared)],
        "meshes": meshes,
    }
    if materials:
        document["materials"] = materials
    document["accessors"] = accessors
    document["bufferViews"] = buffer_views
    # Section 3.6.1.2: the GLB-stored buffer is buffers[0] with no uri.
    document["buffers"] = [{"byteLength": len(binary)}]
    return document, bytes(binary)


def _chunk(chunk_type: int, payload: bytes, pad_byte: bytes) -> bytes:
    """One chunk: uint32 length, uint32 type, data padded to 4 bytes."""
    padded = payload + pad_byte * (-len(payload) % CHUNK_ALIGNMENT)
    return _CHUNK_HEADER.pack(len(padded), chunk_type) + padded


def _json_chunk(json_bytes: bytes) -> bytes:
    return _chunk(CHUNK_TYPE_JSON, json_bytes, JSON_PAD_BYTE)


def _bin_chunk(binary: bytes) -> bytes:
    return _chunk(CHUNK_TYPE_BIN, binary, BIN_PAD_BYTE)


def write_glb(meshes: Sequence[GlbMesh], frame: GlbLocalFrame) -> bytes:
    """Return a GLB (glTF 2.0 binary) for ``meshes`` or raise GlbValidationError.

    One node + one mesh (one indexed TRIANGLES primitive) per input mesh, in
    input order; one material per distinct base colour. Deterministic.
    """
    capped = _check_caps(meshes)
    _check_frame(frame)
    seen: set[str] = set()
    prepared = [_prepare(mesh, i, seen) for i, mesh in enumerate(capped)]
    document, binary = _assemble(prepared, frame)
    # Section 2.7: UTF-8 without BOM; names are plain ASCII so nothing escapes.
    json_bytes = json.dumps(
        document, separators=(",", ":"), ensure_ascii=True, allow_nan=False
    ).encode("utf-8")
    body = _json_chunk(json_bytes) + _bin_chunk(binary)
    total = _HEADER.size + len(body)
    if total > _UINT32_MAX:
        raise GlbValidationError("output_size_exceeded", f"{total} bytes exceed the uint32 bound")
    return _HEADER.pack(GLB_MAGIC, GLB_VERSION, total) + body
