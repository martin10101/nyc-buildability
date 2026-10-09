"""Integrity of the recorded neighbour lot 1 pack (queue item B-11 slice 2).

Re-hashes every byte-faithful official response in
``services/api/tests/fixtures/benchmark_block_7334_neighbor_lot_1/`` and checks each URL's
shape. No network: the pack is replayed only. See the pack README for why it exists (it
closes the gap the B-07 README named: a certificate query keyed on lot 1's BBL).
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

PACK = (Path(__file__).resolve().parents[1]
        / "fixtures" / "benchmark_block_7334_neighbor_lot_1")
MANIFEST_DOC = json.loads((PACK / "MANIFEST.json").read_text("utf-8"))
MANIFEST = {entry["file"]: entry for entry in MANIFEST_DOC["files"]}

NEIGHBOR_BBL = "4073340001"
NEIGHBOR_BIN = "4157401"


def test_pack_identity_fields() -> None:
    assert MANIFEST_DOC["neighbor_bbl"] == NEIGHBOR_BBL
    assert MANIFEST_DOC["subject_bbl"] == "4073340070"
    assert MANIFEST_DOC["neighbor_building_bin"] == NEIGHBOR_BIN


def test_every_file_byte_and_status_is_as_recorded() -> None:
    for name, entry in MANIFEST.items():
        body = (PACK / name).read_bytes()
        assert hashlib.sha256(body).hexdigest() == entry["sha256"], name
        assert (len(body), entry["http_status"]) == (entry["bytes"], 200), name


def test_directory_holds_exactly_the_manifest_files() -> None:
    assert sorted(p.name for p in PACK.iterdir()) == sorted(
        [*MANIFEST, "MANIFEST.json", "README.md", ".gitattributes"])


def test_urls_are_the_documented_shape() -> None:
    jobs = MANIFEST["dob_bis_jobs_ic3t-wcy2_bin_4157401.json"]
    assert jobs["url"].startswith(
        f"https://data.cityofnewyork.us/resource/ic3t-wcy2.json?bin__={NEIGHBOR_BIN}&%24select=")
    # The PII-excluding $select carries zoning-figure columns and no name column.
    assert "existing_zoning_sqft,proposed_zoning_sqft" in jobs["url"]
    for token in ("owner", "applicant", "first_name", "last_name"):
        assert token not in jobs["url"]
    # The two certificate datasets are queried keyed on the neighbour's BBL (the B-07 gap).
    for dataset in ("bs8b-p36w", "pkdm-hqz6"):
        file = next(n for n, e in MANIFEST.items() if e["dataset_id"] == dataset)
        assert MANIFEST[file]["url"] == (
            f"https://data.cityofnewyork.us/resource/{dataset}.json?bbl={NEIGHBOR_BBL}")


def test_certificate_queries_recorded_no_rows() -> None:
    for dataset in ("bs8b-p36w", "pkdm-hqz6"):
        file = next(n for n, e in MANIFEST.items() if e["dataset_id"] == dataset)
        rows = json.loads((PACK / file).read_bytes().decode("utf-8"))
        assert rows == [], file


def test_job_rows_carry_no_name_column() -> None:
    rows = json.loads(
        (PACK / "dob_bis_jobs_ic3t-wcy2_bin_4157401.json").read_bytes().decode("utf-8"))
    assert rows, "the neighbour's building filings must be recorded"
    columns = {key for row in rows for key in row}
    for token in ("owner", "applicant", "first_name", "last_name", "name_of"):
        assert not [c for c in columns if token in c.lower()], token
