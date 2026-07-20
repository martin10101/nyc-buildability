#!/usr/bin/env python3
"""Machine-enforced dependency release-age gate (task M0-T020).

Enforces the owner's permanent dependency-admission rule for Python: every
package version admitted by a hash-pinned lock -- DIRECT and TRANSITIVE, across
BOTH the production runtime lock (services/api/requirements.txt) and the tooling
lock (services/api/requirements-tools.lock) -- must have been published on
official PyPI at least ``MIN_AGE_SECONDS`` (604800 s = 7 days) ago.

Design (age_gate_contract, M0-T020):

* Live gate uses the CURRENT UTC instant taken from PyPI's own ``Date`` response
  header (not the local clock, not a cached table) and official LIVE PyPI JSON
  metadata queried per package/version.
* For a version with multiple artifacts, the gate uses the NEWEST upload
  timestamp among ONLY those artifacts whose sha256 is admitted by the lock.
  This prevents an old version number with a freshly re-uploaded artifact from
  bypassing the wait.
* The comparison is full-instant arithmetic in seconds; exactly 604800 s PASSES,
  604799 s FAILS. No date-only or truncated-day math.
* The gate FAILS CLOSED (exit 1, package marked FAIL, never skipped/passed) on:
  registry outage / network error, missing metadata, a malformed or missing
  upload timestamp, a lock sha256 hash that cannot be matched to any official
  PyPI artifact for that version, or any otherwise ambiguous result.
* Per package/version it prints: name, version, admitted-artifact upload
  timestamp, elapsed age, and PASS/FAIL.
* There is NO agent-created exception path. Any emergency age-only exception is
  an owner action taken OUTSIDE this tool (it cannot waive an advisory affecting
  an installed version, and pip-audit remains the separate blocking advisory
  gate); this module never reads an allowlist or suppression file.

Network access is confined to :class:`PyPIClient`; the pure logic
(:func:`evaluate_lock`, :func:`decide`) takes an injectable ``now`` and an
injectable metadata provider so the unit tests are deterministic and offline.

Usage::

    python scripts/dependency_age_gate.py requirements.txt requirements-tools.lock

Exit code 0 iff every admitted artifact in every given lock is at least seven
days old; 1 otherwise (including any fail-closed condition).
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import sys
import urllib.error
import urllib.request
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from email.utils import parsedate_to_datetime

MIN_AGE_SECONDS = 604_800  # 7 days; exactly this PASSES, one second less FAILS.
PYPI_JSON_URL = "https://pypi.org/pypi/{name}/{version}/json"
PYPI_TIME_URL = "https://pypi.org/pypi/pip/json"  # any stable project; only the Date header is used
_HTTP_TIMEOUT = 30

# A lock line that starts a package pin, e.g. ``fastapi==0.139.0 \`` or
# ``colorama==0.4.6 ; sys_platform == 'win32' \``.
_PIN_RE = re.compile(r"^(?P<name>[A-Za-z0-9._-]+)==(?P<version>[^\s;\\]+)")
_HASH_RE = re.compile(r"--hash=sha256:(?P<sha>[0-9a-fA-F]{64})")


# --------------------------------------------------------------------------- #
# Data model
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class PinnedPackage:
    """A single ``name==version`` pin and the set of sha256 hashes the lock
    admits for it (lower-cased, hex)."""

    name: str
    version: str
    sha256: frozenset[str]


@dataclass(frozen=True)
class PackageResult:
    name: str
    version: str
    admitted_timestamp: _dt.datetime | None
    age_seconds: float | None
    passed: bool
    reason: str  # "" on pass; a fail-closed explanation otherwise


class AgeGateError(Exception):
    """A fail-closed condition (outage, missing/malformed metadata, unmatched
    hash, ambiguous result)."""


# --------------------------------------------------------------------------- #
# Lock parsing
# --------------------------------------------------------------------------- #
def parse_lock(text: str) -> list[PinnedPackage]:
    """Parse a ``--generate-hashes`` requirements lock into pinned packages.

    Hash lines belong to the most recent ``name==version`` pin. A pin with no
    hashes yields an empty hash set, which :func:`decide` treats as a
    fail-closed condition (an unhashed lock line must never be silently
    admitted).
    """
    packages: dict[tuple[str, str], set[str]] = {}
    order: list[tuple[str, str]] = []
    current: tuple[str, str] | None = None
    for raw in text.splitlines():
        pin = _PIN_RE.match(raw)
        if pin:
            name = _normalize(pin.group("name"))
            version = pin.group("version")
            current = (name, version)
            if current not in packages:
                packages[current] = set()
                order.append(current)
        for hm in _HASH_RE.finditer(raw):
            if current is None:
                # A hash line before any pin -> malformed lock; fail closed.
                raise AgeGateError("hash line encountered before any package pin")
            packages[current].add(hm.group("sha").lower())
    return [PinnedPackage(n, v, frozenset(packages[(n, v)])) for (n, v) in order]


def _normalize(name: str) -> str:
    """PEP 503 name normalization (lower-case; runs of -, _, . collapse to -)."""
    return re.sub(r"[-_.]+", "-", name).lower()


# --------------------------------------------------------------------------- #
# Live PyPI access (the only networked surface)
# --------------------------------------------------------------------------- #
class PyPIClient:
    """Fetches the authoritative UTC ``now`` and per-version artifact metadata
    from live PyPI. Every failure is surfaced as :class:`AgeGateError` so the
    gate fails closed rather than skipping a package."""

    def __init__(self, opener: Callable[[urllib.request.Request], object] | None = None):
        self._opener = opener or (lambda req: urllib.request.urlopen(req, timeout=_HTTP_TIMEOUT))

    def utc_now(self) -> _dt.datetime:
        try:
            req = urllib.request.Request(PYPI_TIME_URL, method="HEAD")
            with self._opener(req) as resp:  # type: ignore[attr-defined]
                date_hdr = resp.headers.get("Date")
        except (urllib.error.URLError, OSError, ValueError) as exc:
            raise AgeGateError(f"cannot obtain authoritative UTC time from PyPI: {exc}") from exc
        if not date_hdr:
            raise AgeGateError("PyPI response carried no Date header for the UTC clock")
        try:
            now = parsedate_to_datetime(date_hdr)
        except (TypeError, ValueError) as exc:
            raise AgeGateError(f"malformed PyPI Date header {date_hdr!r}: {exc}") from exc
        if now.tzinfo is None:
            now = now.replace(tzinfo=_dt.UTC)
        return now.astimezone(_dt.UTC)

    def artifacts(self, name: str, version: str) -> list[dict]:
        """Return the raw ``urls`` list (each artifact's metadata) for a
        version. Fails closed on outage, HTTP error, or missing ``urls``."""
        url = PYPI_JSON_URL.format(name=name, version=version)
        try:
            req = urllib.request.Request(url)
            with self._opener(req) as resp:  # type: ignore[attr-defined]
                payload = json.load(resp)
        except (urllib.error.URLError, OSError, ValueError) as exc:
            raise AgeGateError(f"cannot fetch PyPI metadata for {name}=={version}: {exc}") from exc
        urls = payload.get("urls")
        if not isinstance(urls, list) or not urls:
            raise AgeGateError(f"PyPI returned no artifacts for {name}=={version}")
        return urls


# --------------------------------------------------------------------------- #
# Core decision logic (pure; deterministic under injected now + metadata)
# --------------------------------------------------------------------------- #
def _artifact_timestamp(artifact: dict) -> _dt.datetime:
    ts = artifact.get("upload_time_iso_8601")
    if not ts:
        raise AgeGateError("artifact metadata missing upload_time_iso_8601")
    try:
        parsed = _dt.datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise AgeGateError(f"malformed artifact upload timestamp {ts!r}: {exc}") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=_dt.UTC)
    return parsed.astimezone(_dt.UTC)


def decide(
    pkg: PinnedPackage,
    artifacts: Iterable[dict],
    now: _dt.datetime,
) -> PackageResult:
    """Decide PASS/FAIL for one pinned package given its PyPI artifacts.

    Uses the NEWEST upload timestamp among artifacts whose sha256 is admitted by
    the lock. Fails closed if the lock pinned no hashes, if no admitted hash
    matches an official artifact, or on any malformed timestamp.
    """
    if not pkg.sha256:
        return PackageResult(
            pkg.name, pkg.version, None, None, False,
            "lock pins no sha256 hash for this package (unhashed line)",
        )
    newest: _dt.datetime | None = None
    matched = 0
    for art in artifacts:
        digest = (art.get("digests") or {}).get("sha256")
        if not digest or digest.lower() not in pkg.sha256:
            continue
        matched += 1
        ts = _artifact_timestamp(art)  # raises AgeGateError -> fail closed
        if newest is None or ts > newest:
            newest = ts
    if matched == 0 or newest is None:
        return PackageResult(
            pkg.name, pkg.version, None, None, False,
            "no official PyPI artifact matched the lock's admitted sha256 hashes",
        )
    age = (now - newest).total_seconds()
    passed = age >= MIN_AGE_SECONDS
    reason = "" if passed else f"published {age:.0f}s ago; requires >= {MIN_AGE_SECONDS}s"
    return PackageResult(pkg.name, pkg.version, newest, age, passed, reason)


def evaluate_lock(
    packages: Iterable[PinnedPackage],
    metadata_provider: Callable[[str, str], list[dict]],
    now: _dt.datetime,
) -> list[PackageResult]:
    """Evaluate every pin. A fail-closed :class:`AgeGateError` for a single
    package is captured as a FAIL result for that package (the run still fails)
    rather than aborting the whole report, so the operator sees every problem."""
    results: list[PackageResult] = []
    for pkg in packages:
        try:
            artifacts = metadata_provider(pkg.name, pkg.version)
            results.append(decide(pkg, artifacts, now))
        except AgeGateError as exc:
            results.append(PackageResult(pkg.name, pkg.version, None, None, False, str(exc)))
    return results


# --------------------------------------------------------------------------- #
# Reporting / CLI
# --------------------------------------------------------------------------- #
def format_result(r: PackageResult) -> str:
    ts = r.admitted_timestamp.isoformat() if r.admitted_timestamp else "-"
    if r.age_seconds is not None:
        age = f"{r.age_seconds:.0f}s ({r.age_seconds / 86400:.2f}d)"
    else:
        age = "-"
    verdict = "PASS" if r.passed else "FAIL"
    tail = "" if r.passed else f"  [{r.reason}]"
    return f"{verdict}  {r.name}=={r.version}  uploaded={ts}  age={age}{tail}"


def run(lock_paths: list[str], client: PyPIClient | None = None) -> int:
    client = client or PyPIClient()
    try:
        now = client.utc_now()
    except AgeGateError as exc:
        print(f"FAIL-CLOSED: {exc}", file=sys.stderr)
        return 1

    overall_ok = True
    print(f"Dependency release-age gate  (now={now.isoformat()}, min_age={MIN_AGE_SECONDS}s)")
    for lock_path in lock_paths:
        try:
            text = open(lock_path, encoding="utf-8").read()
            packages = parse_lock(text)
        except (OSError, AgeGateError) as exc:
            print(f"FAIL-CLOSED: cannot read/parse lock {lock_path}: {exc}", file=sys.stderr)
            overall_ok = False
            continue
        print(f"\n== {lock_path}  ({len(packages)} pinned packages) ==")
        results = evaluate_lock(packages, client.artifacts, now)
        for r in sorted(results, key=lambda x: (x.name, x.version)):
            print("  " + format_result(r))
            overall_ok = overall_ok and r.passed

    print("\nRESULT:", "PASS — every admitted artifact is >= 7 days old" if overall_ok
          else "FAIL — at least one package is too new or could not be verified")
    return 0 if overall_ok else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Enforce the >=7-day dependency release-age gate over hash-pinned locks.",
    )
    parser.add_argument(
        "locks", nargs="+", help="Paths to --generate-hashes requirements locks to check.",
    )
    args = parser.parse_args(argv)
    return run(args.locks)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
