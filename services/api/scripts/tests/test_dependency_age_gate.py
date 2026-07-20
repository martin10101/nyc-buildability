"""Deterministic, offline unit tests for the dependency release-age gate
(task M0-T020, scenarios TP-S9 / TP-S8 boundary + fail-closed semantics).

Every test injects a fixed UTC ``now`` and a synthetic PyPI-metadata provider,
so nothing here touches the network. The live behaviour (real PyPI ``Date``
header + real per-version metadata) is exercised by the CI age-gate job over the
two real locks; these tests pin the LOGIC: the 604800/604799 boundary, the
newest-admitted-artifact selection, and that every fail-closed branch FAILS
(never skips or passes).
"""

from __future__ import annotations

import datetime as _dt
import importlib.util
import sys
from pathlib import Path

import pytest

# Import the sibling module by path (scripts/ is not a package).
_MODULE_PATH = Path(__file__).resolve().parents[1] / "dependency_age_gate.py"
_spec = importlib.util.spec_from_file_location("dependency_age_gate", _MODULE_PATH)
assert _spec and _spec.loader
age_gate = importlib.util.module_from_spec(_spec)
sys.modules["dependency_age_gate"] = age_gate
_spec.loader.exec_module(age_gate)

PinnedPackage = age_gate.PinnedPackage
AgeGateError = age_gate.AgeGateError
MIN = age_gate.MIN_AGE_SECONDS  # 604800

NOW = _dt.datetime(2026, 7, 20, 12, 0, 0, tzinfo=_dt.UTC)
SHA_A = "a" * 64
SHA_B = "b" * 64
SHA_C = "c" * 64


def _artifact(sha: str, uploaded: _dt.datetime, yanked: bool = False) -> dict:
    return {
        "digests": {"sha256": sha},
        "upload_time_iso_8601": uploaded.isoformat().replace("+00:00", "Z"),
        "yanked": yanked,
    }


def _uploaded_seconds_ago(seconds: int) -> _dt.datetime:
    return NOW - _dt.timedelta(seconds=seconds)


# --------------------------------------------------------------------------- #
# Boundary: exactly 604800 s PASSES; 604799 s FAILS (TP-S9)
# --------------------------------------------------------------------------- #
def test_exactly_seven_days_passes():
    pkg = PinnedPackage("demo", "1.0.0", frozenset({SHA_A}))
    arts = [_artifact(SHA_A, _uploaded_seconds_ago(MIN))]  # 604800 s old
    result = age_gate.decide(pkg, arts, NOW)
    assert result.passed is True
    assert result.age_seconds == MIN
    assert result.reason == ""


def test_one_second_under_seven_days_fails():
    pkg = PinnedPackage("demo", "1.0.0", frozenset({SHA_A}))
    arts = [_artifact(SHA_A, _uploaded_seconds_ago(MIN - 1))]  # 604799 s old
    result = age_gate.decide(pkg, arts, NOW)
    assert result.passed is False
    assert result.age_seconds == MIN - 1
    assert "requires >= 604800s" in result.reason


def test_comfortably_old_passes():
    pkg = PinnedPackage("demo", "2.5.0", frozenset({SHA_A}))
    arts = [_artifact(SHA_A, _uploaded_seconds_ago(30 * 86400))]
    assert age_gate.decide(pkg, arts, NOW).passed is True


# --------------------------------------------------------------------------- #
# Multi-artifact: use the NEWEST upload among LOCK-ADMITTED hashes (TP-S8)
# --------------------------------------------------------------------------- #
def test_multi_artifact_uses_newest_admitted_timestamp():
    # Two admitted artifacts: one old (passes), one 1 s too new (fails). The
    # gate must key on the NEWEST admitted one and therefore FAIL.
    pkg = PinnedPackage("demo", "1.0.0", frozenset({SHA_A, SHA_B}))
    arts = [
        _artifact(SHA_A, _uploaded_seconds_ago(10 * 86400)),  # old
        _artifact(SHA_B, _uploaded_seconds_ago(MIN - 1)),     # too new, admitted
    ]
    result = age_gate.decide(pkg, arts, NOW)
    assert result.passed is False
    assert result.admitted_timestamp == _uploaded_seconds_ago(MIN - 1)


def test_newer_artifact_not_in_lock_is_ignored():
    # A freshly re-uploaded artifact (SHA_C, too new) is NOT admitted by the
    # lock, so it must be ignored; the admitted old artifact governs -> PASS.
    # This is the "old version number, new artifact bypass" defence.
    pkg = PinnedPackage("demo", "1.0.0", frozenset({SHA_A}))
    arts = [
        _artifact(SHA_A, _uploaded_seconds_ago(10 * 86400)),  # admitted, old
        _artifact(SHA_C, _uploaded_seconds_ago(60)),          # NOT admitted, new
    ]
    result = age_gate.decide(pkg, arts, NOW)
    assert result.passed is True
    assert result.admitted_timestamp == _uploaded_seconds_ago(10 * 86400)


