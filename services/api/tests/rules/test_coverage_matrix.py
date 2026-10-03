"""Acceptance tests for the A-01 rule-coverage matrix (plan M1-03, D-090).

These are deterministic: they read the committed matrix JSON, the committed
rulesets, the committed ZR FAR snapshots and the committed rendered Markdown.
No AI, no network, no rule math. They prove the matrix is internally consistent,
that every referenced rule id and test path really exists, that the district
list comes from (and equals) the captured official enumeration, and that the
committed Markdown is exactly what the renderer produces from the JSON.
"""
from __future__ import annotations

import importlib.util
import json
import pathlib

import pytest

TEST_FILE = pathlib.Path(__file__).resolve()
REPO_ROOT = TEST_FILE.parents[4]
API_DIR = TEST_FILE.parents[2]
COVERAGE_DIR = API_DIR / "app" / "rules" / "coverage"
MATRIX_JSON = COVERAGE_DIR / "coverage_matrix.json"
MATRIX_MD = COVERAGE_DIR / "COVERAGE_MATRIX.md"
RENDERER_PY = COVERAGE_DIR / "render_coverage_matrix.py"
RULESET_DIR = API_DIR / "app" / "rules" / "rulesets"
SNAPSHOT_DIR = API_DIR / "app" / "_zr_snapshots" / "v1"

VALID_STATUSES = {
    "implemented_draft",
    "not_implemented",
    "not_applicable",
    "needs_reviewer",
}
VALID_STREET_WIDTH = {
    "dcm_mapped_width",
    "unknown_then_both_results",
    "not_needed",
    None,
}
CELL_KEYS = {
    "status",
    "inputs",
    "rule_ids",
    "tests",
    "zr_sections",
    "street_width_source",
    "notes",
}


def _load_matrix() -> dict:
    return json.loads(MATRIX_JSON.read_text())


def _ruleset_ids() -> set[str]:
    ids = set()
    for path in RULESET_DIR.glob("*.rule.json"):
        ids.add(json.loads(path.read_text())["rule_id"])
    return ids


def _load_renderer():
    spec = importlib.util.spec_from_file_location("a01_render_coverage_matrix", RENDERER_PY)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _all_cells(matrix: dict):
    for row in matrix["districts"]:
        for col_key, cell in row["columns"].items():
            yield row["district"], col_key, cell


MATRIX = _load_matrix()
RULE_IDS = _ruleset_ids()


# --- structure: every row has every column -----------------------------------
def test_every_row_has_every_column():
    expected = list(MATRIX["column_order"])
    assert len(expected) == len(MATRIX["output_columns"]) + len(MATRIX["add_on_columns"])
    assert len(MATRIX["districts"]) > 0
    for row in MATRIX["districts"]:
        assert list(row["columns"].keys()) == expected, row["district"]


# --- structure: every cell has the required fields with valid values ---------
def test_every_cell_has_status_inputs_tests():
    for district, col_key, cell in _all_cells(MATRIX):
        where = f"{district}/{col_key}"
        assert set(cell.keys()) == CELL_KEYS, where
        assert cell["status"] in VALID_STATUSES, where
        assert isinstance(cell["inputs"], list), where
        assert isinstance(cell["tests"], list), where
        assert isinstance(cell["rule_ids"], list), where
        assert isinstance(cell["zr_sections"], list), where
        assert cell["street_width_source"] in VALID_STREET_WIDTH, where
        assert isinstance(cell["notes"], str) and cell["notes"].strip(), where


# --- provenance: every rule id resolves to an existing ruleset rule ----------
def test_every_rule_id_resolves():
    assert RULE_IDS, "no rulesets loaded"
    for district, col_key, cell in _all_cells(MATRIX):
        for rid in cell["rule_ids"]:
            assert rid in RULE_IDS, f"{district}/{col_key}: unknown rule id {rid!r}"


# --- provenance: every cited test path exists --------------------------------
def test_every_test_path_exists():
    for district, col_key, cell in _all_cells(MATRIX):
        for test_path in cell["tests"]:
            resolved = REPO_ROOT / test_path
            assert resolved.is_file(), f"{district}/{col_key}: missing test {test_path}"


# --- positive: implemented_draft cells carry >=1 rule id and >=1 test ---------
def test_implemented_draft_cells_have_rule_and_test():
    implemented = 0
    for district, col_key, cell in _all_cells(MATRIX):
        if cell["status"] != "implemented_draft":
            continue
        implemented += 1
        assert cell["rule_ids"], f"{district}/{col_key}: implemented_draft with no rule id"
        assert cell["tests"], f"{district}/{col_key}: implemented_draft with no test"
    assert implemented > 0, "expected at least one implemented_draft cell"


