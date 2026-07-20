"""Fixture-pack builder for the ZTLDB SODA connector (task M2-T008).

Two phases:

- ``capture``: live KB-scale reads of the official NYC Open Data SODA
  dataset ``fdkv-4t4z`` (anonymous; producer-local network use disclosed in
  the producer report; CI never runs this - CI is offline and replays the
  committed fixtures). Every captured fixture records the exact request URL
  and the retrieval timestamp (UTC) at capture time. No credential material
  of any kind is sent or stored.
- ``derive``: offline derivation of clearly-labeled SYNTHETIC fixtures from
  the captured raw fixtures (slash-tie special district, open-vocabulary
  zoning_district_1, observed-null, uniqueness violation, malformed bodies,
  paging pathologies, 429, freshness-signal negatives). Synthetic fixtures
  exercise connector logic only and are never presented as official data.

Both phases regenerate ``MANIFEST.json`` per the M2-T007 manifest
conventions: official endpoint, dataset id, query parameters, retrieval
timestamp, cryptographic digest, raw/synthetic classification with
``derived_from`` lineage, purpose, and supported acceptance scenarios.

Usage (from services/api):
    python tests/fixtures/ztldb/build_fixture_pack.py capture
    python tests/fixtures/ztldb/build_fixture_pack.py derive
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
DOMAIN = "https://data.cityofnewyork.us"
DATASET_ID = "fdkv-4t4z"
RESOURCE = f"{DOMAIN}/resource/{DATASET_ID}.json"
API_VIEWS = f"{DOMAIN}/api/views/{DATASET_ID}.json"
SOURCE_ID = "nyc-dcp-ztldb-soda"

# ---------------------------------------------------------------------------
# Capture plan: fixture file name -> (request URL, purpose, scenarios).
# All queries are bounded (single-BBL exact filters, count aggregate, tiny
# ordered pages, one metadata document, one deliberate 400).
# BBLs were located by bounded probe queries at build time (2026-07-20):
#   1000010100 - PLUTO fixture F01 lot (R3-2 + GI; no overlay/LH keys)
#   1000010010 - PLUTO fixture F05 split lot (R3-2 + C4-1, GI, map code Y)
#   1001110100 - commercial overlay lot (R7-2 + C1-5)
#   1000030001 - PARK lot (only zoning_district_1 + zoning_map_number keys)
#   1013760011 - limited height lot (R8B + LH-1A)
#   5999999999 - syntactically valid BBL with no ZTLDB row (no-record)
# ---------------------------------------------------------------------------

CAPTURE_PLAN: dict[str, tuple[str, str, list[str]]] = {
    "ZT01_record_single_lot.json": (
        f"{RESOURCE}?bbl=1000010100&%24order=bbl&%24limit=10",
        "Single-lot record for the PLUTO F01 golden lot: 16-column contract "
        "mapping, number-typed columns serialized as JSON strings, blank "
        "columns omitted per record (SODA null-omission)",
        ["ZT-S1", "ZT-S4", "ZT-S13", "ZT-S15"],
    ),
    "ZT02_record_split_lot.json": (
        f"{RESOURCE}?bbl=1000010010&%24order=bbl&%24limit=10",
        "Split-lot record (PLUTO F05 golden lot): zoning_district_1 R3-2 + "
        "zoning_district_2 C4-1 ordering preserved; special district GI; "
        "zoning_map_code Y border flag",
        ["ZT-S2", "ZT-S13", "ZT-S14"],
    ),
    "ZT03_no_record_valid_bbl.json": (
        f"{RESOURCE}?bbl=5999999999&%24order=bbl&%24limit=10",
        "Well-formed empty array for a syntactically valid BBL with no "
        "ZTLDB row: typed no-record RESULT, never an error",
        ["ZT-S3"],
    ),
    "ZT04_record_overlay_lot.json": (
        f"{RESOURCE}?bbl=1001110100&%24order=bbl&%24limit=10",
        "Commercial-overlay lot: commercial_overlay_1 C1-5 within the "
        "official Appendix C value set",
        ["ZT-S5"],
    ),
    "ZT05_record_park_lot.json": (
        f"{RESOURCE}?bbl=1000030001&%24order=bbl&%24limit=10",
        "PARK lot: zoning_district_1 PARK must carry the official "
        "do-not-use-for-open-space caveat; minimal key set demonstrates "
        "blank-omission semantics on a real record",
        ["ZT-S4", "ZT-S7"],
    ),
    "ZT06_record_limited_height_lot.json": (
        f"{RESOURCE}?bbl=1013760011&%24order=bbl&%24limit=10",
        "Limited-height lot: limited_height_district LH-1A within the "
        "official Appendix D value set",
        ["ZT-S5"],
    ),
    "ZT07a_page_offset0.json": (
        f"{RESOURCE}?%24order=bbl&%24limit=5&%24offset=0",
        "Deterministic ordered page 1 (bbl ascending, limit 5, offset 0); "
        "includes real records with absent zoning_district_1 (blank ZD1 "
        "rows exist live despite the 2019-12-31 assignment change)",
        ["ZT-S9", "ZT-S15"],
    ),
    "ZT07b_page_offset5.json": (
        f"{RESOURCE}?%24order=bbl&%24limit=5&%24offset=5",
        "Deterministic ordered page 2 (bbl ascending, limit 5, offset 5): "
        "no duplicates or gaps across the page boundary",
        ["ZT-S9"],
    ),
    "ZT08_api_views_metadata.json": (
        API_VIEWS,
        "Authoritative dataset metadata: the 16-column columns array "
        "(schema authority - never inferred from record keys) and "
        "rowsUpdatedAt (the ONLY official freshness signal; no per-record "
        "version column exists)",
        ["ZT-S10", "ZT-S11"],
    ),
    "ZT09_row_count.json": (
        f"{RESOURCE}?%24select=count%28bbl%29",
        "Row-count baseline at capture time (dataset-scale evidence; the "
        "connector never syncs the full dataset)",
        ["ZT-S10"],
    ),
    "ZT10_no_such_column_400.json": (
        f"{RESOURCE}?%24select=nonexistent_column&%24limit=1",
        "Deliberate HTTP 400 with errorCode query.soql.no-such-column: the "
        "schema-drift signature (drift evidence, not data; never retried)",
        ["ZT-S11"],
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
    for name, (url, purpose, scenarios) in CAPTURE_PLAN.items():
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
                "dataset_id": DATASET_ID,
                "request_url": url,
                "http_status": status,
                "retrieval_timestamp_utc": retrieved,
                "capture_method": (
                    "live urllib GET by M2-T008 producer, anonymous request "
                    "to the official NYC Open Data SODA endpoint, single "
                    "KB-scale bounded request"
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
            "dataset_id": DATASET_ID,
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


def derive() -> None:
    def slash_tie(records: list) -> list:
        # Plausible Appendix-A pair joined by '/': no live row currently
        # carries a slash value (probed 2026-07-20; research OQ-8 stays
        # open), so the documented tie representation is exercised
        # synthetically with two real Appendix A abbreviations.
        records[0]["special_district_1"] = "GI/WP"
        return records

    def open_zd1(records: list) -> list:
        # Research G1 C4: the official Socrata column description states
        # zoning_district_1 may contain a Zoning Resolution section number
        # for selected Queens properties. No such value exists in the live
        # rows today (bounded group-by probe, 2026-07-20), so the open-set
        # behavior is exercised synthetically.
        records[0]["zoning_district_1"] = "107-42"
        return records

    def observed_null(records: list) -> list:
        # SODA omits blank keys; an EXPLICIT null is a distinct
        # observed-null observation, never conflated with omission.
        records[0]["commercial_overlay_1"] = None
        return records

    def duplicate_bbl(records: list) -> list:
        return [records[0], dict(records[0])]

    def unknown_column(records: list) -> list:
        records[0]["mystery_column"] = "x"
        return records

    def page_no_progress(records: list) -> list:
        # A page whose rows were ALL already seen on the previous page
        # (zero new records = no progress).
        return records[:3]

    def drop_rows_updated(meta: dict) -> dict:
        meta.pop("rowsUpdatedAt", None)
        return meta

    def rename_column(meta: dict) -> dict:
        for column in meta["columns"]:
            if column.get("fieldName") == "zoning_district_1":
                column["fieldName"] = "zoning_district_1_renamed"
        return meta

    _derive(
        "ZT01_record_single_lot.json", "ZT90_record_slash_tie_synthetic.json",
        "Slash-tie special district: special_district_1 'GI/WP' must parse "
        "to two Appendix A abbreviations with the official tie semantics "
        "preserved", ["ZT-S6"], slash_tie,
    )
    _derive(
        "ZT01_record_single_lot.json", "ZT91_record_open_zd1_synthetic.json",
        "Open zoning_district_1 vocabulary: a ZR-section-number-shaped value "
        "must be accepted as a typed open-set observation, never rejected "
        "or coerced", ["ZT-S8"], open_zd1,
    )
    _derive(
        "ZT01_record_single_lot.json", "ZT92_record_observed_null_synthetic.json",
        "Explicit JSON null on a normally-omitted column: the distinct "
        "observed-null path (never conflated with not-applicable omission)",
        ["ZT-S4"], observed_null,
    )
    _derive(
        "ZT01_record_single_lot.json", "ZT93_record_duplicate_bbl_synthetic.json",
        "Two records for one BBL: violates the one-row-per-tax-lot dataset "
        "contract - typed schema_drift, never a silent pick", ["ZT-S1"],
        duplicate_bbl,
    )
    _derive(
        "ZT01_record_single_lot.json", "ZT94_malformed_not_array_synthetic.json",
        "Malformed response: JSON object instead of the documented array - "
        "typed malformed_response, NEVER a valid empty result", ["ZT-S3"],
        None, raw_text='{"unexpected": "shape"}',
    )
    _derive(
        "ZT01_record_single_lot.json", "ZT95_malformed_truncated_synthetic.json",
        "Malformed response: JSON truncated mid-body - typed "
        "malformed_response, NEVER a valid empty result", ["ZT-S3"], None,
        raw_text=_load("ZT01_record_single_lot.json")["response_body_raw"][:60],
    )
    _derive(
        "ZT07b_page_offset5.json", "ZT96_page_duplicate_synthetic.json",
        "Paging pathology: page 2 body is byte-identical to page 1 "
        "(upstream returned the same page twice) - typed paging failure, "
        "no silent duplication", ["ZT-S9"], None,
        raw_text=_load("ZT07a_page_offset0.json")["response_body_raw"],
    )
    _derive(
        "ZT07a_page_offset0.json", "ZT97_page_no_progress_synthetic.json",
        "Paging pathology: page whose rows were all already extracted "
        "(zero new records) - typed no-progress failure, never a loop",
        ["ZT-S9"], page_no_progress,
    )
    _derive(
        "ZT01_record_single_lot.json", "ZT98_rate_limited_429_synthetic.json",
        "HTTP 429 throttle body (synthetic; not triggered against the "
        "official service on purpose) - typed rate_limited via the bounded "
        "retry path", ["ZT-S12"], None,
        raw_text='{"message": "Too Many Requests"}', http_status=429,
    )
    _derive(
        "ZT08_api_views_metadata.json",
        "ZT99_meta_missing_rows_updated_synthetic.json",
        "Freshness-guard negative: rowsUpdatedAt removed from the dataset "
        "metadata - the ONLY official freshness signal is missing; typed "
        "schema_drift, never a silent default", ["ZT-S10"], drop_rows_updated,
    )
    _derive(
        "ZT10_no_such_column_400.json", "ZT100_type_mismatch_400_synthetic.json",
        "Non-drift HTTP 400: errorCode query.soql.type-mismatch is NOT the "
        "schema-drift signature and maps to a typed upstream error",
        ["ZT-S11"], None,
        raw_text=(
            '{"message": "Invalid SoQL: type mismatch", '
            '"errorCode": "query.soql.type-mismatch", "data": {}}'
        ),
        http_status=400,
    )
    _derive(
        "ZT01_record_single_lot.json", "ZT101_record_unknown_column_synthetic.json",
        "Unknown record key: a column outside the authoritative 16-column "
        "inventory yields a visible drift signal and NO fact (schema is "
        "never inferred from record keys)", ["ZT-S11"], unknown_column,
    )
    _derive(
        "ZT08_api_views_metadata.json", "ZT102_meta_renamed_column_synthetic.json",
        "Columns-array drift: zoning_district_1 renamed in the metadata "
        "columns snapshot - detected as removed+added by the columns diff",
        ["ZT-S11"], rename_column,
    )
    build_manifest()


# ---------------------------------------------------------------------------
# Manifest (M2-T007 conventions)
# ---------------------------------------------------------------------------


def build_manifest() -> None:
    entries = []
    for path in sorted(FIXTURE_DIR.glob("ZT*.json")):
        fixture = json.loads(path.read_text(encoding="utf-8"))
        body = fixture["response_body_raw"]
        expected_record_count = None
        rows_updated_at = None
        try:
            parsed = json.loads(body)
        except json.JSONDecodeError:
            parsed = None  # intentionally-malformed synthetic fixtures
        if isinstance(parsed, list):
            expected_record_count = len(parsed)
        elif isinstance(parsed, dict):
            rows_updated_at = parsed.get("rowsUpdatedAt")
        entries.append(
            {
                "file": path.name,
                "fixture_id": fixture["fixture_id"],
                "classification": fixture["classification"],
                "official_endpoint": fixture["request_url"],
                "dataset_id": fixture["dataset_id"],
                "query_parameters": fixture["request_url"].split("?", 1)[1]
                if "?" in fixture["request_url"]
                else None,
                "http_status": fixture["http_status"],
                "retrieval_timestamp_utc": fixture["retrieval_timestamp_utc"],
                "rows_updated_at_raw": rows_updated_at,
                "expected_record_count": expected_record_count,
                "response_body_sha256": _sha256(body),
                "derived_from": fixture.get("derived_from"),
                "purpose": fixture["title"],
                "supports_scenarios": fixture["supports_scenarios"],
            }
        )
    manifest = {
        "manifest_version": 1,
        "task": "M2-T008",
        "source_id": SOURCE_ID,
        "dataset_id": DATASET_ID,
        "resource_endpoint": RESOURCE,
        "api_views_endpoint": API_VIEWS,
        "authentication": (
            "none used for any capture (anonymous official SODA reads); the "
            "optional runtime app credential is environment-sourced only and "
            "never appears anywhere in this pack"
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
