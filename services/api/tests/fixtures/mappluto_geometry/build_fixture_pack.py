"""Fixture-pack builder for the MapPLUTO per-BBL geometry connector
(task M2-T009).

Two phases:

- ``capture``: live KB-scale reads of the official DCP_GIS MAPPLUTO ArcGIS
  feature service (keyless; producer-local network use disclosed in the
  producer report; CI never runs this - CI is offline and replays the
  committed fixtures). Every captured fixture records the exact request URL
  and the retrieval timestamp (UTC) at capture time. Capture BBLs:

  * 1008350041 (Manhattan block 835 lot 41, Empire State Building) - normal
    single-polygon lot, one clockwise exterior ring.
  * 1000157501 (Manhattan block 15 lot 7501) - condominium BILLING lot
    (lot range 7501-7599 per research section 2.5 / meta_mappluto.pdf);
    CondoNo 1025; the polygon represents the merged condo complex.
  * 1000151001 (Manhattan block 15 lot 1001) - condominium UNIT lot on the
    same block: MapPLUTO carries NO record for unit lots (research
    section 2.5) - live-captured empty result proves the semantics.
  * 1000010010 (Governors Island) - single polygon WITH TWO HOLES (one CW
    exterior ring + two CCW interior rings observed live).
  * 4142600001 (Queens) - TRUE MULTIPOLYGON lot (two CW exterior rings
    observed live; shoreline-clipped parts).
  * 5999999999 - syntactically valid, nonexistent BBL: well-formed empty
    ``features`` array (typed no_feature outcome).

- ``derive``: offline derivation of clearly-labeled SYNTHETIC fixtures from
  the captured raw fixtures (metadata negatives, wrong-CRS shapes, the
  invalid-geometry taxonomy, identifier mismatches, multiple-feature
  responses, malformed bodies, 429). The invalid-geometry taxonomy shapes
  (self-intersection, unclosed ring, inverted orientation, duplicate
  vertices, degenerate ring, empty/null geometry, geometry-collection
  surprise) cannot be politely obtained from the live official service, so
  they are synthetic BY NECESSITY and labeled as such. Synthetic fixtures
  exercise connector logic only and are never presented as official data.

Both phases regenerate ``MANIFEST.json`` (M2-T007 manifest conventions):
official endpoint, layer, query parameters, retrieval timestamp, source
edit timestamp where available, CRS, expected record count, cryptographic
digest, raw/synthetic classification, purpose, and supported acceptance
scenarios per fixture. No secrets or tokens exist anywhere in this pack
(the service is keyless and no auth header is ever sent).

Usage (from services/api):
    python tests/fixtures/mappluto_geometry/build_fixture_pack.py capture
    python tests/fixtures/mappluto_geometry/build_fixture_pack.py derive
"""

from __future__ import annotations

import hashlib
import json
import sys
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

FIXTURE_DIR = Path(__file__).resolve().parent
SERVICE_ROOT = "https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services"
LAYER = "MAPPLUTO"
SOURCE_ID = "nyc-dcp-mappluto-arcgis"

# Bounded out-field set: the exact set the connector requests (identifier +
# condo + version + official measure fields). Never ``*`` - keeps responses
# KB-scale and the contract explicit.
OUT_FIELDS = (
    "OBJECTID%2CBBL%2CBoroCode%2CBorough%2CBlock%2CLot%2CCondoNo%2CVersion"
    "%2CShape__Area%2CShape__Length"
)


def _lot_query_path(bbl: int) -> str:
    return (
        f"{LAYER}/FeatureServer/0/query?where=BBL%3D{bbl}"
        f"&outFields={OUT_FIELDS}"
        "&orderByFields=OBJECTID%20ASC&resultRecordCount=10&resultOffset=0"
        "&f=json"
    )


