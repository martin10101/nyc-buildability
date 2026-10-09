"""Integrity of the recorded Wallabout records pack (queue item B-08; plan M2-00).

``services/api/tests/fixtures/benchmark_298_wallabout/`` holds official responses for the Pilot B
condominium case at 298 Wallabout Street, Brooklyn (block 2264, base lots 32 & 33, condo billing lot
7515), captured once on 2026-10-02 UTC. ``MANIFEST.json`` pins each file by SHA-256 of its exact
bytes. These tests are offline: they re-hash every file and prove that each connector-backed request
URL is the one the connector itself builds.

The MapPLUTO geometry connector imports ``shapely`` (a CI dependency); to keep this integrity test
collectable without it, the MapPLUTO URL is checked against the documented string shape rather than
rebuilt from an import.
"""

import hashlib
import json
from pathlib import Path

import pytest

from app.connectors import (
    dcm_street_centerline_arcgis,
    pluto_soda,
    ztldb_soda,
)

PACK = Path(__file__).resolve().parents[1] / "fixtures" / "benchmark_298_wallabout"
MANIFEST = json.loads((PACK / "MANIFEST.json").read_text(encoding="utf-8"))
ENTRIES = {entry["file"]: entry for entry in MANIFEST["files"]}
NOT_RECORDINGS = {"MANIFEST.json", "README.md", ".gitattributes"}

BILLING_BBL = "3022647515"
BASE_LOTS = ("3022640032", "3022640033")
# EPSG:2263 bbox of the billing-lot MapPLUTO ring padded by 100 ft (the wide-street buffer), the
# exact envelope the DCM query used at capture (see MANIFEST 'connector' note).
DCM_PAD_FT = 100.0
MAPPLUTO_URL = (
    "https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/MAPPLUTO/FeatureServer/0/"
    "query?where=BBL%3D3022647515&outFields=OBJECTID%2CBBL%2CBoroCode%2CBorough%2CBlock%2CLot"
    "%2CCondoNo%2CVersion%2CShape__Area%2CShape__Length&returnGeometry=true&outSR=2263&f=json"
)


def _billing_ring() -> list[list[float]]:
    doc = json.loads((PACK / "mappluto_lot_3022647515_epsg2263.json").read_bytes())
    return doc["features"][0]["geometry"]["rings"][0]


def _dcm_envelope() -> tuple[float, float, float, float]:
    ring = _billing_ring()
    xs = [p[0] for p in ring]
    ys = [p[1] for p in ring]
    return (
        round(min(xs) - DCM_PAD_FT, 4),
        round(min(ys) - DCM_PAD_FT, 4),
        round(max(xs) + DCM_PAD_FT, 4),
        round(max(ys) + DCM_PAD_FT, 4),
    )


def _rows(name: str) -> list:
    return json.loads((PACK / name).read_bytes())


def test_manifest_lists_exactly_the_recorded_files():
    on_disk = {path.name for path in PACK.iterdir()} - NOT_RECORDINGS
    assert on_disk == set(ENTRIES)
    assert len(MANIFEST["files"]) == len(ENTRIES)
    assert MANIFEST["bbls"]["billing"] == BILLING_BBL
    assert MANIFEST["bbls"]["base_lots"] == list(BASE_LOTS)


@pytest.mark.parametrize("name", sorted(ENTRIES))
def test_file_bytes_match_manifest_sha256(name):
    entry = ENTRIES[name]
    body = (PACK / name).read_bytes()
    assert len(body) == entry["bytes"]
    assert hashlib.sha256(body).hexdigest() == entry["sha256"]
    assert entry["http_status"] == 200


