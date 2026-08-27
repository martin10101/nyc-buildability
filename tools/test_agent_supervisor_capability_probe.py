"""M0-T086 (D-024 Phase A): capability-probe and fixture-pack tests.

Deterministic; no network. Live CLI re-probes are feature-detected and cleanly
skipped when the executable is absent (D-024 16.1: an absent tool skips its
path; the suite must not install anything as a side effect).

Supervisor-freeze qualifying evidence: D-024-R099; re-baselined for the M0-T103
official-updater upgrade under D-024-R148/R149/R168 (amendment 3): the live drift
tooth now points at the post-update fixture (installed 2.1.246); the 2026-08-25 and
2026-08-26 pre-update fixtures remain the frozen 2.1.220 historical record.
Re-baselined again for M0-T104 (unit C; D-024-R153/R172): the machine auto-updated
2.1.246 -> 2.1.247 during the seq-12 R162 discharge, so both live drift teeth now
point at the 2026-08-27 m0t104 fixture (installed 2.1.247); the 2.1.220 and 2.1.246
fixtures stay frozen as the historical upgrade pair.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from tools.agent_supervisor import capability_probe as cp

FIXTURES = Path(__file__).parent / "agent_supervisor" / "fixtures"
# Pre-update historical record (claude 2.1.220): shape/masking invariants only.
LIVE_FIXTURE = FIXTURES / "capability_probe_live_2026-08-25.json"
# M0-T103 post-update record (claude 2.1.246): frozen historical upgrade pair.
POST_FIXTURE = FIXTURES / "capability_probe_live_2026-08-26_m0t103_post_update.json"
# Current record (claude 2.1.247, M0-T104): the live drift teeth target THIS.
CURRENT_FIXTURE = FIXTURES / "capability_probe_live_2026-08-27_m0t104.json"
MATRIX = FIXTURES / "capability_matrix_v1.json"


# ---------- probe design invariants ----------

def test_probe_allowlist_is_read_only():
    """Every allowlisted probe command is non-mutating by construction."""
    for probe_id, argv in cp.PROBE_COMMANDS:
        for token in argv[1:]:
            for bad in cp.MUTATING_TOKENS:
                assert token.lstrip("-") != bad, (
                    f"probe {probe_id} carries mutating token {token!r}")
        assert argv[-1] in ("--version", "--help"), (
            f"probe {probe_id} must end in --version/--help, got {argv[-1]!r}")


def test_absent_binary_classifies_absent_not_success():
    rec = cp._run(["definitely-not-installed-binary-xyz", "--version"])
    assert rec["status"] == "absent"
    assert "exit_code" not in rec


def test_classify_flags_deterministic_and_vocabulary():
    sample = "usage: tool [--alpha] [--beta VALUE]\n  --gamma  does things\n"
    out1 = cp.classify_flags(sample, ["--alpha", "--gamma", "--missing"])
    out2 = cp.classify_flags(sample, ["--missing", "--gamma", "--alpha"])
    assert out1 == out2 == {
        "--alpha": "supported",
        "--gamma": "supported",
        "--missing": "not-detected-in-help",
    }


def test_classify_flags_empty_help_never_supports():
    out = cp.classify_flags("", ["--x"])
    assert out == {"--x": "not-detected-in-help"}


# ---------- committed live-fixture invariants ----------

@pytest.fixture(scope="module")
def live() -> dict:
    return json.loads(LIVE_FIXTURE.read_text(encoding="utf-8"))


def test_live_fixture_shape(live):
    body = live["body"]
    assert body["schema"] == "capability_probe/v1"
    assert body["directive"] == "D-024"
    assert set(body["probes"]) == {pid for pid, _ in cp.PROBE_COMMANDS}
    for rec in body["probes"].values():
        assert rec["status"] in {"supported", "absent", "unknown"}


def test_live_fixture_body_has_no_volatile_data(live):
    """The deterministic body carries no timestamps or user-specific paths."""
    text = json.dumps(live["body"])
    assert "generated_at" not in text
    assert "Users" not in text and "home/" not in text
    # varying metadata lives only under probe_meta
    assert "generated_at" in live["probe_meta"]


def test_live_fixture_interactive_facts_stay_unknown(live):
    ioc = live["body"]["interactive_only_capabilities"]
    for key, val in ioc.items():
        if key == "note":
            continue
        assert val == "unknown", (
            f"{key} must be 'unknown' in the probe body; live behavior is a "
            f"Phase B/F harness deliverable, never guessed")


def test_live_fixture_records_gate0_launch_flags(live):
    """The Gate-0/clean-launch design flags were positively detected."""
    flags = live["body"]["claude_flags"]
    assert flags["--strict-mcp-config"] == "supported"
    assert flags["--mcp-config"] == "supported"


def test_live_fixture_records_codex_transport_surface(live):
    flags = live["body"]["codex_flags"]
    for tok in ("exec", "--sandbox", "--json", "--output-schema", "resume"):
        assert flags[tok] == "supported", f"codex transport token {tok} missing"


# ---------- capability matrix invariants ----------

@pytest.fixture(scope="module")
def matrix() -> dict:
    return json.loads(MATRIX.read_text(encoding="utf-8"))


def test_matrix_vocabulary_enforced(matrix):
    statuses = set(matrix["status_vocabulary"])
    confidences = set(matrix["confidence_vocabulary"])
    assert len(matrix["capabilities"]) >= 15
    for cap in matrix["capabilities"]:
        assert cap["status"] in statuses, cap["id"]
        assert cap["confidence"] in confidences, cap["id"]
        assert cap.get("evidence"), f"{cap['id']} has no evidence"


def test_matrix_measured_claims_match_live_fixture(matrix, live):
    """Every measured-live claim about a probed flag matches the live record."""
    claude_flags = live["body"]["claude_flags"]
    codex_flags = live["body"]["codex_flags"]
    checks = {
        "claude.strict_mcp_config_flag": claude_flags["--strict-mcp-config"],
        "claude.mcp_config_flag": claude_flags["--mcp-config"],
        "claude.worktree_flag": claude_flags["--worktree"],
        "codex.exec_noninteractive": codex_flags["exec"],
        "codex.sandbox_flag": codex_flags["--sandbox"],
        "codex.json_event_output": codex_flags["--json"],
        "codex.output_schema": codex_flags["--output-schema"],
        "codex.resume_thread": codex_flags["resume"],
    }
    by_id = {c["id"]: c for c in matrix["capabilities"]}
    for cap_id, live_status in checks.items():
        assert by_id[cap_id]["status"] == "supported", cap_id
        assert live_status == "supported", (
            f"matrix claims {cap_id} supported but live fixture says "
            f"{live_status}")


def test_matrix_sdk_stays_absent_by_policy(matrix):
    sdk = [c for c in matrix["capabilities"] if c["id"] == "agent_sdk.python"]
    assert sdk and sdk[0]["status"] == "absent-by-policy"


def test_matrix_unknowns_are_explicit_not_missing(matrix):
    unknowns = [c for c in matrix["capabilities"] if c["status"] == "unknown"]
    assert unknowns, "live-harness-dependent facts must be recorded as unknown"
    for cap in unknowns:
        assert "note" in cap


# ---------- live re-probe (feature-detected; skips cleanly when absent) ----------

@pytest.fixture(scope="module")
def post() -> dict:
    return json.loads(POST_FIXTURE.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def current() -> dict:
    return json.loads(CURRENT_FIXTURE.read_text(encoding="utf-8"))


@pytest.mark.skipif(shutil.which("claude") is None,
                    reason="claude CLI not installed on this runner")
def test_live_reprobe_claude_version_matches_fixture(current):
    rec = cp._run(["claude", "--version"])
    assert rec["status"] == "supported"
    assert rec["first_line"] == current["body"]["probes"]["claude_version"]["first_line"], (
        "installed claude version drifted from the committed current fixture; re-run "
        "python -m tools.agent_supervisor.capability_probe and re-review")


def test_upgrade_pair_records_expected_versions(live, post):
    """M0-T103 dual-version invariant (D-024-R167/R168): the pre-update fixture
    freezes 2.1.220 and the post-update fixture freezes 2.1.246; codex is
    unchanged across the upgrade. RED if either side is regenerated wrongly."""
    assert live["body"]["probes"]["claude_version"]["first_line"] == "2.1.220 (Claude Code)"
    assert post["body"]["probes"]["claude_version"]["first_line"] == "2.1.246 (Claude Code)"
    assert (live["body"]["probes"]["codex_version"]["first_line"]
            == post["body"]["probes"]["codex_version"]["first_line"]
            == "codex-cli 0.146.0")


def test_post_update_fixture_masked_and_shaped(post):
    """The post-update fixture obeys the same masking/shape contract as the
    pre-update record (no volatile identity; [HOME]-masked binary paths).
    General leak guards (G3 M0-T103 ADVISORY-2): no drive-rooted user path or
    Users-directory fragment anywhere, not just the current account name."""
    whole = json.dumps(post, sort_keys=True)
    for leak in (":\\\\Users\\\\", ":/Users/", "\\\\Users\\\\MLFLL", "MLFLL"):
        assert leak not in whole, f"unmasked path fragment {leak!r} in fixture"
    assert "claude_version" in post["body"]["probes"]
    binaries = post["probe_meta"].get("claude_binaries", [])
    assert binaries, "probe_meta.claude_binaries missing"
    for rec in binaries:
        assert rec.startswith("[HOME]"), rec


@pytest.mark.skipif(shutil.which("codex") is None,
                    reason="codex CLI not installed on this runner")
def test_live_reprobe_codex_version_matches_fixture(current):
    rec = cp._run(["codex", "--version"])
    assert rec["status"] == "supported"
    assert rec["first_line"] == current["body"]["probes"]["codex_version"]["first_line"]


def test_current_fixture_records_2_1_247_masked_and_shaped(current, post):
    """M0-T104 re-baseline invariant (D-024-R153/R172): the current fixture
    freezes the 2.1.247 auto-update observed during the seq-12 R162 discharge;
    codex is unchanged across it. Same masking/shape contract as its
    predecessors; filename carries the consuming task id (G3 ADV-1)."""
    assert (current["body"]["probes"]["claude_version"]["first_line"]
            == "2.1.247 (Claude Code)")
    assert (current["body"]["probes"]["codex_version"]["first_line"]
            == post["body"]["probes"]["codex_version"]["first_line"]
            == "codex-cli 0.146.0")
    assert "m0t104" in CURRENT_FIXTURE.name
    whole = json.dumps(current, sort_keys=True)
    for leak in (":\\\\Users\\\\", ":/Users/", "\\\\Users\\\\MLFLL", "MLFLL"):
        assert leak not in whole, f"unmasked path fragment {leak!r} in fixture"
    binaries = current["probe_meta"].get("claude_binaries", [])
    assert binaries, "probe_meta.claude_binaries missing"
    for rec in binaries:
        assert rec.startswith("[HOME]"), rec


def test_build_record_is_deterministic_when_tools_absent_or_present():
    """Two consecutive builds produce identical deterministic bodies."""
    a = cp.build_record()["body"]
    b = cp.build_record()["body"]
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)