CAPTURE_PLAN: dict[str, tuple[str, str, list[str]]] = {
    "MPG01_meta.json": (
        f"{LAYER}/FeatureServer/0?f=json",
        "Layer 0 metadata for MAPPLUTO: 103-field inventory, objectIdField, "
        "spatial reference (wkid 102718 / latestWkid 2263), maxRecordCount "
        "2000, editingInfo freshness signals",
        ["GEO-S1", "GEO-S8", "GEO-S11"],
    ),
    "MPG02_lot_single_1008350041.json": (
        _lot_query_path(1008350041),
        "Normal single-lot polygon by BBL (1008350041, Empire State "
        "Building): one feature, one clockwise exterior ring, attributes + "
        "Shape__Area for area cross-check",
        ["GEO-S1", "GEO-S3", "GEO-S7", "GEO-S9"],
    ),
    "MPG03_lot_nofeature_5999999999.json": (
        _lot_query_path(5999999999),
        "Syntactically valid nonexistent BBL: well-formed EMPTY features "
        "array - explicit typed no_feature outcome, never an error and "
        "never a guessed geometry",
        ["GEO-S3"],
    ),
    "MPG04_lot_condo_billing_1000157501.json": (
        _lot_query_path(1000157501),
        "Condo BILLING lot 1000157501 (lot 7501 in billing range 7501-7599, "
        "CondoNo 1025; research section 2.5): polygon represents the merged "
        "condominium complex, never a single unit",
        ["GEO-S4"],
    ),
    "MPG05_lot_condo_unit_1000151001.json": (
        _lot_query_path(1000151001),
        "Condo UNIT lot 1000151001 (lot 1001 in unit range 1001-6999) on "
        "the same block as billing lot 7501: EMPTY result captured live - "
        "MapPLUTO has one record per condo complex, unit lots carry no "
        "polygon (research section 2.5)",
        ["GEO-S4"],
    ),
    "MPG06_lot_holes_1000010010.json": (
        _lot_query_path(1000010010),
        "Holed polygon lot 1000010010 (Governors Island): one CW exterior "
        "ring + two CCW hole rings observed live - hole normalization and "
        "canonical ring ordering input",
        ["GEO-S2", "GEO-S7", "GEO-S9"],
    ),
    "MPG07_lot_multipolygon_4142600001.json": (
        _lot_query_path(4142600001),
        "TRUE MULTIPOLYGON lot 4142600001 (Queens; two CW exterior rings "
        "observed live, shoreline-clipped parts) - multipolygon member "
        "ordering and digest stability input",
        ["GEO-S2", "GEO-S7"],
    ),
}


