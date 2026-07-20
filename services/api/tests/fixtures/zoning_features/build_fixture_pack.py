"""Fixture-pack builder for the GIS Zoning Features connector (task M2-T007).

Two phases:

- ``capture``: live KB-scale reads of the six official DCP_GIS ArcGIS
  services (keyless; producer-local network use disclosed in the producer
  report; CI never runs this - CI is offline and replays the committed
  fixtures). Every captured fixture records the exact request URL and the
  retrieval timestamp (UTC) at capture time.
- ``derive``: offline derivation of clearly-labeled SYNTHETIC fixtures from
  the captured raw fixtures (metadata negatives, drift shapes, paging
  pathologies, malformed bodies, 429). Synthetic fixtures exercise connector
  logic only and are never presented as official data.

Both phases regenerate ``MANIFEST.json`` (packet safeguard 5): official
endpoint, layer id, safe query parameters, retrieval timestamp, source edit
timestamp where available, CRS, expected record count, cryptographic digest,
raw/synthetic classification, purpose, and supported acceptance scenario per
fixture. No secrets or tokens exist anywhere in this pack (the services are
keyless and no auth header is ever sent).

Usage (from services/api):
    python tests/fixtures/zoning_features/build_fixture_pack.py capture
    python tests/fixtures/zoning_features/build_fixture_pack.py derive
"""

from __future__ import annotations

import hashlib
import json
import sys
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

FIXTURE_DIR = Path(__file__).resolve().parent
SERVICE_ROOT = "https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services"
LAYERS = ("nyzd", "nyco", "nysp", "nysp_sd", "nylh", "nyzma")

# ---------------------------------------------------------------------------
# Capture plan: fixture file name -> (relative request path, purpose,
# supported scenarios). All queries are bounded (returnCountOnly, single
# feature, or 6-feature pages on the 14-feature nylh layer).
# ---------------------------------------------------------------------------


def _meta_path(layer: str) -> str:
    return f"{layer}/FeatureServer/0?f=json"


def _count_path(layer: str) -> str:
    return f"{layer}/FeatureServer/0/query?where=1%3D1&returnCountOnly=true&f=json"


CAPTURE_PLAN: dict[str, tuple[str, str, str, list[str]]] = {}
_META_IDS = dict(zip(LAYERS, "abcdef", strict=True))
for _layer in LAYERS:
    CAPTURE_PLAN[f"ZF01{_META_IDS[_layer]}_meta_{_layer}.json"] = (
        _meta_path(_layer),
        _layer,
        f"Layer 0 metadata for {_layer}: field inventory, objectIdField, "
        "spatial reference, maxRecordCount, editingInfo freshness signals",
        ["ZF-S1", "ZF-S12"],
    )
    CAPTURE_PLAN[f"ZF02{_META_IDS[_layer]}_count_{_layer}.json"] = (
        _count_path(_layer),
        _layer,
        f"returnCountOnly baseline for {_layer} at capture time "
        "(count-vs-page-total consistency input)",
        ["ZF-S2"],
    )
