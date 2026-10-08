"""M5-T141: the e2e browser-test harness serves the results route from the recorded files BY PATH
and imports nothing from the server's test tree, so it starts where only the installed ``app``
package is on the Python path (GitHub's web-e2e job). Three checks:

(a) THE GUARD: no Python file under apps/web/e2e/harness imports from ``tests`` - the coupling that
    kept the browser-test job from starting on every head of wave 13 (DB-207). A temp-directory
    mutation proof shows the guard's own detector flags an injected ``from tests`` line.
(b) EQUALITY: for the recorded Northern lot the harness provider returns the SAME study inputs as
    the results-route test's own ``benchmark_provider()`` - compared field by field, with the single
    wall-clock field named and excluded.
(c) ANOTHER LOT: any other BBL raises the provider's unavailable error (the route's fail-safe 503).

This test lives in the server test tree, so it may import from ``tests.*`` and loads the harness by
adding its folder to the Python path, as test_address_resolution_recorded_geoclient.py does.
"""

from __future__ import annotations

import copy
import dataclasses
import http.client
import json
import re
import socket
import sys
from pathlib import Path

import pytest

from app.api.v1.study_inputs import StudyInputs, StudyInputsUnavailableError
from tests.api.test_results_read_api import benchmark_provider

# <root>/services/api/tests/api/test_e2e_harness_results_inputs.py -> parents[4] is the repo root.
_REPO_ROOT = Path(__file__).resolve().parents[4]
_HARNESS_DIR = _REPO_ROOT / "apps" / "web" / "e2e" / "harness"
_BENCHMARK_LOT_FIXTURE = (
    _REPO_ROOT / "packages" / "contracts" / "fixtures" / "valid" / "benchmark_lot"
    / "northern_blvd_215_16_queens_4073340070.json"
)
if str(_HARNESS_DIR) not in sys.path:
    sys.path.insert(0, str(_HARNESS_DIR))
import fixture_api  # noqa: E402 (path set above)

NORTHERN_BBL = "4073340070"
# A line that, after leading spaces, starts with ``from tests`` or ``import tests`` (module level or
# a function body). ``tests`` must be the whole top-level module, so ``tests_helper`` never matches.
_IMPORTS_TESTS = re.compile(r"^(from|import)\s+tests(\.|\s|$)")


def _files_importing_tests(harness_dir: Path) -> list[tuple[str, int, str]]:
    """Every ``(file name, line number, stripped line)`` under ``harness_dir`` whose Python source
    has a line importing from the ``tests`` package."""
    offenders: list[tuple[str, int, str]] = []
    for path in sorted(harness_dir.rglob("*.py")):
        for lineno, line in enumerate(path.read_text("utf-8").splitlines(), 1):
            if _IMPORTS_TESTS.match(line.lstrip()):
                offenders.append((path.name, lineno, line.strip()))
    return offenders


# --------------------------------------------------------------------------- (a) the guard
def test_no_harness_file_imports_from_the_server_test_tree() -> None:
    """S2: no Python file under apps/web/e2e/harness imports from ``tests`` - the import CI cannot
    resolve, because its browser-test job installs the server with only the ``app`` package."""
    offenders = _files_importing_tests(_HARNESS_DIR)
    assert offenders == [], (
        "a harness file imports from the server test tree (tests.*), which the browser-test job "
        f"cannot resolve (only the installed app package is on its path): {offenders}"
    )


def test_the_guard_flags_an_injected_tests_import(tmp_path: Path) -> None:
    """S2 mutation proof: unmutated copies of the harness sources report nothing; a copy with one
    ``from tests`` line appended is reported, at exactly that line - so the guard above would go red
    if the coupling ever came back."""
    clean = tmp_path / "clean"
    clean.mkdir()
    for path in _HARNESS_DIR.rglob("*.py"):
        (clean / path.name).write_text(path.read_text("utf-8"), "utf-8")
    assert _files_importing_tests(clean) == []

    offending_line = "from tests.spatial._northern_replay import replay_pluto"
    mutated = tmp_path / "mutated"
    mutated.mkdir()
    body = (_HARNESS_DIR / "fixture_api.py").read_text("utf-8")
    (mutated / "fixture_api.py").write_text(body + f"\n    {offending_line}\n", "utf-8")
    offenders = _files_importing_tests(mutated)
    assert [name for name, _lineno, _line in offenders] == ["fixture_api.py"]
    assert offenders[0][2] == offending_line


# --------------------------------------------------------------------------- offline guard
def _no_network(monkeypatch) -> None:
    def _blocked(*_a, **_k):
        raise AssertionError("network I/O attempted in a recorded-data test")

    monkeypatch.setattr(http.client.HTTPConnection, "connect", _blocked)
    monkeypatch.setattr(http.client.HTTPSConnection, "connect", _blocked)
    monkeypatch.setattr(socket, "create_connection", _blocked)


# --------------------------------------------------------------------------- (b) equality
def _normalized(inputs: StudyInputs) -> StudyInputs:
    """``inputs`` with the single wall-clock field neutralized. ``build_property_profile`` stamps
    ``property_profile.profile_version.generated_at`` from ``datetime.now(UTC)`` and NEITHER
    provider fixes the profile clock, so it is the ONLY non-deterministic field between two builds.
    Every other field - the confirmed address, the derived B-03 site geometry, the prepared tax-map
    outline and the whole rest of the property profile - stays in the comparison, so a genuinely
    different harness input still fails the equality test."""
    profile = copy.deepcopy(dict(inputs.property_profile))
    version = dict(profile["profile_version"])
    version["generated_at"] = "<wall-clock>"
    profile["profile_version"] = version
    return dataclasses.replace(inputs, property_profile=profile)


def test_harness_inputs_equal_the_test_trees_benchmark_provider(monkeypatch) -> None:
    """S3: for the recorded Northern lot the harness provider's study inputs equal the inputs the
    results-route test's own ``benchmark_provider()`` returns, apart from the wall-clock
    ``profile_version.generated_at`` (named in ``_normalized``). Built offline from the recorded
    pack."""
    _no_network(monkeypatch)
    harness = fixture_api.harness_results_inputs_provider()(NORTHERN_BBL, "cid-harness")
    bench = benchmark_provider()(NORTHERN_BBL, "cid-bench")

    # The one excluded field is genuinely present on both builds (the exclusion is not vacuous)...
    assert harness.property_profile["profile_version"]["generated_at"]
    assert bench.property_profile["profile_version"]["generated_at"]
    # ...and everything else is equal, field by field.
    assert _normalized(harness) == _normalized(bench)

    # The confirmed address really came from the benchmark-lot fixture (read here independently,
    # never retyped) and is the same the test tree's provider supplies.
    fixture_address = json.loads(_BENCHMARK_LOT_FIXTURE.read_text("utf-8"))["identity"]["address"]
    assert harness.address == bench.address == fixture_address
    assert harness.site_geometry is not None
    assert harness.prepared_outline is not None


# --------------------------------------------------------------------------- (c) another lot
@pytest.mark.parametrize("bbl", ["1000010100", "4073340071", "5999999999"])
def test_any_other_lot_raises_the_unavailable_error(bbl: str) -> None:
    """S4: any other BBL is the provider's unavailable error (the route maps it to a bounded 503),
    never a fabricated document."""
    provide = fixture_api.harness_results_inputs_provider()
    with pytest.raises(StudyInputsUnavailableError) as excinfo:
        provide(bbl, "cid")
    assert excinfo.value.reason == "not_served"
