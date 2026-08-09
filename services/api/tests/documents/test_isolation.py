"""Tests for the fail-closed parser-isolation capability gate (M2-T015, R275-R276).

Simulated platform facts are injected by monkeypatching the module's probe seams —
never by real Landlock/seccomp syscalls or platform mutation — so every branch is
deterministic on any host (Windows/macOS dev hosts and Linux CI alike, R274). The one
real-probe test asserts only structural invariants, never a host-specific outcome.
"""

from __future__ import annotations

import dataclasses
import inspect
import json
import re

import pytest

from app.documents import isolation
from app.documents.isolation import (
    CapabilityProbe,
    IsolationCapability,
    ParsingDisabled,
    ParsingPermitted,
    require_isolation,
)


def _simulate_platform(
    monkeypatch: pytest.MonkeyPatch,
    *,
    os_name: str = "Linux",
    landlock: bool = True,
    seccomp: bool = True,
) -> None:
    """Drive the gate through simulated platform facts via the probe seams."""
    monkeypatch.setattr(isolation, "_probe_os_name", lambda: os_name)
    monkeypatch.setattr(isolation, "_probe_kernel_release", lambda: "6.8.0-simulated")
    monkeypatch.setattr(
        isolation,
        "_probe_landlock",
        lambda name: CapabilityProbe(
            capability="landlock",
            available=landlock,
            detail=(
                "simulated: active LSM with Landlock ABI version 4"
                if landlock
                else "simulated: 'landlock' is not among the running kernel's active LSMs"
            ),
        ),
    )
    monkeypatch.setattr(
        isolation,
        "_probe_seccomp",
        lambda name: CapabilityProbe(
            capability="seccomp",
            available=seccomp,
            detail=(
                "simulated: seccomp filter available"
                if seccomp
                else "simulated: no 'Seccomp' field in /proc/self/status"
            ),
        ),
    )


def test_simulated_full_linux_capabilities_permit_parsing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _simulate_platform(monkeypatch)
    result = require_isolation()
    assert isinstance(result, IsolationCapability)
    assert isinstance(result.verdict, ParsingPermitted)
    assert result.verdict.permitted is True
    assert result.os_name == "Linux"
    assert result.kernel_release == "6.8.0-simulated"
    assert result.landlock.available is True
    assert result.seccomp.available is True


@pytest.mark.parametrize("os_name", ["Windows", "Darwin", "FreeBSD", ""])
def test_non_linux_platform_is_disabled_naming_the_platform(
    monkeypatch: pytest.MonkeyPatch, os_name: str
) -> None:
    # Only the os/kernel seams are patched: the REAL landlock/seccomp probes run with
    # the non-Linux os name and must return UNAVAILABLE by construction, touching no
    # kernel interface and no ctypes on any host.
    monkeypatch.setattr(isolation, "_probe_os_name", lambda: os_name)
    monkeypatch.setattr(isolation, "_probe_kernel_release", lambda: "n/a")
    result = require_isolation()
    assert isinstance(result.verdict, ParsingDisabled)
    assert result.verdict.permitted is False
    assert result.verdict.failed_capability == "os"
    assert repr(os_name) in result.verdict.reason
    assert result.landlock.available is False
    assert "by construction" in result.landlock.detail
    assert result.seccomp.available is False
    assert "by construction" in result.seccomp.detail


