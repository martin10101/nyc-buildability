"""M0-T087 (D-024 Phase A2): campaign-continuity record tests.

Deterministic; exercises the fail-closed validation, atomic write, exact-once
advance, staleness detection, and read-only status entry point.

Supervisor-freeze qualifying evidence: D-024-R099 (Phase A item 7).
"""
from __future__ import annotations


import pytest

from tools.agent_supervisor import campaign_continuity as cc

SHA_A = "a" * 40
SHA_B = "b" * 40


def good_record(**over) -> dict:
    data = {
        "schema": cc.SCHEMA,
        "campaign_id": "D-024-fable-codex-loop",
        "directive_id": "D-024",
        "state": "active",
        "control_branch": "control/D-024-fable-codex-loop",
        "ledger_lineage_base": "7649acfc95583287688a503fc5949cd04c9f6b60",
        "authority": "project-control/directives/D-024-fable-codex-loop/"
                     "source-001.md sha256 0611bb45...",
        "restrictions": ["never merge PR #241"],
        "next_action": {"task_id": "M0-T088",
                        "description": "claim and produce B1 telemetry core"},
        "frozen": {"head_sha": SHA_A, "recorded_at": "2026-08-25T00:00:00+00:00"},
        "sequence": 3,
        "updated_at": "2026-08-25T00:00:00+00:00",
    }
    data.update(over)
    return data


# ---------- validation (fail closed) ----------

def test_validate_good_record_roundtrip():
    rec = cc.validate(good_record())
    assert rec.campaign_id == "D-024-fable-codex-loop"
    assert rec.to_dict() == good_record()


@pytest.mark.parametrize("mutation", [
    {"schema": "campaign_continuity/v0"},
    {"state": "running"},                      # not in vocabulary
    {"sequence": -1},
    {"sequence": "3"},
    {"restrictions": "never merge"},           # not a list
    {"next_action": {"task_id": "", "description": "x"}},
    {"next_action": {"task_id": "M0-T088"}},   # missing description
    {"frozen": {"head_sha": "abc", "recorded_at": "t"}},   # not 40-hex
    {"frozen": {"head_sha": SHA_A.upper(), "recorded_at": "t"}},  # uppercase
    {"frozen": {"recorded_at": "t"}},
])
def test_validate_rejects_defects(mutation):
    with pytest.raises(cc.CampaignRecordError):
        cc.validate(good_record(**mutation))


@pytest.mark.parametrize("drop", list(cc.REQUIRED_FIELDS))
def test_validate_rejects_every_missing_field(drop):
    data = good_record()
    del data[drop]
    with pytest.raises(cc.CampaignRecordError):
        cc.validate(data)


def test_load_missing_and_malformed_fail_closed(tmp_path):
    with pytest.raises(cc.CampaignRecordError):
        cc.load(tmp_path / "absent.json")
    bad = tmp_path / "bad.json"
    bad.write_text("{not json", encoding="utf-8")
    with pytest.raises(cc.CampaignRecordError):
        cc.load(bad)
    notdict = tmp_path / "list.json"
    notdict.write_text("[1,2]", encoding="utf-8")
    with pytest.raises(cc.CampaignRecordError):
        cc.load(notdict)


# ---------- atomic write ----------

def test_atomic_write_lf_and_roundtrip(tmp_path):
    path = tmp_path / "c.json"
    rec = cc.validate(good_record())
    cc.atomic_write(path, rec)
    raw = path.read_bytes()
    assert b"\r" not in raw
    assert cc.load(path).to_dict() == rec.to_dict()
    assert not path.with_suffix(".json.tmp").exists()


def test_atomic_write_refuses_invalid_record(tmp_path):
    rec = cc.validate(good_record())
    rec.state = "exploded"
    with pytest.raises(cc.CampaignRecordError):
        cc.atomic_write(tmp_path / "c.json", rec)
    assert not (tmp_path / "c.json").exists()


# ---------- exact-once advance ----------

def test_advance_success_increments_sequence(tmp_path):
    path = tmp_path / "c.json"
    cc.atomic_write(path, cc.validate(good_record(sequence=3)))
    new = cc.advance(path, 3, next_action={"task_id": "M0-T089",
                                           "description": "B2 telemetry"},
                     head_sha=SHA_B)
    assert new.sequence == 4
    assert new.frozen["head_sha"] == SHA_B
    assert cc.load(path).sequence == 4


def test_advance_stale_sequence_refused(tmp_path):
    path = tmp_path / "c.json"
    cc.atomic_write(path, cc.validate(good_record(sequence=3)))
    with pytest.raises(cc.SequenceConflict):
        cc.advance(path, 2, next_action={"task_id": "X", "description": "y"},
                   head_sha=SHA_B)
    assert cc.load(path).sequence == 3  # untouched


def test_two_racers_exactly_one_wins(tmp_path):
    """Both read sequence 3; the first advance wins; the second is refused."""
    path = tmp_path / "c.json"
    cc.atomic_write(path, cc.validate(good_record(sequence=3)))
    seen = cc.load(path).sequence
    cc.advance(path, seen, next_action={"task_id": "A", "description": "1"},
               head_sha=SHA_B)
    with pytest.raises(cc.SequenceConflict):
        cc.advance(path, seen, next_action={"task_id": "B", "description": "2"},
                   head_sha=SHA_B)
    final = cc.load(path)
    assert final.sequence == 4 and final.next_action["task_id"] == "A"


def test_advance_preserves_restrictions_unless_replaced(tmp_path):
    path = tmp_path / "c.json"
    cc.atomic_write(path, cc.validate(good_record()))
    new = cc.advance(path, 3, next_action={"task_id": "X", "description": "y"},
                     head_sha=SHA_B)
    assert new.restrictions == ["never merge PR #241"]


# ---------- staleness + orientation ----------

def test_staleness_detection():
    rec = cc.validate(good_record())
    assert cc.staleness(rec, SHA_A) is None
    warning = cc.staleness(rec, SHA_B)
    assert warning and "reconcile" in warning


def test_orientation_summary_contents():
    text = cc.orientation_summary(cc.validate(good_record()))
    assert "D-024-fable-codex-loop" in text
    assert "NEXT: [M0-T088]" in text
    assert "never merge PR #241" in text
    assert "authority:" in text


# ---------- read-only status entry point ----------

def test_main_status_no_record_fails_closed(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    assert cc.main(["--status"]) == 1
    err = capsys.readouterr().err
    assert "fail closed" in err


def test_main_status_valid_record(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    path = tmp_path / "project-control" / "campaigns" / "D-024.json"
    path.parent.mkdir(parents=True)
    cc.atomic_write(path, cc.validate(good_record()))
    assert cc.main(["--status"]) == 0
    out = capsys.readouterr().out
    assert "NEXT: [M0-T088]" in out


def test_main_status_invalid_record_exit_1(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    path = tmp_path / "project-control" / "campaigns" / "D-024.json"
    path.parent.mkdir(parents=True)
    path.write_text("{}", encoding="utf-8")
    assert cc.main(["--status"]) == 1
    assert "INVALID" in capsys.readouterr().err
