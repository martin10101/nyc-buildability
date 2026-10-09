"""Owner-openable CAD sample files (task M5-T096, D-087 CAD-2), scenario AS-3.

The three committed samples under ``docs/samples/cad/`` are what the owner opens
to confirm the export works (closes DCV-F1 / DB-057 a). This module BUILDS each
sample from ONE synthetic example lot + building and asserts the committed bytes
are byte-identical to a fresh in-memory regeneration, so a sample can never drift
from its writer: change any writer output and the byte-identity assertion reddens.

Offline and deterministic: no network, no clock, stdlib + pytest only. The DXF,
PDF and GLB are built through the ACCEPTED writers' PUBLIC functions
(``app.cad.dxf_writer``, ``app.cad.pdf_sheet_writer``, ``app.cad.glb_writer``);
the GLB massing mesh is a simple extruded box assembled HERE (no production code).

Honesty (D-073-R006 / D-076-R002 / D-083): the lot and building are SYNTHETIC.
Every file carries the synthetic-lot label ``Example lot - not a real property``
and its writer's proposed / not-a-city-record stamp; nothing is presented as a
real property or an allowed building.
"""

import hashlib
from pathlib import Path

import pytest

from app.cad.dxf_writer import (
    LAYER_ANNOTATION,
    TextLabel,
    build_site_plan_document,
    serialize_document,
)
from app.cad.glb_writer import GlbLocalFrame, GlbMesh, write_glb
from app.cad.pdf_sheet_writer import SitePlanInput, render_site_plan_pdf

# --------------------------------------------------------------------------- #
# ONE synthetic example lot + building (EPSG:2263 US survey feet, inside the NYC
# range: easting ~9.9e5, northing ~2.1e5). A 100 x 80 ft rectangular lot with a
# centred 60 x 40 ft, 4-floor (42 ft) building. NOT a real property.
# --------------------------------------------------------------------------- #

SYNTHETIC_LABEL = "Example lot - not a real property"

SAMPLE_LOT = [
    (988000.0, 210000.0),
    (988100.0, 210000.0),
    (988100.0, 210080.0),
    (988000.0, 210080.0),
]
SAMPLE_BUILDING = [
    (988020.0, 210020.0),
    (988080.0, 210020.0),
    (988080.0, 210060.0),
    (988020.0, 210060.0),
]
SAMPLE_FLOOR_HEIGHTS = [12.0, 10.0, 10.0, 10.0]  # 42 ft total
SAMPLE_BUILDING_HEIGHT = sum(SAMPLE_FLOOR_HEIGHTS)

# DXF annotation label geometry for the appended synthetic-lot label (matches the
# writer's own annotation height for a 100 ft lot span: round(100 / 50, 6)).
_DXF_LABEL_HEIGHT = 2.0
_DXF_LABEL_GAP = 3.0

# GLB local frame at the lot's SW corner so local coordinates stay small (float32).
_GLB_ORIGIN = GlbLocalFrame(
    origin_easting_ft=988000.0, origin_northing_ft=210000.0, origin_elevation_ft=0.0
)
_BUILDING_COLOR = (0.70, 0.72, 0.78)          # opaque grey massing
_LOT_COLOR = (0.85, 0.85, 0.60, 0.45)         # translucent lot slab

DXF_NAME = "example-site-plan.dxf"
PDF_NAME = "example-site-plan.pdf"
GLB_NAME = "example-massing.glb"
SAMPLE_NAMES = (DXF_NAME, PDF_NAME, GLB_NAME)

SAMPLES_DIR = Path(__file__).resolve().parents[4] / "docs" / "samples" / "cad"

_SIZE_LIMIT_BYTES = 200 * 1024


# --------------------------------------------------------------------------- #
# Sample builders (deterministic; identical inputs -> byte-identical output).
# --------------------------------------------------------------------------- #

def build_sample_dxf() -> bytes:
    """The site-plan DXF: the accepted writer supplies all geometry and the fixed
    PROPOSED stamp; one ANNOTATION TextLabel carrying the synthetic-lot label is
    appended through the writer's public API and the extents extended to include
    it, then the document is serialized."""
    doc = build_site_plan_document(SAMPLE_LOT, SAMPLE_BUILDING, SAMPLE_FLOOR_HEIGHTS)
    label = TextLabel(
        layer=LAYER_ANNOTATION,
        position=(doc.extents_min[0], doc.extents_min[1] - _DXF_LABEL_GAP, 0.0),
        height=_DXF_LABEL_HEIGHT,
        text=SYNTHETIC_LABEL,
    )
    doc.texts.append(label)
    lx, ly, lz = label.position
    mnx, mny, mnz = doc.extents_min
    mxx, mxy, mxz = doc.extents_max
    doc.extents_min = (min(mnx, lx), min(mny, ly), min(mnz, lz))
    doc.extents_max = (max(mxx, lx), max(mxy, ly), max(mxz, lz))
    return serialize_document(doc).encode("ascii")


def build_sample_pdf() -> bytes:
    """The matching site-plan PDF from the accepted vector-PDF writer. The address
    field carries the synthetic-lot label; the writer always stamps PROPOSED."""
    spec = SitePlanInput(
        lot_ring=tuple(SAMPLE_LOT),
        building_ring=tuple(SAMPLE_BUILDING),
        address=SYNTHETIC_LABEL,
        bbl="EXAMPLE-0000000000",
        generated_at="2026-09-24",
        generator_version="NYC Buildability sample v1",
    )
    result = render_site_plan_pdf(spec)
    assert isinstance(result, bytes), f"PDF writer refused the sample: {result}"
    return result