CAPTURE_PLAN["ZF03_query_nyzd_single_R3-2.json"] = (
    "nyzd/FeatureServer/0/query?where=ZONEDIST%3D%27R3-2%27&outFields=*"
    "&orderByFields=OBJECTID%20ASC&resultRecordCount=1&resultOffset=0&f=json",
    "nyzd",
    "Bounded single-feature attribute query: typed record with attributes, "
    "polygon rings, CRS, provenance stamps",
    ["ZF-S3", "ZF-S10"],
)
CAPTURE_PLAN["ZF04a_page_nylh_offset0.json"] = (
    "nylh/FeatureServer/0/query?where=1%3D1&outFields=*"
    "&orderByFields=OBJECTID%20ASC&resultRecordCount=6&resultOffset=0&f=json",
    "nylh",
    "Real multi-page extraction page 1 of 3 (page size 6 < total 14): "
    "exceededTransferLimit=true observed live (OQ-11 resolution evidence)",
    ["ZF-S4", "ZF-S10"],
)
CAPTURE_PLAN["ZF04b_page_nylh_offset6.json"] = (
    "nylh/FeatureServer/0/query?where=1%3D1&outFields=*"
    "&orderByFields=OBJECTID%20ASC&resultRecordCount=6&resultOffset=6&f=json",
    "nylh",
    "Real multi-page extraction page 2 of 3",
    ["ZF-S4", "ZF-S10"],
)
CAPTURE_PLAN["ZF04c_page_nylh_offset12.json"] = (
    "nylh/FeatureServer/0/query?where=1%3D1&outFields=*"
    "&orderByFields=OBJECTID%20ASC&resultRecordCount=6&resultOffset=12&f=json",
    "nylh",
    "Real multi-page extraction final page 3 of 3 (2 records, no "
    "exceededTransferLimit)",
    ["ZF-S4", "ZF-S10"],
)
CAPTURE_PLAN["ZF05_query_nyzd_nomatch_XX.json"] = (
    "nyzd/FeatureServer/0/query?where=ZONEDIST%3D%27XX%27&outFields=*"
    "&orderByFields=OBJECTID%20ASC&f=json",
    "nyzd",
    "Well-formed empty result (no zoning district named XX): empty features "
    "array is a VALID empty result",
    ["ZF-S6"],
)
CAPTURE_PLAN["ZF06_arcgis_error_bad_field.json"] = (
    "nyzd/FeatureServer/0/query?where=NOSUCHFIELD%3D1&outFields=*&f=json",
    "nyzd",
    "Live ArcGIS error-object behavior for an invalid field reference "
    "(records the ACTUAL http status + error envelope of these services)",
    ["ZF-S7"],
)
CAPTURE_PLAN["ZF07_query_nyzma_single.json"] = (
    "nyzma/FeatureServer/0/query?where=1%3D1&outFields=*"
    "&orderByFields=OBJECTID%20ASC&resultRecordCount=1&resultOffset=0&f=json",
    "nyzma",
    "Single nyzma record: esriFieldTypeDate EFFECTIVE attribute shape "
    "(epoch ms) preserved verbatim in normalized records",
    ["ZF-S3"],
)


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
    for name, (rel_path, layer, purpose, scenarios) in CAPTURE_PLAN.items():
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
                "source_id": "nyc-dcp-zoning-features-arcgis",
                "layer": layer,
                "request_url": url,
                "http_status": status,
                "retrieval_timestamp_utc": retrieved,
                "capture_method": (
                    "live urllib GET by M2-T007 producer, keyless official "
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
            "source_id": "nyc-dcp-zoning-features-arcgis",
            "layer": src["layer"],
            "request_url": src["request_url"],
            "http_status": src["http_status"] if http_status is None else http_status,
            "retrieval_timestamp_utc": src["retrieval_timestamp_utc"],
            "capture_method": (
                f"SYNTHETIC: derived offline from {source_name} by "
                "build_fixture_pack.py derive; NOT official data; exercises "
                "connector failure logic only"
            ),
            "classification": "synthetic",
            "derived_from": source_name,
            "supports_scenarios": scenarios,
            "notes": purpose,
            "response_body_raw": body,
        },
    )