# --------------------------------------------------------------------------- #
# Fail-closed branches (TP-S9): none may skip or pass
# --------------------------------------------------------------------------- #
def test_unmatched_hash_fails_closed():
    # Lock admits SHA_A but PyPI only offers SHA_B -> unmatched -> FAIL closed.
    pkg = PinnedPackage("demo", "1.0.0", frozenset({SHA_A}))
    arts = [_artifact(SHA_B, _uploaded_seconds_ago(10 * 86400))]
    result = age_gate.decide(pkg, arts, NOW)
    assert result.passed is False
    assert "matched" in result.reason


def test_unhashed_pin_fails_closed():
    pkg = PinnedPackage("demo", "1.0.0", frozenset())  # no hashes in lock
    arts = [_artifact(SHA_A, _uploaded_seconds_ago(10 * 86400))]
    result = age_gate.decide(pkg, arts, NOW)
    assert result.passed is False
    assert "unhashed" in result.reason


def test_malformed_timestamp_fails_closed():
    pkg = PinnedPackage("demo", "1.0.0", frozenset({SHA_A}))
    arts = [{"digests": {"sha256": SHA_A}, "upload_time_iso_8601": "not-a-date"}]
    with pytest.raises(AgeGateError):
        age_gate.decide(pkg, arts, NOW)


def test_missing_timestamp_fails_closed():
    pkg = PinnedPackage("demo", "1.0.0", frozenset({SHA_A}))
    arts = [{"digests": {"sha256": SHA_A}}]  # no upload_time_iso_8601
    with pytest.raises(AgeGateError):
        age_gate.decide(pkg, arts, NOW)


def test_registry_outage_fails_closed_in_evaluate_lock():
    # A provider that raises (simulated outage/HTTP error) must yield a FAIL
    # result for that package, not a skip.
    def broken_provider(name: str, version: str) -> list[dict]:
        raise AgeGateError("simulated registry outage")

    pkg = PinnedPackage("demo", "1.0.0", frozenset({SHA_A}))
    results = age_gate.evaluate_lock([pkg], broken_provider, NOW)
    assert len(results) == 1
    assert results[0].passed is False
    assert "outage" in results[0].reason


def test_missing_metadata_urls_fails_closed_via_client():
    # PyPIClient.artifacts must fail closed when 'urls' is empty/missing.
    class FakeResp:
        headers = {"Date": "Mon, 20 Jul 2026 12:00:00 GMT"}

        def __init__(self, payload):
            self._payload = payload

        def read(self):
            import json as _json
            return _json.dumps(self._payload).encode()

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    def opener(req):
        return FakeResp({"info": {}, "urls": []})

    client = age_gate.PyPIClient(opener=opener)
    with pytest.raises(AgeGateError):
        client.artifacts("demo", "1.0.0")


# --------------------------------------------------------------------------- #
# now-source: PyPIClient.utc_now uses the server Date header, not the local clock
# --------------------------------------------------------------------------- #
def test_utc_now_reads_server_date_header():
    class FakeResp:
        headers = {"Date": "Mon, 20 Jul 2026 12:00:00 GMT"}

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    client = age_gate.PyPIClient(opener=lambda req: FakeResp())
    now = client.utc_now()
    assert now == NOW


def test_utc_now_missing_date_header_fails_closed():
    class FakeResp:
        headers: dict = {}

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    client = age_gate.PyPIClient(opener=lambda req: FakeResp())
    with pytest.raises(AgeGateError):
        client.utc_now()


# --------------------------------------------------------------------------- #
# Lock parsing
# --------------------------------------------------------------------------- #
def test_parse_lock_collects_pins_and_hashes():
    text = (
        "fastapi==0.139.0 \\\n"
        f"    --hash=sha256:{SHA_A} \\\n"
        f"    --hash=sha256:{SHA_B}\n"
        "    # via -r requirements.in\n"
        "colorama==0.4.6 ; sys_platform == 'win32' \\\n"
        f"    --hash=sha256:{SHA_C}\n"
        "    # via click\n"
    )
    pkgs = {p.name: p for p in age_gate.parse_lock(text)}
    assert pkgs["fastapi"].version == "0.139.0"
    assert pkgs["fastapi"].sha256 == frozenset({SHA_A, SHA_B})
    assert pkgs["colorama"].version == "0.4.6"
    assert pkgs["colorama"].sha256 == frozenset({SHA_C})


def test_parse_lock_normalizes_names():
    text = f"PyYAML==6.0.3 \\\n    --hash=sha256:{SHA_A}\n"
    pkgs = age_gate.parse_lock(text)
    assert pkgs[0].name == "pyyaml"  # PEP 503 normalized


def test_parse_lock_hash_before_pin_fails_closed():
    text = f"    --hash=sha256:{SHA_A}\n"
    with pytest.raises(AgeGateError):
        age_gate.parse_lock(text)


def test_evaluate_lock_reports_every_package():
    pkgs = [
        PinnedPackage("old", "1.0.0", frozenset({SHA_A})),
        PinnedPackage("new", "2.0.0", frozenset({SHA_B})),
    ]

    def provider(name, version):
        if name == "old":
            return [_artifact(SHA_A, _uploaded_seconds_ago(10 * 86400))]
        return [_artifact(SHA_B, _uploaded_seconds_ago(MIN - 1))]

    results = {r.name: r for r in age_gate.evaluate_lock(pkgs, provider, NOW)}
    assert results["old"].passed is True
    assert results["new"].passed is False