# --- positive spot check: a known implemented FAR cell -----------------------
def test_r6b_far_is_implemented_draft():
    cell = _cell_for("R6B", "far")
    assert cell["status"] == "implemented_draft"
    assert "r6-r12-residential-far" in cell["rule_ids"]
    assert any("r1_r12_residential_far" in t for t in cell["tests"])


# --- negative: an unbuilt output is not_implemented with empty refs ----------
def test_r10_heights_not_implemented():
    cell = _cell_for("R10", "heights")
    assert cell["status"] == "not_implemented"
    assert cell["rule_ids"] == []
    assert cell["tests"] == []
    assert cell["street_width_source"] is None


# --- exception: the one needs_reviewer cell is justified ---------------------
def test_needs_reviewer_cells_are_justified():
    found = [
        (d, c)
        for d, c, cell in _all_cells(MATRIX)
        if cell["status"] == "needs_reviewer"
    ]
    assert found, "expected at least one needs_reviewer cell"
    for d, c in found:
        cell = _cell_for(d, c)
        assert "review" in cell["notes"].lower(), f"{d}/{c}: needs_reviewer without reason"


# --- exception: not_applicable cells cite a basis ----------------------------
def test_not_applicable_cells_cite_a_basis():
    found = [
        (d, c)
        for d, c, cell in _all_cells(MATRIX)
        if cell["status"] == "not_applicable"
    ]
    assert found, "expected at least one not_applicable cell"
    for d, c in found:
        cell = _cell_for(d, c)
        assert cell["rule_ids"] == [] and cell["tests"] == [], f"{d}/{c}"
        assert "§" in cell["notes"] or "plan" in cell["notes"].lower(), f"{d}/{c}"


# --- street-width source only where a rule exists ----------------------------
def test_street_width_source_requires_a_rule():
    for district, col_key, cell in _all_cells(MATRIX):
        if cell["street_width_source"] in {"dcm_mapped_width", "unknown_then_both_results"}:
            assert cell["rule_ids"], f"{district}/{col_key}: width source without a rule"
        if not cell["rule_ids"]:
            assert cell["street_width_source"] is None, f"{district}/{col_key}"


# --- boundary + provenance: district list equals the captured enumeration ----
def test_district_list_equals_recorded_source_enumeration():
    matrix_districts = [row["district"] for row in MATRIX["districts"]]
    assert len(matrix_districts) == len(set(matrix_districts)), "duplicate district rows"

    recorded = set()
    for source in MATRIX["list_source"]["sources"]:
        recorded.update(source["districts"])
    assert set(matrix_districts) == recorded
    assert MATRIX["list_source"]["total_district_count"] == len(matrix_districts)


def test_district_list_matches_live_far_snapshots():
    """Tie the enumeration to the actual captured ZR FAR snapshot bytes."""
    from_snapshots: set[str] = set()
    digests: dict[str, str] = {}
    for source in MATRIX["list_source"]["sources"]:
        snap = json.loads((SNAPSHOT_DIR / f"{source['snapshot_id']}.snapshot.json").read_text())
        for snap_row in snap["table"]["rows"]:
            from_snapshots.update(snap_row["districts"])
        digests[source["snapshot_id"]] = snap["content_digest_sha256"]

    matrix_districts = {row["district"] for row in MATRIX["districts"]}
    assert matrix_districts == from_snapshots

    # effective-date / provenance integrity: recorded digests cannot drift from
    # the live snapshot bytes without this test going red.
    for source in MATRIX["list_source"]["sources"]:
        assert source["content_digest_sha256"] == digests[source["snapshot_id"]]


def test_each_district_records_its_source():
    valid_ids = {s["snapshot_id"] for s in MATRIX["list_source"]["sources"]}
    for row in MATRIX["districts"]:
        src = row["list_source"]
        assert src["snapshot_id"] in valid_ids, row["district"]
        assert (REPO_ROOT / src["snapshot_file"]).is_file(), row["district"]
        assert src["zr_section"], row["district"]


# --- rendered markdown is byte-identical to the committed file ----------------
def test_rendered_markdown_is_byte_identical():
    renderer = _load_renderer()
    produced = renderer.render_markdown(_load_matrix())
    committed = MATRIX_MD.read_text()
    assert produced == committed, (
        "COVERAGE_MATRIX.md is stale; re-run render_coverage_matrix.py"
    )


def test_renderer_is_deterministic():
    renderer = _load_renderer()
    first = renderer.render_markdown(_load_matrix())
    second = renderer.render_markdown(_load_matrix())
    assert first == second


def _cell_for(district: str, column: str) -> dict:
    for row in MATRIX["districts"]:
        if row["district"] == district:
            return row["columns"][column]
    pytest.fail(f"district {district} not in matrix")
    raise AssertionError  # unreachable