def _box_mesh(name, x0, y0, x1, y1, z0, z1, color) -> GlbMesh:
    """A closed rectangular box (8 vertices, 12 triangles, outward CCW). The
    winding mirrors the accepted GLB writer's own box fixture."""
    positions = [
        (x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
        (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1),
    ]
    indices = [
        0, 2, 1, 0, 3, 2,   # bottom (faces down)
        4, 5, 6, 4, 6, 7,   # top (faces up)
        0, 1, 5, 0, 5, 4,   # south
        1, 2, 6, 1, 6, 5,   # east
        2, 3, 7, 2, 7, 6,   # north
        3, 0, 4, 3, 4, 7,   # west
    ]
    return GlbMesh(name, positions, indices, color)


def _slab_mesh(name, x0, y0, x1, y1, color) -> GlbMesh:
    """A flat quad at z = 0 (2 triangles, CCW seen from above)."""
    positions = [(x0, y0, 0.0), (x1, y0, 0.0), (x1, y1, 0.0), (x0, y1, 0.0)]
    indices = [0, 1, 2, 0, 2, 3]
    return GlbMesh(name, positions, indices, color)


def build_sample_glb() -> bytes:
    """The 3D massing GLB: an extruded box for the building plus a flat lot slab,
    built HERE from the same synthetic lot + building (local US survey feet from
    the frame origin). The lot-slab mesh name carries the synthetic-lot label; the
    accepted writer stamps ``Proposed - not a city record`` in the asset + scene."""
    building = _box_mesh(
        "Proposed building option",
        20.0, 20.0, 80.0, 60.0, 0.0, SAMPLE_BUILDING_HEIGHT, _BUILDING_COLOR,
    )
    lot = _slab_mesh(SYNTHETIC_LABEL, 0.0, 0.0, 100.0, 80.0, _LOT_COLOR)
    return write_glb([building, lot], _GLB_ORIGIN)


_BUILDERS = {
    DXF_NAME: build_sample_dxf,
    PDF_NAME: build_sample_pdf,
    GLB_NAME: build_sample_glb,
}


# --------------------------------------------------------------------------- #
# AS-3: each committed sample is byte-identical to a fresh regeneration.
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("name", SAMPLE_NAMES)
def test_as3_sample_regenerates_byte_identically(name):
    """Regenerating the sample in memory reproduces the committed bytes exactly.
    Mutation: any change in a writer's output makes the regeneration differ from
    the committed file and reddens this test."""
    committed = (SAMPLES_DIR / name).read_bytes()
    regenerated = _BUILDERS[name]()
    assert regenerated == committed, f"{name} drifted from its writer"


def test_as3_regeneration_is_deterministic():
    """Two regenerations of every sample agree byte-for-byte (no clock/randomness)."""
    for build in _BUILDERS.values():
        assert build() == build()


def test_as3_byte_identity_comparison_is_strict():
    """The byte-identity check is exact, not a size/prefix compare: a one-byte
    change from the committed bytes would fail it (guards against a vacuous test)."""
    committed = (SAMPLES_DIR / DXF_NAME).read_bytes()
    assert build_sample_dxf() == committed
    assert build_sample_dxf() != committed[:-1] + b"X"


# --------------------------------------------------------------------------- #
# AS-3 honesty: every file carries the synthetic-lot label and a proposed stamp.
# --------------------------------------------------------------------------- #

def test_as3_every_file_carries_the_synthetic_lot_label():
    needle = SYNTHETIC_LABEL.encode("ascii")
    for name in SAMPLE_NAMES:
        assert needle in (SAMPLES_DIR / name).read_bytes(), f"{name} lacks the synthetic label"


def test_as3_every_file_carries_a_proposed_not_a_city_record_stamp():
    # The DXF and PDF writers stamp the upper-case phrase; the accepted GLB writer
    # uses its own title-case honesty label. Each file "keeps" the stamp.
    assert b"PROPOSED - NOT A CITY RECORD" in (SAMPLES_DIR / DXF_NAME).read_bytes()
    assert b"PROPOSED - NOT A CITY RECORD" in (SAMPLES_DIR / PDF_NAME).read_bytes()
    assert b"Proposed - not a city record" in (SAMPLES_DIR / GLB_NAME).read_bytes()


def test_as3_no_claim_class_words_in_any_sample():
    from app.cad.dxf_writer import CLAIM_CLASS_WORDS
    for name in SAMPLE_NAMES:
        upper = (SAMPLES_DIR / name).read_bytes().upper()
        for word in CLAIM_CLASS_WORDS:
            assert word.encode("ascii") not in upper, f"{name} leaks claim word {word}"


def test_as3_each_sample_is_well_under_200kb():
    for name in SAMPLE_NAMES:
        size = (SAMPLES_DIR / name).stat().st_size
        assert 0 < size < _SIZE_LIMIT_BYTES, f"{name} is {size} bytes"


# --------------------------------------------------------------------------- #
# AS-3 README: the plain-English checklist lists the true sha256 of every file.
# --------------------------------------------------------------------------- #

def test_as3_readme_lists_correct_sha256_of_each_file():
    readme = (SAMPLES_DIR / "README.md").read_text(encoding="utf-8")
    for name in SAMPLE_NAMES:
        digest = hashlib.sha256((SAMPLES_DIR / name).read_bytes()).hexdigest()
        assert digest in readme, f"README missing the sha256 {digest} for {name}"
        assert name in readme, f"README does not mention {name}"