def test_simulated_linux_with_missing_landlock_disables_naming_landlock(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _simulate_platform(monkeypatch, landlock=False)
    verdict = require_isolation().verdict
    assert isinstance(verdict, ParsingDisabled)
    assert verdict.failed_capability == "landlock"
    assert "landlock" in verdict.reason


def test_simulated_linux_with_missing_seccomp_disables_naming_seccomp(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _simulate_platform(monkeypatch, seccomp=False)
    verdict = require_isolation().verdict
    assert isinstance(verdict, ParsingDisabled)
    assert verdict.failed_capability == "seccomp"
    assert "Seccomp" in verdict.reason


def test_both_capabilities_missing_names_landlock_first(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Deterministic first-failure order mirrors architecture section 5's property
    # order: filesystem isolation (Landlock) before network denial (seccomp).
    _simulate_platform(monkeypatch, landlock=False, seccomp=False)
    verdict = require_isolation().verdict
    assert isinstance(verdict, ParsingDisabled)
    assert verdict.failed_capability == "landlock"


def test_capability_probe_raising_disables_with_the_error_verbatim(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _simulate_platform(monkeypatch)

    def _exploding_probe(os_name: str) -> CapabilityProbe:
        raise RuntimeError("landlock probe exploded: securityfs went away")

    monkeypatch.setattr(isolation, "_probe_landlock", _exploding_probe)
    result = require_isolation()
    assert isinstance(result.verdict, ParsingDisabled)
    assert result.verdict.failed_capability == "landlock"
    assert "RuntimeError" in result.verdict.reason
    assert "landlock probe exploded: securityfs went away" in result.verdict.reason
    assert result.landlock.available is False


def test_platform_probe_raising_disables_with_the_error_verbatim(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _exploding_os_probe() -> str:
        raise OSError("uname unavailable: kernel fault")

    monkeypatch.setattr(isolation, "_probe_os_name", _exploding_os_probe)
    result = require_isolation()
    assert isinstance(result.verdict, ParsingDisabled)
    assert result.verdict.failed_capability == "os"
    assert "OSError" in result.verdict.reason
    assert "uname unavailable: kernel fault" in result.verdict.reason
    assert result.os_name == "<unprobed>"
    assert result.landlock.available is False
    assert result.seccomp.available is False


def test_results_are_immutable_values(monkeypatch: pytest.MonkeyPatch) -> None:
    _simulate_platform(monkeypatch)
    result = require_isolation()
    with pytest.raises(dataclasses.FrozenInstanceError):
        result.verdict = ParsingDisabled(failed_capability="os", reason="tamper")
    with pytest.raises(dataclasses.FrozenInstanceError):
        result.verdict.permitted = False
    with pytest.raises(dataclasses.FrozenInstanceError):
        result.landlock.available = False
    _simulate_platform(monkeypatch, landlock=False)
    disabled = require_isolation().verdict
    assert isinstance(disabled, ParsingDisabled)
    with pytest.raises(dataclasses.FrozenInstanceError):
        disabled.failed_capability = "nothing"
    with pytest.raises(dataclasses.FrozenInstanceError):
        disabled.reason = "overridden"


def test_gate_takes_no_override_parameter() -> None:
    # R276: no override argument exists — the signature itself is the evidence.
    assert len(inspect.signature(require_isolation).parameters) == 0


def test_module_reads_no_environment_and_spawns_no_process() -> None:
    source = inspect.getsource(isolation)
    assert "subprocess" not in source
    assert "os.environ" not in source
    assert "getenv" not in source
    assert re.search(r"\bimport\s+os\b|\bfrom\s+os\s+import\b", source) is None
    assert not hasattr(isolation, "os")
    assert not hasattr(isolation, "subprocess")


def test_linux_only_probes_are_unavailable_by_construction_off_linux() -> None:
    # Real seam functions, non-Linux os argument: the by-construction branch returns
    # before any kernel file or ctypes use, so this is safe and deterministic on any
    # host.
    landlock = isolation._probe_landlock("Windows")
    assert landlock.available is False
    assert "by construction" in landlock.detail
    seccomp = isolation._probe_seccomp("Darwin")
    assert seccomp.available is False
    assert "by construction" in seccomp.detail


def test_disabled_payload_is_json_serializable_metadata_only(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _simulate_platform(monkeypatch, os_name="Windows", landlock=False, seccomp=False)
    verdict = require_isolation().verdict
    assert isinstance(verdict, ParsingDisabled)
    payload = verdict.to_payload()
    assert set(payload) == {"reject_code", "failed_capability", "reason"}
    assert payload["reject_code"] == "isolation_unavailable"
    assert json.loads(json.dumps(payload)) == payload


def test_real_host_probe_returns_typed_frozen_verdict() -> None:
    # No monkeypatching: structural invariants only, valid on every host. On
    # Windows/macOS this is always ParsingDisabled by construction; on Linux CI the
    # verdict is whatever the kernel affirmatively proves (R274).
    result = require_isolation()
    assert isinstance(result, IsolationCapability)
    assert isinstance(result.verdict, (ParsingPermitted, ParsingDisabled))
    if isinstance(result.verdict, ParsingPermitted):
        assert result.os_name == "Linux"
        assert result.landlock.available is True
        assert result.seccomp.available is True
    else:
        assert result.verdict.failed_capability in {"os", "landlock", "seccomp"}
        assert result.verdict.reason