def _sha256(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def _now_utc() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _write_fixture(name: str, payload: dict) -> None:
    path = FIXTURE_DIR / name
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    print(f"wrote {name} ({path.stat().st_size} bytes)")


def capture() -> None:
    for name, (rel_path, purpose, scenarios) in CAPTURE_PLAN.items():
        url = f"{SERVICE_ROOT}/{rel_path}"
        request = urllib.request.Request(url, headers={"Accept": "application/json"})
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                status = response.status
                body = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:  # capture non-2xx verbatim too
            status = exc.code
            body = exc.read().decode("utf-8")
        retrieved = _now_utc()
        _write_fixture(
            name,
            {
                "fixture_id": name.split("_")[0],
                "title": purpose,
                "source_id": SOURCE_ID,
                "layer": LAYER,
                "request_url": url,
                "http_status": status,
                "retrieval_timestamp_utc": retrieved,
                "capture_method": (
                    "live urllib GET by M2-T009 producer, keyless official "
                    "ArcGIS service, single KB-scale bounded request"
                ),
                "classification": "raw",
                "supports_scenarios": scenarios,
                "notes": purpose,
                "response_body_raw": body,
            },
        )
    build_manifest()


# ---------------------------------------------------------------------------
# Synthetic derivation (offline; every output labeled synthetic)
# ---------------------------------------------------------------------------


def _load(name: str) -> dict:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def _derive(
    source_name: str,
    out_name: str,
    purpose: str,
    scenarios: list[str],
    mutate,
    *,
    raw_text: str | None = None,
    http_status: int | None = None,
) -> None:
    src = _load(source_name)
    if raw_text is not None:
        body = raw_text
    else:
        parsed = json.loads(src["response_body_raw"])
        parsed = mutate(parsed)
        body = json.dumps(parsed, ensure_ascii=False)
    _write_fixture(
        out_name,
        {
            "fixture_id": out_name.split("_")[0],
            "title": purpose,
            "source_id": SOURCE_ID,
            "layer": LAYER,
            "request_url": src["request_url"],
            "http_status": src["http_status"] if http_status is None else http_status,
            "retrieval_timestamp_utc": src["retrieval_timestamp_utc"],
            "capture_method": (
                f"SYNTHETIC: derived offline from {source_name} by "
                "build_fixture_pack.py derive; NOT official data; exercises "
                "connector logic only"
            ),
            "classification": "synthetic",
            "derived_from": source_name,
            "supports_scenarios": scenarios,
            "notes": purpose,
            "response_body_raw": body,
        },
    )


def _replace_geometry(new_geometry) -> callable:
    """Mutator factory: replace the single feature's geometry object."""

    def mutate(doc: dict) -> dict:
        doc["features"][0]["geometry"] = new_geometry
        return doc

    return mutate


def derive() -> None:  # noqa: PLR0915 - explicit linear derivation plan
    # ---- metadata negatives -------------------------------------------
    def meta_wrong_crs(meta: dict) -> dict:
        meta["extent"]["spatialReference"] = {"wkid": 4326, "latestWkid": 4326}
        return meta

    _derive(
        "MPG01_meta.json",
        "MPG90_meta_wrong_crs_synthetic.json",
        "Metadata negative: spatial reference replaced with WGS84 (4326) - "
        "typed wrong_crs failure BEFORE any coordinate interpretation "
        "(authoritative CRS is EPSG:2263 / wkid 102718)",
        ["GEO-S8"],
        meta_wrong_crs,
    )

    def meta_missing_bbl(meta: dict) -> dict:
        meta["fields"] = [f for f in meta["fields"] if f["name"] != "BBL"]
        return meta

    _derive(
        "MPG01_meta.json",
        "MPG91_meta_missing_bbl_field_synthetic.json",
        "Metadata negative: BBL field removed from the live schema - typed "
        "schema_drift, never a silent field guess",
        ["GEO-S1"],
        meta_missing_bbl,
    )

    def meta_retyped_block(meta: dict) -> dict:
        for f in meta["fields"]:
            if f["name"] == "Block":
                f["type"] = "esriFieldTypeString"
        return meta

    _derive(
        "MPG01_meta.json",
        "MPG92_meta_retyped_block_synthetic.json",
        "Metadata negative: Block field re-typed to string - typed "
        "schema_drift",
        ["GEO-S1"],
        meta_retyped_block,
    )

    def meta_missing_oid(meta: dict) -> dict:
        meta.pop("objectIdField", None)
        return meta

    _derive(
        "MPG01_meta.json",
        "MPG93_meta_missing_objectid_synthetic.json",
        "Metadata negative: objectIdField removed - typed schema_drift "
        "(deterministic ordering cannot be established)",
        ["GEO-S1"],
        meta_missing_oid,
    )

    def meta_missing_mrc(meta: dict) -> dict:
        meta.pop("maxRecordCount", None)
        return meta

    _derive(
        "MPG01_meta.json",
        "MPG94_meta_missing_maxrecordcount_synthetic.json",
        "Metadata negative: maxRecordCount removed - typed schema_drift",
        ["GEO-S1"],
        meta_missing_mrc,
    )

    def meta_old_edit_date(meta: dict) -> dict:
        meta["editingInfo"]["dataLastEditDate"] = 1577836800000  # 2020-01-01
        return meta

    _derive(
        "MPG01_meta.json",
        "MPG95_meta_old_edit_date_synthetic.json",
        "Two-staleness rule: dataLastEditDate forced to 2020-01-01 - an old "
        "SOURCE dataset retrieved FRESH must never set transport staleness",
        ["GEO-S11"],
        meta_old_edit_date,
    )

    # ---- result-validation negatives ----------------------------------
    def duplicate_feature(doc: dict) -> dict:
        import copy as _copy

        twin = _copy.deepcopy(doc["features"][0])
        twin["attributes"]["OBJECTID"] = twin["attributes"]["OBJECTID"] + 1
        doc["features"].append(twin)
        return doc

    _derive(
        "MPG02_lot_single_1008350041.json",
        "MPG96_multiple_features_synthetic.json",
        "MULTIPLE features returned for one BBL (duplicated feature, "
        "distinct OBJECTID) - explicit typed multiple_features "
        "review-required outcome; never a silent first-pick",
        ["GEO-S3"],
        duplicate_feature,
    )

    def wrong_lot(doc: dict) -> dict:
        attrs = doc["features"][0]["attributes"]
        attrs["BBL"] = 1008350042
        attrs["Lot"] = 42
        return doc

    _derive(
        "MPG02_lot_single_1008350041.json",
        "MPG97_wrong_lot_returned_synthetic.json",
        "Feature BBL/Lot disagree with the requested lot - typed "
        "result_mismatch failure (returned data is never silently trusted)",
        ["GEO-S1"],
        wrong_lot,
    )

    def component_conflict(doc: dict) -> dict:
        doc["features"][0]["attributes"]["Block"] = 999
        return doc

    _derive(
        "MPG02_lot_single_1008350041.json",
        "MPG98_component_conflict_synthetic.json",
        "BBL matches the request but the Block component attribute "
        "disagrees with the BBL-derived block - visible identifier conflict "
        "surfaced on the result (never silently resolved)",
        ["GEO-S1"],
        component_conflict,
    )

    def query_wrong_crs(doc: dict) -> dict:
        doc["spatialReference"] = {"wkid": 4326, "latestWkid": 4326}
        return doc

    _derive(
        "MPG02_lot_single_1008350041.json",
        "MPG99_query_wrong_crs_synthetic.json",
        "Query response spatial reference replaced with WGS84 (4326) - "
        "typed wrong_crs BEFORE geometry interpretation; proves no "
        "degrees-based area path exists",
        ["GEO-S8"],
        query_wrong_crs,
    )

    # ---- invalid-geometry taxonomy (synthetic by necessity) -----------
    # Coordinates are small EPSG:2263-plausible offsets near the real ESB
    # lot so every shape stays in projected-feet space.
    x0, y0 = 987700.0, 211500.0

    def ring(points):
        return [[x0 + dx, y0 + dy] for dx, dy in points]

    bowtie = {  # self-intersecting single ring (crossing diagonals)
        "rings": [ring([(0, 0), (100, 100), (100, 0), (0, 100), (0, 0)])]
    }
    _derive(
        "MPG02_lot_single_1008350041.json",
        "MPG80_geom_self_intersection_synthetic.json",
        "Self-intersecting (bowtie) ring - typed invalid finding "
        "self_intersection; characterizable repair via pinned "
        "shapely.make_valid with original digest preserved",
        ["GEO-S5", "GEO-S6"],
        _replace_geometry(bowtie),
    )

    unclosed = {  # last vertex differs from first (open ring)
        "rings": [ring([(0, 0), (0, 100), (100, 100), (100, 0)])]
    }
    _derive(
        "MPG02_lot_single_1008350041.json",
        "MPG81_geom_unclosed_ring_synthetic.json",
        "Unclosed ring (first vertex not repeated at the end) - typed "
        "finding unclosed_ring; deterministic ring_closure repair recorded",
        ["GEO-S5", "GEO-S6"],
        _replace_geometry(unclosed),
    )

    duplicate_vertices = {
        "rings": [
            ring(
                [
                    (0, 0),
                    (0, 100),
                    (0, 100),  # exact consecutive duplicate
                    (100, 100),
                    (100, 0),
                    (0, 0),
                ]
            )
        ]
    }
    _derive(
        "MPG02_lot_single_1008350041.json",
        "MPG82_geom_duplicate_vertices_synthetic.json",
        "Consecutive duplicate vertex in a ring - typed finding "
        "duplicate_vertices; deterministic dedup repair recorded",
        ["GEO-S5", "GEO-S6"],
        _replace_geometry(duplicate_vertices),
    )

    degenerate_extra = {
        "rings": [
            # valid CW exterior (esri convention: CW = exterior)
            ring([(0, 0), (0, 100), (100, 100), (100, 0), (0, 0)]),
            # zero-area collinear ring
            ring([(200, 200), (250, 250), (300, 300), (200, 200)]),
        ]
    }
    _derive(
        "MPG02_lot_single_1008350041.json",
        "MPG83_geom_degenerate_ring_synthetic.json",
        "Zero-area collinear ring alongside a valid exterior - typed "
        "finding degenerate_ring; characterized drop_degenerate_ring "
        "repair (polygonal area unchanged)",
        ["GEO-S5", "GEO-S6"],
        _replace_geometry(degenerate_extra),
    )

    _derive(
        "MPG02_lot_single_1008350041.json",
        "MPG84_geom_empty_rings_synthetic.json",
        "Empty rings array - explicit typed empty_geometry invalid state",
        ["GEO-S5"],
        _replace_geometry({"rings": []}),
    )

    _derive(
        "MPG02_lot_single_1008350041.json",
        "MPG85_geom_null_synthetic.json",
        "Geometry JSON null - explicit typed null_geometry invalid state",
        ["GEO-S5"],
        _replace_geometry(None),
    )

    all_ccw = {  # only counterclockwise ring: esri orientation inverted
        "rings": [ring([(0, 0), (100, 0), (100, 100), (0, 100), (0, 0)])]
    }
    _derive(
        "MPG02_lot_single_1008350041.json",
        "MPG86_geom_orientation_all_ccw_synthetic.json",
        "Only counterclockwise ring(s): esri orientation convention "
        "(CW exterior) inverted - typed finding invalid_orientation, "
        "review_required (intent cannot be safely characterized)",
        ["GEO-S5"],
        _replace_geometry(all_ccw),
    )

    paths_surprise = {"paths": [ring([(0, 0), (100, 100)])]}
    _derive(
        "MPG02_lot_single_1008350041.json",
        "MPG87_geom_collection_paths_synthetic.json",
        "Polyline 'paths' payload where polygon 'rings' are contracted - "
        "typed finding geometry_collection (non-polygon surprise), "
        "invalid_geometry",
        ["GEO-S5"],
        _replace_geometry(paths_surprise),
    )

    hole_outside = {
        "rings": [
            # CW exterior 0..100
            ring([(0, 0), (0, 100), (100, 100), (100, 0), (0, 0)]),
            # CCW hole entirely OUTSIDE the exterior
            ring([(300, 300), (350, 300), (350, 350), (300, 350), (300, 300)]),
        ]
    }
    _derive(
        "MPG02_lot_single_1008350041.json",
        "MPG88_geom_hole_outside_shell_synthetic.json",
        "CCW hole ring located entirely outside every exterior ring - typed "
        "finding invalid_orientation, review_required (uncharacterizable "
        "topology; never silently repaired)",
        ["GEO-S5"],
        _replace_geometry(hole_outside),
    )

    # ---- transport/envelope negatives ---------------------------------
    def drop_features_key(doc: dict) -> dict:
        doc.pop("features", None)
        return doc

    _derive(
        "MPG02_lot_single_1008350041.json",
        "MPG100_malformed_missing_features_synthetic.json",
        "Well-formed JSON object WITHOUT a features key - typed "
        "malformed_response, never a valid empty result",
        ["GEO-S10"],
        drop_features_key,
    )

    src_body = _load("MPG02_lot_single_1008350041.json")["response_body_raw"]
    _derive(
        "MPG02_lot_single_1008350041.json",
        "MPG101_malformed_truncated_synthetic.json",
        "JSON truncated mid-body - typed malformed_response, NEVER a valid "
        "empty result",
        ["GEO-S10"],
        None,
        raw_text=src_body[: len(src_body) // 2],
    )

    _derive(
        "MPG02_lot_single_1008350041.json",
        "MPG102_arcgis_error_http200_synthetic.json",
        "ArcGIS error object delivered with HTTP 200 (envelope shape "
        "live-verified on the sibling DCP_GIS services, M2-T007 fixture "
        "ZF06) - typed upstream error, never data",
        ["GEO-S10"],
        None,
        raw_text=json.dumps(
            {
                "error": {
                    "code": 400,
                    "message": "Unable to complete operation.",
                    "details": [],
                }
            }
        ),
    )

    _derive(
        "MPG02_lot_single_1008350041.json",
        "MPG103_rate_limited_429_synthetic.json",
        "HTTP 429 throttle body (synthetic; cannot be triggered politely "
        "against the official service) - typed rate_limited via the "
        "bounded retry path",
        ["GEO-S10"],
        None,
        raw_text=json.dumps({"message": "Too Many Requests"}),
        http_status=429,
    )

    build_manifest()


# ---------------------------------------------------------------------------
# Manifest
# ---------------------------------------------------------------------------


def _crs_of(body: str) -> dict | None:
    try:
        doc = json.loads(body)
    except json.JSONDecodeError:
        return None
    sr = doc.get("spatialReference") or (doc.get("extent") or {}).get(
        "spatialReference"
    )
    if isinstance(sr, dict) and "wkid" in sr:
        out = {"wkid": sr["wkid"], "latestWkid": sr.get("latestWkid")}
        if sr.get("wkid") == 102718:
            out["authority"] = (
                "EPSG:2263 (NAD83 / New York Long Island, US survey feet)"
            )
        return out
    return None


def _edit_ms_of(body: str) -> int | None:
    try:
        doc = json.loads(body)
    except json.JSONDecodeError:
        return None
    editing = doc.get("editingInfo")
    if isinstance(editing, dict) and isinstance(
        editing.get("dataLastEditDate"), int
    ):
        return editing["dataLastEditDate"]
    return None


def _record_count_of(body: str) -> int | None:
    try:
        doc = json.loads(body)
    except json.JSONDecodeError:
        return None
    features = doc.get("features")
    if isinstance(features, list):
        return len(features)
    return None


def build_manifest() -> None:
    entries = []
    for path in sorted(FIXTURE_DIR.glob("MPG*.json")):
        fx = _load(path.name)
        body = fx["response_body_raw"]
        url = fx["request_url"]
        entries.append(
            {
                "file": path.name,
                "fixture_id": fx["fixture_id"],
                "classification": fx["classification"],
                "official_endpoint": url,
                "layer": fx["layer"],
                "query_parameters": url.split("?", 1)[1] if "?" in url else "",
                "http_status": fx["http_status"],
                "retrieval_timestamp_utc": fx["retrieval_timestamp_utc"],
                "source_data_last_edit_ms": _edit_ms_of(body),
                "crs": _crs_of(body),
                "expected_record_count": _record_count_of(body),
                "response_body_sha256": _sha256(body),
                "derived_from": fx.get("derived_from"),
                "purpose": fx["title"],
                "supports_scenarios": fx["supports_scenarios"],
            }
        )
    manifest = {
        "manifest_version": 1,
        "task": "M2-T009",
        "source_id": SOURCE_ID,
        "service_root": SERVICE_ROOT,
        "layer": LAYER,
        "authentication": (
            "none (keyless official service; no credential material exists "
            "in this pack)"
        ),
        "generated_by": "build_fixture_pack.py",
        "generated_at_utc": _now_utc(),
        "digest_algorithm": (
            "sha256:<hex> over the exact UTF-8 bytes of response_body_raw"
        ),
        "fixtures": entries,
    }
    path = FIXTURE_DIR / "MANIFEST.json"
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(manifest, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    print(f"wrote MANIFEST.json ({len(entries)} fixtures)")


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in {"capture", "derive"}:
        print("usage: build_fixture_pack.py capture|derive")
        raise SystemExit(2)
    if sys.argv[1] == "capture":
        capture()
    else:
        derive()
