"""Integrity of the recorded DOF sales pack (queue item B-11; plan section 11b).

``services/api/tests/fixtures/dof_sales_bayside/`` holds official DOF sales responses for the
comparable-sales slice, captured once on 2026-10-02 UTC. ``MANIFEST.json`` pins each file by
SHA-256 of its exact bytes. These tests are offline: they re-hash every file and prove that
each connector-backed request URL is the one the connector itself builds.
"""

import hashlib
import json
from pathlib import Path

from app.connectors.dof_sales_soda import build_by_bbl_url, build_candidates_url

PACK = Path(__file__).resolve().parents[1] / "fixtures" / "dof_sales_bayside"
MANIFEST = json.loads((PACK / "MANIFEST.json").read_text(encoding="utf-8"))
ENTRIES = {entry["file"]: entry for entry in MANIFEST["files"]}
NOT_RECORDINGS = {"MANIFEST.json", "README.md", ".gitattributes"}


def test_manifest_lists_exactly_the_recorded_files():
    on_disk = {p.name for p in PACK.iterdir()} - NOT_RECORDINGS
    assert on_disk == set(ENTRIES)
    assert len(MANIFEST["files"]) == len(ENTRIES)


def test_every_file_matches_its_recorded_sha256_and_bytes():
    for name, entry in ENTRIES.items():
        raw = (PACK / name).read_bytes()
        assert len(raw) == entry["bytes"], name
        assert hashlib.sha256(raw).hexdigest() == entry["sha256"], name


def test_connector_backed_urls_are_rebuilt_from_the_connector():
    assert (
        ENTRIES["dof_sales_w2pb-icbu_bbl_4073340070.json"]["url"]
        == build_by_bbl_url("4073340070", row_limit=50)
    )
    assert (
        ENTRIES["dof_sales_w2pb-icbu_bayside_22_store_buildings.json"]["url"]
        == build_candidates_url("BAYSIDE", "22 STORE BUILDINGS", row_limit=12)
    )


def test_recorded_rows_are_well_formed_json_arrays():
    for name in ("dof_sales_w2pb-icbu_bbl_4073340070.json",
                 "dof_sales_w2pb-icbu_bayside_22_store_buildings.json"):
        rows = json.loads((PACK / name).read_bytes())
        assert isinstance(rows, list) and all(isinstance(r, dict) for r in rows)


def test_metadata_fixture_is_the_official_view_json():
    meta = json.loads((PACK / "dof_sales_api_views_w2pb-icbu.json").read_bytes())
    assert meta["id"] == "w2pb-icbu"
    assert meta["name"] == "NYC Citywide Annualized Calendar Sales Update"
    assert meta["attribution"] == "Department of Finance"
