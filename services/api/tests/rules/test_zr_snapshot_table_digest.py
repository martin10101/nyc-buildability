"""DB-276 (M3-T013): additive ``table_digest_sha256`` tamper-evidence for the ZR
snapshot structured table payloads.

The governing FAR/height/use tables live in a sibling ``table`` / ``tables`` /
``table.row_groups`` payload that ``content_digest_sha256`` (which signs only
``verbatim_excerpt`` - a ``[table - see structured table field]`` placeholder)
does NOT cover. So a silent edit to a table value moves no existing digest. This
suite proves the additive ``table_digest_sha256`` closes that gap:

* every table-bearing snapshot carries a digest that is the sha256 of the
  canonical JSON of its parsed payload, and the digest-bearing set is derived by
  GLOB (never a hard-coded count) so a future table-bearing snapshot - or the
  once-missed ``zr-22-131`` - cannot slip through unsigned (S1);
* ``content_digest_sha256`` is unchanged and still verified (the field is
  additive) (S2);
* a flipped table value fails load, and the pre-change excerpt digest is BLIND
  to that flip, so the new check is the only load-time guard that catches it -
  the mutation + revert proof (S3);
* the loader fails closed on a payload-without-digest, a digest-without-payload,
  and a snapshot carrying both ``table`` and ``tables`` (S4);
* a non-table snapshot still loads with no digest required (S5);
* the digest is over the PARSED payload, so re-indenting/re-ordering the file
  never breaks it (RISK B3).
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from app.rules.snapshots import SnapshotError, load_snapshot_file

# test file: <root>/services/api/tests/rules/test_zr_snapshot_table_digest.py
_REPO_ROOT = Path(__file__).resolve().parents[4]
_DOCS_SNAPSHOT_DIR = _REPO_ROOT / "docs" / "research" / "zr-snapshots" / "v1"
_GLOB = "*.snapshot.json"

# The count today (18 table.rows + 18 tables + 1 table.row_groups). This is a
# tripwire, NOT the source of truth: the derived equality in
# ``test_digest_bearing_set_equals_glob_set`` is the real guard. Bump this
# deliberately only when a table-bearing section is genuinely added or removed.
_EXPECTED_TABLE_BEARING_COUNT = 37


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _canonical_table_json(payload: object) -> str:
    """The canonical JSON the digest signs - computed here INDEPENDENTLY of the
    loader so the digest assertions are non-tautological."""
    return json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def _payload_of(raw: dict) -> object | None:
    if "table" in raw:
        return raw["table"]
    if "tables" in raw:
        return raw["tables"]
    return None


def _table_bearing_files() -> list[Path]:
    """Every canonical snapshot carrying a ``table`` or ``tables`` key, derived by
    glob - never hard-coded - so the set is self-maintaining (S1)."""
    out: list[Path] = []
    for p in sorted(_DOCS_SNAPSHOT_DIR.glob(_GLOB)):
        raw = json.loads(p.read_text(encoding="utf-8"))
        if "table" in raw or "tables" in raw:
            out.append(p)
    return out


def _minimal_table_snapshot() -> dict:
    """A smallest valid ``table.rows`` snapshot with correct excerpt + table digests."""
    excerpt = "R6B standard FAR 2.00; qualifying 2.40. [table - see structured table field]"
    table = {
        "caption": "FAR",
        "columns": ["district", "standard", "qualifying"],
        "rows": [{"district": "R6B", "standard": "2.00", "qualifying": "2.40"}],
    }
    return {
        "snapshot_id": "zr-test-tmp",
        "section_number": "23-22",
        "verbatim_excerpt": excerpt,
        "table": table,
        "table_digest_sha256": _sha256(_canonical_table_json(table)),
        "content_digest_sha256": _sha256(excerpt),
        "source": {"request_url": "https://example.test", "retrieved_at": "2026-10-15"},
        "extraction_status": "extracted_draft",
    }


def _write(tmp_path: Path, raw: dict, name: str = "zr-test-tmp.snapshot.json", **dump) -> Path:
    p = tmp_path / name
    opts = {"indent": 2}
    opts.update(dump)
    p.write_text(json.dumps(raw, **opts), encoding="utf-8")
    return p


# --------------------------------------------------------------------------- S1
def test_every_table_bearing_snapshot_carries_a_correct_table_digest() -> None:
    files = _table_bearing_files()
    assert files, f"no table-bearing snapshots under {_DOCS_SNAPSHOT_DIR}"
    for p in files:
        raw = json.loads(p.read_text(encoding="utf-8"))
        expected = _sha256(_canonical_table_json(_payload_of(raw)))
        assert raw.get("table_digest_sha256") == expected, (
            f"{p.name}: table_digest_sha256 is not sha256 of the canonical table JSON"
        )
        # The loader re-verifies the digest on read; it must load clean.
        snap = load_snapshot_file(p)
        assert snap.snapshot_id


def test_digest_bearing_set_equals_glob_set() -> None:
    """The set of snapshots carrying ``table_digest_sha256`` == the set carrying a
    table payload. Catches the 37-vs-36 gap (``zr-22-131`` must not be missed) and
    any future table-bearing snapshot added without a digest."""
    glob_set = {p.name for p in _table_bearing_files()}
    digest_set = {
        p.name
        for p in sorted(_DOCS_SNAPSHOT_DIR.glob(_GLOB))
        if "table_digest_sha256" in json.loads(p.read_text(encoding="utf-8"))
    }
    assert digest_set == glob_set
    assert "zr-22-131.snapshot.json" in glob_set, "the once-missed tables snapshot must be signed"
    assert len(glob_set) == _EXPECTED_TABLE_BEARING_COUNT


# --------------------------------------------------------------------------- S2
def test_content_digest_still_verified_and_unchanged() -> None:
    for p in _table_bearing_files():
        raw = json.loads(p.read_text(encoding="utf-8"))
        assert raw["content_digest_sha256"] == _sha256(raw["verbatim_excerpt"])
        snap = load_snapshot_file(p)
        assert snap.content_digest_sha256 == _sha256(raw["verbatim_excerpt"])


# --------------------------------------------------------------------------- S3
def test_flipped_table_value_fails_load(tmp_path: Path) -> None:
    raw = _minimal_table_snapshot()
    load_snapshot_file(_write(tmp_path, raw))  # baseline: loads clean
    raw["table"]["rows"][0]["standard"] = "9.99"  # flip, leave the digest stale
    p = _write(tmp_path, raw)
    with pytest.raises(SnapshotError, match="table_digest_sha256 mismatch"):
        load_snapshot_file(p)


def test_pre_change_excerpt_digest_is_blind_to_the_table_edit(tmp_path: Path) -> None:
    """Revert proof: with only the OLD excerpt-digest check (pre-M3-T013) the
    flipped file would still load - a table-value edit leaves
    ``content_digest_sha256`` intact. So the new ``table_digest_sha256`` check is
    the sole load-time guard that catches the edit."""
    raw = _minimal_table_snapshot()
    raw["table"]["rows"][0]["standard"] = "9.99"  # flipped value, stale table digest
    p = _write(tmp_path, raw)
    with pytest.raises(SnapshotError):
        load_snapshot_file(p)  # the new check rejects it
    reread = json.loads(p.read_text(encoding="utf-8"))
    # the pre-change tamper-evidence is satisfied -> the old loader would accept it
    assert reread["content_digest_sha256"] == _sha256(reread["verbatim_excerpt"])


def test_tables_list_shape_round_trips_and_is_signed(tmp_path: Path) -> None:
    excerpt = "Two tables captured. [table - see structured table field]"
    tables = [
        {"caption": "T1", "rows": [{"use": "A", "allowed": "yes"}]},
        {"caption": "T2", "rows": [{"use": "B", "allowed": "no"}]},
    ]
    raw = {
        "snapshot_id": "zr-test-tables",
        "verbatim_excerpt": excerpt,
        "tables": tables,
        "table_digest_sha256": _sha256(_canonical_table_json(tables)),
        "content_digest_sha256": _sha256(excerpt),
        "source": {},
        "extraction_status": "extracted_draft",
    }
    load_snapshot_file(_write(tmp_path, raw, name="zr-test-tables.snapshot.json"))
    raw["tables"][1]["rows"][0]["allowed"] = "TAMPERED"
    p = _write(tmp_path, raw, name="zr-test-tables.snapshot.json")
    with pytest.raises(SnapshotError, match="table_digest_sha256 mismatch"):
        load_snapshot_file(p)


def test_row_groups_shape_round_trips_and_is_signed(tmp_path: Path) -> None:
    excerpt = "Front setback table. [table - see structured table field]"
    table = {"caption": "setback", "row_groups": [{"group": "R6", "rows": [{"a": "1"}]}]}
    raw = {
        "snapshot_id": "zr-test-rg",
        "verbatim_excerpt": excerpt,
        "table": table,
        "table_digest_sha256": _sha256(_canonical_table_json(table)),
        "content_digest_sha256": _sha256(excerpt),
        "source": {},
        "extraction_status": "extracted_draft",
    }
    load_snapshot_file(_write(tmp_path, raw, name="zr-test-rg.snapshot.json"))
    raw["table"]["row_groups"][0]["rows"][0]["a"] = "999"
    p = _write(tmp_path, raw, name="zr-test-rg.snapshot.json")
    with pytest.raises(SnapshotError, match="table_digest_sha256 mismatch"):
        load_snapshot_file(p)


# --------------------------------------------------------------------------- S4
def test_table_payload_without_digest_fails(tmp_path: Path) -> None:
    raw = _minimal_table_snapshot()
    del raw["table_digest_sha256"]
    p = _write(tmp_path, raw)
    with pytest.raises(SnapshotError, match="no .*table_digest_sha256|table payload present"):
        load_snapshot_file(p)


def test_table_digest_without_payload_fails(tmp_path: Path) -> None:
    raw = _minimal_table_snapshot()
    del raw["table"]  # keep the stale digest, drop the payload
    p = _write(tmp_path, raw)
    with pytest.raises(SnapshotError, match="no table payload"):
        load_snapshot_file(p)


def test_both_table_and_tables_fails(tmp_path: Path) -> None:
    raw = _minimal_table_snapshot()
    raw["tables"] = [raw["table"]]  # both keys present -> malformed
    p = _write(tmp_path, raw)
    with pytest.raises(SnapshotError, match="both 'table' and 'tables'"):
        load_snapshot_file(p)


def test_table_payload_of_unexpected_shape_fails(tmp_path: Path) -> None:
    raw = _minimal_table_snapshot()
    raw["table"] = {"caption": "no rows and no row_groups"}  # neither rows nor row_groups
    p = _write(tmp_path, raw)
    with pytest.raises(SnapshotError, match="'table' payload is not an object"):
        load_snapshot_file(p)


# --------------------------------------------------------------------------- S5
def test_non_table_snapshot_loads_without_a_digest(tmp_path: Path) -> None:
    excerpt = "Plain section text with no structured table payload at all."
    raw = {
        "snapshot_id": "zr-test-plain",
        "verbatim_excerpt": excerpt,
        "content_digest_sha256": _sha256(excerpt),
        "source": {},
        "extraction_status": "extracted_draft",
    }
    p = _write(tmp_path, raw, name="zr-test-plain.snapshot.json")
    snap = load_snapshot_file(p)
    assert snap.snapshot_id == "zr-test-plain"


# -------------------------------------------------------------------- RISK B3
def test_digest_is_over_parsed_payload_not_file_bytes(tmp_path: Path) -> None:
    """Re-indenting and re-ordering keys never breaks the digest; it is computed
    over the canonical JSON of the PARSED payload, so only a value edit moves it."""
    raw = _minimal_table_snapshot()
    compact = _write(tmp_path, raw, name="a.snapshot.json", indent=None, separators=(",", ":"))
    load_snapshot_file(compact)
    reordered = dict(reversed(list(raw.items())))
    pretty = _write(tmp_path, reordered, name="b.snapshot.json", indent=4, sort_keys=True)
    load_snapshot_file(pretty)
