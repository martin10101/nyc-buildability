"""Acceptance pack for the D-087 PKT-E scene assembler (task M5-T107, AS-1..AS-3, AS-6).

Fully OFFLINE and deterministic: the massing truth object is built from the accepted
``massing_model`` builders and the context buildings are SYNTHETIC ``ContextBuilding`` /
``ContextBuildingsResult`` objects constructed in-memory here - nothing touches the network.
The connector's own live behaviour is covered by tests/connectors; this pack exercises the
PURE assembler.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

import app.scenario.scene_assembler as sa
from app.cad.claim_words import contains_claim_word
from app.connectors.building_footprints_arcgis import (
    ContextBuilding,
    ContextBuildingsResult,
    FootprintRefusal,
)
from app.connectors.building_footprints_geometry import FootprintPart
from app.scenario.massing_model import VERTICAL_UNIT
from app.scenario.scene_assembler import (
    SceneAssemblyError,
    assemble_scene,
    build_scene_massing,
    parse_ring,
)

MODULE_PATH = Path(sa.__file__)

# A 100 x 120 ft lot rectangle (EPSG:2263), supplied OPEN.
LOT_RING = [[1000000.0, 200000.0], [1000100.0, 200000.0],
            [1000100.0, 200120.0], [1000000.0, 200120.0]]
LOT_RING_STR = [[str(x), str(y)] for x, y in LOT_RING]
RECT = [[1000010.0, 200010.0], [1000050.0, 200010.0],
        [1000050.0, 200070.0], [1000010.0, 200070.0]]


def _outline(vertices):
    return {"srid": 2263, "vertices": vertices + [vertices[0]]}


def _walls(n):
    return [{"id": f"W{i}", "start_vertex_index": i, "end_vertex_index": (i + 1) % n}
            for i in range(n)]


def _pm(vertices=RECT, floor_count=2):
    return {
        "outline": _outline(vertices),
        "levels": [{"level_index": 0, "floor_count": floor_count, "floor_to_floor_ft": 12.0}],
        "exterior_walls": _walls(len(vertices)),
        "provenance": {"author": "a", "editor_version": "v", "kind": "proposed"},
    }


def _building(**overrides) -> ContextBuilding:
    part = FootprintPart(
        exterior=[[1000200.0, 200000.0], [1000260.0, 200000.0],
                  [1000260.0, 200060.0], [1000200.0, 200060.0], [1000200.0, 200000.0]],
        holes=[[[1000220.0, 200020.0], [1000220.0, 200040.0],
                [1000240.0, 200040.0], [1000240.0, 200020.0], [1000220.0, 200020.0]]],
        area_sq_ft=3200.0)
    defaults = dict(
        object_id=123, doitt_id=1, bin=2000001, base_bbl="1000010001",
        mappluto_bbl="1000010001", joins_subject_lot=False, feature_code=2100,
        feature_code_label="Building", height_roof_ft=45.0, ground_elevation_ft=190.0,
        relative_base_z_ft=-10.0, relative_roof_z_ft=35.0, construction_year=1920,
        geom_source="Photogrammetric", last_edited="2020-01-01T00:00:00Z",
        last_status_type="Constructed", geometry_status="valid", geometry_findings=[],
        parts=[part], footprint_area_sq_ft=3200.0, query_relation="partial_overlap",
        query_overlap_area_sq_ft=100.0, flags=["has_holes"], gaps=[],
        attributes={"OBJECTID": 123, "GEOM_SOURCE": "Photogrammetric"},
        original_geometry={"rings": []}, original_geometry_digest="sha256:x")
    defaults.update(overrides)
    return ContextBuilding(**defaults)


def _result(
    buildings=None, *, status="ok", site_ground=200.0, refusal=None
) -> ContextBuildingsResult:
    return ContextBuildingsResult(
        status=status, buildings=buildings if buildings is not None else [_building()],
        refusal=refusal, correlation_id="cid-1", query={"kind": "envelope"},
        site_ground_elevation_ft=site_ground, subject_bbl="1000010001",
        metadata_request_url="u/meta", metadata_raw_digest="sha256:m",
        request_urls=["u/p1"], raw_digests=["sha256:p1"], retrieved_at="2026-09-24T12:00:00Z",
        source_data_last_edited_ms=1, source_data_last_edited="2026-09-20T02:16:01Z",
        pages_fetched=1, drift_signals=[])


def _scene(pm=None, *, context=None, site_ground=200.0, correlation_id="cid-1"):
    massing = build_scene_massing(lot_ring=LOT_RING, proposed_massing=pm or _pm())
    return assemble_scene(massing_model=massing, context_result=context,
                          site_ground_elevation_ft=site_ground, correlation_id=correlation_id)


# ---------------------------------------------------------------------------
# AS-1: the section 2.1 payload shape.
# ---------------------------------------------------------------------------


def test_as1_payload_carries_massing_verbatim_plus_context_and_explicit_vertical_unit():
    massing = build_scene_massing(lot_ring=LOT_RING, proposed_massing=_pm())
    scene = assemble_scene(massing_model=massing, context_result=_result(),
                           site_ground_elevation_ft=200.0, correlation_id="cid-1")
    md = massing.as_dict()
    for key in ("source", "disclosure", "coordinate_reference_system", "parcel",
                "building_layer", "meshes", "plates", "metrics"):
        assert scene[key] == md[key]
    assert "world_to_local" in scene["coordinate_reference_system"]
    assert scene["scene_version"] == sa.SCENE_VERSION
    assert scene["vertical_unit"] == VERTICAL_UNIT == "us_survey_foot"  # DB-054 (k) explicit
    assert scene["layers"] == [*md["layers"], sa.CONTEXT_LAYER]
    assert scene["context_buildings"]["layer"] == sa.CONTEXT_LAYER


def test_as1_one_declared_ground_datum_with_its_source_in_provenance():
    scene = _scene(context=_result())
    datum = scene["provenance"]["scene"]["ground_datum"]
    assert datum is sa.GROUND_DATUM_DECISION
    assert datum["chosen"] == "local_scene_frame_relative_to_site_ground"
    assert datum["source_field"] == "GROUND_ELEVATION" and "OTI" in datum["source"]
    assert datum["vertical_unit"] == "us_survey_foot"
    # BOTH official definitions disclosed; neither reconciled; NAVD88 attributed to the dictionary.
    assert "city_dictionary" in datum["definitions_disclosed"]
    assert "fgdc_metadata" in datum["definitions_disclosed"]
    assert "NAVD88" in datum["navd88_attribution"] and "dictionary" in datum["navd88_attribution"]
    assert scene["context_buildings"]["ground_datum"] is sa.GROUND_DATUM_DECISION


def test_as1_golden_context_building_shape_is_pinned():
    scene = _scene(context=_result())
    (building,) = scene["context_buildings"]["buildings"]
    assert building == {
        "object_id": 123,
        "record_class": "official_city_footprint",
        "disclosure": sa._CONTEXT_RECORD_DISCLOSURE,
        "bin": 2000001,
        "base_bbl": "1000010001",
        "mappluto_bbl": "1000010001",
        "joins_subject_lot": False,
        "feature_code": 2100,
        "feature_code_label": "Building",
        "construction_year": 1920,
        "height_roof_ft": 45.0,
        "ground_elevation_ft": 190.0,
        "base_z_ft": -10.0,
        "roof_z_ft": 35.0,
        "base_z_grounded": True,
        "ground_status": "grounded",
        "vertical_unit": "us_survey_foot",
        "geometry_status": "valid",
        "geometry_findings": [],
        "parts": [{
            "exterior": [[1000200.0, 200000.0], [1000260.0, 200000.0], [1000260.0, 200060.0],
                         [1000200.0, 200060.0], [1000200.0, 200000.0]],
            "holes": [[[1000220.0, 200020.0], [1000220.0, 200040.0], [1000240.0, 200040.0],
                       [1000240.0, 200020.0], [1000220.0, 200020.0]]],
            "area_sq_ft": 3200.0,
        }],
        "has_holes": True,
        "multipart": False,
        "footprint_area_sq_ft": 3200.0,
        "query_relation": "partial_overlap",
        "flags": ["has_holes"],
        "gaps": [],
        "untrusted_text_fields": ["attributes", "geom_source", "last_status_type"],
        "untrusted_text_notice": _building().untrusted_text_notice,
        "geom_source_escaped": "Photogrammetric",
        "last_status_type_escaped": "Constructed",
        "attributes_escaped": {"OBJECTID": 123, "GEOM_SOURCE": "Photogrammetric"},
    }


def test_as1_string_coordinates_parse_to_float():
    """DB-054 (o): a MapPLUTO-style string-coordinate lot ring parses to float and builds."""
    scene = _scene()  # numeric baseline for comparison
    from_strings = assemble_scene(
        massing_model=build_scene_massing(lot_ring=LOT_RING_STR, proposed_massing=_pm()),
        context_result=None, site_ground_elevation_ft=200.0, correlation_id="cid-1")
    assert from_strings["parcel"] == scene["parcel"]
    assert all(isinstance(c, float) for pt in from_strings["parcel"]["ring"] for c in pt)
    assert parse_ring([["1", "2"], ["3", "4"]], "r") == [[1.0, 2.0], [3.0, 4.0]]


def test_as1_non_numeric_or_non_finite_coordinate_is_refused_typed():
    """DB-054 (o): a non-numeric or non-finite coordinate fails closed, never a default."""
    for bad in (["abc", "1"], ["1", "nan"], ["inf", "2"]):
        ring = [bad, ["2", "3"], ["4", "5"], ["6", "7"]]
        with pytest.raises(SceneAssemblyError) as exc:
            build_scene_massing(lot_ring=ring, proposed_massing=_pm())
        assert exc.value.reason == "unparseable_coordinate"
        assert exc.value.field == "lot_ring[0]"


def test_as1_assembler_is_deterministic():
    a = _scene(context=_result())
    b = _scene(context=_result())
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def test_as1_scene_is_strict_json_serializable():
    scene = _scene(context=_result())
    json.dumps(scene, ensure_ascii=False, allow_nan=False).encode("utf-8")


# ---------------------------------------------------------------------------
# AS-2: honesty + disclosure.
# ---------------------------------------------------------------------------


def test_as2_proposed_and_generated_labels_follow_d083():
    proposed = _scene()
    assert proposed["source"] == "proposed"
    assert proposed["disclosure"] == "Proposed - not a city record"
    generated = assemble_scene(
        massing_model=build_scene_massing(lot_ring=LOT_RING, generated_option={"candidate": _pm()}),
        context_result=None, site_ground_elevation_ft=None, correlation_id="cid-1")
    assert generated["source"] == "generated_option"
    assert generated["disclosure"] == "Generated building option"


def test_as2_the_assemblers_own_labels_carry_no_barred_claim_word():
    """AS-2 / D-083: no assembler-emitted label or disclosure uses permitted / approved /
    maximum allowed / as-of-right and the like (the shared claim-word screen, PKT-A)."""
    scene = _scene(context=_result())
    own_strings = [
        scene["source"], scene["disclosure"], scene["building_layer"]["disclosure"],
        sa._CONTEXT_RECORD_DISCLOSURE,
        *[d["detail"] for d in scene["disclosures"]],
        *[d["detail"] for d in scene["context_buildings"]["disclosures"]],
        *[str(v) for v in sa.GROUND_DATUM_DECISION.values() if isinstance(v, str)],
        *[str(v) for v in sa.GROUND_DATUM_DECISION["definitions_disclosed"].values()],
    ]
    for text in own_strings:
        assert contains_claim_word(text) is None, text


def test_as2_per_level_nesting_and_party_wall_are_disclosed():
    """AS-2: DB-054 (l) per-level nesting checked against the lot, and DB-054 (n) the missing
    party-wall distinction, are both disclosed."""
    codes = {d["code"]: d for d in _scene()["disclosures"]}
    assert codes["per_level_nesting_not_asserted"]["backlog"] == "DB-054 (l)"
    assert codes["no_party_wall_distinction"]["backlog"] == "DB-054 (n)"


def test_as2_multipolygon_courtyard_holes_are_disclosed_never_dropped():
    """AS-2: DB-053 (g) - a MultiPolygon/holed footprint keeps every part and hole; the layer
    discloses the holes policy. Mutation guard: dropping the holes key or the disclosure reddens."""
    scene = _scene(context=_result())
    layer = scene["context_buildings"]
    assert any(d["backlog"] == "DB-053 (g)" for d in layer["disclosures"])
    (building,) = layer["buildings"]
    assert building["has_holes"] is True
    assert building["parts"][0]["holes"]  # the hole ring is kept, not dropped
    assert len(building["parts"][0]["holes"][0]) == 5


@pytest.mark.parametrize(
    ("ground", "flags", "site_ground", "base_z", "status"),
    [
        (190.0, [], 200.0, -10.0, "grounded"),
        (0.0, ["ground_elevation_zero_unverified"], 200.0, -200.0, "ground_zero_unverified"),
        (None, [], 200.0, None, "ground_elevation_missing"),
        (190.0, [], None, None, "site_ground_not_supplied"),
    ],
)
def test_as2_zero_and_unverified_grounds_are_disclosed_never_sea_level(
    ground, flags, site_ground, base_z, status
):
    """AS-2: DB-058 (f) - a zero or unverified ground is disclosed, never treated as sea level;
    a missing ground or missing site ground yields base_z null with the reason disclosed."""
    relative = None if ground is None or site_ground is None else round(ground - site_ground, 6)
    building = _building(ground_elevation_ft=ground, flags=flags, relative_base_z_ft=relative,
                         relative_roof_z_ft=None if relative is None else relative + 45.0)
    scene = _scene(context=_result([building], site_ground=site_ground))
    (out,) = scene["context_buildings"]["buildings"]
    assert out["base_z_ft"] == base_z
    assert out["base_z_grounded"] is (base_z is not None)
    assert out["ground_status"] == status


# ---------------------------------------------------------------------------
# AS-3: untrusted text is declared and escaped; refusals bounded; nothing logged.
# ---------------------------------------------------------------------------


def test_as3_source_strings_are_declared_untrusted_and_escaped():
    """AS-3: DB-058 (a) - every context-building source string is declared untrusted and escaped
    for rendering (HTML entities, U+2028/U+2029 stripped); the raw strings are not emitted."""
    building = _building(
        geom_source="Photo<script>alert(1)</script>",
        last_status_type="Constructed  INJECT",
        attributes={"OBJECTID": 123, "GEOM_SOURCE": "a<b>&\"'"})
    scene = _scene(context=_result([building]))
    (out,) = scene["context_buildings"]["buildings"]
    assert out["untrusted_text_fields"] == ["attributes", "geom_source", "last_status_type"]
    assert "escape" in out["untrusted_text_notice"].lower()
    assert out["geom_source_escaped"] == "Photo&lt;script&gt;alert(1)&lt;/script&gt;"
    assert "<script>" not in json.dumps(scene)  # the raw string is nowhere in the payload
    assert out["last_status_type_escaped"] == "ConstructedINJECT"  # separators stripped
    assert " " not in out["last_status_type_escaped"]
    assert out["attributes_escaped"]["GEOM_SOURCE"] == "a&lt;b&gt;&amp;&quot;&#x27;"
    assert out["attributes_escaped"]["OBJECTID"] == 123  # non-strings pass through


def test_as3_escape_guard_is_load_bearing_in_process_mutation(monkeypatch):
    """AS-3 in-process mutation (mutate the CONSUMING namespace): emptying _RENDER_UNSAFE_DELETE
    lets a U+2028 separator survive the escape - proving the strip table is load-bearing."""
    building = _building(last_status_type="a b")
    clean = _scene(context=_result([building]))["context_buildings"]["buildings"][0]
    assert " " not in clean["last_status_type_escaped"]
    monkeypatch.setattr(sa, "_RENDER_UNSAFE_DELETE", {})
    mutated = _scene(context=_result([building]))["context_buildings"]["buildings"][0]
    assert " " in mutated["last_status_type_escaped"]  # the guard, disabled, leaks it


def test_as3_context_refusal_is_disclosed_and_bounded_never_dropped():
    """AS-3: a connector refusal is DISCLOSED in the context layer (never dropped, never a
    fabricated building) with a length-bounded message."""
    refusal = FootprintRefusal(
        error_type="upstream_error", message="x" * 5000, correlation_id="cid-1",
        detail={"url": "u"}, request_url="u/p1", retrieved_at="2026-09-24T12:00:00Z",
        raw_digest="sha256:z")
    scene = _scene(context=_result([], status="refused", refusal=refusal))
    layer = scene["context_buildings"]
    assert layer["status"] == "refused" and layer["buildings"] == []
    assert layer["refusal"]["error_type"] == "upstream_error"
    assert layer["refusal"]["message"].endswith("...(truncated)")
    assert len(layer["refusal"]["message"]) <= sa.MAX_UNTRUSTED_LEN + len("...(truncated)")


def test_as3_no_context_requested_is_an_honest_layer():
    scene = _scene(context=None)
    layer = scene["context_buildings"]
    assert layer["status"] == "not_requested" and layer["buildings"] == []
    assert layer["ground_datum"] is sa.GROUND_DATUM_DECISION


def test_as3_assembler_does_not_log_any_source_or_caller_text():
    """AS-3: the assembler is PURE - it imports no logger and calls none, so no source or caller
    text can reach a log line (that concern is the route's, which logs only a correlation id)."""
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
    roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".")[0])
    assert "logging" not in roots
    source = MODULE_PATH.read_text(encoding="utf-8")
    assert "import logging" not in source and "logging.getLogger" not in source
    assert "logger" not in source  # no logger object is defined or used


# ---------------------------------------------------------------------------
# AS-6: scope - zero new dependencies (stdlib + app only).
# ---------------------------------------------------------------------------


def test_as6_module_imports_only_stdlib_and_app():
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
    roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".")[0])
    assert roots <= {"__future__", "html", "math", "collections", "typing", "app"}