def test_connector_backed_urls_match_their_builders():
    assert ENTRIES["pluto_64uk-42ks_bbl_3022647515.json"]["url"] == (
        f"{pluto_soda.BASE_URL}?bbl={BILLING_BBL}"
    )
    for bbl in BASE_LOTS:
        assert ENTRIES[f"pluto_64uk-42ks_bbl_{bbl}.json"]["url"] == (
            f"{pluto_soda.BASE_URL}?bbl={bbl}"
        )
        assert ENTRIES[f"ztldb_fdkv-4t4z_bbl_{bbl}.json"]["url"] == (
            ztldb_soda.build_record_url(bbl)
        )
    assert ENTRIES["ztldb_fdkv-4t4z_bbl_3022647515.json"]["url"] == (
        ztldb_soda.build_record_url(BILLING_BBL)
    )
    assert ENTRIES["dcm_street_centerline_lot_envelope_3022647515.json"]["url"] == (
        dcm_street_centerline_arcgis.build_segment_query_url(envelope=_dcm_envelope())
    )
    assert ENTRIES["mappluto_lot_3022647515_epsg2263.json"]["url"] == MAPPLUTO_URL


def test_pluto_billing_row_and_absent_base_lots():
    billing = _rows("pluto_64uk-42ks_bbl_3022647515.json")
    assert len(billing) == 1
    row = billing[0]
    assert row["zonedist1"] == "R7-1"
    assert row["yearbuilt"] == "2005"
    assert row["unitsres"] == "20"
    # DOF building area is recorded for reference only; never used as zoning floor area.
    assert row["bldgarea"] == "32289"
    # Condo base lots carry no separate PLUTO record (plan section 4).
    for bbl in BASE_LOTS:
        assert _rows(f"pluto_64uk-42ks_bbl_{bbl}.json") == []


def test_ztldb_base_lots_are_r7_1_and_billing_lot_absent():
    for bbl in BASE_LOTS:
        rows = _rows(f"ztldb_fdkv-4t4z_bbl_{bbl}.json")
        assert len(rows) == 1
        assert rows[0]["zoning_district_1"] == "R7-1"
    # ZTLDB is keyed by base tax lots: the condo billing lot has no record.
    assert _rows("ztldb_fdkv-4t4z_bbl_3022647515.json") == []


def test_dob_permits_recorded_and_no_name_columns_leaked():
    bis = _rows("dob_bis_jobs_ic3t-wcy2_bin_3388750.json")
    assert any(r["job__"] == "301396567" and r["job_type"] == "NB" for r in bis)
    now = _rows("dob_now_jobs_w9ak-ipjd_bbl_3022647515.json")
    assert now and all(r["bin"] == "3388750" for r in now)
    # Certificate-of-occupancy datasets have no row for this building.
    assert _rows("dob_now_co_pkdm-hqz6_bbl_3022647515.json") == []
    assert _rows("dob_bis_co_bs8b-p36w_bin_3388750.json") == []
    # The $select keeps applicant/owner/filing-representative names out of the recorded bodies.
    forbidden = ("owner", "applicant", "first_name", "last_name", "filing_representative")
    for name in ("dob_bis_jobs_ic3t-wcy2_bin_3388750.json",
                 "dob_now_jobs_w9ak-ipjd_bbl_3022647515.json"):
        keys = {k for r in _rows(name) for k in r}
        assert not any(bad in k.lower() for k in keys for bad in forbidden)


def test_acris_is_flag_only_index_metadata():
    for name in ("acris_legals_8h5j-fqxa_bbl_3-2264-32.json",
                 "acris_legals_8h5j-fqxa_bbl_3-2264-33.json"):
        rows = _rows(name)
        assert rows, f"{name} should list at least one document id"
        for row in rows:
            assert row["block"] == "2264"
            assert "document_id" in row


def test_dcm_envelope_segments_carry_free_text_widths():
    feats = json.loads(
        (PACK / "dcm_street_centerline_lot_envelope_3022647515.json").read_bytes()
    )["features"]
    names = {f["attributes"]["Street_NM"] for f in feats}
    assert "Wallabout Street" in names
    # One-sided bounds are present and must never be resolved to a width here (D-052).
    widths = {f["attributes"]["Streetwidth"] for f in feats}
    assert ">75" in widths