def derive() -> None:
    def drop_object_id(meta: dict) -> dict:
        meta.pop("objectIdField", None)
        return meta

    def wrong_crs(meta: dict) -> dict:
        meta["extent"]["spatialReference"] = {"wkid": 4326, "latestWkid": 4326}
        return meta

    def drop_max_record_count(meta: dict) -> dict:
        meta.pop("maxRecordCount", None)
        return meta

    def rename_zonedist(meta: dict) -> dict:
        for field in meta["fields"]:
            if field["name"] == "ZONEDIST":
                field["name"] = "ZONE_DIST"
                field["alias"] = "ZONE_DIST"
        return meta

    def add_field(meta: dict) -> dict:
        meta["fields"].append(
            {
                "name": "NEW_UNEXPECTED",
                "type": "esriFieldTypeString",
                "alias": "NEW_UNEXPECTED",
                "sqlType": "sqlTypeOther",
                "length": 10,
                "nullable": True,
                "editable": True,
                "domain": None,
                "defaultValue": None,
            }
        )
        return meta

    def old_edit_date(meta: dict) -> dict:
        # 2020-01-01T00:00:00Z epoch ms: an OLD source-dataset edit date with
        # a FRESH retrieval - must NOT set transport staleness (ZF-S12).
        meta["editingInfo"] = {
            "lastEditDate": 1577836800000,
            "schemaLastEditDate": 1577836800000,
            "dataLastEditDate": 1577836800000,
        }
        return meta

    def repeated_oid(page: dict) -> dict:
        # Second page whose first feature repeats OBJECTID 6 from page 1.
        page["features"][0]["attributes"]["OBJECTID"] = 6
        return page

    def zero_progress(page: dict) -> dict:
        page["features"] = []
        page["exceededTransferLimit"] = True
        return page

    def drop_features_key(page: dict) -> dict:
        page.pop("features", None)
        return page

    _derive(
        "ZF01a_meta_nyzd.json", "ZF90_meta_nyzd_missing_objectid_synthetic.json",
        "Metadata negative: objectIdField removed - connector must fail typed "
        "(schema_drift), never guess an ordering field", ["ZF-S1"], drop_object_id,
    )
    _derive(
        "ZF01a_meta_nyzd.json", "ZF91_meta_nyzd_wrong_crs_synthetic.json",
        "Metadata negative: spatial reference replaced with WGS84 (4326) - "
        "connector must fail typed on wrong CRS (authoritative CRS is "
        "EPSG:2263 / wkid 102718)", ["ZF-S1"], wrong_crs,
    )
    _derive(
        "ZF01a_meta_nyzd.json", "ZF92_meta_nyzd_missing_maxrecordcount_synthetic.json",
        "Metadata negative: maxRecordCount removed - paging cannot be planned "
        "safely; connector must fail typed", ["ZF-S1"], drop_max_record_count,
    )
    _derive(
        "ZF01a_meta_nyzd.json", "ZF93_meta_nyzd_renamed_field_synthetic.json",
        "Schema drift: ZONEDIST renamed to ZONE_DIST - typed drift failure, "
        "never a silent field guess", ["ZF-S9"], rename_zonedist,
    )
    _derive(
        "ZF01a_meta_nyzd.json", "ZF94_meta_nyzd_added_field_synthetic.json",
        "Schema drift: unexpected added field NEW_UNEXPECTED - typed "
        "degradation signal (visible, non-fatal)", ["ZF-S9"], add_field,
    )
    _derive(
        "ZF01e_meta_nylh.json", "ZF95_meta_nylh_old_edit_date_synthetic.json",
        "Two-staleness rule: dataLastEditDate forced to 2020-01-01 - an old "
        "SOURCE dataset with a FRESH retrieval must NOT set "
        "served_from_cache/stale", ["ZF-S12"], old_edit_date,
    )
    dup_src = _load("ZF04a_page_nylh_offset0.json")
    _derive(
        "ZF04b_page_nylh_offset6.json", "ZF96_page_nylh_duplicate_page_synthetic.json",
        "Paging pathology: page 2 body is byte-identical to page 1 (upstream "
        "returned the same page twice) - typed paging failure, no silent "
        "duplication", ["ZF-S5"], None,
        raw_text=dup_src["response_body_raw"],
    )
    _derive(
        "ZF04b_page_nylh_offset6.json", "ZF97_page_nylh_repeated_oid_synthetic.json",
        "Paging pathology: page 2 repeats OBJECTID 6 from page 1 - typed "
        "paging failure (repeated object id)", ["ZF-S5"], repeated_oid,
    )
    _derive(
        "ZF04b_page_nylh_offset6.json", "ZF98_page_nylh_zero_progress_synthetic.json",
        "Paging pathology: empty features with exceededTransferLimit=true - "
        "zero-progress loop guard must fail typed, never spin", ["ZF-S5"],
        zero_progress,
    )
    _derive(
        "ZF04a_page_nylh_offset0.json", "ZF99_malformed_truncated_synthetic.json",
        "Malformed response: JSON truncated mid-body - typed "
        "malformed_response, NEVER a valid empty result", ["ZF-S6"], None,
        raw_text=dup_src["response_body_raw"][: len(dup_src["response_body_raw"]) // 2],
    )
    _derive(
        "ZF04a_page_nylh_offset0.json",
        "ZF100_malformed_missing_features_key_synthetic.json",
        "Malformed response: well-formed JSON object WITHOUT a features key - "
        "typed malformed_response, never an empty result", ["ZF-S6"],
        drop_features_key,
    )
    _derive(
        "ZF04a_page_nylh_offset0.json", "ZF101_rate_limited_429_synthetic.json",
        "HTTP 429 throttle body (synthetic; cannot be triggered politely "
        "against the official service) - typed rate_limited via the "
        "resilience retry path", ["ZF-S8"], None,
        raw_text='{"error":{"code":429,"message":"Too many requests","details":[]}}',
        http_status=429,
    )
    _derive(
        "ZF04a_page_nylh_offset0.json", "ZF102_arcgis_error_http200_synthetic.json",
        "ArcGIS error object delivered with HTTP 200: SECOND envelope "
        "variant (generic 'Unable to complete operation.' shape) alongside "
        "the LIVE-captured ZF06 (which proved HTTP 200 + error.code 400 "
        "live) - typed upstream error, never data", ["ZF-S7"], None,
        raw_text=(
            '{"error":{"code":400,"message":"Unable to complete operation.",'
            '"details":["Unable to perform query operation."]}}'
        ),
        http_status=200,
    )
    build_manifest()


# ---------------------------------------------------------------------------
# Manifest (packet safeguard 5)
# ---------------------------------------------------------------------------


def build_manifest() -> None:
    entries = []
    for path in sorted(FIXTURE_DIR.glob("ZF*.json")):
        fixture = json.loads(path.read_text(encoding="utf-8"))
        body = fixture["response_body_raw"]
        crs = None
        expected_record_count = None
        source_edit_ms = None
        try:
            parsed = json.loads(body)
        except json.JSONDecodeError:
            parsed = None  # intentionally-malformed synthetic fixtures
        if isinstance(parsed, dict):
            if "count" in parsed:
                expected_record_count = parsed["count"]
            if isinstance(parsed.get("features"), list):
                expected_record_count = len(parsed["features"])
            sr = parsed.get("spatialReference") or (parsed.get("extent") or {}).get(
                "spatialReference"
            )
            if isinstance(sr, dict):
                crs = {
                    "wkid": sr.get("wkid"),
                    "latestWkid": sr.get("latestWkid"),
                    "authority": "EPSG:2263 (NAD83 / New York Long Island, US survey feet)",
                }
            editing = parsed.get("editingInfo")
            if isinstance(editing, dict):
                source_edit_ms = editing.get("dataLastEditDate")
        entries.append(
            {
                "file": path.name,
                "fixture_id": fixture["fixture_id"],
                "classification": fixture["classification"],
                "official_endpoint": fixture["request_url"],
                "layer": fixture["layer"],
                "query_parameters": fixture["request_url"].split("?", 1)[1]
                if "?" in fixture["request_url"]
                else None,
                "http_status": fixture["http_status"],
                "retrieval_timestamp_utc": fixture["retrieval_timestamp_utc"],
                "source_data_last_edit_ms": source_edit_ms,
                "crs": crs,
                "expected_record_count": expected_record_count,
                "response_body_sha256": _sha256(body),
                "derived_from": fixture.get("derived_from"),
                "purpose": fixture["title"],
                "supports_scenarios": fixture["supports_scenarios"],
            }
        )
    manifest = {
        "manifest_version": 1,
        "task": "M2-T007",
        "source_id": "nyc-dcp-zoning-features-arcgis",
        "service_root": SERVICE_ROOT,
        "authentication": "none (keyless official services; no tokens exist in this pack)",
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
    phase = sys.argv[1] if len(sys.argv) > 1 else ""
    if phase == "capture":
        capture()
    elif phase == "derive":
        derive()
    elif phase == "manifest":
        build_manifest()
    else:
        print("usage: build_fixture_pack.py capture|derive|manifest")
        sys.exit(2)
